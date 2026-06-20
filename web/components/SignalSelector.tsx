"use client";

import { SignalCase } from "@/lib/data";
import { pct, num } from "@/lib/format";
import Classification from "./Classification";
import SectionHead from "./SectionHead";

export default function SignalSelector({ cases, selected, onSelect }: {
  cases: SignalCase[]; selected: number; onSelect: (i: number) => void;
}) {
  return (
    <section className="block" id="signal-selector">
      <div className="frame">
        <SectionHead index="01" kicker="Validation docket"
          title="Five signals under review"
          lede="Each row is a research case carried through the same validation sequence. Select one to open its file; the sections that follow update to the selected signal." />
        <div className="s-body">
          <div className="gutter-rule"><span className="gr-line" /></div>
          <table className="docket-table" style={{ marginTop: 6 }}>
            <thead>
              <tr>
                <th style={{ width: 36 }}></th>
                <th>Signal &amp; thesis</th>
                <th style={{ width: 150 }}>Classification</th>
                <th className="col-evi" style={{ width: 170 }}>Key evidence</th>
                <th className="col-weak">Principal weakness</th>
                <th style={{ width: 70 }}></th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c, i) => (
                <tr key={c.signal_family}
                    className={`docket-row ${i === selected ? "active" : ""}`}
                    onClick={() => onSelect(i)}
                    tabIndex={0}
                    onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect(i); } }}>
                  <td><span className="docket-idx">{String(i + 1).padStart(2, "0")}</span></td>
                  <td>
                    <div className="docket-name">{c.signal_name}</div>
                    <div className="docket-hyp">{c.plain_english_hypothesis}</div>
                  </td>
                  <td><Classification verdict={c.verdict} /></td>
                  <td className="col-evi">
                    <span className="docket-evi">
                      Sharpe {num(c.key_metrics.sharpe)} · DD {pct(c.key_metrics.max_drawdown, 0)}<br />
                      CAGR {pct(c.key_metrics.cagr)} net
                    </span>
                  </td>
                  <td className="col-weak"><span className="docket-weak">{c.weaknesses[0] ?? c.expected_weakness[0]}</span></td>
                  <td><span className="docket-open">{i === selected ? "Viewing" : "Open"}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
