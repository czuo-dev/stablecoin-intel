/**
 * Firebase App and Auth initialization.
 * Only initializes when VITE_FIREBASE_* env vars are set (e.g. in production / GitHub Pages).
 */
import { getApps, initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, type Auth } from "firebase/auth";

const config = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

export const isFirebaseConfigured =
  typeof config.apiKey === "string" &&
  config.apiKey.length > 0 &&
  typeof config.authDomain === "string" &&
  typeof config.projectId === "string";

let authInstance: Auth | null = null;

export function getAuthInstance(): Auth | null {
  if (!isFirebaseConfigured) return null;
  if (authInstance) return authInstance;
  const apps = getApps();
  const app = apps.length > 0 ? apps[0] : initializeApp(config);
  authInstance = getAuth(app);
  return authInstance;
}

export const googleProvider = new GoogleAuthProvider();
