# 类目档案构建（category-profile.md）

category_profile 是全部分析的"词典"。先建档案，再跑匹配与分析。
由 `profile_id / display_name / product_name / category_boundary / source / themes / journey_stages / jtbd_jobs / spec_asset_library / report_copy_contract` 组成。

## 1. category_boundary（类目边界）

一句话定义收录范围。示例（GPS 无线电子围栏）：
"GPS-based virtual dog containment systems sold on Amazon US; include fence collars with app-defined boundaries and GPS tracking; exclude in-ground wire fences, radio base wireless fences, GPS trackers only, and training collars only."

## 2. themes（能力主题，9 个左右）

每个主题 = `code / label / keywords[] / action`。keywords 用于标题+正文匹配（含同义/口语表达），action 描述"该能力要证明什么"。
主题必须覆盖：核心性能、环境适配、安全、训练、佩戴/结构、续航、App/安装、追踪、价值/售后。
GPS 无线电子围栏示例（完整词典见原报告，此处列出 code+label+代表性关键词）：
- boundary_accuracy_latency 边界准确/响应延迟：boundary, fence line, drift, spotty, delay, lag, slow to, inconsistent, intermittent, ran through, escaped, gets out, false alert
- signal_environment_fit 卫星信号/环境适配：gps signal, clear sky, sky access, trees, woods, overcast, rain, metal roof, building, cell coverage, wifi, rural, off-grid
- correction_safety_consistency 纠正一致性/安全：shock, static correction, beep, vibrate, burn, injury, high voltage, sporadic, wrong direction, coming back
- training_behavior_learning 训练/犬只学习：train, learned, caught on, recall, flags, leash, stubborn, puppy, rescue dog
- collar_fit_durability 项圈佩戴/结构耐久：collar loose, slips off, strap, buckle, fits, neck, bulky, broke, flimsy, chewed
- battery_charging_reliability 续航/充电可靠：battery, battery life, charge, charger, lasts, quit charging, won't charge
- app_mapping_setup App/建图/安装：app, map, google maps, set up, geo points, custom fence, circular, pin, notification, firmware, connect
- tracking_escape_recovery 越界追踪/找回：track, tracking, location, escaped, outside the boundary, find my dog, coming back
- subscription_value_support 订阅/价值/售后：subscription, fee, price, worth, return, refund, warranty, replacement, customer service, support

## 3. journey_stages（旅程阶段，7 个）

每个 = `code / phase / title / keywords[] / action`：
- Pre-purchase：场地、地形与信号条件判断
- Setup：App 连接、建图与边界校验
- Training：提示音、震动与纠正训练
- Daily use：日常边界触发与犬只安全
- Exception recovery：越界后的追踪与安全回归
- Maintenance：佩戴、续航、充电与结构维护
- After-sales：订阅、退换、质保与替换

## 4. jtbd_jobs（JTBD，6-7 个）

每个 = `job_code / job_name_cn / job_domain / job_step / theme_code / desired_outcome / struggle_moment / switching_trigger / voc_link / evidence_rule / actionability[] / recommendation / risk_hedge / expected_effect`。
- desired_outcome：买前/使用中用户期望的"成功标准"。
- struggle_moment：失败瞬间（对应差评根因）。
- switching_trigger：转向什么条件的 ASIN。
- evidence_rule：哪些评论语言算证据（供匹配复核）。
- actionability：product / firmware / app / safety / QC / listing / visual / support / warranty / pricing / traffic。
- risk_hedge：表达禁区/风险对冲（如"不把最大半径或英亩数写成所有地形都能实现"）。

GPS 示例 7 jobs：
1. choose_system_for_property_and_signal 按场地和信号条件选对系统（fit/compare → signal_environment_fit）
2. contain_dog_with_predictable_boundary 用可预测边界安全限制犬只活动（containment/use → boundary_accuracy_latency）
3. train_with_clear_and_safe_cues 用清晰且安全的提示完成训练（training_safety/train → correction_safety_consistency）
4. keep_collar_powered_and_secure 让项圈持续有电并稳定佩戴（reliability/maintain → battery + collar）
5. build_boundary_without_setup_friction 顺利完成连接、建图和边界测试（setup/install → app_mapping_setup）
6. recover_dog_after_escape 犬只越界后仍能快速定位找回（recovery/recover → tracking_escape_recovery）
7. trust_total_cost_and_support 确认长期成本和售后值得信任（value_trust/support → subscription_value_support）

## 5. spec_asset_library（能力→资产库）

每个主题 = `spec_name / must_win_requirement / listing_module / creative_asset / ad_test`。
GPS 示例（boundary_accuracy_latency）：
- spec_name：边界精度与延迟证据包
- must_win_requirement：证明不同速度和环境下的触发距离、延迟、漂移与回归逻辑
- listing_module：步行/慢跑/冲刺/回归测试 + 安全缓冲 + 失锁状态
- creative_asset：实地走测轨迹、触发点与时间戳对照
- ad_test：边界测试证据版 vs 大面积自由场景版

## 6. report_copy_contract（文案契约，防跑偏）

- `product_noun_cn`（GPS 无线电子围栏）、`purchase_object_cn`（一套 GPS 围栏项圈系统）、`headline_job_code`（主任务）。
- `analysis_slots`：4 个精简报告失败槽位（label + job_code）。
- `audience`：目标人群与关注点。
- `traffic`：core_intent + negative_terms（广告否定词边界，如 "GPS tracker only / AirTag dog collar / in-ground wire fence / training collar only"）。
- `fallbacks`：primary_job / strategy / product_proof 兜底文案。
- `forbidden_generated_terms`：生图/文案禁止出现的不相关产品词。
- `required_visible_terms`：中文报告必须出现的词（如 GPS wireless dog fence / 边界 / 信号 / 项圈 / 训练）。
