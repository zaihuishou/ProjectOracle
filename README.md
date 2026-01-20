# ProjectOracle

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> **理解任何代码库只需一行命令** — AI驱动的项目分析与文档自动生成工具

ProjectOracle通过AI技术自动分析你的代码库,生成详细的架构文档,帮助开发者(和AI助手)快速理解项目结构。

## ✨ 核心特性

- 🔍 **智能项目扫描** - 尊重`.gitignore`,支持大型项目智能采样
- 🧬 **AST符号提取** - 原生Python AST解析,准确提取类/函数/导入
- 💰 **成本控制** - LLM费用估算和限制,避免意外高额账单
- 🎨 **Mermaid架构图** - 自动生成可视化架构图表
- 🔒 **安全扫描** - 检测硬编码密钥和敏感数据
- 🚀 **高性能** - 并发处理,可分析5000+文件
- ⚙️ **灵活配置** - JSON/TOML多源配置支持
- 🤖 **MCP集成** - 完美集成Claude Desktop和Continue

## 🚀 快速开始

### 安装

```bash
pip install project-oracle
```

### 基本使用

```bash
# 1. 设置API密钥
export ANTHROPIC_API_KEY="your-api-key-here"

# 2. 分析项目
project-oracle /path/to/your/project

# 3. 查看生成的报告
cat /path/to/your/project/.ProjectOracle
```

### 高级选项

```bash
# 交互模式
project-oracle /path/to/project --interactive

# 预览成本(不实际分析)
project-oracle /path/to/project --dry-run

# 自定义限制
project-oracle /path/to/project --max-files 10000 --max-cost 1.00

# 强制重新生成
project-oracle /path/to/project --force

# 详细日志
project-oracle /path/to/project --verbose
```

## 🔌 作为MCP服务器使用

ProjectOracle可以作为MCP服务器集成到支持MCP协议的AI助手中。

### Claude Desktop配置

1. 找到Claude Desktop配置文件:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. 添加ProjectOracle服务器配置:

```json
{
  "mcpServers": {
    "project-oracle": {
      "command": "python3",
      "args": ["-m", "project_oracle"],
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

3. 重启Claude Desktop

4. 现在可以在对话中使用:
   ```
   请使用project-oracle分析 /path/to/my/project
   ```

### Continue (VSCode) 配置

在Continue配置中添加:

```json
{
  "mcpServers": {
    "project-oracle": {
      "command": "python3",
      "args": ["-m", "project_oracle"]
    }
  }
}
```

## 📊 生成的报告内容

`.ProjectOracle`报告包含:

1. **🏗️ 基础信息** - 技术栈、框架、入口点
2. **🏛️ 架构骨架** - Mermaid图表或文本流程图
3. **🗺️ 核心模块** - 模块职责和关键组件表格
4. **📋 数据契约** - 模型和API端点
5. **🤖 AI开发指南** - 快速开始和注意事项
6. **📊 项目统计** - 文件、类、函数数量
7. **🔄 改进建议** - 下一步优化方向
8. **⚠️ 安全警告** - 检测到的潜在问题(可选)

## ⚙️ 配置

在项目根目录创建`.projectoracle.config.json`:

```json
{
  "scan": {
    "max_files": 5000,
    "max_depth": 4,
    "workers": 4
  },
  "llm": {
    "max_cost_usd": 0.50,
    "model": "claude-3-5-sonnet-20241022"
  },
  "security": {
    "scan_for_secrets": false
  }
}
```

或在`pyproject.toml`中:

```toml
[tool.projectoracle]
max_files = 5000

[tool.projectoracle.llm]
max_cost_usd = 0.50
```

详细配置选项请查看[配置文档](INSTALL.md)。

## 📖 工作原理

```mermaid
graph LR
    A[扫描项目] --> B[提取符号]
    B --> C[LLM分析]
    C --> D[生成报告]
    D --> E[.ProjectOracle]
```

1. **扫描** - 遍历项目文件,尊重`.gitignore`规则
2. **提取** - 使用Python AST解析代码结构
3. **分类** - 智能识别内部/外部导入
4. **分析** - Claude AI理解架构和业务逻辑
5. **生成** - 创建Markdown格式的详细文档

## 🛠️ 系统要求

- Python 3.10+
- Anthropic API密钥
- 操作系统: macOS, Linux, Windows

## 🤝 贡献

欢迎贡献!请查看[贡献指南](CONTRIBUTING.md)了解如何参与。

### 开发设置

```bash
# 克隆仓库
git clone https://github.com/zaihuishou/ProjectOracle.git
cd ProjectOracle

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/

# 代码格式化
black src/
ruff check src/
```

## 📄 许可证

本项目采用[MIT许可证](LICENSE)。

## 🙏 致谢

- 使用[Model Context Protocol (MCP)](https://modelcontextprotocol.io/)进行AI集成
- 由[Anthropic Claude](https://www.anthropic.com/)提供支持
- 灵感来自于让AI更好地理解代码的愿景

## 📞 支持

- 🐛 [报告Bug](https://github.com/zaihuishou/ProjectOracle/issues)
- 💡 [功能请求](https://github.com/zaihuishou/ProjectOracle/issues)
- 📖 [文档](https://github.com/zaihuishou/ProjectOracle#readme)
- 💬 [讨论区](https://github.com/zaihuishou/ProjectOracle/discussions)

---

**使用ProjectOracle让AI真正理解你的代码库!** ⭐ 如果觉得有用,请给个Star!
