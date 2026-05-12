# 🧠 LogMind - 轻量级智能日志分析引擎

[简体中文](./README.md) | [繁體中文](./i18n/README.zh-TW.md) | [English](./i18n/README.md) | [日本語](./i18n/README.ja-JP.md)

---

## 🎉 项目介绍

**LogMind** 是一款专为开发者设计的轻量级智能日志分析引擎 🔍

在日常开发和运维工作中，日志分析是排查问题的关键环节。但面对庞大的日志文件，如何快速定位问题、分析错误模式、获取修复建议？LogMind 应运而生！

### 🌟 核心价值

- ⚡ **秒级分析** - 支持数百万行日志的秒级解析，无需等待
- 🤖 **AI智能** - 集成OpenAI/Claude/Ollama，自动分析错误根因并提供修复建议
- 🎨 **美观界面** - 丰富的TUI界面，让日志分析成为一种享受
- 🔧 **多格式支持** - JSON、纯文本、Apache、Nginx、Syslog 等多种格式
- 📦 **零依赖** - 核心功能仅需 `rich` 库，部署简单
- 🐍 **纯Python** - 100% Python实现，与您现有的Python工具链无缝集成

### 💡 灵感来源

本项目参考了 [LogAI](https://github.com/ranjan-mohanty/logai) 等优秀日志分析工具的核心理念，但进行了**完全独立自研开发**：

| 对比项 | LogAI (参考) | LogMind (自研) |
|--------|--------------|----------------|
| 实现语言 | Rust | Python |
| 技术栈 | 注重性能 | 注重易用性 |
| 界面 | 基础CLI | 精美TUI |
| 集成 | 企业级 | 开发友好 |
| 部署 | 复杂 | 极简 |

---

## ✨ 核心特性

### 📊 日志解析

- ✅ **多格式支持** - JSON、纯文本、Apache、Nginx、Syslog
- ✅ **自动检测** - 智能识别日志格式，无需手动指定
- ✅ **流式解析** - 支持管道输入，适合实时日志分析
- ✅ **多编码支持** - UTF-8、GBK等常见编码

### 🔍 错误分析

- ✅ **智能分组** - 自动将相似错误归类，发现错误模式
- ✅ **模式提取** - 动态值归一化，提取核心错误特征
- ✅ **频率统计** - 统计错误出现次数和分布
- ✅ **时间分析** - 分析错误发生的时间规律

### 🚨 异常检测

- ✅ **错误率监控** - 实时监控错误率异常
- ✅ **突增检测** - 检测错误频率突增情况
- ✅ **分数评估** - 计算综合异常分数

### 🤖 AI增强（可选）

- ✅ **多AI提供商** - 支持 OpenAI、Claude、Gemini、Ollama
- ✅ **智能分析** - AI自动分析错误根因
- ✅ **修复建议** - 提供具体的修复步骤和代码示例
- ✅ **响应缓存** - 智能缓存，减少API调用成本

---

## 🚀 快速开始

### 📥 安装

**方式一：pip安装（推荐）**

```bash
pip install logmind
```

**方式二：从源码安装**

```bash
git clone https://github.com/gitstq/LogMind-Engine.git
cd LogMind-Engine
pip install -e .
```

**方式三：一键安装脚本**

```bash
curl -sSL https://raw.githubusercontent.com/gitstq/LogMind-Engine/main/install.sh | bash
```

### 📋 环境要求

- Python 3.8+
- 依赖库：`rich >= 13.0.0`
- 可选AI功能：`openai`、`anthropic`

### 🚀 快速使用

**分析日志文件**

```bash
logmind analyze /path/to/your.log
```

**管道输入**

```bash
cat app.log | logmind analyze -
```

**限制行数**

```bash
logmind analyze /path/to/large.log --limit 10000
```

**完整分析模式**

```bash
logmind analyze /path/to/app.log --analyze
```

**AI增强分析（需配置API密钥）**

```bash
# 设置环境变量
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# 使用AI分析
logmind analyze /path/to/app.log --analyze --ai
```

---

## 📖 详细使用指南

### CLI 命令详解

| 命令 | 说明 | 示例 |
|------|------|------|
| `logmind analyze` | 分析日志文件 | `logmind analyze app.log` |
| `logmind stats` | 显示统计信息 | `logmind stats app.log` |
| `logmind errors` | 显示错误分组 | `logmind errors app.log` |
| `logmind entries` | 显示日志条目 | `logmind entries app.log -l 100` |
| `logmind report` | 生成完整报告 | `logmind report app.log -o report.html` |

### 参数说明

| 参数 | 说明 |
|------|------|
| `--limit, -l` | 限制解析的行数 |
| `--analyze, -a` | 执行深度分析 |
| `--ai` | 启用AI增强分析 |
| `--show-entries, -e` | 显示日志条目 |
| `--json` | 输出JSON格式 |
| `--html` | 输出HTML报告 |
| `--verbose, -v` | 显示详细日志 |

### 交互式模式

```bash
logmind interactive

# 在交互式环境中
logmind> load /path/to/app.log
logmind> stats
logmind> errors
logmind> report
logmind> quit
```

### Python API 使用

```python
from logmind.parser import LogParser
from logmind.analyzer import LogAnalyzer
from logmind.tui import LogMindTUI

# 解析日志
parser = LogParser()
entries = parser.parse_file('/path/to/app.log')

# 分析日志
analyzer = LogAnalyzer(parser)
result = analyzer.analyze(entries)

# 输出报告
print(analyzer.generate_report('text'))

# 获取JSON格式
json_report = analyzer.generate_report('json')
```

---

## 💡 设计思路

### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                        LogMind                          │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Parser  │──│ Analyzer │──│   TUI    │──│   AI   │ │
│  │  日志解析 │  │  智能分析  │  │  界面展示 │  │  AI增强 │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 模块说明

| 模块 | 职责 |
|------|------|
| `parser.py` | 日志格式解析，支持多种格式自动检测 |
| `analyzer.py` | 统计分析、错误分组、异常检测 |
| `tui.py` | 基于Rich库的终端用户界面 |
| `ai_providers.py` | AI服务集成，支持多提供商 |
| `cli.py` | 命令行入口 |

### 技术选型原因

| 技术 | 选择理由 |
|------|----------|
| Python | 开发者友好，与现有工具链集成简单 |
| Rich | 最佳Python TUI库，社区活跃 |
| 类型提示 | 提高代码可读性和可维护性 |

---

## 📦 打包与部署

### Python打包

```bash
# 构建wheel包
python -m build

# 安装本地包
pip install dist/logmind-*.whl
```

### 发布到PyPI

```bash
# 安装发布工具
pip install build twine

# 构建发布包
python -m build
twine upload dist/*
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/gitstq/LogMind-Engine.git
cd LogMind-Engine

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 带覆盖率
pytest --cov=logmind --cov-report=html
```

### 代码规范

```bash
# 格式化代码
black .

# 检查导入顺序
isort .

# 类型检查
mypy logmind/
```

---

## 📄 开源协议

本项目采用 [MIT License](./LICENSE) 开源。

---

## 🙏 致谢

- 灵感来源：[LogAI](https://github.com/ranjan-mohanty/logai)
- TUI框架：[Rich](https://github.com/Textualize/rich)
- AI服务：[OpenAI](https://openai.com)、[Anthropic](https://anthropic.com)

---

<p align="center">
  <a href="https://github.com/gitstq/LogMind-Engine">⭐ Star</a>
  &nbsp;|&nbsp;
  <a href="https://github.com/gitstq/LogMind-Engine/fork">🍴 Fork</a>
  &nbsp;|&nbsp;
  <a href="https://github.com/gitstq/LogMind-Engine/issues">🐛 Issues</a>
</p>

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">@gitstq</a>
</p>
