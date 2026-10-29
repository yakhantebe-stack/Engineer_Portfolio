from fastapi.testclient import TestClient

def test_combined_website():
    import app as website
    with TestClient(website.app) as client:
        assert client.get('/').status_code == 200
        assert client.get('/style.css').status_code == 200
        for name in ('support', 'automations', 'documents'):
            page = client.get(f'/{name}/')
            assert page.status_code == 200
            assert f'/{name}/static/app.js' in page.text
            assert client.get(f'/{name}/static/app.js').status_code == 200
            assert client.get(f'/{name}/static/style.css').status_code == 200
            assert client.get(f'/{name}/api/health').json()['ok']
        assert len(client.get('/support/api/tickets').json()) == 3
        assert client.get('/documents/api/documents').json() == []
        workflows = client.get('/automations/api/workflows').json()
        wf = next(w for w in workflows if w['name'] == 'Feedback formatter')
        result = client.post(f"/automations/api/workflows/{wf['id']}/run", json={'text': 'Great service'})
        assert result.json()['status'] == 'success'
        hook = client.get(f"/automations/api/workflows/{wf['id']}/hook").json()['url']
        assert '/automations/api/hooks/' in hook

def test_serverless_schedule_guard(monkeypatch):
    monkeypatch.setenv('VERCEL', '1')
    import app as website
    with TestClient(website.app) as client:
        assert client.get('/api/health').json()['storage'] == 'temporary demo'
        response = client.post('/automations/api/workflows', json={
            'name': 'Scheduled task', 'steps': [{'type':'template', 'template':'{{input}}'}],
            'interval_minutes': 5, 'enabled': True})
        assert response.status_code == 422
