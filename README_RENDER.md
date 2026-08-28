# MegaSoftire WEB 2026 - paquete listo para Render

## Archivos principales
- `main.py`: aplicación MegaSoftire.
- `database.py`: base SQLite de demostración.
- `requirements.txt`: dependencias Python/Flet.
- `render.yaml`: configuración automática para Render.
- `.gitignore`: excluye entorno local, cachés y base de datos local.

## Publicación recomendada: GitHub + Render

### 1. Crear repositorio en GitHub
1. Ingrese a https://github.com/ y cree una cuenta si aún no tiene una.
2. Cree un repositorio nuevo, por ejemplo `megasoftire-web`.
3. Suba **el contenido de esta carpeta**, no el ZIP como un único archivo.
   En la raíz del repositorio deben verse `main.py`, `database.py`, `requirements.txt` y `render.yaml`.

### 2. Crear el servicio en Render
1. Ingrese a https://render.com/ y conecte su cuenta de GitHub.
2. Cree un nuevo **Web Service** desde el repositorio `megasoftire-web`.
3. Render puede leer `render.yaml`. Si solicita los campos manualmente use:
   - Runtime: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
4. Use el plan gratuito si aparece disponible para su cuenta.
5. Pulse **Deploy / Create Web Service**.

### 3. Abrir MegaSoftire
Al finalizar el despliegue, Render asignará una URL parecida a:

`https://megasoftire-web.onrender.com`

Esta dirección se puede abrir desde Chrome, Edge o un navegador móvil sin instalar Python ni Flet en ese equipo.

## Acceso de demostración
- Usuario: `admin`
- Contraseña: `Admin2026!`

**Importante:** cambie estas credenciales antes de utilizar datos reales.

## Base de datos de esta versión
Esta versión conserva SQLite (`data/megasoftire.db`) para demostración. En un hosting sin disco persistente, los datos locales pueden perderse cuando el servicio se reinicia o se vuelve a desplegar. Para uso real multiusuario se debe migrar a PostgreSQL o añadir almacenamiento persistente.

## Cómo se adapta al puerto de Render
Render entrega el puerto mediante la variable de entorno `PORT`. `main.py` copia ese valor a `FLET_SERVER_PORT` y configura Flet como servidor Web en `0.0.0.0`.
