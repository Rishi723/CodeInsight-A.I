"""
CodeInsight AI — Main Application Entry Point

This module serves as the **presentation layer** for the CodeInsight AI
Streamlit application.  It wires together the existing UI components,
the ``AnalyzerService`` orchestrator, and the ``ResponseFormatter`` to
deliver a complete end-to-end code analysis experience.

Responsibilities:
    • Configure the Streamlit page and session state.
    • Compose the UI from reusable components.
    • Trigger the analysis workflow on user action.
    • Display formatted results or user-friendly errors.

Non-responsibilities (delegated to other modules):
    • Prompt construction     → ai/prompts.py
    • HTTP / Ollama transport → ai/ollama_client.py
    • Workflow orchestration  → services/analyzer.py
    • Response parsing        → services/formatter.py

Usage:
    streamlit run app.py
"""

import logging

import streamlit as st
from streamlit_ace import st_ace

from config.settings import APP, STREAMLIT, LANGUAGES, OLLAMA
from ui.styles import get_global_styles
from ui.components import (
    render_sidebar,
    render_loading_placeholder,
    render_footer,
    render_home_page,
    render_documentation_page,
    render_about_project_page,
    render_settings_page,
    render_language_validation_message,
)
from services.analyzer import get_analyzer, ValidationError, AIServiceError
from services.formatter import response_formatter, AnalysisResult
from services.language_detector import validate_language, DetectionStatus

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Page & Session Configuration
# ─────────────────────────────────────────────

def _configure_page() -> None:
    """Set Streamlit page metadata from centralised config."""
    st.set_page_config(
        page_title=APP.page_title,
        page_icon=APP.page_icon,
        layout=STREAMLIT.layout,
        initial_sidebar_state=STREAMLIT.initial_sidebar_state,
    )


def _init_session_state() -> None:
    """Initialise session state variables with safe defaults."""
    defaults: dict = {
        "editor_code": "",
        "show_uploader": False,
        "analysis_result": None,
        "analysis_error": None,
        "language_validation": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ─────────────────────────────────────────────
# Analysis Workflow
# ─────────────────────────────────────────────

def _run_analysis(code: str, language: str) -> None:
    """Execute the full analysis pipeline and store results in session state.

    Workflow:
        1. Call ``AnalyzerService.analyze_code()`` → raw response.
        2. Call ``ResponseFormatter.format_response()`` → ``AnalysisResult``.
        3. Store the result (or error) in ``st.session_state``.

    Args:
        code:     The source code to analyse.
        language: The programming language name.
    """
    analyzer = get_analyzer()

    try:
        logger.info("Analysis triggered  language=%s  code_length=%d", language, len(code))

        raw_response: str = analyzer.analyze_code(
            source_code=code,
            programming_language=language,
        )
       

        result: AnalysisResult = response_formatter.format_response(
            raw_response=raw_response,
            model=OLLAMA.model,
            language=language,
        )

        st.session_state["analysis_result"] = result
        st.session_state["analysis_error"] = None

        logger.info("Analysis completed successfully")

    except ValidationError as exc:
        logger.warning("Validation failed: %s", exc)
        st.session_state["analysis_result"] = None
        st.session_state["analysis_error"] = f"⚠️ {exc}"

    except AIServiceError as exc:
        logger.error("AI service error: %s", exc)
        st.session_state["analysis_result"] = None
        st.session_state["analysis_error"] = f"🔴 {exc}"

    except Exception:
        logger.exception("Unexpected error during analysis")
        st.session_state["analysis_result"] = None
        st.session_state["analysis_error"] = (
            "❌ An unexpected error occurred. Please try again."
        )


# ─────────────────────────────────────────────
# Result Display
# ─────────────────────────────────────────────

def _render_analysis_results(result: AnalysisResult, language: str, theme: str) -> None:
    """Render the parsed AnalysisResult in expandable cards.

    Args:
        result:   The formatted analysis result.
        language: Programming language (for the corrected code editor).
        theme:    Ace editor theme key.
    """
    
    # Section header
    st.markdown(
        """
        <div class="result-section-header animate-in">
            <span class="section-icon">📊</span>
            <span class="section-label">Analysis Results</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Metadata badge bar
    meta_html_parts: list[str] = []
    if result.model:
        meta_html_parts.append(
            f'<span class="meta-item">🤖 <span class="meta-value">{result.model}</span></span>'
        )
    if result.language:
        if meta_html_parts:
            meta_html_parts.append('<span class="meta-divider"></span>')
        meta_html_parts.append(
            f'<span class="meta-item">🌐 <span class="meta-value">{result.language}</span></span>'
        )

    if meta_html_parts:
        st.markdown(
            f'<div class="analysis-meta animate-in">{"".join(meta_html_parts)}</div>',
            unsafe_allow_html=True,
        )

    # ── Card 1: Code Explanation ──
    with st.expander("📖  Code Explanation", expanded=True):
        if result.explanation:
            st.markdown(result.explanation)
            
        else:
            st.info("No explanation available.")

    # ── Card 2: Bugs Found ──
    with st.expander("🐞  Bugs Found", expanded=True):
        if result.bugs:
            if "no bugs detected" in result.bugs.lower():
                st.success("✅ No bugs detected — your code looks clean!")
            else:
                st.markdown(result.bugs)
        else:
            st.info("No bug analysis available.")

    # ── Card 3: Corrected Code (read-only Ace editor) ──
    with st.expander("✅  Corrected Code", expanded=True):
        if result.corrected_code:
            ace_mode: str = LANGUAGES.get_ace_mode(language)

            st_ace(
                value=result.corrected_code,
                language=ace_mode,
                theme=theme,
                height=300,
                font_size=13,
                readonly=True,
                show_gutter=True,
                show_print_margin=False,
                wrap=True,
                auto_update=True,
                key="ace_corrected_result",
            )
        else:
            st.info("No corrected code available — the original code may already be correct.")

    # — New Analysis button —
    st.markdown('<div class="new-analysis-container">', unsafe_allow_html=True)
    if st.button("🔄  New Analysis", key="btn_new_analysis", use_container_width=True):
        st.session_state["analysis_result"] = None
        st.session_state["analysis_error"] = None
        st.session_state["language_validation"] = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Main Application
# ─────────────────────────────────────────────

def main() -> None:
    """Assemble and render the complete CodeInsight AI interface.

    Layout:
        1. Page configuration & session state
        2. Global CSS
        3. Sidebar
        4. Hero header
        5. Editor toolbar (language + theme selectors)
        6. Ace code editor
        7. Editor statistics
        8. Utility buttons (Clear / Sample / Upload / Analyze)
        9. Analysis results or placeholder
        10. Footer
    """
    # — Page config (must be first Streamlit call) —
    _configure_page()

    # — Session state —
    _init_session_state()

    # — Log startup once per session —
    if not st.session_state.get("startup_logged", False):
        logger.info("Starting CodeInsight AI frontend app version %s", APP.version)
        st.session_state["startup_logged"] = True

    # — Inject global CSS —
    st.markdown(get_global_styles(), unsafe_allow_html=True)

    # — Sidebar —
    selected_page = render_sidebar()

    if selected_page == "Home":
        # — Main content —
        code, language, theme, analyze_clicked = render_home_page()

        # — Handle analysis trigger —
        if analyze_clicked:
            if not code or not code.strip():
                st.warning(
                    "⚠️ Please paste your source code before analysing."
                )
            else:
                # — Language validation gate (runs before AnalyzerService) —
                validation_result = validate_language(code, language)
                st.session_state["language_validation"] = {
                    "code": code,
                    "language": language,
                    "result": validation_result,
                }

                if validation_result.status == DetectionStatus.MISMATCH:
                    # Block analysis — clear any stale results so the
                    # validation message is the only thing shown below.
                    st.session_state["analysis_result"] = None
                    st.session_state["analysis_error"] = None
                else:
                    # MATCH or UNCERTAIN (low-confidence) — proceed, the
                    # UNCERTAIN case is a non-blocking heads-up only.
                    with st.spinner("🤖 Analysing your code... Please wait."):
                        _run_analysis(code, language)

        # — Resolve the validation state for the *current* code/language —
        # (self-invalidates automatically if the user edits the code or
        # switches languages after a previous check, so stale messages
        # never linger)
        validation_state = st.session_state.get("language_validation")
        validation_result = None
        if (
            validation_state is not None
            and validation_state["code"] == code
            and validation_state["language"] == language
        ):
            validation_result = validation_state["result"]

        if validation_result is not None:
            render_language_validation_message(validation_result)

        # — Display results, error, or placeholder —
        error_msg = st.session_state.get("analysis_error")
        result = st.session_state.get("analysis_result")

        if validation_result is not None and validation_result.status == DetectionStatus.MISMATCH:
            # Analysis was blocked — the error above already explains why.
            pass
        elif error_msg:
            st.error(error_msg)
        elif isinstance(result, AnalysisResult):
            if not result.success:
                st.error("⚠️ The AI backend returned an empty response. Please try again.")
            else:
                _render_analysis_results(result, language, theme)
        else:
            render_loading_placeholder()

    elif selected_page == "Documentation":
        render_documentation_page()

    elif selected_page == "About Project":
        render_about_project_page()

    elif selected_page == "Settings":
        render_settings_page()

    # — Footer —
    render_footer()


if __name__ == "__main__":
    main()