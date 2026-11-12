# C8 — Mapa de contactos de la pestaña Complejo

Qué se agregó, qué se verificó y con qué datos. Fecha: 2026-11-12.

Vive en **BetaTools** (`beta/`), el canal de pruebas, no en QuEtool (`app/`).

## Qué se agregó

La tarjeta «Interacciones» mira **una pose**: tipo, residuo, átomos, distancia, ángulo. Eso
contesta "cómo se apoya esta pose", pero no "qué residuos toca este ligando" ni, menos aún,
"en qué se parecen entre sí los ligandos que cargué". Para eso está el **Mapa de contactos**:
una matriz con un ligando por fila y un residuo por columna.

El valor de cada celda es la **frecuencia del contacto dentro del cluster elegido**: en
cuántas de sus poses ese residuo aparece con al menos una interacción. Un contacto que sale
en 30 de 30 poses no es lo mismo que uno que salió una vez, y una tabla de pose única no
puede distinguirlos. Es la misma idea que una huella SIFt del documento de diseño
(`docs/diseno-banco-analisis.md`), en su versión más simple.

Detalles de criterio:

- **El cluster lo elige el criterio ya vigente** (`clusterElegido`): población ≥ 10 % de las
  corridas y, entre esos, menor ΔG. No la pose de menor energía suelta.
- **Las interacciones son las mismas de la tarjeta de arriba** (`analizar`), con los mismos
  umbrales documentados en C5. El mapa no define criterios nuevos: sólo los repite sobre
  varias poses y los cuenta por residuo.
- **Tope de 30 poses por ligando**, avisado en la leyenda. Con 50 corridas × varios ligandos
  el cálculo se hace notorio, y la frecuencia ya queda bien estimada con 30.
- **Se destacan los residuos que tocan TODOS los ligandos cargados.** Eso sale del propio
  dato. Marcar "los catalíticos" exigiría saber de qué enzima se trata, y el receptor lo
  pone el usuario: un primer intento marcaba toda Cys/His/Asp/Ser como si fueran el sitio
  activo, lo cual es falso en cualquier proteína.
- **El mapa no se recalcula solo.** Si cambian los ligandos, el receptor o el criterio, se
  descarta y se pide recalcular, para no dejar a la vista un mapa de otros datos.
- Botones de copiar y descargar CSV, con una fila por ligando y la frecuencia por residuo.

## Qué se verificó

Arnés: `arnes/c8-mapa-contactos.py` (Firefox headless de verdad, por selenium; a diferencia
del arnés de C7, que habla WebDriver crudo contra un geckodriver ya levantado).

Datos: receptor `7LBR_PLpro_cat_receptor.pdbqt` y los `.dlg` de **comp02**, **tsc30** y
**comp22** en esa caja, de la campaña `quimioteca-gaussian`.

1. **Los residuos son los correctos.** El mapa da Leu162, Asp164, Arg166, Glu167, Met208,
   Pro248, Tyr264, Tyr268, Gln269, Tyr273, Thr301: **8 de 11 pertenecen al surco BL2**
   (el bolsillo de GRL0617), que es donde el proyecto de docking ya había establecido que
   caen esas poses.
2. **Contra un cálculo independiente.** Un script aparte, que sólo mide "átomo pesado a
   < 4 Å" sobre la mejor pose de comp02, da Leu162, Gly163, Asp164, Arg166, Pro248, Tyr264,
   Gly266, Asn267, Tyr268, Gln269, Tyr273, Thr301. El mapa no lista Gly163, Gly266 ni
   Asn267 porque exige una interacción **tipificada** (puente H, hidrofóbica con sus reglas,
   π–π, halógeno, salino), que es más estricta que la distancia sola. La diferencia es la
   esperada y va en la dirección correcta.
3. **Los clusters coinciden con el proyecto.** comp02 → cluster 1 (tope de 30 poses de las
   50 de su cluster); comp22 → cluster 2 con **5 poses**, consistente con que comp22 no
   converge en esta caja (6/500 en el muestreo profundo del 11-nov).
4. **La invalidación anda**: cambiar el criterio borra el mapa y pide recalcular.

## Trampa encontrada al probar (vale para cualquier prueba futura de la app)

`coi-serviceworker.js` **recarga la página** la primera vez que registra el service worker,
y esa recarga se lleva puesto lo que se haya cargado antes: el receptor subido por el
`input type=file` desaparecía sin dejar rastro y la app seguía con el de ejemplo (la
proteasa de HIV, 4LL3), de modo que el mapa mostraba residuos de otra proteína sin ningún
aviso. La prueba ahora entra una vez, espera, recarga y recién entonces empieza. Conviene
que cualquier arnés nuevo haga lo mismo.
