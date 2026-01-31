import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Bell, Key, ListFilter, Save, Plus, Trash2, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";

// Minimal type for config we read/write; rest is preserved as-is
interface KeywordsConfig {
  version?: string;
  last_updated?: string;
  description?: string;
  company?: Record<string, unknown>;
  search_keywords: { primary: string[]; secondary?: string[] };
  competitors: {
    tier_0_custody: { name: string; twitter?: string }[];
    tier_1_payment_infra?: { name: string; twitter?: string }[];
  };
  [key: string]: unknown;
}

const defaultConfig: KeywordsConfig = {
  search_keywords: { primary: [], secondary: [] },
  competitors: { tier_0_custody: [] },
};

export default function Settings() {
  const [config, setConfig] = useState<KeywordsConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [readOnlyStatic, setReadOnlyStatic] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "ok" | "error">("idle");
  const [newKeyword, setNewKeyword] = useState("");
  const [newCompetitorName, setNewCompetitorName] = useState("");
  const [newCompetitorTwitter, setNewCompetitorTwitter] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setLoadError(null);
    setReadOnlyStatic(false);
    const base = (typeof import.meta !== "undefined" && import.meta.env?.BASE_URL) || "";
    fetch("/api/keywords")
      .then((r) => {
        if (!r.ok) throw new Error(r.statusText || "Failed to load");
        return r.json();
      })
      .then((data) => {
        if (!cancelled) {
          setConfig(data as KeywordsConfig);
        }
      })
      .catch(() => {
        if (cancelled) return;
        const staticUrl = `${base}data/keywords.json`.replace(/([^:]\/)\/+/g, "$1");
        return fetch(staticUrl).then((r) => {
          if (!r.ok) throw new Error("Static config not found");
          return r.json();
        }).then((data) => {
          if (!cancelled) {
            setConfig(data as KeywordsConfig);
            setReadOnlyStatic(true);
          }
        }).catch((e) => {
          if (!cancelled) {
            setLoadError(e instanceof Error ? e.message : "Unable to load keyword config. On static site, ensure data/keywords.json is deployed.");
            setConfig(null);
          }
        });
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  const primaryKeywords = config?.search_keywords?.primary ?? [];
  const competitors = config?.competitors?.tier_0_custody ?? [];

  const addKeyword = () => {
    const t = newKeyword.trim();
    if (!t || !config) return;
    const next = [...(config.search_keywords.primary || []), t];
    setConfig({ ...config, search_keywords: { ...config.search_keywords, primary: next } });
    setNewKeyword("");
  };

  const removeKeyword = (keyword: string) => {
    if (!config) return;
    const next = (config.search_keywords.primary || []).filter((k) => k !== keyword);
    setConfig({ ...config, search_keywords: { ...config.search_keywords, primary: next } });
  };

  const addCompetitor = () => {
    const name = newCompetitorName.trim();
    if (!name || !config) return;
    const twitter = newCompetitorTwitter.trim() || undefined;
    const list = config.competitors?.tier_0_custody ?? [];
    const next = [...list, { name, twitter }];
    setConfig({
      ...config,
      competitors: { ...config.competitors, tier_0_custody: next },
    });
    setNewCompetitorName("");
    setNewCompetitorTwitter("");
  };

  const removeCompetitor = (index: number) => {
    if (!config) return;
    const list = [...(config.competitors.tier_0_custody || [])];
    list.splice(index, 1);
    setConfig({ ...config, competitors: { ...config.competitors, tier_0_custody: list } });
  };

  const saveConfig = async () => {
    if (!config) return;
    setSaveStatus("saving");
    try {
      const res = await fetch("/api/keywords", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || res.statusText);
      }
      setSaveStatus("ok");
      setTimeout(() => setSaveStatus("idle"), 2500);
    } catch (e) {
      setSaveStatus("error");
      setTimeout(() => setSaveStatus("idle"), 3000);
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

  const effectiveConfig = config ?? defaultConfig;

  return (
    <Layout>
      <div className="space-y-8 animate-in fade-in duration-500">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Manage your intelligence preferences and system configuration.
          </p>
        </div>

        {loadError && (
          <div className="rounded-lg border border-amber-200 bg-amber-50 dark:border-amber-900/50 dark:bg-amber-900/10 px-4 py-3 text-sm text-amber-800 dark:text-amber-200">
            {loadError}
          </div>
        )}

        {readOnlyStatic && (
          <div className="rounded-lg border border-blue-200 bg-blue-50 dark:border-blue-900/50 dark:bg-blue-900/10 px-4 py-3 text-sm text-blue-800 dark:text-blue-200">
            Config is read-only on this site (no backend). Keywords and competitors are loaded from the deployed snapshot. To change them, edit <code className="bg-black/10 dark:bg-white/10 px-1 rounded">config/keywords.json</code> in the repo and redeploy.
          </div>
        )}

        <Tabs defaultValue="monitoring" className="w-full">
          <TabsList className="grid w-full grid-cols-3 max-w-[400px] mb-8">
            <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="api">API Access</TabsTrigger>
          </TabsList>

          {/* Monitoring Settings */}
          <TabsContent value="monitoring" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ListFilter className="w-5 h-5" />
                  Tracked Keywords
                </CardTitle>
                <CardDescription>
                  The system scans for these terms across global news sources. Stored in config/keywords.json (search_keywords.primary).
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2 mb-4">
                  <Input
                    placeholder="Add new keyword..."
                    className="max-w-sm"
                    value={newKeyword}
                    onChange={(e) => setNewKeyword(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && addKeyword()}
                  />
                  <Button variant="secondary" onClick={addKeyword} disabled={!effectiveConfig}>
                    <Plus className="w-4 h-4 mr-2" /> Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {primaryKeywords.map((keyword) => (
                    <div key={keyword} className="flex items-center gap-1 bg-secondary px-3 py-1.5 rounded-full text-sm font-medium">
                      {keyword}
                      <button onClick={() => removeKeyword(keyword)} className="text-muted-foreground hover:text-destructive transition-colors ml-1">
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              </CardContent>
              <CardFooter className="bg-muted/50 border-t border-border/50 px-6 py-4">
                <Button onClick={saveConfig} disabled={saveStatus === "saving" || !config || readOnlyStatic}>
                  {saveStatus === "saving" ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                  {readOnlyStatic ? "Read-only (static site)" : saveStatus === "saving" ? "Saving..." : saveStatus === "ok" ? "Saved" : saveStatus === "error" ? "Save failed" : "Save Changes"}
                </Button>
              </CardFooter>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Competitor Watchlist</CardTitle>
                <CardDescription>
                  Specific entities to monitor (tier_0_custody). Name and optional Twitter handle.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap gap-2 items-end">
                  <div className="space-y-1">
                    <Label className="text-xs">Name</Label>
                    <Input
                      placeholder="Company name"
                      className="w-40"
                      value={newCompetitorName}
                      onChange={(e) => setNewCompetitorName(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && addCompetitor()}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Twitter (optional)</Label>
                    <Input
                      placeholder="@handle"
                      className="w-32"
                      value={newCompetitorTwitter}
                      onChange={(e) => setNewCompetitorTwitter(e.target.value)}
                    />
                  </div>
                  <Button variant="secondary" onClick={addCompetitor} disabled={!newCompetitorName.trim() || !config}>
                    <Plus className="w-4 h-4 mr-2" /> Add
                  </Button>
                </div>
                <div className="space-y-2">
                  {competitors.map((c, i) => (
                    <div key={`${c.name}-${i}`} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <span className="font-medium">{c.name}</span>
                        {c.twitter && <span className="text-muted-foreground text-sm ml-2">@{c.twitter.replace(/^@/, "")}</span>}
                      </div>
                      <button onClick={() => removeCompetitor(i)} className="text-muted-foreground hover:text-destructive transition-colors p-1">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </CardContent>
              <CardFooter className="bg-muted/50 border-t border-border/50 px-6 py-4">
                <Button onClick={saveConfig} disabled={saveStatus === "saving" || !config || readOnlyStatic}>
                  {saveStatus === "saving" ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                  {readOnlyStatic ? "Read-only (static site)" : "Save Changes"}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>

          {/* Notification Settings */}
          <TabsContent value="notifications">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="w-5 h-5" />
                  Alert Preferences
                </CardTitle>
                <CardDescription>
                  Configure how and when you receive intelligence updates.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between space-x-2">
                  <Label htmlFor="daily-digest" className="flex flex-col space-y-1">
                    <span>Daily Email Digest</span>
                    <span className="text-xs text-muted-foreground font-normal">Receive a summary of all intel at 8:00 AM EST.</span>
                  </Label>
                  <Switch id="daily-digest" defaultChecked />
                </div>
                <div className="flex items-center justify-between space-x-2">
                  <Label htmlFor="critical-alerts" className="flex flex-col space-y-1">
                    <span>Critical Threat Alerts</span>
                    <span className="text-xs text-muted-foreground font-normal">Immediate email for High Threat items.</span>
                  </Label>
                  <Switch id="critical-alerts" defaultChecked />
                </div>
                <div className="flex items-center justify-between space-x-2">
                  <Label htmlFor="slack" className="flex flex-col space-y-1">
                    <span>Slack Integration</span>
                    <span className="text-xs text-muted-foreground font-normal">Push updates to #stablecoin-intel channel.</span>
                  </Label>
                  <Switch id="slack" />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* API Settings */}
          <TabsContent value="api">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Key className="w-5 h-5" />
                  API Configuration
                </CardTitle>
                <CardDescription>
                  Manage API keys for external integrations.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Current API Key</Label>
                  <div className="flex gap-2">
                    <Input value="sk_live_51M...92xP" readOnly className="font-mono bg-muted" />
                    <Button variant="outline">Copy</Button>
                  </div>
                </div>
                <div className="pt-4">
                  <Button variant="destructive">Revoke Key</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}
