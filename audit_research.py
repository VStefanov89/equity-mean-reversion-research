"""Read-only aggregate audit of private research artifacts; never exports raw rows."""
import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq


def parquet_metadata(path, root):
    pf = pq.ParquetFile(path)
    names = pf.schema_arrow.names
    dates = [name for name in ("date", "entry_date", "exit_date", "year") if name in names]
    result = {
        "file": str(path.relative_to(root)),
        "rows": pf.metadata.num_rows,
        "columns": len(names),
        "date_columns": dates,
    }
    for name in dates:
        index = names.index(name)
        stats = [pf.metadata.row_group(i).column(index).statistics
                 for i in range(pf.metadata.num_row_groups)]
        valid = [s for s in stats if s and s.has_min_max]
        if valid:
            result[name + "_min"] = str(min(s.min for s in valid))
            result[name + "_max"] = str(max(s.max for s in valid))
    return result


def audit(root):
    notebook_name = "Find_triplets_on_weekly_basis.ipynb"
    notebook = json.loads((root / notebook_name).read_text())
    # Locate the recorded pair screen by code content rather than a fixed cell index.
    candidates = [c for c in notebook["cells"]
                  if "def evaluate_pair(" in "".join(c.get("source", []))]
    if len(candidates) != 1:
        raise ValueError("Expected one evaluate_pair cell; inspect notebook manually.")
    screen = candidates[0]
    lines = [line for output in screen.get("outputs", [])
             for line in "".join(output.get("text", [])).splitlines()
             if line.startswith("Pair ")]
    categories = Counter(
        "error" if ": ERROR:" in line else
        "selected" if ": Selected:" in line else
        "correlation" if ": Correlation below 0.7" in line else
        "zscore" if ": Absolute z-score below 1.8" in line else "other"
        for line in lines
    )
    files = [root / rel for rel in (
        "daily_signals.parquet", "triplets_for_ml.parquet",
        "Daily_signals/model_signals_trained.parquet",
        "Daily_signals/triplets_to_use_2026-09-19.parquet",
    )] + sorted((root / "Historical_signals").glob("*.parquet"))
    metadata = [parquet_metadata(f, root) for f in files]
    selected = pq.read_table(
        root / "triplets_for_ml.parquet",
        columns=["ticker1", "ticker2", "ticker3", "year"],
    ).to_pandas()
    keys = {tuple(sorted(map(str, row))) for row in
            selected[["ticker1", "ticker2", "ticker3"]].itertuples(index=False, name=None)}
    before = [r for r in metadata if "before_entry_signals" in r["file"]]
    intrade = [r for r in metadata if "intrade_signals" in r["file"]]
    annual = [year for year in range(2000, 2026)
              if (root / f"triplets_to_use_{year}.csv").exists()]
    validation = [year for year in range(2020, 2027)
                  if (root / f"Validation_Set_{year}.ipynb").exists()]
    fingerprints = [notebook_name, "Generate_triplets.ipynb", "utils_for_daily.py",
                    "utils_backtest_v2.py", "utils_portfolio_construction.py"]
    return {
        "scope": "Saved artifacts; not a fresh screening or backtest run",
        "pair_output_counts": dict(categories),
        "pair_evaluations": len(lines),
        "snapshot_reference_arithmetic": {
            "instruments": 478, "pairs": math.comb(478, 2),
            "possible_triplets": math.comb(478, 3),
            "expanded_candidate_rows": categories["selected"] * (478 - 2),
            "note": "478 is the documented snapshot universe, not inferred for new runs.",
        },
        "annual_candidate_file_years": annual,
        "annual_validation_notebooks": validation,
        "ml_triplet_selection_rows": len(selected),
        "ml_unique_unordered_triplets": len(keys),
        "ml_triplet_rows_by_year": {str(k): int(v) for k, v in selected.groupby("year").size().items()},
        "before_entry_rows_sum": sum(r["rows"] for r in before),
        "intrade_rows_sum": sum(r["rows"] for r in intrade),
        "row_sum_caveat": "Overlapping files; totals are not distinct trades.",
        "parquet_metadata": metadata,
        "source_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                          for name in fingerprints},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.source)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print("Aggregate audit written successfully.")
