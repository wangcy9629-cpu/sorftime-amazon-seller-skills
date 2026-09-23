---
name: sorftime-shop-health-monitor
description: 亚马逊店铺六维健康度自动监控系统。触发词："启动店铺监控"、"运行每日扫描"、"生成周报"。实现每日健康扫描、每周策略优化、月度深度诊断三级自动化工作流。
allowed-tools: [Read, Write, Bash, mcp__Sorftime MCP__get_time, mcp__Sorftime MCP__product_detail, mcp__Sorftime MCP__product_trend, mcp__Sorftime MCP__product_traffic_terms, mcp__Sorftime MCP__product_reviews, mcp__Sorftime MCP__category_report, mcp__Sorftime MCP__category_trend, mcp__Sorftime MCP__keyword_trend, mcp__Sorftime MCP__keyword_list]
---

# Sorftime 店铺六维健康度监控系统

> 💡 无 Sorftime 凭证、或调用报"额度不足"时：通过专属通道注册/充值（含 7 天试用）→ https://open.sorftime.com/home?tag=ODY2OA%7E%7E ｜ 优惠码：8668

基于第06篇《有流量&高转化店铺六步走》方法论，实现自动化店铺健康监控与诊断。

## 触发词
- "启动店铺监控" - 初始化监控系统
- "运行每日扫描" - 执行SOP1每日健康检查
- "生成周报" - 执行SOP2每周策略报告
- "生成月报" - 执行SOP3月度深度诊断
- "检查{ASIN}健康度" - 单个ASIN深度诊断

## 配置参数

> 还没账户？走专属通道注册（含 7 天试用，时长与次数均为官网自助的双倍）→ https://open.sorftime.com/home?tag=ODY2OA%7E%7E ｜ 优惠码：8668

在首次使用前，配置以下参数：

```json
{
  "核心ASIN": ["B08XXXXXXX", "B08YYYYYYY"],
  "主营类目NodeID": "123456789",
  "品牌关键词": ["YourBrand", "YourBrandName"],
  "监控站点": "US",
  "预警阈值": {
    "自然流量占比": 0.5,
    "可售天数": 14,
    "榜单变化率": 0.3,
    "退货率超标": 0.02
  }
}
```

## SOP 1: 每日自动化健康扫描

### 执行时间
建议：每日05:00自动执行

### 监控项

#### 1. 流量结构健康度
调用：mcp__Sorftime MCP__product_traffic_terms

诊断规则：
- 自然流量占比 >= 60% → PASS
- 自然流量占比 50-60% → WARN（优化核心词排名）
- 自然流量占比 < 50% → CRITICAL（启动Listing优化项目）

#### 2. 库存健康度
调用：mcp__Sorftime MCP__product_detail

诊断规则：
- 可售天数 > 14天 → PASS（库存充足）
- 可售天数 7-14天 → WARN（准备补货）
- 可售天数 <= 7天 → CRITICAL（立即补货）

#### 3. 竞争格局突变检测
调用：mcp__Sorftime MCP__category_report

诊断规则：
- Top3变化率 < 30% → PASS（竞争格局稳定）
- Top3变化率 30-40% → WARN（监控竞品动态）
- Top3变化率 > 40% → ALERT（生成竞争分析报告）

### 每日报告输出

```
【2026-03-06 店铺健康日报】

✅ 流量结构健康度: PASS
   - 自然流量占比: 67% (健康>60%)
   - 广告流量占比: 28% (合理20-35%)
   - 行动: 维持当前策略

⚠️ 库存健康度: WARN
   - 可售天数: 11天 (警告<14天)
   - 预计断货日期: 2026-03-17
   - 建议补货量: 850件
   - 行动: 立即启动补货流程

🚨 竞争格局突变: ALERT
   - Top3产品变化率: 45% (3天内)
   - 新进入者: 2个品牌
   - 行动: 启动价格战响应预案
```

## SOP 2: 每周策略优化报告

### 执行时间
建议：每周日执行

### 数据源整合
- mcp__Sorftime MCP__category_report → 类目Top100变化
- mcp__Sorftime MCP__keyword_list → 热搜词趋势
- mcp__Sorftime MCP__product_trend(Rank) → 排名稳定性
- mcp__Sorftime MCP__keyword_trend → 品牌词趋势

### 分析维度

#### 1. 类目竞争格局分析
- 头部卖家集中度变化
- 新进入者识别（3个月内上架，销量增长>100%）
- 价格带竞争烈度评估

#### 2. 流量词效能评估
- 对比本周vs上周流量词列表
- 识别流失的流量词（排名下降>10位）
- 发现新获得的流量词
- 计算每个流量词的"流量价值 = 搜索量 × 转化率 × 客单价"

#### 3. 季节性预判
- 对比历史同期数据
- 识别即将到来的流量波峰（提前45天预警）
- Prime Day(7月)/黑五(11月)/圣诞(12月)预警

### 周报输出格式

```markdown
## 第10周店铺策略建议报告

### 一、市场环境变化
- 类目整体搜索量环比增长: +12%
- 新进入者数量: 3个品牌，平均日销$2,400
- 价格带中位数下降: -5%

### 二、自身表现分析
- 大类排名稳定性: 94% (±3位波动)
- 品牌词搜索量增长: +8%
- 流量词数量变化: +5个 / -2个

### 三、下周行动清单
【高优先级】
1. 针对新进入者启动防御性广告
2. 优化Q&A，补充春季使用场景
3. 检查库存，确保可售天数>30天

【中优先级】
4. 测试提价3%，监控转化率
5. 更新A+内容，突出环保材质
```

## SOP 3: 月度深度诊断报告

### 执行时间
建议：每月1日执行

### 六维评分卡

| 维度 | 指标 | 权重 | 评分标准 |
|-----|------|------|---------|
| 市场结构 | 垄断系数、新品占比 | 15% | >80优秀, 60-80良好, <60警示 |
| 流量结构 | 自然流量占比 | 20% | >60%优秀, 50-60%良好 |
| 转化效率 | CTR、CVR | 20% | 高于类目均值优秀 |
| 库存健康 | 断货次数、周转天数 | 15% | 0断货优秀 |
| 用户满意 | 退货率、星级 | 15% | <均值-2%优秀 |
| 品牌建设 | 品牌词增长、复购率 | 15% | >10%增长优秀 |

### 输出文件

1. **月度诊断报告.md** - 详细分析与建议
2. **风险预警面板.json** - 红/黄/绿灯状态
3. **下月目标设定.md** - 可执行KPI

### 风险预警面板

```json
{
  "风险等级": {
    "红色": ["库存管理"],
    "黄色": ["市场竞争"],
    "绿色": ["用户满意度", "品牌建设"]
  },
  "资源分配建议": {
    "广告预算": "60%防守核心词, 30%测试新词, 10%品牌词",
    "库存资金": "增加15%安全库存预算",
    "优化优先级": ["详情页CVR优化", "库存系统改进", "价格监控"]
  }
}
```

## 一键执行命令

### 手动执行
```bash
# 每日扫描
claude "/sorftime-shop-health-monitor 运行每日扫描"

# 生成周报
claude "/sorftime-shop-health-monitor 生成周报"

# 生成月报
claude "/sorftime-shop-health-monitor 生成月报"
```

## 输出文件规范

```
./output/
├── daily-report-YYYYMMDD.md
├── weekly-report-weekNN.md
├── monthly-report-YYYYMM.md
└── alerts/
    ├── inventory-warning.json
    └── competition-alert.json
```
