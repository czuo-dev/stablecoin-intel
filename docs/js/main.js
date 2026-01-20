// 稳定币情报系统 - 前端脚本
// 注意：reports 数据从 reports.js 加载

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 确保 reports 已加载
    if (typeof reports === 'undefined') {
        console.error('reports.js 未加载');
        document.getElementById('reports-container').innerHTML = 
            '<div style="text-align: center; padding: 3rem; color: #e74c3c;">❌ 数据加载失败</div>';
        return;
    }
    
    loadReports();
    setupLanguageFilter();
    updateStats();
});

// 加载周报列表
function loadReports() {
    const container = document.getElementById('reports-container');
    
    if (reports.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: #7f8c8d;">
                <p style="font-size: 1.2rem; margin-bottom: 0.5rem;">📭</p>
                <p>暂无周报</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">请先运行周报生成器</p>
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
    const totalReports = reports.length;
    const totalNews = reports.reduce((sum, r) => sum + r.stats.total_news, 0);
    
    document.getElementById('total-reports').textContent = totalReports;
    document.getElementById('total-news').textContent = totalNews;
    
    // 更新时间
    const now = new Date();
    document.getElementById('last-update').textContent = 
        now.toLocaleDateString('zh-CN', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
}
