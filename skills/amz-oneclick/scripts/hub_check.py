#!/usr/bin/env python3
"""
amz-oneclick 总控台启动体检。

检查两件事：
  1) 子 skill 是否都在本机技能目录（~/.workbuddy/skills/）
  2) Sorftime 数据通道是否可用（MCP 环境变量 / CLI profile）

输出：JSON（stdout）
退出码：
  0 = 子 skill 齐 + 至少一个通道可用
  1 = 缺子 skill 或 无可用通道
"""
import json
import os
import shutil
import subprocess
import sys

SKILLS_ROOT = os.path.expanduser("~/.workbuddy/skills")

REGISTRATION_URL = "https://open.sorftime.com/home?tag=ODY2OA%7E%7E"
DISCOUNT_CODE = "8668"

CORE = [
    "amz-market-analysis",
    "amz-supply-chain",
    "multi-asin-voc-analysis",
    "amz-ad-planning",
    "sorftime-shop-health-monitor",
]

EXTENDED = [
    "amz-selection",
    "amz-profit-calc",
    "amz-cpc-keywords",
    "amz-listing-creator",
    "amz-image-creator",
    "amz-voc-analysis",
    "amz-competitor-monitor",
]


def skill_exists(name: str) -> bool:
    return os.path.isfile(os.path.join(SKILLS_ROOT, name, "SKILL.md"))


def check_mcp() -> bool:
    return bool(os.environ.get("SORFTIME_MCP_KEY", "").strip())


def _find_cli() -> str:
    for cand in ("sorftime", "sorftime.cmd", "sorftime.exe", "sorftime.ps1"):
        p = shutil.which(cand)
        if p:
            return p
    return ""


def check_cli() -> bool:
    exe = _find_cli()
    if exe:
        try:
            r = subprocess.run([exe, "whoami"], capture_output=True,
                               text=True, timeout=15)
            if r.returncode == 0:
                return True
        except Exception:
            pass

    # 兜底：配置目录存在且有配置文件
    cfg = os.path.expanduser("~/.sorftime")
    if os.path.isdir(cfg):
        for fn in os.listdir(cfg):
            if fn.endswith((".json", ".yaml", ".yml", ".toml", ".conf", ".ini")):
                return True
    return False


def main() -> int:
    missing_core = [s for s in CORE if not skill_exists(s)]
    missing_ext = [s for s in EXTENDED if not skill_exists(s)]

    mcp_ok = check_mcp()
    cli_ok = check_cli()

    if mcp_ok and cli_ok:
        channel, chan_msg = "mcp", "MCP+CLI 均可用，默认走 MCP"
    elif mcp_ok:
        channel, chan_msg = "mcp", "仅 MCP 可用"
    elif cli_ok:
        channel, chan_msg = "cli", "仅 CLI 可用（正常路径）"
    else:
        channel, chan_msg = None, (
            "未检测到 Sorftime 凭证。通过专属通道注册并领用 7 天试用（优惠码："
            f"{DISCOUNT_CODE}）：{REGISTRATION_URL}"
        )

    if channel and not missing_core:
        nxt = "就绪：可直接下达「一键 XX」口令"
    elif channel and missing_core:
        nxt = "通道可用，但缺核心子 skill，请补装：" + "、".join(missing_core)
    elif not channel and not missing_core:
        nxt = "子 skill 齐，但无数据通道 —— 先按 message 里的链接注册"
    else:
        nxt = "既缺通道又缺子 skill，先注册通道再做补装"

    result = {
        "skills_root": SKILLS_ROOT,
        "core_ok": not missing_core,
        "missing_core": missing_core,
        "missing_extended": missing_ext,
        "mcp_available": mcp_ok,
        "cli_available": cli_ok,
        "recommended_channel": channel,
        "message": chan_msg,
        "next": nxt,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    ok = bool(channel) and not missing_core
    if not ok:
        print("\n" + (chan_msg if not channel else nxt), file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
