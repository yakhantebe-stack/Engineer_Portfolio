"""Shared LLM gateway and SQLite utilities. All keys are server-side only."""
from __future__ import annotations
import os, sqlite3
from pathlib import Path
from typing import Any
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / '.env')

ROOT = Path(__file__).resolve().parent

def connect(name: str) -> sqlite3.Connection:
    override = os.getenv(f'{name.upper()}_DB_PATH')
    data_root = Path('/tmp/yakha-portfolio') if os.getenv('VERCEL') else ROOT / 'data'
    path = Path(override) if override else data_root / f'{name}.sqlite3'
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=15, check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA foreign_keys=ON')
    return db

def provider() -> str:
    if os.getenv('ANTHROPIC_API_KEY'):
        return 'Anthropic Claude'
    if os.getenv('OPENAI_API_KEY'):
        return 'OpenAI'
    if os.getenv('OLLAMA_MODEL'):
        return 'Ollama (local)'
    return 'Not configured'

async def generate(system: str, user: str, *, max_tokens: int = 750) -> str:
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    ollama_model = os.getenv('OLLAMA_MODEL')
    if not (anthropic_key or openai_key or ollama_model):
        raise HTTPException(status_code=503, detail='AI is not configured. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or OLLAMA_MODEL in your .env and restart the server.')
    try:
        async with httpx.AsyncClient(timeout=65) as client:
            if anthropic_key:
                response = await client.post('https://api.anthropic.com/v1/messages',
                    headers={'x-api-key':anthropic_key,'anthropic-version':'2023-06-01','content-type':'application/json'},
                    json={'model':os.getenv('ANTHROPIC_MODEL','claude-sonnet-4-5'),'max_tokens':max_tokens,'system':system,
                          'messages':[{'role':'user','content':user}]})
                response.raise_for_status()
                parts = response.json().get('content', [])
                return '\n'.join(part.get('text','') for part in parts if part.get('type')=='text').strip()
            if ollama_model and not openai_key:
                response = await client.post('http://127.0.0.1:11434/api/chat',
                    json={'model':ollama_model,'stream':False,'messages':[{'role':'system','content':system},{'role':'user','content':user}],
                          'options':{'num_predict':max_tokens}})
                response.raise_for_status()
                return response.json()['message']['content'].strip()
            response = await client.post('https://api.openai.com/v1/chat/completions',
                headers={'Authorization':f'Bearer {openai_key}'},
                json={'model':os.getenv('OPENAI_MODEL','gpt-4.1-mini'),'max_tokens':max_tokens,
                      'messages':[{'role':'system','content':system},{'role':'user','content':user}]})
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content'].strip()
    except httpx.HTTPStatusError as exc:
        detail = f'AI provider returned HTTP {exc.response.status_code}. Check your API key, model name, and account credits.'
        raise HTTPException(status_code=502, detail=detail) from None
    except (httpx.RequestError, KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail=f'Could not contact or parse the AI provider: {str(exc)[:180]}') from None

async def embed(texts: list[str]) -> list[list[float]] | None:
    """Real semantic embeddings when OpenAI is configured; None => keyword retrieval."""
    key = os.getenv('OPENAI_API_KEY')
    ollama_model = os.getenv('OLLAMA_EMBED_MODEL')
    if not key and not ollama_model: return None
    if not texts: return None
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            if ollama_model and not key:
                response = await client.post('http://127.0.0.1:11434/api/embed',
                    json={'model':ollama_model,'input':texts})
                response.raise_for_status()
                return response.json()['embeddings']
            response = await client.post('https://api.openai.com/v1/embeddings',
                headers={'Authorization':f'Bearer {key}'},
                json={'model':os.getenv('EMBEDDING_MODEL','text-embedding-3-small'),'input':texts})
            response.raise_for_status()
            return [item['embedding'] for item in sorted(response.json()['data'], key=lambda d:d['index'])]
    except (httpx.HTTPError, KeyError, ValueError):
        return None

def asdicts(rows: Any) -> list[dict]:
    return [dict(row) for row in rows]
