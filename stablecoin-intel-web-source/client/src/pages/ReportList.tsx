import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CalendarDays, ChevronRight, AlertTriangle, Loader2 } from "lucide-react";
import { Link } from "wouter";
import { useState, useEffect } from "react";
import { getReportList, type ReportSummary, reportList as mockReportList } from "@/lib/data-service";

export default function ReportList() {
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState<ReportSummary[]>(mockReportList);

  // 加载报告列表
  useEffect(() => {
    async function loadReports() {
      setLoading(true);
      try {
        const data = await getReportList();
        if (data.length > 0) {
          setReports(data);
        }
      } catch (error) {
        console.error('Failed to load report list:', error);
        // 使用 mock 数据作为降级
      } finally {
        setLoading(false);
      }
    }

    loadReports();
  }, []);

  // 只展示最近两天的日报（01-28、01-29）
  const dailyReports = reports.filter(r => r.type === 'daily').slice(0, 2);
  const weeklyReports = reports.filter(r => r.type === 'weekly');

  const ReportCard = ({ report }: { report: ReportSummary }) => (
    <Link href={`/report/${report.id}`}>
      <a className="block group">
        <Card className="h-full transition-all duration-300 hover:shadow-md border-border/50 bg-card/50 hover:border-primary/50">
          <CardHeader className="pb-3">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                  <CalendarDays className="w-3 h-3" />
                  {report.date}
                </div>
                <CardTitle className="text-lg group-hover:text-primary transition-colors">
                  {report.title}
                </CardTitle>
              </div>
              <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors opacity-0 group-hover:opacity-100" />
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
              {report.summary}
            </p>
            <div className="flex items-center gap-3 text-xs font-medium">
              {report.stats.high > 0 && (
                <span className="flex items-center gap-1 text-red-600 bg-red-50 dark:bg-red-900/20 px-2 py-1 rounded-full">
                  <AlertTriangle className="w-3 h-3" />
                  {report.stats.high} High Threats
                </span>
              )}
              <span className="text-muted-foreground bg-muted px-2 py-1 rounded-full">
                {report.stats.competitorUpdates ?? (report.stats.medium + report.stats.low)} Updates
              </span>
            </div>
          </CardContent>
        </Card>
      </a>
    </Link>
  );

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
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight">Intelligence Center</h1>
          <p className="text-muted-foreground">
            Access daily briefings and weekly summaries.
          </p>
        </div>

        <Tabs defaultValue="daily" className="w-full">
          <TabsList className="grid w-full grid-cols-2 max-w-[400px] mb-8">
            <TabsTrigger value="daily">Daily Briefs ({dailyReports.length})</TabsTrigger>
            <TabsTrigger value="weekly">Weekly Reports ({weeklyReports.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="daily" className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {dailyReports.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {dailyReports.map(report => (
                  <ReportCard key={report.id} report={report} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <p>No daily reports available</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="weekly" className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {weeklyReports.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {weeklyReports.map(report => (
                  <ReportCard key={report.id} report={report} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <p>No weekly reports available yet</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}
