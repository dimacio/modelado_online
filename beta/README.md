# BetaTools — canal de pruebas

Esta carpeta es **BetaTools**: la misma aplicación que BetaTools (`app/`), pero donde se
estrena cada funcionalidad antes de que pase a la versión estable. Lo que está acá puede
cambiar o romperse; lo que la cátedra usa es `app/`.

Queda publicada aparte, en <https://dimacio.github.io/modelado_online/beta/>.

**Lo que hoy tiene BetaTools y BetaTools no:** la pestaña Complejo lee los `.dlg` de
AutoDock 4 / AutoDock-GPU con sus clusters, dibuja la caja de docking y permite cargar
varios ligandos a la vez. Está documentado abajo, en «Complejo».

Una sola página, sin instalación. Las librerías se bajan de jsDelivr, así que alcanza con
servir `index.html` desde cualquier servidor estático.

## Abrirla

**Publicada en GitHub Pages.** En el repositorio, Settings → Pages → Source: `main`, carpeta
raíz. Queda en `https://dimacio.github.io/modelado_online/app/`.

**O localmente**, con `servir.bat` (doble clic) o:

```bash
python3 servidor.py 8000
```

`servidor.py` no es `python -m http.server`: además emite las cabeceras COOP y COEP, que son las
que habilitan `SharedArrayBuffer`. Sin ellas AutoDock Vina no arranca. Los descriptores funcionan
igual con o sin cabeceras, y por eso la página también anda en GitHub Pages.

No alcanza con hacer doble clic en el archivo: abierto como `file://` el navegador bloquea la
carga de módulos.

## Qué hace

SMILES → confórmero 3D → MMFF94 → GFN2-xTB → descriptores, todo en la pestaña. Cada cálculo se
acumula en una tabla que se exporta como CSV.

Incluye un editor de estructuras 2D (OpenChemLib) conectado al campo de SMILES en los dos
sentidos, y un visor de la geometría 3D optimizada (3Dmol.js), que se puede rotar con el mouse.

El dibujo es en 2D, como en cualquier editor químico. La estructura tridimensional no se dibuja:
se genera a partir del dibujo con un generador de confórmeros y se minimiza con el campo de
fuerzas MMFF94. La pestaña "Geometría 3D" muestra el resultado, con su energía.

## Optimización con GFN2

Con la casilla "Optimizar la geometría con GFN2" el cálculo no se queda en MMFF94: hace una
optimización completa a nivel GFN2-xTB y recién después calcula los descriptores electrónicos.
Cuesta entre quince y veinte segundos por molécula, contra menos de tres sin ella, así que viene
apagada.

El optimizador es un L-BFGS escrito en la página, con búsqueda de línea de Armijo, porque el
módulo de optimización que trae la librería solo envuelve Hartree-Fock y DFT. Converge cuando la
mayor componente de la fuerza baja de 10⁻³ Ha/Bohr.

La vista cambia sola a "Geometría 3D" y **la relajación se dibuja paso a paso**, con el número de
paso, la energía acumulada y la fuerza máxima. El encuadre se fija en el primer cuadro y se vuelve
a ajustar al final, para que la molécula no salte en cada iteración.

Los dos parámetros del optimizador son editables: **pasos máximos** y **umbral de fuerza**
(|F|max en Ha/Bohr). Bajar el umbral da una geometría más relajada a cambio de más iteraciones.

## Taller de geometría

Debajo del visor 3D hay una barra para manipular la estructura y ver cómo responde:

- **Clic en un átomo** lo selecciona; los botones X±, Y± y Z± lo desplazan la distancia indicada.
- **Distorsionar** corre todos los átomos esa distancia en direcciones al azar.
- **Reoptimizar** relaja la geometría actual con GFN2, animando cada paso.

La distorsión está acotada: si una combinación al azar comprime un enlace más de un 12 % o deja
dos átomos a menos de 0,95 Å, se descarta y se reintenta con menos amplitud. Por debajo de eso el
campo autoconsistente de GFN2 no converge, y el error que da es poco informativo.

## Sobre cuánto se mueven los átomos

Poco, y es lo esperable. Una optimización es una bajada al mínimo local más cercano: relaja
distancias y ángulos, pero no cambia de confórmero. Para explorar confórmeros distintos hace falta
un muestreo, que hoy no está: `getOneConformerAsMolecule` devuelve siempre el mismo confórmero,
el de las torsiones más probables, y la semilla del generador no lo cambia. Comprobado con cinco
semillas: dipolo idéntico hasta la segunda decimal.

Para muestrear de verdad habría que usar la API de conformeros de OpenChemLib con una de las
estrategias `STRATEGY_*` e iterar, y después decidir si se toma el de menor energía o un promedio
de Boltzmann. Es una decisión de diseño pendiente y tiene peso pedagógico.

## Docking

La pestaña de docking hace la cadena completa: toma el SMILES, genera el confórmero, lo optimiza
con MMFF94, lo pasa a PDBQT con OpenBabel agregando hidrógenos a pH 7,4 y árbol de torsiones, y
lo dockea con AutoDock Vina contra el receptor elegido. Devuelve la tabla de poses con su
ΔG<sub>dock</sub> y el PDBQT descargable.

Viene un receptor de ejemplo, la proteasa de HIV (4LL3), y se puede subir cualquier `.pdbqt`.

**El campo de núcleos importa.** En WebAssembly el pool de hilos rinde peor que un solo hilo en
máquinas chicas: con el valor sin fijar, un docking que tarda 8 segundos con un núcleo puede
pasar de media hora. Si va lento, bajalo a 1.

Esta pestaña **solo funciona con `servidor.py`**, no en GitHub Pages: Vina usa
`SharedArrayBuffer`, que exige las cabeceras COOP y COEP.

## Complejo: poses, clusters y resultados de AutoDock

La pestaña muestra una pose dentro de la proteína y mide sus interacciones. Las poses pueden
venir de tres lados: del docking que se acaba de correr, de un `.pdbqt` de Vina, o de un
**`.dlg` de AutoDock 4 / AutoDock-GPU** corrido afuera —en una GPU, por ejemplo—.

Del `.dlg` salen además los **clusters**. El archivo trae el agrupamiento de AutoDock a 2,0 Å
—su valor por omisión—, que es grueso: junta poses distinguibles e infla la población del
primer cluster. La pestaña reagrupa a **1,0 Å** con el mismo algoritmo (RMSD de átomos
pesados, sin realinear), que es el criterio del proyecto de docking, para que la herramienta y
el ranking hablen del mismo número. La tabla de clusters da, de cada uno, el ΔG del mejor miembro, el
ΔG medio, cuántas corridas cayeron ahí y qué porcentaje del total son. Un clic en una fila lleva
a la mejor pose de ese cluster.

Un ΔG bajo con población baja es una pose que apareció una sola vez; la población es la que dice
si la búsqueda convergió. Por eso la tabla muestra las dos cosas juntas.

Tres modos de vista:

- **Pose** — una pose con sus interacciones, como siempre.
- **Cluster** — la pose elegida más el resto de su cluster en palos finos. Se ve de un vistazo
  si el cluster es compacto o si agrupó cosas distintas.
- **Representantes** — la mejor pose de cada cluster, cada una de un color (diez colores; del
  undécimo en adelante, gris). Es la vista del docking ciego: muestra en qué partes de la
  proteína cayeron las familias de poses.

**Qué cluster es «el» cluster.** El ranking de AutoDock ordena por energía, así que su
cluster 1 puede ser una pose que apareció una sola vez. La pestaña marca —y abre en— el que
elige el criterio del proyecto: **población de al menos el 10 % de las corridas y, entre los
que lo cumplen, el de menor ΔG**. Cuando los dos no coinciden, la tarjeta lo dice.

**RMSD contra el cristal.** Si la corrida llevó `--xraylfile`, el `.dlg` trae el ligando
cristalográfico entero y la columna *Reference RMSD*, que AutoDock calcula corrigiendo por
simetría. La pestaña muestra ese número —no lo recalcula— y dibuja el cristal sobre la pose.
Un redocking de control acepta con ≤ 2 Å. Si el `.dlg` no trae referencia, no se muestra
nada: esa columna mediría contra la geometría de entrada y no significaría nada.

Se pueden cargar **varios archivos a la vez** y pasar de uno a otro con el selector de arriba:
el mismo ligando en distintas cajas, o con distintas cargas parciales.

El receptor se carga desde esta misma pestaña, porque el de la pestaña Docking no tiene por qué
ser el de estas poses. Si una pose no da ninguna interacción, la app mide su distancia al
receptor y avisa cuando no se tocan: es el síntoma de haber cargado el receptor equivocado, o de
una caja puesta en otro lado.

Todo se lee en la máquina: los archivos no salen del navegador.

## Terminar el TP de forma remota

Primera implementación pensada para alumnos que no pudieron terminar el TP con la versión
anterior y lo retoman a distancia:

- **Selector de la serie.** En Descriptores, "Estructura de la serie del TP" carga en el
  campo SMILES cualquiera de las doce estructuras: los diez NNRTI (GFA, EFZ, TBO, TNK,
  NVP, HBQ, QNO47b, U05, ZZE, QNO47c), T50 (control cristalográfico) y EFZ-Br (compuesto
  de diseño).
- **Cargar y descargar por etapa.** Descriptores: la tabla Serie se descarga como CSV y se
  recarga con "Cargar CSV". Docking: "Descargar PDBQT de poses" y "Descargar salida
  completa" (parámetros + log de Vina, listo para el informe). Complejo: se cargan poses
  de archivo y la tabla de interacciones se baja como CSV. Los archivos son el estado:
  nada se guarda en la nube.
- **Receptor 2B6A con la caja del TP.** En Docking, elegir "Transcriptasa reversa de
  HIV-1 (2B6A) — TP" carga el receptor y deja la caja con los parámetros del `conf.txt`
  de la cátedra (centro en el sitio NNRTI, 31 Å de lado, exhaustiveness 10).

**Cómo se usa.** En la versión publicada, un *service worker* agrega las cabeceras
COOP/COEP que el docking necesita (por eso la primera vez la página se recarga sola);
donde los service workers estén bloqueados (ventana privada de Firefox, políticas
corporativas), abrila localmente con `servir.bat` o `python servidor.py 8000`. Completá
las tres pestañas y guardá el CSV de descriptores, los PDBQT de poses y el CSV de
interacciones. Para retomar en otra máquina o sesión se vuelven a cargar esos archivos.

La validación completa de la herramienta contra el TP (protocolo pre-registrado, pasos
C1–C6, datos crudos y bitácoras) está en
[`docs/validacion/`](../docs/validacion/00-protocolo.md).
