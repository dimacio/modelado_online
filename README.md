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

Prueba de concepto verificada de punta a punta dentro de un navegador real. La cadena
SMILES → conformero 3D → MMFF94 → GFN2-xTB → descriptores corre en menos de cuatro segundos por
molécula. Falta integrar la parte de docking.

Las mediciones están en `docs/verificacion-navegador.md`.

## Contenido

```
docs/
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
| [occjs / OCC](https://github.com/peterspackman/occjs) | por confirmar | GFN2-xTB en WebAssembly |
| [Ketcher](https://github.com/epam/ketcher) | Apache-2.0 | alternativa de editor |
| [Webina](https://github.com/durrantlab/webina) | Apache-2.0 | AutoDock Vina en el navegador |
