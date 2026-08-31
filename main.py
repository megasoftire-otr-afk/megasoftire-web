# MegaSoftire Web 2026 - corrección INSP + fechas dd/mm/aaaa (31/08/2026)
import datetime as dt
import os
import flet as ft
from database import init_db, query, execute, authenticate

EVENTS = {
    'INST':'Instalación','DINS':'Desinstalación','REPA':'Reparación',
    'INSP':'Inspección','INSC':'Inspección de cierre','INVE':'Inversión',
    'ROT':'Rotación','BAJA':'Desechar / baja'
}

MODULES = [
    ('Movimiento de neumáticos', ft.Icons.SWAP_HORIZ),
    ('Neumáticos en servicio', ft.Icons.DIRECTIONS_CAR),
    ('Programa de mantenimiento', ft.Icons.BUILD_CIRCLE_OUTLINED),
    ('Retén / Stand-by', ft.Icons.INVENTORY_2_OUTLINED),
    ('Fuera de servicio / baja', ft.Icons.DELETE_OUTLINE),
    ('Inventarios y consumos', ft.Icons.WAREHOUSE_OUTLINED),
    ('Administración', ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED),
    ('Tablas del neumático', ft.Icons.TABLE_CHART_OUTLINED),
    ('Reportes Excel', ft.Icons.ASSESSMENT_OUTLINED),
]

BG = '#F4F7FB'
NAV_BG = '#102A43'
NAV_ACCENT = '#1E5AA8'
CARD_BG = '#FFFFFF'
TEXT_MAIN = '#1B263B'
TEXT_MUTED = '#66788A'


def main(page: ft.Page):
    init_db()
    page.title = 'MegaSoftire Web 2026'
    page.padding = 0
    page.bgcolor = BG
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_800, use_material3=True)

    session = {'user': None}
    app_host = ft.Container(expand=True)

    def snack(msg, err=False):
        page.snack_bar = ft.SnackBar(
            ft.Text(msg),
            bgcolor=ft.Colors.RED_700 if err else ft.Colors.GREEN_700
        )
        page.snack_bar.open = True
        page.update()

    def num(v):
        try:
            return float(v) if v not in (None, '') else None
        except Exception:
            return None

    def format_date(value):
        """Muestra fechas en dd/mm/aaaa sin alterar el valor almacenado.

        Acepta seriales de Excel (p. ej. 46212), fechas ISO y fechas ya
        formateadas. Esto corrige la visualización de datos importados de NEXA.
        """
        if value in (None, ''):
            return ''
        s = str(value).strip()
        # Serial de Excel: usa origen 1899-12-30 (compatibilidad Excel/LibreOffice).
        try:
            f = float(s)
            if f.is_integer() and 1 <= f <= 100000:
                d = dt.date(1899, 12, 30) + dt.timedelta(days=int(f))
                return d.strftime('%d/%m/%Y')
        except Exception:
            pass
        # Fechas textuales comunes.
        for fmt_in in ('%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                d = dt.datetime.strptime(s[:10], fmt_in)
                return d.strftime('%d/%m/%Y')
            except Exception:
                pass
        return s

    def card(content, padding=18, width=None):
        return ft.Container(
            content=content,
            bgcolor=CARD_BG,
            border=ft.Border.all(1, '#E4EAF0'),
            border_radius=14,
            padding=padding,
            width=width,
            shadow=ft.BoxShadow(blur_radius=12, color='#12000000', offset=ft.Offset(0, 3)),
        )

    def metric_card(title, value, icon, subtitle=''):
        return card(
            ft.Column([
                ft.Row([
                    ft.Container(
                        width=40, height=40, border_radius=10,
                        bgcolor='#EAF2FF', alignment=ft.Alignment.CENTER,
                        content=ft.Icon(icon, color=NAV_ACCENT, size=21)
                    ),
                    ft.Container(expand=True),
                    ft.Text(str(value), size=28, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ]),
                ft.Text(title, size=13, weight=ft.FontWeight.W_600, color=TEXT_MAIN),
                ft.Text(subtitle, size=11, color=TEXT_MUTED),
            ], spacing=7), width=205
        )

    content = ft.Container(expand=True, padding=24)
    nav = None

    def page_title(title, subtitle=''):
        return ft.Column([
            ft.Text(title, size=27, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
            ft.Text(subtitle, size=12, color=TEXT_MUTED) if subtitle else ft.Container(height=0),
        ], spacing=2)

    def dashboard():
        def count(where='1=1', params=()):
            return query(f'SELECT COUNT(*) n FROM tires WHERE {where}', params)[0]['n']

        total = count()
        service = count("status='SERVICIO'")
        standby = count("status='STAND-BY'")
        repair = count("status='REPARACIÓN'")
        baja = count("status='BAJA'")
        equip = query('SELECT COUNT(*) n FROM equipment WHERE active=1')[0]['n']
        recent = query('''
            SELECT o.event_date,o.event_code,t.code tire_code,e.code equipment_code,o.position
            FROM occurrences o
            JOIN tires t ON t.id=o.tire_id
            LEFT JOIN equipment e ON e.id=o.equipment_id
            ORDER BY o.event_date DESC,o.id DESC LIMIT 8
        ''')

        recent_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(x)) for x in ['Fecha','Evento','Neumático','Equipo','Pos.']],
            rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(v or ''))) for v in [format_date(r['event_date']),r['event_code'],r['tire_code'],r['equipment_code'],r['position']]]) for r in recent]
        )

        content.content = ft.Column([
            page_title('Panel principal', 'Vista general de la operación de neumáticos OTR'),
            ft.Row([
                metric_card('Neumáticos', total, ft.Icons.TIRE_REPAIR, 'Maestro total'),
                metric_card('En servicio', service, ft.Icons.CHECK_CIRCLE_OUTLINE, 'Actualmente instalados'),
                metric_card('Stand-by', standby, ft.Icons.PAUSE_CIRCLE_OUTLINE, 'Disponibles / retén'),
                metric_card('En reparación', repair, ft.Icons.HANDYMAN_OUTLINED, 'Pendientes de retorno'),
                metric_card('Baja', baja, ft.Icons.CANCEL_OUTLINED, 'Fuera de servicio'),
                metric_card('Equipos activos', equip, ft.Icons.PRECISION_MANUFACTURING_OUTLINED, 'Flota registrada'),
            ], wrap=True, spacing=12, run_spacing=12),
            ft.Row([
                card(ft.Column([
                    ft.Text('Flujo operativo', size=17, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text('Registro → Instalación → Inspección → Rotación / Inversión → Desinstalación → Reparación → Reinstalación / Stand-by / Baja', size=13, color=TEXT_MUTED),
                    ft.Row([
                        ft.Chip(label=ft.Text('INST')),
                        ft.Chip(label=ft.Text('INSP')),
                        ft.Chip(label=ft.Text('INSC')),
                        ft.Chip(label=ft.Text('ROT')),
                        ft.Chip(label=ft.Text('INVE')),
                        ft.Chip(label=ft.Text('DINS')),
                        ft.Chip(label=ft.Text('REPA')),
                        ft.Chip(label=ft.Text('BAJA')),
                    ], wrap=True)
                ]), width=560),
                card(ft.Column([
                    ft.Text('Estado del sistema', size=17, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Row([ft.Icon(ft.Icons.CLOUD_DONE_OUTLINED, color=ft.Colors.GREEN_700), ft.Text('Web listo para publicación', color=TEXT_MAIN)]),
                    ft.Row([ft.Icon(ft.Icons.STORAGE, color=NAV_ACCENT), ft.Text('SQLite — demostración', color=TEXT_MAIN)]),
                    ft.Row([ft.Icon(ft.Icons.PHONE_ANDROID_OUTLINED, color=NAV_ACCENT), ft.Text('Diseño adaptable PC / móvil', color=TEXT_MAIN)]),
                ]), width=390),
            ], wrap=True, spacing=12),
            card(ft.Column([
                ft.Text('Movimientos recientes', size=17, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ft.Row([recent_table], scroll=ft.ScrollMode.AUTO)
            ])),
        ], scroll=ft.ScrollMode.AUTO, spacing=16)
        page.update()

    def equipment_view():
        code=ft.TextField(label='Código de equipo *',width=180)
        brand=ft.TextField(label='Marca',width=180)
        model=ft.TextField(label='Modelo',width=180)
        location=ft.TextField(label='Ubicación',width=200)
        kind=ft.Dropdown(label='Tipo',width=180,options=[ft.dropdown.Option(x) for x in ['Scoop','Dumper','Jumbo','Scaler','Camión','Cargador','Otro']])
        size=ft.TextField(label='Medida neumático',width=190)
        search=ft.TextField(label='Buscar equipo',prefix_icon=ft.Icons.SEARCH,width=280)
        table=ft.DataTable(columns=[ft.DataColumn(ft.Text(x)) for x in ['Código','Marca / Modelo','Tipo','Ubicación','Medida']],rows=[])

        def refresh(e=None):
            term=(search.value or '').strip()
            if term:
                rows=query("SELECT * FROM equipment WHERE code LIKE ? OR brand LIKE ? OR model LIKE ? ORDER BY code",(f'%{term}%',f'%{term}%',f'%{term}%'))
            else:
                rows=query('SELECT * FROM equipment ORDER BY code')
            table.rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(v or ''))) for v in [r['code'],f"{r['brand'] or ''} {r['model'] or ''}".strip(),r['vehicle_type'],r['location'],r['tire_size']]]) for r in rows]
            page.update()
        search.on_change=refresh

        def save(e):
            if not code.value.strip(): return snack('Ingrese el código del equipo.',True)
            try:
                execute('INSERT INTO equipment(code,brand,model,location,vehicle_type,tire_size) VALUES(?,?,?,?,?,?)',(code.value.strip(),brand.value,model.value,location.value,kind.value,size.value))
                for c in [code,brand,model,location,size]: c.value=''
                kind.value=None
                snack('Equipo registrado correctamente.')
                refresh()
            except Exception as ex: snack(str(ex),True)

        refresh()
        content.content=ft.Column([
            page_title('Administración de equipos','Registro y consulta de la flota'),
            card(ft.Column([
                ft.Text('Nuevo equipo',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                ft.Row([code,brand,model,location,kind,size],wrap=True),
                ft.ElevatedButton('Registrar equipo',icon=ft.Icons.SAVE,on_click=save)
            ])),
            card(ft.Column([
                ft.Row([ft.Text('Equipos registrados',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),ft.Container(expand=True),search]),
                ft.Row([table],scroll=ft.ScrollMode.AUTO)
            ]))
        ],scroll=ft.ScrollMode.AUTO,spacing=16)
        page.update()

    def tires_view(status_filter=None):
        code=ft.TextField(label='Código interno *',width=180)
        serial=ft.TextField(label='Serie',width=190)
        brand=ft.TextField(label='Marca',width=170)
        size=ft.TextField(label='Medida',width=170)
        design=ft.TextField(label='Diseño',width=170)
        tread=ft.TextField(label='Prof. nueva (mm)',width=160)
        pressure=ft.TextField(label='Presión recomendada',width=175)
        life=ft.TextField(label='Vida proyectada (h)',width=175)
        search=ft.TextField(label='Buscar neumático',prefix_icon=ft.Icons.SEARCH,width=260)
        eq_options=[ft.dropdown.Option('', 'Todos los equipos')]
        eq_options += [ft.dropdown.Option(str(r['id']), r['code']) for r in query('SELECT id,code FROM equipment WHERE active=1 ORDER BY code')]
        eq_filter=ft.Dropdown(label='Equipo',width=180,value='',options=eq_options)
        summary=ft.Text('',size=12,color=TEXT_MUTED)
        table=ft.DataTable(columns=[ft.DataColumn(ft.Text(x)) for x in [
            'Pos.','Código','Serie','Marca','Medida','Diseño','Estado','Equipo','Horómetro','Cocada I/E','Presión','Vida proy.'
        ]],rows=[])
        history=ft.DataTable(columns=[ft.DataColumn(ft.Text(x)) for x in [
            'Fecha','Evento','Neumático','Serie','Equipo','Pos.','Lectura','Cocada I/E','Presión','Ubicación'
        ]],rows=[])

        def fmt(v):
            if v is None: return ''
            if isinstance(v,float) and v.is_integer(): return str(int(v))
            return str(v)

        def refresh(e=None):
            sql='SELECT t.*,e.code equipment_code FROM tires t LEFT JOIN equipment e ON e.id=t.equipment_id'
            clauses=[]; params=[]
            if status_filter:
                clauses.append('t.status=?'); params.append(status_filter)
            if eq_filter.value:
                clauses.append('t.equipment_id=?'); params.append(int(eq_filter.value))
            term=(search.value or '').strip()
            if term:
                clauses.append('(t.code LIKE ? OR t.serial LIKE ? OR t.brand LIKE ? OR e.code LIKE ?)')
                params += [f'%{term}%',f'%{term}%',f'%{term}%',f'%{term}%']
            if clauses: sql += ' WHERE ' + ' AND '.join(clauses)
            sql += " ORDER BY CAST(COALESCE(NULLIF(t.position,''),'999') AS INTEGER),t.code"
            rows=query(sql,tuple(params))
            table.rows=[]
            for r in rows:
                table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(fmt(v))) for v in [
                    r['position'],r['code'],r['serial'],r['brand'],r['size'],r['design'],r['status'],r['equipment_code'],
                    r['current_meter'],f"{fmt(r['tread_inner'])}/{fmt(r['tread_outer'])}",r['recommended_pressure'],r['projected_life']
                ]]))
            summary.value=f'{len(rows)} neumático(s) mostrado(s)'

            hist_sql=("SELECT o.event_date,o.event_code,t.code tire_code,t.serial,e.code equipment_code,"
                      "o.position,o.meter,o.tread_inner,o.tread_outer,o.pressure,o.location "
                      "FROM occurrences o JOIN tires t ON t.id=o.tire_id "
                      "LEFT JOIN equipment e ON e.id=o.equipment_id")
            hp=[]; hc=[]
            if eq_filter.value:
                hc.append('o.equipment_id=?'); hp.append(int(eq_filter.value))
            if status_filter and not eq_filter.value:
                hc.append('t.status=?'); hp.append(status_filter)
            if term:
                hc.append('(t.code LIKE ? OR t.serial LIKE ? OR e.code LIKE ?)')
                hp += [f'%{term}%',f'%{term}%',f'%{term}%']
            if hc: hist_sql += ' WHERE ' + ' AND '.join(hc)
            hist_sql += ' ORDER BY o.event_date DESC,o.id DESC LIMIT 80'
            hrows=query(hist_sql,tuple(hp))
            history.rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(fmt(v))) for v in [
                r['event_date'],r['event_code'],r['tire_code'],r['serial'],r['equipment_code'],r['position'],r['meter'],
                f"{fmt(r['tread_inner'])}/{fmt(r['tread_outer'])}",r['pressure'],r['location']
            ]]) for r in hrows]
            page.update()

        search.on_change=refresh
        eq_filter.on_change=refresh

        def save(e):
            if not code.value.strip(): return snack('Ingrese código interno.',True)
            try:
                n=num(tread.value) or 0
                execute('INSERT INTO tires(code,serial,brand,size,design,new_tread,recommended_pressure,projected_life,tread_inner,tread_outer) VALUES(?,?,?,?,?,?,?,?,?,?)',(code.value.strip(),serial.value,brand.value,size.value,design.value,n,num(pressure.value) or 0,num(life.value) or 0,n,n))
                for c in [code,serial,brand,size,design,tread,pressure,life]: c.value=''
                snack('Neumático registrado correctamente.')
                refresh()
            except Exception as ex: snack(str(ex),True)

        refresh()
        title='Registro maestro de neumáticos' if not status_filter else f'Neumáticos: {status_filter}'
        subtitle='Consulta y estado actual de cada neumático'
        blocks=[page_title(title,subtitle)]
        if not status_filter:
            blocks.append(card(ft.Column([
                ft.Text('Nuevo neumático',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                ft.Row([code,serial,brand,size,design,tread,pressure,life],wrap=True),
                ft.ElevatedButton('Registrar neumático',icon=ft.Icons.SAVE,on_click=save)
            ])))
        blocks.append(card(ft.Column([
            ft.Row([ft.Text('Listado',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),ft.Container(expand=True),eq_filter,search],wrap=True),
            summary,
            ft.Row([table],scroll=ft.ScrollMode.AUTO)
        ])))
        blocks.append(card(ft.Column([
            ft.Text('Historial operativo',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
            ft.Text('Filtra por equipo para ver juntos todos los movimientos de sus neumáticos.',size=11,color=TEXT_MUTED),
            ft.Row([history],scroll=ft.ScrollMode.AUTO)
        ])))
        content.content=ft.Column(blocks,scroll=ft.ScrollMode.AUTO,spacing=16)
        page.update()


    def service_view():
        """Consulta operativa de neumáticos actualmente instalados."""
        eq_rows = query("""
            SELECT DISTINCT e.id,e.code,e.brand,e.model,e.location,e.vehicle_type,e.tire_size
            FROM equipment e
            JOIN tires t ON t.equipment_id=e.id
            WHERE e.active=1 AND t.status='SERVICIO'
            ORDER BY e.code
        """)
        default_eq = ''
        for er in eq_rows:
            if er['code'] == 'CAT 50':
                default_eq = str(er['id'])
                break
        if not default_eq and eq_rows:
            default_eq = str(eq_rows[0]['id'])

        eq_filter = ft.Dropdown(
            label='Equipo en servicio',
            width=220,
            value=default_eq if default_eq else '',
            options=[ft.dropdown.Option('', 'Todos los equipos')] +
                    [ft.dropdown.Option(str(r['id']), r['code']) for r in eq_rows]
        )
        tire_filter = ft.Dropdown(
            label='Neumático',
            width=280,
            value='',
            options=[ft.dropdown.Option('', 'Todos los neumáticos')]
        )
        search = ft.TextField(
            label='Buscar código / serie',
            prefix_icon=ft.Icons.SEARCH,
            width=260
        )
        eq_info = ft.Text('', size=12, color=TEXT_MUTED)
        summary = ft.Text('', size=12, color=TEXT_MUTED)

        metrics = ft.Row([], wrap=True, spacing=12, run_spacing=12)
        position_grid = ft.Row([], wrap=True, spacing=12, run_spacing=12)

        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(x)) for x in [
                'Pos.','Código','Serie','Marca','Medida','Diseño',
                'Horóm. actual','Horóm. instal.','Horas trab.','Cocada I/E',
                'Desgaste','Remanente','Pres. últ./ref.','Vida proy.'
            ]],
            rows=[]
        )
        history = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(x)) for x in [
                'Fecha','Evento','Neumático','Equipo','Pos.','Lectura',
                'Cocada I/E','Presión','Condición','Ubicación','Motivo'
            ]],
            rows=[]
        )

        def fmt(v, dec=0):
            if v in (None, ''):
                return ''
            try:
                f = float(v)
                if dec == 0 and f.is_integer():
                    return str(int(f))
                return f'{f:.{dec}f}'
            except Exception:
                return str(v)

        def pct(v):
            return '' if v is None else f'{v:.1f}%'

        visible_tire_ids = []

        def selected_tire_id():
            try:
                return int(tire_filter.value) if tire_filter.value else None
            except Exception:
                return None

        def effective_tire_id():
            """Devuelve la llanta seleccionada o, si el filtro deja una sola, esa llanta.

            Este respaldo evita que Flet deje INSP deshabilitado cuando el dropdown
            muestra una única llanta pero el cambio de opciones aún no propagó value.
            """
            tid = selected_tire_id()
            if tid:
                return tid
            return visible_tire_ids[0] if len(visible_tire_ids) == 1 else None

        def tire_operational_data(r):
            tid = r['id']
            eid = r['equipment_id']
            inst = query("""
                SELECT meter,event_date FROM occurrences
                WHERE tire_id=? AND event_code='INST'
                  AND (? IS NULL OR equipment_id=?)
                ORDER BY event_date DESC,id DESC LIMIT 1
            """, (tid, eid, eid))
            inst_meter = inst[0]['meter'] if inst else None
            inst_date = inst[0]['event_date'] if inst else ''
            last = query("""
                SELECT event_date,event_code,meter,tread_inner,tread_outer,pressure,
                       pressure_condition,location,reason
                FROM occurrences WHERE tire_id=?
                ORDER BY event_date DESC,id DESC LIMIT 1
            """, (tid,))
            last_row = last[0] if last else None

            current_meter = r['current_meter']
            worked = None
            if current_meter is not None and inst_meter is not None:
                worked = max(0, float(current_meter) - float(inst_meter))

            vals = [v for v in (r['tread_inner'], r['tread_outer'])
                    if isinstance(v, (int, float))]
            min_tread = min(vals) if vals else None
            new_tread = r['new_tread']
            wear = None
            rem = None
            hpmm = None
            if min_tread is not None and new_tread not in (None, 0):
                wear = max(0, float(new_tread) - float(min_tread))
                rem = max(0, min(100, float(min_tread) / float(new_tread) * 100))
                if worked is not None and wear > 0:
                    hpmm = worked / wear

            last_pressure = last_row['pressure'] if last_row and last_row['pressure'] is not None else None
            return {
                'inst_meter': inst_meter, 'inst_date': inst_date, 'worked': worked,
                'min_tread': min_tread, 'wear': wear, 'rem': rem, 'hpmm': hpmm,
                'last_pressure': last_pressure,
                'last_event': last_row['event_code'] if last_row else '',
                'last_date': last_row['event_date'] if last_row else '',
            }

        def goto_movement(event_code=None):
            tid = effective_tire_id()
            if not tid:
                return snack('Seleccione un neumático para continuar.', True)
            session['movement_tire_id'] = str(tid)
            session['movement_event'] = event_code
            nav.selected_index = 1
            select(1)

        def inspect(e):
            goto_movement('INSP')

        def movement(e):
            goto_movement(None)

        inspect_btn = ft.ElevatedButton(
            'Registrar INSP',
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            on_click=inspect,
            disabled=True
        )
        movement_btn = ft.OutlinedButton(
            'Abrir movimientos',
            icon=ft.Icons.SWAP_HORIZ,
            on_click=movement,
            disabled=True
        )

        def refresh_tire_options(rows):
            current = tire_filter.value
            opts = [ft.dropdown.Option('', 'Todos los neumáticos')]
            for r in rows:
                opts.append(ft.dropdown.Option(str(r['id']), f"{r['code']} | P{r['position'] or '-'} | {r['serial'] or 's/serie'}"))
            tire_filter.options = opts
            valid = set([''] + [str(r['id']) for r in rows])
            if current not in valid:
                tire_filter.value = ''

        def refresh(e=None):
            sql = """
                SELECT t.*,e.code equipment_code,e.brand equipment_brand,e.model equipment_model,
                       e.location equipment_location,e.vehicle_type,e.tire_size equipment_tire_size
                FROM tires t
                LEFT JOIN equipment e ON e.id=t.equipment_id
                WHERE t.status='SERVICIO'
            """
            params = []
            if eq_filter.value:
                sql += ' AND t.equipment_id=?'
                params.append(int(eq_filter.value))
            term = (search.value or '').strip()
            if term:
                sql += ' AND (t.code LIKE ? OR t.serial LIKE ? OR t.brand LIKE ? OR t.design LIKE ?)'
                params += [f'%{term}%'] * 4
            sql += " ORDER BY CAST(COALESCE(NULLIF(t.position,''),'999') AS INTEGER),t.code"
            base_rows = query(sql, tuple(params))
            visible_tire_ids.clear()
            visible_tire_ids.extend([int(r['id']) for r in base_rows])

            # Al cambiar de equipo se reconstruye el selector de neumáticos.
            if e is not None and getattr(e, 'control', None) is eq_filter:
                tire_filter.value = ''
            refresh_tire_options(base_rows)

            tid = effective_tire_id()
            rows = [r for r in base_rows if tid is None or r['id'] == tid]

            # Habilita acciones cuando existe una llanta concreta seleccionada/visible.
            can_open = tid is not None and any(int(r['id']) == int(tid) for r in base_rows)
            inspect_btn.disabled = not can_open
            movement_btn.disabled = not can_open

            ops = [(r, tire_operational_data(r)) for r in rows]
            table.rows = []
            rem_values = []
            worked_values = []

            for r, od in ops:
                if od['rem'] is not None:
                    rem_values.append(od['rem'])
                if od['worked'] is not None:
                    worked_values.append(od['worked'])
                ptxt = f"{fmt(od['last_pressure'])}/{fmt(r['recommended_pressure'])}"
                table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(fmt(r['position']))),
                    ft.DataCell(ft.Text(fmt(r['code']), weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(fmt(r['serial']))),
                    ft.DataCell(ft.Text(fmt(r['brand']))),
                    ft.DataCell(ft.Text(fmt(r['size']))),
                    ft.DataCell(ft.Text(fmt(r['design']))),
                    ft.DataCell(ft.Text(fmt(r['current_meter']))),
                    ft.DataCell(ft.Text(fmt(od['inst_meter']))),
                    ft.DataCell(ft.Text(fmt(od['worked']))),
                    ft.DataCell(ft.Text(f"{fmt(r['tread_inner'])}/{fmt(r['tread_outer'])}")),
                    ft.DataCell(ft.Text(fmt(od['wear'], 1) + (' mm' if od['wear'] is not None else ''))),
                    ft.DataCell(ft.Text(pct(od['rem']))),
                    ft.DataCell(ft.Text(ptxt)),
                    ft.DataCell(ft.Text(fmt(r['projected_life']))),
                ]))

            total_service = len(base_rows)
            eq_count = query("SELECT COUNT(DISTINCT equipment_id) n FROM tires WHERE status='SERVICIO' AND equipment_id IS NOT NULL")[0]['n']
            avg_rem = sum(rem_values) / len(rem_values) if rem_values else None
            current_meter = max([float(r['current_meter']) for r in rows if r['current_meter'] is not None], default=None)
            latest_date = ''
            if rows:
                ids = tuple(r['id'] for r in rows)
                qmarks = ','.join('?' for _ in ids)
                rr = query('SELECT MAX(event_date) d FROM occurrences WHERE tire_id IN (' + qmarks + ')', ids)
                latest_date = rr[0]['d'] if rr else ''

            metrics.controls = [
                metric_card('En servicio', total_service, ft.Icons.TIRE_REPAIR, 'Neumáticos del filtro actual'),
                metric_card('Equipos con neumáticos', eq_count, ft.Icons.PRECISION_MANUFACTURING_OUTLINED, 'Flota actualmente instalada'),
                metric_card('Remanente promedio', pct(avg_rem) if avg_rem is not None else '—', ft.Icons.ASSESSMENT_OUTLINED, 'Sobre profundidad nueva'),
                metric_card('Lectura actual', fmt(current_meter) if current_meter is not None else '—', ft.Icons.DIRECTIONS_CAR, 'Horómetro / km del equipo'),
                metric_card('Último evento', format_date(latest_date) or '—', ft.Icons.SWAP_HORIZ, 'Fecha más reciente'),
            ]

            # Información del equipo seleccionado.
            if eq_filter.value:
                er = query('SELECT * FROM equipment WHERE id=?', (int(eq_filter.value),))
                if er:
                    q = er[0]
                    eq_info.value = (
                        f"{q['code']} · {(q['brand'] or '').strip()} {(q['model'] or '').strip()} · "
                        f"{q['vehicle_type'] or ''} · Ubicación: {q['location'] or ''} · "
                        f"Medida: {q['tire_size'] or ''}"
                    )
                else:
                    eq_info.value = ''
            else:
                eq_info.value = 'Vista consolidada de todos los equipos con neumáticos en servicio.'

            # Tarjetas de posiciones del equipo.
            position_grid.controls = []
            for r, od in ops:
                position_grid.controls.append(
                    card(ft.Column([
                        ft.Row([
                            ft.Container(
                                width=42, height=42, border_radius=21,
                                bgcolor='#EAF2FF',
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(f"P{r['position'] or '-'}", weight=ft.FontWeight.BOLD, color=NAV_ACCENT)
                            ),
                            ft.Column([
                                ft.Text(r['code'], size=18, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                                ft.Text(r['serial'] or 'Sin serie', size=11, color=TEXT_MUTED),
                            ], spacing=1),
                        ]),
                        ft.Text(f"{r['brand'] or ''} · {r['size'] or ''} · {r['design'] or ''}", size=11, color=TEXT_MUTED),
                        ft.Row([
                            ft.Column([ft.Text('Cocada', size=10, color=TEXT_MUTED), ft.Text(f"{fmt(r['tread_inner'])}/{fmt(r['tread_outer'])} mm", weight=ft.FontWeight.BOLD)]),
                            ft.Column([ft.Text('Remanente', size=10, color=TEXT_MUTED), ft.Text(pct(od['rem']) or '—', weight=ft.FontWeight.BOLD)]),
                            ft.Column([ft.Text('Horas trab.', size=10, color=TEXT_MUTED), ft.Text(fmt(od['worked']) or '—', weight=ft.FontWeight.BOLD)]),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(f"Último evento: {od['last_event'] or '—'} · {format_date(od['last_date']) or '—'}", size=10, color=TEXT_MUTED),
                    ], spacing=9), width=300)
                )

            # Historial del equipo / neumático.
            hsql = """
                SELECT o.event_date,o.event_code,t.code tire_code,e.code equipment_code,
                       o.position,o.meter,o.tread_inner,o.tread_outer,o.pressure,
                       o.pressure_condition,o.location,o.reason
                FROM occurrences o
                JOIN tires t ON t.id=o.tire_id
                LEFT JOIN equipment e ON e.id=o.equipment_id
                WHERE 1=1
            """
            hp = []
            if eq_filter.value:
                hsql += ' AND o.equipment_id=?'
                hp.append(int(eq_filter.value))
            if tid:
                hsql += ' AND o.tire_id=?'
                hp.append(tid)
            if term:
                hsql += ' AND (t.code LIKE ? OR t.serial LIKE ?)'
                hp += [f'%{term}%', f'%{term}%']
            hsql += ' ORDER BY o.event_date DESC,o.id DESC LIMIT 120'
            hrows = query(hsql, tuple(hp))
            history.rows = [
                ft.DataRow(cells=[ft.DataCell(ft.Text(fmt(v))) for v in [
                    format_date(r['event_date']), r['event_code'], r['tire_code'], r['equipment_code'],
                    r['position'], r['meter'],
                    f"{fmt(r['tread_inner'])}/{fmt(r['tread_outer'])}",
                    r['pressure'], r['pressure_condition'], r['location'], r['reason']
                ]]) for r in hrows
            ]

            summary.value = (
                f"{len(rows)} neumático(s) mostrado(s) · "
                f"Historial: {len(hrows)} movimiento(s)"
            )
            page.update()

        eq_filter.on_change = refresh
        tire_filter.on_change = refresh
        search.on_change = refresh

        refresh()

        content.content = ft.Column([
            page_title(
                'Neumáticos en servicio',
                'Estado actual, posiciones, horas de trabajo e historial operativo por equipo'
            ),
            card(ft.Column([
                ft.Text('Consulta operativa', size=17, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ft.Row([eq_filter, tire_filter, search], wrap=True, spacing=12, run_spacing=12),
                eq_info,
                ft.Row([inspect_btn, movement_btn], wrap=True, spacing=10),
            ])),
            metrics,
            card(ft.Column([
                ft.Text('Vista de posiciones', size=17, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ft.Text('Cada tarjeta representa la condición actual del neumático instalado en su posición.', size=11, color=TEXT_MUTED),
                position_grid
            ])),
            card(ft.Column([
                ft.Row([
                    ft.Text('Detalle técnico de neumáticos instalados', size=17, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Container(expand=True),
                    summary
                ]),
                ft.Text(
                    'Horas trabajadas = lectura actual − horómetro de la última instalación. '
                    'Remanente = menor cocada actual / profundidad nueva.',
                    size=10, color=TEXT_MUTED
                ),
                ft.Row([table], scroll=ft.ScrollMode.AUTO)
            ])),
            card(ft.Column([
                ft.Text('Historial operativo', size=17, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ft.Text('Muestra INST, INSP, INSC, ROT, INVE, DINS, REPA y BAJA según los filtros seleccionados.', size=11, color=TEXT_MUTED),
                ft.Row([history], scroll=ft.ScrollMode.AUTO)
            ]))
        ], scroll=ft.ScrollMode.AUTO, spacing=16)
        page.update()

    def movement_view():
        tire=ft.Dropdown(label='Neumático *',width=310,options=[ft.dropdown.Option(str(r['id']),f"{r['code']} | {r['serial'] or 's/serie'}") for r in query('SELECT id,code,serial FROM tires ORDER BY code')])
        event=ft.Dropdown(label='Evento *',width=265,options=[ft.dropdown.Option(k,f'{k} - {v}') for k,v in EVENTS.items()])
        date=ft.TextField(label='Fecha',value=dt.date.today().strftime('%d/%m/%Y'),width=165)
        equip=ft.Dropdown(label='Equipo',width=220,options=[ft.dropdown.Option(str(r['id']),r['code']) for r in query('SELECT id,code FROM equipment WHERE active=1 ORDER BY code')])
        pos=ft.TextField(label='Posición',width=120)
        meter=ft.TextField(label='Horómetro / km',width=165)
        ti=ft.TextField(label='Cocada int.',width=130)
        to=ft.TextField(label='Cocada ext.',width=130)
        press=ft.TextField(label='Presión',width=120)
        cond=ft.Dropdown(label='Condición',width=150,options=[ft.dropdown.Option('FRÍO'),ft.dropdown.Option('CALIENTE')])
        reason=ft.TextField(label='Motivo',width=280)
        loc=ft.TextField(label='Ubicación',width=220)
        notes=ft.TextField(label='Observaciones',multiline=True,min_lines=2,max_lines=3)
        ref=ft.Text('',size=11,color=TEXT_MUTED)
        pre_tire = session.pop('movement_tire_id', None)
        pre_event = session.pop('movement_event', None)
        if pre_tire:
            tire.value = pre_tire
        if pre_event:
            event.value = pre_event
        hist=ft.DataTable(columns=[ft.DataColumn(ft.Text(x)) for x in ['Fecha','Evento','Equipo','Pos.','Lectura','Cocada I/E','Presión']],rows=[])

        def fmt(v):
            if v is None:
                return ''
            if isinstance(v,float) and v.is_integer():
                return str(int(v))
            return str(v)

        def current_tire():
            if not tire.value:
                return None
            rows=query(
                'SELECT t.*,e.code equipment_code,e.location equipment_location '
                'FROM tires t LEFT JOIN equipment e ON e.id=t.equipment_id WHERE t.id=?',
                (int(tire.value),)
            )
            return rows[0] if rows else None

        def load_current_state(e=None):
            r=current_tire()
            if not r:
                equip.value=None
                pos.value=''
                meter.value=''
                ti.value=''
                to.value=''
                press.value=''
                loc.value=''
                ref.value=''
                return
            equip.value=str(r['equipment_id']) if r['equipment_id'] is not None else None
            pos.value=fmt(r['position'])
            meter.value=fmt(r['current_meter'])
            ti.value=fmt(r['tread_inner'])
            to.value=fmt(r['tread_outer'])
            press.value=fmt(r['recommended_pressure'])
            loc.value=fmt(r['equipment_location'])
            ref.value=(
                f"Estado actual: {r['status']} · Equipo: {r['equipment_code'] or '-'} · "
                f"Pos.: {r['position'] or '-'} · Última lectura: {fmt(r['current_meter']) or '-'} · "
                f"Cocada I/E: {fmt(r['tread_inner']) or '-'}/{fmt(r['tread_outer']) or '-'}"
            )

        def apply_event_rules(e=None):
            ec=event.value
            r=current_tire()
            locked=ec in ('INSP','INSC')
            equip.disabled=locked
            pos.disabled=locked
            if locked and r:
                equip.value=str(r['equipment_id']) if r['equipment_id'] is not None else None
                pos.value=fmt(r['position'])
                if r['status'] != 'SERVICIO':
                    ref.value=(ref.value + ' · ADVERTENCIA: el neumático no figura EN SERVICIO').strip(' ·')
            page.update()

        def refresh(e=None):
            if not tire.value:
                hist.rows=[]
                load_current_state()
            else:
                rows=query('SELECT o.*,e.code equipment_code FROM occurrences o LEFT JOIN equipment e ON e.id=o.equipment_id WHERE o.tire_id=? ORDER BY o.event_date DESC,o.id DESC',(int(tire.value),))
                hist.rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(v or ''))) for v in [format_date(r['event_date']),r['event_code'],r['equipment_code'],r['position'],r['meter'],f"{r['tread_inner'] or ''}/{r['tread_outer'] or ''}",r['pressure']]]) for r in rows]
                load_current_state()
                apply_event_rules()
            page.update()

        tire.on_change=refresh
        event.on_change=apply_event_rules

        def save(e):
            if not tire.value or not event.value:
                return snack('Seleccione neumático y evento.',True)
            tid=int(tire.value); ec=event.value
            r=current_tire()
            raw_date = (date.value or '').strip()
            event_date = raw_date
            for _fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%Y-%m-%d'):
                try:
                    event_date = dt.datetime.strptime(raw_date[:10], _fmt).strftime('%Y-%m-%d')
                    break
                except Exception:
                    pass
            if ec in ('INSP','INSC'):
                if not r or r['status'] != 'SERVICIO' or r['equipment_id'] is None or not r['position']:
                    return snack('Para registrar una inspección el neumático debe estar instalado y EN SERVICIO.',True)
                eid=int(r['equipment_id'])
                event_pos=str(r['position'])
                equip.value=str(eid)
                pos.value=event_pos
            else:
                eid=int(equip.value) if equip.value else None
                event_pos=pos.value
            if ec=='INSC' and query("SELECT id FROM occurrences WHERE tire_id=? AND event_code='INSC' AND event_date=? AND COALESCE(meter,-1)=COALESCE(?, -1)",(tid,event_date,num(meter.value))):
                return snack('Ya existe una INSC con la misma fecha y lectura.',True)
            execute('INSERT INTO occurrences(tire_id,event_code,event_date,equipment_id,position,meter,tread_inner,tread_outer,pressure,pressure_condition,reason,location,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(tid,ec,event_date,eid,event_pos,num(meter.value),num(ti.value),num(to.value),num(press.value),cond.value,reason.value,loc.value,notes.value))
            if ec=='INST':
                execute("UPDATE tires SET status='SERVICIO',equipment_id=?,position=?,current_meter=?,tread_inner=COALESCE(?,tread_inner),tread_outer=COALESCE(?,tread_outer) WHERE id=?",(eid,event_pos,num(meter.value),num(ti.value),num(to.value),tid))
            elif ec=='DINS':
                execute("UPDATE tires SET status='STAND-BY',equipment_id=NULL,position=NULL,current_meter=? WHERE id=?",(num(meter.value),tid))
            elif ec=='REPA':
                execute("UPDATE tires SET status='REPARACIÓN' WHERE id=?",(tid,))
            elif ec=='BAJA':
                execute("UPDATE tires SET status='BAJA',equipment_id=NULL,position=NULL WHERE id=?",(tid,))
            else:
                execute('UPDATE tires SET current_meter=COALESCE(?,current_meter),tread_inner=COALESCE(?,tread_inner),tread_outer=COALESCE(?,tread_outer) WHERE id=?',(num(meter.value),num(ti.value),num(to.value),tid))
            snack(f'Evento {ec} registrado correctamente.')
            refresh()

        if pre_tire:
            refresh()

        content.content=ft.Column([
            page_title('Movimiento de neumáticos','Registro operativo del ciclo de vida'),
            card(ft.Column([
                ft.Text('Datos del movimiento',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                ft.Row([tire,event,date],wrap=True),
                ref,
                ft.Row([equip,pos,meter],wrap=True),
                ft.Row([ti,to,press,cond],wrap=True),
                ft.Row([reason,loc],wrap=True),
                notes,
                ft.Row([ft.ElevatedButton('Guardar movimiento',icon=ft.Icons.SAVE,on_click=save),ft.Text('INSP/INSC conservan equipo y posición actuales. INSC evita duplicados por fecha + lectura.',size=11,color=TEXT_MUTED)])
            ])),
            card(ft.Column([
                ft.Text('Historial del neumático',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                ft.Row([hist],scroll=ft.ScrollMode.AUTO)
            ]))
        ],scroll=ft.ScrollMode.AUTO,spacing=16)
        page.update()

    def maintenance_view():
        rows=query("SELECT t.code,t.serial,t.status,t.tread_inner,t.tread_outer,t.recommended_pressure,e.code equipment_code,t.position FROM tires t LEFT JOIN equipment e ON e.id=t.equipment_id WHERE t.status='SERVICIO' ORDER BY t.code")
        table=ft.DataTable(columns=[ft.DataColumn(ft.Text(x)) for x in ['Neumático','Serie','Equipo','Pos.','Cocada I/E','Pres. ref.','Prioridad']],rows=[])
        for r in rows:
            vals=[v for v in [r['tread_inner'],r['tread_outer']] if isinstance(v,(int,float))]
            min_t=min(vals) if vals else None
            priority='ALTA' if min_t is not None and min_t <= 20 else ('MEDIA' if min_t is not None and min_t <= 35 else 'NORMAL')
            table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(v or ''))) for v in [r['code'],r['serial'],r['equipment_code'],r['position'],f"{r['tread_inner'] or ''}/{r['tread_outer'] or ''}",r['recommended_pressure'],priority]]))
        content.content=ft.Column([
            page_title('Programa de mantenimiento','Priorización básica según condición actual'),
            card(ft.Column([
                ft.Text('Criterio inicial de demostración',size=16,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                ft.Text('ALTA ≤ 20 mm · MEDIA ≤ 35 mm · NORMAL > 35 mm. Estos límites podrán configurarse por medida/diseño.',color=TEXT_MUTED),
            ])),
            card(ft.Row([table],scroll=ft.ScrollMode.AUTO))
        ],scroll=ft.ScrollMode.AUTO,spacing=16)
        page.update()

    def reports_view():
        reports=[
            ('Neumáticos de baja anual','Bajas por periodo y motivo'),
            ('Remanente, rendimiento y proyección','Profundidad, horas y vida estimada'),
            ('Nivelación de ejes','Comparación de neumáticos por posición'),
            ('Reporte general','Estado consolidado de la flota'),
            ('Costo acumulado','Reparaciones / reencauche / operación'),
            ('Resumen por equipo','Situación de neumáticos por unidad'),
            ('Costo actual operativas / repuestos','Valorización de inventario'),
            ('Proyección de cambios','Próximos cambios estimados'),
        ]
        tiles=[]
        for title,desc in reports:
            tiles.append(card(ft.Row([
                ft.Icon(ft.Icons.DESCRIPTION_OUTLINED,color=NAV_ACCENT),
                ft.Column([ft.Text(title,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),ft.Text(desc,size=11,color=TEXT_MUTED)],expand=True),
                ft.OutlinedButton('Preparar',icon=ft.Icons.DOWNLOAD_OUTLINED,disabled=True)
            ]),width=520))
        content.content=ft.Column([
            page_title('Reportes','Catálogo de reportes del MegaSoft original'),
            ft.Container(padding=12,bgcolor='#FFF7E6',border_radius=10,content=ft.Text('En esta v2 la estructura está preparada; la exportación Excel se implementará en la siguiente etapa.',color='#7A4F01')),
            ft.Row(tiles,wrap=True,spacing=12,run_spacing=12)
        ],scroll=ft.ScrollMode.AUTO,spacing=16)
        page.update()

    def placeholder(title,desc):
        content.content=ft.Column([
            page_title(title,desc),
            card(ft.Column([
                ft.Icon(ft.Icons.CONSTRUCTION_OUTLINED,size=42,color=NAV_ACCENT),
                ft.Text('Módulo preparado para la siguiente etapa.',size=16,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                ft.Text('La navegación y estructura ya están integradas en la versión Web.',color=TEXT_MUTED)
            ],horizontal_alignment=ft.CrossAxisAlignment.CENTER),width=520)
        ],scroll=ft.ScrollMode.AUTO)
        page.update()

    def select(idx):
        if idx==0: dashboard()
        elif idx==1: movement_view()
        elif idx==2: service_view()
        elif idx==3: maintenance_view()
        elif idx==4: tires_view('STAND-BY')
        elif idx==5: tires_view('BAJA')
        elif idx==6: placeholder('Inventarios y consumos','Existencias, costos, consumos y remanentes')
        elif idx==7: equipment_view()
        elif idx==8: tires_view()
        elif idx==9: reports_view()

    def build_shell():
        nonlocal nav
        user=session['user']
        nav=ft.NavigationRail(
            selected_index=0,
            extended=True,
            min_extended_width=290,
            bgcolor=NAV_BG,
            indicator_color='#234A73',
            leading=ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.TIRE_REPAIR,color=ft.Colors.WHITE,size=28),ft.Text('MegaSoftire',size=22,weight=ft.FontWeight.BOLD,color=ft.Colors.WHITE)]),
                    ft.Text('PTS S.A. | Web 2026',size=11,color='#B9C9D9')
                ],spacing=4)
            ),
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icon(ft.Icons.DASHBOARD_OUTLINED,color='#D7E3EF'),selected_icon=ft.Icon(ft.Icons.DASHBOARD,color=ft.Colors.WHITE),label=ft.Text('Panel principal',color=ft.Colors.WHITE))
            ] + [
                ft.NavigationRailDestination(icon=ft.Icon(icon,color='#D7E3EF'),selected_icon=ft.Icon(icon,color=ft.Colors.WHITE),label=ft.Text(f'{i+1}. {name}',color=ft.Colors.WHITE))
                for i,(name,icon) in enumerate(MODULES)
            ]
        )
        nav.on_change=lambda e: select(e.control.selected_index)

        userbar=ft.Container(
            height=62,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border(bottom=ft.BorderSide(1,'#E4EAF0')),
            padding=ft.Padding.symmetric(horizontal=20),
            content=ft.Row([
                ft.Text('Gestión integral de neumáticos OTR',size=13,color=TEXT_MUTED),
                ft.Container(expand=True),
                ft.Icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED,color=NAV_ACCENT),
                ft.Column([ft.Text(user['full_name'] or user['username'],size=12,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),ft.Text(user['role'],size=10,color=TEXT_MUTED)],spacing=0),
                ft.TextButton('Salir',icon=ft.Icons.LOGOUT,on_click=lambda e: logout())
            ])
        )
        shell=ft.Row([
            nav,
            ft.VerticalDivider(width=1,color='#D7E0E8'),
            ft.Column([userbar,content],expand=True,spacing=0)
        ],expand=True,spacing=0)
        app_host.content=shell
        dashboard()
        adapt()

    def logout():
        session['user']=None
        show_login()

    def show_login():
        username=ft.TextField(label='Usuario',prefix_icon=ft.Icons.PERSON_OUTLINE,width=340,autofocus=True)
        password=ft.TextField(label='Contraseña',prefix_icon=ft.Icons.LOCK_OUTLINE,password=True,can_reveal_password=True,width=340)
        error=ft.Text('',color=ft.Colors.RED_700,size=12)

        def do_login(e):
            user=authenticate(username.value or '',password.value or '')
            if not user:
                error.value='Usuario o contraseña incorrectos.'
                page.update(); return
            session['user']=user
            build_shell()
            page.update()

        password.on_submit=do_login
        login_card=ft.Container(
            width=430,
            padding=34,
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(blur_radius=24,color='#26000000',offset=ft.Offset(0,7)),
            content=ft.Column([
                ft.Container(width=64,height=64,border_radius=16,bgcolor='#EAF2FF',alignment=ft.Alignment.CENTER,content=ft.Icon(ft.Icons.TIRE_REPAIR,size=34,color=NAV_ACCENT)),
                ft.Text('MegaSoftire',size=30,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                ft.Text('Gestión de Neumáticos OTR · Versión Web',size=13,color=TEXT_MUTED),
                ft.Divider(height=20,color='#E8EDF3'),
                username,password,error,
                ft.ElevatedButton('INGRESAR',icon=ft.Icons.LOGIN,width=340,height=46,on_click=do_login),
                ft.Container(height=6),
                ft.Text('Acceso inicial de demostración',size=11,color=TEXT_MUTED),
                ft.Text('Usuario: admin   ·   Contraseña: Admin2026!',size=11,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
            ],horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=12)
        )
        app_host.content=ft.Container(
            expand=True,
            bgcolor=BG,
            alignment=ft.Alignment.CENTER,
            content=ft.Row([
                ft.Container(
                    expand=True,
                    padding=50,
                    content=ft.Column([
                        ft.Text('MEGASOFTire WEB 2026',size=38,weight=ft.FontWeight.BOLD,color=NAV_BG),
                        ft.Text('La evolución del control de neumáticos: misma lógica operativa, interfaz moderna y acceso desde navegador.',size=17,color=TEXT_MUTED,width=620),
                        ft.Container(height=12),
                        ft.Row([ft.Icon(ft.Icons.COMPUTER,color=NAV_ACCENT),ft.Text('Windows / navegador',color=TEXT_MAIN)]),
                        ft.Row([ft.Icon(ft.Icons.PHONE_ANDROID,color=NAV_ACCENT),ft.Text('Compatible con móvil',color=TEXT_MAIN)]),
                        ft.Row([ft.Icon(ft.Icons.HISTORY,color=NAV_ACCENT),ft.Text('Historial completo por neumático',color=TEXT_MAIN)]),
                        ft.Row([ft.Icon(ft.Icons.SECURITY,color=NAV_ACCENT),ft.Text('Acceso por usuario',color=TEXT_MAIN)]),
                    ],alignment=ft.MainAxisAlignment.CENTER,spacing=14)
                ),
                ft.Container(width=500,alignment=ft.Alignment.CENTER,content=login_card)
            ],expand=True,vertical_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    def adapt(e=None):
        if not nav: return
        w=page.width or 1280
        nav.extended = w >= 1120
        content.padding = 14 if w < 800 else 24
        page.update()

    page.on_resized=adapt
    page.add(app_host)
    show_login()


if __name__=='__main__':
    if os.environ.get('PORT'):
        os.environ.setdefault('FLET_SERVER_PORT', os.environ['PORT'])
        os.environ.setdefault('FLET_SERVER_IP', '0.0.0.0')
        os.environ.setdefault('FLET_FORCE_WEB_SERVER', 'true')
    ft.run(main)
