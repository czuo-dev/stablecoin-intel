#!/bin/bash
# 完整的新闻处理流水线
# 功能：抓取 → 过滤 → 入库 → 去重 → 生成报告

# =========================
# 配置部分
# =========================

# 项目路径（改成你的实际路径）
PROJECT_DIR="/Users/changbaizuo_1/projects/stablecoin-intel"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/pipeline_$(date +%Y%m%d).log"

# 创建日志目录（如果不存在）
mkdir -p "$LOG_DIR"

# =========================
# 日志函数
# =========================

log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# =========================
# 错误处理
# =========================

# 如果任何命令失败，立即退出
set -e

# 捕获错误并记录
trap 'log_error "脚本在第 $LINENO 行失败"' ERR

# =========================
# 主流程
# =========================

log_info "=========================================="
log_info "开始每日新闻处理流程"
log_info "=========================================="

# 步骤1：切换到项目目录
log_info "步骤1: 切换到项目目录"
cd "$PROJECT_DIR" || {
    log_error "无法切换到项目目录"
    exit 1
}
log_success "项目目录: $PROJECT_DIR"

# 步骤2：激活虚拟环境
log_info "步骤2: 激活虚拟环境"
source venv/bin/activate || {
    log_error "无法激活虚拟环境"
    exit 1
}
log_success "虚拟环境已激活"

# 步骤3：运行 RSS 抓取器
log_info "步骤3: 运行 RSS 抓取器"
python scripts/rss_fetcher.py >> "$LOG_FILE" 2>&1
if [ $? -eq 0 ]; then
    log_success "RSS 抓取完成"
else
    log_error "RSS 抓取失败"
    # 不退出，继续下一步
fi

# 步骤4：运行 NewsAPI 抓取器（如果配置了）
if [ -f "config/api_keys.txt" ]; then
    log_info "步骤4: 运行 NewsAPI 抓取器"
    python scripts/news_fetcher.py >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        log_success "NewsAPI 抓取完成"
    else
        log_error "NewsAPI 抓取失败"
    fi
else
    log_info "步骤4: 跳过 NewsAPI（未配置）"
fi

# 步骤5：运行数据去重
log_info "步骤5: 运行数据去重"
python scripts/data_dedup.py >> "$LOG_FILE" 2>&1
if [ $? -eq 0 ]; then
    log_success "数据去重完成"
else
    log_error "数据去重失败"
fi

# 步骤6：统计信息
log_info "步骤6: 生成统计信息"
NEWS_COUNT=$(find data -name "*.json" -type f | wc -l)
log_info "数据文件总数: $NEWS_COUNT"

# 计算数据库大小
if [ -f "data/news_system_db.json" ]; then
    DB_SIZE=$(wc -l < data/news_system_db.json)
    log_info "数据库行数: $DB_SIZE"
fi

# =========================
# 完成
# =========================

log_success "=========================================="
log_success "流程完成！"
log_success "=========================================="
log_info "日志文件: $LOG_FILE"

# 可选：发送通知（Mac 系统通知）
osascript -e 'display notification "新闻抓取完成" with title "稳定币情报"'