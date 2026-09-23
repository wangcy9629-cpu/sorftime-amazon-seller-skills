#!/usr/bin/env bash
# amz-oneclick 工作台启动脚本
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="/c/Users/HUAWEI/.workbuddy/binaries/python/versions/3.13.12/python.exe"
[ -x "$PY" ] || PY="$(command -v python3 || command -v python)"
"$PY" "$HERE/server.py" --port 8787 --open
