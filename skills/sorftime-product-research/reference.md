# Sorftime MCP 工具详细参考

## 工具分类速查

### 类目分析工具

| 工具 | 功能 | 使用场景 |
|------|------|----------|
| `category_search` | 类目市场筛选 | 宏观市场扫描、蓝海发现 |
| `category_report` | 类目详细报告 | TOP100产品统计 |
| `category_trend` | 类目历史趋势 | 趋势验证、季节性分析 |
| `category_products` | 类目TOP100清单 | 竞争分析 |
| `category_keywords` | 类目核心关键词 | 关键词布局 |

### 产品分析工具

| 工具 | 功能 | 使用场景 |
|------|------|----------|
| `product_search` | 产品筛选 | 多维度条件筛选 |
| `product_detail` | 产品详情 | 单品深度分析 |
| `product_reviews` | 评论分析 | 好评/差评挖掘 |
| `product_trend` | 历史趋势 | 销量/价格趋势 |
| `product_variations` | 变体分析 | 变体策略 |
| `product_traffic_terms` | 流量词分析 | 竞品推广策略 |

### 关键词工具

| 工具 | 功能 | 使用场景 |
|------|------|----------|
| `keyword_search_results` | 搜索结果 | 竞争度分析 |
| `keyword_detail` | 关键词详情 | 搜索量、CPC |
| `keyword_trend` | 关键词趋势 | 季节性判断 |
| `keyword_extends` | 关键词延伸 | 长尾词挖掘 |

### 蓝海挖掘

| 工具 | 功能 | 使用场景 |
|------|------|----------|
| `potential_product` | 隐赚指数挖掘 | 蓝海产品发现 |

### 货源调研

| 工具 | 功能 | 使用场景 |
|------|------|----------|
| `ali1688_similar_product` | 1688货源查询 | 供应链验证 |

---

## 完整参数手册

### category_search

**用途**：类目市场筛选（宏观扫描）

**关键参数**：

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `amzSite` | string | 站点（US/GB/DE等） | "US" |
| `searchName` | string | 类目名称关键词 | "Kitchen" |
| `month_sales_volume_range` | string | 月销量范围 | "[10000,50000]" |
| `price_range` | string | 价格范围 | "[15,40]" |
| `newproduct_sales_share` | string | 新品销量占比 | "[0.3,1]" |
| `top3Product_sales_share` | string | Top3销量占比（垄断系数） | "[0,0.35]" |
| `amazonOwned_sales_share` | string | 自营占比 | "[0,0.3]" |
| `ratings_count_range` | string | 评论数范围 | "[0,500]" |

**蓝海筛选组合**：
```json
{
  "amzSite": "US",
  "newproduct_sales_share": "[0.3,1]",
  "top3Product_sales_share": "[0,0.35]",
  "ratings_count_range": "[0,300]"
}
```

---

### potential_product

**用途**：隐赚指数挖掘（仅US站）

⚠️ **重要限制**：
- 仅支持US站
- 不要在执行前询问用户筛选条件
- 直接拉取名单后筛选分析

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `site` | string | ✅ | 固定值："US" |
| `searchName` | string | ❌ | 关键词筛选（不建议使用） |
| `price_range` | string | ❌ | 价格区间（算法自动评估） |
| `delivery_type` | string | ❌ | FBA/FBM/Both |

**正确用法**：
```python
# 直接调用，不询问用户
potential_product(site="US")

# 然后对结果筛选分析
```

**评分解读**：
- **正分数**：符合潜力标准，分数越高潜力越大
- **-99**：不符合标准（头部产品、老品、品牌产品）
- **-9999**：数据不足（新品<30天）

---

### product_search

**用途**：多维度产品筛选

**常用参数**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `searchName` | 产品名称关键词 | "kitchen organizer" |
| `price_range` | 价格范围 | "[15,35]" |
| `month_sales_volume_range` | 月销量范围 | "[500,5000]" |
| `ratings_count_range` | 评论数范围 | "[0,500]" |
| `ratings_range` | 星级范围 | "[4.0,5.0]" |
| `delivery_type` | 发货方式 | "FBA" / "FBM" / "Both" |
| `brand` | 品牌筛选 | "Generic" |
| `subcategory_sales_volume_rank_range` | 类目排名 | "[1,50]" |

**新手入门筛选**：
```json
{
  "price_range": "[10,30]",
  "month_sales_volume_range": "[500,5000]",
  "ratings_count_range": "[0,500]",
  "delivery_type": "FBA"
}
```

---

### product_reviews

**用途**：评论分析（好评/差评挖掘）

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `asin` | string | 产品ASIN |
| `amzSite` | string | 站点 |
| `reviewType` | string | "Positive"/"Negative"/"Both" |

**分析要点**：
- **好评高频词**：提炼卖点
- **差评高频词**：发现改进机会
- **使用场景**：验证需求

---

### keyword_detail

**用途**：关键词详情（CPC查询）

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `keyword` | string | 关键词 |
| `amzSite` | string | 站点 |

**返回数据**：
- 月搜索量
- 推荐CPC竞价
- 竞价范围

**CPC解读**：
- CPC $0.78：单次点击成本
- 范围 0.52-0.92：竞价区间
- ACOS控制：毛利率40% → ACOS应<20%

---

## 2026年AI算法适配指南

### COSMO语义理解

**从关键词到场景**：

| 传统 | COSMO优化 |
|------|----------|
| "瑜伽垫" | "户外防滑旅行瑜伽垫" |
| "保温杯" | "12小时保温不锈钢旅行杯" |
| "台灯" | "护眼可调光书桌LED台灯" |

**知识图谱关系**：
- `Is_A`：产品类别
- `Used_For`：使用场景
- `Capable_Of`：功能能力
- `Used_for_Audience`：目标人群

### Rufus AI优化

**NPO方法（名词短语优化）**：

❌ 旧式堆砌：
```
Yoga Mat Thick Non-slip Exercise Fitness Pilates
```

✅ NPO优化：
```
Extra Thick 8mm Yoga Mat - Non-slip TPE Material for
Hot Yoga and Pilates Workouts
```

**Q&A种子布局**：
1. "Is this suitable for hot yoga?"
2. "Can I use this on carpet?"
3. "How does this compare to Manduka?"

### A12算法适配

**SPI（多仓分发指数）优化**：
- 标准尺寸产品：优势
- 超大/异形件：劣势
- 多仓库存：排序优先

---

## 数据量建议

| 场景 | 建议数据量 | 分析重点 |
|------|-----------|----------|
| 类目筛选 | 50-100个 | 取TOP 20 |
| 产品筛选 | 最多100条 | 取TOP 20 |
| 关键词验证 | 50个 | 取TOP 10 |
| 评论分析 | 正面+负面各50条 | 共100条 |

---

## 错误处理规范

### 工具调用失败

**立即停止**，返回错误信息：
```
【错误：Sorftime MCP 工具不可用】

当前无法调用 [工具名称] 工具。

可能原因：
1. MCP工具服务未运行
2. 工具配置不正确
3. 网络连接问题

请检查Sorftime MCP工具的可用状态后重试。
```

**禁止行为**：
- 不要重试
- 不要用web_search替代
- 不要继续分析或给出模糊建议

---

## 参数格式规范

| 类型 | 格式 | 正确 | 错误 |
|------|------|------|------|
| 价格范围 | `["min","max"]` | `["15","35"]` | `15-35` |
| 占比范围 | `["0.x","0.y"]` | `["0.1","0.3"]` | `10%-30%` |
| 站点 | 大写双字母 | `"US"` | `"us"` / `"美国"` |

---

*文档版本：v2.0*
*更新日期：2026年2月*
