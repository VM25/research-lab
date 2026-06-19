# 08_DESIGN_SYSTEM.md

# Systematic Alpha Research Lab — Design System

## Design Objective

Create a focused, non-generic interface for a **Signal Survival Lab**.

The design must help users understand:

```text id="fdwuxw"
Signal
→ Hypothesis
→ Evidence
→ Stress Test
→ Verdict
```

The website must feel guided, sharp, and research-driven. It must not overwhelm users with endless charts, dense text, or generic dashboard patterns.

## Product Feeling

The experience should feel like investigating a signal case, not scrolling through a quant encyclopedia.

The user should always know:

* what signal they are viewing
* what question is being tested
* what evidence matters
* what changed after stress testing
* why the verdict was assigned

## Core UX Principle

Every screen must reduce confusion.

Do not assume the user knows what to inspect. The interface must guide them.

Required pattern:

```text id="tidxdy"
Explain first
show evidence second
state verdict third
```

## Information Hierarchy

Prioritize:

1. research question
2. selected signal
3. hypothesis
4. key evidence
5. stress-test result
6. final verdict
7. methodology details

Methodology must be available, but it must not dominate the experience.

## Required Experience Flow

```text id="hvtgvh"
Hero
→ Signal Selector
→ Signal Case
→ Evidence Panel
→ Stress Test Panel
→ Verdict Board
→ Methodology
```

Do not create a long, flat page where every section has equal importance.

## Visual Direction

The design must avoid generic finance-dashboard visuals.

Do not use:

* flat gray cards everywhere
* generic dark dashboard layout
* blue-gray chart panels
* endless metric grids
* wall-of-text explanations
* disconnected chart sections
* oversized technical appendix
* chart dumps without interpretation

The interface must have depth, hierarchy, motion, and strong section rhythm.

## Layout Rules

Use fewer, stronger sections.

Each major section must have:

* one purpose
* one primary interaction
* one clear takeaway
* one visible connection to the final verdict

Avoid long uninterrupted scrolling blocks.

Use progressive disclosure for technical detail.

## Signal Case Design

Each signal must appear as a case file.

Required elements:

```text id="w4i1hl"
Signal Name
Hypothesis
Formula
Portfolio Rule
Key Evidence
Stress Result
Verdict
```

Formula must be present, but not visually dominant.

Plain-English explanation comes first.

## Evidence Design

Every chart must answer one question.

Examples:

* Did net performance survive costs?
* Did it beat the benchmark?
* Did drawdown improve?
* Did turnover destroy the result?
* Did the out-of-sample period hold up?

Every chart must include a short takeaway.

No chart may appear without interpretation.

## Interaction Rules

Allowed interactions:

* signal selector
* gross/net toggle
* benchmark selector
* cost scenario selector
* parameter comparison
* verdict change indicator
* methodology drawer

Do not add interactions that only look impressive.

Every interaction must change the user’s interpretation.

## User Overwhelm Rules

The design must actively prevent overload.

Required:

* short section intros
* clear labels
* visible current signal state
* limited metrics per view
* collapsible methodology
* concise chart annotations
* one primary action per section

Avoid:

* too many simultaneous charts
* too many toggles
* dense tables
* unexplained abbreviations
* long research paragraphs
* small unreadable labels
* unclear scroll behavior

## Typography

Use distinctive, readable typography.

Typography must feel precise, modern, and non-generic.

Use a clear hierarchy:

* strong display type for section identity
* readable body type
* compact technical type only where needed

## Forbidden Fonts

Do not use:

* Anthropic
* Fraunces
* Archivo
* IBM Plex
* Inter
* Geist
* Grotesk
* Grotesque
* Big Shoulder
* Saira
* Public
* Spline
* Arial
* Calibre
* Times New Roman
* JetBrains
* DM Mono
* DM Sans
* Newsreader

Do not use any variants of these families, including:

```text id="x4fkgg"
sans
serif
mono
display
condensed
text
variable
```

Choose alternative font families that are not related to the forbidden list.

## Color Direction

The color system must not look like a default quant dashboard.

Avoid default dark-gray, blue-gray, white-text finance styling.

Use a distinctive palette that supports:

* signal states
* stress states
* verdict classification
* data readability
* section hierarchy

## Forbidden Dark Theme Colors / Tints

For dark themes, do not use:

* Cyan
* Steel
* Graphite
* Amber
* Gold
* Yellow
* Orange
* Slate

## Forbidden Light Theme Colors / Tints

For light themes, do not use:

* Warm
* Beige
* Pure White
* Cream
* Off-white
* White
* Gold
* Amber
* Yellow

## Verdict Visual Language

Verdicts must be visually distinct.

Required classifications:

```text id="o9lwp8"
Survived
Conditional
Rejected
```

Do not rely only on color. Use labels, icons, structure, and text.

Each verdict card must show:

* result
* evidence
* weakness
* best use case
* final note

## Motion and Depth

Use motion to guide comprehension.

Motion should help users understand:

* signal selection
* evidence progression
* stress-test changes
* verdict changes

Avoid decorative animation that distracts from research.

Depth is encouraged, but clarity is mandatory.

## Chart Design

Charts must be clean and readable.

Rules:

* large labels
* limited series per chart
* no unnecessary grid clutter
* consistent scales where comparison matters
* visible benchmark context
* clear net-of-cost distinction
* takeaway attached to every chart

Avoid tiny multi-line legends and dense heatmaps.

## Responsive Rules

The site must work on:

* desktop
* laptop
* tablet
* mobile

No overlapping text, clipped cards, broken sticky sections, unreadable charts, or hidden controls.

Laptop readability is mandatory.

## Content Rules

Use plain English first.

Avoid unexplained jargon.

Do not write long paragraphs inside UI sections.

Use concise copy:

```text id="s1xirb"
What we test
What happened
What changed under stress
What verdict follows
```

## Accessibility Rules

Required:

* strong contrast
* keyboard-accessible controls
* readable font sizes
* visible focus states
* non-color-only status indicators
* responsive chart labels

## Hard Rules

* Do not build a generic dashboard.
* Do not make the site feel flat.
* Do not overwhelm users.
* Do not show charts without takeaways.
* Do not bury verdicts.
* Do not use forbidden fonts.
* Do not use forbidden colors.
* Do not make methodology the main experience.
* Do not create visual polish at the cost of comprehension.

The design succeeds if the user can understand the selected signal, inspect the evidence, stress the assumptions, and explain the verdict without feeling lost.
