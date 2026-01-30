import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import { Network, GitBranch, Zap } from "lucide-react";

const sentimentData = [
  { date: 'Jan 23', positive: 40, negative: 24, neutral: 24 },
  { date: 'Jan 24', positive: 30, negative: 13, neutral: 22 },
  { date: 'Jan 25', positive: 20, negative: 58, neutral: 22 },
  { date: 'Jan 26', positive: 27, negative: 39, neutral: 20 },
  { date: 'Jan 27', positive: 18, negative: 48, neutral: 21 },
  { date: 'Jan 28', positive: 23, negative: 38, neutral: 25 },
  { date: 'Jan 29', positive: 34, negative: 43, neutral: 21 },
];

const entityData = [
  { name: 'Fidelity', mentions: 120, sentiment: -20 },
  { name: 'Circle', mentions: 98, sentiment: 45 },
  { name: 'Tether', mentions: 86, sentiment: -10 },
  { name: 'PayPal', mentions: 65, sentiment: 30 },
  { name: 'Coinbase', mentions: 55, sentiment: 15 },
];

export default function DeepAnalysis() {
  return (
    <Layout>
      <div className="space-y-8 animate-in fade-in duration-500">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight">Deep Analysis</h1>
          <p className="text-muted-foreground">
            Advanced sentiment tracking and entity relationship mapping.
          </p>
        </div>

        {/* Sentiment Trend Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-amber-500" />
              Market Sentiment Trends (Last 7 Days)
            </CardTitle>
            <CardDescription>
              Tracking the emotional tone of global news coverage regarding stablecoins.
            </CardDescription>
          </CardHeader>
          <CardContent className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sentimentData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorPos" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorNeg" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}%`} />
                <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-muted" />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--card)', borderRadius: '8px', border: '1px solid var(--border)' }}
                />
                <Legend />
                <Area type="monotone" dataKey="positive" stroke="#10b981" fillOpacity={1} fill="url(#colorPos)" name="Positive Sentiment" />
                <Area type="monotone" dataKey="negative" stroke="#ef4444" fillOpacity={1} fill="url(#colorNeg)" name="Negative Sentiment" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Entity Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Network className="w-5 h-5 text-blue-500" />
                Key Entity Mentions & Sentiment
              </CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={entityData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" width={80} tick={{fontSize: 12}} />
                  <Tooltip cursor={{fill: 'transparent'}} contentStyle={{ backgroundColor: 'var(--card)', borderRadius: '8px' }} />
                  <Bar dataKey="mentions" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20} name="News Mentions" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Relationship Graph Placeholder */}
          <Card className="flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="w-5 h-5 text-purple-500" />
                Entity Relationship Map
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex items-center justify-center bg-muted/20 m-6 rounded-lg border-2 border-dashed border-muted">
              <div className="text-center p-6">
                <div className="mx-auto w-12 h-12 bg-muted rounded-full flex items-center justify-center mb-3">
                  <Network className="w-6 h-6 text-muted-foreground" />
                </div>
                <h3 className="font-semibold text-foreground">Interactive Graph View</h3>
                <p className="text-sm text-muted-foreground mt-1 max-w-xs mx-auto">
                  Visualization of connections between companies, regulators, and market events will be rendered here.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
}
