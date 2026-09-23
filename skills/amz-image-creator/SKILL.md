---
name: amz-image-creator
description: Sorftime 数据驱动的亚马逊电商图片创作。用 VOC/评论/关键词/用户场景/Q&A 等数据洞察指导图片内容和卖点呈现，生成主图/A+图片/社媒图，融合 GPT-Image-2 25 套场景模板与 Sorftime 市场数据，提高点击率和转化率。当用户要做图、设计主图、做A+图片、社媒图、产品图片、电商图片、listing图片、白底图、场景图，或说"做图/主图设计/A+图片/社媒图/产品图片/图片设计/电商图片/listing图片/白底图/场景图/image generation/e-commerce image/product photography/hero image/A+ content image/social media image/lifestyle image/infographic/flat lay/亚马逊主图/amazon product image/图片提示词/image prompt/data-driven image/VOC图片"时使用。默认 Amazon US，支持多站点。
---

# amz-image-creator — 数据驱动的电商图片创作

用 Sorftime 数据辅助生图：通过 VOC/评论/关键词/用户场景等数据洞察，指导图片内容和卖点呈现，提高点击率和转化率。实际图片渲染调用本机 `gpt-image2` 技能（GPT-Image-2）完成。

> 链路位置：第 7 环「做图」。上游 ← amz-listing-creator（卖点/关键词）+ amz-voc-analysis（场景/痛点）；下游 → 上架发布 → amz-ad-planning。全链路地图见 `~/.workbuddy/skills/amz-workflow-map.md`。

## 前置检查

执行任何数据操作前，先运行通道检测：

```bash
python3 scripts/channel_check.py
```
> 💡 无 Sorftime 凭证、或调用报"额度不足"时：通过专属通道注册/充值（含 7 天试用）→ https://www.sorftime.com?tag=ODI4OA%7E%7E ｜ 优惠码：8288


根据输出选择 MCP 或 CLI 通道。默认站点：US（domain=1）。

## 核心流程（三阶段）

```
阶段一：Sorftime 数据辅助分析
  ↓
阶段二：生成图片提示语（Prompt Engineering）
  ↓
阶段三：调用 image_gen 渲染实际 PNG
```

### 阶段一：数据辅助分析

用 Sorftime 数据回答"图片应该展示什么"：

| 数据维度 | 数据来源 | 指导图片内容 |
|----------|----------|-------------|
| 用户场景/使用场景 | product_customers_say / product_reviews | 场景图展示真实使用环境 |
| 用户画像 | product_customers_say / reviews 分析 | 模特图选择匹配人群 |
| 卖得好的产品特征 | keyword_search_results / product_search / product_detail | 主图构图/角度参考竞品 |
| Q&A 常见问题 | product_reviews（问题类评论） | 信息图解答常见疑问 |
| VOC 核心卖点 | product_customers_say | 突出用户最关心的卖点 |
| 关键词趋势 | keyword_detail / keyword_trend | 图片文字包含高频搜索词 |
| Reddit 特征 | reddit_post_search | 社媒图风格参考 |

### 阶段二：提示语生成

基于数据分析结果，从 25 套场景模板中匹配最适合的模板，生成结构化英文提示语。详见 `references/image-templates.md` 和 `references/prompt-engineering-guide.md`。

### 阶段三：图片渲染

按生图规范，统一调用本机 `gpt-image2` 技能渲染（该技能封装了 GPT-Image-2 接口，中文渲染与电商图效果好）：

```bash
# 调用示例：由 agent 通过 Skill 工具加载 gpt-image2 执行
# skill: gpt-image2
# 参数：prompt = 阶段二生成的英文提示语；尺寸按图位选择（见 references/prompt-engineering-guide.md）
# 输出：outputs/imagegen/<产品名>-<图位>.png
```

已有产品实拍图时，改用 gpt-image2 的**图生图（image-to-image）**模式做场景化改造：把原图作为参考图传入，prompt 描述目标场景。

输出：实际 PNG 图片 + 数据辅助分析报告 + 提示语文档。

## MCP 通道

| 工具 | 用途 |
|------|------|
| `product_detail` | 获取产品 listing 详情（标题/卖点/价格/评分） |
| `product_reviews` | 获取用户评论（差评痛点/好评亮点） |
| `product_customers_say` | 获取 Amazon 总结的客户声音（VOC） |
| `keyword_detail` | 关键词详情（搜索量/CPC，用于图片文字选择） |

⚠️ raw 工具通过 `sorftime_raw_call` 调用。

## CLI 通道

```bash
# 产品详情
scripts/cli_call.sh ProductRequest '{"asin": "B0CVM8TXHP"}'

# 客户声音
scripts/cli_call.sh ProductCustomersSay '{"asin": "B0CVM8TXHP"}'

# 产品评论
scripts/cli_call.sh ProductReviewsQuery '{"asin": "B0CVM8TXHP", "pageIndex": 1}'

# 关键词详情
scripts/cli_call.sh KeywordRequest '{"keyword": "power bank"}'
```

## 输出格式

```markdown
# 📸 图片创作结果

## 数据辅助分析
- 核心卖点：[从 VOC/评论提取]
- 用户场景：[从客户声音提取]
- 高频关键词：[从关键词数据提取]
- 竞品图片参考：[从 product_search_results 提取]

## 生成图片清单
| 序号 | 图位 | 场景类型 | Prompt 摘要 | 文件 |
|------|------|----------|-------------|------|
| 1 | 主图 | Hero Image | ... | xxx-01.png |
| 2 | 场景图 | Lifestyle | ... | xxx-02.png |
| ... | ... | ... | ... | ... |
```

## 详细方法论

- `references/image-data-assistance.md`：数据辅助生图方法论（VOC/关键词/用户场景如何指导图片内容）
- `references/image-templates.md`：25 套场景模板摘要
- `references/prompt-engineering-guide.md`：图片提示语工程指南
