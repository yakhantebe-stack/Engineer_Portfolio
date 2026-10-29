"""One website: homepage plus three mounted FastAPI applications."""
import os
import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from support import app as support
from automations import app as automations
from documents import app as documents

BASE = Path(__file__).resolve().parent

def initialize():
    for module in (support, automations, documents):
        module.init_db()

@asynccontextmanager
async def lifespan(app):
    initialize()
    task = None if os.getenv('VERCEL') else asyncio.create_task(automations.scheduler_loop())
    yield
    if task:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

# Initialize at import too: API requests remain usable in ASGI hosts that do not run lifespan.
initialize()
app = FastAPI(title="Yakha Ntebe — Engineering Portfolio", lifespan=lifespan)

@app.get('/')
def home():
    return FileResponse(BASE / 'portfolio' / 'index.html')

@app.get('/style.css')
def stylesheet():
    return FileResponse(BASE / 'portfolio' / 'style.css', media_type='text/css')

@app.get('/setup')
def setup():
    return FileResponse(BASE / 'DEPLOY.md', media_type='text/plain')

@app.get('/api/health')
def health():
    return {'ok': True, 'storage': 'temporary demo' if os.getenv('VERCEL') else 'local SQLite',
            'scheduler': 'disabled on Vercel' if os.getenv('VERCEL') else 'running'}

app.mount('/screenshots', StaticFiles(directory=BASE / 'screenshots'), name='screenshots')
app.mount('/support', support.app)
app.mount('/automations', automations.app)
app.mount('/documents', documents.app)
