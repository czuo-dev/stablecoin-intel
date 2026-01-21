#!/usr/bin/env python3
"""
周报生成脚本 - 快捷入口
实际脚本位于 scripts/weekly_report.py
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入并运行主脚本
if __name__ == "__main__":
    # 直接执行 scripts/weekly_report.py
    script_path = os.path.join(project_root, "scripts", "weekly_report.py")
    
    if not os.path.exists(script_path):
        print(f"❌ 错误: 找不到脚本文件 {script_path}")
        sys.exit(1)
    
    # 读取并执行脚本
    with open(script_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 在全局命名空间中执行
    exec(compile(code, script_path, 'exec'), {'__name__': '__main__', '__file__': script_path})
