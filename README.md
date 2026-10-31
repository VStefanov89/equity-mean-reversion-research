# Equity Mean-Reversion Research

**An independent quantitative research project by Vasil Stefanov, connecting equity-trading experience with Python, SQL, statistical modelling and portfolio analysis.**

I built a research workflow to investigate systematic mean reversion across equity and ETF pairs and three-instrument baskets (triplets). It covers market-data preparation, candidate generation, statistical screening, signal construction, model experiments and historical portfolio evaluation.

The question is whether a temporary deviation in a relationship between securities can support a repeatable trading rule—and how that conclusion changes when data quality, overlapping exposures, changing regimes and implementation assumptions are examined.

## Project scale: measured from saved artifacts

The following figures were checked against local notebook outputs and Parquet files on **31 October 2026**. They describe particular research artifacts, not a single production run or verified live performance.

| Measure | Verified scope |
|---|---|
| Historical candidate-generation coverage | Annual candidate files for **2000–2025**, plus a **2026** snapshot: 26 complete calendar-year labels plus one partial-year label |
| Universe in a saved weekly screening run | **478 instruments** |
| Pair evaluations recorded in that run | **114,003**, matching `478 choose 2`; no error lines in that saved output |
| Pairs retained by that screen | **1,082** (approximately **0.95%**) |
| Full triplet search space for that universe | **18,088,476** unordered combinations, matching `478 choose 3` |
| Candidate triplet rows produced from selected pairs | **515,032**, matching `1,082 × (478 − 2)` |
| Separate ML triplet-selection artifact | **529,400 rows**, representing **529,359 distinct unordered ticker triplets** |
| Model-signal artifact | **300,662 rows × 361 columns**, with dates spanning **30 June 1998–2 March 2026** |
| Annual validation notebooks | **7**, labelled **2020–2026**; 2026 is partial |
| Saved pre-entry history files | **4,544,198 rows** across seven files |
| Saved in-trade history files | **2,299,419 rows** across seven files |

**Counting matters:** the 18.1 million combinations are a generated search space, not 18.1 million completed backtests. Candidate rows are not independent strategies or executed trades. The two history-file totals include overlapping annual windows and have not been deduplicated. The 361 columns include identifiers, dates, prices and metadata as well as explanatory variables; they are not 361 independent predictive features. Earliest/latest dates do not imply continuous coverage or identical histories for every instrument.

See [the evidence register](EVIDENCE.md) and [machine-readable metrics](metrics.json) for sources and qualifications.

## What I built

### 1. Market-data and candidate workflows

- Download and store historical equity and ETF data using Nasdaq Data Link/Sharadar, MySQL and SQLAlchemy.
- Apply liquidity filters and construct candidate pairs and triplets.
- Use pair-first screening to narrow the triplet candidate set before more expensive research.
- Parallelise independent pair evaluations with a thread-pool implementation; the inspected screen configures 10 workers. No speedup benchmark is claimed.

### 2. Statistical spread research

For a three-instrument basket, the research spread is constructed from weighted log prices:

`spread(t) = w1 × log(P1(t)) + w2 × log(P2(t)) + w3 × log(P3(t))`

The research utilities include Johansen cointegration analysis, ADF stationarity checks, estimated mean-reversion half-life and standardised spread deviations. Signal construction explores multiple rolling windows, spread volatility, entropy and risk/reward measures.

The saved weekly pair screen is more limited: it filters price correlation and absolute z-score, using a Johansen eigenvector for spread weights. It **does not explicitly reject pairs using the Johansen trace statistic**. Passing that preliminary screen is therefore not proof of cointegration.

### 3. Signal features and model experiments

- Construct rolling price, return, volatility, regression and cross-instrument features.
- Include spread and market-context measurements, with SPY, TLT and GLD appearing in the research workflow.
- Explore entry-selection (gate) and in-trade continuation/tail-risk modelling, including LightGBM experiments and probability calibration in the broader notebooks.
- Maintain separate annual validation notebooks and model-drift analysis.

These are research components. Notebook names alone do not establish an independently validated out-of-sample pipeline or a deployed trading system.

### 4. Portfolio construction and monitoring

Portfolio utilities explore position overlap, opposing ticker exposures, buying-power constraints, sector/industry/ticker/pair concentration and PCA-based exposure diagnostics. Different notebook variants use different configurations; there is no universal cap asserted for all experiments.

The broader workflow includes daily signal updates and portfolio-dashboard work. This repository does not claim broker execution or audited live profitability.

## A concrete screening snapshot

The notebook's export is labelled **19 September 2026**. Its saved output records:

```text
478 instruments
  └─ 114,003 pair evaluations
       ├─ 97,811 rejected: price correlation below 0.70
       ├─ 15,110 rejected: absolute spread z-score below 1.80
       └─  1,082 retained
            └─ 515,032 candidate triplet rows
```

This reduces candidate rows to approximately **2.85%** of the full 18,088,476-combination triplet space. This is a **row-count comparison**, not a measured reduction in runtime: a triplet can be generated from more than one retained pair, and leg order can matter later in the workflow.

The pair screen uses the last **250 merged observations**, joined on date and observation type. They should not be described as 250 trading days without checking the observation frequency.

## Research standards and remaining work

- Verify chronological ordering, observation frequency, joins and duplicate keys before applying rolling calculations.
- Audit universe construction and delisted securities for survivorship and availability bias.
- Separate exploratory selection from genuinely untouched test periods; repeated model choices can contaminate an apparent holdout.
- Ensure feature computation is causal. Smoothing and full-sample transformations in exploratory variants require special review before using them in historical trading claims.
- Account consistently for commissions, spreads, slippage, short borrow, financing and executable position sizing.
- Reconcile trade logs, daily P&L and portfolio ledgers, and treat missing history as an unresolved issue rather than a favourable exit.
- Measure portfolio behaviour under competing positions and constraints, rather than summing standalone strategy returns.

No Sharpe ratio, CAGR, win rate or profit claim is published here because those figures need a separately reconciled, configuration-specific performance report.

## Repository contents

This public release is a **documented portfolio case study with an evidence audit**, not the full executable research platform.

- [Methodology](METHODOLOGY.md): what each research stage does and how to interpret it.
- [Evidence register](EVIDENCE.md): precise numerical claims and their source artifacts.
- [Metrics](metrics.json): aggregate metadata and selected source fingerprints, without raw observations.
- [Audit utility](audit_research.py): read-only verification against the author's local research artifacts; source data is not included.

Raw notebooks, market datasets, model binaries, personal records and credentials are excluded. The underlying data remains subject to its provider's terms. A future code release would require refactoring, secret removal and reproducibility checks.

## Technical stack

Python · SQL · MySQL · pandas · NumPy · SQLAlchemy · statsmodels · Jupyter · Parquet/PyArrow · LightGBM research experiments

## About the author

My background includes nine years in equity trading, followed by data-science and tax-data work. This personal project is independent of my employment and illustrates how I approach financial research: explicit hypotheses, measurable workflows and critical examination of results.
