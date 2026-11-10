#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Análisis del criterio C4 (protocolo docs/validacion/00-protocolo.md).

Para cada ligando de la serie (los once, sin T50): toma el MODEL 1 del PDBQT de poses de
Webina, calcula el centroide de sus átomos pesados y mide la distancia al centroide de los
átomos pesados del T50 cristalográfico = (145.876, -24.851, 74.796) — que es exactamente el
centro de la caja de docking. C4 acepta si la corrida no falla y la distancia es <= 10 A.

También arma la tabla final (dG del modo 1, modos generados) y repite la regresión
pIC50 = f(dG) sobre los diez de la serie (sin T50 ni EFZ-Br), como pide cerrar el paso 02.
"""
import glob, json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
POSES = os.path.join(HERE, 'poses')
CENTRO_T50 = (145.876, -24.851, 74.796)

IC50 = {'GFA': 2.00, 'EFZ': 6.03, 'TBO': 14.13, 'TNK': 40.74, 'NVP': 89.13,
        'HBQ': 177.83, 'QNO47b': 213.80, 'U05': 398.11, 'ZZE': 630.96, 'QNO47c': 912.01}

def pIC50(nm):
    return 9 - math.log10(nm)

def modelo1(pdbqt):
    """Devuelve las líneas ATOM/HETATM del MODEL 1."""
    lineas, dentro = [], False
    for ln in pdbqt.splitlines():
        if ln.startswith('MODEL'):
            dentro = ln.strip() == 'MODEL 1'
            continue
        if ln.startswith('ENDMDL'):
            if dentro:
                break
            continue
        if dentro and (ln.startswith('ATOM') or ln.startswith('HETATM')):
            lineas.append(ln)
    return lineas

def centroide(lineas):
    """Centroide de átomos pesados de una lista de líneas PDBQT."""
    xs = ys = zs = 0.0
    n = 0
    for ln in lineas:
        try:
            x = float(ln[30:38]); y = float(ln[38:46]); z = float(ln[46:54])
        except ValueError:
            continue
        elem = ln[76:78].strip() if len(ln) > 77 else ''
        if not elem:
            elem = re.sub(r'[0-9]', '', ln[12:16].strip())[:1]
        if not elem or elem[0].upper() == 'H':
            continue
        xs += x; ys += y; zs += z
        n += 1
    if n == 0:
        return None
    return (xs / n, ys / n, zs / n)

def dist(a, b):
    return math.sqrt(sum((u - v) ** 2 for u, v in zip(a, b)))

filas = []
for jp in sorted(glob.glob(os.path.join(POSES, '*.json'))):
    lig = os.path.basename(jp)[:-5]
    if lig == 'T50':
        with open(os.path.join(POSES, lig + '_webina.pdbqt'), encoding='utf-8') as f:
            pose = f.read()
        c = centroide(modelo1(pose))
        dc = dist(c, CENTRO_T50) if c else None
        cc = '(' + ', '.join(f'{v:.2f}' for v in c) + ')' if c else '—'
        print(f'T50 (control, fuera del veredicto): dG={d["dG_kcal_mol"]:.3f}, '
              f'centroide={cc}, d(cent)={dc:.2f} A')
        continue
    with open(jp, encoding='utf-8') as f:
        d = json.load(f)
    with open(os.path.join(POSES, lig + '_webina.pdbqt'), encoding='utf-8') as f:
        pose = f.read()
    c = centroide(modelo1(pose))
    dc = dist(c, CENTRO_T50) if c else None
    filas.append(dict(lig=lig, dG=d['dG_kcal_mol'], modos=d['modos'],
                      cent=c, dCent=dc, okC4=(dc is not None and dc <= 10.0)))

print('=== C4: poses de Webina vs centroide de T50 cristal ===')
print(f'{"ligando":8s} | {"dG":>9s} | {"modos":>5s} | {"centroide pose":30s} | {"d(cent) A":>9s} | C4')
for r in sorted(filas, key=lambda r: -r['dG']):
    cc = '(' + ', '.join(f'{v:.2f}' for v in r['cent']) + ')' if r['cent'] else '—'
    dc = f'{r["dCent"]:.2f}' if r['dCent'] is not None else '—'
    print(f'{r["lig"]:8s} | {r["dG"]:9.3f} | {r["modos"]:5d} | {cc:30s} | {dc:>9s} | {"OK" if r["okC4"] else "FALLA"}')

todas_ok = all(r['okC4'] for r in filas)
print(f'\nC4: {"ACEPTA" if todas_ok else "NO ACEPTA"} (los once dentro de 10 A y sin fallas)')

print('\n=== Tabla final (orden por dG) ===')
print(f'{"ligando":8s} | {"dG":>9s} | {"modos":>5s} | {"IC50 nM":>8s} | {"pIC50":>6s}')
for r in sorted(filas, key=lambda r: -r['dG']):
    ic = IC50.get(r['lig'])
    print(f'{r["lig"]:8s} | {r["dG"]:9.3f} | {r["modos"]:5d} | '
          f'{(f"{ic:.2f}" if ic is not None else "—"):>8s} | {(f"{pIC50(ic):.3f}" if ic else "—"):>6s}')

# regresión pIC50 = f(dG) sobre los diez de la serie (como en el paso 02)
serie = [r for r in filas if r['lig'] in IC50]
xs = [r['dG'] for r in serie]
ys = [pIC50(IC50[r['lig']]) for r in serie]
n = len(xs)
mx, my = sum(xs) / n, sum(ys) / n
sxx = sum((x - mx) ** 2 for x in xs)
sxy = sum((x - mx) * (y - my) for y, x in zip(ys, xs))
b = sxy / sxx if sxx else 0.0
a = my - b * mx
yhat = [a + b * x for x in xs]
ss_res = sum((y - yh) ** 2 for y, yh in zip(ys, yhat))
ss_tot = sum((y - my) ** 2 for y in ys)
r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
r = math.copysign(math.sqrt(max(r2, 0)), b) if b != 0 else 0.0
t = r * math.sqrt(n - 2) / math.sqrt(max(1 - r * r, 1e-12)) if n > 2 else 0.0
print(f'\n=== pIC50 = f(dG) sobre los diez de la serie (n={n}) ===')
print(f'pendiente = {b:.3f}   ordenada = {a:.3f}   R2 = {r2:.3f}   r = {r:.3f}   t = {t:.2f}')

with open(os.path.join(HERE, 'resultados_c4.csv'), 'w', encoding='utf-8', newline='') as f:
    f.write('ligando,dG_kcal_mol,modos,cent_x,cent_y,cent_z,d_centroide_A,c4_ok\n')
    for r in sorted(filas, key=lambda r: r['lig']):
        cx, cy, cz = r['cent'] if r['cent'] else ('', '', '')
        f.write(f'{r["lig"]},{r["dG"]:.3f},{r["modos"]},{cx:.2f},{cy:.2f},{cz:.2f},'
                f'{r["dCent"]:.2f},{r["okC4"]}\n')
print('\nresultados_c4.csv escrito.')
