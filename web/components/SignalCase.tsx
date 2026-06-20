"use client";

import { SignalCase as Case } from "@/lib/data";
import { pct, num } from "@/lib/format";
import Classification from "./Classification";
import SectionHead from "./SectionHead";

export default function SignalCase({ c }: { c: Case }) {
  const m = c.key_metrics;
  return (
    <section className="block" id="signal-case">
      <div className="frame">
        <SectionHead index="02" kicker="Research file"
          title={c.signal_name}
          lede={c.plain_english_hypothesis} />

        <div className="s-body">
          <div className="case-head">
            <div className="case-head-l">
              <Classification verdict={c.verdict} size="md" />
              <span className="case-meta" style={{ marginTop: 0 }}>
                <span><b>{pct(m.cagr)}</b> CAGR net</span>
                <span><b>{num(m.sharpe)}</b> Sharpe</span>
                <span><b>{pct(m.max_drawdown, 0)}</b> max drawdown</span>
                <span><b>{num(m.annualized_turnover, 1)}×</b> turnover/yr</span>
              </span>
            </div>
          </div>

          <div className="case-grid">
            <div className="case-main">
              <div className="case-sec">
                <div className="case-sec-h"><span className="label">Signal thesis</span></div>
                <p className="case-prose">{c.hypothesis}</p>
              </div>

              <div className="case-sec">
                <div className="case-sec-h"><span className="label">Definition</span></div>
                <p className="case-prose" style={{ marginBottom: 14 }}>{c.formula_short}</p>
                <code className="formula">{c.formula}</code>
                <div className="case-meta">
                  <span>Lookback&nbsp; <b>{c.lookback_window}</b></span>
                  <span>Rebalance&nbsp; <b>{c.rebalance_frequency}</b></span>
                </div>
              </div>

              <div className="case-sec">
                <div className="case-sec-h"><span className="label">Portfolio construction</span></div>
                <p className="case-prose">{c.portfolio_rule}</p>
                <div className="case-meta">
                  <span>Weighting&nbsp; <b>{c.weighting_method.replace(/_/g, " ")}</b></span>
                  <span>Constraints&nbsp; <b>long-only · no leverage · cash fallback</b></span>
                </div>
              </div>

              <div className="case-sec">
                <div className="case-cols">
                  <div>
                    <div className="case-sec-h"><span className="label">Conditions for success</span></div>
                    <ol className="case-list">{c.expected_strength.map((s, i) => <li key={i}>{s}</li>)}</ol>
                  </div>
                  <div>
                    <div className="case-sec-h"><span className="label">Failure conditions</span></div>
                    <ol className="case-list">{c.expected_weakness.map((s, i) => <li key={i}>{s}</li>)}</ol>
                  </div>
                </div>
              </div>
            </div>

            <aside className="case-aside">
              <div className="record-h">
                <span className="label">Research classification</span>
                <Classification verdict={c.verdict} />
              </div>
              <p className="record-note">{c.verdict_reason}</p>

              <div className="record-block">
                <span className="label">Best use</span>
                <p className="defval">{c.best_use_case}</p>
              </div>
              <div className="record-block">
                <span className="label">Recorded weaknesses</span>
                <ul style={{ margin: "8px 0 0", padding: 0, listStyle: "none" }}>
                  {c.weaknesses.map((w, i) => (
                    <li key={i} className="defval" style={{ padding: "6px 0", borderBottom: "1px solid var(--rule)", fontSize: 13.5 }}>{w}</li>
                  ))}
                </ul>
              </div>
              <p className="kicker" style={{ marginTop: 22, color: "var(--ink-4)" }}>Evidence and validation follow below ↓</p>
            </aside>
          </div>
        </div>
      </div>
    </section>
  );
}
