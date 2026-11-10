# Bitácora de desarrollo — Validación C4 (serie de docking con Webina)

**Cuaderno de laboratorio.** Reconstrucción cronológica del razonamiento, las decisiones,
los callejones sin salida y las soluciones de la corrida C4. Es el insumo narrativo de la
sección "proceso de desarrollo" de la publicación, y está pensada para acentuar el valor
didáctico del proyecto: cada incidente tiene su lectura pedagógica (sección 9).

**Fecha de la corrida:** 2026-11-10 (zona America/Buenos_Aires). **Equipo:** Windows 11
Home 10.0.26200, Node.js v24.11.1, npm 11.6.2, git 2.49.0, gh CLI 2.100.0, Python 3.14.
**Repositorio bajo prueba:** [dimacio/modelado_online](https://github.com/dimacio/modelado_online),
commit `ff964ce`.

## 1. Estado inicial y decisión de alcance

El encargo pedía: (1) descargar y decodificar 7 PDBQT faltantes desde Drive, (2) verificar
los 12 archivos, (3) dockear los 11 ligandos (todos menos T50) contra
`2B6A_receptor.pdbqt` con Webina, (4) armar la tabla de ΔG y (5) documentar en
`docs/validacion/04-docking-serie.md` siguiendo el formato de `01-redocking-control.md`.

Dos decisiones de arranque, documentadas porque cambian el método:

- El entorno original (`/home/claude/modelado_online`, Linux) **ya no existe**. La
  reconstrucción de materiales vive en Drive (`G:\Mi unidad\QuEtool - materiales TP
  reconstruidos`) y el árbol vivo de la app está en GitHub. Se trabajó contra el clon del
  repo y contra esa carpeta de materiales.
- Los **7 PDBQT "faltantes" ya estaban** en `Ligandos/` (los 12 archivos presentes): el
  paso de descarga se cumplió por verificación, no por descarga. Esa es la única
  desviación respecto del encargo, y quedó asentada en el paso 4 (bitácora, ítem 13).

## 2. Localización de fuentes

1. En la carpeta de materiales: `Receptor/2B6A_receptor.pdbqt` (765 KB, 7894 átomos),
   `Ligandos/` (12 PDBQT), `Estructuras3D/` (los mismos en SDF), `conf.txt` (caja del
   sitio NNRTI) y `Validacion-Vina-nativo/` (corrida nativa de contraste en Colab, con el
   notebook y el CSV `dG_vina_nativo_vs_webina.csv`).
2. En Drive, la carpeta de la cátedra `Docencia/Quimica-Medicinal-FFyB/Software_online_química_computacional`
   contiene la **app QuEtool completa** (`app/index.html` + `app/lib/Webina/` con
   `vina.1.0.5.js`, `vina.worker.js`, `vina.wasm`).
3. El usuario indicó que el repo vivo es `dimacio/modelado_online`: se clonó y se
   confirmó que trae `docs/validacion/` con el protocolo (00), el redocking de control
   (01) y el contraste con Vina nativo (02), además de los datos crudos de esos pasos.

Lectura clave del protocolo: **C4 está pre-registrado** ("Acepta si los once ligandos se
dockean sin fallas y la pose de cada uno cae dentro del bolsillo NNRTI — centroide a
≤ 10 Å del de T50"). Es un criterio **geométrico**, no de score, y es el que se evalúa;
el "ranking químicamente coherente" del encargo se reporta como discusión, porque el paso
02 ya mostró con el binario nativo que ΔG y pIC50 no correlacionan en esta serie.

## 3. Verificación de insumos

Los doce PDBQT se verificaron con un chequeo estructural: primera línea REMARK, presencia
de ATOM/HETATM, bloque ROOT/ENDROOT y cierre `TORSDOF n` (o END). Los doce conformes,
entre 21 y 28 átomos y 1 a 9 torsiones activas. Se verificó también que el centro del
`conf.txt` (145.876, −24.851, 74.796) es **exactamente** el centroide de los 27 átomos
pesados del T50 cristalográfico (`datos/datos_T50_cristal.txt`), lo que convierte a ese
punto en la referencia del criterio C4.

## 4. Decisión de método: Node directo (camino b)

El encargo ofrecía dos caminos para correr Webina: (a) headless Chromium + la app, o (b)
Node.js directo con el WASM. La evidencia:

- **Playwright no está instalado** en este Windows (ni como módulo de Python ni como
  paquete global), y la política del encargo prohíbe instalarlo → camino (a) descartado.
- **El paquete `webina` no existe en npm** (404 del registry): el motor no se distribuye
  por esa vía. La fuente correcta es el repo de la app, que trae el build exacto que corre
  QuEtool → se copiaron los archivos de `app/lib/Webina/` a la carpeta de trabajo.
- La app además **no acepta ligandos PDBQT**: su pestaña Docking genera el PDBQT desde
  SMILES. El encargo pide dockear los PDBQT preparados (el camino del TP), así que el
  camino (b) es el único que respeta la consigna.

Decisión: arnés propio en Node que replica letra por letra la invocación de la app.

## 5. El motor

`vina.1.0.5.js` es un módulo ES de Emscripten (Vina 1.2.3 → WebAssembly) con pthreads,
pensado para navegador: al arrancar pre-reserva workers (`new Worker('vina.worker.js')`)
y su `callMain` despacha el `main` de Vina a través de un mecanismo proxied que en el
navegador resuelve el event loop. La app lo usa así (literal de `app/index.html`):

```js
const mod = new WEBINA({
  noInitialRun: true,
  locateFile: (p) => 'lib/Webina/' + p,
  preRun: [function (This) {
    This.FS.writeFile('/receptor.pdbqt', receptorTxt);
    This.FS.writeFile('/ligand.pdbqt', ligando);
    iniciado = This;
  }],
  print: (t) => { stdout += t + '\n'; },
  printErr: () => {},
  onExit: () => { /* FS.readFile('/ligand_out.pdbqt') */ },
});
Promise.resolve(mod).then((m) => (m && m.ready) ? m.ready : m).then((m) => {
  const args = []; for (const [k, v] of Object.entries(params)) args.push('--' + k, String(v));
  args.push('--receptor', '/receptor.pdbqt', '--ligand', '/ligand.pdbqt', '--out', '/ligand_out.pdbqt');
  m.callMain(args);
});
```

Parámetros: caja de `conf.txt`, `exhaustiveness 10`, `energy_range 3`, sin `--seed` ni
`--num_modes` (defaults de Vina: semilla aleatoria, 9 modos). Núcleos: 1 (el README de la
app recomienda 1 en máquinas chicas; el paso 1 corrió con 2).

## 6. El arnés, iteración a iteración

### 6.1 `Worker is not defined`

Primer intento de carga en Node: `ReferenceError: Worker is not defined` en
`allocateUnusedWorker` (el módulo pre-reserva dos workers al arrancar, sin try/catch).
Primera solución: un shim `globalThis.Worker` mínimo que responde `loaded` al mensaje de
carga del módulo. El módulo inicializa, la promesa `ready` resuelve… y la corrida se
cuelga.

### 6.2 El módulo inicializa pero nadie "sale"

Con el shim, `callMain` retornaba 0 sin ejecutar nada, `onExit` nunca se disparaba y el
proceso moría con "unsettled top-level await". Dos hallazgos, en este orden:

- **`onExit` no existe en Node para este build.** `callMain` hace
  `runtimeKeepalivePush()` y el `ExitStatus` se traga en `handleException`: el runtime
  queda vivo y no "sale". Solución: leer `/ligand_out.pdbqt` del FS apenas la llamada
  retorna (lo mismo que la app lee en `onExit`).
- **El despacho proxied de `main` no se procesa en Node.** `callMain` encola el `main` en
  el hilo de runtime y retorna 0; en el navegador el event loop bombea la cola, en Node
  no hay quién. Solución: invocar el entry point `_main` del wasm directamente, con un
  `argv` construido a mano (asignación en la pila con `stackAlloc` — el export minificado
  `ca` — y vistas `Uint8Array`/`Uint32Array` sobre `wasmMemory.buffer`).

### 6.3 `too_many_positional_options_error`

La llamada directa a `_main` imprimió el banner de Vina y lanzó una excepción C++ sin
atrapar. Para identificarla se parcheó `___cxa_throw` en la copia de trabajo para decodificar
el nombre del typeinfo desde la memoria del wasm: `boost::wrapexcept<boost::program_options::too_many_positional_options_error>`.
Causa raíz: **`callMain` muta el array de argumentos** (`args.unshift(thisProgram)`) y el
mismo array se reutilizaba para la llamada directa, dejando un `./this.program` espurio
como argumento posicional. Solución: copiar el array antes de `callMain`.

### 6.4 Deadlock intermitente de pthreads

Con el argv corregido, T50 corrió completo (61 s, −12,376 kcal/mol) pero GFA quedó
colgado: ~7 s de CPU en 13 minutos de pared → bloqueo, no cómputo. Causa: Emscripten
inicializa el hilo principal con `can_block = !ENVIRONMENT_IS_WEB`; en Node eso vale
`true`, el `pthread_join` del hilo principal bloquea duro el event loop y el worker queda
esperando respuesta del mailbox. En el navegador `can_block = false` y el join es
asíncrono con el event loop vivo. Solución: parchear `___emscripten_init_main_thread_js`
en la copia de trabajo para fijar `can_block = false` (el valor del navegador). Con ese
parche, los hilos de Vina corren sobre `node:worker_threads` a través de
`worker-bootstrap.mjs`, que emula `self`/`postMessage`/`onmessage` y carga el
`vina.worker.js` original.

### 6.5 Control previo a la serie

Con el arnés estable se redockeó T50 desde su PDBQT preparado: **−12,376 kcal/mol, 6
modos, 61 s** contra −12,501 del paso 1 (app en navegador, 2 núcleos, SMILES) y −12,543
del nativo (semilla 42). Diferencia de 0,13 kcal/mol: ruido estocástico. Arnés validado.

## 7. La serie

Los once ligandos, en orden: GFA, EFZ, TBO, TNK, NVP, HBQ, QNO47b, U05, ZZE, QNO47c,
EFZ-Br. Un proceso de Node por ligando (como una carga de página de la app por docking),
parámetros idénticos, salidas a `poses/<ligando>_webina.pdbqt` + `<ligando>.json`.
Tiempos entre 26 s (NVP) y 161 s (ZZE), acordes con el número de torsiones.

| Ligando | dG (kcal/mol) | Modos | Tiempo (s) |
|---|---:|---:|---:|
| GFA | -10,570 | 4 | 123 |
| EFZ | -10,151 | 3 | 41 |
| TBO | -9,006 | 9 | 39 |
| TNK | -8,480 | 8 | 131 |
| NVP | -8,884 | 9 | 26 |
| HBQ | -8,272 | 9 | 38 |
| QNO47b | -6,953 | 9 | 109 |
| U05 | -8,288 (repetición) | 9 | 43 |
| ZZE | -7,148 | 9 | 159 |
| QNO47c | -9,830 | 4 | 87 |
| EFZ-Br | -8,268 | 9 | 58 |

Serie completa en ~14 minutos (más una repetición de U05, ~44 s). Los tiempos siguen el
número de torsiones activas (ZZE 9, TNK 7 contra NVP 1), como corresponde a la
dimensionalidad de la búsqueda.

## 8. Análisis del criterio C4

`analizar_c4.py` toma el MODEL 1 de cada salida, calcula el centroide de sus átomos
pesados y lo compara con el del T50 cristalográfico (145.876, −24.851, 74.796). El
veredicto y la tabla están en `04-docking-serie.md`.

## 9. Lectura didáctica de cada incidente

Cada callejón sin salida de la sección 6 es, de hecho, un tema de la materia:

1. **`Worker is not defined`** → qué es un worker del navegador, qué es
   `node:worker_threads`, y por qué un build para navegador no es portable por sí solo.
   Materializa la diferencia "JS de navegador vs JS de servidor" que el TP sólo nombra.
2. **El event loop y el despacho proxied de `main`** → por qué Emscripten no puede llamar
   a `main()` directamente en un build con pthreads, y qué papel juega el event loop del
   navegador en la orquestación de hilos. Es la misma idea que estudia el alumno en
   "cómo funciona una página", pero con un motor de docking adentro.
3. **`too_many_positional_options_error`** → sintaxis de línea de comandos, argumentos
   posicionales vs nombrados, y el riesgo silencioso de mutar estructuras compartidas
   (un bug clásico de programación, en un contexto químico real).
4. **Decodificar una excepción C++ desde el typeinfo** → cómo se identifica un error
   cuando el binario no trae símbolos: ABI de Itanium, nombres mangling, punteros en la
   memoria del wasm. Excelente ejercicio de "pensar en bytes".
5. **El deadlock de `can_block`** → concurrencia de verdad: join, mailbox, `Atomics.wait`
   contra event loop, y el diagnóstico por tiempo de CPU ("bloqueado vs calculando").
   Es la lección de hilos más honesta que puede dar un TP: pasó en producción, con un
   docking real.
6. **Estocasticidad sin semilla** → por qué dos corridas del mismo ligando dan ΔG
   distintos (GFA: −9,168 y −10,570, ambas de este arnés), por qué una corrida de U05
   cayó fuera del bolsillo y hubo que repetirla (regla 4 del protocolo), y por qué el
   criterio de aceptación C4 es geométrico y no de score. Conecta con la discusión del
   TP sobre qué significa "validar" un modelo, y deja el ejemplo perfecto de correlación
   espuria: la pose errónea de U05 inflaba la regresión pIC50–ΔG de R² = 0,02 a 0,44.

## 10. Trazabilidad y auditoría

Cómo se audita este proceso, de más a menos "crudo":

1. **Artefactos crudos**, en `docs/validacion/datos/`: las poses PDBQT completas (con las
   líneas `REMARK VINA RESULT`), los JSON por ligando (ΔG, modos, parámetros, tiempos) y
   `resultados_c4.csv`. Cualquier conclusión de `04-docking-serie.md` se puede recalcular
   desde acá.
2. **El arnés**, en `docs/validacion/arnes/`: el código exacto que produjo los archivos
   anteriores. Correrlo de nuevo contra los mismos materiales reproduce la serie.
3. **Esta bitácora** y los documentos numerados del protocolo (00–04): el razonamiento,
   con fechas y commits.
4. **El historial de git** del repo: cada artefacto entra en un commit con fecha; el
   orden de los commits es la línea de tiempo del desarrollo.
5. **La conversación con el asistente** queda en el historial de la sesión de DeepSeek
   Harness (GUI local); no se puede exportar desde el asistente, por eso los puntos 1–4
   son la fuente auditada: todo lo que se afirma acá tiene su archivo en el repo.

**Regla del proyecto (protocolo 00):** "lo que diga 'se verificó' tiene que tener su
archivo". Esta bitácora cumple la misma regla para el proceso: cada iteración de la
sección 6 dejó su rastro (logs de consola capturados en la conversación, estados
intermedios del arnés, y el resultado final reproducible).
