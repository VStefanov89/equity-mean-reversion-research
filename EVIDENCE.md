# Evidence register

Audit date: **31 October 2026**. Sources are the author's private local artifacts. Only aggregate counts, date ranges and selected SHA-256 fingerprints are published. This audit reads saved state; it does not rerun market-data downloads, screening or backtests.

## Weekly screening snapshot

Source: `Find_triplets_on_weekly_basis.ipynb` (zero-based cell indices).

| Claim | Evidence |
|---|---|
| 478 instruments | Cell 26 saved scalar and cell 43 saved scalar |
| 18,088,476 generated triplets | Cells 29–30 saved scalar/table; independently matches C(478,3) |
| 114,003 generated pairs | Cells 32–33; independently matches C(478,2) |
| 114,003 evaluated pairs | Cell 34 contains exactly 114,003 `Pair ...` output lines |
| 97,811 correlation rejects | Recount of cell 34 output |
| 15,110 z-score rejects | Recount of cell 34 output |
| 1,082 selections | Recount of cell 34 output; cell 36 saved table shape |
| 0 recorded error lines | Cell 34 output recount; this is not a claim about other runs |
| 515,032 candidate triplet rows | Cells 48–49; verified against `Daily_signals/triplets_to_use_2026-09-19.parquet` metadata |
| 19 September 2026 snapshot label | Cell 53 export-date assignment and exported filename; notebook modification is later, so the filename alone does not prove the run's execution date |
| 250 rows, correlation 0.70, absolute z-score 1.80, 10 workers | Cell 34 source configuration |

The arithmetic reconciles: `97,811 + 15,110 + 1,082 = 114,003`.

## Historical coverage and dataset size

| Claim | Source and interpretation |
|---|---|
| Candidate-year files 2000–2025 | File inventory, supported by the annual assembly code in `Daily-Signal-Generator-Summary_and_triplets_for_ml.ipynb` |
| Additional 2026 candidate work | `triplets_to_use_2026-05-28.csv` and assembly notebook; partial year |
| 529,400 selection rows | `triplets_for_ml.parquet` footer metadata |
| 529,359 distinct unordered triplets | Count of sorted `(ticker1,ticker2,ticker3)` tuples in that file; 41 fewer than total rows |
| 20 represented year labels in selection file | Grouped row counts in `metrics.json`; this is a selected subset, not every annual candidate |
| 300,662 model-signal rows, 361 columns | `Daily_signals/model_signals_trained.parquet` footer metadata |
| 30 June 1998–2 March 2026 model-signal span | Parquet row-group date minima/maxima; does not establish continuity, training split or full coverage per asset |
| Seven annual validation notebooks | `Validation_Set_2020.ipynb` through `Validation_Set_2026.ipynb`; existence is not an independent performance certification |
| 4,544,198 pre-entry rows | Sum of seven `Historical_signals/before_entry_signals*.parquet` metadata counts |
| 2,299,419 in-trade rows | Sum of seven `Historical_signals/intrade_signals*.parquet` metadata counts |

Each of the seven `signals_YYYY_pass.parquet` files has 3,000 rows and 366 columns. In-trade files have 368 columns. Their schemas and periods differ from the separate model-signal artifact; these counts must not be added together as though they were one distinct trade population.

## Why no total for all combinations ever tested?

Candidate-generation lists, filtered candidates, daily signal rows and full backtests are different units. Some annual candidate files contain tens of millions of rows, while the assembly workflow selects subsets. A defensible lifetime total requires deduplicated execution logs across runs and configurations. The available weekly pair log supports an exact evaluation count for that snapshot; it does not justify treating every generated annual triplet row as a completed backtest.

## Reproduce the audit

With access to the private source artifacts and Python with `pandas` and `pyarrow`:

```sh
python audit_research.py --source /path/to/private/research --output /tmp/metrics.json
```

The utility reads files only and emits aggregate metadata. It does not read credentials from configuration files, connect to a database, call a data provider or publish raw rows. The public repository deliberately excludes the source artifacts, so readers without those files can check the arithmetic and evidence structure but cannot independently reproduce all counts.
