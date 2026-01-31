import { Link, useLocation } from "wouter";
import {
  LayoutDashboard,
  Settings,
  ShieldAlert,
  TrendingUp,
  Menu,
  X,
  Search,
  PieChart,
  LogOut,
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";

export default function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { user, isFirebaseConfigured, signOut } = useAuth();

  const navItems = [
    { href: "/", label: "Intelligence Center", icon: LayoutDashboard },
    { href: "/analysis", label: "Deep Analysis", icon: PieChart },
    { href: "/threats", label: "Threat Radar", icon: ShieldAlert },
    { href: "/trends", label: "Market Trends", icon: TrendingUp },
    { href: "/settings", label: "Settings", icon: Settings },
  ];

  return (
    <div className="min-h-screen lg:h-screen bg-background flex">
      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar - min-h-screen so it fills viewport height on desktop */}
      <aside 
        className={cn(
          "fixed top-0 left-0 z-50 h-full min-h-screen w-64 bg-sidebar text-sidebar-foreground border-r border-sidebar-border transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:min-h-screen flex flex-col",
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo Section */}
        <div className="h-16 flex items-center px-6 border-b border-sidebar-border/50 bg-sidebar">
          <div className="flex items-center gap-3 font-bold text-lg tracking-tight">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground shadow-sm">
              S
            </div>
            <span>Stablecoin Intel</span>
          </div>
          <button 
            className="ml-auto lg:hidden text-sidebar-foreground/70 hover:text-sidebar-foreground"
            onClick={() => setIsSidebarOpen(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search & Nav Section */}
        <div className="flex-1 overflow-y-auto py-6 px-4 space-y-6">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground pointer-events-none" />
            <Input 
              placeholder="Search intel..." 
              className="pl-9 bg-sidebar-accent/50 border-sidebar-border/50 text-sm h-9 focus-visible:ring-1 focus-visible:ring-sidebar-ring"
            />
          </div>

          <nav className="space-y-1">
            {navItems.map((item) => {
              const isActive = location === item.href || (item.href !== "/" && location.startsWith(item.href));
              return (
                <Link key={item.href} href={item.href}>
                  <a className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200 group",
                    isActive 
                      ? "bg-sidebar-primary text-sidebar-primary-foreground shadow-sm" 
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                  )}>
                    <item.icon className={cn(
                      "w-4 h-4 transition-colors",
                      isActive ? "text-sidebar-primary-foreground" : "text-muted-foreground group-hover:text-sidebar-accent-foreground"
                    )} />
                    {item.label}
                  </a>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User Profile Section */}
        <div className="p-4 border-t border-sidebar-border/50 bg-sidebar/50">
          {isFirebaseConfigured && user ? (
            <div className="flex items-center gap-3 px-2 py-2 rounded-lg">
              <div className="w-8 h-8 rounded-full bg-sidebar-accent flex items-center justify-center text-xs font-bold border border-sidebar-border overflow-hidden">
                {user.photoURL ? (
                  <img src={user.photoURL} alt="" className="w-full h-full object-cover" />
                ) : (
                  (user.email?.[0] ?? "U").toUpperCase()
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user.displayName || "User"}</p>
                <p className="text-xs text-muted-foreground truncate">{user.email}</p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => signOut()} title="退出登录">
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-3 px-2 py-2 rounded-lg">
              <div className="w-8 h-8 rounded-full bg-sidebar-accent flex items-center justify-center text-xs font-bold border border-sidebar-border">
                —
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">Guest</p>
                <p className="text-xs text-muted-foreground truncate">未配置登录时可见</p>
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 bg-background/50">
        {/* Mobile Header */}
        <header className="lg:hidden h-16 border-b border-border bg-background flex items-center px-4 sticky top-0 z-30">
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => setIsSidebarOpen(true)}
            className="-ml-2"
          >
            <Menu className="w-5 h-5" />
          </Button>
          <span className="ml-2 font-semibold">Stablecoin Intel</span>
        </header>

        <main className="flex-1 overflow-y-auto p-4 lg:p-8 scroll-smooth">
          <div className="max-w-7xl mx-auto w-full animate-in fade-in duration-500">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
