# 🤝 贡献指南

感谢您对 LogMind 的关注！欢迎贡献代码。

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/gitstq/LogMind-Engine.git
cd LogMind-Engine

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"
```

## 代码规范

### Python代码规范

- 使用 [Black](https://github.com/psf/black) 格式化代码
- 使用 [isort](https://github.com/PyCQA/isort) 整理导入
- 使用类型提示提高代码可读性

```bash
# 格式化代码
black .

# 检查导入顺序
isort .

# 类型检查
mypy logmind/
```

### Git提交规范

使用 Angular 提交规范：

```
feat: 新增功能
fix: 修复问题
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 代码重构
perf: 性能优化
test: 测试相关
chore: 构建/工具相关
```

示例：
```bash
git commit -m "feat(parser): 添加JSON格式自动检测"
git commit -m "fix(analyzer): 修复时间分析边界问题"
git commit -m "docs: 更新README多语言版本"
```

## 测试

```bash
# 运行所有测试
pytest

# 带覆盖率报告
pytest --cov=logmind --cov-report=html

# 只运行特定测试
pytest tests/test_logmind.py::TestLogParser
```

## Pull Request 流程

1. Fork 本仓库
2. 创建特性分支 `git checkout -b feature/your-feature`
3. 提交更改 `git commit -m "feat: add your feature"`
4. 推送到分支 `git push origin feature/your-feature`
5. 创建 Pull Request

## 问题反馈

请通过 [GitHub Issues](https://github.com/gitstq/LogMind-Engine/issues) 反馈问题，包含以下信息：

- 问题描述
- 复现步骤
- 环境信息（Python版本、操作系统等）
- 相关日志或截图

---

## 🎯 待办功能

如果您想贡献代码，可以关注以下待办功能：

- [ ] 流式日志监控模式
- [ ] Web Dashboard
- [ ] MCP协议集成
- [ ] 更多日志格式支持
- [ ] 性能优化

---

再次感谢您的贡献！🙏
