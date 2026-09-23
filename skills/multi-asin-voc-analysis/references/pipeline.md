# 分析流水线（pipeline.md）

按 0-12 步执行。每步产出对应 schema 模块（见 schema.md），最终由渲染器生成 HTML 看板。

## 0. 范围与类目档案

- 确定 `product_name`、`marketplace`（默认 US）、`keyword`（核心意图词）、`representative_asin`。
- ASIN 组合：1 个 benchmark（参考标杆，通常为头部/自有）+ 8-11 个 competitor，共 8-12 个；按 `relevance_status` 分层（core / adjacent / noise）。
- 窗口：近 3 年（如 2023-07-23 → 2026-07-23），更早评论计入 excluded_older_review_records。
- 构建 category_profile（见 references/category-profile.md）：类目边界、9 个左右能力主题（含关键词字典与 action）、7 个旅程阶段、7 个 JTBD jobs、spec 资产库、report_copy_contract。

## 1. 数据采集（逐 ASIN）

每条评论必须含：`asin, rating, title, content, review_date, review_month, verified_purchase, helpful_count, style, review_url, has_image, has_video, source, source_row_index, asin_row_number, portfolio_label, portfolio_role, review_id`。
分页审计：每个 ASIN 记录 `pages_reported / fetched_pages / missing_pages`。
血缘：`run_id / invocation_id / started_at / acquired_at / sources[]`（每个来源含 URL/导出文件路径/页数）。

## 2. 质量闸门（review_sufficiency_gate）

- 逐 ASIN：`coverage_rate = raw_reviews_in_window / expected_review_count`；记录 `coverage_gap_asin_count`、`failed_asin_count`。
- `formal_release_allowed`（可出正式结论）；`full_data_claim_allowed`（可声称全量数据，追溯受限时=false）。
- 追溯审计：`missing_review_url_count / synthetic_review_id_count / traceability_level`（full / trace_limited / limited）。
- 口径统一写入 delivery_contract 的 notice：评论数、窗口、负向定义、追溯限制、置信度说明。

## 3. 关键词/ASIN 分层（关键词精度闸门）

按核心意图把 ASIN 分为：
- core：进入正式产品 VOC 与竞品动作（如 12 个全 core）。
- adjacent：只作参照，不参与攻击结论。
- noise：不进分析，转广告否定词。
每层记录 `keyword_monthly_sales / keyword_sales_share / Top5 销量占比 / 近3年评论数 / 处理方式`。

## 4. 健康总览（aggregate_overview + rating_distribution）

指标：
- `avg_rating`、`negative_count/rate`（1-3★）、`strong_negative_count/rate`（1-2★）、`positive_count/rate`（4-5★）。
- `vp_rate`（已购占比）、`total_helpful_votes`、`helpful_negative_vote_share`（负评有用票占比，>0.5 说明负评被高度认可）。
- 评分分布 1-5 星（count + share）。
- 单 ASIN KPI：review_count、avg_rating、negative_rate、strong_negative_rate、vp_rate、risk_tier（risk/watch）、low_sample_flag（如 <30 条）。

## 5. 主题×ASIN 根因矩阵（theme_matrix）

- 用类目主题关键词字典对「标题+正文」做关键词匹配，记录 `matched_terms / matched_field / matched_spans（start/end/text）`；只统计 1-3★ 评论的负向提及（明确提及，不用变体字段当证据）。
- 每个主题：
  - `total_negative_mentions`、`portfolio_problem_rate = 负向提及 / 组合负评数`。
  - 每个 ASIN cell：`mention_count / negative_count / review_count`
    - `problem_rate = mention_count / negative_count`（负评内提及率）
    - `all_review_rate = mention_count / review_count`（全部评论内提及率）
    - `rate_delta_vs_portfolio = problem_rate - portfolio_problem_rate`
    - `position_type`：problem_rate 显著高于组合 → weak（偏弱观察）；显著低于 → strong（强位）；否则 watch。
  - 每个 cell 配 2-4 条 evidence（rating/date/title/quote/review_id/matched_terms/matched_spans）。

## 6. 能力竞争矩阵（capability_competition_matrix）

主题 × ASIN：
- `positive_mentions`（4-5★ 明确提及）、`negative_mentions`、`strong_negative_mentions`。
- `positive_rate = positive_mentions / review_count`；`failure_rate = negative_mentions / review_count`；`strong_failure_rate`。
- `capability_score`（0-100）：同一公式全库一致（如 正向密度加权 − 失败密度惩罚，负向权重更高）；分数越低越弱。
- `confidence`（normal / limited / low-sample）。
- 正负面原声各 1-2 条，带 matched_terms/spans。

## 7. 正负面翻转（sentiment_flip_matrix + voice_clusters）

- 每个主题：`positive_count / negative_count / flip_ratio = negative / (positive+negative)`。
- `top_positive_asin / top_negative_asin`。
- 输出 `negative_terms / positive_terms`（Top5 关键词+次数）与正负原声簇。
- 判定：flip_ratio 高（如 ≥0.3）且同一表达同时出现在好评与差评 → 该卖点必须写「承诺 + 适用条件 + 失效边界」。

## 8. JTBD 机会（jtbd_taxonomy + opportunity_focus + action_recommendations）

- 7 个左右 job：`job_code / job_name_cn / job_domain / job_step / desired_outcome / struggle_moment / switching_trigger / voc_link / evidence_rule / actionability / recommendation / risk_hedge / expected_effect`。
- 逐条评论打 job 标签（review_job_labels：row_number/asin/review_id/rating/job_code/evidence_signal）。
- opportunity_focus 优先级依据「覆盖评论数 + 负向数 + 涉及 ASIN 数 + 弱位/强位」，focus_reason 写成"不是只看频次：…"。
- action_recommendations 每条含 `priority / action_area / recommendation / jtbd_trace / evidence_trace（含样本 review_id）/ expected_effect / risk_hedge / confidence / confidence_reason`。

## 9. ASIN-first 竞品击破（本报告签名模块）

按竞品 ASIN 读，不按主题倒推：

1. **击破总控塔**（asin_knockout_control_tower）：每 ASIN 卡给 lane（正面击破/残余破绽/低样本观察/相邻参照/排除否词）、priority、可击破/避战/观察计数、最弱能力、最强/避战能力、primary_opponent、battle_snapshot、claim_to_make、claim_to_avoid、product/listing/ad 动作、监控阈值。
2. **缺陷差异剖面**（asin_defect_difference_profiles）：区分「相对竞品可击破差异 differentiated」vs「共性/标准化 standardized」vs「强项护城河 moat」；每条差异带 target_evidence + peer_evidence + difference_read + knockout_move。
3. **差异证据对照台账**（asin_difference_evidence_ledger）：每行 = 目标 ASIN × 能力：benchmark、score_gap_to_best、目标 1-3★ 负面原声、强位 4-5★ 正面原声、分差、proof gap、验证动作。
4. **1v1 能力对位地图**（asin_pairwise_battle_map）：两两对比输/赢/持平能力 + 击破/避战话术 + 验证路线。
5. **对手定向击破指令**（opponent_specific_attack_directives）：对目标×对手：主张、证据与素材、流量与边界、指标阈值、禁区/下一步。
6. **Listing/素材/广告改写包**（listing_execution_rewrite_packs）：title 角度、bullet 主张、A+ 模块、主图/对比图 caption、PPC headline、搜索词簇、否定词边界、proof/visual 资产、traffic_route、primary/guardrail 指标、go/stop 阈值、review_monitor_trigger。
7. **击破顺序总览**（asin_attack_decision_board）：谁正面击破、谁只打残余、谁低样本观察、谁相邻参照、谁排除否词，附"为什么现在这样打"。
8. **主张上线门禁**（asin_claim_readiness_gates）：7 个 gate = 目标痛点证据 / 标杆强项证据 / 产品证明 / Listing 主张 / 素材资产 / 流量测试 / 成败监控，各 pass/watch/block，输出 readiness_score + status（可上线 A/B / 观察 / 拦截）+ missing_assets + next_action。
9. **A/B 测试队列**（asin_ab_test_queue）：只把门禁通过的主张转测试；其余进 monitor_tasks。每条含 hypothesis / control / treatment / assets / traffic / primary+guardrail 指标 / go_threshold（如连续 14 天 CTR 或 CVR ≥ control 8% 且新增差评不升）/ stop_threshold / review_monitor。
10. **击破资产清单**（winning_spec_blueprint + asin_capability_gap_ledger）：把能力差距翻译成 spec 资产包：spec_name / must_win_requirement / listing_module / creative_asset / ad_test / target_asins / avoid_asins / direct_attack_asins / evidence_quote / max_gap_to_best。

## 10. 时间维度（yearly_drift + theme_yearly_capability + hv）

- 每 ASIN 逐年：`review_count / negative_count / negative_rate / strong_negative_count / strong_negative_rate`，`negative_rate_delta`（最新年 vs 前期），trend_label（近期恶化/稳定/改善/低样本）。
- 每主题×ASIN 逐年能力分：`failure_rate / capability_score / trend_label`。
- 横纵交汇（hv_intersections）：横向弱位 × 纵向恶化 = 优先击破窗口；每条给 `trigger`（如"新增 30 条评论中该主题 1-3★ 明确提及 ≥2，或最新年差评率继续高于前期 X% → 升级复核"）。
- 低样本（如单年 <30 条）判定为噪声，不设触发阈值。

## 11. 证据三角与闭环（evidence_triangles + asin_first_evidence_triangles）

每条攻击 = 三角：
- 目标负面证据（target_failure_quote）+ 强位/标杆正面证明（benchmark_positive_quote）+ 市场证据（目标 vs 标杆评论量）。
- `score_gap`、`proof_gap`（强位正向数 / 弱位正向数、弱位失败数 / 强位失败数）。
- 输出 proof_decision（用标杆正向证明作市场标尺）+ execution_action。

## 12. 多视图阅读环（multi_view_analysis_ring）

把单 ASIN VOC 的视图迁移成多 ASIN 视图并说明"能证明什么/不能证明什么"：
- 口碑健康度 → #quality（覆盖审计）
- 关键词/变体分层 → #precision
- 趋势与异常 → #hv（时间漂移）
- 差评根因 → #complex（主题×ASIN 交叉）
- 场景画像 → #journey（旅程断点）
- 高频表达/正向卖点 → #complex（原声簇 + 正负面翻转）
- 原始评论明细 → #raw-data
每个 curated view 含 `why_selected / data_slice / proves / cannot_prove / decision / target_section`。

## 13. 交付

- 生成 dashboard JSON（按 schema.md 全量字段）+ 单文件 HTML（按 dashboard-html.md）。
- 数据质量审计 + 原始评论明细必须保留。
