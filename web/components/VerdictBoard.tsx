"use client";

import { ClassificationBoard, Verdict } from "@/lib/data";
import { verdictClass, verdictGlyph } from "@/lib/format";

const DESCRIPT: Record<Verdict, string> = {
  Survived: "Useful net-of-cost performance, controlled drawdowns, and credible out-of-sample evidence that does not hinge on one setting.",
  Conditional: "Works under specific regimes, costs, or as a risk overlay — valuable, but not standalone alpha.",
  Rejected: "Costs, turnover, benchmark-inferiority, or instability undo it. A clear negative result is still a result.",
};

export default function VerdictBoard({ board, onSelect, currentFamily }: {
  board: ClassificationBoard; onSelect: (f: string) => void; currentFamily: string;
}) {
  return (
    <section className="section-pad verdict-section" id="verdict-board">
      <div className="wrap">
        <div className="section-intro">
          <span className="eyebrow">Step 05 · The verdict board</span>
          <h2>Which signals survived reality?</h2>
          <p>Every signal lands in one of three buckets, each backed by the same evidence you just inspected. Click any card to investigate it.</p>
        </div>

        <div className="board-grid">
          {board.order.map((v) => (
            <div key={v} className={`board-col ${verdictClass(v)}`}>
              <div className="board-col-head">
                <span className="bc-glyph v-glyph">{verdictGlyph(v)}</span>
                <h3 className="bc-title">{v}</h3>
                <span className="bc-count mono">{board.counts[v]}</span>
              </div>
              <p className="bc-desc">{DESCRIPT[v]}</p>
              <div className="board-cards">
                {board.groups[v].length === 0 && <div className="board-empty mono">None in this bucket</div>}
                {board.groups[v].map((card) => (
                  <button key={card.signal_family}
                          className={`board-card ${card.signal_family === currentFamily ? "active" : ""}`}
                          onClick={() => onSelect(card.signal_family)}>
                    <div className="boc-name">{card.signal_name}</div>
                    <div className="boc-result mono">{card.one_line_result}</div>
                    <div className="boc-row"><span className="boc-k">Evidence</span><span>{card.primary_evidence}</span></div>
                    <div className="boc-row"><span className="boc-k">Weakness</span><span>{card.main_weakness}</span></div>
                    <div className="boc-row"><span className="boc-k">Best use</span><span>{card.best_use_case}</span></div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
