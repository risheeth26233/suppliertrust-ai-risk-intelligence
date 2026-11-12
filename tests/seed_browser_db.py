from datetime import datetime, timezone
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.main import connection

with connection() as db:
    for table in ('audit_events','documents','performance','evidence','screenings','suppliers'):
        db.execute(f'DELETE FROM {table}')
    db.execute('DELETE FROM ofac_snapshot WHERE id=1')
    db.execute('INSERT INTO ofac_snapshot(id,retrieved_at,sha256,records,source) VALUES(1,?,?,?,?)',(datetime.now(timezone.utc).isoformat(),'browser-fixture','[{"id":"BROWSER-1","name":"Fictional Example Trading Co"}]','Synthetic browser fixture'))
