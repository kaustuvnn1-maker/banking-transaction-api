import os, pytest, requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
@pytest.mark.rate_limit
@pytest.mark.skipif(os.getenv('RUN_RATE_LIMIT_TESTS')!='1',reason='Enable with RUN_RATE_LIMIT_TESTS=1')
def test_nginx_rate_limit():
    statuses=[requests.get('https://localhost:8443/api/health',verify=False,timeout=10).status_code for _ in range(40)]
    assert 429 in statuses
