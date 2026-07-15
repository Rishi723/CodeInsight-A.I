"""
Prompt Engineering — ai/prompts.py

Centralised, reusable prompt management system for CodeInsight AI.

This module is the **single source of truth** for every AI prompt used
by the application.  It generates structured prompt strings that are
consumed by the Ollama client (``ai/ollama_client.py``) via the
service layer (``services/analyzer.py``).

Responsibilities:
    • Construct well-engineered prompts for code explanation,
      bug detection, code correction, and full analysis.
    • Share common base instructions across all prompt types
      to avoid duplication and ensure consistent AI behaviour.
    • Accept ``source_code`` and ``programming_language`` as inputs
      and dynamically embed them into the prompt.

Non-responsibilities (kept in other modules):
    • Sending prompts to Ollama     → ai/ollama_client.py
    • Parsing AI responses          → services/analyzer.py
    • Rendering results in the UI   → ui/components.py

Architecture:
    ``PromptBuilder`` uses a shared ``_base_instructions()`` method
    that encapsulates the persona, tone, and guardrails common to
    every prompt.  Each public method appends task-specific
    instructions and the user's source code, producing a complete,
    ready-to-send prompt string.

    Adding a new prompt type (e.g. security analysis, unit test
    generation) requires only a single new method — the base
    instructions and code-injection logic are fully reused.

Usage:
    >>> from ai.prompts import prompt_builder
    >>> prompt = prompt_builder.build_full_analysis_prompt(
    ...     source_code='print("hello")',
    ...     programming_language="Python",
    ... )
    >>> # prompt is now ready to send to OllamaClient.generate()
"""

from __future__ import annotations


class PromptBuilder:
    """Factory for structured AI prompts.

    All prompt construction logic is encapsulated here.  The class is
    stateless — every method is a pure function of its arguments — so
    a single instance can be safely shared across the application.

    Design principles:
        • **DRY** — common instructions live in ``_base_instructions()``.
        • **Open / Closed** — new prompt types are added by writing a
          new method; existing methods never need modification.
        • **Single Responsibility** — this class only *builds* strings;
          it never sends them or interprets responses.
    """

    # ─────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────

    @staticmethod
    def _base_instructions() -> str:
        """Return the shared persona and behavioural guidelines.

        These instructions are prepended to **every** prompt to ensure
        the AI responds with a consistent voice, quality level, and
        formatting style regardless of the specific task.

        Returns:
            str: Multi-line base instruction block.
        """
        return (
            "You are a Senior Software Engineer with deep expertise in "
            "multiple programming languages and software architecture.\n\n"
            "Follow these rules strictly:\n"
            "- Analyze the provided code objectively and thoroughly.\n"
            "- Never invent, fabricate, or assume bugs that do not exist.\n"
            "- Preserve the original intended functionality of the code.\n"
            "- Explain concepts clearly, concisely, and professionally.\n"
            "- Suggest corrections only when genuine issues are found.\n"
            "- If no bugs exist, explicitly state: \"No bugs detected.\"\n"
            "- Produce well-structured Markdown output.\n"
            "- Do not include unnecessary commentary outside the "
            "requested structure.\n"
        )

    @staticmethod
    def _format_code_block(
        source_code: str,
        programming_language: str,
    ) -> str:
        """Wrap source code in a labelled, fenced Markdown code block.

        Args:
            source_code:          The user-supplied source code.
            programming_language: Display name of the language.

        Returns:
            str: A section header + fenced code block ready for
                 embedding in a prompt.
        """
        lang_lower = programming_language.lower()
        return (
            f"Programming Language: {programming_language}\n\n"
            f"```{lang_lower}\n"
            f"{source_code}\n"
            "```\n"
        )

    def _build_prompt(
        self,
        task_instructions: str,
        source_code: str,
        programming_language: str,
    ) -> str:
        """Assemble a complete prompt from base + task + code.

        This is the core composition method.  Every public builder
        delegates here to guarantee a uniform structure:

            [base instructions]
            [task-specific instructions]
            [source code block]

        Args:
            task_instructions:    Instructions specific to the task.
            source_code:          The user-supplied source code.
            programming_language: Display name of the language.

        Returns:
            str: A complete, ready-to-send prompt string.
        """
        return (
            f"{self._base_instructions()}\n"
            f"{task_instructions}\n\n"
            f"{self._format_code_block(source_code, programming_language)}"
        )

    # ─────────────────────────────────────────
    # Public prompt builders
    # ─────────────────────────────────────────

    def build_explanation_prompt(
        self,
        source_code: str,
        programming_language: str,
    ) -> str:
        """Build a prompt focused on explaining source code.

        The AI is asked to describe what the code does, how it works,
        and which programming concepts it demonstrates.

        Args:
            source_code:          The code to explain.
            programming_language: Language of the source code.

        Returns:
            str: The assembled explanation prompt.
        """
        task = (
            "YOUR TASK:\n"
            "Explain the following source code in detail.\n\n"
            "Your explanation must cover:\n"
            "1. The overall purpose of the code.\n"
            "2. How each major section or function works.\n"
            "3. Key programming concepts used.\n"
            "4. Any important design patterns or algorithms present.\n\n"
            "Respond using clear, professional Markdown."
        )
        return self._build_prompt(task, source_code, programming_language)

    def build_bug_detection_prompt(
        self,
        source_code: str,
        programming_language: str,
    ) -> str:
        """Build a prompt focused on detecting bugs and issues.

        The AI is asked to identify genuine bugs, potential runtime
        errors, logic flaws, and edge-case vulnerabilities.

        Args:
            source_code:          The code to analyse.
            programming_language: Language of the source code.

        Returns:
            str: The assembled bug-detection prompt.
        """
        task = (
            "YOUR TASK:\n"
            "Analyse the following source code for bugs, errors, and "
            "potential issues.\n\n"
            "For each bug found, provide:\n"
            "1. **Bug description** — what is wrong.\n"
            "2. **Location** — where in the code it occurs.\n"
            "3. **Severity** — Critical, Major, Minor, or Suggestion.\n"
            "4. **Fix recommendation** — how to resolve it.\n\n"
            "If no bugs are found, respond with exactly:\n"
            "\"No bugs detected.\"\n\n"
            "Do NOT invent or fabricate bugs. Report only genuine issues.\n"
            "Respond using clear, professional Markdown."
        )
        return self._build_prompt(task, source_code, programming_language)

    def build_correction_prompt(
        self,
        source_code: str,
        programming_language: str,
    ) -> str:
        """Build a prompt focused on producing corrected code.

        The AI is asked to fix any genuine bugs while preserving
        the original intended functionality.

        Args:
            source_code:          The code to correct.
            programming_language: Language of the source code.

        Returns:
            str: The assembled correction prompt.
        """
        lang_lower = programming_language.lower()
        task = (
            "YOUR TASK:\n"
            "Review the following source code and produce a corrected "
            "version.\n\n"
            "Rules:\n"
            "1. Fix all genuine bugs and issues.\n"
            "2. Preserve the original intended functionality exactly.\n"
            "3. Do NOT add unnecessary features or refactoring.\n"
            "4. Include brief inline comments for every fix you make.\n"
            "5. If the code is already correct, return it unchanged and "
            "state: \"No corrections needed.\"\n\n"
            "Respond with ONLY the corrected code inside a fenced "
            f"Markdown code block using ```{lang_lower}```."
        )
        return self._build_prompt(task, source_code, programming_language)

    def build_full_analysis_prompt(
        self,
        source_code: str,
        programming_language: str,
    ) -> str:
        """Build a comprehensive analysis prompt (primary V1 prompt).

        This is the main prompt used by the application.  It asks the
        AI to explain the code, detect bugs, and provide corrected code
        in a single, structured response.

        The AI is instructed to respond using **exactly** this Markdown
        structure::

            ## Code Explanation
            <explanation>

            ## Bugs Found
            <bugs or "No bugs detected.">

            ## Corrected Code
            ```<language>
            <corrected code>
            ```

        Args:
            source_code:          The code to analyse.
            programming_language: Language of the source code.

        Returns:
            str: The assembled full-analysis prompt.
        """
        lang_lower = programming_language.lower()
        task = (
            "YOUR TASK:\n"
            "Perform a comprehensive analysis of the following source "
            "code. Your response MUST follow this exact structure:\n\n"
            "## Code Explanation\n"
            "<Provide a clear, detailed explanation of what the code "
            "does, how it works, and which concepts it uses.>\n\n"
            "## Bugs Found\n"
            "<List every genuine bug with its description, location, "
            "severity, and fix recommendation. If there are no bugs, "
            "write exactly: \"No bugs detected.\">\n\n"
            "## Corrected Code\n"
            f"```{lang_lower}\n"
            "<Provide the full corrected source code. If no corrections "
            "are needed, return the original code unchanged.>\n"
            "```\n\n"
            "IMPORTANT:\n"
            "- Do NOT include any text outside the three sections above.\n"
            "- Do NOT invent bugs that do not exist.\n"
            "- Preserve the original functionality of the code.\n"
            "- Use professional, well-structured Markdown."
        )
        return self._build_prompt(task, source_code, programming_language)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Module-Level Convenience Singleton
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

prompt_builder = PromptBuilder()
"""Module-level singleton for convenient imports.

Usage:
    >>> from ai.prompts import prompt_builder
    >>> prompt = prompt_builder.build_full_analysis_prompt(code, lang)
"""
