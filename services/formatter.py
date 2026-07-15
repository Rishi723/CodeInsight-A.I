"""
Response Formatter — services/formatter.py

Converts raw AI Markdown responses into structured ``AnalysisResult``
objects that the UI can consume directly.

This module is the **only** place that parses AI output.  It sits
between the ``AnalyzerService`` (which returns raw text) and the
Streamlit UI (which needs discrete fields).

Responsibilities:
    • Parse a Markdown response into three sections:
      explanation, bugs, and corrected code.
    • Handle missing or malformed sections gracefully.
    • Provide a clean dataclass (``AnalysisResult``) as the
      contract between the backend and the UI.

Non-responsibilities (kept in other modules):
    • Prompt construction       → ai/prompts.py
    • HTTP / Ollama transport   → ai/ollama_client.py
    • Workflow orchestration    → services/analyzer.py
    • UI rendering              → ui/components.py

Architecture notes:
    ``ResponseFormatter`` uses regex-based section splitting that
    tolerates common LLM formatting quirks (extra whitespace,
    inconsistent heading levels, missing sections).  The parser is
    intentionally lenient — it extracts what it can and fills
    remaining fields with safe defaults.

    Future response formats (JSON, XML, streaming chunks) can be
    supported by adding a new formatter class that produces the
    same ``AnalysisResult`` dataclass.

Usage:
    >>> from services.formatter import ResponseFormatter
    >>> formatter = ResponseFormatter()
    >>> result = formatter.format_response(raw_ai_text, "llama3", "Python")
    >>> print(result.explanation)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AnalysisResult dataclass
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class AnalysisResult:
    """Structured container for a parsed AI analysis response.

    This dataclass is the **contract** between the backend and the
    UI layer.  The UI never reads raw Markdown — it consumes these
    typed fields instead.

    Attributes:
        explanation:    Parsed "Code Explanation" section.
        bugs:           Parsed "Bugs Found" section.
        corrected_code: Parsed "Corrected Code" section (code only,
                        without the fenced block markers).
        raw_response:   The original, unmodified AI response text.
        success:        ``True`` if the response was parsed without
                        critical errors.
        model:          The Ollama model that produced the response.
        language:       The programming language of the analysed code.
    """

    explanation: str = ""
    bugs: str = ""
    corrected_code: str = ""
    raw_response: str = ""
    success: bool = True
    model: str | None = None
    language: str | None = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ResponseFormatter
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ResponseFormatter:
    """Parses raw AI Markdown into an ``AnalysisResult``.

    The parser is **lenient by design** — LLMs do not always produce
    perfectly formatted output.  Missing sections are filled with
    human-readable defaults rather than raising exceptions.

    Section detection:
        The formatter looks for Markdown headings that match
        (case-insensitive) ``Code Explanation``, ``Bugs Found``,
        and ``Corrected Code``.  Both ``#`` and ``##`` levels are
        accepted.

    Example:
        >>> fmt = ResponseFormatter()
        >>> result = fmt.format_response(raw_text)
        >>> result.explanation   # str
        >>> result.bugs          # str
        >>> result.corrected_code  # str (code only)
    """

    # Regex patterns for section heading detection.
    # Accept 1–3 leading hashes, optional emoji, flexible spacing.
    _HEADING_EXPLANATION = re.compile(
        r"^#{1,3}\s*(?:📖\s*)?Code\s+Explanation\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    _HEADING_BUGS = re.compile(
        r"^#{1,3}\s*(?:🐞\s*)?Bugs?\s+Found\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    _HEADING_CORRECTED = re.compile(
        r"^#{1,3}\s*(?:✅\s*)?Corrected\s+Code\s*$",
        re.IGNORECASE | re.MULTILINE,
    )

    # Matches a fenced code block: ```lang\n...\n```
    _CODE_BLOCK = re.compile(
        r"```[\w+#]*\s*\n(.*?)```",
        re.DOTALL,
    )

    # ─────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────

    def format_response(
        self,
        raw_response: str,
        model: str | None = None,
        language: str | None = None,
    ) -> AnalysisResult:
        """Parse a raw AI response into a structured ``AnalysisResult``.

        Workflow:
            1. Guard against empty / ``None`` input.
            2. Split the response into sections by heading.
            3. Extract the code explanation text.
            4. Extract the bugs-found text.
            5. Extract the corrected code (stripped of fence markers).
            6. Package everything into ``AnalysisResult``.

        Args:
            raw_response: The full Markdown string returned by the AI.
            model:        The model name (metadata, passed through).
            language:     The programming language (metadata).

        Returns:
            AnalysisResult: A populated result object.  ``success``
            is ``True`` even when some sections are missing — it is
            ``False`` only if the entire response is empty.
        """
        logger.info(
            "Formatting response  length=%d  model=%s  language=%s",
            len(raw_response) if raw_response else 0,
            model,
            language,
        )

        # Guard: empty response
        if not raw_response or not raw_response.strip():
            logger.warning("Received empty AI response")
            return AnalysisResult(
                raw_response=raw_response or "",
                success=False,
                model=model,
                language=language,
                explanation="No response received from the AI model.",
                bugs="No response received.",
                corrected_code="",
            )

        # Split into sections
        sections = self._split_sections(raw_response)

        explanation = self._clean(sections.get("explanation", ""))
        bugs = self._clean(sections.get("bugs", ""))
        corrected_raw = sections.get("corrected_code", "")
        corrected_code = self._extract_code(corrected_raw)

        # Fill defaults for missing sections
        if not explanation:
            explanation = "Explanation not available."
            logger.debug("Explanation section missing — using default")

        if not bugs:
            bugs = "Bug analysis not available."
            logger.debug("Bugs section missing — using default")

        if not corrected_code:
            corrected_code = ""
            logger.debug("Corrected code section missing or empty")

        logger.info(
            "Formatting complete  explanation=%d chars  bugs=%d chars  "
            "corrected_code=%d chars",
            len(explanation),
            len(bugs),
            len(corrected_code),
        )

        return AnalysisResult(
            explanation=explanation,
            bugs=bugs,
            corrected_code=corrected_code,
            raw_response=raw_response,
            success=True,
            model=model,
            language=language,
        )

    # ─────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────

    def _split_sections(
        self,
        text: str,
    ) -> dict[str, str]:
        """Split the Markdown response into named sections.

        Uses the compiled heading regexes to locate each section
        boundary.  Text between two headings belongs to the first
        heading.

        Args:
            text: The full Markdown response.

        Returns:
            dict: Keys are ``"explanation"``, ``"bugs"``, and
                  ``"corrected_code"``.  Missing keys mean the
                  section was not found.
        """
        # Find all section starts: (name, start_index)
        anchors: list[tuple[str, int]] = []

        for match in self._HEADING_EXPLANATION.finditer(text):
            anchors.append(("explanation", match.end()))

        for match in self._HEADING_BUGS.finditer(text):
            anchors.append(("bugs", match.end()))

        for match in self._HEADING_CORRECTED.finditer(text):
            anchors.append(("corrected_code", match.end()))

        # Sort by position in the text
        anchors.sort(key=lambda a: a[1])

        # Extract content between consecutive anchors
        sections: dict[str, str] = {}
        for i, (name, start) in enumerate(anchors):
            end = anchors[i + 1][1] if i + 1 < len(anchors) else len(text)

            # When there's a next anchor, trim back to the start of its
            # heading line (walk backwards past the heading text).
            if i + 1 < len(anchors):
                next_start = anchors[i + 1][1]
                # Find the beginning of the heading line
                line_start = text.rfind("\n", 0, next_start)
                if line_start == -1:
                    line_start = 0
                end = line_start

            sections[name] = text[start:end]

        # Fallback: if no sections detected, treat entire text as
        # the explanation (common with simpler models).
        if not sections:
            logger.debug(
                "No section headings detected — treating entire "
                "response as explanation"
            )
            sections["explanation"] = text

        return sections

    @staticmethod
    def _extract_code(text: str) -> str:
        """Extract code from a fenced Markdown code block.

        If a fenced block (````` ``` ```) is found, return its inner
        content.  Otherwise return the raw text stripped of
        whitespace (handles models that omit fences).

        Args:
            text: Text that may contain a fenced code block.

        Returns:
            str: The extracted code, or an empty string.
        """
        if not text:
            return ""

        match = re.search(
            r"```[\w+#]*\s*\n(.*?)```",
            text,
            re.DOTALL,
        )
        if match:
            return match.group(1).strip()

        # Fallback: return cleaned text if no fences found
        cleaned = text.strip()
        return cleaned if cleaned else ""

    @staticmethod
    def _clean(text: str) -> str:
        """Remove excessive whitespace while preserving structure.

        Strips leading/trailing whitespace and collapses runs of
        more than two consecutive newlines into two.

        Args:
            text: Raw section text.

        Returns:
            str: Cleaned text.
        """
        if not text:
            return ""
        text = text.strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Module-Level Convenience Singleton
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

response_formatter = ResponseFormatter()
"""Module-level singleton for convenient imports.

Usage:
    >>> from services.formatter import response_formatter
    >>> result = response_formatter.format_response(raw_text)
"""
