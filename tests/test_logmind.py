#!/usr/bin/env python3
"""
LogMind Test Suite - 测试套件
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from logmind.parser import LogParser, LogEntry, LogLevel, LogFormat
from logmind.analyzer import LogAnalyzer, AnalysisResult


# 测试数据
SAMPLE_PLAIN_LOG = """
2025-01-15 10:30:00 INFO Starting application
2025-01-15 10:30:01 DEBUG Loading configuration
2025-01-15 10:30:02 INFO Application started successfully
2025-01-15 10:30:05 WARNING Connection timeout, retrying...
2025-01-15 10:30:06 ERROR Failed to connect to database
2025-01-15 10:30:07 ERROR Connection refused
2025-01-15 10:30:10 CRITICAL System shutdown initiated
"""

SAMPLE_JSON_LOG = """
{"timestamp": "2025-01-15T10:30:00", "level": "INFO", "message": "Server started"}
{"timestamp": "2025-01-15T10:30:01", "level": "DEBUG", "message": "Loading config"}
{"timestamp": "2025-01-15T10:30:05", "level": "ERROR", "message": "Connection failed"}
"""

SAMPLE_MIXED_LOG = """
2025-01-15 10:30:00 INFO Application starting
2025-01-15 10:30:01 ERROR Database connection timeout
2025-01-15 10:30:02 {"level": "ERROR", "message": "Failed to process request"}
2025-01-15 10:30:03 WARNING Retrying connection...
"""


class TestLogParser:
    """日志解析器测试"""
    
    def test_detect_format_plain(self):
        """测试普通文本格式检测"""
        parser = LogParser()
        format_type = parser.detect_format(SAMPLE_PLAIN_LOG)
        assert format_type == LogFormat.PLAIN_TEXT
    
    def test_detect_format_json(self):
        """测试JSON格式检测"""
        parser = LogParser()
        format_type = parser.detect_format(SAMPLE_JSON_LOG)
        assert format_type == LogFormat.JSON
    
    def test_parse_plain_log(self):
        """测试解析普通文本日志"""
        parser = LogParser()
        entries = parser.parse_content(SAMPLE_PLAIN_LOG)
        
        assert len(entries) > 0
        assert any(e.level == LogLevel.INFO for e in entries)
        assert any(e.level == LogLevel.ERROR for e in entries)
        assert any(e.level == LogLevel.CRITICAL for e in entries)
    
    def test_parse_json_log(self):
        """测试解析JSON日志"""
        parser = LogParser()
        entries = parser.parse_content(SAMPLE_JSON_LOG)
        
        assert len(entries) > 0
        assert all(e.level != LogLevel.UNKNOWN for e in entries)
    
    def test_parse_mixed_log(self):
        """测试解析混合格式日志"""
        parser = LogParser()
        entries = parser.parse_content(SAMPLE_MIXED_LOG)
        
        assert len(entries) > 0
    
    def test_filter_by_level(self):
        """测试按级别过滤"""
        parser = LogParser()
        entries = parser.parse_content(SAMPLE_PLAIN_LOG)
        
        error_entries = parser.filter_by_level(LogLevel.ERROR)
        assert all(e.level == LogLevel.ERROR for e in error_entries)
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        parser = LogParser()
        parser.parse_content(SAMPLE_PLAIN_LOG)
        stats = parser.get_statistics()
        
        assert 'total_entries' in stats
        assert stats['total_entries'] > 0
        assert 'level_distribution' in stats
        assert 'error_count' in stats
        assert stats['error_count'] >= 2  # 至少有2个ERROR
    
    def test_group_by_pattern(self):
        """测试错误分组"""
        parser = LogParser()
        parser.parse_content(SAMPLE_PLAIN_LOG)
        groups = parser.group_by_pattern()
        
        # 应该有错误分组
        error_groups = [g for g in groups if g.count >= 2]
        assert len(error_groups) > 0


class TestLogAnalyzer:
    """日志分析器测试"""
    
    def test_analyze(self):
        """测试完整分析"""
        parser = LogParser()
        parser.parse_content(SAMPLE_PLAIN_LOG)
        
        analyzer = LogAnalyzer(parser)
        result = analyzer.analyze(parser.entries)
        
        assert result.total_entries > 0
        assert len(result.level_distribution) > 0
        assert result.error_count >= 0
    
    def test_level_distribution(self):
        """测试级别分布分析"""
        parser = LogParser()
        parser.parse_content(SAMPLE_PLAIN_LOG)
        
        analyzer = LogAnalyzer(parser)
        result = analyzer.analyze(parser.entries)
        
        assert 'INFO' in result.level_distribution
        assert 'ERROR' in result.level_distribution
        assert result.level_distribution['ERROR'] >= 2
    
    def test_generate_summary(self):
        """测试摘要生成"""
        parser = LogParser()
        parser.parse_content(SAMPLE_PLAIN_LOG)
        
        analyzer = LogAnalyzer(parser)
        result = analyzer.analyze(parser.entries)
        summary = analyzer.generate_report('text')
        
        assert len(summary) > 0
        assert 'LogMind' in summary or '日志' in summary
    
    def test_generate_json_report(self):
        """测试JSON报告生成"""
        parser = LogParser()
        parser.parse_content(SAMPLE_PLAIN_LOG)
        
        analyzer = LogAnalyzer(parser)
        result = analyzer.analyze(parser.entries)
        json_report = analyzer.generate_report('json')
        
        import json
        data = json.loads(json_report)
        assert 'total_entries' in data
        assert 'level_distribution' in data


class TestLogEntry:
    """日志条目测试"""
    
    def test_to_dict(self):
        """测试转换为字典"""
        entry = LogEntry(
            timestamp=None,
            level=LogLevel.INFO,
            message="Test message",
            source="test.py",
            line_number=1
        )
        
        d = entry.to_dict()
        assert d['level'] == 'INFO'
        assert d['message'] == 'Test message'


def run_tests():
    """运行所有测试"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_tests()
