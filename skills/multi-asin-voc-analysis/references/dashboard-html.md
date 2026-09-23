# HTML 看板交付规范（dashboard-html.md）

交付物 = 单个自包含 HTML 文件：内联 CSS + 一个 JSON payload（script）+ 一个渲染 JS（script）。
不依赖外部资源；商品图以 base64 内嵌（embedded_product_image_* 审计）；ASIN 可跳前台；原声可回看；数据可导出。

## 顶层结构

1. **头部**：报告标题（`Amazon 多ASIN VOC 报告`）、报告切换（详情报告 / 精简报告 双模式）、KPI 条（组合评论数、平均星级、差评率、强差评率、VP 率、页数审计）。
2. **数据范围说明**（delivery-scope-notice）：评论数、窗口、负向定义、追溯级别、置信度说明，按 delivery_contract.notice 渲染。
3. **ASIN 产品速览**（#asin-product-index）：12 张商品卡；悬停/键盘聚焦显示完整产品图、标题、品牌、价格、节点、排名、月销量、评论数。
4. **精简报告**（#concise-report）：观察→分析→焦点→策略 四块 + 方法卡（数据范围/JTBD 任务/证据标签/动作闭环），每块右侧同步原声证据。
5. **详情报告面板**（按顺序，均带锚点 id）：
   - #knockout ASIN 竞品击破总控塔
   - #motion Data2Motion 动态阅读包
   - #defect-diff ASIN 缺陷差异剖面
   - #diff-evidence ASIN 差异证据对照台账
   - #analysis-ring ASIN-first 证据阅读路线（含"从附件学到的视图迁移"）
   - #delta ASIN 竞品能力差异主控台
   - #pairwise 1v1 ASIN 能力对位地图
   - #directives 对手定向击破指令
   - #rewrite Listing / 素材 / 广告改写包
   - #decision 竞品击破顺序总览
   - #dossiers ASIN 竞争强弱画像
   - #matchup ASIN × 能力强弱棋盘
   - #strike 目标 ASIN 击破作战包
   - #strike-evidence 目标 ASIN 作战证据链
   - #readiness 目标 ASIN 主张上线门禁
   - #abtest ASIN 击破 A/B 测试队列
   - #playbook 1v1 ASIN 击破剧本
   - #spec 击破资产清单
   - #command ASIN-first 竞品能力指挥台
   - #precision 关键词精度闸门
   - #matrix 横向竞争地图
   - #attack 竞品缺陷差异与击破地图
   - #capability ASIN-first 竞争能力判读与矩阵审计
   - #profiles ASIN-first 竞品战术档案
   - #complex ASIN-first 复杂证据环（根因交叉 / 需求与未满足 / 正负面对比 / 原声簇）
   - #jtbd JTBD 机会模块
   - #hv ASIN-first 时间触发与横纵交汇
   - #drift ASIN-first 年份漂移判读
   - #themes 竞品 ASIN 能力判读与证据矩阵
   - #journey ASIN-first 场景与卖点翻转击破环
   - #evidence ASIN-first 击破证据三角
   - #quality 数据质量审计
   - #raw-data 原始评论明细

## 详情/精简双模式

- 详情：保留横向竞争、证据链、击破资产、原始评论，适合逐项审计。
- 精简：按 观察/分析/焦点/策略 压缩为决策版，右侧同步原声证据；共用同一套 ASIN 与原始评论证据。
  - 观察：JTBD 主任务（覆盖评论数、负向数、横跨 ASIN 数、成功标准、切换触发、弱强位）。
  - 分析：4 个 analysis_slots 失败路径（如 边界准确/环境信号/训练安全/续航佩戴），解释低星=期望落差。
  - 焦点：把主任务拆成可证明购买标准，弱位暴露失败边界、强位提供可借鉴证明。
  - 策略：一级动作 + 产品/Listing/预期效果/复验阈值，带原声证据。
- 折叠：面板可折叠（foldSectionBody），默认按 report_mode 压缩非重点模块。

## 渲染与交互要求

- 所有 ASIN 字符串渲染成可点击链接（前台商品页）+ 悬停卡（图片/标题/品牌/价格/节点/排名/月销/评论数）；悬停卡数据来自 product_cards。
- 所有评论文本引用可回到原始评论明细；SYN-* 合成 ID 不生成前台评论链接，只标注"追溯受限"。
- 原始评论明细（#raw-data）：分页（20 条/页）、按 ASIN/星级/情感/验证购买筛选、导出当前筛选 CSV / 全部 CSV。
- KPI 与条状图用内联函数（fmtInt/fmtPct/fmtRating/bar/sparkbar）保持视觉一致。
- 模块统一色彩语义：risk（红）/ watch（琥珀）/ good（绿）；能力分低=红，高=绿。
- 每个面板的 lead 文案用中文说明"先读什么、为什么这样读"。

## 数据质量审计（#quality）

- 组合：raw_review_records / expected / coverage_rate / pages_reported / fetched_pages / missing_pages。
- 逐 ASIN 审计表：pages_reported / fetched / missing / raw_reviews_in_window / excluded_older / status。
- 追溯说明：missing_review_url_count、synthetic_review_id_count、traceability_label（如"源数据未提供真实 Review ID/URL；SYN-* 仅为合成审计 ID，不生成原评论链接"）。
- 页面审计（page_audit）每条含 source_path、review_window、collection_scope、page_data_status。

## 质量底线

- 单文件可离线打开；无外链图片/CSS/JS。
- product_cards 每个 ASIN 至少 1 张内嵌图；缺失则用占位卡并标注。
- 所有数值与 payload 一致；不渲染 payload 中没有的数据。
