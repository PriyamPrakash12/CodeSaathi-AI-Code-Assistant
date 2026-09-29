# Workbench — AI Code Assistant

A four-mode AI code assistant with a browser UI: **Explain**, **Generate**,
**Fix**, and **Refactor**. Built as a beginner project to practice both web
app basics and prompt engineering.

## Setup

```bash
pip install -r requirements.txt --break-system-packages
export ANTHROPIC_API_KEY="your-key-here"
python app.py
```

Then open **http://localhost:5000** in your browser.

## Project structure

```
ai-code-assistant/
├── app.py              # Flask backend — all prompt logic lives here
├── requirements.txt
├── templates/
│   └── index.html       # Page structure
└── static/
    ├── style.css         # Workshop-style dark UI
    └── script.js         # Mode switching + API calls
```

## The four modes

| Mode | Input | Output |
|---|---|---|
| **Explain** | code + skill level | summary, line-by-line breakdown, issues, suggestions |
| **Generate** | plain-English description | new code + explanation + assumptions |
| **Fix** | broken code + error message | diagnosis + corrected code + what changed |
| **Refactor** | code + optional goal | improved code + list of changes with reasoning |

## Prompt engineering techniques used (see `app.py`)

- **Role prompting** — `SYSTEM_PROMPT` sets a consistent "senior engineer" persona
- **Audience-adaptive prompting** — Explain mode changes depth based on skill level
- **Few-shot prompting** — Generate mode includes one worked example to anchor format
- **Chain-of-thought** — Explain mode is told to reason WHAT → HOW → WHY before answering
- **Grounding** — Fix mode is given the actual error message, narrowing the solution space
- **Goal-directed constraints** — Refactor mode takes an explicit goal so the model doesn't make unrelated changes
- **Structured output** — every mode forces a strict JSON schema, parsed server-side

## Things to try next

1. **Compare prompt versions**: edit one of the `build_*_prompt()` functions, remove a technique (e.g. the few-shot example in Generate), and see how output quality/consistency changes.
2. **Add a "test generation" mode**: given a function, generate unit tests for it.
3. **Add conversation memory**: let the user ask a follow-up like "make this shorter" and pass conversation history back to the model instead of starting fresh.
4. **Streaming responses**: use Anthropic's streaming API so code appears token-by-token instead of all at once.
5. **Syntax highlighting**: drop in a library like Prism.js or highlight.js to color the code blocks in the output pane.
6. **Retry on bad JSON**: if `json.loads` fails, send the raw output back with "this wasn't valid JSON, fix it" and retry once.

## Notes

- The Anthropic API key stays server-side in `app.py` — it's never sent to the browser, which is the correct way to handle secrets in a real app.
- This is a learning project, not production-hardened: there's no rate limiting, auth, or input sanitization beyond basic HTML-escaping in the UI.
