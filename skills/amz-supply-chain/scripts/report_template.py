# -*- coding: utf-8 -*-
"""生成 B0FSSBFS37 1688 供应链找货 HTML 报告（自包含）"""
import json

D = json.load(open('_work/calc.json', encoding='utf-8'))
IMG = json.load(open('_work/imgs.json', encoding='utf-8'))
bom, sets, SC = D['bom'], D['sets'], D['scenarios']
RATE = D['rate']

def img(k, cls=''):
    v = IMG.get(k)
    if not v:
        return ''
    return f'<img class="{cls}" src="{v}" alt="">'

def rmb2usd(x):
    return round(x / RATE, 2)

def score_cls(t):
    if t >= 70: return 'sc-a'
    if t >= 55: return 'sc-b'
    if t >= 40: return 'sc-c'
    return 'sc-d'

def score_label(t):
    if t >= 70: return '优质'
    if t >= 55: return '良好'
    if t >= 40: return '一般'
    return '偏弱'

# ============ 组件卡片 ============
bom_cards = []
for b in sorted(bom, key=lambda x: -x['total']):
    alt = b.get('alt')
    alt_html = ''
    if alt:
        alt_html = (f'<div class="alt">备用货源 #{alt["id"]} · ¥{alt["price"]} · 服务分 {alt["svc"]} · '
                    f'30天销 {alt["s30"]:,} · {"支持一件代发" if alt["drop"] else "批量采购"}<br>'
                    f'<a href="https://detail.1688.com/offer/{alt["id"]}.html" target="_blank">{alt["title"]}</a></div>')
    bom_cards.append(f'''
    <div class="card bom">
      <div class="bom-head">
        <div class="thumb">{img('ali_' + b['id'])}</div>
        <div class="bom-meta">
          <div class="bom-part">{b['part']}</div>
          <a class="bom-title" href="https://detail.1688.com/offer/{b['id']}.html" target="_blank">{b['title']}</a>
          <div class="chips">
            <span class="chip">ID {b['id']}</span>
            <span class="chip">MOQ {b['moq']}</span>
            <span class="chip">{'一件代发' if b['drop'] else '非代发'}</span>
            <span class="chip">{b['org']}</span>
          </div>
        </div>
        <div class="bom-price">
          <div class="p1">¥{b['standard']}</div>
          <div class="p2">≈ ${b['std_usd']}</div>
          <div class="p3">优化 ¥{b['optimized']} / ${b['opt_usd']}</div>
          <div class="score {score_cls(b['total'])}">评分 {b['total']}</div>
        </div>
      </div>
      <div class="bars">
        {''.join(f'<div class="bar"><span>{n}</span><i><b style="width:{v:.0f}%"></b></i><em>{v:.0f}</em></div>' for n, v in [
          ('价格竞争力', b['price_score']), ('供应商资质', b['qual_score']), ('服务质量', b['svc_score']),
          ('出货稳定性', b['stab_score']), ('物流时效', b['log_score']), ('一件代发', b['drop_score'])] )}
      </div>
      <div class="bom-foot">
        <span>服务分 <b>{b['svc']}</b></span>
        <span>30天销量 <b>{b['s30']:,}</b></span>
        <span>复购率 <b>{b['rep']}%</b></span>
        <span>库存 <b>{b['stock']:,}</b></span>
        <span>发货 <b>{b['ship']}</b></span>
      </div>
      {alt_html}
    </div>''')

# ============ 成品套装表 ============
set_rows = []
for s in sorted(sets, key=lambda x: -x['total']):
    price = f"¥{s['price']}" + (f"–{s['price_max']}" if s['price_max'] and s['price_max'] != s['price'] else '')
    usd = f"${s['usd']}" if s['usd'] else '—'
    set_rows.append(f'''<tr>
      <td class="td-img">{img('ali_' + s['id'])}</td>
      <td><a href="https://detail.1688.com/offer/{s['id']}.html" target="_blank">{s['title']}</a>
          <div class="sub">ID {s['id']} · {s['org'] or '—'} · {s['size']}</div></td>
      <td class="num">{price}</td>
      <td class="num">{usd}</td>
      <td class="num">{s['moq'] or '—'}</td>
      <td class="num">{s['svc'] or '—'}</td>
      <td class="num">{s['s30']:,}</td>
      <td class="num">{s['rep']}%</td>
      <td class="num">{'是' if s['drop'] else '否'}</td>
      <td><span class="badge {score_cls(s['total'])}">{s['total']}</span></td>
    </tr>''')

# ============ 利润瀑布图（BOM 优化版 @ $24.99） ============
wb = SC['B_opt_2499']
wf_items = [('Amazon 售价', wb['price'], 'in'), ('采购成本', -wb['cogs'], 'out'),
            ('头程物流', -wb['inbound'], 'out'), ('平台佣金 15%', -wb['comm'], 'out'),
            ('FBA 配送费', -wb['fba'], 'out'), ('广告摊销 12%', -wb['ads'], 'out'),
            ('退货与杂费 3%', -wb['ret'], 'out')]
maxv = wb['price']
W, H, PADL, PADT = 660, 260, 62, 26
barw = (W - PADL - 16) / (len(wf_items) + 1)
scale = (H - PADT - 42) / maxv
wf_svg, run = [], 0.0
for i, (name, val, kind) in enumerate(wf_items):
    x = PADL + i * barw + barw * 0.18
    bw = barw * 0.64
    if kind == 'in':
        y0, h = (H - 42) - val * scale, val * scale
        top, run = val, val
        color = '#4f46e5'
    else:
        h = -val * scale
        y0 = (H - 42) - run * scale
        run = run + val
        color = '#e11d48'
    wf_svg.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(h,2):.1f}" rx="4" fill="{color}" opacity="0.88"/>')
    wf_svg.append(f'<text x="{x+bw/2:.1f}" y="{y0-6:.1f}" text-anchor="middle" class="wfv">{val:+.2f}</text>')
    for j, ln in enumerate(name.split(' ')):
        wf_svg.append(f'<text x="{x+bw/2:.1f}" y="{H-26+j*12:.1f}" text-anchor="middle" class="wfn">{ln}</text>')
# 净利
x = PADL + len(wf_items) * barw + barw * 0.18
bw = barw * 0.64
net = wb['net']
y0 = (H - 42) - net * scale
# 连接线：从上一条柱子的当前累计高度拉到净利柱顶部
prev_x = PADL + (len(wf_items) - 1) * barw + barw * 0.18 + barw * 0.64
prev_y = (H - 42) - run * scale
wf_svg.append(f'<line x1="{prev_x:.1f}" y1="{prev_y:.1f}" x2="{x:.1f}" y2="{prev_y:.1f}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/>')
wf_svg.append(f'<line x1="{x:.1f}" y1="{prev_y:.1f}" x2="{x:.1f}" y2="{y0:.1f}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/>')
wf_svg.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(net*scale,2):.1f}" rx="4" fill="#059669"/>')
wf_svg.append(f'<text x="{x+bw/2:.1f}" y="{y0-6:.1f}" text-anchor="middle" class="wfv net">{net:+.2f}</text>')
wf_svg.append(f'<text x="{x+bw/2:.1f}" y="{H-26:.1f}" text-anchor="middle" class="wfn" style="font-weight:700;fill:#047857">净利润</text>')
wf_svg.append(f'<text x="{x+bw/2:.1f}" y="{H-14:.1f}" text-anchor="middle" class="wfa">{wb["rate"]}%</text>')
for g in range(6):
    v = maxv / 5 * g
    y = (H - 42) - v * scale
    wf_svg.append(f'<line x1="{PADL}" y1="{y:.1f}" x2="{W-8}" y2="{y:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
    wf_svg.append(f'<text x="{PADL-8}" y="{y+4:.1f}" text-anchor="end" class="wfa">${v:.0f}</text>')
waterfall = f'<svg viewBox="0 0 {W} {H}" class="wf">{"".join(wf_svg)}</svg>'

# ============ 售价阶梯 ============
ladder_keys = ['B_opt_1699', 'B_opt_1999', 'B_opt_2499', 'B_opt_2999']
ladder = []
for k in ladder_keys:
    v = SC[k]
    lv = 'lv-bad' if v['rate'] < 10 else ('lv-mid' if v['rate'] < 20 else ('lv-ok' if v['rate'] < 35 else 'lv-good'))
    tag = '不建议' if v['rate'] < 10 else ('勉强' if v['rate'] < 20 else ('可行' if v['rate'] < 35 else '优质'))
    ladder.append(f'''<div class="lad {lv}">
      <div class="lad-p">${v['price']:.2f}</div>
      <div class="lad-bar"><i style="height:{min(100, v['rate']*2.2):.0f}%"></i></div>
      <div class="lad-rate">{v['rate']}%</div>
      <div class="lad-net">净利 ${v['net']}</div>
      <div class="lad-tag">{tag}</div>
    </div>''')

# ============ 场景表 ============
sc_rows = []
names = {
    'A_set45_1699': ('成品整套采购 ¥45 @ $16.99', '不可行', 'bad'),
    'B_std_1699': ('BOM 标准版 ¥20.28 @ $16.99', '勉强', 'mid'),
    'B_opt_1699': ('BOM 优化版 ¥13.06 @ $16.99', '勉强', 'mid'),
    'B_opt_1999': ('BOM 优化版 ¥13.06 @ $19.99', '可行', 'ok'),
    'B_opt_2499': ('BOM 优化版 ¥13.06 @ $24.99', '可行偏优', 'ok'),
    'B_opt_2999': ('BOM 优化版 ¥13.06 @ $29.99', '优质', 'good'),
    'B_std_2499': ('BOM 标准版 ¥20.28 @ $24.99', '可行', 'ok'),
}
for k in ['A_set45_1699', 'B_std_1699', 'B_opt_1699', 'B_opt_1999', 'B_opt_2499', 'B_std_2499', 'B_opt_2999']:
    v = SC[k]
    n, tag, cls = names[k]
    sc_rows.append(f'''<tr>
      <td>{n}</td>
      <td class="num">${v['price']:.2f}</td>
      <td class="num">${v['cogs']}</td>
      <td class="num">${v['inbound']}</td>
      <td class="num">${v['comm']}</td>
      <td class="num">${v['fba']}</td>
      <td class="num">${v['ads']}</td>
      <td class="num">${v['ret']}</td>
      <td class="num strong {'neg' if v['net']<0 else 'pos'}">${v['net']}</td>
      <td class="num"><b>{v['rate']}%</b></td>
      <td><span class="badge {cls}">{tag}</span></td>
    </tr>''')

std, opt = D['std_cogs'], D['opt_cogs']
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>1688 供应链找货报告 · B0FSSBFS37</title>
<style>
:root{{
  --ink:#0f172a; --ink2:#334155; --muted:#64748b; --line:#e2e8f0; --bg:#f6f7fb; --card:#ffffff;
  --indigo:#4f46e5; --teal:#0d9488; --rose:#e11d48; --amber:#d97706; --green:#059669;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei","Hiragino Sans GB",sans-serif;
  line-height:1.65;-webkit-font-smoothing:antialiased;font-size:14px}}
.wrap{{max-width:1120px;margin:0 auto;padding:32px 22px 72px}}
a{{color:var(--indigo);text-decoration:none;border-bottom:1px solid #c7d2fe}}
a:hover{{color:#3730a3;border-bottom-color:var(--indigo)}}

/* header */
.hero{{background:linear-gradient(135deg,#eef2ff 0%,#f0fdfa 60%,#fff 100%);border:1px solid var(--line);
  border-radius:18px;padding:26px;display:flex;gap:24px;align-items:flex-start;position:relative;overflow:hidden}}
.hero:before{{content:"";position:absolute;right:-60px;top:-60px;width:240px;height:240px;border-radius:50%;
  background:radial-gradient(circle,#c7d2fe55,transparent 70%)}}
.hero .thumb-lg{{flex:0 0 132px;width:132px;height:132px;border-radius:14px;overflow:hidden;background:#fff;
  border:1px solid var(--line);box-shadow:0 6px 18px rgba(15,23,42,.08)}}
.hero .thumb-lg img{{width:100%;height:100%;object-fit:contain}}
.hero h1{{font-size:23px;line-height:1.35;letter-spacing:-.2px;margin-bottom:8px}}
.hero .asin{{display:inline-flex;align-items:center;gap:6px;font-family:ui-monospace,Menlo,Consolas,monospace;
  background:#0f172a;color:#fff;font-size:12px;padding:3px 10px;border-radius:6px;letter-spacing:.5px}}
.hero .tagline{{color:var(--ink2);font-size:13px;margin-top:8px;max-width:660px}}
.hero .kw{{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}}
.hero .kw span{{background:#fff;border:1px solid var(--line);color:var(--muted);font-size:11.5px;
  padding:2px 9px;border-radius:20px}}
.eyebrow{{font-size:11.5px;letter-spacing:2.4px;color:var(--indigo);font-weight:700;text-transform:uppercase;margin-bottom:8px}}

/* metric cards */
.metrics{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:18px 0 6px}}
.m{{background:var(--card);border:1px solid var(--line);border-radius:13px;padding:14px 15px;position:relative;overflow:hidden}}
.m:after{{content:"";position:absolute;left:0;top:0;width:3px;height:100%;background:var(--indigo);opacity:.85}}
.m.teal:after{{background:var(--teal)}} .m.amber:after{{background:var(--amber)}}
.m.rose:after{{background:var(--rose)}} .m.green:after{{background:var(--green)}}
.m .k{{font-size:11.5px;color:var(--muted);letter-spacing:.3px}}
.m .v{{font-size:22px;font-weight:800;letter-spacing:-.5px;margin-top:3px}}
.m .s{{font-size:11.5px;color:var(--muted);margin-top:2px}}

/* sections */
section{{margin-top:34px}}
h2{{font-size:17px;display:flex;align-items:center;gap:10px;margin-bottom:4px}}
h2 .n{{flex:0 0 26px;height:26px;border-radius:8px;background:#0f172a;color:#fff;font-size:12px;
  display:flex;align-items:center;justify-content:center;font-weight:700;letter-spacing:0}}
h2 .sub{{font-size:12px;color:var(--muted);font-weight:400;margin-left:auto}}
.lead{{color:var(--ink2);font-size:13.5px;margin:8px 0 16px;max-width:900px}}

.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}

/* table */
.tbl{{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:14px;border:1px solid var(--line);
  background:var(--card)}}
.tbl table{{border:0;border-radius:0}}
table{{width:100%;border-collapse:separate;border-spacing:0;font-size:12.7px;background:var(--card);
  border:1px solid var(--line);border-radius:14px;overflow:hidden}}
th{{background:#f8fafc;color:var(--muted);font-weight:600;text-align:left;padding:10px 11px;
  border-bottom:1px solid var(--line);white-space:nowrap;font-size:12px}}
td{{padding:11px;border-bottom:1px solid #f1f5f9;vertical-align:middle}}
tr:last-child td{{border-bottom:none}}
tbody tr:hover{{background:#fbfcfe}}
td.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
td.strong{{font-weight:800}}
.pos{{color:var(--green)}} .neg{{color:var(--rose)}}
.td-img{{width:56px;padding:7px 8px}}
.td-img img{{width:48px;height:48px;object-fit:contain;border-radius:8px;border:1px solid var(--line);background:#fff}}
.sub{{font-size:11.5px;color:var(--muted);margin-top:2px}}
.badge{{display:inline-block;min-width:38px;text-align:center;padding:2px 8px;border-radius:20px;
  font-weight:700;font-size:11.5px;color:#fff}}
.badge.bad,.sc-d{{background:#94a3b8}} .badge.mid,.sc-c{{background:var(--amber)}}
.badge.ok,.sc-b{{background:var(--teal)}} .badge.good,.sc-a{{background:var(--green)}}

/* bom cards */
.bom{{margin-bottom:14px;padding:16px}}
.bom-head{{display:flex;gap:16px;align-items:flex-start}}
.bom .thumb{{flex:0 0 84px;width:84px;height:84px;border-radius:11px;overflow:hidden;background:#f8fafc;
  border:1px solid var(--line);display:flex;align-items:center;justify-content:center}}
.bom .thumb img{{width:100%;height:100%;object-fit:contain}}
.bom-meta{{flex:1;min-width:0}}
.bom-part{{font-size:11.5px;letter-spacing:1.6px;color:var(--indigo);font-weight:700;text-transform:uppercase}}
.bom-title{{display:block;font-size:14px;font-weight:600;color:var(--ink);border:none;margin:3px 0 7px;line-height:1.45}}
.bom-title:hover{{color:var(--indigo)}}
.chips{{display:flex;flex-wrap:wrap;gap:6px}}
.chip{{background:#f1f5f9;color:var(--ink2);font-size:11px;padding:2px 8px;border-radius:6px}}
.bom-price{{text-align:right;flex:0 0 116px}}
.bom-price .p1{{font-size:20px;font-weight:800;letter-spacing:-.5px}}
.bom-price .p2{{font-size:11.5px;color:var(--muted)}}
.bom-price .p3{{font-size:11.5px;color:var(--teal);margin-top:3px}}
.bom-price .score{{display:inline-block;margin-top:7px;font-size:11.5px;font-weight:700;color:#fff;
  padding:2px 9px;border-radius:20px}}
.bars{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px 18px;margin-top:14px;
  border-top:1px dashed var(--line);padding-top:12px}}
.bar{{display:flex;align-items:center;gap:8px;font-size:11.5px;color:var(--muted)}}
.bar span{{flex:0 0 66px}}
.bar i{{flex:1;height:6px;background:#eef2f7;border-radius:6px;overflow:hidden;display:block}}
.bar i b{{display:block;height:100%;background:linear-gradient(90deg,#6366f1,#0d9488);border-radius:6px}}
.bar em{{flex:0 0 24px;text-align:right;font-style:normal;color:var(--ink2);font-variant-numeric:tabular-nums}}
.bom-foot{{display:flex;flex-wrap:wrap;gap:16px;margin-top:12px;font-size:11.8px;color:var(--muted)}}
.bom-foot b{{color:var(--ink)}}
.alt{{margin-top:10px;background:#f0fdfa;border:1px dashed #99f6e4;border-radius:9px;padding:9px 11px;
  font-size:11.8px;color:#115e59;line-height:1.6}}

/* svg */
.wf{{width:100%;height:auto;display:block}}
.wfv{{font-size:10.5px;font-weight:700;fill:#334155}}
.wfv.net{{fill:#047857}}
.wfn{{font-size:10px;fill:#64748b}}
.wfa{{font-size:10px;fill:#94a3b8}}

/* ladder */
.ladder{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:6px}}
.lad{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;text-align:center;position:relative}}
.lad-p{{font-size:19px;font-weight:800;letter-spacing:-.5px}}
.lad-bar{{height:72px;display:flex;align-items:flex-end;justify-content:center;margin:10px 0 8px}}
.lad-bar i{{display:block;width:34px;border-radius:7px 7px 0 0;background:linear-gradient(180deg,#818cf8,#4f46e5)}}
.lad.lv-good .lad-bar i{{background:linear-gradient(180deg,#34d399,#059669)}}
.lad.lv-ok .lad-bar i{{background:linear-gradient(180deg,#2dd4bf,#0d9488)}}
.lad.lv-mid .lad-bar i{{background:linear-gradient(180deg,#fbbf24,#d97706)}}
.lad.lv-bad .lad-bar i{{background:linear-gradient(180deg,#fb7185,#e11d48)}}
.lad-rate{{font-size:15px;font-weight:800}}
.lad-net{{font-size:11.5px;color:var(--muted);margin-top:2px}}
.lad-tag{{margin-top:8px;font-size:11.5px;font-weight:700;padding:3px 0;border-radius:7px;color:#fff;background:var(--amber)}}
.lad.lv-good .lad-tag{{background:var(--green)}} .lad.lv-ok .lad-tag{{background:var(--teal)}}
.lad.lv-bad .lad-tag{{background:var(--rose)}}

/* callouts */
.note{{border-left:3px solid var(--indigo);background:#f8faff;border-radius:0 10px 10px 0;padding:12px 15px;
  font-size:13px;color:var(--ink2);margin:14px 0}}
.note.warn{{border-left-color:var(--amber);background:#fffbeb}}
.note.danger{{border-left-color:var(--rose);background:#fff1f2}}
.note.ok{{border-left-color:var(--green);background:#ecfdf5}}
.note b{{color:var(--ink)}}

ol.steps,ul.plain{{padding-left:0;list-style:none;counter-reset:s}}
ol.steps li{{counter-increment:s;position:relative;padding-left:34px;margin-bottom:11px;font-size:13.3px;color:var(--ink2)}}
ol.steps li:before{{content:counter(s);position:absolute;left:0;top:1px;width:22px;height:22px;border-radius:7px;
  background:#eef2ff;color:var(--indigo);font-weight:700;font-size:11.5px;display:flex;align-items:center;justify-content:center}}
ul.plain li{{position:relative;padding-left:18px;margin-bottom:9px;font-size:13.3px;color:var(--ink2)}}
ul.plain li:before{{content:"";position:absolute;left:2px;top:9px;width:6px;height:6px;border-radius:2px;background:var(--indigo)}}
ul.plain li b,ol.steps li b{{color:var(--ink)}}

.kv{{display:grid;grid-template-columns:auto 1fr;gap:7px 14px;font-size:12.8px}}
.kv dt{{color:var(--muted)}}
.kv dd{{color:var(--ink);font-weight:600}}

footer{{margin-top:46px;border-top:1px solid var(--line);padding-top:18px;font-size:11.5px;color:var(--muted);
  display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}}
@media(max-width:900px){{
  .metrics{{grid-template-columns:repeat(3,1fr)}}
  .grid2,.grid3{{grid-template-columns:1fr}}
  .ladder{{grid-template-columns:repeat(2,1fr)}}
  .hero{{flex-direction:column}}
  .bars{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>
<div class="wrap">

<!-- ============ HERO ============ -->
<div class="hero">
  {img('amz_main', 'thumb-lg')}
  <div style="flex:1;min-width:0">
    <div class="eyebrow">1688 Sourcing Report · amz-supply-chain</div>
    <h1>Care Package for Women — Get Well Soon 7 件套康复礼盒</h1>
    <div><span class="asin">ASIN B0FSSBFS37</span>
      <span class="asin" style="background:#334155;margin-left:6px">Amazon US</span>
      <span class="asin" style="background:#0d9488;margin-left:6px">1688 domain 601</span></div>
    <p class="tagline">品牌 <b>Gagalico</b>（Buybox 卖家 Gagalico US，发货地 CN）· 上架 2025-11-27（288 天）·
      当前售价 <b>$16.99</b>（历史划线价 $39.99）· 评分 4.8/73 条 · BSR 类目 #98。</p>
    <div class="kw"><span>#get well soon gifts</span><span>#care package for women</span>
      <span>#after surgery recovery gift</span><span>#hug in a box</span><span>#gift basket</span>
      <span>#7pcs 组合礼盒</span></div>
  </div>
</div>

<!-- ============ METRICS ============ -->
<div class="metrics">
  <div class="m"><div class="k">Amazon 售价</div><div class="v">$16.99</div><div class="s">历史划线价 $39.99</div></div>
  <div class="m teal"><div class="k">近 30 天销量</div><div class="v">900</div><div class="s">年度累计 6,279 件</div></div>
  <div class="m amber"><div class="k">BSR 排名</div><div class="v">#98</div><div class="s">Tumblers &amp; Water Glasses</div></div>
  <div class="m rose"><div class="k">FBA 配送费</div><div class="v">$5.93</div><div class="s">佣金 $2.55（15%）</div></div>
  <div class="m green"><div class="k">1688 最优采购</div><div class="v">¥{opt}</div><div class="s">≈ ${rmb2usd(opt)} / 套（BOM 优化版）</div></div>
  <div class="m"><div class="k">价差倍数</div><div class="v">{round(16.99/rmb2usd(opt),1)}×</div><div class="s">售价 ÷ 采购成本</div></div>
</div>

<div class="note"><b>一句话结论：</b>这是一个典型的「低客单 + 组合礼盒」品。1688 上<b>没有同款成品可一件直采</b>（命中一条数据未公开的同款链接），
但 7 个组件全部能在 1688 找到高销量货源，<b>自配 BOM 后采购成本可从 ¥{std} 压到 ¥{opt}（≈${rmb2usd(opt)}）</b>。
在当前 $16.99 价位毛利率仅 {SC['B_opt_1699']['rate']}%，<b>必须提价到 $24.99+ 才能进入健康毛利区间</b>。</div>

<!-- ============ 01 数据来源 ============ -->
<section>
  <h2><span class="n">01</span>数据来源与调用记录<span class="sub">Sorftime CLI · 本机已认证 profile</span></h2>
  <p class="lead">本次执行走 <b>CLI 通道</b>（MCP 未配置凭证）。1688 端点固定 <code>--domain 601</code>，Amazon 侧 <code>--domain 1</code>。</p>
  <div class="grid3">
    <div class="card">
      <div class="eyebrow">搜索路径</div>
      <dl class="kv">
        <dt>以图搜货</dt><dd>ProductSearchFromImage × 4（200 条）</dd>
        <dt>按名搜索</dt><dd>ProductSearchFromName × 7（600+ 条）</dd>
        <dt>去重候选</dt><dd>813 条</dd>
      </dl>
    </div>
    <div class="card">
      <div class="eyebrow">明细拉取</div>
      <dl class="kv">
        <dt>组件变体</dt><dd>ProductVariations × 8</dd>
        <dt>组件详情</dt><dd>ProductRequest × 4</dd>
        <dt>Amazon 详情</dt><dd>ProductRequest × 1</dd>
      </dl>
    </div>
    <div class="card">
      <div class="eyebrow">配额消耗</div>
      <dl class="kv">
        <dt>请求额度</dt><dd>29,557 / 29,999 剩余</dd>
        <dt>本次消耗</dt><dd>≈ 30 requests</dd>
        <dt>汇率假定</dt><dd>1 USD = {RATE} CNY</dd>
      </dl>
    </div>
  </div>
</section>

<!-- ============ 02 产品画像 ============ -->
<section>
  <h2><span class="n">02</span>Amazon 产品画像<span class="sub">ProductRequest · domain 1</span></h2>
  <p class="lead">卖家侧关键经营参数，用于反推可承受的采购成本上限。</p>
  <div class="grid2">
    <div class="card">
      <div class="eyebrow">Listing 与销售</div>
      <dl class="kv">
        <dt>Listing 标题</dt><dd style="font-weight:400;font-size:12.5px">Care Package for Women Get Well Gifts for Women After Surgery Recovery Gift…</dd>
        <dt>品牌 / 卖家</dt><dd>Gagalico / Gagalico US（CN 发货）</dd>
        <dt>上架时间</dt><dd>2025-11-27（288 天）</dd>
        <dt>售价 / 划线价</dt><dd>$16.99 / $39.99</dd>
        <dt>价格走势</dt><dd>$15.29 → $16.99（2026-09-07 调价）</dd>
        <dt>近 30 天销量</dt><dd>900 件</dd>
        <dt>年度累计</dt><dd>6,279 件</dd>
        <dt>评分 / 评论</dt><dd>4.8 ★ / 73 条</dd>
        <dt>BSR</dt><dd>Tumblers &amp; Water Glasses #98</dd>
      </dl>
    </div>
    <div class="card">
      <div class="eyebrow">成本与物流</div>
      <dl class="kv">
        <dt>配送方式</dt><dd>FBA（Ships from Amazon）</dd>
        <dt>FBA 配送费</dt><dd>$5.93</dd>
        <dt>平台佣金</dt><dd>$2.55（15.0%）</dd>
        <dt>毛利（未计采购）</dt><dd>$8.51 / 50.09%</dd>
        <dt>包装尺寸</dt><dd>21.21 × 16.79 × 9.60 cm</dd>
        <dt>重量</dt><dd>789 g（Listing 标注 0.85 kg）</dd>
        <dt>变体数 / 跟卖</dt><dd>0 变体 / 1 个卖家</dd>
        <dt>A+ 页面</dt><dd>有（无品牌旗舰店）</dd>
        <dt>Coupon / 促销</dt><dd>无</dd>
      </dl>
    </div>
  </div>
  <div class="note warn"><b>关键约束：</b>单价 $16.99 中已被 FBA（$5.93）+ 佣金（$2.55）吃掉 <b>$8.48（49.9%）</b>，
  留给「采购 + 头程 + 广告 + 退货」的空间只有 <b>$8.51</b>。因此采购成本必须压到 <b>$3 以内</b> 才有利润，
  这是本报告筛选货源的硬性红线。</div>
</section>

<!-- ============ 03 产品结构拆解 ============ -->
<section>
  <h2><span class="n">03</span>产品结构拆解：7 件套 BOM<span class="sub">来源：Listing 描述 + 以图搜货命中</span></h2>
  <p class="lead">该品并非单一工厂原品，而是「<b>多组件 + 礼盒外包装</b>」的装配式礼品。官网描述明确列出 7 件内容物，
  以图搜货也分别命中了其中的袜子、钩织盆栽、贺卡三类组件，验证了 BOM 拆解方向正确。</p>
  <div class="tbl"><table>
    <thead><tr><th>#</th><th>组件</th><th>Listing 描述</th><th>1688 命中</th><th>采购价</th></tr></thead>
    <tbody>
      <tr><td>1</td><td><b>16oz 花朵玻璃杯</b></td><td>1× 16oz floral glass cup</td><td>✅ 命中（¥1.6，30 天销 4.3 万）</td><td class="num">¥1.60</td></tr>
      <tr><td>2</td><td>蓝铃花香薰蜡烛</td><td>1× bluebell scented candle</td><td>✅ 命中（¥1.51 含礼盒）</td><td class="num">¥1.51</td></tr>
      <tr><td>3</td><td>手工钩织心形多肉</td><td>1× handwoven heart-shaped succulent</td><td>✅ 命中（¥2.8–6.5）</td><td class="num">¥2.80</td></tr>
      <tr><td>4</td><td>珊瑚绒袜子</td><td>1× fuzzy socks</td><td>✅ 命中（¥2.2，30 天销 2.9 万）</td><td class="num">¥2.20</td></tr>
      <tr><td>5</td><td>爱心浴盐球</td><td>1× bath bomb</td><td>✅ 命中（¥3.0 空心款）</td><td class="num">¥3.00</td></tr>
      <tr><td>6</td><td>祝福贺卡</td><td>1× gift card</td><td>✅ 命中（¥0.02，超级工厂）</td><td class="num">¥0.02</td></tr>
      <tr><td>7</td><td>天地盖礼盒</td><td>1× elegant gift box</td><td>✅ 命中（¥2.5–3.5）</td><td class="num">¥2.50</td></tr>
      <tr style="background:#f0fdfa"><td colspan="4"><b>合计（优化版 @ 一件代发/小批量价）</b></td><td class="num strong">¥{opt}</td></tr>
      <tr style="background:#f8fafc"><td colspan="4">合计（标准版：盆栽取 ¥6.5、浴球取 ¥4.8、礼盒取 ¥3.5）</td><td class="num strong">¥{std}</td></tr>
    </tbody>
  </table></div>
</section>

<!-- ============ 04 找货执行 ============ -->
<section>
  <h2><span class="n">04</span>1688 找货执行与命中情况<span class="sub">3 条路径 · 813 条去重结果</span></h2>
  <p class="lead">按方法论走了三条路径，最终去重得到 813 条候选，逐一打分后得到下面的推荐清单。</p>
  <div class="grid3">
    <div class="card"><div class="eyebrow">路径 A · 以图搜货</div>
      <p style="font-size:12.8px;color:var(--ink2)">用 4 张 Amazon 主图反查，分别命中<b>玻璃杯</b>（主图）、<b>钩织盆栽</b>、<b>珊瑚绒袜</b>、<b>贺卡</b>四类组件。这条路是本次最大的收获——<b>直接验证了 BOM 的组件构成</b>。</p></div>
    <div class="card"><div class="eyebrow">路径 B · 中文关键词</div>
      <p style="font-size:12.8px;color:var(--ink2)">7 组关键词命中「沐浴 spa 礼盒 / 香薰蜡烛礼盒」类成品套装（¥45–52），以及礼盒、飞机盒等外包装货源。<b>未找到完全同款的 7 件套成品</b>。</p></div>
    <div class="card"><div class="eyebrow">路径 C · 英文原名</div>
      <p style="font-size:12.8px;color:var(--ink2)">用 Amazon 英文标题直搜，返回结果多为礼品袋、空礼盒等包装类目，<b>相关性低</b>。结论：英文品名不适合 1688 搜货，须先翻译/拆解为中文组件词。</p></div>
  </div>
  <div class="note danger"><b>无法直采同款的原因：</b>该品是品牌方（Gagalico）自行组合定制的礼盒，1688 无对应成品链接。
  唯一命中的同款 <code>ID 1076910243306</code>（标题含「亚马逊同款康复礼品套装」）关键字段（价格/服务分/销量）全部为空，无法评估，
  <b>建议直接联系该供应商询价</b>。</div>
</section>

<!-- ============ 05 成品套装 ============ -->
<section>
  <h2><span class="n">05</span>货源候选 A：成品整套方案<span class="sub">评分公式见方法论</span></h2>
  <p class="lead">「买现成套装 + 换包装」路径。优点是省事，缺点是加了中间商成本，本案例中<b>成本直接顶穿利润线</b>。</p>
  <div class="tbl"><table>
    <thead><tr><th></th><th>供应商 / 产品</th><th>批发价</th><th>≈USD</th><th>MOQ</th><th>服务分</th><th>30天销量</th><th>复购率</th><th>代发</th><th>评分</th></tr></thead>
    <tbody>{''.join(set_rows)}</tbody>
  </table></div>
  <div class="note danger"><b>淘汰结论：</b>两家 spa 礼盒 ¥45/套（≈$6.29）看似便宜，但放到 $16.99 价位上测算
  <b>净利 −$1.52（−8.9%）直接亏损</b>。且其内容物是「沐浴 spa 套装」，与 Amazon 的「康复慰问」主题错配，需要重新做视觉与文案。
  除非把售价拉到 <b>$29.99 以上</b>，否则成品整套方案不建议采用。</div>
</section>

<!-- ============ 06 BOM 组件 ============ -->
<section>
  <h2><span class="n">06</span>货源候选 B：组件 BOM 方案（推荐）<span class="sub">按综合评分排序</span></h2>
  <p class="lead">自配 7 件的采购成本仅为成品套装的 <b>{round(opt/45*100)}%</b>，是本案唯一能跑通利润的路径。
  评分 = 价格竞争力 30% + 供应商资质 20% + 服务质量 15% + 出货稳定性 15% + 物流时效 10% + 一件代发 10%；组件价格得分以该组件的成本预算为基准计算。</p>
  {''.join(bom_cards)}
  <div class="note ok"><b>Top 3 组件货源：</b>
  <b>① 贺卡 ¥0.02</b>（超级工厂 + 一天 2,100 万+ 出单，服务分 4.5，综合 85.4 分）；
  <b>② 16oz 花朵玻璃杯 ¥1.6</b>（30 天销 4.3 万件、复购率 57%、库存近 5 亿，主角件唯一高性价比来源，64.0 分）；
  <b>③ 天地盖礼盒 ¥3.5</b>（义乌，服务分 5.0、复购率 64%、11 个尺寸 SKU 可选，51.8 分）。</div>
</section>

<!-- ============ 07 利润测算 ============ -->
<section>
  <h2><span class="n">07</span>价格差与利润测算<span class="sub">汇率 1 USD = {RATE} CNY · 海运头程 $1.4/kg</span></h2>
  <p class="lead">以 BOM 优化版（采购 ¥{opt} ≈ ${rmb2usd(opt)}）为例，拆解每个价格档位下的成本结构与净利。</p>

  <div class="card" style="margin-bottom:18px">
    <div class="eyebrow" style="margin-bottom:10px">成本瀑布 · BOM 优化版 @ $24.99</div>
    {waterfall}
  </div>

  <div class="ladder">{''.join(ladder)}</div>

  <div style="margin-top:20px">
  <div class="tbl"><table>
    <thead><tr><th>方案 / 售价场景</th><th>售价</th><th>1688 采购</th><th>头程</th><th>佣金15%</th><th>FBA</th><th>广告12%</th><th>退货3%</th><th>净利润</th><th>毛利率</th><th>判断</th></tr></thead>
    <tbody>{''.join(sc_rows)}</tbody>
  </table></div>
  </div>

  <div class="note warn"><b>核心结论：</b>售价每上一个台阶，毛利率提升约 <b>8–10 个百分点</b>。
  $16.99 时只有 <b>{SC['B_opt_1699']['rate']}%</b>（勉强），$19.99 时 <b>{SC['B_opt_1999']['rate']}%</b>（可行），
  $24.99 时 <b>{SC['B_opt_2499']['rate']}%</b>（可行偏优），$29.99 时 <b>{SC['B_opt_2999']['rate']}%</b>（优质）。
  该品历史划线价 $39.99、且属于「礼品/慰问」场景（对价格敏感度低、送礼人愿付溢价），
  <b>建议以 $24.99–$29.99 卡位，而不是跟着 $16.99 打价格战</b>。</div>

  <div class="note"><b>测算口径说明：</b>
  1）采购成本取 1688 一件代发/小批量档位价，批量采购（≥200 套）通常还可再降 10–20%；
  2）头程按 0.85 kg 实重 × $1.4/kg 海运估算，空运（¥35/kg）会显著压缩利润，补货请优先海运；
  3）FBA 费在 $19.99 以上档位按尺寸分段上调（$6.21 / $6.49）；
  4）广告摊销按售价 12%、退货及杂费按 3% 经验值计提，实际以运营数据为准。</div>
</section>

<!-- ============ 08 评估结论 ============ -->
<section>
  <h2><span class="n">08</span>供应商评估结论与推荐</h2>
  <div class="grid2">
    <div class="card">
      <div class="eyebrow">Top 推荐组合（BOM 方案）</div>
      <ol class="steps">
        <li><b>玻璃杯（主角件）</b> — ID 851663692164 · 徐州 · ¥1.6 · 服务分 4.0 · 30 天销 43,158 · 一件代发。全店库存近 5 亿，5 色可选，是拉开视觉差异的关键件。</li>
        <li><b>钩织盆栽（主题件）</b> — ID 1041185116624（优化）/ 1059357985456（标准）· 安徽亳州 · ¥2.8–6.5 · 30 天销 5,963–8,088。以图搜货精准命中同一造型，是最能体现「慰问」主题的差异化组件。</li>
        <li><b>珊瑚绒袜</b> — ID 604774156513 · 浙江诸暨市果石袜厂 · ¥2.35（≥2000 双 ¥2.20）· 30 天销 29,138。袜厂直供，阶梯价清晰。</li>
        <li><b>香薰蜡烛礼盒</b> — ID 962491120188 · 义乌 · ¥0.94（M 号）/ ¥1.51（L 号）· 30 天销 21,955 · 21 个 SKU 可选尺寸。自带礼盒包装，可直接作内盒。</li>
        <li><b>浴盐球 / 贺卡 / 外盒</b> — ID 730328227810（¥3.0 空心款）/ 640770180117（¥0.02 超级工厂）/ 673109322785（¥2.5–3.5 天地盖，11 尺寸）。</li>
      </ol>
    </div>
    <div class="card">
      <div class="eyebrow">风险提示</div>
      <ul class="plain">
        <li><b>组件拼配的品控风险</b>：7 家供应商 = 7 条物流与 7 个质检口，色差、批差、包装磕碰都会放大退货率。<b>建议先各买 1 件打样，再集中到 1 家做组装外包</b>。</li>
        <li><b>MOQ 约束</b>：贺卡 MOQ 500（¥0.02 × 500 = ¥10，可接受）；钩织盆栽 MOQ 5；其余多支持 1 件起。<b>整柜采购请以 ≥200 套为一个批次谈阶梯价</b>。</li>
        <li><b>低毛利预警</b>：若售价守在 $16.99，任何一项成本波动（FBA 涨费、广告超 15%、退货超 5%）都会把毛利率打到 10% 以下。</li>
        <li><b>数据缺口</b>：同款链接 1076910243306 关键字段为空；部分组件（盆栽、袜子）1688 未返回库存字段，需人工核实。</li>
        <li><b>合规与知识产权</b>：Listing 已注册品牌 Gagalico，直接照抄标题与 A+ 素材存在侵权风险；「Get Well Soon」类表达本身无商标，可正常使用。</li>
      </ul>
    </div>
  </div>
</section>

<!-- ============ 09 行动清单 ============ -->
<section>
  <h2><span class="n">09</span>行动清单</h2>
  <div class="card">
    <ol class="steps">
      <li><b>先询价同款供应商</b>：联系 ID 1076910243306（标题含「亚马逊同款康复礼品套装」），确认是否即 Gagalico 的上游，若能直接拿到成品报价可省去组装环节。</li>
      <li><b>组件全部打样</b>：按 BOM 顺序各下单 1–2 件（总支出约 ¥25），核对尺寸是否能装进 21×16.8×9.6 cm 的礼盒，并确认颜色与「康复慰问」主题的视觉统一。</li>
      <li><b>谈批量阶梯价</b>：以 200 套/批为目标，向 7 家组件供应商分别议价（预期降幅 10–20%），把 BOM 采购成本从 ¥{opt} 压到 ¥11–12（≈$1.6）。</li>
      <li><b>定价决策</b>：以 <b>$24.99</b> 为首发价（预计毛利率 {SC['B_opt_2499']['rate']}%），$29.99 为促销后目标价；<b>不要跟进 $16.99 的价格战</b>。</li>
      <li><b>组装与包装</b>：寻找义乌/金华的礼盒组装外包（一件代发群常见服务），把 7 件归集为 1 套后再整批发 FBA，避免多次头程。</li>
      <li><b>上架前复核</b>：用 Sorftime 的利润测算与关键词工具复核 FBA 费、佣金与核心词 CPC，确认广告预算能守住 12% 摊销线。</li>
    </ol>
  </div>
  <div class="note ok"><b>下一步可衔接：</b>amz-profit-calc（FBA 费用与隐赚指数精算）→ amz-listing-creator（标题/五点/A+ 差异化文案）→ amz-ad-planning（关键词 CPC 与广告结构）。</div>
</section>

<footer>
  <div>报告由 <b>Sorftime · amz-supply-chain</b> 生成 · 数据源：Sorftime CLI（Amazon US domain 1 / 1688 domain 601）· 本机已认证 profile</div>
  <div>生成时间：2026-09-11 · 汇率假定 1 USD = {RATE} CNY · 采购价与利润为测算值，实际以供应商报价为准</div>
</footer>

</div>
</body>
</html>'''

path = 'B0FSSBFS37_1688供应链找货报告.html'
open(path, 'w', encoding='utf-8').write(html)
print('written', path, len(html) // 1024, 'KB')
