// C7.4 — Que el RMSD contra el cristal que muestra la pestaña sea el del .dlg.
// Uso: node c7-controles-cristal.mjs <ruta/beta/index.html> <carpeta controls/results>
// El numero NO se recalcula: AutoDock lo escribe en la columna "Reference RMSD" de la
// RMSD TABLE cuando la corrida llevo --xraylfile, ya corregido por simetria. Se contrasta
// contra los valores publicados en los controles del proyecto quimioteca-gaussian.
import { readFileSync } from 'fs';
const src = readFileSync(process.argv[2], 'utf8');
const corte = (i, f) => { const a = src.indexOf(i), b = src.indexOf(f, a); return src.slice(a, b); };
const mod = [
  corte('const TIPO_ELEM', 'const ACEPTORES'),
  corte('function leerPDBQT', '\nfunction separarPoses'),
  corte('function separarPoses', '\n// ── AutoDock 4'),
  corte('function leerDLG', '\n// "6W63_3CLpro_receptor"'),
  corte('// "6W63_3CLpro_receptor"', '\nfunction pintarSelPoses'),
].join('\n') + '\nexport { leerConjunto, clusterElegido };';
const { leerConjunto, clusterElegido } = await import('data:text/javascript,' + encodeURIComponent(mod));

// [archivo, corrida, RMSD publicado en los controles del proyecto]
// valores leidos a mano de la RMSD TABLE de cada .dlg
const esperado = [
  ['X77_6W63_redock', 32, 0.88], ['X77_6W63_redock', 19, 0.85],
  ['A5I_7QCH_redock', 46, 1.00], ['A5I_7QCH_redock', 6, 4.27],
  ['XT7_7LBR_redock', 39, 1.95], ['N3_6LU7_redock', 14, 3.30],
];
// el criterio del proyecto (poblacion >= 10%, y entre esos el de menor dG) contra lo que
// elegiria el ranking de AutoDock (energia sola). El caso que lo motiva es A5I/7QCH.
const criterio = [
  // archivo, cluster que elige el criterio, RMSD de su pose top, cluster 1 y su RMSD
  ['A5I_7QCH_redock', 2, 1.00, 1, 4.27],
  ['X77_6W63_redock', 1, 0.88, 1, 0.88],
  ['XT7_7LBR_redock', 1, 1.95, 1, 1.95],
];
let mal = 0;
for (const [f, run, esp] of esperado) {
  const c = leerConjunto(readFileSync(`${process.argv[3]}/${f}.dlg`, 'utf8'), f);
  const p = c.poses.find((x) => x.run === run);
  const ok = p && Math.abs(p.rmsdRef - esp) < 0.005 && c.meta.xray;
  if (!ok) mal++;
  console.log(`${ok ? 'OK   ' : 'FALLA'} ${f.padEnd(16)} corrida ${String(run).padStart(3)}: ` +
    `dlg ${p ? p.rmsdRef.toFixed(2) : '—'} / publicado ${esp.toFixed(2)}  [xray: ${c.meta.xray || 'NO'}]`);
}
for (const [f, rank, rmsdEleg, rank1, rmsd1] of criterio) {
  const c = leerConjunto(readFileSync(`${process.argv[3]}/${f}.dlg`, 'utf8'), f);
  const e = clusterElegido(c);
  const top = c.poses[e.idx[0]], top1 = c.poses[c.clusters[0].idx[0]];
  const ok = e.rank === rank && Math.abs(top.rmsdRef - rmsdEleg) < 0.005
    && c.clusters[0].rank === rank1 && Math.abs(top1.rmsdRef - rmsd1) < 0.005;
  if (!ok) mal++;
  const tot = c.poses.length;
  console.log(`${ok ? 'OK   ' : 'FALLA'} ${f.padEnd(16)} criterio → cluster ${e.rank} ` +
    `(${(100 * e.n / tot).toFixed(0)} % de las corridas, RMSD ${top.rmsdRef.toFixed(2)}) | ` +
    `energia sola → cluster ${c.clusters[0].rank} ` +
    `(${(100 * c.clusters[0].n / tot).toFixed(0)} %, RMSD ${top1.rmsdRef.toFixed(2)})`);
}

// y que en una corrida de produccion (sin --xraylfile) NO se ofrezca el RMSD
const prod = leerConjunto(readFileSync(process.argv[4], 'utf8'), 'produccion');
const okProd = !prod.meta.xray && !prod.meta.xrayLineas;
if (!okProd) mal++;
console.log(`${okProd ? 'OK   ' : 'FALLA'} produccion sin --xraylfile: no declara cristal (${prod.meta.xray || 'ninguno'})`);
console.log(`\n${esperado.length + 1 - mal} OK, ${mal} fallas`);
process.exit(mal ? 1 : 0);
