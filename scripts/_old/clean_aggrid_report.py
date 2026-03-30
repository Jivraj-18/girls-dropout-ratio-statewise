from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


def _norm(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    if not text or text.lower() == "nan":
        return None
    return text


def clean_aggrid_excel(
    input_path: str | Path,
    output_csv: str | Path,
    sheet: int | str = 0,
    header_rows: tuple[int, int, int] = (3, 4, 5),
    data_start_row: int = 6,
    stop_token: str = "..",
) -> pd.DataFrame:
    """Clean NIC/UDISE 'ag-grid' Excel exports into a flat table.

    These exports typically have:
    - a few metadata rows
    - multi-row headers with merged cells
    - data rows starting at a fixed offset

    This function forward-fills merged header cells horizontally and then
    composes a unique column name from (stage | metric | detail).
    """

    input_path = Path(input_path)
    output_csv = Path(output_csv)

    raw = pd.read_excel(input_path, sheet_name=sheet, header=None)
    if raw.empty:
        raise ValueError(f"No data found in {input_path}")

    stage_row, metric_row, detail_row = header_rows
    stage = raw.iloc[stage_row].copy()
    metric = raw.iloc[metric_row].copy()
    detail = raw.iloc[detail_row].copy()

    # Keep the first two identifier columns as-is.
    # Forward-fill merged header cells across the remaining columns.
    stage.iloc[:2] = None
    metric.iloc[:2] = None
    stage = stage.ffill()
    metric = metric.ffill()

    col_names: list[str] = []
    for j in range(raw.shape[1]):
        if j in (0, 1):
            name = _norm(detail.iat[j]) or f"col_{j}"
            col_names.append(name)
            continue

        parts = [
            _norm(stage.iat[j]),
            _norm(metric.iat[j]),
            _norm(detail.iat[j]),
        ]
        parts = [p for p in parts if p]
        col_names.append(" | ".join(parts) if parts else f"col_{j}")

    data = raw.iloc[data_start_row:].copy()
    data.columns = col_names

    first_col = col_names[0]
    data = data[data[first_col].notna()]
    data = data[data[first_col].astype(str).str.strip() != stop_token]
    data = data.dropna(axis=1, how="all").reset_index(drop=True)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_csv, index=False)
    return data


if __name__ == "__main__":
    # Example usage for the current workspace file.
    fixed_xlsx = (
        "Promotion Rate , Repetition Rate , Dropout Rate by Gender, Level of School "
        "Education and Social Category_Report type - National_22_fixed.xlsx"
    )
    out_csv = "national_22_promotion_repetition_dropout_clean.csv"
    df = clean_aggrid_excel(fixed_xlsx, out_csv)
    print(f"Wrote {out_csv} with shape {df.shape}")