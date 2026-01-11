# 数据导出模块
# 功能：将新闻数据导出为Excel

import json
import pandas as pd
from datetime import datetime
import os

# =========================
# 导出函数
# =========================

def export_to_excel(json_file, output_file=None):
    """
    将JSON数据导出为Excel
    
    参数:
        json_file: JSON数据文件路径
        output_file: 输出Excel文件路径（可选）
    """
    try:
        # 读取JSON数据
        print(f"读取数据: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 转换为DataFrame
        df = pd.DataFrame(data)
        
        # 选择要导出的列
        columns_to_export = [
            'title', 'source', 'category', 'date', 
            'url', 'summary'
        ]
        
        # 只保留存在的列
        existing_columns = [col for col in columns_to_export if col in df.columns]
        df_export = df[existing_columns]
        
        # 生成输出文件名
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"data/exports/stablecoin_news_{timestamp}.xlsx"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 导出到Excel
        print(f"导出到: {output_file}")
        df_export.to_excel(output_file, index=False, engine='openpyxl')
        
        print(f"✅ 成功导出 {len(df_export)} 条数据")
        print(f"📄 文件位置: {output_file}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return None

def export_summary_stats(json_file, output_file=None):
    """
    导出统计摘要到Excel
    
    参数:
        json_file: JSON数据文件路径
        output_file: 输出Excel文件路径
    """
    try:
        # 读取数据
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        # 生成统计表
        stats = {
            '按分类': df.groupby('category').size().reset_index(name='数量'),
            '按来源': df.groupby('source').size().reset_index(name='数量').head(10),
            '按日期': df.groupby('date').size().reset_index(name='数量')
        }
        
        # 生成输出文件名
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"data/exports/stats_{timestamp}.xlsx"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 导出到Excel（多个sheet）
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for sheet_name, df_sheet in stats.items():
                df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"✅ 统计报告已导出: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ 导出统计失败: {e}")
        return None

# =========================
# 主程序
# =========================

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python data_exporter.py data <json文件>     # 导出原始数据")
        print("  python data_exporter.py stats <json文件>    # 导出统计数据")
        return
    
    command = sys.argv[1]
    
    if len(sys.argv) < 3:
        print("❌ 请指定JSON文件路径")
        return
    
    json_file = sys.argv[2]
    
    if not os.path.exists(json_file):
        print(f"❌ 文件不存在: {json_file}")
        return
    
    if command == "data":
        export_to_excel(json_file)
    
    elif command == "stats":
        export_summary_stats(json_file)
    
    else:
        print("❌ 无效的命令")

if __name__ == "__main__":
    main()