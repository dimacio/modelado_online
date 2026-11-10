# Paso 2 — Vina nativo como contraste

**Fecha:** 2026-11-10. **Dónde corrió:** Google Colab, CPU, por Dimas.
**Motor:** AutoDock Vina nativo 1.2.3 (binario oficial), misma versión que Webina.
**Notebook:** `validacion_vina_nativo.ipynb`. **Datos:** `datos/dG_vina_nativo_vs_webina.csv`.

Los once ligandos más EFZ-Br se dockearon con Vina nativo contra `2B6A_receptor.pdbqt`,
con la caja leída del `conf.txt` (centro 145.876 / −24.851 / 74.796, 31³, exhaustiveness 10,
semilla 42).

## Resultado 1 — el port a WebAssembly no se desvía del nativo

Único ligando con valor de Webina hasta ahora, el control T50:

| | ΔG (kcal/mol) |
|---|---|
| Vina nativo 1.2.3 | −12,543 |
| Webina (QuEtool) | −12,501 |
| **diferencia** | **−0,042** |

Cuarenta milésimas de kcal/mol de diferencia. Webina es Vina 1.2.3 compilado a WebAssembly
y se comporta como el binario oficial. El resto de la columna de Webina se completa con la
corrida de los once en QuEtool; el punto de control ya da coincidencia.

## Resultado 2 — ΔG de docking contra actividad (C6, preliminar con nativo)

Sobre los diez de la serie (sin T50 que es control, sin EFZ-Br que se predice), ajustando
pIC50 = f(ΔG_dock):

- R² = 0,020 · r de Pearson = −0,141 · Spearman = −0,127
- pendiente = −0,118 · t de Student = −0,40
- t crítico (8 gl, α 0,05) = 2,306 → **la relación NO es significativa**

Es una respuesta válida y esperable: para esta serie y este blanco, el ΔG de docking **no
predice** la potencia. La Sección VI del TP pregunta justamente si la relación es
significativa, y "no lo es" es una conclusión correcta, no una falla de la herramienta.
Como el protocolo fijó C6 sin criterio de aprobación, esto no invalida nada.

Lo importante para la validación: este R² ≈ 0,02 sale de Vina nativo, así que cuando QuEtool
dé lo mismo —y el control T50 anticipa que lo dará— quedará claro que el resultado es del
método de docking, no un artefacto de QuEtool.

## Pendiente

- Completar la columna de Webina con la corrida de los once en QuEtool y confirmar que el
  ΔG-vs-pIC50 de QuEtool coincide con el nativo (R² ≈ 0,02).
- Repetir la regresión con los ΔG de Webina para cerrar C6 con la herramienta bajo prueba.
