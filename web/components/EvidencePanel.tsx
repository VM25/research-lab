"use client";

import { useMemo, useState } from "react";
import { SignalCase, BacktestSummary } from "@/lib/data";
import { pct, pctSigned, num } from "@/lib/format";
import LineChart, { Series } from "./charts/LineChart";
import SectionHead from "./SectionHead";

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
  const spyDD = backtest.benchmarks.find((b) => b.benchmark_key === "spy_buy_hold")!.max_drawdown;

  const equity: Series[] = useMemo(() => [
    { name: backtest.benchmark_labels[bench], values: curves.benchmarks[bench], color: "var(--ink-3)", dash: "6 4", width: 1.5, label: true },
    { name: "Strategy, gross", values: fam.gross, color: "var(--ink-2)", dash: "2 3", width: mode === "gross" ? 2.3 : 1.2 },
    { name: "Strategy, net", values: fam.net, color: "var(--accent)", width: mode === "net" ? 2.4 : 1.2, label: true, area: mode === "net" },
  ], [mode, bench, fam, curves, backtest.benchmark_labels]);

  const ddSeries: Series[] = [
    { name: "Drawdown", values: fam.drawdown, color: "var(--ink)", width: 1.6, label: true },
  ];

  return (
    <section className="block" id="evidence">
      <div className="frame">
        <SectionHead index="03" kicker="Evidence summary"
          title="Performance, gross and net of costs"
          lede={`Growth of an index of 100 over the backtest sample (from ${backtest.common_start}), against a selectable benchmark. The strategy is shown gross and net of ${backtest.base_cost_bps} bps transaction costs.`} />

        <div className="s-body">
          <div className="ev-main">
            <div className="sheet-head">
              <div>
                <div className="sheet-title">{c.signal_name} vs {backtest.benchmark_labels[bench]}</div>
                <div className="sheet-q">Did the signal add value after realistic execution costs?</div>
              </div>
              <div className="ev-controls">
                <div className="ctrl-field">
                  <span className="ctrl-label">Emphasis</span>
                  <div className="ctrl">
                    <button aria-pressed={mode === "net"} onClick={() => setMode("net")}>Net of costs</button>
                    <button aria-pressed={mode === "gross"} onClick={() => setMode("gross")}>Gross</button>
                  </div>
                </div>
                <div className="ctrl-field">
                  <span className="ctrl-label">Benchmark</span>
                  <div className="ctrl">
                    {BENCH_ORDER.map((b) => (
                      <button key={b} aria-pressed={bench === b} onClick={() => setBench(b)}>{backtest.benchmark_labels[b]}</button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="ev-chart">
              <div className="legend" style={{ marginBottom: 14 }}>
                <span><i style={{ borderColor: "var(--ink)" }} />Strategy, net ({backtest.base_cost_bps} bps)</span>
                <span><i style={{ borderColor: "var(--ink-2)", borderTopStyle: "dotted" }} />Strategy, gross</span>
                <span><i style={{ borderColor: "var(--ink-3)", borderTopStyle: "dashed" }} />{backtest.benchmark_labels[bench]}</span>
              </div>
              <LineChart dates={curves.dates} series={equity} height={340}
                         yFormat={(v) => v.toFixed(0)}
                         ariaLabel={`Index of 100: ${c.signal_name} net and gross versus ${backtest.benchmark_labels[bench]}`} />
              <div className="finding">
                <span className="finding-tag">Finding</span>
                <span className="finding-text">
                  {mode === "net"
                    ? <>Net of {backtest.base_cost_bps} bps, the strategy compounded at <b>{pct(km.cagr)}</b> per year</>
                    : <>Gross of costs it compounded at <b>{pct(grossCagr)}</b> per year; costs reduce this by <b>{pct(km.transaction_cost_drag, 2)}</b></>}
                  {cmp && <>, {cmp.excess_return >= 0 ? "ahead of" : "behind"} {backtest.benchmark_labels[bench]} by <b>{pctSigned(cmp.excess_return)}</b> per year, at Sharpe <b>{num(cmp.strategy_sharpe)}</b> against <b>{num(cmp.benchmark_sharpe)}</b>.</>}
                </span>
              </div>
            </div>
          </div>

          <div className="stat-grid" style={{ gridTemplateColumns: "repeat(6, 1fr)", marginTop: 24 }}>
            <Stat k={mode === "net" ? "CAGR, net" : "CAGR, gross"} v={pct(mode === "net" ? km.cagr : grossCagr)} />
            <Stat k="Sharpe" v={num(mode === "net" ? km.sharpe : grossSharpe)} />
            <Stat k="Max drawdown" v={pct(km.max_drawdown, 0)} />
            <Stat k="Volatility" v={pct(km.annualized_volatility)} />
            <Stat k="Turnover / yr" v={`${num(km.annualized_turnover, 1)}×`} />
            <Stat k="Cost drag / yr" v={pct(km.transaction_cost_drag, 2)} last />
          </div>

          <div className="ev-two">
            <div>
              <div className="sheet-title" style={{ fontSize: 16 }}>Drawdown profile</div>
              <div className="sheet-q" style={{ marginBottom: 12 }}>How deep were the peak-to-trough losses?</div>
              <LineChart dates={curves.dates} series={ddSeries} height={200} baselineZero
                         yFormat={(v) => `${(v * 100).toFixed(0)}%`} ariaLabel="Drawdown over time" />
              <div className="finding">
                <span className="finding-tag">Finding</span>
                <span className="finding-text">Worst peak-to-trough loss of <b>{pct(km.max_drawdown, 0)}</b>, against <b>{pct(spyDD, 0)}</b> for SPY buy-and-hold over the same window.</span>
              </div>
            </div>
            <div>
              <div className="sheet-title" style={{ fontSize: 16 }}>Out-of-sample check</div>
              <div className="sheet-q" style={{ marginBottom: 12 }}>Did it hold on data the parameters never saw?</div>
              <table className="oos-table">
                <tbody>
                  <tr>
                    <td>In-sample, 2006 to 2016</td>
                    <td className="num">{pct(c.stress_test_summary.train_test.train_cagr)}</td>
                    <td className="num">{num(c.stress_test_summary.train_test.train_sharpe)}</td>
                  </tr>
                  <tr className="hl">
                    <td>Out-of-sample · 2017→</td>
                    <td className="num">{pct(c.stress_test_summary.train_test.test_cagr)}</td>
                    <td className="num">{num(c.stress_test_summary.train_test.test_sharpe)}</td>
                  </tr>
                  <tr><td className="label" style={{ borderBottom: 0, paddingTop: 4 }}></td><td className="label num" style={{ borderBottom: 0 }}>CAGR</td><td className="label num" style={{ borderBottom: 0 }}>Sharpe</td></tr>
                </tbody>
              </table>
              <div className="finding">
                <span className="finding-tag">Finding</span>
                <span className="finding-text">{c.stress_test_summary.train_test.test_verdict_note}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Stat({ k, v, last }: { k: string; v: string; last?: boolean }) {
  return (
    <div className="stat" style={last ? { borderRight: 0 } : undefined}>
      <div className="stat-key">{k}</div>
      <div className="stat-val">{v}</div>
    </div>
  );
}
