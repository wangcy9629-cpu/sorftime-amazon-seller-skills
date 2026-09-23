#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Makeup Mirror market report HTML, 1:1 replicating the Cordless-Snow-Shovel template."""
import json, os, datetime

D = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(D, 'data'))
css = open('../template.css').read().replace('<style>', '').replace('</style>', '')
c = json.load(open('consolidated.json'))
c['records'] = json.load(open('records_coupled.json'))
a = json.load(open('analysis.json'))

months = c['meta']['months']
kpi = c['kpi']
NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# slim records for embedding
recs = []
for r in c['records']:
    info = r.get('info') or {}
    sp = ' · '.join(f"{k}: {v}" for k, v in list(info.items())[:8]) if info else ''
    recs.append({
        'asin': r['asin'], 'parent': r['parent'], 'image': r['photo'],
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
    'meta': c['meta'], 'kpi': kpi, 'records': recs,
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
DATA_JSON = json.dumps(DATA, ensure_ascii=False)

html_head = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Amazon Market Report</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%23eef4fb'/%3E%3Cpath d='M8 22V9h4.2l3.8 8.3L19.8 9H24v13h-3.1v-8.2L17.2 22h-2.4l-3.7-8.2V22H8z' fill='%23ff6b35'/%3E%3C/svg%3E">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js">
</script>
<style>
__REPORT_CSS__
</style>
</head>
<body>
<script data-report-state-bootstrap="1">
(function() {
  var STORAGE_KEY = "reportState:v1:Makeup-Mirror-with-Lights_20260901";
  var VERSION = 1;
  function emptyState() { return {version: VERSION, values: {}}; }
  function loadState() {
    try {
      if (window.__REPORT_STATE__ && window.__REPORT_STATE__.version === VERSION) {
        return JSON.parse(JSON.stringify(window.__REPORT_STATE__));
      }
    } catch (e) {}
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return emptyState();
      var parsed = JSON.parse(raw);
      if (!parsed || parsed.version !== VERSION) return emptyState();
      return parsed;
    } catch (e) { return emptyState(); }
  }
  var state = loadState();
  function persist() { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {} }
  window.REPORT_STATE_STORAGE_KEY = STORAGE_KEY;
  window.reportStorage = {
    getItem: function(key) { return Object.prototype.hasOwnProperty.call(state.values, key) ? state.values[key] : null; },
    setItem: function(key, value) { state.values[key] = String(value); persist(); },
    removeItem: function(key) { delete state.values[key]; persist(); },
    clear: function() { state = emptyState(); try { localStorage.removeItem(STORAGE_KEY); } catch (e) {} },
    exportState: function() { return JSON.parse(JSON.stringify(state)); }
  };
})();
</script>
<div id="reportTimestamps" style="position:fixed;top:8px;right:16px;font-size:11px;color:var(--muted);z-index:100;text-align:right;pointer-events:none">生成: __NOW__<br>修改: <span id="modTime">—</span></div>
<h1>Makeup Mirror with Lights</h1>
<p class="keyword-translation">关键词中文：化妆镜带灯 / 带灯化妆镜（核心词 makeup mirror with lights，月搜索 133,053）</p>
<p class="subtitle">数据驱动的市场结构分析与产品改良报告 &mdash; 57 个产品, __NBRANDS__ 个品牌（美国站·带灯化妆镜，按近6月GMV取Top57）</p>
<nav class="nav-toc"><a href="#decisionBriefModule">核心决策主线</a><a href="#s1b">1. 候选产品与竞品</a><a href="#v1ProductDefinition">2. V1产品定义与机会假设</a><a href="#s1c">3. 利润与广告验证</a><a href="#s2b">4. 用户反馈与风险</a><a href="#s1">5. 市场证据</a><a href="#s1a">类目产品介绍</a><a href="#s2">市场结构分析</a><a href="#marketDetailAppendix">关键词/父体明细</a><a href="#opportunityDetailAppendix">功能/属性/组合明细</a></nav>

<section id="decisionBriefModule" class="decision-brief">
  <div class="decision-brief-head">
    <h2>核心决策主线</h2>
    <span class="decision-brief-sub">先看阶段性决策，再关闭证据、动作与验收</span>
  </div>
  <div id="decisionCommandHost"></div>
  <div id="decisionActionHost" class="decision-action-grid"></div>
  <details class="decision-score-details"><summary>展开判定依据与多维度评分（__SCORE__/100）</summary><div class="decision-scorecard"><div class="decision-score-head"><strong>决策判定清单与多维度评分</strong><div class="decision-score-total">__SCORE__/100</div></div><div class="table-wrap"><table class="decision-score-table"><thead><tr><th>评分维度</th><th>观察值</th><th>规则</th><th>判定</th><th>分数</th><th>业务含义</th></tr></thead><tbody id="scoreTableBody"></tbody></table></div><p class="decision-score-note">评分口径：12 项准入规则加权求和后归一化为百分制（满分 1200 → 100）。判定为「待定」的维度需在样品测试、利润测算或文案扫描补齐证据后重新评审。</p></div></details>
</section>

<h2 id="s1b">1. 候选产品与竞品</h2>

<h3>产品数据总表 <span style="font-size:12px;color:var(--muted);font-weight:400">— 按近6月GMV降序，点击★标注对标产品，点击+添加我方产品，月份左新右旧</span>
<button id="toggleEmptyMonthsBtn" onclick="toggleEmptyMonthColumns()" style="background:var(--card);color:var(--accent);border:1px solid var(--border);border-radius:4px;padding:2px 10px;font-size:11px;cursor:pointer;margin-left:12px">显示全部月份</button>
<button type="button" onclick="jumpToMonthlyColumns()" style="background:var(--card);color:var(--accent);border:1px solid var(--border);border-radius:4px;padding:2px 10px;font-size:11px;cursor:pointer;margin-left:6px">跳到月度销量</button>
<button type="button" onclick="scrollProductTableToStart()" style="background:var(--card);color:var(--accent);border:1px solid var(--border);border-radius:4px;padding:2px 10px;font-size:11px;cursor:pointer;margin-left:6px">回到最前</button></h3>
<div class="product-workflow-toolbar" aria-label="产品判断工作流">
  <strong style="font-size:11px">工作视图</strong>
  <button type="button" data-product-view="decision" onclick="setProductViewMode('decision')">决策</button>
  <button type="button" data-product-view="spec" onclick="setProductViewMode('spec')">规格</button>
  <button type="button" data-product-view="full" onclick="setProductViewMode('full')">完整数据</button>
  <span style="width:1px;height:18px;background:var(--border)"></span>
  <select id="productStatusFilter" aria-label="按产品判断状态筛选" onchange="setProductStatusFilter(this.value)">
    <option value="all">全部状态</option><option value="candidate">候选</option><option value="benchmark">对标</option><option value="excluded">排除</option><option value="unreviewed">未判断</option>
  </select>
  <select id="productBulkStatus" aria-label="批量设置产品状态">
    <option value="candidate">标为候选</option><option value="benchmark">标为对标</option><option value="excluded">标为排除</option><option value="unreviewed">标为未判断</option>
  </select>
  <button type="button" onclick="applyBulkProductStatus()">应用到勾选行</button>
  <span id="productWorkflowSummary" class="product-workflow-summary"></span>
</div>
<div style="display:flex;align-items:center;gap:8px;margin:-2px 0 6px">
  <button id="toggleMyProductRowBtn" type="button" onclick="toggleMyProductEditor()" style="background:var(--card);color:var(--accent);border:1px solid var(--border);border-radius:4px;padding:2px 10px;font-size:11px;cursor:pointer">添加我方产品</button>
  <button id="copyAllAsinsBtn" type="button" onclick="copyAllAsins()" style="background:var(--card);color:var(--accent);border:1px solid var(--border);border-radius:4px;padding:2px 10px;font-size:11px;cursor:pointer">复制全部 ASIN</button>
  <button id="restoreProductColumnsBtn" type="button" onclick="restoreProductColumns()" style="background:var(--card);color:var(--accent);border:1px solid var(--border);border-radius:4px;padding:2px 10px;font-size:11px;cursor:pointer">恢复隐藏列</button>
  <button id="clearAllFiltersBtn" type="button" onclick="clearAllProductFilters()" style="background:var(--card);color:var(--accent);border:1px solid var(--border);border-radius:4px;padding:2px 10px;font-size:11px;cursor:pointer">清除筛选</button>
  <template id="productColHideButtonTemplate"><button type="button" class="col-hide-btn">×</button></template>
  <span id="copyAllAsinsStatus" style="font-size:11px;color:var(--muted)"></span>
</div>
<div id="productTableWrap" class="table-wrap wide" style="max-height:700px">
<table id="productTable"><colgroup id="productColgroup"></colgroup><thead><tr id="productHeadRow"></tr></thead><tbody id="productTablePinnedBody"></tbody><tbody id="productTableBody"></tbody></table>
</div>
<div id="productFilterPopover" class="product-filter-popover" role="dialog" aria-modal="false" aria-label="列筛选">
  <div class="product-filter-head">
    <span id="productFilterTitle">筛选</span>
    <button id="productFilterClose" class="product-filter-close" type="button" aria-label="关闭筛选">×</button>
  </div>
  <div class="product-filter-controls">
    <input id="productFilterSearch" class="product-filter-search" type="search" placeholder="搜索值">
    <div id="productFilterNumberRange" style="display:none">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
        <input id="productFilterMin" class="product-filter-number" type="number" placeholder="最小值">
        <input id="productFilterMax" class="product-filter-number" type="number" placeholder="最大值">
      </div>
    </div>
    <div class="product-filter-actions">
      <button type="button" onclick="selectAllFilterValues()">全选</button>
      <button type="button" onclick="clearFilterSelection()">全不选</button>
      <button type="button" onclick="invertFilterSelection()">反选</button>
      <button type="button" onclick="clearCurrentProductFilter()">清除此列</button>
    </div>
  </div>
  <div id="productFilterValues" class="product-filter-values"></div>
  <div class="product-filter-footer">
    <button id="productFilterCancel" type="button">取消</button>
    <button id="productFilterApply" class="primary" type="button">应用</button>
  </div>
</div>
<div id="productImagePreview" class="product-image-preview" role="dialog" aria-modal="true" aria-label="产品图片预览">
  <button id="productImagePreviewClose" type="button" aria-label="关闭图片预览">×</button>
  <img id="productImagePreviewImg" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==" alt="产品图片预览" hidden>
</div>
<div id="productImageHoverPreview" class="product-image-hover-preview" aria-hidden="true">
  <img id="productImageHoverPreviewImg" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==" alt="" hidden>
</div>

<div id="benchmarkHost"></div>
<h2>2. V1产品定义与机会假设</h2>
<section id="v1ProductDefinition" class="v1-definition"><div class="v1-definition-grid" id="v1Grid"></div>
<div class="opportunity-hypotheses"><h3>Top 3 机会假设</h3><div id="oppHost"></div></div>
</section>
<h2 id="s1c">3. 利润与广告验证</h2>
<h3>利润核算表 <span style="font-size:12px;color:var(--muted);font-weight:400">— 仅显示产品数据表已标星竞品和下方我方产品；首行目标SKU与PPC共用目标售价</span></h3>
<div class="profit-scenario-toolbar" aria-label="利润测算场景">
  <strong>测算场景</strong>
  <button type="button" data-profit-scenario="conservative" onclick="applyProfitScenario('conservative')">保守</button>
  <button type="button" data-profit-scenario="base" class="active" onclick="applyProfitScenario('base')">基准</button>
  <button type="button" data-profit-scenario="optimistic" onclick="applyProfitScenario('optimistic')">乐观</button>
  <span id="profitScenarioNote" style="color:var(--muted)">基准：广告15%、退货8%、仓储2%</span>
  <label style="margin-left:auto">目标毛利%
    <input id="targetMarginRateInput" type="number" min="0" max="80" value="22.0" step="0.5" style="width:58px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px" oninput="setTargetMarginRate(this.value)">
  </label>
</div>
<div style="display:flex;flex-wrap:wrap;gap:12px;padding:8px 12px;background:var(--card);border:1px solid var(--border);border-radius:8px;margin-bottom:8px;font-size:12px">
  <label>汇率: <input id="fxRate" type="number" value="7.15" step="0.01" style="width:65px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px" onchange="recalcProfit()" oninput="recalcProfit()"></label>
  <label>头程RMB/kg: <input id="shippingRmb" type="number" value="8" step="0.5" style="width:55px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px" onchange="recalcProfit()" oninput="recalcProfit()"></label>
  <label>仓储%: <input id="storageRate" type="number" value="2" step="0.5" style="width:50px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px" onchange="recalcProfit()" oninput="recalcProfit()"></label>
  <label>广告%: <input id="adRate" type="number" value="15" step="0.5" style="width:50px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px" onchange="recalcProfit()" oninput="recalcProfit()"></label>
  <label>促销%: <input id="promoRate" type="number" value="0" step="0.5" style="width:50px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px" onchange="recalcProfit()" oninput="recalcProfit()"></label>
  <label>退货%: <input id="returnRate" type="number" value="8" step="0.5" style="width:50px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px" onchange="recalcProfit()" oninput="recalcProfit()"></label>
  <label>佣金%: <input id="commissionRate" type="number" value="15" step="0.5" style="width:50px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px" title="亚马逊Referral Fee，家居类目15%" onchange="recalcProfit()" oninput="recalcProfit()"></label>
</div>
<div class="profit-model-feedback">
  <div id="targetProcurementLimit">填写目标SKU售价、尺寸和重量后，系统将反推满足目标毛利的采购成本上限。</div>
  <div id="profitValidation" class="profit-validation-ok">输入检查：正常</div>
</div>
<div id="profitBenchmarkEmpty" style="display:none;margin:0 0 8px;padding:8px 12px;border:1px dashed var(--border);border-radius:6px;color:var(--muted);font-size:12px">尚未选择对标产品，请在产品数据表点击星标。</div>
<div class="table-wrap wide"><table id="profitTable" style="table-layout:fixed;width:100%"><thead><tr>
  <th style="width:44px">图片</th><th style="width:130px">ASIN</th><th style="width:100px">尺寸(cm/in)</th><th style="width:85px">重量(kg/lb)</th><th style="width:45px">月销</th><th style="width:60px">包装类型</th>
  <th style="width:65px">成交价</th><th style="width:72px">含税成本¥</th><th style="width:58px;font-size:14px">毛利率</th><th style="width:65px">不含税RMB</th><th style="width:55px">不含税$</th><th style="width:50px">头程</th><th style="width:52px">配置费</th>
  <th style="width:48px">佣金</th><th style="width:55px">FBA</th><th style="width:48px">仓储</th><th style="width:65px">毛利RMB</th><th style="width:55px">毛利$</th>
  <th style="width:55px;color:var(--orange)">广告费</th><th style="width:48px;color:var(--orange)">促销费</th><th style="width:52px;color:var(--red)">退货费</th>
  <th style="width:58px">总成本</th><th style="width:52px">采购占比</th><th style="width:52px">配送占比</th></tr></thead><tbody id="profitTableBody"></tbody></table></div>
<div id="fbaOptimTips" style="margin-top:6px"></div>

<div class="keyword-ppc-module" id="keywordPpcModule">
  <h3>PPC启动验证与关键词明细</h3>
  <div class="keyword-ppc-head"><p>以「makeup mirror with lights」为核心的启动词表：搜索量、转化、CPC 与可承受出价均来自 Sorftime 关键词库（更新于 2026-08-25）。可承受 CPC = 均价 × 搜索转化率 ÷ 目标ACOS(25%)。</p><span class="keyword-ppc-limit">展示前 16 个关键词</span></div>
  <div id="keywordPpcEconomicsSummary" class="keyword-ppc-summary-grid"></div>
  <div class="table-wrap wide"><table class="keyword-ppc-table" id="keywordPpcTable"><colgroup>
    <col style="width:200px"><col style="width:92px"><col style="width:110px"><col style="width:240px"><col style="width:84px"><col style="width:88px"><col style="width:88px"><col style="width:80px"><col style="width:80px"><col style="width:74px"><col style="width:84px"><col style="width:88px"><col style="width:64px"><col style="width:84px"><col style="width:80px"><col style="width:64px">
  </colgroup><thead><tr>
    <th class="sortable" data-key="kw" data-type="str">关键词</th><th class="sortable" data-key="tier" data-type="str">词层</th><th class="sortable" data-key="cn" data-type="str">中文释义</th><th>投放建议</th>
    <th class="sortable" data-key="sv" data-type="num">月搜索量</th><th class="sortable" data-key="sales90" data-type="num">90天出单</th><th class="sortable" data-key="products" data-type="num">关联商品数</th><th class="sortable" data-key="scr" data-type="num">搜索转化%</th><th class="sortable" data-key="cvr" data-type="num">点击转化%</th><th class="sortable" data-key="cpc" data-type="num">CPC$</th><th class="sortable" data-key="sug_bid" data-type="num">建议竞价$</th><th class="sortable" data-key="affordable" data-type="num">可承受CPC$</th><th class="sortable" data-key="pri" data-type="str">优先级</th><th class="sortable" data-key="acos" data-type="num">ACOS上限%</th><th class="sortable" data-key="share" data-type="num">点击份额%</th><th class="sortable" data-key="wc" data-type="num">词数</th>
  </tr></thead><tbody id="keywordPpcBody"></tbody></table></div>
</div>

<h2 id="s2b">4. 用户反馈与风险</h2>
<div id="reviewGateHost"></div>
<div class="chart-grid">
  <div class="chart-box">
    <h3>评论结论摘要</h3>
    <div id="reviewSummaryHost"></div>
  </div>
  <div class="chart-box">
    <h3>评论差评痛点分布：占有效差评比例 <span style="font-size:12px;color:var(--muted);font-weight:400">— 基于 Top5 ASIN 的 Amazon Customers Say 负面提及聚合</span></h3>
    <canvas id="painChart" style="max-height:320px"></canvas>
  </div>
  <div class="chart-box">
    <h3>好评保留点</h3>
    <div class="table-wrap" id="posKeepHost"></div>
  </div>
</div>

<h2 id="s1">5. 市场证据</h2>
<div class="kpi-grid" id="kpiGrid"></div>
<div class="chart-grid">
  <div class="chart-box">
    <h3>月度市场趋势与预测</h3>
    <canvas id="trendChart"></canvas>
    <div class="chart-range-wrap">
      <label>起始</label>
      <div class="chart-range-stack">
        <input type="range" class="chart-range" id="trendChartSliderLeft" min="0" step="1" />
        <input type="range" class="chart-range" id="trendChartSliderRight" min="0" step="1" />
        <div class="chart-range-overlay" id="trendChartSliderOverlay"></div>
      </div>
      <label>结束</label>
    </div>
    <div class="fc-quality" style="margin-top:6px;font-size:12px;color:var(--muted);text-align:center">基于过去 __NMONTHS__ 个月数据建模（年季节性+趋势检测），虚线为预测值，阴影为 80% 置信区间</div>
  </div>
  <div class="chart-box">
    <h3>季节性分析</h3>
    <canvas id="seasonalityChart" style="max-height:280px"></canvas>
    <div style="display:flex;gap:20px;margin-top:8px;font-size:12px;color:var(--muted);justify-content:center">
      <span><span style="display:inline-block;width:10px;height:10px;background:#e8783c;border-radius:2px;margin-right:4px"></span>旺季 (&gt;1.3)</span>
      <span><span style="display:inline-block;width:10px;height:10px;background:#8a94a6;border-radius:2px;margin-right:4px"></span>平季</span>
      <span><span style="display:inline-block;width:10px;height:10px;background:#64748b;border-radius:2px;margin-right:4px"></span>淡季 (&lt;0.7)</span>
    </div>
    <div id="seasonalityMeta" style="display:flex;gap:24px;margin-top:8px;font-size:13px;flex-wrap:wrap"></div>
    <p id="seasonalityNote" style="margin-top:6px;font-size:12px;color:var(--muted)"></p>
  </div>
</div>
<h3 id="s1a">类目产品介绍</h3>
<section id="productIntroModule" class="product-intro-module">
  <div class="product-intro-head">
    <div><h3>类目产品说明</h3><span class="product-intro-status">分析生成</span></div>
    <span id="productIntroStatus" class="product-intro-status"></span>
  </div>
  <div class="product-intro-grid" id="productIntroGrid"></div>
</section>
<h3 id="s2">市场结构分析</h3>
<div class="chart-grid">
  <div class="chart-box">
    <h3>价格带分布</h3>
    <canvas id="priceBandChart"></canvas>
    <div class="table-wrap" style="max-height:260px;margin-top:10px" id="priceBandTableHost"></div>
  </div>
  <div class="chart-box">
    <h3>品牌集中度</h3>
    <canvas id="brandDonutChart" style="max-height:280px"></canvas>
    <div class="table-wrap" style="max-height:200px" id="brandCrTableHost"></div>
  </div>
  <div class="chart-box">
    <h3>Top 10 品牌近6月GMV</h3>
    <canvas id="brandBarChart" style="height:500px"></canvas>
  </div>
</div>
<div class="distribution-tabs">
  <h3>销量结构分布</h3>
  <div class="tab-bar"><button class="tab-btn active" onclick="switchDistributionTab(this, 'distPrice')">价格销量分布</button><button class="tab-btn" onclick="switchDistributionTab(this, 'distRating')">星级销量分布</button><button class="tab-btn" onclick="switchDistributionTab(this, 'distSellerType')">卖家与发货方式销量分布</button><button class="tab-btn" onclick="switchDistributionTab(this, 'distBrand')">品牌销量分布</button><button class="tab-btn" onclick="switchDistributionTab(this, 'distSeller')">卖家销量分布</button><button class="tab-btn" onclick="switchDistributionTab(this, 'distAge')">上架时间销量分布</button></div>
  <div id="distPrice" class="tab-content active"><div class="chart-box"><h3>价格销量分布</h3><canvas id="distPriceChart" style="height:360px"></canvas></div><div class="table-wrap" style="margin-top:10px;max-height:260px" id="distPriceTableHost"></div></div>
  <div id="distRating" class="tab-content"><div class="chart-box"><h3>星级销量分布</h3><canvas id="distRatingChart" style="height:360px"></canvas></div><div class="table-wrap" style="margin-top:10px;max-height:260px" id="distRatingTableHost"></div></div>
  <div id="distSellerType" class="tab-content"><div class="chart-box"><h3>卖家与发货方式销量分布</h3><canvas id="distSellerTypeChart" style="height:360px"></canvas></div><div class="table-wrap" style="margin-top:10px;max-height:260px" id="distSellerTypeTableHost"></div></div>
  <div id="distBrand" class="tab-content"><div class="chart-box"><h3>品牌销量分布</h3><canvas id="distBrandChart" style="height:360px"></canvas></div><div class="table-wrap" style="margin-top:10px;max-height:260px" id="distBrandTableHost"></div></div>
  <div id="distSeller" class="tab-content"><div class="chart-box"><h3>卖家销量分布</h3><canvas id="distSellerChart" style="height:360px"></canvas></div><div class="table-wrap" style="margin-top:10px;max-height:260px" id="distSellerTableHost"></div></div>
  <div id="distAge" class="tab-content"><div class="chart-box"><h3>上架时间销量分布</h3><canvas id="distAgeChart" style="height:360px"></canvas></div><div class="table-wrap" style="margin-top:10px;max-height:260px" id="distAgeTableHost"></div></div>
</div>
<div class="chart-box">
  <h3>本年价格与销量分布 <span style="font-size:12px;color:var(--muted);font-weight:400">— 横轴: 2026年销量(件), 纵轴: 价格($), Top3品牌着色，绿色外圈=一年内新品</span></h3>
  <canvas id="priceVolumeScatter" style="max-height:420px"></canvas>
  <div class="scatter-chart-legend scatter-legend" id="scatterLegend"></div>
</div>

<details id="reviewDetailAppendix" class="analysis-appendix"><summary>明细附录：评论原文与动作表</summary>
  <h3>差评问题与改进建议</h3>
  <div class="table-wrap" id="painDetailHost"></div>
  <h3>研发与工厂产品改进开工单</h3>
  <div class="table-wrap" id="ticketHost"></div>
  <h3>重点 ASIN 复盘</h3>
  <div class="table-wrap" id="asinReviewHost"></div>
  <details class="review-excerpts-toggle"><summary>展开重点差评原文摘录</summary>
    <h3>重点差评原文摘录</h3>
    <div class="excerpt-toolbar">
      <button onclick="document.querySelectorAll('.review-excerpt').forEach(function(el){el.open=true})">展开全部</button>
      <button onclick="document.querySelectorAll('.review-excerpt').forEach(function(el){el.open=false})">折叠全部</button>
      <span style="font-size:11px;color:var(--muted)" id="excerptCount"></span>
    </div>
    <div id="excerptHost"></div>
  </details>
</details>
<details id="marketDetailAppendix" class="analysis-appendix"><summary>明细附录：关键词与父体结构</summary>
  <h3>Parent ASIN Top 10 分析</h3>
  <div class="table-wrap" id="parentTableHost"></div>
  <div class="chart-box" style="margin-top:1rem">
    <h3 style="margin:0">Parent ASIN Top 10 月销量+月销售额 <span style="font-size:11px;color:var(--muted);font-weight:400">— 实线销量, 虚线销售额, 点击品牌按钮切换</span></h3>
    <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:6px;justify-content:center" id="brandToggles_groupChart_Parent_ASIN"></div>
    <canvas id="groupChart_Parent_ASIN" style="height:650px"></canvas>
    <div class="chart-range-wrap">
      <label>← 历史</label>
      <input type="range" class="chart-range" id="groupChart_Parent_ASINSlider" min="0" step="1" />
      <label>最近 →</label>
    </div>
  </div>
</details>
<details id="opportunityDetailAppendix" class="analysis-appendix"><summary>明细附录：功能、属性与组合明细</summary>
  <h3 id="s3">功能优先级、卖点共识与产品改良空间</h3>
  <div class="chart-box full"><h3>功能优先级 Kano 分布</h3><div class="scatter-wrap" id="kanoScatter"></div><div class="scatter-legend"><span class="scatter-legend-item"><span class="scatter-legend-dot" style="background:#2f6fed"></span>高覆盖高GMV（门槛功能）</span><span class="scatter-legend-item"><span class="scatter-legend-dot" style="background:#c07d10"></span>中覆盖（溢价功能）</span><span class="scatter-legend-item"><span class="scatter-legend-dot" style="background:#e5484d"></span>低覆盖（观察项）</span></div></div>
  <h3>卖点共识与 Listing 建议</h3>
  <div class="table-wrap" id="consensusHost"></div>
  <h3>属性机会矩阵</h3>
  <div class="table-wrap" id="attMatrixHost"></div>
  <h3 id="s4">竞品格局与组合机会</h3>
  <h3>属性组合机会排名</h3>
  <div class="table-wrap" id="comboHost"></div>
</details>
<div class="footer">Amazon Market Analyzer &mdash; product research report</div>
<div class="report-action-toolbar">
<button id="exportBtn" onclick="exportReport()" style="position:fixed;bottom:16px;right:174px;z-index:100;background:var(--card);color:var(--accent);border:1px solid var(--border);border-radius:6px;padding:4px 12px;font-size:11px;cursor:pointer;font-weight:600">导出副本</button>
<button id="saveCurrentHtmlBtn" onclick="saveCurrentHtml()" style="position:fixed;bottom:16px;right:80px;z-index:100;background:var(--accent);color:#fff;border:none;border-radius:6px;padding:4px 12px;font-size:11px;cursor:pointer;font-weight:600">保存当前HTML</button>
<button id="resetAllBtn" onclick="resetReportState()" style="position:fixed;bottom:16px;right:16px;z-index:100;background:var(--card);color:var(--muted);border:1px solid var(--border);border-radius:6px;padding:4px 12px;font-size:11px;cursor:pointer">重置</button>
</div>
"""

HTML_BODY = html_head.replace('__REPORT_CSS__', css).replace('__NOW__', NOW).replace('__NBRANDS__', str(kpi['brands'])).replace('__SCORE__', str(a['score_100'])).replace('__NMONTHS__', str(len(months)))
open('../_shell.html', 'w').write(HTML_BODY)
print('shell written:', len(HTML_BODY))
