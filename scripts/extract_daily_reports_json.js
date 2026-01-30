#!/usr/bin/env node
/**
 * 从 docs/daily-reports.js 提取 dailyReports 数组，写入 JSON 文件。
 * 用于 GitHub Pages 静态部署时前端无 /api 可请求，改为请求此 JSON。
 * 用法: node scripts/extract_daily_reports_json.js [docs/daily-reports.js] [输出路径]
 */

const fs = require('fs');
const path = require('path');

const src = process.argv[2] || path.join(__dirname, '..', 'docs', 'daily-reports.js');
const out = process.argv[3] || path.join(__dirname, '..', 'stablecoin-intel-web-source', 'dist', 'public', 'data', 'daily-reports.json');

if (!fs.existsSync(src)) {
  console.warn('extract_daily_reports_json: source not found', src);
  process.exit(0);
}

const content = fs.readFileSync(src, 'utf8');
const start = content.indexOf('[');
if (start < 0) {
  console.warn('extract_daily_reports_json: no array in source');
  process.exit(0);
}

let depth = 0, inString = null, escape = false, i = start;
while (i < content.length) {
  const c = content[i];
  if (escape) { escape = false; i++; continue; }
  if (c === '\\' && inString) { escape = true; i++; continue; }
  if (inString) { if (c === inString) inString = null; i++; continue; }
  if (c === '"') { inString = '"'; i++; continue; }
  if (c === '[') depth++;
  else if (c === ']') { depth--; if (depth === 0) break; }
  i++;
}
const end = i + 1;
const arr = JSON.parse(content.slice(start, end));

const outDir = path.dirname(out);
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(out, JSON.stringify({ dailyReports: arr }), 'utf8');
console.log('extract_daily_reports_json: wrote', arr.length, 'reports to', out);
