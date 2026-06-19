"""End-to-end research pipeline.

    data -> signals -> backtests -> validation -> classification
         -> website JSON -> research report

Run with:  python -m systematic_alpha_lab.pipeline
"""
from __future__ import annotations

import shutil
import time

from .data.dataset import build_dataset
from .signals.factory import compute_all_signals, write_signal_outputs
from .backtest.runner import run_all
from .validation.run_validation import run_validation
from .outputs.website_json import generate_website_json
from .outputs.report import generate_report
from .utils.io import WEB_DATA_DIR, OUTPUT_DIR, ensure_dirs

WEBSITE_FILES = [
    "overview.json", "data_summary.json", "signal_cases.json",
    "backtest_summary.json", "validation_summary.json",
    "classification_board.json", "failure_modes.json",
]


def run_pipeline(use_cache: bool = True, verbose: bool = True):
    t0 = time.time()
    ensure_dirs()

    def log(msg):
        if verbose:
            print(f"[{time.time()-t0:6.1f}s] {msg}", flush=True)

    log("Building dataset (real ETF + macro data)...")
    ds = build_dataset(use_cache=use_cache)
    log(f"  {len(ds.tradable)} ETFs, {ds.calendar.min().date()} -> {ds.calendar.max().date()}")

    log("Computing signals...")
    signals = compute_all_signals(ds)
    write_signal_outputs(signals)

    log("Running backtests (5 signals x 5 cost scenarios + benchmarks)...")
    bt = run_all(ds, signals)

    log("Running validation suite (train/test, walk-forward, robustness)...")
    val = run_validation(ds, bt)
    log(f"  verdicts: {val['conclusions']['verdict_counts']}")

    log("Generating website JSON...")
    generate_website_json(ds, bt, val)

    log("Generating research report...")
    generate_report(ds, bt, val)

    # mirror website JSON into research/outputs/website_json/
    dest = OUTPUT_DIR / "website_json"
    dest.mkdir(parents=True, exist_ok=True)
    for fn in WEBSITE_FILES:
        src = WEB_DATA_DIR / fn
        if src.exists():
            shutil.copy(src, dest / fn)

    log("Done.")
    return ds, bt, val


if __name__ == "__main__":
    run_pipeline()
