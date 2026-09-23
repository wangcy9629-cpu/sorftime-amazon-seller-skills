#!/usr/bin/env bash
# 安装 Sorftime Amazon Seller Skills 到本机 AI 工具
# 用法：bash install.sh

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$ROOT/skills"

if [ ! -d "$SKILLS_DIR" ]; then
  echo "❌ 找不到 skills/ 目录，请在仓库根目录运行本脚本。"
  exit 1
fi

found=0

install_to() {
  target="$1"
  label="$2"
  if [ -d "$(dirname "$target")" ]; then
    mkdir -p "$target"
    cp -r "$SKILLS_DIR"/. "$target"/
    count=$(ls -1 "$SKILLS_DIR" | wc -l | tr -d ' ')
    echo "✅ $label  ->  $target  ($count 个技能)"
    found=1
  fi
}

echo "开始安装 Sorftime Amazon Seller Skills ..."
echo ""

install_to "$HOME/.workbuddy/skills" "WorkBuddy"
install_to "$HOME/.claude/skills"    "Claude Code"
install_to "$HOME/.codex/skills"     "Codex"

if [ "$found" = "0" ]; then
  echo "⚠️  没检测到已安装的 AI 工具目录。"
  echo "   请手动把 skills/ 下的目录复制到你的 skills 路径。"
fi

echo ""
echo "----------------------------------------"
echo "下一步：配置 Sorftime 数据通道"
echo ""
echo "  npm install -g sorftime-cli"
echo "  sorftime add myprofile <你的 Account-SK>"
echo "  sorftime use myprofile"
echo ""
echo "没有账号？专属通道注册（含 7 天免费试用）："
echo "  https://open.sorftime.com/home?tag=ODY2OA~~   优惠码：8668"
echo "----------------------------------------"
