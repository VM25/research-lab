"use client";

import { Overview } from "@/lib/data";

export default function SiteFooter({ overview, sources }: { overview: Overview; sources: string[] }) {
  return (
    <footer className="colophon">
      <div className="frame colo-grid">
        <div>
          <span className="kicker">Systematic Alpha Research Lab</span>
          <p className="colo-q">Does this signal survive reality?</p>
        </div>
        <div className="colo-meta">
          <p>{overview.data_note}</p>
          <p className="colo-discl">
            RESEARCH AND EDUCATIONAL PROJECT — <b>NOT INVESTMENT ADVICE</b> AND NOT A LIVE TRADING SYSTEM.<br />
            Built on real market data ({sources.join(", ")}). Results are historical and do not guarantee future performance.
          </p>
        </div>
      </div>
    </footer>
  );
}
