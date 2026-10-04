def test_correlation_id_is_generated(api):
    r=api.get('/health'); assert r.status_code==200; assert r.headers.get('X-Correlation-ID')

def test_client_correlation_id_is_preserved(api):
    cid='pytest-correlation-12345'; r=api.get('/health',headers={'X-Correlation-ID':cid}); assert r.status_code==200; assert r.headers.get('X-Correlation-ID')==cid

def test_security_headers_present(api):
    r=api.get('/health'); assert r.status_code==200; assert r.headers.get('X-Content-Type-Options')=='nosniff'; assert r.headers.get('X-Frame-Options')=='DENY'; assert r.headers.get('Referrer-Policy')=='no-referrer'; assert "default-src 'none'" in r.headers.get('Content-Security-Policy','')

def test_allowed_cors_origin(api):
    o='http://localhost:3000'; r=api.options('/accounts',headers={'Origin':o,'Access-Control-Request-Method':'GET','Access-Control-Request-Headers':'Authorization,Content-Type,X-Correlation-ID'}); assert r.status_code==204; assert r.headers.get('Access-Control-Allow-Origin')==o

def test_unapproved_cors_origin_not_reflected(api):
    o='https://evil.example.com'; r=api.options('/accounts',headers={'Origin':o,'Access-Control-Request-Method':'GET'}); assert r.status_code==204; assert r.headers.get('Access-Control-Allow-Origin')!=o
