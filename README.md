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

Las mediciones están en `docs/verificacion-navegador.md`.

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
app/                              la aplicación: un solo index.html, sin compilación
  servidor.py, servir.bat         servidor local con las cabeceras que el docking necesita
  coi-serviceworker.js            las mismas cabeceras cuando el hosting no deja ponerlas
  _headers                        las mismas cabeceras en Cloudflare Pages o Netlify
  lib/                            Webina (Vina) y OpenBabel compilados a WebAssembly
  datos/                          receptor de ejemplo en PDBQT
docs/
  paleta-opciones.html            las cinco paletas que se evaluaron para la interfaz
  referencia-tp-qsar-docking.md   qué piden los trabajos prácticos: datos, parámetros,
                                  consignas y requisitos funcionales
  fundamentos-y-analisis.md       estado del arte, factibilidad y validación
  verificacion-navegador.md       mediciones dentro de Chromium
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
