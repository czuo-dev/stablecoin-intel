/**
 * 数据服务层
 * 负责加载真实数据或降级使用 mock 数据
 */

/* build-time define from vite.config.ts */
declare const __BUILD_TS__: string | undefined;

import { NewsItem, ReportSummary, mockNews, stats as mockStats, dailySummary as mockDailySummary, reportList as mockReportList } from './mock-data';

// 日报数据接口（与后端 daily-reports.js 格式对齐）
export interface DailyReport {
  date: string;
  title: string;
  file: string;
  newsItems: NewsItem[];
  stats: {
    totalThreats: number;
    highThreats: number;
    mediumThreats: number;
    lowThreats: number;
    competitorUpdates: number;
    customerUpdates: number;
    industryUpdates: number;
  };
  dailySummary: {
    competitorThreat: string;
    industryTrend: string;
  };
  highlights?: {
    competitors: NewsItem[];
    clients: NewsItem[];
    industry: NewsItem[];
  };
}

// 全局数据缓存
let cachedReports: DailyReport[] | null = null;
let dataLoaded = false;

/**
 * 从后端加载日报数据
 * 优先级：/api/reports（本地有后端）→ 静态 data/daily-reports.json（GitHub Pages）→ mock
 */
export async function loadDailyReports(): Promise<DailyReport[]> {
  if (cachedReports !== null) {
    return cachedReports;
  }

  const base = (typeof import.meta !== "undefined" && import.meta.env?.BASE_URL) || "";

  try {
    const apiRes = await fetch("/api/reports");
    if (apiRes.ok) {
      const data = await apiRes.json();
      cachedReports = data.dailyReports || data;
      dataLoaded = true;
      return cachedReports;
    }
  } catch {
    /* API not available */
  }

  try {
    // 线上 base 为 /stablecoin-intel/，静态文件需在 base 下；本地 base 为 / 时用 /data/...
    const dataPath = base && base !== "/" ? `${base.replace(/\/$/, "")}/data/daily-reports.json` : "/data/daily-reports.json";
    const staticUrl = typeof __BUILD_TS__ !== "undefined" ? `${dataPath}?v=${__BUILD_TS__}` : dataPath;
    const staticRes = await fetch(staticUrl);
    if (staticRes.ok) {
      const data = await staticRes.json();
      cachedReports = data.dailyReports || data;
      dataLoaded = true;
      return cachedReports;
    }
  } catch {
    /* static JSON not available */
  }

  cachedReports = convertMockToReports();
  dataLoaded = true;
  return cachedReports;
}

/**
 * 获取指定日期的报告
 */
export async function getReportByDate(date: string): Promise<DailyReport | null> {
  const reports = await loadDailyReports();
  return reports.find(r => r.date === date) || null;
}

/**
 * 获取最新报告
 */
export async function getLatestReport(): Promise<DailyReport | null> {
  const reports = await loadDailyReports();
  return reports[0] || null;
}

/**
 * 获取所有新闻项（可按日期筛选）
 */
export async function getNewsItems(date?: string): Promise<NewsItem[]> {
  if (date) {
    const report = await getReportByDate(date);
    return report?.newsItems || [];
  }

  // 默认返回最新报告的新闻
  const latest = await getLatestReport();
  return latest?.newsItems || mockNews;
}

/**
 * 获取统计数据
 */
export async function getStats(date?: string): Promise<DailyReport['stats']> {
  if (date) {
    const report = await getReportByDate(date);
    if (report) return report.stats;
  }

  const latest = await getLatestReport();
  return latest?.stats || mockStats;
}

/**
 * 获取每日总结
 */
export async function getDailySummary(date?: string): Promise<DailyReport['dailySummary']> {
  if (date) {
    const report = await getReportByDate(date);
    if (report) return report.dailySummary;
  }

  const latest = await getLatestReport();
  return latest?.dailySummary || mockDailySummary;
}

/**
 * 获取报告列表（用于 ReportList 页面）
 * Daily 来自 /api/reports，Weekly 来自 /api/weekly-reports（reports/weekly 中英西班牙语周报）
 */
export async function getReportList(): Promise<ReportSummary[]> {
  const reports = await loadDailyReports();

  const dailySummaries: ReportSummary[] = reports.map(report => {
    const competitors = report.newsItems?.filter(n => n.category === 'competitor') || [];
    const high = (report.newsItems?.filter(n => n.threatLevel === 'high') ?? []).length;
    const medium = competitors.filter(n => n.threatLevel === 'medium').length;
    const low = competitors.filter(n => n.threatLevel === 'low').length;
    const competitorUpdates = competitors.length;
    const topItems = report.highlights?.competitors?.slice(0, 2) || [];
    const summaryText = topItems.map(item => item.title?.slice(0, 30)).join('; ') || report.title;

    return {
      id: report.date,
      date: report.date,
      title: report.title || 'Daily Intelligence Brief',
      summary: summaryText,
      stats: { high, medium, low, competitorUpdates },
      type: 'daily' as const
    };
  });
  dailySummaries.sort((a, b) => b.date.localeCompare(a.date));

  let weeklySummaries: ReportSummary[] = [];
  const base = (typeof import.meta !== 'undefined' && import.meta.env?.BASE_URL) || '';
  try {
    const res = await fetch('/api/weekly-reports');
    if (res.ok) {
      const data = await res.json();
      const list = data.weeklyReports || [];
      weeklySummaries = list.map((w: { id: string; date: string; title: string; summary: string; stats: { high: number; medium: number; low: number } }) => ({
        id: w.id,
        date: w.date,
        title: w.title,
        summary: w.summary,
        stats: w.stats || { high: 0, medium: 0, low: 0 },
        type: 'weekly' as const
      }));
    } else {
      const staticUrl = `${base}data/weekly-reports.json`.replace(/([^:]\/)\/+/g, '$1');
      const fallback = await fetch(staticUrl);
      if (fallback.ok) {
        const data = await fallback.json();
        const list = data.weeklyReports || [];
        weeklySummaries = list.map((w: { id: string; date: string; title: string; summary: string; stats?: { high: number; medium: number; low: number } }) => ({
          id: w.id,
          date: w.date,
          title: w.title,
          summary: w.summary,
          stats: w.stats || { high: 0, medium: 0, low: 0 },
          type: 'weekly' as const
        }));
      }
    }
  } catch {
    try {
      const staticUrl = `${base}data/weekly-reports.json`.replace(/([^:]\/)\/+/g, '$1');
      const fallback = await fetch(staticUrl);
      if (fallback.ok) {
        const data = await fallback.json();
        const list = data.weeklyReports || [];
        weeklySummaries = list.map((w: { id: string; date: string; title: string; summary: string; stats?: { high: number; medium: number; low: number } }) => ({
          id: w.id,
          date: w.date,
          title: w.title,
          summary: w.summary,
          stats: w.stats || { high: 0, medium: 0, low: 0 },
          type: 'weekly' as const
        }));
      }
    } catch {
      weeklySummaries = mockReportList.filter(r => r.type === 'weekly');
    }
  }
  return [...dailySummaries, ...weeklySummaries];
}

/**
 * 将 mock 数据转换为 DailyReport 格式
 */
function convertMockToReports(): DailyReport[] {
  // 按日期分组 mock 数据
  const byDate = new Map<string, NewsItem[]>();

  for (const item of mockNews) {
    const date = item.date;
    if (!byDate.has(date)) {
      byDate.set(date, []);
    }
    byDate.get(date)!.push(item);
  }

  // 转换为 DailyReport 格式
  const reports: DailyReport[] = [];

  for (const [date, items] of byDate) {
    const competitors = items.filter(n => n.category === 'competitor');
    const customers = items.filter(n => n.category === 'customer');
    const industry = items.filter(n => n.category === 'industry');

    const high = competitors.filter(n => n.threatLevel === 'high').length;
    const medium = competitors.filter(n => n.threatLevel === 'medium').length;
    const low = competitors.filter(n => n.threatLevel === 'low').length;

    reports.push({
      date,
      title: '稳定币行业日报',
      file: `reports/daily/daily_brief_${date}.md`,
      newsItems: items,
      stats: {
        totalThreats: competitors.length,
        highThreats: high,
        mediumThreats: medium,
        lowThreats: low,
        competitorUpdates: competitors.length,
        customerUpdates: customers.length,
        industryUpdates: industry.length
      },
      dailySummary: mockDailySummary,
      highlights: {
        competitors: competitors.slice(0, 3),
        clients: customers.slice(0, 3),
        industry: industry.slice(0, 3)
      }
    });
  }

  // 按日期降序排列
  reports.sort((a, b) => b.date.localeCompare(a.date));

  return reports;
}

// 同步导出（用于不支持 async 的场景，返回 mock 数据）
export { mockNews, mockStats as stats, mockDailySummary as dailySummary, mockReportList as reportList };
export type { NewsItem, ReportSummary };
