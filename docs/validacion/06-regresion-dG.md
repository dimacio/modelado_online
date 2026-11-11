# Paso 6 — pIC50 = f(ΔGdock) (C6, cierre formal)

**Fecha:** 2026-11-10. El protocolo 00 fija que C6 **no tiene criterio de aprobación**:
el TP pregunta *si* la relación es significativa, y "no lo es" es una respuesta válida y
publicable. Este documento reúne las tres regresiones que quedaron dispersas en los pasos
02 y 04, con R², pendiente, su signo y la p de Student, y cierra el paso.

## Las tres corridas

Sobre los diez NNRTI de la serie (sin T50, que es control, y sin EFZ-Br, que se predice):

| Corrida | R² | r | pendiente | t | p (Student) | significativa (α 0,05) |
|---|---:|---:|---:|---:|---:|---|
| Vina nativo 1.2.3, semilla 42 (paso 02) | 0,020 | −0,141 | −0,118 | −0,40 | 0,70 | no |
| Webina/QuEtool, corrida de la serie (paso 04) | 0,409 | −0,640 | −0,479 | −2,36 | 0,046 | marginal |
| Webina con la pose espuria de U05 (1.ª corrida, descartada) | 0,443 | −0,665 | −0,425 | −2,52 | 0,036 | sí |

## Conclusión

La relación **no es robusta**: el signo de la pendiente es siempre negativo (a más
afinidad predicha, más potencia, como espera la teoría), pero la fuerza del ajuste cambia
de corrida en corrida con la semilla estocástica — de R² = 0,02 a R² = 0,41 — y una sola
pose espuria fuera del bolsillo (U05, primera corrida del paso 04) infla el ajuste hasta
0,44. La respuesta a la pregunta del TP es: *con estos datos no hay una relación
significativa estable entre ΔGdock y pIC50*; la respuesta "sí" de una corrida suelta es un
artefacto de muestreo, no un modelo.

Para el material educativo éste es el resultado más valioso de la validación: muestra con
números propios por qué la discusión (Sección VI) pide justificar si *"el modelo obtenido
se encuentra validado"* — y por qué la respuesta honesta es **falso**.

**C6: reportado, sin criterio de aprobación** (como fija el protocolo). Los números
crudos están en `datos/dG_vina_nativo_vs_webina.csv` (nativo vs Webina, ligando por
ligando) y en los pasos 02 y 04.
