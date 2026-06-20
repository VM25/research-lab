"use client";

import { Overview, ClassificationBoard, Verdict } from "@/lib/data";
import { clsClass } from "@/lib/format";

const VERDICTS: Verdict[] = ["Survived", "Conditional", "Rejected"];

export default function Hero({ overview, board }: {
  overview: Overview; board: ClassificationBoard; onJump?: (f: string) => void;
}) {
  const u = overview.universe_summary;
  const years = Math.round(
    (new Date(u.sample_end).getTime() - new Date(u.sample_start).getTime()) / 3.15576e10
  );
  const toBoard = () =>
    document.getElementById("verdict-board")?.scrollIntoView({ behavior: "smooth" });

  return (
    <header className="masthead">
      <div className="frame">
        <div className="mast-bar">
          <span className="mast-id"><b>Systematic Alpha Research Lab</b> &nbsp;·&nbsp; Signal Validation Report</span>
          <span className="mast-status">Research only · Not investment advice</span>
        </div>

        <div className="mast-grid">
          <div>
            <span className="kicker">Research question</span>
            <h1 className="mast-question">Does this signal<br />survive reality?</h1>
            <p className="mast-mandate">{overview.headline} Each signal is treated as a research case and carried through a fixed validation sequence — thesis, cost-aware evidence, out-of-sample and walk-forward testing, robustness, and a documented classification.</p>
            <p className="mast-discl">RESEARCH ONLY · NOT INVESTMENT ADVICE · NOT A LIVE TRADING SYSTEM</p>
          </div>

          <div>
            <div className="mast-meta">
              <Row k="Universe" v={`${u.asset_count} liquid ETFs · ${u.asset_groups} asset groups`} />
              <Row k="Price sample" v={`${u.sample_start} – ${u.sample_end} · ${years} yrs`} mono />
              <Row k="Backtest" v={`${overview.backtest_start ?? u.sample_start} – ${u.sample_end}`} mono />
              <Row k="Return basis" v="Dividend- & split-adjusted close" />
              <Row k="Cost basis" v={`${overview.primary_cost_bps} bps per unit turnover (primary)`} mono />
              <Row k="Signals tested" v={`${overview.signal_count}`} mono />
            </div>

            <div className="docket-mini">
              <table className="ledger" style={{ marginTop: 18 }}>
                <thead>
                  <tr><th>Classification</th><th style={{ textAlign: "right" }}>Count</th></tr>
                </thead>
                <tbody>
                  {VERDICTS.map((v) => (
                    <tr key={v} onClick={toBoard} style={{ cursor: "pointer" }}>
                      <td>
                        <span className={`cls ${clsClass(v)}`}>
                          <span className="cls-mark" aria-hidden="true" />
                          <span className="cls-name">{v}</span>
                        </span>
                      </td>
                      <td className="num">{overview.verdict_summary[v]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

function Row({ k, v, mono }: { k: string; v: string; mono?: boolean }) {
  return (
    <div className="mast-metarow">
      <span className="mast-metakey">{k}</span>
      <span className={`mast-metaval ${mono ? "mono" : ""}`}>{v}</span>
    </div>
  );
}
