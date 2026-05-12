# 🧠 LogMind - 軽量インテリジェントログ分析エンジン

[简体中文](./README.md) | [繁體中文](./i18n/README.zh-TW.md) | [English](./i18n/README.md) | [日本語](./README.md)

---

## 🎉 プロジェクト紹介

**LogMind** は開発者向けに設計された軽量インテリジェントログ分析エンジンです 🔍

日常の開発と運用業務において、ログ分析は問題解決の重要なステップです。しかし、大量のログファイル，面对，如何迅速に問題を発見し、エラータイプを分析し、修正提案を取得しますか？LogMind が登場しました！

### 🌟 コアバリュー

- ⚡ **秒速分析** - 数百万行のログを秒単位で解析
- 🤖 **AI搭載** - OpenAI/Claude/Ollamaと統合、根因分析と修正提案を自動提供
- 🎨 **美しいインターフェース** - 豊かなTUIインターフェース
- 🔧 **マルチフォーマット対応** - JSON、プレーンテキスト、Apache、Nginx、Syslog
- 📦 **ゼロ依存** - コア機能は `rich` ライブラリのみ
- 🐍 **ピュアPython** - 100% Python実装

---

## ✨ コア機能

### 📊 ログ解析

- ✅ **マルチフォーマット対応** - JSON、プレーンテキスト、Apache、Nginx、Syslog
- ✅ **自動検出** - ログフォーマットをインテリジェントに識別
- ✅ **ストリーミング** - パイプライン入力をサポート
- ✅ **マルチエンコーディング** - UTF-8、GBKなど

### 🔍 エラー分析

- ✅ **スマートグループ化** - 類似エラーを自動分類
- ✅ **パターン抽出** - 動的値の正規化
- ✅ **頻度統計** - エラーの発生回数をカウント
- ✅ **時間分析** - エラーの時間的パターンを分析

### 🚨 異常検出

- ✅ **エラー率監視** - リアルタイムのエラー率監視
- ✅ **バースト検出** - エラーの急増を検出
- ✅ **スコア評価** - 総合異常スコアを計算

### 🤖 AI強化（オプション）

- ✅ **マルチプロバイダー** - OpenAI、Claude、Gemini、Ollamaをサポート
- ✅ **スマート分析** - AIがエラーの根因を自動分析
- ✅ **修正提案** - 具体的な修正ステップとコード例を提供
- ✅ **応答キャッシュ** - インテリジェントなキャッシュ

---

## 🚀 クイックスタート

### 📥 インストール

```bash
pip install logmind
```

または

```bash
git clone https://github.com/gitstq/LogMind-Engine.git
cd LogMind-Engine
pip install -e .
```

### 📋 必要環境

- Python 3.8+
- 依存ライブラリ：`rich >= 13.0.0`

### 🚀 クイック使用

**ログファイルを分析**

```bash
logmind analyze /path/to/your.log
```

**パイプライン入力**

```bash
cat app.log | logmind analyze -
```

**完全分析モード**

```bash
logmind analyze /path/to/app.log --analyze
```

**AI強化分析**

```bash
export OPENAI_API_KEY="sk-..."
logmind analyze /path/to/app.log --analyze --ai
```

---

## 📖 詳細な使用ガイド

### CLI コマンド

| コマンド | 説明 |
|---------|------|
| `logmind analyze` | ログファイルを分析 |
| `logmind stats` | 統計情報を表示 |
| `logmind errors` | エラーグループを表示 |
| `logmind report` | 完全レポートを生成 |

### Python API

```python
from logmind.parser import LogParser
from logmind.analyzer import LogAnalyzer

# ログを解析
parser = LogParser()
entries = parser.parse_file('/path/to/app.log')

# ログを分析
analyzer = LogAnalyzer(parser)
result = analyzer.analyze(entries)

# レポートを出力
print(analyzer.generate_report('text'))
```

---

## 🤝 コントリビューション

Issue と Pull Request をお待ちしています！

---

## 📄 ライセンス

MITライセンスの下で公開されています。

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">@gitstq</a>
</p>
