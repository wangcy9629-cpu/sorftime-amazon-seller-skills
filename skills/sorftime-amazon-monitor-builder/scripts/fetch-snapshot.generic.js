"use strict";
/* =====================================================================
 * fetch-snapshot.generic.js  (通用版 — 从项目复制后参数化)
 * 每日快照管线：抓取 N ASIN ProductRequest → 归一化落盘 snapshots/
 * 用法:
 *   node scripts/fetch-snapshot.generic.js --project tasks/project.json
 *   node scripts/fetch-snapshot.generic.js --project tasks/project.json --date 2026-09-05
 *   node scripts/fetch-snapshot.generic.js --project tasks/project.json --dry-run
 * 依赖: sorftime CLI (本机 profile), project.json（含 main_asin + competitors）
 * ===================================================================== */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const BASE = path.join(__dirname, '..');

/* ---------- 参数 ---------- */
const args = process.argv.slice(2);
const DRY = args.includes('--dry-run');
let dateArg = null;
const di = args.indexOf('--date');
if (di >= 0 && args[di + 1]) dateArg = args[di + 1];
let projArg = null;
const pi = args.indexOf('--project');
if (pi >= 0 && args[pi + 1]) projArg = args[pi + 1];
const TODAY = dateArg || new Date().toISOString().slice(0, 10); // YYYY-MM-DD
if (!/^\d{4}-\d{2}-\d{2}$/.test(TODAY)) { console.error('bad --date:', TODAY); process.exit(3); }

/* ---------- 项目配置（唯一入口：main_asin + competitors + 站点） ---------- */
const PROJECT_FILE = projArg ? path.resolve(BASE, projArg) : path.join(BASE, 'tasks/project.json');
const project = JSON.parse(fs.readFileSync(PROJECT_FILE, 'utf8'));
const DOMAIN = { US: 1, UK: 2, DE: 3, FR: 4, CA: 6, JP: 7, ES: 8, IT: 9, MX: 10, AU: 12 }[project.marketplace || 'US'] || 1;
const PROFILE = process.env.SORFTIME_PROFILE || project.profile || null;

/* ---------- CLI 定位 ---------- */
function findSorftime() {
  const candidates = process.env.SORFTIME_BIN
    ? [process.env.SORFTIME_BIN]
    : [];
  for (const c of candidates) { if (fs.existsSync(c)) return c; }
  return 'sorftime';
}
const SORFTIME = findSorftime();

/* ---------- 读取 project：main + competitors（含 tier） ---------- */
const ASINS = [{ asin: project.main_asin, tier: 'MAIN' }]
  .concat((project.competitors || []).map(c => ({ asin: c.asin, tier: c.tier })));
const MAIN = project.main_asin;
console.log('项目:', project.project, '| 站点:', project.marketplace, '| ASIN 池:', ASINS.length, '个');
if (ASINS.length > 10) console.log('→ 超过 10 个将自动分批（每批 ≤10）');

/* ---------- 调用 sorftime api（≤10/批，13 个分两批） ---------- */
function api(asinCsv) {
  // Windows 下 execFileSync 会剥离内层双引号 → 用 JSON5 单引号形式（CLI 支持 {site:'US'} 风格）
  const payload = "{asin:'" + asinCsv + "'}";
  const cmd = SORFTIME;
  const args = ['api', 'ProductRequest', payload, '--domain', String(DOMAIN)];
  if (PROFILE) args.push('--profile', PROFILE);   // 未指定则用 CLI 当前 active profile
  if (DRY) { console.log('[dry-run]', cmd, args.join(' ')); return null; }
  console.log('[api] ProductRequest', asinCsv.split(',').length, 'ASINs ...');
  const out = execFileSync(cmd, args, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, shell: process.platform === 'win32' });
  return JSON.parse(out);
}
function chunk(arr, n) { const r = []; for (let i = 0; i < arr.length; i += n) r.push(arr.slice(i, i + n)); return r; }

/* ---------- 归一化单条 raw -> snapshot v1 ---------- */
function norm(it, tier) {
  const cents = v => (v == null || v === -9999 || v === 0 ? null : +(v / 100).toFixed(2));
  const bs = (it.BsrCategory && it.BsrCategory[0]) || [];
  const cat = it.Category && it.Category[0];
  const sub = bs[0] || null;          // 子类目名
  const node = bs[1] || null;         // node id
  const subRank = bs[2] != null ? +bs[2] : null;
  const rank = it.Rank != null && it.Rank !== -9999 ? +it.Rank : null; // 父类目排名
  // 月销：ListingSalesVolumeOfMonthTrend 是[日期,值,...] 配对数组，取最后一个值；同配金额
  const mt = it.ListingSalesVolumeOfMonthTrend || [];
  const lastPair = mt.length >= 2 ? mt.slice(-2) : [];
  const est_month = lastPair.length === 2 ? +lastPair[1] : null;
  const amount = est_month != null && it.SalesPrice ? Math.round(est_month * (it.SalesPrice / 100)) : null;
  const delivery = it.IsFBA ? 'AmzFBA' : (it.ShipsFrom ? ('FBM/' + it.ShipsFrom) : 'FBM');
  const price = cents(it.SalesPrice), list = cents(it.ListPrice) || price;
  return {
    asin: it.Asin, tier,
    brand: it.Brand || '', title: (it.Title || '') + (it.SubTitle ? ' ' + it.SubTitle : ''),
    price, list,
    rating: it.Ratings != null && it.Ratings > 0 ? +it.Ratings : null,
    reviews: it.RatingsCount != null ? +it.RatingsCount : null,
    monthly_sales_volume: est_month, monthly_sales_amount: amount, est_month,
    fba: !!it.IsFBA, delivery_type: delivery,
    fba_fee: cents(it.FbaFee),
    buybox: it.BuyboxSeller || null, sellers: it.SellerCount != null ? +it.SellerCount : null,
    variation_count: it.VariationASINCount != null ? +it.VariationASINCount : (Array.isArray(it.VariationASIN) ? it.VariationASIN.length : null),
    cat: sub, rank: subRank,
    top_category: cat ? cat + (rank != null ? ' (Rank: ' + rank + ')' : '') : null,
    subcategory: sub ? sub + (subRank != null ? ' (Rank: ' + subRank + ')' : '') : null,
    days_on_shelf: it.OnlineDays != null && it.OnlineDays >= 0 ? +it.OnlineDays : null,
    online_date: it.OnlineDate || null,
    gross_profit: cents(it.Profit),
    gross_profit_rate: it.ProfitRate != null ? +(+it.ProfitRate).toFixed(2) : null,
    a_plus: !!it.APlus, node_id: node, weight_g: it.Weight != null ? +it.Weight : null
  };
}

/* ---------- 主流程 ---------- */
function main() {
  console.log('=== 每日快照管线 ===', TODAY, '| pool', ASINS.length, 'ASIN |', SORFTIME);
  let rawList = [];
  let requestLeft = null;
  if (!DRY) {
    for (const c of chunk(ASINS, 10)) {
      const resp = api(c.map(a => a.asin).join(','));
      if (!resp || (resp.Code != null && resp.Code !== 0)) {
        console.error('API 失败:', resp && (resp.Message || resp.code));
        process.exit(2);
      }
      const d = resp.Data;
      const arr = Array.isArray(d) ? d : (d ? [d] : []);
      arr.forEach(it => rawList.push(it));
      if (resp.RequestLeft != null) requestLeft = resp.RequestLeft;
      console.log('  Code=0 RequestLeft=' + resp.RequestLeft + ' Consumed=' + resp.RequestConsumed);
    }
  }

  /* 归一化：保持 pool 顺序 */
  const snapshots = [];
  const tierOf = {};
  ASINS.forEach(a => tierOf[a.asin] = a.tier);
  if (DRY) {
    ASINS.forEach(a => snapshots.push({ asin: a.asin, tier: a.tier, title: '(dry-run)' }));
  } else {
    const byAsin = {};
    rawList.forEach(it => { byAsin[it.Asin] = it; });
    for (const a of ASINS) {
      const it = byAsin[a.asin];
      if (!it) { console.warn('⚠️ 缺返回:', a.asin); continue; }
      snapshots.push(norm(it, a.tier));
    }
  }

  const detail = {
    meta: {
      project: project.project, main_asin: MAIN, marketplace: project.marketplace || 'US',
      captured_at: DRY ? TODAY + 'T00:00:00+08:00' : (new Date().toISOString().slice(0, 10) + 'T' + new Date().toTimeString().slice(0, 8) + '+08:00'),
      source: 'sorftime_cli(ProductRequest, domain=' + DOMAIN + ' ' + (project.marketplace || 'US') + ')',
      request_left: DRY ? null : requestLeft,
      pool_size: ASINS.length,
      note: '每日快照：' + ASINS.length + ' ASIN product_detail；由 scripts/fetch-snapshot.generic.js 生成'
    },
    snapshots
  };

  const OUT = path.join(BASE, 'snapshots/' + TODAY + '.pitcher-' + MAIN + '.detail.json');
  if (DRY) {
    console.log('(dry-run 不落盘。预计输出:', path.basename(OUT) + ')');
    return;
  }
  fs.writeFileSync(OUT, JSON.stringify(detail, null, 2), 'utf8');
  console.log('已落盘:', OUT, '(' + snapshots.length, 'ASIN)');

  /* 若存在 build 脚本则重建 dashboard 数据（可选；SKILL 指引里会说明） */
  const build = path.join(BASE, 'scripts/build-dashboard-data.generic.js');
  if (fs.existsSync(build)) {
    console.log('--- 重建 dashboard-data.js ---');
    execFileSync(process.execPath, [build, '--project', PROJECT_FILE], { encoding: 'utf8', stdio: 'inherit', shell: process.platform === 'win32' });
  } else {
    console.log('(未发现 build 脚本，跳过重建)');
  }
}
main();
