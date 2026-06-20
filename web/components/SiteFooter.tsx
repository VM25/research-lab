"use client";

import { Overview } from "@/lib/data";

export default function SiteFooter({ overview, sources }: { overview: Overview; sources: string[] }) {
  const u = overview.universe_summary;
  return (
    <footer className="colophon">
      <div className="frame">
        <div className="colo-close">
          <span className="colo-rule" aria-hidden="true" />
          <span className="colo-end">End of validation record</span>
          <span className="colo-rule" aria-hidden="true" />
        </div>
        <div className="colo-grid">
          <div>
            <span className="kicker">Systematic Alpha Research Lab · Report SAL-01</span>
            <p className="colo-q">Does this signal survive reality?</p>
            <p className="colo-summary">
              {overview.signal_count} signals across {u.asset_count} ETFs, {u.sample_start.slice(0, 4)} to {u.sample_end.slice(0, 4)}, classified Survived / Conditional / Rejected
            </p>
          </div>
          <div className="colo-meta">
            <p>{overview.data_note}</p>
            <p className="colo-discl">
              Research and educational project. <b>Not investment advice</b> and not a live trading system.
              Built on real market data ({sources.join(", ")}). Results are historical and do not guarantee future performance.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
