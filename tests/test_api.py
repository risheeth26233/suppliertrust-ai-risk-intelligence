import os, tempfile
os.environ['SUPPLIERTRUST_DB'] = os.path.join(tempfile.mkdtemp(), 'test.db')
from fastapi.testclient import TestClient
from backend.main import app, identifier_status, normalize
client=TestClient(app)

def test_workflow():
    data={'name':'Fictional Example Trading Co','country':'India','category':'Manufacturing','identifier':'bad'}
    r=client.post('/api/suppliers',json=data); assert r.status_code==201
    s=r.json(); sid=s['id']; assert s['risk']['score']==35 and s['risk']['coverage']==33
    assert client.get('/api/suppliers?q=fictional').json()[0]['id']==sid
    data['category']='Services'; assert client.put(f'/api/suppliers/{sid}',json=data).json()['category']=='Services'
    e={'source_url':'https://example.com','reviewer':'Analyst','verified_on':'2026-01-01','status':'verified','notes':'Synthetic evidence'}
    assert client.post(f'/api/suppliers/{sid}/evidence',json=e).json()['risk']['score']==15
    s=client.post(f'/api/suppliers/{sid}/screen').json(); assert s['screening']['candidate'] and s['risk']['score']==45
    s=client.post(f"/api/screenings/{s['screening']['id']}/decision",json={'decision':'false_positive','reviewer':'Analyst','note':'Different entity'}).json(); assert s['risk']['score']==15
    report=client.get(f'/api/suppliers/{sid}/report'); assert 'Synthetic fixture' in report.text and 'https://example.com' in report.text
    assert client.delete(f'/api/suppliers/{sid}').status_code==200
    assert client.get(f'/api/suppliers/{sid}').status_code==404

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
