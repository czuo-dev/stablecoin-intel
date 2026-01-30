import Layout from "@/components/Layout";
import NewsCard from "@/components/NewsCard";
import { mockNews, dailySummary as mockDailySummary } from "@/lib/mock-data";
import { getLatestReport } from "@/lib/data-service";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertTriangle, TrendingUp, Users, Activity, ArrowUpRight, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { Link } from "wouter";

export default function Home() {
  const [newsItems, setNewsItems] = useState(mockNews);
  const [dailySummary, setDailySummary] = useState(mockDailySummary);
  const [reportDate, setReportDate] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getLatestReport()
      .then((report) => {
        if (cancelled || !report) return;
        setNewsItems(report.newsItems || []);
        setDailySummary(report.dailySummary || mockDailySummary);
        setReportDate(report.date || "");
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  const highThreatNews = newsItems.filter(n => n.threatLevel === 'high');
  const otherNews = newsItems.filter(n => n.threatLevel !== 'high');
  const derivedStats = {
    highThreats: highThreatNews.length,
    competitorUpdates: newsItems.filter(n => n.category === 'competitor').length,
    industryUpdates: newsItems.filter(n => n.category === 'industry').length,
    customerUpdates: newsItems.filter(n => n.category === 'customer').length,
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

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">Daily Intelligence Brief</h1>
            <p className="text-muted-foreground mt-1">
              {reportDate ? new Date(reportDate + "T12:00:00").toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" }) : "Latest"} • Stablecoin Market Analysis
            </p>
          </div>
          <div className="flex gap-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
              <span className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse" />
              System Active
            </span>
          </div>
        </div>

        {/* Stats Grid - derived from same report as detail page */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link href={reportDate ? `/report/${reportDate}` : "/reports"}>
            <a className="block">
              <Card className="border-l-4 border-l-red-500 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-4 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">High Threats</p>
                    <div className="flex items-baseline gap-2">
                      <h2 className="text-2xl font-bold text-red-600">{derivedStats.highThreats}</h2>
                      {derivedStats.highThreats > 0 && <span className="text-xs text-red-600 font-medium">Requires attention</span>}
                    </div>
                  </div>
                  <div className="h-10 w-10 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center text-red-600">
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                </CardContent>
              </Card>
            </a>
          </Link>

          <Card className="border-l-4 border-l-blue-500 shadow-sm">
            <CardContent className="p-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Competitor Updates</p>
                <div className="flex items-baseline gap-2">
                  <h2 className="text-2xl font-bold text-blue-600">{derivedStats.competitorUpdates}</h2>
                  <span className="text-xs text-muted-foreground">New activities</span>
                </div>
              </div>
              <div className="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center text-blue-600">
                <Users className="w-5 h-5" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-amber-500 shadow-sm">
            <CardContent className="p-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Industry Trends</p>
                <div className="flex items-baseline gap-2">
                  <h2 className="text-2xl font-bold text-amber-600">{derivedStats.industryUpdates}</h2>
                  <span className="text-xs text-amber-600 font-medium flex items-center">
                    <TrendingUp className="w-3 h-3 mr-1" /> {derivedStats.industryUpdates > 20 ? "High Activity" : "Normal"}
                  </span>
                </div>
              </div>
              <div className="h-10 w-10 rounded-full bg-amber-100 dark:bg-amber-900/20 flex items-center justify-center text-amber-600">
                <Activity className="w-5 h-5" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-emerald-500 shadow-sm">
            <CardContent className="p-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Customer Signals</p>
                <div className="flex items-baseline gap-2">
                  <h2 className="text-2xl font-bold text-emerald-600">{derivedStats.customerUpdates}</h2>
                  <span className="text-xs text-muted-foreground">Opportunities</span>
                </div>
              </div>
              <div className="h-10 w-10 rounded-full bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center text-emerald-600">
                <ArrowUpRight className="w-5 h-5" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Executive Summary */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2 border-primary/20 bg-primary/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-primary">
                <AlertTriangle className="w-5 h-5" />
                Executive Summary: Competitor Threats
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-foreground/80 leading-relaxed">
                {dailySummary.competitorThreat}
              </p>
            </CardContent>
          </Card>

          <Card className="border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-muted-foreground" />
                Market Pulse
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {dailySummary.industryTrend}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="all" className="w-full">
          <div className="flex items-center justify-between mb-4">
            <TabsList>
              <TabsTrigger value="all">All Intelligence</TabsTrigger>
              <TabsTrigger value="high_threat">High Threats</TabsTrigger>
              <TabsTrigger value="competitors">Competitors</TabsTrigger>
              <TabsTrigger value="customers">Customers</TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="all" className="space-y-6">
            {highThreatNews.length > 0 && (
              <section>
                <h3 className="text-sm font-semibold text-red-600 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  Critical Attention Required
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {highThreatNews.map(item => (
                    <NewsCard key={item.id} item={item} />
                  ))}
                </div>
              </section>
            )}

            <section>
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                General Intelligence
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {otherNews.map(item => (
                  <NewsCard key={item.id} item={item} />
                ))}
              </div>
            </section>
          </TabsContent>

          <TabsContent value="high_threat">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {newsItems.filter(n => n.threatLevel === 'high').map(item => (
                <NewsCard key={item.id} item={item} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="competitors">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {newsItems.filter(n => n.category === 'competitor').map(item => (
                <NewsCard key={item.id} item={item} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="customers">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {newsItems.filter(n => n.category === 'customer').map(item => (
                <NewsCard key={item.id} item={item} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}
