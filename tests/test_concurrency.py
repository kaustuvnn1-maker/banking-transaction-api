import os, uuid, requests
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
BASE_URL=os.getenv('API_BASE_URL','https://localhost:8443/api').rstrip('/')
VERIFY_TLS=os.getenv('VERIFY_TLS','false').lower()=='true'
def d(v): return Decimal(str(v))
def bal(api,u):
    r=api.get(f'/accounts/{u.account_id}',headers=u.headers); assert r.status_code==200; return d(r.json()['balance'])
def send(token,a,b,amount,key): return requests.post(f'{BASE_URL}/transfers',verify=VERIFY_TLS,timeout=15,headers={'Authorization':f'Bearer {token}','Idempotency-Key':key},json={'from_account':a,'to_account':b,'amount':str(amount)})

def test_concurrent_transfers_cannot_double_spend(api,user_factory):
    s=user_factory(balance='1000'); a=user_factory(balance='0'); b=user_factory(balance='0')
    with ThreadPoolExecutor(max_workers=2) as ex:
        x=ex.submit(send,s.token,s.account_id,a.account_id,'800',str(uuid.uuid4())); y=ex.submit(send,s.token,s.account_id,b.account_id,'800',str(uuid.uuid4())); rx,ry=x.result(),y.result()
    assert sorted([rx.status_code,ry.status_code])==[200,400]; assert bal(api,s)==Decimal('200'); assert bal(api,a)+bal(api,b)==Decimal('800')

def test_concurrent_duplicate_idempotency_requests_move_money_once(api,user_factory):
    s=user_factory(balance='1000'); r=user_factory(balance='0'); k=str(uuid.uuid4())
    with ThreadPoolExecutor(max_workers=2) as ex:
        x=ex.submit(send,s.token,s.account_id,r.account_id,'100',k); y=ex.submit(send,s.token,s.account_id,r.account_id,'100',k); rx,ry=x.result(),y.result()
    assert rx.status_code==200 and ry.status_code==200; assert bal(api,s)==Decimal('900'); assert bal(api,r)==Decimal('100')
