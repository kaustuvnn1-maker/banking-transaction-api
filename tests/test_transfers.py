import uuid
from decimal import Decimal

def d(v): return Decimal(str(v))
def headers(u,k): return {**u.headers,'Idempotency-Key':k}
def balance(api,u,aid):
    r=api.get(f'/accounts/{aid}',headers=u.headers); assert r.status_code==200; return d(r.json()['balance'])
def history(api,u,aid):
    r=api.get(f'/accounts/{aid}/transactions',headers=u.headers); assert r.status_code==200; return r.json()

def test_successful_transfer(api,user_factory):
    s=user_factory(balance='1000'); rcv=user_factory(balance='100'); r=api.post('/transfers',headers=headers(s,str(uuid.uuid4())),json={'from_account':s.account_id,'to_account':rcv.account_id,'amount':'250'}); assert r.status_code==200; assert balance(api,s,s.account_id)==Decimal('750'); assert balance(api,rcv,rcv.account_id)==Decimal('350')

def test_insufficient_balance_does_not_change_money(api,user_factory):
    s=user_factory(balance='100'); rcv=user_factory(balance='200'); r=api.post('/transfers',headers=headers(s,str(uuid.uuid4())),json={'from_account':s.account_id,'to_account':rcv.account_id,'amount':'500'}); assert r.status_code==400; assert balance(api,s,s.account_id)==Decimal('100'); assert balance(api,rcv,rcv.account_id)==Decimal('200')

def test_same_account_transfer_rejected(api,user_factory):
    s=user_factory(balance='1000'); r=api.post('/transfers',headers=headers(s,str(uuid.uuid4())),json={'from_account':s.account_id,'to_account':s.account_id,'amount':'100'}); assert r.status_code==400; assert balance(api,s,s.account_id)==Decimal('1000')

def test_customer_cannot_transfer_from_another_users_account(api,user_factory):
    owner=user_factory(balance='1000'); attacker=user_factory(balance='100'); r=api.post('/transfers',headers=headers(attacker,str(uuid.uuid4())),json={'from_account':owner.account_id,'to_account':attacker.account_id,'amount':'100'}); assert r.status_code==403; assert balance(api,owner,owner.account_id)==Decimal('1000')

def test_transfer_requires_authentication(api,user_factory):
    rcv=user_factory(balance='100'); assert api.post('/transfers',headers={'Idempotency-Key':str(uuid.uuid4())},json={'from_account':1,'to_account':rcv.account_id,'amount':'10'}).status_code==401

def test_transfer_requires_idempotency_key(api,user_factory):
    s=user_factory(balance='1000'); r=user_factory(balance='100'); assert api.post('/transfers',headers=s.headers,json={'from_account':s.account_id,'to_account':r.account_id,'amount':'100'}).status_code==422

def test_zero_transfer_amount_rejected(api,user_factory):
    s=user_factory(balance='1000'); r=user_factory(balance='100'); assert api.post('/transfers',headers=headers(s,str(uuid.uuid4())),json={'from_account':s.account_id,'to_account':r.account_id,'amount':'0'}).status_code==422

def test_negative_transfer_amount_rejected(api,user_factory):
    s=user_factory(balance='1000'); r=user_factory(balance='100'); assert api.post('/transfers',headers=headers(s,str(uuid.uuid4())),json={'from_account':s.account_id,'to_account':r.account_id,'amount':'-100'}).status_code==422

def test_same_idempotency_key_same_request_moves_money_once(api,user_factory):
    s=user_factory(balance='1000'); r=user_factory(balance='100'); k=str(uuid.uuid4()); before=len(history(api,s,s.account_id)); p={'from_account':s.account_id,'to_account':r.account_id,'amount':'100'}; assert api.post('/transfers',headers=headers(s,k),json=p).status_code==200; assert api.post('/transfers',headers=headers(s,k),json=p).status_code==200; assert balance(api,s,s.account_id)==Decimal('900'); assert balance(api,r,r.account_id)==Decimal('200'); assert len(history(api,s,s.account_id))==before+1

def test_same_idempotency_key_different_request_returns_409(api,user_factory):
    s=user_factory(balance='1000'); r=user_factory(balance='100'); k=str(uuid.uuid4()); assert api.post('/transfers',headers=headers(s,k),json={'from_account':s.account_id,'to_account':r.account_id,'amount':'100'}).status_code==200; assert api.post('/transfers',headers=headers(s,k),json={'from_account':s.account_id,'to_account':r.account_id,'amount':'150'}).status_code==409; assert balance(api,s,s.account_id)==Decimal('900')
