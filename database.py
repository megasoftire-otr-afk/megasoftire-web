from pathlib import Path
import os
import sqlite3
import hashlib

DB_PATH = Path(os.environ.get('MEGASOFTIRE_DB_PATH', Path(__file__).parent / 'data' / 'megasoftire.db'))

SCHEMA = '''
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL,
 full_name TEXT,
 role TEXT NOT NULL DEFAULT 'ADMIN',
 active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS equipment(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 code TEXT NOT NULL UNIQUE,
 brand TEXT, model TEXT, location TEXT, vehicle_type TEXT,
 tire_size TEXT, hours_per_day REAL DEFAULT 0, active INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS tires(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 code TEXT NOT NULL UNIQUE, serial TEXT, brand TEXT, size TEXT, design TEXT,
 new_tread REAL DEFAULT 0, recommended_pressure REAL DEFAULT 0,
 projected_life REAL DEFAULT 0, status TEXT NOT NULL DEFAULT 'STAND-BY',
 equipment_id INTEGER, position TEXT, current_meter REAL,
 tread_inner REAL, tread_outer REAL,
 FOREIGN KEY(equipment_id) REFERENCES equipment(id)
);
CREATE TABLE IF NOT EXISTS occurrences(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 tire_id INTEGER NOT NULL, event_code TEXT NOT NULL, event_date TEXT NOT NULL,
 equipment_id INTEGER, position TEXT, meter REAL,
 tread_inner REAL, tread_outer REAL, pressure REAL,
 pressure_condition TEXT, reason TEXT, location TEXT, notes TEXT,
 created_at TEXT DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(tire_id) REFERENCES tires(id),
 FOREIGN KEY(equipment_id) REFERENCES equipment(id)
);
CREATE TABLE IF NOT EXISTS app_meta(
 key TEXT PRIMARY KEY,
 value TEXT
);
CREATE INDEX IF NOT EXISTS idx_occ_tire_date ON occurrences(tire_id,event_date,id);
CREATE INDEX IF NOT EXISTS idx_tires_status ON tires(status);
'''

MIGRATION_KEY = 'nexa_cat50_v2'


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    return con


def _seed_nexa_cat50(con):
    """Migración única del CAT 50 usando PROYECTO2/NEXA como fuente oficial."""
    done = con.execute('SELECT value FROM app_meta WHERE key=?', (MIGRATION_KEY,)).fetchone()
    if done:
        return

    con.execute(
        '''INSERT INTO equipment(code,brand,model,location,vehicle_type,tire_size,hours_per_day,active)
           VALUES(?,?,?,?,?,?,?,1)
           ON CONFLICT(code) DO UPDATE SET
             brand=excluded.brand, model=excluded.model, location=excluded.location,
             vehicle_type=excluded.vehicle_type, tire_size=excluded.tire_size, active=1''',
        ('CAT 50', 'CATERPILLA', 'R1600H', 'MINA', 'SCOOP', '18.00-25', 0),
    )
    eq_id = con.execute("SELECT id FROM equipment WHERE code='CAT 50'").fetchone()['id']

    # Estado actual confirmado en LLANTA/OCTIRE del PROYECTO2/NEXA.
    tires = [
        ('1376','12251Y10060','GOODYEAR','18.00-25','SMO-5D',84.0,90,4815,'1',5019,75.0,70.0),
        ('1362','12251Y10747','GOODYEAR','18.00-25','SMO-5D',84.0,90,2278,'2',5019,67.0,60.0),
        ('1378','12251Y10332','GOODYEAR','18.00-25','SMO-5D',84.0,90,3500,'3',5019,77.0,73.0),
        ('1367','122251Y100700','GOODYEAR','18.00-25','SMO-5D',84.0,90,1129,'4',5019,55.0,50.0),
    ]
    for code, serial, brand, size, design, new_tread, pressure, proj, pos, meter, tin, tout in tires:
        con.execute(
            '''INSERT INTO tires(code,serial,brand,size,design,new_tread,recommended_pressure,
               projected_life,status,equipment_id,position,current_meter,tread_inner,tread_outer)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(code) DO UPDATE SET
                 serial=excluded.serial, brand=excluded.brand, size=excluded.size, design=excluded.design,
                 new_tread=excluded.new_tread, recommended_pressure=excluded.recommended_pressure,
                 projected_life=excluded.projected_life, status='SERVICIO', equipment_id=excluded.equipment_id,
                 position=excluded.position, current_meter=excluded.current_meter,
                 tread_inner=excluded.tread_inner, tread_outer=excluded.tread_outer''',
            (code, serial, brand, size, design, new_tread, pressure, proj, 'SERVICIO', eq_id, pos, meter, tin, tout),
        )

    # Primera migración: sustituye los movimientos de demostración de estos cuatro códigos
    # por los eventos oficiales NEXA. Esto NO vuelve a ejecutarse en reinicios posteriores.
    codes = tuple(t[0] for t in tires)
    qmarks = ','.join('?' for _ in codes)
    con.execute(
        'DELETE FROM occurrences WHERE tire_id IN (SELECT id FROM tires WHERE code IN (' + qmarks + '))',
        codes,
    )

    history = [
        ('1376','INST','2026-05-07','1',4056,84,84,90,'MINA'),
        ('1376','INSP','2026-07-09','1',5019,75,70,90,'MINA'),
        ('1362','INST','2026-04-10','2',4056,84,84,90,''),
        ('1362','INSP','2026-07-09','2',5019,67,60,90,'MINA'),
        ('1378','INST','2026-05-22','3',4494,84,84,90,'MINA'),
        ('1378','INSP','2026-07-09','3',5019,77,73,90,'MINA'),
        ('1367','INST','2026-04-11','4',4071,84,84,90,''),
        ('1367','INSP','2026-07-09','4',5019,55,50,90,'MINA'),
    ]
    for code, event, date, pos, meter, tin, tout, pressure, loc in history:
        tire_id = con.execute('SELECT id FROM tires WHERE code=?', (code,)).fetchone()['id']
        con.execute(
            '''INSERT INTO occurrences(tire_id,event_code,event_date,equipment_id,position,meter,
               tread_inner,tread_outer,pressure,location,notes)
               VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
            (tire_id, event, date, eq_id, pos, meter, tin, tout, pressure, loc, 'Migrado desde PROYECTO2/NEXA'),
        )

    con.execute('INSERT OR REPLACE INTO app_meta(key,value) VALUES(?,?)', (MIGRATION_KEY, '2026-08-28'))


def init_db():
    with connect() as con:
        con.executescript(SCHEMA)
        exists = con.execute("SELECT id FROM users WHERE username='admin'").fetchone()
        if not exists:
            con.execute(
                'INSERT INTO users(username,password_hash,full_name,role) VALUES(?,?,?,?)',
                ('admin', _hash_password('Admin2026!'), 'Administrador MegaSoftire', 'ADMIN'),
            )
        _seed_nexa_cat50(con)
        con.commit()


def authenticate(username: str, password: str):
    with connect() as con:
        return con.execute(
            'SELECT id,username,full_name,role FROM users WHERE username=? AND password_hash=? AND active=1',
            (username.strip(), _hash_password(password)),
        ).fetchone()


def query(sql, params=()):
    with connect() as con:
        return con.execute(sql, params).fetchall()


def execute(sql, params=()):
    with connect() as con:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid
