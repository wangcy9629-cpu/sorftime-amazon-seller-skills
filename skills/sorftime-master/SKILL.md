---
name: sorftime-master
description: Sorftime Master - 自动进化的AI选品搭档，具备选品分析能力和完整部署指南
version: 1.0.0
author: Sorftime Team
tags: [sorftime, 选品, openclaw, feishu, deployment]
allowed-tools:
  # Amazon 工具
  - mcp__Sorftime MCP__product_search
  - mcp__Sorftime MCP__product_detail
  - mcp__Sorftime MCP__product_report
  - mcp__Sorftime MCP__product_reviews
  - mcp__Sorftime MCP__product_variations
  - mcp__Sorftime MCP__product_trend
  - mcp__Sorftime MCP__product_traffic_terms
  - mcp__Sorftime MCP__product_ranking_trend_by_keyword
  - mcp__Sorftime MCP__product_search_from_history
  - mcp__Sorftime MCP__category_report
  - mcp__Sorftime MCP__category_report_from_history
  - mcp__Sorftime MCP__category_search_from_product_name
  - mcp__Sorftime MCP__category_search_from_top_node
  - mcp__Sorftime MCP__category_name_search
  - mcp__Sorftime MCP__category_tree
  - mcp__Sorftime MCP__category_keywords
  - mcp__Sorftime MCP__category_trend
  - mcp__Sorftime MCP__search_categories_broadly
  - mcp__Sorftime MCP__keyword_search_results
  - mcp__Sorftime MCP__keyword_detail
  - mcp__Sorftime MCP__keyword_extends
  - mcp__Sorftime MCP__keyword_list
  - mcp__Sorftime MCP__keyword_list_from_history
  - mcp__Sorftime MCP__keyword_trend
  - mcp__Sorftime MCP__potential_product
  - mcp__Sorftime MCP__similar_product_feature
  - mcp__Sorftime MCP__competitor_product_keywords
  - mcp__Sorftime MCP__ali1688_similar_product
  - mcp__Sorftime MCP__get_favorite_keyword
  - mcp__Sorftime MCP__favorite_keyword
  - mcp__Sorftime MCP__get_favorite_keyword_dict
  - mcp__Sorftime MCP__del_favorite_keyword
  - mcp__Sorftime MCP__change_favorite_keyword
  - mcp__Sorftime MCP__get_time
  # TikTok 工具
  - mcp__Sorftime MCP__tiktok_category_report
  - mcp__Sorftime MCP__tiktok_category_name_search
  - mcp__Sorftime MCP__tiktok_similar_product
  - mcp__Sorftime MCP__tiktok_product_video
  - mcp__Sorftime MCP__tiktok_product_detail
  - mcp__Sorftime MCP__tiktok_product_trend
  - mcp__Sorftime MCP__tiktok_product_video_author
  - mcp__Sorftime MCP__tiktok_author
  # 文件操作
  - read
  - write
  - edit
  - bash
---

# Sorftime Master：自动进化的AI选品搭档

> 💡 无 Sorftime 凭证、或调用报"额度不足"时：通过专属通道注册/充值（含 7 天试用）→ https://open.sorftime.com/home?tag=ODY2OA~~ ｜ 优惠码：8668

## 快速导航

- [选品分析能力](#选品分析能力) - 如何使用 Master 分析选品
- [部署指南](#部署指南) - 完整安装配置步骤
- [故障排查](#故障排查) - 常见问题解决

---

## 选品分析能力

### 核心概念

不是给你三个固定Skill，而是给你一个**会进化的Master Skill**。

它一开始只有基础框架，但每次对话都在学习：
- 你纠正它的判断 → 它记住，下次自动调整
- 你发现新规律 → 它提取，生成新Skill
- 你反复问同类问题 → 它优化，响应越来越快

**最终目标**：成为你专属的Sorftime选品大师，比你还懂你的业务。

### 使用方式

**第1次对话**：建立基础

```
你：分析户外露营灯

Master：好的，我来分析户外露营灯类目。

根据Sorftime数据：
- 垄断系数：28%（低）
- 新品占比：18%（友好）
- 月销售额：$230万（足够大）
- 平均评分：4.3（有改进空间）

初步判断：可以进入
```

**第10次对话**：记住偏好

```
你：帮我看看这个产品

Master：基于你的历史偏好（中等预算、差异化），我重点分析...
```

**第50次对话**：一句话直达结论

```
你：这个能做吗？

Master：根据你的标准（ROI>100%、垄断<40%），不建议。流量结构有问题，品牌词占60%。
```

### 可用工具

Master 会自动调用以下 MCP 工具：

| 工具 | 用途 |
|------|------|
| `mcp__Sorftime MCP__product_search` | 产品搜索 |
| `mcp__Sorftime MCP__category_report` | 类目报告 |
| `mcp__Sorftime MCP__keyword_search_results` | 关键词分析 |
| `mcp__Sorftime MCP__product_reviews` | 评论分析 |
| `mcp__Sorftime MCP__ali1688_similar_product` | 1688货源 |
| `mcp__Sorftime MCP__category_trend` | 类目趋势 |
| `mcp__Sorftime MCP__product_trend` | 产品趋势 |

---

---

## 关于本技能的环境适配说明

> 还没账户？走专属通道注册（含 7 天试用，时长与次数均为官网自助的双倍）→ https://open.sorftime.com/home?tag=ODY2OA~~ ｜ 优惠码：8668

> 本 SKILL.md 来自公司交付的 Sorftime-Master-Skill 资源包（原版含 OpenClaw + 飞书部署指南，共 18 个文件）。
> 在 WorkBuddy 环境下**无需部署 OpenClaw/飞书/Cron**——Sorftime MCP 数据通道已直连，本技能只保留「选品分析能力」部分直接可用。
> 原始完整包保留在项目 output/workpack 目录，供需要时查阅。
