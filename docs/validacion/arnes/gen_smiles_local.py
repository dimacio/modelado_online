#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SMILES canónicos de los 11 ligandos desde los SDF (copia local), con RDKit CLI."""
import glob, json, os
from rdkit import Chem

AQUI = os.path.dirname(os.path.abspath(__file__))
SDF_DIR = AQUI  # los SDF están copiados acá

orden = ['GFA', 'EFZ', 'TBO', 'TNK', 'NVP', 'HBQ', 'QNO47b', 'U05', 'ZZE', 'QNO47c', 'EFZ-Br']
salida = {}
for nom in orden:
    p = os.path.join(SDF_DIR, nom + '.sdf')
    mol = Chem.MolFromMolFile(p, removeHs=False, strictParsing=False, sanitize=True)
    if mol is None:
        raise SystemExit(f'no se pudo leer {p}')
    sinH = Chem.RemoveHs(mol)
    smi = Chem.MolToSmiles(sinH, canonical=True, isomericSmiles=True)
    salida[nom] = smi
    print(f'{nom:8s} {smi}', flush=True)

with open(os.path.join(AQUI, 'smiles_nnrti.json'), 'w', encoding='utf-8') as f:
    json.dump(salida, f, ensure_ascii=False, indent=2)
print('smiles_nnrti.json escrito.', flush=True)
