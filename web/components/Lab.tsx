"use client";

import { useCallback, useState } from "react";
import { LabData } from "@/lib/data";
import Hero from "./Hero";
import ContextBar from "./ContextBar";
import SignalSelector from "./SignalSelector";
import SignalCase from "./SignalCase";
import EvidencePanel from "./EvidencePanel";
import StressPanel from "./StressPanel";
import VerdictBoard from "./VerdictBoard";
import Methodology from "./Methodology";
import SiteFooter from "./SiteFooter";

export default function Lab({ data }: { data: LabData }) {
  const cases = data.signalCases;
  const [selected, setSelected] = useState(0);
  const current = cases[selected];

  const selectByIndex = useCallback((i: number, scroll = true) => {
    setSelected(i);
    if (scroll) {
      requestAnimationFrame(() =>
        document.getElementById("signal-case")?.scrollIntoView({ behavior: "smooth", block: "start" })
      );
    }
  }, []);

  const selectByFamily = useCallback((family: string) => {
    const i = cases.findIndex((c) => c.signal_family === family);
    if (i >= 0) selectByIndex(i);
  }, [cases, selectByIndex]);

  return (
    <main>
      <Hero overview={data.overview} board={data.board} onJump={selectByFamily} />
      <ContextBar current={current} index={selected} total={cases.length} />
      <SignalSelector cases={cases} selected={selected} onSelect={selectByIndex} />
      <SignalCase c={current} />
      <EvidencePanel c={current} backtest={data.backtest} />
      <StressPanel c={current} backtest={data.backtest} />
      <VerdictBoard board={data.board} onSelect={selectByFamily} currentFamily={current.signal_family} />
      <Methodology data={data.dataSummary} overview={data.overview} />
      <SiteFooter overview={data.overview} sources={data.dataSummary.sources} />
    </main>
  );
}
