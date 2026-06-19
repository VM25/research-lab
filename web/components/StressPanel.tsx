"use client";

import { useState } from "react";
import { SignalCase, BacktestSummary } from "@/lib/data";
import { pct, pctSigned, num, verdictClass, verdictGlyph } from "@/lib/format";
import LineChart, { Series } from "./charts/LineChart";
import BarChart, { Bar } from "./charts/BarChart";

const COST_KEYS = ["low", "base", "high", "stress"] as const;

export default function StressPanel({ c, backtest }: { c: SignalCase; backtest: BacktestSummary }) {
  const [costKey, setCostKey] = useState<(typeof COST_KEYS)[number]>("base");
  const curves = backtest.curves;
  const fam = curves.strategies[c.signal_family];
  const st = c.stress_test_summary;

  const costRows = [...st.cost_sensitivity].sort((a, b) => a.cost_bps - b.cost_bps);
  const sel = costRows.find((r) => r.scenario === costKey) ?? costRows[1];

  const costSeries: Series[] = [
    { name: "Gross", color: "var(--series-gross)", values: fam.gross, dashed: true, width: 1.6 },
    { name: `Net @ ${sel.cost_bps} bps`, color: "var(--series-net)", values: fam.net_by_cost[costKey], fill: true, width: 2.4 },
  ];

  const costBars: Bar[] = costRows.map((r) => ({
    label: `${r.cost_bps} bps`, value: r.net_sharpe,
    highlight: r.scenario === costKey, color: "var(--accent)",
    sub: r.classification_at_cost_level,
  }));

  const paramBars: Bar[] = st.parameter_robustness.map((p) => ({
    label: p.parameter_set, value: p.sharpe, color: "var(--accent-2)",
    sub: p.parameter_result,
  }));

  const rebalBars: Bar[] = st.rebalance_sensitivity.map((r) => ({
    label: r.rebalance_frequency.slice(0, 1).toUpperCase() + r.rebalance_frequency.slice(1, 3),
    value: r.net_sharpe, highlight: r.rebalance_frequency === "monthly", color: "var(--accent)",
  }));

  const regimeBars: Bar[] = st.regimes.map((r) => ({
    label: shortRegime(r.regime_name), value: r.sharpe,
    color: r.sharpe >= 0 ? "var(--survived)" : "var(--rejected)",
  }));

  const crisisBars: Bar[] = st.crisis.map((cr) => ({
    label: shortCrisis(cr.crisis_period), value: cr.cumulative_return,
    color: cr.cumulative_return >= 0 ? "var(--survived)" : "var(--rejected)",
  }));

  const stableParams = st.parameter_robustness.filter((p) => p.sharpe > 0.1).length;
  const worstRegime = [...st.regimes].sort((a, b) => a.sharpe - b.sharpe)[0];
  const bestRegime = [...st.regimes].sort((a, b) => b.sharpe - a.sharpe)[0];
  const worstCrisis = [...st.crisis].sort((a, b) => a.cumulative_return - b.cumulative_return)[0];

  // verdict-change indicator: does the cost-level label degrade?
  const baseLabel = costRows.find((r) => r.scenario === "base")!.classification_at_cost_level;
  const changed = sel.classification_at_cost_level !== baseLabel;

  return (
    <section className="section-pad" id="stress">
      <div className="wrap">
        <div className="section-intro">
          <span className="eyebrow">Step 04 · Stress the assumptions</span>
          <h2>What breaks it?</h2>
          <p>Push on costs, parameters, rebalance timing, market regimes, and crises. A signal only earns a verdict if it holds when the assumptions move.</p>
        </div>

        {/* COST STRESS */}
        <div className="panel chart-card stress-cost">
          <div className="chart-head">
            <div>
              <div className="chart-title">Cost sensitivity</div>
              <div className="chart-q">Do trading costs quietly eat the edge?</div>
            </div>
            <div className="control-group">
              <span className="ctrl-label mono">Cost per trade</span>
              <div className="btn-row">
                {costRows.map((r) => (
                  <button key={r.scenario} className="toggle" aria-pressed={r.scenario === costKey}
                          onClick={() => setCostKey(r.scenario as (typeof COST_KEYS)[number])}>{r.cost_bps} bps</button>
                ))}
              </div>
            </div>
          </div>

          <div className="stress-cost-grid">
            <div>
              <div className="legend">
                <span><i style={{ background: "var(--series-net)" }} />Net @ {sel.cost_bps} bps</span>
                <span><i style={{ background: "var(--series-gross)" }} />Gross</span>
              </div>
              <LineChart dates={curves.dates} series={costSeries} height={250}
                         yFormat={(v) => v.toFixed(0)} ariaLabel="Net growth at selected cost vs gross" />
            </div>
            <div className="cost-readout">
              <div className="metric"><span className="label">Net CAGR @ {sel.cost_bps} bps</span><span className="value">{pct(sel.net_cagr)}</span></div>
              <div className="metric"><span className="label">Net Sharpe</span><span className="value">{num(sel.net_sharpe)}</span></div>
              <div className="metric"><span className="label">Cost drag / yr</span><span className="value">{pct(sel.cost_drag, 2)}</span></div>
              <div className={`verdict-stability ${changed ? "warn" : "ok"}`}>
                <span className="vs-label mono">Cost test · this scenario only</span>
                <span className="vs-val">{sel.classification_at_cost_level}{changed ? " — weaker than baseline" : " — unchanged vs baseline"}</span>
                <span className="vs-final mono">Final signal verdict: <b>{c.verdict}</b> — set by the full evidence (turnover &amp; benchmark-relative), not cost alone.</span>
              </div>
            </div>
          </div>
          <BarChart bars={costBars} height={200} yFormat={(v) => v.toFixed(2)} ariaLabel="Net Sharpe across cost levels" />
          <div className="takeaway">
            <span className="tk-label">Takeaway</span>
            <span>From 1 → 25 bps, net Sharpe moves {num(costRows[0].net_sharpe)} → {num(costRows[costRows.length - 1].net_sharpe)} and cost drag rises to {pct(costRows[costRows.length - 1].cost_drag, 2)}/yr. {sel.net_sharpe < 0.2 ? "At stress costs the edge is largely gone." : "It still clears costs at the stress level."}</span>
          </div>
        </div>

        {/* PARAM + REBALANCE */}
        <div className="stress-two">
          <div className="panel chart-card">
            <div className="chart-head"><div><div className="chart-title">Parameter robustness</div><div className="chart-q">Does it work only on one lucky setting?</div></div></div>
            {paramBars.length ? <BarChart bars={paramBars} height={210} yFormat={(v) => v.toFixed(2)} ariaLabel="Sharpe across parameter sets" />
              : <p className="empty-note">The ensemble has no single tunable parameter — it averages the other signals.</p>}
            <div className="takeaway"><span className="tk-label">Takeaway</span>
              <span>{paramBars.length ? `${stableParams} of ${paramBars.length} parameter settings stay economically useful — ${stableParams >= Math.ceil(paramBars.length * 0.6) ? "not a one-setting fluke." : "the result is parameter-sensitive."}` : "Robustness comes from blending four independent signals rather than tuning one."}</span></div>
          </div>

          <div className="panel chart-card">
            <div className="chart-head"><div><div className="chart-title">Rebalance timing</div><div className="chart-q">Does the verdict depend on when you trade?</div></div></div>
            <BarChart bars={rebalBars} height={210} yFormat={(v) => v.toFixed(2)} ariaLabel="Sharpe across rebalance frequencies" />
            <div className="takeaway"><span className="tk-label">Takeaway</span>
              <span>{rebalDelta(st)}</span></div>
          </div>
        </div>

        {/* REGIME + CRISIS */}
        <div className="stress-two">
          <div className="panel chart-card">
            <div className="chart-head"><div><div className="chart-title">Market regimes</div><div className="chart-q">When does it help, and when does it hurt?</div></div></div>
            <BarChart bars={regimeBars} height={220} yFormat={(v) => v.toFixed(2)} ariaLabel="Sharpe by market regime" />
            <div className="takeaway"><span className="tk-label">Takeaway</span>
              <span>Strongest in {bestRegime?.regime_name} (Sharpe {num(bestRegime?.sharpe)}), weakest in {worstRegime?.regime_name} (Sharpe {num(worstRegime?.sharpe)}) — {Math.abs((bestRegime?.sharpe ?? 0) - (worstRegime?.sharpe ?? 0)) > 0.8 ? "performance is regime-dependent." : "behaviour is fairly steady across regimes."}</span></div>
          </div>

          <div className="panel chart-card">
            <div className="chart-head"><div><div className="chart-title">Crisis windows</div><div className="chart-q">How did it behave when markets broke?</div></div></div>
            <BarChart bars={crisisBars} height={220} yFormat={(v) => `${(v * 100).toFixed(0)}%`} ariaLabel="Cumulative return across crisis windows" />
            <div className="takeaway"><span className="tk-label">Takeaway</span>
              <span>Worst crisis was {worstCrisis?.crisis_period}: {pctSigned(worstCrisis?.cumulative_return)} cumulative ({pctSigned(worstCrisis?.benchmark_relative_return)} vs SPY).</span></div>
          </div>
        </div>

        {/* VERDICT TRANSITION */}
        <div className={`panel verdict-transition ${verdictClass(c.verdict)}`}>
          <div className="vt-left">
            <span className="vt-label mono">After all stress tests</span>
            <div className="vt-verdict">
              <span className={`verdict-chip ${verdictClass(c.verdict)}`}><span className="v-glyph">{verdictGlyph(c.verdict)}</span> {c.verdict}</span>
            </div>
          </div>
          <p className="vt-note">{c.verdict_reason}</p>
        </div>
      </div>
    </section>
  );
}

function rebalDelta(st: SignalCase["stress_test_summary"]) {
  const m = st.rebalance_sensitivity.find((r) => r.rebalance_frequency === "monthly");
  const w = st.rebalance_sensitivity.find((r) => r.rebalance_frequency === "weekly");
  if (!m || !w) return "Monthly is the reported setting.";
  const spread = Math.abs(m.net_sharpe - w.net_sharpe);
  return `Weekly turnover (${num(w.annual_turnover, 1)}×) vs monthly (${num(m.annual_turnover, 1)}×); net Sharpe ${spread > 0.2 ? "shifts materially" : "is stable"} across frequencies (${num(w.net_sharpe)} → ${num(m.net_sharpe)}).`;
}

function shortRegime(r: string) {
  return ({ "High Volatility": "High Vol", "Inflation Stress": "Inflation", "Rate Shock": "Rate Shock", "Risk-On": "Risk-On", "Risk-Off": "Risk-Off", Normal: "Normal" } as Record<string, string>)[r] ?? r;
}
function shortCrisis(c: string) {
  return ({ "Global Financial Crisis": "GFC '08", "Eurozone / US Downgrade Stress": "Euro '11", "COVID Crash": "COVID '20", "Inflation / Rate Shock": "Rates '22", "Higher-Rate Regime": "High-Rate '23+" } as Record<string, string>)[c] ?? c;
}
