// C7 — Regresion de C5: el mapa de interacciones no cambia al agregar el lector de .dlg.
// Uso: node c7-regresion-c5.mjs <ruta/beta/index.html> <docs/validacion/datos>
// Corre analizar() sobre la pose 1 de los once ligandos de C4 contra 2B6A y compara
// fila por fila contra los CSV ya validados. La unica normalizacion es la etiqueta
// pi-pi, que el arnes de Python escribio en ASCII.
// Regresión C5: que analizar() siga dando exactamente lo validado contra 2B6A,
// con el PDBQT de Vina leído por el camino de siempre (separarPoses).
import { readFileSync } from 'fs';
const APP = process.argv[2], DAT = process.argv[3];
const src = readFileSync(APP, 'utf8');
const corte = (i, f) => { const a = src.indexOf(i), b = src.indexOf(f, a); return src.slice(a, b); };
const mod = [
  corte('const TIPO_ELEM', 'const ACEPTORES'),
  corte('const ACEPTORES', '// el ligando se distingue'),
  corte('const ANILLOS_RES', '\nconst cEstado'),
  corte('function leerPDBQT', '\nfunction separarPoses'),
  corte('function separarPoses', '\n// ── AutoDock 4'),
  corte('function leerDLG', '\nfunction leerConjunto'),
  corte('// geometría elemental', '\n// ── dibujo ──'),
].join('\n') + '\nexport { leerPDBQT, separarPoses, leerDLG, analizar };';
const M = await import('data:text/javascript,' + encodeURIComponent(mod));

const rec = M.leerPDBQT(readFileSync(APP.replace(/index\.html$/, 'datos/2B6A_receptor.pdbqt'), 'utf8'));
let fallas = 0, ok = 0;
for (const lig of ['NVP', 'EFZ', 'TNK', 'U05', 'T50', 'ZZE', 'GFA', 'HBQ', 'TBO', 'QNO47b', 'QNO47c', 'EFZ-Br']) {
  let poses, esperado;
  try {
    poses = M.separarPoses(readFileSync(`${DAT}/${lig}_webina.pdbqt`, 'utf8'));
    esperado = readFileSync(`${DAT}/${lig}_interacciones.csv`, 'utf8').trim().split('\n').slice(1);
  } catch { continue; }
  const got = M.analizar(rec, M.leerPDBQT(poses[0].lineas.join('\n')));
  const mio = got.map((x) => [x.tipo, x.residuo, x.atRes, x.atLig, x.d.toFixed(3),
    x.ang === null ? '' : x.ang.toFixed(1), x.rol].join(','));
  const norm = (l) => l.replace('π–π', 'pi-pi');
  const igual = mio.length === esperado.length && mio.every((l, i) => norm(l) === esperado[i]);
  if (igual) { ok++; console.log(`OK    ${lig}: ${mio.length} interacciones idénticas al CSV validado`); }
  else {
    fallas++;
    console.log(`FALLA ${lig}: ${mio.length} vs ${esperado.length} esperadas`);
    for (let i = 0; i < Math.max(mio.length, esperado.length); i++)
      if (norm(mio[i] ?? '') !== esperado[i]) { console.log(`   fila ${i}\n    mio: ${mio[i]}\n    csv: ${esperado[i]}`); break; }
  }
}
console.log(`\n${ok} ligandos idénticos, ${fallas} con diferencias`);
process.exit(fallas ? 1 : 0);
