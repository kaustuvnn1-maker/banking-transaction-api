from __future__ import annotations
import os, time, uuid
from dataclasses import dataclass
import pytest, requests, urllib3
from dotenv import load_dotenv

load_dotenv('.env.test')
BASE_URL = os.getenv('API_BASE_URL', 'https://localhost:8443/api').rstrip('/')
REQUEST_DELAY = float(os.getenv('TEST_REQUEST_DELAY', '0.25'))
VERIFY_TLS = os.getenv('VERIFY_TLS', 'false').lower() == 'true'
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
DEFAULT_PASSWORD = 'TestPassword123!'

@dataclass
class UserContext:
    username: str
    password: str
    token: str
    user_id: int | None = None
    account_id: int | None = None
    @property
    def headers(self):
        return {'Authorization': f'Bearer {self.token}'}

class ApiClient:
    def __init__(self, session, base_url): self.session, self.base_url = session, base_url
    def request(self, method, path, **kwargs):
        time.sleep(REQUEST_DELAY)
        return self.session.request(method, f'{self.base_url}{path}', timeout=15, **kwargs)
    def get(self, path, **kwargs): return self.request('GET', path, **kwargs)
    def post(self, path, **kwargs): return self.request('POST', path, **kwargs)
    def patch(self, path, **kwargs): return self.request('PATCH', path, **kwargs)
    def options(self, path, **kwargs): return self.request('OPTIONS', path, **kwargs)

@pytest.fixture(scope='session')
def api():
    session = requests.Session(); session.verify = VERIFY_TLS
    yield ApiClient(session, BASE_URL)
    session.close()

@pytest.fixture
def unique_username(): return f'pytest_{uuid.uuid4().hex[:12]}'

@pytest.fixture
def user_factory(api):
    def create_user(balance=None, username=None, password=DEFAULT_PASSWORD, account_name=None):
        username = username or f'pytest_{uuid.uuid4().hex[:12]}'
        r = api.post('/auth/register', json={'username': username, 'password': password})
        assert r.status_code in (200, 201), r.text
        data = r.json(); user_id = data.get('userID') or data.get('user_id')
        r = api.post('/auth/login', json={'username': username, 'password': password})
        assert r.status_code == 200, r.text
        user = UserContext(username, password, r.json()['access_token'], user_id=user_id)
        if balance is not None:
            r = api.post('/accounts', headers=user.headers, json={'account_holder_name': account_name or f'{username} Account', 'balance': str(balance)})
            assert r.status_code in (200, 201), r.text
            user.account_id = r.json()['account_id']
        return user
    return create_user

@pytest.fixture
def admin_user(api):
    username, password = os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD')
    if not username or not password: pytest.skip('ADMIN_USERNAME and ADMIN_PASSWORD not configured.')
    r = api.post('/auth/login', json={'username': username, 'password': password})
    assert r.status_code == 200, r.text
    return UserContext(username, password, r.json()['access_token'])
