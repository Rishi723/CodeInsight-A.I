"""
Centralized Application Configuration — config/settings.py

This module serves as the **single source of truth** for every
configurable value in the CodeInsight AI application.

Architecture:
    Configuration is organized into frozen dataclasses, each
    encapsulating one logical domain (Single Responsibility Principle).
    All classes are instantiated as module-level singletons so that
    any module can import them directly::

        from config.settings import APP, OLLAMA, THEME

Design Decisions:
    • ``@dataclass(frozen=True)`` — prevents accidental mutation
      at runtime, enforcing config immutability.
    • Type hints on every field — enables IDE autocompletion and
      static analysis with mypy / pyright.
    • Logical grouping — each class owns only its own concern,
      making it trivial to extend in future phases.
    • Placeholder sections (Logging, Auth, Database, API Keys, OCR)
      are defined but contain only default / sentinel values,
      ready for Phase 4+ implementation.

Naming Convention:
    • Class names  → PascalCase ending in ``Config``
    • Singletons   → UPPER_SNAKE_CASE (e.g. ``APP``, ``OLLAMA``)
    • Internal use → underscore prefix (e.g. ``_LANGUAGE_ACE_MAP``)

Usage:
    >>> from config.settings import APP
    >>> print(APP.name)        # "CodeInsight AI"
    >>> print(APP.version)     # "0.3.0"
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Application Metadata
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class AppConfig:
    """Core application identity and metadata.

    Attributes:
        name:        Human-readable product name.
        version:     Semantic version string (Major.Minor.Patch).
        description: One-line marketing tagline shown in the hero banner.
        author:      Primary author or organization.
        page_title:  Browser tab / window title for Streamlit.
        page_icon:   Emoji or path used as the Streamlit page favicon.
    """

    name: str = "CodeInsight AI"
    version: str = "0.3.0"
    description: str = (
        "Understand your code, detect bugs, and generate "
        "intelligent fixes — instantly."
    )
    author: str = "CodeInsight AI Team"
    page_title: str = "CodeInsight AI — Code Explainer & Debugger"
    page_icon: str = "🤖"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Streamlit Page Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class StreamlitConfig:
    """Streamlit-specific page and layout settings.

    These values are passed directly to ``st.set_page_config()``.

    Attributes:
        layout:               Page layout mode — "centered" or "wide".
        initial_sidebar_state: Sidebar visibility on first load.
    """

    layout: str = "centered"
    initial_sidebar_state: str = "expanded"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Ollama Connection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class OllamaConfig:
    """Connection parameters for the Ollama local LLM server.

    These will be consumed by ``ai/ollama_client.py`` in Phase 4.

    Attributes:
        base_url:        Root URL of the Ollama HTTP API.
        model:           Default model identifier to use for inference.
        request_timeout: Maximum seconds to wait for an API response.
    """

    base_url: str = "http://localhost:11434"
    model: str = "llama3"
    request_timeout: int = 120


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. AI Processing Limits
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class AIConfig:
    """Constraints applied to AI analysis requests.

    Attributes:
        max_code_length:     Maximum number of characters accepted
                             in the input source code.
        max_response_length: Maximum number of characters the AI
                             response may contain (soft limit).
    """

    max_code_length: int = 15_000
    max_response_length: int = 10_000


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. Programming Language Support
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class LanguageConfig:
    """Supported programming languages and their editor mappings.

    Attributes:
        supported:    Ordered list of language names shown in the UI dropdown.
        ace_mode_map: Mapping from display name → Ace editor mode identifier.
    """

    supported: tuple[str, ...] = (
        "Python",
        "C++",
        "Java",
        "JavaScript",
    )

    ace_mode_map: dict[str, str] = field(default_factory=lambda: {
        "Python": "python",
        "C++": "c_cpp",
        "Java": "java",
        "JavaScript": "javascript",
    })

    def get_ace_mode(self, language: str) -> str:
        """Return the Ace editor mode for the given language.

        Args:
            language: Display name of the programming language.

        Returns:
            str: The Ace mode string. Falls back to ``"python"``.
        """
        return self.ace_mode_map.get(language, "python")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. File Upload
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class FileConfig:
    """Settings for the file upload feature.

    Attributes:
        supported_extensions: File extensions accepted by the uploader.
        max_file_size_mb:     Maximum upload size in megabytes (future use).
    """

    supported_extensions: tuple[str, ...] = (
        "py", "cpp", "c", "h", "hpp",
        "java",
        "js", "ts",
        "txt",
    )
    max_file_size_mb: int = 5


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. Editor / Theme
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class ThemeConfig:
    """Visual design tokens and editor theme options.

    Attributes:
        primary_color:       Main brand colour (Indigo).
        secondary_color:     Accent colour (Purple).
        gradient_start:      Left / top stop of the hero gradient.
        gradient_mid:        Middle stop of the hero gradient.
        gradient_end:        Right / bottom stop of the hero gradient.
        card_radius_px:      Default border-radius for card components.
        spacing_unit_rem:    Base spacing unit used for padding / margin.
        editor_themes:       Available Ace editor theme identifiers.
        editor_theme_labels: Human-readable labels for each theme.
        default_editor_theme: Theme applied when the app first loads.
        editor_font_size:    Default font size (px) in the Ace editor.
        editor_height:       Default editor height (px).
    """

    primary_color: str = "#6366F1"
    secondary_color: str = "#A855F7"

    gradient_start: str = "#4F46E5"
    gradient_mid: str = "#7C3AED"
    gradient_end: str = "#A855F7"

    card_radius_px: int = 12
    spacing_unit_rem: float = 1.0

    editor_themes: tuple[str, ...] = (
        "monokai",
        "github",
        "tomorrow_night",
        "dracula",
    )

    editor_theme_labels: dict[str, str] = field(default_factory=lambda: {
        "monokai": "🌙 Monokai",
        "github": "☀️ GitHub",
        "tomorrow_night": "🌃 Tomorrow Night",
        "dracula": "🧛 Dracula",
    })

    default_editor_theme: str = "monokai"
    editor_font_size: int = 14
    editor_height: int = 380


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. Future Feature Placeholders
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class LoggingConfig:
    """Placeholder — logging configuration for future implementation.

    Attributes:
        level:    Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Path to the log file (None = stdout only).
        enabled:  Master toggle for file logging.
    """

    level: str = "INFO"
    log_file: str | None = None
    enabled: bool = False


@dataclass(frozen=True)
class AuthConfig:
    """Placeholder — authentication configuration for future implementation.

    Attributes:
        enabled:  Whether authentication is required.
        provider: Auth provider name (e.g. "local", "oauth2", "ldap").
        secret_key: Secret used for token signing (must be overridden).
    """

    enabled: bool = False
    provider: str = "local"
    secret_key: str = "CHANGE_ME_IN_PRODUCTION"


@dataclass(frozen=True)
class DatabaseConfig:
    """Placeholder — database configuration for future implementation.

    Attributes:
        enabled:    Whether a database connection is used.
        engine:     Database engine (e.g. "sqlite", "postgresql").
        connection: Connection string or DSN.
    """

    enabled: bool = False
    engine: str = "sqlite"
    connection: str = "sqlite:///codeinsight.db"


@dataclass(frozen=True)
class APIKeysConfig:
    """Placeholder — third-party API keys for future implementation.

    Attributes:
        openai_key:    OpenAI API key (for optional cloud fallback).
        github_token:  GitHub personal access token.
    """

    openai_key: str | None = None
    github_token: str | None = None


@dataclass(frozen=True)
class OCRConfig:
    """Placeholder — OCR configuration for future code-from-image feature.

    Attributes:
        enabled: Whether the OCR feature is active.
        engine:  OCR engine identifier (e.g. "tesseract", "easyocr").
    """

    enabled: bool = False
    engine: str = "tesseract"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Module-Level Singletons
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Import these directly in any module:
#     from config.settings import APP, OLLAMA, THEME

APP = AppConfig()
"""Application metadata singleton."""

STREAMLIT = StreamlitConfig()
"""Streamlit page configuration singleton."""

OLLAMA = OllamaConfig()
"""Ollama connection parameters singleton."""

AI = AIConfig()
"""AI processing limits singleton."""

LANGUAGES = LanguageConfig()
"""Programming language support singleton."""

FILE = FileConfig()
"""File upload settings singleton."""

THEME = ThemeConfig()
"""Visual design tokens and editor options singleton."""

LOGGING = LoggingConfig()
"""Logging configuration singleton (placeholder)."""

AUTH = AuthConfig()
"""Authentication configuration singleton (placeholder)."""

DATABASE = DatabaseConfig()
"""Database configuration singleton (placeholder)."""

API_KEYS = APIKeysConfig()
"""Third-party API keys singleton (placeholder)."""

OCR = OCRConfig()
"""OCR configuration singleton (placeholder)."""
