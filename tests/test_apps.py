"""Integration tests: real CRUD, persistence, retrieval and request plumbing.
Provider calls mocked: an API key is neither supplied nor billed during tests.
"""
import io
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def temp_databases(monkeypatch,tmp_path):
    for name in ('SUPPORT','AUTOMATIONS','DOCUMENTS'):
        monkeypatch.setenv(f'{name}_DB_PATH',str(tmp_path/f'{name.lower()}.sqlite3'))
    monkeypatch.delenv('ANTHROPIC_API_KEY',raising=False)
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    monkeypatch.delenv('OLLAMA_MODEL',raising=False)
    monkeypatch.delenv('OLLAMA_EMBED_MODEL',raising=False)

def test_support_crud_and_draft(monkeypatch):
    from support import app as module
    async def fake_generate(*args,**kwargs):return 'Hello Avery, please visit Billing settings.'
    monkeypatch.setattr(module,'generate',fake_generate)
    with TestClient(module.app) as c:
        assert c.get('/').status_code==200
        assert len(c.get('/api/tickets').json())==3
        t=c.post('/api/tickets',json={'customer':'Demo','email':'demo@example.com','subject':'Help please','body':'I need some help with my account','priority':'high'})
        assert t.status_code==201
        id=t.json()['id']
        assert c.patch(f'/api/tickets/{id}',json={'status':'resolved'}).status_code==200
        assert c.get(f'/api/tickets/{id}').json()['ticket']['status']=='resolved'
        assert c.post(f'/api/tickets/{id}/draft').json()['draft'].startswith('Hello')
        assert len(c.get(f'/api/tickets/{id}').json()['notes'])==1
        assert c.post('/api/articles',json={'title':'New support policy','body':'Human escalation required'}).status_code==201
        assert c.get('/api/tickets/99999').status_code==404

def test_workflow_engine_manual_run_and_failure(monkeypatch):
    from automations import app as module
    async def fake_generate(system,user,**kw):return 'AI transformed the input'
    monkeypatch.setattr(module,'generate',fake_generate)
    with TestClient(module.app) as c:
        r=c.post('/api/workflows',json={'name':'Test pipeline','description':'Testing','steps':[{'type':'template','template':'Here: {{input}}'},{'type':'ai','instruction':'Rewrite the input'}], 'interval_minutes':5,'enabled':True})
        assert r.status_code==201, r.text
        id=r.json()['id']
        v=c.post(f'/api/workflows/{id}/run',json={'text':'check this'})
        assert v.json()['status']=='success',v.text
        assert v.json()['output']=='AI transformed the input'
        assert c.get('/api/runs').json()[0]['trigger']=='manual'
        assert c.get(f'/api/workflows/{id}/hook').json()['url'].endswith(f'/{id}/'+c.get(f'/api/workflows/{id}/hook').json()['url'].split('/')[-1])
        assert c.patch(f'/api/workflows/{id}/schedule',json={'enabled':False}).status_code==200
        assert c.delete(f'/api/workflows/{id}').status_code==200
        assert c.post('/api/workflows',json={'name':'Broken template','steps':[{'type':'template','template':'No variable'}]}).status_code==422

def test_document_upload_search_and_ask(monkeypatch):
    from documents import app as module
    async def fake_generate(*args,**kwargs):return 'Renewals occur on the 15th [1].'
    async def no_embed(x):return None
    monkeypatch.setattr(module,'generate',fake_generate)
    monkeypatch.setattr(module,'embed',no_embed)
    with TestClient(module.app) as c:
        upload=c.post('/api/documents',files={'file':('policy.txt',b'Company policies: renewals occur on the 15th of each month. Refunds require approval.','text/plain')})
        assert upload.status_code==201, upload.text
        id=upload.json()['id']
        assert upload.json()['search_mode']=='keyword'
        result=c.post('/api/ask',json={'question':'When do renewals occur?','document_id':id})
        assert result.status_code==200,result.text
        assert '[1]' in result.json()['answer']
        assert result.json()['sources'][0]['name']=='policy.txt'
        assert c.get('/api/search',params={'q':'renewals'}).json()['results'][0]['score']>0
        assert c.get(f'/api/documents/{id}/chunks').json()['chunks']
        assert c.delete(f'/api/documents/{id}').status_code==200
        assert c.post('/api/ask',json={'question':'What now?'}).status_code==404
        assert c.post('/api/documents',files={'file':('bad.exe',b'hello')}).status_code==415

def test_missing_ai_provider_returns_503():
    from core import generate
    from fastapi import HTTPException
    import asyncio
    with pytest.raises(HTTPException) as err:asyncio.run(generate('system','user'))
    assert err.value.status_code==503
