# CodeSaathi — AI Code Assistant

A four-mode AI code assistant with a browser UI: **Explain**, **Generate**, **Fix**, and **Refactor**.

Built as a beginner project to practice web application development, prompt engineering, structured AI output, and integration with Google's Gemini API.

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

On Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Set your Gemini API key

On Windows Command Prompt:

```cmd
set GEMINI_API_KEY=your-key-here
```

On Windows PowerShell:

```powershell
$env:GEMINI_API_KEY="your-key-here"
```

On macOS/Linux:

```bash
export GEMINI_API_KEY="your-key-here"
```

### 4. Start the application

```bash
python app.py
```

Then open:

**http://localhost:5000**

## Project Structure

```text
ai-code-assistant/
├── app.py                  # Flask backend and prompt logic
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Page structure
└── static/
    ├── style.css           # UI styling
    └── script.js           # Mode switching and API calls
```

## The Four Modes

| Mode         | Input                       | Output                                               |
| ------------ | --------------------------- | ---------------------------------------------------- |
| **Explain**  | Code + skill level          | Summary, line-by-line breakdown, issues, suggestions |
| **Generate** | Plain-English description   | New code, explanation, assumptions                   |
| **Fix**      | Broken code + error message | Diagnosis, corrected code, changes made              |
| **Refactor** | Code + optional goal        | Improved code, changes and reasoning                 |

## Prompt Engineering Techniques Used

The prompt engineering techniques are implemented in `app.py`.

* **Role prompting** — `SYSTEM_PROMPT` establishes a consistent senior software engineer role.
* **Audience-adaptive prompting** — Explain mode adjusts the explanation according to the user's skill level.
* **Few-shot prompting** — Generate mode includes a worked example to demonstrate the expected output format.
* **Structured analysis** — Explain mode asks the model to examine the code through WHAT → HOW → WHY.
* **Grounding** — Fix mode provides the actual error message together with the code to help identify the root cause.
* **Goal-directed constraints** — Refactor mode accepts a specific goal and instructs the model to preserve existing behavior.
* **Structured output** — The application requests JSON responses and parses the returned JSON server-side.
* **Server-side API key handling** — The Gemini API key is kept on the backend and is never exposed to the browser.

## Things to Try Next

1. **Compare prompt versions**
   Edit one of the `build_*_prompt()` functions, remove a technique such as the few-shot example in Generate mode, and compare the resulting output quality and consistency.

2. **Add a Test Generation mode**
   Given a function or class, generate appropriate unit tests for it.

3. **Add Conversation Memory**
   Allow follow-up requests such as "make this shorter" by passing relevant conversation history back to Gemini.

4. **Add Streaming Responses**
   Stream Gemini responses so generated code appears progressively instead of waiting for the complete response.

5. **Add Syntax Highlighting**
   Use a library such as Prism.js or highlight.js to improve the presentation of generated code.

6. **Retry Invalid JSON**
   If `json.loads()` fails, send the malformed output back to the model with an instruction to return valid JSON and retry once.

## Notes

* The Gemini API key is stored server-side through the `GEMINI_API_KEY` environment variable and is never sent to the browser.
* The API key should not be committed to Git.
* `.env` files and virtual environments are excluded through `.gitignore`.
