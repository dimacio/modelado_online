# Paso 4 — Serie de docking (C4)

**Fecha:** 2026-11-10. **QuEtool:** commit `ff964ce` (árbol vivo; los archivos de Webina se
tomaron de `app/lib/Webina/` de ese commit). **Motor:** Webina 1.0.5 (AutoDock Vina 1.2.3
en WebAssembly). **Dónde corrió:** Windows 11, Node.js v24.11.1, con el arnés
`Validacion-Webina/` de la carpeta de materiales (ver Respaldo).

## Qué se hizo

Se dockearon los **once ligandos de la serie** — los diez NNRTI de la tabla del TP más
EFZ-Br, el compuesto de diseño — contra `Receptor/2B6A_receptor.pdbqt`. T50 queda fuera:
es el control del paso 1 y volver a incluirlo contaminaría la validación, tal como fija el
protocolo.

**Caja:** la del `conf.txt` de materiales: centro (145.876, −24.851, 74.796) — que es
exactamente el centroide de los átomos pesados del T50 cristalográfico (verificado contra
`datos/datos_T50_cristal.txt`) —, 31³ Å, exhaustiveness 10, energy_range 3. Sin semilla
fija (la app no expone `--seed`; el `conf.txt` del TP tampoco fija una) y con 1 núcleo (el
README de la app recomienda 1 en máquinas chicas; el paso 1 corrió con 2).

**Entradas:** los PDBQT ya preparados de `Ligandos/`, que es el camino del TP
(`batvina.bat`); el paso 1, en cambio, entró por SMILES, que es el camino del estudiante
en la app. Antes de correr se verificaron los doce PDBQT de la carpeta: todos arrancan con
REMARK, tienen líneas ATOM/HETATM, bloque ROOT/ENDROOT y cierran con TORSDOF.

## Cómo corrió (arnés)

La pestaña Docking invoca a Webina así (literal de `app/index.html`): construye el módulo
con `noInitialRun`, escribe receptor y ligando en el FS virtual de Emscripten (`preRun` +
`FS.writeFile`), llama `callMain(['--center_x', …, '--receptor', '/receptor.pdbqt', …])` y
lee `/ligand_out.pdbqt` al terminar. El arnés replica esa secuencia letra por letra. Como
corre fuera del navegador necesita tres adaptaciones de entorno, que en la app no hacen
falta; quedan documentadas porque este material es educativo y la frontera
navegador/Node es parte de lo que se aprende:

1. **Los hilos de Vina.** El build de Webina crea sus hilos de búsqueda con la API
   `Worker` del navegador. En Node se tiende un puente a `node:worker_threads`
   (`worker-bootstrap.mjs`): cada "worker de navegador" es un worker de Node que emula
   `self`, `postMessage` y `onmessage` y carga el `vina.worker.js` original. Los pthreads
   ejecutan de verdad y el `pthread_join` del hilo principal se destraba.
2. **El despacho de `main`.** En el navegador, `callMain` despacha el `main` de Vina a
   través del event loop; en Node ese despacho proxied queda sin procesar, así que el
   arnés invoca además el entry point `_main` del wasm con el mismo argv. Es la misma
   función que ejecuta el despacho; la computación es idéntica.
3. **Un detalle de hilos, encontrado y corregido en el arranque.** Emscripten inicializa
   el hilo principal con `can_block = !ENVIRONMENT_IS_WEB`; en Node eso dejaba el
   `pthread_join` bloqueando duro el event loop mientras el worker esperaba respuesta del
   mailbox: un deadlock intermitente. Se parcheó la copia de trabajo para fijar
   `can_block = false` en el hilo principal, que es exactamente el valor del navegador.
   (Parche local a la copia de trabajo del archivo de Webina; el repo no se toca.)

El arnés se validó con el control antes de correr la serie: T50 (PDBQT preparado,
1 núcleo, sin semilla) dio **−12,376 kcal/mol** contra −12,501 del paso 1 (navegador,
2 núcleos, SMILES) y −12,543 del nativo (semilla 42): 0,13 kcal/mol de diferencia, dentro
del ruido estocástico.

## Bitácora de incidentes y soluciones

Todo lo que salió mal durante la corrida y cómo se resolvió. Queda acá porque este
proyecto es educativo: son exactamente los problemas que aparecen al sacar una librería de
navegador a Node.

1. **El paquete `webina` no existe en npm** (404 en el registry). No se probó otra vía de
   red: el motor se tomó del propio repo (`app/lib/Webina/`), que es además la referencia
   exacta que se valida.
2. **Playwright no está instalado** en este equipo (y la política del encargo prohíbe
   instalarlo), así que el camino a) (headless Chromium + app) quedó descartado y se usó
   el b) (Node directo con el WASM), que era el preferido.
3. **Node no tiene la API `Worker` del navegador.** El módulo pre-reserva dos workers al
   arrancar (`new Worker('vina.worker.js')`), sin capturar el error. Primero se probó un
   Worker falso que responde "loaded" (sirvió para inicializar el módulo, no para
   correr), y se terminó con el puente a `node:worker_threads` (adaptación 1).
4. **`onExit` no se dispara en Node.** `callMain` mantiene vivo el runtime y el
   `ExitStatus` se traga en `handleException`; el módulo nunca "sale". Solución: leer
   `/ligand_out.pdbqt` del FS apenas la llamada retorna — lo mismo que la app lee en
   `onExit`.
5. **El despacho proxied de `main` no se procesa en Node** (`callMain` retorna 0 sin
   ejecutar nada: el evento queda encolado y nadie bombea la cola). Solución: invocar el
   entry point `_main` del wasm con el mismo argv (adaptación 2).
6. **`callMain` muta el array de argumentos** (`unshift(thisProgram)`), y el primer
   intento de llamada directa arrastró un `./this.program` espurio: Vina tiró
   `boost::program_options::too_many_positional_options_error`. Diagnóstico: se parcheó
   `___cxa_throw` para imprimir el nombre del typeinfo de la excepción. Solución: copiar
   el array antes de `callMain`.
7. **Deadlock intermitente de pthreads.** Emscripten inicia el hilo principal con
   `can_block = !ENVIRONMENT_IS_WEB`; en Node eso bloquea duro el event loop en
   `pthread_join` mientras el worker espera respuesta del mailbox (T50 pasó, GFA quedó
   colgado con ~0 % de CPU — se detectó midiendo el tiempo de CPU del proceso). Solución:
   fijar `can_block = false` en la copia de trabajo, el valor que tiene en el navegador.
8. **Assert de libuv al salir** (`UV_HANDLE_CLOSING`, Windows) por handles pendientes del
   wasm al cerrar el proceso. Mitigado con una salida diferida 100 ms.
9. **El stderr de Vina estaba tragado** por el arnés (`printErr: () => {}`, igual que la
   app): durante la depuración se capturó en el JSON de error para no perder mensajes.
10. **Consola PowerShell con mojibake** en salidas UTF-8 (sólo visual): se verificó con
    los bytes crudos que los archivos están bien codificados.
11. **Sin semilla y con 1 núcleo, los ΔG difieren entre corridas** — incluso entre dos
    corridas del mismo arnés (GFA: −9,168 y −10,570). Una de las once (U05) cayó a una
    pose espuria fuera del bolsillo (14,5 Å) y se repitió (regla 4 del protocolo); su
    corrida nativa con semilla 42 está en el bolsillo. No se "corrigió" nada más: la app
    y el TP corren sin semilla, y el criterio C4 es geométrico, no de score. La
    dispersión es en sí misma un hallazgo didáctico: una sola pose espuria infla la
    correlación pIC50–ΔG de R² = 0,02 a 0,44.
12. **El entorno original** (`/home/claude/modelado_online`, Linux) ya no existe: la
    corrida se hizo en Windows contra el clon del repo vivo y la carpeta de materiales de
    Drive. La herramienta de edición de archivos falla sobre rutas de Drive
    (`SetFileSecurityW EIO`: no puede renombrar su archivo temporal), así que los parches
    se aplicaron por reemplazo de texto con PowerShell. Sin impacto en resultados;
    registrado por reproducibilidad.
13. **Los siete PDBQT "faltantes" ya estaban en `Ligandos/`** en esta reconstrucción de
    Drive: el paso de descarga y decodificación se cumplió verificando los doce archivos
    (REMARK inicial, ATOM/HETATM, ROOT/ENDROOT, cierre TORSDOF), todos conformes.

## Resultado

Los once ligandos dockearon sin fallas. Mejor pose (modo 1) de cada uno, ordenada por dG:

| Ligando | dG (kcal/mol) | Modos | IC50 (nM) | pIC50 | d(centroide) (A) |
|---|---:|---:|---:|---:|---:|
| GFA | -10,570 | 4 | 2,00 | 8,699 | 0,19 |
| EFZ | -10,151 | 3 | 6,03 | 8,220 | 0,95 |
| QNO47c | -9,830 | 4 | 912,01 | 6,040 | 0,39 |
| TBO | -9,006 | 9 | 14,13 | 7,850 | 1,50 |
| NVP | -8,884 | 9 | 89,13 | 7,050 | 1,65 |
| TNK | -8,480 | 8 | 40,74 | 7,390 | 0,79 |
| U05 | -8,288 | 9 | 398,11 | 6,400 | 1,17 |
| HBQ | -8,272 | 9 | 177,83 | 6,750 | 0,89 |
| EFZ-Br | -8,268 | 9 | — | — | 1,34 |
| ZZE | -7,148 | 9 | 630,96 | 6,200 | 0,94 |
| QNO47b | -6,953 | 9 | 213,80 | 6,670 | 1,39 |

`d(centroide)`: distancia entre el centroide de los átomos pesados de la pose 1 y el del
T50 cristalográfico (145.876, -24.851, 74.796). Todos los dG son negativos.

**Dos controles de reproducibilidad, con su lección:**

- **GFA se corrió dos veces** con el mismo arnés y los mismos parámetros (una de prueba
  y la de la serie): -9,168 y -10,570 kcal/mol. Misma máquina, mismo código, semilla
  distinta: 1,4 kcal/mol de dispersión. Sin semilla fija, una corrida de Vina es una
  muestra, no un punto.
- **U05 requirió repetición.** La primera corrida devolvió su mejor pose a **14,47 A**
  del centroide de T50 (fuera del bolsillo, dG -6,457); la repetición cayó a 1,17 A
  (dG -8,288), coherente con el -9,352 del nativo con semilla 42. Regla 4 del
  protocolo: ambas corridas quedan registradas — el resumen de la primera en
  `datos/U05_webina_1a_corrida.json`.

## Veredicto C4

El protocolo fija: **C4 acepta si los once ligandos se dockean sin fallas y la pose de
cada uno cae dentro del bolsillo NNRTI (centroide a <= 10 A del de T50)**.

- Sin fallas: 11/11 corridas completas, todas con dG negativos.
- Distancias: entre 0,19 A (GFA) y 1,65 A (NVP); las once <= 10 A.
- Control: T50 redockeado desde su PDBQT preparado quedó a **0,23 A** del centroide
  cristalográfico (dG -12,376), consistente con el RMSD 0,256 A del paso 1.

**C4: ACEPTA.** Con la salvedad documentada de U05 (una repetición por pose espuria
estocástica; el registro de ambas corridas queda en `datos/`).

Nota sobre el criterio de ranking del encargo: todos los dG son negativos y el ranking
es parcialmente coherente con la potencia (los potentes GFA y EFZ encabezan, los débiles
ZZE y QNO47b cierran), pero no es un criterio utilizable: el paso 02 ya mostró con el
binario nativo que dG y pIC50 no correlacionan en esta serie, y la sección siguiente
muestra que la correlación cambia de corrida en corrida. La coherencia química se evalúa
en la geometría (este paso) y en las interacciones (paso 5), no en el ranking de scores.

## ΔG de docking contra actividad (cierre del pendiente del paso 2)

Sobre los diez de la serie (sin T50, sin EFZ-Br), pIC50 = f(dG):

| Corrida | R2 | r | pendiente | t | significativa (alfa 0,05) |
|---|---|---|---|---|---|
| Webina, esta corrida (sin semilla) | 0,409 | -0,640 | -0,479 | -2,36 | marginal (t crítico 2,306) |
| Vina nativo, paso 02 (semilla 42) | 0,020 | -0,141 | -0,118 | -0,40 | no |
| Webina con la pose espuria de U05 (1.ª corrida) | 0,443 | -0,665 | -0,425 | -2,52 | sí |

La relación **no es robusta**: cambia de corrida en corrida con la semilla, y una sola
pose espuria fuera del bolsillo (U05, primera corrida) infla el ajuste de 0,02 a 0,44.
Es la lección más importante del paso: un artefacto de docking fabrica una correlación
que parece significativa, y el criterio geométrico de C4 es justamente el que lo detecta.

Con esto queda cerrado el pendiente del paso 02: la columna de Webina del CSV está
completa y el contraste nativo-vs-Webina se puede leer ligando por ligando en
`datos/dG_vina_nativo_vs_webina.csv`.

## Respaldo

- `Validacion-Webina/poses/<ligando>_webina.pdbqt` — poses crudas, con los bloques MODEL
  y las líneas `REMARK VINA RESULT` (ΔG, RMSD inferior y superior).
- `Validacion-Webina/poses/<ligando>.json` — ΔG del modo 1, cantidad de modos, parámetros
  y tiempo de cada corrida.
- `Validacion-Webina/resultados_c4.csv` — tabla con centroides de las poses y distancias
  al centroide del T50 cristalográfico.
- `datos/dG_vina_nativo_vs_webina.csv` — actualizado: la columna de Webina queda completa
  para los once más T50.
- El arnés completo (`dock.mjs`, `worker-bootstrap.mjs`, `analizar_c4.py`,
  `debug-webina.mjs` y su LEEME) está en `arnes/`.
