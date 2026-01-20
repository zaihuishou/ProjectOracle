# ProjectOracle

> AI驱动的代码分析工具 - 快速理解任何Python项目

## ✨ 特性

- 🔍 **智能扫描** - 自动识别项目结构和关键文件
- 🤖 **AI分析** - 支持Claude、GPT-4、Gemini三种AI模型
- 💰 **免费选项** - 扫描模式完全免费，Gemini有免费层级
- 📊 **详细报告** - 生成Markdown格式的架构分析报告
- 🔌 **MCP集成** - 可作为Claude Desktop的MCP服务器

---

## 🚀 快速开始

### Standard MCP Features

ProjectOracle fully implements the [Model Context Protocol](https://modelcontextprotocol.io/):

#### 🛠️ Tools
- `analyze_project`: Analyze codebase with specific LLM provider
  - Arguments: `path`, `llm_provider`, `llm_model`, `force`, `dry_run`

#### 📂 Resources
- `project:///{path}`: Read any file in the analyzed project
- **List Resources**: Automatically lists all project files

#### 💬 Prompts
- `analyze-architecture`: Guided architecture analysis
- `security-audit`: Security vulnerability assessment

#### 🤖 Multi-Provider Support
Configure via environment variables or arguments:
- **Anthropic**: `ANTHROPIC_API_KEY` (Default)
- **OpenAI**: `OPENAI_API_KEY`
- **Gemini**: `GEMINI_API_KEY`

Example MCP Config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "project-oracle": {
      "command": "uvx",
      "args": ["project-oracle"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-...",
        "OPENAI_API_KEY": "sk-...",
        "GEMINI_API_KEY": "AI..."
      }
    }
  }
}
```

### 安装

```bash
# 克隆项目
git clone https://github.com/zaihuishou/ProjectOracle.git
cd ProjectOracle

# 创建虚拟环境并安装
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

### 使用

**重要**: 每次使用前需要激活虚拟环境！

```bash
# 1. 进入项目目录
cd ProjectOracle

# 2. 激活虚拟环境
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 运行分析
project-oracle /path/to/your/project
```

或者使用Python模块方式（不需要激活虚拟环境）：

```bash
python3 -m project_oracle.cli /path/to/your/project
```

---

## 📋 交互式流程

### 步骤1: 选择分析模式

```
📋 Step 1: Choose analysis mode

  1. Scan Only (FREE - No API key needed)
     → Quick scan, basic statistics

  2. AI Analysis (Requires API key)
     → Deep analysis with architecture insights

Select mode [1]:
```

- 选择 `1` - 仅扫描（免费，无需API密钥）
- 选择 `2` - AI分析（需要API密钥）

### 步骤2: 选择AI Provider（如果选择AI分析）

```
🤖 Step 2: Choose AI Provider

  1. Claude (Anthropic) - Best quality
     Cost: ~$0.01-0.50 per analysis

  2. GPT-4 (OpenAI) - High quality
     Cost: ~$0.03-1.00 per analysis

  3. Gemini (Google) - FREE tier available!
     Cost: FREE (with limits) or very cheap

Select AI provider [3]:
```

- 选择 `1` - Claude（最佳质量，付费）
- 选择 `2` - GPT-4（高质量，付费）
- 选择 `3` - Gemini（推荐，有免费层级）

### 步骤3: 确认并开始

```
⚙️  Configuration Summary
   Mode: AI Analysis
   AI Provider: Gemini
   Max Files: 5000

▶️  Start analysis? [Y/n]:
```

---

## 🔑 获取API密钥

### Gemini (推荐 - 有免费层级)

1. 访问 https://makersuite.google.com/app/apikey
2. 创建API密钥
3. 设置环境变量:
   ```bash
   export GEMINI_API_KEY="your-key-here"
   ```

### Claude (Anthropic)

1. 访问 https://console.anthropic.com/
2. 创建API密钥
3. 设置环境变量:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

### GPT-4 (OpenAI)

1. 访问 https://platform.openai.com/api-keys
2. 创建API密钥
3. 设置环境变量:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

**提示**: 如果没有设置环境变量，程序会在运行时提示您输入，或自动切换到扫描模式。

---

## 📄 查看报告

分析完成后，报告保存在项目根目录的 `.ProjectOracle/` 文件夹中：

```bash
# 报告位置
/path/to/your/project/.ProjectOracle/{项目名}_analysis.md

# 示例：对于项目 yuu
cat /path/to/yuu/.ProjectOracle/yuu_analysis.md

# 示例：对于项目 ProjectOracle
cat /path/to/ProjectOracle/.ProjectOracle/ProjectOracle_analysis.md
```

报告包含：
- 📊 项目统计（文件数、类、函数）
- 🏗️ 架构模式识别
- 🗺️ 核心模块分析
- 📈 数据流描述
- ⚠️ 潜在问题点

---

## 🎯 作为MCP服务器使用

在Claude Desktop配置文件中添加:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "project-oracle": {
      "command": "python3",
      "args": ["-m", "project_oracle"],
      "env": {
        "GEMINI_API_KEY": "your-key-here"
      }
    }
  }
}
```

重启Claude Desktop后，可以在对话中使用 `analyze_project` 工具。

---

## 💰 成本估算

| 模式 | 成本 | 说明 |
|------|------|------|
| **Scan Only** | 免费 | 基础扫描和统计 |
| **Gemini** | 免费或 $0.001-0.01 | 有慷慨的免费层级 |
| **Claude** | $0.01-0.50 | 最佳质量 |
| **GPT-4** | $0.03-1.00 | 高质量 |

*成本取决于项目大小和复杂度*

---

## 🛠️ 高级选项

```bash
# 强制重新生成报告
project-oracle /path/to/project --force

# 限制扫描文件数
project-oracle /path/to/project --max-files 1000

# 详细日志输出
project-oracle /path/to/project --verbose
```

---

## ❓ 常见问题

### Q: 命令找不到 `project-oracle: command not found`

**解决方法**:

1. 确保激活了虚拟环境:
   ```bash
   source venv/bin/activate
   ```

2. 或使用Python模块方式:
   ```bash
   python3 -m project_oracle.cli /path/to/project
   ```

### Q: 如何退出虚拟环境？

```bash
deactivate
```

### Q: 可以全局安装吗？

可以，但不推荐。建议使用虚拟环境以避免依赖冲突。

---

## 📚 更多信息

- [安装指南](INSTALL.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)
- [GitHub仓库](https://github.com/zaihuishou/ProjectOracle)

---

## 📝 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**快速开始**: 
```bash
source venv/bin/activate && project-oracle .
```
