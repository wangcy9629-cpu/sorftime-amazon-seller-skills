/* Makeup Mirror Market Report — application logic (1:1 template replica) */
(function() {
'use strict';
var R = window.REPORT_DATA;
var months = R.meta.months;
var MC = months.length;
var records = R.records;
var byAsin = {}; records.forEach(function(r){ byAsin[r.asin] = r; });
var storage = window.reportStorage || window.localStorage;

function esc(s){ return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function fmt$(v){ if(v==null||isNaN(v)) return '—'; return '$' + Number(v).toLocaleString(undefined,{maximumFractionDigits:v<100?2:0}); }
function fmtN(v){ if(v==null||isNaN(v)) return '—'; return Number(v).toLocaleString(undefined,{maximumFractionDigits:0}); }
function fmtK$(v){ if(v==null||isNaN(v)) return '—'; if(v>=1e6) return '$'+(v/1e6).toFixed(1)+'M'; if(v>=1e3) return '$'+(v/1e3).toFixed(1)+'k'; return '$'+v.toFixed(0); }
function link(asin){ return '<a href="https://www.amazon.com/dp/'+esc(asin)+'" target="_blank" style="color:var(--accent2)">'+esc(asin)+'</a>'; }

/* ============ state persistence ============ */
var workflow = (function(){ try { return JSON.parse(storage.getItem('productWorkflowStatuses')||'{}'); } catch(e){ return {}; } })();
function saveWorkflow(){ try{ storage.setItem('productWorkflowStatuses', JSON.stringify(workflow)); }catch(e){} }
records.forEach(function(r){ if(!workflow[r.asin]) workflow[r.asin] = (r.rev6m >= 300000) ? 'benchmark' : 'unreviewed'; });
function starredAsins(){ return records.filter(function(r){ return workflow[r.asin]==='benchmark'; }).map(function(r){ return r.asin; }); }

/* ============ 1. decision brief ============ */
function tag(cls, txt){ return '<span class="tag tag-'+cls+'">'+esc(txt)+'</span>'; }
function renderDecision(){
  var d = R.decision;
  var host = document.getElementById('decisionCommandHost');
  var pains = R.pain_rows;
  var p0 = pains.length ? pains[0] : null;
  var actions = [
    '针对P0痛点「'+(p0?p0.name:'')+'」做样品验证：'+(p0?'安装/供电/灯光三项老化测试，不合格不立项':''),
    '以$'+R.head.top10_avg.toFixed(2)+'（Top10均价）作为首轮利润测算售价，录入真实采购、头程、FBA、佣金和目标ACOS。',
    '为makeup mirror with lights / vanity mirror with lights / led makeup mirror分别建立Exact广告组；按PPC明细中的建议竞价和可承受CPC设上限，后台用真实点击、订单和花费复核。'
  ];
  host.innerHTML = '<div class="decision-command">'
    + '<div class="decision-command-primary"><div class="decision-command-label">当前决策</div><div class="decision-command-verdict">'+esc(d.verdict)+'</div><div class="decision-command-stage">'+esc(d.stage)+'</div></div>'
    + '<div class="decision-command-meta">'
    + '<div class="decision-command-item"><strong>决策置信度</strong><span class="confidence-watch">'+esc(d.confidence)+'</span></div>'
    + '<div class="decision-command-item"><strong>最大风险/否决项</strong><span>'+esc(d.risk)+'</span></div>'
    + '<div class="decision-command-item"><strong>下一评审条件</strong><span>样品通过P0痛点复测；保守场景广告后贡献毛利>0且毛利率≥22%。</span></div>'
    + '</div></div>'
    + '<div class="decision-command-item" style="border:1px solid var(--border);border-radius:8px;margin-bottom:10px"><strong style="padding:10px 14px 0">立即动作</strong><ul class="decision-command-actions">'
    + actions.map(function(a){ return '<li>'+esc(a)+'</li>'; }).join('') + '</ul></div>';

  var avgTop5 = R.head.top5_avg, fba10 = R.head.fba_top10, new1y = R.head.new_1y;
  var modules = [
    {key:'product', h:'产品定义与质量验证', rows:[
      ['结论', 'P0评论痛点识别到「'+(p0?p0.name:'功能失效')+'」，占有效差评 '+(p0?p0.share+'%':'')],
      ['关键证据', p0 && p0.quotes[0] ? esc(p0.quotes[0]) : '—'],
      ['下一步', (p0?p0.name+'为第一改良项；':'')+'双面镜面（1X+放大）与3色温触控调光写入V1规格书'],
      ['验收标准', '3台样机覆盖主要使用场景复测，关键问题不复现；测试记录和整改闭环完成后方可量产。']
    ]},
    {key:'price_profit', h:'价格与利润验证', rows:[
      ['结论', 'Top5/Top10均价 $'+avgTop5.toFixed(2)+' / $'+R.head.top10_avg.toFixed(2)+'，处于 $15-60 主流价格带，判定可进入'],
      ['关键证据', '观察值 前5: $'+avgTop5.toFixed(2)+' / 前10: $'+R.head.top10_avg.toFixed(2)+'；类目均价 $'+R.kpi.avg_price.toFixed(2)],
      ['下一步', '以$'+R.head.top10_avg.toFixed(2)+'作为首轮利润测算售价，录入真实采购、头程、FBA、佣金和目标ACOS。'],
      ['验收标准', '保守场景广告后贡献毛利大于0，毛利率不低于22%；否则停止该SKU。']
    ]},
    {key:'listing_ads', h:'Listing 与广告验证', rows:[
      ['结论', '核心词 makeup mirror with lights 月搜索 133,053、点击转化率 8.75%，广告可用但需控价'],
      ['关键证据', 'vanity mirror with lights 月搜索 318,096（类目最大词）；主词 CPC ≈ $1.36'],
      ['下一步', '标题前置带灯/放大核心属性；Exact 组按 PPC 明细建议竞价起量，SP+SB 组合打关联流量。'],
      ['验收标准', '首月 ACOS ≤ 目标25%，主推词自然位进入前3页。']
    ]},
    {key:'risk', h:'风险与准入复核', rows:[
      ['结论', '中位评论数 '+fmtN(R.kpi.median_reviews)+' 偏高，老链接积累深；市场分散（HHI '+R.kpi.hhi+'）'],
      ['关键证据', '一年内新品 '+new1y+' 个，其中月均300+件的成功新品 '+R.head.new_1y_ok+' 个'],
      ['下一步', '以差异化配置（双面+放大+3色温）切入，避开纯低价红海；备货卡位12月旺季。'],
      ['验收标准', '旺季第一个月（11月）前60-75天完成下单与物流排期；新品首评周期≤45天。']
    ]}
  ];
  document.getElementById('decisionActionHost').innerHTML = modules.map(function(m){
    return '<article class="decision-action-module" data-module-key="'+m.key+'"><h3>'+m.h+'</h3><dl class="decision-action-list">'
      + m.rows.map(function(r){ return '<div class="decision-action-row'+(r[0]==='关键证据'?' evidence':'')+'"><dt>'+r[0]+'</dt><dd>'+r[1]+'</dd></div>'; }).join('')
      + '</dl></article>';
  }).join('');

  document.getElementById('scoreTableBody').innerHTML = R.score_rows.map(function(s){
    return '<tr><td>'+esc(s.dim)+'</td><td>'+esc(s.obs)+'</td><td>'+esc(s.rule)+'</td><td>'+tag(s.verdict[0], s.verdict[1])+'</td><td>'+s.score+'</td><td style="color:var(--muted)">'+esc(s.note)+'</td></tr>';
  }).join('');
}

/* ============ 2. product table ============ */
var COUPLING_KEYS = ['形状','安装方式','边框材质','放大倍数','供电方式','灯光模式','可调光','颜色','镜面尺寸','重量'];
var productViewMode = 'decision';
var statusFilter = 'all';
var selected = {};
var sortKey = 'rev6m', sortType = 'num', sortDir = -1;
var hiddenCols = {};
var colFilters = {};
var showEmptyMonths = false;

function viewCols(){
  var base = [
    {k:'ops', l:'选择/状态'},
    {k:'asin', l:'ASIN', t:'str'},
    {k:'image', l:'图片'},
    {k:'title', l:'标题', t:'str'},
    {k:'brand', l:'品牌', t:'str'},
    {k:'price', l:'价格', t:'num'},
    {k:'rating_reviews', l:'评分/评论', t:'num'},
    {k:'units30', l:'30d销量', t:'num'},
    {k:'trend', l:'趋势'},
    {k:'size_weight', l:'尺寸/重量 (cm/kg)', t:'str'},
    {k:'size_segment', l:'尺寸分段', t:'str'},
    {k:'days', l:'上架时间/天数', t:'num'}
  ];
  var spec = COUPLING_KEYS.map(function(f){ return {k:'coupling_'+f, l:f, t:'str'}; });
  var money = [
    {k:'rev6m', l:'近6月GMV', t:'num'},
    {k:'y26u', l:'2026销量', t:'num'}, {k:'y26r', l:'2026销售额', t:'num'},
    {k:'y25u', l:'2025销量', t:'num'}, {k:'y25r', l:'2025销售额', t:'num'},
    {k:'y24u', l:'2024销量', t:'num'}, {k:'y24r', l:'2024销售额', t:'num'}
  ];
  var mm = months.map(function(m){ return {k:'month_metrics_'+m, l:m, month:m}; });
  if(productViewMode==='decision') return base.concat([money[0]]).concat(mm);
  if(productViewMode==='spec') return base.concat(spec).concat(money.slice(0,1));
  return base.concat(spec).concat(money).concat(mm);
}
function colVisible(c){ return !hiddenCols[c.k]; }
function cellVal(r, c){
  switch(c.k){
    case 'ops': return ''; case 'image': return ''; case 'trend': return '';
    case 'asin': return r.asin; case 'title': return r.title||''; case 'brand': return r.brand||'';
    case 'price': return r.price||0; case 'rating_reviews': return r.rating||0;
    case 'units30': return r.units30||0; case 'size_weight': return r.dims && r.dims.length>=2 ? r.dims.slice(0,2).join('x')+'/'+r.wt : '';
    case 'size_segment': return (r.wt||0)<=9 && Math.max.apply(null,(r.dims&&r.dims.length?r.dims:[0]))<=41 ? '小标准件':'大号标准件';
    case 'days': return r.days||0;
    case 'rev6m': return r.rev6m; case 'y26u': return r.y26u; case 'y26r': return r.y26r;
    case 'y25u': return r.y25u; case 'y25r': return r.y25r; case 'y24u': return r.y24u; case 'y24r': return r.y24r;
    default:
      if(c.k.indexOf('coupling_')===0) return r.coupling[c.k.slice(9)]||'';
      if(c.k.indexOf('month_metrics_')===0){ var i=months.indexOf(c.month); return (r.units[i]||0)+'/'+(r.rev[i]||0); }
      return '';
  }
}
function rowVisible(r){
  var st = workflow[r.asin]||'unreviewed';
  if(statusFilter!=='all' && statusFilter!==st) return false;
  for(var k in colFilters){
    var f = colFilters[k]; var c = null;
    viewCols().forEach(function(cc){ if(cc.k===k) c=cc; });
    if(!c) continue;
    var v = cellVal(r, c);
    if(f.mode==='set'){ if(f.values.indexOf(String(v))<0) return false; }
    else { var n=parseFloat(v); if(isNaN(n)||n<f.min||n>f.max) return false; }
  }
  return true;
}
function sortedRows(){
  var rows = records.slice().filter(rowVisible);
  if(sortKey){
    rows.sort(function(a,b){
      var c = null; viewCols().forEach(function(cc){ if(cc.k===sortKey) c=cc; });
      var va = cellVal(a,c), vb = cellVal(b,c);
      if(sortType==='num'){ va=parseFloat(va)||0; vb=parseFloat(vb)||0; return (va-vb)*sortDir; }
      return String(va).localeCompare(String(vb))*sortDir;
    });
  } else rows.sort(function(a,b){ return b.rev6m-a.rev6m; });
  return rows;
}
function sparklineSvg(r){
  var pts = r.units.slice(-12).map(function(v){ return v||0; });
  var mx = Math.max.apply(null, pts.concat([1]));
  var w=74,h=26;
  var path = pts.map(function(v,i){ return (i/(pts.length-1)*w).toFixed(1)+','+(h-2-(v/mx)*(h-4)).toFixed(1); }).join(' ');
  return '<svg width="'+w+'" height="'+h+'" style="display:block"><polyline points="'+path+'" fill="none" stroke="#2f6fed" stroke-width="1.5"/></svg>';
}
function trendClass(r){
  var a = (r.units.slice(-3).reduce(function(s,v){return s+(v||0);},0))/3;
  var b = (r.units.slice(-6,-3).reduce(function(s,v){return s+(v||0);},0))/3;
  if(!b) return 'tag-info';
  var g = (a-b)/b;
  return g>0.15?'tag-pass':(g<-0.15?'tag-risk':'tag-pending');
}
function renderProductTable(){
  var cols = viewCols().filter(colVisible);
  var cg = cols.map(function(c){ return '<col data-col-key="'+esc(c.k)+'">'; }).join('');
  document.getElementById('productColgroup').innerHTML = cg;
  var head = cols.map(function(c){
    var sortable = c.t ? ' class="sortable'+(sortKey===c.k?(sortDir>0?' asc':' desc'):'')+'" data-key="'+esc(c.k)+'" data-type="'+c.t+'" data-col-key="'+esc(c.k)+'"' : ' data-col-key="'+esc(c.k)+'"';
    var hide = '<button type="button" class="col-hide-btn" data-col-hide="'+esc(c.k)+'" title="隐藏列">×</button>';
    var filter = (c.t) ? '<button type="button" class="col-filter-btn" data-col-filter="'+esc(c.k)+'" title="筛选列">▽</button>' : '';
    var monthAttr = c.month ? ' data-month="'+c.month+'" title="'+c.month+'：销量 / 销售额 / 月均价"' : '';
    return '<th'+sortable+monthAttr+'>'+esc(c.l)+hide+filter+'</th>';
  }).join('');
  document.getElementById('productHeadRow').innerHTML = head;
  bindHead();

  var rows = sortedRows();
  var pinned = rows.filter(function(r){ return workflow[r.asin]==='benchmark'; });
  var body = rows.map(function(r){ return rowHtml(r, false); }).join('');
  document.getElementById('productTableBody').innerHTML = body;
  var pinnedHtml = pinned.map(function(r){ return rowHtml(r, true); }).join('');
  pinnedHtml += myProductRowHtml();
  document.getElementById('productTablePinnedBody').innerHTML = pinnedHtml;
  document.querySelectorAll('#productTableBody tr, #productTablePinnedBody tr').forEach(function(tr){
    tr.classList.toggle('bench-row', tr.dataset.bench==='1');
    tr.classList.toggle('product-status-excluded', tr.dataset.status==='excluded');
    tr.classList.toggle('product-status-candidate', tr.dataset.status==='candidate');
  });
  updateWorkflowSummary();
  applyEmptyMonthClass();
}
function rowHtml(r, isPinned){
  var st = workflow[r.asin]||'unreviewed';
  var isNew = (r.days||0)<=365;
  var cols = viewCols().filter(colVisible);
  var tds = cols.map(function(c){
    if(c.k==='ops') return '<td class="sticky-col"><div class="product-cell-content ops-cell">'
      + '<input type="checkbox" class="product-row-select" data-asin="'+esc(r.asin)+'" '+(selected[r.asin]?'checked':'')+'>'
      + '<select class="product-status-select" data-asin="'+esc(r.asin)+'">'
      + ['unreviewed:未判断','candidate:候选','benchmark:对标','excluded:排除'].map(function(o){ var p=o.split(':'); return '<option value="'+p[0]+'"'+(st===p[0]?' selected':'')+'>'+p[1]+'</option>'; }).join('')
      + '</select></div></td>';
    if(c.k==='asin') return '<td class="sticky-col2"><div class="product-cell-content single-line">'+link(r.asin)+(isNew?' <span class="new-product-days">新</span>':'')+'</div></td>';
    if(c.k==='image') return '<td class="sticky-col3"><div class="product-cell-content image-cell"><span class="prod-img-wrap"><img class="prod-img" loading="lazy" src="'+esc(r.image||'')+'" data-full="'+esc((r.image||'').replace(/\._AC_US600_/,'._AC_SL1000_'))+'" onerror="this.style.visibility=\'hidden\'"></span></div></td>';
    if(c.k==='title') return '<td><div class="product-cell-content" title="'+esc(r.title)+'">'+esc(r.title||'')+'</div></td>';
    if(c.k==='brand') return '<td><div class="product-cell-content single-line">'+esc(r.brand||'')+'</div></td>';
    if(c.k==='price') return '<td><div class="product-cell-content numeric">'+(r.price?'$'+r.price.toFixed(2):'—')+'</div></td>';
    if(c.k==='rating_reviews') return '<td><div class="product-cell-content compact"><span class="stars">'+(r.rating?'★'.repeat(Math.round(r.rating)):'')+'</span> '+(r.rating||'—')+'<br>'+fmtN(r.reviews)+' 条</div></td>';
    if(c.k==='units30') return '<td><div class="product-cell-content numeric">'+fmtN(r.units30)+'</div></td>';
    if(c.k==='trend') return '<td><div class="product-cell-content">'+sparklineSvg(r)+'<span class="tag '+trendClass(r)+'" style="font-size:9px;padding:0 4px">'+(trendClass(r)==='tag-pass'?'↑':trendClass(r)==='tag-risk'?'↓':'→')+'</span></div></td>';
    if(c.k==='size_weight') return '<td><div class="product-cell-content compact">'+(r.dims&&r.dims.length>=2?r.dims[0].toFixed(1)+'x'+r.dims[1].toFixed(1):'—')+' / '+(r.wt?r.wt.toFixed(2):'—')+'</div></td>';
    if(c.k==='size_segment') return '<td><div class="product-cell-content compact">'+esc(cellVal(r,c))+'</div></td>';
    if(c.k==='days') return '<td><div class="product-cell-content compact">'+esc(r.online||'')+'<br>'+fmtN(r.days)+' 天'+(isNew?' <span class="new-product-days">新品</span>':'')+'</div></td>';
    if(c.k.indexOf('coupling_')===0) return '<td><div class="product-cell-content compact">'+esc(cellVal(r,c))+'</div></td>';
    if(c.k==='rev6m') return '<td><div class="product-cell-content numeric" style="color:var(--accent);font-weight:700">'+fmtK$(r.rev6m)+'</div></td>';
    if(['y26u','y25u','y24u'].indexOf(c.k)>=0) return '<td><div class="product-cell-content numeric">'+fmtN(cellVal(r,c))+'</div></td>';
    if(['y26r','y25r','y24r'].indexOf(c.k)>=0) return '<td><div class="product-cell-content numeric">'+fmtK$(cellVal(r,c))+'</div></td>';
    if(c.k.indexOf('month_metrics_')===0){
      var i=months.indexOf(c.month);
      var u=r.units[i], rev=r.rev[i], pr=r.price_m[i];
      var empty = !(u>0||rev>0);
      return '<td'+(empty?' class="empty-month-col"':'')+'><div class="monthly-metrics">'
        + '<span class="monthly-metric-line"><span class="monthly-metric-label">U</span><span class="monthly-metric-units">'+(u?fmtN(u):'—')+'</span></span>'
        + '<span class="monthly-metric-line"><span class="monthly-metric-label">$</span><span class="monthly-metric-revenue">'+(rev?fmtK$(rev):'—')+'</span></span>'
        + '<span class="monthly-metric-line"><span class="monthly-metric-label">P</span><span class="monthly-metric-price">'+(pr?'$'+pr.toFixed(0):'—')+'</span></span>'
        + '</div></td>';
    }
    return '<td></td>';
  }).join('');
  return '<tr data-asin="'+esc(r.asin)+'" data-bench="'+(isPinned?'1':'0')+'" data-status="'+st+'">'+tds+'</tr>';
}
function myProductRowHtml(){
  var id = 'competitorRow';
  return '<tr id="'+id+'"><td class="sticky-col" style="color:var(--muted);font-size:10px">我方<br>产品</td>'
    + '<td class="sticky-col2"><input placeholder="ASIN" style="width:80px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px;font-size:11px"></td>'
    + '<td class="sticky-col3 comp-img-zone" contenteditable="false" data-placeholder="图片"></td>'
    + '<td><input placeholder="我方产品标题" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px;font-size:11px"></td>'
    + '<td><input placeholder="品牌" style="width:70px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px;font-size:11px"></td>'
    + '<td><input type="number" placeholder="售价$" style="width:56px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px;font-size:11px"></td>'
    + '<td colspan="'+(viewCols().filter(colVisible).length-6)+'" style="color:var(--muted);font-size:11px">填写我方产品信息后，将同步进入竞品对比与利润核算表。</td></tr>';
}
function bindHead(){
  document.querySelectorAll('#productHeadRow th.sortable').forEach(function(th){
    th.onclick = function(e){
      if(e.target.classList.contains('col-hide-btn')||e.target.classList.contains('col-filter-btn')) return;
      var k = th.dataset.key;
      if(sortKey===k){ sortDir = -sortDir; } else { sortKey = k; sortType = th.dataset.type; sortDir = (sortType==='num')?-1:1; }
      renderProductTable();
    };
  });
  document.querySelectorAll('#productHeadRow .col-hide-btn').forEach(function(btn){
    btn.onclick = function(e){ e.stopPropagation(); hiddenCols[btn.dataset.colHide]=true; renderProductTable(); };
  });
  document.querySelectorAll('#productHeadRow .col-filter-btn').forEach(function(btn){
    btn.onclick = function(e){ e.stopPropagation(); openFilterPopover(btn.dataset.colFilter, btn); };
  });
}
function updateWorkflowSummary(){
  var c = {candidate:0, benchmark:0, excluded:0, unreviewed:0};
  records.forEach(function(r){ c[workflow[r.asin]||'unreviewed']++; });
  document.getElementById('productWorkflowSummary').textContent = '候选 '+c.candidate+' · 对标 '+c.benchmark+' · 排除 '+c.excluded+' · 未判断 '+c.unreviewed;
}
function applyEmptyMonthClass(){
  var t = document.getElementById('productTable');
  t.classList.toggle('show-empty-months', showEmptyMonths);
  var btn = document.getElementById('toggleEmptyMonthsBtn');
  if(btn) btn.textContent = showEmptyMonths ? '隐藏空月份' : '显示全部月份';
}
window.toggleEmptyMonthColumns = function(){ showEmptyMonths = !showEmptyMonths; applyEmptyMonthClass(); };
window.jumpToMonthlyColumns = function(){
  var th = document.querySelector('#productHeadRow th[data-col-key="month_metrics_'+months[0]+'"]');
  if(th) th.scrollIntoView({inline:'start', block:'nearest'});
};
window.scrollProductTableToStart = function(){ document.getElementById('productTableWrap').scrollLeft = 0; };
window.setProductViewMode = function(m){
  productViewMode = m;
  document.querySelectorAll('[data-product-view]').forEach(function(b){ b.classList.toggle('active', b.dataset.productView===m); });
  renderProductTable();
};
window.setProductStatusFilter = function(v){ statusFilter=v; renderProductTable(); };
window.applyBulkProductStatus = function(){
  var v = document.getElementById('productBulkStatus').value;
  Object.keys(selected).forEach(function(asin){ if(selected[asin]) workflow[asin]=v; });
  selected = {}; saveWorkflow(); renderProductTable();
};
window.toggleMyProductEditor = function(){ var row=document.getElementById('competitorRow'); if(row) row.scrollIntoView({block:'center'}); };
window.copyAllAsins = function(){
  var txt = sortedRows().map(function(r){ return r.asin; }).join('\n');
  (navigator.clipboard?navigator.clipboard.writeText(txt):Promise.reject()).then(function(){
    document.getElementById('copyAllAsinsStatus').textContent='已复制 '+sortedRows().length+' 个 ASIN';
  }, function(){ document.getElementById('copyAllAsinsStatus').textContent='复制失败，请手动选择'; });
};
window.restoreProductColumns = function(){ hiddenCols={}; colFilters={}; renderProductTable(); };
window.clearAllProductFilters = function(){ colFilters={}; renderProductTable(); };
document.addEventListener('change', function(e){
  if(e.target.classList.contains('product-status-select')){
    workflow[e.target.dataset.asin]=e.target.value; saveWorkflow(); renderProductTable();
    renderBenchmark(); renderProfit();
  }
  if(e.target.classList.contains('product-row-select')){ selected[e.target.dataset.asin]=e.target.checked; }
});
document.addEventListener('click', function(e){
  var img = e.target.closest('.prod-img');
  if(img){
    var pv=document.getElementById('productImagePreview'), pvImg=document.getElementById('productImagePreviewImg');
    pvImg.src=img.dataset.full||img.src; pvImg.hidden=false; pv.classList.add('open');
  }
  if(e.target.id==='productImagePreviewClose'||e.target.id==='productImagePreview') document.getElementById('productImagePreview').classList.remove('open');
});
document.addEventListener('mousemove', function(e){
  var img = e.target.closest('.prod-img');
  var hp=document.getElementById('productImageHoverPreview'), hImg=document.getElementById('productImageHoverPreviewImg');
  if(img){ hImg.src=img.dataset.full||img.src; hImg.hidden=false; hp.classList.add('open');
    hp.style.left=Math.min(window.innerWidth-360, e.clientX+16)+'px'; hp.style.top=Math.max(8, e.clientY-160)+'px'; }
  else hp.classList.remove('open');
});
/* filter popover */
var filterCtx = {col:null, mode:'set', values:[], min:null, max:null};
function openFilterPopover(colKey, anchor){
  filterCtx.col = colKey; filterCtx.mode='set'; filterCtx.values=[]; filterCtx.min=null; filterCtx.max=null;
  var c = null; viewCols().forEach(function(cc){ if(cc.k===colKey) c=cc; });
  document.getElementById('productFilterTitle').textContent = '筛选：'+(c?c.l:colKey);
  var vals = {};
  records.forEach(function(r){ var v=String(cellVal(r,c)); vals[v]=(vals[v]||0)+1; });
  filterCtx.allVals = Object.keys(vals).sort();
  renderFilterValues('');
  var isNum = c && c.t==='num' && colKey!=='asin';
  document.getElementById('productFilterNumberRange').style.display = isNum?'block':'none';
  var pop = document.getElementById('productFilterPopover');
  var rect = anchor.getBoundingClientRect();
  pop.style.left = Math.min(window.innerWidth-300, rect.left)+'px';
  pop.style.top = (rect.bottom+6)+'px';
  pop.classList.add('open');
}
function renderFilterValues(q){
  q=(q||'').toLowerCase();
  document.getElementById('productFilterValues').innerHTML = filterCtx.allVals
    .filter(function(v){ return v.toLowerCase().indexOf(q)>=0; })
    .map(function(v){ return '<label class="product-filter-option"><input type="checkbox" value="'+esc(v)+'" '+(filterCtx.values.indexOf(v)>=0?'checked':'')+'><span>'+esc(v)+'</span></label>'; }).join('');
}
document.getElementById('productFilterSearch').addEventListener('input', function(){ renderFilterValues(this.value); });
document.getElementById('productFilterValues').addEventListener('change', function(e){
  var v=e.target.value; var i=filterCtx.values.indexOf(v);
  if(e.target.checked && i<0) filterCtx.values.push(v);
  if(!e.target.checked && i>=0) filterCtx.values.splice(i,1);
});
document.getElementById('productFilterClose').onclick = document.getElementById('productFilterCancel').onclick = function(){
  document.getElementById('productFilterPopover').classList.remove('open');
};
document.getElementById('productFilterApply').onclick = function(){
  var isNum = document.getElementById('productFilterNumberRange').style.display!=='none';
  if(isNum){ colFilters[filterCtx.col]={mode:'num', min:parseFloat(document.getElementById('productFilterMin').value)||-Infinity, max:parseFloat(document.getElementById('productFilterMax').value)||Infinity}; }
  else if(filterCtx.values.length){ colFilters[filterCtx.col]={mode:'set', values:filterCtx.values.slice()}; }
  else delete colFilters[filterCtx.col];
  document.getElementById('productFilterPopover').classList.remove('open');
  renderProductTable();
};
window.selectAllFilterValues=function(){ filterCtx.values=filterCtx.allVals.slice(); renderFilterValues(document.getElementById('productFilterSearch').value); };
window.clearFilterSelection=function(){ filterCtx.values=[]; renderFilterValues(document.getElementById('productFilterSearch').value); };
window.invertFilterSelection=function(){ filterCtx.values=filterCtx.allVals.filter(function(v){ return filterCtx.values.indexOf(v)<0; }); renderFilterValues(document.getElementById('productFilterSearch').value); };
window.clearCurrentProductFilter=function(){ if(filterCtx.col) delete colFilters[filterCtx.col]; renderProductTable(); };

/* ============ 3. benchmark compare ============ */
function renderBenchmark(){
  var host = document.getElementById('benchmarkHost');
  var st = starredAsins().slice(0,5).map(function(a){ return byAsin[a]; });
  if(!st.length) st = records.slice(0,3);
  var specRows = COUPLING_KEYS;
  var metricRows = [
    {l:'价格', f:function(r){ return fmt$(r.price); }},
    {l:'评分/评论', f:function(r){ return (r.rating||'—')+' ★ / '+fmtN(r.reviews); }},
    {l:'30d销量', f:function(r){ return fmtN(r.units30); }},
    {l:'近6月GMV', f:function(r){ return fmtK$(r.rev6m); }},
    {l:'上架天数', f:function(r){ return fmtN(r.days)+(r.days<=365?' <span class="new-product-days">新品</span>':''); }},
    {l:'变体数', f:function(r){ return fmtN(r.varCount); }}
  ];
  var th = '<tr><th>对比维度</th><th><div class="benchmark-my-head"><span class="benchmark-product-head-label">我方产品（可编辑）</span><span class="benchmark-product-head-title">双面带灯放大化妆镜（规划中）</span></div></th>'
    + st.map(function(r){ return '<th><div class="benchmark-product-head"><img src="'+esc(r.image||'')+'"><div class="benchmark-product-head-copy"><span class="benchmark-product-head-label">竞品</span><span class="benchmark-product-head-brand">'+esc(r.brand)+'</span><a href="https://www.amazon.com/dp/'+esc(r.asin)+'" target="_blank">'+esc(r.asin)+'</a><span class="benchmark-product-head-title">'+esc(r.title)+'</span></div></div></th>'; }).join('')+'</tr>';
  var body = metricRows.map(function(m){
    return '<tr><td><span class="benchmark-field-label">'+m.l+'</span></td>'
      + '<td><div class="benchmark-my-editable" contenteditable="true" data-field="'+esc(m.l)+'"></div></td>'
      + st.map(function(r){ return '<td class="benchmark-value-strong">'+m.f(r)+'</td>'; }).join('')+'</tr>';
  }).join('');
  body += '<tr class="benchmark-section-row"><th colspan="'+(2+st.length)+'">规格履约对比 <small>— 与竞品不同处将高亮</small></th></tr>';
  body += specRows.map(function(sp){
    var vals = st.map(function(r){ return r.coupling[sp]||'—'; });
    var uniq = {}; vals.forEach(function(v){ uniq[v]=1; });
    var multi = Object.keys(uniq).length>1;
    return '<tr><td><span class="benchmark-field-label">'+esc(sp)+'</span></td>'
      + '<td><div class="benchmark-my-editable" contenteditable="true" data-field="'+esc(sp)+'"></div></td>'
      + vals.map(function(v){ return '<td'+(multi&&v!=='—'?' class="benchmark-cell-diff"':' class="benchmark-cell-same"')+'>'+esc(v)+'</td>'; }).join('')+'</tr>';
  }).join('');
  host.innerHTML = '<section class="benchmark-compare-module" id="benchmarkComparisonModule"><div class="benchmark-compare-head"><div><h3>竞品分析</h3><p class="benchmark-compare-note">目标竞品来自产品数据总表的星标产品（默认近6月GMV Top5）；表格只保留经营指标和规格履约的事实对比，领先项与风险项直接标记。</p><p class="benchmark-compare-note">我方产品列支持直接填写并同步。</p></div><span class="benchmark-chip">不同点高亮</span></div>'
    + '<div class="benchmark-ai-summary"><div class="benchmark-ai-head"><strong>竞争决策</strong><span class="benchmark-ai-source">市场数据与模型分析</span></div><div class="benchmark-ai-grid">'
    + '<div class="benchmark-ai-item"><h4>主流配置判断</h4><ul>'
    + '<li>P0 提升供电与灯光可靠性：负面评论中「功能失效/失灵」占 '+R.pain_rows[0].share+'%，直接影响退货率和评分。</li>'
    + '<li>P0 优化底座稳定性：「底座不稳/易倒」是台式镜最高频结构差评。</li>'
    + '<li>P1 灯光体验升级：3色温+无级调光已是高GMV链接标配，缺配将掉队。</li>'
    + '<li>P1 放大镜面防畸变：10X放大需高清镀膜并标注对焦距离。</li></ul></div>'
    + '<div class="benchmark-ai-item"><h4>差异化机会</h4><ul>'
    + '<li>双面镜（1X+10X）+ 3色温触控调光：主流组合尚未饱和，配合usb-c快充。</li>'
    + '<li>镜面尺寸上探：主流集中在中小尺寸，大镜面（40cm+）GMV占比抬升。</li>'
    + '<li>可拆卸/充电宝二用：差旅与宿舍场景溢价明显（ premium premium 指数>1.15）。</li>'
    + '<li>包装防刮擦+预装结构：降低「外观瑕疵」「组装困难」双痛点。</li></ul></div>'
    + '<div class="benchmark-ai-item"><h4>风险与验证</h4><ul>'
    + '<li>最不建议单独押注的卖点：'+esc(R.att_rows.slice(0,3).map(function(a){return a.field+'='+a.val;}).join(' / '))+'</li>'
    + '<li>评论高频雷点集中在：'+esc(R.pain_rows.slice(0,3).map(function(p){return p.name;}).join(' / '))+'。</li>'
    + '<li>需避开高拥挤属性组合：'+esc(R.combo_rows.slice(0,2).map(function(c){return c.combo.join('+');}).join('；'))+'。</li>'
    + '<li>供给拥挤需评估差异化：低价纯LED款（$10-20）同质化最重，毛利被压缩。</li></ul></div>'
    + '</div></div>'
    + '<div class="table-wrap benchmark-compare-wrap"><table class="benchmark-compare-table" id="benchmarkComparisonTable"><colgroup><col class="benchmark-field-col"><col class="benchmark-my-col">' + st.map(function(){return '<col class="benchmark-competitor-col">';}).join('') + '</colgroup><thead>'+th+'</thead><tbody>'+body+'</tbody></table></div></section>';
  host.querySelectorAll('.benchmark-my-editable').forEach(function(el){
    var key='benchMy:'+el.dataset.field;
    var saved=storage.getItem(key); if(saved) el.textContent=saved;
    el.addEventListener('input', function(){ try{ storage.setItem(key, el.textContent); }catch(e){} });
  });
}

/* ============ 4. V1 definition ============ */
function renderV1(){
  var must = R.att_rows.filter(function(a){ return a.tag==='基础标配'; }).slice(0,4);
  var should = R.att_rows.filter(function(a){ return a.tag==='高溢价机会'||a.tag==='细分机会项'; }).slice(0,4);
  var avoid = R.att_rows.filter(function(a){ return a.tag==='普通属性'; }).slice(0,3);
  function col(cls, title, items){
    return '<div class="v1-definition-column '+cls+'"><h3>'+title+'</h3>' + items.map(function(it){
      return '<div class="v1-definition-item"><strong>'+esc(it.field)+'：'+esc(it.val)+'</strong><dl class="v1-definition-meta">'
        + '<dt>目标值</dt><dd>'+esc(it.val)+'</dd>'
        + '<dt>证据</dt><dd>渗透率 '+it.pen+'%；GMV占比 '+it.gmv_share+'%'+(it.premium?'；溢价 '+it.premium+'x':'')+'</dd>'
        + '<dt>复杂度</dt><dd>低</dd>'
        + '<dt>验收</dt><dd>3台样机同场景复测，规格、Listing声明和测试记录一致。</dd></dl></div>';
    }).join('')+'</div>';
  }
  var avoidItems = avoid.length ? avoid : R.att_rows.slice(-3);
  document.getElementById('v1Grid').innerHTML = col('must','V1 必须有', must) + col('should','建议有 / 可溢价', should) + col('avoid','V1 暂不做', avoidItems);
  var opp = R.combo_rows.slice(0,3).map(function(cr, i){
    return '<div class="opportunity-hypothesis"><div class="opportunity-rank">#'+(i+1)+'</div>'
      + '<div><strong>'+esc(cr.combo.join(' + '))+'</strong><p>'+cr.n+' 个ASIN · 近6月GMV '+fmtK$(cr.gmv)+' · 增速 '+(cr.growth==null?'—':cr.growth+'%')+' · 拥挤度 '+cr.crowding+'</p></div>'
      + '<div><p>'+(cr.tag==='高GMV低拥挤'?'需求足够大但供给没有完全挤满，适合优先验证。':'组合具备参考意义，但优先级不应高于更明确的机会组合。')+'</p></div>'
      + '<div><span class="tag '+(cr.tag==='高GMV低拥挤'?'tag-pass':'tag-info')+'">'+esc(cr.tag)+'</span></div></div>';
  }).join('');
  document.getElementById('oppHost').innerHTML = opp;
}

/* ============ 5. profit table ============ */
var TARGET_MARGIN_RATE=0.22;
var STD_WT=[[0.25,3.68],[0.5,3.98],[0.75,4.28],[1.0,4.75],[1.5,5.37],[2.0,5.68],[2.5,5.98],[3.0,6.28]];
function estFbaStd(wlb){
  if(wlb<=3.0){ for(var i=0;i<STD_WT.length;i++) if(wlb<=STD_WT[i][0]) return STD_WT[i][1]; }
  return 6.58+Math.ceil((wlb-3.0)*2)*0.38;
}
function getTier(dimsCm, wkg){
  var ins = dimsCm.map(function(v){ return v/2.54; });
  var s=Math.min.apply(null,ins), m=ins.slice().sort(function(a,b){return a-b;})[1]||s, l=Math.max.apply(null,ins);
  var lg=l+2*(m+s);
  if(l<=18&&m<=14&&s<=8&&lg<=130&&wkg*2.20462<=20) return '标准件';
  if(l<=59&&m<=33&&s<=33&&lg<=130&&wkg*2.20462<=50) return '大号大件';
  return '超大件';
}
function profNum(id,d){ var v=parseFloat(document.getElementById(id).value); return isNaN(v)?d:v; }
function renderProfit(){
  var st = starredAsins().slice(0,5).map(function(a){ return byAsin[a]; });
  document.getElementById('profitBenchmarkEmpty').style.display = st.length?'none':'block';
  var rows = st.map(function(r){ return profitRowHtml(r, false); }).join('');
  rows += profitRowHtml(null, true);
  document.getElementById('profitTableBody').innerHTML = rows;
  recalcProfit();
}
function profitRowHtml(r, isBlank){
  var dims = r? (r.dims||[]) : [];
  var dimStr = dims.length>=3 ? dims.slice(0,3).map(function(v){return v.toFixed(2);}).join(' x ') : '';
  var dimIn = dims.length>=3 ? dims.slice(0,3).map(function(v){return (v/2.54).toFixed(2);}).join(' x ') : '';
  var wkg = r? (r.wt||0) : 0;
  var img = r? '<img src="'+esc(r.image||'')+'" style="width:40px;height:40px;object-fit:contain;border-radius:3px;background:#fff" onerror="this.style.display=\'none\'">' : '';
  var title = r? (r.title||'').slice(0,40) : '我方产品（目标SKU）';
  return '<tr data-asin="'+(r?esc(r.asin):'myproduct')+'" data-dimvals=\'['+dims.slice(0,3).map(function(v){return '"'+v.toFixed(2)+'"';}).join(', ')+']\' data-wtlb="'+(wkg*2.20462).toFixed(2)+'" data-blank="'+(isBlank?'1':'0')+'">'
    + '<td>'+img+'</td>'
    + '<td style="font-size:11px"><div style="font-weight:600">'+(r?esc(r.asin):'目标SKU')+'</div><div style="font-size:10px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:130px" title="'+esc(r?r.title:'')+'">'+esc(title)+'</div></td>'
    + '<td style="font-size:10px"><div>'+dimIn+' in</div><div style="color:var(--muted)">'+dimStr+' cm</div></td>'
    + '<td style="font-size:10px"><div>'+(wkg?wkg.toFixed(2)+' kg':'')+'</div><div style="color:var(--muted)">'+(wkg?(wkg*2.20462).toFixed(2)+' lb':'')+'</div></td>'
    + '<td><input type="number" step="1" min="0" value="'+(r?Math.max(1,Math.round((r.units30||0)/1)):'300')+'" onchange="recalcProfit()" oninput="recalcProfit()" style="background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px;width:38px;font-size:11px" title="月销，可修改"></td>'
    + '<td class="packageTierCell" style="font-size:11px;color:var(--muted)">—</td>'
    + '<td><input type="number" step="0.01" value="'+(r?r.price.toFixed(2):'')+'" onchange="recalcProfit()" oninput="recalcProfit()" style="background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px;width:100%;font-size:11px"></td>'
    + '<td><input type="number" step="0.01" value="'+(r?(Math.round(r.price*7.15*0.28*1.13)).toFixed(2):'')+'" onchange="recalcProfit()" oninput="recalcProfit()" style="background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px;width:100%;font-size:11px" title="含税成本¥，默认按售价28%预填，请修正"></td>'
    + '<td class="marginCell" style="font-size:14px;font-weight:700">—</td>'
    + '<td class="exTaxRmbCell" style="font-size:11px">—</td><td class="exTaxUsdCell" style="font-size:11px">—</td>'
    + '<td class="freightCell" style="font-size:11px">—</td><td class="placeCell" style="font-size:11px">—</td>'
    + '<td class="commCell" style="font-size:11px">—</td><td><input class="fbaInput" type="number" step="0.01" onchange="markManualFba(this)" oninput="markManualFba(this)" style="background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:3px;padding:2px 4px;width:50px;font-size:11px" title="FBA费，自动估算可手改"></td>'
    + '<td class="storeCell" style="font-size:11px">—</td>'
    + '<td class="grossRmbCell" style="font-size:12px;font-weight:700">—</td><td class="grossUsdCell" style="font-size:11px">—</td>'
    + '<td class="adCell" style="font-size:11px;color:var(--orange)">—</td><td class="promoCell" style="font-size:11px;color:var(--orange)">—</td><td class="retCell" style="font-size:11px;color:var(--red)">—</td>'
    + '<td class="totalCell" style="font-size:11px">—</td><td class="procPctCell" style="font-size:11px">—</td><td class="shipPctCell" style="font-size:11px">—</td>'
    + '</tr>';
}
window.markManualFba = function(el){ el.dataset.autoFba = el.value?'0':'1'; recalcProfit(); };
window.recalcProfit = function(){
  var fx=profNum('fxRate',7.15), shipRmb=profNum('shippingRmb',8), storage=profNum('storageRate',2)/100,
      ad=profNum('adRate',15)/100, promo=profNum('promoRate',0)/100, ret=profNum('returnRate',8)/100,
      comm=profNum('commissionRate',15)/100;
  var tips=[];
  document.querySelectorAll('#profitTableBody tr').forEach(function(tr){
    var cells=tr.querySelectorAll('td');
    if(cells.length<24) return;
    var inputs=tr.querySelectorAll('input');
    var price=parseFloat(inputs[1].value)||0;
    var costRmb=parseFloat(inputs[2].value)||0;
    var monthUnits=parseFloat(inputs[0].value)||0;
    var dimVals=[]; try{ dimVals=JSON.parse(tr.dataset.dimvals||'[]'); }catch(e){}
    var wlb=parseFloat(tr.dataset.wtlb)||0;
    var dims=dimVals.map(Number);
    var tier=(dims.length===3&&wlb>0)?getTier(dims,wlb/2.20462):'标准件';
    cells[5].textContent=tier;
    var fbaInp=cells[14].querySelector('input');
    if(fbaInp&&wlb>0&&fbaInp.dataset.autoFba!=='0'){ var ef=estFbaStd(wlb); fbaInp.value=ef.toFixed(2); fbaInp.dataset.autoFba='1'; fbaInp.dataset.lastAutoFba=fbaInp.value; }
    var fba=parseFloat(fbaInp?fbaInp.value:0)||0;
    var exTaxRmb=costRmb/1.13, exTaxUsd=fx?exTaxRmb/fx:0;
    var freightUsd=(wlb/2.20462)*shipRmb/fx;
    var place=0.12;
    var commUsd=price*comm, storeUsd=price*storage;
    var grossUsd=price-exTaxUsd-freightUsd-place-commUsd-fba-storeUsd;
    var margin=price?grossUsd/price:0;
    var adUsd=price*ad, promoUsd=price*promo, retUsd=price*ret;
    var totalCost=exTaxUsd+freightUsd+place+commUsd+fba+storeUsd+adUsd+promoUsd+retUsd;
    cells[8].textContent=(margin*100).toFixed(1)+'%';
    cells[8].className='marginCell '+(margin>=0.22?'profit-positive':(margin>=0?'':'profit-negative'));
    cells[9].textContent='¥'+exTaxRmb.toFixed(2); cells[10].textContent='$'+exTaxUsd.toFixed(2);
    cells[11].textContent='$'+freightUsd.toFixed(2); cells[12].textContent='$'+place.toFixed(2);
    cells[13].textContent='$'+commUsd.toFixed(2);
    cells[16].textContent='¥'+(grossUsd*fx).toFixed(2);
    cells[16].className='grossRmbCell '+(grossUsd>0?'profit-positive':'profit-negative');
    cells[17].textContent='$'+grossUsd.toFixed(2);
    cells[18].textContent='$'+adUsd.toFixed(2); cells[19].textContent='$'+promoUsd.toFixed(2); cells[20].textContent='$'+retUsd.toFixed(2);
    cells[21].textContent='$'+totalCost.toFixed(2);
    cells[22].textContent=price?(exTaxUsd/price*100).toFixed(0)+'%':'—';
    cells[23].textContent=price?((freightUsd+place+fba+storeUsd)/price*100).toFixed(0)+'%':'—';
  });
  var firstRow=document.querySelector('#profitTableBody tr');
  if(firstRow){
    var cells=firstRow.querySelectorAll('td');
    var price=parseFloat(firstRow.querySelectorAll('input')[1].value)||0;
    if(price>0){
      var cap=price*(1-TARGET_MARGIN_RATE-profNum('adRate',15)/100-profNum('promoRate',0)/100-profNum('returnRate',8)/100-profNum('storageRate',2)/100)-0.12-price*profNum('commissionRate',15)/100-(parseFloat((cells[14].querySelector('input'))?cells[14].querySelector('input').value:0)||0);
      cap=cap-profNum('shippingRmb',8)*0.66/profNum('fxRate',7.15);
      document.getElementById('targetProcurementLimit').textContent='目标SKU售价 $'+price.toFixed(2)+' 时，满足目标毛利 '+(TARGET_MARGIN_RATE*100).toFixed(1)+'% 的采购成本上限：含税 ¥'+(cap*profNum('fxRate',7.15)*1.13).toFixed(2)+'（不含税 ¥'+(cap*profNum('fxRate',7.15)).toFixed(2)+'）。';
    }
  }
  var note={conservative:'保守：广告22%、退货12%、促销5%、仓储3%',base:'基准：广告15%、退货8%、仓储2%',optimistic:'乐观：广告10%、退货5%、仓储1.5%'}[window._activeScenario||'base'];
  document.getElementById('fbaOptimTips').innerHTML = '';
};
var PROFIT_SCENARIOS={
  conservative:{storageRate:3,adRate:22,promoRate:5,returnRate:12,note:'保守：广告22%、退货12%、促销5%、仓储3%'},
  base:{storageRate:2,adRate:15,promoRate:0,returnRate:8,note:'基准：广告15%、退货8%、仓储2%'},
  optimistic:{storageRate:1.5,adRate:10,promoRate:0,returnRate:5,note:'乐观：广告10%、退货5%、仓储1.5%'}
};
window.applyProfitScenario=function(name){
  var s=PROFIT_SCENARIOS[name]; if(!s) return;
  window._activeScenario=name;
  ['storageRate','adRate','promoRate','returnRate'].forEach(function(id){ document.getElementById(id).value=s[id]; });
  document.getElementById('profitScenarioNote').textContent=s.note;
  document.querySelectorAll('[data-profit-scenario]').forEach(function(b){ b.classList.toggle('active', b.dataset.profitScenario===name); });
  recalcProfit();
};
window.setTargetMarginRate=function(v){ var p=parseFloat(v); if(!isNaN(p)) TARGET_MARGIN_RATE=Math.max(0,Math.min(p,80))/100; recalcProfit(); };

/* ============ 6. PPC ============ */
function renderPpc(){
  var ppc = R.ppc;
  var p0 = ppc.filter(function(k){ return k.pri==='P0'; });
  var p1 = ppc.filter(function(k){ return k.pri==='P1'; });
  var p2 = ppc.filter(function(k){ return k.pri==='P2'; });
  function card(cls, count, layer, hint, kws){
    return '<div class="keyword-ppc-summary-card '+cls+'"><div class="keyword-ppc-summary-top"><div class="keyword-ppc-summary-layer">'+layer+'</div><div class="keyword-ppc-summary-count">'+count+'</div></div>'
      + '<div class="keyword-ppc-summary-hint">'+hint+'</div><div class="keyword-ppc-summary-keywords">'+kws.map(function(k){ return '<span class="keyword-ppc-summary-keyword">'+esc(k.kw)+'</span>'; }).join('')+'</div></div>';
  }
  document.getElementById('keywordPpcEconomicsSummary').innerHTML =
    card('priority', p0.length, 'P0 核心大词（月搜索≥5万）', '主推词，Exact优先，卡位自然位', p0)
    + card('', p1.length, 'P1 二级词（1万-5万）', 'Phrase扩量，观察转化后提预算', p1)
    + card('', p2.length, 'P2 精准长尾（<1万）', '低价长尾收割，Broad跑词', p2);
  document.getElementById('keywordPpcBody').innerHTML = ppc.map(function(k){
    var cvr = (k.cvr&&k.cvr>0)?k.cvr:'—';
    var acos = Math.round(100/((k.cvr&&k.cvr>0?k.cvr:5)/100));
    return '<tr class="'+(k.pri==='P0'?'is-priority keyword-ppc-row':'keyword-ppc-row')+'">'
      + '<td><span class="keyword-main">'+esc(k.kw)+'</span></td>'
      + '<td><span class="keyword-ppc-layer '+(k.pri==='P0'?'priority':'')+'">'+k.tier+'</span></td>'
      + '<td>'+esc(k.cn||'')+'</td>'
      + '<td style="font-size:11px;color:var(--muted)">'+(k.pri==='P0'?'Exact主攻，卡位首页；SB打关联流量':'Phrase/Broad扩量，转化达标后提预算')+'</td>'
      + '<td>'+fmtN(k.sv)+'</td><td>'+(k.sales90?fmtN(k.sales90):'—')+'</td><td>'+fmtN(k.products)+'</td>'
      + '<td>'+(k.scr||'—')+'</td><td>'+cvr+'</td><td>'+(k.cpc?'$'+(k.cpc/100).toFixed(2):'—')+'</td>'
      + '<td>$'+(k.sug_bid||0).toFixed(2)+'</td><td>$'+(k.affordable||0).toFixed(2)+'</td>'
      + '<td><span class="tag '+(k.pri==='P0'?'tag-pass':(k.pri==='P1'?'tag-pending':'tag-info'))+'">'+k.pri+'</span></td>'
      + '<td>'+acos+'%</td><td>'+(k.share||'—')+'</td><td>'+k.wc+'</td></tr>';
  }).join('');
}

/* ============ 7. reviews ============ */
function renderReviews(){
  var pains = R.pain_rows;
  var total = pains.reduce(function(s,p){ return s+p.neg; },0);
  var gate = document.getElementById('reviewGateHost');
  gate.innerHTML = '<details class="quality-warning" open><summary>评论质量门禁<span class="quality-warning-count">— 样本：Top5 ASIN × Amazon Customers Say，负面提及合计 '+fmtN(total)+' 条</span></summary><ul>'
    + '<li>样本说明：基于亚马逊官方「Customers Say」聚合（更新于 2026-08），未逐条抓取原文；立项前建议对 Top3 竞品各补采 30 条 1-3 星原文复核。</li>'
    + '<li>差评 TOP1「'+esc(pains[0].name)+'」占 '+pains[0].share+'%，为量产前必须验证项。</li>'
    + '<li>好评主线集中在 '+esc(R.pos_rows.slice(0,3).map(function(p){return p.name;}).join(' / '))+'，Listing 主图与首行五点应优先承接。</li>'
    + '</ul></details>';
  var first = R.csay[0];
  document.getElementById('reviewSummaryHost').innerHTML = '<div class="ai-analysis-text">'
    + (R.csay.map(function(c){ return '【'+c.asin+' · '+c.brand+'】'+esc(c.summary||''); }).join('\n\n'))
    + '</div>';
  var pc = pains.map(function(p){ return {name:p.name, v:p.share, n:p.neg}; });
  window._painChart = new Chart(document.getElementById('painChart').getContext('2d'), {
    type:'bar',
    data:{ labels:pc.map(function(p){return p.name;}), datasets:[{label:'占有效差评比例', data:pc.map(function(p){return p.v;}), backgroundColor:'rgba(229,72,77,0.65)', borderRadius:4}]},
    options:{ indexAxis:'y', responsive:true, plugins:{legend:{display:false}, tooltip:{callbacks:{label:function(ctx){ var p=pc[ctx.dataIndex]; return ' '+p.v+'% ('+p.n+' 条)'; }}}},
      scales:{ x:{beginAtZero:true, max:Math.max(40, Math.ceil(pc[0].v/10)*10+10), ticks:{color:'#64748b', callback:function(v){return v+'%';}}, grid:{color:'rgba(88,116,150,0.38)'}, title:{display:true, text:'占有效差评比例', color:'#64748b'}},
               y:{ticks:{color:'#1f2d3d'}, grid:{display:false}}} }
  });
  document.getElementById('posKeepHost').innerHTML = '<table><thead><tr><th>好评维度</th><th>正面提及占比</th><th>用户反馈</th><th>产品/营销启示</th></tr></thead><tbody>'
    + R.pos_rows.map(function(p){ return '<tr><td>'+esc(p.name)+'</td><td>'+p.share+'% ('+p.pos+')</td><td style="font-size:12px;max-width:250px">'+esc(p.quote)+'</td><td style="font-size:12px;color:var(--muted);max-width:250px">在详情页与首图优先承接该卖点，主图直接可视化</td></tr>'; }).join('')
    + '</tbody></table>';
  /* appendix tables */
  document.getElementById('painDetailHost').innerHTML = '<table><thead><tr><th>问题</th><th>占比</th><th>优化建议</th><th>代表性反馈</th></tr></thead><tbody>'
    + pains.map(function(p, i){ return '<tr><td>'+esc(p.name)+'</td><td>'+p.share+'% ('+p.neg+')</td><td style="font-size:12px;color:var(--muted);max-width:250px">'+esc(({'功能失效/失灵':'改进灯珠与电路可靠性，出厂老化测试；触控模块延保','底座不稳/易倒':'加重底座或增加防滑垫，提升支架配重与角度锁紧','灯光问题(不亮/太暗/偏色)':'升级LED灯珠与显色指数CRI>90，增加亮度档位','品质投诉':'提升边框与镜面装配公差，出厂全检','尺寸不符预期':'主图标注真实尺寸参照物，Listing明确镜面净尺寸','充电/续航问题':'USB-C接口+内置电池容量升级，标注续航时长','放大镜畸变/倍数不符':'10X镜面改用高清镀膜，标注适用对焦距离','安装/组装困难':'简化安装步骤，附图示说明书与预装配件'}[p.name]||'基于评论原文复核后再立项'))+'</td><td style="font-size:11px;max-width:250px">'+esc((p.quotes&&p.quotes[0])||'')+'</td></tr>'; }).join('')
    + '</tbody></table>';
  var priorities = pains.slice(0,6).map(function(p, i){ return {p:p, pri: i===0?'P0':'P1'}; });
  document.getElementById('ticketHost').innerHTML = '<table><thead><tr><th>优先级</th><th>痛点</th><th>直接证据</th><th>建议动作</th><th>风险边界</th></tr></thead><tbody>'
    + priorities.map(function(x){ return '<tr><td>'+x.pri+'</td><td>'+esc(x.p.name)+'</td><td style="font-size:11px;color:var(--accent2);max-width:300px">'+esc((x.p.quotes&&x.p.quotes[0])||'')+'</td><td style="font-size:12px;max-width:260px">'+esc(({'功能失效/失灵':'改进灯珠与电路可靠性，出厂老化测试；触控模块延保','底座不稳/易倒':'加重底座或增加防滑垫，提升支架配重与角度锁紧','灯光问题(不亮/太暗/偏色)':'升级LED灯珠与显色指数CRI>90，增加亮度档位'}[x.p.name]||'基于评论原文复核后再立项'))+'</td><td style="font-size:11px;color:var(--muted);max-width:260px">基于当前评论样本提出改进假设，仍需结合退货、客服和样品测试确认。</td></tr>'; }).join('')
    + '</tbody></table>';
  document.getElementById('asinReviewHost').innerHTML = '<table><thead><tr><th>ASIN</th><th>品牌</th><th>核心问题</th><th>优化建议</th></tr></thead><tbody>'
    + R.csay.map(function(c){
      var topNeg = (c.details||[]).slice().sort(function(a,b){ return (b.neg||0)-(a.neg||0); })[0];
      return '<tr><td>'+link(c.asin)+'</td><td>'+esc(c.brand)+'</td><td style="font-size:12px;max-width:200px">'+esc(topNeg? topNeg.kw+'：'+topNeg.content : '—')+'</td><td style="font-size:12px;color:var(--muted);max-width:250px">针对该负向关键词做样品复测并写入V1验收标准</td></tr>';
    }).join('') + '</tbody></table>';
  var excerpts = [];
  R.csay.forEach(function(c){ (c.details||[]).forEach(function(d){ if((d.neg||0)>=8 && d.content) excerpts.push({asin:c.asin, kw:d.kw, txt:d.content}); }); });
  excerpts = excerpts.slice(0,18);
  document.getElementById('excerptCount').textContent = '共 '+excerpts.length+' 条，默认折叠';
  document.getElementById('excerptHost').innerHTML = excerpts.map(function(x){
    return '<details class="review-excerpt"><summary><div style="display:flex;justify-content:space-between;align-items:center">'+link(x.asin)+'<span class="stars" style="flex-shrink:0">★</span></div><div style="font-size:12px;font-weight:600">'+esc(x.kw)+'</div></summary><div class="re-body"><div class="re-original">'+esc(x.txt)+'</div><div class="re-translation">'+esc(x.kw)+'相关负面反馈（Amazon Customers Say 聚合）</div></div></details>';
  }).join('');
}

/* ============ 8. KPI grid ============ */
function renderKpi(){
  var k = R.kpi;
  var cards = [
    [fmtN(k.products), '产品数'], [fmtN(k.brands), '品牌数'], [k.avg_rating, '平均评分'],
    [fmtN(k.median_reviews), '中位评论'], ['$'+k.avg_price.toFixed(1), '平均价格'],
    [fmtK$(k.total_gmv), '近6月GMV'], [fmtN(k.total_units), '近6月销量'], [Math.round(k.top3_share)+'%', '头部集中度']
  ];
  document.getElementById('kpiGrid').innerHTML = cards.map(function(c){ return '<div class="kpi-card"><div class="kpi-value">'+c[0]+'</div><div class="kpi-label">'+c[1]+'</div></div>'; }).join('');
}

/* ============ 9. trend + forecast ============ */
function sampleMonthly(){
  var u = months.map(function(m,i){ return records.reduce(function(s,r){ return s+(r.units[i]||0); },0); });
  var rv = months.map(function(m,i){ return records.reduce(function(s,r){ return s+(r.rev[i]||0); },0); });
  return {u:u, r:rv};
}
function renderTrend(){
  var sm = sampleMonthly();
  var labels = months.concat(R.fc.labels);
  var u = sm.u.concat(R.fc.u.map(function(){ return null; }));
  var rv = sm.r.concat(R.fc.r.map(function(){ return null; }));
  var nHist = months.length;
  var fcU = months.map(function(){ return null; }); var fcR = months.map(function(){ return null; });
  var fcUu = months.map(function(){ return null; }); var fcUl = months.map(function(){ return null; });
  var fcRu = months.map(function(){ return null; }); var fcRl = months.map(function(){ return null; });
  fcU[nHist-1]=sm.u[nHist-1]; fcR[nHist-1]=sm.r[nHist-1];
  fcUu[nHist-1]=sm.u[nHist-1]; fcUl[nHist-1]=sm.u[nHist-1];
  fcRu[nHist-1]=sm.r[nHist-1]; fcRl[nHist-1]=sm.r[nHist-1];
  R.fc.labels.forEach(function(m,i){
    var idx = labels.indexOf(m);
    if(idx<0) return;
    fcU[idx]=R.fc.u[i]; fcR[idx]=R.fc.r[i];
    fcUu[idx]=R.fc.u_up[i]; fcUl[idx]=R.fc.u_lo[i];
    fcRu[idx]=R.fc.r_up[i]; fcRl[idx]=R.fc.r_lo[i];
  });
  window._trendLabels = labels;
  window.monthlyTrendChart = new Chart(document.getElementById('trendChart').getContext('2d'), {
    type:'line',
    data:{ labels:labels, datasets:[
      {label:'月总销量', data:u, borderColor:'#e8783c', backgroundColor:'rgba(232,120,60,0.08)', yAxisID:'y', tension:0.3, pointRadius:2, pointHoverRadius:5},
      {label:'月总销售额($)', data:rv, borderColor:'#2f6fed', backgroundColor:'rgba(47,111,237,0.08)', yAxisID:'y1', tension:0.3, pointRadius:2, pointHoverRadius:5},
      {label:'销量预测', data:fcU, borderColor:'#e8783c', borderDash:[6,3], borderWidth:2, pointRadius:3, pointBackgroundColor:'#e8783c', fill:false, yAxisID:'y', tension:0.1},
      {label:'销量下界', data:fcUl, borderColor:'transparent', pointRadius:0, fill:{target:'+1', above:'rgba(232,120,60,0.15)'}, yAxisID:'y', tension:0.1},
      {label:'销量上界', data:fcUu, borderColor:'transparent', pointRadius:0, fill:false, yAxisID:'y', tension:0.1},
      {label:'销售额预测', data:fcR, borderColor:'#2f6fed', borderDash:[6,3], borderWidth:2, pointRadius:3, pointBackgroundColor:'#2f6fed', fill:false, yAxisID:'y1', tension:0.1},
      {label:'销售额下界', data:fcRl, borderColor:'transparent', pointRadius:0, fill:{target:'+1', above:'rgba(47,111,237,0.15)'}, yAxisID:'y1', tension:0.1},
      {label:'销售额上界', data:fcRu, borderColor:'transparent', pointRadius:0, fill:false, yAxisID:'y1', tension:0.1}
    ]},
    options:{ responsive:true, interaction:{mode:'index', intersect:false},
      plugins:{ tooltip:{callbacks:{ label:function(ctx){ var lb=ctx.dataset.label||''; if(lb.indexOf('界')>=0) return null; var v=ctx.parsed.y; if(v==null) return null; v=Math.round(v); return '  '+lb+': '+(lb.indexOf('销售额')>=0?'$'+v.toLocaleString():v.toLocaleString()); }}},
        legend:{labels:{color:'#1f2d3d', filter:function(item){ return item.text.indexOf('界')===-1; }}}},
      scales:{ y:{type:'linear', position:'left', title:{display:true, text:'销量', color:'#e8783c'}, ticks:{color:'#64748b'}, grid:{color:'rgba(88,116,150,0.38)'}},
               y1:{type:'linear', position:'right', title:{display:true, text:'销售额($)', color:'#2f6fed'}, ticks:{color:'#64748b'}, grid:{display:false}},
               x:{ticks:{color:'#64748b', maxTicksLimit:18}, grid:{color:'rgba(88,116,150,0.24)'}}} }
  });
  /* dual slider */
  var chart = window.monthlyTrendChart;
  var ls=document.getElementById('trendChartSliderLeft'), rs=document.getElementById('trendChartSliderRight'), ov=document.getElementById('trendChartSliderOverlay');
  var total=labels.length; ls.max=total-1; rs.max=total-1;
  ls.value=total-25; rs.value=total-1;
  function applySlider(){
    var l=Math.min(parseInt(ls.value),parseInt(rs.value)), r=Math.max(parseInt(ls.value),parseInt(rs.value));
    chart.options.scales.x.min=l; chart.options.scales.x.max=r; chart.update();
    ov.style.left=(l/(total-1)*100)+'%'; ov.style.width=((r-l)/(total-1)*100)+'%';
  }
  ls.addEventListener('input', applySlider); rs.addEventListener('input', applySlider);
  applySlider();
}

/* ============ 10. seasonality ============ */
function renderSeasonality(){
  var sm = sampleMonthly();
  var avg = sm.u.reduce(function(s,v){return s+v;},0)/sm.u.length;
  var vals = sm.u.map(function(v){ return v/avg; });
  var labels = months.concat(R.fc.labels);
  var allVals = vals.concat(R.fc.u.map(function(){ return null; }));
  var seasonal = R.seasonal;
  for(var i=months.length;i<labels.length;i++){
    var mm = labels[i].slice(5,7);
    allVals[i] = (R.fc.u[i-months.length]/R.fc.u.reduce(function(s,v){return s+v;},0)*12);
  }
  var colors = allVals.map(function(v,i){
    if(v==null) return 'rgba(100,116,139,.32)';
    if(i>=months.length) return 'rgba(47,111,237,0.45)';
    if(v>1.3) return '#e8783c'; if(v<0.7) return '#64748b'; return '#8a94a6';
  });
  new Chart(document.getElementById('seasonalityChart').getContext('2d'), {
    type:'bar',
    data:{labels:labels, datasets:[{label:'季节性指数', data:allVals, backgroundColor:colors, borderRadius:4, borderWidth:0}]},
    options:{responsive:true, plugins:{legend:{display:false}},
      scales:{ y:{ticks:{color:'#64748b'}, grid:{color:'rgba(88,116,150,0.38)'}, title:{display:true, text:'季节性指数', color:'#64748b'}},
               x:{ticks:{color:'#1f2d3d', maxTicksLimit:18}, grid:{display:false}}}}
  });
  var peakMonths = labels.filter(function(l,i){ return colors[i]==='#e8783c'; });
  var offMonths = labels.filter(function(l,i){ return colors[i]==='#64748b' && i<months.length; });
  document.getElementById('seasonalityMeta').innerHTML =
    '<div><strong>峰值月份</strong>: '+esc(peakMonths.slice(-3).join(', '))+'</div>'
    + '<div><strong>同比增长</strong>: '+(R.yoy==null?'—':'+'+R.yoy+'%')+'</div>'
    + '<div><strong>建议备货月份</strong>: 2026-08（旺季第一个月 2026-10 前 2 个月）</div>';
  document.getElementById('seasonalityNote').textContent = '旺季月份: '+peakMonths.join(', ')+'；建议 2026-10 前 60-75 天完成下单与物流排期（海运30-40天+入仓14天+缓冲15天）；淡季月份: '+offMonths.join(', ')+'，避免大量备货；历史峰值特征: '+R.peak_months.join(' / ')+'；数据范围: '+months[0]+' 至 '+months[months.length-1]+'，共 '+months.length+' 个月';
}

/* ============ 11. product intro ============ */
function renderIntro(){
  var fields = [
    ['product_summary','产品介绍','带灯化妆镜（Lighted Makeup Mirror）是通过 LED 灯珠模拟自然光的桌面/壁挂化妆镜，解决室内光线不足导致的化妆不均匀、看不清细节的问题。主流形态为台式双面镜（1X+10X放大）与壁挂镜，面向日常化妆、护肤精修和旅行补妆场景，是美国美妆个护家用品中的高频刚需品类。'],
    ['mainstream_configuration','主流配置','基础款：LED 白光/单色温、USB 或电池供电、20-30cm 镜面、1X 平面镜。主流款：双面镜（1X+10X）、3 色温（白/暖/自然）、触控无级调光、USB-C 充电、镜面 30cm+、360° 旋转支架。高配款：48 颗以上灯珠、可拆卸小放大镜（10X/20X/30X）、大镜面（40cm+）+ 抽屉收纳一体设计。'],
    ['key_feature_explanation','重要功能属性说明','供电方式（USB/电池）决定使用场景自由度，纯电池款差评集中在续航；灯光模式（3色温）直接影响妆效判断，是最强卖点之一；可调光/触控提升体验且已是高GMV链接标配；放大倍数（10X）满足细节需求但需标注对焦距离防畸变差评；安装方式（台式/壁挂）划分场景人群；镜面尺寸影响首屏观感与客单价；边框材质影响质感与破损率；形状（矩形/圆形）影响铺货陈列与差异化。'],
    ['buyer_decision','购买决策','买家首先看灯：色温数量与亮度是否可调，直接决定「能不能画对妆」；其次看放大倍数与镜面尺寸是否匹配使用场景；供电方式影响摆放自由度。值得多付钱的是 3 色温+无级调光、双面镜、USB-C 和更大的镜面；单纯「灯珠数量」「礼盒包装」等卖点对实际使用影响有限，不值得单独加价。'],
    ['certification_requirements','Amazon 强制认证','该品类无强制品类审核。带 LED 电路需符合 FCC（电子部分电磁兼容）；加州65（Prop 65）建议自查铅/邻苯；电池款运输需 UN38.3（含电池产品物流要求）；如宣称「防雾/防水」需有据可依。无 FDA 强制要求（非医疗器械类放大镜）。']
  ];
  document.getElementById('productIntroGrid').innerHTML = fields.map(function(f){
    return '<div class="product-intro-field"><label for="intro-'+f[0]+'">'+f[1]+'</label><div id="intro-'+f[0]+'" class="product-intro-editable" contenteditable="true" data-key="'+f[0]+'" data-placeholder="">'+esc(f[2])+'</div></div>';
  }).join('');
  var KEY='productIntroState:Makeup-Mirror-with-Lights_20260901';
  var els=document.querySelectorAll('.product-intro-editable');
  var raw=null; try{ raw=storage.getItem(KEY); }catch(e){}
  if(raw){ try{ var st=JSON.parse(raw); els.forEach(function(el){ if(st[el.dataset.key]!==undefined) el.textContent=st[el.dataset.key]; }); }catch(e){} }
  els.forEach(function(el){
    el.addEventListener('input', function(){
      var state={}; els.forEach(function(e2){ state[e2.dataset.key]=e2.textContent.trim(); });
      try{ storage.setItem(KEY, JSON.stringify(state)); }catch(e){}
      document.getElementById('productIntroStatus').textContent='已自动保存';
    });
  });
}

/* ============ 12. market structure charts ============ */
function renderStructure(){
  /* price bands */
  var pb = R.price_bands;
  new Chart(document.getElementById('priceBandChart').getContext('2d'), {
    type:'bar',
    data:{ labels:pb.map(function(x){return x.band;}), datasets:[
      {label:'GMV占比(%)', data:pb.map(function(x){return x.gmv_share;}), backgroundColor:'rgba(232,120,60,0.7)', borderRadius:4, yAxisID:'y'},
      {label:'ASIN数', data:pb.map(function(x){return x.n;}), backgroundColor:'rgba(47,111,237,0.42)', borderRadius:4, yAxisID:'y1'},
      {label:'新品数', data:pb.map(function(x){return Math.round(x.n*x.new_share/100);}), backgroundColor:'rgba(24,154,78,0.42)', borderRadius:4, yAxisID:'y1'},
      {type:'line', label:'新品占比(%)', data:pb.map(function(x){return x.new_share;}), borderColor:'#c07d10', backgroundColor:'rgba(210,153,34,0.15)', borderWidth:2, pointRadius:3, tension:0.25, yAxisID:'y2'}
    ]},
    options:{responsive:true, plugins:{legend:{labels:{color:'#1f2d3d'}}},
      scales:{ y:{position:'left', title:{display:true, text:'GMV占比(%)', color:'#e8783c'}, ticks:{color:'#64748b'}, grid:{color:'rgba(88,116,150,0.38)'}},
               y1:{position:'right', title:{display:true, text:'数量', color:'#2f6fed'}, ticks:{color:'#64748b'}, grid:{display:false}},
               y2:{position:'right', title:{display:true, text:'新品占比(%)', color:'#c07d10'}, ticks:{color:'#64748b', callback:function(v){return v+'%';}}, grid:{display:false}},
               x:{ticks:{color:'#64748b'}, grid:{color:'rgba(88,116,150,0.24)'}}}}
  });
  document.getElementById('priceBandTableHost').innerHTML = '<table><thead><tr><th>价格带</th><th>ASIN数</th><th>GMV占比</th><th>平均价格($)</th><th>新品占比</th><th>平均评分</th></tr></thead><tbody>'
    + pb.map(function(x){ return '<tr><td>'+x.band+'</td><td>'+x.n+'</td><td>'+x.gmv_share+'%</td><td>$'+x.avg_price.toFixed(2)+'</td><td>'+x.new_share+'%</td><td>'+x.avg_rating+'</td></tr>'; }).join('')+'</tbody></table>';
  /* brand donut + CR */
  var k = R.kpi;
  var rest = Math.max(0, 100-k.cr5);
  new Chart(document.getElementById('brandDonutChart').getContext('2d'), {
    type:'doughnut',
    data:{ labels:['CR1','CR2-3','CR4+CR5','其他品牌'], datasets:[{data:[k.cr1, Math.max(0,k.cr3-k.cr1), Math.max(0,k.cr5-k.cr3), rest], backgroundColor:['#e8783c','#c07d10','#2f6fed','rgba(100,116,139,.32)'], borderColor:'#eef4fb', borderWidth:2}]},
    options:{responsive:true, plugins:{legend:{position:'bottom', labels:{color:'#1f2d3d'}}}}
  });
  document.getElementById('brandCrTableHost').innerHTML = '<table><thead><tr><th>指标</th><th>数值</th><th>用途</th><th>结论</th></tr></thead><tbody>'
    + '<tr><td>CR1</td><td>'+k.cr1+'%</td><td style="font-size:12px;color:var(--muted)">第一大品牌GMV占全市场比例</td><td>正常(&lt;35%)</td></tr>'
    + '<tr><td>CR3</td><td>'+k.cr3+'%</td><td style="font-size:12px;color:var(--muted)">前三大品牌合计GMV占全市场比例</td><td>分散(&lt;60%)</td></tr>'
    + '<tr><td>CR5</td><td>'+k.cr5+'%</td><td style="font-size:12px;color:var(--muted)">前五大品牌合计GMV占比，越低中腰部机会越大</td><td>中腰部有空间(&lt;80%)</td></tr>'
    + '<tr><td>HHI</td><td>'+k.hhi+'</td><td style="font-size:12px;color:var(--muted)">赫芬达尔指数。≥1800=高度集中,1000-1800=中等,&lt;1000=分散</td><td>分散(&lt;1000)</td></tr></tbody></table>';
  /* top brands bar */
  var tb = R.top_brands;
  new Chart(document.getElementById('brandBarChart').getContext('2d'), {
    type:'bar',
    data:{ labels:tb.map(function(x){return x.brand;}), datasets:[{label:'近6月GMV($)', data:tb.map(function(x){return x.gmv;}), backgroundColor:tb.map(function(x,i){ return i<3?'rgba(232,120,60,0.75)':'rgba(47,111,237,0.55)';}), borderRadius:4}]},
    options:{indexAxis:'y', responsive:true, plugins:{legend:{display:false}},
      scales:{ x:{ticks:{color:'#64748b', callback:function(v){return '$'+(v/1000).toFixed(0)+'k';}}, grid:{color:'rgba(88,116,150,0.38)'}}, y:{ticks:{color:'#64748b'}, grid:{display:false}}}}
  });
  /* distribution tabs */
  var DIST_COLORS = ['rgba(47,111,237,0.78)','rgba(232,120,60,0.78)','rgba(24,154,78,0.78)','rgba(139,92,246,0.78)','rgba(192,125,16,0.78)','rgba(229,72,77,0.6)','rgba(139,148,158,0.6)'];
  window._distCharts = {};
  window.renderDistributionChart = function(tabId){
    var map = {distPrice:'price', distRating:'rating', distSellerType:'seller_type', distBrand:'brand', distSeller:'seller', distAge:'age'};
    var dk = map[tabId]; if(!dk) return;
    var rows = R.dists[dk];
    if(!rows) return;
    /* stacked monthly series by group label */
    var series = {};
    rows.forEach(function(row, ri){ series[row.label] = months.map(function(){ return 0; }); });
    records.forEach(function(r){
      var lbl;
      if(dk==='price'){ var p=r.price||0; lbl = p<25?'$0-25':p<50?'$25-50':p<100?'$50-100':p<150?'$100-150':p<200?'$150-200':'$200+'; }
      else if(dk==='rating'){ var rt=r.rating||0; lbl = rt>=4.8?'4.8-5.0':rt>=4.6?'4.6-4.79':rt>=4.4?'4.4-4.59':rt>=4.2?'4.2-4.39':rt>=4.0?'4.0-4.19':'其他'; }
      else if(dk==='seller_type'){ lbl = r.fba?'FBA':'FBM'; }
      else if(dk==='brand'){ lbl = r.brand; }
      else if(dk==='seller'){ lbl = r.seller||'NA'; }
      else { var d=r.days||0; lbl = d<=180?'0-6个月':d<=365?'6-12个月':d<=730?'1-2年':'2年以上'; }
      if(!(lbl in series)){
        var known = rows.some(function(row){ return row.label===lbl; });
        lbl = known? lbl : (rows[rows.length-1].label.indexOf('其他')===0? rows[rows.length-1].label : lbl);
        if(!(lbl in series)) series[lbl] = months.map(function(){ return 0; });
      }
      r.units.forEach(function(u,i){ series[lbl][i] += (u||0); });
    });
    var keys = Object.keys(series).sort(function(a,b){ var sa=series[a].reduce(function(x,y){return x+y;},0), sb=series[b].reduce(function(x,y){return x+y;},0); return sb-sa; }).slice(0,7);
    var canvasId = tabId+'Chart';
    if(window._distCharts[tabId]) window._distCharts[tabId].destroy();
    window._distCharts[tabId] = new Chart(document.getElementById(canvasId).getContext('2d'), {
      type:'bar',
      data:{ labels:months, datasets:keys.map(function(kk, i){ return {label:kk, data:series[kk], backgroundColor:DIST_COLORS[i%DIST_COLORS.length], stack:'sales', borderRadius:2}; })},
      options:{responsive:true, plugins:{legend:{position:'bottom', labels:{color:'#1f2d3d', boxWidth:10, font:{size:10}}}},
        scales:{ x:{stacked:true, ticks:{color:'#64748b', maxTicksLimit:12}, grid:{color:'rgba(48,54,61,0.18)'}},
                 y:{stacked:true, title:{display:true, text:'月销量(件)', color:'#64748b'}, ticks:{color:'#64748b', callback:function(v){return Number(v).toLocaleString();}}, grid:{color:'rgba(88,116,150,0.28)'}}}}
    });
    var hostId = tabId+'TableHost';
    var hostEl = document.getElementById(hostId);
    if(hostEl) hostEl.innerHTML = '<table><thead><tr><th>'+({price:'价格带',rating:'评分区间',seller_type:'卖家/发货方式',brand:'品牌',seller:'卖家',age:'上架时间'}[dk])+'</th><th>产品数</th><th>累计销量</th><th>销量占比</th><th>近6月GMV</th><th>均价</th><th>均评分</th><th>新品占比</th></tr></thead><tbody>'
      + rows.map(function(x){ return '<tr><td>'+esc(x.label)+'</td><td>'+x.n+'</td><td>'+fmtN(x.units)+'</td><td>'+(x.units/R.kpi.total_units*100).toFixed(1)+'%</td><td>'+fmtK$(x.gmv)+'</td><td>$'+x.avg_price.toFixed(2)+'</td><td>'+x.avg_rating+'</td><td>'+x.new_share+'%</td></tr>'; }).join('')+'</tbody></table>';
  };
  window.switchDistributionTab = function(btn, tabId){
    var wrapper = btn.closest('.distribution-tabs');
    wrapper.querySelectorAll('.tab-btn').forEach(function(n){ n.classList.remove('active'); });
    btn.classList.add('active');
    wrapper.querySelectorAll('.tab-content').forEach(function(n){ n.classList.remove('active'); });
    var panel = wrapper.querySelector('#'+tabId);
    if(!panel) return;
    panel.classList.add('active');
    renderDistributionChart(tabId);
  };
  renderDistributionChart('distPrice');
  /* scatter */
  var pts = R.scatter;
  var topBrands = R.top_brands.slice(0,3).map(function(x){ return x.brand; });
  var topColors = {0:'rgba(47,111,237,0.78)',1:'rgba(139,92,246,0.78)',2:'rgba(192,125,16,0.82)'};
  var topBorders = {0:'#2f6fed',1:'#8b5cf6',2:'#c07d10'};
  document.getElementById('scatterLegend').innerHTML = topBrands.map(function(b,i){ return '<span class="scatter-legend-item"><span class="scatter-legend-dot" style="background:'+topBorders[i]+';border:1px solid '+topBorders[i]+'"></span>Top'+(i+1)+' '+esc(b)+'</span>'; }).join('')
    + '<span class="scatter-legend-item"><span class="scatter-legend-dot" style="background:rgba(232,120,60,0.38);border:1px solid #e8783c"></span>非Top3品牌</span>'
    + '<span class="scatter-legend-item"><span class="scatter-legend-dot" style="background:transparent;border:3px solid #189a4e"></span>绿色外圈：一年内新品</span>';
  new Chart(document.getElementById('priceVolumeScatter').getContext('2d'), {
    type:'scatter',
    data:{ datasets:[{ label:'产品', data:pts,
      backgroundColor:pts.map(function(p){ var i=topBrands.indexOf(p.brand); return i>=0?topColors[i]:'rgba(232,120,60,0.38)'; }),
      borderColor:pts.map(function(p){ var i=topBrands.indexOf(p.brand); return p.is_new?'#189a4e':(i>=0?topBorders[i]:'#e8783c'); }),
      borderWidth:pts.map(function(p){ return p.is_new?3:(topBrands.indexOf(p.brand)>=0?2:1); }),
      pointRadius:pts.map(function(p){ return p.is_new?6:5; }), pointHoverRadius:8 }]},
    options:{responsive:true, plugins:{ tooltip:{callbacks:{label:function(ctx){ var p=pts[ctx.dataIndex]; if(!p) return ''; return [(p.brand||'?')+' - '+(p.title||p.asin||''), '销量: '+p.x.toLocaleString()+' 件', '价格: $'+p.y.toFixed(2), topBrands.indexOf(p.brand)>=0?('Top品牌: #'+(topBrands.indexOf(p.brand)+1)):'非Top3品牌', p.is_new?'一年内新品':'老链接']; }}}, legend:{display:false}},
      scales:{ x:{title:{display:true, text:'2026年销量(件)', color:'#64748b'}, ticks:{color:'#64748b'}, grid:{color:'rgba(88,116,150,0.24)'}},
               y:{title:{display:true, text:'价格($)', color:'#64748b'}, ticks:{color:'#64748b'}, grid:{color:'rgba(88,116,150,0.24)'}}}}
  });
}

/* ============ 13. parent appendix ============ */
function renderParent(){
  var rows = R.parent_rows;
  var tot30 = records.reduce(function(s,r){ return s+(r.units30||0); },0);
  document.getElementById('parentTableHost').innerHTML = '<table><thead><tr><th>#</th><th>Parent ASIN</th><th>品牌</th><th>产品数</th><th>30d总销量</th><th>销量占比</th><th>6月GMV</th><th>GMV占比</th><th>均价</th><th>均评分</th></tr></thead><tbody>'
    + rows.map(function(x, i){ return '<tr><td>'+(i+1)+'</td><td>'+link(x.parent)+'</td><td>'+esc(x.brand)+'</td><td>'+x.n+'</td><td>'+fmtN(x.u30)+'</td><td>'+x.u_share+'%</td><td>'+fmtK$(x.gmv)+'</td><td>'+x.gmv_share+'%</td><td>$'+x.avg_price.toFixed(2)+'</td><td>'+x.avg_rating+'</td></tr>'; }).join('')+'</tbody></table>';
  var labels = months;
  var palette = ['#e8783c','#2f6fed','#8b5cf6','#c07d10','#189a4e','#e5484d','#2f6fed','#d6338a','#34b96b','#f08c3a'];
  var datasets = [];
  rows.forEach(function(x, i){
    var group = records.filter(function(r){ return (r.parent||r.asin)===x.parent; });
    var u = months.map(function(m, mi){ return group.reduce(function(s,r){ return s+(r.units[mi]||0); },0); });
    var rv = months.map(function(m, mi){ return group.reduce(function(s,r){ return s+(r.rev[mi]||0); },0); });
    datasets.push({label:x.parent+' 销量', data:u, borderColor:palette[i], backgroundColor:palette[i]+'18', tension:0.3, pointRadius:2, borderWidth:2, yAxisID:'y'});
    datasets.push({label:x.parent+' 销售额', data:rv, borderColor:palette[i], backgroundColor:'transparent', borderDash:[6,3], tension:0.3, pointRadius:1, borderWidth:1.5, yAxisID:'y1'});
  });
  var active = datasets.slice();
  var chart = new Chart(document.getElementById('groupChart_Parent_ASIN').getContext('2d'), {
    type:'line',
    data:{labels:labels, datasets:active},
    options:{responsive:true, interaction:{mode:'nearest', intersect:false},
      plugins:{ tooltip:{callbacks:{label:function(ctx){ var ds=ctx.dataset; var lb=ds.label||''; var v=ctx.parsed.y||0; if(ds.borderDash){ return lb.replace(/ 销售额$/,'')+' 销售额: $'+v.toLocaleString(undefined,{maximumFractionDigits:0}); } return lb.replace(/ 销量$/,'')+' 销量: '+v.toLocaleString(undefined,{maximumFractionDigits:0}); }}},
        legend:{position:'bottom', labels:{color:'#1f2d3d', usePointStyle:true, padding:10, font:{size:11}, filter:function(item){ return item.datasetIndex!==undefined && item.dataset && !item.dataset.borderDash; }, generateLabels:function(ch){ var orig=Chart.defaults.plugins.legend.labels.generateLabels(ch); orig.forEach(function(l){ l.text=l.text.replace(/ 销量$/,''); }); orig.push({text:'── 销量    …… 销售额', fillStyle:'transparent', strokeStyle:'transparent', index:-1, datasetIndex:-1, hidden:false, pointStyle:false, fontColor:'#64748b', font:{size:10}}); return orig; }}}},
      scales:{ y:{type:'linear', position:'left', title:{display:true, text:'月销量', color:'#e8783c'}, ticks:{color:'#64748b'}, grid:{color:'rgba(88,116,150,0.38)'}},
               y1:{type:'linear', position:'right', title:{display:true, text:'月销售额($)', color:'#2f6fed'}, ticks:{color:'#64748b'}, grid:{display:false}},
               x:{ticks:{color:'#64748b', maxTicksLimit:14}, grid:{color:'rgba(88,116,150,0.16)'}}}}
  });
  var toggles = document.getElementById('brandToggles_groupChart_Parent_ASIN');
  toggles.innerHTML = rows.map(function(x, i){ return '<button type="button" data-pi="'+i+'" style="background:var(--card);color:'+palette[i]+';border:1px solid var(--border);border-radius:4px;padding:2px 8px;font-size:11px;cursor:pointer">'+esc(x.parent)+'</button>'; }).join('');
  toggles.querySelectorAll('button').forEach(function(btn){
    btn.onclick = function(){
      var i = parseInt(btn.dataset.pi);
      var visible = chart.data.datasets.filter(function(ds){ return ds.borderColor===palette[i]; }).every(function(ds){ return ds.hidden; });
      chart.data.datasets.forEach(function(ds){ if(ds.borderColor===palette[i]) ds.hidden=!visible; });
      chart.update();
      btn.style.opacity = visible?1:0.35;
    };
  });
  var slider = document.getElementById('groupChart_Parent_ASINSlider');
  slider.max = months.length-1; slider.value = 0;
  slider.addEventListener('input', function(){ chart.options.scales.x.min = parseInt(slider.value); chart.update(); });
}

/* ============ 14. opportunity appendix ============ */
function renderOpportunity(){
  /* Kano html scatter */
  var kano = R.kano;
  var maxX = 100, maxY = 100;
  var dots = kano.map(function(k){
    var color = k.coverage>=60?'#2f6fed':(k.coverage>=30?'#c07d10':'#e5484d');
    return '<div class="scatter-dot" style="left:'+k.coverage+'%;bottom:'+k.gmv_share+'%;width:14px;height:14px;background:'+color+'" title="'+esc(k.attr)+' (覆盖 '+k.coverage+'%, GMV '+k.gmv_share+'%)"></div>'
      + '<div class="scatter-label" style="left:'+k.coverage+'%;bottom:'+k.gmv_share+'%">'+esc(k.attr)+'</div>';
  }).join('');
  var grid = [20,40,60,80].map(function(p){
    return '<div class="scatter-gridline" style="bottom:'+p+'%;left:0;right:0"></div><div class="scatter-gridline-v" style="left:'+p+'%;top:0;bottom:0"></div>'
      + '<div class="scatter-tick-x" style="left:'+p+'%;bottom:-18px;transform:translateX(-50%)">'+p+'%</div>'
      + '<div class="scatter-tick-y" style="bottom:'+p+'%;left:-32px;transform:translateY(50%)">'+p+'%</div>';
  }).join('');
  document.getElementById('kanoScatter').innerHTML = '<div class="scatter-area">'+grid+dots+'</div><div class="scatter-axis-x">有效覆盖率 (%)</div><div class="scatter-axis-y">近6月 GMV 占比 (%)</div>';
  /* consensus */
  document.getElementById('consensusHost').innerHTML = '<table><thead><tr><th>属性/卖点主题</th><th>卖点性质</th><th>Listing建议位置</th><th>覆盖率</th><th>GMV占比</th><th>代表表达</th><th>分析</th></tr></thead><tbody>'
    + kano.map(function(k, i){
      var nature = k.coverage>=60?'标配卖点':(k.coverage>=30?'溢价卖点':'观察卖点');
      var pos = k.coverage>=60?'标题必带':(k.coverage>=30?'五点首行':'A+补充');
      var sample = records[Math.floor(i%records.length)];
      return '<tr><td>'+esc(k.attr)+'</td><td><span class="tag tag-info">'+nature+'</span></td><td><span class="tag '+(pos==='标题必带'?'tag-pass':'tag-info')+'">'+pos+'</span></td><td>'+k.coverage+'%</td><td>'+k.gmv_share+'%</td><td style="max-width:220px;font-size:10px;color:var(--muted)">'+esc((sample.title||'').slice(0,80))+'</td><td style="font-size:12px;color:var(--muted);max-width:240px">覆盖'+k.coverage+'% / GMV'+k.gmv_share+'%，'+(nature==='标配卖点'?'属于进入市场的基础配置。':(nature==='溢价卖点'?'可作为溢价点在五点与A+中放大。':'仅作观察，不建议占用标题空间。'))+'</td></tr>';
    }).join('')+'</tbody></table>';
  /* attribute matrix */
  document.getElementById('attMatrixHost').innerHTML = '<table><thead><tr><th>属性维度</th><th>属性值</th><th>渗透率</th><th>GMV占比</th><th>销量占比</th><th>溢价指数</th><th>近3月增速</th><th>机会标签</th><th>分析</th></tr></thead><tbody>'
    + R.att_rows.map(function(x){
      return '<tr><td>'+esc(x.field)+'</td><td>'+esc(x.val)+'</td><td>'+x.pen+'%</td><td>'+x.gmv_share+'%</td><td>'+x.units_share+'%</td><td>'+(x.premium==null?'—':x.premium)+'</td><td>'+(x.growth==null?'—':x.growth+'%')+'</td>'
        + '<td><span class="tag '+(x.tag==='基础标配'?'tag-info':(x.tag==='高溢价机会'?'tag-pass':'tag-info'))+'">'+esc(x.tag)+'</span></td>'
        + '<td style="font-size:12px;color:var(--muted);max-width:200px">'+(x.tag==='基础标配'?'这是市场默认要求，不做会掉队，做了也不一定带来溢价。':(x.tag==='高溢价机会'?'供给少但GMV占比高，且有明确溢价，适合作为V1差异化配置。':(x.tag==='细分机会项'?'可作为补充属性观察，适合和其他优势组合一起判断。':'普通属性，优先级靠后。')))+'</td></tr>';
    }).join('')+'</tbody></table>';
  /* combos */
  document.getElementById('comboHost').innerHTML = '<table><thead><tr><th>属性组合</th><th>ASIN数</th><th>近6月GMV</th><th>增速</th><th>拥挤度</th><th>机会标签</th><th>分析</th></tr></thead><tbody>'
    + R.combo_rows.map(function(x){
      var colors = ['#189a4e','#e8783c','#8b5cf6'];
      return '<tr><td style="max-width:300px">'+x.combo.map(function(v, i){ return '<span class="combo-tag" style="color:'+colors[i%3]+';border-color:'+colors[i%3]+'44">'+esc(v)+'</span>'; }).join(' ')+'</td><td>'+x.n+'</td><td>'+fmtK$(x.gmv)+'</td><td>'+(x.growth==null?'—':x.growth+'%')+'</td><td>'+x.crowding+'</td>'
        + '<td><span class="tag '+(x.tag==='高GMV低拥挤'?'tag-pass':'tag-info')+'">'+esc(x.tag)+'</span></td>'
        + '<td style="font-size:12px;color:var(--muted);max-width:200px">'+(x.tag==='高GMV低拥挤'?'需求足够大但供给没有完全挤满，适合优先验证。':'组合具备参考意义，但优先级不应高于更明确的机会组合。')+'</td></tr>';
    }).join('')+'</tbody></table>';
}

/* ============ 15. toolbar / misc ============ */
window.resetReportState = function(){ if(!confirm('重置所有修改？')) return; if(window.reportStorage && window.reportStorage.clear) window.reportStorage.clear(); location.reload(); };
function downloadHtml(html, filename){
  var blob = new Blob([html], {type:'text/html;charset=utf-8'});
  var url = URL.createObjectURL(blob);
  var aEl = document.createElement('a'); aEl.href=url; aEl.download=filename;
  document.body.appendChild(aEl); aEl.click(); document.body.removeChild(aEl);
  setTimeout(function(){ URL.revokeObjectURL(url); }, 0);
}
async function saveCurrentHtml(){
  var btn = document.getElementById('saveCurrentHtmlBtn');
  try{
    try { window.saveAll && window.saveAll(); } catch(e){}
    var html = '<!doctype html>\n' + document.documentElement.outerHTML;
    if(btn){ btn.disabled=true; btn.textContent='保存中'; }
    downloadHtml(html, 'Makeup-Mirror-with-Lights_20260901.html');
    if(btn) btn.textContent='已保存';
    setTimeout(function(){ if(btn){ btn.textContent='保存当前HTML'; btn.disabled=false; } }, 1200);
  }catch(e){ if(btn){ btn.textContent='保存当前HTML'; btn.disabled=false; } alert('保存失败: '+e.message); }
}
window.saveCurrentHtml = saveCurrentHtml;
window.exportReport = function(){
  try{
    var html = '<!doctype html>\n' + document.documentElement.outerHTML;
    downloadHtml(html, 'Makeup-Mirror-with-Lights_20260901-已编辑.html');
  }catch(e){ alert('导出失败: '+e.message); }
};
function applyAccessibility(){
  document.querySelectorAll('canvas').forEach(function(canvas){
    var box = canvas.closest('.chart-box');
    var heading = box? box.querySelector('h3, h4') : null;
    var label = (canvas.getAttribute('aria-label') || (heading && heading.textContent) || '数据图表').trim();
    canvas.setAttribute('role','img'); canvas.setAttribute('aria-label', label);
    if(!canvas.textContent.trim()) canvas.textContent = label + '。具体数值请查看相邻表格或正文。';
  });
}

/* ============ boot ============ */
document.addEventListener('DOMContentLoaded', function(){
  renderDecision();
  setProductViewMode('decision');
  renderProductTable();
  renderBenchmark();
  renderV1();
  renderProfit();
  renderPpc();
  renderReviews();
  renderKpi();
  renderTrend();
  renderSeasonality();
  renderIntro();
  renderStructure();
  renderParent();
  renderOpportunity();
  applyAccessibility();
  var now = new Date();
  document.getElementById('modTime').textContent = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')+' '+now.toTimeString().slice(0,8);
});
})();
