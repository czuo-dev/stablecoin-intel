import { cn } from "@/lib/utils";

type ThreatLevel = 'high' | 'medium' | 'low' | 'neutral';

interface ThreatBadgeProps {
  level: ThreatLevel;
  className?: string;
}

export default function ThreatBadge({ level, className }: ThreatBadgeProps) {
  const styles = {
    high: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-800",
    medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200 dark:border-amber-800",
    low: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800",
    neutral: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400 border-slate-200 dark:border-slate-700",
  };

  const labels = {
    high: "High Threat",
    medium: "Medium Threat",
    low: "Low Threat",
    neutral: "Neutral",
  };

  return (
    <span className={cn(
      "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
      styles[level],
      className
    )}>
      <span className={cn(
        "w-1.5 h-1.5 rounded-full mr-1.5",
        level === 'high' && "bg-red-500",
        level === 'medium' && "bg-amber-500",
        level === 'low' && "bg-emerald-500",
        level === 'neutral' && "bg-slate-500"
      )} />
      {labels[level]}
    </span>
  );
}
