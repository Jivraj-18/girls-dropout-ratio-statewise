from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import pandas as pd

from .udise_utils import TableSchema, normalize_whitespace


_COLNUM_RE = re.compile(r"^\(\s*1\s*\)$")


def read_multiheader_csv(path: Path) -> tuple[pd.DataFrame, TableSchema]:
    """Read UDISE-extracted CSVs that often have multi-row headers.

    Strategy:
    - Read raw with header=None.
    - Detect the row that contains column-number markers like '(1)'.
    - Build flat column names by concatenating non-empty header cells above.
    - Return the data rows below the marker row.

    This is intentionally tolerant of messy line breaks and stray empty columns.
    """

    raw = pd.read_csv(path, header=None, dtype=str, engine="python")

    # Drop columns that are entirely empty
    raw = raw.dropna(axis=1, how="all")

    header_end_idx: Optional[int] = None
    for idx in range(min(20, len(raw))):
        first_cell = str(raw.iat[idx, 0]) if raw.shape[1] > 0 else ""
        if _COLNUM_RE.match(normalize_whitespace(first_cell)):
            header_end_idx = idx
            break
        # Some files put (1) in the *second* column.
        if raw.shape[1] > 1:
            second_cell = str(raw.iat[idx, 1])
            if _COLNUM_RE.match(normalize_whitespace(second_cell)):
                header_end_idx = idx
                break

    if header_end_idx is None:
        # Fall back: treat first row as header if no marker line exists.
        header_end_idx = 0

    header_rows = list(range(header_end_idx))
    header_cells = raw.iloc[header_rows].fillna("") if header_rows else raw.iloc[[]]

    columns: list[str] = []
    for col_idx in range(raw.shape[1]):
        parts: list[str] = []
        for r in header_rows:
            cell = normalize_whitespace(str(raw.iat[r, col_idx]))
            if cell and cell.lower() not in {"nan", "none"}:
                parts.append(cell)
        col_name = normalize_whitespace(" ".join(parts)) if parts else f"col_{col_idx}"
        columns.append(col_name)

    # Ensure unique column names (UDISE exports can repeat header fragments).
    seen: dict[str, int] = {}
    unique_columns: list[str] = []
    for c in columns:
        base = c
        if base not in seen:
            seen[base] = 0
            unique_columns.append(base)
            continue
        seen[base] += 1
        unique_columns.append(f"{base}__{seen[base]}")

    data = raw.iloc[header_end_idx + 1 :].copy()
    data.columns = unique_columns

    # Trim whitespace in object columns.
    for col_idx, c in enumerate(list(data.columns)):
        series = data.iloc[:, col_idx]
        if series.dtype == object:
            data.iloc[:, col_idx] = series.astype(str).map(
                lambda x: normalize_whitespace(x) if x not in {"nan", "None"} else ""
            )

    # Drop fully blank rows
    data = data.replace({"": pd.NA}).dropna(axis=0, how="all").reset_index(drop=True)

    # Light schema snapshot
    sample_states: list[str] = []
    if len(data) > 0:
        first_col = data.columns[0]
        sample_states = (
            data[first_col]
            .dropna()
            .astype(str)
            .head(10)
            .map(normalize_whitespace)
            .tolist()
        )

    schema = TableSchema(
        file=str(path),
        header_rows=header_end_idx,
        detected_columns=unique_columns,
        n_rows=int(data.shape[0]),
        n_cols=int(data.shape[1]),
        sample_states=sample_states,
    )
    return data, schema
