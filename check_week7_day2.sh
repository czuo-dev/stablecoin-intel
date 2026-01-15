#!/bin/bash

echo "🔍 Week 7 Day 2 完成度检查"
echo "============================================================"

# 检查1：文件是否创建
echo "✓ 检查文件创建"
if [ -f "src/processors/batch_summarizer.py" ]; then
    echo "  [✓] batch_summarizer.py 存在"
else
    echo "  [✗] batch_summarizer.py 缺失"
fi

if [ -f "src/processors/prompt_templates.py" ]; then
    echo "  [✓] prompt_templates.py 存在"
else
    echo "  [✗] prompt_templates.py 缺失"
fi

# 检查2：测试文件
echo ""
echo "✓ 检查测试文件"
if [ -f "test_batch_simple.py" ]; then
    echo "  [✓] test_batch_simple.py 存在"
else
    echo "  [✗] test_batch_simple.py 缺失"
fi

if [ -f "test_prompt_compare.py" ]; then
    echo "  [✓] test_prompt_compare.py 存在"
else
    echo "  [✗] test_prompt_compare.py 缺失"
fi

# 检查3：报告生成
echo ""
echo "✓ 检查报告生成"
report_count=$(ls reports/daily_brief_*.md 2>/dev/null | wc -l)
echo "  已生成 $report_count 份报告"

# 检查4：语法检查
echo ""
echo "✓ 检查语法"
python3 -m py_compile src/processors/batch_summarizer.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  [✓] batch_summarizer.py 语法正确"
else
    echo "  [✗] batch_summarizer.py 有语法错误"
fi

python3 -m py_compile src/processors/prompt_templates.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  [✓] prompt_templates.py 语法正确"
else
    echo "  [✗] prompt_templates.py 有语法错误"
fi

echo ""
echo "============================================================"
echo "🎉 检查完成！"
