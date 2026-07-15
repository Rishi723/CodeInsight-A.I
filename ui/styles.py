"""
UI Styles — Enhanced Edition

Custom CSS for the CodeInsight AI Streamlit application.
Provides a premium, modern SaaS aesthetic with polished editor
toolbar, stat badges, utility buttons, and enhanced result cards.

Design System:
    - Primary: Indigo (#6366F1)
    - Accent: Purple (#A855F7)
    - Surface: Slate Dark (#0F172A)
    - Radius: 8–20px
    - Font: 'Inter' + 'JetBrains Mono' via Google Fonts
"""


def get_global_styles() -> str:
    """Return the complete CSS stylesheet for the application.

    Returns:
        str: A <style> block containing all custom CSS rules.
    """
    return """
    <style>
    /* ===== Google Fonts ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

    /* ===== Root & Global Reset ===== */
    :root {
        /* Core Colors */
        --primary: #6366F1;
        --primary-light: #818CF8;
        --primary-dark: #4F46E5;
        --accent: #A855F7;
        --accent-light: #C084FC;
        
        /* Status Colors */
        --success: #10B981;
        --success-light: rgba(16, 185, 129, 0.15);
        --warning: #F59E0B;
        --warning-light: rgba(245, 158, 11, 0.15);
        --danger: #EF4444;
        --danger-light: rgba(239, 68, 68, 0.15);
        
        /* Dark Theme Surfaces */
        --surface: #0F172A;
        --surface-secondary: #1E293B;
        --surface-tertiary: #334155;
        --surface-overlay: rgba(30, 41, 59, 0.8);
        
        /* Dark Theme Text */
        --text-primary: #F8FAFC;
        --text-secondary: #CBD5E1;
        --text-muted: #94A3B8;
        
        /* Dark Theme Borders */
        --border: #334155;
        --border-light: #475569;
        
        /* Shadows & Effects */
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
        --shadow-lg: 0 8px 30px rgba(0,0,0,0.5);
        --shadow-glow: 0 0 20px rgba(99, 102, 241, 0.15);
        
        /* Layout Metrics */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

     html, body, [class*="st-"] {
         font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
     }
     /* Restore Streamlit's Material Symbols icon font (fixes expander chevron
   and other built-in icons being broken by the global font override above) */
    [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded' !important;
    }

    /* ===== Hide Default Streamlit Branding ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* ===== Main Container ===== */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 920px !important;
    }

    /* ===== Sidebar Styling ===== */
    section[data-testid="stSidebar"] {
        background: #0B1120 !important;
        border-right: 1px solid var(--border) !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdown"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdown"] span,
    section[data-testid="stSidebar"] [data-testid="stMarkdown"] li,
    section[data-testid="stSidebar"] [data-testid="stMarkdown"] h1,
    section[data-testid="stSidebar"] [data-testid="stMarkdown"] h2,
    section[data-testid="stSidebar"] [data-testid="stMarkdown"] h3,
    section[data-testid="stSidebar"] [data-testid="stMarkdown"] h4 {
        color: var(--text-secondary) !important;
    }

    /* ===== Hero / Header Card ===== */
    .hero-container {
        background: linear-gradient(135deg, var(--surface-secondary) 0%, var(--surface) 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        padding: 2.5rem 2rem 2rem 2rem;
        text-align: center;
        box-shadow: var(--shadow-lg), var(--shadow-glow);
        margin-bottom: 1.75rem;
        position: relative;
        overflow: hidden;
    }

    .hero-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        opacity: 0.8;
    }

    .hero-container h1 {
        color: var(--text-primary) !important;
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.25rem !important;
        letter-spacing: -0.03em;
    }

    .hero-container .subtitle {
        color: var(--primary-light) !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }

    .hero-container .description {
        color: var(--text-muted) !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        max-width: 560px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ===== Section Titles ===== */
    .section-title {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.01em;
    }

    /* ===== Editor Toolbar Container ===== */
    .editor-toolbar {
        background: var(--surface-secondary);
        border: 1px solid var(--border);
        border-bottom: none;
        border-radius: var(--radius-md) var(--radius-md) 0 0;
        padding: 0.75rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }

    /* ===== Ace Editor Wrapper ===== */
    .ace-editor-wrapper {
        border: 1px solid var(--border);
        border-top: none;
        border-radius: 0 0 var(--radius-md) var(--radius-md);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        margin-bottom: 0.75rem;
    }

    /* ===== Editor Stat Badges ===== */
    .editor-stats {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex-wrap: wrap;
        padding: 0.6rem 0;
    }

    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: var(--surface-secondary);
        border: 1px solid var(--border);
        border-radius: 100px;
        padding: 0.35rem 0.85rem;
        font-size: 0.78rem;
        font-weight: 500;
        color: var(--text-secondary);
        transition: var(--transition);
    }

    .stat-badge:hover {
        border-color: var(--border-light);
        background: var(--surface-tertiary);
        color: var(--text-primary);
    }

    .stat-badge .stat-icon {
        font-size: 0.85rem;
    }

    .stat-badge .stat-value {
        font-weight: 600;
        color: var(--text-primary);
    }

    /* ===== Utility Buttons Row ===== */
    .utility-btn-row {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.75rem;
    }

    /* Secondary button style (Clear / Sample / Upload) */
    div[data-testid="stColumns"] div.stButton > button {
        background: var(--surface-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: var(--shadow-sm) !important;
        transition: var(--transition) !important;
        width: 100%;
    }

    div[data-testid="stColumns"] div.stButton > button:hover {
        border-color: var(--primary-light) !important;
        background: var(--surface-tertiary) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px);
    }

    /* ===== Primary Analyze Button ===== */
    .analyze-btn-container {
        margin-top: 0.5rem;
    }
    
    .analyze-btn-container div.stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.9rem 2.5rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.25) !important;
        transition: var(--transition) !important;
        width: 100%;
    }

    .analyze-btn-container div.stButton > button:hover {
        box-shadow: 0 6px 24px rgba(99, 102, 241, 0.40) !important;
        transform: translateY(-2px);
        filter: brightness(1.1);
    }

    .analyze-btn-container div.stButton > button:active {
        transform: translateY(0px);
    }

    /* ===== SelectBox (General) ===== */
    div[data-baseweb="select"] {
        border-radius: var(--radius-sm) !important;
    }

    div[data-baseweb="select"] > div {
        border-radius: var(--radius-sm) !important;
        border-color: var(--border) !important;
        background: var(--surface-secondary) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
    }

    /* ===== Result Section Cards ===== */
    .result-section-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    .result-section-header .section-icon {
        font-size: 1.15rem;
    }

    .result-section-header .section-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
    }

    /* Expander Styling */
    details[data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        background: var(--surface-secondary) !important;
        box-shadow: var(--shadow-sm) !important;
        margin-bottom: 0.85rem !important;
        transition: var(--transition) !important;
        overflow: hidden;
    }

    details[data-testid="stExpander"]:hover {
        box-shadow: var(--shadow-md) !important;
        border-color: var(--border-light) !important;
    }

    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.98rem !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem 1.25rem !important;
        transition: var(--transition) !important;
    }
    
    .streamlit-expanderContent {
        color: var(--text-secondary) !important;
        padding: 0 1.25rem 1.25rem 1.25rem !important;
        line-height: 1.6 !important;
    }

    /* ===== Loading / Placeholder Area ===== */
    .placeholder-area {
        background: var(--surface-secondary);
        border: 1px dashed var(--border-light);
        border-radius: var(--radius-lg);
        padding: 3rem 1.5rem;
        text-align: center;
        color: var(--text-muted);
        margin: 1.5rem 0;
        transition: var(--transition);
        box-shadow: var(--shadow-sm);
    }

    .placeholder-area .placeholder-icon {
        font-size: 2.2rem;
        margin-bottom: 0.8rem;
        opacity: 0.7;
    }

    .placeholder-area .placeholder-text {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 1.05rem;
    }

    .placeholder-area .placeholder-subtext {
        font-size: 0.9rem;
        color: var(--text-muted);
        margin-top: 0.4rem;
    }

    /* ===== Footer ===== */
    .app-footer {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        margin-top: 3rem;
        border-top: 1px solid var(--border);
        color: var(--text-muted);
    }

    .app-footer .footer-brand {
        font-weight: 700;
        color: var(--text-primary);
        font-size: 0.95rem;
        letter-spacing: -0.01em;
    }

    .app-footer .footer-tech {
        margin-top: 0.4rem;
        font-size: 0.85rem;
    }

    .app-footer .footer-tech strong {
        color: var(--text-secondary);
    }

    .app-footer .footer-copy {
        margin-top: 0.6rem;
        font-size: 0.8rem;
        color: var(--text-muted);
    }

    /* ===== Sidebar Nav Items ===== */
    .sidebar-nav-item {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        padding: 0.7rem 1rem;
        border-radius: var(--radius-sm);
        color: var(--text-secondary) !important;
        font-size: 0.92rem;
        font-weight: 500;
        cursor: pointer;
        transition: var(--transition);
        margin-bottom: 0.25rem;
    }

    .sidebar-nav-item:hover {
        background: var(--surface-secondary);
        color: var(--text-primary) !important;
    }

    .sidebar-nav-item.active {
        background: var(--surface-tertiary);
        color: var(--primary-light) !important;
        font-weight: 600;
        border-left: 3px solid var(--primary);
    }

    .sidebar-nav-item .nav-icon {
        font-size: 1.1rem;
        width: 1.4rem;
        text-align: center;
    }

    /* ===== Sidebar Brand ===== */
    .sidebar-brand {
        text-align: center;
        padding: 0.5rem 1rem 1.5rem 1rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }

    .sidebar-brand .brand-logo {
        font-size: 2.2rem;
        margin-bottom: 0.25rem;
    }

    .sidebar-brand .brand-name {
        font-size: 1.35rem;
        font-weight: 800;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em;
    }

    .sidebar-brand .brand-tagline {
        font-size: 0.78rem;
        color: var(--text-muted) !important;
        font-weight: 500;
        margin-top: 0.15rem;
    }

    /* ===== Sidebar Section Label ===== */
    .sidebar-section-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0 1rem;
        margin-bottom: 0.5rem;
        margin-top: 0.5rem;
    }

    /* ===== Sidebar Divider ===== */
    .sidebar-divider {
        height: 1px;
        background: var(--border);
        margin: 1.25rem 0;
    }

    /* ===== Sidebar Info Box ===== */
    .sidebar-info-box {
        background: var(--surface-secondary);
        border-radius: var(--radius-sm);
        padding: 1rem 1.25rem;
        margin-top: 1rem;
        border: 1px solid var(--border);
    }

    .sidebar-info-box .info-title {
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }

    .sidebar-info-box .info-text {
        font-size: 0.85rem;
        color: var(--text-secondary) !important;
        line-height: 1.6;
    }
    
    .sidebar-copyright {
        text-align: center;
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 2rem;
        opacity: 0.8;
    }

    /* ===== Sidebar Status Indicator ===== */
    .sidebar-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-secondary) !important;
        background: var(--surface-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        margin: 0.5rem 1rem;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--success);
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
        animation: pulse-dot 2.5s ease-in-out infinite;
    }

    .status-dot-offline {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--danger);
        box-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
    }

    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    /* ===== Analysis Metadata Badge ===== */
    .analysis-meta {
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-wrap: wrap;
        padding: 0.75rem 1rem;
        background: var(--surface-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        margin-bottom: 1rem;
        font-size: 0.88rem;
        color: var(--text-secondary);
    }

    .analysis-meta .meta-item {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }

    .analysis-meta .meta-value {
        font-weight: 600;
        color: var(--text-primary);
    }

    .analysis-meta .meta-divider {
        width: 1px;
        height: 16px;
        background: var(--border-light);
    }

    /* ===== New Analysis Button (secondary) ===== */
    .new-analysis-container {
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    .new-analysis-container div.stButton > button {
        background: var(--surface-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.6rem 1.5rem !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: var(--transition) !important;
        width: 100%;
    }

    .new-analysis-container div.stButton > button:hover {
        background: var(--surface-tertiary) !important;
        border-color: var(--primary-light) !important;
        box-shadow: var(--shadow-sm) !important;
        transform: translateY(-1px);
    }

    /* ===== Alerts / Status Messages ===== */
    div[data-testid="stAlert"] {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border) !important;
        background: var(--surface-secondary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Code Blocks */
    code {
        color: var(--primary-light) !important;
        background: var(--surface) !important;
        padding: 0.15rem 0.35rem;
        border-radius: var(--radius-sm);
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9em;
    }
    
    pre code {
        background: transparent !important;
        padding: 0;
        color: inherit !important;
    }

    /* ===== Subtle Animations ===== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .animate-in {
        animation: fadeInUp 0.5s ease-out forwards;
    }

    /* ===== Sidebar Navigation Buttons ===== */
    .sidebar-nav-btn-wrapper {
        width: 100%;
        margin-bottom: 0.25rem;
    }
    
    .sidebar-nav-btn-wrapper div.stButton > button {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        padding: 0.7rem 1rem !important;
        border-radius: var(--radius-sm) !important;
        width: 100% !important;
        transition: var(--transition) !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.65rem !important;
    }

    .sidebar-nav-btn-wrapper div.stButton > button:hover {
        background: var(--surface-secondary) !important;
        color: var(--text-primary) !important;
    }

    .sidebar-nav-btn-wrapper.active-nav div.stButton > button {
        background: var(--surface-tertiary) !important;
        color: var(--primary-light) !important;
        font-weight: 600 !important;
        border-left: 3px solid var(--primary) !important;
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0 !important;
    }

    /* ===== Documentation & About Cards ===== */
    .doc-card {
        background: var(--surface-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
    }
    
    .doc-card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--border-light);
    }

    .doc-card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .doc-card-text {
        font-size: 0.92rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }

    /* ===== Visual Workflow Step ===== */
    .workflow-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1.5rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        margin: 1rem 0;
    }

    .workflow-step {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        background: var(--surface-secondary);
        border: 1px solid var(--border-light);
        padding: 0.6rem 1.25rem;
        border-radius: var(--radius-sm);
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--text-primary);
        width: 100%;
        max-width: 280px;
        box-shadow: var(--shadow-sm);
    }

    .workflow-arrow {
        color: var(--primary-light);
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0.35rem 0;
    }

    /* ===== Technology Stack Badges ===== */
    .tech-badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }

    .tech-badge {
        background: var(--surface-tertiary);
        border: 1px solid var(--border-light);
        color: var(--text-primary);
        padding: 0.35rem 0.75rem;
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* ===== Settings Cards ===== */
    .settings-group {
        background: var(--surface-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        margin-bottom: 1.25rem;
    }

    .settings-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--border);
    }

    .settings-row:last-child {
        border-bottom: none;
    }

    .settings-label {
        font-size: 0.92rem;
        font-weight: 600;
        color: var(--text-primary);
    }

    .settings-value {
        font-size: 0.88rem;
        color: var(--text-muted);
        background: var(--surface-tertiary);
        padding: 0.25rem 0.6rem;
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-light);
    }

    /* ===== Responsive Adjustments ===== */
    @media (max-width: 768px) {
        .hero-container {
            padding: 2rem 1.5rem;
        }
        .hero-container h1 {
            font-size: 2rem !important;
        }
        .editor-stats {
            gap: 0.5rem;
        }
        .stat-badge {
            padding: 0.3rem 0.6rem;
            font-size: 0.75rem;
        }
        .analyze-btn-container div.stButton > button {
            padding: 0.8rem 1.5rem !important;
        }
    }
    </style>
    """
