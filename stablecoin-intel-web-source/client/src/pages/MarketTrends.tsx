import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { TrendingUp, PieChart as PieChartIcon, DollarSign } from "lucide-react";

const marketCapData = [
  { date: 'Jan 1', usdt: 92, usdc: 25, dai: 5 },
  { date: 'Jan 5', usdt: 93, usdc: 24.8, dai: 4.9 },
  { date: 'Jan 10', usdt: 93.5, usdc: 24.5, dai: 4.8 },
  { date: 'Jan 15', usdt: 94, usdc: 24.2, dai: 4.8 },
  { date: 'Jan 20', usdt: 95, usdc: 24.0, dai: 4.7 },
  { date: 'Jan 25', usdt: 96, usdc: 23.8, dai: 4.6 },
  { date: 'Jan 29', usdt: 96.5, usdc: 23.5, dai: 4.5 },
];

const voiceShareData = [
  { name: 'Tether (USDT)', value: 45, color: '#10b981' },
  { name: 'Circle (USDC)', value: 30, color: '#3b82f6' },
  { name: 'PayPal (PYUSD)', value: 15, color: '#f59e0b' },
  { name: 'Others', value: 10, color: '#64748b' },
];

export default function MarketTrends() {
  return (
    <Layout>
      <div className="space-y-8 animate-in fade-in duration-500">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight">Market Trends</h1>
          <p className="text-muted-foreground">
            Quantitative analysis of market capitalization and media presence.
          </p>
        </div>

        {/* Market Cap Trend */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-500" />
              Stablecoin Market Cap Growth (Billions USD)
            </CardTitle>
            <CardDescription>
              30-day tracking of major stablecoin supplies.
            </CardDescription>
          </CardHeader>
          <CardContent className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={marketCapData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-muted" />
                <XAxis dataKey="date" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--card)', borderRadius: '8px', border: '1px solid var(--border)' }} />
                <Legend />
                <Line type="monotone" dataKey="usdt" stroke="#10b981" strokeWidth={2} dot={false} name="Tether (USDT)" />
                <Line type="monotone" dataKey="usdc" stroke="#3b82f6" strokeWidth={2} dot={false} name="Circle (USDC)" />
                <Line type="monotone" dataKey="dai" stroke="#f59e0b" strokeWidth={2} dot={false} name="DAI" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Share of Voice */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChartIcon className="w-5 h-5 text-purple-500" />
                Share of Voice (Media Mentions)
              </CardTitle>
              <CardDescription>
                Who is dominating the news cycle this week?
              </CardDescription>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={voiceShareData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {voiceShareData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'var(--card)', borderRadius: '8px' }} />
                  <Legend verticalAlign="bottom" height={36}/>
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Key Insights */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-500" />
                Analyst Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-4">
                <li className="flex gap-3">
                  <div className="flex-shrink-0 w-1.5 h-1.5 mt-2 rounded-full bg-primary" />
                  <p className="text-sm text-muted-foreground">
                    <span className="font-semibold text-foreground">USDT Dominance:</span> Continues to capture market share despite regulatory FUD, growing 4% this month.
                  </p>
                </li>
                <li className="flex gap-3">
                  <div className="flex-shrink-0 w-1.5 h-1.5 mt-2 rounded-full bg-primary" />
                  <p className="text-sm text-muted-foreground">
                    <span className="font-semibold text-foreground">PYUSD Growth:</span> PayPal's stablecoin is seeing increased adoption in DeFi protocols, a 15% WoW increase.
                  </p>
                </li>
                <li className="flex gap-3">
                  <div className="flex-shrink-0 w-1.5 h-1.5 mt-2 rounded-full bg-primary" />
                  <p className="text-sm text-muted-foreground">
                    <span className="font-semibold text-foreground">USDC Strategy:</span> Circle is pivoting focus to EU markets ahead of MiCA implementation.
                  </p>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
}
