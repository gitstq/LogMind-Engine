# 🧠 LogMind - 輕量級智能日誌分析引擎

[簡體中文](./README.md) | [繁體中文](./README.md) | [English](./i18n/README.md) | [日本語](./i18n/README.ja-JP.md)

---

## 🎉 專案介紹

**LogMind** 是一款專為開發者設計的輕量級智能日誌分析引擎 🔍

在日常開發和運維工作中，日誌分析是排查問題的關鍵環節。但面對龐大的日誌文件，如何快速定位問題、分析錯誤模式、獲取修復建議？LogMind 應運而生！

### 🌟 核心價值

- ⚡ **秒級分析** - 支援數百萬行日誌的秒級解析，無需等待
- 🤖 **AI智能** - 集成OpenAI/Claude/Ollama，自動分析錯誤根因並提供修復建議
- 🎨 **美觀介面** - 豐富的TUI介面，讓日誌分析成一種享受
- 🔧 **多格式支援** - JSON、純文字、Apache、Nginx、Syslog 等多種格式
- 📦 **零依賴** - 核心功能僅需 `rich` 庫，部署簡單
- 🐍 **純Python** - 100% Python實現，與您現有的Python工具鏈無縫集成

---

## ✨ 核心功能

### 📊 日誌解析

- ✅ **多格式支援** - JSON、純文字、Apache、Nginx、Syslog
- ✅ **自動檢測** - 智能識別日誌格式，無需手動指定
- ✅ **流式解析** - 支援管道輸入，適合即時日誌分析
- ✅ **多編碼支援** - UTF-8、GBK等常見編碼

### 🔍 錯誤分析

- ✅ **智能分組** - 自動將相似錯誤歸類，發現錯誤模式
- ✅ **模式提取** - 動態值歸一化，提取核心錯誤特徵
- ✅ **頻率統計** - 統計錯誤出現次數和分布
- ✅ **時間分析** - 分析錯誤發生的時間規律

### 🚨 異常檢測

- ✅ **錯誤率監控** - 即時監控錯誤率異常
- ✅ **突增檢測** - 檢測錯誤頻率突增情況
- ✅ **分數評估** - 計算綜合異常分數

### 🤖 AI增強（可選）

- ✅ **多AI提供商** - 支援 OpenAI、Claude、Gemini、Ollama
- ✅ **智能分析** - AI自動分析錯誤根因
- ✅ **修復建議** - 提供具體的修復步驟和代碼示例
- ✅ **回應緩存** - 智能緩存，減少API調用成本

---

## 🚀 快速開始

### 📥 安裝

**方式一：pip安裝（推薦）**

```bash
pip install logmind
```

**方式二：從原始碼安裝**

```bash
git clone https://github.com/gitstq/LogMind-Engine.git
cd LogMind-Engine
pip install -e .
```

### 📋 環境要求

- Python 3.8+
- 依賴庫：`rich >= 13.0.0`
- 可選AI功能：`openai`、`anthropic`

### 🚀 快速使用

**分析日誌檔案**

```bash
logmind analyze /path/to/your.log
```

**管道輸入**

```bash
cat app.log | logmind analyze -
```

**限制行數**

```bash
logmind analyze /path/to/large.log --limit 10000
```

**完整分析模式**

```bash
logmind analyze /path/to/app.log --analyze
```

---

## 📖 詳細使用指南

### CLI 命令詳解

| 命令 | 說明 | 示例 |
|------|------|------|
| `logmind analyze` | 分析日誌檔案 | `logmind analyze app.log` |
| `logmind stats` | 顯示統計資訊 | `logmind stats app.log` |
| `logmind errors` | 顯示錯誤分組 | `logmind errors app.log` |
| `logmind entries` | 顯示日誌條目 | `logmind entries app.log -l 100` |
| `logmind report` | 生成完整報告 | `logmind report app.log -o report.html` |

### Python API 使用

```python
from logmind.parser import LogParser
from logmind.analyzer import LogAnalyzer

# 解析日誌
parser = LogParser()
entries = parser.parse_file('/path/to/app.log')

# 分析日誌
analyzer = LogAnalyzer(parser)
result = analyzer.analyze(entries)

# 輸出報告
print(analyzer.generate_report('text'))
```

---

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發環境設置

```bash
# 克隆倉庫
git clone https://github.com/gitstq/LogMind-Engine.git
cd LogMind-Engine

# 建立虛擬環境
python -m venv venv
source venv/bin/activate

# 安裝開發依賴
pip install -e ".[dev]"
```

---

## 📄 開源協議

本專案採用 [MIT License](./LICENSE) 開源。

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">@gitstq</a>
</p>
