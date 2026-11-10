# Paso 1 — Redocking de control (C1, bloqueante)

**Fecha:** 2026-11-10. **QuEtool:** commit `3d4b21c`, servido en local desde el mismo
árbol que el publicado. **Motor:** Webina (AutoDock Vina 1.2.3 en WebAssembly).

## Qué se hizo

Se redockeó T50 —el ligando cristalográfico de 2B6A, que es TBZ1— contra su propio
receptor, y se comparó la pose de menor energía contra las coordenadas cristalográficas.
El ligando entró por **SMILES** (`Cc1cccc2c1nc(-c1c(F)cccc1F)n2Cc1c(F)cccc1F`), que es el
camino del estudiante: QuEtool genera el confórmero, le pone hidrógenos a pH 7,4, lo
convierte a PDBQT con Gasteiger y lo dockea. O sea que el confórmero de partida **no** es
el cristalográfico; que vuelva a la pose cristalográfica es justamente lo que prueba la
configuración.

**Caja:** centro (145.876, −24.851, 74.796), 31³ Å, exhaustiveness 10, 2 núcleos.
**Receptor:** `2B6A_receptor.pdbqt` (9568 líneas, cargado desde archivo).

## Resultado

- Corrida completa en **29 s**.
- Mejor pose: **−12,501 kcal/mol**.
- **RMSD de átomos pesados contra el cristal: 0,256 Å in situ** (sin re-superponer, mismo
  marco de coordenadas); 0,126 Å con re-superposición óptima. Corregido por la simetría de
  la molécula (dos grupos 2,6-difluorofenilo): 4 correspondencias por isomorfismo, se tomó
  el mínimo.

## Veredicto

**C1: ACEPTA** (umbral ≤ 2,0 Å, obtenido 0,256 Å). La preparación del receptor, la caja y
la cadena de preparación del ligando reproducen la pose cristalográfica. Se habilita correr
la serie.

## Respaldo

- `datos/T50_redock.pdbqt` — las poses crudas que devolvió QuEtool.
- `datos/T50_cristal.pdb` — T50 extraído de 2B6A, átomos pesados, confórmero A.
- RMSD calculado con RDKit sobre el esqueleto de conectividad, in situ, mínimo sobre las
  automorfismos de la molécula.

## Nota de método

El RMSD se informa **in situ**, sin volver a superponer, porque el receptor es el mismo y
está fijo: es la medida correcta para un redocking y la más exigente. El valor con
re-superposición se da sólo como referencia.
