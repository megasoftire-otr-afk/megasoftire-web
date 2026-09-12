import os
import secrets
import datetime as dt
from typing import Optional

import flet.fastapi as flet_fastapi
from fastapi import Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import main as megasoft_main
from database import init_db, query, authenticate

# Initialize the same database used by MegaSoftire Web.
init_db()

app = flet_fastapi.FastAPI(title='MegaSoftire Web + Mobile API')

# Mobile origin. Override in Render with MEGASOFTIRE_MOBILE_ORIGIN if needed.
mobile_origin = os.environ.get(
    'MEGASOFTIRE_MOBILE_ORIGIN',
    'https://megasoftire-movil.onrender.com',
).rstrip('/')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[mobile_origin, 'http://localhost:8000', 'http://127.0.0.1:8000'],
    allow_credentials=False,
    allow_methods=['GET', 'POST', 'OPTIONS'],
    allow_headers=['Authorization', 'Content-Type'],
)

# Prototype session tokens: enough for the first read-only integration test.
# They are intentionally held in memory; restarting Render invalidates them.
TOKENS: dict[str, dict] = {}


class LoginBody(BaseModel):
    username: str
    password: str


def _to_iso_date(value) -> Optional[str]:
    if value in (None, ''):
        return None
    raw = str(value).strip()
    try:
        f = float(raw)
        if f.is_integer() and 1 <= f <= 100000:
            return (dt.date(1899, 12, 30) + dt.timedelta(days=int(f))).isoformat()
    except Exception:
        pass
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return dt.datetime.strptime(raw[:10], fmt).date().isoformat()
        except Exception:
            pass
    return raw


def _auth_user(authorization: Optional[str] = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Sesión requerida.')
    token = authorization.split(' ', 1)[1].strip()
    user = TOKENS.get(token)
    if not user:
        raise HTTPException(status_code=401, detail='Sesión inválida o vencida.')
    return user


@app.get('/api/mobile/health')
def mobile_health():
    return {'ok': True, 'service': 'MegaSoftire Web', 'api': 'mobile-read-v0.1'}


@app.post('/api/mobile/login')
def mobile_login(body: LoginBody):
    row = authenticate(body.username, body.password)
    if not row:
        raise HTTPException(status_code=401, detail='Usuario o clave incorrectos.')
    token = secrets.token_urlsafe(32)
    user = dict(row)
    TOKENS[token] = user
    return {
        'token': token,
        'user': {
            'id': user.get('id'),
            'username': user.get('username'),
            'full_name': user.get('full_name'),
            'role': user.get('role'),
        },
    }


@app.get('/api/mobile/equipment')
def mobile_equipment(user=Depends(_auth_user)):
    rows = query(
        '''SELECT id,code,brand,model,location,vehicle_type,active
           FROM equipment
           WHERE active=1
           ORDER BY code'''
    )
    return [dict(r) for r in rows]


@app.get('/api/mobile/equipment/{equipment_id}/tires')
def mobile_equipment_tires(equipment_id: int, user=Depends(_auth_user)):
    rows = query(
        '''SELECT t.id,t.code,t.serial,t.brand,t.size,t.design,t.status,
                  t.equipment_id,t.position,t.current_meter,t.tread_inner,t.tread_outer,
                  t.new_tread,t.recommended_pressure,e.code AS equipment_code
           FROM tires t
           LEFT JOIN equipment e ON e.id=t.equipment_id
           WHERE t.equipment_id=? AND t.status='SERVICIO'
           ORDER BY CAST(COALESCE(NULLIF(t.position,''),'999') AS INTEGER),t.code''',
        (equipment_id,),
    )
    return [dict(r) for r in rows]


@app.get('/api/mobile/tire/{tire_id}')
def mobile_tire(tire_id: int, user=Depends(_auth_user)):
    rows = query(
        '''SELECT t.id,t.code,t.serial,t.brand,t.size,t.design,t.status,
                  t.equipment_id,t.position,t.current_meter,t.tread_inner,t.tread_outer,
                  t.new_tread,t.recommended_pressure,e.code AS equipment_code,e.location AS equipment_location
           FROM tires t
           LEFT JOIN equipment e ON e.id=t.equipment_id
           WHERE t.id=?''',
        (tire_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail='Neumático no encontrado.')
    tire = dict(rows[0])
    last = query(
        '''SELECT o.id,o.event_code,o.event_date,o.meter,o.tread_inner,o.tread_outer,
                  o.pressure,o.pressure_condition,o.location,e.code AS equipment_code,o.position
           FROM occurrences o
           LEFT JOIN equipment e ON e.id=o.equipment_id
           WHERE o.tire_id=?
           ORDER BY o.id DESC LIMIT 1''',
        (tire_id,),
    )
    last_event = dict(last[0]) if last else None
    if last_event:
        last_event['event_date'] = _to_iso_date(last_event.get('event_date'))
    tire['last_event'] = last_event
    return tire


@app.get('/api/mobile/tire/{tire_id}/history')
def mobile_tire_history(tire_id: int, limit: int = 5, user=Depends(_auth_user)):
    limit = max(1, min(int(limit), 20))
    rows = query(
        '''SELECT o.id,o.event_code,o.event_date,o.meter,o.tread_inner,o.tread_outer,
                  o.pressure,o.pressure_condition,o.reason,o.location,o.notes,
                  e.code AS equipment_code,o.position
           FROM occurrences o
           LEFT JOIN equipment e ON e.id=o.equipment_id
           WHERE o.tire_id=?
           ORDER BY o.id DESC LIMIT ?''',
        (tire_id, limit),
    )
    result = []
    for r in rows:
        item = dict(r)
        item['event_date'] = _to_iso_date(item.get('event_date'))
        result.append(item)
    return result


# IMPORTANT: mount Flet last because its root app contains a SPA catch-all.
app.mount('/', flet_fastapi.app(megasoft_main.main))
