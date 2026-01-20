# ProjectOracle - 快速开始

## 🚀 安装

```bash
# 克隆项目
git clone https://github.com/zaihuishou/ProjectOracle.git
cd ProjectOracle

# 创建虚拟环境并安装
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

## 💡 使用

### 简单运行
```bash
project-oracle /path/to/your/project
```

### 交互式选择

运行后会提示您选择：

**步骤1: 选择分析模式**
- `1` - 仅扫描 (免费，无需API密钥)
- `2` - AI分析 (需要API密钥)

**步骤2: 如果选择AI分析，选择provider**
- `1` - Claude (Anthropic) - 最佳质量
- `2` - GPT-4 (OpenAI) - 高质量
- `3` - Gemini (Google) - 有免费层级！

### 示例流程

```
🔮 ProjectOracle - AI-Powered Code Analysis
============================================================

📁 Project: MyProject

📋 Step 1: Choose analysis mode

  1. Scan Only (FREE - No API key needed)
  2. AI Analysis (Requires API key)

Select mode [1]: 2

🤖 Step 2: Choose AI Provider

  1. Claude (Anthropic) - Best quality
  2. GPT-4 (OpenAI) - High quality  
  3. Gemini (Google) - FREE tier available!

Select AI provider [3]: 3

⚙️  Configuration Summary
   Mode: AI Analysis
   AI Provider: Gemini
   Max Files: 5000

▶️  Start analysis? [Y/n]: y
```

## 🔑 获取API密钥

### Gemini (推荐 - 有免费层级)
1. 访问: https://makersuite.google.com/app/apikey
2. 创建API密钥
3. 设置环境变量: `export GEMINI_API_KEY="your-key"`

### Claude (Anthropic)
1. 访问: https://console.anthropic.com/
2. 创建API密钥
3. 设置环境变量: `export ANTHROPIC_API_KEY="your-key"`

### GPT-4 (OpenAI)
1. 访问: https://platform.openai.com/api-keys
2. 创建API密钥
3. 设置环境变量: `export OPENAI_API_KEY="your-key"`

## 📄 查看报告

分析完成后，报告保存在项目根目录的 `.ProjectOracle` 文件中：

```bash
cat /path/to/your/project/.ProjectOracle
```

## 🎯 作为MCP服务器使用

在Claude Desktop配置文件中添加:

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

## 💰 成本估算

- **Scan Only**: 完全免费
- **Gemini**: 免费层级或 ~$0.001-0.01
- **Claude**: ~$0.01-0.50
- **GPT-4**: ~$0.03-1.00

## 📚 更多信息

- [完整文档](INSTALL.md)
- [贡献指南](CONTRIBUTING.md)
- [GitHub仓库](https://github.com/zaihuishou/ProjectOracle)

---

**快速开始**: `project-oracle .`
