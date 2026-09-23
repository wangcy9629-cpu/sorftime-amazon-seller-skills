---
name: amz-profit-calc
description: Sorftime 亚马逊利润测算 / 隐赚分析。当用户要算利润、算 FBA 费用、算盈亏平衡点、做定价策略、判断隐赚指数/HPI、找轻量小而美高利润品、测算单均毛利净利、评估某 ASIN 能不能赚钱，或说"利润测算/利润计算/FBA费用/佣金/盈亏平衡/保本销量/隐赚/隐赚指数/HPI/轻量利润/小而美/定价/毛利/净利/利润表/profit calculation/FBA fee/break-even/invisible profit/HPI/lightweight profit/pricing strategy/margin"时使用。融合隐赚指数、轻量利润、定价位置方法论，用 ProductRequest 取真实价格/排名/费用数据，输出利润测算表（成本/费用/毛利/净利/盈亏平衡销量/隐赚评分）。默认 Amazon US，支持多站点。
---

# amz-profit-calc — 利润测算 / 隐赚

给一个 ASIN（或一组假设成本/售价）算出真实利润账：FBA 费用、平台佣金、广告、退货侵蚀、盈亏平衡销量、隐赚评分。

> 链路位置：第 4 环「利润测算」。上游 ← amz-supply-chain（采购成本）；下游 → amz-cpc-keywords（go 后建词库）。全链路地图见 `~/.workbuddy/skills/amz-workflow-map.md`。

## 前置检查

开始前先运行：

```bash
python3 scripts/channel_check.py
```
> 💡 无 Sorftime 凭证、或调用报"额度不足"时：通过专属通道注册/充值（含 7 天试用）→ https://open.sorftime.com/home?tag=ODY2OA~~ ｜ 优惠码：8668


按 `recommended_channel` 选 MCP 或 CLI 通道。默认 site=US（domain=1）。

## 典型流程

1. **取真实数据**（MCP `product_detail` 或 CLI `ProductRequest`）：售价 SalesPrice、FbaFee、PlatformFee、Profit、ProfitRate、Weight、月销 AsinSalesVolume
2. **补假设成本**：采购成本（含头程）问用户，或用 1688 价估算
3. **跑测算**：`scripts/profit_calculator.py`（或在线 P&L）
4. **出利润表 + 隐赚评分 + 盈亏平衡 + go/no-go**

公式见 [references/profit-formula.md](references/profit-formula.md)。

---

## MCP 通道

- `product_detail` — 取 SalesPrice / FbaFee / FbaDetetail / PlatformFee / Profit / ProfitRate / RatingsCount / Weight / Size / OnlineDate
- `product_trend` — 取 6 个月销量/价格趋势（判断盈利可持续性）
- `product_variations` — 变体矩阵（算套装/多件变体利润）

---

## CLI 通道

端点文档见 [references/endpoints-reference.md](references/endpoints-reference.md)。

```bash
# 1. 取单品真实价格/FBA费/佣金/利润（最关键一步）
scripts/cli_call.sh ProductRequest '{"asin": "B0CVM8TXHP"}'

# 2. 取官方披露的变体销量历史（算月销）
scripts/cli_call.sh AsinSalesVolume '{"asin": "B0CVM8TXHP"}'

# 3. 取全部变体（套装/多件 SKU 利润）
scripts/cli_call.sh ProductVariations '{"asin": "B0CVM8TXHP"}'
```

拿到 SalesPrice / FbaFee / 月销后，喂给本地测算脚本：

```bash
# 用真实拉到的 FBA 费覆盖估算
python3 scripts/profit_calculator.py \
  --price 24.99 --cost 6.5 --weight 0.35 \
  --fba-fee 4.75 --monthly-sales 800 --return-rate 0.05

# 只看公式样例
python3 scripts/profit_calculator.py --json
```

非 US 站点加 `--domain <N>`。

---

## 输出规范

利润测算表必须包含：

| 项目 | 来源 |
|---|---|
| 售价 / 采购成本 | 用户输入 或 ProductRequest.SalesPrice |
| FBA 配送费 | ProductRequest.FbaFee（优先）/ 估算 |
| 平台佣金(Referral) | ProductRequest.PlatformFee |
| 广告成本(估 ~15%) | 假设，标注 |
| 单均毛利 / 毛利率 | 计算 |
| 退货后单均净利 | 按退货率敏感性 |
| 盈亏平衡销量 | 按月固定成本 |
| 月净利 | 月销 × 单均净利 − 固定成本 |
| 隐赚评分 | 本地代理分（官方 HPI 走 MCP potential_product） |
| go / caution / no-go | 综合净利 + 退货敏感性 |

⚠️ 所有利润数字是**估算**；FBA 费必须以官方 Revenue Calculator 复核（尤其大件/异形）；广告占比、退货率按类目假设，须显式标注 `[ASSUMED]`。
