"use client";

import { SignalCase } from "@/lib/data";
import Classification from "./Classification";

export default function ContextBar({ current, index, total }: {
  current: SignalCase; index: number; total: number;
}) {
  return (
    <div className="ctxbar">
      <div className="frame ctx-in">
        <div className="ctx-left">
          <span className="ctx-tag">Case {String(index + 1).padStart(2, "0")} / {String(total).padStart(2, "0")}</span>
          <span className="ctx-name">{current.signal_name}</span>
        </div>
        <Classification verdict={current.verdict} />
      </div>
    </div>
  );
}
