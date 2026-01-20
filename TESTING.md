# 完整测试流程：从GitHub到本地Ollama

## 🎯 目标
从零开始，完成：下载 → 安装 → 使用本地Ollama模型测试

---

## � 方式1: 自动化脚本（推荐）

### 一键运行
```bash
cd /Users/beste/PythonProjects/ProjectOracle
./complete_test.sh
```

这个脚本会自动完成所有9个步骤！

---

## 📋 方式2: 手动步骤（详细学习）

### 步骤1: 准备新目录
```bash
# 创建测试目录
mkdir -p /tmp/ProjectOracle_test
cd /tmp/ProjectOracle_test
```

### 步骤2: 从GitHub克隆
```bash
git clone https://github.com/zaihuishou/ProjectOracle.git
cd ProjectOracle
```

### 步骤3: 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

### 步骤4: 安装ProjectOracle
```bash
pip install -e .
```

### 步骤5: 验证安装
```bash
project-oracle --help
```

### 步骤6: 测试Scan-Only（无需API）
```bash
project-oracle . --scan-only
cat .ProjectOracle
```

### 步骤7: 安装Ollama（如果未安装）
```bash
# macOS
brew install ollama

# 启动Ollama服务
ollama serve &

# 下载模型（约4GB）
ollama pull llama2
```

### 步骤8: 安装ollama Python包
```bash
pip install ollama
```

### 步骤9: 使用Ollama进行AI分析
```bash
project-oracle . --llm-provider ollama --llm-model llama2 --force
```

### 步骤10: 查看AI生成的报告
```bash
cat .ProjectOracle
```

---

## 🚀 快速测试（最小步骤）

如果Ollama已安装：

```bash
# 1. 克隆并进入
git clone https://github.com/zaihuishou/ProjectOracle.git
cd ProjectOracle

# 2. 安装
python3 -m venv venv && source venv/bin/activate
pip install -e . && pip install ollama

# 3. 测试
ollama pull llama2  # 首次需要
project-oracle . --llm-provider ollama
```

---

## 📊 预期结果

### Scan-Only模式输出
```
🔍 Scanning project...
📊 Scan Results:
  • Total files found: 13
  • Files to analyze: 13
✅ Analysis complete!
```

### Ollama模式输出
```
💡 Using Ollama (local LLM) - FREE!
🔍 Scanning project...
📝 Extracting symbols...
🤖 Analyzing with Ollama (llama2)...
✅ Analysis complete!
```

---

## ❓ 常见问题

### Q1: Ollama下载很慢？
```bash
# 使用更小的模型
ollama pull llama2:7b  # 约4GB
# 或
ollama pull phi  # 约1.6GB
```

### Q2: Ollama连接失败？
```bash
# 确保服务运行
ollama serve

# 在新终端运行分析
project-oracle . --llm-provider ollama
```

### Q3: 想用其他模型？
```bash
# 列出可用模型
ollama list

# 使用其他模型
project-oracle . --llm-provider ollama --llm-model codellama
```

### Q4: 不想用Ollama？
```bash
# 使用免费的Gemini
export GEMINI_API_KEY="your-key"
project-oracle . --llm-provider gemini

# 或仅扫描
project-oracle . --scan-only
```

---

## 🧹 清理

测试完成后清理：

```bash
# 退出虚拟环境
deactivate

# 删除测试目录
rm -rf /tmp/ProjectOracle_test

# 停止Ollama（可选）
pkill ollama
```

---

## 📸 测试截图检查点

1. ✅ `git clone` 成功
2. ✅ `pip install -e .` 无错误
3. ✅ `project-oracle --help` 显示帮助
4. ✅ `.ProjectOracle` 文件生成
5. ✅ `ollama list` 显示llama2
6. ✅ Ollama分析完成

---

## 💡 下一步

测试成功后，可以：

1. **在自己项目上测试**
   ```bash
   project-oracle /path/to/your/project --llm-provider ollama
   ```

2. **尝试不同provider**
   ```bash
   project-oracle . --llm-provider gemini  # 需要API key
   ```

3. **调整参数**
   ```bash
   project-oracle . --llm-provider ollama --max-files 1000
   ```

---

**立即开始**: `./complete_test.sh` 或按照手动步骤操作
