#!/usr/bin/env python3
"""
LogMind - 轻量级智能日志分析引擎
Lightweight Intelligent Log Analysis Engine

A powerful CLI tool for analyzing application logs with AI-powered insights.
Supports multi-format logs, error grouping, and intelligent suggestions.

Author: gitstq
License: MIT
Repository: https://github.com/gitstq/LogMind
"""

__version__ = "1.0.0"
__author__ = "gitstq"

from .parser import LogParser
from .analyzer import LogAnalyzer
from .tui import LogMindTUI
from .ai_providers import AIManager

__all__ = [
    "LogParser",
    "LogAnalyzer", 
    "LogMindTUI",
    "AIManager",
]
