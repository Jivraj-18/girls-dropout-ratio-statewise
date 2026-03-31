from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.udise_readers import read_multiheader_csv
from src.udise_utils import normalize_state_ut_name


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "analysis"


def profile_table(path: Path, table_id: str) -> dict:
    df, schema = read_multiheader_csv(path)

    # Try to normalize the first column as state/UT name for diagnostics
    state_col = df.columns[0] if len(df.columns) else None
    sample_states = []
    if state_col:
        sample_states = (
            df[state_col]
            .dropna()
            .astype(str)
            .head(20)
            .map(normalize_state_ut_name)
            .tolist()
        )

    missing = {c: int(df[c].isna().sum()) for c in df.columns}

    return {
        "table_id": table_id,
        "file": str(path.relative_to(ROOT)),
        "header_rows_detected": schema.header_rows,
        "n_rows": schema.n_rows,
        "n_cols": schema.n_cols,
        "flattened_columns": schema.detected_columns,
        "missing_cells_by_column": missing,
        "sample_state_ut_values_normalized": sample_states,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    t_513_2018 = ROOT / "udise_csv_data" / "2018-19" / "csv_files" / "Table 5.13 Dropout Rate by level of school education and gender, 2018-19 - page 83.csv"
    t_25_2024_p1 = ROOT / "udise_csv_data" / "2024-25" / "csv_files" / "Table 2.5 State wise highlights of the UDISE+ 2024-25 data Infrastructure,, - page 35.csv"
    t_25_2024_p2 = ROOT / "udise_csv_data" / "2024-25" / "csv_files" / "Table 2.5 (continued) State wise highlights of the UDISE+ 2024-25 data Infrastructure., - page 36.csv"

    if not t_513_2018.exists():
        raise FileNotFoundError(t_513_2018)
    if not t_25_2024_p1.exists():
        raise FileNotFoundError(t_25_2024_p1)
    if not t_25_2024_p2.exists():
        raise FileNotFoundError(t_25_2024_p2)

    discovery = {
        "dropout_rate_table_2018_19_table_5_13": profile_table(t_513_2018, "2018-19::Table 5.13 Dropout Rate"),
        "infrastructure_table_2024_25_table_2_5_page_35": profile_table(t_25_2024_p1, "2024-25::Table 2.5 Infrastructure (page 35)"),
        "infrastructure_table_2024_25_table_2_5_page_36": profile_table(t_25_2024_p2, "2024-25::Table 2.5 Infrastructure (page 36)"),
    }

    out_path = OUT_DIR / "schema_discovery.json"
    out_path.write_text(json.dumps(discovery, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
