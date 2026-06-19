export const pct = (x: number | null | undefined, d = 1): string =>
  x === null || x === undefined || Number.isNaN(x) ? "—" : `${(x * 100).toFixed(d)}%`;

export const pctSigned = (x: number | null | undefined, d = 1): string =>
  x === null || x === undefined || Number.isNaN(x) ? "—" : `${x >= 0 ? "+" : ""}${(x * 100).toFixed(d)}%`;

export const num = (x: number | null | undefined, d = 2): string =>
  x === null || x === undefined || Number.isNaN(x) ? "—" : x.toFixed(d);

export const verdictClass = (v: string): string =>
  v === "Survived" ? "v-survived" : v === "Rejected" ? "v-rejected" : "v-conditional";

export const verdictGlyph = (v: string): string =>
  v === "Survived" ? "✓" : v === "Rejected" ? "✕" : "≈";

export const verdictColorVar = (v: string): string =>
  v === "Survived" ? "var(--survived)" : v === "Rejected" ? "var(--rejected)" : "var(--conditional)";

export const failureLabel = (f: string): string =>
  ({
    cost_failure: "Cost failure",
    turnover_failure: "Excessive turnover",
    parameter_fragility: "Parameter fragility",
    regime_dependency: "Regime dependency",
    drawdown_failure: "Drawdown failure",
    out_of_sample_failure: "Out-of-sample failure",
    benchmark_underperformance: "Benchmark underperformance",
  } as Record<string, string>)[f] ?? f;
