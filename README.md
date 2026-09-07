# 🧠 CodeInsight AI

**AI-powered source code analysis, bug detection, and code correction — driven by Ollama.**

CodeInsight AI is a production-ready, local-first web application that empowers developers to understand, debug, and optimize their code instantly. It uses Streamlit for its polished, modern interface and Ollama for executing local inference, preserving complete privacy and security.

---

## 📋 Features

- 📖 **Code Explanation:** A structured, plain-English breakdown of code logic, design patterns, and algorithms.
- 🐞 **Bug Detection:** Identifies logical errors, syntax issues, anti-patterns, and vulnerability edge-cases with detailed severity metrics.
- 🔧 **Code Correction:** Provides a syntactically validated corrected version of the code with fixes applied and explained.
- 🌐 **Multi-Language Support:** Full syntax highlighting and AST analysis support for Python, C++, Java, and JavaScript.
- 🎨 **Visual Customization:** Theme integration with support for monokai, dracula, tomorrow_night, and github editors.
- 📂 **File Upload:** Upload code files directly to populate the editor automatically.
- 📊 **Real-time Metrics:** Inline indicators tracking character and line counts dynamically.
- 🔌 **Dynamic Connection Status:** Active polling checks status of local Ollama nodes with a 30-second TTL cache for responsiveness.

---

## 🛠️ Technology Stack

- **Language:** Python 3.10+
- **Frontend Framework:** Streamlit
- **AI Core:** Ollama (local LLM server)
- **Editor Integration:** Streamlit Ace
- **HTTP Transport:** Requests

---

## 📁 Folder Structure

```text
CodeInsight-AI/
│
├── .streamlit/             # Streamlit configuration parameters
│   └── config.toml         # Custom dark theme options
│
├── app.py                  # Main application entry point & orchestration
│
├── config/                 # Configuration and settings singletons
│   ├── __init__.py
│   └── settings.py         # Application settings configuration
│
├── ai/                     # AI abstraction layer
│   ├── __init__.py
│   ├── ollama_client.py    # HTTP client for Ollama API
│   └── prompts.py          # Structured prompt builders
│
├── services/               # Core business logic services
│   ├── __init__.py
│   ├── analyzer.py         # Code analysis orchestration
│   └── formatter.py        # Markdown response parser
│
├── ui/                     # Presentation layer components
│   ├── __init__.py
│   ├── components.py       # Reusable layout sections
│   └── styles.py           # Global dark theme CSS stylesheet
│
├── utils/                  # Shared utility functions
│   ├── __init__.py
│   └── helpers.py          # Placeholder helper stubs
│
├── assets/                 # Static assets (images, icons)
│
├── tests/                  # Unit and integration tests
│   └── __init__.py
│
├── requirements.txt        # Python dependency manifest
├── README.md               # Product documentation
└── .gitignore              # Git ignore rules
```

---

## 💻 Requirements & Dependencies

- **OS:** Windows / macOS / Linux
- **Python:** 3.10 or higher
- **Ollama:** Installed locally and running on standard port `11434`
- **Model:** `llama3` (or configured override model)

For complete Python dependencies, inspect `requirements.txt`.

---

## ⚙️ Installation & Setup

### 1. Set Up the Python Environment

Clone this repository, navigate to the directory, and set up a virtual environment:

```bash
# Clone the repository
git clone https://github.com/your-username/CodeInsight-AI.git
cd CodeInsight-AI

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\\Scripts\\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install and Set Up Ollama

1. Download and install Ollama from [ollama.com](https://ollama.com).
2. Start the Ollama server locally (it usually runs automatically in the background).
3. Pull the default LLM model (`llama3`):
   ```bash
   ollama pull llama3
   ```
4. Verify the server is running by visiting `http://localhost:11434` in your browser.

---

## 🚀 Running the Application

To launch CodeInsight AI, execute:

```bash
streamlit run app.py
```

The application will start, and a browser window should automatically open to `http://localhost:8501`.

---

## 🌐 Supported Languages

CodeInsight AI currently provides syntax highlighting, template code loader support, and LLM-targeted prompt generation for the following languages:

* 🐍 **Python**
* ⚙️ **C++**
* ☕ **Java**
* 🟨 **JavaScript**

---

## 🖼️ Application Screenshots

*Below are conceptual layouts of the production user interface:*

<!-- 
Screenshot Placeholder 1: Main Dashboard
[IMAGE: A screenshot showing the dark mode theme, the code editor on the left filled with a Python Fibonacci sample, and the dynamic Ollama Connected status badge in the sidebar.]
-->

<!-- 
Screenshot Placeholder 2: Analysis Results
[IMAGE: A screenshot displaying code explanations, identified bugs highlighted in warning banners, and a side-by-side read-only editor showing corrected code.]
-->

---

## 🔮 Future Improvements

1. **Local Conversation History:** Persist previous code analyses across browser sessions using an SQLite database layer.
2. **Additional Language ASTs:** Integrate support for Rust, Go, TypeScript, and HTML/CSS.
3. **Advanced OCR Integration:** Allow uploading screenshots of code from physical whiteboards or screens to extract and analyze code.
4. **Custom Prompt Tweaks:** Give users direct settings inputs to control explanation verbosity or target specific standards (e.g. PEP 8, MISRA C).
5. **Multi-Model Support:** Easily toggle between different locally running LLMs (e.g., `mistral`, `codegemma`, `phi3`) from the UI.

---

> Built with 🧠 by the CodeInsight AI team.


