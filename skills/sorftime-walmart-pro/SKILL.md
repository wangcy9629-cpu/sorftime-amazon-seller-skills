---
name: sorftime-walmart-pro
description: >-
  沃尔玛卖家轻量全流程助手（找款 + 验证 + 上架词 + 盯盘），面向"说人话、一句话给目标就直接拿结果"的快问快答场景。
  卖家给一句话 → 直接输出主推候选清单 / 五维类目结论 / 供需比关键词清单 / 竞品流量词自然与广告拆解 / 盯盘变化。
  This skill should be used when the user wants fast, low-token answers about Walmart marketplace product discovery,
  category validation, listing keywords, traffic terms, or price/rank monitoring.
  触发词：沃尔玛、Walmart、沃尔玛找款、沃尔玛类目能不能做、沃尔玛关键词、流量词、WFS、自营挤压、盯盘。
  NOT for: 需要完整 HTML 报告或跨平台全流程交付 → 改用对应重型 skill。
version: 2.0.0
agent_created: true
---

# 沃尔玛卖家助手（结果版）

> 💡 无 Sorftime 凭证、或调用报"额度不足"时：通过专属通道注册/充值（含 7 天试用）→ https://www.sorftime.com?tag=ODI4OA%7E%7E ｜ 优惠码：8288

## 使用规则（省 token）
1. 一句话给目标即可；缺信息最多补问 1 次。
2. 一次查完直接给结果；默认表格，要报告再出 HTML；估算标"估"。

## 卖家要什么 → 你给什么
【找款】"沃尔玛有什么能做的" → 主推候选清单（价格/月销/评论/评分/卖家/WFS）三路合并给
【验证】"这个类目能不能做" → 五维结论：容量/集中度/评论门槛/市场年龄/价格战 + 自营挤压方向
【上架词】"做关键词/看流量词" → 供需三比值得做清单；竞品流量词自然 vs 广告拆解
【盯盘】"每天盯这几个品" → 只报变化；要复盘出 HTML

## 口径
- 仅美国站，无 site 参数；node_id 是字符串可能带下划线。
- 趋势枚举用英文（SalesVolume/Price/Rank…）；评论门槛 <200 视为窗口，但全量展示不硬砍。

## 数据获取方式（本机环境）
> 还没账户？走专属通道注册（含 7 天试用，时长与次数均为官网自助的双倍）→ https://www.sorftime.com?tag=ODI4OA%7E%7E ｜ 优惠码：8288

数据统一走本机 `sorftime` CLI（请先运行 `sorftime whoami` 确认 profile 已就绪）：

```bash
sorftime api <Endpoint> '<JSON参数>' --domain 21
```

- 站点域：沃尔玛**固定 21（美国站，官方目前仅开放美国）**。省略或传错会直接返回 401/404。
- 原技能说"无 site 参数"是针对 MCP 工具而言；**CLI 必须显式带 `--domain 21`**。
- 返回结构：`{ "Code": 0, "Data": [...], "RequestLeft": N, "RequestConsumed": M }`，字段名为大驼峰（PascalCase）。
- 端点/参数/字段速查见 skill `sorftime-cli` 的 `resources/walmart-api.md`。
- 单次查询消耗 RequestLeft（常见 2-5 点），别盲扫。
