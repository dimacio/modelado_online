# modelado_online

Software para hacer modelado molecular y dar prácticas en línea.

Corre entero en el navegador. No hay nada que instalar, no hace falta licencia y funciona en
cualquier sistema operativo, incluso en computadoras administradas donde no se puede instalar
software.

Permite dibujar una estructura o ingresarla como SMILES, generar su geometría en 3D, optimizarla,
calcular descriptores fisicoquímicos y electrónicos, hacer docking contra un receptor y ajustar
modelos QSAR con su análisis estadístico.

Está pensado para los trabajos prácticos de Química Medicinal (FFyB-UBA), pero sirve para
cualquier curso que necesite estas herramientas.

**Probalo en línea:** <https://dimacio.github.io/modelado_online/> — el landing en la
raíz, la aplicación en [`app/`](https://dimacio.github.io/modelado_online/app/), sin
instalar nada.

## Estado

Aplicación en uso, verificada de punta a punta dentro de un navegador real. Tiene tres pestañas:

- **Descriptores** — dibujo 2D, geometría 3D, minimización GFN2-xTB con los átomos moviéndose en
  pantalla, arrastre de átomos con el mouse y descriptores fisicoquímicos y electrónicos. La cadena
  SMILES → conformero 3D → MMFF94 → GFN2-xTB → descriptores tarda unos tres segundos por molécula.
- **Docking** — AutoDock Vina compilado a WebAssembly, con preparación del ligando a pH 7,4. Una
  corrida con *exhaustiveness* 8 y un núcleo tarda entre diez y quince segundos.
- **Complejo** — la pose dentro de la proteína y un mapa de interacciones (puente de hidrógeno,
  hidrofóbica, π–π, halógeno y puente salino) medido sobre la geometría, con tabla exportable a CSV.
  Los criterios geométricos están escritos en la propia pestaña.

## Los dos canales

| | Qué es | Dónde |
|---|---|---|
| **QuEtool** | la versión estable, la que usa la cátedra | [`app/`](https://dimacio.github.io/modelado_online/app/) |
| **BetaTools** | el canal de pruebas: estrena cada funcionalidad antes de que pase a QuEtool | [`beta/`](https://dimacio.github.io/modelado_online/beta/) |

Las dos salen del mismo repositorio y se publican en el mismo sitio, en carpetas distintas;
el landing de la raíz lleva a cualquiera de las dos. Una funcionalidad nueva se escribe en
`beta/`, se usa, y recién después se copia a `app/`.

**Lo que hoy tiene BetaTools y QuEtool no:** la pestaña Complejo lee los `.dlg` de AutoDock 4 /
AutoDock-GPU **con sus clusters** —reagrupados a 1,0 Å, no con los 2,0 Å por omisión que trae el archivo—
(tabla de población, cluster superpuesto, representantes de cada cluster), dibuja la caja de
docking leída del propio `.dlg`, muestra el **RMSD contra el
ligando cristalográfico** y lo dibuja cuando el `.dlg` trae referencia, **elige el cluster
pesando energía y población** —y no energía sola, que es lo que hace el ranking de AutoDock—
y permite cargar varios ligandos a la vez. Validado en [`docs/validacion/07-dlg-clusters.md`](docs/validacion/07-dlg-clusters.md).
Además tiene un **mapa de contactos** que pone un ligando por fila y un residuo por columna, y
en cada celda cuenta en cuántas poses del cluster aparece el contacto —lo que distingue un
contacto sostenido de uno que salió una sola vez—, con CSV para bajar. Validado en
[`docs/validacion/08-mapa-contactos.md`](docs/validacion/08-mapa-contactos.md).

Las mediciones están en `docs/verificacion-navegador.md`; la validación completa contra el
TP, paso a paso y con sus datos crudos, está en [`docs/validacion/`](docs/validacion/00-protocolo.md).

## Validación

La herramienta se validó contra el TP de la cátedra con un protocolo **escrito antes de
correr nada** —los criterios quedaron pre-registrados en
[`docs/validacion/00-protocolo.md`](docs/validacion/00-protocolo.md)— y cada paso dejó sus
datos crudos y su código en `docs/validacion/datos/` y `docs/validacion/arnes/`:

| Paso | Qué se validó | Criterio | Resultado | Doc |
|---|---|---|---|---|
| C1 | Redocking de control: T50, el ligando cristalográfico de 2B6A | RMSD de átomos pesados ≤ 2,0 Å | **0,256 Å → ACEPTA** | `01-redocking-control.md` |
| C2 | Descriptores de la app vs RDKit de línea de comandos | coincidir salvo redondeo, y SCF de GFN2 convergido en los once compuestos | idénticos (máx. Δ = 0,044); SCF 11/11 → **ACEPTA** | `03-descriptores-qsar.md` |
| C3 | QSAR del TP 1 (Partes A y B) | ajustar modelos de 1–3 variables con R², Fisher y Student (α = 0,05) y aplicar ortogonalidad | todos los modelos ajustables → **ACEPTA** | `03-descriptores-qsar.md` |
| C4 | Serie de docking: los once ligandos contra 2B6A, con Webina (Vina 1.2.3 en WebAssembly) | once corridas sin fallas y pose de cada uno dentro del bolsillo NNRTI (centroide a ≤ 10 Å del de T50) | 0,19–1,65 Å → **ACEPTA** | `04-docking-serie.md` |
| C5 | Interacciones de la pestaña Complejo | tabla ligando × residuo; los residuos detectados incluyen los del sitio NNRTI de la bibliografía | 86–100 % de contactos en el sitio; Tyr181/Tyr188 en todos → **ACEPTA** | `05-interacciones.md` |
| C6 | pIC50 = f(ΔGdock) | sin criterio de aprobación (el TP pregunta *si* la relación es significativa) | no robusta entre corridas (R² de 0,02 a 0,44) → **reportado** | `06-regresion-dG.md` |
| C7 | Lectura de `.dlg` de AutoDock y sus clusters en la pestaña Complejo (BetaTools) | leer una campaña entera sin fallas, agrupar igual que el pipeline de docking, no alterar el mapa de interacciones de C5, y andar en un navegador real | 1553/1553 `.dlg`; 1550/1550 iguales al ranking; 12/12 CSV idénticos; 32/32 en Firefox → **ACEPTA** | `07-dlg-clusters.md` |
| C8 | Mapa de contactos ligando × residuo (BetaTools) | que los residuos que salen sean los del sitio donde el proyecto de docking ya ubicó esas poses, y que coincida con un cálculo de distancias independiente | 8/11 residuos en el surco BL2; coincide con el cálculo aparte → **ACEPTA** | `08-mapa-contactos.md` |

**Cómo se corrió.** El docking usó el mismo motor que la app (Webina 1.0.5, AutoDock Vina
1.2.3 compilado a WebAssembly) ejecutado desde Node.js con un arnés que replica la
invocación exacta de la pestaña Docking, y la app real se corrió en un navegador headless
para los descriptores. De contraste —nunca para producir lo que se valida—: RDKit de línea
de comandos (C2) y el binario nativo de Vina 1.2.3 en Colab
(`02-contraste-vina-nativo.md`). Todo lo que se afirma "verificado" tiene su archivo: los
datos crudos en `docs/validacion/datos/`, los scripts en `docs/validacion/arnes/` y las
bitácoras de desarrollo (`bitacora-desarrollo-c4.md` y `bitacora-desarrollo-c2-c3-c5.md`),
que narran además los problemas encontrados y su lectura didáctica.

## Cómo publicarlo

El docking necesita `SharedArrayBuffer`, y eso exige que la página se sirva con las cabeceras
`Cross-Origin-Opener-Policy: same-origin` y `Cross-Origin-Embedder-Policy: credentialless`.
Los descriptores no las necesitan y andan en cualquier lado.

| Dónde | Cómo quedan las cabeceras | Docking |
|---|---|---|
| `app/servir.bat` en una máquina propia | las pone `app/servidor.py` | sí |
| GitHub Pages | no se pueden configurar; las simula `app/coi-serviceworker.js` (MIT) | sí, tras una recarga automática en la primera visita |
| Cloudflare Pages o Netlify | las toma de `app/_headers` | sí, sin service worker |

En GitHub Pages el service worker necesita HTTPS, que el dominio `github.io` ya da. La primera
visita recarga sola una vez: es esperable y está documentado en el propio script.

## Contenido

```
index.html                        el landing: lleva a QuEtool o a la Beta
app/                              QuEtool, la versión estable: un solo index.html, sin compilación
  servidor.py, servir.bat         servidor local con las cabeceras que el docking necesita
  coi-serviceworker.js            las mismas cabeceras cuando el hosting no deja ponerlas
  _headers                        las mismas cabeceras en Cloudflare Pages o Netlify
  lib/                            Webina (Vina) y OpenBabel compilados a WebAssembly
  datos/                          receptor de ejemplo en PDBQT
beta/                             BetaTools, el canal de pruebas: la misma estructura que app/
                                  con lo que todavía no pasó a la estable
docs/
  paleta-opciones.html            las cinco paletas que se evaluaron para la interfaz
  referencia-tp-qsar-docking.md   qué piden los trabajos prácticos: datos, parámetros,
                                  consignas y requisitos funcionales
  fundamentos-y-analisis.md       estado del arte, factibilidad y validación
  verificacion-navegador.md       mediciones dentro de Chromium
  validacion/                     protocolo pre-registrado (00), pasos 01–07, bitácoras
                                  de desarrollo, datos crudos y arnés de cada corrida
spike/                            prueba de concepto ejecutable
data/
  tzd-rawal-2005.csv              serie de 15 tiazolidinonas con actividad y descriptores
                                  publicados
  descriptores-gfn2-rdkit.csv     los mismos descriptores recalculados con este stack
```

## Componentes

| Pieza | Licencia | Rol |
|---|---|---|
| [OpenChemLib](https://github.com/cheminfo/openchemlib-js) | BSD-3-Clause | editor, conformeros 3D, MMFF94 |
| [RDKit MinimalLib](https://github.com/rdkit/rdkit-js) | BSD-3-Clause | descriptores fisicoquímicos |
| [occjs / OCC](https://github.com/peterspackman/occjs) | GPL-3.0-or-later o LGPL-3.0-or-later | GFN2-xTB en WebAssembly |
| [Webina](https://github.com/durrantlab/webina) | Apache-2.0 | AutoDock Vina en el navegador |
| [OpenBabel](https://github.com/openbabel/openbabel) | GPL-2.0 | ligando a PDBQT, hidrógenos a pH 7,4 |
| [3Dmol.js](https://github.com/3dmol/3Dmol.js) | BSD-3-Clause | visor 3D y mapa de interacciones |
| [coi-serviceworker](https://github.com/gzuidhof/coi-serviceworker) | MIT | COOP/COEP en hostings estáticos |
