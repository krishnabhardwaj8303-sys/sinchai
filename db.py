import sqlite3, os, datetime
BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "sinchai.db")
PHOTOS = os.path.join(BASE, "photos")
os.makedirs(PHOTOS, exist_ok=True)
SCHEMA = """
CREATE TABLE IF NOT EXISTS farmers(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT UNIQUE,
  village TEXT, crop TEXT, stage TEXT DEFAULT 'sowing', soil TEXT DEFAULT 'dorsa', lang TEXT DEFAULT 'hi',
  node_id TEXT DEFAULT 'NODE-01', photo TEXT DEFAULT '', status TEXT DEFAULT 'pending', created TEXT);
CREATE TABLE IF NOT EXISTS readings(id INTEGER PRIMARY KEY AUTOINCREMENT, node_id TEXT, moisture REAL, ts TEXT);
CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY AUTOINCREMENT, farmer_id INTEGER, phone TEXT,
  lang TEXT, code TEXT, text TEXT, status TEXT, ts TEXT);
"""

def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def run(sql, args=(), fetch=False):
    c = sqlite3.connect(DB, timeout=10)
    c.row_factory = sqlite3.Row
    try:
        c.executescript(SCHEMA)
        cur = c.execute(sql, args)
        rows = [dict(r) for r in cur.fetchall()] if fetch else None
        c.commit()
        return rows if fetch else cur.lastrowid
    finally:
        c.close()

def add_farmer(name, phone, village, crop, lang, photo=None, ext=".jpg", soil="dorsa", node="NODE-01", status="pending"):
    if run("SELECT id FROM farmers WHERE phone=?", (phone,), fetch=True):
        raise ValueError("dup")
    path = ""
    if photo:
        path = os.path.join(PHOTOS, f"{phone}{ext}")
        with open(path, "wb") as f:
            f.write(photo)
    return run("INSERT INTO farmers(name,phone,village,crop,lang,photo,soil,node_id,status,created) VALUES(?,?,?,?,?,?,?,?,?,?)",
               (name, phone, village, crop, lang, path, soil, node, status, _now()))

def farmers(status=None, node=None):
    q, a = "SELECT * FROM farmers WHERE 1=1", []
    if status: q += " AND status=?"; a.append(status)
    if node: q += " AND node_id=?"; a.append(node)
    return run(q + " ORDER BY id", tuple(a), fetch=True)

_OK = {"soil", "node_id", "status", "stage", "crop", "lang", "village", "name"}
def update_farmer(fid, **kw):
    kw = {k: v for k, v in kw.items() if k in _OK}
    if kw:
        run(f"UPDATE farmers SET {', '.join(k + '=?' for k in kw)} WHERE id=?", (*kw.values(), fid))

def nodes():
    return [r["node_id"] for r in run("SELECT DISTINCT node_id FROM farmers WHERE status='active' ORDER BY node_id", fetch=True)]

def add_reading(node, moisture):
    """ASLI HARDWARE YAHI CALL KAREGA: db.add_reading('NODE-01', 31.5)"""
    run("INSERT INTO readings(node_id,moisture,ts) VALUES(?,?,?)", (node, float(moisture), _now()))

def replace_history(node, values):
    run("DELETE FROM readings WHERE node_id=?", (node,))
    for v in values:
        add_reading(node, v)

def history(node, n=30):
    r = run("SELECT moisture FROM readings WHERE node_id=? ORDER BY id DESC LIMIT ?", (node, n), fetch=True)
    return [x["moisture"] for x in reversed(r)]

def queue_sms(fid, phone, lang, code, text, status):
    run("INSERT INTO outbox(farmer_id,phone,lang,code,text,status,ts) VALUES(?,?,?,?,?,?,?)",
        (fid, phone, lang, code, text, status, _now()))

def outbox(limit=100):
    return run("SELECT ts,phone,lang,code,text,status FROM outbox ORDER BY id DESC LIMIT ?", (limit,), fetch=True)