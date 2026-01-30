import Layout from "@/components/Layout";
import NewsCard from "@/components/NewsCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertTriangle, TrendingUp, Users, Activity, ArrowUpRight, ArrowLeft, Loader2 } from "lucide-react";
import { Link, useRoute } from "wouter";
import { cn } from "@/lib/utils";
import { useState, useRef, useEffect } from "react";
import { getReportByDate, getLatestReport, type DailyReport, type NewsItem, mockNews, stats as mockStats, dailySummary as mockDailySummary } from "@/lib/data-service";

// StatCard 组件的属性接口
interface StatCardProps {
  title: string;
  value: number;
  subtext: string;
  icon: React.ComponentType<{ className?: string }>;
  colorClass: string;
  bgClass: string;
  borderClass: string;
  targetTab: string;
  onClick: (tab: string) => void;
}

const StatCard = ({ title, value, subtext, icon: Icon, colorClass, bgClass, borderClass, targetTab, onClick }: StatCardProps) => (
  <div
    onClick={() => onClick(targetTab)}
    className={cn(
      "cursor-pointer transition-all duration-300 transform hover:scale-[1.02] hover:shadow-lg",
      "bg-card border-l-4 rounded-r-lg shadow-sm p-4 flex items-center justify-between",
      borderClass
    )}
  >
    <div>
      <p className="text-sm font-medium text-muted-foreground">{title}</p>
      <div className="flex items-baseline gap-2 mt-1">
        <h2 className={cn("text-2xl font-bold", colorClass)}>{value}</h2>
        <span className={cn("text-xs font-medium", colorClass)}>{subtext}</span>
      </div>
    </div>
    <div className={cn("h-10 w-10 rounded-full flex items-center justify-center", bgClass, colorClass)}>
      <Icon className="w-5 h-5" />
    </div>
  </div>
);

export default function ReportDetail() {
  const [, params] = useRoute("/report/:id");
  const reportId = params?.id; // 日期格式，如 "2026-01-29"
  const [activeTab, setActiveTab] = useState("all");
  const contentRef = useRef<HTMLDivElement>(null);

  // 数据状态
  const [loading, setLoading] = useState(true);
  const [newsItems, setNewsItems] = useState<NewsItem[]>(mockNews);
  const [stats, setStats] = useState(mockStats);
  const [dailySummary, setDailySummary] = useState(mockDailySummary);
  const [reportDate, setReportDate] = useState(reportId || new Date().toISOString().split('T')[0]);
  const [weeklyTitle, setWeeklyTitle] = useState<string | null>(null);
  const [weeklyContent, setWeeklyContent] = useState<string | null>(null);
  const [reportNotFound, setReportNotFound] = useState(false);

  // 加载数据（日报或周报）
  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setWeeklyTitle(null);
      setWeeklyContent(null);
      setReportNotFound(false);
      try {
        if (reportId?.startsWith("weekly-")) {
          const listRes = await fetch("/api/weekly-reports");
          if (listRes.ok) {
            const { weeklyReports } = await listRes.json();
            const found = (weeklyReports || []).find((w: { id: string; file: string; title: string }) => w.id === reportId);
            if (found?.file) {
              const contentRes = await fetch(`/api/weekly-report?file=${encodeURIComponent(found.file)}`);
              if (contentRes.ok) {
                const text = await contentRes.text();
                setWeeklyTitle(found.title);
                setWeeklyContent(text);
              }
            }
          }
          setLoading(false);
          return;
        }

        let report: DailyReport | null;
        if (reportId) {
          report = await getReportByDate(reportId);
        } else {
          report = await getLatestReport();
        }

        if (report) {
          setNewsItems(report.newsItems || []);
          const st = report.stats;
          setStats(st && typeof st.highThreats === "number" ? st : {
            totalThreats: 0,
            highThreats: 0,
            mediumThreats: 0,
            lowThreats: 0,
            competitorUpdates: (st as any)?.competitors ?? 0,
            customerUpdates: (st as any)?.clients ?? 0,
            industryUpdates: (st as any)?.industry ?? 0,
          });
          setDailySummary(report.dailySummary && typeof report.dailySummary.competitorThreat === "string"
            ? report.dailySummary
            : { competitorThreat: "", industryTrend: "" });
          setReportDate(report.date);
        } else if (reportId) {
          setReportDate(reportId);
          setReportNotFound(true);
        }
      } catch (error) {
        console.error("Failed to load report data:", error);
        if (reportId) setReportNotFound(true);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [reportId]);

  // 计算筛选后的新闻
  const highThreatNews = newsItems.filter(n => n.threatLevel === 'high');
  const otherNews = newsItems.filter(n => n.threatLevel !== 'high');

  // 从 newsItems 派生统计，与下方 Tab 数量一致，避免顶部方块与第三行数据不对齐
  const derivedStats = {
    highThreats: highThreatNews.length,
    competitorUpdates: newsItems.filter(n => n.category === 'competitor').length,
    customerUpdates: newsItems.filter(n => n.category === 'customer').length,
    industryUpdates: newsItems.filter(n => n.category === 'industry').length,
  };

  const scrollToContent = (tab: string) => {
    setActiveTab(tab);
    contentRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 格式化日期显示
  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
        </div>
      </Layout>
    );
  }

  if (weeklyContent !== null) {
    return (
      <Layout>
        <div className="space-y-8">
          <div className="flex flex-col gap-4">
            <Link href="/">
              <a className="inline-flex items-center text-sm text-muted-foreground hover:text-primary transition-colors">
                <ArrowLeft className="w-4 h-4 mr-1" /> Back to Intelligence Center
              </a>
            </Link>
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-foreground">Weekly Report</h1>
              <p className="text-muted-foreground mt-1">{weeklyTitle || reportId}</p>
            </div>
          </div>
          <Card>
            <CardContent className="p-6">
              <div className="prose dark:prose-invert max-w-none whitespace-pre-wrap font-sans text-sm leading-relaxed">
                {weeklyContent}
              </div>
            </CardContent>
          </Card>
        </div>
      </Layout>
    );
  }

  if (reportNotFound && reportId) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
          <p className="text-muted-foreground">Report not found for {reportId}.</p>
          <Link href="/">
            <a className="text-sm text-primary hover:underline">Back to Intelligence Center</a>
          </Link>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header Section */}
        <div className="flex flex-col gap-4">
          <Link href="/">
            <a className="inline-flex items-center text-sm text-muted-foreground hover:text-primary transition-colors">
              <ArrowLeft className="w-4 h-4 mr-1" /> Back to Intelligence Center
            </a>
          </Link>

          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-foreground">Daily Intelligence Brief</h1>
              <p className="text-muted-foreground mt-1">
                {formatDate(reportDate)} • Stablecoin Market Analysis
              </p>
            </div>
            <div className="flex gap-2">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                <span className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse" />
                Report Generated
              </span>
            </div>
          </div>
        </div>

        {/* Interactive Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="High Threats"
            value={derivedStats.highThreats}
            subtext={derivedStats.highThreats > 0 ? "Requires attention" : "All clear"}
            icon={AlertTriangle}
            colorClass="text-red-600"
            bgClass="bg-red-100 dark:bg-red-900/20"
            borderClass="border-l-red-500"
            targetTab="high_threat"
            onClick={scrollToContent}
          />
          <StatCard
            title="Competitor Updates"
            value={derivedStats.competitorUpdates}
            subtext="New activities"
            icon={Users}
            colorClass="text-blue-600"
            bgClass="bg-blue-100 dark:bg-blue-900/20"
            borderClass="border-l-blue-500"
            targetTab="competitors"
            onClick={scrollToContent}
          />
          <StatCard
            title="Industry Trends"
            value={derivedStats.industryUpdates}
            subtext={derivedStats.industryUpdates > 20 ? "High Activity" : "Normal"}
            icon={Activity}
            colorClass="text-amber-600"
            bgClass="bg-amber-100 dark:bg-amber-900/20"
            borderClass="border-l-amber-500"
            targetTab="all"
            onClick={scrollToContent}
          />
          <StatCard
            title="Customer Signals"
            value={derivedStats.customerUpdates}
            subtext="Opportunities"
            icon={ArrowUpRight}
            colorClass="text-emerald-600"
            bgClass="bg-emerald-100 dark:bg-emerald-900/20"
            borderClass="border-l-emerald-500"
            targetTab="customers"
            onClick={scrollToContent}
          />
        </div>

        {/* Executive Summary & Market Pulse - Balanced Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
          <Card className="border-primary/20 bg-primary/5 flex flex-col h-full">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-primary text-lg">
                <AlertTriangle className="w-5 h-5" />
                Executive Summary: Competitor Threats
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1">
              <p className="text-foreground/80 leading-relaxed text-sm md:text-base">
                {dailySummary?.competitorThreat || "No significant competitor threats identified today."}
              </p>
            </CardContent>
          </Card>

          <Card className="border-border/50 flex flex-col h-full">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-lg">
                <TrendingUp className="w-5 h-5 text-muted-foreground" />
                Market Pulse
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1">
              <p className="text-muted-foreground leading-relaxed text-sm md:text-base">
                {dailySummary?.industryTrend || "No major industry trends to report today."}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <div ref={contentRef} className="pt-4">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <div className="flex items-center justify-between mb-6 overflow-x-auto pb-2">
              <TabsList>
                <TabsTrigger value="all">All Intelligence</TabsTrigger>
                <TabsTrigger value="high_threat">High Threats ({highThreatNews.length})</TabsTrigger>
                <TabsTrigger value="competitors">Competitors ({newsItems.filter(n => n.category === 'competitor').length})</TabsTrigger>
                <TabsTrigger value="customers">Customers ({newsItems.filter(n => n.category === 'customer').length})</TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="all" className="space-y-8 animate-in fade-in duration-500">
              {highThreatNews.length > 0 && (
                <section>
                  <div className="flex items-center gap-2 mb-4 p-2 bg-red-50 dark:bg-red-900/10 rounded-lg border border-red-100 dark:border-red-900/30 w-fit">
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                    <h3 className="text-sm font-bold text-red-600 uppercase tracking-wider">
                      Critical Attention Required
                    </h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {highThreatNews.map(item => (
                      <NewsCard key={item.id} item={item} />
                    ))}
                  </div>
                </section>
              )}

              <section>
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 px-1">
                  General Intelligence ({otherNews.length} items)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {otherNews.map(item => (
                    <NewsCard key={item.id} item={item} />
                  ))}
                </div>
              </section>
            </TabsContent>

            <TabsContent value="high_threat" className="animate-in fade-in duration-500">
              {highThreatNews.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {highThreatNews.map(item => (
                    <NewsCard key={item.id} item={item} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <AlertTriangle className="w-12 h-12 mx-auto mb-4 opacity-20" />
                  <p>No high threats identified today</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="competitors" className="animate-in fade-in duration-500">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {newsItems.filter(n => n.category === 'competitor').map(item => (
                  <NewsCard key={item.id} item={item} />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="customers" className="animate-in fade-in duration-500">
              {newsItems.filter(n => n.category === 'customer').length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {newsItems.filter(n => n.category === 'customer').map(item => (
                    <NewsCard key={item.id} item={item} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <Users className="w-12 h-12 mx-auto mb-4 opacity-20" />
                  <p>No customer signals today</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </Layout>
  );
}
