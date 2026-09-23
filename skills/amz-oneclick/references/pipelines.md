# 流水线定义与环间交接（amz-oneclick）

> 每个 `<run-id>` = `_work/amz-oneclick/<YYYYMMDD-HHMM>-<slug>/`，所有中间产物落盘于此。
> 环间传参**只认落盘文件**，不靠对话记忆。

---

## P1 类目可行性（评估要不要进）

**触发**："一键跑类目可行性：<品类名>" / "这个类目能不能做，走一遍"

| 序 | 子 skill | 输入 | 产出文件 | 关键字段 |
|---|---|---|---|---|
| 1 | amz-market-analysis | 品类名 / nodeId、站点（默认 US） | `step01-market.json` + `step01-market.html` | 11 维评分、市场容量、价格带甜区、品牌集中度、进入建议 |
| 2 | amz-supply-chain | step01 的目标产品定义 + 价格带甜区 | `step02-sourcing.json` | 1688 候选货源、批发价(¥)、MOQ、供应商评分、跨平台价差 |
| 3 | amz-profit-calc | step02 批发价 + Amazon 售价/FbaFee/PlatformFee | `step03-profit.json` | 单均毛利、净利、毛利率、盈亏平衡销量、隐赚分 |

**终局产出**：`report.html`（顶部结论：**进 / 不进 / 有条件进**＋理由＋价格带建议）
**预估消耗**：~60-95 请求（②占大头）

---

## P2 竞品击破（已有竞品清单）

**触发**："一键击破这批竞品：<ASIN×8-12>" / "VOC + 广告一起做"

| 序 | 子 skill | 输入 | 产出文件 | 关键字段 |
|---|---|---|---|---|
| 1 | multi-asin-voc-analysis | 品类名 + 8-12 个竞品 ASIN、站点 | `step01-voc.json` + `step01-voc-dashboard.html` | ASIN 分层、主题×ASIN 根因矩阵、能力竞争矩阵、正负面翻转、JTBD 机会、击破窗口+触发阈值 |
| 2 | amz-ad-planning | step01 的 Top 痛点词 + 弱位卖点 + 竞品核心词 | `step02-ad.json` | 活动结构、预算分配、出价策略、否定词清单、SP/SB/SD 组合 |
| 3（可选） | amz-listing-creator | step01 的痛点/卖点/场景 | `step03-listing.json` | 标题（7.27 新规）、五点、后台词 |

**终局产出**：`report.html`（顶部：**打哪里 / 凭什么 / 怎么验证** 三段结论）
**预估消耗**：VOC 5-15 Credits + 广告 ~10 请求（+ Listing ~10-20）

**交接要点**：VOC 的「弱位 × 近期恶化」结论 = 广告的**主打卖点方向**；VOC 的差评高频词 = 广告**否定词初稿**（需人工确认，别直接上线）。

---

## P3 新品启动（已决定要上）

**触发**："一键新品启动：<品类名 或 目标 ASIN>"

| 序 | 子 skill | 输入 | 产出文件 | 关键字段 |
|---|---|---|---|---|
| 1 | amz-market-analysis | 品类名 / nodeId | `step01-market.json` | 价格带甜区、竞争强度、进入策略 |
| 2 | amz-supply-chain | 目标产品 + 价格带 | `step02-sourcing.json` | 货源、批发价、价差 |
| 3 | amz-ad-planning | step01 关键词方向 + step02 定价 | `step03-ad.json` | 冷启动活动结构、预算分配、出价 |

**终局产出**：`report.html`（顶部：**定价建议 + 冷启动广告方案 + 时间线**）
**预估消耗**：~70-110 请求

---

## P4 守盘（自有店铺例行巡检）

**触发**："一键守盘" / "一键守盘周报" / "一键守盘月报"

| 序 | 子 skill | 输入 | 产出文件 |
|---|---|---|---|
| 1 | sorftime-shop-health-monitor | 自有核心 ASIN、主营类目 nodeId、品牌关键词、预警阈值 | `step01-health.json` + `health-report.html` |

**注意**：
- 首次使用需先确认 §配置参数（核心 ASIN / nodeId / 品牌词 / 阈值）——缺就一次性问全。
- 哨兵类端点消耗 Credits（月度清零），**注册监控任务前先算周成本**并报给用户。
**预估消耗**：按任务计（关键词监控 504 Credits/周/词；跟卖 2 Credits/次/ASIN）

---

## P5 全链路（最重，必须二次确认）

**触发**："一键全流程：<品类名>" —— ⚠️ **跑前必须跟用户确认**（消耗最大、耗时长）

执行顺序：`P1（市场→找货→利润）` → 如判定「进」→ `P3（广告）` 或 `P2（若有竞品 ASIN）` → `P4（守盘，仅当用户有自有店铺）`

- 中途若 P1 结论为「不进」→ **停下**，把理由给用户，不继续消耗。
- 终局产出：`report.html` + 每个环节独立文件，顶部给「下一步动作清单」。

---

## 通用交接字段词汇表（跨环统一口径）

| 字段 | 含义 | 出现环 |
|---|---|---|
| `nodeId` | Amazon 类目节点 ID | ① ② ④ |
| `targetAsin` | 目标/标杆 ASIN | ② ③ ④ ⑥ ⑧ |
| `priceBand` | 价格带甜区（USD） | ② ③ |
| `wholesalePrice` | 1688 批发价（¥，最小货币单位） | ③ ④ |
| `salesPrice` / `fbaFee` / `platformFee` | Amazon 侧价格与费用（最小货币单位） | ④ |
| `grossMargin` | 毛利率 | ④ ⑤ |
| `keywords[]` | 词库（含 SearchVolume / CPC 区间 / 竞争度） | ⑤ ⑥ ⑧ |
| `painPoints[]` | 差评高频痛点 | ⑨ ⑥ ⑧ |
| `diffGap` | 差异缺口（弱位 × 近期恶化） | VOC ⑧ |

> 金额与 CPC 字段均为**最小货币单位**（1999 = $19.99）。
