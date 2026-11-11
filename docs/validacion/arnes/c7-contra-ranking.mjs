// C7.5 — Que el agrupamiento de la pestaña sea EL MISMO que el del ranking del proyecto.
// Uso: node c7-contra-ranking.mjs <ruta/beta/index.html> <results/> <ranking.csv>
// Compara, archivo por archivo, el numero de clusters, la poblacion del cluster elegido y
// su dG contra lo que escribio collect_scores.py (quimioteca-gaussian), que reagrupa a
// 1,0 A sobre atomos pesados. Si esto pasa, los dos lados hablan del mismo numero.
import { readFileSync, readdirSync } from 'fs';
const src = readFileSync(process.argv[2], 'utf8');
const corte = (i, f) => { const a = src.indexOf(i), b = src.indexOf(f, a); return src.slice(a, b); };
const mod = [
  corte('const TIPO_ELEM', 'const ACEPTORES'),
  corte('function leerPDBQT', '\nfunction separarPoses'),
  corte('function separarPoses', '\n// Tolerancia de reagrupamiento'),
  corte('// Tolerancia de reagrupamiento', '\n// "6W63_3CLpro_receptor"'),
  corte('// "6W63_3CLpro_receptor"', '\nfunction pintarSelPoses'),
].join('\n') + '\nexport { leerConjunto, clusterElegido };';
const { leerConjunto, clusterElegido } = await import('data:text/javascript,' + encodeURIComponent(mod));

// ranking.csv -> {receptor|carga|ligando: fila}
const csv = readFileSync(process.argv[4], 'utf8').trim().split('\n');
const cab = csv[0].split(',');
const fila = (l) => {           // parser chico: el campo "criterio" puede venir entre comillas
  const out = []; let cur = '', q = false;
  for (const ch of l) {
    if (ch === '"') q = !q;
    else if (ch === ',' && !q) { out.push(cur); cur = ''; }
    else cur += ch;
  }
  out.push(cur);
  return Object.fromEntries(cab.map((c, i) => [c, out[i]]));
};
const R = new Map(csv.slice(1).map(fila).map((r) => [`${r.receptor}|${r.carga}|${r.ligando}`, r]));

let n = 0, mal = [], sinFila = 0;
for (const d of readdirSync(process.argv[3], { withFileTypes: true })) {
  if (!d.isDirectory()) continue;
  const m = d.name.match(/^(.*)_(cm5|gasteiger)$/);
  const [rec, car] = m ? [m[1], m[2]] : [d.name, '?'];
  for (const f of readdirSync(`${process.argv[3]}/${d.name}`)) {
    if (!f.endsWith('.dlg')) continue;
    const lig = f.replace(/\.dlg$/, '');
    const r = R.get(`${rec}|${car}|${lig}`);
    if (!r) { sinFila++; continue; }
    n++;
    const c = leerConjunto(readFileSync(`${process.argv[3]}/${d.name}/${f}`, 'utf8'), lig);
    const e = clusterElegido(c);
    const dif = [];
    if (c.clusters.length !== +r.n_clusters) dif.push(`n_clusters ${c.clusters.length} vs ${r.n_clusters}`);
    if (e && e.n !== +r.n_c1) dif.push(`n_c1 ${e.n} vs ${r.n_c1}`);
    if (e && r.dG_cluster && Math.abs(e.mejor - +r.dG_cluster) > 0.005)
      dif.push(`dG ${e.mejor.toFixed(2)} vs ${r.dG_cluster}`);
    if (dif.length) mal.push(`${rec}/${car} ${lig}: ${dif.join(', ')}`);
  }
}
console.log(`${n} .dlg comparados contra ranking.csv (${sinFila} sin fila)`);
console.log(`coinciden: ${n - mal.length} | difieren: ${mal.length}`);
for (const x of mal.slice(0, 10)) console.log('  ', x);
process.exit(mal.length ? 1 : 0);
