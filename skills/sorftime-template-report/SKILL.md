---
name: sorftime-template-report
description: This skill should be used when the user wants to generate a professional Amazon market research HTML report based on a template structure, using Sorftime data. It covers the full pipeline from template study, Sorftime CLI data collection, Python data consolidation and analysis, to interactive HTML report generation with Chart.js charts, dynamic product tables, decision scorecards, profit analysis, PPC tables, review pain points, trend forecasting, seasonality, market structure distributions, Kano scatter plots, attribute opportunity matrices, and Parent ASIN grouping.
agent_created: true
---

# Sorftime Template Market Report Pipeline

> 💡 无 Sorftime 凭证、或调用报"额度不足"时：通过专属通道注册/充值（含 7 天试用）→ https://open.sorftime.com/home?tag=ODY2OA%7E%7E ｜ 优惠码：8668

## Purpose

Generate interactive, data-driven Amazon market research HTML reports that mirror a professional template structure. The pipeline pulls real data via Sorftime CLI, computes advanced analytics (scorecards, forecasts, seasonality, opportunity matrices), and renders an interactive dark-themed HTML report with Chart.js visualizations, editable fields, and persistent state via localStorage.

## When to Use

Trigger this skill when the user asks to:
- "按模板做一份XX市场报告"
- "复制/复刻/还原这份模板报告"
- "用Sorftime数据生成XX品类的调研报告"
- Any request involving Amazon market research report generation with a template reference

- Sorftime CLI installed and authenticated (`sorftime api` commands available)
- Python 3.x with `jq` CLI tool installed
- A template HTML report to study (for CSS extraction and structural reference)

> **环境注记（按本机实际情况调整）**
> - 需要 `jq`：若不在 PATH，先 `export PATH="$HOME/.workbuddy/bin:$PATH"`，或直接写 jq 的绝对路径。
> - Python 3.x、Node ≥18 按本机实际安装路径调用。
> - CLI profile：先跑 `sorftime whoami` 确认已认证（Windows 上见下方「本机环境适配」第 1 条，需走 node 直调）。
> - 本机没有 `scripts/doctor.sh`，连通性用一次轻量调用验证即可，例如 `CategorySearchFromName '{"name":"kitchen"}'`（1 credit）。
> - 报告管线数据源为 Sorftime CLI，不经过 MCP 工具，无需工具名适配。

## Pipeline Overview
## Pipeline Overview

```
Template Study → Sorftime Data Collection → Data Consolidation → Analysis →
HTML Shell Generation → App JS Development → Assembly → Validation
```

### Step 1: Template Study

1. Read the template HTML file in segments (it may be large, e.g. 0.6MB)
2. Extract CSS (usually lines 10-608) into `template.css`
3. **CRITICAL**: Strip `<style>` tags from the extracted CSS before injecting into shell — nested `<style>` tags break rendering
4. Map all anchor IDs: `s1b`, `v1ProductDefinition`, `s1c`, `s2b`, `s1`, `s1a`, `s2`, `s3`, `s4`, `marketDetailAppendix`, `opportunityDetailAppendix`, `reviewDetailAppendix`
5. Identify all container divs: `decisionBriefModule`, `benchmarkHost`, `productTableContainer`, `v1Grid`, `profitTableContainer`, `ppcTableContainer`, `reviewSection`, `kpiGrid`, `trendChartContainer`, `seasonChartContainer`, `marketStructureContainer`, `parentChartContainer`, `opportunityMatrixContainer`
6. Note interactive features: product status workflow (candidate/benchmark/exclude/undecided), column hiding, filtering, sorting, image preview, month column collapsing, editable fields, reportStorage persistence

### Step 2: Sorftime Data Collection

**Domain mapping**: US=1, UK=2, DE=3, etc.

**Credit budget example** (57 ASINs, makeup mirrors):
- CategorySearchFromName: 1 credit
- CategoryRequest (Top100): 5 credits
- ProductRequest batch ×6 (10 ASINs each, trend=1): ~60 credits for full trend data
- CategoryTrend (sales+price): 2 credits
- KeywordRequest ×3 (core terms): 3 credits
- KeywordList/Extends: 2-4 credits
- ProductCustomersSay ×5 (Top5 ASINs): 5 credits
- **Total**: ~80 credits per report

**Key endpoints**:
```bash
# Search category
sorftime api CategorySearchFromName '{"name":"Makeup Mirrors","domain":1}' --domain 1

# Top100 products
sorftime api CategoryRequest '{"nodeId":"3785121","type":1,"pageSize":100}' --domain 1

# Batch product trends (max 10 ASINs per call)
sorftime api ProductRequest '{"asinList":"B095YT2QB3,...","trend":1,"queryTrendStartDt":"2022-06-01"}' --domain 1

# Category trends
sorftime api CategoryTrend '{"nodeId":"3785121","trendIndex":0,"pageSize":24}' --domain 1
```

**Data processing notes**:
- CLI output has a 2-line banner — always pipe through `tail -n +3` before `jq`
- ProductRequest trend arrays (`ListingSalesVolumeOfMonthTrend`, `ListingSalesOfMonthTrend`, `PriceTrend`) are daily "rolling 30-day" values. To get monthly values, take the last day of each month
- Price fields are in **cents** — divide by 100
- `photo` field may be a URL array, not a string — take `[0]`
- `Size` field may be a string like `"['44.91,34.80,4.90']"` — use regex to extract numbers

### Step 3: Data Consolidation (`scripts/consolidate.py`)

Inputs: `products.json`, `prod_*.json`, `trend_*.json`, `kw_*.json`, `csay_*.json`
Outputs: `consolidated.json`, `records_coupled.json`

Key computations:
- `last_day_map()`: extract monthly values from daily trend arrays
- KPIs: product count, brand count, avg rating, median reviews, avg price, total GMV, total units, CR1/CR3/CR5, HHI
- Price bands (e.g. <$20, $20-30, $30-40, $40-50, $50+)
- Brand concentration (Top10 by units)
- 6 distributions: price, rating, seller type, brand, seller, age
- Scatter data (price vs units, color by brand)
- Keyword aggregation
- CustomersSay aggregation (positive/negative mentions)
- Product coupling fields from title + ProductInfo (shape, mount, frame, magnification, power, light modes, dimmable, color, mirror size, weight)

### Step 4: Analysis (`scripts/analysis.py`)

Input: `consolidated.json`, `records_coupled.json`
Output: `analysis.json`

Computations:
- **Scorecard** (12 dimensions, normalized to 100): market size, growth, concentration, rating health, review barrier, price stability, margin space, seasonality, FBA share, brand diversity, new product survival, keyword breadth
- **Kano data** for scatter plot
- **Attribute opportunity matrix**: penetration, GMV share, premium index, 3-month growth, opportunity tags (basic/premium/niche/ordinary)
- **Combination opportunities**: shape × mount × power combinations
- **Seasonality**: monthly index, peak months, YoY growth
- **Forecast**: 12-month projection using seasonal mean × recent mean, with ±volume confidence intervals
- **Pain points**: aggregated from CustomersSay negative mentions, mapped to CN labels
- **Parent ASINs**: grouped by parent, top 10
- **PPC economics**: 16 keywords with tier classification (core/secondary/long-tail), suggested bid, affordable CPC

### Step 5: HTML Shell Generation (`scripts/build_shell.py`)

- Inject `template.css` into `<style>` block
- Create all container divs with correct IDs matching template anchors
- Substitute placeholders: `__SCORE__`, `__NOW__`
- Generate `reportStorage` localStorage wrapper with correct `STORAGE_KEY`

### Step 6: App JS (`scripts/app.js`)

~700-800 lines, 15 render modules:
1. `renderDecision()` — decision command + action cards + scorecard
2. Product table engine — decision/spec/full views, filtering, sorting, sparklines, image preview
3. `renderBenchmark()` — competitor comparison with spec diff highlighting
4. `renderV1()` — must/should/avoid columns + opportunity hypotheses
5. `renderProfit()` — editable profit rows with FBA estimation, 3 scenarios
6. `renderPpc()` — PPC keyword cards + economics table
7. `renderReviews()` — quality gate + pain chart + positive keepers + excerpts
8. `renderKpi()` — 8 KPI cards
9. `renderTrend()` — historical + forecast chart with dual sliders
10. `renderSeasonality()` — 51+12 month bars with seasonal coloring
11. `renderIntro()` — editable product intro fields
12. `renderStructure()` — 6 distribution tabs (lazy render), price band donut, brand charts, scatter
13. `renderParent()` — parent ASIN table + grouped line chart with brand toggles
14. `renderOpportunity()` — Kano scatter, consensus table, attribute matrix, combo table
15. `applyAccessibility()` — ARIA labels for canvas charts

**Boot sequence**:
```javascript
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
});
```

### Step 7: Assembly (`scripts/assemble.py`)

1. Load `consolidated.json` and `records_coupled.json`
2. Load `analysis.json`
3. Build `window.REPORT_DATA` object with all required keys
4. Read `_shell.html` and `app.js`
5. Inject: `shell + <script>window.REPORT_DATA = {...}</script> + <script>app.js</script> + </body></html>`
6. Escape `</script>` to `<\/script>` inside JSON and JS to prevent premature script termination
7. Write final `Makeup-Mirror-with-Lights_YYYYMMDD.html`

### Step 8: Validation Checklist

- [ ] `node --check app.js` passes
- [ ] All 11+ anchor IDs present in final HTML
- [ ] 15 `function render*` definitions present
- [ ] `window.REPORT_DATA` JSON parses correctly
- [ ] REPORT_DATA contains keys: `meta`, `kpi`, `records`, `price_bands`, `top_brands`, `dists`, `scatter`, `cat_trend`, `kw_core`, `csay`, `score_rows`, `score_total`, `score_100`, `decision`, `head`, `kano`, `att_rows`, `combo_rows`, `seasonal`, `fc`, `peak_months`, `yoy`, `pain_rows`, `pos_rows`, `parent_rows`, `ppc`
- [ ] Chart.js CDN loaded
- [ ] No `TODO`/`FIXME`/placeholder text remaining

## 本机环境适配（Windows 11 + PowerShell 5.1 实测，2026-09-22）

> 在 Windows 上跑这条管线有 4 个必踩的坑，照着做能省 1 小时。

1. **不要调 `sorftime.ps1`**。本机执行策略禁脚本，会报 `running scripts is disabled on this system`。
   直接走 node 调 CLI 入口：
   ```powershell
   $node = "C:\Users\HUAWEI\.workbuddy\binaries\node\versions\22.22.2-3\node.exe"
   $cli  = "D:\Nodejs\node_modules\sorftime-cli\dist\index.js"
   & $node $cli api <Endpoint> '<JSON>' --domain 1
   ```

2. **PowerShell 会吞掉参数里 JSON 的双引号**：`'{"name":"Glasses Case"}'` 传到 CLI 变成 `{name:Glasses Case}`，
   报 `参数格式错误，请输入有效的JSON/JSON5字符串`。
   对策：写一个 **`sf.js` 参数代理**——从 JSON 文件读 argv 数组，用 `spawnSync(NODE, [CLI, ...argv])` 传参，
   完全绕开 shell 的引号解析。批量拉数据时直接写成 `fetch_*.js` 脚本，别在 PowerShell 里拼命令。

3. **CLI 的 stdout 混着 2 行 banner，stderr 混着进度提示**（`- 正在调用API...` / `√ 调用成功`），
   且 PowerShell 的 `2>&1` 会把两者交错。可靠做法：**只取 stdout**，再从第一个 `{` 开始切。

4. **路径速查**：`jq` → `C:\Users\HUAWEI\.workbuddy\bin\jq.exe`；
   Python → `C:\Users\HUAWEI\.workbuddy\binaries\python\versions\3.13.12\python.exe`
   （★ 别用 WindowsApps 里的 `python.exe`，那是 Microsoft Store 的 stub，执行无输出）。
   报告生成后**必须**在浏览器里目检 + 跑 `scripts/validate.js`，别只看脚本没报错。

---

## 换品类适配清单（5 个改动点）

从模板迁移到新品类（以眼镜盒 Eyeglass Cases 为例），要改的就是这 5 处：

| # | 文件 | 改什么 |
|---|---|---|
| 1 | `consolidate.py` | ① 价格带 `band()` 按新品类分位重设（先跑 `dump_titles.js` 看 p10/p50/p90，别沿用旧品类的）② `MONTH_END` ③ `meta` 的 category/nodeId/keyword/scope ④ 关键词文件名 |
| 2 | `analysis.py` | ① `_coupling` 提取规则（新品类属性，从 Title + ProductInfo 正则提）② `ATTR_FIELDS` ③ `combo_fields` ④ `CN` 痛点中文映射 ⑤ 评分卡里的价格带区间与业务文案 |
| 3 | `app.js` | ① **`COUPLING_KEYS` 必须与 `_coupling` 的键完全一致**（否则表格列全空）② 硬编码品类文案：决策动作卡、benchmark 的「差异化机会」、`renderIntro` 的 4 段介绍 ③ 导出文件名 |
| 4 | `build_shell.py` | ① 路径（`ROOT` 改为项目根）② `STORAGE_KEY` + `<h1>` + 关键词中文 + subtitle ③ PPC 模块文案 |
| 5 | `assemble.py` | ① 路径 ② 输出文件名 |

**两条硬经验**：

- **`CN` 痛点映射别凭想象写。** 先拉 Top5 的 `ProductCustomersSay`，把所有 `Details[].Keyword` 按 `Negative` 排序打出来，
  照着**真实词表**补 `CN` dict。否则 `CN.get(kw)` 全走兜底分支，痛点表会退化成英文原词（眼镜盒实测：
  `fit / softness / protection / size / quality / portability / closure / zipper / durability / ease of use / value for money / material / suitability / functionality`）。
- **把「痛点什么建议」放在后端算**。原模板在 `app.js` 里内联了一份 `{痛点中文: 建议}` 映射，和 `analysis.py` 的 `CN` 表重复。
  改成品类后要维护两处，极易漏。正解：`analysis.py` 在 `pain_rows` 里直接输出 `advice` 字段，前端只读 `p.advice`。

---

## ⚠️ 品类放大后的两个渲染陷阱（2026-09-22 实测，会被误判成"视觉做烂了"）

模板是按 57 个产品设计的。样本放大到 100 个、属性列变多后，会出现**"页面大片空白"的假故障**：
打开报告后大片区域空白，看起来像 CSS 没加载或图表挂了。

实测排除过程（下次直接跳过）：CSS 完好（`:root` / `.kpi-card` 规则都在，无嵌套 `<style>`）、
Chart.js 4.4.7 内联正常、jsdom 下**运行时错误 0 个**、15 个 render 全部产出内容。
真正原因是下面两条，**都要修**：

### 1. 同步串行 boot 会冻结主线程

默认视图下产品表是 `行数 × (基础列 + 全部月份列)`：100 行 × 64 列 ≈ **250 万字符 DOM**。
一次性 `innerHTML` 插入期间浏览器无法重绘，用户看到的就是"半成品"页面。

对策（三件套一起做）：
- **首屏只渲染前 N 行**（本次用 40 行）+ 一个「显示全部」按钮 → DOM 立刻从 250 万降到 99 万字符
- **把 boot 的 15 个 render 改成 `setTimeout` 分片执行**，每步之间让出主线程，浏览器可逐步重绘
- 加一个 fixed 定位的「正在渲染报告… n/15」进度提示，渲染完成后移除

### 2. 没有异常隔离，一个模块挂掉会拖垮后面 7 个

原 boot 是一条平铺调用序列：`renderReviews()` 里的第一个 `new Chart()` 一旦抛错，
后面的 renderKpi / renderTrend / renderSeasonality / renderIntro / renderStructure /
renderParent / renderOpportunity **全部不执行** —— 表现出来就是"下半页全空"。

对策：每个 render 用 try/catch 包住，失败只记录 `console.error('[render:xx]', err)` 并**继续跑后续模块**。

### 3. UMD 包在宿主环境里会「静默消失」（最隐蔽，2026-09-22 实测定位）

**症状**：报告能打开、文字和表格都正常，**但所有图表空白**；页面底部诊断条报
`图表 xxx 渲染失败：Chart is not defined`，而控制台**没有**任何报错。

**根因**：Chart.js 是 UMD 包，加载器按 CommonJS → AMD → 浏览器全局 的优先级选分支：
```js
"object" == typeof exports && "undefined" != typeof module ? t(exports)
: "function" == typeof define && define.amd ? define([...], t)
: (global.Chart = factory());
```
宿主外壳（预览面板、桌面端容器、某些打包器/SDK）如果预置了 `define` / `module` / `exports`，
Chart.js 就走进前两个分支，**只写进那个局部对象，不挂 `window.Chart`**。

实测复现（`scripts/test-umd.js`，同一份 HTML 跑三个场景）：

| 宿主注入的全局 | `window.Chart` |
|---|---|
| 无 | ✅ function v4.4.7 |
| `define = function(){}; define.amd = {}` | ❌ **undefined** ← 本次故障原因 |
| `module = {exports:{}}; exports = ...` | ✅ function |

**对策**：内联 UMD 库时**前后各加一段守卫**，加载期间把这三个标识符临时藏起来，
强制它走浏览器全局分支：

```html
<script>(function(){window.__umdSaved={d:window.define,m:window.module,e:window.exports};
try{window.define=undefined;window.module=undefined;window.exports=undefined;}catch(err){}})();</script>
<script>/* 库源码 */</script>
<script>(function(){try{var s=window.__umdSaved||{};
if(s.d!==undefined)window.define=s.d;if(s.m!==undefined)window.module=s.m;
if(s.e!==undefined)window.exports=s.e;delete window.__umdSaved;}catch(err){}})();</script>
```

> **通用结论**：任何 UMD 库内联进报告，都要做这层守卫。
> 并且——**"本地 file:// 打开正常" ≠ "宿主里正常"**，两者全局环境不同，必须都验。
> 定位手法：先让页面把 `typeof window.Chart` 直接显示出来（诊断条），
> 再在 jsdom 里逐个注入 `define` / `module` 复现，比盯着控制台猜快得多。

**终极保险：加一条内置降级渲染通道**。与其赌宿主环境，不如让图表有兜底：

```js
function safeChart(id, config){
  try{
    if(typeof window.Chart !== 'function') throw new Error('Chart 库未加载');
    return new Chart(document.getElementById(id).getContext('2d'), config);
  }catch(err){
    var ok = false;
    try{ ok = svgFallbackChart(id, config); }catch(e2){}
    showDiag(...);   // 把降级/失败原因显示在页面上
    return null;
  }
}
```

`svgFallbackChart()` 只用原生 DOM 画水平条形图（读 `config.data.labels` + 第一个有值的 dataset），
不依赖任何库。散点图这类没有 labels 的配置，渲染一条说明而不是留空 canvas。

本次实测：把内联的 Chart.js **整块删掉**后，9 个图表区块全部降级成功、257 条条形正常渲染，
所有数据表格完全不受影响 —— 也就是**最坏情况下报告依然可读**。

另外 `safeChart` 返回 `null` 之后，任何 `chart.options.xxx` / `chart.update()` 都要加判空，
否则会抛 `Cannot read properties of null`（本次踩到，症状是趋势图的滑块一初始化就报错）。

### 其他加固

- **改完必须换输出文件名**：WorkBuddy 预览面板对同一个 URL 可能不重新加载，
  结果是"修复已生效、用户看到的却一直是旧版"（本次因此白跑两轮排查）。
  `assemble.py` 用 `REPORT_BUILD` 环境变量给文件名加构建号（如 `..._v3.html`），
  URL 一变预览必然重新加载。判断用户看的是新版还是旧版，可以看诊断条格式有无变化。
- **Chart.js 在容器首次布局尺寸为 0 时会算出 0×0 画布**（图表空白且不报错）。
  boot 结束后 `setTimeout(350ms)` 遍历 `Chart.getChart(el).resize()` + `update('none')` 强制重算。
- **必须内联 Chart.js**：`assemble.py` 先从 CDN 抓一份 `chart.umd.min.js` 存到项目根，
  再把 `<script src="...cdn...">` 整段替换成内联。报告常要发给客户，走 CDN 一旦对方网络受限就是满屏空白。

> 排查这类"假故障"的可用工具（已沉淀在 `eyeglass-case-report/scripts/`）：
> `validate.js`（结构校验）、`checkfields.js`（前端引用字段 vs 数据源契约）、
> `test-render.js`（jsdom + Chart stub，测非 canvas 逻辑）、
> `test-chart-real.js`（jsdom + 真 Chart.js + mock 2D context，测图表初始化是否抛错）。
> 注意：`msedge --headless --dump-dom` 在本机被沙箱拦（GUI 可执行文件），别浪费时间。

---

## Known Pitfalls

1. **template.css nesting**: Extracted CSS may still contain `<style>` open/close tags from the template. Strip them before injection or the entire stylesheet fails to parse and the page renders as unstyled white background.
2. **macOS grep**: BSD grep doesn't support `\|` alternation without `-E`. Always use `grep -E` for alternation patterns.
3. **Sorftime trend arrays**: `ListingSalesVolumeOfMonthTrend` etc. are daily rolling 30-day values, not true monthly aggregates. Monthly values must be extracted by taking the value on the last day of each month.
4. **Photo field type**: Can be string or array. Always normalize: `photo = photo[0] if isinstance(photo, list) else photo`
5. **Hidden tab canvases**: Chart.js canvases inside hidden tabs have 0×0 dimensions. This is normal — rebuild charts when tab is activated (`switchDistributionTab`).
6. **JSON escaping**: When injecting REPORT_DATA into HTML, escape `</script>` sequences to `<\/script>` to prevent the browser from closing the script tag early.
7. **ProductRequest batch size**: Maximum 10 ASINs per call. Split large ASIN lists into batches.
8. **CLI banner**: Sorftime CLI outputs a 2-line banner before JSON. Always use `tail -n +3` before piping to `jq`.

9. **`ProductRequest` 参数名是 `asin`（逗号分隔），不是 `asinList`**。写错直接报 `Code 10 Invalid request parameter`。
   趋势跨度超过 15 天必须显式给 `queryTrendStartDt`（如 `2022-06-01`），否则只回 15 天数据。

10. **服务端会偶发限流，而且返回的 `Code` 仍然是 0**：
    `{"Code":0,"Message":"Success","Data":null,"RequestLeft":0}`。
    必须靠 **`Data === null`** 判定失败，不能只看 Code。实测批量拉 100 个 ASIN（10 批）时约有 5 批首次失败，
    间隔 4s 重试即可全部成功。**务必加重试 + 批次间 1.5s 节流**，否则会误判为"没数据"。

11. **各 endpoint 的 `Data` 结构不统一**，解析时必须兼容：

    | Endpoint | `Data` 形态 |
    |---|---|
    | `CategoryRequest` | `{ Products: [...] }` |
    | `ProductRequest`（单 ASIN） | 对象 |
    | `ProductRequest`（多 ASIN） | 数组 |
    | `KeywordRequest` | 对象 |
    | `KeywordQuery` / `KeywordExtends` / `CategoryRequestKeyword` | 数组 |
    | `CategoryTrend` | `[月份, 值, 月份, 值, ...]` 扁平数组 |
    | `ProductCustomersSay` | `{ CustomerSay: str, Details: [...] }` |

12. **`CategoryTrend` 每个 `TrendIndex` 都要单独花 5 credits**（销量=0 / 均价=3 / 品牌数=1 / 卖家数=2 /
    3个月新品占比=7 / 自营占比=9 / 平均利润=12 / Top3 品牌垄断=32 …）。基础报告只需 0 和 3。

## File Structure (Example Project)

```
makeup-mirror-report/
├── template.css              # Extracted from template
├── _shell.html               # Generated by build_shell.py
├── app.js                    # Application logic
├── assemble.py               # Final assembly script
├── build_shell.py            # Shell generation script
├── data/
│   ├── consolidate.py        # Data consolidation
│   ├── analysis.py           # Analytics computation
│   ├── consolidated.json     # Merged raw data
│   ├── records_coupled.json  # Records with coupling fields
│   ├── analysis.json         # Computed analytics
│   ├── products.json         # Top100 from CategoryRequest
│   ├── prod_0.json ...       # Batch ProductRequest results
│   ├── trend_sales.json      # Category sales trend
│   ├── trend_price.json      # Category price trend
│   ├── kw_main.json          # Core keyword data
│   ├── kw_ext.json           # Extended keywords
│   └── csay_*.json           # CustomersSay per ASIN
└── Makeup-Mirror-with-Lights_20260901.html  # Final deliverable
```

## Customization Notes

- **Category-specific coupling fields**: Update `COUPLING_KEYS` and extraction regex in both `analysis.py` and `app.js` to match the new category's relevant attributes.
- **Scorecard weights**: Adjust in `analysis.py` based on category characteristics.
- **FBA fee estimation**: Update `STD_WT` tiers in `app.js` if Amazon changes fee structure.
- **Theme**: The default template is dark theme. Use `retheme.py` (color replacement map) to convert to light blue business style if needed.
