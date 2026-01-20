# ProjectOracle本地测试指南

## 🚀 快速开始（5分钟）

### 步骤1: 安装项目

```bash
cd /Users/beste/PythonProjects/ProjectOracle

# 开发模式安装（推荐）
pip install -e .

# 或使用 pip3
pip3 install -e .
```

这会安装所有依赖并创建 `project-oracle` 命令。

---

## 🧪 测试方案

### 测试1: 验证安装 ✅

```bash
# 检查命令是否可用
project-oracle --help

# 预期输出: 显示帮助信息和所有选项
```

### 测试2: Scan-Only模式（最简单，无需API密钥）

```bash
# 在ProjectOracle项目自己上测试
cd /Users/beste/PythonProjects/ProjectOracle

# 运行scan-only模式
project-oracle . --scan-only

# 预期结果:
# - 扫描所有Python文件
# - 生成 .ProjectOracle 报告
# - 显示基础统计信息
# - 不调用任何LLM API
```

### 测试3: Dry-Run模式（预览成本）

```bash
# 设置API密钥（如果有）
export ANTHROPIC_API_KEY="sk-ant-..."

# Dry-run测试
project-oracle . --dry-run

# 预期结果:
# - 显示估算的token数量
# - 显示预估成本
# - 不实际调用API
# - 不生成报告
```

### 测试4: 完整分析（需要API密钥）

#### 选项A: 使用Anthropic Claude

```bash
export ANTHROPIC_API_KEY="your-api-key"
project-oracle . --max-cost 0.10

# 预期: 生成完整AI分析报告
```

#### 选项B: 使用Gemini（免费层级）

```bash
# 获取免费API: https://makersuite.google.com/app/apikey
export GEMINI_API_KEY="your-gemini-key"
project-oracle . --llm-provider gemini

# 预期: 使用Gemini生成分析
```

#### 选项C: 使用Ollama（本地，完全免费）

```bash
# 1. 安装Ollama（如果未安装）
# macOS:
brew install ollama

# 2. 启动Ollama服务
ollama serve &

# 3. 下载模型（首次）
ollama pull llama2

# 4. 运行分析
project-oracle . --llm-provider ollama --llm-model llama2

# 预期: 使用本地LLM生成分析
```

---

## 📋 测试检查清单

### 基础功能测试

- [ ] **安装验证**
  ```bash
  project-oracle --help
  which project-oracle
  ```

- [ ] **Scan-only模式**
  ```bash
  project-oracle . --scan-only
  ls -lh .ProjectOracle
  head -20 .ProjectOracle
  ```

- [ ] **文件扫描统计**
  ```bash
  project-oracle . --scan-only --verbose
  # 查看扫描了多少文件
  ```

- [ ] **交互模式**
  ```bash
  project-oracle . --interactive
  # 选择: scan-only或其他provider
  ```

### 高级功能测试

- [ ] **Dry-run模式**
  ```bash
  export ANTHROPIC_API_KEY="sk-ant-..."
  project-oracle . --dry-run
  ```

- [ ] **指定文件数量**
  ```bash
  project-oracle . --scan-only --max-files 100
  ```

- [ ] **强制重新生成**
  ```bash
  project-oracle . --scan-only --force
  ```

- [ ] **详细日志**
  ```bash
  project-oracle . --scan-only --verbose
  ```

### Provider测试（可选）

- [ ] **Gemini Provider**
  ```bash
  export GEMINI_API_KEY="..."
  project-oracle . --llm-provider gemini --dry-run
  ```

- [ ] **Ollama Provider**
  ```bash
  ollama pull llama2
  project-oracle . --llm-provider ollama --dry-run
  ```

---

## 🔍 验证结果

### 成功的标志

1. **命令执行无错误**
   - 没有Python异常
   - 没有import错误

2. **生成报告文件**
   ```bash
   ls -lh .ProjectOracle
   # 应该看到一个markdown文件
   ```

3. **报告内容正确**
   ```bash
   cat .ProjectOracle
   ```
   应包含:
   - 项目名称
   - 文件统计
   - 目录结构
   - 类和函数列表

4. **日志信息清晰**
   - 显示扫描进度
   - 显示处理的文件数
   - 显示生成的统计信息

---

## ❌ 常见问题排查

### 问题1: 命令找不到

```bash
# 症状
-bash: project-oracle: command not found

# 解决
pip install -e .  # 重新安装
# 或者直接运行
python -m project_oracle.cli /path/to/project --scan-only
```

### 问题2: Import错误

```bash
# 症状
ModuleNotFoundError: No module named 'anthropic'

# 解决
pip install anthropic  # 核心依赖
```

### 问题3: API密钥错误

```bash
# 症状
Error: ANTHROPIC_API_KEY environment variable not set

# 解决 - 使用免费模式
project-oracle . --scan-only
# 或
project-oracle . --llm-provider ollama
```

### 问题4: Ollama连接失败

```bash
# 症状
Ollama error: connection refused

# 解决
ollama serve  # 启动Ollama服务
# 在新终端运行分析
```

---

## 📊 预期输出示例

### Scan-Only模式输出

```
🔍 Scanning project...

📊 Scan Results:
  • Total files found: 22
  • Files to analyze: 22
  • Strategy: full
  • Estimated time: ~2s

🚀 Starting analysis...

📝 Extracting symbols from 22 files...
Processing  [####################################]  100%

📋 Generating scan-only report...
📄 Generating report...

✅ Analysis complete!
📄 Report saved to: /Users/beste/PythonProjects/ProjectOracle/.ProjectOracle
📊 Statistics:
  • Files scanned: 22
  • Files analyzed: 22
  • Classes found: 15
  • Functions found: 45

💡 For AI-powered analysis, use:
   --llm-provider anthropic  (paid)
   --llm-provider ollama     (free, local)
```

---

## 🎯 推荐测试顺序

1. **首次测试** (2分钟)
   ```bash
   pip install -e .
   project-oracle . --scan-only
   cat .ProjectOracle
   ```

2. **验证不同模式** (3分钟)
   ```bash
   project-oracle . --scan-only --verbose
   project-oracle . --dry-run  # 如有API key
   ```

3. **测试在其他项目** (5分钟)
   ```bash
   project-oracle /path/to/another/python/project --scan-only
   ```

4. **尝试AI分析** (可选)
   - Gemini (免费): 获取API key然后测试
   - Ollama (本地): 安装并测试

---

## ✅ 完整测试脚本

保存为 `test_local.sh`:

```bash
#!/bin/bash
set -e

echo "=== ProjectOracle本地测试 ==="
echo ""

echo "1. 验证安装..."
project-oracle --help > /dev/null && echo "✅ 命令可用"

echo ""
echo "2. 测试scan-only模式..."
project-oracle . --scan-only --force

echo ""
echo "3. 验证报告生成..."
if [ -f .ProjectOracle ]; then
    echo "✅ 报告已生成"
    wc -l .ProjectOracle
else
    echo "❌ 报告未生成"
    exit 1
fi

echo ""
echo "4. 查看报告内容..."
head -20 .ProjectOracle

echo ""
echo "=== 所有测试通过! ==="
```

运行:
```bash
chmod +x test_local.sh
./test_local.sh
```

---

**立即开始测试**: `pip install -e . && project-oracle . --scan-only`
