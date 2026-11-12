import os, re, json, difflib, unicodedata, uuid, csv, hashlib, urllib.request, time
from collections import deque
from io import BytesIO
from pathlib import Path
from datetime import date, datetime, timezone, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response
from fastapi import UploadFile, File
from pypdf import PdfReader
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import create_engine, text, inspect
from urllib.parse import urlsplit

demo_mode=os.getenv('SUPPLIERTRUST_MODE','local').lower()=='demo'
if os.getenv('RENDER') and not demo_mode:
    raise RuntimeError('Set SUPPLIERTRUST_MODE=demo before starting SupplierTrust on Render.')

database_url=os.getenv('DATABASE_URL')
if database_url and database_url.startswith(('postgres://','postgresql://')): database_url='postgresql+psycopg://'+database_url.split('://',1)[1]
if os.getenv('RENDER') and not database_url: raise RuntimeError('Set DATABASE_URL to the isolated Neon PostgreSQL database before starting SupplierTrust on Render.')
if not database_url: database_url='sqlite:///'+os.path.abspath(os.getenv('SUPPLIERTRUST_DB','suppliertrust.db')).replace('\\','/')
engine=create_engine(database_url,connect_args={'check_same_thread':False} if database_url.startswith('sqlite') else {},pool_pre_ping=True)
app = FastAPI(title='SupplierTrust', version='0.1.0', docs_url=None if demo_mode else '/docs', redoc_url=None if demo_mode else '/redoc', openapi_url=None if demo_mode else '/openapi.json')
origins=[x.strip() for x in os.getenv('SUPPLIERTRUST_ALLOWED_ORIGINS','http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174').split(',') if x.strip()]
if os.getenv('RENDER') and not os.getenv('SUPPLIERTRUST_ALLOWED_ORIGINS'): raise RuntimeError('Set SUPPLIERTRUST_ALLOWED_ORIGINS to the exact Vercel demo origin before starting SupplierTrust on Render.')
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['GET'] if demo_mode else ['GET','POST','PUT','DELETE'], allow_headers=['Content-Type'])
demo_requests=deque()
OFAC_HOSTS={'sanctionslistservice.ofac.treas.gov','wc2h-sls-prod-public-published.s3.us-gov-west-1.amazonaws.com'}

class OfacRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        target=urlsplit(newurl)
        if target.scheme!='https' or target.hostname not in OFAC_HOSTS:
            raise urllib.error.HTTPError(newurl,code,'OFAC redirect host rejected',headers,fp)
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def secure_response(response,request):
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
    response.headers['Cache-Control']='no-store'
    response.headers['Content-Security-Policy']="default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    if request.url.scheme=='https': response.headers['Strict-Transport-Security']='max-age=31536000; includeSubDomains'
    return response

@app.middleware('http')
async def security_boundary(request, call_next):
    try: content_length=int(request.headers.get('content-length','0') or 0)
    except ValueError: return secure_response(PlainTextResponse('Invalid content length',status_code=400),request)
    if content_length>6*1024*1024: return secure_response(PlainTextResponse('Request is too large',status_code=413),request)
    if demo_mode:
        read_route=request.url.path in ('/healthz','/api/demo/suppliers','/api/demo/screening/status') or re.fullmatch(r'/api/demo/suppliers/\d+(?:/report)?',request.url.path)
        preflight=request.method=='OPTIONS' and request.headers.get('access-control-request-method')=='GET'
        if request.method=='OPTIONS':
            origin=request.headers.get('origin','')
            requested_headers={x.strip().lower() for x in request.headers.get('access-control-request-headers','').split(',') if x.strip()}
            if read_route and preflight and origin in origins and requested_headers<={'content-type'}:
                return secure_response(Response(status_code=200,headers={'Access-Control-Allow-Origin':origin,'Access-Control-Allow-Methods':'GET','Access-Control-Allow-Headers':'Content-Type','Access-Control-Max-Age':'600','Vary':'Origin'}),request)
            return secure_response(PlainTextResponse('Public demonstration is read-only and contains fictional sample data.',status_code=403),request)
        if not read_route or request.method!='GET':
            return secure_response(PlainTextResponse('Public demonstration is read-only and contains fictional sample data.',status_code=403),request)
        now=time.monotonic()
        while demo_requests and demo_requests[0] < now-60: demo_requests.popleft()
        if len(demo_requests)>=120: return secure_response(PlainTextResponse('Demo request limit reached; retry shortly.',status_code=429),request)
        demo_requests.append(now)
    response=await call_next(request)
    return secure_response(response,request)

def connection():
    conn=engine.connect()
    if conn.dialect.name=='sqlite': conn.exec_driver_sql('PRAGMA foreign_keys=ON')
    return Database(conn)

def demo_record():
    return {'id':1,'name':'Northstar Components Ltd. (Fictional)','country':'India','category':'Manufacturing','identifier':'27AAPFU0939F1ZV','identifier_status':'GSTIN checksum valid','contact':'demo@example.com','website':'https://example.com','created_at':'2026-01-12','evidence':[{'id':1,'source_url':'https://example.com/verification','reviewer':'Demo analyst','verified_on':'2026-01-14','status':'verified','notes':'Fictional example verification record.'}],'documents':[],'performance':[{'id':1,'observed_on':'2026-01-15','on_time_rate':0.78,'defect_rate':0.12,'source_url':'https://example.com/performance.csv','reviewer':'Demo analyst','notes':'Fictional example observation.'}],'audit':[{'id':3,'occurred_at':'2026-01-15T10:30:00+00:00','actor':'Demo analyst','action':'performance_observed','detail':'Fictional delivery observation recorded.'},{'id':2,'occurred_at':'2026-01-14T10:30:00+00:00','actor':'Demo analyst','action':'evidence_recorded','detail':'Fictional verification evidence recorded.'},{'id':1,'occurred_at':'2026-01-12T10:30:00+00:00','actor':'Demo analyst','action':'supplier_created','detail':'Fictional sample supplier.'}],'screening':{'id':1,'checked_at':'2026-01-15T10:30:00+00:00','candidate':'Fictional screening fixture — not an official list entry','similarity':0.84,'decision':'pending','reviewer':'','note':'','source':'Synthetic demo fixture','source_ref':'DEMO-ONLY'},'risk':{'score':60,'coverage':100,'confidence':'Limited','review_status':'Review required','factors':[{'label':'Synthetic match fixture awaiting review','points':30,'basis':'Synthetic demo fixture only. This is not an official sanctions result.'},{'label':'Low recorded on-time delivery rate','points':15,'basis':'78% in a fictional example observation. Source: https://example.com/performance.csv'},{'label':'Elevated recorded defect rate','points':15,'basis':'12% in a fictional example observation. Source: https://example.com/performance.csv'}]}}

@app.get('/healthz')
def health():
    try:
        with engine.connect() as db: db.execute(text('SELECT 1'))
        return {'status':'ok'}
    except Exception: raise HTTPException(503,'Database unavailable')

@app.get('/api/demo/suppliers')
def demo_suppliers(): return [demo_record()]

@app.get('/api/demo/suppliers/{sid}')
def demo_supplier(sid:int):
    if sid!=1: raise HTTPException(404,'Demo record not found')
    return demo_record()

@app.get('/api/demo/screening/status')
def demo_screening_status(): return {'status':'demo_fixture','source':'Synthetic demo fixture','retrieved_at':None,'sha256':None}

@app.get('/api/demo/suppliers/{sid}/report',response_class=PlainTextResponse)
def demo_report(sid:int):
    if sid!=1: raise HTTPException(404,'Demo record not found')
    s=demo_record()
    lines=['SUPPLIERTRUST — FICTIONAL DEMONSTRATION REPORT','Demo data only; no live screening was performed.',f"Supplier: {s['name']}",f"Risk indicator index: {s['risk']['score']}/100",'','RISK INDICATORS']
    lines += [f"- {f['label']} (+{f['points']}): {f['basis']}" for f in s['risk']['factors']]
    lines += ['','This report is fictional and is not a compliance or identity determination.']
    return PlainTextResponse('\n'.join(lines),headers={'Content-Disposition':'attachment; filename="supplier-demo-report.txt"'})

class Result:
    def __init__(self,result,lastrowid=None): self.result=result; self.lastrowid=lastrowid
    def fetchone(self): return self.result.mappings().fetchone()
    def fetchall(self): return self.result.mappings().fetchall()
    def __iter__(self): return iter(self.result.mappings())

class Database:
    def __init__(self,conn): self.conn=conn; self.tx=conn.get_transaction() or conn.begin()
    def __enter__(self): return self
    def __exit__(self,kind,value,tb):
        self.tx.commit() if kind is None else self.tx.rollback()
        self.conn.close()
    def execute(self,sql,params=()):
        if sql.startswith('PRAGMA table_info('):
            return Result(self.conn.exec_driver_sql(sql))
        names=re.findall(r'\?',sql); values={f'p{i}':v for i,v in enumerate(params)}
        for i in range(len(names)): sql=sql.replace('?',f':p{i}',1)
        returns=sql.lstrip().lower().startswith('insert into suppliers')
        if returns and 'returning' not in sql.lower(): sql+=' RETURNING id'
        result=self.conn.execute(text(sql),values)
        inserted=result.scalar_one() if returns else None
        return Result(result,inserted)
    def executescript(self,script):
        for statement in script.split(';'):
            statement=statement.strip()
            if not statement: continue
            if self.conn.dialect.name=='postgresql': statement=re.sub(r'INTEGER PRIMARY KEY','SERIAL PRIMARY KEY',statement,flags=re.I)
            self.conn.execute(text(statement))

def init():
    if engine.dialect.name!='sqlite': return  # PostgreSQL schema is managed by Alembic.
    with connection() as db:
        db.executescript('''CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, country TEXT NOT NULL, category TEXT NOT NULL, identifier TEXT NOT NULL DEFAULT '', contact TEXT NOT NULL DEFAULT '', website TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS evidence (id INTEGER PRIMARY KEY, supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE, source_url TEXT NOT NULL, reviewer TEXT NOT NULL, verified_on TEXT NOT NULL, status TEXT NOT NULL, notes TEXT NOT NULL); CREATE TABLE IF NOT EXISTS screenings (id INTEGER PRIMARY KEY, supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE, checked_at TEXT NOT NULL, candidate TEXT NOT NULL, similarity REAL NOT NULL, decision TEXT NOT NULL DEFAULT 'pending', reviewer TEXT NOT NULL DEFAULT '', note TEXT NOT NULL DEFAULT '', source TEXT NOT NULL DEFAULT 'synthetic', source_ref TEXT NOT NULL DEFAULT ''); CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE, filename TEXT NOT NULL, stored_name TEXT NOT NULL, uploaded_at TEXT NOT NULL, extracted_name TEXT NOT NULL DEFAULT '', extracted_identifier TEXT NOT NULL DEFAULT '', extraction_status TEXT NOT NULL, discrepancies TEXT NOT NULL DEFAULT '[]'); CREATE TABLE IF NOT EXISTS ofac_snapshot (id INTEGER PRIMARY KEY CHECK(id=1), retrieved_at TEXT NOT NULL, sha256 TEXT NOT NULL, records TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'OFAC SDN'); CREATE TABLE IF NOT EXISTS performance (id INTEGER PRIMARY KEY, supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE, observed_on TEXT NOT NULL, on_time_rate REAL NOT NULL, defect_rate REAL NOT NULL, source_url TEXT NOT NULL, reviewer TEXT NOT NULL, notes TEXT NOT NULL); CREATE TABLE IF NOT EXISTS audit_events (id INTEGER PRIMARY KEY, supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL, occurred_at TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL, detail TEXT NOT NULL);''')
        if db.conn.dialect.name=='sqlite': cols={r['name'] for r in db.execute('PRAGMA table_info(screenings)')}
        else: cols={r['name'] for r in db.execute('SELECT column_name AS name FROM information_schema.columns WHERE table_name=?',('screenings',))}
        for col in ('source','source_ref'):
            if col not in cols: db.execute(f"ALTER TABLE screenings ADD COLUMN {col} TEXT NOT NULL DEFAULT '{'synthetic' if col=='source' else ''}'")
        snapshot_cols={r['name'] for r in db.execute('PRAGMA table_info(ofac_snapshot)')}
        if 'source' not in snapshot_cols: db.execute("ALTER TABLE ofac_snapshot ADD COLUMN source TEXT NOT NULL DEFAULT 'OFAC SDN'")
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

def validate_source_url(value):
    parts=urlsplit(value)
    if parts.scheme not in ('http','https') or not parts.hostname or parts.username or parts.password or any(ord(c)<32 for c in value): raise ValueError('Source must be a valid HTTP(S) URL without embedded credentials')
    return value

class Evidence(BaseModel):
    source_url: str = Field(min_length=1, max_length=500)
    reviewer: str = Field(min_length=1, max_length=120)
    verified_on: date
    status: str
    notes: str = Field(min_length=1, max_length=2000)

    @field_validator('source_url')
    @classmethod
    def valid_source_url(cls,value): return validate_source_url(value)

class Decision(BaseModel):
    decision: str
    reviewer: str = Field(min_length=1, max_length=120)
    note: str = Field(min_length=1, max_length=1000)

class Performance(BaseModel):
    observed_on: date
    on_time_rate: float = Field(ge=0,le=1)
    defect_rate: float = Field(ge=0,le=1)
    source_url: str = Field(min_length=1,max_length=500)
    reviewer: str = Field(min_length=1,max_length=120)
    notes: str = Field(min_length=1,max_length=1000)

    @field_validator('source_url')
    @classmethod
    def valid_source_url(cls,value): return validate_source_url(value)

def normalize(s): return ' '.join(re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()))
def parse_ofac_csv(raw):
    # OFAC's legacy SDN.CSV is headerless; column 0 is the SDN ID and column 1 the primary name.
    return [{'id':r[0].strip(),'name':r[1].strip()} for r in csv.reader(raw.decode('utf-8-sig').splitlines()) if len(r)>1 and r[0].strip() and r[1].strip()]
def snapshot_fresh(retrieved_at):
    age=(datetime.now(timezone.utc)-datetime.fromisoformat(retrieved_at)).total_seconds()
    return 0 <= age <= 7*86400
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
    performance=[dict(x) for x in db.execute('SELECT * FROM performance WHERE supplier_id=? ORDER BY observed_on DESC',(sid,))]
    audit=[dict(x) for x in db.execute('SELECT * FROM audit_events WHERE supplier_id=? ORDER BY id DESC LIMIT 50',(sid,))]
    for doc in docs:
        doc['discrepancies']=json.loads(doc['discrepancies'])
    screen=db.execute('SELECT * FROM screenings WHERE supplier_id=? ORDER BY id DESC LIMIT 1',(sid,)).fetchone()
    screen=dict(screen) if screen else None
    snapshot=db.execute('SELECT retrieved_at,sha256,source FROM ofac_snapshot WHERE id=1').fetchone()
    if screen and snapshot and screen['source']==snapshot['source']:
        screen['source_snapshot_at']=snapshot['retrieved_at'] if snapshot else None
        screen['source_sha256']=snapshot['sha256'] if snapshot else None
    factors=[]
    if not any(e['status']=='verified' for e in ev): factors.append({'label':'No manually verified evidence recorded','points':20,'basis':'Missing verification; not an adverse finding.'})
    if identifier_status(s['identifier']) in ('GSTIN checksum invalid','Format not recognized'): factors.append({'label':'Identifier requires review','points':15,'basis':identifier_status(s['identifier'])})
    for doc in docs:
        for discrepancy in doc['discrepancies']:
            factors.append({'label':discrepancy,'points':15,'basis':f"Extracted from PDF {doc['filename']}; OCR/text extraction is not authenticity verification."})
    if performance:
        avg_ontime=sum(x['on_time_rate'] for x in performance)/len(performance)
        avg_defects=sum(x['defect_rate'] for x in performance)/len(performance)
        sources='; '.join(f"{x['observed_on']} {x['source_url']}" for x in performance)
        if avg_ontime<.8: factors.append({'label':'Low recorded on-time delivery rate','points':15,'basis':f'{avg_ontime:.0%} average across {len(performance)} reviewer-entered observations. Sources: {sources}'})
        if avg_defects>.1: factors.append({'label':'Elevated recorded defect rate','points':15,'basis':f'{avg_defects:.0%} average across {len(performance)} reviewer-entered observations. Sources: {sources}'})
    if screen and screen['candidate'] and screen['decision']=='pending': factors.append({'label':'Potential sanctions name match awaiting review' if screen['source']=='OFAC SDN' else 'Synthetic name-match fixture awaiting review','points':30,'basis':f"{screen['source']} name similarity only; identity is unconfirmed. Source record: {screen['source_ref']}"})
    if screen and screen['candidate'] and screen['decision']=='confirmed': factors.append({'label':'Potential match confirmed by reviewer' if screen['source']=='OFAC SDN' else 'Synthetic fixture confirmed by reviewer','points':30,'basis':f"Human review required; source: {screen['source']} record {screen['source_ref']}"})
    coverage=round(100*(bool(s['identifier'])+bool(ev)+bool(screen))/3)
    return {**s,'identifier_status':identifier_status(s['identifier']),'evidence':ev,'documents':docs,'performance':performance,'audit':audit,'screening':screen,'risk':{'score':min(100,sum(x['points'] for x in factors)),'coverage':coverage,'confidence':'Limited' if coverage<100 else 'Moderate','factors':factors,'review_status':'Review required' if factors else 'No indicators recorded'}}

def audit(db,sid,actor,action,detail):
    db.execute('INSERT INTO audit_events(supplier_id,occurred_at,actor,action,detail) VALUES(?,?,?,?,?)',(sid,datetime.now(timezone.utc).isoformat(),actor,action,detail))

@app.get('/api/suppliers')
def list_suppliers(q: str = '', category: str = ''):
    with connection() as db:
        ids=[r['id'] for r in db.execute('SELECT id FROM suppliers WHERE lower(name) LIKE ? AND lower(category) LIKE ? ORDER BY id DESC',('%'+q.lower()+'%','%'+category.lower()+'%'))]
        return [details(db,i) for i in ids]

@app.post('/api/suppliers', status_code=201)
def create_supplier(s: Supplier):
    with connection() as db:
        cur=db.execute('INSERT INTO suppliers(name,country,category,identifier,contact,website,created_at) VALUES(?,?,?,?,?,?,?)',(*[getattr(s,x).strip() for x in ('name','country','category','identifier','contact','website')],date.today().isoformat()))
        audit(db,cur.lastrowid,'local analyst','supplier_created',s.name)
        return details(db,cur.lastrowid)

@app.get('/api/suppliers/{sid}')
def supplier(sid:int):
    with connection() as db: return details(db,sid)

@app.put('/api/suppliers/{sid}')
def update_supplier(sid:int,s:Supplier):
    with connection() as db:
        get_supplier(db,sid)
        db.execute('UPDATE suppliers SET name=?,country=?,category=?,identifier=?,contact=?,website=? WHERE id=?',(*[getattr(s,x).strip() for x in ('name','country','category','identifier','contact','website')],sid))
        audit(db,sid,'local analyst','supplier_updated',s.name)
        return details(db,sid)

@app.delete('/api/suppliers/{sid}')
def delete_supplier(sid:int):
    with connection() as db:
        supplier=get_supplier(db,sid); audit(db,sid,'local analyst','supplier_deleted',supplier['name']); db.execute('DELETE FROM suppliers WHERE id=?',(sid,))
        return {'deleted':True}

@app.post('/api/suppliers/{sid}/evidence')
def add_evidence(sid:int,e:Evidence):
    if e.status not in ('verified','unverified','inconclusive'): raise HTTPException(422,'Invalid evidence status')
    with connection() as db:
        get_supplier(db,sid)
        db.execute('INSERT INTO evidence(supplier_id,source_url,reviewer,verified_on,status,notes) VALUES(?,?,?,?,?,?)',(sid,e.source_url,e.reviewer,e.verified_on.isoformat(),e.status,e.notes))
        audit(db,sid,e.reviewer,'evidence_recorded',e.status+' '+e.source_url)
        return details(db,sid)

@app.post('/api/suppliers/{sid}/performance')
def add_performance(sid:int,p:Performance):
    with connection() as db:
        get_supplier(db,sid)
        db.execute('INSERT INTO performance(supplier_id,observed_on,on_time_rate,defect_rate,source_url,reviewer,notes) VALUES(?,?,?,?,?,?,?)',(sid,p.observed_on.isoformat(),p.on_time_rate,p.defect_rate,p.source_url,p.reviewer,p.notes))
        audit(db,sid,p.reviewer,'performance_observed',f'on-time {p.on_time_rate:.0%}; defects {p.defect_rate:.0%}; '+p.source_url)
        return details(db,sid)

@app.post('/api/suppliers/{sid}/screen')
def screen(sid:int):
    with connection() as db:
        s=get_supplier(db,sid)
        snapshot=db.execute('SELECT * FROM ofac_snapshot WHERE id=1').fetchone()
        if not snapshot or not snapshot_fresh(snapshot['retrieved_at']): raise HTTPException(409,'Screening data is missing, future-dated, or older than 7 days. Refresh it before screening.')
        candidates=[]
        for record in json.loads(snapshot['records']):
            score=difflib.SequenceMatcher(None,normalize(s['name']),normalize(record['name'])).ratio()
            if score>=.80: candidates.append((score,record))
        candidates.sort(key=lambda x:x[0],reverse=True)
        for score,record in reversed(candidates[:10]):
            db.execute('INSERT INTO screenings(supplier_id,checked_at,candidate,similarity,source,source_ref) VALUES(?,?,?,?,?,?)',(sid,datetime.now(timezone.utc).isoformat(),record['name'],score,snapshot['source'],record['id']))
        if not candidates: db.execute('INSERT INTO screenings(supplier_id,checked_at,candidate,similarity,source,source_ref) VALUES(?,?,?,?,?,?)',(sid,datetime.now(timezone.utc).isoformat(),'','0',snapshot['source'],''))
        audit(db,sid,'local analyst','ofac_screening',f'{len(candidates)} potential candidate(s); {snapshot["source"]} snapshot {snapshot["retrieved_at"]}')
        return details(db,sid)

@app.post('/api/screening/ofac/refresh')
def refresh_ofac():
    url='https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV'
    request=urllib.request.Request(url,headers={'User-Agent':'SupplierTrust/1.0 (supplier screening dataset refresh)'})
    try:
        with urllib.request.build_opener(OfacRedirectHandler).open(request,timeout=30) as response:
            if urlsplit(response.geturl()).hostname not in OFAC_HOSTS or urlsplit(response.geturl()).scheme!='https': raise ValueError('Unexpected redirect host')
            raw=response.read(15*1024*1024+1)
        if len(raw)>15*1024*1024: raise ValueError('Dataset is too large')
        records=parse_ofac_csv(raw)
        if len(records)<1000: raise ValueError('Downloaded dataset failed validation')
    except Exception as e: raise HTTPException(503,f'OFAC dataset refresh failed; existing snapshot retained: {type(e).__name__}')
    digest=hashlib.sha256(raw).hexdigest(); retrieved=datetime.now(timezone.utc).isoformat()
    with connection() as db:
        db.execute('INSERT INTO ofac_snapshot(id,retrieved_at,sha256,records,source) VALUES(1,?,?,?,?) ON CONFLICT(id) DO UPDATE SET retrieved_at=excluded.retrieved_at,sha256=excluded.sha256,records=excluded.records,source=excluded.source',(retrieved,digest,json.dumps(records),'OFAC SDN'))
    return {'source':'OFAC SDN','source_url':url,'retrieved_at':retrieved,'sha256':digest,'record_count':len(records)}

@app.get('/api/screening/status')
def screening_status():
    with connection() as db:
        row=db.execute('SELECT retrieved_at,sha256,source FROM ofac_snapshot WHERE id=1').fetchone()
        return {'status':'available' if row else 'not_checked','source':row['source'] if row else 'OFAC SDN','source_url':'https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV' if not row or row['source']=='OFAC SDN' else None,'retrieved_at':row['retrieved_at'] if row else None,'sha256':row['sha256'] if row else None}

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
        audit(db,sid,'local analyst','document_uploaded',Path(file.filename).name[:200])
        return details(db,sid)

@app.post('/api/screenings/{screen_id}/decision')
def decide(screen_id:int,d:Decision):
    if d.decision not in ('false_positive','confirmed','pending'): raise HTTPException(422,'Invalid decision')
    with connection() as db:
        row=db.execute('SELECT * FROM screenings WHERE id=?',(screen_id,)).fetchone()
        if not row or not row['candidate']: raise HTTPException(404,'Candidate not found')
        db.execute('UPDATE screenings SET decision=?,reviewer=?,note=? WHERE id=?',(d.decision,d.reviewer,d.note,screen_id))
        audit(db,row['supplier_id'],d.reviewer,'screening_decision',d.decision+': '+d.note)
        return details(db,row['supplier_id'])

@app.get('/api/suppliers/{sid}/report', response_class=PlainTextResponse)
def report(sid:int):
    with connection() as db: s=details(db,sid)
    screening='Not checked'
    if s['screening']:
        x=s['screening']; provenance=f" | Retrieved {x['source_snapshot_at']} | SHA-256 {x['source_sha256']}" if x.get('source_snapshot_at') else ''
        screening=f"{x['source']}{provenance} | record {x['source_ref'] or 'none'} | {x['candidate'] or 'no candidate'} | decision {x['decision']} | reviewer {x['reviewer']} | rationale {x['note']}"
    lines=['SUPPLIERTRUST — DUE DILIGENCE REPORT',f"Generated: {date.today().isoformat()}",f"Supplier: {s['name']}",f"Country: {s['country']} | Category: {s['category']}",f"Identifier: {s['identifier'] or 'Not provided'} ({s['identifier_status']})",f"Risk index: {s['risk']['score']}/100 | Evidence coverage: {s['risk']['coverage']}% | Confidence: {s['risk']['confidence']}",f"Review status: {s['risk']['review_status']}",'','RISK INDICATORS']
    lines += [f"- {f['label']} (+{f['points']}): {f['basis']}" for f in s['risk']['factors']] or ['- No indicators recorded.']
    lines += ['','EVIDENCE']+[f"- {e['status']} | {e['verified_on']} | {e['reviewer']} | {e['source_url']} | {e['notes']}" for e in s['evidence']]
    lines += ['',f'Screening: {screening}','A potential name match is not proof of identity or wrongdoing; analyst review is required.','Identifier format validation does not establish registration or active status.','Follow-up: independently verify registration and review supporting documents.','This index is not a probability of fraud or regulatory certification.']
    return PlainTextResponse('\n'.join(lines),headers={'Content-Disposition':f'attachment; filename="supplier-{sid}-report.txt"'})
