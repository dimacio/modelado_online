#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C5 — Interacciones de la pose 1 de cada ligando contra 2B6A, replicando EXACTAMENTE
el analizar() de la pestaña Complejo de QuEtool (app/index.html): mismos umbrales, mismos
tipos de átomo, mismas definiciones de anillos y grupos cargados. Salidas: CSV por
ligando (mismo formato que el export de la app), tabla de doble entrada ligando x residuo
y contraste con los residuos del sitio NNRTI de la bibliografía."""
import glob, json, math, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
REC_PATH = os.path.join(AQUI, 'receptor_2B6A.pdbqt')
POSES = os.path.join(AQUI, 'poses')

TIPO_ELEM = {'A':'C','C':'C','N':'N','NA':'N','NS':'N','O':'O','OA':'O','OS':'O','S':'S','SA':'S',
             'HD':'H','H':'H','F':'F','CL':'Cl','BR':'Br','I':'I','P':'P','MG':'Mg','ZN':'Zn','MN':'Mn','CA':'Ca','FE':'Fe'}
ACEPTORES = {'OA','NA','SA'}
ANILLOS_RES = {
    'PHE': [['CG','CD1','CE1','CZ','CE2','CD2']],
    'TYR': [['CG','CD1','CE1','CZ','CE2','CD2']],
    'HIS': [['CG','ND1','CE1','NE2','CD2']],
    'TRP': [['CG','CD1','NE1','CE2','CD2'], ['CD2','CE2','CZ2','CH2','CZ3','CE3']],
}
CATION_RES = {'ARG': ['NE','NH1','NH2'], 'LYS': ['NZ'], 'HIS': ['ND1','CE1','NE2']}
ANION_RES = {'ASP': ['OD1','OD2'], 'GLU': ['OE1','OE2']}

SITIO = {'LEU100','LYS101','LYS103','VAL106','VAL179','ILE180','TYR181','TYR188','VAL189',
         'GLY190','PHE227','TRP229','LEU234','HIS235','PRO236','TYR318'}

def leer_pdbqt(txt):
    at = []
    for l in txt.splitlines():
        if not l.startswith(('ATOM', 'HETATM')):
            continue
        if len(l) < 79:
            continue
        t = l[77:79].strip() or l[12:14].strip()
        at.append(dict(
            nombre=l[12:16].strip(), res=l[17:20].strip(), cad=l[21:22].strip(),
            num=int(l[22:26] or 0), x=float(l[30:38]), y=float(l[38:46]), z=float(l[46:54]),
            t=t, el=(TIPO_ELEM.get(t.upper()) or t[:1])))
    return at

def dist(a, b): return math.hypot(a['x']-b['x'], a['y']-b['y'], a['z']-b['z'])
def resta(a, b): return [a['x']-b['x'], a['y']-b['y'], a['z']-b['z']]
def punto(u, v): return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]
def norma(u): return math.hypot(*u)
def angulo_en(a, b, c):
    u, v = resta(a, b), resta(c, b)
    d = punto(u, v) / (norma(u) * norma(v) or 1)
    return math.degrees(math.acos(max(-1, min(1, d))))
def centroide(ps):
    return dict(x=sum(p['x'] for p in ps)/len(ps), y=sum(p['y'] for p in ps)/len(ps), z=sum(p['z'] for p in ps)/len(ps))
def normal_newell(ps):
    nx = ny = nz = 0.0
    for i in range(len(ps)):
        a, b = ps[i], ps[(i+1) % len(ps)]
        nx += (a['y']-b['y'])*(a['z']+b['z']); ny += (a['z']-b['z'])*(a['x']+b['x']); nz += (a['x']-b['x'])*(a['y']+b['y'])
    m = math.hypot(nx, ny, nz) or 1
    return [nx/m, ny/m, nz/m]
def radio_enlace(a, b):
    g = lambda e: 0.37 if e == 'H' else (1.05 if e in ('S','P','Cl','Br','I') else 0.77)
    return g(a['el']) + g(b['el']) + 0.45
def conectar(at):
    ady = [[] for _ in at]
    for i in range(len(at)):
        for j in range(i+1, len(at)):
            if dist(at[i], at[j]) < radio_enlace(at[i], at[j]):
                ady[i].append(j); ady[j].append(i)
    return ady

def anillos_ligando(at, ady):
    salida, vistos = [], set()
    for s in range(len(at)):
        if at[s]['el'] == 'H':
            continue
        pila = [[s, [s]]]
        while pila:
            u, cam = pila.pop()
            for v in ady[u]:
                if at[v]['el'] == 'H':
                    continue
                if v == s and 5 <= len(cam) <= 6:
                    k = ','.join(map(str, sorted(cam)))
                    if k not in vistos:
                        vistos.add(k); salida.append(cam[:])
                elif v > s and v not in cam and len(cam) < 6:
                    pila.append([v, cam + [v]])
    out = []
    for ciclo in salida:
        ps = [at[i] for i in ciclo]
        if sum(1 for a in ps if a['t'] in ('A', 'NA')) < 3:
            continue
        c = centroide(ps); n = normal_newell(ps)
        if all(abs(punto(resta(p, c), n)) < 0.3 for p in ps):
            out.append(dict(idx=ciclo, c=c, n=n))
    return out

def anillos_receptor(at):
    por = {}
    for i, a in enumerate(at):
        por.setdefault((a['cad'], a['num'], a['res']), []).append(i)
    salida = []
    for k, idxs in por.items():
        res = k[2]
        for nombres in ANILLOS_RES.get(res, []):
            ps = []
            ok = True
            for nm in nombres:
                f = [i for i in idxs if at[i]['nombre'] == nm]
                if not f:
                    ok = False; break
                ps.append(f[0])
            if not ok:
                continue
            pts = [at[i] for i in ps]
            salida.append(dict(idx=ps, c=centroide(pts), n=normal_newell(pts), res=at[ps[0]]))
    return salida

def cargas_receptor(at):
    por = {}
    for i, a in enumerate(at):
        por.setdefault((a['cad'], a['num'], a['res']), []).append(i)
    g = []
    for k, idxs in por.items():
        res = k[2]
        for tabla, signo in [(CATION_RES, 1), (ANION_RES, -1)]:
            nombres = tabla.get(res)
            if not nombres:
                continue
            ps = [i for i in idxs if at[i]['nombre'] in nombres]
            if ps:
                g.append(dict(c=centroide([at[i] for i in ps]), signo=signo, ref=at[ps[0]]))
    return g

def cargas_ligando(at, ady):
    g = []
    for i, a in enumerate(at):
        vecinos = [at[j] for j in ady[i]]
        if a['el'] == 'C':
            ox = [j for j in ady[i] if at[j]['el'] == 'O']
            if len(ox) == 2 and not any(any(at[h]['el'] == 'H' for h in ady[j]) for j in ox):
                g.append(dict(c=centroide([a] + [at[j] for j in ox]), signo=-1, ref=a))
            ns = [j for j in ady[i] if at[j]['el'] == 'N']
            if len(ns) >= 3:
                g.append(dict(c=centroide([a] + [at[j] for j in ns]), signo=1, ref=a))
        if a['el'] in ('S', 'P') and sum(1 for j in ady[i] if at[j]['el'] == 'O') >= 3:
            g.append(dict(c=centroide([a] + [at[j] for j in ady[i] if at[j]['el'] == 'O']), signo=-1, ref=a))
        if a['el'] == 'N':
            pes = [j for j in ady[i] if at[j]['el'] != 'H']
            hs = [j for j in ady[i] if at[j]['el'] == 'H']
            if len(pes) >= 4 or (len(pes) == 1 and len(hs) >= 3):
                g.append(dict(c=dict(a), signo=1, ref=a))
    return g

def donantes(at, ady):
    d = []
    for i, a in enumerate(at):
        if a['el'] not in ('N', 'O', 'S'):
            continue
        for j in ady[i]:
            if at[j]['el'] == 'H':
                d.append(dict(D=i, H=j))
    return d

def etiqueta(a):
    return f"{a['res']}{a['num']}{' ' + a['cad'] if a['cad'] else ''}"

def analizar(rec, lig):
    out = []
    lim = 6.5
    bb = []
    for k in ('x', 'y', 'z'):
        vals = [a[k] for a in lig]
        bb.append([min(vals) - lim, max(vals) + lim])
    cerca = []
    for i, a in enumerate(rec):
        if bb[0][0] < a['x'] < bb[0][1] and bb[1][0] < a['y'] < bb[1][1] and bb[2][0] < a['z'] < bb[2][1]:
            cerca.append(i)

    hrec = {}
    for i in cerca:
        if rec[i]['el'] != 'H':
            continue
        mejor, dm = -1, 1.3
        for j in cerca:
            if rec[j]['el'] != 'H' and dist(rec[i], rec[j]) < dm:
                dm = dist(rec[i], rec[j]); mejor = j
        if mejor >= 0:
            hrec.setdefault(mejor, []).append(i)

    adyL = conectar(lig)

    # puentes H: ligando dona
    for dc in donantes(lig, adyL):
        D, H = dc['D'], dc['H']
        for j in cerca:
            if rec[j]['t'] not in ACEPTORES:
                continue
            dDA = dist(lig[D], rec[j]); dHA = dist(lig[H], rec[j])
            ang = angulo_en(lig[D], lig[H], rec[j])
            if dDA <= 3.5 and dHA <= 2.6 and ang >= 130:
                out.append(dict(tipo='puente H', residuo=etiqueta(rec[j]), atRes=rec[j]['nombre'],
                                atLig=lig[D]['nombre'] or lig[D]['el'], d=dDA, ang=ang, nota='ligando dona'))
    # puentes H: receptor dona
    for Di, Hs in hrec.items():
        for H in Hs:
            for k in range(len(lig)):
                if lig[k]['t'] not in ACEPTORES:
                    continue
                dDA = dist(rec[Di], lig[k]); dHA = dist(rec[H], lig[k])
                ang = angulo_en(rec[Di], rec[H], lig[k])
                if dDA <= 3.5 and dHA <= 2.6 and ang >= 130:
                    out.append(dict(tipo='puente H', residuo=etiqueta(rec[Di]), atRes=rec[Di]['nombre'],
                                    atLig=lig[k]['nombre'] or lig[k]['el'], d=dDA, ang=ang, nota='receptor dona'))

    # hidrofóbicas
    apolar = lambda a, ady, todos: a['el'] == 'C' and not any(todos[j]['el'] in ('N', 'O') for j in ady)
    mejores = {}
    for k in range(len(lig)):
        if not apolar(lig[k], adyL[k], lig):
            continue
        for j in cerca:
            if rec[j]['el'] != 'C':
                continue
            vecinos = [m for m in cerca if m != j and dist(rec[j], rec[m]) < 1.8]
            if any(rec[m]['el'] in ('N', 'O') for m in vecinos):
                continue
            d = dist(lig[k], rec[j])
            if d > 4.0:
                continue
            key = etiqueta(rec[j])
            if key not in mejores or mejores[key]['d'] > d:
                mejores[key] = dict(tipo='hidrofóbica', residuo=key, atRes=rec[j]['nombre'],
                                    atLig=lig[k]['nombre'] or lig[k]['el'], d=d, ang=None, nota='')
    out.extend(mejores.values())

    # pi-pi
    anL = anillos_ligando(lig, adyL)
    anR = anillos_receptor([rec[i] for i in cerca])
    for al in anL:
        for ar in anR:
            d = dist(al['c'], ar['c'])
            if d > 5.5:
                continue
            ang = math.degrees(math.acos(max(-1, min(1, abs(punto(al['n'], ar['n']))))))
            v = resta(ar['c'], al['c'])
            nv = norma(v) or 1
            desp = min(nv * math.sin(math.acos(min(1, abs(punto(v, al['n'])) / nv))),
                       nv * math.sin(math.acos(min(1, abs(punto(v, ar['n'])) / nv))))
            paralela = ang < 30 and desp <= 2.0
            enT = ang > 50 and desp <= 3.0
            if paralela or enT:
                out.append(dict(tipo='pi-pi', residuo=etiqueta(ar['res']), atRes='anillo', atLig='anillo',
                                d=d, ang=ang, nota='paralela' if paralela else 'en T'))

    # halógenos
    for k in range(len(lig)):
        if lig[k]['el'] not in ('Cl', 'Br', 'I'):
            continue
        c = next((j for j in adyL[k] if lig[j]['el'] == 'C'), None)
        if c is None:
            continue
        for j in cerca:
            if rec[j]['el'] not in ('N', 'O'):
                continue
            d = dist(lig[k], rec[j])
            if d > 4.0:
                continue
            ang = angulo_en(lig[c], lig[k], rec[j])
            if ang >= 140:
                out.append(dict(tipo='halógeno', residuo=etiqueta(rec[j]), atRes=rec[j]['nombre'],
                                atLig=lig[k]['el'], d=d, ang=ang, nota=''))

    # puentes salinos
    cR = cargas_receptor([rec[i] for i in cerca])
    cL = cargas_ligando(lig, adyL)
    for gl in cL:
        for gr in cR:
            if gl['signo'] == gr['signo']:
                continue
            d = dist(gl['c'], gr['c'])
            if d > 5.0:
                continue
            out.append(dict(tipo='puente salino', residuo=etiqueta(gr['ref']), atRes=gr['ref']['nombre'],
                            atLig=gl['ref']['nombre'] or gl['ref']['el'], d=d, ang=None,
                            nota='ligando aniónico' if gl['signo'] < 0 else 'ligando catiónico'))

    orden = {'puente H': 0, 'puente salino': 1, 'pi-pi': 2, 'halógeno': 3, 'hidrofóbica': 4}
    out.sort(key=lambda x: (orden[x['tipo']], x['d'] if x['d'] is not None else 9))
    return out

# ── corrida ──
rec = leer_pdbqt(open(REC_PATH, encoding='utf-8').read())
print(f'receptor: {len(rec)} átomos leídos')
SALIDA = os.path.join(AQUI, 'interacciones')
os.makedirs(SALIDA, exist_ok=True)

filas_tabla = {}
residuos_total = set()
for p in sorted(glob.glob(os.path.join(POSES, '*_webina.pdbqt'))):
    nom = os.path.basename(p)[:-len('_webina.pdbqt')]
    txt = open(p, encoding='utf-8').read()
    # MODEL 1
    lineas, dentro = [], False
    for l in txt.splitlines():
        if l.startswith('MODEL'):
            dentro = l.strip() == 'MODEL 1'; continue
        if l.startswith('ENDMDL'):
            if dentro: break
            continue
        if dentro:
            lineas.append(l)
    lig = leer_pdbqt('\n'.join(lineas))
    inter = analizar(rec, lig)
    # CSV por ligando, formato de la app
    cab = 'tipo,residuo,atomo_receptor,atomo_ligando,distancia_A,angulo_grados,nota'
    with open(os.path.join(SALIDA, nom + '_interacciones.csv'), 'w', encoding='utf-8', newline='') as f:
        f.write(cab + '\n')
        for x in inter:
            f.write(','.join([x['tipo'], x['residuo'], x['atRes'], x['atLig'],
                              f"{x['d']:.3f}" if x['d'] is not None else '',
                              f"{x['ang']:.1f}" if x['ang'] is not None else '', x['nota']]) + '\n')
    # residuos por tipo
    por_tipo = {}
    for x in inter:
        por_tipo.setdefault(x['tipo'], set()).add(x['residuo'])
    filas_tabla[nom] = dict(inter=inter, n=len(inter), por_tipo=por_tipo,
                            residuos=set(x['residuo'] for x in inter))
    residuos_total |= filas_tabla[nom]['residuos']
    print(f'{nom:8s} {len(inter):3d} interacciones  {sorted(por_tipo.keys())}')

# tabla de doble entrada: ligandos x residuos contactados
res_cols = sorted(residuos_total, key=lambda r: (int(re.sub(r'\D', '', r) or 0), r))
print('\n== tabla de doble entrada (ligando x residuo; S = residuo del sitio NNRTI) ==')
hdr = 'ligando  ' + '  '.join(f'{r:>7s}' for r in res_cols)
print(hdr)
for nom in sorted(filas_tabla):
    fila = ' '.join(('X' if r in filas_tabla[nom]['residuos'] else '.') .rjust(7) for r in res_cols)
    print(f'{nom:8s} {fila}')

# contraste con el sitio bibliográfico
print('\n== contraste con los residuos del sitio NNRTI (bibliografía) ==')
print(f'{"ligando":8s} {"en sitio":>8s} {"total":>5s} {"%":>5s}   residuos del sitio contactados')
for nom in sorted(filas_tabla):
    rs = filas_tabla[nom]['residuos']
    rs_base = {r.split(' ')[0] for r in rs}
    en = rs_base & SITIO
    print(f'{nom:8s} {len(en):8d} {len(rs):5d} {100*len(en)/max(len(rs),1):5.0f}   {sorted(en, key=lambda r: int(r[3:]))}')

json.dump({n: dict(n=f['n'], por_tipo={k: sorted(v) for k, v in f['por_tipo'].items()},
                   residuos=sorted(f['residuos']))
           for n, f in filas_tabla.items()},
          open(os.path.join(SALIDA, 'resumen_interacciones.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print('\nresumen_interacciones.json escrito.')
