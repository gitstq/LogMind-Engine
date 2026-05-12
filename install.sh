#!/bin/bash
# LogMind 安装脚本
# LogMind Installation Script

set -e

echo "🚀 LogMind 安装程序"
echo "===================="

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 检测到 Python 版本: $PYTHON_VERSION"

# 最低要求 Python 3.8
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ LogMind 需要 Python 3.8 或更高版本"
    exit 1
fi

# 创建虚拟环境（可选）
if [ "$1" = "--venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv logmind-env
    source logmind-env/bin/activate
fi

# 安装依赖
echo "📥 安装依赖..."
pip install --upgrade pip

# 安装 LogMind
echo "📥 安装 LogMind..."
pip install rich

# 可选依赖
read -p "是否安装AI功能依赖? (需要API密钥) [y/N]: " install_ai
if [ "$install_ai" = "y" ] || [ "$install_ai" = "Y" ]; then
    echo "📥 安装AI功能依赖..."
    pip install openai anthropic
fi

# 创建配置目录
mkdir -p ~/.logmind/cache
echo "✅ 配置文件目录已创建: ~/.logmind"

# 创建符号链接（可选）
read -p "是否创建全局命令 'logmind'? [y/N]: " create_symlink
if [ "$create_symlink" = "y" ] || [ "$create_symlink" = "Y" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    ln -sf "$SCRIPT_DIR/logmind/cli.py" /usr/local/bin/logmind
    chmod +x /usr/local/bin/logmind
    echo "✅ 已创建全局命令: /usr/local/bin/logmind"
fi

echo ""
echo "🎉 安装完成!"
echo ""
echo "快速开始:"
echo "  logmind analyze /path/to/your.log"
echo "  cat app.log | logmind analyze -"
echo ""
echo "查看帮助:"
echo "  logmind --help"
echo ""
