import {
  onAuthStateChanged,
  signInWithPopup as firebaseSignInWithPopup,
  signOut as firebaseSignOut,
  type User,
} from "firebase/auth";
import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { getAuthInstance, googleProvider, isFirebaseConfigured } from "@/lib/firebase";

const ALLOWED_DOMAIN = "cobo.com";

interface AuthContextType {
  user: User | null;
  allowed: boolean;
  loading: boolean;
  error: string | null;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  isFirebaseConfigured: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [allowed, setAllowed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkDomain = useCallback((u: User | null): boolean => {
    if (!u?.email) return false;
    const domain = u.email.toLowerCase().trim().split("@")[1] || "";
    return domain === ALLOWED_DOMAIN;
  }, []);

  useEffect(() => {
    if (!isFirebaseConfigured) {
      setLoading(false);
      return;
    }
    const auth = getAuthInstance();
    if (!auth) {
      setLoading(false);
      return;
    }
    const unsubscribe = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setAllowed(checkDomain(u));
      setError(null);
      setLoading(false);
    });
    return () => unsubscribe();
  }, [checkDomain]);

  const signInWithGoogle = useCallback(async () => {
    setError(null);
    const auth = getAuthInstance();
    if (!auth) {
      setError("Auth not configured.");
      return;
    }
    try {
      const result = await firebaseSignInWithPopup(auth, googleProvider);
      const u = result.user;
      if (!checkDomain(u)) {
        await firebaseSignOut(auth);
        setError("仅限 cobo.com 企业邮箱登录。");
      }
    } catch (err: unknown) {
      const msg = err && typeof err === "object" && "message" in err ? String((err as { message: string }).message) : "登录失败";
      setError(msg);
    }
  }, [checkDomain]);

  const signOut = useCallback(async () => {
    setError(null);
    const auth = getAuthInstance();
    if (auth) await firebaseSignOut(auth);
  }, []);

  const value: AuthContextType = {
    user,
    allowed,
    loading,
    error,
    signInWithGoogle,
    signOut,
    isFirebaseConfigured,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (ctx === undefined) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
