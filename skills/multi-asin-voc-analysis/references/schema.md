# Dashboard JSON 数据契约（schema.md）

渲染器从单一 JSON payload 读全部数据（`dashboard_schema_version: multi-asin-voc-dashboard-v1`）。
顶层键必须齐全；缺数据的键用 null / 空数组，绝不填假值。

## 顶层键

```
dashboard_schema_version, generated_at,
fresh_run_lineage        {schema_version, run_id, invocation_id, started_at, acquired_at, product_name, representative_asin, fresh_acquisition, reuse_mode, run_directory_name, sources[]}
review_sufficiency_gate  {schema_version, status, formal_release_allowed, full_data_claim_allowed, review_completeness_policy, asin_count, data_scope_reconciliation_count, coverage_gap_asin_count, failed_asin_count, asins[], run_id, lineage_status, frontend_audit_path}
delivery_contract        {mode, report_classification, report_delivery_status, must_render_full_structure, available_review_count, asin_count, source_status, source_report_status, review_completeness_policy, full_data_claim_allowed, notice_title, notice_body}
source_paths             {portfolio, manifest, report_markdown}
portfolio_meta           {portfolio_name, marketplace, asin_count, total_review_count, expected_review_count, source_total_review_count, coverage_rate, source_status, negative_definition, positive_definition, excluded_older_review_count, review_window_start, review_window_end, collection_scope, report_status, product_name, category_profile_id, commercial_metrics_status}
run_meta                 {portfolio_name, marketplace, keyword, review_window_start, review_window_end, ranking_basis, product_name, category_profile_id, category_profile_source, commercial_metrics_status}
aggregate_overview       {total_asins, total_reviews, expected_review_count, coverage_rate, avg_rating, negative_count, negative_rate, strong_negative_count, strong_negative_rate, positive_count, positive_rate, vp_rate, total_helpful_votes, negative_helpful_total, helpful_negative_vote_share, source_status_counts}
rating_distribution[]    {rating, label, review_count, review_share}
asin_summaries[]         {asin, label, role(benchmark|competitor), marketplace, input_path, source, review_count, expected_review_count, coverage_rate, source_status, avg_rating, negative_count, negative_rate, strong_negative_count, strong_negative_rate, positive_count, positive_rate, vp_rate, helpful_risk_score, helpful_negative_vote_share, traceability_limited, low_sample_flag, risk_tier, relevance_status, keyword_monthly_sales, keyword_sales_share, brand, title, source_review_count, excluded_older_review_count}
cross_asin_comparison[]  与 asin_summaries 同构（横向比较卡）
keyword_segments[]       {status(core|adjacent|noise), label, asin_list, asin_count, keyword_monthly_sales, keyword_sales_share, review_count, decision}
yearly_drift[]           {asin, label, role, relevance_status, years[{year, review_count, negative_count, negative_rate, strong_negative_count, strong_negative_rate}], interpretation}
asin_yearly_drift_verdicts {lead, summary{asin_count, risk_count, watch_count, boundary_count}, cards[{asin, label, lane, tone, latest_year, latest_review_count, latest_negative_rate, latest_strong_negative_rate, prior_negative_rate, negative_rate_delta, negative_rate_spread, year_series[], theme_label, score_gap, benchmark_asin, weakness_count, strength_count, decision, action, trigger, table_interpretation}]}
theme_matrix[]           {code, label, total_negative_mentions, core_negative_mentions, adjacent_negative_mentions, portfolio_problem_rate, asin_cells[{asin, label, relevance_status, mention_count, negative_count, review_count, problem_rate, all_review_rate, rate_delta_vs_portfolio, position_type, position_label, evidence[]}]}
asin_first_theme_evidence_matrix {lead, rows[], summary}
asin_theme_competitor_verdicts  {lead, summary, cards[]}
competitive_attack_map[] {asin, label, priority, position, review_count, negative_rate, strengths[], weaknesses[], avoid[], claims, verification}
capability_competition_matrix[] {theme_code, theme_label, cells[{asin, label, relevance_status, review_count, keyword_monthly_sales, positive_mentions, negative_mentions, strong_negative_mentions, positive_rate, failure_rate, strong_failure_rate, capability_score, confidence, positive_evidence[], negative_evidence[]}]}
competitor_battlecards[] {asin, label, relevance_status, priority, position, review_count, keyword_monthly_sales, negative_rate, strengths[], weaknesses[], avoid[], claims, verification}
strategic_attack_routes[] {theme_code, theme_label, priority, target_asin, target_label, avoid_asin, avoid_label, score_gap, target_failure_rate, target_score, avoid_score, route}
theme_yearly_capability[] {theme_code, theme_label, years[], recent_years[], prior_years[], cells[{asin, label, relevance_status, years[{year, review_count, positive_mentions, negative_mentions, strong_negative_mentions, failure_rate, capability_score}], recent_* , prior_*, failure_rate_delta, trend_label}]}
hv_competitive_intersections[] {job_code, job_name_cn, type, horizontal_signal, vertical_signal, hv_source_signal, decision, trigger, confidence}
asin_time_strike_routes   {lead, summary, cards[]}
asin_competitive_command_center {lead, asin_cards[], dimension_rankings[], summary}
asin_competitive_delta_control {lead, cards[], summary}
asin_knockout_control_tower  {lead, cards[{asin, label, lane, priority, sequence, relevance_status, keyword_monthly_sales, review_count, negative_rate, avg_rating, strong_negative_rate, attackable_count, avoid_count, watch_count, knockout_focus, weakest_capability, strongest_or_avoid_capability, primary_opponent, battle_snapshot, claim_to_make, claim_to_avoid, product_move, listing_move, ad_move, metrics, trigger}], summary}
asin_defect_difference_profiles {lead, profiles[{asin, label, lane, priority, position, review_count, differentiated_attack_count, standardized_count, moat_count, rejected_evidence_count, differentiated_attacks[{theme_code, theme_label, command_label, capability_score, score_gap_to_best, negative_mentions, positive_mentions, peer_best_asin, target_evidence, peer_evidence, evidence_status, target_match_terms, peer_match_terms, difference_read, knockout_move}]}], summary}
asin_difference_evidence_ledger {lead, rows[{asin, label, lane, priority, theme_code, theme_label, command_label, benchmark_asin, score_gap_to_best, target_negative_mentions, target_positive_mentions, benchmark_positive_mentions, benchmark_negative_mentions, target_negative_evidence, benchmark_positive_evidence, target_positive_evidence, proof_gap, validation_action}], summary}
asin_pairwise_battle_map {lead, battles[{target_asin, opponent_asin, battle_type, loss_count, residual_count, win_count, loss_capabilities[], win_capabilities[], tie_capabilities[], attack_language, avoid_language, validation_route}], summary}
opponent_specific_attack_directives {lead, directives[{target_asin, opponent_asin, theme_code, theme_label, claim, evidence_assets, traffic_boundaries, metrics_thresholds, no_go, next_step}], summary}
listing_execution_rewrite_packs {lead, packs[{pack_id, target_asin, opponent_asin, directive_type, theme_code, theme_label, title_angle, bullet_claim, aplus_module, main_image_caption, comparison_image_caption, ppc_headline, search_term_cluster, negative_boundary_terms, proof_asset, visual_asset, traffic_route, evidence_quote, primary_metric, guardrail_metric, go_threshold, stop_threshold, review_monitor_trigger, owner_ready_next_action}], summary}
asin_attack_decision_board {lead, rows[{sequence, asin, lane, priority, main_attack, avoid, why_now, product_ad_actions}], summary}
asin_1v1_attack_playbooks {lead, playbooks[{sequence, target_asin, opponent_asin, benchmark, sayable_claims, expression_prohibitions, evidence_assets, traffic_test, thresholds}], summary}
asin_differentiation_dossiers {lead, dossiers[{asin, label, attackable_weaknesses[], avoid_strengths[], capability_spectrum[], next_actions}], summary}
asin_capability_matchup_board {lead, asin_columns[], rows[{theme_code, theme_label, asin_cells[{asin, score, tone, verdict}]}], scoreboard[], summary}
asin_strike_packages {lead, packages[{asin, target, attack_chain[], borrow_avoid[], evidence_assets[], traffic_monitoring[]}], summary}
asin_strike_evidence_chains {lead, packages[{asin, theme_code, theme_label, target_negative_evidence, benchmark_positive_evidence, claim, product_proof, assets_traffic_validation}], flat_chains[], summary}
asin_claim_readiness_gates {lead, rows[{asin, label, lane, priority, decision_score, readiness_score, status, gate_pass_count, gate_watch_count, gate_blocked_count, chain_count, target_evidence_count, benchmark_evidence_count, gates[{name, status, evidence, missing}], missing_assets[], next_action}], summary}
asin_ab_test_queue {lead, queue[{test_id, asin, label, lane, priority, theme_code, theme_label, benchmark_asin, readiness_score, hypothesis, control, treatment, listing_asset, creative_asset, traffic_setup, primary_metric, guardrail_metric, go_threshold, stop_threshold, review_monitor, evidence_quote}], monitor_tasks[], summary}
asin_capability_gap_ledger {lead, asin_ledgers[], flat_rows[], summary}
winning_spec_blueprint {lead, spec_cards[{theme_code, theme_label, priority, spec_name, must_win_requirement, listing_module, creative_asset, ad_test, target_asins[], avoid_asins[], direct_attack_asins[], evidence_quote, max_gap_to_best, negative_mentions, positive_mentions}], summary}
asin_tactical_profiles[] {asin, label, moats[], weaknesses[], product_move[], listing_move[], creative_move[], traffic_move[]}
multi_view_analysis_ring {lead, center, asin_routes{routes[]}, reference_sources[{name, reference_pattern, borrowed_structure, fit_to_product, why_selected}], process_steps[{step, input, view, readout, handoff}], curated_view_cards[{view, why_selected, data_slice, proves, cannot_prove, decision, target_section}], spokes[{code, title, reference_view, question, data_slice, metric_label, metric_value, weight, finding, action, tone, target_section}], reference_bridges[{reference, multi_asin_view, section, decision}], summary}
complex_analysis_module {lead, negative_denominator, positive_denominator, asin_first_briefs[], asin_voice_competitive_playbooks[], lens_cards[{title, question, data_scope, finding, action, tone}], root_cause{label, heading, description, rows[{priority, theme_code, theme_label, mentions, core_mentions, negative_share, weak_asin, weak_rate, strong_asin, strong_rate, evidence, interpretation, action}]}, demand_analysis{label, heading, description, motives[{label, count, share, asin, asin_count, evidence, read}]}, sentiment_comparison{label, heading, description, rows[{theme_code, theme_label, positive_count, negative_count, flip_ratio, positive_asin, negative_asin, positive_evidence, negative_evidence}]}, voice_clusters[{theme_code, theme_label, negative_mentions, positive_mentions, negative_terms[], positive_terms[], negative_voice, positive_voice, interpretation}]}
jtbd_taxonomy[]          {job_code, job_name_cn, job_domain, job_step, theme_code, desired_outcome, struggle_moment, switching_trigger, voc_link, evidence_rule, actionability[], recommendation, risk_hedge, expected_effect}
review_job_labels[]      {row_number, asin, review_id, rating, job_code, evidence_signal}
core_jobs[], desired_outcomes[], struggle_moments[], switching_triggers[]  (jtbd 各列视图)
opportunity_focus[]      {job_code, job_name_cn, priority, priority_basis, focus_reason, recommended_action}
hv_horizontal_view[], hv_vertical_view[], hv_intersections[] (见 hv_competitive_intersections)
action_recommendations[] {priority, action_area, recommendation, jtbd_trace, evidence_trace, focus_reason, expected_effect, risk_hedge, confidence, confidence_reason}
evidence_revalidation    {raw_review_records, expected_review_count, coverage_rate, fetched_pages, missing_pages, missing_review_url_count, synthetic_review_id_count, traceability_level, sampled_evidence[], checks[]}
jtbd_strategy_module     {core_jobs, opportunity_focus, hv_intersections, action_recommendations, evidence_revalidation}
sentiment_flip_matrix[]  {theme_code, theme_label, positive_count, negative_count, flip_ratio, top_positive_asin, top_positive_label, top_positive_count, top_negative_asin, top_negative_label, top_negative_count, positive_evidence[], negative_evidence[]}
journey_competition_map[] {code, phase, title, mention_count, positive_count, negative_count, negative_rate, top_weak_asin, top_weak_label, top_weak_count, top_strong_asin, top_strong_label, top_strong_count, action, interpretation}
asin_journey_competitive_routes {lead, summary, cards[]}
asin_first_journey_flip_playbooks {summary, lead, cards[]}
asin_evidence_closure_board {lead, summary, cards[]}
asin_first_evidence_triangles {lead, rows[], summary}
evidence_triangles[]      {rank, capability, lane, tone, target_asin, target_label, target_review_count, target_score, target_failure_mentions, target_positive_mentions, target_failure_quote, benchmark_asin, benchmark_label, benchmark_review_count, benchmark_score, benchmark_positive_mentions, benchmark_failure_mentions, benchmark_positive_quote, score_gap, proof_gap, target_failure_evidence, benchmark_proof_evidence, market_evidence, proof_decision, execution_action}
page_audit[]             {asin, label, source_path, pages_reported, fetched_pages, missing_pages, review_window_start, review_window_end, raw_reviews_in_window, excluded_older_review_count, collection_scope, page_data_status, status}
quality_summary           {source_status, raw_review_records, source_raw_review_records, excluded_older_review_count, unknown_date_review_count, expected_review_count, coverage_rate, asin_count, traceability_limited_asin_count, low_sample_asin_count, pages_reported, fetched_pages, missing_pages, page_data_status, review_window_start, review_window_end, missing_review_url_count, synthetic_review_id_count, source_missing_review_url_count, source_synthetic_review_id_count, traceability_label}
product_cards[]           {asin, label, brand, title, price, node, rank, monthly_sales, review_count, image}
product_data_quality      {source_path, card_count, image_card_count, local_image_card_count, placeholder_card_count, rank_card_count, rank_missing_count, rank_missing_asins, enriched_card_count, manifest_only_card_count, embedded_image_card_count, single_file_status}
raw_review_records[]      {row_number, review_id, asin, rating, sentiment_group, title, content, review_date, review_month, verified_purchase, helpful_count, style, review_url, has_image, has_video, source, source_row_index, asin_row_number, portfolio_label, portfolio_role}
raw_review_records_source[], excluded_older_review_records[]  (同 raw_review_records 结构)
category_profile          (见 references/category-profile.md)
single_file_quality       {status, product_card_count, embedded_product_image_count, embedded_product_image_bytes, active_relative_product_image_count, external_only_product_image_asins, missing_product_image_asins, delivery_contract}
```

## evidence 对象（所有证据共用）

`{asin, rating, date, title, quote, review_id, review_url, source, asin_row_number, matched_terms[], matched_field, matched_spans[{field, term, start, end, text}], quote_source_field}`

## 数值口径

- 负向=1-3★，强负向=1-2★，正向=4-5★。
- `problem_rate = mention_count / negative_count`；`all_review_rate = mention_count / review_count`；`rate_delta_vs_portfolio = problem_rate - portfolio_problem_rate`。
- `failure_rate = negative_mentions / review_count`；`flip_ratio = negative_count / (positive_count + negative_count)`。
- `capability_score`：0-100，全库同一公式（正向密度 − 加权失败密度），低=弱。
- `score_gap_to_best = 标杆分数 − 目标分数`。
- 置信度：追溯受限（SYN-* ID）一律 medium；低样本（<30 条）标注 low-sample。
