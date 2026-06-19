"use client";

import { SignalCase as Case } from "@/lib/data";
import { verdictClass, verdictGlyph, verdictColorVar } from "@/lib/format";

export default function SignalCase({ c }: { c: Case }) {
  return (
    <section className="section-pad case-section" id="signal-case">
      <div className="wrap">
        <div className="section-intro">
          <span className="eyebrow">Step 02 · Understand the hypothesis</span>
          <h2>{c.signal_name}</h2>
          <p>{c.plain_english_hypothesis}</p>
        </div>

        <div className="case-grid">
          <div className="case-left">
            <div className="panel case-block">
              <div className="cb-label mono">The hypothesis</div>
              <p className="cb-body">{c.hypothesis}</p>
            </div>

            <div className="case-two">
              <div className="panel case-block">
                <div className="cb-label mono">How it is measured</div>
                <p className="cb-body small">{c.formula_short}</p>
                <code className="formula mono">{c.formula}</code>
                <div className="cb-meta mono">
                  <span>Lookback · {c.lookback_window}</span>
                  <span>Rebalance · {c.rebalance_frequency}</span>
                </div>
              </div>
              <div className="panel case-block">
                <div className="cb-label mono">How it becomes a portfolio</div>
                <p className="cb-body small">{c.portfolio_rule}</p>
                <div className="cb-meta mono">
                  <span>Weighting · {c.weighting_method.replace(/_/g, " ")}</span>
                  <span>Long-only · cash fallback</span>
                </div>
              </div>
            </div>

            <div className="case-two">
              <div className="panel case-block strength">
                <div className="cb-label mono">Why it might work</div>
                <ul className="case-list">{c.expected_strength.map((s, i) => <li key={i}>{s}</li>)}</ul>
              </div>
              <div className="panel case-block weakness">
                <div className="cb-label mono">What can break it</div>
                <ul className="case-list">{c.expected_weakness.map((s, i) => <li key={i}>{s}</li>)}</ul>
              </div>
            </div>
          </div>

          <aside className="case-verdict panel" style={{ borderColor: verdictColorVar(c.verdict) }}>
            <div className="cv-top">
              <span className="cv-label mono">Final verdict</span>
              <span className={`verdict-chip ${verdictClass(c.verdict)}`}>
                <span className="v-glyph">{verdictGlyph(c.verdict)}</span> {c.verdict}
              </span>
            </div>
            <p className="cv-note">{c.verdict_reason}</p>
            <div className="cv-evidence">
              <div className="cv-sub mono">Best use case</div>
              <p>{c.best_use_case}</p>
            </div>
            <div className="cv-hint mono">↓ The evidence and stress tests behind this verdict</div>
          </aside>
        </div>
      </div>
    </section>
  );
}
