"use client";

import { useState } from "react";
import { DataSummary, Overview } from "@/lib/data";
import SectionHead from "./SectionHead";

export default function Methodology({ data }: { data: DataSummary; overview: Overview }) {
  const [open, setOpen] = useState(false);

  return (
    <section className="block" id="methodology">
      <div className="frame">
        <SectionHead index="06" kicker="Methodology · Audit trail"
          title="Data, construction, and validation record"
          lede={`${data.source_summary} Every figure on this page is produced by the Python research engine and read from generated JSON — none is entered by hand.`} />

        <div className="s-body">
          <div className="method-grid">
            <div className="method-cell">
              <span className="label">Data &amp; universe</span>
              <ul>
                <li><b>{data.universe.length}</b> liquid ETFs · {data.asset_groups.length} asset groups</li>
                <li>Price panel {data.sample_period.start} → {data.sample_period.end}</li>
                <li>Backtest calendar from {data.backtest_period.start}</li>
                <li>Returns: {data.return_basis}</li>
                <li>Sources: {data.sources.join(", ")}</li>
              </ul>
            </div>
            <div className="method-cell">
              <span className="label">No-lookahead &amp; cash proxy</span>
              <p className="method-body">{data.no_lookahead_rule}</p>
              <p className="method-body" style={{ marginTop: 12 }}>{data.cash_handling}</p>
            </div>
            <div className="method-cell">
              <span className="label">Cost model &amp; turnover</span>
              <p className="method-body">{data.cost_model.description}</p>
              <p className="method-body" style={{ marginTop: 10 }}>{data.cost_model.turnover_definition}</p>
              <p className="method-body mono" style={{ marginTop: 12, color: "var(--ink-3)", fontSize: 12.5 }}>
                {data.cost_model.scenarios.map((s) => `${s.cost_bps}`).join(" / ")} bps · primary {data.cost_model.primary_cost_bps} bps
              </p>
            </div>
            <div className="method-cell">
              <span className="label">Validation protocol</span>
              <ul>
                <li>Train {data.train_test_split.train}</li>
                <li>Test {data.train_test_split.test}</li>
                <li>{data.walk_forward_windows} expanding walk-forward windows</li>
                <li>Cost · parameter · rebalance · regime · crisis</li>
              </ul>
              <p className="method-body" style={{ marginTop: 10, fontSize: 12.5 }}>{data.regime_note}</p>
            </div>
          </div>

          <button className="method-toggle" aria-expanded={open} onClick={() => setOpen(!open)}>
            {open ? "Hide" : "Inspect"} ETF universe &amp; limitations <span style={{ color: "var(--ink-3)" }}>{open ? "−" : "+"}</span>
          </button>

          {open && (
            <div className="method-detail">
              <div className="method-detail-grid">
                <div>
                  <span className="label" style={{ display: "block", marginBottom: 12 }}>Universe — {data.universe.length} ETFs, all included</span>
                  <table className="uni-table">
                    <thead><tr><th>Ticker</th><th>Asset</th><th>Group</th><th>First</th><th>Last</th><th>Source</th></tr></thead>
                    <tbody>
                      {data.universe.map((a) => (
                        <tr key={a.ticker}>
                          <td className="mono">{a.ticker}</td>
                          <td>{a.name}</td>
                          <td className="muted" style={{ textTransform: "capitalize" }}>{a.group.replace(/_/g, " ")}</td>
                          <td className="mono">{a.first_date.slice(0, 7)}</td>
                          <td className="mono">{a.last_date.slice(0, 7)}</td>
                          <td className="muted">{a.source}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <p className="uni-note">{data.sample_period.note}</p>
                </div>
                <div>
                  <span className="label" style={{ display: "block", marginBottom: 12 }}>Benchmarks</span>
                  <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
                    {data.benchmarks.map((b) => (
                      <li key={b.key} style={{ padding: "7px 0", borderBottom: "1px solid var(--rule)", fontSize: 13.5, color: "var(--ink-2)" }}>{b.name}</li>
                    ))}
                  </ul>
                  <span className="label" style={{ display: "block", margin: "22px 0 12px" }}>Limitations</span>
                  <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
                    {data.limitations.map((l, i) => (
                      <li key={i} style={{ padding: "8px 0", borderBottom: "1px solid var(--rule)", fontSize: 12.5, color: "var(--ink-3)", lineHeight: 1.5 }}>{l}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
