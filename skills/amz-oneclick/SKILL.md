---
name: amz-oneclick
description: 亚马逊全链路 Skill 总控台（一键调用入口）。把 amz-market-analysis（市场分析）、amz-supply-chain（1688 找货源）、multi-asin-voc-analysis（多 ASIN VOC 竞品击破）、amz-ad-planning（广告规划）、sorftime-shop-health-monitor（店铺健康监控）等 skill 收进一个入口：用户只要说"一键 XX"、"总控台"、"跑全流程"、"开始跑市场分析/找货源/VOC/广告/守盘"、"该用哪个 skill"、"帮我把这几个 skill 串起来"，本 skill 负责先做环境体检，再自动路由到对应子 skill 并按其 SKILL.md 严格执行；多环节任务按预设流水线串联，环间自动传递数据、统一输出中文 HTML 报告。触发词：一键、总控、总控台、跑全流程、全链路、一条龙、串起来、帮我调度、amz hub、one click、以哪个skill开始、不知道该用哪个技能。当用户点名了具体子 skill（如"做市场分析"）也可直接由子 skill 命中；本 skill 的价值在于"一次调用解决路由 + 串联 + 交付"。
agent_created: true
---

# amz-oneclick — 亚马逊全链路总控台

**一句话定位**：把 10+ 个 amz-* skill 变成一个入口。用户不再需要记住该用哪个技能、该按什么顺序跑、数据怎么往下传。

> 全链路地图见 `~/.workbuddy/skills/amz-workflow-map.md`；本 skill 是它的可执行前端。

---

## 0. 铁律（违反即返工）

1. **不要凭记忆复述子 skill 的内容** —— 必须用 Skill 工具实际加载目标子 skill，严格按其 `SKILL.md` / `references/` 执行。
2. **不编数据**。子 skill 拿不到数据时如实说明并给替代方案，禁止估算冒充实测。
3. **参数一次问全**。缺关键参数（品类名 / ASIN / 站点 / 自有店铺 ASIN）时，最多问 **1 轮**，用一条消息把缺的全列出来，不要连环追问。
4. **默认值先兜底**：站点默认 Amazon US（`--domain 1`）；1688 固定 `--domain 601`；报告语言中文。
5. **跑前报预算、跑后报消耗**。多环节流水线开始前用一句话说明预估请求数（参考本文件 §4 成本表）。
6. **交付规范**：单文件 HTML + 内联样式 + 中文 + 可跳转链接；文件落在当前工作区 `_work/amz-oneclick/<run-id>/`。

---

## 1. 启动动作（每次必做，1 次调用）

```bash
python3 ~/.workbuddy/skills/amz-oneclick/scripts/hub_check.py
```

输出 JSON 三件事：
- `skills_ok`：约定的子 skill 是否都在本机技能目录（缺哪个会列出来）
- `channel`：Sorftime 通道（mcp / cli）+ 是否可用
- `next`：建议动作

**若通道不可用** → 直接把注册引导给用户（含 7 天试用）：https://www.sorftime.com?tag=ODI4OA%7E%7E ｜ 优惠码：8288
（可扫码的注册图：`amz-oneclick/assets/sorftime-register-qr.jpg`，用 present_files 呈现给用户）

### 图形工作台（可选，用户说"打开工作台 / 工作台"时）

```bash
python3 ~/.workbuddy/skills/amz-oneclick/workbench/server.py --port 8787 --workdir "<当前工作区>" --open
```

零依赖本地服务（Python 标准库），页面能力：技能矩阵状态灯 + 流水线/单环节选择 + 参数表单 → 一键生成中文指令 + **派发到待办队列** + 历史跑批浏览。
Windows 也可直接双击 `workbench\start.bat`。启动后用 present_files 把 `http://127.0.0.1:8787/` 呈现给用户。

---

## 2. 路由表（核心 5 个 = 用户常用；扩展档补齐全链路）

### 核心 5（总控台优先支持）

| 一键口令 | 子 skill | 它干什么 | 最少输入 |
|---|---|---|---|
| `一键市场` / 这品类能不能做 | **amz-market-analysis** | 11 维评分判断类目值不值得进、价格带甜区、品牌垄断 | 品类名 / 类目 nodeId |
| `一键找货` / 1688 找同款 | **amz-supply-chain** | 1688 找工厂、货源对比、Amazon↔1688 价差 | 产品名 或 目标 ASIN |
| `一键VOC` / 竞品评论击破 | **multi-asin-voc-analysis** | 8-12 个竞品 ASIN 评论深挖，出 ASIN-first 击破作战包 | 品类名 + ASIN 清单 |
| `一键广告` | **amz-ad-planning** | 纯数据驱动广告结构 / 预算 / 出价 / 否定词 | 目标 ASIN 或 关键词表 |
| `一键守盘` / 店铺体检 | **sorftime-shop-health-monitor** | 自有店铺六维健康度：日扫 / 周策 / 月诊 | 自有核心 ASIN + 类目 nodeId |

### 扩展档（按同一口令风格可直接路由）

| 口令 | 子 skill | 干什么 |
|---|---|---|
| `一键选品` | amz-selection | 6 大选品指数全排序，≥20 候选 + go/no-go |
| `一键算利润` | amz-profit-calc | 单均 P&L / 盈亏平衡 / 隐赚代理分 |
| `一键词库` | amz-cpc-keywords | 4 分类打标词库（核心/长尾/场景/痛点） |
| `一键Listing` | amz-listing-creator | 两段式标题（7.27 新规）+ 五点 + 后台词 |
| `一键做图` | amz-image-creator | 数据驱动卖点可视化，走 gpt-image2 渲染 |
| `一键单ASIN评论` | amz-voc-analysis | 单 ASIN 评论痛点 / 卖点 / 场景提取 |
| `一键盯盘` | amz-competitor-monitor | 关键词排名 / 榜单 / 跟卖监控 + 盯盘日报 |

**路由决策顺序**：用户明确点名子 skill → 直接路由；用户只给目标（如"这个品能不能做"）→ 按语义就近匹配核心 5；跨环节需求 → 走 §3 流水线。

---

## 3. 预设流水线（"一条命令跑一串"）

详细定义、交接字段、产出清单见 **`references/pipelines.md`**。速查：

| 流水线 | 口令示例 | 环节序列 | 适用 |
|---|---|---|---|
| **P1 类目可行性** | "一键跑类目可行性：XXX" | 市场分析 → 找货源 → 算利润 | 手上有品类名，评估要不要进 |
| **P2 竞品击破** | "一键击破这批竞品" | 多ASIN VOC → 广告规划（+Listing） | 有 8-12 个竞品 ASIN |
| **P3 新品启动** | "一键新品启动：XXX" | 市场分析 → 找货源 → 广告规划 | 确定要上，出启动方案 |
| **P4 守盘周报** | "一键守盘周报" | 店铺监控（周策略） | 自有店铺例行巡检 |
| **P5 全链路** | "一键全流程：XXX" | P1 + P2 + P4 合并 | 完整跑一遍（消耗最大，先确认） |

**串联执行协议**：
1. 建工作目录 `_work/amz-oneclick/<YYYYMMDD-HHMM>-<slug>/`
2. 每环开始前：`Skill(skill="<子skill名>")` 加载 → 按其 SKILL.md 执行 → 中间产物（JSON/表格）落盘到该目录
3. 环间数据按 `references/pipelines.md` 的交接字段传，**不靠对话记忆传参**
4. 每环结束向用户报一行进度：`② 市场分析 ✅ → 目标类目 nodeId=xxx / 甜区 $19.99-29.99`
5. 全部结束后出**一份合并 HTML 总报告**（各环节折叠分区 + 顶部结论摘要），并对 P5 额外给「下一步建议」

### 待办队列执行协议（工作台 → Agent 的桥）

用户在工作台里点「派发到待办队列」后说「**执行待办**」时：

1. 读 `<workdir>/_work/amz-oneclick/_queue/*.json`，按 `created` 升序取 `status == "pending"` 的任务
2. 每条任务用其 `instruction` 字段走 §2 路由 → §3 串联协议执行
3. 执行完把该 JSON 的 `status` 改成 `"done"` 并补 `finished` 时间戳（原地改文件，不删）
4. 全部跑完汇总回复：`✅ 已执行 N 条待办` + 每条一行结果 + 报告路径
5. 队列里有缺参数的任务 → 一次性问全后再跑，不要跳过后继续

---

## 4. 消耗参考（CLI 通道实测，跑前一句话报给用户）

| 环节 | 一次完整跑动 | 备注 |
|---|---|---|
| ① 选品 | ~15-30 请求 | 搜品 2 页 + 详情批量 |
| ② 市场分析 | ~53 积分 | 含 6 维趋势 |
| ③ 找货源 | ~5-10 请求 | 1688 搜品 2 + 详情 1 + 变体 1 |
| ④ 利润测算 | 2-3 请求 | 本地脚本零消耗 |
| ⑤ 词库 | ~50-100 请求 | 拓展 ×多页 + 反查 |
| ⑥ Listing | ~10-20 请求 | 关键词详情 + 反查 |
| ⑦ 做图 | 2-3 请求 + 生图额度 | — |
| ⑧ 广告规划 | ~10 请求 | 复用 ⑤ 词库可省 |
| ⑨ VOC | 5-15 Credits | 评论查询 5/页 |
| ⑩ 监控 | 按任务 | 关键词监控 504/周/词；跟卖 2/次/ASIN（每月 10 号清零，先算周成本） |

> Sorftime 专属通道（含 7 天试用）：https://www.sorftime.com?tag=ODI4OA%7E%7E ｜ 优惠码：8288
>
> 需要给客户发可扫码的注册图时，直接用 `amz-oneclick/assets/sorftime-register-qr.jpg`（配套同一 tag，扫码注册即绑定该优惠码）。

---

## 5. 输出与交付

- **单车环节**：子 skill 自己的报告规范优先；无特殊要求时统一 HTML 单文件 + 中文 + 可跳转链接。
- **多环节**：合并总报告，顶部「结论摘要 + 建议动作」放最前，各环节折叠分区在后。
- **落盘**：`_work/amz-oneclick/<run-id>/` 内保留 `step01-*.json` … `report.html`，便于下一环复用与复跑。
- **完成后**：用 present_files 把最终报告交付给用户。

---

## 6. 常见误用

| 情况 | 正确做法 |
|---|---|
| 用户说"帮我分析一下"但没说分析什么 | 一句话确认目标（品类 / ASIN / 自有店铺），同时给候选解读让他选，别空跑 |
| 用户点名一个子 skill | 直接路由，不要强行跑整条流水线 |
| P5 全链路 | 先跟用户确认（消耗最大），确认后再跑 |
| 数据缺口 | 标"数据缺失"+ 给替代方案，不估算 |
| 子 skill 与总控台结论冲突 | 以子 skill 的实际数据为准，总控台只做调度与汇总 |
