#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Consolidate Sorftime data for Makeup Mirror (lighted) market report."""
import json, glob, re, os
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
os.chdir(D)

def load_tail(path):
    with open(path) as f:
        txt = f.read()
    # skip the CLI banner lines
    i = txt.find('{')
    if i < 0: return None
    # find matching outermost JSON: try progressively from last '{'
    try:
        return json.loads(txt[i:])
    except Exception:
        # find first line that is '{' after banner
        lines = txt.splitlines()
        for idx, ln in enumerate(lines):
            if ln.strip() == '{':
                try: return json.loads('\n'.join(lines[idx:]))
                except Exception: continue
    return None

# ---- load 57 products with trends ----
prods = []
seen = set()
for f in sorted(glob.glob('prod_*.json')):
    d = load_tail(f)
    if not d or not d.get('Data'): continue
    for p in d['Data']:
        if p['Asin'] in seen: continue
        seen.add(p['Asin'])
        prods.append(p)
print('products loaded:', len(prods))

MONTH_START, MONTH_END = '2022-06', '2026-08'

def month_key(ym):  # ymd int 20240131 -> '2024-01'
    s = str(ym)
    return f"{s[:4]}-{s[4:6]}"

def last_day_map(trend):
    """trend: [date, val, ...] daily; keep last day per month."""
    out = {}
    if not trend: return out
    for i in range(0, len(trend)-1, 2):
        dt, val = trend[i], trend[i+1]
        mk = month_key(dt)
        if mk not in out or dt > out[mk][0]:
            out[mk] = (dt, val)
    return out

ALL_MONTHS = []
y, m = 2022, 6
while (y, m) <= (2026, 8):
    ALL_MONTHS.append(f"{y}-{m:02d}")
    m += 1
    if m > 12: y, m = y+1, 1
print('months:', len(ALL_MONTHS))

records = []
for p in prods:
    asin = p['Asin']
    um = last_day_map(p.get('ListingSalesVolumeOfMonthTrend'))
    rm = last_day_map(p.get('ListingSalesOfMonthTrend'))
    pm = last_day_map(p.get('PriceTrend'))
    units, rev, price = [], [], []
    for mk in ALL_MONTHS:
        u = um.get(mk, (None, None))[1]
        r = rm.get(mk, (None, None))[1]
        pr = pm.get(mk, (None, None))[1]
        units.append(None if u is None or u < 0 else u)
        rev.append(None if r is None or r < 0 else round(r/100, 2))
        price.append(None if pr is None or pr <= 0 else round(pr/100, 2))
    info = p.get('ProductInfo') or []
    info_d = {}
    if isinstance(info, list):
        for i in range(0, len(info)-1, 2):
            info_d[str(info[i])] = str(info[i+1])
    size = p.get('Size')
    dims_cm = []
    if size:
        try:
            dims_cm = [float(x) for x in re.findall(r'\d+\.?\d*', str(size))][:3]
        except Exception:
            dims_cm = []
    wkg = (p.get('Weight') or 0) / 1000.0
    records.append({
        'asin': asin, 'parent': p.get('ParentAsin'), 'title': p.get('Title'),
        'brand': p.get('Brand'), 'price': p.get('SalesPrice', 0)/100,
        'rating': p.get('Ratings'), 'reviews': p.get('RatingsCount'),
        'units30': p.get('ListingSalesVolumeOfMonth'), 'sales30': round((p.get('ListingSalesOfMonth') or 0)/100, 2),
        'sales365': round((p.get('ListingSalesVolumeOfYear') or 0)/100, 2),
        'seller': p.get('BuyboxSeller'), 'fba': bool(p.get('IsFBA')),
        'online': p.get('OnlineDate'), 'days': p.get('OnlineDays'),
        'dims_cm': dims_cm, 'weight_kg': round(wkg, 3),
        'fba_fee': round((p.get('FbaFee') or 0)/100, 2),
        'platform_fee': round((p.get('PlatformFee') or 0)/100, 2),
        'profit_rate': p.get('ProfitRate'),
        'photo': p.get('Photo'), 'varCount': p.get('VariationASINCount') or 0,
        'seller_count': p.get('SellerCount'),
        'stars': {1: p.get('OneStartRatings'), 2: p.get('TwoStartRatings'), 3: p.get('ThreeStartRatings'),
                  4: p.get('FourStartRatings'), 5: p.get('FiveStartRatings')},
        'info': info_d,
        'attribute': p.get('Attribute'),
        'feature': p.get('Feature'),
        'description': p.get('Description'),
        'units': units, 'rev': rev, 'price_m': price,
    })
print('records:', len(records))

# ---- year aggregates & rev6m ----
for r in records:
    r['rev6m'] = round(sum(v for v in r['rev'][-6:] if v), 2)
    r['units6m'] = sum(v for v in r['units'][-6:] if v)
    for yr in ('2026', '2025', '2024'):
        idx = [i for i, mk in enumerate(ALL_MONTHS) if mk.startswith(yr)]
        r[f'y{yr[2:]}u'] = sum(v for i, v in enumerate(r['units']) if i in idx and v)
        r[f'y{yr[2:]}r'] = round(sum(v for i, v in enumerate(r['rev']) if i in idx and v), 2)

records.sort(key=lambda r: -r['rev6m'])
asins57 = [l.strip() for l in open('asins57.txt') if l.strip()]
records.sort(key=lambda r: -r['rev6m'])

# ---- market aggregates ----
def agg(rs):
    tot_u = sum(r['units6m'] for r in rs)
    tot_g = sum(r['rev6m'] for r in rs)
    return tot_u, tot_g

tot_units, tot_gmv = agg(records)
valid = [r for r in records if r['rating']]
avg_rating = round(sum(r['rating'] for r in valid)/len(valid), 2)
prices = [r['price'] for r in records if r['price'] > 0]
avg_price = round(sum(prices)/len(prices), 2)
revs = sorted(r['reviews'] for r in records)
median_reviews = revs[len(revs)//2] if revs else 0

# brand share
brand_gmv = defaultdict(float)
for r in records: brand_gmv[r['brand']] += r['rev6m']
bg = sorted(brand_gmv.items(), key=lambda x: -x[1])
cr1 = bg[0][1]/tot_gmv*100 if tot_gmv else 0
cr3 = sum(v for _, v in bg[:3])/tot_gmv*100 if tot_gmv else 0
cr5 = sum(v for _, v in bg[:5])/tot_gmv*100 if tot_gmv else 0
hhi = round(sum((v/tot_gmv*100)**2 for _, v in bg)) if tot_gmv else 0
top_brands = bg[:10]

# price bands
def band(p):
    if p < 25: return '$0-25'
    if p < 50: return '$25-50'
    if p < 100: return '$50-100'
    if p < 150: return '$100-150'
    if p < 200: return '$150-200'
    return '$200+'
BAND_ORDER = ['$0-25', '$25-50', '$50-100', '$100-150', '$150-200', '$200+']
pb = {b: {'n': 0, 'gmv': 0, 'units': 0, 'new': 0, 'prices': [], 'ratings': []} for b in BAND_ORDER}
for r in records:
    b = band(r['price'] or 0)
    pb[b]['n'] += 1; pb[b]['gmv'] += r['rev6m']; pb[b]['units'] += r['units6m']
    pb[b]['prices'].append(r['price']); pb[b]['ratings'].append(r['rating'] or 0)
    if r['days'] and r['days'] <= 365: pb[b]['new'] += 1

# distributions
def dist_group(keyfn, topn=6):
    g = defaultdict(lambda: {'n': 0, 'units': 0, 'gmv': 0, 'prices': [], 'ratings': [], 'new': 0})
    for r in records:
        k = keyfn(r)
        d = g[k]; d['n'] += 1; d['units'] += r['units6m']; d['gmv'] += r['rev6m']
        d['prices'].append(r['price']); d['ratings'].append(r['rating'] or 0)
        if r['days'] and r['days'] <= 365: d['new'] += 1
    items = sorted(g.items(), key=lambda x: -x[1]['units'])
    rest = items[topn-1:]
    rows = []
    for k, d in items[:topn-1]:
        rows.append((k, d))
    if rest:
        rd = {'n': sum(d['n'] for _, d in rest), 'units': sum(d['units'] for _, d in rest),
              'gmv': sum(d['gmv'] for _, d in rest), 'new': sum(d['new'] for _, d in rest),
              'prices': [p for _, d in rest for p in d['prices']],
              'ratings': [x for _, d in rest for x in d['ratings']]}
        rows.append((f'其他({len(rest)}项)', rd))
    return rows

def rating_band(r):
    rt = r['rating'] or 0
    if rt == 0: return '无评分'
    if rt >= 4.8: return '4.8-5.0'
    if rt >= 4.6: return '4.6-4.79'
    if rt >= 4.4: return '4.4-4.59'
    if rt >= 4.2: return '4.2-4.39'
    if rt >= 4.0: return '4.0-4.19'
    return '其他'

def age_band(r):
    d = r['days'] or 0
    if d <= 180: return '0-6个月'
    if d <= 365: return '6-12个月'
    if d <= 730: return '1-2年'
    return '2年以上'

dists = {
    'price': dist_group(lambda r: band(r['price'] or 0), 7),
    'rating': dist_group(rating_band, 7),
    'seller_type': dist_group(lambda r: ('FBA' if r['fba'] else 'FBM'), 4),
    'brand': dist_group(lambda r: r['brand'], 7),
    'seller': dist_group(lambda r: (r['seller'] or 'NA'), 7),
    'age': dist_group(age_band, 5),
}

# scatter points (2026 units vs price)
scatter = []
for r in records:
    if not r['price'] or r['y26u'] <= 0: continue
    scatter.append({'x': r['y26u'], 'y': r['price'], 'brand': r['brand'], 'asin': r['asin'],
                    'title': (r['title'] or '')[:50], 'is_new': bool(r['days'] and r['days'] <= 365)})

# ---- category trend (24 months) ----
ts = load_tail('trend_sales.json'); tp = load_tail('trend_price.json')
cat_trend = {}
for name, f in (('units', ts), ('price', tp)):
    d = f.get('Data') or []
    series = {}
    for i in range(0, len(d)-1, 2):
        series[str(d[i])] = d[i+1]
    cat_trend[name] = series
cat_months = sorted(cat_trend['units'].keys())
cat_labels = [f"{k[:4]}-{k[4:]}" for k in cat_months]
cat_units = [cat_trend['units'].get(k) for k in cat_months]
cat_price = [round(cat_trend['price'].get(k, 0)/100, 2) for k in cat_months]

# ---- keywords ----
kw_core = []
for f in ('kw_main.json', 'kw_vanity.json', 'kw_led.json'):
    d = load_tail(f)
    if d and d.get('Data'):
        k = d['Data']
        kw_core.append({'kw': k['Keyword'], 'cn': k.get('KeywordCNName'), 'sv': k.get('SearchVolume'),
                        'sales90': k.get('SalesVolumeOf90D'), 'products': k.get('ProductCount'),
                        'cpc': k.get('Cpc'), 'cvr': k.get('ClickConversionRateD90'),
                        'scr': k.get('SearchConversionRate'), 'share': k.get('ShareClickRate')})
kw_pool, kw_seen = [], set()
for f in ('kw_list.json', 'kw_list2.json'):
    for k in json.load(open(f)):
        if k['kw'] in kw_seen: continue
        kw_seen.add(k['kw'])
        kw_pool.append(k)

# ---- customers say (reviews) ----
csay = []
for f in sorted(glob.glob('csay_*.json')):
    d = load_tail(f)
    if not d or not d.get('Data'): continue
    asin = f.replace('csay_', '').replace('.json', '')
    rec = next((r for r in records if r['asin'] == asin), None)
    det = d['Data'].get('Details') or []
    csay.append({'asin': asin, 'brand': rec['brand'] if rec else '', 'summary': d['Data'].get('CustomerSay'),
                 'details': [{'kw': x.get('Keyword'), 'content': x.get('Content'), 'mention': x.get('Mention'),
                              'pos': x.get('Positive'), 'neg': x.get('Negative')} for x in det]})

out = {
    'meta': {'category': 'Makeup Mirrors', 'nodeId': '3785121', 'keyword': 'makeup mirror with lights',
             'scope': 'US Amazon, lighted makeup mirrors, top 57 by 6mo GMV',
             'months': ALL_MONTHS, 'generated': '2026-09-01'},
    'records': records,
    'kpi': {'products': len(records), 'brands': len(brand_gmv), 'avg_rating': avg_rating,
            'median_reviews': median_reviews, 'avg_price': avg_price,
            'total_gmv': round(tot_gmv, 2), 'total_units': tot_units,
            'top3_share': round(cr3, 1), 'cr1': round(cr1, 1), 'cr3': round(cr3, 1),
            'cr5': round(cr5, 1), 'hhi': hhi},
    'price_bands': [{'band': b, 'n': pb[b]['n'], 'gmv_share': round(pb[b]['gmv']/tot_gmv*100, 1) if tot_gmv else 0,
                     'avg_price': round(sum(pb[b]['prices'])/len(pb[b]['prices']), 2) if pb[b]['prices'] else 0,
                     'new_n': pb[b]['new'], 'new_share': round(pb[b]['new']/pb[b]['n']*100, 1) if pb[b]['n'] else 0,
                     'avg_rating': round(sum(pb[b]['ratings'])/len(pb[b]['ratings']), 2) if pb[b]['ratings'] else 0}
                    for b in BAND_ORDER if pb[b]['n']],
    'top_brands': [{'brand': b, 'gmv': round(v, 2)} for b, v in top_brands],
    'dists': {k: [{'label': lbl, 'n': d['n'], 'units': d['units'], 'gmv': round(d['gmv'], 2),
                   'avg_price': round(sum(d['prices'])/len(d['prices']), 2) if d['prices'] else 0,
                   'avg_rating': round(sum(d['ratings'])/len(d['ratings']), 2) if d['ratings'] else 0,
                   'new_share': round(d['new']/d['n']*100, 1) if d['n'] else 0}
                  for lbl, d in v] for k, v in dists.items()},
    'scatter': scatter,
    'cat_trend': {'labels': cat_labels, 'units': cat_units, 'price': cat_price},
    'kw_core': kw_core, 'kw_pool': kw_pool, 'csay': csay,
}
with open('consolidated.json', 'w') as f:
    json.dump(out, f, ensure_ascii=False)
print('KPI:', json.dumps(out['kpi'], ensure_ascii=False))
print('saved consolidated.json', os.path.getsize('consolidated.json'))
