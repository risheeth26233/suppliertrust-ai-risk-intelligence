import os, sqlite3, re, json, difflib, unicodedata, uuid, csv, hashlib, urllib.request
from io import BytesIO
from pathlib import Path
from datetime import date, datetime, timezone
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi import UploadFile, File
from pypdf import PdfReader
from pydantic import BaseModel, Field, field_validator

DB = os.getenv('SUPPLIERTRUST_DB', 'suppliertrust.db')
app = FastAPI(title='SupplierTrust', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173','http://127.0.0.1:5173'], allow_methods=['*'], allow_headers=['*'])

@contextmanager
def connection():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    try:
        yield db
        db.commit()
    finally: db.close()

def init():
    with connection() as db:
        db.executescript('''CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, country TEXT NOT NULL, category TEXT NOT NULL, identifier TEXT NOT NULL DEFAULT '', contact TEXT NOT NULL DEFAULT '', website TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS evidence (id INTEGER PRIMARY KEY, supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE, source_url TEXT NOT NULL, reviewer TEXT NOT NULL, verified_on TEXT NOT NULL, status TEXT NOT NULL, notes TEXT NOT NULL); CREATE TABLE IF NOT EXISTS screenings (id INTEGER PRIMARY KEY, supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE, checked_at TEXT NOT NULL, candidate TEXT NOT NULL, similarity REAL NOT NULL, decision TEXT NOT NULL DEFAULT 'pending', reviewer TEXT NOT NULL DEFAULT '', note TEXT NOT NULL DEFAULT '', source TEXT NOT NULL DEFAULT 'synthetic', source_ref TEXT NOT NULL DEFAULT ''); CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE, filename TEXT NOT NULL, stored_name TEXT NOT NULL, uploaded_at TEXT NOT NULL, extracted_name TEXT NOT NULL DEFAULT '', extracted_identifier TEXT NOT NULL DEFAULT '', extraction_status TEXT NOT NULL, discrepancies TEXT NOT NULL DEFAULT '[]'); CREATE TABLE IF NOT EXISTS ofac_snapshot (id INTEGER PRIMARY KEY CHECK(id=1), retrieved_at TEXT NOT NULL, sha256 TEXT NOT NULL, records TEXT NOT NULL);''')
        cols={r['name'] for r in db.execute('PRAGMA table_info(screenings)')}
        for col in ('source','source_ref'):
            if col not in cols: db.execute(f"ALTER TABLE screenings ADD COLUMN {col} TEXT NOT NULL DEFAULT '{'synthetic' if col=='source' else ''}'")
init()

class Supplier(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    country: str = Field(min_length=2, max_length=80)
    category: str = Field(min_length=2, max_length=80)
    identifier: str = Field(default='', max_length=40)
    contact: str = Field(default='', max_length=160)
    website: str = Field(default='', max_length=300)

    @field_validator('name', 'country', 'category')
    @classmethod
    def nonblank(cls, value):
        if len(value.strip()) < 2: raise ValueError('Must contain at least two non-space characters')
        return value.strip()

class Evidence(BaseModel):
    source_url: str = Field(min_length=1, max_length=500)
    reviewer: str = Field(min_length=1, max_length=120)
    verified_on: date
    status: str
    notes: str = Field(min_length=1, max_length=2000)

class Decision(BaseModel):
    decision: str
    reviewer: str = Field(min_length=1, max_length=120)
    note: str = Field(min_length=1, max_length=1000)

def normalize(s): return ' '.join(re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()))
def parse_ofac_csv(raw):
    # OFAC's legacy SDN.CSV is headerless; column 0 is the SDN ID and column 1 the primary name.
    return [{'id':r[0].strip(),'name':r[1].strip()} for r in csv.reader(raw.decode('utf-8-sig').splitlines()) if len(r)>1 and r[0].strip() and r[1].strip()]
def snapshot_fresh(retrieved_at):
    return (datetime.now(timezone.utc)-datetime.fromisoformat(retrieved_at)).total_seconds() <= 7*86400
def identifier_status(value):
    v=value.strip().upper()
    if not v: return 'Not provided'
    if re.fullmatch(r'\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]', v):
        chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'; total=0
        for i, ch in enumerate(v[:14]):
            n=chars.index(ch)*(1 if i%2==0 else 2); total += n//36+n%36
        return 'GSTIN checksum valid' if chars[(36-total%36)%36]==v[-1] else 'GSTIN checksum invalid'
    if re.fullmatch(r'[UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}',v): return 'CIN format valid'
    return 'Format not recognized'

def get_supplier(db, sid):
    row=db.execute('SELECT * FROM suppliers WHERE id=?',(sid,)).fetchone()
    if not row: raise HTTPException(404,'Supplier not found')
    return dict(row)

def details(db, sid):
    s=get_supplier(db,sid)
    ev=[dict(x) for x in db.execute('SELECT * FROM evidence WHERE supplier_id=? ORDER BY id DESC',(sid,))]
    docs=[dict(x) for x in db.execute('SELECT * FROM documents WHERE supplier_id=? ORDER BY id DESC',(sid,))]
    for doc in docs:
        doc['discrepancies']=json.loads(doc['discrepancies'])
    screen=db.execute('SELECT * FROM screenings WHERE supplier_id=? ORDER BY id DESC LIMIT 1',(sid,)).fetchone()
    screen=dict(screen) if screen else None
    snapshot=db.execute('SELECT retrieved_at,sha256 FROM ofac_snapshot WHERE id=1').fetchone()
    if screen and screen['source']=='OFAC SDN':
        screen['source_snapshot_at']=snapshot['retrieved_at'] if snapshot else None
        screen['source_sha256']=snapshot['sha256'] if snapshot else None
    factors=[]
    if not any(e['status']=='verified' for e in ev): factors.append({'label':'No manually verified evidence recorded','points':20,'basis':'Missing verification; not an adverse finding.'})
    if identifier_status(s['identifier']) in ('GSTIN checksum invalid','Format not recognized'): factors.append({'label':'Identifier requires review','points':15,'basis':identifier_status(s['identifier'])})
    for doc in docs:
        for discrepancy in doc['discrepancies']:
            factors.append({'label':discrepancy,'points':15,'basis':f"Extracted from PDF {doc['filename']}; OCR/text extraction is not authenticity verification."})
    if screen and screen['candidate'] and screen['decision']=='pending': factors.append({'label':'Potential sanctions name match awaiting review','points':30,'basis':f"{screen['source']} name similarity only; identity is unconfirmed. Source record: {screen['source_ref']}"})
    if screen and screen['candidate'] and screen['decision']=='confirmed': factors.append({'label':'Potential match confirmed by reviewer','points':30,'basis':f"Human review required; source: {screen['source']} record {screen['source_ref']}"})
    coverage=round(100*(bool(s['identifier'])+bool(ev)+bool(screen))/3)
    return {**s,'identifier_status':identifier_status(s['identifier']),'evidence':ev,'documents':docs,'screening':screen,'risk':{'score':min(100,sum(x['points'] for x in factors)),'coverage':coverage,'confidence':'Limited' if coverage<100 else 'Moderate','factors':factors,'review_status':'Review required' if factors else 'No indicators recorded'}}

@app.get('/api/suppliers')
def list_suppliers(q: str = '', category: str = ''):
    with connection() as db:
        ids=[r['id'] for r in db.execute('SELECT id FROM suppliers WHERE lower(name) LIKE ? AND lower(category) LIKE ? ORDER BY id DESC',('%'+q.lower()+'%','%'+category.lower()+'%'))]
        return [details(db,i) for i in ids]

@app.post('/api/suppliers', status_code=201)
def create_supplier(s: Supplier):
    with connection() as db:
        cur=db.execute('INSERT INTO suppliers(name,country,category,identifier,contact,website,created_at) VALUES(?,?,?,?,?,?,?)',(*[getattr(s,x).strip() for x in ('name','country','category','identifier','contact','website')],date.today().isoformat()))
        return details(db,cur.lastrowid)

@app.get('/api/suppliers/{sid}')
def supplier(sid:int):
    with connection() as db: return details(db,sid)

@app.put('/api/suppliers/{sid}')
def update_supplier(sid:int,s:Supplier):
    with connection() as db:
        get_supplier(db,sid)
        db.execute('UPDATE suppliers SET name=?,country=?,category=?,identifier=?,contact=?,website=? WHERE id=?',(*[getattr(s,x).strip() for x in ('name','country','category','identifier','contact','website')],sid))
        return details(db,sid)

@app.delete('/api/suppliers/{sid}')
def delete_supplier(sid:int):
    with connection() as db:
        get_supplier(db,sid); db.execute('DELETE FROM suppliers WHERE id=?',(sid,))
        return {'deleted':True}

@app.post('/api/suppliers/{sid}/evidence')
def add_evidence(sid:int,e:Evidence):
    if e.status not in ('verified','unverified','inconclusive'): raise HTTPException(422,'Invalid evidence status')
    if not re.match(r'^https?://',e.source_url): raise HTTPException(422,'Source must be an HTTP(S) URL')
    with connection() as db:
        get_supplier(db,sid)
        db.execute('INSERT INTO evidence(supplier_id,source_url,reviewer,verified_on,status,notes) VALUES(?,?,?,?,?,?)',(sid,e.source_url,e.reviewer,e.verified_on.isoformat(),e.status,e.notes))
        return details(db,sid)

@app.post('/api/suppliers/{sid}/screen')
def screen(sid:int):
    with connection() as db:
        s=get_supplier(db,sid)
        snapshot=db.execute('SELECT * FROM ofac_snapshot WHERE id=1').fetchone()
        if not snapshot or not snapshot_fresh(snapshot['retrieved_at']): raise HTTPException(409,'OFAC data is missing or older than 7 days. Refresh it before screening.')
        candidates=[]
        for record in json.loads(snapshot['records']):
            score=difflib.SequenceMatcher(None,normalize(s['name']),normalize(record['name'])).ratio()
            if score>=.80: candidates.append((score,record))
        candidates.sort(key=lambda x:x[0],reverse=True)
        for score,record in reversed(candidates[:10]):
            db.execute('INSERT INTO screenings(supplier_id,checked_at,candidate,similarity,source,source_ref) VALUES(?,?,?,?,?,?)',(sid,datetime.now(timezone.utc).isoformat(),record['name'],score,'OFAC SDN',record['id']))
        if not candidates: db.execute('INSERT INTO screenings(supplier_id,checked_at,candidate,similarity,source,source_ref) VALUES(?,?,?,?,?,?)',(sid,datetime.now(timezone.utc).isoformat(),'','0','OFAC SDN',''))
        return details(db,sid)

@app.post('/api/screening/ofac/refresh')
def refresh_ofac():
    url='https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV'
    request=urllib.request.Request(url,headers={'User-Agent':'SupplierTrust/1.0 (supplier screening dataset refresh)'})
    try:
        with urllib.request.urlopen(request,timeout=30) as response:
            if response.geturl().split('/')[2] not in ('sanctionslistservice.ofac.treas.gov','wc2h-sls-prod-public-published.s3.us-gov-west-1.amazonaws.com'): raise ValueError('Unexpected redirect host')
            raw=response.read(15*1024*1024+1)
        if len(raw)>15*1024*1024: raise ValueError('Dataset is too large')
        records=parse_ofac_csv(raw)
        if len(records)<1000: raise ValueError('Downloaded dataset failed validation')
    except Exception as e: raise HTTPException(503,f'OFAC dataset refresh failed; existing snapshot retained: {type(e).__name__}')
    digest=hashlib.sha256(raw).hexdigest(); retrieved=datetime.now(timezone.utc).isoformat()
    with connection() as db:
        db.execute('INSERT INTO ofac_snapshot(id,retrieved_at,sha256,records) VALUES(1,?,?,?) ON CONFLICT(id) DO UPDATE SET retrieved_at=excluded.retrieved_at,sha256=excluded.sha256,records=excluded.records',(retrieved,digest,json.dumps(records)))
    return {'source':'OFAC SDN','source_url':url,'retrieved_at':retrieved,'sha256':digest,'record_count':len(records)}

@app.get('/api/screening/status')
def screening_status():
    with connection() as db:
        row=db.execute('SELECT retrieved_at,sha256 FROM ofac_snapshot WHERE id=1').fetchone()
        return {'status':'available' if row else 'not_checked','source':'OFAC SDN','source_url':'https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV','retrieved_at':row['retrieved_at'] if row else None,'sha256':row['sha256'] if row else None}

@app.post('/api/suppliers/{sid}/documents')
async def upload_document(sid: int, file: UploadFile = File(...)):
    if not file.filename or Path(file.filename).suffix.lower() != '.pdf' or file.content_type != 'application/pdf':
        raise HTTPException(415,'Only PDF documents are supported')
    data=await file.read(5*1024*1024+1)
    if len(data)>5*1024*1024: raise HTTPException(413,'PDF exceeds the 5 MB limit')
    if not data.startswith(b'%PDF-'): raise HTTPException(415,'File content is not a valid PDF')
    try:
        reader=PdfReader(BytesIO(data), strict=True)
        text=' '.join((page.extract_text() or '') for page in reader.pages[:20])[:100_000]
    except Exception: raise HTTPException(422,'PDF could not be safely read')
    with connection() as db:
        supplier=get_supplier(db,sid)
        names=re.findall(r'(?im)^\s*(?:legal\s+)?(?:business\s+)?name\s*[:\-]\s*(.{2,160})',text)
        ids=re.findall(r'\b(?:\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]|[UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6})\b',text.upper())
        extracted_name=names[0].strip()[:160] if names else ''
        extracted_id=ids[0] if ids else ''
        discrepancies=[]
        if extracted_name and difflib.SequenceMatcher(None,normalize(extracted_name),normalize(supplier['name'])).ratio()<.8: discrepancies.append('Document business name differs from supplier record')
        if extracted_id and supplier['identifier'] and extracted_id!=supplier['identifier'].upper(): discrepancies.append('Document registration identifier differs from supplier record')
        stored_name=uuid.uuid4().hex+'.pdf'
        upload_dir=Path(os.getenv('SUPPLIERTRUST_UPLOAD_DIR','private_uploads')).resolve(); upload_dir.mkdir(parents=True,exist_ok=True)
        (upload_dir/stored_name).write_bytes(data)
        db.execute('INSERT INTO documents(supplier_id,filename,stored_name,uploaded_at,extracted_name,extracted_identifier,extraction_status,discrepancies) VALUES(?,?,?,?,?,?,?,?)',(sid,Path(file.filename).name[:200],stored_name,datetime.now(timezone.utc).isoformat(),extracted_name,extracted_id,'text extracted' if text else 'no extractable text',json.dumps(discrepancies)))
        return details(db,sid)

@app.post('/api/screenings/{screen_id}/decision')
def decide(screen_id:int,d:Decision):
    if d.decision not in ('false_positive','confirmed','pending'): raise HTTPException(422,'Invalid decision')
    with connection() as db:
        row=db.execute('SELECT * FROM screenings WHERE id=?',(screen_id,)).fetchone()
        if not row or not row['candidate']: raise HTTPException(404,'Candidate not found')
        db.execute('UPDATE screenings SET decision=?,reviewer=?,note=? WHERE id=?',(d.decision,d.reviewer,d.note,screen_id))
        return details(db,row['supplier_id'])

@app.get('/api/suppliers/{sid}/report', response_class=PlainTextResponse)
def report(sid:int):
    with connection() as db: s=details(db,sid)
    lines=['SUPPLIERTRUST — DUE DILIGENCE REPORT',f"Generated: {date.today().isoformat()}",f"Supplier: {s['name']}",f"Country: {s['country']} | Category: {s['category']}",f"Identifier: {s['identifier'] or 'Not provided'} ({s['identifier_status']})",f"Risk index: {s['risk']['score']}/100 | Evidence coverage: {s['risk']['coverage']}% | Confidence: {s['risk']['confidence']}",f"Review status: {s['risk']['review_status']}",'','RISK INDICATORS']
    lines += [f"- {f['label']} (+{f['points']}): {f['basis']}" for f in s['risk']['factors']] or ['- No indicators recorded.']
    lines += ['','EVIDENCE']+[f"- {e['status']} | {e['verified_on']} | {e['reviewer']} | {e['source_url']} | {e['notes']}" for e in s['evidence']]
    lines += ['',f"Screening: {'OFAC SDN snapshot '+str(s['screening'].get('source_snapshot_at'))+' | SHA-256 '+str(s['screening'].get('source_sha256'))+' | record '+s['screening']['source_ref']+' | '+(s['screening']['candidate'] or 'no candidate')+' | decision '+s['screening']['decision']+' | reviewer '+s['screening']['reviewer']+' | rationale '+s['screening']['note'] if s['screening'] and s['screening']['source']=='OFAC SDN' else 'Not checked'}",'A potential name match is not proof of identity or wrongdoing; analyst review is required.','Identifier format validation does not establish registration or active status.','Follow-up: independently verify registration and review supporting documents.','This index is not a probability of fraud or regulatory certification.']
    return PlainTextResponse('\n'.join(lines),headers={'Content-Disposition':f'attachment; filename="supplier-{sid}-report.txt"'})
