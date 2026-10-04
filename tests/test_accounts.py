from decimal import Decimal

def d(v): return Decimal(str(v))

def test_account_creation_requires_authentication(api): assert api.post('/accounts',json={'account_holder_name':'Unauthorized User','balance':'1000'}).status_code==401

def test_customer_can_create_account(api,user_factory):
    u=user_factory(); r=api.post('/accounts',headers=u.headers,json={'account_holder_name':'Primary Account','balance':'1000.00'}); assert r.status_code in (200,201); assert 'account_id' in r.json(); assert d(r.json()['balance'])==Decimal('1000.00')

def test_customer_can_view_own_account(api,user_factory):
    u=user_factory(balance='1500'); r=api.get(f'/accounts/{u.account_id}',headers=u.headers); assert r.status_code==200; assert r.json()['account_id']==u.account_id

def test_customer_accounts_list_contains_only_own_accounts(api,user_factory):
    a=user_factory(balance='1000'); b=user_factory(balance='2000'); r=api.get('/accounts',headers=a.headers); assert r.status_code==200; ids={x['account_id'] for x in r.json()}; assert a.account_id in ids and b.account_id not in ids

def test_customer_cannot_view_another_customers_account(api,user_factory):
    a=user_factory(balance='1000'); b=user_factory(balance='1000'); assert api.get(f'/accounts/{b.account_id}',headers=a.headers).status_code==403

def test_customer_cannot_view_another_customers_transaction_history(api,user_factory):
    a=user_factory(balance='1000'); b=user_factory(balance='1000'); assert api.get(f'/accounts/{b.account_id}/transactions',headers=a.headers).status_code==403

def test_nonexistent_account_returns_404(api,user_factory):
    u=user_factory(); assert api.get('/accounts/999999999',headers=u.headers).status_code==404

def test_negative_balance_rejected(api,user_factory):
    u=user_factory(); assert api.post('/accounts',headers=u.headers,json={'account_holder_name':'Invalid','balance':'-100'}).status_code==422

def test_blank_account_name_rejected(api,user_factory):
    u=user_factory(); assert api.post('/accounts',headers=u.headers,json={'account_holder_name':'   ','balance':'100'}).status_code==422

def test_client_cannot_choose_account_owner(api,user_factory):
    a=user_factory(); b=user_factory(); r=api.post('/accounts',headers=a.headers,json={'account_holder_name':'Ownership Attack','balance':'500','user_id':b.user_id})
    if r.status_code==422: return
    assert r.status_code in (200,201); aid=r.json()['account_id']; assert api.get(f'/accounts/{aid}',headers=a.headers).status_code==200; assert api.get(f'/accounts/{aid}',headers=b.headers).status_code==403
