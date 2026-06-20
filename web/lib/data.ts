import { promises as fs } from "fs";
import path from "path";

/* ---------- shared types ---------- */
export type Verdict = "Survived" | "Conditional" | "Rejected";

export interface KeyMetrics {
  cagr: number;
  annualized_volatility: number;
  sharpe: number;
  max_drawdown: number;
  annualized_turnover: number;
  transaction_cost_drag: number;
  benchmark_relative_return: number;
  out_of_sample_sharpe: number;
  out_of_sample_cagr: number;
  gross_cagr: number;
}

export interface CostRow {
  signal_family: string; cost_bps: number; scenario: string;
  gross_cagr: number; net_cagr: number; gross_sharpe: number; net_sharpe: number;
  annual_turnover: number; cost_drag: number; classification_at_cost_level: string;
}
export interface ParamRow {
  parameter_set: string; cagr: number; sharpe: number; max_drawdown: number;
  turnover: number; cost_drag: number; benchmark_relative_return: number; parameter_result: string;
}
export interface RebalRow {
  rebalance_frequency: string; net_cagr: number; net_sharpe: number; max_drawdown: number;
  annual_turnover: number; cost_drag: number; classification_at_frequency: string;
}
export interface RegimeRow {
  regime_name: string; observation_count: number; cagr: number; sharpe: number;
  max_drawdown: number; hit_rate: number; turnover: number; regime_note: string;
}
export interface CrisisRow {
  crisis_period: string; start_date: string; end_date: string; cumulative_return: number;
  max_drawdown: number; benchmark_relative_return: number; crisis_note: string;
}
export interface WalkRow {
  train_start: string; train_end: string; test_start: string; test_end: string;
  selected_parameters: string; test_cagr: number; test_sharpe: number;
  test_max_drawdown: number; test_excess_return_vs_benchmark: number;
  window_result: string; window_note: string;
}
export interface TrainTestRow {
  train_start: string; train_end: string; test_start: string; test_end: string;
  train_cagr: number; test_cagr: number; train_sharpe: number; test_sharpe: number;
  train_max_drawdown: number; test_max_drawdown: number; out_of_sample_held: boolean;
  test_verdict_note: string;
}
export interface ComparisonRow {
  benchmark_name: string; benchmark_key: string; strategy_cagr: number; benchmark_cagr: number;
  strategy_sharpe: number; benchmark_sharpe: number; strategy_max_drawdown: number;
  benchmark_max_drawdown: number; excess_return: number; information_ratio: number;
  comparison_note: string;
}

export interface SignalCase {
  signal_name: string;
  signal_family: string;
  plain_english_hypothesis: string;
  hypothesis: string;
  formula: string;
  formula_short: string;
  portfolio_rule: string;
  expected_strength: string[];
  expected_weakness: string[];
  lookback_window: string;
  rebalance_frequency: string;
  weighting_method: string;
  key_metrics: KeyMetrics;
  benchmark_comparison: ComparisonRow[];
  stress_test_summary: {
    cost_sensitivity: CostRow[];
    parameter_robustness: ParamRow[];
    rebalance_sensitivity: RebalRow[];
    regimes: RegimeRow[];
    crisis: CrisisRow[];
    walk_forward: WalkRow[];
    train_test: TrainTestRow;
  };
  verdict: Verdict;
  verdict_reason: string;
  primary_evidence: string[];
  weaknesses: string[];
  best_use_case: string;
  failure_modes: string[];
}

export interface Overview {
  project_name: string; tagline: string; research_question: string; headline: string;
  signal_count: number;
  universe_summary: { asset_count: number; asset_groups: number; sample_start: string; sample_end: string; trading_days: number; };
  validation_standard: string[];
  primary_cost_bps: number;
  verdict_summary: Record<Verdict, number>;
  verdict_headline: string;
  backtest_start?: string;
  data_note: string;
}

export interface DataSummary {
  universe: { ticker: string; name: string; group: string; first_date: string; last_date: string; source: string; status: string }[];
  asset_groups: string[];
  sample_period: { start: string; end: string; trading_days: number; note: string };
  backtest_period: { start: string; end: string; note: string };
  sources: string[];
  source_summary: string;
  return_basis: string;
  cash_handling: string;
  no_lookahead_rule: string;
  excluded_assets: string[];
  cost_model: { description: string; turnover_definition: string; scenarios: { scenario: string; cost_bps: number }[]; primary_cost_bps: number };
  regime_note: string;
  benchmarks: { key: string; name: string }[];
  train_test_split: { train: string; test: string };
  walk_forward_windows: number;
  primary_strategy_rules: string[];
  limitations: string[];
}

export interface Curves {
  dates: string[];
  strategies: Record<string, {
    net: (number | null)[]; gross: (number | null)[]; drawdown: (number | null)[];
    net_by_cost: Record<string, (number | null)[]>;
  }>;
  benchmarks: Record<string, (number | null)[]>;
}

export interface BacktestSummary {
  common_start: string; base_cost_bps: number;
  cost_scenarios: { scenario: string; cost_bps: number }[];
  strategies: any[];
  benchmarks: { benchmark_name: string; benchmark_key: string; cagr: number; annualized_volatility: number; sharpe: number; max_drawdown: number; annualized_turnover: number }[];
  comparison: ComparisonRow[];
  benchmark_labels: Record<string, string>;
  curves: Curves;
}

export interface ClassificationBoard {
  order: Verdict[];
  counts: Record<Verdict, number>;
  groups: Record<Verdict, {
    signal_name: string; signal_family: string; one_line_result: string;
    primary_evidence: string; main_weakness: string; best_use_case: string;
    final_research_note: string; verdict: Verdict;
  }[]>;
}

export interface LabData {
  overview: Overview;
  dataSummary: DataSummary;
  signalCases: SignalCase[];
  backtest: BacktestSummary;
  board: ClassificationBoard;
}

const DATA_DIR = path.join(process.cwd(), "public", "research-data");

async function readJson<T>(file: string): Promise<T> {
  const raw = await fs.readFile(path.join(DATA_DIR, file), "utf-8");
  return JSON.parse(raw) as T;
}

export async function loadLabData(): Promise<LabData> {
  const [overview, dataSummary, signalCases, backtest, board] = await Promise.all([
    readJson<Overview>("overview.json"),
    readJson<DataSummary>("data_summary.json"),
    readJson<SignalCase[]>("signal_cases.json"),
    readJson<BacktestSummary>("backtest_summary.json"),
    readJson<ClassificationBoard>("classification_board.json"),
  ]);
  return { overview, dataSummary, signalCases, backtest, board };
}
