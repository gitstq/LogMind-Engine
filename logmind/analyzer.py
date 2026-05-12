#!/usr/bin/env python3
"""
LogMind Analyzer Module - 日志分析器模块
支持日志统计、分组、异常检测等功能
"""

import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .parser import LogParser, LogEntry, LogLevel, LogGroup


@dataclass
class AnalysisResult:
    """分析结果数据结构"""
    total_entries: int = 0
    level_distribution: Dict[str, int] = field(default_factory=dict)
    error_groups: List[LogGroup] = field(default_factory=list)
    time_distribution: Dict[str, int] = field(default_factory=dict)
    top_sources: List[Tuple[str, int]] = field(default_factory=list)
    anomaly_score: float = 0.0
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_entries': self.total_entries,
            'level_distribution': self.level_distribution,
            'error_groups': [
                {
                    'pattern': g.pattern,
                    'count': g.count,
                    'samples': g.samples
                }
                for g in self.error_groups
            ],
            'time_distribution': self.time_distribution,
            'top_sources': self.top_sources,
            'anomaly_score': self.anomaly_score,
            'summary': self.summary,
            'recommendations': self.recommendations
        }


@dataclass
class AnomalyDetection:
    """异常检测结果"""
    detected: bool = False
    score: float = 0.0
    reasons: List[str] = field(default_factory=list)
    affected_entries: List[int] = field(default_factory=list)


class LogAnalyzer:
    """
    日志分析器核心类
    提供日志统计、分组、异常检测等分析功能
    """
    
    def __init__(self, parser: Optional[LogParser] = None):
        """初始化分析器"""
        self.parser = parser or LogParser()
        self.entries: List[LogEntry] = []
        self.result: Optional[AnalysisResult] = None
        
        # 配置参数
        self.anomaly_threshold = 0.7  # 异常阈值
        self.rare_level_threshold = 0.05  # 稀有级别阈值
        self.burst_window_seconds = 60  # 突增检测窗口
        
    def analyze(self, entries: List[LogEntry]) -> AnalysisResult:
        """
        执行完整的日志分析
        
        Args:
            entries: 日志条目列表
            
        Returns:
            分析结果
        """
        self.entries = entries
        
        # 统计日志级别分布
        level_dist = self._analyze_levels()
        
        # 按模式分组错误
        error_groups = self._group_errors()
        
        # 时间分布分析
        time_dist = self._analyze_time_distribution()
        
        # 来源分析
        top_sources = self._analyze_sources()
        
        # 异常检测
        anomaly = self._detect_anomalies()
        
        # 生成摘要
        summary = self._generate_summary(level_dist, error_groups, anomaly)
        
        # 生成建议
        recommendations = self._generate_recommendations(error_groups, anomaly)
        
        self.result = AnalysisResult(
            total_entries=len(entries),
            level_distribution=level_dist,
            error_groups=error_groups[:10],  # 只保留前10个错误组
            time_distribution=time_dist,
            top_sources=top_sources,
            anomaly_score=anomaly.score,
            summary=summary,
            recommendations=recommendations
        )
        
        return self.result
    
    def _analyze_levels(self) -> Dict[str, int]:
        """分析日志级别分布"""
        level_counter = Counter(e.level.value for e in self.entries)
        return dict(level_counter)
    
    def _group_errors(self) -> List[LogGroup]:
        """分组错误日志"""
        return self.parser.group_by_pattern()
    
    def _analyze_time_distribution(self) -> Dict[str, int]:
        """分析时间分布"""
        time_buckets: Dict[str, int] = defaultdict(int)
        
        for entry in self.entries:
            if entry.timestamp:
                # 按分钟分组
                bucket = entry.timestamp.strftime('%Y-%m-%d %H:%M')
                time_buckets[bucket] += 1
        
        return dict(sorted(time_buckets.items())[:100])  # 最多100个时间点
    
    def _analyze_sources(self) -> List[Tuple[str, int]]:
        """分析日志来源"""
        source_counter = Counter(e.source for e in self.entries if e.source)
        return source_counter.most_common(10)
    
    def _detect_anomalies(self) -> AnomalyDetection:
        """检测异常"""
        anomaly = AnomalyDetection()
        
        if not self.entries:
            return anomaly
        
        total = len(self.entries)
        
        # 1. 检查错误率是否异常
        error_count = sum(1 for e in self.entries 
                        if e.level in (LogLevel.ERROR, LogLevel.CRITICAL))
        error_rate = error_count / total if total > 0 else 0
        
        if error_rate > 0.1:  # 超过10%错误率
            anomaly.reasons.append(f"High error rate: {error_rate:.1%}")
            anomaly.score += 0.3
        
        # 2. 检查是否存在CRITICAL级别日志
        critical_count = sum(1 for e in self.entries if e.level == LogLevel.CRITICAL)
        if critical_count > 0:
            anomaly.reasons.append(f"Critical errors detected: {critical_count}")
            anomaly.score += 0.4
        
        # 3. 检测错误突增
        timestamps = sorted([e.timestamp for e in self.entries 
                           if e.timestamp and e.level in (LogLevel.ERROR, LogLevel.CRITICAL)])
        
        if len(timestamps) >= 3:
            # 检查是否有时间相近的错误（可能表示故障）
            for i in range(len(timestamps) - 1):
                gap = (timestamps[i+1] - timestamps[i]).total_seconds()
                if gap < 10:  # 10秒内连续错误
                    anomaly.reasons.append(f"Burst of errors detected (gap: {gap}s)")
                    anomaly.score += 0.2
                    break
        
        # 4. 检查稀有级别
        level_dist = self._analyze_levels()
        for level, count in level_dist.items():
            ratio = count / total
            if ratio < self.rare_level_threshold and level != 'UNKNOWN':
                # 稀有级别可能表示异常
                pass
        
        # 5. 检查日志量突增
        if len(timestamps) >= 2:
            # 计算平均错误间隔
            total_span = (timestamps[-1] - timestamps[0]).total_seconds()
            if total_span > 0:
                avg_interval = total_span / (len(timestamps) - 1)
                if avg_interval < 30:  # 平均间隔小于30秒
                    anomaly.reasons.append(f"High frequency errors (avg interval: {avg_interval:.1f}s)")
                    anomaly.score += 0.2
        
        anomaly.score = min(1.0, anomaly.score)
        anomaly.detected = anomaly.score >= self.anomaly_threshold
        
        return anomaly
    
    def _generate_summary(self, level_dist: Dict[str, int], 
                         error_groups: List[LogGroup],
                         anomaly: AnomalyDetection) -> str:
        """生成分析摘要"""
        lines = []
        
        total = self.entries.__len__() if hasattr(self.entries, '__len__') else len(self.entries)
        lines.append(f"📊 共分析 {total} 条日志")
        
        # 级别统计
        if level_dist:
            level_emoji = {
                'DEBUG': '🔍',
                'INFO': 'ℹ️',
                'WARNING': '⚠️',
                'ERROR': '🔴',
                'CRITICAL': '🚨',
                'UNKNOWN': '❓'
            }
            level_parts = []
            for level, count in sorted(level_dist.items(), 
                                       key=lambda x: ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'UNKNOWN'].index(x[0])):
                emoji = level_emoji.get(level, '📌')
                level_parts.append(f"{emoji} {level}: {count}")
            lines.append(" | ".join(level_parts))
        
        # 错误组统计
        if error_groups:
            lines.append(f"\n🔍 发现 {len(error_groups)} 种错误模式")
            if error_groups:
                top_error = error_groups[0]
                lines.append(f"   最常见错误: {top_error.pattern[:60]}...")
                lines.append(f"   出现次数: {top_error.count} 次")
        
        # 异常状态
        if anomaly.detected:
            lines.append(f"\n🚨 检测到异常! 异常分数: {anomaly.score:.2f}")
            for reason in anomaly.reasons:
                lines.append(f"   • {reason}")
        else:
            lines.append("\n✅ 未检测到明显异常")
        
        return "\n".join(lines)
    
    def _generate_recommendations(self, error_groups: List[LogGroup],
                                 anomaly: AnomalyDetection) -> List[str]:
        """生成修复建议"""
        recommendations = []
        
        # 基于错误模式的建议
        for group in error_groups[:3]:
            pattern = group.pattern
            
            # 特定模式匹配
            if 'Connection' in pattern or 'timeout' in pattern.lower():
                recommendations.append("🔌 建议检查网络连接配置和超时设置")
            if 'memory' in pattern.lower() or 'OutOfMemory' in pattern:
                recommendations.append("💾 建议增加内存分配或检查内存泄漏")
            if 'permission' in pattern.lower() or 'denied' in pattern.lower():
                recommendations.append("🔐 建议检查文件/目录权限配置")
            if 'database' in pattern.lower() or 'sql' in pattern.lower():
                recommendations.append("🗄️ 建议检查数据库连接池和查询性能")
            if 'null' in pattern.lower() or 'None' in pattern:
                recommendations.append("🐛 建议添加空值检查和异常处理")
            if 'authentication' in pattern.lower() or 'auth' in pattern.lower():
                recommendations.append("🔑 建议检查认证令牌和会话配置")
        
        # 基于异常检测的建议
        if anomaly.detected:
            if any('error rate' in r.lower() for r in anomaly.reasons):
                recommendations.append("📈 高错误率需要立即关注，建议检查最近部署的变更")
            if any('burst' in r.lower() for r in anomaly.reasons):
                recommendations.append("⚡ 检测到错误突增，可能存在级联故障，建议检查依赖服务")
        
        # 默认建议
        if not recommendations:
            recommendations.append("✅ 系统运行正常，建议继续保持当前监控策略")
        
        return recommendations
    
    def generate_report(self, output_format: str = 'text') -> str:
        """
        生成分析报告
        
        Args:
            output_format: 输出格式 (text, json, html)
            
        Returns:
            格式化的报告字符串
        """
        if not self.result:
            return "No analysis results available. Run analyze() first."
        
        if output_format == 'json':
            import json
            return json.dumps(self.result.to_dict(), indent=2, ensure_ascii=False)
        
        elif output_format == 'html':
            return self._generate_html_report()
        
        else:  # text
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """生成文本格式报告"""
        if not self.result:
            return ""
        
        lines = []
        lines.append("=" * 60)
        lines.append("📋 LogMind 日志分析报告")
        lines.append("=" * 60)
        lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"分析日志数: {self.result.total_entries}")
        
        lines.append("\n\n📊 日志级别分布:")
        for level, count in self.result.level_distribution.items():
            pct = count / self.result.total_entries * 100 if self.result.total_entries > 0 else 0
            bar = "█" * int(pct / 2)
            lines.append(f"  {level:10s} | {bar:25s} | {count:6d} ({pct:5.1f}%)")
        
        if self.result.error_groups:
            lines.append("\n\n🔴 错误模式分析 (Top 10):")
            for i, group in enumerate(self.result.error_groups, 1):
                lines.append(f"\n  [{i}] {group.pattern[:70]}")
                lines.append(f"      出现次数: {group.count}")
                if group.first_seen:
                    lines.append(f"      首次出现: {group.first_seen}")
                if group.last_seen:
                    lines.append(f"      最后出现: {group.last_seen}")
                if group.samples:
                    lines.append(f"      示例消息: {group.samples[0][:80]}...")
        
        if self.result.top_sources:
            lines.append("\n\n📍 主要日志来源 (Top 10):")
            for source, count in self.result.top_sources:
                lines.append(f"  {source or '(unknown)':30s} | {count:6d}")
        
        if self.result.anomaly_score > 0:
            lines.append(f"\n\n🚨 异常分数: {self.result.anomaly_score:.2f}")
            if self.result.anomaly_score >= self.anomaly_threshold:
                lines.append("   状态: ⚠️ 检测到异常，建议立即检查!")
        
        if self.result.recommendations:
            lines.append("\n\n💡 建议:")
            for rec in self.result.recommendations:
                lines.append(f"  {rec}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    def _generate_html_report(self) -> str:
        """生成HTML格式报告"""
        if not self.result:
            return ""
        
        # 简单的HTML模板
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>LogMind Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
        .level-bar {{ display: flex; align-items: center; margin: 5px 0; }}
        .level-name {{ width: 100px; }}
        .level-count {{ width: 80px; text-align: right; }}
        .error-pattern {{ background: #ffe6e6; padding: 10px; margin: 10px 0; border-left: 4px solid #e74c3c; }}
        .recommendation {{ background: #e8f5e9; padding: 10px; margin: 5px 0; border-left: 4px solid #4caf50; }}
        .anomaly {{ background: #fff3e0; padding: 15px; border-left: 4px solid #ff9800; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 LogMind 日志分析报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>分析日志数: <strong>{self.result.total_entries}</strong></p>
    </div>
    
    <div class="section">
        <h2>📊 日志级别分布</h2>
        {''.join(f"<p>{level}: {count} ({count/self.result.total_entries*100:.1f}%)</p>" 
                 for level, count in self.result.level_distribution.items())}
    </div>
    
    <div class="section">
        <h2>🔴 错误模式分析</h2>
        {''.join(f'''
        <div class="error-pattern">
            <strong>{g.pattern[:100]}</strong><br>
            出现次数: {g.count}
        </div>''' for g in self.result.error_groups[:10])}
    </div>
    
    {"<div class='anomaly'><h2>🚨 异常检测</h2><p>异常分数: " + str(self.result.anomaly_score) + "</p></div>" if self.result.anomaly_score > 0 else ""}
    
    <div class="section">
        <h2>💡 建议</h2>
        {''.join(f'<div class="recommendation">{rec}</div>' for rec in self.result.recommendations)}
    </div>
</body>
</html>
"""
        return html


class StreamAnalyzer:
    """
    流式日志分析器
    支持实时日志流分析和增量更新
    """
    
    def __init__(self, window_size: int = 1000):
        """
        初始化流式分析器
        
        Args:
            window_size: 滑动窗口大小
        """
        self.window_size = window_size
        self.entries: List[LogEntry] = []
        self.level_buffer: Dict[LogLevel, int] = defaultdict(int)
        self.last_analysis: Optional[AnalysisResult] = None
        
    def add_entry(self, entry: LogEntry):
        """添加单条日志"""
        self.entries.append(entry)
        self.level_buffer[entry.level] += 1
        
        # 滑动窗口：保持最近的日志
        if len(self.entries) > self.window_size:
            removed = self.entries.pop(0)
            self.level_buffer[removed.level] -= 1
    
    def add_entries(self, entries: List[LogEntry]):
        """批量添加日志"""
        for entry in entries:
            self.add_entry(entry)
    
    def get_realtime_stats(self) -> Dict[str, Any]:
        """获取实时统计"""
        return {
            'total_entries': len(self.entries),
            'level_distribution': dict(self.level_buffer),
            'error_count': self.level_buffer[LogLevel.ERROR] + self.level_buffer[LogLevel.CRITICAL]
        }
