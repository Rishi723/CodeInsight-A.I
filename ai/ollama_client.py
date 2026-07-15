"""
Ollama Client — ai/ollama_client.py

Production-quality communication layer between CodeInsight AI and
the Ollama local LLM server.

This module is the **only** place that talks to the Ollama HTTP API.
It owns the network boundary and exposes a clean, typed interface
that higher-level modules (analyzers, services) consume.

Responsibilities:
    • Connection health-checking
    • Model discovery
    • Prompt → response generation
    • Centralised error handling and logging

Non-responsibilities (kept in other modules):
    • Prompt construction     → ai/prompts.py
    • Business / analysis     → services/analyzer.py
    • UI rendering            → ui/components.py

Architecture notes:
    The class accepts an ``OllamaConfig`` instance via its constructor
    (dependency injection) so that tests can supply alternate configs
    without touching global state.  A convenience module-level factory
    ``get_client()`` provides a ready-to-use singleton backed by the
    default settings from ``config/settings.py``.

Usage:
    >>> from ai.ollama_client import get_client
    >>> client = get_client()
    >>> if client.check_connection():
    ...     response = client.generate("Explain this code: ...")
"""

from __future__ import annotations

import logging
from typing import Any

import requests
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
    ReadTimeout,
    RequestException,
)

from config.settings import OLLAMA, OllamaConfig

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Custom Exceptions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class OllamaConnectionError(Exception):
    """Raised when the Ollama server cannot be reached."""


class OllamaTimeoutError(Exception):
    """Raised when a request to Ollama exceeds the configured timeout."""


class OllamaModelNotFoundError(Exception):
    """Raised when the requested model is not available locally."""


class OllamaAPIError(Exception):
    """Raised for unexpected Ollama API errors (non-2xx responses)."""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OllamaClient
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class OllamaClient:
    """Reusable, stateless HTTP client for the Ollama REST API.

    All configuration is read from the injected ``OllamaConfig``
    dataclass — base URL, default model name, and request timeout.

    Args:
        config: An ``OllamaConfig`` instance.  Defaults to the
                module-level ``OLLAMA`` singleton from settings.

    Example:
        >>> client = OllamaClient()
        >>> client.check_connection()
        True
        >>> text = client.generate("Say hello")
        'Hello! How can I help you today?'
    """

    # Ollama REST endpoints (relative to base_url)
    _ENDPOINT_GENERATE: str = "/api/generate"
    _ENDPOINT_TAGS: str = "/api/tags"

    def __init__(self, config: OllamaConfig | None = None) -> None:
        self._config: OllamaConfig = config or OLLAMA
        self._base_url: str = self._config.base_url.rstrip("/")
        self._model: str = self._config.model
        self._timeout: int = self._config.request_timeout

        logger.info(
            "OllamaClient initialised  url=%s  model=%s  timeout=%ds",
            self._base_url,
            self._model,
            self._timeout,
        )

    # ─────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────

    def check_connection(self) -> bool:
        """Verify whether the Ollama server is reachable.

        Sends a lightweight GET to the server root (``/``) and
        returns ``True`` if a 200 response is received.

        Returns:
            bool: ``True`` if Ollama is running, ``False`` otherwise.
        """
        url = self._base_url
        logger.debug("Checking Ollama connection at %s", url)

        try:
            response = requests.get(url, timeout=10)
            is_alive = response.status_code == 200
            if is_alive:
                logger.info("Ollama server is online  url=%s", url)
            else:
                logger.warning(
                    "Ollama responded with unexpected status %d",
                    response.status_code,
                )
            return is_alive

        except RequestsConnectionError:
            logger.warning("Ollama server unreachable at %s", url)
            return False
        except ReadTimeout:
            logger.warning("Ollama health-check timed out  url=%s", url)
            return False
        except RequestException as exc:
            logger.error("Unexpected error during health-check: %s", exc)
            return False

    def list_models(self) -> list[str]:
        """Return the names of all locally installed Ollama models.

        Calls ``GET /api/tags`` and extracts the ``name`` field from
        each model entry.

        Returns:
            list[str]: Model name strings, e.g. ``["llama3", "mistral"]``.

        Raises:
            OllamaConnectionError: If the server is unreachable.
            OllamaAPIError:        If the server returns a non-200 status.
        """
        url = f"{self._base_url}{self._ENDPOINT_TAGS}"
        logger.debug("Listing models from %s", url)

        data = self._get(url)
        models: list[str] = [
            m.get("name", "unknown")
            for m in data.get("models", [])
        ]

        logger.info("Available Ollama models: %s", models)
        return models

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        *,
        stream: bool = False,
    ) -> str:
        """Send a prompt to Ollama and return the generated text.

        Args:
            prompt: The full prompt string to send.
            model:  Override the default model for this request.
                    If ``None``, uses the model from configuration.
            stream: Reserved for future streaming support.
                    Currently must be ``False``.

        Returns:
            str: The generated response text.

        Raises:
            OllamaConnectionError:   If the server is unreachable.
            OllamaTimeoutError:       If the request exceeds the timeout.
            OllamaModelNotFoundError: If the requested model is not found.
            OllamaAPIError:           For any other API-level error.
            ValueError:               If the prompt is empty.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        target_model = model or self._model
        url = f"{self._base_url}{self._ENDPOINT_GENERATE}"

        payload: dict[str, Any] = {
            "model": target_model,
            "prompt": prompt,
            "stream": stream,
        }

        logger.info(
            "Generating response  model=%s  prompt_length=%d",
            target_model,
            len(prompt),
        )

        data = self._post(url, payload)
        response_text: str = data.get("response", "")

        logger.info(
            "Generation complete  model=%s  response_length=%d",
            target_model,
            len(response_text),
        )

        return response_text

    def get_current_model(self) -> str:
        """Return the configured default model name.

        Returns:
            str: The model identifier from configuration.
        """
        return self._model

    # ─────────────────────────────────────────
    # Internal HTTP helpers
    # ─────────────────────────────────────────

    def _get(self, url: str) -> dict[str, Any]:
        """Execute a GET request and return the parsed JSON body.

        Args:
            url: Fully-qualified URL to request.

        Returns:
            dict: Parsed JSON response.

        Raises:
            OllamaConnectionError: Server unreachable.
            OllamaTimeoutError:    Request timed out.
            OllamaAPIError:        Non-200 status or invalid JSON.
        """
        try:
            response = requests.get(url, timeout=self._timeout)
        except RequestsConnectionError as exc:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self._base_url}. "
                "Ensure the Ollama server is running."
            ) from exc
        except ReadTimeout as exc:
            raise OllamaTimeoutError(
                f"Request timed out after {self._timeout}s  url={url}"
            ) from exc
        except RequestException as exc:
            raise OllamaAPIError(
                f"Unexpected request error: {exc}"
            ) from exc

        return self._parse_response(response)

    def _post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute a POST request and return the parsed JSON body.

        Args:
            url:     Fully-qualified URL to request.
            payload: JSON-serialisable dictionary for the request body.

        Returns:
            dict: Parsed JSON response.

        Raises:
            OllamaConnectionError:   Server unreachable.
            OllamaTimeoutError:      Request timed out.
            OllamaModelNotFoundError: Model not found (HTTP 404).
            OllamaAPIError:          Non-200 status or invalid JSON.
        """
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self._timeout,
            )
        except RequestsConnectionError as exc:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self._base_url}. "
                "Ensure the Ollama server is running."
            ) from exc
        except ReadTimeout as exc:
            raise OllamaTimeoutError(
                f"Request timed out after {self._timeout}s. "
                "The model may be loading or the prompt may be too long."
            ) from exc
        except RequestException as exc:
            raise OllamaAPIError(
                f"Unexpected request error: {exc}"
            ) from exc

        return self._parse_response(response)

    @staticmethod
    def _parse_response(response: requests.Response) -> dict[str, Any]:
        """Validate HTTP status and parse the JSON body.

        Args:
            response: The ``requests.Response`` object.

        Returns:
            dict: Parsed JSON body.

        Raises:
            OllamaModelNotFoundError: HTTP 404.
            OllamaAPIError:           Any other non-200 status or
                                      malformed JSON.
        """
        if response.status_code == 404:
            raise OllamaModelNotFoundError(
                "Model not found. Run `ollama pull <model>` to "
                "download it first."
            )

        if response.status_code != 200:
            raise OllamaAPIError(
                f"Ollama returned HTTP {response.status_code}: "
                f"{response.text[:300]}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise OllamaAPIError(
                "Ollama returned invalid JSON. "
                f"Raw response: {response.text[:300]}"
            ) from exc


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Module-Level Convenience Factory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_default_client: OllamaClient | None = None


def get_client() -> OllamaClient:
    """Return a module-level ``OllamaClient`` singleton.

    The singleton is lazily created on first call using the default
    ``OLLAMA`` configuration from ``config/settings.py``.

    Returns:
        OllamaClient: The shared client instance.
    """
    global _default_client  # noqa: PLW0603
    if _default_client is None:
        _default_client = OllamaClient()
    return _default_client
