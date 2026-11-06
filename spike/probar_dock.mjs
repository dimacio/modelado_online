import { createRequire } from 'module';
const { chromium } = createRequire('/home/claude/')('playwright');
import { readFileSync } from 'fs';
const b = await chromium.launch();
const pg = await b.newPage();
const errs = [];
pg.on('pageerror', e => errs.push(String(e).slice(0,300)));
pg.on('console', m => { if (m.type()==='error') errs.push(m.text().slice(0,200)); });
await pg.goto('http://127.0.0.1:8781/dock.html');
await pg.waitForFunction(() => window.__listo === true, null, { timeout: 120000 });
console.log('modulo cargado en el navegador');

const rec = readFileSync('datos/4LL3_receptor_HIV-protease.pdbqt','utf8');
const lig = readFileSync('datos/4LL3_ligand_darunavir.pdbqt','utf8');

// parametros del TP (conf.txt) salvo centro/tamano, que son del benchmark 4LL3
const params = {
  center_x: -9.81455263, center_y: 15.20044737, center_z: 26.96442105,
  size_x: 20, size_y: 20, size_z: 20,
  exhaustiveness: 10, energy_range: 3, seed: 123456789, cpu: 4,
  weight_gauss1: -0.035579, weight_gauss2: -0.005156, weight_repulsion: 0.840245,
  weight_hydrophobic: -0.035069, weight_hydrogen: -0.587439, weight_rot: 0.05846,
};
const r = await pg.evaluate(([p, re, li]) => window.dockear(p, re, li), [params, rec, lig]);
console.log('ok:', r.ok, '| tiempo:', r.ms ? (r.ms/1000).toFixed(1)+' s' : '-');
if (r.error) console.log('error:', r.error);
if (r.stdout) { console.log('--- stdout ---'); console.log(r.stdout.slice(0,1200)); }
if (r.stderr) { console.log('--- stderr ---'); console.log(r.stderr.slice(0,400)); }
if (r.pose) {
  const lineas = r.pose.split('\n').filter(l => l.includes('VINA RESULT'));
  console.log('--- poses en el PDBQT de salida:', lineas.length, '---');
  lineas.slice(0,9).forEach(l => console.log('  ' + l.trim()));
}
if (errs.length) { console.log('--- errores de pagina ---'); errs.slice(0,5).forEach(e=>console.log('  '+e)); }
await b.close();
