from datetime import datetime, timedelta, timezone
import os, jwt, pytest

def test_user_can_register_and_login(api, unique_username):
    p='TestPassword123!'; r=api.post('/auth/register',json={'username':unique_username,'password':p}); assert r.status_code in (200,201)
    r=api.post('/auth/login',json={'username':unique_username,'password':p}); assert r.status_code==200; assert 'access_token' in r.json()

def test_duplicate_username_rejected(api, unique_username):
    p={'username':unique_username,'password':'TestPassword123!'}; assert api.post('/auth/register',json=p).status_code in (200,201); assert api.post('/auth/register',json=p).status_code==409

def test_wrong_password_rejected(api,user_factory):
    u=user_factory(); assert api.post('/auth/login',json={'username':u.username,'password':'WrongPassword123!'}).status_code==401

def test_unknown_username_rejected(api): assert api.post('/auth/login',json={'username':'user_that_does_not_exist_987','password':'WrongPassword123!'}).status_code==401

def test_protected_endpoint_without_token(api): assert api.get('/accounts').status_code==401

def test_invalid_token_rejected(api): assert api.get('/accounts',headers={'Authorization':'Bearer definitely-invalid-token'}).status_code==401

def test_tampered_jwt_rejected(api,user_factory):
    u=user_factory(); parts=u.token.split('.'); sig=parts[2]; sig=('A' if sig[0]!='A' else 'B')+sig[1:]; token=f'{parts[0]}.{parts[1]}.{sig}'
    assert api.get('/accounts',headers={'Authorization':f'Bearer {token}'}).status_code==401

def test_expired_jwt_rejected(api,user_factory):
    secret=os.getenv('JWT_SECRET_KEY')
    if not secret: pytest.skip('JWT_SECRET_KEY not loaded from .env.test')
    u=user_factory(); payload=jwt.decode(u.token,options={'verify_signature':False}); now=datetime.now(timezone.utc)
    token=jwt.encode({'sub':payload['sub'],'username':payload.get('username'),'iat':now-timedelta(minutes=10),'exp':now-timedelta(minutes=5)},secret,algorithm='HS256')
    assert api.get('/accounts',headers={'Authorization':f'Bearer {token}'}).status_code==401

def test_public_registration_cannot_create_admin(api,unique_username):
    p='TestPassword123!'; r=api.post('/auth/register',json={'username':unique_username,'password':p,'role':'ADMIN'})
    if r.status_code==422: return
    assert r.status_code in (200,201); token=api.post('/auth/login',json={'username':unique_username,'password':p}).json()['access_token']
    assert api.get('/transactions',headers={'Authorization':f'Bearer {token}'}).status_code==403

def test_sql_injection_like_login_does_not_bypass_auth(api): assert api.post('/auth/login',json={'username':"' OR 1=1 --",'password':"' OR 1=1 --"}).status_code in (401,422)
