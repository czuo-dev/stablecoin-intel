import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { useAuth } from "@/contexts/AuthContext";
import NotFound from "@/pages/NotFound";
import { Route, Router as WouterRouter, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { AuthProvider } from "./contexts/AuthContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import ReportList from "./pages/ReportList";
import ReportDetail from "./pages/ReportDetail";
import DeepAnalysis from "./pages/DeepAnalysis";
import ThreatRadar from "./pages/ThreatRadar";
import MarketTrends from "./pages/MarketTrends";
import Settings from "./pages/Settings";
import Login from "./pages/Login";
import { Loader2 } from "lucide-react";

// BASE_URL from Vite: "/" in dev, "/stablecoin-intel/" when deployed to GitHub Pages
const base = import.meta.env.BASE_URL;

function Router() {
  return (
    <WouterRouter base={base}>
    <Switch>
      <Route path="/" component={ReportList} />
      <Route path="/report/:id" component={ReportDetail} />
      <Route path="/analysis" component={DeepAnalysis} />
      <Route path="/threats" component={ThreatRadar} />
      <Route path="/trends" component={MarketTrends} />
      <Route path="/settings" component={Settings} />
      <Route path="/404" component={NotFound} />
      {/* Final fallback route */}
      <Route component={NotFound} />
    </Switch>
    </WouterRouter>
  );
}

function AuthGate({ children }: { children: React.ReactNode }) {
  const { isFirebaseConfigured, loading, allowed } = useAuth();
  if (!isFirebaseConfigured) return <>{children}</>;
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }
  if (!allowed) return <Login />;
  return <>{children}</>;
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="light"
        // switchable
      >
        <AuthProvider>
          <TooltipProvider>
            <Toaster />
            <AuthGate>
              <Router />
            </AuthGate>
          </TooltipProvider>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
