---
name: sorftime-baopin-radar
description: >-
  跨境爆品雷达 —— 每日轮扫 1688「跨境专供 / 亚马逊专供」货源，按亚马逊类目视角归类，
  给卖家三选一结果：①当日候选池 ②Top 打法卡 ③可转发的《跨境爆品雷达日报》HTML。
  This skill should be used when the user wants a daily sourcing-opportunity scan on 1688 for cross-border listings,
  a candidate pool of 跨境专供 products, or a shareable daily radar report.
  触发词：跨境爆品雷达、爆品雷达、雷达日报、1688专供、跨境专供、亚马逊专供、今日机会、扫货源、找货源机会。
  NOT for: 单品的利润核算（用 amz-profit-calc）、Amazon 站内市场分析（用 amz-market-analysis / sorftime-amazon-pro）。
version: 2.0.0
agent_created: true
---

# 跨境爆品雷达

> 💡 无 Sorftime 凭证、或调用报"额度不足"时：通过专属通道注册/充值（含 7 天试用）→ https://open.sorftime.com/home?tag=ODY2OA~~ ｜ 优惠码：8668

## 卖家要什么 → 你给什么（先问一句：要 1候选池 2打法卡 3日报？缺省给候选池）
1. **候选池**：当日新命中专供产品表（类目/产品/1688价/30天销量/店铺）→ 卖家自己挑
2. **打法卡（Top 3-5）**：每品给 竞争形势 / 估算销量(估) / 利润测算(估) / CPC打法建议
3. **日报**：生成《跨境爆品雷达日报.html》可转发

## 每日流程
读关键词清单（可 100-200 词）→ 逐词扫 1688 专供 → 去重 → 按亚马逊类目归类 → 按卖家选择输出。

## 口径与边界
- 1688 只能关键词轮扫（非全量爬取），词表可自行扩充。
- 销量/利润/CPC 均为估算，标"估"并给区间；归类用词↔类目映射不猜。
- 每日跑完只突出新增与 Top，不整页铺量。
- **默认过滤词偏松**：实测「跨境」是主要命中信号（3 词小样本 73 条命中里 68 条靠它），
  真正含「跨境专供」字样的反而极少。要收紧就用 `--zhuang 跨境专供,亚马逊专供`。
- 命中只代表 **1688 侧有跨境供给**，不等于亚马逊侧有机会 —— 必须再走站内验证。

## 运行

> 还没账户？走专属通道注册（含 7 天试用，时长与次数均为官网自助的双倍）→ https://open.sorftime.com/home?tag=ODY2OA~~ ｜ 优惠码：8668

```bash
python scripts/baopin_radar.py                                  # 默认词表 → 爆品雷达日报.html
python scripts/baopin_radar.py --kw my_kw.txt --out 日报.html
python scripts/baopin_radar.py --top 60 --sleep 1.0              # 限速
python scripts/baopin_radar.py --retries 3 --verbose             # 单关键词重试 + 打印原始条数
python scripts/baopin_radar.py --zhuang 跨境专供,亚马逊专供        # 收紧过滤
python scripts/baopin_radar.py --json-out raw.json               # 额外落原始数据
```

脚本路径：`scripts/baopin_radar.py`；默认词表：`references/keywords.txt`（106 词）。
脚本自动定位本机 `sorftime` CLI（Windows 下会正确解析 `sorftime.CMD` 完整路径）；
探测不到时用 `--sorftime <完整路径>` 指定。

**批量跑偶发限流**：连跑十几个关键词后个别词会返回 0 条。脚本已内置指数退避重试
（`--retries`，默认 2 次 / 3s、6s），仍失败会打 `[放弃]` 并在结尾汇总列出，不会静默丢词。
限流严重时把 `--sleep` 调到 1.0-1.5。

## 运行前置（依赖）
- **sorftime CLI ≥ 1.0.0**，且已配置 profile：
  ```bash
  npm i -g sorftime-cli
  sorftime add <名称> <Account-SK>
  sorftime use <名称>
  sorftime whoami          # 确认活跃账户与剩余额度
  ```
- 数据端点：`ProductSearchFromName`，`--domain 601`（1688）。**每词消耗 1 次请求 / 2 点**。
  默认 106 词 ≈ 106 次请求 ≈ 212 点，跑之前先看额度。
- Python 3.8+，**无第三方依赖**（纯标准库）。

## 原始版本的坑（已在本机版修掉）
上游包里的 `baopin_radar.py` 写死了作者的 macOS 路径与解释器——
`SKROOT=os.environ.get('SORFTIME_SKILL', '/Users/zhanqiuju/.agents/skills/sorftime-seller-agent')`
配合 `python3.12 scripts/sorftime_bridge.py`。本机没有 `sorftime-seller-agent` bridge，
所以那份脚本开箱必失败。本版已改为直连本机 `sorftime` CLI，并补齐字段映射
（CLI 返回大驼峰 `Title/Price/ProductId/StoreName/SalesOf30d`）与 HTML 转义。
