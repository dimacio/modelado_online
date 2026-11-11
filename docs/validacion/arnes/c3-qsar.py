#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C3 — QSAR del TP1 con los datos que produce la cadena libre.

Parte B (los 10 NNRTI): modelos pIC50 = a·d + b para cada descriptor de QuEtool, los dos
mejores combinados, análisis de ortogonalidad (matriz de correlaciones) y pruebas de
Fisher y Student a alfa = 0,05.

Parte A (las 15 TZD de Rawal 2005): los modelos que pide la guía sobre los descriptores
publicados (logP, mu(MNDO), Eoop) y su versión con los descriptores que calcula QuEtool
(clogP, dipolo, y demás), con el control del valor anómalo del compuesto 11.
"""
import csv, json, math, os
import numpy as np
from scipy import stats

AQUI = os.path.dirname(os.path.abspath(__file__))
ALFA = 0.05

# ── datos Parte B: descriptores de la app (corrida real) + IC50 ──
app = {f['nombre']: f for f in json.load(open(os.path.join(AQUI, 'descriptores_quetool_nnrti.json'), encoding='utf-8'))}
CAMPOS = ['mw', 'clogP', 'mr', 'tpsa', 'asa', 'dipolo', 'homo', 'lumo', 'gap']
IC50 = {'GFA': 2.00, 'EFZ': 6.03, 'TBO': 14.13, 'TNK': 40.74, 'NVP': 89.13,
        'HBQ': 177.83, 'QNO47b': 213.80, 'U05': 398.11, 'ZZE': 630.96, 'QNO47c': 912.01}
SERIE = list(IC50)

def limpia(s):
    return float(''.join(ch for ch in s if ch in '0123456789.-'))

desc = {}
for nom in SERIE:
    desc[nom] = {k: limpia(v) for k, v in zip(CAMPOS, app[nom]['celdas'])}

pIC = {n: 9 - math.log10(IC50[n]) for n in SERIE}

def lin1(x, y):
    res = stats.linregress(x, y)
    return dict(a=res.intercept, b=res.slope, r=res.rvalue, r2=res.rvalue**2, p=res.pvalue)

def lin2(X, y):
    """Mínimos cuadrados con 2 variables + término independiente; R2, R2aj, F, t."""
    n, k = X.shape[0], X.shape[1]
    A = np.column_stack([np.ones(n), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = A @ beta
    ssr = float(np.sum((y - yhat)**2)); sst = float(np.sum((y - y.mean())**2))
    r2 = 1 - ssr/sst; r2aj = 1 - (1-r2)*(n-1)/(n-k-1)
    F = (r2/k)/((1-r2)/(n-k-1))
    pF = 1 - stats.f.cdf(F, k, n-k-1)
    # errores estándar y t por coeficiente
    dof = n - k - 1
    s2 = ssr/dof
    cov = s2*np.linalg.inv(A.T @ A)
    se = np.sqrt(np.diag(cov))
    t = beta/se
    pt = [2*(1-stats.t.cdf(abs(tv), dof)) for tv in t]
    return dict(beta=beta, r2=r2, r2aj=r2aj, F=F, pF=pF, t=t, pt=pt, se=se)

print('=' * 100)
print('PARTE B — NNRTI (n = 10): pIC50 = a·descriptor + b, un descriptor por vez')
print('=' * 100)
print(f'{"descriptor":10s} {"a":>8s} {"b":>8s} {"R2":>7s} {"r":>7s} {"p":>8s} {"signif(0,05)":>12s}')
for k in CAMPOS:
    x = np.array([desc[n][k] for n in SERIE])
    m = lin1(x, np.array([pIC[n] for n in SERIE]))
    print(f'{k:10s} {m["b"]:8.3f} {m["a"]:8.3f} {m["r2"]:7.3f} {m["r"]:7.3f} {m["p"]:8.4f} {str(m["p"] < ALFA):>12s}')

print('\n== ortogonalidad: matriz de correlaciones entre descriptores ==')
print(f'{"":10s} ' + ' '.join(f'{k:>9s}' for k in CAMPOS))
for k1 in CAMPOS:
    fila = [desc[n][k1] for n in SERIE]
    print(f'{k1:10s} ' + ' '.join(f'{np.corrcoef(fila, [desc[n][k2] for n in SERIE])[0,1]:9.3f}' for k2 in CAMPOS))

print('\n== mejor modelo de 2 variables ==')
import itertools
mejor = None
for k1, k2 in itertools.combinations(CAMPOS, 2):
    X = np.array([[desc[n][k1], desc[n][k2]] for n in SERIE])
    m = lin2(X, np.array([pIC[n] for n in SERIE]))
    m['par'] = (k1, k2)
    if mejor is None or m['r2aj'] > mejor['r2aj']:
        mejor = m
print(f'mejor par: {mejor["par"]}  R2 = {mejor["r2"]:.3f}  R2aj = {mejor["r2aj"]:.3f}  '
      f'F = {mejor["F"]:.2f} (p = {mejor["pF"]:.4f})')
print(f'coeficientes: cte = {mejor["beta"][0]:.3f}, {mejor["par"][0]} = {mejor["beta"][1]:.4f} '
      f'(t = {mejor["t"][1]:.2f}, p = {mejor["pt"][1]:.4f}), {mejor["par"][1]} = {mejor["beta"][2]:.4f} '
      f'(t = {mejor["t"][2]:.2f}, p = {mejor["pt"][2]:.4f})')
tc = stats.t.ppf(1 - ALFA/2, 10 - 2 - 1)
print(f't crítico (7 gl, alfa 0,05) = {tc:.3f}')

print()
print('=' * 100)
print('PARTE A — TZD de Rawal 2005 (n = 15): pEC50 = f(logP, mu, Eoop) publicados')
print('=' * 100)
# tabla publicada en la guía (referencia-tp-qsar-docking.md, sección 2.3)
TZD = [
    # (id, EC50_uM, logP, mu, Eoop)
    (1, 0.204, 3.485, 3.169, 0.094), (2, 2.88, 2.607, 3.758, 0.006),
    (3, 0.576, 3.327, 4.463, 0.030), (4, 43.54, 2.897, 1.779, 0.034),
    (5, 6.43, 2.895, 3.376, 0.065), (6, 42.16, 3.600, 0.778, 0.009),
    (7, 57.78, 2.259, 3.147, 0.008), (8, 85.64, 2.261, 3.221, 0.006),
    (9, 262.69, 1.995, 2.424, 0.028), (10, 358.17, 1.746, 2.841, 0.051),
    (11, 6.88, 2.243, 0.012, 4.189), (12, 29.08, 2.601, 2.210, 0.081),
    (13, 7.80, 2.897, 2.209, 0.100), (14, 46.85, 3.525, 1.038, 0.005),
    (15, 5.53, 3.525, 2.467, 0.027),
]
pEC = np.array([6 - math.log10(t[1]) for t in TZD])
logP = np.array([t[2] for t in TZD]); mu = np.array([t[3] for t in TZD]); eoop = np.array([t[4] for t in TZD])
print(f'{"modelo":28s} {"R2":>7s} {"r":>7s} {"p":>8s} {"signif":>7s}')
for nom, x in [('pEC50 ~ logP', logP), ('pEC50 ~ mu', mu), ('pEC50 ~ Eoop', eoop)]:
    m = lin1(x, pEC)
    print(f'{nom:28s} {m["r2"]:7.3f} {m["r"]:7.3f} {m["p"]:8.4f} {str(m["p"] < ALFA):>7s}')
for k1, k2, nom in [(logP, mu, 'pEC50 ~ logP + mu'), (logP, eoop, 'pEC50 ~ logP + Eoop'), (mu, eoop, 'pEC50 ~ mu + Eoop')]:
    m = lin2(np.column_stack([k1, k2]), pEC)
    print(f'{nom:28s} {m["r2"]:7.3f} {"":>7s} {m["pF"]:8.4f} {str(m["pF"] < ALFA):>7s}   F = {m["F"]:.2f}')
m3 = lin2(np.column_stack([logP, mu, eoop]), pEC)
print(f'{"pEC50 ~ logP + mu + Eoop":28s} {m3["r2"]:7.3f} {"":>7s} {m3["pF"]:8.4f} {str(m3["pF"] < ALFA):>7s}   F = {m3["F"]:.2f}')
print('\nortogonalidad (publicados):')
for a, b, na, nb in [(logP, mu, 'logP', 'mu'), (logP, eoop, 'logP', 'Eoop'), (mu, eoop, 'mu', 'Eoop')]:
    print(f'r({na},{nb}) = {np.corrcoef(a, b)[0,1]:.3f}')

print('\n== Parte A con descriptores de QuEtool (clogP, dipolo del CSV del repo) ==')
csv_path = os.path.join(AQUI, '..', 'tzd_quetool.csv')
# se lee del CSV original del repo
repo_csv = r'G:\Mi unidad\modelado_online\data\descriptores-gfn2-rdkit.csv'
filas_tzd = list(csv.DictReader(open(repo_csv, encoding='utf-8')))
clogP_t = np.array([float(f['clogP']) for f in filas_tzd])
dip_t = np.array([float(f['dipolo']) for f in filas_tzd])
pEC_t = np.array([float(f['pEC50']) for f in filas_tzd])
print(f'{"modelo":28s} {"R2":>7s} {"r":>7s} {"p":>8s} {"signif":>7s}')
for nom, x in [('pEC50 ~ clogP (QuEtool)', clogP_t), ('pEC50 ~ dipolo (QuEtool)', dip_t)]:
    m = lin1(x, pEC_t)
    print(f'{nom:28s} {m["r2"]:7.3f} {m["r"]:7.3f} {m["p"]:8.4f} {str(m["p"] < ALFA):>7s}')
m = lin2(np.column_stack([clogP_t, dip_t]), pEC_t)
print(f'{"pEC50 ~ clogP + dipolo":28s} {m["r2"]:7.3f} {"":>7s} {m["pF"]:8.4f} {str(m["pF"] < ALFA):>7s}   F = {m["F"]:.2f}')
print(f'\ndipolo QuEtool del compuesto 11: {dip_t[10]:.2f} D (la tabla publicada dice mu = 0,012; ver anomalía)')
print(f'r(clogP, dipolo) = {np.corrcoef(clogP_t, dip_t)[0,1]:.3f}')
