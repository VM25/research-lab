"use client";

import { SignalCase } from "@/lib/data";
import { verdictClass, verdictGlyph } from "@/lib/format";

export default function ContextBar({ current, index, total }: {
  current: SignalCase; index: number; total: number;
}) {
  return (
    <div className="contextbar">
      <div className="wrap cb-inner">
        <div className="cb-left">
          <span className="cb-tag mono">Now inspecting · {String(index + 1).padStart(2, "0")}/{String(total).padStart(2, "0")}</span>
          <span className="cb-name">{current.signal_name}</span>
        </div>
        <div className="cb-right">
          <span className={`verdict-chip ${verdictClass(current.verdict)}`}>
            <span className="v-glyph">{verdictGlyph(current.verdict)}</span> {current.verdict}
          </span>
        </div>
      </div>
    </div>
  );
}
