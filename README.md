# modelado_online

Herramienta web libre para los trabajos prácticos de QSAR y docking molecular de la cátedra de
Química Medicinal (FFyB-UBA). Reemplaza una cadena de software propietario, de escritorio y solo
para Windows por un pipeline que corre entero en el navegador, sin instalación ni licencias.

## Por qué

Los TP actuales dependen de HyperChem, comercial y discontinuado de hecho, y de MGLTools, sin
mantenimiento activo. La cátedra ya tuvo que redactar un procedimiento alternativo completo
porque AutoDockTools falla en algunas máquinas con Windows 11 y drivers AMD. Un estudiante con
macOS, Linux o una computadora administrada no puede completar el práctico.

## Estado

Factibilidad técnica verificada de punta a punta, dentro de un navegador real. La cadena
SMILES → conformero 3D → MMFF94 → GFN2-xTB → descriptores corre en menos de cuatro segundos por
molécula y reproduce las conclusiones químicas del caso de literatura que usa el TP.

Ver `docs/verificacion-navegador.md` para las mediciones y `docs/fundamentos-y-analisis.md` para
el análisis completo.

## Contenido

```
docs/
  referencia-tp-qsar-docking.md   destilado de las guías de cátedra: datos, parámetros,
                                  consignas y requisitos funcionales que se desprenden
  fundamentos-y-analisis.md       problema, estado del arte, factibilidad y validación
  verificacion-navegador.md       mediciones dentro de Chromium
spike/                            prueba de concepto ejecutable
data/
  tzd-rawal-2005.csv              las 15 tiazolidinonas: SMILES, actividad y descriptores
                                  publicados
  descriptores-gfn2-rdkit.csv     descriptores recalculados con el stack libre
```

## Componentes

| Pieza | Licencia | Rol |
|---|---|---|
| [OpenChemLib](https://github.com/cheminfo/openchemlib-js) | BSD-3-Clause | editor, conformeros 3D, MMFF94 |
| [RDKit MinimalLib](https://github.com/rdkit/rdkit-js) | BSD-3-Clause | descriptores fisicoquímicos |
| [occjs / OCC](https://github.com/peterspackman/occjs) | por confirmar | GFN2-xTB en WebAssembly |
| [Ketcher](https://github.com/epam/ketcher) | Apache-2.0 | alternativa de editor |
| [Webina](https://github.com/durrantlab/webina) | Apache-2.0 | AutoDock Vina en el navegador |

## Destino

Technology Report en el *Journal of Chemical Education*, con piloto en aula previsto para 2027.
