#!/usr/bin/env python3
"""
LogMind CLI - 命令行入口
轻量级智能日志分析引擎命令行工具
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional, List

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from logmind.parser import LogParser, LogLevel
from logmind.analyzer import LogAnalyzer, AnalysisResult
from logmind.tui import LogMindTUI
from logmind.ai_providers import AIManager, AIConfig


def setup_logging(verbose: bool = False):
    """设置日志配置"""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def cmd_analyze(args):
    """分析日志文件"""
    tui = LogMindTUI()
    tui.print_banner()
    
    parser = LogParser()
    analyzer = LogAnalyzer(parser)
    
    try:
        # 解析日志
        if args.file == '-':
            # 从标准输入读取
            if sys.stdin.isatty():
                print("❌ 请通过管道传入日志数据，例如: cat app.log | logmind analyze -")
                return 1
            content = sys.stdin.read()
            entries = parser.parse_content(content)
        else:
            # 从文件读取
            if not Path(args.file).exists():
                print(f"❌ 文件不存在: {args.file}")
                return 1
            entries = parser.parse_file(args.file, limit=args.limit)
        
        if not entries:
            print("⚠️ 未解析到任何日志条目")
            return 0
        
        # 显示统计信息
        stats = parser.get_statistics()
        tui.print_statistics(stats)
        
        # 执行分析
        if args.analyze:
            result = analyzer.analyze(entries)
            
            # 显示错误分组
            tui.print_error_groups(result.error_groups, limit=10)
            
            # 显示异常检测
            tui.print_anomaly(analyzer._detect_anomalies())
            
            # 显示建议
            tui.print_recommendations(result.recommendations)
            
            # AI增强分析
            if args.ai:
                ai_manager = AIManager(AIConfig.from_env())
                if ai_manager.is_available():
                    print("\n🤖 AI智能分析...")
                    for group in result.error_groups[:3]:
                        print(f"\n分析错误模式: {group.pattern[:50]}...")
                        analysis = ai_manager.analyze_error(group.pattern, "\n".join(group.samples))
                        print(analysis)
                else:
                    print("\n⚠️ AI服务不可用，请设置相应的API密钥")
        
        # 显示日志条目
        if args.show_entries:
            tui.print_entries(entries, limit=args.show_entries)
        
        # 输出JSON报告
        if args.json:
            import json
            result = analyzer.analyze(entries)
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        
        # 输出HTML报告
        if args.html:
            result = analyzer.analyze(entries)
            html = analyzer.generate_report('html')
            output_file = args.html if args.html != True else 'logmind_report.html'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ HTML报告已保存到: {output_file}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_stats(args):
    """显示统计信息"""
    tui = LogMindTUI()
    
    if not args.file or args.file == '-':
        print("❌ 请指定日志文件")
        return 1
    
    parser = LogParser()
    entries = parser.parse_file(args.file, limit=args.limit)
    stats = parser.get_statistics()
    tui.print_statistics(stats)
    return 0


def cmd_errors(args):
    """显示错误分组"""
    tui = LogMindTUI()
    
    parser = LogParser()
    if args.file == '-':
        content = sys.stdin.read()
        entries = parser.parse_content(content)
    else:
        entries = parser.parse_file(args.file, limit=args.limit)
    
    groups = parser.group_by_pattern()
    tui.print_error_groups(groups, limit=args.limit or 10)
    return 0


def cmd_entries(args):
    """显示日志条目"""
    tui = LogMindTUI()
    
    parser = LogParser()
    if args.file == '-':
        content = sys.stdin.read()
        entries = parser.parse_content(content)
    else:
        entries = parser.parse_file(args.file, limit=args.limit)
    
    tui.print_entries(entries, limit=args.limit or 50)
    return 0


def cmd_report(args):
    """生成完整报告"""
    tui = LogMindTUI()
    
    parser = LogParser()
    analyzer = LogAnalyzer(parser)
    
    if args.file == '-':
        content = sys.stdin.read()
        entries = parser.parse_content(content)
    else:
        entries = parser.parse_file(args.file, limit=args.limit)
    
    result = analyzer.analyze(entries)
    tui.print_full_report(result)
    
    if args.output:
        if args.output.endswith('.json'):
            import json
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        elif args.output.endswith('.html'):
            html = analyzer.generate_report('html')
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(html)
        else:
            text = analyzer.generate_report('text')
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
        print(f"✅ 报告已保存到: {args.output}")
    
    return 0


def cmd_interactive(args):
    """交互式模式"""
    tui = LogMindTUI()
    tui.print_banner()
    tui.print_help()
    
    current_entries = []
    current_result = None
    
    while True:
        try:
            command = input("\nlogmind> ").strip()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            args_list = parts[1:]
            
            if cmd in ('quit', 'exit', 'q'):
                print("👋 再见!")
                break
            
            elif cmd == 'help':
                tui.print_help()
            
            elif cmd == 'load':
                if not args_list:
                    print("❌ 请指定文件路径")
                    continue
                file_path = args_list[0]
                if not Path(file_path).exists():
                    print(f"❌ 文件不存在: {file_path}")
                    continue
                parser = LogParser()
                current_entries = parser.parse_file(file_path)
                print(f"✅ 已加载 {len(current_entries)} 条日志")
                tui.print_statistics(parser.get_statistics())
            
            elif cmd == 'stats':
                if current_entries:
                    parser = LogParser()
                    parser.entries = current_entries
                    tui.print_statistics(parser.get_statistics())
                else:
                    print("⚠️ 请先加载日志文件: load <file>")
            
            elif cmd == 'errors':
                if current_entries:
                    parser = LogParser()
                    parser.entries = current_entries
                    groups = parser.group_by_pattern()
                    tui.print_error_groups(groups)
                else:
                    print("⚠️ 请先加载日志文件: load <file>")
            
            elif cmd == 'report':
                if current_entries:
                    analyzer = LogAnalyzer()
                    result = analyzer.analyze(current_entries)
                    tui.print_full_report(result)
                else:
                    print("⚠️ 请先加载日志文件: load <file>")
            
            else:
                print(f"❌ 未知命令: {cmd}")
                print("   输入 'help' 查看帮助")
        
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except EOFError:
            break
    
    return 0


def main():
    """主函数"""
    parser_main = argparse.ArgumentParser(
        description='LogMind - 轻量级智能日志分析引擎',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  logmind analyze /var/log/app.log
  logmind analyze /var/log/app.log --limit 1000
  logmind analyze /var/log/app.log --ai
  cat app.log | logmind analyze -
  logmind report /var/log/app.log -o report.html
  logmind interactive

更多帮助: https://github.com/gitstq/LogMind
        """
    )
    
    parser_main.add_argument('--version', action='version', version='LogMind 1.0.0')
    parser_main.add_argument('-v', '--verbose', action='store_true', help='显示详细日志')
    
    subparsers = parser_main.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    p_analyze = subparsers.add_parser('analyze', help='分析日志文件')
    p_analyze.add_argument('file', help='日志文件路径 (使用 - 读取标准输入)')
    p_analyze.add_argument('--limit', '-l', type=int, help='限制解析行数')
    p_analyze.add_argument('--analyze', '-a', action='store_true', help='执行深度分析')
    p_analyze.add_argument('--ai', action='store_true', help='启用AI增强分析')
    p_analyze.add_argument('--show-entries', '-e', nargs='?', const=50, type=int, help='显示日志条目')
    p_analyze.add_argument('--json', action='store_true', help='输出JSON格式')
    p_analyze.add_argument('--html', nargs='?', const='logmind_report.html', help='输出HTML报告')
    p_analyze.set_defaults(func=cmd_analyze)
    
    # stats 命令
    p_stats = subparsers.add_parser('stats', help='显示统计信息')
    p_stats.add_argument('file', help='日志文件路径')
    p_stats.add_argument('--limit', '-l', type=int, help='限制解析行数')
    p_stats.set_defaults(func=cmd_stats)
    
    # errors 命令
    p_errors = subparsers.add_parser('errors', help='显示错误分组')
    p_errors.add_argument('file', help='日志文件路径 (使用 - 读取标准输入)')
    p_errors.add_argument('--limit', '-l', nargs='?', const=10, type=int, help='显示数量限制')
    p_errors.set_defaults(func=cmd_errors)
    
    # entries 命令
    p_entries = subparsers.add_parser('entries', help='显示日志条目')
    p_entries.add_argument('file', help='日志文件路径 (使用 - 读取标准输入)')
    p_entries.add_argument('--limit', '-l', nargs='?', const=50, type=int, help='显示数量限制')
    p_entries.set_defaults(func=cmd_entries)
    
    # report 命令
    p_report = subparsers.add_parser('report', help='生成完整报告')
    p_report.add_argument('file', help='日志文件路径 (使用 - 读取标准输入)')
    p_report.add_argument('--limit', '-l', type=int, help='限制解析行数')
    p_report.add_argument('-o', '--output', help='输出文件路径')
    p_report.set_defaults(func=cmd_report)
    
    # interactive 命令
    p_interactive = subparsers.add_parser('interactive', help='交互式模式')
    p_interactive.add_argument('--file', '-f', help='预加载日志文件')
    p_interactive.set_defaults(func=cmd_interactive)
    
    args = parser_main.parse_args()
    
    # 设置日志级别
    setup_logging(args.verbose)
    
    # 如果没有子命令，显示帮助
    if not args.command:
        # 默认执行分析
        if len(sys.argv) > 1:
            args.file = sys.argv[1]
            args.func = cmd_analyze
            args.analyze = True
            args.limit = None
            args.ai = False
            args.show_entries = None
            args.json = False
            args.html = False
        else:
            parser_main.print_help()
            return 0
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
