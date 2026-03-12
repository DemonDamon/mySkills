#!/bin/bash
# github-hunter 快捷启动脚本
#
# 用法:
#   ./run.sh --since daily --limit 15
#   ./run.sh --language python --capture
#   ./run.sh --help

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 进入技能目录
cd "$SCRIPT_DIR"

# 检查 Python 是否可用
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

# 运行主脚本
echo "🚀 启动 github-hunter..."
echo "📂 工作目录: $SCRIPT_DIR"
echo ""

export PYTHONPATH="$SCRIPT_DIR"
python3 scripts/run_workflow.py "$@"
