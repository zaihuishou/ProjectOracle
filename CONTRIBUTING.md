# Contributing to ProjectOracle

首先,感谢你考虑为ProjectOracle做出贡献!🎉

## 行为准则

本项目遵循友好、包容的开源社区准则。参与即表示你同意维护尊重和建设性的环境。

## 如何贡献

### 报告Bug 🐛

发现Bug?请帮助我们改进!

1. 检查[Issues](https://github.com/zaihuishou/ProjectOracle/issues)确认问题未被报告
2. 创建新Issue,包含:
   - 清晰的标题
   - 复现步骤
   - 预期行为vs实际行为
   - 环境信息(Python版本、OS等)
   - 相关日志或截图

### 提议新功能 💡

有好想法?我们乐意倾听!

1. 先在[Discussions](https://github.com/zaihuishou/ProjectOracle/discussions)讨论
2. 如果获得积极反馈,创建Feature Request Issue
3. 描述:
   - 功能用途和使用场景
   - 可能的实现方案
   - 是否愿意贡献代码

### 提交代码 🔧

#### 开发环境设置

```bash
# 1. Fork并克隆仓库
git clone https://github.com/your-username/ProjectOracle.git
cd ProjectOracle

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装开发依赖
pip install -e ".[dev]"

# 4. 创建功能分支
git checkout -b feature/your-feature-name
```

#### 代码规范

我们使用以下工具保持代码质量:

```bash
# 格式化代码
black src/ tests/

# 检查代码风格
ruff check src/ tests/

# 类型检查(可选但推荐)
mypy src/
```

**编码标准**:
- 遵循PEP 8
- 使用类型注解
- 添加docstring(Google风格)
- 保持函数简洁(< 50行)
- 测试新功能

#### 提交消息规范

使用清晰的提交消息:

```
feat: add support for JavaScript AST parsing
fix: correct gitignore pattern matching
docs: update MCP configuration examples
test: add scanner test cases
refactor: simplify symbol extraction logic
```

#### Pull Request流程

1. **确保测试通过**:
   ```bash
   pytest tests/
   ```

2. **更新文档**:
   - 如果改变API,更新相关文档
   - 在CHANGELOG.md中记录变更

3. **创建PR**:
   - 提供清晰的描述
   - 关联相关Issue(`Closes #123`)
   - 请求代码审查

4. **响应反馈**:
   - 及时回复审查意见
   - 必要时进行修改

### 测试 🧪

#### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_scanner.py

# 查看覆盖率
pytest --cov=project_oracle tests/
```

#### 添加测试

为新功能添加测试:

```python
# tests/test_new_feature.py
import pytest
from project_oracle.core import YourNewClass

def test_basic_functionality():
    """Test basic usage of new feature."""
    obj = YourNewClass()
    result = obj.your_method()
    assert result == expected_value

def test_edge_case():
    """Test edge case handling."""
    obj = YourNewClass()
    with pytest.raises(ValueError):
        obj.your_method(invalid_input)
```

## 项目结构

```
ProjectOracle/
├── src/project_oracle/
│   ├── __init__.py
│   ├── __main__.py        # MCP server entry
│   ├── cli.py             # CLI interface
│   ├── server.py          # MCP server
│   ├── models.py          # Data models
│   ├── core/
│   │   ├── scanner.py     # File scanning
│   │   ├── symbol_extractor.py  # AST parsing
│   │   ├── oracle_engine.py     # LLM analysis
│   │   └── config.py      # Config management
│   └── utils/
│       └── __init__.py    # Utilities
├── tests/
│   ├── test_scanner.py
│   ├── test_parser.py
│   └── test_engine.py
├── docs/                  # Documentation
├── examples/              # Example projects
└── pyproject.toml
```

## 开发重点领域

欢迎在以下方面贡献:

### 高优先级 🔥
- [ ] 添加更多语言支持(JavaScript, TypeScript, Go)
- [ ] 改进Mermaid图表生成
- [ ] 增强测试覆盖率
- [ ] 性能优化(大项目处理)

### 中优先级 ⭐
- [ ] 添加Lock系统(增量更新)
- [ ] 安全扫描功能增强
- [ ] 更多配置选项
- [ ] 文档改进

### 低优先级 📋
- [ ] 国际化(i18n)
- [ ] Web UI  
- [ ] 更多输出格式(JSON, HTML)
- [ ] 插件系统

## 发布流程

(维护者专用)

1. 更新版本号:
   ```bash
   # 在pyproject.toml中更新version
   ```

2. 更新CHANGELOG.md

3. 创建发布标签:
   ```bash
   git tag -a v1.0.1 -m "Release v1.0.1"
   git push origin v1.0.1
   ```

4. GitHub Actions自动发布到PyPI

## 获取帮助

遇到问题?

- 📖 查看[文档](README.md)
- 💬 在[Discussions](https://github.com/zaihuishou/ProjectOracle/discussions)提问
- 🐛 搜索[已知Issue](https://github.com/zaihuishou/ProjectOracle/issues)

## 许可证

通过贡献代码,你同意你的贡献基于[MIT许可证](LICENSE)。

---

再次感谢你的贡献!每个PR和Issue都让ProjectOracle变得更好! ❤️
