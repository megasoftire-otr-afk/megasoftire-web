# MegaSoftire Web 2026 - corrección INSP + fechas dd/mm/aaaa (31/08/2026)
import datetime as dt
import os
import hashlib
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


MASTER_TIRE_UPDATES_20260902 = [
    ('1345', '08251Y10267', '01/01/2026', 3850.0, 'Goodyear', '18.00-25', 'SMO-5D', 'L-5S', 'Tire SOL', 100.0, 84.0, 84.0, 15.0, 2300.0, 'Convencional', 'Nueva'),
    ('1350', '08251Y10009', '01/01/2026', 3850.0, 'Goodyear', '18.00-25', 'SMO-5D', 'L-5S', 'Tire SOL', 100.0, 84.0, 84.0, 15.0, 2300.0, 'Convencional', 'Nueva'),
    ('1351', '08251Y10104', '01/01/2026', 3850.0, 'Goodyear', '18.00-25', 'SMO-5D', 'L-5S', 'Tire SOL', 100.0, 84.0, 84.0, 15.0, 2300.0, 'Convencional', 'Nueva'),
    ('1352', '08251Y10759', '01/01/2026', 3850.0, 'Goodyear', '18.00-25', 'SMO-5D', 'L-5S', 'Tire SOL', 100.0, 84.0, 84.0, 15.0, 2300.0, 'Convencional', 'Nueva'),
    ('1376', '12251Y10060', '01/01/2026', 3850.0, 'Goodyear', '18.00-25', 'SMO-5D', 'L-5S', 'Tire SOL', 100.0, 84.0, 84.0, 15.0, 2300.0, 'Convencional', 'Nueva'),
    ('1362', '12251Y10747', '01/01/2026', 3850.0, 'Goodyear', '18.00-25', 'SMO-5D', 'L-5S', 'Tire SOL', 100.0, 84.0, 84.0, 15.0, 2300.0, 'Convencional', 'Nueva'),
    ('1378', '12251Y10332', '01/01/2026', 3850.0, 'Goodyear', '18.00-25', 'SMO-5D', 'L-5S', 'Tire SOL', 100.0, 84.0, 84.0, 15.0, 2300.0, 'Convencional', 'Nueva'),
    ('1367', '12251Y10070', '01/01/2026', 3850.0, 'Goodyear', '18.00-25', 'SMO-5D', 'L-5S', 'Tire SOL', 100.0, 84.0, 84.0, 15.0, 2300.0, 'Convencional', 'Nueva'),
    ('1363', 'HC3MVC493', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1364', 'HC7MVC174', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1365', 'HC4MVC666', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1366', 'HC7MVC176', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1374', 'AE1HVC1933', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1375', 'HC6MVC992', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1354', 'XY2AVC992', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1377', 'HC3MVC631', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1346', 'XY3AVC183', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1357', 'AE4HVC653', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1320', 'AE3HVC510', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1321', 'AE4HVC655', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1359', 'AEIHVC194', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1355', 'AU7MVC799', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1316', 'AH6GVC949', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1317', 'XH2GVC017', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1370', 'XYZAVC991', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1349', 'XY1AVC833', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1329', 'AE1HVC196', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1344', 'XY3AVC184', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1353', 'XY1AVC835', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1358', 'AEOHVC048', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1327', 'HE9HVC270', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1328', 'AE1HVC195', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1371', 'AE2HVC375', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1372', 'CH9MVC663', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1324', 'AE2HVC373', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
    ('1373', 'HC5MYC850', '01/01/2026', 7800.0, 'Yokohama', '29.5-29', 'Y524', 'L-5', 'Tire SOL', 100.0, 104.0, 104.0, 15.0, 2800.0, 'Convencional', 'Nueva'),
]


def main(page: ft.Page):
    init_db()

    # Campos maestros necesarios para la consulta operativa y el registro maestro.
    startup_cols = {r['name'] for r in query("PRAGMA table_info(tires)")}
    for col_name, col_type in [
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
    ]:
        if col_name not in startup_cols:
            execute(f'ALTER TABLE tires ADD COLUMN {col_name} {col_type}')

    # Actualización única del maestro de 36 neumáticos.
    # Se actualiza por Código: no crea duplicados y no toca estado, equipo,
    # posición, horómetro, profundidades actuales ni historial de eventos.
    master_migration_key = 'master_tires_20260902_v1'
    master_done = query('SELECT value FROM app_meta WHERE key=?', (master_migration_key,))
    if not master_done:
        for (
            tire_code, serial, entry_date, cost_usd, brand, size, design,
            tra, supplier, pressure, tread_ext, tread_int, retirement_tread,
            life_target, construction_type, tire_condition
        ) in MASTER_TIRE_UPDATES_20260902:
            execute(
                '''
                UPDATE tires
                SET serial=?,
                    entry_date=?,
                    cost_usd=?,
                    brand=?,
                    size=?,
                    design=?,
                    compound=?,
                    supplier=?,
                    recommended_pressure=?,
                    new_tread=?,
                    new_tread_outer=?,
                    new_tread_inner=?,
                    retirement_tread=?,
                    projected_life_target=?,
                    projected_life=?,
                    construction_type=?,
                    tire_condition=?
                WHERE code=?
                ''',
                (
                    serial, entry_date, cost_usd, brand, size, design, tra,
                    supplier, pressure, tread_ext, tread_ext, tread_int,
                    retirement_tread, life_target, life_target,
                    construction_type, tire_condition, tire_code
                )
            )
        execute(
            'INSERT OR REPLACE INTO app_meta(key,value) VALUES(?,?)',
            (master_migration_key, '36 neumáticos actualizados por código - 02/09/2026')
        )

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
        compound = make_catalog_field('Clasificación TRA', 'compound', FIELD_W)
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
            ('Clasificación TRA', 135),
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
                ('Clasificación TRA', compound_value),
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

        # Dashboard visual tipo Power BI. Se alimenta exclusivamente de los
        # mismos datos calculados para la tabla de neumáticos en servicio.
        rem_chart_body = ft.Column([], spacing=7)
        hours_chart_body = ft.Column([], spacing=7)
        brand_pie_body = ft.Column([], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        pressure_pie_body = ft.Column([], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        valve_pie_body = ft.Column([], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        def dashboard_bar(label, value, max_value, suffix='', decimals=1):
            try:
                val = float(value)
            except Exception:
                val = 0.0
            try:
                mx = max(float(max_value), 0.0001)
            except Exception:
                mx = 1.0
            ratio = max(0.0, min(1.0, val / mx))
            return ft.Row([
                ft.Text(label, width=72, size=10, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ft.Stack([
                    ft.Container(width=260, height=14, bgcolor='#E9EEF5', border_radius=7),
                    ft.Container(width=max(3, 260 * ratio), height=14, bgcolor=NAV_ACCENT, border_radius=7),
                ], width=260, height=14),
                ft.Text(f'{val:.{decimals}f}{suffix}', width=72, size=10, text_align=ft.TextAlign.RIGHT, color=TEXT_MAIN),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        def _soft_dotted_grid(width=1200, segments=120):
            """Cuadrícula horizontal punteada suave, sin dependencias nuevas."""
            return ft.Row(
                [ft.Container(width=4, height=1, bgcolor='#D8E1EB') for _ in range(segments)],
                spacing=5,
                width=width,
                height=1,
            )

        def grouped_remanente_chart(groups):
            """Remanente: equipos en X, P1-P4 agrupadas y eje Y fijo 0-100%."""
            pos_order = ['P1', 'P2', 'P3', 'P4']
            if not any(v is not None for vals in groups.values() for v in vals.values()):
                return ft.Text('Sin datos suficientes para graficar.', size=11, color=TEXT_MUTED)

            chart_h = 150
            bar_w = 10
            ticks = [100, 80, 60, 40, 20, 0]
            y_axis = ft.Column(
                [ft.Text(f'{t}%', size=8.5, color=TEXT_MUTED) for t in ticks],
                height=chart_h,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.END,
            )

            group_blocks = []
            group_items = list(groups.items())
            for idx, (eq, pos_values) in enumerate(group_items):
                bars = []
                for pos in pos_order:
                    val = pos_values.get(pos)
                    if val is None:
                        bar = ft.Container(width=bar_w, height=2, bgcolor='#CBD5E1', border_radius=2)
                    else:
                        v = max(0.0, min(100.0, float(val)))
                        h = max(3, chart_h * v / 100.0)
                        bar = ft.Container(width=bar_w, height=h, bgcolor=NAV_ACCENT, border_radius=2)
                    bars.append(ft.Column([
                        ft.Container(height=chart_h, alignment=ft.Alignment.BOTTOM_CENTER, content=bar),
                        ft.Text(pos, size=7.2, weight=ft.FontWeight.BOLD, color=TEXT_MUTED,
                                text_align=ft.TextAlign.CENTER),
                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER))

                group_blocks.append(ft.Container(
                    width=76,
                    content=ft.Column([
                        ft.Row(bars, spacing=4, alignment=ft.MainAxisAlignment.CENTER,
                               vertical_alignment=ft.CrossAxisAlignment.END),
                        ft.Text(eq, size=9, weight=ft.FontWeight.BOLD,
                                color=TEXT_MAIN, text_align=ft.TextAlign.CENTER),
                    ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ))
                if idx < len(group_items) - 1:
                    group_blocks.append(ft.Container(
                        width=12,
                        height=chart_h + 28,
                        alignment=ft.Alignment.BOTTOM_CENTER,
                        content=ft.Text('|', size=12, weight=ft.FontWeight.BOLD, color=TEXT_MUTED),
                    ))

            # Separación compacta entre equipos; la barra vertical queda centrada en el espacio blanco.
            plot = ft.Stack([
                ft.Column(
                    [_soft_dotted_grid() for _ in ticks],
                    height=chart_h,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=0,
                ),
                ft.Row(
                    group_blocks,
                    spacing=4,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
            ], height=chart_h + 28)

            return ft.Row([
                ft.Column([
                    ft.Text('% Rem.', size=8.5, color=TEXT_MUTED),
                    y_axis,
                    ft.Container(height=24),
                ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.END),
                ft.Container(expand=True, content=plot),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START)

        def grouped_hours_chart(groups):
            """Horas por posición: acumuladas (azul) + restantes proyectadas (naranja)."""
            import math
            pos_order = ['P1', 'P2', 'P3', 'P4']
            all_totals = []
            for vals in groups.values():
                for data in vals.values():
                    if data is None:
                        continue
                    if isinstance(data, dict):
                        worked = float(data.get('worked') or 0.0)
                        remaining = float(data.get('remaining') or 0.0)
                    else:
                        worked = float(data)
                        remaining = 0.0
                    all_totals.append(max(0.0, worked) + max(0.0, remaining))
            if not all_totals:
                return ft.Text('Sin datos suficientes para graficar.', size=11, color=TEXT_MUTED)

            step = 500
            max_total = max(all_totals)
            # Eje Y siempre en rangos exactos de 500 h y con un escalón libre
            # por encima de la barra más alta para que la proyección no quede
            # pegada al borde superior del gráfico.
            next_tick = (int(math.floor(max_total / step)) + 1) * step
            y_max = max(4000, next_tick)
            ticks = list(range(y_max, -1, -step))
            chart_h = 150
            bar_w = 10
            y_axis = ft.Column(
                [ft.Text(f'{t}', size=8.5, color=TEXT_MUTED) for t in ticks],
                height=chart_h,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.END,
            )

            group_blocks = []
            group_items = list(groups.items())
            for idx, (eq, pos_values) in enumerate(group_items):
                bars = []
                for pos in pos_order:
                    data = pos_values.get(pos)
                    if data is None:
                        stacked_bar = ft.Container(width=bar_w, height=2, bgcolor='#CBD5E1', border_radius=2)
                    else:
                        if isinstance(data, dict):
                            worked = max(0.0, float(data.get('worked') or 0.0))
                            remaining = max(0.0, float(data.get('remaining') or 0.0))
                        else:
                            worked = max(0.0, float(data))
                            remaining = 0.0
                        worked_h = chart_h * min(worked, float(y_max)) / float(y_max)
                        remaining_h = chart_h * min(remaining, max(0.0, float(y_max) - worked)) / float(y_max)
                        segments = []
                        if remaining > 0:
                            segments.append(ft.Container(
                                width=bar_w,
                                height=max(2, remaining_h),
                                bgcolor='#F59E0B',
                                border_radius=ft.BorderRadius.only(top_left=2, top_right=2),
                            ))
                        if worked > 0:
                            segments.append(ft.Container(
                                width=bar_w,
                                height=max(3, worked_h),
                                bgcolor=NAV_ACCENT,
                                border_radius=(
                                    ft.BorderRadius.only(bottom_left=2, bottom_right=2)
                                    if remaining > 0 else 2
                                ),
                            ))
                        stacked_bar = ft.Column(segments, spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    bars.append(ft.Column([
                        ft.Container(height=chart_h, alignment=ft.Alignment.BOTTOM_CENTER, content=stacked_bar),
                        ft.Text(pos, size=7.2, weight=ft.FontWeight.BOLD, color=TEXT_MUTED,
                                text_align=ft.TextAlign.CENTER),
                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER))

                group_blocks.append(ft.Container(
                    width=76,
                    content=ft.Column([
                        ft.Row(bars, spacing=4, alignment=ft.MainAxisAlignment.CENTER,
                               vertical_alignment=ft.CrossAxisAlignment.END),
                        ft.Text(eq, size=9, weight=ft.FontWeight.BOLD,
                                color=TEXT_MAIN, text_align=ft.TextAlign.CENTER),
                    ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ))
                if idx < len(group_items) - 1:
                    group_blocks.append(ft.Container(
                        width=12,
                        height=chart_h + 28,
                        alignment=ft.Alignment.BOTTOM_CENTER,
                        content=ft.Text('|', size=12, weight=ft.FontWeight.BOLD, color=TEXT_MUTED),
                    ))

            plot = ft.Stack([
                ft.Column(
                    [_soft_dotted_grid() for _ in ticks],
                    height=chart_h,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=0,
                ),
                ft.Row(
                    group_blocks,
                    spacing=4,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
            ], height=chart_h + 28)

            legend = ft.Row([
                ft.Row([
                    ft.Container(width=10, height=10, bgcolor=NAV_ACCENT, border_radius=2),
                    ft.Text('Horas acumuladas', size=9, color=TEXT_MUTED),
                ], spacing=5),
                ft.Row([
                    ft.Container(width=10, height=10, bgcolor='#F59E0B', border_radius=2),
                    ft.Text('Horas restantes proyectadas', size=9, color=TEXT_MUTED),
                ], spacing=5),
            ], spacing=16)

            return ft.Column([
                legend,
                ft.Row([
                    ft.Column([
                        ft.Text('Horas (h)', size=8.5, color=TEXT_MUTED),
                        y_axis,
                        ft.Container(height=24),
                    ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.END),
                    ft.Container(expand=True, content=plot),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
            ], spacing=4)

        def donut_svg_chart(items, total=None, palette=None, legend_lines=None, center_label='Total'):
            """Dona SVG compatible con Flet actual, con leyenda compacta y simétrica."""
            if not items:
                return ft.Text('Sin datos suficientes para graficar.', size=11, color=TEXT_MUTED)
            import base64, math
            if total is None:
                total = sum(count for _label, count in items)
            if palette is None:
                palette = ['#1D4ED8', '#16A34A', '#EA580C', '#A855F7', '#DC2626', '#0D9488', '#CA8A04', '#475569']
            cx, cy, radius, stroke = 82, 82, 50, 24
            circumference = 2 * math.pi * radius
            offset = 0.0
            circles = []
            legend = []
            for idx, (label, count) in enumerate(items):
                color = palette[idx % len(palette)]
                pct_value = (count / total * 100.0) if total else 0.0
                dash = circumference * (count / total) if total else 0.0
                gap = max(0.0, circumference - dash)
                if count > 0:
                    circles.append(
                        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{color}" '
                        f'stroke-width="{stroke}" stroke-dasharray="{dash:.3f} {gap:.3f}" '
                        f'stroke-dashoffset="{-offset:.3f}" transform="rotate(-90 {cx} {cy})" />'
                    )
                offset += dash
                legend.append(ft.Row([
                    ft.Container(width=9, height=9, bgcolor=color, border_radius=2),
                    ft.Text(f'{label}: {count} ({pct_value:.1f}%)', size=9.2, color=TEXT_MAIN),
                ], spacing=6))
            svg = (
                '<svg xmlns="http://www.w3.org/2000/svg" width="164" height="164" viewBox="0 0 164 164">'
                '<circle cx="82" cy="82" r="50" fill="none" stroke="#E2E8F0" stroke-width="24" />'
                + ''.join(circles) +
                f'<text x="82" y="79" text-anchor="middle" font-family="Arial" font-size="23" font-weight="700" fill="#172033">{total}</text>'
                f'<text x="82" y="98" text-anchor="middle" font-family="Arial" font-size="10" fill="#64748B">{center_label}</text>'
                '</svg>'
            )
            svg_b64 = base64.b64encode(svg.encode('utf-8')).decode('ascii')
            chart = ft.Image(src='data:image/svg+xml;base64,' + svg_b64, width=164, height=164, fit=ft.BoxFit.CONTAIN)
            controls = [
                ft.Row([chart, ft.Column(legend, spacing=5)], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ]
            if legend_lines:
                controls.append(
                    ft.Container(
                        width=285,
                        border=ft.Border.all(1, '#CBD5E1'),
                        border_radius=8,
                        padding=8,
                        content=ft.Column([
                            ft.Text('LEYENDA / CRITERIO', size=9, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                            *[ft.Text(line, size=8.5, color=TEXT_MAIN) for line in legend_lines],
                        ], spacing=3),
                    )
                )
            return ft.Column(controls, spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        def brand_pie_chart(brand_counts):
            if not brand_counts:
                return ft.Text('Sin datos suficientes para graficar.', size=11, color=TEXT_MUTED)
            ordered = sorted(brand_counts.items(), key=lambda x: (-x[1], x[0]))
            return donut_svg_chart(ordered, palette=['#1D4ED8', '#16A34A', '#EA580C', '#A855F7', '#DC2626', '#0D9488'])

        def pressure_pie_chart(counts):
            items = [
                ('± 5 psi (OK)', counts.get('green', 0)),
                ('> 5 a 10 psi', counts.get('orange', 0)),
                ('> 10 psi', counts.get('red', 0)),
            ]
            return donut_svg_chart(
                items,
                palette=['#16A34A', '#F59E0B', '#DC2626'],
            )

        def valve_pie_chart(counts):
            items = [
                ('Con tapa', counts.get('yes', 0)),
                ('Sin tapa', counts.get('no', 0)),
            ]
            return donut_svg_chart(items, palette=['#16A34A', '#DC2626'])

        def dashboard_card(title, subtitle, body, height=None):
            return ft.Container(
                expand=True,
                height=height,
                bgcolor=CARD_BG,
                border=ft.Border.all(1, '#E2E8F0'),
                border_radius=14,
                padding=16,
                content=ft.Column([
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text(subtitle, size=10, color=TEXT_MUTED),
                    ft.Divider(height=10, color='#E2E8F0'),
                    body,
                ], spacing=5),
            )

        # Dashboard: primero las tres donas simétricas; debajo,
        # remanente y horas acumuladas a todo el ancho.
        dashboard = ft.Column([
            ft.Row([
                dashboard_card('DISTRIBUCIÓN POR MARCA', 'Participación de neumáticos actualmente en servicio', brand_pie_body, height=245),
                dashboard_card('PRESIONES VS. PRESIÓN RECOMENDADA', 'Diferencia absoluta entre presión actual y recomendada', pressure_pie_body, height=245),
                dashboard_card('TAPA VÁLVULA', 'Estado de tapa de válvula en neumáticos en servicio', valve_pie_body, height=245),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
            dashboard_card('REMANENTE POR POSICIÓN (%)', 'Eje X: equipos · P1, P2, P3 y P4 · Eje Y: % remanente', rem_chart_body),
            dashboard_card('HORAS ACUMULADAS + HORAS RESTANTES POR POSICIÓN (h)', 'Azul: horas acumuladas · Naranja: horas restantes proyectadas · Altura total: proyección de vida', hours_chart_body),
        ], spacing=12)

        # Tabla técnica compacta: encabezado fijo + desplazamiento vertical interno.
        # El contenedor horizontal usa ScrollMode.ALWAYS para mantener disponible
        # la barra horizontal durante todo el recorrido de la tabla.
        service_columns = [
            'CÓDIGO DE\nEQUIPO',
            'POSICIÓN',
            'CÓDIGO',
            'SERIE',
            'MARCA',
            'MODELO',
            'CONDICIÓN',
            'HORAS\nACUMULADAS',
            'COSTO X\nHRS',
            'COCADA\nORIGINAL',
            'COCADA\nEXT/INT',
            '%\nREMANENTE',
            'Hs/mm',
            'PROYECCIÓN DE\nVIDA (h)',
            'PRESIÓN\nRECOMENDADA',
            'PRESIÓN\nACTUAL',
            'TAPA\nVÁLVULA',
            'FECHA ÚLTIMA\nINSPECCIÓN',
            'ÚLTIMO\nHORÓMETRO',
        ]
        service_widths = [112,72,78,112,92,82,82,100,90,105,100,90,65,118,112,92,82,120,105]
        service_total_width = sum(service_widths)

        def service_cell(value, width, header=False, bold=False):
            return ft.Container(
                width=width,
                height=36 if header else 22,
                padding=ft.Padding(left=4, top=0, right=4, bottom=0),
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    str(value),
                    size=9 if header else 9.5,
                    weight=ft.FontWeight.BOLD if header or bold else None,
                    text_align=ft.TextAlign.CENTER,
                    max_lines=2 if header else 1,
                ),
                border=ft.Border(bottom=ft.BorderSide(1, '#D7DEE8')),
            )

        service_header = ft.Row(
            [service_cell(label, width, header=True) for label, width in zip(service_columns, service_widths)],
            spacing=0,
        )
        # Tabla completa verticalmente: todas las filas forman parte del scroll general de la página.
        service_body = ft.Column([], spacing=0)
        service_table_view = ft.Row([
            ft.Container(
                width=service_total_width,
                content=ft.Column([service_header, service_body], spacing=0),
            )
        ], scroll=ft.ScrollMode.ALWAYS, spacing=0)
        # Historial operativo retirado de este módulo; los datos históricos se conservan en la base.


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
                       pressure_condition,location,reason,notes
                FROM occurrences WHERE tire_id=?
                ORDER BY event_date DESC,id DESC LIMIT 1
            """, (tid,))
            last_row = last[0] if last else None

            # Para la tabla de Neumáticos en servicio, los campos de inspección
            # se toman de la última INSP/INSC registrada del neumático.
            insp = query("""
                SELECT event_date,event_code,meter,tread_inner,tread_outer,pressure,
                       pressure_condition,location,reason,notes
                FROM occurrences
                WHERE tire_id=? AND event_code IN ('INSP','INSC')
                ORDER BY event_date DESC,id DESC LIMIT 1
            """, (tid,))
            inspection_row = insp[0] if insp else last_row

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

            last_pressure = inspection_row['pressure'] if inspection_row and inspection_row['pressure'] is not None else None
            note_text = str(inspection_row['notes'] or '').upper() if inspection_row else ''
            valve_cap = 'SI' if ('TAPA' in note_text or 'VALVULA' in note_text or 'VÁLVULA' in note_text) else 'NO'
            return {
                'inst_meter': inst_meter, 'inst_date': inst_date, 'worked': worked,
                'min_tread': min_tread, 'wear': wear, 'rem': rem, 'hpmm': hpmm,
                'last_pressure': last_pressure,
                'last_event': last_row['event_code'] if last_row else '',
                'last_date': last_row['event_date'] if last_row else '',
                'inspection_date': inspection_row['event_date'] if inspection_row else '',
                'inspection_meter': inspection_row['meter'] if inspection_row else None,
                'valve_cap': valve_cap,
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
                options_sql += " ORDER BY COALESCE(e.code,''), CAST(COALESCE(NULLIF(t.position,''),'999') AS INTEGER), t.code"
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
            service_body.controls = []
            rem_values = []
            worked_values = []

            previous_equipment = None
            for r, od in ops:
                if od['rem'] is not None:
                    rem_values.append(od['rem'])
                if od['worked'] is not None:
                    worked_values.append(od['worked'])

                equipment_code = r['equipment_code'] or '—'

                # Separador horizontal entre equipos, manteniendo una sola tabla.
                if previous_equipment is not None and equipment_code != previous_equipment:
                    service_body.controls.append(ft.Container(height=7, bgcolor=BG))
                previous_equipment = equipment_code

                original_outer = r['new_tread_outer'] if 'new_tread_outer' in r.keys() else None
                original_inner = r['new_tread_inner'] if 'new_tread_inner' in r.keys() else None
                if original_outer is None:
                    original_outer = r['new_tread']
                if original_inner is None:
                    original_inner = r['new_tread']

                original_vals = [v for v in (original_outer, original_inner) if isinstance(v, (int, float))]
                current_vals = [v for v in (r['tread_outer'], r['tread_inner']) if isinstance(v, (int, float))]
                original_min = min(original_vals) if original_vals else None
                current_min = min(current_vals) if current_vals else None
                rem_pct = None
                wear_mm = None
                hs_mm = None
                if original_min not in (None, 0) and current_min is not None:
                    rem_pct = max(0, min(100, float(current_min) / float(original_min) * 100))
                    wear_mm = max(0, float(original_min) - float(current_min))
                    if od['worked'] is not None and wear_mm > 0:
                        hs_mm = float(od['worked']) / wear_mm

                cost_hour = None
                if r['cost_usd'] is not None and od['worked'] is not None and float(od['worked']) > 0:
                    cost_hour = float(r['cost_usd']) / float(od['worked'])

                # Proyección de vida total (h), usando el mismo criterio conservador
                # del Hs/mm: la MENOR lectura entre RTD EXT e INT.
                #
                # Hs/mm = horas acumuladas / (cocada original - RTD mínimo actual)
                # Horas restantes = (RTD mínimo actual - profundidad de retiro) * Hs/mm
                # Proyección total = horas acumuladas + horas restantes
                projected_life = None
                retirement_tread = r['retirement_tread'] if 'retirement_tread' in r.keys() else None
                if (hs_mm is not None and od['worked'] is not None and
                        current_min is not None and retirement_tread is not None):
                    remaining_mm = max(0.0, float(current_min) - float(retirement_tread))
                    projected_life = float(od['worked']) + (remaining_mm * float(hs_mm))

                condition_value = r['tire_condition'] if 'tire_condition' in r.keys() else ''

                row_values = [
                    equipment_code,
                    f"P{r['position']}" if r['position'] not in (None, '') else '—',
                    r['code'] or '—',
                    r['serial'] or '—',
                    r['brand'] or '—',
                    r['design'] or '—',
                    condition_value or '—',
                    fmt(od['worked']) or '—',
                    f"$ {cost_hour:.2f}/h" if cost_hour is not None else '—',
                    fmt(original_min) if original_min is not None else '—',
                    f"{fmt(r['tread_outer'])}/{fmt(r['tread_inner'])}" if current_vals else '—',
                    f"{rem_pct:.1f}%" if rem_pct is not None else '—',
                    f"{hs_mm:.2f}" if hs_mm is not None else '—',
                    f"{projected_life:,.0f}" if projected_life is not None else '—',
                    fmt(r['recommended_pressure']) or '—',
                    fmt(od['last_pressure']) or '—',
                    od['valve_cap'],
                    format_date(od['inspection_date']) or '—',
                    fmt(od['inspection_meter']) or '—',
                ]
                service_body.controls.append(ft.Row([
                    service_cell(v, service_widths[idx], bold=idx in (0,2))
                    for idx, v in enumerate(row_values)
                ], spacing=0))

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
            ]

            # Dashboard por equipo y posición. En Remanente, el eje X son los equipos
            # y dentro de cada equipo se muestran P1, P2, P3 y P4; eje Y = % remanente.
            chart_groups = {}
            for r, od in ops:
                eq = r['equipment_code'] or '—'
                pos = f"P{r['position']}" if r['position'] not in (None, '') else '—'
                original_outer = r['new_tread_outer'] if 'new_tread_outer' in r.keys() else None
                original_inner = r['new_tread_inner'] if 'new_tread_inner' in r.keys() else None
                if original_outer is None:
                    original_outer = r['new_tread']
                if original_inner is None:
                    original_inner = r['new_tread']
                original_vals = [v for v in (original_outer, original_inner) if isinstance(v, (int, float))]
                current_vals = [v for v in (r['tread_outer'], r['tread_inner']) if isinstance(v, (int, float))]
                rem = None
                if original_vals and current_vals and min(original_vals) not in (None, 0):
                    rem = max(0, min(100, float(min(current_vals)) / float(min(original_vals)) * 100))
                worked = None
                if od['worked'] is not None:
                    try:
                        worked = max(0.0, float(od['worked']))
                    except Exception:
                        worked = None
                # Horas restantes proyectadas usando el mismo criterio aprobado:
                # menor RTD EXT/INT y profundidad de retiro del Registro Maestro.
                remaining_hours = None
                if worked is not None and original_vals and current_vals:
                    original_min_chart = min(original_vals)
                    current_min_chart = min(current_vals)
                    wear_mm_chart = max(0.0, float(original_min_chart) - float(current_min_chart))
                    retirement_tread_chart = r['retirement_tread'] if 'retirement_tread' in r.keys() else None
                    if wear_mm_chart > 0 and retirement_tread_chart is not None:
                        hs_mm_chart = float(worked) / wear_mm_chart
                        remaining_mm_chart = max(0.0, float(current_min_chart) - float(retirement_tread_chart))
                        remaining_hours = remaining_mm_chart * hs_mm_chart

                g = chart_groups.setdefault(eq, {'rem_by_pos': {}, 'hours_by_pos': {}})
                if rem is not None and pos in ('P1','P2','P3','P4'):
                    g['rem_by_pos'][pos] = rem
                if worked is not None and pos in ('P1','P2','P3','P4'):
                    g['hours_by_pos'][pos] = {
                        'worked': worked,
                        'remaining': remaining_hours if remaining_hours is not None else 0.0,
                    }

            rem_groups = {k: v['rem_by_pos'] for k, v in chart_groups.items() if v['rem_by_pos']}
            hours_groups = {k: v['hours_by_pos'] for k, v in chart_groups.items() if v['hours_by_pos']}
            rem_chart_body.controls = [grouped_remanente_chart(rem_groups)]
            hours_chart_body.controls = [grouped_hours_chart(hours_groups)]

            brand_counts = {}
            for r, _od in ops:
                brand = str(r['brand'] or 'Sin marca').strip() or 'Sin marca'
                brand_counts[brand] = brand_counts.get(brand, 0) + 1
            brand_pie_body.controls = [brand_pie_chart(brand_counts)]

            # Distribución de presión por diferencia absoluta respecto a la presión recomendada.
            # Criterio: <= 5 psi verde; >5 y <=10 psi naranja; >10 psi rojo.
            pressure_counts = {'green': 0, 'orange': 0, 'red': 0}
            for r, od in ops:
                rec = r['recommended_pressure']
                act = od['last_pressure']
                if rec is None or act is None:
                    continue
                try:
                    diff = abs(float(act) - float(rec))
                except Exception:
                    continue
                if diff <= 5:
                    pressure_counts['green'] += 1
                elif diff <= 10:
                    pressure_counts['orange'] += 1
                else:
                    pressure_counts['red'] += 1
            pressure_pie_body.controls = [pressure_pie_chart(pressure_counts)]

            valve_counts = {'yes': 0, 'no': 0}
            for _r, od in ops:
                if str(od['valve_cap'] or '').strip().upper() == 'SI':
                    valve_counts['yes'] += 1
                else:
                    valve_counts['no'] += 1
            valve_pie_body.controls = [valve_pie_chart(valve_counts)]

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

            summary.value = f"{len(rows)} neumático(s) mostrado(s)"
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
                'Estado actual, posiciones y horas de trabajo por equipo'
            ),
            metrics,
            dashboard,
            card(ft.Column([
                ft.Row([
                    ft.Text('Detalle técnico de neumáticos instalados', size=17, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Container(expand=True),
                    summary
                ]),
                ft.Text(
                    'Una fila por neumático instalado. Cada equipo muestra P1, P2, P3 y P4 en orden, con separación antes del siguiente equipo.',
                    size=10, color=TEXT_MUTED
                ),
                service_table_view
            ]))        ], scroll=ft.ScrollMode.AUTO, spacing=16)
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
            'Clasificación TRA',
            'Costo $',
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
                            ft.Text('Clasificación TRA:', size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                            foxpro_values['Clasificación TRA'],
                            ft.Text('Costo $:', size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                            foxpro_values['Costo $'],
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
            # Orden cronológico real de los eventos. No dependemos del formato
            # textual almacenado en SQLite ni del id de inserción.
            occ_raw = query(
                '''SELECT * FROM occurrences
                   WHERE tire_id=?''',
                (int(tid),)
            )

            def occurrence_sort_key(item):
                parsed = parse_event_date(item['event_date'])
                # Fechas no interpretables quedan al inicio para no desplazar
                # un evento válido reciente de la columna "Último".
                return (parsed or dt.datetime.min, int(item['id'] or 0))

            occ = sorted(occ_raw, key=occurrence_sort_key)
            last = occ[-1] if occ else None
            first = occ[0] if occ else None

            inst = [o for o in occ if o['event_code'] == 'INST']
            last_inst = inst[-1] if inst else None

            # Para la ficha operativa usamos el horómetro del evento
            # cronológicamente más reciente. Si no existe, conservamos el
            # current_meter del maestro como respaldo.
            current_meter = (
                last['meter'] if last and last['meter'] is not None
                else r['current_meter']
            )
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
            foxpro_values['Clasificación TRA'].value = str(r['compound'] or '—')
            try:
                header_cost = float(r['cost_usd']) if r['cost_usd'] is not None else None
            except Exception:
                header_cost = None
            foxpro_values['Costo $'].value = f"$ {header_cost:,.2f}" if header_cost is not None else '—'
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
            life_value = r['projected_life_target'] if r['projected_life_target'] is not None else r['projected_life']
            foxpro_values['Proyección Hrs'].value = fmt(life_value) or '—'
            foxpro_values['Horas Acumuladas'].value = f"{hrs_acum:.1f}" if hrs_acum is not None else '—'
            if header_cost is not None and hrs_acum is not None and hrs_acum > 0:
                foxpro_values['Costo x Hrs.'].value = f"$ {header_cost / hrs_acum:.2f}/h"
            else:
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
                values['Proyección Hrs'].value = fmt(life_value) or '—'
                values['Horas Acumuladas'].value = (
                    f"{event_hours:.1f}" if event_hours is not None else '—'
                )
                if header_cost is not None and event_hours is not None and event_hours > 0:
                    values['Costo x Hrs.'].value = f"$ {header_cost / event_hours:.2f}/h"
                else:
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
        """Programa de mantenimiento - Prueba 01: evaluación de remanente (RTD)."""
        rows = query("""
            SELECT
                t.code, t.serial, t.brand, t.size, t.design,
                t.tread_inner, t.tread_outer,
                e.id AS equipment_id, e.code AS equipment_code,
                e.vehicle_type, e.model AS equipment_model, t.position
            FROM tires t
            LEFT JOIN equipment e ON e.id=t.equipment_id
            WHERE t.status='SERVICIO'
            ORDER BY COALESCE(e.code,''), t.position, t.code
        """)

        def rtd_value(r):
            vals=[]
            for value in (r['tread_inner'], r['tread_outer']):
                try:
                    if value is not None and str(value).strip() != '':
                        vals.append(float(value))
                except Exception:
                    pass
            return min(vals) if vals else None

        def rtd_condition(rtd):
            # Criterio aprobado para Prueba 01:
            # Buen estado > 30 mm
            # Próximo cambio > 20 y <= 30 mm
            # Cambio urgente 0 a 20 mm
            if rtd is None or rtd < 0:
                return 'SIN LECTURA'
            if rtd > 30:
                return 'BUEN ESTADO'
            if rtd > 20:
                return 'PRÓXIMO CAMBIO'
            return 'CAMBIO URGENTE'

        evaluated=[]
        for r in rows:
            rtd=rtd_value(r)
            evaluated.append((r, rtd, rtd_condition(rtd)))

        total=len(rows)
        equipment_count=len({r['equipment_id'] for r in rows if r['equipment_id'] is not None})
        counts={
            'BUEN ESTADO': 0,
            'PRÓXIMO CAMBIO': 0,
            'CAMBIO URGENTE': 0,
            'SIN LECTURA': 0,
        }
        for _,_,condition in evaluated:
            counts[condition]=counts.get(condition,0)+1

        evaluated_total=total-counts['SIN LECTURA']
        good_pct=(counts['BUEN ESTADO']/evaluated_total*100) if evaluated_total else 0
        attention=counts['PRÓXIMO CAMBIO']+counts['CAMBIO URGENTE']
        attention_pct=(attention/evaluated_total*100) if evaluated_total else 0

        def pct(value, base):
            return (value/base*100) if base else 0

        def top_metric(title, value, subtitle, value_color=TEXT_MAIN):
            return ft.Container(
                width=250,
                height=108,
                bgcolor=CARD_BG,
                border=ft.Border.all(1, '#DDE5ED'),
                border_radius=10,
                padding=14,
                content=ft.Column([
                    ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=TEXT_MAIN,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text(str(value), size=29, weight=ft.FontWeight.BOLD, color=value_color,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text(subtitle, size=10, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )

        criteria_rows = ft.Column([
            ft.Container(
                bgcolor='#F5F7FA', padding=8,
                content=ft.Row([
                    ft.Text('CONDICIÓN', width=150, size=11, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text('CRITERIO RTD', width=150, size=11, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text('INTERPRETACIÓN', expand=True, size=11, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ])
            ),
            ft.Container(
                border=ft.Border(bottom=ft.BorderSide(1,'#E6EBF0')), padding=8,
                content=ft.Row([
                    ft.Container(width=8, height=28, bgcolor='#2E9B45', border_radius=4),
                    ft.Text('BUEN ESTADO', width=135, size=11, weight=ft.FontWeight.BOLD, color='#2E9B45'),
                    ft.Text('Mayor a 30 mm', width=150, size=11, color=TEXT_MAIN),
                    ft.Text('Continuar en servicio.', expand=True, size=11, color=TEXT_MUTED),
                ], spacing=8)
            ),
            ft.Container(
                border=ft.Border(bottom=ft.BorderSide(1,'#E6EBF0')), padding=8,
                content=ft.Row([
                    ft.Container(width=8, height=28, bgcolor='#F2A900', border_radius=4),
                    ft.Text('PRÓXIMO CAMBIO', width=135, size=11, weight=ft.FontWeight.BOLD, color='#C98600'),
                    ft.Text('20 a 30 mm', width=150, size=11, color=TEXT_MAIN),
                    ft.Text('Programar seguimiento / próximo cambio.', expand=True, size=11, color=TEXT_MUTED),
                ], spacing=8)
            ),
            ft.Container(
                padding=8,
                content=ft.Row([
                    ft.Container(width=8, height=28, bgcolor='#D92D20', border_radius=4),
                    ft.Text('CAMBIO URGENTE', width=135, size=11, weight=ft.FontWeight.BOLD, color='#D92D20'),
                    ft.Text('0 a 20 mm', width=150, size=11, color=TEXT_MAIN),
                    ft.Text('Programar cambio con prioridad.', expand=True, size=11, color=TEXT_MUTED),
                ], spacing=8)
            ),
        ], spacing=0)

        def rtd_donut_chart():
            """Dona compacta con la condición RTD calculada de la última lectura disponible."""
            import base64, math
            items=[
                ('Buen Estado', counts['BUEN ESTADO'], '#2E9B45'),
                ('Próximo Cambio', counts['PRÓXIMO CAMBIO'], '#F2A900'),
                ('Cambio Urgente', counts['CAMBIO URGENTE'], '#D92D20'),
            ]
            total_chart=sum(n for _,n,_ in items)
            cx=cy=78; radius=46; stroke=22
            circumference=2*math.pi*radius
            offset=0.0; circles=[]; legend=[]
            for label,n,color in items:
                dash=circumference*(n/total_chart) if total_chart else 0
                gap=max(0.0,circumference-dash)
                if n>0:
                    circles.append(
                        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{color}" '
                        f'stroke-width="{stroke}" stroke-dasharray="{dash:.3f} {gap:.3f}" '
                        f'stroke-dashoffset="{-offset:.3f}" transform="rotate(-90 {cx} {cy})" />'
                    )
                offset += dash
                pc=(n/total_chart*100) if total_chart else 0
                legend.append(ft.Row([
                    ft.Container(width=9,height=9,bgcolor=color,border_radius=2),
                    ft.Text(f'{label}: {n} ({pc:.1f}%)',size=9.2,color=TEXT_MAIN),
                ],spacing=5))
            svg=(
                '<svg xmlns="http://www.w3.org/2000/svg" width="156" height="156" viewBox="0 0 156 156">'
                '<circle cx="78" cy="78" r="46" fill="none" stroke="#E2E8F0" stroke-width="22" />'
                + ''.join(circles) +
                f'<text x="78" y="76" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700" fill="#172033">{total_chart}</text>'
                '<text x="78" y="94" text-anchor="middle" font-family="Arial" font-size="9" fill="#64748B">neumáticos</text>'
                '</svg>'
            )
            src='data:image/svg+xml;base64,'+base64.b64encode(svg.encode('utf-8')).decode('ascii')
            return ft.Row([
                ft.Image(src=src,width=150,height=150,fit=ft.BoxFit.CONTAIN),
                ft.Column(legend,spacing=7),
            ],spacing=8,vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # Resumen por tipo de vehículo, basado en los neumáticos actualmente en servicio.
        vehicle_summary={}
        for r,_,_ in evaluated:
            vehicle=(str(r['vehicle_type']).strip().upper() if r['vehicle_type'] else 'SIN CLASIFICAR')
            vehicle_summary[vehicle]=vehicle_summary.get(vehicle,0)+1
        vehicle_table=ft.DataTable(
            heading_row_height=34,
            data_row_min_height=30,
            data_row_max_height=30,
            column_spacing=26,
            columns=[
                ft.DataColumn(ft.Text('Tipo de Vehículo', size=11, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text('N° Neumáticos', size=11, weight=ft.FontWeight.BOLD), numeric=True),
                ft.DataColumn(ft.Text('% del Total', size=11, weight=ft.FontWeight.BOLD), numeric=True),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(vehicle, size=10)),
                    ft.DataCell(ft.Text(str(n), size=10)),
                    ft.DataCell(ft.Text(f'{pct(n,total):.1f}%', size=10)),
                ])
                for vehicle,n in sorted(vehicle_summary.items(), key=lambda kv:(-kv[1],kv[0]))
            ] + ([ft.DataRow(cells=[
                ft.DataCell(ft.Text('TOTAL', size=10, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text(str(total), size=10, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text('100.0%' if total else '0.0%', size=10, weight=ft.FontWeight.BOLD)),
            ])] if total else [])
        )

        # Resumen específico de SCOOP por modelo registrado en Administración de equipos.
        scoop_summary={}
        for r,_,_ in evaluated:
            vehicle=(str(r['vehicle_type']).strip().upper() if r['vehicle_type'] else '')
            if 'SCOOP' in vehicle:
                model=(str(r['equipment_model']).strip().upper() if r['equipment_model'] else 'SIN MODELO')
                scoop_summary[model]=scoop_summary.get(model,0)+1
        scoop_total=sum(scoop_summary.values())
        scoop_table=ft.DataTable(
            heading_row_height=34, data_row_min_height=30, data_row_max_height=30, column_spacing=18,
            columns=[
                ft.DataColumn(ft.Text('Modelo Scoop',size=11,weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text('N° Neumáticos',size=11,weight=ft.FontWeight.BOLD),numeric=True),
                ft.DataColumn(ft.Text('% del Total',size=11,weight=ft.FontWeight.BOLD),numeric=True),
            ],
            rows=[ft.DataRow(cells=[
                ft.DataCell(ft.Text(model,size=10)),
                ft.DataCell(ft.Text(str(n),size=10)),
                ft.DataCell(ft.Text(f'{pct(n,scoop_total):.1f}%',size=10)),
            ]) for model,n in sorted(scoop_summary.items())] + ([ft.DataRow(cells=[
                ft.DataCell(ft.Text('TOTAL',size=10,weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text(str(scoop_total),size=10,weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text('100.0%' if scoop_total else '0.0%',size=10,weight=ft.FontWeight.BOLD)),
            ])] if scoop_total else [])
        )

        condition_rows=[]
        for label,text_color,row_color in [
            ('BUEN ESTADO','#176B2C','#DDF3E3'),
            ('PRÓXIMO CAMBIO','#8A5A00','#FFF0C2'),
            ('CAMBIO URGENTE','#A61B12','#FAD9D6'),
        ]:
            n=counts[label]
            condition_rows.append(ft.DataRow(color=row_color, cells=[
                ft.DataCell(ft.Text(label.title(), size=10, weight=ft.FontWeight.BOLD, color=text_color)),
                ft.DataCell(ft.Text(str(n), size=10, weight=ft.FontWeight.BOLD, color=text_color)),
                ft.DataCell(ft.Text(f'{pct(n,evaluated_total):.1f}%', size=10, weight=ft.FontWeight.BOLD, color=text_color)),
            ]))
        if counts['SIN LECTURA']:
            condition_rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text('Sin lectura', size=10, weight=ft.FontWeight.BOLD, color=TEXT_MUTED)),
                ft.DataCell(ft.Text(str(counts['SIN LECTURA']), size=10)),
                ft.DataCell(ft.Text(f'{pct(counts["SIN LECTURA"],total):.1f}%', size=10)),
            ]))
        condition_rows.append(ft.DataRow(color='#000000', cells=[
            ft.DataCell(ft.Text('TOTAL', size=10, weight=ft.FontWeight.BOLD, color='#FFFFFF')),
            ft.DataCell(ft.Text(str(total), size=10, weight=ft.FontWeight.BOLD, color='#FFFFFF')),
            ft.DataCell(ft.Text('100.0%' if total else '0.0%', size=10, weight=ft.FontWeight.BOLD, color='#FFFFFF')),
        ]))
        condition_table=ft.DataTable(
            heading_row_height=34,
            heading_row_color='#000000',
            data_row_min_height=30,
            data_row_max_height=30,
            column_spacing=34,
            columns=[
                ft.DataColumn(ft.Text('Condición', size=11, weight=ft.FontWeight.BOLD, color='#FFFFFF')),
                ft.DataColumn(ft.Text('Cantidad', size=11, weight=ft.FontWeight.BOLD, color='#FFFFFF'), numeric=True),
                ft.DataColumn(ft.Text('% del Total', size=11, weight=ft.FontWeight.BOLD, color='#FFFFFF'), numeric=True),
            ],
            rows=condition_rows
        )

        content.content=ft.Column([
            page_title('3. Programa de mantenimiento · 1. Evaluación de Remanente (RTD)',
                       'Evaluación automática de neumáticos en servicio según profundidad remanente'),
            ft.Row([
                top_metric('NEUMÁTICOS EN SERVICIO', total, 'Total actualmente instalado', '#C81D2A'),
                top_metric('EQUIPOS EN SERVICIO', equipment_count, 'Equipos con neumáticos instalados'),
                top_metric('NEUMÁTICOS EN BUEN ESTADO', f'{good_pct:.1f}%',
                           f'{counts["BUEN ESTADO"]} neumáticos', '#2E9B45'),
                top_metric('NEUMÁTICOS QUE REQUIEREN ATENCIÓN', f'{attention_pct:.1f}%',
                           f'{attention} neumáticos', '#C81D2A'),
            ], wrap=True, spacing=12, run_spacing=12),
            ft.Row([
                ft.Container(expand=1, content=card(ft.Column([
                    ft.Text('SCOOP POR MODELO', size=14, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Row([scoop_table], scroll=ft.ScrollMode.AUTO),
                    ft.Text('Modelos tomados del registro de equipos.', size=9.5, italic=True, color=TEXT_MUTED),
                ], spacing=8))),
                ft.Container(expand=1, content=card(ft.Column([
                    ft.Text('CONDICIÓN GENERAL DE NEUMÁTICOS (RTD)', size=14, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Row([condition_table], scroll=ft.ScrollMode.AUTO),
                ], spacing=8))),
                ft.Container(expand=1, content=card(ft.Column([
                    ft.Text('GRÁFICO DE CONDICIÓN RTD', size=14, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    rtd_donut_chart(),
                    ft.Text('Evaluación según la menor lectura RTD disponible.', size=9.5, italic=True, color=TEXT_MUTED),
                ], spacing=8))),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
        ], scroll=ft.ScrollMode.AUTO, spacing=16)
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
                    ft.Text('Web 2026',size=11,color='#B9C9D9')
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
        # Portada inspirada en el diseño clásico de MegaSoftire/FoxPro.
        # Se conserva la lógica de acceso de v22; solo cambia la presentación.
        classic_blue = '#0000AA'
        classic_white = '#FFFFFF'
        outer_bg = '#E5E7EB'
        expected_user = 'admin'
        expected_password_hash = '04445e6487736590d1ef50186b414e737e0164683cbbec64e00e73c000fd3bef'

        user_field = ft.TextField(
            value='', width=220, height=38, autofocus=True,
            text_size=16, bgcolor=classic_blue, color=classic_white,
            border_color=classic_white, focused_border_color=classic_white,
            cursor_color=classic_white, content_padding=ft.Padding(left=8, top=4, right=8, bottom=4),
        )
        password_field = ft.TextField(
            value='', width=220, height=38, password=True,
            text_size=16, bgcolor=classic_blue, color=classic_white,
            border_color=classic_white, focused_border_color=classic_white,
            cursor_color=classic_white, content_padding=ft.Padding(left=8, top=4, right=8, bottom=4),
        )
        login_message = ft.Text('', size=12, color='#FFFF66', text_align=ft.TextAlign.CENTER,
                                font_family='Courier New')

        def enter_system(e=None):
            username = (user_field.value or '').strip()
            password = password_field.value or ''
            password_ok = hashlib.sha256(password.encode('utf-8')).hexdigest() == expected_password_hash
            if username != expected_user or not password_ok:
                login_message.value = 'USUARIO O CLAVE INCORRECTOS'
                password_field.value = ''
                page.update()
                return
            # Login web estable: después de validar usuario/clave usamos un perfil
            # conocido y completo. Esto evita que una fila antigua/incompleta de la
            # tabla users en Render bloquee la construcción de la pantalla principal.
            session['user'] = {'username': 'admin', 'full_name': 'Administrador', 'role': 'ADMIN'}
            try:
                build_shell()
                page.update()
            except Exception as ex:
                # Si hubiera un error al construir la pantalla principal, no dejar el
                # botón aparentemente sin respuesta: mostramos el fallo en la portada.
                session['user'] = None
                login_message.value = f'ERROR AL INGRESAR: {str(ex)[:120]}'
                page.update()

        user_field.on_submit = lambda e: password_field.focus()
        password_field.on_submit = enter_system

        dos_font = 'Courier New'
        login_panel = ft.Container(
            width=900, height=600, bgcolor=classic_blue, padding=12,
            border=ft.Border(
                left=ft.BorderSide(2, classic_white), top=ft.BorderSide(2, classic_white),
                right=ft.BorderSide(2, classic_white), bottom=ft.BorderSide(2, classic_white),
            ),
            content=ft.Container(
                expand=True, padding=14,
                border=ft.Border(
                    left=ft.BorderSide(1, classic_white), top=ft.BorderSide(1, classic_white),
                    right=ft.BorderSide(1, classic_white), bottom=ft.BorderSide(1, classic_white),
                ),
                content=ft.Column([
                    ft.Container(height=8),
                    ft.Container(
                        width=560, height=58, alignment=ft.Alignment.CENTER,
                        border=ft.Border(
                            left=ft.BorderSide(2, classic_white), top=ft.BorderSide(2, classic_white),
                            right=ft.BorderSide(2, classic_white), bottom=ft.BorderSide(2, classic_white),
                        ),
                        content=ft.Text('SISTEMA DE CONTROL DE NEUMÁTICOS OTR', size=19,
                                        weight=ft.FontWeight.BOLD, color=classic_white,
                                        text_align=ft.TextAlign.CENTER, font_family=dos_font),
                    ),
                    ft.Container(height=18),
                    ft.Text('MegaSoftire', size=92, weight=ft.FontWeight.BOLD,
                            color=classic_white, text_align=ft.TextAlign.CENTER, font_family=dos_font),
                    ft.Text('VERSIÓN WEB 2026', size=20, weight=ft.FontWeight.BOLD,
                            color=classic_white, text_align=ft.TextAlign.CENTER, font_family=dos_font),
                    ft.Container(height=10),
                    ft.Row([
                        ft.Text('USUARIO  :', width=125, size=18, weight=ft.FontWeight.BOLD,
                                color=classic_white, font_family=dos_font), user_field,
                    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([
                        ft.Text('CLAVE    :', width=125, size=18, weight=ft.FontWeight.BOLD,
                                color=classic_white, font_family=dos_font), password_field,
                    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    login_message,
                    ft.Container(height=2),
                    ft.ElevatedButton(
                        'INGRESAR',
                        on_click=enter_system,
                        width=220,
                        height=42,
                        bgcolor=classic_blue,
                        color=classic_white,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=0),
                            side=ft.BorderSide(2, classic_white),
                            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD, font_family=dos_font),
                        ),
                    ),
                    ft.Container(height=2),
                    ft.Text('UD. ESTÁ AUTORIZADO PARA INGRESAR AL SISTEMA', size=16,
                            weight=ft.FontWeight.BOLD, color=classic_white,
                            text_align=ft.TextAlign.CENTER, font_family=dos_font),
                    ft.Text('PRESIONE ENTER PARA INGRESAR', size=16,
                            weight=ft.FontWeight.BOLD, color=classic_white,
                            text_align=ft.TextAlign.CENTER, font_family=dos_font),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            ),
        )

        app_host.content = ft.Container(expand=True, bgcolor=outer_bg,
                                        alignment=ft.Alignment.CENTER, content=login_panel)
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
