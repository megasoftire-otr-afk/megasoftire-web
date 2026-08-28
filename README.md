# MegaSoftire – primer prototipo Python + Flet para Windows

Base funcional para reconstruir el sistema FoxPro/DOS siguiendo el flujograma confirmado.

## Incluye
- Menú principal con 9 módulos.
- Base de datos SQLite local.
- Panel de situación.
- Registro de equipos.
- Registro maestro de neumáticos.
- Eventos: INST, DINS, REPA, INSP, INSC, INVE, ROT y BAJA.
- Historial por neumático.
- Validación inicial para evitar INSC duplicada por fecha y lectura.
- Estados: SERVICIO, STAND-BY, REPARACIÓN y BAJA.

## Ejecutar en Windows
1. Instalar Python 3.11 o superior.
2. Abrir PowerShell en esta carpeta.
3. Ejecutar:

   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   flet run main.py

La base se crea automáticamente en `data/megasoftire.db`.

## Próximos pasos
1. Completar reglas de FLT1110–FLT1190.
2. Importar los DBF históricos.
3. Agregar remanente, horas/mm, vida proyectada y costo/hora.
4. Construir reportes Excel.
5. Agregar usuarios, auditoría y respaldo.
6. Empaquetar como EXE para Windows.
