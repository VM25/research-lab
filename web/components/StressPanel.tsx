"use client";

import { useState } from "react";
import { SignalCase, BacktestSummary } from "@/lib/data";
import { pct, pctSigned, num } from "@/lib/format";
import LineChart, { Series } from "./charts/LineChart";
import BarChart, { Bar } from "./charts/BarChart";
import Classification from "./Classification";
import SectionHead from "./SectionHead";

const COST_KEYS = ["low", "base", "high", "stress"] as const;

export default function StressPanel({ c, backtest }: { c: SignalCase; backtest: BacktestSummary }) {
  const [costKey, setCostKey] = useState<(typeof COST_KEYS)[number]>("base");
  const curves = backtest.curves;
  const fam = curves.strategies[c.signal_family];
  const st = c.stress_test_summary;

  const costRows = [...st.cost_sensitivity].sort((a, b) => a.cost_bps - b.cost_bps);
  const sel = costRows.find((r) => r.scenario === costKey) ?? costRows[1];

  const costSeries: Series[] = [
    { name: "Gross", values: fam.gross, color: "var(--ink-3)", dash: "2 3", width: 1.4 },
    { name: `Net @ ${sel.cost_bps} bps`, values: fam.net_by_cost[costKey], color: "var(--accent)", width: 2.3, label: true, area: true },
  ];

  const costBars: Bar[] = costRows.map((r) => ({
    label: `${r.cost_bps} bps`, value: r.net_sharpe, highlight: r.scenario === costKey,
  }));
  const paramBars: Bar[] = st.parameter_robustness.map((p) => ({ label: p.parameter_set, value: p.sharpe }));
  const rebalBars: Bar[] = st.rebalance_sensitivity.map((r) => ({
    label: r.rebalance_frequency.slice(0, 1).toUpperCase() + r.rebalance_frequency.slice(1, 3),
    value: r.net_sharpe, highlight: r.rebalance_frequency === "monthly",
  }));
  const regimeBars: Bar[] = st.regimes.map((r) => ({ label: shortRegime(r.regime_name), value: r.sharpe }));
  const crisisBars: Bar[] = st.crisis.map((cr) => ({ label: shortCrisis(cr.crisis_period), value: cr.cumulative_return }));

  const stableParams = st.parameter_robustness.filter((p) => p.sharpe > 0.1).length;
  const worst = [...st.regimes].sort((a, b) => a.sharpe - b.sharpe)[0];
  const best = [...st.regimes].sort((a, b) => b.sharpe - a.sharpe)[0];
  const worstCrisis = [...st.crisis].sort((a, b) => a.cumulative_return - b.cumulative_return)[0];
  const baseLabel = costRows.find((r) => r.scenario === "base")!.classification_at_cost_level;
  const changed = sel.classification_at_cost_level !== baseLabel;

  return (
    <section className="block" id="stress">
      <div className="frame">
        <SectionHead index="04" kicker="Validation review"
          title="Response to moving assumptions"
          lede="Each module re-runs the signal under a different perturbation — cost, parameter, rebalance frequency, market regime, and crisis window — to test whether the result holds when the assumptions move." />

        <div className="s-body">
          {/* COST */}
          <div className="stress-lead">
            <div className="sheet-head">
              <div>
                <div className="sheet-title">Cost sensitivity</div>
                <div className="sheet-q">Do transaction costs erode the edge as execution gets more expensive?</div>
              </div>
              <div className="ctrl-field">
                <span className="ctrl-label">Cost per unit turnover</span>
                <div className="ctrl">
                  {costRows.map((r) => (
                    <button key={r.scenario} aria-pressed={r.scenario === costKey}
                            onClick={() => setCostKey(r.scenario as (typeof COST_KEYS)[number])}>{r.cost_bps} bps</button>
                  ))}
                </div>
              </div>
            </div>
            <div className="stress-cost-grid">
              <div>
                <div className="legend" style={{ marginBottom: 12 }}>
                  <span><i style={{ borderColor: "var(--ink)" }} />Net @ {sel.cost_bps} bps</span>
                  <span><i style={{ borderColor: "var(--ink-3)", borderTopStyle: "dotted" }} />Gross</span>
                </div>
                <LineChart dates={curves.dates} series={costSeries} height={240}
                           yFormat={(v) => v.toFixed(0)} ariaLabel="Net index at selected cost versus gross" />
              </div>
              <div className="cost-readout">
                <div className="metrics">
                  <Row k={`Net CAGR @ ${sel.cost_bps} bps`} v={pct(sel.net_cagr)} />
                  <Row k="Net Sharpe" v={num(sel.net_sharpe)} />
                  <Row k="Cost drag / yr" v={pct(sel.cost_drag, 2)} />
                </div>
                <div className="cost-verdict">
                  <span className="label">Cost test · this scenario only</span>
                  <div className="cv-line">{sel.classification_at_cost_level} — {changed ? "weaker than baseline" : "unchanged vs baseline"}</div>
                  <div className="cv-final">Final classification: <b>{c.verdict}</b> — determined by the full evidence (turnover and benchmark-relative result), not cost level alone.</div>
                </div>
              </div>
            </div>
            <div className="sheet-pad" style={{ paddingTop: 8 }}>
              <BarChart bars={costBars} height={200} yFormat={(v) => v.toFixed(2)} ariaLabel="Net Sharpe across cost levels" />
              <div className="finding">
                <span className="finding-tag">Result</span>
                <span className="finding-text">From 1 → 25 bps, net Sharpe moves <b>{num(costRows[0].net_sharpe)}</b> → <b>{num(costRows[costRows.length - 1].net_sharpe)}</b> and cost drag rises to <b>{pct(costRows[costRows.length - 1].cost_drag, 2)}</b>/yr. {sel.net_sharpe < 0.2 ? "At the stress level the edge is largely gone." : "It still clears costs at the stress level."}</span>
              </div>
            </div>
          </div>

          {/* MODULES */}
          <div className="stress-grid">
            <div className="stress-mod">
              <div className="mod-h"><span className="mod-title">Parameter robustness</span><span className="mod-q">one setting or many?</span></div>
              {paramBars.length
                ? <BarChart bars={paramBars} height={190} yFormat={(v) => v.toFixed(2)} ariaLabel="Sharpe across parameter sets" />
                : <p className="empty-note">The ensemble has no single tunable parameter; robustness comes from blending four signals.</p>}
              <div className="mod-result">RESULT — {paramBars.length ? `${stableParams} of ${paramBars.length} parameter settings remain economically useful; ${stableParams >= Math.ceil(paramBars.length * 0.6) ? "the result is not a one-setting artefact." : "the result is parameter-sensitive."}` : "robustness derives from diversification across signals."}</div>
            </div>

            <div className="stress-mod">
              <div className="mod-h"><span className="mod-title">Rebalance frequency</span><span className="mod-q">timing-dependent?</span></div>
              <BarChart bars={rebalBars} height={190} yFormat={(v) => v.toFixed(2)} ariaLabel="Sharpe across rebalance frequencies" />
              <div className="mod-result">RESULT — {rebalDelta(st)}</div>
            </div>

            <div className="stress-mod">
              <div className="mod-h"><span className="mod-title">Market regimes</span><span className="mod-q">where it helps / hurts</span></div>
              <BarChart bars={regimeBars} height={200} yFormat={(v) => v.toFixed(2)} ariaLabel="Sharpe by market regime" />
              <div className="mod-result">RESULT — strongest in {best?.regime_name} (Sharpe {num(best?.sharpe)}), weakest in {worst?.regime_name} (Sharpe {num(worst?.sharpe)}); {Math.abs((best?.sharpe ?? 0) - (worst?.sharpe ?? 0)) > 0.8 ? "behaviour is regime-dependent." : "behaviour is fairly steady across regimes."}</div>
            </div>

            <div className="stress-mod">
              <div className="mod-h"><span className="mod-title">Crisis windows</span><span className="mod-q">behaviour under stress</span></div>
              <BarChart bars={crisisBars} height={200} yFormat={(v) => `${(v * 100).toFixed(0)}%`} ariaLabel="Cumulative return across crisis windows" />
              <div className="mod-result">RESULT — worst window {worstCrisis?.crisis_period}: {pctSigned(worstCrisis?.cumulative_return)} cumulative ({pctSigned(worstCrisis?.benchmark_relative_return)} relative to SPY).</div>
            </div>
          </div>

          <div className="stress-summary">
            <Classification verdict={c.verdict} size="md" />
            <p className="ss-note">{c.verdict_reason}</p>
          </div>
        </div>
      </div>
    </section>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return <div className="metric-row"><span className="metric-key">{k}</span><span className="metric-val">{v}</span></div>;
}

function rebalDelta(st: SignalCase["stress_test_summary"]) {
  const m = st.rebalance_sensitivity.find((r) => r.rebalance_frequency === "monthly");
  const w = st.rebalance_sensitivity.find((r) => r.rebalance_frequency === "weekly");
  if (!m || !w) return "monthly is the reported setting.";
  const spread = Math.abs(m.net_sharpe - w.net_sharpe);
  return `weekly turnover (${num(w.annual_turnover, 1)}×) against monthly (${num(m.annual_turnover, 1)}×); net Sharpe ${spread > 0.2 ? "shifts materially" : "is stable"} across frequencies (${num(w.net_sharpe)} → ${num(m.net_sharpe)}).`;
}
function shortRegime(r: string) {
  return ({ "High Volatility": "High Vol", "Inflation Stress": "Inflation", "Rate Shock": "Rate Shock", "Risk-On": "Risk-On", "Risk-Off": "Risk-Off", Normal: "Normal" } as Record<string, string>)[r] ?? r;
}
function shortCrisis(c: string) {
  return ({ "Global Financial Crisis": "GFC '08", "Eurozone / US Downgrade Stress": "Euro '11", "COVID Crash": "COVID '20", "Inflation / Rate Shock": "Rates '22", "Higher-Rate Regime": "High-Rate '23+" } as Record<string, string>)[c] ?? c;
}
