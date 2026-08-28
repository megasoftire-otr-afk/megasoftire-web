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
CREATE INDEX IF NOT EXISTS idx_occ_tire_date ON occurrences(tire_id,event_date,id);
CREATE INDEX IF NOT EXISTS idx_tires_status ON tires(status);
'''

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    return con

def init_db():
    with connect() as con:
        con.executescript(SCHEMA)
        exists = con.execute("SELECT id FROM users WHERE username='admin'").fetchone()
        if not exists:
            con.execute(
                'INSERT INTO users(username,password_hash,full_name,role) VALUES(?,?,?,?)',
                ('admin', _hash_password('Admin2026!'), 'Administrador MegaSoftire', 'ADMIN')
            )
        con.commit()

def authenticate(username: str, password: str):
    with connect() as con:
        return con.execute(
            'SELECT id,username,full_name,role FROM users WHERE username=? AND password_hash=? AND active=1',
            (username.strip(), _hash_password(password))
        ).fetchone()

def query(sql, params=()):
    with connect() as con:
        return con.execute(sql, params).fetchall()

def execute(sql, params=()):
    with connect() as con:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid
