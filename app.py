"""
AI Code Assistant — Flask backend
-----------------------------------
A small multi-mode code assistant using Google's Gemini API.

Modes:
  - explain   : explain what code does (audience-adaptive)
  - generate  : write code from a plain-English description
  - fix       : take broken code + an error message, return a fix
  - refactor  : improve existing code, explain what changed and why

The Gemini API key is read server-side only — it is never exposed
to the browser.

Setup:
    pip install flask google-genai

Set environment variable:
    GEMINI_API_KEY="your-key-here"

Then run:
    python app.py

Open:
    http://localhost:5000
"""

import os
import json

from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types


# ---------------------------------------------------------------------------
# APP + GEMINI CLIENT
# ---------------------------------------------------------------------------

app = Flask(__name__)

# Gemini automatically reads GEMINI_API_KEY from the environment
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

# Gemini model
MODEL = "gemini-3.8-flash"


# ---------------------------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a precise, helpful senior software engineer
acting as an AI code assistant embedded in a developer tool.

You always respond with a single valid JSON object matching the schema
provided in the user's request.

Do not use markdown fences.
Do not write prose before or after the JSON.
"""


# ---------------------------------------------------------------------------
# PROMPT BUILDERS
# ---------------------------------------------------------------------------

def build_explain_prompt(code: str, skill_level: str) -> str:
    """Audience-adaptive prompting + structured output."""

    return f"""Explain the following code for a "{skill_level}" level programmer.

Analyze the code carefully:

1. Identify WHAT the code does.
2. Identify HOW it works.
3. Explain WHY the code might be written this way.

Then produce the final answer.

Respond ONLY with JSON in this schema:

{{
  "summary": "one or two sentence plain-English summary",
  "line_by_line": ["explanation of each meaningful line or block"],
  "potential_issues": ["bugs, edge cases, bad practices, or [] if none"],
  "suggestions": ["improvements or best practices, or [] if none"]
}}

Code:
{code}
"""


def build_generate_prompt(description: str, language: str) -> str:
    """Few-shot example + explicit constraints."""

    few_shot = """Example:

Description: "a function that reverses a string"
Language: python

Response:
{
  "code": "def reverse_string(s):\\n    return s[::-1]",
  "explanation": "Uses Python slice notation with a step of -1 to reverse the string.",
  "assumptions": ["Input is a standard Python string."]
}
"""

    return f"""{few_shot}

Now generate code for this request.

Description: "{description}"
Language: {language}

Requirements:
- Write clean, idiomatic {language}.
- Include minimal inline comments only where non-obvious.
- Do not add unnecessary error handling.
- Keep the solution appropriate for the requested problem.

Respond ONLY with JSON in this schema:

{{
  "code": "the generated code as a single string with \\n line breaks",
  "explanation": "1-2 sentence explanation of the approach",
  "assumptions": [
    "any assumptions made about ambiguous parts of the request, or []"
  ]
}}
"""


def build_fix_prompt(
    code: str,
    error_message: str,
    language: str
) -> str:
    """Error-message grounding."""

    return f"""The following {language} code produces this error:

Error:
{error_message}

Code:
{code}

Diagnose the root cause, then produce a corrected version of the code.

Change as little as possible while fully fixing the issue.

Respond ONLY with JSON in this schema:

{{
  "diagnosis": "1-2 sentence explanation of what is actually wrong",
  "fixed_code": "the corrected code as a single string with \\n line breaks",
  "what_changed": [
    "short bullet points describing each change made"
  ]
}}
"""


def build_refactor_prompt(
    code: str,
    language: str,
    goal: str
) -> str:
    """Goal-directed refactoring."""

    goal_text = (
        goal.strip()
        if goal.strip()
        else "general readability, clarity, and best practices"
    )

    return f"""Refactor the following {language} code with this specific goal:

"{goal_text}"

Preserve existing behavior.

Do not change functionality unless the current behavior is clearly a bug.

Code:
{code}

Respond ONLY with JSON in this schema:

{{
  "refactored_code": "the improved code as a single string with \\n line breaks",
  "changes": [
    {{
      "change": "short description of one change",
      "why": "why this improves the code"
    }}
  ]
}}
"""


# ---------------------------------------------------------------------------
# GEMINI API CALL
# ---------------------------------------------------------------------------

def call_gemini(prompt: str) -> dict:

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    raw = response.text.strip()

    try:
        return json.loads(raw)

    except json.JSONDecodeError:

        # Fallback in case Gemini returns unexpected formatting
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip()

        try:
            return json.loads(raw)

        except json.JSONDecodeError:

            return {
                "error": "Could not parse Gemini output as JSON",
                "raw": raw
            }


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/assist", methods=["POST"])
def assist():

    data = request.get_json(force=True)

    mode = data.get("mode")
    language = data.get("language", "python")


    # -----------------------------------------------------------------------
    # CHECK API KEY
    # -----------------------------------------------------------------------

    if not os.environ.get("GEMINI_API_KEY"):

        return jsonify({
            "error": "GEMINI_API_KEY is not set on the server."
        }), 500


    # -----------------------------------------------------------------------
    # SELECT PROMPT BASED ON MODE
    # -----------------------------------------------------------------------

    try:

        if mode == "explain":

            prompt = build_explain_prompt(
                data.get("code", ""),
                data.get("skill_level", "beginner")
            )


        elif mode == "generate":

            prompt = build_generate_prompt(
                data.get("description", ""),
                language
            )


        elif mode == "fix":

            prompt = build_fix_prompt(
                data.get("code", ""),
                data.get("error_message", ""),
                language
            )


        elif mode == "refactor":

            prompt = build_refactor_prompt(
                data.get("code", ""),
                language,
                data.get("goal", "")
            )


        else:

            return jsonify({
                "error": f"Unknown mode: {mode}"
            }), 400


        # -------------------------------------------------------------------
        # CALL GEMINI
        # -------------------------------------------------------------------

        result = call_gemini(prompt)

        return jsonify(result)


    # -----------------------------------------------------------------------
    # GEMINI / API ERROR
    # -----------------------------------------------------------------------

    except Exception as e:

        return jsonify({
            "error": f"Gemini API error: {str(e)}"
        }), 502


# ---------------------------------------------------------------------------
# START FLASK SERVER
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )