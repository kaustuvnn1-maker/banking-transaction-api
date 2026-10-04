def test_customer_cannot_access_admin_transaction_endpoint(api,user_factory):
    u=user_factory(); assert api.get('/transactions',headers=u.headers).status_code==403

def test_admin_can_access_transaction_audit(api,admin_user):
    r=api.get('/transactions',headers=admin_user.headers); assert r.status_code==200; assert isinstance(r.json(),list)
