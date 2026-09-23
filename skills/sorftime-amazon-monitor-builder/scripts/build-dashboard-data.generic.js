"use strict";
/* =====================================================================
 * build-dashboard-data.generic.js  (通用版)
 * 读入 Sorftime 落盘快照（详情 / 关键词 / 月度价格趋势）→ 生成 docs/dashboard-data.js
 * 用法: node scripts/build-dashboard-data.generic.js --project tasks/project.json
 * ===================================================================== */
const fs = require('fs');
const path = require('path');

const BASE = path.join(__dirname, '..');
const snapDir = path.join(BASE, 'snapshots');

/* 项目配置（与 fetch-snapshot.generic.js 共用同一 project.json，保证口径一致） */
const args = process.argv.slice(2);
let projArg = null;
const pi = args.indexOf('--project');
if (pi >= 0 && args[pi + 1]) projArg = args[pi + 1];
const PROJECT_FILE = projArg ? path.resolve(BASE, projArg) : path.join(BASE, 'tasks/project.json');
const project = JSON.parse(fs.readFileSync(PROJECT_FILE, 'utf8'));
const MAIN_FIX = project.main_asin;
const DOMAIN_NAME = project.marketplace || 'US';

/* 动态发现最新快照文件（按文件名内嵌日期 YYYY-MM-DD 取最大），支持每日自动化持续跑 */
function latestSnap(prefix, suffix) {
  const files = fs.readdirSync(snapDir).filter(f => f.startsWith(prefix) && f.endsWith(suffix));
  if (!files.length) throw new Error('未找到快照文件: ' + prefix + '*' + suffix);
  files.sort((a, b) => b.localeCompare(a));
  return path.join(snapDir, files[0]);
}
const detailFile = latestSnap('', '.pitcher-' + MAIN_FIX + '.detail.json');
const kwFile     = latestSnap('keywords-', '-' + MAIN_FIX + '.json');
const trendFile  = latestSnap('trend-price-', '-' + MAIN_FIX + '.json');
const detail = JSON.parse(fs.readFileSync(detailFile, 'utf8'));
const kw     = JSON.parse(fs.readFileSync(kwFile, 'utf8'));
const trend  = JSON.parse(fs.readFileSync(trendFile, 'utf8'));
const poolCfg= project;   // generic：project.json 即 pool 配置源

const MAIN = detail.meta.main_asin;                 // 主品 ASIN
const CAPTURED = detail.meta.captured_at;           // e.g. 2026-09-04T11:00:00+08:00
const D0 = CAPTURED.slice(5, 10);                   // '09-04'
const B0 = CAPTURED.slice(0, 10);                   // '2026-09-04'（基线日期，动态）
const RL = detail.meta.request_left != null ? detail.meta.request_left : 29999;   // RequestLeft（优先取快照落盘值）

/* ---------- 短名（显示用）→ 由 project.json 的 alias 生成；主品带 ★ ---------- */
const SHORT = {};
if (project.competitors) {
  for (const c of project.competitors) SHORT[c.asin] = c.alias || c.asin;
}
SHORT[MAIN] = '★ ' + (project.main_alias || SHORT[MAIN] || '主品');
if (project.main_alias) SHORT[MAIN] = '★ ' + project.main_alias;

/* ---------- 词表字典（CN 中文名 / NOISE 噪音词）→ 外置 assets/term-dict.js，可按品类增删 ---------- */
const dictPath = path.join(BASE, 'assets/term-dict.js');
let CN = {}, NOISE = new Set();
if (fs.existsSync(dictPath)) {
  const dict = require(dictPath);
  CN = dict.CN || {};
  NOISE = (dict.NOISE instanceof Set) ? dict.NOISE : new Set(dict.NOISE || []);
} else {
  console.warn('⚠️ 未找到 assets/term-dict.js —— 使用空词表（中文名显示原文、噪音词不过滤）');
}

/* ---------- 解析位置 P{page}#{pos} → 全局位次（Sorftime 60/页栅格） ---------- */
function parsePos(s){ if(!s) return null; const m=String(s).match(/^P(\d+)#(\d+)$/); return m?((+m[1]-1)*60 + (+m[2])):null; }

/* ---------- 1. 关键词聚合 ---------- */
// wordInfo: {vol, org:Set(asin), ad:Set(asin), pos:{asin:globalOrg}, adPos:{asin:globalAd}}
const W = new Map();
const keepTerms = {}; // asin -> [{w, vol, org, ad}]
for (const [asin, rows] of Object.entries(kw.terms)) {
  keepTerms[asin] = [];
  for (const r of rows) {
    const w = r[0], vol = r[1], orgRaw = r[3], adRaw = r[4];
    if (NOISE.has(w)) continue;
    const org = parsePos(orgRaw), ad = parsePos(adRaw);
    if (org == null && ad == null) continue;
    let wi = W.get(w); if (!wi) { wi = { vol, org:new Set(), ad:new Set(), pos:{}, adPos:{} }; W.set(w, wi); }
    if (org != null) { wi.org.add(asin); wi.pos[asin] = org; }
    if (ad  != null) { wi.ad.add(asin);  wi.adPos[asin] = ad; }
    keepTerms[asin].push({ w, vol, org, ad });
  }
}
const words = [...W.keys()];
const asins = detail.snapshots.map(s => s.asin);

/* ---------- 2. 词库 wordlist（全部保留词，按月搜量降序） ---------- */
const wordlist = words
  .map(w => {
    const wi = W.get(w);
    const op = Object.values(wi.pos), ap = Object.values(wi.adPos);
    const best = [].concat(op, ap).length ? Math.min(...[].concat(op, ap)) : null;
    return { w, cn: CN[w] || '', vol: wi.vol, cc: wi.org.size + wi.ad.size, best };
  })
  .sort((a,b)=> b.vol - a.vol);

/* ---------- 3. 直接竞争词池 pool（≥2 ASIN 有自然位；per 含广告位信息） ---------- */
const pool = [];
for (const w of words) {
  const wi = W.get(w);
  if (wi.org.size < 2) continue;
  const per = {};
  for (const a of asins) {
    const hasOrg = wi.pos[a] != null, hasAd = wi.adPos[a] != null;
    if (hasOrg || hasAd) per[a] = { p: hasOrg ? wi.pos[a] : null, ad: hasAd ? wi.adPos[a] : null };
  }
  pool.push({ w, cn: CN[w] || '', vol: wi.vol, cc: wi.org.size, best: Math.min(...Object.values(wi.pos)), per });
}
pool.sort((a,b)=> (b.cc - a.cc) || (b.vol - a.vol));

/* ---------- 4. per_asin（各 ASIN 词覆盖统计） ---------- */
const per_asin = {};
for (const s of detail.snapshots) {
  const a = s.asin;
  let org=0,t10=0,t20=0,t50=0,ad=0;
  for (const t of keepTerms[a]) {
    if (t.org != null) { org++; if(t.org<=10)t10++; if(t.org<=20)t20++; if(t.org<=50)t50++; }
    if (t.ad  != null) ad++;
  }
  per_asin[a] = { name: SHORT[a] || s.brand, org, t10, t20, t50, ad };
}

/* ---------- 5. gaps：主品无自然位、但 ≥2 竞品在池内自然进入的高流量词 ---------- */
const gaps = pool
  .filter(p => p.vol >= 1000 && !(p.per[MAIN] && p.per[MAIN].p))
  .map(p => ({ w:p.w, vol:p.vol, cc:p.cc, missing:[{ asin:MAIN, name:SHORT[MAIN] }], best:p.best }))
  .sort((a,b)=> b.vol - a.vol).slice(0, 30);

/* ---------- 6. asins（详情快照 + 近12月价格序列 price7 + bsr14 空） ---------- */
const PRICE_WINDOW = 12;
function lastMonths(rows){
  const v = (rows||[]).filter(x=>x.v>0).slice(-PRICE_WINDOW);
  return v.map(x=>({ d:x.m, v:x.v }));
}
const ASINS = detail.snapshots.map(s => ({
  asin:s.asin, brand:s.brand, title:s.title, price:s.price, list:s.list, deal:null,
  rank:s.rank, rating:s.rating, reviews:s.reviews, est_month:s.monthly_sales_volume, est_amount:s.monthly_sales_amount,
  fba:s.fba, buybox:s.buybox, sellers:s.sellers, cat:s.cat,
  price7:lastMonths(trend.trends[s.asin]), bsr14:[],
  tier:s.tier, name:SHORT[s.asin]||s.brand, delivery_type:s.delivery_type, fba_fee:s.fba_fee,
  variation_count:s.variation_count, days_on_shelf:s.days_on_shelf, online_date:s.online_date,
  top_category:s.top_category, subcategory:s.subcategory, gross_profit_rate:s.gross_profit_rate, node_id:s.node_id
}));

/* ---------- 7. changes：相邻两个月度均价环比（真数据，无变化不生成） ---------- */
const changes = [];
for (const s of detail.snapshots) {
  const rows = (trend.trends[s.asin]||[]).filter(x=>x.v>0);
  if (rows.length < 2) continue;
  const before = rows[rows.length-2], after = rows[rows.length-1];
  const delta = +(after.v - before.v).toFixed(2);
  if (Math.abs(delta) < 0.5) continue;
  changes.push({
    date: D0, asin: s.asin, name: SHORT[s.asin]||s.brand,
    field: '月度均价 ' + before.m.slice(2).replace('-','/') + '→' + after.m.slice(2).replace('-','/'),
    before: before.v, after: after.v,
    lvl: Math.abs(delta) >= 5 ? 'P1' : 'P2',
    src: 'sorftime_cli(ProductTrend.Price monthly)'
  });
}
changes.sort((a,b)=> Math.abs(b.after-b.before) - Math.abs(a.after-a.before));

/* ---------- 8. signals（通用数据规则引擎：Buybox 第三方/渠道名不一致/FBM 履约/低价锚点/月初闪折） ---------- */
// 品类专属洞察不在此硬编码——由运行本 skill 的 agent 依用户品类现场补充（见 SKILL.md 第 6 步）。
const signals = [];
const by = a => ASINS.find(x=>x.asin===a);
const nm = a => (SHORT[a] || (by(a)&&by(a).brand) || a);
function sig(title,lvl,reason,evidence){ signals.push({title,lvl,reason,evidence}); }

// R1 主品 Buybox 被第三方持有（BuyboxSeller 不是主品 Brand，且卖家数>1 才提示）
const mainBox = by(MAIN);
if (mainBox && mainBox.buybox && mainBox.brand &&
    String(mainBox.buybox).toLowerCase() !== String(mainBox.brand).toLowerCase() &&
    mainBox.sellers != null && mainBox.sellers > 1) {
  sig('主品 Buybox 由第三方卖家持有 · 疑似跟卖', 'P1',
    `主品（${mainBox.brand}）Buybox 现由 ${mainBox.buybox} 持有（与品牌名不一致），卖家数 ${mainBox.sellers} → 需人工确认是否被跟卖抢 Buybox。`,
    `sorftime_cli(ProductDetail): Buybox=${mainBox.buybox} / Brand=${mainBox.brand} / Sellers=${mainBox.sellers}`);
}
// R2 任一竞品 Buybox 与品牌不一致（第三方持 Buybox 渠道信号）
for (const a of ASINS.filter(x=>x.asin!==MAIN)) {
  const it = by(a.asin);
  if (!it || !it.buybox || !it.brand) continue;
  if (String(it.buybox).toLowerCase() === String(it.brand).toLowerCase()) continue;
  sig('竞品 Buybox 渠道名与品牌不一致 · 待人工确认', 'P2',
    `${nm(a.asin)} Buybox 由 ${it.buybox} 持有（品牌 ${it.brand}），月销 ${it.est_month??'--'} → 若为同集团渠道则正常，否则注意第三方持 Buybox。`,
    `sorftime_cli(ProductDetail): Buybox=${it.buybox} / Brand=${it.brand}`);
}
// R3 FBM 履约且无货架天数（配送时效落后 FBA 的信号）
for (const a of ASINS.filter(x=>x.asin!==MAIN)) {
  const it = by(a.asin);
  if (!it || it.fba || !/FBM/i.test(String(it.delivery_type||''))) continue;
  sig('竞品为 FBM 自发货 · 配送时效落后', 'P2',
    `${nm(a.asin)}（${it.brand||''}）以 FBM 履约（非 FBA）${(it.days_on_shelf==null||it.days_on_shelf===0)?'且无货架天数记录':''} → 配送时效落后 FBA 竞品，可能以低价引流。`,
    `sorftime_cli(ProductDetail): DeliveryType=${it.delivery_type} / DaysOnShelf=${it.days_on_shelf}`);
}
// R4 低价走量大卖锚点（月销 Top2 且价格 < 主品 70%）
const priced = ASINS.filter(a => by(a.asin) && by(a.asin).est_month && by(a.asin).price).sort((a,b)=> (by(b.asin).est_month - by(a.asin).est_month));
const mainPrice = mainBox && mainBox.price;
const anchors = priced.filter(a => mainPrice && by(a.asin).price < mainPrice*0.7).slice(0,2);
if (anchors.length >= 1 && mainPrice) {
  sig('低价走量大卖形成价格带下沿锚点', 'P2',
    `${anchors.map(a=>nm(a.asin)+'（$'+by(a.asin).price+'，月销 '+by(a.asin).est_month+'）').join('与')} 价格显著低于主品 $${mainPrice} → 价格敏感流量可能被截走，需用品牌/场景差异防守。`,
    'sorftime_cli(ProductDetail): 池内月销前列存在低价走量款');
}
// R5 主品最近两个月度均价变化 >5%（月初闪折/调价窗口）
if (mainBox) {
  const rows = (trend.trends[MAIN]||[]).filter(x=>x.v>0);
  if (rows.length >= 2) {
    const b0 = rows[rows.length-2], b1 = rows[rows.length-1];
    const dPct = (b1.v - b0.v)/b0.v*100;
    if (Math.abs(dPct) >= 5) {
      sig('主品月度均价波动显著 · 检查促销排期', dPct<=-10?'P1':'P2',
        `主品月度均价 ${b0.m} $${b0.v} → ${b1.m} $${b1.v}（${dPct>=0?'+':''}${dPct.toFixed(1)}%），实时价 $${mainPrice} → 建议人工复核促销排期与价格保护。`,
        `sorftime_cli(ProductTrend.Price): ${b0.m}=${b0.v} / ${b1.m}=${b1.v} vs 实时 ${mainPrice}`);
    }
  }
}

/* ---------- 9. suggestions（规则驱动：主品标题未覆盖高流量词 / 广告零位 vs 竞品买量） ---------- */
// gapTitles 高频词清单可按品类扩充（SKILL.md 说明如何改）。通用版取词库内 vol 最高且主品未覆盖的前 5 个词。
function sugg(kind,label,lvl,reason,evidence,asin){ return {kind,label,lvl,reason,evidence,asin}; }
const suggestions = [];
const poolBest = w => { const p=pool.find(x=>x.w===w); return p; };
function compNames(w){ const p=poolBest(w); if(!p) return '--'; return Object.entries(p.per).filter(([a,v])=>v.p).sort((x,y)=>x[1].p-y[1].p).map(([a,v])=>nm(a)+' #'+v.p).join('、'); }
const mainTitle = ((by(MAIN)||{}).title||'').toLowerCase();
const gapTitles = wordlist
  .filter(w => w.vol >= 1000 && !(poolBest(w.w) && poolBest(w.w).per[MAIN] && poolBest(w.w).per[MAIN].p)
              && !new Set(['water','water bottle']).has(w.w))   // 占位排除项：按品类调整
  .slice(0, 5);
for (const w of gapTitles) {
  suggestions.push(sugg('Title', `Title·${w.w} | 高流量词未进入且标题未覆盖`, 'P2',
    `词库中 “${w.w}” 月搜 ${w.vol>=1000000?(w.vol/1000000).toFixed(1)+'M':Math.round(w.vol/1000)+'K'}，${w.cc} 个 ASIN 进入自然排名（${compNames(w.w)}），主品无自然位且标题未覆盖 → 若产品形态允许，建议在标题/五点加入该表达。系统未自动修改 Amazon。`,
    `${w.w}（搜索量 ${w.vol}）· 竞品最佳 #${w.best}`,
    MAIN));
}
// 广告空缺建议（主品 0 广告位 vs 竞品买量证据）
const adEv = [];
for (const a of asins) { const n=(keepTerms[a]||[]).filter(t=>t.ad!=null).length; if(n>0 && a!==MAIN) adEv.push(`${nm(a)}(${n}词)`); }
if (adEv.length) {
  suggestions.push(sugg('Ads', 'Ads·头部词广告测试 | 主品反查零广告位', 'P2',
    `主品反查词中无广告位记录；竞品 ${adEv.join('、')} 已在头部词买量 → 主品 Listing 相关性与评分确立前，可先在核心 3-5 词小额投放测试转化。`,
    `ASINRequestKeyword(page1): 主品 AdPosition=0；竞品广告词来自同一反查快照`,
    MAIN));
}

/* ---------- 10. schedule（任务配置，保持模板语义） ---------- */
const schedule = [
  { task:'competitor_snapshot', freq:'每日 02:00', use:'保存价格、BSR 和基础快照（13 ASIN）', status:'enabled' },
  { task:'competitor_history_refresh', freq:'每日 03:00', use:'保存近 30 天价格/排名历史（ProductTrend）', status:'enabled' },
  { task:'keyword_rank_monitor', freq:'每日 03:30', use:'保存自然/广告排名快照（ASINRequestKeyword）', status:'enabled' },
  { task:'keyword_gap_scan', freq:'每周一 04:00', use:'对比主品 vs 竞品关键词矩阵，刷新 Keyword Gap', status:'enabled' },
  { task:'competitor_discovery', freq:'每周一 05:00', use:'按产品边界扫描新上架同赛道候选竞品', status:'enabled' },
  { task:'buybox_watch', freq:'每小时', use:'Buybox 持有者变化监控（跟卖预警）', status:'disabled' }
];

/* ---------- totals / meta ---------- */
const poolWords = pool.length;
const totals = {
  asins: ASINS.length,
  words: wordlist.length,
  top10_words: pool.filter(p=>p.best<=10).length,
  top20_words: pool.filter(p=>p.best<=20).length,
  top50_words: pool.filter(p=>p.best<=50).length,
  ad_words: words.filter(w=>W.get(w).ad.size>0).length,
  pool: poolWords,
  changes: changes.length,
  request_left: RL
};
const meta = {
  project: detail.meta.project || project.project,
  site: DOMAIN_NAME,
  status: 'ready',
  captured_at: CAPTURED,
  schema: 'amazon-competitor-monitor/snapshot.daily.v1',
  main_asin: MAIN,
  main_title: by(MAIN).title,
  main_price: by(MAIN).price,
  pool_size: ASINS.length,
  own_count: 1,
  comp_count: ASINS.length - 1,
  topk: 20,
  boundary: project.boundary || poolCfg.meta && poolCfg.meta.product_boundary || '',
  baseline: B0,
  snapshot_files: [
    { file: path.basename(detailFile), tag: '快照', note: ASINS.length + ' ASIN product_detail 实时快照' },
    { file: path.basename(kwFile), tag: '最新', note: '关键词反查快照' },
    { file: path.basename(trendFile), tag: '最新', note: '月度平均售价序列（PriceTrend 聚合）' }
  ]
};

/* ---------- 输出 ---------- */
const MONITOR_DATA = { meta, totals, per_asin, asins: ASINS, wordlist, pool, changes, gaps, suggestions, signals, schedule };
const js = '/* 自动生成：' + new Date().toISOString() + ' · 由 scripts/build-dashboard-data.generic.js 生成，请勿手改 */\n'
  + 'window.MONITOR_DATA = ' + JSON.stringify(MONITOR_DATA) + ';\n';
const docsDir = path.join(BASE, 'docs');
if (!fs.existsSync(docsDir)) fs.mkdirSync(docsDir, { recursive: true });
fs.writeFileSync(path.join(docsDir, 'dashboard-data.js'), js, 'utf8');

/* 控制台摘要 */
console.log('=== ' + (meta.project || '项目') + ' 数据重建摘要 ===');
console.log('meta.project:', meta.project, '| main:', MAIN, '| captured:', CAPTURED);
console.log('ASIN 总数:', ASINS.length, '(自有 1 + 竞品', ASINS.length-1, ')');
console.log('词库 wordlist:', wordlist.length, '词 | 直接竞争词池 pool:', poolWords, '词');
console.log('totals:', JSON.stringify(totals));
console.log('per_asin:'); Object.entries(per_asin).forEach(([a,k])=>console.log('  ', a, k.name, JSON.stringify({org:k.org,t10:k.t10,t20:k.t20,t50:k.t50,ad:k.ad})));
console.log('changes:', changes.length, '条'); changes.forEach(c=>console.log('  ', c.name, c.field, c.before, '→', c.after, c.lvl));
console.log('gaps:', gaps.length, '条 | suggestions:', suggestions.length, '| signals:', signals.length);
console.log('输出文件: docs/dashboard-data.js (' + (js.length/1024).toFixed(1) + ' KB)');
