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
