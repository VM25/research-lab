"use client";

import { Fragment } from "react";
import { ClassificationBoard, Verdict } from "@/lib/data";
import Classification from "./Classification";
import SectionHead from "./SectionHead";

const numWord = (n: number) => (["zero", "one", "two", "three", "four", "five"][n] ?? String(n));

const DESCRIPT: Record<Verdict, string> = {
  Survived: "Useful net-of-cost performance, controlled drawdowns, and credible out-of-sample evidence that does not depend on a single parameter choice.",
  Conditional: "Adds value under specific regimes or cost levels, or as a risk-control overlay — useful, but not standalone alpha.",
  Rejected: "Costs, turnover, benchmark-relative weakness, or instability undo the signal. A documented negative result.",
};

export default function VerdictBoard({ board, onSelect, currentFamily }: {
  board: ClassificationBoard; onSelect: (f: string) => void; currentFamily: string;
}) {
  return (
    <section className="block" id="verdict-board">
      <div className="frame">
        <SectionHead index="05" kicker="Research classification"
          title="Classification ledger"
          lede="The committee classification for each signal, grouped by verdict and backed by the same evidence inspected above. Select any row to reopen its file." />

        <div className="s-body">
          <p className="board-conclusion">
            Of five signals examined, <b>{numWord(board.counts.Survived)}</b> survived validation as documented research overlays, <b>{numWord(board.counts.Conditional)}</b> {board.counts.Conditional === 1 ? "is" : "are"} conditional, and <b>{numWord(board.counts.Rejected)}</b> {board.counts.Rejected === 1 ? "is" : "are"} rejected on this evidence.
          </p>
          <table className="board-table">
            <thead>
              <tr>
                <th style={{ width: "26%" }}>Signal</th>
                <th style={{ width: "26%" }}>Primary evidence</th>
                <th style={{ width: "20%" }}>Principal weakness</th>
                <th className="col-note">Research note</th>
              </tr>
            </thead>
            <tbody>
              {board.order.map((v) => {
                const cards = board.groups[v];
                return (
                  <Fragment key={v}>
                    <tr className="board-grouphead">
                      <td colSpan={4}>
                        <div className="bg-h">
                          <Classification verdict={v} size="md" />
                          <span className="bg-count">{board.counts[v]} {board.counts[v] === 1 ? "signal" : "signals"}</span>
                        </div>
                        <div className="bg-desc">{DESCRIPT[v]}</div>
                      </td>
                    </tr>
                    {cards.length === 0 && (
                      <tr key={`e-${v}`}><td colSpan={4} className="dim" style={{ fontStyle: "italic" }}>None in this category.</td></tr>
                    )}
                    {cards.map((card) => (
                      <tr key={card.signal_family}
                          className={`board-row ${card.signal_family === currentFamily ? "active" : ""}`}
                          onClick={() => onSelect(card.signal_family)} tabIndex={0}
                          onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect(card.signal_family); } }}>
                        <td>
                          <div className="board-signame">{card.signal_name}</div>
                          <div className="board-result">{card.one_line_result}</div>
                          <div className="board-cell-k" style={{ marginTop: 8 }}>{card.best_use_case}</div>
                        </td>
                        <td>{card.primary_evidence}</td>
                        <td>{card.main_weakness}</td>
                        <td className="col-note">{card.final_research_note}</td>
                      </tr>
                    ))}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
