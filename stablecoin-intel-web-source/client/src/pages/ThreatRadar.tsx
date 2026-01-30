import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, Cell, CartesianGrid } from 'recharts';
import { ShieldAlert, Target, AlertTriangle } from "lucide-react";

const riskMatrixData = [
  { name: 'Regulatory Crackdown', probability: 85, impact: 90, type: 'Regulatory' },
  { name: 'Competitor M&A', probability: 60, impact: 70, type: 'Market' },
  { name: 'De-pegging Event', probability: 10, impact: 95, type: 'Technical' },
  { name: 'New Entrant (Big Tech)', probability: 40, impact: 80, type: 'Market' },
  { name: 'Wallet Exploit', probability: 20, impact: 60, type: 'Security' },
  { name: 'Banking Partner Loss', probability: 30, impact: 85, type: 'Operational' },
];

const radarData = [
  { subject: 'Regulatory', A: 120, fullMark: 150 },
  { subject: 'Technical', A: 98, fullMark: 150 },
  { subject: 'Market', A: 86, fullMark: 150 },
  { subject: 'Security', A: 99, fullMark: 150 },
  { subject: 'Operational', A: 85, fullMark: 150 },
  { subject: 'Reputational', A: 65, fullMark: 150 },
];

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-card border border-border p-3 rounded-lg shadow-lg">
        <p className="font-semibold text-sm">{data.name}</p>
        <p className="text-xs text-muted-foreground">Impact: {data.impact} | Prob: {data.probability}%</p>
      </div>
    );
  }
  return null;
};

export default function ThreatRadar() {
  return (
    <Layout>
      <div className="space-y-8 animate-in fade-in duration-500">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight">Threat Radar</h1>
          <p className="text-muted-foreground">
            Real-time monitoring of potential risks and strategic threats.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Threat Matrix */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5 text-red-500" />
                Risk Assessment Matrix
              </CardTitle>
              <CardDescription>
                Visualizing threats by Probability (X) vs. Impact (Y). 
                <span className="text-red-500 font-medium ml-1">Top Right = Critical Priority</span>
              </CardDescription>
            </CardHeader>
            <CardContent className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" dataKey="probability" name="Probability" unit="%" domain={[0, 100]} label={{ value: 'Probability', position: 'bottom', offset: 0 }} />
                  <YAxis type="number" dataKey="impact" name="Impact" unit="" domain={[0, 100]} label={{ value: 'Impact', angle: -90, position: 'insideLeft' }} />
                  <ZAxis type="number" range={[100, 400]} />
                  <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
                  <Scatter name="Risks" data={riskMatrixData} fill="#8884d8">
                    {riskMatrixData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.impact > 80 && entry.probability > 50 ? '#ef4444' : entry.impact > 50 ? '#f59e0b' : '#10b981'} />
                    ))}
                  </Scatter>
                  {/* Quadrant Labels */}
                  <text x="85%" y="15%" textAnchor="middle" fill="#ef4444" opacity={0.5} fontSize={12} fontWeight="bold">CRITICAL</text>
                  <text x="85%" y="85%" textAnchor="middle" fill="#f59e0b" opacity={0.5} fontSize={12} fontWeight="bold">MONITOR</text>
                  <text x="15%" y="15%" textAnchor="middle" fill="#f59e0b" opacity={0.5} fontSize={12} fontWeight="bold">PREPARE</text>
                  <text x="15%" y="85%" textAnchor="middle" fill="#10b981" opacity={0.5} fontSize={12} fontWeight="bold">LOW RISK</text>
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Threat Categories Radar */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-blue-500" />
                Vulnerability Profile
              </CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 150]} tick={false} />
                  <Radar name="Threat Level" dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                </RadarChart>
              </ResponsiveContainer>
              <div className="mt-4 text-center text-sm text-muted-foreground">
                Current highest exposure: <span className="font-semibold text-foreground">Regulatory</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Alerts List */}
        <Card className="border-l-4 border-l-red-500">
          <CardHeader>
            <CardTitle className="text-red-600 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Active Critical Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[1, 2].map((i) => (
                <div key={i} className="flex items-start gap-3 pb-4 border-b last:border-0 last:pb-0">
                  <div className="w-2 h-2 mt-2 rounded-full bg-red-500 shrink-0" />
                  <div>
                    <h4 className="font-medium text-sm">SEC to announce new stablecoin guidance on Friday</h4>
                    <p className="text-xs text-muted-foreground mt-1">Source: Internal Analyst • Confidence: High • Est. Impact: High</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
