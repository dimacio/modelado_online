# Validación de QuEtool contra el TP de la cátedra — protocolo

> **Escrito antes de correr nada**, el 2026-11-10. Los criterios de la sección 4 quedan
> fijados de antemano para que el resultado no se pueda acomodar después. Cada paso se
> documenta en su archivo numerado y deja sus datos crudos en `datos/`. Lo que diga "se
> verificó" tiene que tener su archivo; si no lo tiene, va marcado como no respaldado.

## 1. Qué se valida

Que la cadena libre de QuEtool permite cumplir **las consignas del TP 2 de Química
Medicinal (FFyB-UBA)**, que hoy se hacen con HyperChem, MGLTools y AutoDock Vina de
escritorio. La unidad de validación es la consigna, no la función: no alcanza con que
calcule un dipolo, tiene que permitir contestar lo que el TP pregunta.

## 2. Qué no se valida

- Que QuEtool dé **los mismos números** que HyperChem. Son métodos distintos (GFN2-xTB
  contra AM1, Wildman-Crippen contra el logP de HyperChem) y esperar coincidencia numérica
  sería un error conceptual. Se valida que las *conclusiones* se sostengan.
- El acierto biológico de los modelos. Un R² bajo no es una falla de la herramienta.
- El rendimiento en hardware de estudiante, que se mide aparte.

## 3. Materiales y versiones

**Entradas:** carpeta de Drive "QuEtool - materiales TP reconstruidos"; su `LEEME.md`
documenta la procedencia de cada archivo. Receptor 2B6A del PDB, diez ligandos de la serie,
T50 como control y EFZ-Br como compuesto de diseño.

**Bajo prueba:** QuEtool en `dimacio.github.io/modelado_online/app/`, con el commit anotado
en cada paso. Componentes: OpenChemLib 9.25.2, RDKit MinimalLib 2026.09.2, occjs 0.9.7
(GFN2-xTB), Webina 1.0.5 (Vina 1.2.3 en WebAssembly), OpenBabel en WebAssembly, 3Dmol.js 2.4.2.

**De referencia**, sólo para contrastar y nunca para producir lo que se valida: RDKit y
OpenBabel de línea de comandos.

**Limitación del entorno, declarada.** Bajar el binario nativo de Vina fue rechazado por la
política del entorno de ejecución, así que todo el docking corre en Webina. No es una
elección metodológica: implica que, fuera del control de redocking, no hay una corrida
nativa independiente contra la cual contrastar los ΔG.

## 4. Criterios de aceptación

**C1 — Redocking de control (bloqueante).** Se redockea T50 y se compara la pose de menor
energía contra la cristalográfica. Acepta con **RMSD de átomos pesados ≤ 2,0 Å**. Si falla,
la configuración está mal y no se corre nada más.

**C2 — Descriptores.** Acepta si los descriptores que RDKit de referencia también calcula
coinciden salvo redondeo, y si los que dependen de la geometría se obtienen con el SCF
convergido en los once compuestos. Se registra aparte, sin criterio de aprobación, la
brecha ya conocida: la guía pide Volume, Polarizability y Hydration Energy, que QuEtool no
calcula.

**C3 — QSAR del TP 1.** Acepta si se pueden ajustar y comparar los modelos de una y dos
variables con R², Fisher y Student a α = 0,05, y aplicar el criterio de ortogonalidad. El
valor de R² no entra en el criterio.

**C4 — Serie de docking.** Acepta si los once ligandos se dockean sin fallas y la pose de
cada uno cae dentro del bolsillo NNRTI (centroide a ≤ 10 Å del de T50).

**C5 — Interacciones.** Acepta si la pestaña Complejo produce la tabla de doble entrada que
pide la Sección IV, y si para los complejos con estructura cristalográfica los residuos
detectados incluyen los del sitio descrito en la bibliografía.

**C6 — pIC50 = f(ΔGdock).** No tiene criterio de aprobación: el TP pregunta *si* la
relación es significativa, y "no lo es" es una respuesta válida y publicable. Se reporta
R², pendiente, su signo y el p de Student.

## 5. Reglas de registro

1. Cada paso anota la fecha, el commit de QuEtool y los parámetros exactos usados.
2. Los archivos de salida sin procesar van a `datos/`, con el nombre del paso.
3. Los resultados que no cumplen un criterio se escriben igual, con el criterio al lado.
4. Si un paso se repite, queda el registro de las dos corridas y por qué se repitió.
