# 🧠 LogMind - Lightweight Intelligent Log Analysis Engine

[简体中文](./README.md) | [繁體中文](./README.zh-TW.md) | [English](./README.md) | [日本語](./README.ja-JP.md)

---

## 🎉 Project Introduction

**LogMind** is a lightweight intelligent log analysis engine designed specifically for developers 🔍

In daily development and operations work, log analysis is crucial for troubleshooting. But when facing massive log files, how do you quickly locate issues, analyze error patterns, and get fix suggestions? LogMind comes to the rescue!

### 🌟 Core Value

- ⚡ **Lightning Fast** - Analyze millions of log lines in seconds
- 🤖 **AI-Powered** - Integrated with OpenAI/Claude/Ollama, automatically analyze root causes and provide fix suggestions
- 🎨 **Beautiful Interface** - Rich TUI interface makes log analysis enjoyable
- 🔧 **Multi-Format Support** - JSON, plain text, Apache, Nginx, Syslog and more
- 📦 **Zero Dependencies** - Core features only require `rich` library
- 🐍 **Pure Python** - 100% Python implementation, seamlessly integrated with your existing Python toolchain

---

## ✨ Core Features

### 📊 Log Parsing

- ✅ **Multi-format Support** - JSON, plain text, Apache, Nginx, Syslog
- ✅ **Auto Detection** - Intelligently identify log format
- ✅ **Streaming** - Support pipe input for real-time log analysis
- ✅ **Multi-encoding** - UTF-8, GBK and more

### 🔍 Error Analysis

- ✅ **Smart Grouping** - Automatically categorize similar errors
- ✅ **Pattern Extraction** - Normalize dynamic values, extract core error features
- ✅ **Frequency Stats** - Count error occurrences and distribution
- ✅ **Time Analysis** - Analyze error timing patterns

### 🚨 Anomaly Detection

- ✅ **Error Rate Monitoring** - Real-time error rate monitoring
- ✅ **Burst Detection** - Detect sudden error spikes
- ✅ **Score Assessment** - Calculate comprehensive anomaly scores

### 🤖 AI Enhancement (Optional)

- ✅ **Multi-Provider** - Support OpenAI, Claude, Gemini, Ollama
- ✅ **Smart Analysis** - AI automatically analyzes error root causes
- ✅ **Fix Suggestions** - Provide specific fix steps and code examples
- ✅ **Response Cache** - Smart caching to reduce API costs

---

## 🚀 Quick Start

### 📥 Installation

**Method 1: pip install (Recommended)**

```bash
pip install logmind
```

**Method 2: From source**

```bash
git clone https://github.com/gitstq/LogMind-Engine.git
cd LogMind-Engine
pip install -e .
```

### 📋 Requirements

- Python 3.8+
- Dependency: `rich >= 13.0.0`
- Optional AI: `openai`, `anthropic`

### 🚀 Quick Usage

**Analyze log file**

```bash
logmind analyze /path/to/your.log
```

**Pipe input**

```bash
cat app.log | logmind analyze -
```

**Limit lines**

```bash
logmind analyze /path/to/large.log --limit 10000
```

**Full analysis mode**

```bash
logmind analyze /path/to/app.log --analyze
```

**AI-enhanced analysis (requires API key)**

```bash
# Set environment variable
export OPENAI_API_KEY="sk-..."

# Use AI analysis
logmind analyze /path/to/app.log --analyze --ai
```

---

## 📖 Detailed Usage Guide

### CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `logmind analyze` | Analyze log file | `logmind analyze app.log` |
| `logmind stats` | Show statistics | `logmind stats app.log` |
| `logmind errors` | Show error groups | `logmind errors app.log` |
| `logmind entries` | Show log entries | `logmind entries app.log -l 100` |
| `logmind report` | Generate full report | `logmind report app.log -o report.html` |

### Parameters

| Parameter | Description |
|-----------|-------------|
| `--limit, -l` | Limit number of lines to parse |
| `--analyze, -a` | Perform deep analysis |
| `--ai` | Enable AI enhancement |
| `--show-entries, -e` | Show log entries |
| `--json` | Output JSON format |
| `--html` | Output HTML report |
| `--verbose, -v` | Show detailed logs |

### Interactive Mode

```bash
logmind interactive

# In interactive environment
logmind> load /path/to/app.log
logmind> stats
logmind> errors
logmind> report
logmind> quit
```

### Python API

```python
from logmind.parser import LogParser
from logmind.analyzer import LogAnalyzer

# Parse logs
parser = LogParser()
entries = parser.parse_file('/path/to/app.log')

# Analyze logs
analyzer = LogAnalyzer(parser)
result = analyzer.analyze(entries)

# Output report
print(analyzer.generate_report('text'))

# Get JSON format
json_report = analyzer.generate_report('json')
```

---

## 💡 Design Philosophy

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        LogMind                          │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Parser  │──│ Analyzer │──│   TUI    │──│   AI   │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Module Description

| Module | Responsibility |
|--------|----------------|
| `parser.py` | Log format parsing, multi-format auto detection |
| `analyzer.py` | Statistics, error grouping, anomaly detection |
| `tui.py` | Terminal UI based on Rich library |
| `ai_providers.py` | AI service integration, multi-provider support |
| `cli.py` | Command line entry |

---

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

### Development Setup

```bash
# Clone repository
git clone https://github.com/gitstq/LogMind-Engine.git
cd LogMind-Engine

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

---

## 📄 License

This project is open source under [MIT License](./LICENSE).

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
