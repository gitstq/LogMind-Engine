#!/usr/bin/env python3
"""
LogMind TUI Module - 终端用户界面模块
基于Rich库构建的美观终端界面
"""

import sys
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.layout import Layout
    from rich.live import Live
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from .parser import LogParser, LogEntry, LogLevel, LogGroup, LogFormat
from .analyzer import LogAnalyzer, AnalysisResult, AnomalyDetection


class LogMindTUI:
    """
    LogMind 终端用户界面
    提供交互式的日志分析体验
    """
    
    def __init__(self):
        """初始化TUI"""
        self.console = Console() if HAS_RICH else None
        self.parser = LogParser()
        self.analyzer = LogAnalyzer(self.parser)
        self.entries: List[LogEntry] = []
        self.result: Optional[AnalysisResult] = None
        
    def print_banner(self):
        """打印欢迎横幅"""
        if not HAS_RICH:
            print("=" * 60)
            print("LogMind - 智能日志分析引擎")
            print("=" * 60)
            return
        
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██╗     ██╗   ██╗███╗  ██╗ ██████╗ ██████╗ ███╗   ██╗      ║
║   ██║     ██║   ██║████╗ ██║██╔═══██╗██╔══██╗████╗  ██║      ║
║   ██║     ██║   ██║██╔██╗██║██║   ██║██████╔╝██╔██╗██║      ║
║   ██║     ██║   ██║██║╚████║██║   ██║██╔══██╗██║╚████║      ║
║   ███████╗╚██████╔╝██║ ╚███║╚██████╔╝██║  ██║██║ ╚███║      ║
║   ╚══════╝ ╚═════╝ ╚═╝  ╚══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚══╝      ║
║                                                               ║
║   🧠 Lightweight Intelligent Log Analysis Engine              ║
║   📖 轻量级智能日志分析引擎                                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="bold cyan")
    
    def print_statistics(self, stats: Dict[str, Any]):
        """打印统计信息表格"""
        if not HAS_RICH or not self.console:
            self._print_statistics_plain(stats)
            return
        
        # 创建统计表格
        table = Table(title="📊 日志统计概览", show_header=True, header_style="bold magenta")
        table.add_column("指标", style="cyan", width=25)
        table.add_column("数值", style="green", width=20)
        table.add_column("说明", style="white", width=35)
        
        table.add_row("总日志条数", str(stats.get('total_entries', 0)), "📝")
        table.add_row("检测格式", stats.get('format_detected', 'unknown').upper(), "🔍")
        table.add_row("错误数量", str(stats.get('error_count', 0)), "🔴")
        
        # 时间范围
        time_range = stats.get('time_range', {})
        if time_range.get('start') and time_range.get('end'):
            table.add_row("时间范围", f"{time_range['start'][:19]} ~", "⏰")
        
        self.console.print(table)
        
        # 日志级别分布
        level_dist = stats.get('level_distribution', {})
        if level_dist:
            self._print_level_bar(level_dist, stats.get('total_entries', 1))
    
    def _print_statistics_plain(self, stats: Dict[str, Any]):
        """打印统计信息（纯文本模式）"""
        print("\n📊 日志统计概览")
        print("-" * 50)
        print(f"  总日志条数: {stats.get('total_entries', 0)}")
        print(f"  检测格式: {stats.get('format_detected', 'unknown').upper()}")
        print(f"  错误数量: {stats.get('error_count', 0)}")
        
        level_dist = stats.get('level_distribution', {})
        if level_dist:
            print("\n📈 日志级别分布:")
            for level, count in sorted(level_dist.items(), 
                                       key=lambda x: ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'UNKNOWN'].index(x[0]) if x[0] in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'UNKNOWN'] else 5):
                pct = count / stats.get('total_entries', 1) * 100
                bar = "█" * int(pct / 2)
                print(f"  {level:10s} | {bar:25s} | {count:6d} ({pct:5.1f}%)")
    
    def _print_level_bar(self, level_dist: Dict[str, int], total: int):
        """打印日志级别分布条形图"""
        if not HAS_RICH or not self.console:
            return
        
        level_icons = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '🔴',
            'CRITICAL': '🚨',
            'UNKNOWN': '❓'
        }
        
        # 按严重程度排序
        order = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'UNKNOWN']
        sorted_levels = sorted(level_dist.items(), 
                             key=lambda x: order.index(x[0]) if x[0] in order else 5)
        
        for level, count in sorted_levels:
            pct = count / total * 100 if total > 0 else 0
            emoji = level_icons.get(level, '📌')
            bar = Text()
            
            # 根据级别使用不同颜色
            color = {
                'CRITICAL': 'red bold',
                'ERROR': 'red',
                'WARNING': 'yellow',
                'INFO': 'blue',
                'DEBUG': 'cyan',
                'UNKNOWN': 'white'
            }.get(level, 'white')
            
            bar.append(f"{emoji} {level:10s} ", style=color)
            bar.append("█" * int(pct / 2), style=color)
            bar.append(f" {count:6d} ({pct:5.1f}%)", style="white")
            
            self.console.print(bar)
    
    def print_error_groups(self, groups: List[LogGroup], limit: int = 10):
        """打印错误分组"""
        if not HAS_RICH or not self.console:
            self._print_error_groups_plain(groups, limit)
            return
        
        if not groups:
            self.console.print(Panel("✅ 未发现错误日志", style="green"))
            return
        
        self.console.print(f"\n🔴 发现 {len(groups)} 种错误模式\n")
        
        for i, group in enumerate(groups[:limit], 1):
            # 创建错误组面板
            pattern_text = Text(group.pattern[:80] + "..." if len(group.pattern) > 80 else group.pattern)
            
            severity = "red bold" if group.count > 5 else "red"
            
            content = []
            content.append(f"[bold]出现次数:[/bold] {group.count}")
            
            if group.first_seen:
                content.append(f"[bold]首次出现:[/bold] {group.first_seen}")
            if group.last_seen:
                content.append(f"[bold]最后出现:[/bold] {group.last_seen}")
            
            if group.samples:
                content.append(f"\n[bold]示例消息:[/bold]")
                for sample in group.samples[:2]:
                    content.append(f"  📄 {sample[:100]}...")
            
            panel = Panel(
                "\n".join(content),
                title=f"[{severity}] [{i}] 错误模式[/]",
                border_style=severity,
                width=80
            )
            self.console.print(panel)
    
    def _print_error_groups_plain(self, groups: List[LogGroup], limit: int = 10):
        """打印错误分组（纯文本模式）"""
        if not groups:
            print("\n✅ 未发现错误日志")
            return
        
        print(f"\n🔴 发现 {len(groups)} 种错误模式\n")
        
        for i, group in enumerate(groups[:limit], 1):
            print(f"[{i}] {'='*60}")
            print(f"    模式: {group.pattern[:80]}")
            print(f"    次数: {group.count}")
            if group.first_seen:
                print(f"    首次: {group.first_seen}")
            if group.last_seen:
                print(f"    最后: {group.last_seen}")
            if group.samples:
                print(f"    示例: {group.samples[0][:100]}")
            print()
    
    def print_anomaly(self, anomaly: AnomalyDetection):
        """打印异常检测结果"""
        if not HAS_RICH or not self.console:
            self._print_anomaly_plain(anomaly)
            return
        
        if not anomaly.detected:
            self.console.print(Panel("✅ 未检测到异常", style="green"))
            return
        
        # 异常警告面板
        severity_color = "red bold" if anomaly.score > 0.7 else "yellow bold"
        
        content = []
        content.append(f"[bold]异常分数:[/bold] [red]{anomaly.score:.2f}[/red]")
        content.append("\n[bold]检测原因:[/bold]")
        for reason in anomaly.reasons:
            content.append(f"  ⚠️ {reason}")
        
        panel = Panel(
            "\n".join(content),
            title="🚨 异常检测警告",
            border_style="red",
            width=80
        )
        self.console.print(panel)
    
    def _print_anomaly_plain(self, anomaly: AnomalyDetection):
        """打印异常检测结果（纯文本模式）"""
        if not anomaly.detected:
            print("\n✅ 未检测到异常")
            return
        
        print("\n🚨 异常检测警告")
        print("-" * 50)
        print(f"  异常分数: {anomaly.score:.2f}")
        print("  检测原因:")
        for reason in anomaly.reasons:
            print(f"    ⚠️ {reason}")
    
    def print_recommendations(self, recommendations: List[str]):
        """打印建议"""
        if not HAS_RICH or not self.console:
            self._print_recommendations_plain(recommendations)
            return
        
        if not recommendations:
            return
        
        self.console.print("\n💡 智能建议:", style="bold green")
        for rec in recommendations:
            self.console.print(f"  {rec}")
    
    def _print_recommendations_plain(self, recommendations: List[str]):
        """打印建议（纯文本模式）"""
        if not recommendations:
            return
        
        print("\n💡 智能建议:")
        for rec in recommendations:
            print(f"  {rec}")
    
    def print_full_report(self, result: AnalysisResult):
        """打印完整分析报告"""
        if not HAS_RICH or not self.console:
            print(self.analyzer.generate_report('text'))
            return
        
        self.console.print("\n")
        self.console.print(Panel.fit(
            f"[bold cyan]LogMind 日志分析报告[/bold cyan]\n"
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            border_style="cyan"
        ))
        
        # 统计概览
        self.console.print("\n[bold]📊 统计概览[/bold]")
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column(style="cyan")
        stats_table.add_column(style="green")
        stats_table.add_row("总日志条数", str(result.total_entries))
        stats_table.add_row("错误模式数", str(len(result.error_groups)))
        stats_table.add_row("异常分数", f"{result.anomaly_score:.2f}")
        self.console.print(stats_table)
        
        # 级别分布
        if result.level_distribution:
            self.console.print("\n[bold]📈 日志级别分布[/bold]")
            self._print_level_bar(result.level_distribution, result.total_entries)
        
        # 错误模式
        if result.error_groups:
            self.console.print("\n[bold]🔴 错误模式分析[/bold]")
            self._print_error_groups_plain(result.error_groups, 5)
        
        # 异常检测
        if result.anomaly_score > 0:
            anomaly = AnomalyDetection(
                detected=result.anomaly_score >= 0.7,
                score=result.anomaly_score
            )
            self.console.print("\n[bold]🚨 异常检测[/bold]")
            self._print_anomaly_plain(anomaly)
        
        # 建议
        if result.recommendations:
            self.console.print("\n[bold]💡 建议[/bold]")
            self._print_recommendations_plain(result.recommendations)
        
        self.console.print("\n" + "=" * 70)
    
    def print_entries(self, entries: List[LogEntry], limit: int = 50):
        """打印日志条目列表"""
        if not HAS_RICH or not self.console:
            self._print_entries_plain(entries, limit)
            return
        
        # 创建日志条目表格
        table = Table(title=f"📋 日志条目 (显示前 {min(limit, len(entries))} 条)", 
                     show_header=True, header_style="bold magenta")
        
        table.add_column("行号", style="cyan", width=8)
        table.add_column("时间", style="white", width=20)
        table.add_column("级别", style="white", width=10)
        table.add_column("消息", style="white", width=52)
        
        for entry in entries[:limit]:
            level_style = {
                'DEBUG': 'cyan',
                'INFO': 'blue',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red bold',
                'UNKNOWN': 'white'
            }.get(entry.level.value, 'white')
            
            timestamp_str = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S') if entry.timestamp else '-'
            message = entry.message[:50] + "..." if len(entry.message) > 50 else entry.message
            
            table.add_row(
                str(entry.line_number),
                timestamp_str,
                f"[{level_style}]{entry.level.value}[/{level_style}]",
                message
            )
        
        self.console.print(table)
    
    def _print_entries_plain(self, entries: List[LogEntry], limit: int = 50):
        """打印日志条目列表（纯文本模式）"""
        print(f"\n📋 日志条目 (显示前 {min(limit, len(entries))} 条)")
        print("-" * 100)
        
        for entry in entries[:limit]:
            timestamp_str = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S') if entry.timestamp else '-'
            message = entry.message[:60] + "..." if len(entry.message) > 60 else entry.message
            print(f"{entry.line_number:6d} | {timestamp_str:20s} | {entry.level.value:10s} | {message}")
    
    def print_help(self):
        """打印帮助信息"""
        if not HAS_RICH or not self.console:
            self._print_help_plain()
            return
        
        help_text = """
[bold]📖 LogMind 使用帮助[/bold]

[bold cyan]基本命令:[/bold cyan]
  analyze <file>     分析日志文件
  stats               显示统计信息
  errors              显示错误分组
  entries [n]         显示日志条目 (默认50条)
  anomaly             显示异常检测结果
  report              显示完整分析报告
  help                显示帮助信息
  quit / exit / q    退出程序

[bold cyan]快捷键:[/bold cyan]
  Ctrl+C              退出程序
  Ctrl+L              清除屏幕

[bold cyan]示例:[/bold cyan]
  logmind analyze /var/log/app.log
  logmind analyze /var/log/app.log --limit 1000
  cat app.log | logmind analyze -
        """
        
        panel = Panel(help_text, title="📖 帮助", border_style="cyan")
        self.console.print(panel)
    
    def _print_help_plain(self):
        """打印帮助信息（纯文本模式）"""
        print("""
📖 LogMind 使用帮助

基本命令:
  analyze <file>     分析日志文件
  stats              显示统计信息
  errors             显示错误分组
  entries [n]        显示日志条目 (默认50条)
  anomaly            显示异常检测结果
  report             显示完整分析报告
  help               显示帮助信息
  quit / exit / q    退出程序

示例:
  logmind analyze /var/log/app.log
  cat app.log | logmind analyze -
        """)


class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, console: Optional[Any] = None):
        """初始化进度跟踪器"""
        self.console = console or (Console() if HAS_RICH else None)
        self.progress: Optional[Progress] = None
        
    def __enter__(self):
        """上下文管理器入口"""
        if HAS_RICH and self.console:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            )
            self.progress.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self.progress:
            self.progress.__exit__(exc_type, exc_val, exc_tb)
    
    def add_task(self, description: str, total: int = 100) -> int:
        """添加任务"""
        if self.progress:
            return self.progress.add_task(description, total=total)
        return 0
    
    def update(self, task_id: int, advance: int = 1, **kwargs):
        """更新任务进度"""
        if self.progress:
            self.progress.update(task_id, advance=advance, **kwargs)
