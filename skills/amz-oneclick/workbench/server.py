#!/usr/bin/env python3
"""
amz-oneclick 本地工作台（零依赖，仅用 Python 标准库）。

功能：
  GET  /                 工作台页面
  GET  /api/status       子 skill 清单 + Sorftime 通道状态 + 工作目录
  GET  /api/runs         历史跑批记录（扫 <workdir>/_work/amz-oneclick/）
  GET  /api/queue        待办队列
  POST /api/queue        派发一条任务到待办队列（Agent 执行时读取）
  POST /api/queue/done   标记/清理待办

用法：
  python server.py [--port 8787] [--workdir <目录>]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS_ROOT = os.path.expanduser("~/.workbuddy/skills")
INDEX = os.path.join(HERE, "index.html")

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

WORKDIR = os.getcwd()


# ---------------- 工具 ----------------

def read_desc(skill: str) -> str:
    """从 SKILL.md frontmatter 里抠 description，截成一句话。"""
    p = os.path.join(SKILLS_ROOT, skill, "SKILL.md")
    if not os.path.isfile(p):
        return ""
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except Exception:
        return ""

    desc, buf, collecting = "", [], False
    for ln in lines[:60]:
        if ln.startswith("description:"):
            rest = ln.split(":", 1)[1].strip()
            if rest in (">", "|", ">-", "|-"):
                collecting = True
                continue
            desc = rest
            break
        if collecting:
            if ln.startswith((" ", "\t")) and ln.strip():
                buf.append(ln.strip())
            elif ln.strip():
                break
    if buf:
        desc = " ".join(buf)

    desc = re.sub(r"\s+", " ", desc).strip().strip('"')
    # 取第一个句号前的核心句，最长 88 字
    cut = desc.find("。")
    if 0 < cut < 88:
        desc = desc[:cut]
    return desc[:88] + ("…" if len(desc) > 88 else "")


def check_channel():
    mcp = bool(os.environ.get("SORFTIME_MCP_KEY", "").strip())
    exe = ""
    for c in ("sorftime", "sorftime.cmd", "sorftime.exe", "sorftime.ps1"):
        exe = shutil.which(c) or ""
        if exe:
            break
    cli = False
    if exe:
        try:
            r = subprocess.run([exe, "whoami"], capture_output=True,
                               text=True, timeout=15)
            cli = r.returncode == 0
        except Exception:
            cli = False
    if not cli:
        cfg = os.path.expanduser("~/.sorftime")
        if os.path.isdir(cfg):
            cli = any(f.endswith((".json", ".yaml", ".yml", ".toml", ".conf", ".ini"))
                      for f in os.listdir(cfg))
    return {
        "mcp_available": mcp,
        "cli_available": cli,
        "channel": "mcp" if mcp else ("cli" if cli else None),
        "sorftime_exe": exe,
    }


def queue_dir() -> str:
    d = os.path.join(WORKDIR, "_work", "amz-oneclick", "_queue")
    os.makedirs(d, exist_ok=True)
    return d


def runs_root() -> str:
    return os.path.join(WORKDIR, "_work", "amz-oneclick")


def list_runs():
    root = runs_root()
    out = []
    if os.path.isdir(root):
        for name in sorted(os.listdir(root), reverse=True):
            d = os.path.join(root, name)
            if name == "_queue" or not os.path.isdir(d):
                continue
            files = os.listdir(d)
            steps = sorted(f for f in files if f.startswith("step"))
            report = next((f for f in files if f.endswith(".html")), "")
            out.append({
                "id": name,
                "dir": d,
                "steps": len(steps),
                "report": os.path.join(d, report) if report else "",
                "report_name": report,
                "mtime": datetime.fromtimestamp(
                    os.path.getmtime(d)).strftime("%Y-%m-%d %H:%M"),
                "files": files[:40],
            })
    return out[:50]


def list_queue():
    d = queue_dir()
    out = []
    for fn in sorted(os.listdir(d), reverse=True):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(d, fn), "r", encoding="utf-8") as f:
                t = json.load(f)
            t["_file"] = fn
            out.append(t)
        except Exception:
            continue
    return out[:80]


# ---------------- HTTP ----------------

class Handler(BaseHTTPRequestHandler):
    server_version = "amz-oneclick-workbench/1.0"

    def log_message(self, fmt, *args):  # 静音
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            if not os.path.isfile(INDEX):
                return self._send(500, "index.html missing", "text/plain; charset=utf-8")
            with open(INDEX, "r", encoding="utf-8") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")
        if path == "/api/status":
            skills = []
            for group, names in (("core", CORE), ("extended", EXTENDED)):
                for n in names:
                    skills.append({
                        "name": n,
                        "group": group,
                        "ok": os.path.isfile(os.path.join(SKILLS_ROOT, n, "SKILL.md")),
                        "desc": read_desc(n),
                    })
            return self._json({
                "skills": skills,
                "channel": check_channel(),
                "workdir": WORKDIR,
                "skills_root": SKILLS_ROOT,
                "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        if path == "/api/runs":
            return self._json({"runs": list_runs(), "root": runs_root()})
        if path == "/api/queue":
            return self._json({"queue": list_queue()})
        return self._json({"error": "not found"}, 404)

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            n = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json({"error": "bad json"}, 400)

        if path == "/api/queue":
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            item = {
                "id": ts,
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pipeline": payload.get("pipeline", ""),
                "pipeline_name": payload.get("pipeline_name", ""),
                "params": payload.get("params", {}),
                "instruction": payload.get("instruction", ""),
                "status": "pending",
            }
            with open(os.path.join(queue_dir(), f"{ts}.json"), "w", encoding="utf-8") as f:
                json.dump(item, f, ensure_ascii=False, indent=2)
            return self._json({"ok": True, "task": item})

        if path == "/api/queue/clear":
            d = queue_dir()
            removed = 0
            for fn in os.listdir(d):
                if fn.endswith(".json") and payload.get("all"):
                    os.remove(os.path.join(d, fn))
                    removed += 1
            return self._json({"ok": True, "removed": removed})

        return self._json({"error": "not found"}, 404)


def main():
    global WORKDIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--workdir", default=os.getcwd())
    ap.add_argument("--open", action="store_true", help="启动后自动打开浏览器")
    a = ap.parse_args()
    WORKDIR = os.path.abspath(a.workdir)

    port = a.port
    for attempt in range(12):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            port += 1
    else:
        print("找不到可用端口", file=sys.stderr)
        return 1

    url = f"http://127.0.0.1:{port}/"
    print(f"[amz-oneclick] 工作台已启动: {url}")
    print(f"[amz-oneclick] 工作目录: {WORKDIR}")
    print("[amz-oneclick] Ctrl+C 停止")
    if a.open:
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[amz-oneclick] 已停止")
    return 0


if __name__ == "__main__":
    sys.exit(main())
