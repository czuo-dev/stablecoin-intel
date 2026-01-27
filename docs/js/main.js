// 稳定币情报系统 - 前端脚本
// 注意：reports 数据从 reports.js 加载，dailyReports 从 daily-reports.js 加载

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 确保数据已加载
    if (typeof reports === 'undefined') {
        console.error('reports.js 未加载');
    }
    if (typeof dailyReports === 'undefined') {
        console.error('daily-reports.js 未加载');
    }

    loadDailyReports();
    loadWeeklyReports();
    setupTypeSwitcher();
    setupLanguageFilter();
    updateStats();
});

// 设置报告类型切换
function setupTypeSwitcher() {
    const buttons = document.querySelectorAll('.type-btn');
    const dailyContainer = document.getElementById('daily-container');
    const weeklyContainer = document.getElementById('weekly-container');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            // 更新按钮状态
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const type = btn.dataset.type;

            if (type === 'daily') {
                dailyContainer.style.display = 'block';
                dailyContainer.classList.add('active');
                weeklyContainer.style.display = 'none';
                weeklyContainer.classList.remove('active');
            } else {
                dailyContainer.style.display = 'none';
                dailyContainer.classList.remove('active');
                weeklyContainer.style.display = 'block';
                weeklyContainer.classList.add('active');
            }
        });
    });
}

// 加载日报列表
function loadDailyReports() {
    const container = document.getElementById('daily-container');

    if (typeof dailyReports === 'undefined' || dailyReports.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>暂无日报</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem; color: #95a5a6;">
                    运行 daily_job_v2.py 生成日报
                </p>
            </div>
        `;
        return;
    }

    // 按日期倒序
    const sortedReports = [...dailyReports].sort((a, b) =>
        new Date(b.date) - new Date(a.date)
    );

    let html = '';

    sortedReports.forEach(report => {
        html += createDailyCard(report);
    });

    container.innerHTML = html;
}

// 渲染日报条目（支持字符串或对象格式）
function renderDailyItem(item, showThreat = false) {
    // 兼容旧格式（纯字符串）
    if (typeof item === 'string') {
        return `<div class="daily-item">${item}</div>`;
    }

    // 新格式（对象，包含 title, url, source）
    const title = item.title || '';
    const url = item.url || '';
    const source = item.source || '';

    // 威胁分析（仅竞争对手）
    const threatLevel = item.threat_level || '';
    const impactAreas = item.impact_areas || [];
    const suggestedAction = item.suggested_action || '';

    let threatHtml = '';
    if (showThreat && threatLevel) {
        const threatIcon = {high: '🔴', medium: '🟡', low: '🟢'}[threatLevel] || '';
        const threatText = {high: '高威胁', medium: '中威胁', low: '低威胁'}[threatLevel] || '';
        threatHtml = `
            <div class="daily-item-threat">
                <span class="threat-badge threat-${threatLevel}">${threatIcon} ${threatText}</span>
                ${impactAreas.length > 0 ? `<span class="impact-areas">${impactAreas.join('、')}</span>` : ''}
            </div>
            ${suggestedAction ? `<div class="daily-item-action">💡 ${suggestedAction}</div>` : ''}
        `;
    }

    if (url) {
        return `
            <div class="daily-item ${threatLevel ? 'has-threat' : ''}">
                <a href="${url}" target="_blank" class="daily-item-link">${title}</a>
                ${threatHtml}
                ${source ? `<div class="daily-item-source">${source}</div>` : ''}
            </div>
        `;
    }

    return `
        <div class="daily-item ${threatLevel ? 'has-threat' : ''}">
            ${title}
            ${threatHtml}
            ${source ? `<div class="daily-item-source">${source}</div>` : ''}
        </div>
    `;
}

// 创建日报卡片
function createDailyCard(report) {
    const stats = report.stats || {};
    const highlights = report.highlights || {};

    // 格式化日期
    const dateObj = new Date(report.date);
    const formattedDate = dateObj.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    });

    // 构建分类内容
    let sectionsHtml = '';

    // 竞争对手动态（显示威胁分析）
    if (stats.competitors > 0) {
        const items = highlights.competitors || [];
        sectionsHtml += `
            <div class="daily-section section-competitors">
                <div class="daily-section-title">🏢 竞争对手动态 (${stats.competitors})</div>
                ${items.length > 0 ? items.slice(0, 3).map(item =>
                    renderDailyItem(item, true)
                ).join('') : '<div class="daily-item" style="color: #95a5a6;">查看完整报告了解详情</div>'}
            </div>
        `;
    }

    // 客户进展
    if (stats.clients > 0) {
        const items = highlights.clients || [];
        sectionsHtml += `
            <div class="daily-section section-clients">
                <div class="daily-section-title">🤝 客户进展 (${stats.clients})</div>
                ${items.length > 0 ? items.slice(0, 3).map(item =>
                    renderDailyItem(item)
                ).join('') : '<div class="daily-item" style="color: #95a5a6;">查看完整报告了解详情</div>'}
            </div>
        `;
    }

    // 行业进展
    if (stats.industry > 0) {
        const items = highlights.industry || [];
        sectionsHtml += `
            <div class="daily-section section-industry">
                <div class="daily-section-title">📈 行业进展 (${stats.industry})</div>
                ${items.length > 0 ? items.slice(0, 3).map(item =>
                    renderDailyItem(item)
                ).join('') : '<div class="daily-item" style="color: #95a5a6;">查看完整报告了解详情</div>'}
            </div>
        `;
    }

    const totalItems = (stats.competitors || 0) + (stats.clients || 0) + (stats.industry || 0);

    return `
        <div class="daily-card">
            <div class="daily-header">
                <div class="daily-date">📅 ${formattedDate}</div>
                <div class="daily-stats">
                    <span class="daily-stat">共 ${totalItems} 条</span>
                </div>
            </div>
            <div class="daily-sections">
                ${sectionsHtml || '<div style="color: #95a5a6; text-align: center; padding: 1rem;">暂无数据</div>'}
            </div>
            <a href="${report.file}" target="_blank" class="daily-view-full">
                查看完整日报 →
            </a>
        </div>
    `;
}

// 加载周报列表
function loadWeeklyReports() {
    const container = document.getElementById('reports-container');

    if (typeof reports === 'undefined' || reports.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>暂无周报</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem; color: #95a5a6;">
                    请先运行周报生成器
                </p>
            </div>
        `;
        return;
    }

    const grid = document.createElement('div');
    grid.className = 'reports-grid';

    // 按日期倒序
    const sortedReports = [...reports].sort((a, b) =>
        new Date(b.date) - new Date(a.date)
    );

    sortedReports.forEach(report => {
        const card = createReportCard(report);
        grid.appendChild(card);
    });

    container.innerHTML = '';
    container.appendChild(grid);
}

// 创建周报卡片
function createReportCard(report) {
    const card = document.createElement('div');
    card.className = 'report-card';

    card.innerHTML = `
        <div class="report-date">📅 ${report.period}</div>
        <h3 class="report-title">${report.title}</h3>

        <div class="report-meta">
            <span class="meta-badge">📰 ${report.stats.total_news || 0} 条新闻</span>
            <span class="meta-badge">📋 ${report.stats.by_category?.policy || 0} 条政策</span>
            <span class="meta-badge">🏢 ${report.stats.by_category?.company || 0} 条公司</span>
        </div>

        <div class="report-links">
            <a href="reports/${report.date}/zh.html"
               class="report-link link-zh"
               target="_blank">
                🇨🇳 中文版
            </a>
            <a href="reports/${report.date}/en.html"
               class="report-link link-en"
               target="_blank">
                🇺🇸 English
            </a>
            <a href="reports/${report.date}/es.html"
               class="report-link link-es"
               target="_blank">
                🇪🇸 Español
            </a>
        </div>
    `;

    return card;
}

// 语言过滤
function setupLanguageFilter() {
    const buttons = document.querySelectorAll('.lang-btn');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            // 更新按钮状态
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const lang = btn.dataset.lang;
            filterReports(lang);
        });
    });
}

function filterReports(lang) {
    // 过滤显示的链接
    const links = document.querySelectorAll('.report-link');

    links.forEach(link => {
        if (lang === 'all') {
            link.style.display = 'block';
        } else {
            const isMatch = link.classList.contains(`link-${lang}`);
            link.style.display = isMatch ? 'block' : 'none';
        }
    });
}

// 更新统计数据
function updateStats() {
    // 日报统计
    const totalDaily = typeof dailyReports !== 'undefined' ? dailyReports.length : 0;
    const dailyEl = document.getElementById('total-daily');
    if (dailyEl) {
        dailyEl.textContent = totalDaily;
    }

    // 周报统计
    const totalReports = typeof reports !== 'undefined' ? reports.length : 0;
    document.getElementById('total-reports').textContent = totalReports;

    // 新闻总数
    let totalNews = 0;
    if (typeof reports !== 'undefined') {
        totalNews = reports.reduce((sum, r) => sum + (r.stats.total_news || 0), 0);
    }
    if (typeof dailyReports !== 'undefined') {
        totalNews += dailyReports.reduce((sum, r) => {
            const stats = r.stats || {};
            return sum + (stats.competitors || 0) + (stats.clients || 0) + (stats.industry || 0);
        }, 0);
    }
    document.getElementById('total-news').textContent = totalNews;

    // 更新时间
    const now = new Date();
    const lastUpdateEl = document.getElementById('last-update');
    if (lastUpdateEl) {
        lastUpdateEl.textContent = now.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
}
