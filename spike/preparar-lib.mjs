// Copia los binarios de las dependencias a spike/lib/, que es desde donde los sirve la pagina.
// No se versionan: son unos 76 MB.
import { cp, mkdir } from 'fs/promises';
const N = 'node_modules';
await mkdir('lib', { recursive: true });
await cp(`${N}/@peterspackman/occjs/dist`, 'lib/occjs', { recursive: true });
for (const f of ['@rdkit/rdkit/dist/RDKit_minimal.js', '@rdkit/rdkit/dist/RDKit_minimal.wasm',
                 'openchemlib/dist/openchemlib.js', 'openchemlib/dist/resources.json'])
  await cp(`${N}/${f}`, 'lib/' + f.split('/').pop());
console.log('lib/ lista');
