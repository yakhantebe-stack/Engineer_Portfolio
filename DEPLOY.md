DEPLOY THIS FOLDER AS ONE VERCEL WEBSITE

1. Unzip this download. Open the vercel-ready folder in VS Code.
2. Put its CONTENTS in your GitHub repository root (app.py, core.py,
   requirements.txt, pyproject.toml, support/, automations/, documents/,
   portfolio/, screenshots/, etc.). Do not upload the ZIP itself.
   Use a new repository if you want to keep your original project untouched.
3. Import that repository into Vercel. Root Directory: blank/default.
   Framework: FastAPI (or leave automatic detection enabled).
   Clear custom Build Command and Output Directory overrides.
4. Deploy. The homepage links to /support/, /automations/, /documents/.

TRY LOCALLY FIRST (Windows / VS Code terminal)
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app:app --reload
Open http://127.0.0.1:8000

AI CONFIGURATION
Ordinary CRUD, document upload/search, and template workflows work without AI.
AI reply drafting, AI workflow steps, and AI answers require a provider API key.
Set OPENAI_API_KEY or ANTHROPIC_API_KEY in Vercel Environment Variables, then
redeploy. Never commit .env or API keys. API usage is billed separately.

HOSTING LIMITS
Vercel: SQLite files live in /tmp and may reset or differ across instances.
This is a shared demo, not private user storage. Do not enter private documents.
Automatic background schedules are disabled on Vercel; manual runs work.
For durable SQLite data and schedules, run uvicorn app:app on an always-on
Python server with one worker and a persistent volume. Set SUPPORT_DB_PATH,
AUTOMATIONS_DB_PATH and DOCUMENTS_DB_PATH to files on that volume.

GAME
The original Godot game is not included in this web deployment package.
Its source must be exported to Web from Godot before it can run in a browser.
The original uploaded ZIP still contains your game source and other files.

VALIDATION
Run python -m pytest tests -q. Provider calls are mocked in the tests.
This package was checked locally; a successful Vercel build still needs to be
confirmed after you push these files and deploy.
