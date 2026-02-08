/**
 * GitHub Contents API helpers for reading / writing config/keywords.json
 * directly in the repository. Used on GitHub Pages (static site) where
 * there is no backend to persist changes.
 */

const OWNER = "czuo-dev";
const REPO = "stablecoin-intel";
const FILE_PATH = "config/keywords.json";
const API_BASE = "https://api.github.com";

/** Token injected at build time via VITE_GH_PAT (set in deploy-pages.yml). */
export function getGitHubToken(): string | null {
  const t = import.meta.env.VITE_GH_PAT;
  return typeof t === "string" && t.length > 0 ? t : null;
}

export interface GitHubFileResult<T = unknown> {
  config: T;
  sha: string; // needed for subsequent PUT (optimistic concurrency)
}

/**
 * Fetch the latest config/keywords.json from the GitHub repo.
 * Returns the parsed JSON together with the blob SHA.
 */
export async function fetchKeywordsFromGitHub<T = unknown>(
  token: string,
): Promise<GitHubFileResult<T>> {
  const url = `${API_BASE}/repos/${OWNER}/${REPO}/contents/${FILE_PATH}`;
  const res = await fetch(url, {
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`GitHub API ${res.status}: ${body}`);
  }
  const data = await res.json();
  // decodeURIComponent + escape reverses the btoa(unescape(encodeURIComponent(...))) used when writing,
  // and also correctly handles non-ASCII (Chinese) characters from plain base64.
  const content = decodeURIComponent(escape(atob(data.content.replace(/\n/g, ""))));
  const config = JSON.parse(content) as T;
  return { config, sha: data.sha };
}

/**
 * Commit an updated keywords config back to the repo.
 * @param sha - The blob SHA obtained from the last fetch (prevents conflicts).
 * @param committerEmail - Used in the commit message for audit trail.
 */
export async function saveKeywordsToGitHub(
  token: string,
  config: unknown,
  sha: string,
  committerEmail?: string,
): Promise<void> {
  const url = `${API_BASE}/repos/${OWNER}/${REPO}/contents/${FILE_PATH}`;
  const pretty = JSON.stringify(config, null, 2) + "\n";
  const encoded = btoa(unescape(encodeURIComponent(pretty)));

  const who = committerEmail ? ` by ${committerEmail}` : "";
  const message = `chore: update keywords config from Settings UI${who}`;

  const res = await fetch(url, {
    method: "PUT",
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, content: encoded, sha }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = (body as Record<string, unknown>).message ?? res.statusText;
    throw new Error(`GitHub API ${res.status}: ${detail}`);
  }
}
