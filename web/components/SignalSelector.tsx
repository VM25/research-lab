"use client";

import { SignalCase } from "@/lib/data";
import { pct, num, verdictClass, verdictGlyph } from "@/lib/format";

export default function SignalSelector({ cases, selected, onSelect }: {
  cases: SignalCase[]; selected: number; onSelect: (i: number) => void;
}) {
  return (
    <section className="section-pad" id="signal-selector">
      <div className="wrap">
        <div className="section-intro">
          <span className="eyebrow">Step 01 · Pick a signal</span>
          <h2>Five explainable signals. One question each.</h2>
          <p>Each is a research case with a hypothesis, evidence, and a verdict. Choose one to investigate — the sections below update to that signal.</p>
        </div>

        <div className="selector-grid">
          {cases.map((c, i) => (
            <button key={c.signal_family}
                    className={`sig-card ${i === selected ? "active" : ""}`}
                    aria-pressed={i === selected}
                    onClick={() => onSelect(i)}>
              <div className="sig-card-top">
                <span className="sig-idx mono">{String(i + 1).padStart(2, "0")}</span>
                <span className={`verdict-chip ${verdictClass(c.verdict)}`}>
                  <span className="v-glyph">{verdictGlyph(c.verdict)}</span> {c.verdict}
                </span>
              </div>
              <h3 className="sig-name">{c.signal_name}</h3>
              <p className="sig-hyp">{c.plain_english_hypothesis}</p>
              <div className="sig-foot">
                <span className="sig-metric"><b>{pct(c.key_metrics.cagr)}</b> CAGR</span>
                <span className="sig-metric"><b>{num(c.key_metrics.sharpe)}</b> Sharpe</span>
                <span className="sig-metric"><b>{pct(c.key_metrics.max_drawdown, 0)}</b> max DD</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
