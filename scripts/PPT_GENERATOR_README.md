# PPT生成器使用说明

## 功能说明

这个脚本可以将Markdown格式的稳定币日报自动转换为PowerPoint演示文稿。

## 安装依赖

首先需要安装 `python-pptx` 库：

```bash
pip install python-pptx
# 或
pip3 install python-pptx
```

## 使用方法

### 基本用法

```bash
python3 scripts/generate_ppt.py reports/daily/daily_brief_2026-01-27.md
```

### 指定输出文件

```bash
python3 scripts/generate_ppt.py reports/daily/daily_brief_2026-01-27.md -o output.pptx
```

## 生成的PPT结构

1. **标题页** - 显示报告标题和日期
2. **每日洞察页** - 竞争对手威胁总结和行业趋势总结
3. **竞争对手动态页** - 每个竞争对手一条幻灯片
4. **行业进展页** - 每个行业进展一条幻灯片
5. **总结页** - 报告统计信息

## 示例

```bash
# 生成今日日报的PPT
python3 scripts/generate_ppt.py reports/daily/daily_brief_2026-01-27.md

# 输出文件将保存在: reports/daily/daily_brief_2026-01-27.pptx
```

## 注意事项

- 脚本会自动解析Markdown文件中的标题、日期、竞争对手动态和行业进展
- 如果某些字段缺失，会跳过相应的内容
- PPT使用16:9比例，适合现代演示设备
