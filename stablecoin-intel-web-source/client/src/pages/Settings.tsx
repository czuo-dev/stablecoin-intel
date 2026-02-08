import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Bell, ListFilter, Save, Plus, Trash2, Loader2, Github } from "lucide-react";
import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import {
  getGitHubToken,
  fetchKeywordsFromGitHub,
  saveKeywordsToGitHub,
} from "@/lib/github-keywords";

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

type SaveStatus = "idle" | "saving" | "ok" | "ok_github" | "error";

export default function Settings() {
  const { user } = useAuth();
  const [config, setConfig] = useState<KeywordsConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [readOnly, setReadOnly] = useState(false);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");
  const [newKeyword, setNewKeyword] = useState("");
  const [newCompetitorName, setNewCompetitorName] = useState("");
  const [newCompetitorTwitter, setNewCompetitorTwitter] = useState("");

  // SHA of the file on GitHub — needed for conflict-free commits
  const [githubSha, setGithubSha] = useState<string | null>(null);
  // Whether we loaded from GitHub API (vs local backend or static file)
  const [usingGitHub, setUsingGitHub] = useState(false);

  const ghToken = getGitHubToken();

  // ── Load config ──────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setLoadError(null);
    setReadOnly(false);
    setUsingGitHub(false);

    const base = (typeof import.meta !== "undefined" && import.meta.env?.BASE_URL) || "";

    // Priority 1: local backend API (dev / Express)
    fetch("/api/keywords")
      .then((r) => {
        if (!r.ok) throw new Error(r.statusText || "Failed to load");
        return r.json();
      })
      .then((data) => {
        if (!cancelled) setConfig(data as KeywordsConfig);
      })
      .catch(() => {
        if (cancelled) return;

        // Priority 2: GitHub API (production with GH_PAT)
        if (ghToken) {
          return fetchKeywordsFromGitHub<KeywordsConfig>(ghToken)
            .then(({ config: cfg, sha }) => {
              if (!cancelled) {
                setConfig(cfg);
                setGithubSha(sha);
                setUsingGitHub(true);
              }
            })
            .catch(() => {
              // fall through to static
              if (cancelled) return;
              return loadStatic();
            });
        }

        // Priority 3: static JSON (read-only)
        return loadStatic();

        function loadStatic() {
          const staticUrl = `${base}data/keywords.json`.replace(/([^:]\/)\/+/g, "$1");
          return fetch(staticUrl)
            .then((r) => {
              if (!r.ok) throw new Error("Static config not found");
              return r.json();
            })
            .then((data) => {
              if (!cancelled) {
                setConfig(data as KeywordsConfig);
                setReadOnly(true);
              }
            })
            .catch((e) => {
              if (!cancelled) {
                setLoadError(
                  e instanceof Error
                    ? e.message
                    : "Unable to load keyword config.",
                );
                setConfig(null);
              }
            });
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [ghToken]);

  // ── Derived state ────────────────────────────────────────────
  const primaryKeywords = config?.search_keywords?.primary ?? [];
  const competitors = config?.competitors?.tier_0_custody ?? [];

  // ── Keyword CRUD ─────────────────────────────────────────────
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

  // ── Competitor CRUD ──────────────────────────────────────────
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

  // ── Save config ──────────────────────────────────────────────
  const saveConfig = async () => {
    if (!config) return;
    setSaveStatus("saving");

    try {
      if (usingGitHub && ghToken && githubSha) {
        // Production: commit to GitHub
        await saveKeywordsToGitHub(ghToken, config, githubSha, user?.email ?? undefined);
        // Re-fetch to get the new SHA for future saves
        const { sha: newSha } = await fetchKeywordsFromGitHub(ghToken);
        setGithubSha(newSha);
        setSaveStatus("ok_github");
        setTimeout(() => setSaveStatus("idle"), 4000);
      } else {
        // Dev: use local backend API
        const res = await fetch("/api/keywords", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(config),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error((err as Record<string, string>).error || res.statusText);
        }
        setSaveStatus("ok");
        setTimeout(() => setSaveStatus("idle"), 2500);
      }
    } catch (e) {
      console.error("Save failed:", e);
      setSaveStatus("error");
      setTimeout(() => setSaveStatus("idle"), 3000);
    }
  };

  // ── Save button label ────────────────────────────────────────
  const saveLabel = (showGitHubHint = false) => {
    if (readOnly) return "Read-only (no token)";
    if (saveStatus === "saving") return "Saving...";
    if (saveStatus === "ok") return "Saved";
    if (saveStatus === "ok_github") return "Committed! Takes effect tomorrow";
    if (saveStatus === "error") return "Save failed";
    if (showGitHubHint && usingGitHub) return "Save & Commit to GitHub";
    return "Save Changes";
  };

  const saveIcon = () => {
    if (saveStatus === "saving") return <Loader2 className="w-4 h-4 mr-2 animate-spin" />;
    if (usingGitHub && !readOnly) return <Github className="w-4 h-4 mr-2" />;
    return <Save className="w-4 h-4 mr-2" />;
  };

  // ── Loading state ────────────────────────────────────────────
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

        {readOnly && (
          <div className="rounded-lg border border-blue-200 bg-blue-50 dark:border-blue-900/50 dark:bg-blue-900/10 px-4 py-3 text-sm text-blue-800 dark:text-blue-200">
            Config is read-only (no GitHub token configured). To enable editing, ensure <code className="bg-black/10 dark:bg-white/10 px-1 rounded">GH_PAT</code> is set in repository Secrets and redeploy.
          </div>
        )}

        {usingGitHub && (
          <div className="rounded-lg border border-green-200 bg-green-50 dark:border-green-900/50 dark:bg-green-900/10 px-4 py-3 text-sm text-green-800 dark:text-green-200">
            <Github className="w-4 h-4 inline mr-1.5 -mt-0.5" />
            Connected to GitHub. Changes will be committed to the repository and take effect in the next daily collection.
          </div>
        )}

        <Tabs defaultValue="monitoring" className="w-full">
          <TabsList className="grid w-full grid-cols-2 max-w-[400px] mb-8">
            <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
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
                  The system scans for these terms across global news sources. Changes take effect in the next daily collection.
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
                    disabled={readOnly}
                  />
                  <Button variant="secondary" onClick={addKeyword} disabled={!effectiveConfig || readOnly}>
                    <Plus className="w-4 h-4 mr-2" /> Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {primaryKeywords.map((keyword) => (
                    <div key={keyword} className="flex items-center gap-1 bg-secondary px-3 py-1.5 rounded-full text-sm font-medium">
                      {keyword}
                      <button
                        onClick={() => removeKeyword(keyword)}
                        className="text-muted-foreground hover:text-destructive transition-colors ml-1"
                        disabled={readOnly}
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              </CardContent>
              <CardFooter className="bg-muted/50 border-t border-border/50 px-6 py-4">
                <Button onClick={saveConfig} disabled={saveStatus === "saving" || !config || readOnly}>
                  {saveIcon()}
                  {saveLabel(true)}
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
                      disabled={readOnly}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Twitter (optional)</Label>
                    <Input
                      placeholder="@handle"
                      className="w-32"
                      value={newCompetitorTwitter}
                      onChange={(e) => setNewCompetitorTwitter(e.target.value)}
                      disabled={readOnly}
                    />
                  </div>
                  <Button variant="secondary" onClick={addCompetitor} disabled={!newCompetitorName.trim() || !config || readOnly}>
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
                      <button
                        onClick={() => removeCompetitor(i)}
                        className="text-muted-foreground hover:text-destructive transition-colors p-1"
                        disabled={readOnly}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </CardContent>
              <CardFooter className="bg-muted/50 border-t border-border/50 px-6 py-4">
                <Button onClick={saveConfig} disabled={saveStatus === "saving" || !config || readOnly}>
                  {saveIcon()}
                  {saveLabel()}
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
        </Tabs>
      </div>
    </Layout>
  );
}
