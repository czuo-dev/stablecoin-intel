#!/usr/bin/env node
/**
 * 扫描 reports/weekly/*.md，生成 weeklyReports 列表 JSON，供静态部署时前端请求 data/weekly-reports.json。
 * 用法: node scripts/extract_weekly_reports_json.js [reports/weekly 路径] [输出路径]
 */

const fs = require('fs');
const path = require('path');

const repoRoot = path.join(__dirname, '..');
const weeklyDir = process.argv[2] || path.join(repoRoot, 'reports', 'weekly');
const outFile = process.argv[3] || path.join(repoRoot, 'stablecoin-intel-web-source', 'dist', 'public', 'data', 'weekly-reports.json');

if (!fs.existsSync(weeklyDir)) {
  console.warn('extract_weekly_reports_json: reports/weekly not found', weeklyDir);
  const outDir = path.dirname(outFile);
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(outFile, JSON.stringify({ weeklyReports: [] }), 'utf8');
  console.log('extract_weekly_reports_json: wrote empty list to', outFile);
  process.exit(0);
}

const langLabels = { bilingual: '中英双语', zh: '中文', en: 'English', es: 'Español' };
const re = /^weekly_(bilingual|zh|es|en)_(\d{4})_W(\d+)_(\d{4}-\d{2}-\d{2})\.md$/;
const files = fs.readdirSync(weeklyDir).filter((f) => f.endsWith('.md'));

const list = [];
for (const file of files) {
  const m = file.match(re);
  if (!m) continue;
  const [, lang, year, week, date] = m;
  const langLabel = langLabels[lang] || lang;
  list.push({
    id: `weekly-${lang}-${year}-W${week}`,
    date,
    title: `${year} W${week} ${langLabel}`,
    summary: `周报 ${year} 第${week}周 (${langLabel})`,
    type: 'weekly',
    stats: { high: 0, medium: 0, low: 0 },
    file,
    lang,
  });
}
list.sort((a, b) => b.date.localeCompare(a.date));

const outDir = path.dirname(outFile);
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(outFile, JSON.stringify({ weeklyReports: list }, null, 0), 'utf8');
console.log('extract_weekly_reports_json: wrote', list.length, 'weekly reports to', outFile);
