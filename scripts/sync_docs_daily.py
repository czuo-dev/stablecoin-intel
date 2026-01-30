#!/usr/bin/env python3
# scripts/sync_docs_daily.py
"""
同步日报到前端：将 reports/daily/*.md 复制到 docs/reports/daily/，
并根据 data/processed/business_intel_*.json 重新生成 docs/daily-reports.js。
在日报已生成但前端未更新时运行（例如只改了 report 未跑完流水线）。
需在项目根目录执行：python3 scripts/sync_docs_daily.py
"""

import os
import sys
import json
import shutil
import glob
from pathlib import Path

# 确保在项目根目录运行
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))


def copy_reports_to_docs():
    """复制 reports/daily/*.md 到 docs/reports/daily/"""
    src_dir = PROJECT_ROOT / "reports" / "daily"
    dst_dir = PROJECT_ROOT / "docs" / "reports" / "daily"
    if not src_dir.exists():
        print("⚠️  reports/daily/ 不存在，跳过复制")
        return 0
    dst_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in src_dir.glob("daily_brief_*.md"):
        shutil.copy2(f, dst_dir / f.name)
        count += 1
        print(f"   📄 {f.name} -> docs/reports/daily/")
    return count


def regenerate_daily_reports_js():
    """根据所有 business_intel_*.json 重新生成 docs/daily-reports.js（按日期从旧到新合并，避免丢日期）"""
    from scripts.daily_job_v2 import generate_daily_reports_js

    processed_dir = PROJECT_ROOT / "data" / "processed"
    reports_dir = PROJECT_ROOT / "reports" / "daily"

    # 找到既有 report 又有 business_intel 的日期，按日期升序（从旧到新），这样合并后顺序为 [最新, ..., 最旧]
    biz_files = sorted(glob.glob(str(processed_dir / "business_intel_*.json")))
    to_process = []
    for path in biz_files:
        date_str = Path(path).stem.replace("business_intel_", "")
        report_md = reports_dir / f"daily_brief_{date_str}.md"
        if report_md.exists():
            to_process.append((path, date_str))

    if not to_process:
        print("   ⚠️  未找到可用的 business_intel_*.json（需对应日期的 report 存在），跳过 JS 更新")
        return

    for path, date_str in to_process:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        generate_daily_reports_js(data, date_str)
        print(f"   ✅ 已合并 business_intel_{date_str}.json -> docs/daily-reports.js")
    print(f"   共合并 {len(to_process)} 天日报")


def main():
    print("=" * 60)
    print("📂 同步日报到前端 (docs/)")
    print("=" * 60)

    print("\n1️⃣ 复制 reports/daily/*.md -> docs/reports/daily/")
    n = copy_reports_to_docs()
    print(f"   共复制 {n} 个文件\n")

    print("2️⃣ 重新生成 docs/daily-reports.js")
    regenerate_daily_reports_js()

    print("\n" + "=" * 60)
    print("✅ 同步完成。若前端仍显示旧内容：")
    print("   - 本地：强制刷新浏览器 (Cmd+Shift+R / Ctrl+Shift+R)")
    print("   - GitHub Pages：提交并推送 docs/ 后等待部署")
    print("=" * 60)


if __name__ == "__main__":
    main()
