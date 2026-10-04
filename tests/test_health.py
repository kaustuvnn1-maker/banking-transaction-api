def test_health_endpoint(api):
    r = api.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'
