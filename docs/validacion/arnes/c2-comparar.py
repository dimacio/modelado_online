#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C2 — Compara los descriptores de QuEtool (corrida real de la app) contra el RDKit de
línea de comandos, para los mismos SMILES. La app usa RDKit (build JS) para mw, clogP, mr,
tpsa y asa; el referente del protocolo es el RDKit CLI (build Python). La comparación es
entre dos builds independientes de la misma librería de referencia, más la verificación de
que el SCF de GFN2 convergió (descriptores geométricos)."""
import json, os
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

AQUI = os.path.dirname(os.path.abspath(__file__))

smis = json.load(open(os.path.join(AQUI, 'smiles_nnrti.json'), encoding='utf-8'))
app = {f['nombre']: f for f in json.load(open(os.path.join(AQUI, 'descriptores_quetool_nnrti.json'), encoding='utf-8'))}

def limpia(s):
    return float(''.join(ch for ch in s if ch in '0123456789.-'))

# orden de las celdas según CAMPOS de la app: mw, clogP, mr, tpsa, asa, dipolo, homo, lumo, gap
CAMPOS = ['mw', 'clogP', 'mr', 'tpsa', 'asa', 'dipolo', 'homo', 'lumo', 'gap']

filas = []
print(f'{"ligando":8s} | {"mw app/ref":22s} | {"clogP app/ref":26s} | {"mr app/ref":22s} | {"tpsa app/ref":22s} | {"asa app/ref":22s} | SCF')
for nom in smis:
    mol = Chem.MolFromSmiles(smis[nom])
    ref = {
        'mw': Descriptors.MolWt(mol),
        'clogP': Descriptors.MolLogP(mol),
        'mr': Descriptors.MolMR(mol),
        'tpsa': Descriptors.TPSA(mol),
        'asa': rdMolDescriptors.CalcLabuteASA(mol),
    }
    f = app[nom]
    cel = {k: limpia(v) for k, v in zip(CAMPOS, f['celdas'])}
    scf = 'convergió' in f['tiempos']
    dif = {k: round(cel[k] - ref[k], 3) for k in ref}
    filas.append({'ligando': nom, 'smiles': smis[nom], 'scf': scf,
                  'app': {k: cel[k] for k in CAMPOS}, 'ref': ref, 'dif': dif})
    print(f'{nom:8s} | {cel["mw"]:>10.2f}/{ref["mw"]:10.2f} | {cel["clogP"]:>10.3f}/{ref["clogP"]:10.3f} '
          f'| {cel["mr"]:>10.2f}/{ref["mr"]:10.2f} | {cel["tpsa"]:>10.1f}/{ref["tpsa"]:10.1f} '
          f'| {cel["asa"]:>10.1f}/{ref["asa"]:10.1f} | {scf}')

# resumen de desviaciones máximas (en valor absoluto, para los 5 descriptores RDKit)
print('\n== desviaciones máximas app vs RDKit CLI (los 5 descriptores topológicos) ==')
for k in ['mw', 'clogP', 'mr', 'tpsa', 'asa']:
    mx = max(abs(f['dif'][k]) for f in filas)
    print(f'{k:6s} max|d| = {mx:.4f}')

todos_scf = all(f['scf'] for f in filas)
print(f'\nSCF convergido en los once: {todos_scf}')

with open(os.path.join(AQUI, 'descriptores_nnrti_comparacion.json'), 'w', encoding='utf-8') as f:
    json.dump(filas, f, ensure_ascii=False, indent=2)
print('descriptores_nnrti_comparacion.json escrito.')
