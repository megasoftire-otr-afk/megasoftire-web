# MegaSoftire Web — Desarrollo CAT 50 / NEXA

Esta versión toma PROYECTO2/NEXA como fuente oficial para el CAT 50.

## Mejoras incorporadas
- Migración única del CAT 50: no vuelve a borrar inspecciones nuevas en cada reinicio.
- CAT 50 CATERPILLA R1600H con posiciones 1 a 4 según NEXA.
- Neumáticos oficiales: 1376, 1362, 1378 y 1367.
- Marca/medida/diseño: GOODYEAR / 18.00-25 / SMO-5D.
- Historial inicial INST + INSP por neumático.
- Filtro por equipo en Neumáticos en servicio.
- Vista ampliada: posición, código, serie, marca, medida, diseño, horómetro, cocadas, presión y vida proyectada.
- Historial operativo conjunto por equipo.
- INSP/INSC conservan equipo y posición actuales para evitar alteraciones accidentales.

## Despliegue
Reemplazar en GitHub, como mínimo, `main.py` y `database.py`, hacer Commit y dejar que Render despliegue el último commit.
