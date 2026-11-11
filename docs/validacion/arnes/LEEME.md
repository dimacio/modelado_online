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

## Scripts de los pasos C2, C3 y C5 (archivados)

- `c2-app.mjs` — maneja la app real (pestaña Descriptores) vía CDP sobre Edge headless;
  necesita un `http.server` sirviendo `app/index.html` y Edge con
  `--headless=new --remote-debugging-port=9222`.
- `gen_smiles_local.py` — SMILES canónicos de los SDF con RDKit CLI.
- `c2-comparar.py` — contraste descriptores de la app vs RDKit CLI.
- `c3-qsar.py` — modelos de 1–3 variables con R², Fisher y Student (scipy) y matriz de
  ortogonalidad, Partes A y B del TP 1.
- `c5-interacciones.py` — port exacto de `analizar()` de la pestaña Complejo; lee el
  receptor y las poses `*_webina.pdbqt` y produce los CSV por ligando y la tabla de
  doble entrada.

Los scripts apuntan a rutas absolutas del equipo donde corrieron (Drive y
`C:\Users\dimas\c2-work`); para reproducirlos, ajustar `PROJ`/`REC_PATH`/`AQUI` según
`MATERIALES_DIR` o una copia local.

## Prueba funcional de la app (TP remoto)

- `test-app.mjs` — corre la app real (servida con `servidor.py`, que da COOP/COEP) sobre
  Edge headless vía CDP y verifica de punta a punta: selector de la serie, CSV de
  descriptores (export e import), receptor 2B6A con la caja del TP, docking completo con
  descargas de poses y salida, complejo con tabla de interacciones y su CSV, y carga de
  poses desde archivo. Última corrida: 16/16 chequeos OK (NVP contra 2B6A, 24 s).

## Parches locales al motor (sólo en la copia de trabajo)

Para correr fuera del navegador, la copia de trabajo parchea `vina.1.0.5.js` en dos
puntos (ver `04-docking-serie.md`, sección "Cómo corrió"): el `can_block` del hilo
principal pasa a `false` (el valor que tiene en el navegador) y `___cxa_throw` registra el
tipo de excepción en consola (diagnóstico). Los archivos del repo no se modifican.
