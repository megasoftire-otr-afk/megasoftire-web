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

# ===== CARGA MASIVA DESDE EXCEL 2026-08-29 =====
EXCEL_EQUIPOS = [['SC-47', 'CATERPILLAR', 'R1600H', 'Scoop ', 'MINA', '18.00-25', 20, 'SI', None], ['SC-50', 'CATERPILLAR', 'R1600H', 'Scoop ', 'MINA', '18.00-25', 20, 'SI', None], ['SC-39', 'CATERPILLAR', 'R2900G', 'Scoop ', 'MINA', '29.5-29', 20, 'SI', None], ['SC-42', 'CATERPILLAR', 'R2900G', 'Scoop ', 'MINA', '29.5-29', 20, 'SI', None], ['SC-43', 'CATERPILLAR', 'R2900G', 'Scoop ', 'MINA', '29.5-29', 20, 'SI', None], ['SC-44', 'CATERPILLAR', 'R2900G', 'Scoop ', 'MINA', '29.5-29', 20, 'SI', None], ['SC-46', 'CATERPILLAR', 'R2900XE', 'Scoop ', 'MINA', '29.5-29', 20, 'SI', None], ['SC-48', 'CATERPILLAR', 'R2900XE', 'Scoop ', 'MINA', '29.5-29', 20, 'SI', None], ['SC-51', 'CATERPILLAR', 'R2900XE', 'Scoop ', 'MINA', '29.5-29', 20, 'SI', None]]
EXCEL_NEUMATICOS = [[1345, None, 'Goodyear', '18.00-25', 'SMO-5D', 84, 100, 3953, 'STAND-BY', 'SC-47', 1, 4943, 71, 74, 46212, 3850, 2000, 'MINA', 'Ejemplo NEXA'], [1350, None, 'Goodyear', '18.00-25', 'SMO-5D', 84, 100, 4060, 'STAND-BY', 'SC-47', 2, 4943, 73, 76, 46212, 3850, 2000, 'MINA', 'Ejemplo NEXA'], [1351, None, 'Goodyear', '18.00-25', 'SMO-5D', 84, 100, 4060, 'STAND-BY', 'SC-47', 3, 4943, 70, 74, 46212, 3850, 2000, 'MINA', 'Ejemplo NEXA'], [1352, None, 'Goodyear', '18.00-25', 'SMO-5D', 84, 100, 4060, 'SERVICIO', 'SC-47', 4, 4943, 70, 74, 46212, 3850, 2000, 'MINA', 'Ejemplo NEXA'], [1376, None, 'Goodyear', '18.00-25', 'SMO-5D', 84, 100, 4056.4, 'SERVICIO', 'SC-50', 1, 5019, 70, 75, 46212, 3850, 2000, 'MINA', 'Ejemplo NEXA'], [1362, None, 'Goodyear', '18.00-25', 'SMO-5D', 84, 100, 4056.4, 'SERVICIO', 'SC-50', 2, 5019, 60, 67, 46212, 3850, 2000, 'MINA', 'Ejemplo NEXA'], [1378, None, 'Goodyear', '18.00-25', 'SMO-5D', 84, 100, 4493.6, 'SERVICIO', 'SC-50', 3, 5019, 73, 77, 46212, 3850, 2000, 'MINA', 'Ejemplo NEXA'], [1367, None, 'Goodyear', '18.00-25', 'SMO-5D', 84, 100, 4070.8, 'SERVICIO', 'SC-50', 4, 5019, 50, 55, 46212, 3850, 2000, 'MINA', 'Ejemplo NEXA'], [1363, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 26282.8, 'SERVICIO', 'SC-39', 1, 27236, 81, 84, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1364, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 26282.8, 'SERVICIO', 'SC-39', 2, 27236, 75, 78, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1365, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 26282.8, 'SERVICIO', 'SC-39', 3, 27236, 78, 78, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1366, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 26282.8, 'SERVICIO', 'SC-39', 4, 27236, 83, 78, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1374, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 16846.8, 'SERVICIO', 'SC-42', 1, 17631, 83, 87, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1375, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 16846.8, 'SERVICIO', 'SC-42', 2, 17631, 87, 83, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1354, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 16421.8, 'SERVICIO', 'SC-42', 3, 17631, 77, 89, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1377, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 17102.1, 'SERVICIO', 'SC-42', 4, 17631, 91, 94, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1346, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 14776, 'SERVICIO', 'SC-43', 1, 16353, 57, 71, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1357, None, 'yokohama', '29.5-29', 'Y524', 104, 100, 15124, 'SERVICIO', 'SC-43', 2, 16353, 65, 73, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1320, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 13870.5, 'SERVICIO', 'SC-43', 3, 16353, 33, 44, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1321, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 13870.5, 'SERVICIO', 'SC-43', 4, 16832, 39, 50, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1359, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 15165.6, 'SERVICIO', 'SC-44', 1, 16282, 65, 75, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1355, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 15210.4, 'SERVICIO', 'SC-44', 2, 16282, 66, 73, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1316, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 13355.1, 'SERVICIO', 'SC-44', 3, 16282, 33, 44, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1317, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 13355.1, 'SERVICIO', 'SC-44', 4, 16282, 43, 50, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1370, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 6459.4, 'SERVICIO', 'SC-46', 1, 7392, 81, 85, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1349, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 5871, 'SERVICIO', 'SC-46', 2, 7392, 65, 72, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1329, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 5150.7, 'SERVICIO', 'SC-46', 3, 7392, 56, 60, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1344, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 5620, 'SERVICIO', 'SC-46', 4, 7392, 67, 71, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1353, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 5923.6, 'SERVICIO', 'SC-48', 1, 7438, 66, 73, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1358, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 6040.1, 'SERVICIO', 'SC-48', 2, 7438, 67, 74, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1327, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 4810.5, 'SERVICIO', 'SC-48', 3, 7438, 49, 60, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1328, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 4810.5, 'SERVICIO', 'SC-48', 4, 7438, 46, 58, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1371, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 3707.1, 'SERVICIO', 'SC-51', 1, 4708, 76, 81, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1372, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 3707.1, 'SERVICIO', 'SC-51', 2, 4708, 76, 81, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1324, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 2029.4, 'SERVICIO', 'SC-51', 3, 4708, 30, 43, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA'], [1373, None, 'Yokohama', '29.5-29', 'Y524', 104, 100, 3758.6, 'SERVICIO', 'SC-51', 4, 4708, 83, 85, 46212, 7800, 2000, 'MINA', 'Ejemplo NEXA']]
EXCEL_MOVIMIENTOS = [[1345, 46143, 'INST', 'SC-47', 1, 3953, 84, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1350, 46143, 'INST', 'SC-47', 2, 4060, 84, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1351, 46143, 'INST', 'SC-47', 3, 4060, 84, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1352, 46143, 'INST', 'SC-47', 4, 4060, 84, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1376, 46143, 'INST', 'SC-50', 1, 4056.4, 84, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1362, 46143, 'INST', 'SC-50', 2, 4056.4, 84, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1378, 46143, 'INST', 'SC-50', 3, 4493.6, 84, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1367, 46143, 'INST', 'SC-50', 4, 4070.8, 84, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1363, 46143, 'INST', 'SC-39', 1, 26282.8, 84, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1364, 46143, 'INST', 'SC-39', 2, 26282.8, 84, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1365, 46143, 'INST', 'SC-39', 3, 26282.8, 84, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1366, 46143, 'INST', 'SC-39', 4, 26282.8, 84, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1374, 46143, 'INST', 'SC-42', 1, 16846.8, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1375, 46143, 'INST', 'SC-42', 2, 16846.8, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1354, 46143, 'INST', 'SC-42', 3, 16421.8, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1377, 46143, 'INST', 'SC-42', 4, 17102.1, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1346, 46143, 'INST', 'SC-43', 1, 14776, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1357, 46143, 'INST', 'SC-43', 2, 15124, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1320, 46143, 'INST', 'SC-43', 3, 13870.5, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1321, 46143, 'INST', 'SC-43', 4, 13870.5, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1359, 46143, 'INST', 'SC-44', 1, 15165.6, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1355, 46143, 'INST', 'SC-44', 2, 15210.4, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1316, 46143, 'INST', 'SC-44', 3, 13355.1, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1317, 46143, 'INST', 'SC-44', 4, 13355.1, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1370, 46143, 'INST', 'SC-46', 1, 6459.4, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1349, 46143, 'INST', 'SC-46', 2, 5871, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1329, 46143, 'INST', 'SC-46', 3, 5150.7, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1344, 46143, 'INST', 'SC-46', 4, 5620, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1353, 46143, 'INST', 'SC-48', 1, 5923.6, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1358, 46143, 'INST', 'SC-48', 2, 6040.1, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1327, 46143, 'INST', 'SC-48', 3, 4810.5, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1328, 46143, 'INST', 'SC-48', 4, 4810.5, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1371, 46143, 'INST', 'SC-51', 1, 3707.1, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1372, 46143, 'INST', 'SC-51', 2, 3707.1, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1324, 46143, 'INST', 'SC-51', 3, 2029.4, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1373, 46143, 'INST', 'SC-51', 4, 3758.6, 104, 104, 100, 'FRIO', None, 'MINA', 'NEXA'], [1345, 46212, 'INSP', 'SC-47', 1, 4943, 71, 74, 90, 'FRIO', None, 'MINA', 'NEXA'], [1350, 46212, 'INSP', 'SC-47', 2, 4943, 73, 76, 90, 'FRIO', None, 'MINA', 'NEXA'], [1351, 46212, 'INSP', 'SC-47', 3, 4943, 70, 74, 90, 'FRIO', None, 'MINA', 'NEXA'], [1352, 46212, 'INSP', 'SC-47', 4, 4943, 70, 74, 90, 'FRIO', None, 'MINA', 'NEXA'], [1376, 46212, 'INSP', 'SC-50', 1, 5019, 70, 75, 90, 'FRIO', None, 'MINA', 'NEXA'], [1362, 46212, 'INSP', 'SC-50', 2, 5019, 60, 67, 90, 'FRIO', None, 'MINA', 'NEXA'], [1378, 46212, 'INSP', 'SC-50', 3, 5019, 73, 77, 90, 'FRIO', None, 'MINA', 'NEXA'], [1367, 46212, 'INSP', 'SC-50', 4, 5019, 50, 55, 90, 'FRIO', None, 'MINA', 'NEXA'], [1363, 46212, 'INSP', 'SC-39', 1, 27236, 81, 84, 90, 'FRIO', None, 'MINA', 'NEXA'], [1364, 46212, 'INSP', 'SC-39', 2, 27236, 75, 78, 90, 'FRIO', None, 'MINA', 'NEXA'], [1365, 46212, 'INSP', 'SC-39', 3, 27236, 78, 78, 90, 'FRIO', None, 'MINA', 'NEXA'], [1366, 46212, 'INSP', 'SC-39', 4, 27236, 83, 78, 90, 'FRIO', None, 'MINA', 'NEXA'], [1374, 46212, 'INSP', 'SC-42', 1, 17631, 83, 87, 100, 'FRIO', None, 'MINA', 'NEXA'], [1375, 46212, 'INSP', 'SC-42', 2, 17631, 87, 83, 100, 'FRIO', None, 'MINA', 'NEXA'], [1354, 46212, 'INSP', 'SC-42', 3, 17631, 77, 89, 100, 'FRIO', None, 'MINA', 'NEXA'], [1377, 46212, 'INSP', 'SC-42', 4, 17631, 91, 94, 100, 'FRIO', None, 'MINA', 'NEXA'], [1346, 46212, 'INSP', 'SC-43', 1, 16353, 57, 71, 100, 'FRIO', None, 'MINA', 'NEXA'], [1357, 46212, 'INSP', 'SC-43', 2, 16353, 65, 73, 100, 'FRIO', None, 'MINA', 'NEXA'], [1320, 46212, 'INSP', 'SC-43', 3, 16353, 33, 44, 100, 'FRIO', None, 'MINA', 'NEXA'], [1321, 46212, 'INSP', 'SC-43', 4, 16832, 39, 50, 100, 'FRIO', None, 'MINA', 'NEXA'], [1359, 46212, 'INSP', 'SC-44', 1, 16282, 65, 75, 100, 'FRIO', None, 'MINA', 'NEXA'], [1355, 46212, 'INSP', 'SC-44', 2, 16282, 66, 73, 100, 'FRIO', None, 'MINA', 'NEXA'], [1316, 46212, 'INSP', 'SC-44', 3, 16282, 33, 44, 100, 'FRIO', None, 'MINA', 'NEXA'], [1317, 46212, 'INSP', 'SC-44', 4, 16282, 43, 50, 100, 'FRIO', None, 'MINA', 'NEXA'], [1370, 46212, 'INSP', 'SC-46', 1, 7392, 81, 85, 100, 'FRIO', None, 'MINA', 'NEXA'], [1349, 46212, 'INSP', 'SC-46', 2, 7392, 65, 72, 100, 'FRIO', None, 'MINA', 'NEXA'], [1329, 46212, 'INSP', 'SC-46', 3, 7392, 56, 60, 100, 'FRIO', None, 'MINA', 'NEXA'], [1344, 46212, 'INSP', 'SC-46', 4, 7392, 67, 71, 100, 'FRIO', None, 'MINA', 'NEXA'], [1353, 46212, 'INSP', 'SC-48', 1, 7438, 66, 73, 100, 'FRIO', None, 'MINA', 'NEXA'], [1358, 46212, 'INSP', 'SC-48', 2, 7438, 67, 74, 100, 'FRIO', None, 'MINA', 'NEXA'], [1327, 46212, 'INSP', 'SC-48', 3, 7438, 49, 60, 100, 'FRIO', None, 'MINA', 'NEXA'], [1328, 46212, 'INSP', 'SC-48', 4, 7438, 46, 58, 100, 'FRIO', None, 'MINA', 'NEXA'], [1371, 46212, 'INSP', 'SC-51', 1, 4708, 76, 81, 100, 'FRIO', None, 'MINA', 'NEXA'], [1372, 46212, 'INSP', 'SC-51', 2, 4708, 76, 81, 100, 'FRIO', None, 'MINA', 'NEXA'], [1324, 46212, 'INSP', 'SC-51', 3, 4708, 30, 43, 100, 'FRIO', None, 'MINA', 'NEXA'], [1373, 46212, 'INSP', 'SC-51', 4, 4708, 83, 85, 100, 'FRIO', None, 'MINA', 'NEXA']]

def seed_excel_carga_masiva():
    """Importación idempotente de la plantilla Excel suministrada por el usuario."""
    marker = "excel_carga_masiva_20260829_v1"
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS app_migrations(
            migration_key TEXT PRIMARY KEY, applied_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        if con.execute("SELECT 1 FROM app_migrations WHERE migration_key=?", (marker,)).fetchone():
            return

        # Equipos
        for r in EXCEL_EQUIPOS:
            code,brand,model,vtype,location,tire_size,hours_day,active,notes = r
            con.execute("""INSERT INTO equipment(code,brand,model,location,vehicle_type,tire_size,hours_per_day,active)
                VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(code) DO UPDATE SET brand=excluded.brand,model=excluded.model,
                location=excluded.location,vehicle_type=excluded.vehicle_type,tire_size=excluded.tire_size,
                hours_per_day=excluded.hours_per_day,active=excluded.active""",
                (str(code).strip(), brand, model, location, str(vtype).strip() if vtype else None,
                 tire_size, hours_day or 0, 1 if str(active).strip().upper()=="SI" else 0))

        # Neumáticos
        for r in EXCEL_NEUMATICOS:
            code,serial,brand,size,design,new_tread,pressure,install_meter,status,eq_code,pos,current_meter,tin,tout,purchase,cost,warranty,location,notes = r
            eq_id=None
            if eq_code:
                er=con.execute("SELECT id FROM equipment WHERE code=?",(str(eq_code).strip(),)).fetchone()
                eq_id=er["id"] if er else None
            con.execute("""INSERT INTO tires(code,serial,brand,size,design,new_tread,recommended_pressure,
                projected_life,status,equipment_id,position,current_meter,tread_inner,tread_outer)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(code) DO UPDATE SET serial=excluded.serial,brand=excluded.brand,size=excluded.size,
                design=excluded.design,new_tread=excluded.new_tread,recommended_pressure=excluded.recommended_pressure,
                status=excluded.status,equipment_id=excluded.equipment_id,position=excluded.position,
                current_meter=excluded.current_meter,tread_inner=excluded.tread_inner,tread_outer=excluded.tread_outer""",
                (str(code).strip(), serial, brand, size, design, new_tread, pressure, None,
                 str(status).strip().upper(), eq_id, str(pos).strip() if pos is not None else None,
                 current_meter,tin,tout))

        # Sustituir historial de los neumáticos incluidos por el historial entregado en Excel.
        codes=[str(r[0]).strip() for r in EXCEL_NEUMATICOS]
        if codes:
            qm=",".join("?" for _ in codes)
            con.execute("DELETE FROM occurrences WHERE tire_id IN (SELECT id FROM tires WHERE code IN ("+qm+"))", tuple(codes))

        for r in EXCEL_MOVIMIENTOS:
            code,date,event,eq_code,pos,meter,tin,tout,pressure,pcond,reason,location,notes=r
            tr=con.execute("SELECT id FROM tires WHERE code=?",(str(code).strip(),)).fetchone()
            if not tr: continue
            eq_id=None
            if eq_code:
                er=con.execute("SELECT id FROM equipment WHERE code=?",(str(eq_code).strip(),)).fetchone()
                eq_id=er["id"] if er else None
            con.execute("""INSERT INTO occurrences(tire_id,event_code,event_date,equipment_id,position,meter,
                tread_inner,tread_outer,pressure,pressure_condition,reason,location,notes)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (tr["id"],str(event).strip().upper(),date,eq_id,str(pos).strip() if pos is not None else None,
                 meter,tin,tout,pressure,pcond,reason,location,notes or "Carga Excel"))

        con.execute("INSERT INTO app_migrations(migration_key) VALUES(?)",(marker,))
        con.commit()

seed_excel_carga_masiva()
