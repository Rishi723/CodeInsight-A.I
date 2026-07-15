"""
UI Package

This package contains all user-interface components, styles, and layout
definitions for the CodeInsight AI Streamlit application.

Modules:
    components: Reusable Streamlit UI widget functions
    styles: Custom CSS stylesheet for the premium SaaS look
"""

from ui.components import (
    render_sidebar,
    render_hero_header,
    render_editor_toolbar,
    render_code_editor,
    render_editor_stats,
    render_utility_buttons,
    render_loading_placeholder,
    render_footer,
)

__all__ = [
    "render_sidebar",
    "render_hero_header",
    "render_editor_toolbar",
    "render_code_editor",
    "render_editor_stats",
    "render_utility_buttons",
    "render_loading_placeholder",
    "render_footer",
]
