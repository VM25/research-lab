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
          <span className="mast-status">Report SAL-01 &nbsp;·&nbsp; As of <b>{u.sample_end}</b></span>
        </div>

        <div className="mast-grid">
          <div>
            <span className="mast-eyebrow">Research mandate</span>
            <h1 className="mast-question">Does this signal survive reality?</h1>
            <p className="mast-mandate">{overview.headline} Each of {overview.signal_count} signals is treated as a research case and carried through one validation sequence.</p>

            <div className="mast-pipeline">
              <span className="mp-label">Validation sequence</span>
              <ol className="mp-steps">
                {["Thesis", "Cost-aware evidence", "Out-of-sample", "Walk-forward", "Robustness", "Classification"].map((s, i) => (
                  <li key={s}><span className="mp-n">{String(i + 1).padStart(2, "0")}</span>{s}</li>
                ))}
              </ol>
            </div>
          </div>

          <div>
            <div className="mast-meta">
              <Row k="Universe" v={`${u.asset_count} liquid ETFs · ${u.asset_groups} asset groups`} />
              <Row k="Price sample" v={`${u.sample_start} to ${u.sample_end}`} mono />
              <Row k="Backtest window" v={`${overview.backtest_start ?? u.sample_start} to ${u.sample_end}`} mono />
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
