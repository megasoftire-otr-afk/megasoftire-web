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
    ('Administración de equipos', ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED),
    ('Registro maestro de neumáticos', ft.Icons.TABLE_CHART_OUTLINED),
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
        # Administración maestra de equipos. Se conservan la tabla equipment
        # y todos sus registros existentes; solo se amplía con tipo de motor.
        existing_cols = {r['name'] for r in query("PRAGMA table_info(equipment)")}
        if 'motor_type' not in existing_cols:
            execute('ALTER TABLE equipment ADD COLUMN motor_type TEXT')

        # Catálogos dinámicos para evitar variantes de escritura y permitir
        # autocompletar/autoguardar en un solo campo.
        execute("""
            CREATE TABLE IF NOT EXISTS equipment_catalogs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                value TEXT COLLATE NOCASE NOT NULL,
                UNIQUE(category, value)
            )
        """)

        catalog_defaults = {
            'vehicle_type': ['Scoop','Dumper','Jumbo','Scaler','Camión','Cargador','Otro'],
            'motor_type': ['Diésel','Eléctrico','Híbrido','Otro'],
        }
        for category, values in catalog_defaults.items():
            for value in values:
                execute('INSERT OR IGNORE INTO equipment_catalogs(category,value) VALUES(?,?)',(category,value))

        # Incorporar al catálogo los valores que ya existen en la flota.
        historic_fields = {
            'brand': 'brand',
            'model': 'model',
            'location': 'location',
            'vehicle_type': 'vehicle_type',
            'motor_type': 'motor_type',
        }
        for category, field_name in historic_fields.items():
            for row in query(
                f"SELECT DISTINCT {field_name} value FROM equipment "
                f"WHERE {field_name} IS NOT NULL AND TRIM({field_name})<>''"
            ):
                execute('INSERT OR IGNORE INTO equipment_catalogs(category,value) VALUES(?,?)',
                        (category,str(row['value']).strip()))

        def catalog_options(category):
            return [ft.dropdown.Option(str(r['value'])) for r in query(
                'SELECT value FROM equipment_catalogs WHERE category=? ORDER BY value COLLATE NOCASE',(category,))]

        def make_catalog_field(label, category, width=190):
            return ft.Dropdown(label=label,width=width,editable=True,enable_filter=True,enable_search=True,
                               options=catalog_options(category))

        def normalize_catalog_key(value):
            return ''.join(str(value or '').strip().lower().split())

        def catalog_value(dropdown):
            typed=(getattr(dropdown,'text',None) or '').strip()
            selected=(dropdown.value or '').strip()
            raw=typed if typed else selected
            if not raw: return ''
            key=normalize_catalog_key(raw)
            for option in dropdown.options or []:
                candidate=str(getattr(option,'key',None) or getattr(option,'text',None) or '').strip()
                if candidate and normalize_catalog_key(candidate)==key:
                    return candidate
            return raw

        def save_catalog_value(category,value):
            clean=(value or '').strip()
            if not clean: return clean
            wanted=normalize_catalog_key(clean)
            for row in query('SELECT value FROM equipment_catalogs WHERE category=?',(category,)):
                existing=str(row['value']).strip()
                if normalize_catalog_key(existing)==wanted:
                    return existing
            execute('INSERT OR IGNORE INTO equipment_catalogs(category,value) VALUES(?,?)',(category,clean))
            return clean

        code=ft.TextField(label='Código de equipo *',width=190)
        brand=make_catalog_field('Marca','brand')
        model=make_catalog_field('Modelo','model')
        location=make_catalog_field('Ubicación','location')
        kind=make_catalog_field('Tipo','vehicle_type')
        motor=make_catalog_field('Tipo de motor','motor_type')
        search=ft.TextField(label='Buscar equipo',prefix_icon=ft.Icons.SEARCH,width=280)
        table=ft.DataTable(columns=[ft.DataColumn(ft.Text(x)) for x in ['Código','Marca / Modelo','Tipo','Ubicación','Tipo de motor']],rows=[])

        catalog_fields=[(brand,'brand'),(model,'model'),(location,'location'),(kind,'vehicle_type'),(motor,'motor_type')]

        def refresh_catalog_dropdowns():
            for control,category in catalog_fields:
                control.options=catalog_options(category)

        def refresh(e=None):
            term=(search.value or '').strip()
            if term:
                rows=query("SELECT * FROM equipment WHERE code LIKE ? OR brand LIKE ? OR model LIKE ? ORDER BY code",(f'%{term}%',f'%{term}%',f'%{term}%'))
            else:
                rows=query('SELECT * FROM equipment ORDER BY code')
            table.rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(v or ''))) for v in [
                r['code'],f"{r['brand'] or ''} {r['model'] or ''}".strip(),r['vehicle_type'],r['location'],r['motor_type']
            ]]) for r in rows]
            page.update()
        search.on_change=refresh

        def clear_catalog_control(control):
            control.value=None
            try: control.text=''
            except Exception: pass

        def save(e):
            if not (code.value or '').strip(): return snack('Ingrese el código del equipo.',True)
            try:
                values={category:save_catalog_value(category,catalog_value(control)) for control,category in catalog_fields}
                execute('INSERT INTO equipment(code,brand,model,location,vehicle_type,motor_type) VALUES(?,?,?,?,?,?)',(
                    code.value.strip(),values['brand'],values['model'],values['location'],values['vehicle_type'],values['motor_type']))
                code.value=''
                for control,_ in catalog_fields: clear_catalog_control(control)
                refresh_catalog_dropdowns()
                snack('Equipo registrado correctamente.')
                refresh()
            except Exception as ex: snack(str(ex),True)

        refresh()
        content.content=ft.Column([
            page_title('Administración de equipos','Registro y consulta de la flota'),
            card(ft.Column([
                ft.Text('Nuevo equipo',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                ft.Row([code,brand,model,location,kind,motor],wrap=True),
                ft.ElevatedButton('Registrar equipo',icon=ft.Icons.SAVE,on_click=save)
            ])),
            card(ft.Column([
                ft.Row([ft.Text('Equipos registrados',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),ft.Container(expand=True),search]),
                ft.Row([table],scroll=ft.ScrollMode.AUTO)
            ]))
        ],scroll=ft.ScrollMode.AUTO,spacing=16)
        page.update()

    def tires_view(status_filter=None, prefill_code=None):
        # Registro maestro de neumáticos.
        existing_cols = {r['name'] for r in query("PRAGMA table_info(tires)")}
        extra_cols = [
            ('entry_date', 'TEXT'),
            ('cost_usd', 'REAL'),
            ('compound', 'TEXT'),
            ('supplier', 'TEXT'),
            ('new_tread_outer', 'REAL'),
            ('new_tread_inner', 'REAL'),
            ('construction_type', 'TEXT'),
            ('tire_condition', 'TEXT'),
            ('retirement_tread', 'REAL'),
            ('projected_life_target', 'REAL'),
        ]
        for col_name, col_type in extra_cols:
            if col_name not in existing_cols:
                execute(f'ALTER TABLE tires ADD COLUMN {col_name} {col_type}')

        # Catálogos dinámicos del Registro Maestro.
        # Permiten seleccionar un valor existente o DIGITAR uno nuevo.
        execute("""
            CREATE TABLE IF NOT EXISTS tire_catalogs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                value TEXT COLLATE NOCASE NOT NULL,
                UNIQUE(category, value)
            )
        """)

        catalog_defaults = {
            'brand': ['GoodYear','Bridgestone','Michelin','Yokohama','Techking','Maxam'],
            'supplier': ['Soltrak','Nuema','PTS','Renova','Tire SOL','J.CH.','Pimentel'],
        }
        for category, values in catalog_defaults.items():
            for value in values:
                execute(
                    'INSERT OR IGNORE INTO tire_catalogs(category,value) VALUES(?,?)',
                    (category, value)
                )

        # Recuperar también valores ya existentes en los neumáticos históricos.
        historic_catalog_fields = {
            'brand': 'brand',
            'size': 'size',
            'design': 'design',
            'compound': 'compound',
            'supplier': 'supplier',
        }
        for category, field_name in historic_catalog_fields.items():
            for row in query(
                f"SELECT DISTINCT {field_name} value FROM tires "
                f"WHERE {field_name} IS NOT NULL AND TRIM({field_name})<>''"
            ):
                execute(
                    'INSERT OR IGNORE INTO tire_catalogs(category,value) VALUES(?,?)',
                    (category, str(row['value']).strip())
                )

        def catalog_options(category):
            return [
                ft.dropdown.Option(str(r['value']))
                for r in query(
                    'SELECT value FROM tire_catalogs WHERE category=? ORDER BY value COLLATE NOCASE',
                    (category,)
                )
            ]

        def make_catalog_field(label, category, width):
            # Un solo cuadro: permite escribir y al mismo tiempo filtra/autocompleta
            # con los valores ya guardados en el catálogo.
            return ft.Dropdown(
                label=f'{label} *',
                width=width,
                editable=True,
                enable_filter=True,
                enable_search=True,
                options=catalog_options(category)
            )

        def normalize_catalog_key(value):
            # Para detectar equivalencias como:
            # GoodYear / GOODYEAR / GOOD YEAR
            return ''.join(str(value or '').strip().lower().split())

        def catalog_value(dropdown):
            typed = (getattr(dropdown, 'text', None) or '').strip()
            selected = (dropdown.value or '').strip()
            raw = typed if typed else selected
            if not raw:
                return ''

            key = normalize_catalog_key(raw)
            for option in dropdown.options or []:
                option_key = getattr(option, 'key', None)
                option_text = getattr(option, 'text', None)
                candidate = str(option_key or option_text or '').strip()
                if candidate and normalize_catalog_key(candidate) == key:
                    return candidate
            return raw

        def save_catalog_value(category, value):
            clean = (value or '').strip()
            if not clean:
                return clean

            wanted_key = normalize_catalog_key(clean)
            for row in query(
                'SELECT value FROM tire_catalogs WHERE category=?',
                (category,)
            ):
                existing_value = str(row['value']).strip()
                if normalize_catalog_key(existing_value) == wanted_key:
                    return existing_value

            execute(
                'INSERT OR IGNORE INTO tire_catalogs(category,value) VALUES(?,?)',
                (category, clean)
            )
            return clean

        FIELD_W = 220

        code=ft.TextField(label='Código *',width=FIELD_W,value=(str(prefill_code) if prefill_code else ''))
        serial=ft.TextField(label='Serie Fab. *',width=FIELD_W)
        entry_date=ft.TextField(label='Fecha de ingreso *',value=dt.date.today().strftime('%d/%m/%Y'),width=FIELD_W)
        cost_usd=ft.TextField(label='Costo $ *',width=FIELD_W)

        brand = make_catalog_field('Marca', 'brand', FIELD_W)
        size = make_catalog_field('Medida', 'size', FIELD_W)
        design = make_catalog_field('Diseño', 'design', FIELD_W)
        compound = make_catalog_field('Compuesto', 'compound', FIELD_W)
        supplier = make_catalog_field('Proveedor', 'supplier', FIELD_W)

        pressure=ft.TextField(label='Presión recomendada *',width=FIELD_W)
        tread_outer_new=ft.TextField(label='Profundidad nueva EXT *',width=FIELD_W)
        tread_inner_new=ft.TextField(label='Profundidad nueva INT *',width=FIELD_W)
        retirement_tread=ft.TextField(label='Profundidad de retiro (mm) *',width=FIELD_W)
        projected_life_target=ft.TextField(label='Proyección de vida (h) *',width=FIELD_W)

        construction=ft.Dropdown(
            label='Tipo de construcción *', width=FIELD_W,
            options=[ft.dropdown.Option('Radial'),ft.dropdown.Option('Convencional')]
        )
        condition=ft.Dropdown(
            label='Condición *', width=FIELD_W,
            options=[ft.dropdown.Option('Nueva'),ft.dropdown.Option('Reencauchada')]
        )

        search=ft.TextField(label='Buscar neumático',prefix_icon=ft.Icons.SEARCH,width=260)
        eq_options=[ft.dropdown.Option('', 'Todos los equipos')]
        eq_options += [ft.dropdown.Option(str(r['id']), r['code']) for r in query('SELECT id,code FROM equipment WHERE active=1 ORDER BY code')]
        eq_filter=ft.Dropdown(label='Equipo',width=180,value='',options=eq_options)
        summary=ft.Text('',size=12,color=TEXT_MUTED)

        # Listado maestro: se construye con filas explícitas para que los
        # encabezados sean visibles aun cuando no haya registros y para evitar
        # el bloque gris que estaba mostrando DataTable en la vista web.
        master_columns = [
            ('Código', 90),
            ('Serie Fab.', 125),
            ('Fecha ingreso', 115),
            ('Costo $', 90),
            ('Marca', 120),
            ('Medida', 105),
            ('Diseño', 115),
            ('Compuesto', 115),
            ('Proveedor', 120),
            ('Presión rec.', 105),
            ('Prof. nueva EXT', 120),
            ('Prof. nueva INT', 120),
            ('Prof. retiro', 105),
            ('Proy. vida (h)', 115),
            ('Tipo construcción', 140),
            ('Condición', 120),
        ]

        def master_cell(value, width, header=False):
            return ft.Container(
                content=ft.Text(
                    value,
                    size=12,
                    weight=ft.FontWeight.BOLD if header else ft.FontWeight.NORMAL,
                    color=TEXT_MAIN,
                    no_wrap=True,
                ),
                width=width,
                padding=ft.Padding(left=6, top=8, right=6, bottom=8),
            )

        master_header = ft.Row(
            [master_cell(label, width, True) for label, width in master_columns],
            spacing=0,
        )
        master_rows = ft.Column(spacing=0)
        master_table = ft.Column([
            ft.Container(
                content=master_header,
                bgcolor='#EEF2F7',
                border=ft.Border(bottom=ft.BorderSide(1, '#D5DCE5')),
            ),
            master_rows,
        ], spacing=0)

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
            term=(search.value or '').strip()
            if term:
                clauses.append('(t.code LIKE ? OR t.serial LIKE ? OR t.brand LIKE ? OR e.code LIKE ?)')
                params += [f'%{term}%',f'%{term}%',f'%{term}%',f'%{term}%']
            if clauses:
                sql += ' WHERE ' + ' AND '.join(clauses)
            sql += " ORDER BY CAST(COALESCE(NULLIF(t.position,''),'999') AS INTEGER),t.code"
            rows=query(sql,tuple(params))

            master_rows.controls=[]
            for idx, r in enumerate(rows):
                values = [
                    r['code'],
                    r['serial'],
                    format_date(r['entry_date']) if r['entry_date'] else None,
                    r['cost_usd'],
                    r['brand'],
                    r['size'],
                    r['design'],
                    r['compound'],
                    r['supplier'],
                    r['recommended_pressure'],
                    r['new_tread_outer'],
                    r['new_tread_inner'],
                    r['retirement_tread'],
                    r['projected_life_target'],
                    r['construction_type'],
                    r['tire_condition'],
                ]

                display_values = [
                    '—' if v is None or str(v).strip() == '' else fmt(v)
                    for v in values
                ]

                master_rows.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                master_cell(display_values[i], master_columns[i][1])
                                for i in range(len(master_columns))
                            ],
                            spacing=0,
                        ),
                        bgcolor='#FFFFFF' if idx % 2 == 0 else '#F8FAFC',
                        border=ft.Border(bottom=ft.BorderSide(1, '#E5E9EF')),
                    )
                )

            summary.value=f'{len(rows)} neumático(s) registrado(s)'

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
            if hc:
                hist_sql += ' WHERE ' + ' AND '.join(hc)
            hist_sql += ' ORDER BY o.event_date DESC,o.id DESC LIMIT 80'
            hrows=query(hist_sql,tuple(hp))

            history.rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(fmt(v))) for v in [
                format_date(r['event_date']),r['event_code'],r['tire_code'],r['serial'],r['equipment_code'],r['position'],r['meter'],
                f"{fmt(r['tread_inner'])}/{fmt(r['tread_outer'])}",r['pressure'],r['location']
            ]]) for r in hrows]
            page.update()

        search.on_change=refresh
        eq_filter.on_change=refresh

        required_controls = [
            ('Código', code),
            ('Serie Fab.', serial),
            ('Fecha de ingreso', entry_date),
            ('Costo $', cost_usd),
            ('Presión recomendada', pressure),
            ('Profundidad nueva EXT', tread_outer_new),
            ('Profundidad nueva INT', tread_inner_new),
            ('Profundidad de retiro', retirement_tread),
            ('Proyección de vida', projected_life_target),
            ('Tipo de construcción', construction),
            ('Condición', condition),
        ]

        def normalize_date(value):
            raw=(value or '').strip()
            for date_fmt in ('%d/%m/%Y','%d-%m-%Y','%Y-%m-%d','%Y/%m/%d'):
                try:
                    return dt.datetime.strptime(raw[:10],date_fmt).strftime('%Y-%m-%d')
                except Exception:
                    pass
            return None

        def clear_form():
            for ctrl in [code,serial,cost_usd,pressure,
                         tread_outer_new,tread_inner_new,retirement_tread,projected_life_target]:
                ctrl.value=''
            entry_date.value=dt.date.today().strftime('%d/%m/%Y')

            for dropdown in [brand, size, design, compound, supplier]:
                dropdown.value=None
                try:
                    dropdown.text=''
                except Exception:
                    pass

            construction.value=None
            condition.value=None

        def save(e):
            missing=[]
            for label,ctrl in required_controls:
                value=ctrl.value
                if value is None or not str(value).strip():
                    missing.append(label)

            brand_value = catalog_value(brand)
            size_value = catalog_value(size)
            design_value = catalog_value(design)
            compound_value = catalog_value(compound)
            supplier_value = catalog_value(supplier)

            for label, value in [
                ('Marca', brand_value),
                ('Medida', size_value),
                ('Diseño', design_value),
                ('Compuesto', compound_value),
                ('Proveedor', supplier_value),
            ]:
                if not value:
                    missing.append(label)

            if missing:
                return snack('Faltan campos obligatorios: ' + ', '.join(missing), True)

            date_iso=normalize_date(entry_date.value)
            if not date_iso:
                return snack('Fecha de ingreso inválida. Use dd/mm/aaaa.', True)

            cost=num(cost_usd.value)
            rec_pressure=num(pressure.value)
            new_ext=num(tread_outer_new.value)
            new_int=num(tread_inner_new.value)
            retirement=num(retirement_tread.value)
            life_target=num(projected_life_target.value)

            if cost is None or cost < 0:
                return snack('Costo $ inválido.', True)
            if rec_pressure is None or rec_pressure <= 0:
                return snack('Presión recomendada inválida.', True)
            if new_ext is None or new_ext <= 0:
                return snack('Profundidad nueva EXT inválida.', True)
            if new_int is None or new_int <= 0:
                return snack('Profundidad nueva INT inválida.', True)
            if retirement is None or retirement < 0:
                return snack('Profundidad de retiro inválida.', True)
            if retirement >= min(float(new_ext), float(new_int)):
                return snack('La profundidad de retiro debe ser menor que la profundidad nueva.', True)
            if life_target is None or life_target <= 0:
                return snack('Proyección de vida inválida.', True)

            new_tread_ref=max(float(new_ext), float(new_int))

            # Si se digitó un valor nuevo, se incorpora al catálogo y queda
            # disponible automáticamente para los siguientes registros.
            brand_value = save_catalog_value('brand', brand_value)
            size_value = save_catalog_value('size', size_value)
            design_value = save_catalog_value('design', design_value)
            compound_value = save_catalog_value('compound', compound_value)
            supplier_value = save_catalog_value('supplier', supplier_value)

            def refresh_catalog_dropdowns():
                for category, dropdown in [
                    ('brand', brand),
                    ('size', size),
                    ('design', design),
                    ('compound', compound),
                    ('supplier', supplier),
                ]:
                    dropdown.options = catalog_options(category)

            try:
                execute(
                    """INSERT INTO tires(
                           code,serial,brand,size,design,new_tread,recommended_pressure,
                           tread_inner,tread_outer,entry_date,cost_usd,compound,supplier,
                           new_tread_outer,new_tread_inner,construction_type,tire_condition,
                           retirement_tread,projected_life_target,projected_life
                       ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        code.value.strip(),
                        serial.value.strip(),
                        brand_value,
                        size_value,
                        design_value,
                        new_tread_ref,
                        rec_pressure,
                        new_int,
                        new_ext,
                        date_iso,
                        cost,
                        compound_value,
                        supplier_value,
                        new_ext,
                        new_int,
                        construction.value,
                        condition.value,
                        retirement,
                        life_target,
                        life_target,
                    )
                )
                refresh_catalog_dropdowns()
                clear_form()
                snack('Neumático registrado correctamente.')
                refresh()
            except Exception as ex:
                snack(str(ex),True)

        refresh()
        title='Registro maestro de neumáticos' if not status_filter else f'Neumáticos: {status_filter}'
        subtitle='Consulta y estado actual de cada neumático'
        blocks=[page_title(title,subtitle)]

        if not status_filter:
            blocks.append(card(ft.Column([
                ft.Text('Nuevo neumático',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                ft.Text('Todos los campos son obligatorios.',size=11,color=TEXT_MUTED),

                ft.Row([code,serial,entry_date,cost_usd],wrap=True,spacing=10,run_spacing=10),
                ft.Row([brand,size,design,compound],wrap=True,spacing=10,run_spacing=10),
                ft.Row([supplier,pressure,tread_outer_new,tread_inner_new],wrap=True,spacing=10,run_spacing=10),
                ft.Row([retirement_tread,projected_life_target,construction,condition],wrap=True,spacing=10,run_spacing=10),

                ft.ElevatedButton('Registrar neumático',icon=ft.Icons.SAVE,on_click=save)
            ])))

        if status_filter:
            blocks.append(card(ft.Column([
                ft.Row([
                    ft.Text('Listado de neumáticos registrados',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                    ft.Container(expand=True),search
                ],wrap=True),
                summary,
                ft.Row(
                    [ft.Container(content=master_table, width=1880)],
                    scroll=ft.ScrollMode.ALWAYS
                )
            ])))

        # El historial se conserva para las vistas operativas filtradas,
        # pero no se muestra dentro del Registro maestro de neumáticos.
        if status_filter:
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
        ALL='__ALL__'
        eq_filter = ft.Dropdown(
            label='Equipo en servicio',
            width=220,
            value=ALL,
            options=[ft.dropdown.Option(key=ALL, text='Todos los equipos')] +
                    [ft.dropdown.Option(key=str(r['id']), text=r['code']) for r in eq_rows]
        )
        equipment_by_code = {str(r['code']).strip().upper(): str(r['id']) for r in eq_rows}
        equipment_ids = {str(r['id']) for r in eq_rows}
        equipment_state = {'id': ALL}
        equipment_rows_state = {'rows': None}
        mode_state = {'mode': None}  # None | 'search' | 'equipment'
        tire_filter = ft.Dropdown(
            label='Neumático',
            width=280,
            value=ALL,
            options=[ft.dropdown.Option(key=ALL, text='Todos los neumáticos')]
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
                return int(tire_filter.value) if tire_filter.value not in (None, '', ALL) else None
            except Exception:
                return None

        def effective_tire_id(allow_search_auto=True):
            """Devuelve el neumático activo según el modo de consulta.

            Modo búsqueda: solo auto-selecciona cuando el texto deja un único resultado.
            Modo equipo: solo acepta un neumático elegido manualmente.
            Sin modo activo: no habilita eventos.
            """
            mode = mode_state['mode']
            if mode == 'equipment':
                return selected_tire_id()
            if mode == 'search':
                term = (search.value or '').strip()
                if allow_search_auto and term and len(visible_tire_ids) == 1:
                    return visible_tire_ids[0]
                return None
            return None

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

        # Accesos directos a todos los eventos desde la vista de neumáticos en servicio.
        # INST permanece bloqueado porque todo neumático mostrado aquí ya está instalado.
        event_icons = {
            'INST': ft.Icons.ADD_CIRCLE_OUTLINE,
            'INSP': ft.Icons.CHECK_CIRCLE_OUTLINE,
            'INSC': ft.Icons.FACT_CHECK_OUTLINED,
            'ROT': ft.Icons.SYNC_ALT,
            'INVE': ft.Icons.SWAP_HORIZ,
            'DINS': ft.Icons.REMOVE_CIRCLE_OUTLINE,
            'REPA': ft.Icons.HANDYMAN_OUTLINED,
            'BAJA': ft.Icons.DELETE_OUTLINE,
        }
        event_buttons = {}
        for code in ['INST','INSP','INSC','ROT','INVE','DINS','REPA','BAJA']:
            event_buttons[code] = ft.OutlinedButton(
                code,
                icon=event_icons[code],
                tooltip=EVENTS.get(code, code),
                on_click=lambda e, ec=code: goto_movement(ec),
                disabled=True
            )

        event_buttons['INST'].tooltip = 'Instalación bloqueada: el neumático ya está EN SERVICIO'
        event_buttons['ROT'].tooltip = 'Rotación bloqueada: funcionalidad pendiente de definición'

        def refresh_tire_options(rows):
            current = tire_filter.value
            opts = [ft.dropdown.Option(key=ALL, text='Todos los neumáticos')]
            for r in rows:
                opts.append(ft.dropdown.Option(key=str(r['id']), text=f"{r['code']} | P{r['position'] or '-'} | {r['serial'] or 's/serie'}"))
            tire_filter.options = opts
            valid = set([ALL] + [str(r['id']) for r in rows])
            if current not in valid:
                tire_filter.value = ALL

        def refresh(e=None):
            selected_value = str(tire_filter.value or ALL)

            # El selector Neumático depende EXCLUSIVAMENTE del equipo seleccionado.
            # Si on_equipment_change ya construyó la lista, reutilizamos exactamente
            # esos registros y no volvemos a mezclarlos con el buscador.
            if equipment_rows_state['rows'] is not None:
                option_rows = list(equipment_rows_state['rows'])
            else:
                options_sql = """
                    SELECT t.*,e.code equipment_code,e.brand equipment_brand,e.model equipment_model,
                           e.location equipment_location,e.vehicle_type,e.tire_size equipment_tire_size
                    FROM tires t
                    LEFT JOIN equipment e ON e.id=t.equipment_id
                    WHERE t.status='SERVICIO'
                """
                options_params = []
                if equipment_state['id'] not in (None, '', ALL):
                    options_sql += ' AND t.equipment_id=?'
                    options_params.append(int(equipment_state['id']))
                options_sql += " ORDER BY CAST(COALESCE(NULLIF(t.position,''),'999') AS INTEGER),t.code"
                option_rows = query(options_sql, tuple(options_params))

            refresh_tire_options(option_rows)

            valid_ids = {str(r['id']) for r in option_rows}
            if selected_value not in ('', ALL) and selected_value in valid_ids:
                tire_filter.value = selected_value
                tid = int(selected_value)
            else:
                if tire_filter.value in (None, '') or str(tire_filter.value) not in valid_ids | {ALL}:
                    tire_filter.value = ALL
                tid = selected_tire_id()

            # La consulta visible sí responde a búsqueda + equipo + neumático.
            rows = list(option_rows)
            term = (search.value or '').strip()
            if term:
                term_l = term.lower()
                rows = [r for r in rows if
                        term_l in str(r['code'] or '').lower() or
                        term_l in str(r['serial'] or '').lower() or
                        term_l in str(r['brand'] or '').lower() or
                        term_l in str(r['design'] or '').lower()]
            if tid is not None:
                rows = [r for r in rows if int(r['id']) == int(tid)]

            visible_tire_ids.clear()
            visible_tire_ids.extend([int(r['id']) for r in rows])

            # Habilitar eventos solo si:
            # 1) se seleccionó manualmente un neumático, o
            # 2) Buscar código / serie dejó un único resultado.
            # Elegir únicamente un equipo NO activa eventos.
            active_tid = effective_tire_id(allow_search_auto=True)
            can_open = active_tid is not None and str(active_tid) in valid_ids
            for code, btn in event_buttons.items():
                # INST: bloqueado porque el neumático ya está en servicio.
                # ROT: bloqueado hasta definir su funcionalidad.
                btn.disabled = (not can_open) or code in ('INST', 'ROT')

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

            total_service = len(rows)
            eq_count = len({r['equipment_id'] for r in rows if r['equipment_id'] is not None})
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
                metric_card('Equipos con neumáticos', eq_count, ft.Icons.PRECISION_MANUFACTURING_OUTLINED, 'Flota del filtro actual'),
                metric_card('Remanente promedio', pct(avg_rem) if avg_rem is not None else '—', ft.Icons.ASSESSMENT_OUTLINED, 'Sobre profundidad nueva'),
                metric_card('Lectura actual', fmt(current_meter) if current_meter is not None else '—', ft.Icons.DIRECTIONS_CAR, 'Horómetro / km del equipo'),
                metric_card('Último evento', format_date(latest_date) or '—', ft.Icons.SWAP_HORIZ, 'Fecha más reciente'),
            ]

            if equipment_state['id'] not in (None, '', ALL):
                er = query('SELECT * FROM equipment WHERE id=?', (int(equipment_state['id']),))
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
            if equipment_state['id'] not in (None, '', ALL):
                hsql += ' AND o.equipment_id=?'
                hp.append(int(equipment_state['id']))
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

        def resolve_equipment_from_event(e):
            candidates = []
            ctrl = getattr(e, 'control', None)
            if ctrl is not None:
                candidates.append(getattr(ctrl, 'value', None))
            candidates.append(getattr(e, 'data', None))

            for raw in candidates:
                if raw in (None, ''):
                    continue
                val = str(raw).strip()
                if val == ALL or val.lower() == 'todos los equipos':
                    return ALL
                if val in equipment_ids:
                    return val
                eid = equipment_by_code.get(val.upper())
                if eid:
                    return eid
            return ALL

        def on_equipment_change(e):
            """Cambio de equipo totalmente independiente del buscador.

            Flujo:
            equipo -> limpiar neumático -> bloquear eventos -> consultar solo ese
            equipment_id -> reconstruir selector -> refrescar vista.
            """
            eid = resolve_equipment_from_event(e)
            equipment_state['id'] = eid
            eq_filter.value = eid

            # Nunca conservar un neumático seleccionado del equipo anterior.
            tire_filter.value = ALL
            visible_tire_ids.clear()
            for code, btn in event_buttons.items():
                btn.disabled = True

            sql = """
                SELECT t.*,e.code equipment_code,e.brand equipment_brand,e.model equipment_model,
                       e.location equipment_location,e.vehicle_type,e.tire_size equipment_tire_size
                FROM tires t
                LEFT JOIN equipment e ON e.id=t.equipment_id
                WHERE t.status='SERVICIO'
            """
            params = []
            if eid != ALL:
                sql += ' AND t.equipment_id=?'
                params.append(int(eid))
            sql += " ORDER BY CAST(COALESCE(NULLIF(t.position,''),'999') AS INTEGER),t.code"
            option_rows = query(sql, tuple(params))

            # Guardamos exactamente la lista del equipo; refresh no la recalcula
            # a partir del buscador ni de un neumático anterior.
            equipment_rows_state['rows'] = list(option_rows)
            tire_filter.options = [ft.dropdown.Option(key=ALL, text='Todos los neumáticos')] + [
                ft.dropdown.Option(
                    key=str(r['id']),
                    text=f"{r['code']} | P{r['position'] or '-'} | {r['serial'] or 's/serie'}"
                ) for r in option_rows
            ]
            tire_filter.value = ALL
            refresh()

        def set_mode(mode):
            """Activa un único camino de consulta y bloquea el otro."""
            mode_state['mode'] = mode
            if mode == 'search':
                eq_filter.disabled = True
                tire_filter.disabled = True
                equipment_state['id'] = ALL
                equipment_rows_state['rows'] = None
                eq_filter.value = ALL
                tire_filter.value = ALL
            elif mode == 'equipment':
                search.disabled = True
                search.value = ''
                tire_filter.disabled = False
            else:
                search.disabled = False
                eq_filter.disabled = False
                tire_filter.disabled = False

        def reset_query_modes():
            """ESC: vuelve al estado inicial y elimina cualquier selección activa."""
            mode_state['mode'] = None
            search.value = ''
            search.disabled = False
            eq_filter.disabled = False
            eq_filter.value = ALL
            equipment_state['id'] = ALL
            equipment_rows_state['rows'] = None
            tire_filter.disabled = False
            tire_filter.value = ALL
            visible_tire_ids.clear()
            for code, btn in event_buttons.items():
                btn.disabled = True
            refresh()

        def on_search_focus(e):
            if not search.disabled:
                set_mode('search')
                refresh()

        def on_search_change(e):
            if mode_state['mode'] != 'search':
                set_mode('search')
            refresh(e)

        def on_equipment_focus(e):
            if not eq_filter.disabled:
                set_mode('equipment')
                page.update()

        # Conservamos la lógica de filtrado por equipo, pero activando primero
        # su modo exclusivo y eliminando cualquier búsqueda previa.
        original_on_equipment_change = on_equipment_change
        def on_equipment_change_mode(e):
            set_mode('equipment')
            original_on_equipment_change(e)

        def on_tire_change(e):
            if mode_state['mode'] != 'equipment':
                return
            selected = getattr(e, 'data', None)
            if selected not in (None, ''):
                tire_filter.value = str(selected)
            elif getattr(e, 'control', None) is not None:
                tire_filter.value = str(e.control.value or ALL)
            refresh(e)

        def on_service_keyboard(e):
            key = str(getattr(e, 'key', '') or '').upper()
            if key in ('ESCAPE', 'ESC'):
                reset_query_modes()

        search.on_focus = on_search_focus
        search.on_change = on_search_change
        eq_filter.on_focus = on_equipment_focus
        eq_filter.on_change = on_equipment_change_mode
        tire_filter.on_change = on_tire_change
        page.on_keyboard_event = on_service_keyboard

        refresh()

        content.content = ft.Column([
            page_title(
                'Neumáticos en servicio',
                'Estado actual, posiciones, horas de trabajo e historial operativo por equipo'
            ),
            card(ft.Column([
                ft.Text('Consulta operativa', size=17, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ft.Row([search, eq_filter, tire_filter], wrap=True, spacing=12, run_spacing=12),
                eq_info,
                ft.Text('Registrar evento', size=12, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                ft.Row(
                    [event_buttons[c] for c in ['INST','INSP','INSC','ROT','INVE','DINS','REPA','BAJA']],
                    wrap=True, spacing=8, run_spacing=8
                ),
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
        # ROT se mantiene fuera del selector hasta definir su funcionalidad.
        event=ft.Dropdown(
            label='Evento *',
            width=265,
            options=[ft.dropdown.Option(k,f'{k} - {v}') for k,v in EVENTS.items() if k != 'ROT']
        )
        date=ft.TextField(label='Fecha',value=dt.date.today().strftime('%d/%m/%Y'),width=165)
        equip=ft.Dropdown(label='Equipo',width=220,options=[ft.dropdown.Option(str(r['id']),r['code']) for r in query('SELECT id,code FROM equipment WHERE active=1 ORDER BY code')])
        pos=ft.TextField(label='Posición',width=120)
        meter=ft.TextField(label='Horómetro / km',width=165)
        ti=ft.TextField(label='Cocada int.',width=130)
        to=ft.TextField(label='Cocada ext.',width=130)
        press=ft.TextField(label='Presión',width=120)
        cond=ft.Dropdown(
            label='Condición', width=160, value='FRIO',
            options=[ft.dropdown.Option('FRIO','FRIO'), ft.dropdown.Option('CALIENTE','CALIENTE')]
        )
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

        hist=ft.DataTable(
            columns=[ft.DataColumn(ft.Text(x)) for x in [
                'Fecha','Evento','Equipo','Pos.','Lectura','Cocada I/E','Presión','Condición','Ubicación','Acción'
            ]],
            rows=[]
        )

        def fmt(v):
            if v is None:
                return ''
            if isinstance(v,float) and v.is_integer():
                return str(int(v))
            return str(v)

        def select_all_on_focus(e):
            c=e.control
            try:
                value=str(c.value or '')
                c.selection=ft.TextSelection(base_offset=0, extent_offset=len(value))
                c.update()
            except Exception:
                pass

        for ctrl in [date,pos,meter,ti,to,press,reason,loc,notes]:
            ctrl.on_focus=select_all_on_focus

        def current_tire():
            if not tire.value:
                return None
            rows=query(
                'SELECT t.*,e.code equipment_code,e.location equipment_location '
                'FROM tires t LEFT JOIN equipment e ON e.id=t.equipment_id WHERE t.id=?',
                (int(tire.value),)
            )
            return rows[0] if rows else None

        def historical_limits(tid):
            rows=query(
                '''SELECT
                       MAX(meter) max_meter,
                       MIN(CASE WHEN tread_inner IS NOT NULL AND tread_inner>0 THEN tread_inner END) min_ti,
                       MIN(CASE WHEN tread_outer IS NOT NULL AND tread_outer>0 THEN tread_outer END) min_to
                   FROM occurrences WHERE tire_id=?''',
                (tid,)
            )
            return rows[0] if rows else None

        def parse_event_date(value):
            if value in (None, ''):
                return None
            raw=str(value).strip()
            try:
                f=float(raw)
                if f.is_integer() and 1 <= f <= 100000:
                    return dt.date(1899,12,30)+dt.timedelta(days=int(f))
            except Exception:
                pass
            for f in ('%d/%m/%Y','%d-%m-%Y','%Y/%m/%d','%Y-%m-%d'):
                try:
                    return dt.datetime.strptime(raw[:10],f).date()
                except Exception:
                    pass
            return None

        def latest_event_date(tid):
            rows=query('SELECT event_date FROM occurrences WHERE tire_id=?',(tid,))
            dates=[parse_event_date(r['event_date']) for r in rows]
            dates=[d for d in dates if d is not None]
            return max(dates) if dates else None

        def recalc_numeric_state(tid):
            lim=historical_limits(tid)
            if not lim:
                return
            execute(
                '''UPDATE tires SET
                       current_meter=COALESCE(?,current_meter),
                       tread_inner=COALESCE(?,tread_inner),
                       tread_outer=COALESCE(?,tread_outer)
                   WHERE id=?''',
                (lim['max_meter'],lim['min_ti'],lim['min_to'],tid)
            )

        def load_current_state(e=None):
            r=current_tire()
            if not r:
                equip.value=None
                pos.value=''
                meter.value=''
                ti.value=''
                to.value=''
                press.value=''
                cond.value='FRIO'
                loc.value=''
                ref.value=''
                return

            equip.value=str(r['equipment_id']) if r['equipment_id'] is not None else None
            pos.value=fmt(r['position'])

            lim=historical_limits(int(r['id']))
            meter.value=fmt(lim['max_meter'] if lim and lim['max_meter'] is not None else r['current_meter'])
            ti.value=fmt(lim['min_ti'] if lim and lim['min_ti'] is not None else r['tread_inner'])
            to.value=fmt(lim['min_to'] if lim and lim['min_to'] is not None else r['tread_outer'])

            last=query(
                '''SELECT pressure,pressure_condition,location
                   FROM occurrences
                   WHERE tire_id=?
                   ORDER BY id DESC LIMIT 1''',
                (int(r['id']),)
            )
            last_row=last[0] if last else None
            press.value=fmt(last_row['pressure']) if last_row and last_row['pressure'] is not None else fmt(r['recommended_pressure'])

            last_cond=(last_row['pressure_condition'] if last_row else None) or 'FRIO'
            last_cond=str(last_cond).strip().upper().replace('Í','I')
            cond.value='CALIENTE' if last_cond.startswith('CAL') else 'FRIO'

            loc.value=fmt(last_row['location']) if last_row and last_row['location'] else fmt(r['equipment_location'])
            ref.value=(
                f"Estado actual: {r['status']} · Equipo: {r['equipment_code'] or '-'} · "
                f"Pos.: {r['position'] or '-'} · Última lectura válida: {meter.value or '-'} · "
                f"Cocada I/E válida: {ti.value or '-'}/{to.value or '-'}"
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

        def ask_delete(occ_id):
            if not tire.value:
                return
            tid=int(tire.value)

            def close_dialog(e=None):
                dlg.open=False
                page.update()

            def do_delete(e=None):
                execute('DELETE FROM occurrences WHERE id=? AND tire_id=?',(occ_id,tid))
                recalc_numeric_state(tid)
                dlg.open=False
                snack('Evento eliminado correctamente.')
                refresh()

            dlg=ft.AlertDialog(
                modal=True,
                title=ft.Text('Eliminar evento'),
                content=ft.Text('¿Desea eliminar este evento del historial? Esta acción no se puede deshacer.'),
                actions=[
                    ft.TextButton('Cancelar',on_click=close_dialog),
                    ft.ElevatedButton('Eliminar',icon=ft.Icons.DELETE_OUTLINE,on_click=do_delete)
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            page.dialog=dlg
            dlg.open=True
            page.update()

        save_btn=ft.ElevatedButton(
            'Guardar movimiento',
            icon=ft.Icons.SAVE,
            disabled=True
        )

        def form_is_valid():
            if not tire.value or not event.value:
                return False
            # Seguridad adicional: ROT no puede guardarse mientras esté bloqueado.
            if event.value == 'ROT':
                return False
            r=current_tire()
            if not r:
                return False
            tid=int(tire.value)
            lim=historical_limits(tid)

            entered_date=parse_event_date(date.value)
            last_date=latest_event_date(tid)
            if entered_date is None:
                return False
            if last_date is not None and entered_date < last_date:
                return False

            new_meter=num(meter.value)
            if new_meter is None:
                return False
            if lim and lim['max_meter'] is not None and float(new_meter) < float(lim['max_meter']):
                return False

            new_ti=num(ti.value)
            new_to=num(to.value)
            max_new=num(r['new_tread'])
            if new_ti is not None:
                if new_ti < 0:
                    return False
                if max_new is not None and new_ti > max_new:
                    return False
                if lim and lim['min_ti'] is not None and new_ti > float(lim['min_ti']):
                    return False
            if new_to is not None:
                if new_to < 0:
                    return False
                if max_new is not None and new_to > max_new:
                    return False
                if lim and lim['min_to'] is not None and new_to > float(lim['min_to']):
                    return False

            if event.value in ('INSP','INSC'):
                if r['status'] != 'SERVICIO' or r['equipment_id'] is None or not r['position']:
                    return False
            if event.value == 'INST' and (not equip.value or not (pos.value or '').strip()):
                return False
            return True

        def update_save_state(e=None):
            save_btn.disabled = not form_is_valid()
            page.update()

        def refresh(e=None):
            if not tire.value:
                hist.rows=[]
                load_current_state()
            else:
                rows=query(
                    '''SELECT o.*,e.code equipment_code
                       FROM occurrences o
                       LEFT JOIN equipment e ON e.id=o.equipment_id
                       WHERE o.tire_id=?
                       ORDER BY o.id DESC''',
                    (int(tire.value),)
                )
                hist.rows=[]
                for r in rows:
                    hist.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(format_date(r['event_date']))),
                            ft.DataCell(ft.Text(fmt(r['event_code']))),
                            ft.DataCell(ft.Text(fmt(r['equipment_code']))),
                            ft.DataCell(ft.Text(fmt(r['position']))),
                            ft.DataCell(ft.Text(fmt(r['meter']))),
                            ft.DataCell(ft.Text(f"{fmt(r['tread_inner'])}/{fmt(r['tread_outer'])}")),
                            ft.DataCell(ft.Text(fmt(r['pressure']))),
                            ft.DataCell(ft.Text(fmt(r['pressure_condition']))),
                            ft.DataCell(ft.Text(fmt(r['location']))),
                            ft.DataCell(ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip='Eliminar evento',
                                on_click=lambda e, oid=r['id']: ask_delete(oid)
                            ))
                        ])
                    )
                load_current_state()
                apply_event_rules()
            save_btn.disabled = not form_is_valid()
            page.update()

        def on_tire_change(e):
            refresh(e)

        def on_event_change(e):
            apply_event_rules(e)
            save_btn.disabled = not form_is_valid()
            page.update()

        tire.on_change=on_tire_change
        event.on_change=on_event_change
        date.on_change=update_save_state
        equip.on_change=update_save_state
        pos.on_change=update_save_state
        meter.on_change=update_save_state
        ti.on_change=update_save_state
        to.on_change=update_save_state
        press.on_change=update_save_state
        cond.on_change=update_save_state
        reason.on_change=update_save_state
        loc.on_change=update_save_state

        def save(e):
            if not tire.value or not event.value:
                return snack('Seleccione neumático y evento.',True)

            tid=int(tire.value)
            ec=event.value
            if ec == 'ROT':
                return snack('ROT está bloqueado hasta definir su funcionalidad.', True)
            r=current_tire()
            if not r:
                return snack('No se encontró el neumático seleccionado.',True)

            lim=historical_limits(tid)
            new_meter=num(meter.value)
            max_meter=lim['max_meter'] if lim else None
            if new_meter is None:
                return snack('Ingrese el horómetro / km.',True)
            if max_meter is not None and float(new_meter) < float(max_meter):
                return snack(
                    f'Horómetro inválido: {fmt(new_meter)} es menor que la última lectura válida {fmt(max_meter)}.',
                    True
                )

            new_ti=num(ti.value)
            new_to=num(to.value)
            max_new=num(r['new_tread'])

            if new_ti is not None:
                if new_ti < 0:
                    return snack('La cocada interior no puede ser negativa.',True)
                if max_new is not None and new_ti > max_new:
                    return snack(f'Cocada interior inválida: no puede superar la profundidad nueva ({fmt(max_new)} mm).',True)
                if lim and lim['min_ti'] is not None and new_ti > float(lim['min_ti']):
                    return snack(
                        f'Cocada interior inválida: {fmt(new_ti)} mm es mayor que la última cocada válida {fmt(lim["min_ti"])} mm.',
                        True
                    )

            if new_to is not None:
                if new_to < 0:
                    return snack('La cocada exterior no puede ser negativa.',True)
                if max_new is not None and new_to > max_new:
                    return snack(f'Cocada exterior inválida: no puede superar la profundidad nueva ({fmt(max_new)} mm).',True)
                if lim and lim['min_to'] is not None and new_to > float(lim['min_to']):
                    return snack(
                        f'Cocada exterior inválida: {fmt(new_to)} mm es mayor que la última cocada válida {fmt(lim["min_to"])} mm.',
                        True
                    )

            raw_date=(date.value or '').strip()
            event_date=raw_date
            date_ok=False
            for _fmt in ('%d/%m/%Y','%d-%m-%Y','%Y/%m/%d','%Y-%m-%d'):
                try:
                    event_date=dt.datetime.strptime(raw_date[:10],_fmt).strftime('%Y-%m-%d')
                    date_ok=True
                    break
                except Exception:
                    pass
            if not date_ok:
                return snack('Fecha inválida. Use dd/mm/aaaa.',True)

            entered_date=parse_event_date(event_date)
            last_date=latest_event_date(tid)
            if last_date is not None and entered_date is not None and entered_date < last_date:
                return snack(
                    f'Fecha inválida: {entered_date.strftime("%d/%m/%Y")} es anterior al último evento {last_date.strftime("%d/%m/%Y")}.',
                    True
                )

            if ec in ('INSP','INSC'):
                if r['status'] != 'SERVICIO' or r['equipment_id'] is None or not r['position']:
                    return snack('Para registrar una inspección el neumático debe estar instalado y EN SERVICIO.',True)
                eid=int(r['equipment_id'])
                event_pos=str(r['position'])
                equip.value=str(eid)
                pos.value=event_pos
            else:
                eid=int(equip.value) if equip.value else None
                event_pos=pos.value

            if ec=='INSC' and query(
                "SELECT id FROM occurrences WHERE tire_id=? AND event_code='INSC' AND event_date=? AND COALESCE(meter,-1)=COALESCE(?, -1)",
                (tid,event_date,new_meter)
            ):
                return snack('Ya existe una INSC con la misma fecha y lectura.',True)

            condition=(cond.value or 'FRIO').strip().upper().replace('Í','I')
            condition='CALIENTE' if condition.startswith('CAL') else 'FRIO'

            execute(
                '''INSERT INTO occurrences(
                       tire_id,event_code,event_date,equipment_id,position,meter,
                       tread_inner,tread_outer,pressure,pressure_condition,reason,location,notes
                   ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (tid,ec,event_date,eid,event_pos,new_meter,new_ti,new_to,
                 num(press.value),condition,reason.value,loc.value,notes.value)
            )

            if ec=='INST':
                execute(
                    "UPDATE tires SET status='SERVICIO',equipment_id=?,position=?,current_meter=?,"
                    "tread_inner=COALESCE(?,tread_inner),tread_outer=COALESCE(?,tread_outer) WHERE id=?",
                    (eid,event_pos,new_meter,new_ti,new_to,tid)
                )
            elif ec=='DINS':
                execute(
                    "UPDATE tires SET status='STAND-BY',equipment_id=NULL,position=NULL,current_meter=? WHERE id=?",
                    (new_meter,tid)
                )
            elif ec=='REPA':
                execute("UPDATE tires SET status='REPARACIÓN' WHERE id=?",(tid,))
            elif ec=='BAJA':
                execute("UPDATE tires SET status='BAJA',equipment_id=NULL,position=NULL WHERE id=?",(tid,))
            else:
                execute(
                    'UPDATE tires SET current_meter=COALESCE(?,current_meter),'
                    'tread_inner=COALESCE(?,tread_inner),tread_outer=COALESCE(?,tread_outer) WHERE id=?',
                    (new_meter,new_ti,new_to,tid)
                )

            snack(f'Evento {ec} registrado correctamente.')
            refresh()
            update_event_button_states(tid)
            save_btn.disabled = True
            page.update()

        save_btn.on_click=save

        if pre_tire:
            refresh()
        else:
            save_btn.disabled = True

        history_scroller=ft.Row(
            [ft.Container(content=hist,width=1280)],
            scroll=ft.ScrollMode.ALWAYS
        )

        # ------------------------------------------------------------------
        # CABECERA OPERATIVA - lógica visual basada en MegaSoftire FoxPro.
        # Primero se busca/selecciona el neumático; luego se muestra su ficha
        # vertical y los eventos. El formulario de movimiento queda oculto
        # hasta escoger un evento.
        # ------------------------------------------------------------------
        search_tire = ft.TextField(
            label='Buscar código / serie',
            prefix_icon=ft.Icons.SEARCH,
            width=255
        )
        search_result = ft.Dropdown(
            label='Neumático encontrado',
            width=255,
            visible=False,
            options=[]
        )

        register_missing_btn = ft.ElevatedButton(
            'REGISTRAR NEUMÁTICO',
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            visible=False
        )

        foxpro_values = {}
        foxpro_order = [
            'Código',
            'Serie',
            'Marca',
            'Medida',
            'Modelo / Diseño',
            'Estado',
            'Nro. Eventos',
            'Fecha',
            'Equipo-Posición',
            'Horómetro',
            'Hrs Acumuladas',
            'Ext/Int - Inicial',
            'Ext/Int - Último',
            'Psi Act(F/C)-Rec',
            'Proyección Hrs',
            'Horas Acumuladas',
            'Costo Acumulado',
            'Costo x Hrs.',
            'Tapa Válvula',
            'Lugar de Operación',
        ]
        for label in foxpro_order:
            foxpro_values[label] = ft.Text('—', size=13, color=TEXT_MAIN)

        header_tire = ft.Text('Seleccione un neumático', size=18, weight=ft.FontWeight.BOLD, color=TEXT_MAIN)
        header_detail = ft.Text('', size=12, color=TEXT_MUTED)

        ficha_rows = []
        vertical_labels = [
            'Nro. Eventos',
            'Fecha',
            'Equipo-Posición',
            'Horómetro',
            'Hrs Acumuladas',
            'Ext/Int - Inicial',
            'Ext/Int - Último',
            'Psi Act(F/C)-Rec',
            'Proyección Hrs',
            'Horas Acumuladas',
            'Costo Acumulado',
            'Costo x Hrs.',
            'Tapa Válvula',
            'Lugar de Operación',
        ]
        event_values = [foxpro_values]
        for _ in range(2):
            event_values.append({
                label: ft.Text('—', size=13, color=TEXT_MAIN)
                for label in vertical_labels
            })

        event_headers = [
            ft.Text('Último evento', size=11, weight=ft.FontWeight.BOLD, color=TEXT_MUTED),
            ft.Text('Penúltimo evento', size=11, weight=ft.FontWeight.BOLD, color=TEXT_MUTED),
            ft.Text('Antepenúltimo evento', size=11, weight=ft.FontWeight.BOLD, color=TEXT_MUTED),
        ]
        # Cabecera de las tres columnas de eventos.
        ficha_rows.append(
            ft.Row([
                ft.Container(width=185),
                *[
                    ft.Container(content=event_headers[i], expand=True)
                    for i in range(3)
                ],
            ], spacing=12)
        )

        for label in vertical_labels:
            ficha_rows.append(
                ft.Row([
                    ft.Container(
                        content=ft.Text(label, size=12, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                        width=185
                    ),
                    *[
                        ft.Container(
                            content=event_values[i][label],
                            expand=True
                        )
                        for i in range(3)
                    ],
                ], spacing=12)
            )

        ficha_panel = card(
            ft.Column([
                ft.Text('Consulta del neumático', size=17, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            header_tire,
                        ], spacing=2),
                        expand=2
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text('Marca:', size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                            foxpro_values['Marca'],
                            ft.Text('Diseño:', size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                            foxpro_values['Modelo / Diseño'],
                        ], spacing=2),
                        expand=1
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text('Medida:', size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                            foxpro_values['Medida'],
                            ft.Text('Estado:', size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                            foxpro_values['Estado'],
                        ], spacing=2),
                        expand=1
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text('Modelo:', size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                            foxpro_values['Modelo / Diseño'],
                            ft.Text('Precio:', size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                            ft.Text('—', size=13, color=TEXT_MAIN),
                        ], spacing=2),
                        expand=1
                    ),
                ], spacing=18, vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Divider(height=8),
                *ficha_rows,
            ], spacing=7),
            width=None
        )

        movement_form = card(ft.Column([
            ft.Text('Datos del movimiento',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
            ft.Row([tire,event,date],wrap=True),
            ref,
            ft.Row([equip,pos,meter],wrap=True),
            ft.Row([ti,to,press,cond],wrap=True),
            ft.Row([reason,loc],wrap=True),
            notes,
            ft.Row([
                save_btn,
                ft.Text(
                    'Guardar se habilita solo cuando fecha, horómetro y cocadas cumplen las validaciones.',
                    size=11,color=TEXT_MUTED
                )
            ],wrap=True)
        ]))
        movement_form.visible = False

        def clear_foxpro_ficha():
            header_tire.value = 'Seleccione un neumático'
            header_detail.value = ''
            for label in foxpro_order:
                foxpro_values[label].value = '—'
            for i in range(1, 3):
                for label in vertical_labels:
                    event_values[i][label].value = '—'
            event_headers[0].value = 'Último evento'
            event_headers[1].value = 'Penúltimo evento'
            event_headers[2].value = 'Antepenúltimo evento'

        def load_foxpro_ficha(tid):
            rows = query(
                '''SELECT t.*,e.code equipment_code
                   FROM tires t LEFT JOIN equipment e ON e.id=t.equipment_id
                   WHERE t.id=?''',
                (int(tid),)
            )
            if not rows:
                clear_foxpro_ficha()
                return
            r = rows[0]
            occ = query(
                '''SELECT * FROM occurrences
                   WHERE tire_id=?
                   ORDER BY event_date ASC,id ASC''',
                (int(tid),)
            )
            last = occ[-1] if occ else None
            first = occ[0] if occ else None

            inst = [o for o in occ if o['event_code'] == 'INST']
            last_inst = inst[-1] if inst else None

            current_meter = r['current_meter']
            inst_meter = last_inst['meter'] if last_inst else None
            hrs_acum = None
            try:
                if current_meter is not None and inst_meter is not None:
                    hrs_acum = max(0, float(current_meter) - float(inst_meter))
            except Exception:
                hrs_acum = None

            initial_i = first['tread_inner'] if first and first['tread_inner'] is not None else r['new_tread']
            initial_e = first['tread_outer'] if first and first['tread_outer'] is not None else r['new_tread']
            last_i = last['tread_inner'] if last and last['tread_inner'] is not None else r['tread_inner']
            last_e = last['tread_outer'] if last and last['tread_outer'] is not None else r['tread_outer']

            actual_press = last['pressure'] if last and last['pressure'] is not None else None
            press_cond = last['pressure_condition'] if last and last['pressure_condition'] else ''
            rec_press = r['recommended_pressure']

            header_tire.value = f"{r['code']} | {r['serial'] or 's/serie'}"
            header_detail.value = (
                f"{r['brand'] or ''} · {r['size'] or ''} · {r['design'] or ''} · Estado: {r['status'] or '-'}"
            )

            foxpro_values['Código'].value = str(r['code'] or '—')
            foxpro_values['Serie'].value = str(r['serial'] or 's/serie')
            foxpro_values['Marca'].value = str(r['brand'] or '—')
            foxpro_values['Medida'].value = str(r['size'] or '—')
            foxpro_values['Modelo / Diseño'].value = str(r['design'] or '—')
            foxpro_values['Estado'].value = str(r['status'] or '—')
            foxpro_values['Nro. Eventos'].value = str(len(occ))
            foxpro_values['Fecha'].value = format_date(last['event_date']) if last else '—'
            foxpro_values['Equipo-Posición'].value = (
                f"{r['equipment_code'] or '-'} - P{r['position'] or '-'}"
            )
            foxpro_values['Horómetro'].value = fmt(current_meter) or '—'
            foxpro_values['Hrs Acumuladas'].value = f"{hrs_acum:.1f}" if hrs_acum is not None else '—'
            foxpro_values['Ext/Int - Inicial'].value = f"{fmt(initial_e)}/{fmt(initial_i)}"
            foxpro_values['Ext/Int - Último'].value = f"{fmt(last_e)}/{fmt(last_i)}"
            foxpro_values['Psi Act(F/C)-Rec'].value = (
                f"{fmt(actual_press) or '-'} ({press_cond or '-'}) / {fmt(rec_press) or '-'}"
            )
            foxpro_values['Proyección Hrs'].value = fmt(r['projected_life']) or '—'
            # La base web actual aún no contiene campos económicos equivalentes
            # a los del FoxPro. Se dejan visibles en su posición original.
            foxpro_values['Horas Acumuladas'].value = f"{hrs_acum:.1f}" if hrs_acum is not None else '—'
            foxpro_values['Costo Acumulado'].value = '—'
            foxpro_values['Costo x Hrs.'].value = '—'
            foxpro_values['Tapa Válvula'].value = 'NO'
            foxpro_values['Lugar de Operación'].value = fmt(last['location']) if last and last['location'] else '—'


            # --------------------------------------------------------------
            # Visualización de los tres últimos eventos en paralelo.
            # Mantiene el mismo orden vertical de la ficha aprobada.
            # --------------------------------------------------------------
            last_three = list(reversed(occ[-3:]))

            def fill_event_column(col_idx, target):
                values = event_values[col_idx]
                if not target:
                    for label in vertical_labels:
                        values[label].value = '—'
                    return

                # Posición ordinal real del evento dentro del historial.
                target_index = next(
                    (i for i, item in enumerate(occ) if item['id'] == target['id']),
                    None
                )
                event_number = (target_index + 1) if target_index is not None else '—'

                # Última instalación vigente hasta ese evento.
                base_inst = None
                if target_index is not None:
                    for item in reversed(occ[:target_index + 1]):
                        if item['event_code'] == 'INST':
                            base_inst = item
                            break

                event_hours = None
                try:
                    if target['meter'] is not None and base_inst and base_inst['meter'] is not None:
                        event_hours = max(0, float(target['meter']) - float(base_inst['meter']))
                except Exception:
                    event_hours = None

                init_i = (
                    base_inst['tread_inner']
                    if base_inst and base_inst['tread_inner'] is not None
                    else r['new_tread']
                )
                init_e = (
                    base_inst['tread_outer']
                    if base_inst and base_inst['tread_outer'] is not None
                    else r['new_tread']
                )
                evt_i = target['tread_inner'] if target['tread_inner'] is not None else '—'
                evt_e = target['tread_outer'] if target['tread_outer'] is not None else '—'
                evt_press = target['pressure'] if target['pressure'] is not None else None
                evt_cond = target['pressure_condition'] if target['pressure_condition'] else ''

                values['Nro. Eventos'].value = str(event_number)
                values['Fecha'].value = format_date(target['event_date'])
                values['Equipo-Posición'].value = (
                    f"{target['equipment_id'] or '-'} - P{target['position'] or '-'}"
                )

                # Mostrar código de equipo en lugar del id cuando exista.
                if target['equipment_id']:
                    eq_row = query(
                        'SELECT code FROM equipment WHERE id=?',
                        (int(target['equipment_id']),)
                    )
                    if eq_row:
                        values['Equipo-Posición'].value = (
                            f"{eq_row[0]['code']} - P{target['position'] or '-'}"
                        )

                values['Horómetro'].value = fmt(target['meter']) or '—'
                values['Hrs Acumuladas'].value = (
                    f"{event_hours:.1f}" if event_hours is not None else '—'
                )
                values['Ext/Int - Inicial'].value = f"{fmt(init_e)}/{fmt(init_i)}"
                values['Ext/Int - Último'].value = f"{fmt(evt_e)}/{fmt(evt_i)}"
                values['Psi Act(F/C)-Rec'].value = (
                    f"{fmt(evt_press) or '-'} ({evt_cond or '-'}) / {fmt(rec_press) or '-'}"
                )
                values['Proyección Hrs'].value = fmt(r['projected_life']) or '—'
                values['Horas Acumuladas'].value = (
                    f"{event_hours:.1f}" if event_hours is not None else '—'
                )
                values['Costo Acumulado'].value = '—'
                values['Costo x Hrs.'].value = '—'
                note_text = str(target['notes'] or '').upper() if 'notes' in target.keys() else ''
                values['Tapa Válvula'].value = (
                    'SI' if ('TAPA' in note_text or 'VALVULA' in note_text or 'VÁLVULA' in note_text) else 'NO'
                )
                values['Lugar de Operación'].value = fmt(target['location']) if target['location'] else '—'

            for col_idx in range(3):
                target = last_three[col_idx] if col_idx < len(last_three) else None
                fill_event_column(col_idx, target)
                if target:
                    prefix = ['Último', 'Penúltimo', 'Antepenúltimo'][col_idx]
                    event_headers[col_idx].value = f"{prefix}: {target['event_code']}"
                else:
                    event_headers[col_idx].value = ['Último evento', 'Penúltimo evento', 'Antepenúltimo evento'][col_idx]

        def select_operational_tire(tid):
            if not tid:
                return
            tire.value = str(tid)
            movement_form.visible = False
            event.value = None
            load_foxpro_ficha(tid)
            update_event_button_states(tid)
            refresh()
            movement_form.visible = False
            page.update()

        def go_register_missing(e=None):
            pending_code = (search_tire.value or '').strip()
            if not pending_code:
                return
            tires_view(prefill_code=pending_code)

        register_missing_btn.on_click = go_register_missing

        def do_search(e=None):
            term = (search_tire.value or '').strip()
            movement_form.visible = False
            event.value = None
            register_missing_btn.visible = False
            if not term:
                search_result.visible = False
                search_result.options = []
                search_result.value = None
                tire.value = None
                clear_foxpro_ficha()
                update_event_button_states(None)
                page.update()
                return

            rows = query(
                '''SELECT id,code,serial FROM tires
                   WHERE code LIKE ? OR serial LIKE ?
                   ORDER BY code''',
                (f'%{term}%', f'%{term}%')
            )
            search_result.options = [
                ft.dropdown.Option(str(r['id']), f"{r['code']} | {r['serial'] or 's/serie'}")
                for r in rows
            ]
            if len(rows) == 1:
                search_result.visible = False
                search_result.value = str(rows[0]['id'])
                select_operational_tire(rows[0]['id'])
            elif len(rows) > 1:
                search_result.visible = True
                search_result.value = None
                clear_foxpro_ficha()
                update_event_button_states(None)
                page.update()
            else:
                search_result.visible = False
                search_result.value = None
                tire.value = None
                clear_foxpro_ficha()
                update_event_button_states(None)
                register_missing_btn.visible = True
                snack('Código no registrado. Puede registrar el neumático desde el botón habilitado.', True)
                page.update()

        def on_search_result(e):
            selected = getattr(e, 'data', None) or search_result.value
            if selected:
                search_result.value = str(selected)
                select_operational_tire(selected)

        search_tire.on_submit = do_search
        search_tire.on_change = do_search
        search_result.on_change = on_search_result

        event_icons_local = {
            'INST': ft.Icons.ADD_CIRCLE_OUTLINE,
            'INSP': ft.Icons.CHECK_CIRCLE_OUTLINE,
            'INSC': ft.Icons.FACT_CHECK_OUTLINED,
            'ROT': ft.Icons.SYNC_ALT,
            'INVE': ft.Icons.SWAP_HORIZ,
            'DINS': ft.Icons.REMOVE_CIRCLE_OUTLINE,
            'REPA': ft.Icons.HANDYMAN_OUTLINED,
            'BAJA': ft.Icons.DELETE_OUTLINE,
        }
        event_buttons_local = {}

        def update_event_button_states(tid=None):
            # Regla operativa:
            # - Registrado pero sin instalar: solo INST habilitado.
            # - Instalado en un equipo: INST bloqueado y eventos operativos habilitados.
            # - ROT permanece bloqueado hasta definir su funcionalidad.
            if not tid:
                for code, btn in event_buttons_local.items():
                    btn.disabled = True
                return

            rows = query(
                """SELECT id,equipment_id,position,status
                   FROM tires
                   WHERE id=?""",
                (int(tid),)
            )
            if not rows:
                for code, btn in event_buttons_local.items():
                    btn.disabled = True
                return

            r = rows[0]
            installed = r['equipment_id'] is not None and str(r['position'] or '').strip() != ''

            for code, btn in event_buttons_local.items():
                if code == 'ROT':
                    btn.disabled = True
                elif installed:
                    btn.disabled = (code == 'INST')
                else:
                    btn.disabled = (code != 'INST')

        def open_event_form(ec):
            if not tire.value:
                return snack('Primero busque y seleccione un neumático.', True)
            if ec == 'ROT':
                return snack('ROT permanece bloqueado hasta definir su funcionalidad.', True)
            event.value = ec
            movement_form.visible = True
            load_current_state()
            apply_event_rules()
            update_save_state()
            page.update()

        for ec in ['INST','INSP','INSC','ROT','INVE','DINS','REPA','BAJA']:
            event_buttons_local[ec] = ft.OutlinedButton(
                ec,
                icon=event_icons_local[ec],
                tooltip=EVENTS.get(ec, ec),
                disabled=True,
                on_click=lambda e, code=ec: open_event_form(code)
            )

        if pre_tire:
            search_tire.value = str(current_tire()['code']) if current_tire() else ''
            load_foxpro_ficha(pre_tire)
            update_event_button_states(pre_tire)

        left_panel = ft.Column([
            card(ft.Column([
                ft.Text('Consulta operativa', size=17, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                search_tire,
                search_result,
                register_missing_btn,
            ], spacing=8), width=285),
            card(
                ft.Column([
                    ft.Text('Registrar evento', size=12, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                    *[
                        ft.Container(
                            content=event_buttons_local[c],
                            width=140
                        )
                        for c in ['INST','INSP','INSC','ROT','INVE','DINS','REPA','BAJA']
                    ],
                ], spacing=8),
                width=185
            ),
        ], spacing=12)

        top_operational_area = ft.Row([
            ft.Container(content=left_panel, width=300),
            ft.Container(content=ficha_panel, expand=True),
        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START)

        content.content=ft.Column([
            page_title('Movimiento de neumáticos','Registro operativo del ciclo de vida'),
            top_operational_area,
            movement_form,
            card(ft.Column([
                ft.Text('Historial del neumático',size=17,weight=ft.FontWeight.BOLD,color=TEXT_MAIN),
                ft.Text('Use la barra inferior para desplazarse horizontalmente. La columna Acción permite eliminar eventos.',size=11,color=TEXT_MUTED),
                history_scroller
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
        # El manejo de ESC pertenece solo a Neumáticos en servicio.
        if idx != 2:
            page.on_keyboard_event = None
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
