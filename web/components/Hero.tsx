"use client";

import { Overview, ClassificationBoard, Verdict } from "@/lib/data";
import { verdictClass, verdictGlyph } from "@/lib/format";

const VERDICTS: Verdict[] = ["Survived", "Conditional", "Rejected"];

export default function Hero({ overview, board, onJump }: {
  overview: Overview; board: ClassificationBoard; onJump: (f: string) => void;
}) {
  const u = overview.universe_summary;
  const years = Math.round(
    (new Date(u.sample_end).getTime() - new Date(u.sample_start).getTime()) / 3.15576e10
  );

  return (
    <header className="hero">
      <div className="hero-grid wrap">
        <div className="hero-main">
          <span className="eyebrow">{overview.project_name}</span>
          <h1 className="hero-title">
            Does this signal<br /><span className="grad">survive reality?</span>
          </h1>
          <p className="hero-sub">{overview.headline}</p>

          <div className="hero-verdicts" role="group" aria-label="Verdict summary">
            {VERDICTS.map((v) => (
              <button key={v} className={`hero-verdict ${verdictClass(v)}`}
                      onClick={() => {
                        document.getElementById("verdict-board")?.scrollIntoView({ behavior: "smooth" });
                      }}>
                <span className="hv-count">{overview.verdict_summary[v]}</span>
                <span className="hv-label"><span className="v-glyph">{verdictGlyph(v)}</span> {v}</span>
              </button>
            ))}
          </div>

          <div className="hero-stats">
            <Stat n={String(overview.signal_count)} l="signals tested" />
            <Stat n={String(u.asset_count)} l="real ETFs" />
            <Stat n={`${years} yrs`} l={`${u.sample_start.slice(0,4)}–${u.sample_end.slice(0,4)}`} />
            <Stat n={`${overview.primary_cost_bps} bps`} l="cost baseline" />
          </div>
        </div>

        <aside className="hero-side panel">
          <div className="hs-head">What we put each signal through</div>
          <ol className="hs-list">
            {overview.validation_standard.map((s, i) => (
              <li key={i}><span className="hs-num mono">{String(i + 1).padStart(2, "0")}</span>{s}</li>
            ))}
          </ol>
          <div className="hs-note">{overview.data_note}</div>
        </aside>
      </div>

      <div className="hero-flow wrap" aria-hidden="true">
        {["Pick a signal", "Understand the hypothesis", "Inspect the evidence", "Stress the assumptions", "Receive a verdict"].map((s, i, a) => (
          <span key={i} className="flow-step">
            <span className="flow-dot" /> {s}{i < a.length - 1 && <span className="flow-arrow">→</span>}
          </span>
        ))}
      </div>
    </header>
  );
}

function Stat({ n, l }: { n: string; l: string }) {
  return (
    <div className="hstat">
      <div className="hstat-n">{n}</div>
      <div className="hstat-l">{l}</div>
    </div>
  );
}
