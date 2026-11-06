# Aplicación

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
