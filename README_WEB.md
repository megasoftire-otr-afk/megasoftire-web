# MegaSoftire WEB 2026 — v2

Versión Web modernizada del proyecto MegaSoftire.

## Acceso inicial
- Usuario: `admin`
- Contraseña: `Admin2026!`

> Credenciales solo para demostración. En producción deben cambiarse y almacenarse con un esquema de autenticación más robusto.

## Incluido en v2
- Pantalla de inicio de sesión.
- Dashboard de indicadores.
- Navegación lateral moderna con los 9 módulos originales.
- Maestro de equipos.
- Maestro de neumáticos y búsqueda.
- Estados: SERVICIO, STAND-BY, REPARACIÓN y BAJA.
- Eventos: INST, DINS, REPA, INSP, INSC, INVE, ROT y BAJA.
- Historial operativo por neumático.
- Validación de INSC duplicada por fecha + lectura.
- Programa de mantenimiento básico por profundidad remanente.
- Catálogo visual de reportes del sistema original.
- Interfaz adaptable a PC y pantallas angostas.
- Preparado para publicación en Render.

## Ejecución local
```bash
pip install -r requirements.txt
flet run --web main.py
```

## Publicar en Render
1. Subir la carpeta a GitHub.
2. En Render crear `New > Web Service`.
3. Runtime: Python.
4. Build command: `pip install -r requirements.txt`.
5. Start command: `python main.py`.
6. Crear el servicio.

## Base de datos
Actualmente SQLite para demostración (`data/megasoftire.db`).
Para producción multiusuario se recomienda PostgreSQL y almacenamiento persistente.
