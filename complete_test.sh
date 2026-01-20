#!/bin/bash
# ProjectOracle完整测试流程 - 从GitHub到本地Ollama
# 使用方法: chmod +x complete_test.sh && ./complete_test.sh

set -e  # 遇到错误立即退出

echo "🚀 ProjectOracle完整测试流程"
echo "================================"
echo ""

# 步骤1: 清理旧环境（可选）
echo "📦 步骤1: 准备测试目录..."
TEST_DIR="/tmp/ProjectOracle_test"
if [ -d "$TEST_DIR" ]; then
    echo "   清理旧测试目录..."
    rm -rf "$TEST_DIR"
fi
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"
echo "   ✅ 测试目录: $TEST_DIR"
echo ""

# 步骤2: 从GitHub克隆
echo "📥 步骤2: 从GitHub克隆项目..."
git clone https://github.com/zaihuishou/ProjectOracle.git
cd ProjectOracle
echo "   ✅ 克隆完成"
echo ""

# 步骤3: 创建虚拟环境
echo "🐍 步骤3: 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate
echo "   ✅ 虚拟环境已激活"
echo ""

# 步骤4: 安装ProjectOracle
echo "📦 步骤4: 安装ProjectOracle..."
pip install -e . > /dev/null 2>&1
echo "   ✅ 安装完成"
echo ""

# 步骤5: 验证安装
echo "✓ 步骤5: 验证安装..."
project-oracle --help > /dev/null
echo "   ✅ 命令可用"
echo ""

# 步骤6: 测试Scan-Only模式
echo "🔍 步骤6: 测试Scan-Only模式（无需API）..."
project-oracle . --scan-only --force
if [ -f .ProjectOracle ]; then
    echo "   ✅ Scan-only报告已生成"
    echo "   📄 报告位置: $(pwd)/.ProjectOracle"
    echo "   📊 报告大小: $(wc -l < .ProjectOracle) 行"
else
    echo "   ❌ 报告生成失败"
    exit 1
fi
echo ""

# 步骤7: 检查Ollama
echo "🤖 步骤7: 检查Ollama状态..."
if command -v ollama &> /dev/null; then
    echo "   ✅ Ollama已安装"
    
    # 检查Ollama服务是否运行
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "   ✅ Ollama服务正在运行"
    else
        echo "   ⚠️  Ollama未运行，正在启动..."
        ollama serve > /tmp/ollama.log 2>&1 &
        sleep 3
        echo "   ✅ Ollama服务已启动"
    fi
    
    # 检查llama2模型
    if ollama list | grep -q llama2; then
        echo "   ✅ llama2模型已安装"
    else
        echo "   📥 正在下载llama2模型（约4GB，需要几分钟）..."
        ollama pull llama2
        echo "   ✅ llama2模型下载完成"
    fi
else
    echo "   ❌ Ollama未安装"
    echo "   💡 安装方法: brew install ollama"
    echo "   ⏭️  跳过Ollama测试"
    SKIP_OLLAMA=1
fi
echo ""

# 步骤8: 使用Ollama测试（如果可用）
if [ -z "$SKIP_OLLAMA" ]; then
    echo "🧠 步骤8: 使用Ollama进行AI分析..."
    echo "   ⚠️  注意: 本地LLM分析可能需要1-2分钟"
    
    # 安装ollama Python包
    pip install ollama > /dev/null 2>&1
    
    # 运行分析
    project-oracle . --llm-provider ollama --llm-model llama2 --force
    
    if [ -f .ProjectOracle ]; then
        echo "   ✅ Ollama分析报告已生成"
        echo "   📊 查看AI生成的架构分析:"
        echo ""
        grep -A 5 "## 2. 🏛️ Architecture" .ProjectOracle || echo "   (报告格式可能不同)"
    else
        echo "   ❌ Ollama分析失败"
    fi
else
    echo "⏭️  步骤8: 跳过Ollama测试（未安装）"
fi
echo ""

# 步骤9: 总结
echo "✅ 测试完成！"
echo "================================"
echo ""
echo "📋 测试总结:"
echo "   • 项目位置: $TEST_DIR/ProjectOracle"
echo "   • 虚拟环境: $TEST_DIR/ProjectOracle/venv"
echo "   • 生成报告: $TEST_DIR/ProjectOracle/.ProjectOracle"
echo ""
echo "🔍 查看报告:"
echo "   cat $TEST_DIR/ProjectOracle/.ProjectOracle"
echo ""
echo "🧹 清理测试环境:"
echo "   rm -rf $TEST_DIR"
echo ""
echo "💡 在您自己的项目上测试:"
echo "   cd $TEST_DIR/ProjectOracle"
echo "   source venv/bin/activate"
echo "   project-oracle /path/to/your/project --scan-only"
echo ""
