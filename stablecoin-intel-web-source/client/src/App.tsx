import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import ReportList from "./pages/ReportList";
import ReportDetail from "./pages/ReportDetail";
import DeepAnalysis from "./pages/DeepAnalysis";
import ThreatRadar from "./pages/ThreatRadar";
import MarketTrends from "./pages/MarketTrends";
import Settings from "./pages/Settings";


function Router() {
  return (
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
  );
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
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
