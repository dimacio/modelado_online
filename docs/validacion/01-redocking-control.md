# Paso 1 — Control de redocking de T50 (criterio C1)

**Fecha:** 2026-11-10 · **QuEtool:** commit `3d4b21c`, servido localmente desde `app/`
· **Resultado: ACEPTA.** RMSD 0,26 Å contra un criterio de ≤ 2,0 Å.

## Qué se hizo

T50 es el ligando cristalográfico de 2B6A, o sea que su pose correcta se conoce. Si el
sistema está bien configurado, Vina tiene que volver a encontrarla. Si no lo hace, los ΔG
de los otros once ligandos no significan nada, y por eso este paso es bloqueante.

Se hizo el camino completo de un estudiante, no un atajo: se cargó el SMILES de T50 en la
pestaña de descriptores, se lo pasó al dibujo, y QuEtool generó por su cuenta el confórmero
3D, le agregó hidrógenos a pH 7,4 y lo convirtió a PDBQT. **La geometría cristalográfica no
se usó como entrada** — entró sólo al final, como referencia para medir.

SMILES: `Cc1cccc2c1nc(-c1c(F)cccc1F)n2Cc1c(F)cccc1F`

## Parámetros

Receptor `2B6A_receptor.pdbqt`, 9568 líneas. Caja centrada en (145.876, −24.851, 74.796),
31×31×31 Å, *exhaustiveness* 10, 2 núcleos. El `conf.txt` usado está en
`datos/conf-2B6A.txt`.

## Resultado

| Pose | ΔG (kcal/mol) | RMSD in-place vs cristal |
|---|---|---|
| 1 | **−12,501** | **0,26 Å** |
| 2 | −9,985 | 5,77 Å |

El RMSD se midió **sin alinear** —lo que importa es la posición absoluta dentro del
bolsillo, no el parecido de forma— y con reconocimiento de simetría molecular, que hace
falta porque los dos anillos 2,6-difluorofenilo son intercambiables. Herramienta:
`rdMolAlign.CalcRMS` de RDKit, con los órdenes de enlace asignados desde el SDF ideal del
PDB. Átomos pesados solamente: 27.

Tiempo: **29 segundos** en el contenedor de dos núcleos, dentro del navegador.

## Observación que conviene registrar

Se corrió dos veces. La primera dio **−11,291** kcal/mol y la segunda **−12,501**, con la
misma configuración. Vina es estocástico y no se le fijó semilla, así que la diferencia es
esperable, pero es de 1,2 kcal/mol y **merece figurar en el material del TP**: dos
estudiantes con los mismos archivos van a obtener números distintos, y conviene que lo
sepan de antemano en vez de descubrirlo comparando informes. La pose de la primera corrida
no se guardó por un error del script, así que su RMSD no se midió; sólo consta el ΔG.

## Interpretación

0,26 Å es un acuerdo muy bueno — para referencia, los controles propios de la cátedra en la
campaña de cisteín-proteasas dan 0,78 Å y 0,94 Å. Lo que queda validado con esto:

- el receptor quedó bien preparado al pasarlo por OpenBabel,
- el centro de caja calculado sobre el centroide de T50 apunta al sitio correcto, lo que
  confirma de forma independiente que el centro del `conf.txt` original no servía para el
  2B6A del PDB,
- la preparación de ligando de QuEtool —confórmero, hidrógenos, PDBQT— produce una entrada
  que Vina resuelve bien,
- y Webina, la compilación a WebAssembly, reproduce el comportamiento esperado de Vina.

## Datos crudos

`datos/T50_redock.pdbqt` (las dos poses), `datos/T50_salida_vina.txt` (salida del
programa), `datos/T50_tabla_poses.txt`, `datos/datos_T50_cristal.txt` (referencia) y
`datos/conf-2B6A.txt`.
