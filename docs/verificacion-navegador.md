# Verificación en navegador

Medido el 6 de noviembre de 2026, Chromium vía Playwright, página servida localmente con
cabeceras `Cross-Origin-Opener-Policy: same-origin` y `Cross-Origin-Embedder-Policy: require-corp`.

## Aislamiento y carga

| | |
|---|---|
| `SharedArrayBuffer` disponible | sí |
| `crossOriginIsolated` | `true` |
| OpenChemLib (registro de recursos) | 32 ms |
| RDKit MinimalLib 2026.09.2 | 198 ms |
| occjs (WASM + data) | 244 ms |

Los tiempos de carga corresponden a servido local; sobre red hay que sumar la transferencia de
unos 40 MB (25 MB de `occjs.wasm`, 8,4 MB de `occjs.data`, 7,1 MB de `RDKit_minimal.wasm`).

## Cadena completa, dentro de la página

| | Efavirenz | TZD 1 |
|---|---|---|
| Átomos | 30 | 31 |
| SMILES → 3D + MMFF94 | 2,71 s | 1,66 s |
| GFN2 punto simple | 543 ms | 344 ms |
| Descriptores RDKit | 116 ms | 4 ms |
| E(MMFF94) [kcal/mol] | 39,261 | −14,548 |
| E(GFN2) [Ha] | −64,337 | −59,006 |
| SCF convergido | sí | sí |
| HOMO [eV] | −11,385 | −10,183 |
| LUMO [eV] | −7,633 | −7,404 |
| Dipolo [D] | 3,354 | 2,189 |
| clogP | 3,613 | 4,361 |
| Refractividad molar | 68,845 | 80,919 |

Heap de JavaScript tras ambos cálculos: 48 MB.

## Gradiente

`XtbCalculator.gradient()` devuelve la matriz 3×N (3×30 y 3×31 respectivamente), de modo que la
optimización de geometría con GFN2 es alcanzable desde JavaScript. El módulo `optimization.js`
que trae la librería solo envuelve HF y DFT, así que el bucle optimizador hay que escribirlo.

## Nota sobre los dipolos

Estos valores son de punto simple sobre geometría MMFF94, no sobre geometría optimizada con GFN2.
Son menores que los de la cadena con optimización completa (5,56 D y 4,19 D respectivamente).
La diferencia no es un error: es la dependencia conformacional del dipolo, que en este proyecto
es además contenido pedagógico. Ver la sección correspondiente de `fundamentos-y-analisis.md`.

---

# Docking en el navegador (Webina)

[Webina](https://github.com/durrantlab/webina) 1.0.5, Apache-2.0, es AutoDock Vina **1.2.3**
compilado a WebAssembly. El TP usa Vina 1.2.7, así que hay una diferencia de versión a declarar.

## Interfaz

```js
Webina.start(vinaParams, receptorPDBQTTxt, ligandoPDBQTTxt, onDone, onError, baseUrl)
```

Recibe receptor y ligando **como texto**, no como rutas de archivo, porque el navegador no puede
leer el sistema de archivos. Eso encaja directo con la salida del pipeline: no hace falta pasar
por disco.

`vinaParams` acepta todos los parámetros del `conf.txt` del TP: `center_x/y/z`, `size_x/y/z`,
`exhaustiveness`, `energy_range` y los seis pesos de la función de scoring, más `cpu`, `seed` y
`num_modes`. El único que no toma es `spacing`, que de todos modos no es un parámetro de Vina 1.2
sino de AutoDock4, y Vina lo ignora.

`onDone(salida, stdout, stderr)` devuelve el PDBQT con las poses, con sus líneas
`REMARK VINA RESULT`, y la salida estándar de Vina.

## Tamaño

| Archivo | Tamaño |
|---|---|
| `vina.wasm` | 640 KB |
| `vina.js` | 93 KB |
| `vina.worker.js` | 2 KB |

Prácticamente no mueve la aguja frente a los 40 MB del resto del stack.

## Medición

Receptor 4LL3 (proteasa de HIV, 148 KB) con darunavir, en el contenedor de pruebas, que tiene
2 núcleos:

| Exhaustiveness | CPU | Tiempo | Mejor pose | Poses |
|---|---|---|---|---|
| 4 | 1 | 80 s | −9,343 kcal/mol | 9 |
| 10 | 4 | 96 s | −9,872 kcal/mol | 9 |

Con los parámetros del TP, unos 96 s por ligando sobre 2 núcleos. Los 11 ligandos de la serie
dan alrededor de 18 minutos en este hardware, y menos en una notebook con más núcleos. Es
aceptable para un práctico, sobre todo porque corre desatendido.

## Lo que Webina además trae

- `src/pdbqt_convert/openbabel.wasm` (2,9 MB): **OpenBabel compilado a WebAssembly**, con su
  licencia aparte. Resuelve la conversión a PDBQT y, por `--gen3d`, es una alternativa para la
  generación de coordenadas 3D.
- `src/mol_editor/libs/kekule`: Kekule.js como editor 2D.
- Visualización de poses y selección de la caja de docking con 3Dmol.js, que cubre el requisito
  de captura de pantalla del informe de TP.

## Trampa de integración

La carpeta `dist/` está en el `.gitignore` del proyecto, así que el repositorio no trae binarios
listos: hay que tomar los cuatro archivos de `src/Webina/`. Y `vina.worker.js` importa
`./vina.1.0.5.js` con el nombre escrito a mano, que es como el script de build renombra a
`vina.js`. Con cualquier otro nombre el worker no carga, el hilo principal espera indefinidamente
y no se emite ningún error: el proceso queda en 0 % de CPU. Conviene dejarlo documentado porque
el síntoma no apunta a la causa.
