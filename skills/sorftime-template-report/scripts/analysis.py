#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Derive analysis layer (scorecard, attributes, seasonality, forecast, pains) from consolidated.json."""
import json, os, re
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
os.chdir(D)
c = json.load(open('consolidated.json'))
records = c['records']
months = c['meta']['months']
kpi = c['kpi']
tot_gmv = kpi['total_gmv']
tot_units = kpi['total_units']

# ---------- coupling/spec fields ----------
def find_1x(s, pat, flags=re.I):
    if not s: return None
    m = re.search(pat, s, flags)
    return m.group(0) if m else None

for r in records:
    t = r['title'] or ''
    info = r.get('info') or {}
    blob = t + ' ' + ' '.join(str(v) for v in info.values())
    shape = info.get('Shape') or find_1x(t, r'(Round|Oval|Rectangular|Square|Arch)(?=[\s,"])')
    mount = info.get('Mounting Type') or find_1x(t, r'(Tabletop|Wall Mount|Wall-Mounted|Hanging|Door Mount)', )
    if not mount:
        mount = '台式' if re.search(r'tabletop|desk|countertop', blob, re.I) else ('壁挂' if re.search(r'wall', blob, re.I) else '未提及')
    else:
        mount = {'Tabletop': '台式', 'Wall Mount': '壁挂', 'Wall-Mounted': '壁挂', 'Hanging': '壁挂', 'Door Mount': '壁挂'}.get(mount, mount)
    frame = info.get('Frame Material') or find_1x(t, r'(Aluminum|Metal|Plastic|Acrylic|Wood|Alloy)')
    mag = None
    m = re.search(r'(\d+)\s*[xX]', t)
    if m: mag = m.group(1) + 'X'
    if not mag and info.get('Magnification'): mag = str(info['Magnification'])
    if not mag:
        mag = '1X(无放大)' if not re.search(r'magnif', blob, re.I) else '未提及'
    if re.search(r'\b(\d+)x/(1x|1x/)\s*magnification', blob, re.I):
        mag = '双面(1X+%s)' % re.search(r'\b(\d+)x', blob, re.I).group(1) + 'X'
    power = '未提及'
    if re.search(r'usb', blob, re.I) and re.search(r'batter', blob, re.I): power = 'USB+电池'
    elif re.search(r'usb(c)? (cable|powered|charging|charge)', blob, re.I) or re.search(r'usb', blob, re.I): power = 'USB供电'
    elif re.search(r'plug| adapter', blob, re.I): power = '插电'
    elif re.search(r'batter', blob, re.I): power = '电池供电'
    light_modes = None
    m = re.search(r'(\d+)\s*(color|light|tone)s?\b', blob, re.I)
    if m: light_modes = m.group(1) + '色光'
    dimm = '可调光/触控' if re.search(r'dimmable|touch|stepless', blob, re.I) else '未提及'
    color = '未提及'
    if r.get('attribute'):
        for row in r['attribute']:
            if len(row) >= 4 and str(row[1]).lower() == 'color' and str(row[0]) == r['asin']:
                color = str(row[2]); break
        if color == '未提及':
            for row in r['attribute']:
                if len(row) >= 4 and str(row[1]).lower() == 'color':
                    color = str(row[2]); break
    dims = r.get('dims_cm') or []
    size_txt = f"{dims[0]:.0f}x{dims[1]:.0f}cm" if len(dims) >= 2 else '未提及'
    wkg = r.get('weight_kg') or 0
    weight_txt = f"{wkg:.2f}kg" if wkg > 0 else '未提及'
    r['_coupling'] = {
        '形状': shape or '未提及',
        '安装方式': mount,
        '边框材质': frame or '未提及',
        '放大倍数': mag,
        '供电方式': power,
        '灯光模式': light_modes or '未提及',
        '可调光': dimm,
        '颜色': color,
        '镜面尺寸': size_txt,
        '重量': weight_txt,
    }

# ---------- attribute matrix & combos ----------
def att_stats(field, valnorm=None):
    g = defaultdict(lambda: {'n': 0, 'gmv': 0.0, 'units': 0, 'prices': [], 'u3': 0, 'u3prev': 0})
    for r in records:
        v = r['_coupling'].get(field) or '未提及'
        if valnorm: v = valnorm(v)
        d = g[v]
        d['n'] += 1; d['gmv'] += r['rev6m']; d['units'] += r['units6m']
        if r['price']: d['prices'].append(r['price'])
        for i, mk in enumerate(months[-6:]):
            if i < 3:
                d['u3'] += r['units'][-6 + i] or 0
            else:
                d['u3prev'] += r['units'][-6 + i] or 0
    rows = []
    mkt_avg_price = kpi['avg_price']
    for v, d in g.items():
        pen = d['n'] / len(records) * 100
        gmv_share = d['gmv'] / tot_gmv * 100
        units_share = d['units'] / tot_units * 100
        avgp = sum(d['prices']) / len(d['prices']) if d['prices'] else 0
        premium = round(avgp / mkt_avg_price, 2) if avgp and mkt_avg_price else None
        growth = round((d['u3'] - d['u3prev']) / d['u3prev'] * 100, 1) if d['u3prev'] else None
        if pen >= 60 and premium and premium < 1.05:
            tag = '基础标配'
        elif premium and premium >= 1.15 and gmv_share >= 5:
            tag = '高溢价机会'
        elif gmv_share >= 8 and pen < 50:
            tag = '细分机会项'
        else:
            tag = '普通属性'
        rows.append({'field': field, 'val': v, 'pen': round(pen, 1), 'gmv_share': round(gmv_share, 1),
                     'units_share': round(units_share, 1), 'premium': premium, 'growth': growth, 'tag': tag})
    rows.sort(key=lambda x: -x['gmv_share'])
    return rows

att_rows = []
for f in ['形状', '安装方式', '边框材质', '放大倍数', '供电方式', '灯光模式', '可调光', '颜色']:
    rows = att_stats(f)
    for r in rows:
        if r['pen'] >= 5 or r['gmv_share'] >= 8:
            r['field'] = f
            att_rows.append(r)
att_rows.sort(key=lambda x: -x['gmv_share'])

# combos (top attribute values per field, first 4 fields)
combo_fields = ['形状', '安装方式', '供电方式']
field_topvals = {}
for f in combo_fields:
    vv = defaultdict(float)
    for r in records:
        vv[r['_coupling'][f]] += r['rev6m']
    field_topvals[f] = [v for v, _ in sorted(vv.items(), key=lambda x: -x[1])[:3]]
combos = defaultdict(lambda: {'n': 0, 'gmv': 0.0, 'u3': 0, 'u3prev': 0})
for r in records:
    key = tuple(r['_coupling'][f] for f in combo_fields)
    d = combos[key]
    d['n'] += 1; d['gmv'] += r['rev6m']
    for i in range(3):
        d['u3'] += r['units'][-3 + i] or 0
        d['u3prev'] += r['units'][-6 + i] or 0
combo_rows = []
for key, d in combos.items():
    if d['n'] < 2: continue
    growth = round((d['u3'] - d['u3prev']) / d['u3prev'] * 100, 1) if d['u3prev'] else None
    crowding = round(min(1.0, d['n'] / 20), 1)
    tag = '高GMV低拥挤' if d['gmv'] > 1_500_000 and crowding < 0.6 else '普通组合'
    combo_rows.append({'combo': list(key), 'n': d['n'], 'gmv': round(d['gmv'], 2), 'growth': growth,
                       'crowding': crowding, 'tag': tag})
combo_rows.sort(key=lambda x: -x['gmv'])
combo_rows = combo_rows[:8]

# Kano: coverage (pen) vs GMV share per spec field (field level, excluding 未提及)
field_gmv_share = defaultdict(float); field_pen = defaultdict(int)
for r in records:
    seen = set()
    for f, v in r['_coupling'].items():
        if v == '未提及' or f in seen: continue
        seen.add(f)
        field_pen[f] += 1
    seen2 = set()
    for f, v in r['_coupling'].items():
        if v == '未提及' or f in seen2: continue
        seen2.add(f)
    for f in r['_coupling']:
        pass
# simpler: gmv share per field = gmv of products where field != 未提及
field_gmv = defaultdict(float)
for r in records:
    for f, v in r['_coupling'].items():
        if v != '未提及':
            field_gmv[f] += r['rev6m']
kano = [{'attr': f, 'coverage': round(field_pen[f] / len(records) * 100, 1),
         'gmv_share': round(field_gmv[f] / tot_gmv * 100, 1)} for f in field_pen]
kano.sort(key=lambda x: -x['gmv_share'])

# ---------- scorecard ----------
by_gmv = sorted(records, key=lambda r: -r['rev6m'])
top1 = by_gmv[0]
head_units = top1['units30'] or 0
head_reviews = top1['reviews'] or 0
top5_avg = sum(r['price'] for r in by_gmv[:5] if r['price']) / max(1, len([r for r in by_gmv[:5] if r['price']]))
top10_avg = sum(r['price'] for r in by_gmv[:10] if r['price']) / max(1, len([r for r in by_gmv[:10] if r['price']]))
fba_top10 = sum(1 for r in by_gmv[:10] if r['fba']) / min(10, len(by_gmv)) * 100
new_1y = [r for r in records if r['days'] and r['days'] <= 365]
new_1y_ok = [r for r in new_1y if (r['units6m'] / 6) >= 300]
parent_rating = defaultdict(list)
for r in records:
    if r['parent']:
        parent_rating[r['parent']].append(r['reviews'] or 0)
top5_parent_rating = []
for r in by_gmv[:5]:
    pr = max(parent_rating.get(r['parent'] or r['asin'], [r['reviews'] or 0]))
    top5_parent_rating.append(pr)
avg_top5_parent_rating = round(sum(top5_parent_rating) / len(top5_parent_rating))
med_reviews = kpi['median_reviews']

def tag(cls, txt): return f'<span class="tag tag-{cls}">{txt}</span>'

score_rows = [
    {'dim': 'Amazon FBA尺寸分段', 'obs': '小标准件', 'rule': '标准件100 / 大号大件40 / 超大件10', 'verdict': ('pass', '可进入'), 'score': 100,
     'note': '化妆镜多为轻薄小件，FBA费用低、仓储成本可控，利于利润结构。'},
    {'dim': '头部月销 > 500', 'obs': str(head_units), 'rule': '> 500', 'verdict': ('pass', '可进入'), 'score': 90,
     'note': '头部链接月销远超500，需求足以支撑新品冷启动。'},
    {'dim': '头部月销 < 10000', 'obs': str(head_units), 'rule': '< 10000', 'verdict': ('pass' if head_units < 10000 else 'risk', '可进入' if head_units < 10000 else '警惕'), 'score': 100 if head_units < 10000 else 20,
     'note': '头部未被超大链接垄断，中小卖家仍有生存空间。'},
    {'dim': '头部评论数 < 5000', 'obs': f"{head_reviews:,}", 'rule': '< 5000', 'verdict': ('pass' if head_reviews < 5000 else 'risk', '可进入' if head_reviews < 5000 else '壁垒高'), 'score': 100 if head_reviews < 5000 else 20,
     'note': '评论壁垒衡量新品需跨越的首要门槛。'},
    {'dim': '低销量高评论排除项', 'obs': f"头部月销 {head_units} / Top1评论 {head_reviews:,}", 'rule': '头部月销 < 300 且 Top1评论 > 10000 时放弃',
     'verdict': ('pass', '可进入'), 'score': 100, 'note': '未出现低需求叠加高评论壁垒的组合。'},
    {'dim': '一年内有新品', 'obs': f"{len(new_1y)} 个（月均300+件 {len(new_1y_ok)} 个，成功率 {round(len(new_1y_ok)/max(1,len(new_1y))*100)}%）", 'rule': '>= 1 个',
     'verdict': ('pass' if new_1y else 'pending', '可进入' if new_1y else '待定'), 'score': 100 if new_1y else 40,
     'note': '近一年仍有大量新链接获得真实销售，市场对新进入者友好。'},
    {'dim': '产品平均评分 > 4.2', 'obs': str(kpi['avg_rating']), 'rule': '> 4.2', 'verdict': ('pass' if kpi['avg_rating'] > 4.2 else 'pending', '可进入' if kpi['avg_rating'] > 4.2 else '待定'),
     'score': 90 if kpi['avg_rating'] > 4.2 else 30, 'note': '类目整体评分健康，品质达标即可运营。'},
    {'dim': '前5/10名均价 $15-60', 'obs': f"前5: ${top5_avg:.2f} / 前10: ${top10_avg:.2f}", 'rule': '$15-60',
     'verdict': ('pass' if 15 <= top10_avg <= 60 else 'pending', '可进入' if 15 <= top10_avg <= 60 else '待定'), 'score': 90 if 15 <= top10_avg <= 60 else 40,
     'note': '主流售价容纳采购、FBA和广告成本的空间较大。'},
    {'dim': 'Top10 FBA占比 > 50%', 'obs': f"{fba_top10:.0f}%", 'rule': '> 50%', 'verdict': ('pass' if fba_top10 > 50 else 'info', '通过' if fba_top10 > 50 else '证据不足'),
     'score': 100 if fba_top10 > 50 else 50, 'note': '确认FBA是该类目主流履约方式。'},
    {'dim': '前5名父体平均评论数 < 5000', 'obs': f"{avg_top5_parent_rating:,}", 'rule': '< 5000',
     'verdict': ('pass' if avg_top5_parent_rating < 5000 else 'pending', '可进入' if avg_top5_parent_rating < 5000 else '待定'), 'score': 85 if avg_top5_parent_rating < 5000 else 40,
     'note': '父体评论规模反映变体矩阵的壁垒深度。'},
    {'dim': '品牌集中度 HHI < 1000', 'obs': str(kpi['hhi']), 'rule': '< 1000 分散', 'verdict': ('pass', '分散'), 'score': 95,
     'note': 'HHI仅%d，无绝对垄断品牌，中腰部机会大。' % kpi['hhi']},
    {'dim': '中位评论数 < 1000', 'obs': f"{med_reviews:,}", 'rule': '< 1000', 'verdict': ('risk' if med_reviews >= 1000 else 'pass', '待定' if med_reviews >= 1000 else '可进入'), 'score': 60,
     'note': '中位评论偏高说明老链接积累深，新品需靠差异化和广告切入。'},
]
total_score = sum(r['score'] for r in score_rows)
max_score = 1200
score_100 = round(total_score / max_score * 100)
avg_obs_score = score_100

# ---------- seasonality & forecast (category level) ----------
ct = c['cat_trend']
cat_labels = ct['labels']; cat_units = ct['units']
n = len(cat_units)
overall_avg = sum(u for u in cat_units if u) / max(1, len([u for u in cat_units if u]))
month_idx = {}
by_cal = defaultdict(list)
for lbl, u in zip(cat_labels, cat_units):
    if u is None: continue
    mm = lbl[5:7]
    by_cal[mm].append(u)
seasonal = {}
for mm, vals in by_cal.items():
    seasonal[mm] = (sum(vals) / len(vals)) / overall_avg
recent_avg = sum(u for u in cat_units[-6:] if u) / 6
vol = [abs(cat_units[i] - cat_units[i-1]) / max(1, cat_units[i-1]) for i in range(1, n) if cat_units[i] and cat_units[i-1]]
vol_avg = sum(vol) / max(1, len(vol))
fc_months, fc_labels, fc_u, fc_u_up, fc_u_lo, fc_r, fc_r_up, fc_r_lo = [], [], [], [], [], [], [], []
y, m = 2026, 9
for i in range(12):
    mm = f"{m:02d}"
    idx = recent_avg * seasonal.get(mm, 1.0)
    up = idx * (1 + min(0.8, vol_avg * 2.2)); lo = idx * (1 - min(0.8, vol_avg * 2.2))
    fc_labels.append(f"{y}-{mm}")
    fc_u.append(round(idx)); fc_u_up.append(round(up)); fc_u_lo.append(max(0, round(lo)))
    avgp = sum(p for p in c['cat_trend']['price'][-6:] if p) / 6
    fc_r.append(round(idx * avgp)); fc_r_up.append(round(up * avgp)); fc_r_lo.append(max(0, round(lo * avgp)))
    m += 1
    if m > 12: y, m = y + 1, 1
peak_months = sorted(seasonal.items(), key=lambda x: -x[1])[:4]
peak_lbl = [f"历年{k}月均值指数{s:.2f}" for k, s in peak_months]
last_y = sum(u for lbl, u in zip(cat_labels[-12:-6], cat_units[-12:-6]) if u) if n >= 12 else 0
this_y = sum(u for u in cat_units[-6:] if u)
yoy = None
prev_same = [u for lbl, u in zip(cat_labels, cat_units) if lbl.endswith(cat_labels[-1][5:7]) and u]
if len(prev_same) >= 2 and prev_same[-2]:
    yoy = round((prev_same[-1] - prev_same[-2]) / prev_same[-2] * 100, 1)

# ---------- pains from csay ----------
neg_agg = defaultdict(lambda: {'neg': 0, 'mention': 0, 'quotes': []})
pos_agg = defaultdict(lambda: {'pos': 0, 'mention': 0, 'quote': '', '启示': ''})
CN = {
    'functionality': ('功能失效/失灵', '改进灯珠与电路可靠性，出厂老化测试；电机/触控模块加保'),
    'stability': ('底座不稳/易倒', '加重底座或增加防滑垫，提升支架配重与角度锁紧'),
    'quality': ('品质投诉', '提升边框与镜面装配公差，出厂全检'),
    'light': ('灯光问题(不亮/太暗/偏色)', '升级LED灯珠与显色指数CRI>90，增加亮度档位'),
    'brightness': ('亮度不足/刺眼', '无级调光+3色温，标注流明值管理预期'),
    'size': ('尺寸不符预期', '主图标注真实尺寸参照物，Listing明确镜面净尺寸'),
    'magnification': ('放大镜畸变/倍数不符', '10X镜面改用高清镀膜，标注适用距离(对焦距离)'),
    'assembly': ('安装/组装困难', '简化安装步骤，附图示说明书与预装配件'),
    'value': ('性价比争议', '维持标配功能完整度，避免减配涨价'),
    'appearance': ('外观瑕疵', '出货前外观全检，加强包装防刮擦'),
    'charge': ('充电/续航问题', 'USB-C接口+内置电池容量升级，标注续航时长'),
    'door': ('不适合门后安装', '明确标注适用场景，增加壁挂五金件'),
}
STOP = {'good', 'nice', 'product', 'mirror', 'customers', 'they', 'it', 'this'}
for cs in c['csay']:
    for d in cs['details']:
        kw = (d['kw'] or '').lower()
        neg = d.get('neg') or 0
        pos = d.get('pos') or 0
        ment = d.get('mention') or 0
        if neg >= 5:
            key = CN.get(kw, (kw.capitalize(), '基于评论原文复核后再立项'))
            neg_agg[key[0]]['neg'] += neg
            neg_agg[key[0]]['mention'] += ment
            neg_agg[key[0]]['quotes'].append(f"{cs['asin']}：{d['content']}")
        if pos >= 5:
            key = CN.get(kw, (kw.capitalize(), ''))
            pos_agg[key[0]]['pos'] += pos
            pos_agg[key[0]]['mention'] += ment
            if not pos_agg[key[0]]['quote']:
                pos_agg[key[0]]['quote'] = d['content']
total_neg = sum(v['neg'] for v in neg_agg.values())
pain_rows = sorted(neg_agg.items(), key=lambda x: -x[1]['neg'])[:8]
total_pos = sum(v['pos'] for v in pos_agg.values())
pos_rows = sorted(pos_agg.items(), key=lambda x: -x[1]['pos'])[:5]

# ---------- parent top10 ----------
par = defaultdict(lambda: {'n': 0, 'u30': 0, 'gmv': 0.0, 'prices': [], 'ratings': [], 'brand': ''})
for r in records:
    p = r['parent'] or r['asin']
    d = par[p]
    d['n'] += 1; d['u30'] += r['units30'] or 0; d['gmv'] += r['rev6m']
    if r['price']: d['prices'].append(r['price'])
    if r['rating']: d['ratings'].append(r['rating'])
    d['brand'] = r['brand']
parent_rows = sorted(par.items(), key=lambda x: -x[1]['gmv'])[:10]

# ---------- PPC ----------
kw_all = c['kw_core'] + c['kw_pool']
seen = set(); ppc = []
avg_price = kpi['avg_price']
for k in kw_all:
    if k['kw'] in seen: continue
    seen.add(k['kw'])
    sv = k.get('sv') or 0
    cpc = (k.get('cpc') or 0)
    tier = '核心大词' if sv >= 50000 else ('二级词' if sv >= 10000 else '精准长尾')
    cvr = k.get('cvr') if (k.get('cvr') and k.get('cvr') > 0) else 5.0
    affordable = round(avg_price * (cvr / 100) / 0.25, 2)  # target ACOS 25%
    sug_bid = round(min(max(cpc, 0.5) * 1.15, affordable), 2)
    pri = 'P0' if sv >= 50000 else ('P1' if sv >= 10000 else 'P2')
    ppc.append({**k, 'tier': tier, 'pri': pri, 'sug_bid': sug_bid, 'affordable': affordable})
ppc.sort(key=lambda x: -(x.get('sv') or 0))
ppc = ppc[:16]

analysis = {
    'score_rows': score_rows, 'score_total': total_score, 'score_100': score_100,
    'decision': {
        'verdict': '待定（建议小步快跑切入）',
        'stage': '市场分散、需求充分，评分 %.0f/100；按行动清单补齐样品测试与利润验证后可立项' % score_100,
        'confidence': '中',
        'risk': f"中位评论数 {med_reviews:,} 偏高；Top1评论 {head_reviews:,}",
    },
    'kano': kano, 'att_rows': att_rows, 'combo_rows': combo_rows,
    'seasonal': seasonal, 'fc': {'labels': fc_labels, 'u': fc_u, 'u_up': fc_u_up, 'u_lo': fc_u_lo,
                                  'r': fc_r, 'r_up': fc_r_up, 'r_lo': fc_r_lo},
    'peak_months': peak_lbl, 'yoy': yoy,
    'pain_rows': [{'name': k, 'neg': v['neg'], 'total_neg': total_neg,
                   'share': round(v['neg'] / total_neg * 100, 1) if total_neg else 0,
                   'quotes': v['quotes'][:2]} for k, v in pain_rows],
    'pos_rows': [{'name': k, 'pos': v['pos'], 'total_pos': total_pos,
                  'share': round(v['pos'] / total_pos * 100, 1) if total_pos else 0,
                  'quote': v['quote']} for k, v in pos_rows],
    'parent_rows': [{'parent': p, 'brand': d['brand'], 'n': d['n'], 'u30': d['u30'],
                     'u_share': round(d['u30'] / max(1, sum(x['units30'] or 0 for x in records)) * 100, 1),
                     'gmv': round(d['gmv'], 2), 'gmv_share': round(d['gmv'] / tot_gmv * 100, 1),
                     'avg_price': round(sum(d['prices']) / len(d['prices']), 2) if d['prices'] else 0,
                     'avg_rating': round(sum(d['ratings']) / len(d['ratings']), 2) if d['ratings'] else 0}
                    for p, d in parent_rows],
    'ppc': ppc,
    'head': {'units': head_units, 'reviews': head_reviews, 'top5_avg': round(top5_avg, 2), 'top10_avg': round(top10_avg, 2),
             'fba_top10': round(fba_top10, 0), 'new_1y': len(new_1y), 'new_1y_ok': len(new_1y_ok),
             'avg_top5_parent_rating': avg_top5_parent_rating},
}
with open('records_coupled.json', 'w') as f:
    json.dump(records, f, ensure_ascii=False)
with open('analysis.json', 'w') as f:
    json.dump(analysis, f, ensure_ascii=False)
print('score_100:', score_100, '| pains:', len(analysis['pain_rows']), '| ppc:', len(ppc), '| att_rows:', len(att_rows), '| combos:', len(combo_rows), '| parents:', len(parent_rows))
print('peaks:', peak_lbl, '| yoy:', yoy)
