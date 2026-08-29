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

    def card(content, padding=18, width=None):
        return ft.Container(
            content=content,
            bgcolor=CARD_BG,
            border=ft.border.all(1, '#E4EAF0'),
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
            rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(v or ''))) for v in [r['event_date'],r['event_code'],r['tire_code'],r['equipment_code'],r['position']]]) for r in recent]
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
                    ft.Row([ft.Icon(ft.Icons.DATABASE_OUTLINED, color=NAV_ACCENT), ft.Text('SQLite — demostración', color=TEXT_MAIN)]),
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
        search=ft.TextField(label='Buscar neumático',prefix_icon=ft.Icons.SEARCH,width=280)
        table=ft.DataTable(columns=[ft.DataColumn(ft.Text(x)) for x in ['Código','Serie','Marca','Medida','Diseño','Estado','Equipo','Pos.','Cocada I/E']],rows=[])

        def refresh(e=None):
            sql='SELECT t.*,e.code equipment_code FROM tires t LEFT JOIN equipment e ON e.id=t.equipment_id'
            clauses=[]; params=[]
            if status_filter:
                clauses.append('t.status=?'); params.append(status_filter)
            term=(search.value or '').strip()
            if term:
                clauses.append('(t.code LIKE ? OR t.serial LIKE ? OR t.brand LIKE ?)'); params += [f'%{term}%',f'%{term}%',f'%{term}%']
            if clauses: sql += ' WHERE ' + ' AND '.join(clauses)
            sql += ' ORDER BY t.code'
            rows=query(sql,tuple(params))
            table.rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(v or ''))) for v in [r['code'],r['serial'],r['brand'],r['size'],r['design'],r['status'],r['equipment_code'],r['position'],f"{r['tread_inner'] or ''}/{r['tread_outer'] or ''}"]]) for r in rows]
            page.update()
        search.on_change=refresh

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
        blocks=[page_title('Registro maestro de neumáticos' if not status_filter else f'Neumáticos: {status_filter}','Consulta y estado actual de cada neumático')]
        if not status_filter:
            blocks.append(card(ft.Column([
                ft.Text('Nuevo neumático',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                ft.Row([code,serial,brand,size,design,tread,pressure,life],wrap=True),
                ft.ElevatedButton('Registrar neumático',icon=ft.Icons.SAVE,on_click=save)
            ])))
        blocks.append(card(ft.Column([
            ft.Row([ft.Text('Listado',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),ft.Container(expand=True),search]),
            ft.Row([table],scroll=ft.ScrollMode.AUTO)
        ])))
        content.content=ft.Column(blocks,scroll=ft.ScrollMode.AUTO,spacing=16)
        page.update()

    def movement_view():
        tire=ft.Dropdown(label='Neumático *',width=310,options=[ft.dropdown.Option(str(r['id']),f"{r['code']} | {r['serial'] or 's/serie'}") for r in query('SELECT id,code,serial FROM tires ORDER BY code')])
        event=ft.Dropdown(label='Evento *',width=265,options=[ft.dropdown.Option(k,f'{k} - {v}') for k,v in EVENTS.items()])
        date=ft.TextField(label='Fecha',value=dt.date.today().isoformat(),width=165)
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
        hist=ft.DataTable(columns=[ft.DataColumn(ft.Text(x)) for x in ['Fecha','Evento','Equipo','Pos.','Lectura','Cocada I/E','Presión']],rows=[])

        def refresh(e=None):
            if not tire.value:
                hist.rows=[]
            else:
                rows=query('SELECT o.*,e.code equipment_code FROM occurrences o LEFT JOIN equipment e ON e.id=o.equipment_id WHERE o.tire_id=? ORDER BY o.event_date DESC,o.id DESC',(int(tire.value),))
                hist.rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(v or ''))) for v in [r['event_date'],r['event_code'],r['equipment_code'],r['position'],r['meter'],f"{r['tread_inner'] or ''}/{r['tread_outer'] or ''}",r['pressure']]]) for r in rows]
            page.update()
        tire.on_change=refresh

        def save(e):
            if not tire.value or not event.value: return snack('Seleccione neumático y evento.',True)
            tid=int(tire.value); ec=event.value; eid=int(equip.value) if equip.value else None
            if ec=='INSC' and query("SELECT id FROM occurrences WHERE tire_id=? AND event_code='INSC' AND event_date=? AND COALESCE(meter,-1)=COALESCE(?, -1)",(tid,date.value,num(meter.value))):
                return snack('Ya existe una INSC con la misma fecha y lectura.',True)
            execute('INSERT INTO occurrences(tire_id,event_code,event_date,equipment_id,position,meter,tread_inner,tread_outer,pressure,pressure_condition,reason,location,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(tid,ec,date.value,eid,pos.value,num(meter.value),num(ti.value),num(to.value),num(press.value),cond.value,reason.value,loc.value,notes.value))
            if ec=='INST':
                execute("UPDATE tires SET status='SERVICIO',equipment_id=?,position=?,current_meter=?,tread_inner=COALESCE(?,tread_inner),tread_outer=COALESCE(?,tread_outer) WHERE id=?",(eid,pos.value,num(meter.value),num(ti.value),num(to.value),tid))
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

        content.content=ft.Column([
            page_title('Movimiento de neumáticos','Registro operativo del ciclo de vida'),
            card(ft.Column([
                ft.Text('Datos del movimiento',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                ft.Row([tire,event,date],wrap=True),
                ft.Row([equip,pos,meter],wrap=True),
                ft.Row([ti,to,press,cond],wrap=True),
                ft.Row([reason,loc],wrap=True),
                notes,
                ft.Row([ft.ElevatedButton('Guardar movimiento',icon=ft.Icons.SAVE,on_click=save),ft.Text('INSC evita duplicados por fecha + lectura.',size=11,color=TEXT_MUTED)])
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
        elif idx==2: tires_view('SERVICIO')
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
            padding=ft.padding.symmetric(horizontal=20),
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
