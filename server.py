import os
import secrets
import datetime as dt
from typing import Optional

import flet.fastapi as flet_fastapi
from fastapi import Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import main as megasoft_main
from database import init_db, query, execute, authenticate

init_db()

app = flet_fastapi.FastAPI(title='MegaSoftire Web + Mobile API')

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

TOKENS: dict[str, dict] = {}

EVENT_LABELS = {
    'INST': 'Instalación',
    'INSP': 'Inspección',
    'INSC': 'Inspección de cierre',
    'ROT': 'Rotación',
    'INVE': 'Inversión',
    'DINS': 'Desinstalación',
    'REPA': 'Reparación',
    'BAJA': 'Desechar / baja',
}

BAJA_REASONS = {
    'GAST': 'Desgaste regular',
    'CORL': 'Corte lateral',
    'CORB': 'Corte en banda',
    'SEPA': 'Separación banda',
    'PSIB': 'Baja presión',
    'RTEQ': 'Retiro de equipo',
    'EXPL': 'Exposición de lona / alambre',
    'REEN': 'Reencauche',
    'DIB': 'Daño irregular',
    'CGH': 'Corte / golpe hombro',
    'DTB': 'Daño talón',
    'IRB': 'Irregularidad banda',
    'IBR': 'Impacto banda rodamiento',
}

REPA_REASONS = {
    'ARO': 'Aro',
    'PERF': 'Perforación',
    'CORB': 'Corte banda',
    'CORL': 'Corte lateral',
    'VALV': 'Válvula',
    'ORIN': 'O-ring',
    'OTRO': 'Otro',
}


class LoginBody(BaseModel):
    username: str
    password: str


class MovementBody(BaseModel):
    tire_id: int
    event_code: str
    event_date: str
    meter: float
    tread_outer: Optional[float] = None
    tread_inner: Optional[float] = None
    pressure: Optional[float] = None
    pressure_condition: str = 'FRIO'
    reason: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    work_start: Optional[str] = None
    work_end: Optional[str] = None
    equipment_id: Optional[int] = None
    position: Optional[str] = None


def _parse_date(value) -> Optional[dt.date]:
    if value in (None, ''):
        return None
    raw = str(value).strip()
    try:
        f = float(raw)
        if f.is_integer() and 1 <= f <= 100000:
            return dt.date(1899, 12, 30) + dt.timedelta(days=int(f))
    except Exception:
        pass
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return dt.datetime.strptime(raw[:10], fmt).date()
        except Exception:
            pass
    return None


def _to_iso_date(value) -> Optional[str]:
    d = _parse_date(value)
    return d.isoformat() if d else (str(value).strip() if value not in (None, '') else None)


def _auth_user(authorization: Optional[str] = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Sesión requerida.')
    token = authorization.split(' ', 1)[1].strip()
    user = TOKENS.get(token)
    if not user:
        raise HTTPException(status_code=401, detail='Sesión inválida o vencida.')
    return user


def _tire(tire_id: int) -> dict:
    rows = query(
        '''SELECT t.*,e.code AS equipment_code,e.location AS equipment_location
           FROM tires t
           LEFT JOIN equipment e ON e.id=t.equipment_id
           WHERE t.id=?''',
        (tire_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail='Neumático no encontrado.')
    return dict(rows[0])


def _historical_limits(tire_id: int) -> dict:
    meter_rows = query('SELECT MAX(meter) AS max_meter FROM occurrences WHERE tire_id=?', (tire_id,))
    last_tread = query(
        '''SELECT tread_inner,tread_outer
           FROM occurrences
           WHERE tire_id=? AND (tread_inner IS NOT NULL OR tread_outer IS NOT NULL)
           ORDER BY id DESC LIMIT 1''',
        (tire_id,),
    )
    return {
        'max_meter': meter_rows[0]['max_meter'] if meter_rows else None,
        'last_ti': last_tread[0]['tread_inner'] if last_tread else None,
        'last_to': last_tread[0]['tread_outer'] if last_tread else None,
    }


def _latest_event_date(tire_id: int) -> Optional[dt.date]:
    rows = query('SELECT event_date FROM occurrences WHERE tire_id=?', (tire_id,))
    dates = [_parse_date(r['event_date']) for r in rows]
    dates = [d for d in dates if d is not None]
    return max(dates) if dates else None


def _parse_clock(value: Optional[str]) -> Optional[dt.time]:
    if not value:
        return None
    for fmt in ('%H:%M', '%H:%M:%S'):
        try:
            return dt.datetime.strptime(value.strip(), fmt).time()
        except ValueError:
            pass
    raise HTTPException(status_code=400, detail='Hora inválida. Use HH:MM.')


def _duration_minutes(start: Optional[str], end: Optional[str]) -> Optional[int]:
    a = _parse_clock(start)
    b = _parse_clock(end)
    if not a or not b:
        return None
    da = dt.datetime.combine(dt.date.today(), a)
    db = dt.datetime.combine(dt.date.today(), b)
    if db < da:
        db += dt.timedelta(days=1)
    return int((db - da).total_seconds() // 60)


@app.get('/api/mobile/health')
def mobile_health():
    return {'ok': True, 'service': 'MegaSoftire Web', 'api': 'mobile-write-v0.8'}


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
           FROM equipment WHERE active=1 ORDER BY code'''
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


@app.get('/api/mobile/tires/catalog')
def mobile_tires_catalog(user=Depends(_auth_user)):
    rows = query(
        '''SELECT t.id,t.code,t.serial,t.brand,t.size,t.design,t.status,
                  t.equipment_id,t.position,t.current_meter,t.tread_inner,t.tread_outer,
                  e.code AS equipment_code
           FROM tires t
           LEFT JOIN equipment e ON e.id=t.equipment_id
           ORDER BY t.code'''
    )
    return [dict(r) for r in rows]


@app.get('/api/mobile/tires/search')
def mobile_tires_search(q: str = '', user=Depends(_auth_user)):
    text = (q or '').strip()
    if not text:
        return []
    term = f'%{text}%'
    rows = query(
        '''SELECT t.id,t.code,t.serial,t.brand,t.size,t.design,t.status,
                  t.equipment_id,t.position,t.current_meter,t.tread_inner,t.tread_outer,
                  e.code AS equipment_code
           FROM tires t
           LEFT JOIN equipment e ON e.id=t.equipment_id
           WHERE t.code LIKE ? OR COALESCE(t.serial,'') LIKE ?
           ORDER BY CASE WHEN UPPER(t.code)=UPPER(?) THEN 0 ELSE 1 END,t.code
           LIMIT 50''',
        (term, term, text),
    )
    return [dict(r) for r in rows]


@app.get('/api/mobile/tire/{tire_id}')
def mobile_tire(tire_id: int, user=Depends(_auth_user)):
    tire = _tire(tire_id)
    last = query(
        '''SELECT o.id,o.event_code,o.event_date,o.meter,o.tread_inner,o.tread_outer,
                  o.pressure,o.pressure_condition,o.reason,o.location,o.notes,
                  e.code AS equipment_code,o.position
           FROM occurrences o
           LEFT JOIN equipment e ON e.id=o.equipment_id
           WHERE o.tire_id=? ORDER BY o.id DESC LIMIT 1''',
        (tire_id,),
    )
    last_event = dict(last[0]) if last else None
    if last_event:
        last_event['event_date'] = _to_iso_date(last_event.get('event_date'))
    tire['last_event'] = last_event
    installed = tire.get('equipment_id') is not None and str(tire.get('position') or '').strip() != ''
    status_norm = str(tire.get('status') or '').strip().upper().replace('_','-')
    if installed and status_norm == 'SERVICIO':
        allowed = {'INSP','INSC','INVE','DINS','BAJA'}
    elif status_norm in ('STAND-BY','STAND BY','STANDBY'):
        allowed = {'INST','INVE','REPA','BAJA'}
    else:
        allowed = set()
    tire['event_access'] = {code: code in allowed for code in EVENT_LABELS}
    tire['reason_catalogs'] = {
        'BAJA': [{'code': k, 'label': v} for k,v in BAJA_REASONS.items()],
        'REPA': [{'code': k, 'label': v} for k,v in REPA_REASONS.items()],
    }
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
           WHERE o.tire_id=? ORDER BY o.id DESC LIMIT ?''',
        (tire_id, limit),
    )
    result = []
    for r in rows:
        item = dict(r)
        item['event_date'] = _to_iso_date(item.get('event_date'))
        result.append(item)
    return result


@app.post('/api/mobile/movements')
def mobile_save_movement(body: MovementBody, user=Depends(_auth_user)):
    code = (body.event_code or '').strip().upper()
    if code not in EVENT_LABELS:
        raise HTTPException(status_code=400, detail='Evento no permitido.')
    if code == 'ROT':
        raise HTTPException(status_code=409, detail='ROT permanece bloqueado hasta definir su funcionalidad.')

    t = _tire(body.tire_id)
    installed = t.get('equipment_id') is not None and str(t.get('position') or '').strip() != ''

    # Misma matriz operacional aprobada en Web v05.
    status_norm = str(t.get('status') or '').strip().upper().replace('_','-')
    if installed and status_norm == 'SERVICIO':
        allowed_events = {'INSP','INSC','INVE','DINS','BAJA'}
    elif status_norm in ('STAND-BY','STAND BY','STANDBY'):
        allowed_events = {'INST','INVE','REPA','BAJA'}
    else:
        allowed_events = set()
    if code not in allowed_events:
        if code == 'REPA' and installed:
            raise HTTPException(status_code=409, detail='REPA no está permitido para neumáticos instalados. Primero debe pasar a STAND-BY.')
        raise HTTPException(status_code=409, detail=f'El evento {code} no está permitido para el estado actual del neumático.')

    if code in ('REPA','BAJA'):
        reason = (body.reason or '').strip().upper()
        valid = REPA_REASONS if code == 'REPA' else BAJA_REASONS
        if not reason:
            raise HTTPException(status_code=400, detail=f'Seleccione un motivo para {code}.')
        if reason not in valid:
            raise HTTPException(status_code=400, detail=f'El motivo seleccionado no es válido para {code}.')
        body.reason = reason
    else:
        body.reason = None

    if code in ('INSP', 'INSC'):
        if t.get('status') != 'SERVICIO' or not installed:
            raise HTTPException(status_code=409, detail='Para registrar una inspección el neumático debe estar instalado y EN SERVICIO.')

    entered_date = _parse_date(body.event_date)
    if entered_date is None:
        raise HTTPException(status_code=400, detail='Fecha inválida. Use dd/mm/aaaa.')
    event_date = entered_date.isoformat()
    last_date = _latest_event_date(body.tire_id)
    if last_date is not None and entered_date < last_date:
        raise HTTPException(
            status_code=409,
            detail=f'Fecha inválida: {entered_date.strftime("%d/%m/%Y")} es anterior al último evento {last_date.strftime("%d/%m/%Y")}.',
        )

    lim = _historical_limits(body.tire_id)
    if lim['max_meter'] is not None and float(body.meter) < float(lim['max_meter']):
        raise HTTPException(
            status_code=409,
            detail=f'Horómetro inválido: {body.meter:g} es menor que la última lectura válida {float(lim["max_meter"]):g}.',
        )

    new_ti = body.tread_inner
    new_to = body.tread_outer

    if code == 'INVE':
        # Same current Web rule: meter/equipment/position stay and EXT/INT swap automatically.
        last = query(
            '''SELECT meter,tread_inner,tread_outer FROM occurrences
               WHERE tire_id=? ORDER BY id DESC LIMIT 1''',
            (body.tire_id,),
        )
        last_row = dict(last[0]) if last else None
        if last_row and last_row.get('meter') is not None:
            body.meter = float(last_row['meter'])
        prev_int = last_row.get('tread_inner') if last_row else t.get('tread_inner')
        prev_ext = last_row.get('tread_outer') if last_row else t.get('tread_outer')
        new_to = prev_int
        new_ti = prev_ext

    max_new = t.get('new_tread')
    checks = (
        (new_ti, 'interior', lim['last_ti']),
        (new_to, 'exterior', lim['last_to']),
    )
    for value, label, previous in checks:
        if value is None:
            continue
        if float(value) < 0:
            raise HTTPException(status_code=400, detail=f'La cocada {label} no puede ser negativa.')
        if max_new is not None and float(value) > float(max_new):
            raise HTTPException(status_code=409, detail=f'Cocada {label} inválida: no puede superar la profundidad nueva ({float(max_new):g} mm).')
        if code != 'INVE' and previous is not None and float(value) > float(previous):
            raise HTTPException(status_code=409, detail=f'Cocada {label} inválida: {float(value):g} mm es mayor que la última cocada válida {float(previous):g} mm.')

    # BAJA/DINS: el RTD debe conservar exactamente el último valor válido.
    # La regla general anterior bloquea aumentos; esta regla bloquea reducciones.
    if code in ('BAJA','DINS'):
        for value, label, previous in checks:
            if previous is not None and (value is None or float(value) < float(previous)):
                raise HTTPException(status_code=409, detail=f'Remanente {label} inválido: no puede ser menor que el existente ({float(previous):g} mm).')

    if code == 'INSC':
        duplicate = query(
            "SELECT id FROM occurrences WHERE tire_id=? AND event_code='INSC' AND event_date=? AND COALESCE(meter,-1)=COALESCE(?, -1)",
            (body.tire_id, event_date, body.meter),
        )
        if duplicate:
            raise HTTPException(status_code=409, detail='Ya existe una INSC con la misma fecha y lectura.')

    if code == 'INST':
        eid = body.equipment_id
        event_pos = str(body.position or '').strip()
        if eid is None or not event_pos:
            raise HTTPException(status_code=400, detail='INST requiere equipo y posición.')
        eq = query('SELECT id FROM equipment WHERE id=? AND active=1', (eid,))
        if not eq:
            raise HTTPException(status_code=404, detail='Equipo no encontrado o inactivo.')
    else:
        eid = t.get('equipment_id')
        event_pos = str(t.get('position') or '')

    condition = (body.pressure_condition or 'FRIO').strip().upper().replace('Í', 'I')
    condition = 'CALIENTE' if condition.startswith('CAL') else 'FRIO'

    duration = _duration_minutes(body.work_start, body.work_end)
    notes = (body.notes or '').strip()
    timing = []
    if body.work_start:
        timing.append(f'Inicio {body.work_start}')
    if body.work_end:
        timing.append(f'Fin {body.work_end}')
    if duration is not None:
        timing.append(f'Duración {duration} min')
    if timing:
        notes = (notes + ' | ' if notes else '') + ' · '.join(timing)

    execute(
        '''INSERT INTO occurrences(
               tire_id,event_code,event_date,equipment_id,position,meter,
               tread_inner,tread_outer,pressure,pressure_condition,reason,location,notes
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (
            body.tire_id, code, event_date, eid, event_pos, body.meter,
            new_ti, new_to, body.pressure, condition, body.reason,
            body.location, notes,
        ),
    )

    if code == 'INST':
        execute(
            "UPDATE tires SET status='SERVICIO',equipment_id=?,position=?,current_meter=?,"
            "tread_inner=COALESCE(?,tread_inner),tread_outer=COALESCE(?,tread_outer) WHERE id=?",
            (eid, event_pos, body.meter, new_ti, new_to, body.tire_id),
        )
    elif code == 'DINS':
        execute(
            "UPDATE tires SET status='STAND-BY',equipment_id=NULL,position=NULL,current_meter=? WHERE id=?",
            (body.meter, body.tire_id),
        )
    elif code == 'REPA':
        execute("UPDATE tires SET status='REPARACIÓN' WHERE id=?", (body.tire_id,))
    elif code == 'BAJA':
        execute("UPDATE tires SET status='BAJA',equipment_id=NULL,position=NULL WHERE id=?", (body.tire_id,))
    else:
        execute(
            '''UPDATE tires SET current_meter=COALESCE(?,current_meter),
               tread_inner=COALESCE(?,tread_inner),tread_outer=COALESCE(?,tread_outer)
               WHERE id=?''',
            (body.meter, new_ti, new_to, body.tire_id),
        )

    return {
        'ok': True,
        'event': code,
        'duration_minutes': duration,
        'message': f'Evento {code} registrado correctamente.',
    }


# Mount Flet last because the root app contains a SPA catch-all.
app.mount('/', flet_fastapi.app(megasoft_main.main))
