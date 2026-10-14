# Codebase Onboarding Agent

A small Streamlit app that explores a public GitHub repository or an uploaded ZIP. It provides three repository tools (`list_files`, `read_file`, and `search_code`) and a Gemini-powered chat agent that uses those tools to answer questions with source file and line references.

## Features

- Load a public GitHub repository URL or upload a repository ZIP.
- Browse the repository file list.
- Ask questions in a persistent chat.
- Agent tools: list files/directories, read a file or line range, and search source text.
- Tool output includes exact paths and original line numbers for citations.
- Basic protections against path traversal, symbolic links, secrets, and oversized archives/files.

## Run locally

Python 3.11+ recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Google AI API key:

```env
GOOGLE_API_KEY=your_real_key
GOOGLE_MODEL_NAME=gemini-3-flash-preview
```

Run:

```bash
streamlit run UIapp.py
```

## Deploy to Streamlit Community Cloud

1. Push these project files to GitHub. Do **not** upload `.env` or any API key.
2. In Streamlit Community Cloud, create/deploy the app and set the main file to `UIapp.py`.
3. Open **App settings → Secrets** and add:

```toml
GOOGLE_API_KEY = "your_real_key"
GOOGLE_MODEL_NAME = "gemini-3-flash-preview"
```

4. Streamlit Cloud installs packages from `requirements.txt` automatically.

## Notes and limitations

- GitHub URL loading supports public repositories. Upload a ZIP for private repositories.
- `search_code` currently provides literal text search. Semantic search is not implemented in this version.
- Citation correctness is encouraged by the prompt and exact tool output, but an LLM can still make mistakes; verify citations against the displayed source.
- This version covers the first three agreed project tasks: repository tools, tool-using agent, and Streamlit chat. MCP, code-aware RAG, test execution, and the 20-question evaluation suite are separate later tasks.
