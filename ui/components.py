"""
UI Components — Production Edition

Reusable Streamlit UI components for the CodeInsight AI application.

This module follows the Single Responsibility Principle — each function
renders exactly one visual section of the interface. Components are
purely presentational and contain no business logic.

Components:
    - render_sidebar:             Sidebar with live Ollama status
    - render_hero_header:         Gradient hero banner
    - render_editor_toolbar:      Language + theme selectors
    - render_code_editor:         Ace code editor with syntax highlighting
    - render_editor_stats:        Live line / char / language stats
    - render_utility_buttons:     Clear, Sample, Upload buttons
    - render_analyze_button:      Primary analyze CTA
    - render_loading_placeholder: Welcome state before analysis
    - render_footer:              Bottom attribution bar
"""

from __future__ import annotations

import streamlit as st
from streamlit_ace import st_ace

from config.settings import APP, LANGUAGES, THEME, FILE
from services.language_detector import DetectionStatus, LanguageDetectionResult


# ─────────────────────────────────────────────
# Constants & Mappings
# ─────────────────────────────────────────────

SUPPORTED_LANGUAGES: list[str] = list(LANGUAGES.supported)

_LANGUAGE_TO_ACE_MODE: dict[str, str] = dict(LANGUAGES.ace_mode_map)

EDITOR_THEMES: list[str] = list(THEME.editor_themes)

_THEME_DISPLAY_NAMES: dict[str, str] = dict(THEME.editor_theme_labels)

_SAMPLE_CODE: dict[str, str] = {
    "Python": '''def fibonacci(n: int) -> list[int]:
    """Return the first n Fibonacci numbers."""
    if n <= 0:
        return []
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]


if __name__ == "__main__":
    result = fibonacci(10)
    print(f"Fibonacci: {result}")
''',
    "C++": '''#include <iostream>
#include <vector>

std::vector<int> fibonacci(int n) {
    std::vector<int> seq;
    if (n <= 0) return seq;
    seq.push_back(0);
    if (n == 1) return seq;
    seq.push_back(1);
    for (int i = 2; i < n; i++) {
        seq.push_back(seq[i-1] + seq[i-2]);
    }
    return seq;
}

int main() {
    auto result = fibonacci(10);
    for (int val : result) {
        std::cout << val << " ";
    }
    return 0;
}
''',
    "Java": '''import java.util.ArrayList;
import java.util.List;

public class Fibonacci {
    public static List<Integer> fibonacci(int n) {
        List<Integer> seq = new ArrayList<>();
        if (n <= 0) return seq;
        seq.add(0);
        if (n == 1) return seq;
        seq.add(1);
        for (int i = 2; i < n; i++) {
            seq.add(seq.get(i-1) + seq.get(i-2));
        }
        return seq;
    }

    public static void main(String[] args) {
        List<Integer> result = fibonacci(10);
        System.out.println(result);
    }
}
''',
    "JavaScript": '''function fibonacci(n) {
    if (n <= 0) return [];
    const seq = [0, 1];
    while (seq.length < n) {
        seq.push(seq[seq.length - 1] + seq[seq.length - 2]);
    }
    return seq.slice(0, n);
}

// Run
const result = fibonacci(10);
console.log("Fibonacci:", result);
''',
}


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────

def render_sidebar() -> str:
    """Render the sidebar with branding, navigation, live status, and info.

    Includes:
        - Brand logo area
        - Navigation links (functional)
        - Live Ollama connection status
        - Project info with version from config

    Returns:
        str: The currently selected page name.
    """
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Home"

    with st.sidebar:
        # — Brand —
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-logo">🤖</div>
                <div class="brand-name">CodeInsight AI</div>
                <div class="brand-tagline">Intelligent Code Analysis</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # — Navigation —
        st.markdown(
            '<p class="sidebar-section-label">Navigation</p>',
            unsafe_allow_html=True,
        )

        nav_items = [
            ("Home", "🏠"),
            ("Documentation", "📘"),
            ("About Project", "ℹ️"),
            ("Settings", "⚙️"),
        ]

        for label, icon in nav_items:
            is_active = st.session_state["current_page"] == label
            active_class = "active-nav" if is_active else ""
            
            st.markdown(f'<div class="sidebar-nav-btn-wrapper {active_class}">', unsafe_allow_html=True)
            if st.button(
                f"{icon}  {label}", 
                key=f"btn_nav_{label.lower().replace(' ', '_')}", 
                use_container_width=True
            ):
                st.session_state["current_page"] = label
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # — Divider —
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        # — System Status (live Ollama check) —
        st.markdown(
            '<p class="sidebar-section-label">System</p>',
            unsafe_allow_html=True,
        )

        # Check Ollama connection (non-blocking, cached for performance)
        ollama_online = _check_ollama_status()

        if ollama_online:
            st.markdown(
                '<div class="sidebar-status">'
                '<span class="status-dot"></span>'
                '<span>Ollama Connected</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="sidebar-status">'
                '<span class="status-dot-offline"></span>'
                '<span>Ollama Offline</span></div>',
                unsafe_allow_html=True,
            )

        # — Project Info Box —
        st.markdown(
            """
            <div class="sidebar-info-box">
                <div class="info-title">Project</div>
                <div class="info-text">
                    AI-Powered Code Explainer<br/>
                    &amp; Debugger
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # — Version Info Box (from config) —
        st.markdown(
            f"""
            <div class="sidebar-info-box" style="margin-top:0.5rem;">
                <div class="info-title">Version</div>
                <div class="info-text">v{APP.version} · Production</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # — Copyright —
        st.markdown(
            '<p class="sidebar-copyright">© 2026 CodeInsight AI</p>',
            unsafe_allow_html=True,
        )

    return st.session_state["current_page"]


def _check_ollama_status() -> bool:
    """Check Ollama connection status with a 30-second TTL cache.

    Uses session state to cache the result across reruns while allowing
    status updates if Ollama goes online/offline.

    Returns:
        bool: True if Ollama is reachable.
    """
    import time
    now = time.time()
    cache_key = "ollama_status_cache"

    if cache_key not in st.session_state or (now - st.session_state[cache_key]["time"]) > 30:
        try:
            from ai.ollama_client import get_client
            status = get_client().check_connection()
        except Exception:
            status = False
        st.session_state[cache_key] = {"status": status, "time": now}

    return st.session_state[cache_key]["status"]


# ─────────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────────

def render_hero_header() -> None:
    """Render the gradient hero banner with application title and tagline."""
    st.markdown(
        f"""
        <div class="hero-container animate-in">
            <h1>🤖 {APP.name}</h1>
            <p class="subtitle">AI-Powered Code Explainer &amp; Debugger</p>
            <p class="description">{APP.description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Editor Toolbar (Language + Theme)
# ─────────────────────────────────────────────

def render_editor_toolbar() -> tuple[str, str]:
    """Render the toolbar above the code editor with language and theme selectors.

    Returns:
        tuple[str, str]: (selected_language, selected_ace_theme)
    """
    st.markdown(
        '<p class="section-title" style="margin-top:0.25rem;">📝 Code Editor</p>',
        unsafe_allow_html=True,
    )

    col_lang, col_theme = st.columns([1, 1])

    with col_lang:
        language: str = st.selectbox(
            "🌐 Language",
            options=SUPPORTED_LANGUAGES,
            index=0,
            key="editor_language",
        )

    with col_theme:
        theme_key: str = st.selectbox(
            "🎨 Editor Theme",
            options=EDITOR_THEMES,
            format_func=lambda t: _THEME_DISPLAY_NAMES.get(t, t),
            index=0,
            key="editor_theme",
        )

    return language, theme_key


# ─────────────────────────────────────────────
# Ace Code Editor
# ─────────────────────────────────────────────

def render_code_editor(language: str, theme: str) -> str:
    """Render the streamlit-ace code editor.

    The editor mode is dynamically set based on the selected language.

    Args:
        language: The programming language name (e.g. 'Python').
        theme: The Ace editor theme key (e.g. 'monokai').

    Returns:
        str: The source code entered by the user.
    """
    ace_mode: str = _LANGUAGE_TO_ACE_MODE.get(language, "python")

    # Retrieve any pre-loaded sample code from session state
    default_code: str = st.session_state.get("editor_code", "")

    code: str = st_ace(
        value=default_code,
        language=ace_mode,
        theme=theme,
        height=THEME.editor_height,
        font_size=THEME.editor_font_size,
        show_gutter=True,
        show_print_margin=False,
        wrap=True,
        auto_update=True,
        key="ace_editor",
        placeholder="Paste your source code here...",
    )

    return code if code else ""


# ─────────────────────────────────────────────
# Editor Statistics
# ─────────────────────────────────────────────

def render_editor_stats(code: str, language: str) -> None:
    """Display live statistics about the current code in the editor.

    Shows total lines, total characters, selected language, and
    editor status as inline pill badges.

    Args:
        code: The current source code string.
        language: The selected programming language name.
    """
    total_lines: int = len(code.split("\n")) if code else 0
    total_chars: int = len(code) if code else 0
    status: str = "Ready" if not code else "Editing"

    st.markdown(
        f"""
        <div class="editor-stats">
            <span class="stat-badge">
                <span class="stat-icon">📄</span>
                Lines: <span class="stat-value">{total_lines}</span>
            </span>
            <span class="stat-badge">
                <span class="stat-icon">🔤</span>
                Characters: <span class="stat-value">{total_chars}</span>
            </span>
            <span class="stat-badge">
                <span class="stat-icon">🌐</span>
                <span class="stat-value">{language}</span>
            </span>
            <span class="stat-badge">
                <span class="stat-icon">{"✏️" if code else "⏳"}</span>
                Status: <span class="stat-value">{status}</span>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Language Validation Message
# ─────────────────────────────────────────────

def render_language_validation_message(result: LanguageDetectionResult) -> None:
    """Render the outcome of the pre-analysis language validation check.

    Purely presentational: receives an already-computed
    ``LanguageDetectionResult`` (see ``services/language_detector.py``)
    and renders the appropriate Streamlit alert. Contains no detection
    logic itself, consistent with this module's role as the UI layer.

    Args:
        result: The structured validation result produced by
            ``services.language_detector.validate_language``.
    """
    if result.status == DetectionStatus.MATCH:
        st.success(result.message)
    elif result.status == DetectionStatus.MISMATCH:
        st.error(result.message)
    else:
        st.warning(result.message)


# ─────────────────────────────────────────────
# Utility Buttons
# ─────────────────────────────────────────────

def render_utility_buttons(language: str) -> bool:
    """Render the utility action buttons below the editor.

    Buttons:
        🗑 Clear Code — clears editor content and analysis results
        📋 Load Sample — loads language-specific sample code
        📂 Upload File — opens a file uploader

    Args:
        language: The currently selected programming language.

    Returns:
        bool: True if the Analyze Code button was clicked.
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️  Clear Code", key="btn_clear", use_container_width=True):
            st.session_state["editor_code"] = ""
            st.session_state["analysis_result"] = None
            st.session_state["analysis_error"] = None
            st.rerun()

    with col2:
        if st.button("📋  Load Sample", key="btn_sample", use_container_width=True):
            st.session_state["editor_code"] = _SAMPLE_CODE.get(language, "")
            st.session_state["analysis_result"] = None
            st.session_state["analysis_error"] = None
            st.rerun()

    with col3:
        if st.button("📂  Upload File", key="btn_upload_toggle", use_container_width=True):
            st.session_state["show_uploader"] = not st.session_state.get(
                "show_uploader", False
            )
            st.rerun()

    # — File uploader (toggleable) —
    if st.session_state.get("show_uploader", False):
        uploaded_file = st.file_uploader(
            "Upload a source file",
            type=list(FILE.supported_extensions),
            key="file_uploader",
        )
        if uploaded_file is not None:
            try:
                file_content: str = uploaded_file.read().decode("utf-8")
                st.session_state["editor_code"] = file_content
                st.session_state["show_uploader"] = False
                st.session_state["analysis_result"] = None
                st.session_state["analysis_error"] = None
            except UnicodeDecodeError:
                st.session_state["analysis_error"] = (
                    "⚠️ Failed to decode file. Please upload a valid UTF-8 text file."
                )
                st.session_state["analysis_result"] = None
            except Exception as exc:
                st.session_state["analysis_error"] = (
                    f"⚠️ Failed to read uploaded file: {exc}"
                )
                st.session_state["analysis_result"] = None
            st.rerun()

    # — Primary Analyze button —
    st.markdown('<div class="analyze-btn-container">', unsafe_allow_html=True)
    analyze_clicked: bool = st.button(
        "🚀  Analyze Code",
        key="btn_analyze",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    return analyze_clicked


# ─────────────────────────────────────────────
# Loading / Welcome Placeholder
# ─────────────────────────────────────────────

def render_loading_placeholder() -> None:
    """Render a professional welcome state before analysis begins."""
    st.markdown(
        """
        <div class="placeholder-area animate-in">
            <div class="placeholder-icon">✨</div>
            <div class="placeholder-text">Ready to analyse your code</div>
            <div class="placeholder-subtext">
                Paste your code, select a language, and click
                <strong>Analyze Code</strong> to get started
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────

def render_footer() -> None:
    """Render the application footer with attribution."""
    st.markdown(
        f"""
        <div class="app-footer">
            <div class="footer-brand">{APP.name}</div>
            <div class="footer-tech">
                Built with ❤️ using
                <strong>Python</strong>, <strong>Streamlit</strong> &amp;
                <strong>Ollama</strong>
            </div>
            <div class="footer-copy">
                © 2026 {APP.name} · v{APP.version}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Reusable Page Renderers
# ─────────────────────────────────────────────

def render_home_page() -> tuple[str, str, str, bool]:
    """Render the main home page consisting of the code editor and toolbar.

    Returns:
        tuple[str, str, str, bool]: (entered_code, selected_language, selected_theme, analyze_clicked)
    """
    render_hero_header()
    language, theme = render_editor_toolbar()
    code = render_code_editor(language, theme)
    render_editor_stats(code, language)
    analyze_clicked = render_utility_buttons(language)
    return code, language, theme, analyze_clicked


def render_documentation_page() -> None:
    """Render a professional, interactive documentation page."""
    st.markdown(
        """
        <div class="result-section-header animate-in">
            <span class="section-icon">📘</span>
            <span class="section-label">Documentation & Guides</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Getting Started
    st.markdown(
        """
        <div class="doc-card animate-in">
            <div class="doc-card-title">🚀 Getting Started</div>
            <div class="doc-card-text">
                CodeInsight AI is a completely local code analysis application. To run the analysis pipeline, ensure you have:
                <ul>
                    <li><strong>Ollama</strong> installed and active on your machine.</li>
                    <li>The default <strong>llama3</strong> model pulled and running (run <code>ollama pull llama3</code> in your terminal).</li>
                    <li>The application running via <code>streamlit run app.py</code>.</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Visual Workflow & AI Pipeline
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(
            """
            <div class="doc-card animate-in" style="height: 100%;">
                <div class="doc-card-title">⚙️ Application Workflow & Pipeline</div>
                <div class="doc-card-text">
                    The analysis utilizes a unidirectional, multi-layer architecture:
                    <ol>
                        <li><strong>Input Layer:</strong> User uploads or pastes code into the editor.</li>
                        <li><strong>Validation Layer:</strong> Ensures correctness of files, length constraints, and supported languages.</li>
                        <li><strong>AI Core Orchestration:</strong> Constructing highly detailed engineer persona prompts.</li>
                        <li><strong>LLM Inference:</strong> Passing requests via raw API calls to the local Ollama daemon.</li>
                        <li><strong>Format & Render:</strong> Splitting the raw markdown stream using lenient regex rules and displaying them in modular layout containers.</li>
                    </ol>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="workflow-container animate-in">
                <div class="doc-card-title" style="margin-bottom:1rem; font-size:1rem;">📌 AI Pipeline</div>
                <div class="workflow-step">📝 User Code</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">🧠 Analyzer</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">⚡ Prompt Builder</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">🔌 Ollama</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">🤖 Llama3</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">📋 Formatter</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">📊 Results</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # How to Use & Supported Languages
    col3, col4 = st.columns([1, 1])

    with col3:
        st.markdown(
            """
            <div class="doc-card animate-in">
                <div class="doc-card-title">📖 How to Use</div>
                <div class="doc-card-text">
                    1. <strong>Select Language & Theme:</strong> Use the editor toolbar to match your source syntax.
                    2. <strong>Load or Paste:</strong> Write code directly, load a built-in pre-coded sample, or drag-and-drop code files directly.
                    3. <strong>Analyze:</strong> Hit the primary action CTA to run analysis.
                    4. <strong>Review:</strong> Inspect explanations, detailed bugs, and corrected read-only diffs.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
            <div class="doc-card animate-in">
                <div class="doc-card-title">🌐 Supported Languages</div>
                <div class="doc-card-text">
                    CodeInsight AI supports the following standard languages:
                    <ul>
                        <li><strong>Python:</strong> Syntax highlighting, custom AST-tailored prompt structure.</li>
                        <li><strong>C++:</strong> Handles standard templates, headers, source extensions.</li>
                        <li><strong>Java:</strong> Full OOP structure and class template loader.</li>
                        <li><strong>JavaScript:</strong> Modern ES6+ syntax support.</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Features
    st.markdown(
        """
        <div class="doc-card animate-in">
            <div class="doc-card-title">⭐ Core Features</div>
            <div class="doc-card-text">
                <ul>
                    <li><strong>Code Explanation:</strong> Breaks down complex design patterns, functions, and overall intent into plain English.</li>
                    <li><strong>Bug Finder:</strong> Detects logic bugs, runtime errors, and performance anti-patterns with severity markings.</li>
                    <li><strong>Corrected Code Block:</strong> Produces ready-to-run code with inline comments fixing all issues.</li>
                    <li><strong>Editor Stats:</strong> Live counters monitoring character lengths and line metrics.</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # FAQ
    st.markdown(
        """
        <div class="result-section-header animate-in" style="margin-top:1.5rem;">
            <span class="section-icon">❓</span>
            <span class="section-label">Frequently Asked Questions (FAQ)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("🔒 Is my source code sent to any third-party servers?", expanded=False):
        st.write(
            "No. CodeInsight AI relies entirely on a local instance of Ollama. "
            "Your code remains local on your filesystem and never exits your system boundary, "
            "making the application safe for corporate or confidential codebase analysis."
        )

    with st.expander("🚀 Can I use a model other than llama3?", expanded=False):
        st.write(
            "Yes! You can configure the model parameter inside `config/settings.py` under "
            "`OllamaConfig.model`. Ensure you pull the model locally using `ollama pull <model-name>` "
            "before triggering analysis."
        )

    with st.expander("⏳ What should I do if the analysis times out?", expanded=False):
        st.write(
            "Local LLMs can take time to run if they are loaded into system memory (RAM/VRAM) for "
            "the first time. If it times out, verify your Ollama status, make sure the model is pulled, "
            "and trigger the analysis again. The default timeout is configured at 120 seconds in `config/settings.py`."
        )


def render_about_project_page() -> None:
    """Render a professional About Project page with architecture diagram and tech details."""
    st.markdown(
        """
        <div class="result-section-header animate-in">
            <span class="section-icon">ℹ️</span>
            <span class="section-label">About CodeInsight AI</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Overview & Motivation
    st.markdown(
        """
        <div class="doc-card animate-in">
            <div class="doc-card-title">📖 Project Overview & Motivation</div>
            <div class="doc-card-text">
                <strong>CodeInsight AI</strong> was created to bridge the gap between AI code generation and local security policies. 
                Many developers want advanced explanation and debug capabilities but cannot upload proprietary, private, or 
                student assignment codes to commercial cloud models. This project offers a completely containerized, 
                private workflow driven by local LLMs via Ollama.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Architecture & Design Principles
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(
            """
            <div class="doc-card animate-in" style="height: 100%;">
                <div class="doc-card-title">📐 Design Principles</div>
                <div class="doc-card-text">
                    <ul>
                        <li><strong>Single Responsibility Principle (SRP):</strong> Every class, function, and module owns exactly one concern.</li>
                        <li><strong>Persona Guardrails:</strong> Prompts are optimized to restrict hallucinated issues, enforcing strict code preservation.</li>
                        <li><strong>Clean Interface Separations:</strong> UI widgets only read formatted data models; they contain no parsing or HTTP logic.</li>
                        <li><strong>Config-Driven:</strong> Visual tokens, timeouts, and rules are isolated from functional logic.</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="workflow-container animate-in">
                <div class="doc-card-title" style="margin-bottom:1rem; font-size:1rem;">🏗️ Architecture</div>
                <div class="workflow-step">🌐 Streamlit UI</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">⚙️ AnalyzerService</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">⚡ Prompt Builder</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">🔌 Ollama Client</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">🤖 Llama3</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">📋 Response Formatter</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">📊 AnalysisResult</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">🖥️ UI</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Technology Stack
    st.markdown(
        """
        <div class="doc-card animate-in">
            <div class="doc-card-title">🛠️ Technology Stack</div>
            <div class="doc-card-text">
                The application relies on these core technologies:
                <div class="tech-badge-container">
                    <span class="tech-badge">🐍 Python 3.10+</span>
                    <span class="tech-badge">👑 Streamlit</span>
                    <span class="tech-badge">🤖 Ollama</span>
                    <span class="tech-badge">💻 Llama3 Model</span>
                    <span class="tech-badge">📝 Streamlit Ace</span>
                    <span class="tech-badge">⚡ Requests HTTP</span>
                    <span class="tech-badge">🧪 Pytest</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Project Information
    st.markdown(
        """
        <div class="doc-card animate-in">
            <div class="doc-card-title">📝 Project Metadata</div>
            <div class="doc-card-text">
                <ul>
                    <li><strong>Application:</strong> CodeInsight AI</li>
                    <li><strong>Version:</strong> v0.3.0 · Production</li>
                    <li><strong>Scope:</strong> Phase 12 - Professional Navigation System</li>
                    <li><strong>Developer:</strong> CodeInsight AI Team</li>
                    <li><strong>License:</strong> Educational & Development Use</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_settings_page() -> None:
    """Render a clean, read-only settings configuration dashboard."""
    st.markdown(
        """
        <div class="result-section-header animate-in">
            <span class="section-icon">⚙️</span>
            <span class="section-label">Application Settings</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="settings-group animate-in">
            <div class="doc-card-title" style="font-size:1.15rem; margin-bottom: 1rem;">🎨 Appearance</div>
            <div class="settings-row">
                <span class="settings-label">Application Theme</span>
                <span class="settings-value">Dark Mode (Forced)</span>
            </div>
            <div class="settings-row">
                <span class="settings-label">Primary Brand Color</span>
                <span class="settings-value">#6366F1 (Indigo)</span>
            </div>
            <div class="settings-row">
                <span class="settings-label">Accent Highlight Color</span>
                <span class="settings-value">#A855F7 (Purple)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="settings-group animate-in">
            <div class="doc-card-title" style="font-size:1.15rem; margin-bottom: 1rem;">📝 Editor Preferences</div>
            <div class="settings-row">
                <span class="settings-label">Editor Font Size</span>
                <span class="settings-value">14px</span>
            </div>
            <div class="settings-row">
                <span class="settings-label">Editor Height</span>
                <span class="settings-value">380px</span>
            </div>
            <div class="settings-row">
                <span class="settings-label">Syntax Highlighting Mode</span>
                <span class="settings-value">Auto-detected from selection</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="settings-group animate-in">
            <div class="doc-card-title" style="font-size:1.15rem; margin-bottom: 1rem;">🧠 Analysis Preferences</div>
            <div class="settings-row">
                <span class="settings-label">Maximum Code Input Length</span>
                <span class="settings-value">15,000 characters</span>
            </div>
            <div class="settings-row">
                <span class="settings-label">Maximum AI Response Length</span>
                <span class="settings-value">10,000 tokens</span>
            </div>
            <div class="settings-row">
                <span class="settings-label">Analysis Target Persona</span>
                <span class="settings-value">Senior Software Engineer</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="settings-group animate-in">
            <div class="doc-card-title" style="font-size:1.15rem; margin-bottom: 1rem;">🤖 AI Model Information</div>
            <div class="settings-row">
                <span class="settings-label">Ollama Host Address</span>
                <span class="settings-value">http://localhost:11434</span>
            </div>
            <div class="settings-row">
                <span class="settings-label">Configured LLM Model</span>
                <span class="settings-value">llama3</span>
            </div>
            <div class="settings-row">
                <span class="settings-label">Request Timeout Limit</span>
                <span class="settings-value">120 seconds</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="settings-group animate-in">
            <div class="doc-card-title" style="font-size:1.15rem; margin-bottom: 1rem;">📋 Application Information</div>
            <div class="settings-row">
                <span class="settings-label">Application Version</span>
                <span class="settings-value">v0.3.0 · Production</span>
            </div>
            <div class="settings-row">
                <span class="settings-label">Release Branch</span>
                <span class="settings-value">Main (Phase 12)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )