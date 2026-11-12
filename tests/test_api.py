import os, tempfile
os.environ['SUPPLIERTRUST_DB'] = os.path.join(tempfile.mkdtemp(), 'test.db')
from fastapi.testclient import TestClient
from backend.main import app, identifier_status, normalize, connection, parse_ofac_csv, snapshot_fresh
import backend.main as main
from datetime import datetime, timezone, timedelta
client=TestClient(app)

def test_workflow():
    data={'name':'Fictional Example Trading Co','country':'India','category':'Manufacturing','identifier':'bad'}
    r=client.post('/api/suppliers',json=data); assert r.status_code==201
    s=r.json(); sid=s['id']; assert s['risk']['score']==35 and s['risk']['coverage']==33
    assert client.get('/api/suppliers?q=fictional').json()[0]['id']==sid
    data['category']='Services'; assert client.put(f'/api/suppliers/{sid}',json=data).json()['category']=='Services'
    e={'source_url':'https://example.com','reviewer':'Analyst','verified_on':'2026-01-01','status':'verified','notes':'Synthetic evidence'}
    assert client.post(f'/api/suppliers/{sid}/evidence',json=e).json()['risk']['score']==15
    with connection() as db:
        db.execute('DELETE FROM ofac_snapshot WHERE id=1')
        db.execute('INSERT INTO ofac_snapshot(id,retrieved_at,sha256,records,source) VALUES(1,?,?,?,?)',(datetime.now(timezone.utc).isoformat(),'test-hash','[{"id":"TEST-1","name":"Fictional Example Trading Co"}]','Synthetic test fixture'))
    s=client.post(f'/api/suppliers/{sid}/screen').json(); assert s['screening']['candidate'] and s['screening']['source']=='Synthetic test fixture' and s['risk']['score']==45
    assert 'Synthetic test fixture' in client.get(f'/api/suppliers/{sid}/report').text
    assert s['risk']['factors'][-1]['label']=='Synthetic name-match fixture awaiting review'
    s=client.post(f"/api/screenings/{s['screening']['id']}/decision",json={'decision':'false_positive','reviewer':'Analyst','note':'Different entity'}).json(); assert s['risk']['score']==15
    report=client.get(f'/api/suppliers/{sid}/report'); assert 'Synthetic test fixture' in report.text and 'https://example.com' in report.text
    assert client.delete(f'/api/suppliers/{sid}').status_code==200
    assert client.get(f'/api/suppliers/{sid}').status_code==404
    with connection() as db: assert db.execute("SELECT action FROM audit_events WHERE action='supplier_deleted'").fetchone()

def test_validation_and_uncertainty():
    assert identifier_status('')=='Not provided'
    assert identifier_status('U12345MH2020PTC123456')=='CIN format valid'
    assert identifier_status('27AAPFU0939F1ZV')=='GSTIN checksum valid'
    assert identifier_status('27AAPFU0939F1ZA')=='GSTIN checksum invalid'
    assert normalize('Acme, Ltd.')=='acme ltd'
    assert client.post('/api/suppliers',json={'name':'','country':'India','category':'x'}).status_code==422
    r=client.post('/api/suppliers',json={'name':'Another Fictional Supplier','country':'India','category':'Other'}).json()
    assert r['screening'] is None and r['risk']['coverage']==0
    assert client.post(f"/api/suppliers/{r['id']}/evidence",json={'source_url':'https://example.com','reviewer':'A','verified_on':'2026-01-01','status':'unverified','notes':'x'}).json()['risk']['score']==20
    assert client.post(f"/api/suppliers/{r['id']}/evidence",json={'source_url':'file:///etc/passwd','reviewer':'A','verified_on':'2026-01-01','status':'verified','notes':'x'}).status_code==422
    for bad_url in ('http://','https://user:password@example.com/private'):
        assert client.post(f"/api/suppliers/{r['id']}/evidence",json={'source_url':bad_url,'reviewer':'A','verified_on':'2026-01-01','status':'verified','notes':'x'}).status_code==422
from io import BytesIO
from pypdf import PdfWriter

def test_pdf_intake_limits_and_private_storage(tmp_path, monkeypatch):
    monkeypatch.setenv('SUPPLIERTRUST_UPLOAD_DIR', str(tmp_path / 'private'))
    s=client.post('/api/suppliers',json={'name':'PDF Test Supplier','country':'India','category':'Services'}).json()
    sid=s['id']
    bad=client.post(f'/api/suppliers/{sid}/documents',files={'file':('fake.pdf',b'not a pdf','application/pdf')})
    assert bad.status_code==415
    writer=PdfWriter(); writer.add_blank_page(width=72,height=72); data=BytesIO(); writer.write(data)
    response=client.post(f'/api/suppliers/{sid}/documents',files={'file':('test.pdf',data.getvalue(),'application/pdf')})
    assert response.status_code==200
    doc=response.json()['documents'][0]
    assert doc['filename']=='test.pdf' and doc['extraction_status']=='no extractable text'
    assert list((tmp_path/'private').glob('*.pdf'))
    too_large=client.post(f'/api/suppliers/{sid}/documents',files={'file':('big.pdf',b'%PDF-'+b'0'*(5*1024*1024),'application/pdf')})
    assert too_large.status_code==413


def test_ofac_csv_is_headerless_and_snapshot_expiry():
    import urllib.error
    rows=parse_ofac_csv(b'36,Fictional Entity,-0-,CUBA\n37,Second Entity,-0-,OTHER')
    assert rows==[{'id':'36','name':'Fictional Entity'},{'id':'37','name':'Second Entity'}]
    assert snapshot_fresh(datetime.now(timezone.utc).isoformat())
    assert not snapshot_fresh('2020-01-01T00:00:00+00:00')
    assert not snapshot_fresh((datetime.now(timezone.utc)+timedelta(days=1)).isoformat())
    handler=main.OfacRedirectHandler()
    assert handler.redirect_request(urllib.request.Request('https://sanctionslistservice.ofac.treas.gov/data'),None,302,'Found',{},'https://wc2h-sls-prod-public-published.s3.us-gov-west-1.amazonaws.com/data').get_full_url().startswith('https://')
    try: handler.redirect_request(urllib.request.Request('https://sanctionslistservice.ofac.treas.gov/data'),None,302,'Found',{},'http://127.0.0.1/private')
    except urllib.error.HTTPError: pass
    else: raise AssertionError('OFAC redirects must reject non-allowlisted URLs')
from datetime import datetime, timezone

def test_performance_scoring_and_audit_trail():
    s=client.post('/api/suppliers',json={'name':'Performance Test Co','country':'India','category':'Logistics'}).json(); sid=s['id']
    p={'observed_on':'2026-01-02','on_time_rate':0.6,'defect_rate':0.2,'source_url':'https://example.com/delivery.csv','reviewer':'Analyst','notes':'Fictional test observation'}
    s=client.post(f'/api/suppliers/{sid}/performance',json=p).json()
    assert s['risk']['score']==50
    assert any(x['label']=='Low recorded on-time delivery rate' for x in s['risk']['factors'])
    assert any(x['action']=='performance_observed' for x in s['audit'])
    p['on_time_rate']=1.1
    assert client.post(f'/api/suppliers/{sid}/performance',json=p).status_code==422

def test_read_only_demo_boundary(monkeypatch):
    import time
    monkeypatch.setattr(main,'demo_mode',True)
    main.demo_requests.clear()
    assert client.get('/api/demo/suppliers').json()[0]['risk']['factors'][0]['basis'].startswith('Synthetic demo fixture')
    assert client.get('/api/demo/suppliers/1/report').text.startswith('SUPPLIERTRUST — FICTIONAL')
    assert client.get('/api/suppliers').status_code==403
    assert client.post('/api/suppliers',json={'name':'Visitor Data','country':'India','category':'Other'}).status_code==403
    assert client.post('/api/suppliers/1/documents').status_code==403
    assert client.post('/api/screening/ofac/refresh').status_code==403
    assert client.get('/docs').status_code==403
    assert client.get('/healthz',headers={'Origin':'https://unlisted.example'}).headers.get('access-control-allow-origin') is None
    assert client.get('/healthz',headers={'content-length':str(6*1024*1024+1)}).status_code==413
    assert client.get('/healthz').headers['x-content-type-options']=='nosniff'
    main.demo_requests.extend([time.monotonic()]*120)
    limited=client.get('/api/demo/suppliers')
    assert limited.status_code==429 and limited.headers['cache-control']=='no-store'
    main.demo_requests.clear()
