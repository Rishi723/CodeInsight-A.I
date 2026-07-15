"""
Analyzer Service — services/analyzer.py

Central orchestration layer for the CodeInsight AI application.

``AnalyzerService`` is the "brain" that coordinates the end-to-end
code analysis workflow.  It receives user input, validates it,
delegates prompt construction to ``PromptBuilder``, sends the prompt
to ``OllamaClient``, and returns the AI response.

Responsibilities:
    • Input validation  (empty code, unsupported language, length)
    • Workflow orchestration  (prompt → client → response)
    • Centralised error handling and logging

Non-responsibilities (kept in other modules):
    • Prompt construction   → ai/prompts.py
    • HTTP communication    → ai/ollama_client.py
    • UI rendering          → ui/components.py
    • Response formatting   → services/formatter.py (future)

Design:
    Constructor dependency injection is used for ``PromptBuilder`` and
    ``OllamaClient``.  This keeps the class easily testable — tests
    can supply mocks without touching production singletons.

    A module-level ``get_analyzer()`` factory provides a ready-to-use
    singleton backed by the default instances from their respective
    modules.

Usage:
    >>> from services.analyzer import get_analyzer
    >>> analyzer = get_analyzer()
    >>> response = analyzer.analyze_code("print('hi')", "Python")
"""

from __future__ import annotations

import logging
import time

from ai.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaTimeoutError,
    OllamaModelNotFoundError,
    OllamaAPIError,
    get_client,
)
from ai.prompts import PromptBuilder, prompt_builder
from config.settings import LANGUAGES, AI

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Custom Exceptions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AnalysisError(Exception):
    """Base exception for all analysis failures."""


class ValidationError(AnalysisError):
    """Raised when user input fails validation."""


class AIServiceError(AnalysisError):
    """Raised when the AI backend fails to produce a response."""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AnalyzerService
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AnalyzerService:
    """Central coordinator for the code analysis workflow.

    Orchestrates the interaction between ``PromptBuilder`` (prompt
    creation) and ``OllamaClient`` (AI communication) without owning
    either responsibility.

    Args:
        prompt_builder: Instance of ``PromptBuilder`` used to
                        construct AI prompts.
        ollama_client:  Instance of ``OllamaClient`` used to send
                        prompts to the Ollama server.

    Example:
        >>> service = AnalyzerService(prompt_builder, ollama_client)
        >>> result = service.analyze_code("x = 1 + 2", "Python")
    """

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        ollama_client: OllamaClient,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._client = ollama_client

        logger.info("AnalyzerService initialised")

    # ─────────────────────────────────────────
    # Primary analysis method (V1)
    # ─────────────────────────────────────────

    def analyze_code(
        self,
        source_code: str,
        programming_language: str,
        model: str | None = None,
    ) -> str:
        """Perform a full code analysis (explain + bugs + correction).

        This is the primary method used by Version 1 of the
        application.  It validates input, builds a comprehensive
        prompt via ``PromptBuilder.build_full_analysis_prompt()``,
        sends it to Ollama, and returns the raw AI response.

        Args:
            source_code:          The user-supplied source code.
            programming_language: Display name of the language
                                  (e.g. ``"Python"``).
            model:                Optional model override.  If ``None``,
                                  the client's default model is used.

        Returns:
            str: The raw AI-generated analysis in Markdown format.

        Raises:
            ValidationError: If the input fails validation.
            AIServiceError:  If the AI backend fails.
        """
        start_time = time.monotonic()
        logger.info(
            "Analysis started  language=%s  code_length=%d  model=%s",
            programming_language,
            len(source_code),
            model or self._client.get_current_model(),
        )

        # 1. Validate
        self._validate_input(source_code, programming_language)
        logger.debug("Input validation passed")

        # 2. Build prompt
        prompt = self._prompt_builder.build_full_analysis_prompt(
            source_code=source_code,
            programming_language=programming_language,
        )
        logger.debug("Prompt generated  prompt_length=%d", len(prompt))

        # 3. Send to Ollama & receive response
        response = self._send_to_ollama(prompt, model)

        elapsed = time.monotonic() - start_time
        logger.info(
            "Analysis complete  language=%s  response_length=%d  "
            "elapsed=%.2fs",
            programming_language,
            len(response),
            elapsed,
        )

        return response

    # ─────────────────────────────────────────
    # Specialised analysis methods (future)
    # ─────────────────────────────────────────

    def explain_code(
        self,
        source_code: str,
        programming_language: str,
        model: str | None = None,
    ) -> str:
        """Generate a detailed explanation of the source code.

        Args:
            source_code:          The code to explain.
            programming_language: Language of the source code.
            model:                Optional model override.

        Returns:
            str: AI-generated explanation in Markdown.

        Raises:
            ValidationError: If input fails validation.
            AIServiceError:  If the AI backend fails.
        """
        logger.info("Explanation requested  language=%s", programming_language)
        self._validate_input(source_code, programming_language)

        prompt = self._prompt_builder.build_explanation_prompt(
            source_code=source_code,
            programming_language=programming_language,
        )
        return self._send_to_ollama(prompt, model)

    def detect_bugs(
        self,
        source_code: str,
        programming_language: str,
        model: str | None = None,
    ) -> str:
        """Detect bugs and issues in the source code.

        Args:
            source_code:          The code to analyse.
            programming_language: Language of the source code.
            model:                Optional model override.

        Returns:
            str: AI-generated bug report in Markdown.

        Raises:
            ValidationError: If input fails validation.
            AIServiceError:  If the AI backend fails.
        """
        logger.info("Bug detection requested  language=%s", programming_language)
        self._validate_input(source_code, programming_language)

        prompt = self._prompt_builder.build_bug_detection_prompt(
            source_code=source_code,
            programming_language=programming_language,
        )
        return self._send_to_ollama(prompt, model)

    def correct_code(
        self,
        source_code: str,
        programming_language: str,
        model: str | None = None,
    ) -> str:
        """Produce corrected source code.

        Args:
            source_code:          The code to correct.
            programming_language: Language of the source code.
            model:                Optional model override.

        Returns:
            str: AI-generated corrected code in Markdown.

        Raises:
            ValidationError: If input fails validation.
            AIServiceError:  If the AI backend fails.
        """
        logger.info("Code correction requested  language=%s", programming_language)
        self._validate_input(source_code, programming_language)

        prompt = self._prompt_builder.build_correction_prompt(
            source_code=source_code,
            programming_language=programming_language,
        )
        return self._send_to_ollama(prompt, model)

    # ─────────────────────────────────────────
    # Input validation
    # ─────────────────────────────────────────

    @staticmethod
    def _validate_input(
        source_code: str,
        programming_language: str,
    ) -> None:
        """Validate user-supplied inputs before processing.

        Checks:
            1. Source code is not empty or whitespace-only.
            2. Source code does not exceed the configured max length.
            3. Programming language is in the supported list.

        Args:
            source_code:          The code string to validate.
            programming_language: The language name to validate.

        Raises:
            ValidationError: With a descriptive message if any
                             check fails.
        """
        if not source_code or not source_code.strip():
            raise ValidationError(
                "Source code cannot be empty. "
                "Please paste your code and try again."
            )

        if len(source_code) > AI.max_code_length:
            raise ValidationError(
                f"Source code exceeds the maximum length of "
                f"{AI.max_code_length:,} characters "
                f"(received {len(source_code):,})."
            )

        if programming_language not in LANGUAGES.supported:
            supported = ", ".join(LANGUAGES.supported)
            raise ValidationError(
                f"Unsupported programming language: "
                f"'{programming_language}'. "
                f"Supported languages: {supported}."
            )

    # ─────────────────────────────────────────
    # Ollama communication wrapper
    # ─────────────────────────────────────────

    def _send_to_ollama(
        self,
        prompt: str,
        model: str | None = None,
    ) -> str:
        """Send a prompt to Ollama and return the response text.

        Wraps ``OllamaClient.generate()`` with unified error handling,
        converting all Ollama-specific exceptions into a single
        ``AIServiceError`` that upper layers can handle uniformly.

        Args:
            prompt: The fully-constructed prompt string.
            model:  Optional model override.

        Returns:
            str: The AI-generated response text.

        Raises:
            AIServiceError: If any Ollama interaction fails.
        """
        try:
            logger.debug("Sending prompt to Ollama  model=%s", model or "default")
            response = self._client.generate(prompt=prompt, model=model)
            logger.debug("Response received  length=%d", len(response))
            return response

        except OllamaConnectionError as exc:
            logger.error("Ollama connection failed: %s", exc)
            raise AIServiceError(
                "Cannot connect to the Ollama server. "
                "Please ensure Ollama is running and try again."
            ) from exc

        except OllamaTimeoutError as exc:
            logger.error("Ollama request timed out: %s", exc)
            raise AIServiceError(
                "The AI request timed out. "
                "The code may be too long or the model is still loading."
            ) from exc

        except OllamaModelNotFoundError as exc:
            logger.error("Ollama model not found: %s", exc)
            raise AIServiceError(
                "The requested AI model was not found. "
                "Please run `ollama pull <model>` to install it."
            ) from exc

        except OllamaAPIError as exc:
            logger.error("Ollama API error: %s", exc)
            raise AIServiceError(
                "An unexpected error occurred while communicating "
                "with the AI backend."
            ) from exc

        except Exception as exc:
            logger.exception("Unexpected error during analysis")
            raise AIServiceError(
                f"An unexpected error occurred: {exc}"
            ) from exc


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Module-Level Convenience Factory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_default_analyzer: AnalyzerService | None = None


def get_analyzer() -> AnalyzerService:
    """Return a module-level ``AnalyzerService`` singleton.

    The singleton is lazily created on first call using the default
    ``prompt_builder`` and ``get_client()`` instances from their
    respective modules.

    Returns:
        AnalyzerService: The shared analyzer instance.
    """
    global _default_analyzer  # noqa: PLW0603
    if _default_analyzer is None:
        _default_analyzer = AnalyzerService(
            prompt_builder=prompt_builder,
            ollama_client=get_client(),
        )
    return _default_analyzer
