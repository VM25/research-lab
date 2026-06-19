# 07_PRODUCT_REQUIREMENTS.md

# Systematic Alpha Research Lab — Product Requirements

## Product Objective

Build an interactive website that explains and tests systematic trading signals as clear research cases.

The website must help users answer:

```text id="srv58x"
Does this signal survive reality?
```

The product must be rigorous, but not overwhelming.

## Product Concept

The website is a **Signal Survival Lab**.

Each signal appears as a case file:

```text id="k6bcz7"
Hypothesis
→ Evidence
→ Stress Test
→ Verdict
```

The viewer should always know what to inspect, what changed, and what the result means.

## Target Users

## Recruiter

Needs to understand quickly:

* what the project is
* what skills it demonstrates
* why it matters for quant roles
* which signals survived, failed, or were conditional

## Quant Interviewer

Needs to inspect:

* signal logic
* data assumptions
* backtest timing
* transaction costs
* walk-forward validation
* robustness results
* final classification logic

## Technical Reviewer

Needs to verify:

* data provenance
* no-lookahead handling
* generated outputs
* reproducibility
* website/data consistency

## Required User Journey

The site must follow this sequence:

```text id="rws381"
Project Question
→ Signal Selection
→ Signal Case
→ Evidence
→ Stress Tests
→ Verdict Board
→ Methodology
```

Do not force users through a long technical scroll before they understand the project.

## Required Sections

## 1. Hero

Must show:

* project name
* one-line research question
* signal count
* universe summary
* validation standard
* final verdict summary

Required headline idea:

```text id="cm4osc"
Testing whether systematic alpha signals survive costs, out-of-sample validation, and market stress.
```

## 2. Signal Selector

Users must be able to choose a signal:

* Time-Series Momentum
* Cross-Sectional Momentum
* Short-Term Reversal
* Volatility-Scaled Momentum
* Equal-Weight Signal Ensemble

Each signal card must show:

* hypothesis
* one-line result
* verdict
* primary weakness

## 3. Signal Case View

For the selected signal, show:

* plain-English hypothesis
* formula
* portfolio rule
* expected strength
* expected weakness
* final verdict

This section must explain before showing charts.

## 4. Evidence Panel

Show only the evidence needed to judge the signal:

* net performance
* benchmark comparison
* drawdown
* turnover
* transaction-cost drag
* out-of-sample result

Use concise charts and summary cards.

## 5. Stress Test Panel

Users must inspect how the signal behaves under:

* higher costs
* different parameters
* different rebalance frequencies
* crisis periods
* market regimes

Each stress test must show whether the verdict changed.

## 6. Verdict Board

Group all signals into:

```text id="d7w0fn"
Survived
Conditional
Rejected
```

Each verdict card must show:

* signal name
* main evidence
* weakness
* best use case
* final research note

## 7. Methodology

Keep methodology concise.

Must include:

* data universe
* adjusted-close return basis
* no-lookahead rule
* cost model
* benchmark list
* train/test split
* walk-forward logic
* limitations

This section must support auditability without becoming the main product.

## Required Interactions

The product must include:

* signal selector
* gross/net toggle
* benchmark selector
* cost scenario selector
* parameter comparison
* verdict change indicator
* concise methodology drawer or section

Do not add interactions that do not help evaluate signal survival.

## Required Data Sources

The website must read from generated JSON files:

```text id="foe375"
overview.json
data_summary.json
signal_cases.json
backtest_summary.json
validation_summary.json
classification_board.json
failure_modes.json
```

No results may be manually hardcoded.

## Required Metrics

Display only key metrics:

* CAGR
* Sharpe ratio
* max drawdown
* turnover
* cost drag
* benchmark-relative return
* out-of-sample result

Do not overload the product with every metric from the research engine.

## UX Rules

The website must be guided, not exploratory chaos.

Required behavior:

* each section must explain its purpose
* every chart must have a takeaway
* every interaction must change an interpretation
* every signal must end with a verdict
* every verdict must cite evidence

## Content Rules

Use plain English first, formulas second.

Avoid unexplained jargon.

Do not write long research paragraphs inside the website.

Use short labels, direct explanations, and evidence-led conclusions.

## Visual Product Direction

The product must not look like a generic quant dashboard.

Avoid:

* flat card grids
* endless metric tables
* generic dark dashboard layouts
* blue-gray finance visuals
* chart dumps
* oversized technical appendix sections

The design must feel like a focused research investigation.

## Performance Requirements

The website must be:

* responsive
* fast
* static-export friendly
* accessible
* readable on laptop screens
* usable without backend services

## Success Criteria

The product succeeds if a viewer can answer within two minutes:

* what the project tests
* which signal they are inspecting
* how the signal works
* what the evidence says
* what breaks under stress
* why the signal was classified as Survived, Conditional, or Rejected

## Hard Rules

* Do not build a giant research dossier.
* Do not bury the verdict.
* Do not show charts without takeaways.
* Do not make users guess what to click.
* Do not use simulated results as main evidence.
* Do not claim live-trading readiness.
* Do not manually hardcode research numbers.

The website must make the research easier to understand, not harder.
