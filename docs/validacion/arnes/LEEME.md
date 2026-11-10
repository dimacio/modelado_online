# Arnés de la validación C4 — Webina desde Node.js

Copia archivada del arnés con el que se corrió el paso 4. La copia de trabajo vive en la
carpeta de materiales de Drive (`QuEtool - materiales TP reconstruidos/Validacion-Webina/`),
donde el receptor, los ligandos y el `conf.txt` están un nivel arriba; esta copia sirve
para leer y reproducir.

## Para reproducir

1. El motor (Webina 1.0.5) se toma de `app/lib/Webina/` de este mismo repo; no hay que
   bajar nada.
2. Los materiales van en una carpeta que contenga `Receptor/2B6A_receptor.pdbqt`,
   `Ligandos/*.pdbqt` y `conf.txt`; se la indica con la variable de entorno
   `MATERIALES_DIR` (si no, se asume un nivel arriba del arnés).
3. `node dock.mjs <ligando> [carpeta_salida]` dockea un ligando; por defecto escribe las
   poses (`<ligando>_webina.pdbqt`) y el resumen (`<ligando>.json`) en `poses/`.
4. `python -I analizar_c4.py` evalúa el criterio C4 (centroide de cada pose contra el del
   T50 cristalográfico) y escribe `resultados_c4.csv`.

## Parches locales al motor (sólo en la copia de trabajo)

Para correr fuera del navegador, la copia de trabajo parchea `vina.1.0.5.js` en dos
puntos (ver `04-docking-serie.md`, sección "Cómo corrió"): el `can_block` del hilo
principal pasa a `false` (el valor que tiene en el navegador) y `___cxa_throw` registra el
tipo de excepción en consola (diagnóstico). Los archivos del repo no se modifican.
