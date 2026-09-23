#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble final report: _shell.html + REPORT_DATA + app.js -> Makeup-Mirror-with-Lights_20260901.html"""
import json, os

D = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(D, 'data'))
c = json.load(open('consolidated.json'))
c['records'] = json.load(open('records_coupled.json'))
a = json.load(open('analysis.json'))

recs = []
for r in c['records']:
    info = r.get('info') or {}
    sp = ' · '.join(f"{k}: {v}" for k, v in list(info.items())[:8]) if info else ''
    photo = r.get('photo')
    if isinstance(photo, list):
        photo = photo[0] if photo else ''
    recs.append({
        'asin': r['asin'], 'parent': r['parent'], 'image': photo,
        'title': r['title'], 'brand': r['brand'], 'price': r['price'],
        'rating': r['rating'], 'reviews': r['reviews'], 'units30': r['units30'],
        'rev6m': r['rev6m'], 'units6m': r['units6m'],
        'y26u': r['y26u'], 'y26r': r['y26r'], 'y25u': r['y25u'], 'y25r': r['y25r'],
        'y24u': r['y24u'], 'y24r': r['y24r'],
        'days': r['days'], 'online': r['online'], 'dims': r['dims_cm'], 'wt': r['weight_kg'],
        'fba': r['fba'], 'seller': r['seller'], 'varCount': r['varCount'],
        'fbaFee': r['fba_fee'], 'platformFee': r['platform_fee'], 'profitRate': r['profit_rate'],
        'units': r['units'], 'rev': r['rev'], 'price_m': r['price_m'],
        'coupling': r['_coupling'], 'sp': sp,
    })

DATA = {
    'meta': c['meta'], 'kpi': c['kpi'], 'records': recs,
    'price_bands': c['price_bands'], 'top_brands': c['top_brands'],
    'dists': c['dists'], 'scatter': c['scatter'], 'cat_trend': c['cat_trend'],
    'kw_core': c['kw_core'], 'csay': c['csay'],
    'score_rows': a['score_rows'], 'score_total': a['score_total'], 'score_100': a['score_100'],
    'decision': a['decision'], 'head': a['head'],
    'kano': a['kano'], 'att_rows': a['att_rows'], 'combo_rows': a['combo_rows'],
    'seasonal': a['seasonal'], 'fc': a['fc'], 'peak_months': a['peak_months'], 'yoy': a['yoy'],
    'pain_rows': a['pain_rows'], 'pos_rows': a['pos_rows'],
    'parent_rows': a['parent_rows'], 'ppc': a['ppc'],
}
DATA_JSON = json.dumps(DATA, ensure_ascii=False).replace('</', '<\\/')

shell = open('../_shell.html').read()
app_js = open('../app.js').read().replace('</script>', '<\\/script>')

final = (shell
         + '\n<script>\nwindow.REPORT_DATA = ' + DATA_JSON + ';\n</script>'
         + '\n<script>\n' + app_js + '\n</script>'
         + '\n</body>\n</html>\n')

out = os.path.join(D, 'Makeup-Mirror-with-Lights_20260901.html')
open(out, 'w').write(final)
print('written:', out, len(final), 'bytes')
