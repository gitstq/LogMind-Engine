#!/usr/bin/env python3
"""
LogMind Parser Module - 日志解析器模块
支持多种日志格式的智能解析和标准化处理
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"
    
    @classmethod
    def from_string(cls, level_str: str) -> 'LogLevel':
        """从字符串解析日志级别"""
        level_map = {
            'DEBUG': cls.DEBUG,
            'INFO': cls.INFO,
            'WARN': cls.WARNING,
            'WARNING': cls.WARNING,
            'ERROR': cls.ERROR,
            'ERR': cls.ERROR,
            'FATAL': cls.CRITICAL,
            'CRITICAL': cls.CRITICAL,
        }
        return level_map.get(level_str.upper().strip(), cls.UNKNOWN)


class LogFormat(Enum):
    """日志格式枚举"""
    JSON = "json"
    PLAIN_TEXT = "plain_text"
    APACHE = "apache"
    NGINX = "nginx"
    SYSLOG = "syslog"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


@dataclass
class LogEntry:
    """单条日志条目数据结构"""
    timestamp: Optional[datetime] = None
    level: LogLevel = LogLevel.UNKNOWN
    message: str = ""
    source: str = ""
    line_number: int = 0
    raw_content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'level': self.level.value,
            'message': self.message,
            'source': self.source,
            'line_number': self.line_number,
            'metadata': self.metadata
        }


@dataclass
class LogGroup:
    """日志分组数据结构"""
    pattern: str
    count: int = 0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    entries: List[LogEntry] = field(default_factory=list)
    samples: List[str] = field(default_factory=list)
    
    def add_entry(self, entry: LogEntry):
        """添加日志条目"""
        self.entries.append(entry)
        self.count += 1
        if not self.first_seen or (entry.timestamp and entry.timestamp < self.first_seen):
            self.first_seen = entry.timestamp
        if not self.last_seen or (entry.timestamp and entry.timestamp > self.last_seen):
            self.last_seen = entry.timestamp
        if len(self.samples) < 3:
            self.samples.append(entry.message[:200])


class LogParser:
    """
    日志解析器核心类
    支持多种日志格式的自动检测和解析
    """
    
    # 预定义的正则表达式模式
    PATTERNS = {
        'apache_common': r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] "(?P<request>[^"]+)" (?P<status>\d+) (?P<size>[\d-]+)',
        'apache_combined': r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] "(?P<request>[^"]+)" (?P<status>\d+) (?P<size>[\d-]+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"',
        'nginx': r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] "(?P<request>[^"]+)" (?P<status>\d+) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"',
        'syslog': r'(?P<timestamp>\w+\s+\d+\s+[\d:]+) (?P<host>\S+) (?P<process>\S+)(?:\[(?P<pid>\d+)\])?: (?P<message>.*)',
        'python_stdlib': r'(?P<timestamp>[\d-]+\s+[\d:,]+)\s+-\s+(?P<logger>\S+)\s+-\s+(?P<level>\w+)\s+-\s+(?P<message>.*)',
        'java_log4j': r'(?P<timestamp>[\d\-\s:]+)\s+(?P<level>\w+)\s+\[(?P<class>[^\]]+)\]\s+(?P<message>.*)',
        'spring_boot': r'(?P<timestamp>[\d-]+\s+[\d:]+)\.\d+\s+\|\s+(?P<level>\w+)\s+\|\s+(?P<logger>\S+)\s+\|\s+(?P<message>[^|]+)',
        'simple': r'(?P<timestamp>[\d\-\s:]+)\s+(?P<level>\w+)\s+(?P<message>.*)',
    }
    
    def __init__(self):
        """初始化日志解析器"""
        self.entries: List[LogEntry] = []
        self.format_detected: Optional[LogFormat] = None
        self.compiled_patterns: Dict[str, re.Pattern] = {
            name: re.compile(pattern) 
            for name, pattern in self.PATTERNS.items()
        }
        
    def detect_format(self, content: str) -> LogFormat:
        """
        自动检测日志格式
        
        Args:
            content: 日志内容样本
            
        Returns:
            检测到的日志格式
        """
        lines = content.strip().split('\n')[:10]  # 只取前10行检测
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # JSON格式检测
            try:
                json.loads(line)
                return LogFormat.JSON
            except json.JSONDecodeError:
                pass
            
            # Apache格式检测
            if re.match(r'\d+\.\d+\.\d+\.\d+ - - \[', line):
                if '" "' in line:  # combined格式有referer和user_agent
                    return LogFormat.APACHE
                return LogFormat.APACHE
            
            # Nginx格式检测
            if re.match(r'\d+\.\d+\.\d+\.\d+ - - \[', line):
                return LogFormat.NGINX
            
            # Syslog格式检测
            if re.match(r'\w+\s+\d+\s+[\d:]+', line) and 'kernel' not in line.lower():
                return LogFormat.SYSLOG
            
            # Python标准库格式
            if re.match(r'[\d-]+\s+[\d:,]+\s+-\s+\S+\s+-\s+\w+\s+-', line):
                return LogFormat.PLAIN_TEXT
            
            # Spring Boot格式
            if '|' in line and re.match(r'[\d-]+\s+[\d:]+', line):
                return LogFormat.SPRING_BOOT
        
        return LogFormat.PLAIN_TEXT
    
    def parse_json_line(self, line: str, line_number: int) -> Optional[LogEntry]:
        """解析JSON格式日志"""
        try:
            data = json.loads(line)
            
            # 尝试提取时间戳
            timestamp = None
            for ts_field in ['timestamp', 'time', '@timestamp', 'ts', 'datetime']:
                if ts_field in data:
                    try:
                        ts_str = str(data[ts_field])
                        if ts_str.isdigit():
                            timestamp = datetime.fromtimestamp(int(ts_str))
                        else:
                            timestamp = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                        break
                    except (ValueError, OSError):
                        pass
            
            # 提取日志级别
            level = LogLevel.UNKNOWN
            for level_field in ['level', 'severity', 'lvl', 'log_level']:
                if level_field in data:
                    level = LogLevel.from_string(str(data[level_field]))
                    break
            
            # 提取消息
            message = ''
            for msg_field in ['message', 'msg', 'text', 'body']:
                if msg_field in data:
                    message = str(data[msg_field])
                    break
            
            # 提取源代码位置
            source = ''
            for src_field in ['source', 'logger', 'class', 'file']:
                if src_field in data:
                    source = str(data[src_field])
                    break
            
            # 构建元数据
            metadata = {k: v for k, v in data.items() 
                       if k not in ['timestamp', 'time', '@timestamp', 'ts', 
                                   'level', 'severity', 'lvl', 'log_level',
                                   'message', 'msg', 'text', 'body', 'source', 'logger', 'class', 'file']}
            
            return LogEntry(
                timestamp=timestamp,
                level=level,
                message=message,
                source=source,
                line_number=line_number,
                raw_content=line,
                metadata=metadata
            )
        except json.JSONDecodeError:
            return None
    
    def parse_plain_line(self, line: str, line_number: int, format_type: str = 'simple') -> Optional[LogEntry]:
        """解析普通文本日志"""
        for pattern_name, pattern in self.compiled_patterns.items():
            if pattern_name == format_type or (format_type == 'plain_text' and pattern_name == 'simple'):
                match = pattern.match(line)
                if match:
                    groups = match.groupdict()
                    
                    # 解析时间戳
                    timestamp = None
                    if 'timestamp' in groups:
                        try:
                            ts_str = groups['timestamp'].strip()
                            if ts_str:
                                # 尝试多种时间格式
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S,%f', 
                                           '%Y-%m-%d %H:%M:%S.%f', '%Y/%m/%d %H:%M:%S',
                                           '%b %d %H:%M:%S', '%m/%d/%Y %H:%M:%S']:
                                    try:
                                        timestamp = datetime.strptime(ts_str, fmt)
                                        break
                                    except ValueError:
                                        continue
                        except Exception:
                            pass
                    
                    # 解析日志级别
                    level = LogLevel.UNKNOWN
                    if 'level' in groups:
                        level = LogLevel.from_string(groups['level'])
                    
                    # 提取消息
                    message = groups.get('message', line)
                    if not message:
                        message = line
                    
                    # 构建元数据
                    metadata = {k: v for k, v in groups.items() 
                               if k not in ['timestamp', 'level', 'message'] and v}
                    
                    return LogEntry(
                        timestamp=timestamp,
                        level=level,
                        message=message.strip(),
                        source=groups.get('logger', groups.get('class', '')),
                        line_number=line_number,
                        raw_content=line,
                        metadata=metadata
                    )
        
        # 无法解析，返回基础条目
        return LogEntry(
            timestamp=None,
            level=LogLevel.UNKNOWN,
            message=line,
            source='',
            line_number=line_number,
            raw_content=line
        )
    
    def parse_line(self, line: str, line_number: int, force_format: Optional[LogFormat] = None) -> Optional[LogEntry]:
        """
        解析单行日志
        
        Args:
            line: 日志行内容
            line_number: 行号
            force_format: 强制指定格式
            
        Returns:
            解析后的日志条目
        """
        line = line.strip()
        if not line:
            return None
        
        # 如果是多行日志的一部分（缩进的行）
        if line_number > 1 and line.startswith((' ', '\t', 'at ', 'Caused by:', 'Exception:')):
            # 这可能是堆栈跟踪的一部分
            pass
        
        if force_format == LogFormat.JSON or (not force_format and self._looks_like_json(line)):
            result = self.parse_json_line(line, line_number)
            if result:
                return result
        
        return self.parse_plain_line(line, line_number)
    
    def _looks_like_json(self, line: str) -> bool:
        """检查是否像JSON格式"""
        return line.strip().startswith(('{', '['))
    
    def parse_file(self, file_path: str, encoding: str = 'utf-8', 
                   limit: Optional[int] = None) -> List[LogEntry]:
        """
        解析日志文件
        
        Args:
            file_path: 日志文件路径
            encoding: 文件编码
            limit: 最大解析行数
            
        Returns:
            解析后的日志条目列表
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Log file not found: {file_path}")
        
        # 先检测格式
        with open(path, 'r', encoding=encoding, errors='replace') as f:
            sample = f.read(4096)
        
        self.format_detected = self.detect_format(sample)
        
        # 重新解析全部内容
        self.entries = []
        with open(path, 'r', encoding=encoding, errors='replace') as f:
            for i, line in enumerate(f, 1):
                if limit and i > limit:
                    break
                entry = self.parse_line(line, i, self.format_detected)
                if entry:
                    self.entries.append(entry)
        
        return self.entries
    
    def parse_content(self, content: str, format_type: Optional[LogFormat] = None) -> List[LogEntry]:
        """
        解析日志内容字符串
        
        Args:
            content: 日志内容
            format_type: 指定格式
            
        Returns:
            解析后的日志条目列表
        """
        self.entries = []
        if format_type is None:
            format_type = self.detect_format(content)
        self.format_detected = format_type
        
        for i, line in enumerate(content.split('\n'), 1):
            entry = self.parse_line(line, i, format_type)
            if entry:
                self.entries.append(entry)
        
        return self.entries
    
    def parse_stream(self, input_iterator, format_type: Optional[LogFormat] = None) -> List[LogEntry]:
        """
        从流中解析日志（用于管道输入）
        
        Args:
            input_iterator: 输入迭代器
            format_type: 指定格式
            
        Returns:
            解析后的日志条目列表
        """
        self.entries = []
        for i, line in enumerate(input_iterator, 1):
            entry = self.parse_line(line.rstrip('\n'), i, format_type)
            if entry:
                self.entries.append(entry)
        return self.entries
    
    def filter_by_level(self, level: LogLevel) -> List[LogEntry]:
        """按日志级别过滤"""
        return [e for e in self.entries if e.level == level]
    
    def filter_by_level_range(self, min_level: LogLevel, max_level: LogLevel) -> List[LogEntry]:
        """按日志级别范围过滤"""
        level_order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, 
                      LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.UNKNOWN]
        try:
            min_idx = level_order.index(min_level)
            max_idx = level_order.index(max_level)
            return [e for e in self.entries 
                   if e.level in level_order[min_idx:max_idx+1]]
        except ValueError:
            return self.entries
    
    def filter_by_keyword(self, keyword: str, case_sensitive: bool = False) -> List[LogEntry]:
        """按关键词过滤"""
        if case_sensitive:
            return [e for e in self.entries if keyword in e.message]
        else:
            keyword_lower = keyword.lower()
            return [e for e in self.entries if keyword_lower in e.message.lower()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        if not self.entries:
            return {}
        
        level_counts = {}
        for entry in self.entries:
            level_counts[entry.level.value] = level_counts.get(entry.level.value, 0) + 1
        
        timestamps = [e.timestamp for e in self.entries if e.timestamp]
        
        return {
            'total_entries': len(self.entries),
            'level_distribution': level_counts,
            'error_count': level_counts.get('ERROR', 0) + level_counts.get('CRITICAL', 0),
            'format_detected': self.format_detected.value if self.format_detected else 'unknown',
            'time_range': {
                'start': min(timestamps).isoformat() if timestamps else None,
                'end': max(timestamps).isoformat() if timestamps else None
            }
        }
    
    def group_by_pattern(self) -> List[LogGroup]:
        """
        按错误模式分组
        
        Returns:
            分组后的日志组列表
        """
        pattern_groups: Dict[str, LogGroup] = {}
        
        for entry in self.entries:
            if entry.level in (LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.WARNING):
                # 归一化消息用于模式匹配
                normalized = self._normalize_message(entry.message)
                pattern = self._extract_pattern(normalized)
                
                if pattern not in pattern_groups:
                    pattern_groups[pattern] = LogGroup(pattern=pattern)
                
                pattern_groups[pattern].add_entry(entry)
        
        # 按出现次数排序
        return sorted(pattern_groups.values(), key=lambda x: x.count, reverse=True)
    
    def _normalize_message(self, message: str) -> str:
        """归一化消息，用于模式匹配"""
        # 替换数字、IP地址、UUID等为占位符
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}', '<DATE>', message)
        normalized = re.sub(r'\d{2}:\d{2}:\d{2}', '<TIME>', normalized)
        normalized = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '<IP>', normalized)
        normalized = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '<UUID>', normalized)
        normalized = re.sub(r'\d+', '<NUM>', normalized)
        normalized = re.sub(r'0x[0-9a-fA-F]+', '<HEX>', normalized)
        return normalized
    
    def _extract_pattern(self, normalized: str) -> str:
        """从归一化消息中提取核心模式"""
        # 移除括号内的内容
        pattern = re.sub(r'<[^>]+>', '<*>', normalized)
        # 移除多余空格
        pattern = ' '.join(pattern.split())
        return pattern
