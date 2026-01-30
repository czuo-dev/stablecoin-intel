import { NewsItem } from "@/lib/mock-data";
import ThreatBadge from "./ThreatBadge";
import { ExternalLink, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";

interface NewsCardProps {
  item: NewsItem;
}

export default function NewsCard({ item }: NewsCardProps) {
  return (
    <Card className="group hover:shadow-md transition-all duration-300 border-border/50 bg-card/50 backdrop-blur-sm">
      <CardHeader className="pb-3 pt-5 px-5">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 mb-2">
              <ThreatBadge level={item.threatLevel} />
              <span className="text-xs text-muted-foreground font-mono px-1.5 py-0.5 rounded bg-muted/50">
                {item.source}
              </span>
              <span className="text-xs text-muted-foreground">
                {item.date}
              </span>
            </div>
            <h3 className="text-lg font-semibold leading-tight group-hover:text-primary transition-colors">
              {item.title}
            </h3>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="px-5 pb-3">
        <p className="text-sm text-muted-foreground leading-relaxed mb-4">
          {item.summary}
        </p>
        
        {item.impact && item.impact.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {item.impact.map((tag, i) => (
              <span key={i} className="text-[10px] font-medium px-2 py-1 rounded bg-secondary text-secondary-foreground">
                {tag}
              </span>
            ))}
          </div>
        )}
        
        <div className="bg-muted/30 rounded-md p-3 text-xs border border-border/50">
          <span className="font-semibold text-primary block mb-1">Recommended Action:</span>
          {item.action}
        </div>
      </CardContent>
      
      <CardFooter className="px-5 py-3 border-t border-border/50 bg-muted/10 flex justify-between items-center">
        <div className="flex gap-2">
          {item.tickers?.map(ticker => (
            <span key={ticker} className="text-[10px] font-mono font-medium text-muted-foreground">
              ${ticker}
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" className="h-8 text-xs" asChild>
            <a href={item.url} target="_blank" rel="noopener noreferrer">
              Source <ExternalLink className="w-3 h-3 ml-1" />
            </a>
          </Button>
          <Button variant="outline" size="sm" className="h-8 text-xs">
            Analyze <ChevronRight className="w-3 h-3 ml-1" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
