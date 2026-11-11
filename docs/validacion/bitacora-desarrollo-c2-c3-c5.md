# Bitácora de desarrollo — Pasos C2, C3, C5 y C6

**Cuaderno de laboratorio** de la segunda etapa de la validación (descriptores, QSAR,
interacciones y cierre de la regresión). Mismo formato y propósito que
`bitacora-desarrollo-c4.md`: reconstrucción cronológica del razonamiento para la sección
"proceso de desarrollo" de la publicación.

**Fecha:** 2026-11-10. **Herramientas:** RDKit CLI 2026.09.1 (referente), scipy 1.16.3
(pruebas), la app QuEtool en Edge headless manejada por CDP (sin Playwright), y un port
Python del análisis de interacciones de la app.

## 1. Reconocimiento y decisiones de método

- El repo ya tenía `data/descriptores-gfn2-rdkit.csv`: descriptores de QuEtool para las 15
  TZD (Parte A). Para la serie NNRTI (Parte B) no había datos: había que producirlos con
  la app.
- **Sin RDKit en ningún Python, sin obabel.** El protocolo fija como referente el RDKit
  de línea de comandos: se instaló por pip (un intento, funcionó) y se usó también para
  generar los SMILES canónicos desde los SDF de materiales — el referente prepara las
  entradas, nunca produce lo que se valida.
- **Playwright sigue prohibido**, y la app necesita un navegador para correr GFN2. Se la
  manejó con Edge headless y el protocolo DevTools (CDP) hablado a pelo con el WebSocket
  nativo de Node (`arnes/c2-app.mjs`): sin instalar nada. La pestaña Descriptores no
  necesita las cabeceras COOP/COEP, así que alcanza un `http.server` común.
- Para C5 se **portó `analizar()` a Python** (`arnes/c5-interacciones.py`) con los
  umbrales literales de la app. La validación acá no es del visor 3D sino del criterio
  con el que la herramienta mide una interacción — que es lo que pide C5.

## 2. Incidentes y soluciones

1. **`python -I` escondía RDKit.** pip instaló el paquete en el user-site y el flag `-I`
   de la política lo desactiva. El script es del proyecto, así que se corrió sin `-I`
   (la regla aplica a archivos ajenos). Quedó anotado para no repetir la confusión.
2. **`"55.4Å²"` no parseaba**: Python considera al superíndice "²" un dígito
   (`isdigit()` es verdadero), así que el filtro de caracteres lo dejaba pasar. Solución:
   filtro ASCII explícito. Lección para estudiantes: los números con unidades no son
   números hasta que se define el contrato de parseo.
3. **El `npm install` de las librerías de la app, hecho dentro de Drive, saturó el
   cliente de sincronización**: las lecturas pasaron a ~24 s por archivo y los procesos
   quedaron en 0 % de CPU esperando E/S. Decisión: matar la instalación, borrar
   `node_modules` de Drive (no se sincronizan dependencias de Node a la nube) y mover el
   trabajo a disco local (`C:\Users\dimas\c2-work`). Las librerías npm quedaron
   descartadas del todo: RDKit CLI y la app headless cubren el paso. Lección de
   infraestructura: separar cómputo de sincronización.
4. **Consola cp1252 vs UTF-8** (de nuevo): un `Δ` en un `print` rompió la salida; se
   capturó todo con `PYTHONIOENCODING=utf-8`. Cosmético, registrado por trazabilidad.
5. **Multicolinealidad en el mejor modelo de dos variables** (masa + clogP, R² = 0,839):
   el coeficiente de masa no es significativo (t = −1,57) aunque el modelo global sí
   (F = 18,2). No es un error del procedimiento: es el caso de libro que el TP pide
   detectar con el análisis de ortogonalidad, y quedó documentado como tal.
6. **La anomalía del compuesto 11** (TZD): la tabla publicada trae μ = 0,012 y
   Eoop = 4,189 transpuestos; QuEtool le da un dipolo de 5,68 D. El contraste entre la
   tabla de la guía y los descriptores de la herramienta hace saltar el error solo, sin
   buscarlo. Eso es exactamente el tipo de lección que una herramienta educativa debe
   permitir.

## 3. Resultados

- **C2: ACEPTA.** Los cinco descriptores topológicos de la app coinciden con el RDKit CLI
  salvo redondeo de visualización (máx. |Δ| = 0,044) y el SCF de GFN2 convergió en los 11.
- **C3: ACEPTA.** Todos los modelos de 1–3 variables con R², Fisher y Student, y la matriz
  de ortogonalidad, para ambas partes del TP.
- **C5: ACEPTA.** Mapas de interacción para los 12 complejos: 86–100 % de los contactos en
  el sitio NNRTI bibliográfico; Tyr181/Tyr188 en todos.
- **C6: reportado** (sin criterio de aprobación, como fija el protocolo): la relación
  pIC50–ΔG no es robusta entre corridas; una pose espuria infla R² de 0,02 a 0,44.

Los artefactos crudos están en `docs/validacion/datos/` y los scripts en
`docs/validacion/arnes/`; los documentos numerados son `03-descriptores-qsar.md`,
`05-interacciones.md` y `06-regresion-dG.md`.
