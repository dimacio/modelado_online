// C7 — Barrido del lector de .dlg sobre una campaña entera de AutoDock-GPU.
// Uso: node c7-barrido-dlg.mjs <ruta/app/index.html> <carpeta con .dlg>
// Extrae leerDLG/leerConjunto del propio index.html (no hay copia del codigo acá) y
// verifica en cada archivo: que haya poses, que todas tengan dG, que la suma de los
// clusters sea igual al numero de corridas y que cada cluster indexe a sus miembros.
import { readFileSync, readdirSync, statSync } from 'fs';
const src = readFileSync(process.argv[2], 'utf8');
const corte=(i,f)=>{const a=src.indexOf(i),b=src.indexOf(f,a);return src.slice(a,b)};
const mod=[corte('const TIPO_ELEM','const ACEPTORES'),corte('function leerPDBQT','\nfunction separarPoses'),
corte('function separarPoses','\n// ── AutoDock 4'),corte('function leerDLG','\nfunction leerConjunto'),
corte('function leerConjunto','\nfunction pintarSelPoses')].join('\n')+'\nexport {leerConjunto};';
const { leerConjunto } = await import('data:text/javascript,'+encodeURIComponent(mod));
let n=0, mal=[], raros=[];
function rec(d){for(const e of readdirSync(d,{withFileTypes:true})){const p=d+'/'+e.name;
 if(e.isDirectory())rec(p); else if(e.name.endsWith('.dlg')){n++;
  try{const c=leerConjunto(readFileSync(p,'utf8'),e.name);
   const sum=c.clusters.reduce((s,x)=>s+x.n,0);
   if(!c.poses.length) mal.push([p,'0 poses']);
   else if(!c.clusters.length) raros.push([p,'sin clusters']);
   else if(sum!==c.poses.length) mal.push([p,`sumN ${sum} != poses ${c.poses.length}`]);
   else if(c.poses.some(q=>q.dg==null)) mal.push([p,'pose sin dG']);
   else if(!c.clusters.every(x=>x.idx.length===x.n)) mal.push([p,'idx incompleto']);
  }catch(err){mal.push([p,'EXCEPCION '+err.message])}}}}
rec(process.argv[3]);
console.log(`revisados ${n} .dlg | fallas ${mal.length} | sin clusters ${raros.length}`);
for(const x of mal.slice(0,15))console.log('  FALLA',x[0].split('/').slice(-2).join('/'),'→',x[1]);
for(const x of raros.slice(0,5))console.log('  raro',x[0].split('/').slice(-2).join('/'),'→',x[1]);
