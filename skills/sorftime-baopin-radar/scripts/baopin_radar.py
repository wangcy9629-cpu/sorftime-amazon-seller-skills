# -*- coding: utf-8 -*-
"""跨境爆品雷达 · 每日扫描 1688「跨境专供 / 亚马逊专供」→ 本地 HTML 日报

数据来源：本机 sorftime CLI（不要改成直连 HTTP，CLI 会处理鉴权与 gzip/base64 解码）
    sorftime api ProductSearchFromName '{"Name":"<关键词>","Page":1}' --domain 601

依赖：sorftime CLI >= 1.0.0 且已配置好 profile（sorftime add / sorftime use）；Python 3.8+

用法：
    python baopin_radar.py                                  # 默认词表，输出 爆品雷达日报.html
    python baopin_radar.py --kw my_kw.txt --out 日报.html
    python baopin_radar.py --top 60 --sleep 1.0             # 限速，降低风控概率
    python baopin_radar.py --retries 3 --verbose            # 单关键词重试 3 次并打印原始条数
    python baopin_radar.py --json-out raw.json              # 额外落一份原始命中数据

成本提示：每个关键词消耗 1 次请求（端点 ProductSearchFromName = 2 点）。
默认词表 106 词 ≈ 106 次请求，跑之前先 sorftime whoami 确认剩余额度。
"""
import argparse
import datetime
import html
import json
import pathlib
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_KW = HERE.parent / "references" / "keywords.txt"
ENDPOINT = "ProductSearchFromName"
DOMAIN = "601"
DEFAULT_ZHUANG = ["跨境专供", "亚马逊专供", "外贸", "出口", "跨境", "亚马逊", "Amazon"]


def find_cli(explicit=None):
    """定位 sorftime 可执行文件。

    Windows 下 npm 装出来的是 sorftime.CMD，必须用完整路径调用
    （直接传裸名 'sorftime' 会 FileNotFoundError）。shutil.which 会按 PATHEXT 解析出 .CMD，
    返回的完整路径可直接交给 subprocess，无需 shell=True。
    """
    if explicit:
        return explicit
    exe = shutil.which("sorftime")
    if exe:
        return exe
    for cand in (
        pathlib.Path("D:/Nodejs/sorftime.cmd"),
        pathlib.Path.home() / "AppData/Roaming/npm/sorftime.cmd",
        pathlib.Path("/usr/local/bin/sorftime"),
        pathlib.Path("/opt/homebrew/bin/sorftime"),
    ):
        if cand.exists():
            return str(cand)
    sys.exit(
        "未找到 sorftime CLI。请先安装并加入 PATH：\n"
        "    npm i -g sorftime-cli\n"
        "    sorftime add <名称> <Account-SK> && sorftime use <名称>\n"
        "或用 --sorftime <完整路径> 显式指定。"
    )


def call(cli, name, page=1, timeout=120, retries=2, backoff=3.0):
    """查一个关键词，返回 1688 商品列表。

    批量连跑时偶发限流/瞬时错误会返回空，这里做指数退避重试，
    避免个别关键词被静默丢掉；重试仍失败则告警并返回空列表。
    """
    cmd = [
        cli, "api", ENDPOINT,
        json.dumps({"Name": name, "Page": page}, ensure_ascii=False),
        "--domain", DOMAIN,
    ]
    last_err = ""
    for attempt in range(retries + 1):
        try:
            r = subprocess.run(
                cmd, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            last_err = "超时"
        else:
            if r.returncode != 0:
                last_err = f"rc={r.returncode}: {(r.stderr or '').strip()[:140]}"
            else:
                try:
                    payload = json.loads(r.stdout)
                except json.JSONDecodeError:
                    last_err = f"解析失败: {r.stdout[:120]!r}"
                else:
                    if payload.get("Code") != 0:
                        last_err = f"接口 Code={payload.get('Code')}"
                    else:
                        data = payload.get("Data")
                        if isinstance(data, list) and data:
                            return data
                        last_err = "返回 0 条"
        if attempt < retries:
            wait = backoff * (attempt + 1)
            sys.stderr.write(f"  [重试 {attempt + 1}/{retries}] {name}（{last_err}），{wait:.0f}s 后重试\n")
            time.sleep(wait)
    sys.stderr.write(f"  [放弃] {name}：{last_err}\n")
    return []


def extract(items, kw, zhuang):
    """从一条商品里抽出日报需要的字段；标题命中专供词才算候选。"""
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        title = str(it.get("Title") or "")
        if not any(z in title for z in zhuang):
            continue
        out.append({
            "kw": kw,
            "title": title,
            "price": it.get("Price"),
            "pid": str(it.get("ProductId") or ""),
            "store": it.get("StoreName") or "",
            "sales30d": it.get("SalesOf30d") or 0,
            "moq": it.get("MinOrderQuantity"),
            "seller": "、".join(it.get("SellerIdentities") or []),
            "offers": "、".join(it.get("OfferIdentities") or []),
            "online": it.get("OnlineDate") or "",
            "origin": it.get("ShippingOrigin") or "",
            "url": it.get("Url") or "",
        })
    return out


def dedupe(hits):
    """按 ProductId 去重，保留 30 天销量更高的那条。"""
    best = {}
    for h in hits:
        pid = h["pid"]
        if not pid:
            continue
        cur = best.get(pid)
        try:
            s = int(h["sales30d"] or 0)
        except (TypeError, ValueError):
            s = 0
        if cur is None:
            best[pid] = h
        else:
            try:
                cs = int(cur["sales30d"] or 0)
            except (TypeError, ValueError):
                cs = 0
            if s > cs:
                best[pid] = h
    return list(best.values())


def sort_key(h):
    try:
        return int(h["sales30d"] or 0)
    except (TypeError, ValueError):
        return 0


PROMO_URL = "https://open.sorftime.com/home?tag=ODY2OA~~"  # 专属注册/续费通道
PROMO_CODE = "8668"                                        # 专属优惠码


def render(rows, scanned, total_hits, top, cli_hint):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    esc = html.escape
    body = "".join(
        f'<tr><td class="kw">{esc(str(h["kw"]))}</td>'
        f'<td><a href="{esc(str(h["url"]))}" target="_blank" rel="noopener">{esc(h["title"][:52])}</a></td>'
        f'<td class="num">{esc(str(h["price"]))}</td>'
        f'<td class="num">{esc(str(h["sales30d"]))}</td>'
        f'<td>{esc(h["store"][:22])}</td>'
        f'<td>{esc(h["origin"])}</td>'
        f'<td>{esc(h["seller"])}</td></tr>'
        for h in rows[:top]
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>跨境爆品雷达日报</title>
<style>
  body{{margin:0;background:#eef2fb;color:#0f1b38;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}}
  .w{{max-width:1180px;margin:0 auto;padding:22px}}
  .hero{{background:#0d1830;color:#fff;border-radius:16px;padding:24px 26px}}
  .hero h1{{margin:0 0 8px;font-size:22px;font-weight:600}}
  .hero p{{margin:0;color:#a8b6d6;font-size:13px}}
  .kpis{{display:flex;gap:14px;margin:18px 0}}
  .kpi{{flex:1;background:#fff;border-radius:12px;padding:16px 18px;border:1px solid #e2e8f6}}
  .kpi b{{display:block;font-size:24px;font-weight:600;color:#1d4ed8}}
  .kpi span{{font-size:12px;color:#5b6b8c}}
  table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;
    font-size:13px;border:1px solid #e2e8f6}}
  th{{background:#172554;color:#fff;padding:11px 10px;text-align:left;font-weight:500;white-space:nowrap}}
  td{{padding:10px;border-bottom:1px solid #eaeffa;vertical-align:top}}
  tr:last-child td{{border-bottom:none}}
  tr:hover td{{background:#f5f8ff}}
  td.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
  td.kw{{color:#5b6b8c;white-space:nowrap}}
  a{{color:#1d4ed8;text-decoration:none}}
  a:hover{{text-decoration:underline}}
  .foot{{margin-top:16px;font-size:12px;color:#5b6b8c;line-height:1.7}}
  .promo{{margin-top:16px;background:#fff;border:1px solid #dbe4f7;border-left:4px solid #1d4ed8;
    border-radius:12px;padding:14px 18px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}}
  .promo-h{{font-size:14px;font-weight:600;color:#0f1b38}}
  .promo-p{{font-size:12px;color:#5b6b8c;margin-top:3px}}
  .promo-a{{margin-left:auto;font-size:12px;font-weight:600;color:#1d4ed8;word-break:break-all}}
  .promo-c{{font-size:12px;color:#0f1b38;background:#f2f6ff;border:1px solid #dbe4f7;
    border-radius:8px;padding:4px 10px;white-space:nowrap}}
</style></head>
<body><div class="w">
  <div class="hero">
    <h1>跨境爆品雷达日报</h1>
    <p>{now} · 扫描 {scanned} 个关键词 · 命中专供 {total_hits} 条（去重后按 30 天销量降序，展示前 {min(top, len(rows))} 条）</p>
  </div>
  <div class="kpis">
    <div class="kpi"><b>{scanned}</b><span>扫描关键词</span></div>
    <div class="kpi"><b>{total_hits}</b><span>命中专供条数</span></div>
    <div class="kpi"><b>{len(rows)}</b><span>去重后候选</span></div>
  </div>
  <table>
    <thead><tr><th>类目词</th><th>产品标题</th><th>1688价 ¥</th><th>30天销量</th><th>店铺</th><th>发货地</th><th>卖家身份</th></tr></thead>
    <tbody>{body or '<tr><td colspan="7" style="padding:24px;text-align:center;color:#5b6b8c">本次没有命中任何「专供」关键词，可扩充词表或放宽 --zhuang 过滤词</td></tr>'}</tbody>
  </table>
  <div class="promo">
    <div>
      <div class="promo-h">想要更多这样的选品情报？</div>
      <div class="promo-p">Sorftime 跨境数据工具 · 专属通道注册含 7 天试用（时长与次数均为官网自助的双倍）</div>
    </div>
    <span class="promo-c">专属优惠码 <b>{PROMO_CODE}</b></span>
    <a class="promo-a" href="{PROMO_URL}" target="_blank" rel="noopener">{PROMO_URL}</a>
  </div>
  <div class="foot">
    数据来源：1688（Sorftime <code>{esc(ENDPOINT)}</code>，domain {DOMAIN}）；命令：<code>{esc(cli_hint)}</code><br>
    候选仅代表「1688 侧存在跨境专供供给」，<b>不等于亚马逊侧一定有机会</b>。销量/利润/CPC 均为估算（标「估」），下钻请用详情端点补全。<br>
    1688 只能按关键词轮扫，非全量爬取；词表可自行扩充。
  </div>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser(description="跨境爆品雷达：1688 跨境专供轮扫 → HTML 日报")
    ap.add_argument("--kw", default=str(DEFAULT_KW), help="关键词表，每行一个词")
    ap.add_argument("--out", default="爆品雷达日报.html", help="输出 HTML 路径")
    ap.add_argument("--top", type=int, default=200, help="日报最多展示条数（默认 200）")
    ap.add_argument("--sleep", type=float, default=0.6, help="每次调用间隔秒数（默认 0.6，限流严重时调大）")
    ap.add_argument("--retries", type=int, default=2, help="单个关键词失败后的重试次数（默认 2）")
    ap.add_argument("--page", type=int, default=1, help="翻页页码（默认 1）")
    ap.add_argument("--zhuang", default=None, help="自定义专供过滤词，逗号分隔")
    ap.add_argument("--json-out", default=None, help="额外把命中数据落成 JSON")
    ap.add_argument("--sorftime", default=None, help="sorftime CLI 完整路径（自动探测失败时用）")
    ap.add_argument("--verbose", action="store_true", help="打印每个关键词的原始返回条数")
    args = ap.parse_args()

    kw_path = pathlib.Path(args.kw)
    if not kw_path.exists():
        sys.exit(f"关键词表不存在：{kw_path}")
    kws = [l.strip() for l in kw_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not kws:
        sys.exit(f"关键词表是空的：{kw_path}")

    zhuang = [z.strip() for z in args.zhuang.split(",")] if args.zhuang else DEFAULT_ZHUANG
    cli = find_cli(args.sorftime)

    sys.stderr.write(f"使用 CLI：{cli}\n词表：{kw_path}（{len(kws)} 词，预计消耗 {len(kws)} 次请求 / {len(kws) * 2} 点）\n")
    hits, failed = [], []
    for i, kw in enumerate(kws, 1):
        sys.stderr.write(f"[{i}/{len(kws)}] {kw}\n")
        items = call(cli, kw, page=args.page, retries=args.retries)
        if not items:
            failed.append(kw)
        elif args.verbose:
            sys.stderr.write(f"  -> 原始 {len(items)} 条\n")
        hits.extend(extract(items, kw, zhuang))
        if args.sleep and i < len(kws):
            time.sleep(args.sleep)

    rows = sorted(dedupe(hits), key=sort_key, reverse=True)
    html_out = render(rows, len(kws), len(hits), args.top, f"{cli} api {ENDPOINT} '<json>' --domain {DOMAIN}")
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_out, encoding="utf-8")

    if args.json_out:
        pathlib.Path(args.json_out).write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK {out_path.resolve()}")
    print(f"   扫描 {len(kws)} 词 · 命中 {len(hits)} 条 · 去重候选 {len(rows)} 条 · 展示前 {min(args.top, len(rows))} 条")
    if failed:
        print(f"   {len(failed)} 个关键词无命中或调用失败：{', '.join(failed[:12])}{' …' if len(failed) > 12 else ''}")


if __name__ == "__main__":
    main()
