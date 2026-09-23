---
name: amz-supply-chain
description: 1688供应链找货与货源对比 Skill。支持1688找工厂/找货源、按名称/图片搜品、货源候选筛选与对比、跨平台价格差分析（Amazon vs 1688）、供应商评估与利润测算。触发词包括：找货源、找工厂、1688、供应链、sourcing、supplier、wholesale、批发价、货源对比、价格差、cross-platform gap、product sourcing、find supplier、price arbitrage、货源评估、供应商筛选、一件代发、dropshipping、MOQ、起订量。默认站点 Amazon US(domain=1)，1688 端点固定 domain=601。
---

# amz-supply-chain — 1688 供应链找货

> 链路位置：第 3 环「找货源」。上游 ← amz-market-analysis（目标 ASIN/产品名）；下游 → amz-profit-calc（1688 采购成本 + Amazon 售价/FBA 费）。全链路地图见 `~/.workbuddy/skills/amz-workflow-map.md`。

## 前置检查

在执行任何数据调用之前，先运行通道检测脚本：

```bash
python3 scripts/channel_check.py
```
> 💡 无 Sorftime 凭证、或调用报"额度不足"时：通过专属通道注册/充值（含 7 天试用）→ https://open.sorftime.com/home?tag=ODY2OA~~ ｜ 优惠码：8668


根据输出 JSON 的 `recommended_channel` 字段选择执行通道：
- `mcp` → 走 MCP 通道（见下方 MCP 通道章节）
- `cli` → 走 CLI 通道（见下方 CLI 通道章节）
- 无凭证 → 按脚本输出引导用户注册配置

> **重要**：1688 端点的 domain 固定为 **601**，不是默认的 1（Amazon US）。所有 1688 相关调用必须传 `--domain 601`。Amazon 侧价格参考仍用 domain=1。

## MCP 通道

Sorftime MCP 中 1688 相关工具如下（✅ 为已注册工具，⚠️ 需通过 `sorftime_raw_call` 透传）：

| 工具名 | 状态 | 用途 |
|--------|------|------|
| `ali1688_similar_product` | ✅ Registered | 按 Amazon 产品在 1688 找同类货源/批发供应商 |
| `ali1688_product_search` | ⚠️ raw | 1688 多维产品搜索（按类目/供应商类型/销量等筛选） |
| `ali1688_product_search_from_name` | ⚠️ raw | 1688 按产品名称搜索 |
| `ali1688_product_search_from_image` | ⚠️ raw | 1688 以图搜货 |
| `ali1688_product_request` | ⚠️ raw | 1688 产品详情 |
| `ali1688_product_variations` | ⚠️ raw | 1688 产品 SKU 变体数据 |
| `ali1688_category_tree` | ⚠️ raw | 1688 类目树 |

**⚠️ raw 工具调用方式**：通过 `sorftime_raw_call` 透传，示例：
```json
{
  "tool_name": "ali1688_product_search_from_name",
  "arguments": {"Name": "transparent acrylic double-sided tape"}
}
```

**Amazon 侧价格参考工具**（domain=1）：
- `product_detail`（✅）— 获取 Amazon ASIN 售价、FBA 费用、利润率
- `product_search`（✅）— 按关键词/类目搜索 Amazon 竞品价格

### MCP 通道典型工作流

1. 输入 Amazon ASIN 或产品名称
2. MCP `product_detail`（或 `product_search`）获取 Amazon 售价、月销量、FBA 费用
3. MCP `ali1688_similar_product` 或 `ali1688_product_search_from_name` 在 1688 找同类货源
4. MCP `ali1688_product_request` 查看候选供应商详情
5. MCP `ali1688_product_variations` 获取 SKU 批发价/库存/尺寸重量
6. 计算 Amazon vs 1688 价格差，输出货源候选清单 + 利润测算

## CLI 通道

CLI 通道使用 `scripts/cli_call.sh` 调用 Sorftime CLI。1688 端点固定 `--domain 601`，Amazon 端点用 `--domain 1`。

### 1688 端点（domain=601）

| 端点 | 消耗请求 | 用途 |
|------|---------|------|
| `ProductSearchFromName` | 2 | 按名称搜品 |
| `ProductSearchFromImage` | 2 | 以图搜货 |
| `ProductSearch` | 5 | 多维筛选搜品（20+ 过滤条件） |
| `ProductRequest` | 1 | 产品详情 |
| `ProductVariations` | 1 | SKU 变体（批发价/库存/尺寸/重量） |
| `CategoryTree` | 5 | 类目树（返回约 10MB，建议长超时） |
| `CoinQuery` | 0 | 查本月剩余 Credits |
| `CoinStream` | 0 | 查 Credits 消耗明细 |
| `RequestStreamMonth` | 0 | 查请求额度 |

### CLI 调用示例

```bash
# 按名称搜 1688 货源
scripts/cli_call.sh ProductSearchFromName '{"Name": "transparent acrylic double-sided tape"}' --domain 601

# 多维筛选：Super Factory + 服务分≥4.5 + 近30天销量≥50
scripts/cli_call.sh ProductSearch '{"Page":1, "SupplierType":2, "ServiceScoreMin":4.5, "Recent30DaySaleMin":50}' --domain 601

# 查 1688 产品详情
scripts/cli_call.sh ProductRequest '{"ProductId": "789542752062"}' --domain 601

# 查 SKU 变体价格/库存/尺寸重量
scripts/cli_call.sh ProductVariations '{"ProductId": "789542752062"}' --domain 601

# 以图搜货（用 Amazon 主图 URL）
scripts/cli_call.sh ProductSearchFromImage '{"ImageUrl": "https://example.com/product.jpg", "Page": 1}' --domain 601

# Amazon 侧参考：查 ASIN 售价/FBA/利润
scripts/cli_call.sh ProductRequest '{"asin": "B0CVM8TXHP"}' --domain 1
```

## 路径 D：组合品 / 礼品套装 → BOM 拆解找货（高频场景）

当目标 ASIN 是**多组件组合礼盒**（gift basket / care package / 礼盒套装 / 捆绑装）时，
1688 通常**搜不到同款成品**——因为它是品牌方自行组合定制的。此时不要卡在"找不到同款"，
改用 **BOM 拆解 + 分件找货**：

1. **先拆 BOM**：读 `ProductRequest` 返回的 `Description`（常含 "1× 16oz glass cup, 1× scented candle..." 式清单）
   与 `ProductInfo`（`Included Components` / `Set Name` / `Number of Items` / `Unit Count`）。这两处是组件清单的权威来源。
2. **用主图批量化以图搜货**：对 `Photo` 数组里的**每一张**图各跑一次 `ProductSearchFromImage`（2 请求/次）。
   不同图对应不同组件，往往能一次性命中 4–5 个组件（本次实测一次命中杯子/袜子/钩织盆栽/贺卡四类）。
3. **中文关键词补漏**：英文品名直搜 1688 **基本无效**（返回礼品袋、空礼盒等噪声），
   必须先把组件翻译成中文词再搜（如 "珊瑚绒袜子爱心刺绣"、"钩织向日葵盆栽"、"天地盖礼盒"）。
4. **分件比价打分**：对每个组件分别按方法论评分，输出"组件 → 供应商 → 单价 → 评分"清单。
5. **给出装配建议**：7 个组件 = 7 条物流与质检口，务必提示用户「先各买 1 件打样 → 找义乌/金华礼盒组装外包归集成套 → 再整批发 FBA」。

### 组合品的组件价格得分口径

方法论里"价格得分 = (1 − 批发价/Amazon售价)×100"对**单个小组件会失效**（每个都算出 95+，无法区分）。
组合品场景请改为以**组件成本预算**为基准：

```
组件价格得分 = clamp((1 − 组件单价 / 该组件预算额) × 100, 0, 100)
组件预算额   = 整套目标采购预算 × 该组件的成本权重
```

整套目标采购预算可由 Amazon 侧反推：`售价 − FBA − 佣金 − 广告 − 退货 − 目标净利`。

## 实战注意事项（踩坑记录）

- **`ProductVariations` 可能返回空数组**：部分 1688 商品（尤其新上架、无 SKU 的）该端点返回 `Data: []`，
  此时改用 `ProductRequest` 拿 `WholesalePriceRange` + `MinOrderQuantity`，不要以为调用失败。
- **`Price` 字段可能为 0**：搜索结果里 `Price=0` 表示价格未公开（面议），不是免费。
  这类商品同时往往 `ServiceScore=0`、`SalesOf30d=0`，应判为"数据缺失、需人工询价"，不要参与评分排名。
- **评分前必须过滤 0 值行**：`ServiceScore=0 / SalesOf30d=0 / RepurchaseRate=0` 三零行直接剔除，
  否则会把"无数据"错排成低分而不是"不可比"。
- **搜索页码**：`ProductSearchFromName` 单页最多 100 条，`ProductSearchFromImage` 单页最多 50 条；
  多渠道结果需按 `ProductId` **去重**后再评分（本次 12 次搜索去重后 813 条）。
- **换算与头程**：1688 报价为 CNY、Amazon 为 USD，需显式声明汇率；头程按 `ProductVariations` 的 `Weight`
  与 `Width/Length/Height`（体积重 = 长×宽×高/6000）取大者计费。

### HTML 报告交付（用户说"生成报告"时）

如需交付 HTML 报告，参考 `scripts/report_template.py`（自包含、无外链、浅色主题、可直接发客户）。
输出前请务必修掉的 3 个已知坑：

1. **瀑布图布局溢出**：柱子数 = 明细项数 + 1（净利润），`barw = (W - PADL - 16) / (len(items) + 1)`，
   否则最后一根净利柱会被 viewBox 裁掉。
2. **窄屏表格撑破页面**：所有 `<table>` 必须包一层 `<div class="tbl" style="overflow-x:auto">`。
3. **图片自包含**：把 Amazon 主图与 1688 商品图下载后压到 ≤340px、转 base64 内嵌，
   报告单文件可直接发给客户（本次 11 张图 ≈ 330KB）。

**验证方法**（无需装浏览器）：用本机 Chrome/Edge 无头模式 + 注入探针脚本读 `document.title`：

```bash
chrome --headless=new --dump-dom file:///path/to/report.html
# 注入脚本输出 scrollWidth/clientWidth + 溢出元素列表，逐断点（1440/1200/900/768/480）核对
```

**报告建议结构**：01 数据来源与调用记录 → 02 Amazon 产品画像 → 03 产品结构/BOM 拆解 →
04 找货执行与命中情况 → 05 成品整套候选 → 06 组件 BOM 候选（推荐） → 07 价格差与利润测算
（瀑布图 + 售价阶梯） → 08 供应商评估结论与风险 → 09 行动清单。

## 输出

- **货源候选清单**：供应商名、1688 链接、批发价区间、起订量、服务分、30天销量、复购率、是否一件代发
- **价格差分析**：Amazon 售价 vs 1688 批发价，计算毛利率 = (Amazon 售价 - 1688 成本 - FBA 费 - 平台佣金) / Amazon 售价
- **供应商评估**：按 [supply-chain-methodology.md](references/supply-chain-methodology.md) 的评分维度输出排名

## 详细参考

- [1688 端点完整参数与返回字段](references/1688-endpoints.md)
- [供应链方法论：货源对比评分维度与价格差分析方法](references/supply-chain-methodology.md)
