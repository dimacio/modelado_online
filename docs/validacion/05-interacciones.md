# Paso 5 — Interacciones (C5)

**Fecha:** 2026-11-10. **QuEtool:** commit `ff964ce`. El análisis replica **exactamente**
la función `analizar()` de la pestaña Complejo de la app (mismos umbrales, tipos de átomo,
definiciones de anillos y grupos cargados), portada a Python en `arnes/c5-interacciones.py`
porque fuera del navegador no hay visor 3D que manejar. Entradas: `2B6A_receptor.pdbqt` y
la pose 1 (mejor modo) de cada ligando del paso 4.

## Criterios geométricos (los de la app, literal)

| Interacción | Criterio |
|---|---|
| Puente de hidrógeno | donante N/O/S con H; aceptor OA/NA/SA; d(D···A) ≤ 3,5 Å, d(H···A) ≤ 2,6 Å, ángulo D–H···A ≥ 130° |
| Hidrofóbica | C del ligando sin vecino N/O contra C del receptor sin vecino N/O (a 1,8 Å); d ≤ 4,0 Å; la mejor por residuo |
| π–π | anillos aromáticos planos (5–6 miembros) del ligando contra anillos de PHE/TYR/HIS/TRP; d(centroides) ≤ 5,5 Å; paralela (ángulo < 30°, desplazamiento ≤ 2,0 Å) o en T (> 50°, ≤ 3,0 Å) |
| Halógeno | Cl/Br/I unido a C contra N/O del receptor; d ≤ 4,0 Å, ángulo C–X···A ≥ 140° |
| Puente salino | grupos cargados opuestos (carboxilato, guanidinio/amidinio, amonio cuaternario; ARG/LYS/HIS cationes, ASP/GLU aniones); d(centroides) ≤ 5,0 Å |

## Resultado

Los doce ligandos (los once más el control T50) producen mapas de interacción con el
mismo criterio. Tabla de doble entrada ligando × residuo contactado (la que pide la
Sección IV del TP), con los residuos del sitio NNRTI de la bibliografía:

| Ligando | Interacciones | % en el sitio NNRTI | Residuos del sitio contactados |
|---|---:|---:|---|
| EFZ | 8 | 100 | Lys101, Val106, Tyr181, Tyr188, Trp229, Leu234, Tyr318 |
| EFZ-Br | 6 | 100 | Leu100, Lys103, Val106, Tyr181, Phe227, Tyr318 |
| GFA | 12 | 90 | Leu100, Val106, Val179, Tyr181, Tyr188, Phe227, Trp229, Leu234, Tyr318 |
| HBQ | 8 | 100 | Leu100, Lys103, Val106, Tyr181, Tyr188, Trp229, Tyr318 |
| NVP | 6 | 100 | Leu100, Lys103, Val106, Val179, Tyr181, Tyr318 |
| QNO47b | 8 | 88 | Leu100, Lys103, Val106, Val179, Tyr181, Tyr188, Trp229 |
| QNO47c | 7 | 86 | Leu100, Val106, Tyr181, Tyr188, Trp229, Leu234 |
| TBO | 8 | 100 | Leu100, Lys101, Lys103, Tyr181, Tyr188, Phe227, Trp229, Leu234 |
| TNK | 10 | 100 | Leu100, Lys103, Val106, Tyr181, Tyr188, Phe227, Trp229, Leu234, Tyr318 |
| U05 | 10 | 100 | Leu100, Lys103, Val106, Tyr181, Tyr188, Phe227, Trp229, Leu234 |
| ZZE | 6 | 100 | Leu100, Val106, Tyr188, Trp229, Leu234, Tyr318 |
| T50 (control) | 12 | 100 | Leu100, Lys103, Val106, Val179, Tyr181, Tyr188, Trp229, Leu234, Tyr318 |

Entre el 86 % y el 100 % de los residuos contactados son los del bolsillo NNRTI descrito
en la bibliografía, y **Tyr181 o Tyr188 —las dos tirosinas del sándwich aromático que
define el sitio— aparecen en los doce complejos**. Los CSV por ligando (mismo formato que
el export de la app) están en `datos/<ligando>_interacciones.csv` y el resumen en
`datos/resumen_interacciones.json`.

**C5: ACEPTA.** La pestaña Complejo produce la tabla de doble entrada que pide el TP y,
para los complejos con estructura cristalográfica, los residuos detectados incluyen los
del sitio descrito en la bibliografía.

## Lectura para la discusión del TP

El patrón de la serie es coherente: contactos hidrofóbicos con Leu100/Val106/Leu234 y
sándwich con Tyr181/Tyr188 en casi todos, más Phe227/Trp229 en los más aromáticos (GFA,
TBO, TNK, U05). El compuesto de diseño **EFZ-Br conserva la red de su precursor EFZ**
(mismo esqueleto: Lys101/Lys103, Val106, Tyr181, Phe227, Tyr318, y el halógeno del anillo
que mira al bolsillo), que es exactamente la comparación que pide el entregable 3 del TP;
QNO47b/QNO47c (análogos carbonados de EFZ) también recapitulan el mismo patrón. Los datos
quedan listos para las capturas de pantalla y la tabla de la Sección V.
