"use client";

import { useMemo, useState } from "react";
import { SignalCase, BacktestSummary } from "@/lib/data";
import { pct, pctSigned, num } from "@/lib/format";
import LineChart, { Series } from "./charts/LineChart";

const BENCH_ORDER = ["spy_buy_hold", "sixty_forty", "equal_weight_universe", "cash_proxy", "inverse_volatility"];

export default function EvidencePanel({ c, backtest }: { c: SignalCase; backtest: BacktestSummary }) {
  const [mode, setMode] = useState<"net" | "gross">("net");
  const [bench, setBench] = useState("spy_buy_hold");

  const curves = backtest.curves;
  const fam = curves.strategies[c.signal_family];
  const km = c.key_metrics;
  const baseCost = c.stress_test_summary.cost_sensitivity.find((r) => r.scenario === "base");
  const grossCagr = baseCost?.gross_cagr ?? km.gross_cagr;
  const grossSharpe = baseCost?.gross_sharpe ?? km.sharpe;
  const cmp = c.benchmark_comparison.find((b) => b.benchmark_key === bench);

  const equitySeries: Series[] = useMemo(() => {
    const stratVals = mode === "net" ? fam.net : fam.gross;
    return [
      { name: c.signal_name, color: "var(--series-net)", values: stratVals, fill: true, width: 2.4 },
      { name: backtest.benchmark_labels[bench], color: "var(--series-bench)", values: curves.benchmarks[bench], width: 1.8 },
    ];
  }, [mode, bench, fam, curves, c.signal_name, backtest.benchmark_labels]);

  const ddSeries: Series[] = [
    { name: "Drawdown", color: "var(--rejected)", values: fam.drawdown, fill: true, width: 1.8 },
  ];

  return (
    <section className="section-pad" id="evidence">
      <div className="wrap">
        <div className="section-intro">
          <span className="eyebrow">Step 03 · Inspect the evidence</span>
          <h2>What happened, before and after costs</h2>
          <p>Growth of $100 over the backtest sample (from {backtest.common_start}). Toggle gross vs net of {backtest.base_cost_bps} bps costs, and compare against any benchmark — every change updates the takeaway.</p>
        </div>

        <div className="panel chart-card evidence-main">
          <div className="chart-head">
            <div>
              <div className="chart-title">{c.signal_name} vs {backtest.benchmark_labels[bench]}</div>
              <div className="chart-q">Did the signal create value after real-world costs?</div>
            </div>
            <div className="evidence-controls">
              <div className="control-group">
                <span className="ctrl-label mono">Returns</span>
                <div className="btn-row">
                  <button className="toggle" aria-pressed={mode === "net"} onClick={() => setMode("net")}>Net of costs</button>
                  <button className="toggle" aria-pressed={mode === "gross"} onClick={() => setMode("gross")}>Gross</button>
                </div>
              </div>
              <div className="control-group">
                <span className="ctrl-label mono">Benchmark</span>
                <div className="btn-row">
                  {BENCH_ORDER.map((b) => (
                    <button key={b} className="toggle" aria-pressed={bench === b} onClick={() => setBench(b)}>
                      {backtest.benchmark_labels[b]}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="legend">
            <span><i style={{ background: "var(--series-net)" }} />{c.signal_name} ({mode})</span>
            <span><i style={{ background: "var(--series-bench)" }} />{backtest.benchmark_labels[bench]}</span>
          </div>

          <LineChart dates={curves.dates} series={equitySeries} height={320}
                     yFormat={(v) => v.toFixed(0)}
                     ariaLabel={`Growth of $100: ${c.signal_name} versus ${backtest.benchmark_labels[bench]}`} />

          <div className="takeaway">
            <span className="tk-label">Takeaway</span>
            <span>
              {mode === "net"
                ? `Net of ${backtest.base_cost_bps} bps, the signal compounded at ${pct(km.cagr)} a year`
                : `Gross of costs it compounded at ${pct(grossCagr)} a year — costs shave off ${pct(km.transaction_cost_drag, 2)}`}
              {cmp && `, ${cmp.excess_return >= 0 ? "ahead of" : "behind"} ${backtest.benchmark_labels[bench]} by ${pctSigned(cmp.excess_return)}/yr (Sharpe ${num(cmp.strategy_sharpe)} vs ${num(cmp.benchmark_sharpe)}).`}
            </span>
          </div>
        </div>

        <div className="metric-strip">
          <Tile label={mode === "net" ? "Net CAGR" : "Gross CAGR"} value={pct(mode === "net" ? km.cagr : grossCagr)} />
          <Tile label="Sharpe" value={num(mode === "net" ? km.sharpe : grossSharpe)} />
          <Tile label="Max drawdown" value={pct(km.max_drawdown, 0)} tone="neg" />
          <Tile label="Volatility" value={pct(km.annualized_volatility)} />
          <Tile label="Turnover / yr" value={`${num(km.annualized_turnover, 1)}×`} />
          <Tile label="Cost drag / yr" value={pct(km.transaction_cost_drag, 2)} />
        </div>

        <div className="evidence-two">
          <div className="panel chart-card">
            <div className="chart-head">
              <div>
                <div className="chart-title">Drawdown</div>
                <div className="chart-q">How deep were the losses along the way?</div>
              </div>
            </div>
            <LineChart dates={curves.dates} series={ddSeries} height={200} baselineZero
                       yFormat={(v) => `${(v * 100).toFixed(0)}%`} ariaLabel="Drawdown over time" />
            <div className="takeaway">
              <span className="tk-label">Takeaway</span>
              <span>Worst peak-to-trough loss was {pct(km.max_drawdown, 0)} — versus {pct(backtest.benchmarks.find((b) => b.benchmark_key === "spy_buy_hold")!.max_drawdown, 0)} for buy-and-hold SPY.</span>
            </div>
          </div>

          <div className="panel chart-card oos-card">
            <div className="chart-head">
              <div>
                <div className="chart-title">Out-of-sample check</div>
                <div className="chart-q">Did it hold up on data it never saw?</div>
              </div>
            </div>
            <div className="oos-rows">
              <OosRow label="In-sample (2006–2016)" cagr={c.stress_test_summary.train_test.train_cagr} sharpe={c.stress_test_summary.train_test.train_sharpe} />
              <OosRow label="Out-of-sample (2017+)" cagr={c.stress_test_summary.train_test.test_cagr} sharpe={c.stress_test_summary.train_test.test_sharpe} highlight />
            </div>
            <div className="takeaway">
              <span className="tk-label">Takeaway</span>
              <span>{c.stress_test_summary.train_test.test_verdict_note}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Tile({ label, value, tone }: { label: string; value: string; tone?: "neg" | "pos" }) {
  return (
    <div className="metric tile">
      <span className="label">{label}</span>
      <span className={`value ${tone ?? ""}`}>{value}</span>
    </div>
  );
}

function OosRow({ label, cagr, sharpe, highlight }: { label: string; cagr: number; sharpe: number; highlight?: boolean }) {
  return (
    <div className={`oos-row ${highlight ? "hl" : ""}`}>
      <span className="oos-label">{label}</span>
      <span className="oos-vals mono">
        <b>{pct(cagr)}</b> CAGR · <b>{num(sharpe)}</b> Sharpe
      </span>
    </div>
  );
}
