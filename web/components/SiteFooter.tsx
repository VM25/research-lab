"use client";

import { Overview } from "@/lib/data";

export default function SiteFooter({ overview, sources }: { overview: Overview; sources: string[] }) {
  return (
    <footer className="site-footer">
      <div className="wrap footer-inner">
        <div className="footer-q">
          <span className="eyebrow">{overview.project_name}</span>
          <p className="footer-tag">Does this signal survive reality?</p>
        </div>
        <div className="footer-meta">
          <p>{overview.data_note}</p>
          <p className="footer-disc">
            Research and educational project — <strong>not investment advice</strong> and not a live trading system.
            Built on real market data ({sources.join(", ")}); results are historical and do not guarantee future performance.
          </p>
        </div>
      </div>
    </footer>
  );
}
