## Deploy the combined website

Start with **DEPLOY.md** for the updated one-website setup. The instructions below describe the original three-process local setup.

# AI Engineering Portfolio — three working full-stack projects

These are **three real, separate browser applications with server-side APIs and SQLite persistence**. They are portfolio-grade local demos, not pretend screenshots or fake AI output.

## Run all three (Windows, macOS or Linux)

You'll need **Python 3.10+**, an internet connection to install dependencies, and either a provider API key **or a local Ollama model** if you want AI responses.

1. Unzip the folder, then open a terminal *inside* `AI_Engineer_Portfolio`.
2. Create an environment: `python -m venv .venv`.
3. Activate it:
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`
   - Windows CMD: `.venv\Scripts\activate.bat`
   - macOS/Linux: `source .venv/bin/activate`
4. Install: `python -m pip install -r requirements.txt`
5. Copy `.env.example` to `.env`. For AI responses, add **one** of: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `OLLAMA_MODEL` (see free setup below). If you skip these, CRUD, scheduling, template workflows, search, uploads, and previews still work; AI generation displays an explicit configuration error.
6. Start: `python start.py`
7. Open the sites:

| Project | Local URL | Core features |
| --- | --- | --- |
| **ResolveDesk** | http://127.0.0.1:8001 | Support tickets, statuses, knowledge base, AI draft replies, history |
| **FlowForge** | http://127.0.0.1:8002 | Multi-step workflow builder, AI steps, scheduled jobs, inbound/outbound webhooks, run logs |
| **Atlas** | http://127.0.0.1:8003 | PDF/TXT/MD ingestion, retrieval, grounded Q&A, source citations, history |

Use **Ctrl+C** to stop. The databases are created automatically under `data/` and survive restarts.

### Alternative: Docker Compose

Make your `.env`, then run `docker compose up --build`. The apps are intentionally bound to **localhost**, not exposed publicly.

## Project 1 — ResolveDesk

**Stack:** FastAPI + SQLite + vanilla HTML/CSS/JavaScript + Anthropic Claude / OpenAI.

- Three seeded demo tickets plus create-ticket form; status controls and searchable inbox.
- Knowledge base: add/delete company policy articles.
- **Draft with AI** generates a real response using ticket and knowledge-base context, stores it as an internal draft, and **never sends email automatically**.
- Internal ticket notes, overview metrics, and API docs at `/docs`.

**Demo:** Open ticket `Invoice discrepancy`, click **Draft with AI**, examine its response, add an internal note, then mark the ticket pending. Never claim a draft was delivered to a real customer.

## Project 2 — FlowForge

**Stack:** FastAPI + Python asyncio scheduler + SQLite + Anthropic/OpenAI.

- Create pipelines of up to eight steps: `template` (substitute `{{input}}`), `ai` (real provider call), `webhook` (HTTP POST).
- Manually run and inspect input, output, status, failures and timestamps.
- Persistent interval settings (5/15/60/1440 minutes in UI) and scheduler poll (every ~10 seconds); resuming on startup.
- Secret inbound webhook endpoint for each workflow. Use **Hook** to copy it. Anyone holding that URL can invoke the workflow.
- Outbound webhooks require HTTPS and a hostname listed in `AUTOMATION_ALLOWED_WEBHOOK_HOSTS` (comma-separated) in `.env`. Do not allow untrusted destinations.

**Demo without an API key:** Run seeded **Feedback formatter**, enter customer feedback, and inspect its transformed output. **Demo with a key:** Run **Lead intelligence**, then create a two-step AI → template workflow.

**Important limitation:** This is a **single-process educational scheduler**. Don't scale the scheduler horizontally as-is; in production use a dedicated task queue and distributed coordination, plus retries, idempotency keys and task timeouts.

## Project 3 — Atlas Documents

**Stack:** FastAPI + SQLite + pypdf + Anthropic/OpenAI + optional OpenAI embeddings.

- Upload and parse PDF, TXT or Markdown, up to 5 MB and 180 extracted chunks.
- Search documents and retrieve relevant passages. Without an OpenAI key this uses keyword overlap. With an OpenAI key it additionally computes **real embeddings** and cosine similarity.
- Ask natural-language questions; a real LLM generates an answer with passage references such as `[1]`, while the UI shows filenames, pages and matching excerpts.
- Inspect extracted passages, filter questions by document, delete uploaded documents, revisit question history.
- Text extraction does **not** OCR scanned image-only PDFs.

**Demo:** Upload `samples/company_handbook.txt`; ask **“What is the escalation procedure for billing disputes?”**. Compare the answer and its source passage. With no AI key, use Preview Text to verify extraction.

## Free AI without a paid API key (optional)

If you have enough laptop RAM and disk space, install [Ollama](https://ollama.com), then in a separate terminal run:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
ollama serve  # only if Ollama is not already running
```

Add `OLLAMA_MODEL=llama3.2:3b` and `OLLAMA_EMBED_MODEL=nomic-embed-text` to `.env`. Restart `python start.py`. All three apps can now call your **local model**, while document embeddings run locally too. Ollama must be running; response speed depends on your laptop. If using Docker, the Ollama endpoint is not automatically available inside containers; use the Python launch for this local setup.

## Environment settings

| Setting | Description |
| --- | --- |
| `ANTHROPIC_API_KEY` | Optional. If set, Claude handles text generation. |
| `ANTHROPIC_MODEL` | Claude model ID; edit as supported by your account. |
| `OPENAI_API_KEY` | Optional. OpenAI is used for generation if Anthropic isn't set, and for document embeddings if available. |
| `OPENAI_MODEL` | OpenAI text model ID. |
| `EMBEDDING_MODEL` | OpenAI embedding model ID. |
| `OLLAMA_MODEL` | Optional free local model, e.g. `llama3.2:3b`, served on localhost port 11434. |
| `OLLAMA_EMBED_MODEL` | Optional free local embedding model, e.g. `nomic-embed-text`. |
| `AUTOMATION_ALLOWED_WEBHOOK_HOSTS` | Explicit outbound webhook host allowlist. |

**API keys must live in the backend `.env`, not in browser JavaScript.** API usage may incur provider charges. Current model availability and billing are determined by your provider account.

## Automated tests

```bash
python -m pytest -q
```

Tests exercise endpoints for ticket management, AI draft plumbing, workflow execution and logs, document upload, search, source-grounded response plumbing and error paths. AI calls are **mocked in tests** to avoid consuming real API credits; manual testing with your own key is still needed to verify the provider connection.

## Portfolio use and professional honesty

These projects are starter systems that you can test, improve, deploy responsibly, and explain. They **aren't deployed production products** and **do not demonstrate that you used Claude Code daily**. For the vacancy, genuinely work with Claude Code to customize, refactor, debug and test the code; record what you personally changed so you can discuss it accurately.

**Suggested enhancements for a production-oriented portfolio:** authentication/RBAC, rate limiting, encrypted storage, secret management, audit logs, monitoring, CI/CD, database migrations, background worker for AI, PDF abuse protection, retry/idempotency policies, request tracing, and deployment security. Start locally; **do not expose these unauthenticated demo APIs publicly**, especially when API keys are connected.

## Architecture

```
Browser UI (3 independent apps)
       | REST / JSON
       v
FastAPI backend (each app) -> SQLite databases (separate)
       |                        |
       v                        v
 shared LLM gateway        persisted objects
       |
       +---- Anthropic Messages API (Claude)
       +---- OpenAI Chat Completions + Embeddings API
       +---- Ollama local Chat + Embeddings API
```

- `support/app.py` — tickets, KB, reviewable AI replies
- `automations/app.py` — pipeline steps, timer, inbound hooks, runs
- `documents/app.py` — parse, chunk, embed/retrieve, grounded answers
- `core.py` — provider calls, configuration, DB helpers
- `*/static/` — independent frontends
- `tests/` — endpoint integration tests
- `start.py` — start all three with one command

## Included example data

- ResolveDesk and FlowForge create seeded demo objects on the first run.
- Atlas includes a **sample company handbook** for uploading. Sample content is fictitious and for demonstration.

## Portfolio homepage

Open `portfolio/index.html` in a browser for a static, presentable project showcase. It uses the included real interface screenshots, project descriptions and an architecture section. **This is not a deployed live demo.** The three interactive apps need their Python servers, as described above.

To demonstrate your own development honestly, customize a project in Claude Code, run the tests, commit the changes to your GitHub repository and document exactly what you did. During an interview, show a real feature, trace it from the UI through the API to the database, and explain its limitations.
