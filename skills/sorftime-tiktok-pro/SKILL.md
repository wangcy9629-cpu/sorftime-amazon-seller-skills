---
name: sorftime-tiktok-pro
description: >-
  TikTok 卖家轻量全流程助手（找爆款 + 验证 + 达人放量 + 盯盘），面向"说人话、一句话给目标就直接拿结果"的快问快答场景。
  卖家给一句话 → 直接输出对标爆款清单 / 类目大盘与结论 / 达人建联清单与切入点 / 可拍视频脚本 / 推广节奏时间轴。
  This skill should be used when the user wants fast, low-token answers about TikTok Shop product discovery, category sizing,
  creator outreach, video script hooks, or campaign pacing.
  触发词：TikTok、TikTok爆款、找对标、达人、建联、达人清单、视频脚本、钩子、推广节奏、盯盘。
  NOT for: 需要完整 HTML 报告或跨平台全流程交付 → 改用对应重型 skill。
version: 2.0.0
agent_created: true
---

# TikTok 卖家助手（结果版）

> 💡 无 Sorftime 凭证、或调用报"额度不足"时：通过专属通道注册/充值（含 7 天试用）→ https://www.sorftime.com?tag=ODI4OA%7E%7E ｜ 优惠码：8288

## 使用规则（省 token）
1. 一句话给目标即可；缺信息最多补问 1 次。
2. 一次查完直接给结果；默认表格，要报告/脚本清单再出 HTML/文档；估算标"估"。

## 卖家要什么 → 你给什么
【找爆款】"TikTok 有什么好做的" → 对标爆款清单（价格/销量/卖点/视频表现）
【验证】"这个类目能不能做" → 类目大盘（叶子类目月销/MoM/均价）+ 结论
【放量·达人】"找达人/建联" → 达人清单（量级/匹配/历史带货）+ 建联切入点
【放量·内容】"写视频脚本/看什么内容能跑" → 内容套路+可拍脚本（钩子/结构/指令）
【盯盘】"看这个爆款节奏/每日盯" → 推广节奏时间轴；或只报变化

## 口径
- 类目报告 Top50 无 product_id，下钻先查详情；视频 tag 噪音大，只用标题抽 hashtag。
- 达人粉丝数常为 0，忽略；以该品带货记录为准。

## 数据获取方式（本机环境）
> 还没账户？走专属通道注册（含 7 天试用，时长与次数均为官网自助的双倍）→ https://www.sorftime.com?tag=ODI4OA%7E%7E ｜ 优惠码：8288

数据统一走本机 `sorftime` CLI（请先运行 `sorftime whoami` 确认 profile 已就绪）：

```bash
sorftime api <Endpoint> '<JSON参数>' --domain <站点域>
```

- 站点域：TikTok 301-308，**301 = 美国站**。注意 `AuthorRequest` / `VideoRequest` / `VideoTagSearch` 三个端点**只支持 301（美国）**。
- 返回结构：`{ "Code": 0, "Data": [...], "RequestLeft": N, "RequestConsumed": M }`，字段名为大驼峰（PascalCase）。
- 端点/参数/字段速查见 skill `sorftime-cli` 的 `resources/tiktok-api.md`；站点表见 `resources/_common.md`。
- 单次查询消耗 RequestLeft（常见 2-5 点），别盲扫。
