"""
Programming Language Validation — services/language_detector.py

A lightweight, fully deterministic pre-analysis check that detects the
programming language of pasted source code using syntax heuristics, and
compares it against the language the user selected in the UI.

This module intentionally does **not** call any AI model. It exists to
catch an obvious, common user mistake (pasting Java into a Python-selected
editor, for example) *before* the expensive/slow ``AnalyzerService`` call
is made.

Architecture:
    • ``LanguageSignal``           — one weighted regex heuristic.
    • ``_LANGUAGE_SIGNATURES``     — registry mapping language name →
                                     list of signals. This is the single
                                     place that encodes "what does this
                                     language look like".
    • ``detect_language()``        — scores every registered language
                                     against the pasted code and returns
                                     the best guess + confidence.
    • ``validate_language()``      — the public entry point used by
                                     ``app.py``. Wraps ``detect_language``
                                     and produces a structured, UI-ready
                                     ``LanguageDetectionResult``.

Design Decisions:
    • Deterministic regex/keyword scoring was chosen over an AI or
      statistical (e.g. n-gram model) approach because it is:
        - instant (sub-millisecond for typical inputs),
        - dependency-free and offline,
        - fully explainable ("Java detected because of `public static
          void main` and `System.out.println`"),
        - trivially testable and extensible.
      A ML/AI classifier would add latency, a dependency, and
      non-determinism for a problem that simple syntax fingerprinting
      already solves well for the small, fixed set of languages this
      app supports.
    • Language support is data-driven (``_LANGUAGE_SIGNATURES`` is a
      plain dict). Adding a new language requires no changes to the
      scoring/decision logic — just a new registry entry (see
      ``register_language`` below) plus adding the language name to
      ``config.settings.LanguageConfig.supported``.
    • The result is a frozen dataclass so the UI layer can render it
      without re-deriving any decision logic (keeps ``ui/components.py``
      purely presentational, consistent with the rest of the app).

Usage:
    >>> from services.language_detector import validate_language
    >>> result = validate_language(code, "Python")
    >>> result.status          # DetectionStatus.MATCH / MISMATCH / UNCERTAIN
    >>> result.message         # human-readable explanation for the UI
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Pattern

from config.settings import LANGUAGES


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Result Types
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DetectionStatus(str, Enum):
    """Outcome category of a language validation check."""

    MATCH = "match"
    MISMATCH = "mismatch"
    UNCERTAIN = "uncertain"


@dataclass(frozen=True)
class LanguageDetectionResult:
    """Structured, UI-ready outcome of a language validation check.

    Attributes:
        detected_language: Best-guess language name, or ``None`` if no
            language could be confidently identified at all.
        selected_language: The language the user chose in the dropdown.
        confidence:        Share of total syntax "evidence" that pointed
                            to ``detected_language``, in ``[0.0, 1.0]``.
                            ``0.0`` when nothing was detected.
        status:             ``MATCH``, ``MISMATCH``, or ``UNCERTAIN``.
        is_match:           Convenience bool — ``True`` only when
                             ``status is DetectionStatus.MATCH``.
        message:            Human-readable explanation, ready to display.
        scores:             Raw per-language heuristic scores (debugging /
                             future UI use, e.g. a confidence breakdown).
    """

    detected_language: str | None
    selected_language: str
    confidence: float
    status: DetectionStatus
    is_match: bool
    message: str
    scores: dict[str, float] = field(default_factory=dict)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Heuristic Signals
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class LanguageSignal:
    """A single weighted syntax fingerprint for one language.

    Attributes:
        pattern:     Compiled regex tested against the raw source code.
        weight:      Contribution to that language's score if the
                     pattern matches at least once (matches are counted
                     once each, regardless of how many times they occur,
                     so a single repeated token can't dominate the score).
        description: Short human label, useful for debugging/logging.
    """

    pattern: Pattern[str]
    weight: float
    description: str = ""


def _compile(patterns: list[tuple[str, float, str]]) -> list[LanguageSignal]:
    """Compile a list of (regex, weight, description) tuples into signals."""
    return [
        LanguageSignal(re.compile(p, re.MULTILINE), w, d)
        for p, w, d in patterns
    ]


# Registry: language display name → ordered list of syntax signals.
#
# Keys must match the display names used in
# ``config.settings.LanguageConfig.supported`` so the detector and the
# language dropdown stay in sync.
_LANGUAGE_SIGNATURES: dict[str, list[LanguageSignal]] = {
    "Python": _compile([
        (r"^\s*def\s+\w+\s*\(.*\)\s*:", 2.0, "def function signature"),
        (r"^\s*class\s+\w+.*:\s*$", 1.5, "class ... : (no braces)"),
        (r"^\s*(from\s+[\w.]+\s+import\s+|import\s+\w+)", 1.5, "import statement"),
        (r"^\s*elif\b", 1.5, "elif keyword"),
        (r"^\s*except\b.*:", 1.0, "except clause"),
        (r"\bself\b", 1.0, "self reference"),
        (r"^\s*#", 0.5, "hash comment"),
        (r"\bprint\s*\(", 0.75, "print() call"),
        (r"f[\"'][^\"']*\{[^}]*\}", 1.0, "f-string interpolation"),
        (r"__init__|__main__", 1.5, "python dunder name"),
        (r":\s*$", 0.4, "trailing colon block opener"),
        (r"\blambda\b", 1.0, "lambda expression"),
    ]),
    "C++": _compile([
        (r"#include\s*[<\"][\w./]+[>\"]", 2.5, "#include directive"),
        (r"\bstd::", 2.0, "std:: namespace"),
        (r"\bcout\s*<<|\bcin\s*>>", 2.0, "cout/cin stream operator"),
        (r"\bint\s+main\s*\(", 2.0, "int main() entry point"),
        (r"\busing\s+namespace\s+std\s*;", 1.5, "using namespace std;"),
        (r"\btemplate\s*<", 1.0, "template<...>"),
        (r"\bnullptr\b", 1.0, "nullptr"),
        (r"^\s*(public|private|protected)\s*:", 1.0, "access specifier label"),
        (r"->", 0.5, "pointer member access"),
        (r";\s*$", 0.3, "semicolon statement terminator"),
    ]),
    "Java": _compile([
        (r"\bpublic\s+class\s+\w+", 2.5, "public class declaration"),
        (r"\bpublic\s+static\s+void\s+main\s*\(\s*String", 2.5, "main(String[]) signature"),
        (r"\bSystem\.out\.println\s*\(", 2.0, "System.out.println()"),
        (r"^\s*import\s+java\.", 2.0, "java.* import"),
        (r"\bextends\b|\bimplements\b", 1.0, "extends/implements"),
        (r"@Override\b", 1.0, "@Override annotation"),
        (r"^\s*package\s+[\w.]+\s*;", 1.5, "package statement"),
        (r"\bnew\s+\w+\s*(<[^>]*>)?\s*\(", 0.5, "object instantiation"),
        (r";\s*$", 0.3, "semicolon statement terminator"),
    ]),
    "JavaScript": _compile([
        (r"\bconsole\.log\s*\(", 2.0, "console.log()"),
        (r"\b(const|let|var)\s+\w+\s*=", 1.25, "variable declaration"),
        (r"=>", 1.5, "arrow function"),
        (r"\bfunction\s*\w*\s*\(", 1.0, "function keyword"),
        (r"\brequire\s*\(", 1.5, "CommonJS require()"),
        (r"\bmodule\.exports\b", 1.5, "CommonJS module.exports"),
        (r"^\s*export\s+(default\s+)?", 1.0, "ES module export"),
        (r"^\s*import\s+.*\s+from\s+[\"']", 1.5, "ES module import"),
        (r"\bdocument\.|\bwindow\.", 1.0, "browser DOM global"),
        (r"`[^`]*\$\{[^}]*\}", 1.0, "template literal interpolation"),
    ]),
}


def register_language(name: str, patterns: list[tuple[str, float, str]]) -> None:
    """Register (or override) syntax heuristics for a language.

    This is the extension point for future languages: add an entry here
    (and to ``config.settings.LanguageConfig.supported``) and the
    scoring/decision logic in ``detect_language`` / ``validate_language``
    picks it up automatically — no other code needs to change.

    Args:
        name:     Display name, must match the dropdown's language name.
        patterns: List of ``(regex, weight, description)`` tuples.
    """
    _LANGUAGE_SIGNATURES[name] = _compile(patterns)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Scoring & Detection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Minimum raw score a language needs before it can be considered
# "detected" at all. Filters out near-empty or ambiguous snippets that
# happen to trip a single weak signal.
_MIN_SIGNAL_SCORE = 2.0

# Minimum share of total evidence the winning language needs to be
# reported as a *confident* detection rather than "uncertain".
_HIGH_CONFIDENCE_RATIO = 0.6


def _score_language(code: str, signals: list[LanguageSignal]) -> float:
    """Sum the weights of every signal that matches at least once."""
    return sum(signal.weight for signal in signals if signal.pattern.search(code))


def _compute_scores(code: str) -> dict[str, float]:
    """Score ``code`` against every language currently offered by the UI."""
    return {
        lang: _score_language(code, signals)
        for lang, signals in _LANGUAGE_SIGNATURES.items()
        if lang in LANGUAGES.supported
    }


def detect_language(code: str) -> tuple[str | None, float, dict[str, float]]:
    """Detect the most likely programming language of a code snippet.

    Deterministic and dependency-free: every supported language is
    scored via weighted regex heuristics, and the highest-scoring
    language wins provided it clears a minimum absolute score.

    Args:
        code: Raw source code pasted into the editor.

    Returns:
        A 3-tuple of ``(best_language_or_None, confidence, raw_scores)``
        where ``confidence`` is the winning language's share of total
        evidence (``0.0`` when nothing was confidently detected).
    """
    if not code or not code.strip():
        return None, 0.0, {}

    scores = _compute_scores(code)
    total = sum(scores.values())
    if total <= 0:
        return None, 0.0, scores

    best_lang, best_score = max(scores.items(), key=lambda kv: kv[1])

    if best_score < _MIN_SIGNAL_SCORE:
        return None, 0.0, scores

    confidence = round(best_score / total, 2)
    return best_lang, confidence, scores


def validate_language(code: str, selected_language: str) -> LanguageDetectionResult:
    """Validate pasted code against the user's selected language.

    This is the public entry point ``app.py`` calls before invoking
    ``AnalyzerService``. It never raises for malformed/empty input —
    it degrades to an ``UNCERTAIN`` result instead, so the caller can
    always safely render ``result.message``.

    Args:
        code:               Source code from the editor.
        selected_language:  Language chosen in the UI dropdown.

    Returns:
        LanguageDetectionResult: structured, UI-ready outcome.
    """
    detected, confidence, scores = detect_language(code)

    # Case 1: nothing could be confidently detected at all.
    if detected is None:
        return LanguageDetectionResult(
            detected_language=None,
            selected_language=selected_language,
            confidence=confidence,
            status=DetectionStatus.UNCERTAIN,
            is_match=False,
            message=(
                "⚠️ We couldn't confidently detect a programming language from "
                "the pasted code. Please verify that "
                f"**{selected_language}** is the correct selection before analysing."
            ),
            scores=scores,
        )

    # Case 2: a language was detected, but the signal is weak.
    if confidence < _HIGH_CONFIDENCE_RATIO:
        return LanguageDetectionResult(
            detected_language=detected,
            selected_language=selected_language,
            confidence=confidence,
            status=DetectionStatus.UNCERTAIN,
            is_match=(detected == selected_language),
            message=(
                f"⚠️ The code looks like it might be **{detected}**, but the "
                f"signal is weak ({confidence:.0%} confidence). Please verify "
                f"that **{selected_language}** is the correct selection before "
                "analysing."
            ),
            scores=scores,
        )

    # Case 3: confident detection — either a clean match or a real mismatch.
    is_match = detected == selected_language
    if is_match:
        return LanguageDetectionResult(
            detected_language=detected,
            selected_language=selected_language,
            confidence=confidence,
            status=DetectionStatus.MATCH,
            is_match=True,
            message=(
                f"✅ Detected language matches your selection "
                f"(**{selected_language}**, {confidence:.0%} confidence)."
            ),
            scores=scores,
        )

    return LanguageDetectionResult(
        detected_language=detected,
        selected_language=selected_language,
        confidence=confidence,
        status=DetectionStatus.MISMATCH,
        is_match=False,
        message=(
            f"🔴 The pasted code appears to be **{detected}** "
            f"({confidence:.0%} confidence), but **{selected_language}** is "
            f"currently selected. Please switch the language selector to "
            f"**{detected}**, or paste code that matches **{selected_language}**, "
            "before analysing."
        ),
        scores=scores,
    )