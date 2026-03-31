from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .udise_readers import read_multiheader_csv
from .udise_utils import (
    find_first_matching_file,
    normalize_state_ut_name,
    normalize_whitespace,
    to_number,
)


@dataclass(frozen=True)
class LoadedTable:
    df: pd.DataFrame
    schema: object


def _udise_year_dirs(root: Path) -> list[Path]:
    base = root / "udise_csv_data"
    years = []
    for child in base.iterdir():
        if child.is_dir() and (child / "csv_files").exists():
            years.append(child)
    return sorted(years)


def load_dropout_rates_all_years(root: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    """Load state-wise dropout rates (Primary / Upper Primary / Secondary; Boys/Girls/Total).

    2018-20: typically Table 5.13
    2021-25: typically Table 6.13

    Returns a long dataframe:
      year, state_ut, level, gender, rate
    """

    schemas: dict[str, object] = {}
    out_rows: list[pd.DataFrame] = []

    for year_dir in _udise_year_dirs(root):
        year = year_dir.name
        csv_dir = year_dir / "csv_files"

        dropout_file = find_first_matching_file(
            csv_dir,
            patterns=[
                "*Table 5.13*Dropout Rate*gender*.csv",
                "*Table 6.13*Dropout Rate*gender*.csv",
                "*Dropout Rate by level*gender*.csv",
            ],
        )

        df_raw, schema = read_multiheader_csv(dropout_file)
        schemas[f"dropout::{year}"] = schema

        # Identify the state column: usually first.
        state_col = df_raw.columns[0]
        df = df_raw.copy()
        df[state_col] = df[state_col].map(normalize_state_ut_name)

        # Drop invalid keys (None/empty/'nan') and in-body header repeats
        df = df[df[state_col].notna()]
        df = df[df[state_col].astype(str).str.strip().ne("")]
        df = df[~df[state_col].astype(str).str.lower().eq("nan")]

        # Keep only the first 10 columns if extra junk columns exist
        df = df.iloc[:, :10]

        # Standard positions in these tables:
        # 0 State
        # 1-3 Primary (B,G,T), 4-6 Upper Primary (B,G,T), 7-9 Secondary (B,G,T)
        expected_width = 10
        if df.shape[1] < expected_width:
            raise ValueError(f"Unexpected dropout table width for {year}: {df.shape[1]} columns in {dropout_file}")

        data = pd.DataFrame(
            {
                "year": year,
                "state_ut": df.iloc[:, 0],
                "primary_boys": to_number(df.iloc[:, 1]),
                "primary_girls": to_number(df.iloc[:, 2]),
                "primary_total": to_number(df.iloc[:, 3]),
                "upper_primary_boys": to_number(df.iloc[:, 4]),
                "upper_primary_girls": to_number(df.iloc[:, 5]),
                "upper_primary_total": to_number(df.iloc[:, 6]),
                "secondary_boys": to_number(df.iloc[:, 7]),
                "secondary_girls": to_number(df.iloc[:, 8]),
                "secondary_total": to_number(df.iloc[:, 9]),
            }
        )

        long = data.melt(
            id_vars=["year", "state_ut"],
            var_name="metric",
            value_name="rate",
        )
        long["level"] = long["metric"].str.split("_").str[0].replace(
            {
                "primary": "Primary (1-5)",
                "upper": "Upper Primary (6-8)",
                "secondary": "Secondary (9-10)",
            }
        )
        # Fix for 'upper_primary_*'
        long.loc[long["metric"].str.startswith("upper_primary"), "level"] = "Upper Primary (6-8)"

        long["gender"] = long["metric"].str.split("_").str[-1].str.title()
        long = long.drop(columns=["metric"])

        out_rows.append(long)

    all_long = pd.concat(out_rows, ignore_index=True)

    # Ensure consistent year order
    all_long["year_start"] = all_long["year"].str.slice(0, 4).astype(int)
    all_long = all_long.sort_values(["year_start", "state_ut", "level", "gender"]).drop(columns=["year_start"])

    return all_long, schemas


def load_promotion_or_repetition_rates(
    root: Path,
    kind: str,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """kind: 'promotion' | 'repetition'"""

    if kind not in {"promotion", "repetition"}:
        raise ValueError("kind must be 'promotion' or 'repetition'")

    table_patterns = {
        "promotion": [
            "*Table 5.11*Promotion Rate*gender*.csv",
            "*Table 6.11*Promotion Rate*gender*.csv",
            "*Promotion Rate by level*gender*.csv",
        ],
        "repetition": [
            "*Table 5.12*Repetition Rate*gender*.csv",
            "*Table 6.12*Repetition Rate*gender*.csv",
            "*Repetition Rate by level*gender*.csv",
        ],
    }[kind]

    schemas: dict[str, object] = {}
    out_rows: list[pd.DataFrame] = []

    for year_dir in _udise_year_dirs(root):
        year = year_dir.name
        csv_dir = year_dir / "csv_files"

        rate_file = find_first_matching_file(csv_dir, patterns=table_patterns)
        df_raw, schema = read_multiheader_csv(rate_file)
        schemas[f"{kind}::{year}"] = schema

        state_col = df_raw.columns[0]
        df = df_raw.copy()
        df[state_col] = df[state_col].map(normalize_state_ut_name)

        df = df[df[state_col].notna()]
        df = df[df[state_col].astype(str).str.strip().ne("")]
        df = df[~df[state_col].astype(str).str.lower().eq("nan")]
        df = df.iloc[:, :10]
        if df.shape[1] < 10:
            raise ValueError(f"Unexpected {kind} table width for {year}: {df.shape[1]} in {rate_file}")

        data = pd.DataFrame(
            {
                "year": year,
                "state_ut": df.iloc[:, 0],
                "primary_boys": to_number(df.iloc[:, 1]),
                "primary_girls": to_number(df.iloc[:, 2]),
                "primary_total": to_number(df.iloc[:, 3]),
                "upper_primary_boys": to_number(df.iloc[:, 4]),
                "upper_primary_girls": to_number(df.iloc[:, 5]),
                "upper_primary_total": to_number(df.iloc[:, 6]),
                "secondary_boys": to_number(df.iloc[:, 7]),
                "secondary_girls": to_number(df.iloc[:, 8]),
                "secondary_total": to_number(df.iloc[:, 9]),
            }
        )

        long = data.melt(id_vars=["year", "state_ut"], var_name="metric", value_name=kind)
        long["level"] = long["metric"].str.split("_").str[0].replace(
            {
                "primary": "Primary (1-5)",
                "upper": "Upper Primary (6-8)",
                "secondary": "Secondary (9-10)",
            }
        )
        long.loc[long["metric"].str.startswith("upper_primary"), "level"] = "Upper Primary (6-8)"
        long["gender"] = long["metric"].str.split("_").str[-1].str.title()
        long = long.drop(columns=["metric"])

        out_rows.append(long)

    all_long = pd.concat(out_rows, ignore_index=True)
    all_long["year_start"] = all_long["year"].str.slice(0, 4).astype(int)
    all_long = all_long.sort_values(["year_start", "state_ut", "level", "gender"]).drop(columns=["year_start"])
    return all_long, schemas


def load_infrastructure_table(root: Path, year: str) -> tuple[pd.DataFrame, dict[str, object]]:
    """Load Table 2.5 infrastructure for a given year (available in 2022-23+ in this repo).

    Returns a wide dataframe with one row per state/UT.
    """

    year_dir = root / "udise_csv_data" / year / "csv_files"
    files = sorted(year_dir.glob("*Table 2.5*Infrastructure*page*.csv"))
    if not files:
        files = sorted(year_dir.glob("*Table 2.5*Infrastructure*.csv"))
    if not files:
        raise FileNotFoundError(f"No Table 2.5 Infrastructure files found for {year} in {year_dir}")

    schemas: dict[str, object] = {}
    frames: list[pd.DataFrame] = []

    for f in files:
        df_raw, schema = read_multiheader_csv(f)
        schemas[f"infra::{year}::{Path(f).name}"] = schema

        df = df_raw.copy().dropna(axis=1, how="all")

        # Identify the state/UT column by header text (do NOT drop 'Total Schools').
        normalized_cols = {c: normalize_whitespace(str(c)).lower() for c in df.columns}
        state_candidates = [
            c
            for c, cl in normalized_cols.items()
            if ("state" in cl and "ut" in cl) or cl in {"state/ut", "state /ut", "india/state/ut", "india/state /ut"}
        ]
        if not state_candidates:
            # Fall back to the first column.
            state_col = df.columns[0]
        else:
            state_col = state_candidates[0]

        df["state_ut"] = df[state_col].map(normalize_state_ut_name)
        df = df[df["state_ut"].notna()]
        df = df[df["state_ut"].astype(str).str.strip().ne("")]
        df = df[~df["state_ut"].astype(str).str.lower().eq("nan")]
        df = df.drop(columns=[state_col])

        # Convert likely-numeric columns
        for c in df.columns:
            if c == "state_ut":
                continue
            df[c] = pd.to_numeric(
                df[c]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
                .replace({"-": pd.NA, "": pd.NA, "nan": pd.NA}),
                errors="coerce",
            )

        frames.append(df)

    merged = frames[0]
    for f in frames[1:]:
        merged = merged.merge(f, on="state_ut", how="outer", suffixes=("", "_dup"))
        # Drop duplicate columns created by overlaps
        dup_cols = [c for c in merged.columns if c.endswith("_dup")]
        if dup_cols:
            merged = merged.drop(columns=dup_cols)

    # Standardize a small set of core columns if we can infer them
    # Try to find total schools
    total_candidates = [c for c in merged.columns if "Total" in c and "School" in c]
    if total_candidates:
        merged = merged.rename(columns={total_candidates[0]: "total_schools"})

    return merged, schemas


def load_single_teacher_risk(root: Path, year: str) -> tuple[pd.DataFrame, dict[str, object]]:
    """Load Table 2.2 (Schools, Enrolments and Teachers) and extract single-teacher fields."""

    csv_dir = root / "udise_csv_data" / year / "csv_files"
    file_path = find_first_matching_file(
        csv_dir,
        patterns=[
            "*Table 2.2*Schools, Enrolments and Teachers*.csv",
            "*Table 2.2*Schools, Enrolments and Teachers*page*.csv",
        ],
    )

    df_raw, schema = read_multiheader_csv(file_path)

    df = df_raw.copy().dropna(axis=1, how="all")
    state_col = df.columns[0]
    df["state_ut"] = df[state_col].map(normalize_state_ut_name)
    df = df[df["state_ut"].notna()]
    df = df[df["state_ut"].astype(str).str.strip().ne("")]
    df = df[~df["state_ut"].astype(str).str.lower().eq("nan")]

    # Table 2.2 has total number of schools as the next column in this dump.
    if df.shape[1] < 2:
        raise ValueError(f"Unexpected Table 2.2 width for {year}: {df.shape[1]} in {file_path}")
    total_schools = pd.to_numeric(df.iloc[:, 1], errors="coerce")

    cols = {c: normalize_whitespace(c).lower() for c in df.columns}
    single_teacher_schools_col = None
    single_teacher_enrol_col = None

    for c, cl in cols.items():
        if "schools" in cl and "single" in cl and "teacher" in cl:
            single_teacher_schools_col = c
        if "enrol" in cl and "single" in cl and "teacher" in cl:
            single_teacher_enrol_col = c

    if single_teacher_schools_col is None:
        raise ValueError(f"Could not find 'Schools with Single Teachers' column in {file_path}")

    out = pd.DataFrame(
        {
            "year": year,
            "state_ut": df["state_ut"],
            "total_schools": total_schools,
            "schools_with_single_teacher": pd.to_numeric(df[single_teacher_schools_col], errors="coerce"),
        }
    )
    if single_teacher_enrol_col is not None:
        out["enrolments_in_single_teacher_schools"] = pd.to_numeric(df[single_teacher_enrol_col], errors="coerce")

    return out, {f"single_teacher::{year}": schema}


def load_female_teacher_share(root: Path, year: str) -> tuple[pd.DataFrame, dict[str, object]]:
    """Load Table 4.13 (All management) and compute female teacher share by state."""

    csv_dir = root / "udise_csv_data" / year / "csv_files"
    file_path = find_first_matching_file(
        csv_dir,
        patterns=["*Table 4.13*Number of teachers by management, gender and classes taught*All Management*.csv"],
    )

    df_raw, schema = read_multiheader_csv(file_path)

    df = df_raw.copy().dropna(axis=1, how="all")
    state_col = df.columns[0]
    df["state_ut"] = df[state_col].map(normalize_state_ut_name)
    df = df[df["state_ut"].notna()]
    df = df[df["state_ut"].astype(str).str.strip().ne("")]
    df = df[~df["state_ut"].astype(str).str.lower().eq("nan")]

    # Detect the 'Total Male', 'Total Female', 'Total Total' columns by header fragments
    # In these tables, columns 1,2,3 are typically Male/Female/Total under 'Total'
    if df.shape[1] < 4:
        raise ValueError(f"Unexpected Table 4.13 shape in {file_path}: {df.shape}")

    male = pd.to_numeric(df.iloc[:, 1], errors="coerce")
    female = pd.to_numeric(df.iloc[:, 2], errors="coerce")
    total = pd.to_numeric(df.iloc[:, 3], errors="coerce")

    out = pd.DataFrame(
        {
            "year": year,
            "state_ut": df["state_ut"],
            "teachers_male": male,
            "teachers_female": female,
            "teachers_total": total,
        }
    )
    out["female_teacher_share"] = out["teachers_female"] / out["teachers_total"]
    return out, {f"female_teachers::{year}": schema}


def load_ger_all_years(root: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    """Load Gross Enrolment Ratio (GER) tables across years.

    2018-20: commonly Table 5.1/5.2/5.3 (same schema family)
    2021-25: commonly Table 6.1 (All Social Groups)

    Returns long dataframe:
      year, state_ut, level, gender, ger
    """

    schemas: dict[str, object] = {}
    out_rows: list[pd.DataFrame] = []

    for year_dir in _udise_year_dirs(root):
        year = year_dir.name
        csv_dir = year_dir / "csv_files"

        # Prefer the broadest/all-social-groups version where available.
        ger_file = None
        for patterns in [
            ["*Table 6.1*Gross Enrolment Ratio (GER)*All Social Groups*.csv"],
            ["*Table 6.1*Gross Enrolment Ratio (GER)*.csv"],
            ["*Table 5.1*Gross Enrolment Ratio (GER)*.csv"],
            ["*Gross Enrolment Ratio (GER) by Gender and Level*.csv"],
        ]:
            try:
                ger_file = find_first_matching_file(csv_dir, patterns=patterns)
                break
            except FileNotFoundError:
                continue

        if ger_file is None:
            continue

        df_raw, schema = read_multiheader_csv(ger_file)
        schemas[f"ger::{year}"] = schema

        state_col = df_raw.columns[0]
        df = df_raw.copy()
        df[state_col] = df[state_col].map(normalize_state_ut_name)
        df = df[df[state_col].notna()]
        df = df[df[state_col].astype(str).str.strip().ne("")]
        df = df[~df[state_col].astype(str).str.lower().eq("nan")]

        # GER tables are typically:
        # 1 state + (levels) * (Boys,Girls,Total)
        # We infer levels from expected width; handle both 16-col (5 levels) and 10-col (3 levels) variants.
        n = df.shape[1]
        if n >= 16:
            df = df.iloc[:, :16]
            data = pd.DataFrame(
                {
                    "year": year,
                    "state_ut": df.iloc[:, 0],
                    "primary_boys": to_number(df.iloc[:, 1]),
                    "primary_girls": to_number(df.iloc[:, 2]),
                    "primary_total": to_number(df.iloc[:, 3]),
                    "upper_primary_boys": to_number(df.iloc[:, 4]),
                    "upper_primary_girls": to_number(df.iloc[:, 5]),
                    "upper_primary_total": to_number(df.iloc[:, 6]),
                    "elementary_boys": to_number(df.iloc[:, 7]),
                    "elementary_girls": to_number(df.iloc[:, 8]),
                    "elementary_total": to_number(df.iloc[:, 9]),
                    "secondary_boys": to_number(df.iloc[:, 10]),
                    "secondary_girls": to_number(df.iloc[:, 11]),
                    "secondary_total": to_number(df.iloc[:, 12]),
                    "higher_secondary_boys": to_number(df.iloc[:, 13]),
                    "higher_secondary_girls": to_number(df.iloc[:, 14]),
                    "higher_secondary_total": to_number(df.iloc[:, 15]),
                }
            )
            long = data.melt(id_vars=["year", "state_ut"], var_name="metric", value_name="ger")
            long["level"] = long["metric"].str.rsplit("_", n=1).str[0].replace(
                {
                    "primary": "Primary (1-5)",
                    "upper_primary": "Upper Primary (6-8)",
                    "elementary": "Elementary (1-8)",
                    "secondary": "Secondary (9-10)",
                    "higher_secondary": "Higher Secondary (11-12)",
                }
            )
            long["gender"] = long["metric"].str.rsplit("_", n=1).str[-1].str.title()
            long = long.drop(columns=["metric"])
            out_rows.append(long)
        elif n >= 10:
            # Some early-year files in this repo may appear in the 3-level form.
            df = df.iloc[:, :10]
            data = pd.DataFrame(
                {
                    "year": year,
                    "state_ut": df.iloc[:, 0],
                    "primary_boys": to_number(df.iloc[:, 1]),
                    "primary_girls": to_number(df.iloc[:, 2]),
                    "primary_total": to_number(df.iloc[:, 3]),
                    "upper_primary_boys": to_number(df.iloc[:, 4]),
                    "upper_primary_girls": to_number(df.iloc[:, 5]),
                    "upper_primary_total": to_number(df.iloc[:, 6]),
                    "secondary_boys": to_number(df.iloc[:, 7]),
                    "secondary_girls": to_number(df.iloc[:, 8]),
                    "secondary_total": to_number(df.iloc[:, 9]),
                }
            )
            long = data.melt(id_vars=["year", "state_ut"], var_name="metric", value_name="ger")
            long["level"] = long["metric"].str.rsplit("_", n=1).str[0].replace(
                {
                    "primary": "Primary (1-5)",
                    "upper_primary": "Upper Primary (6-8)",
                    "secondary": "Secondary (9-10)",
                }
            )
            long["gender"] = long["metric"].str.rsplit("_", n=1).str[-1].str.title()
            long = long.drop(columns=["metric"])
            out_rows.append(long)

    if not out_rows:
        return pd.DataFrame(columns=["year", "state_ut", "level", "gender", "ger"]), schemas

    all_long = pd.concat(out_rows, ignore_index=True)
    all_long["year_start"] = all_long["year"].str.slice(0, 4).astype(int)
    all_long = all_long.sort_values(["year_start", "state_ut", "level", "gender"]).drop(columns=["year_start"])
    return all_long, schemas


def load_ict_labs_table(root: Path, year: str) -> tuple[pd.DataFrame, dict[str, object]]:
    """Load Table 9.9 ICT labs availability for Govt/Govt Aided schools (state-wise).

    Returns tidy dataframe:
      year, state_ut,
      pct_gov_ict_labs, pct_gov_functional_ict_labs,
      pct_aided_ict_labs, pct_aided_functional_ict_labs
    """

    csv_dir = root / "udise_csv_data" / year / "csv_files"
    file_path = find_first_matching_file(
        csv_dir,
        patterns=["*Table 9.9*having ICT*.csv", "*Table 9.9*ICT*.csv"],
    )

    df_raw, schema = read_multiheader_csv(file_path)

    df = df_raw.copy().dropna(axis=1, how="all")
    state_col = df.columns[0]
    df["state_ut"] = df[state_col].map(normalize_state_ut_name)
    df = df[df["state_ut"].notna()]
    df = df[df["state_ut"].astype(str).str.strip().ne("")]
    df = df[~df["state_ut"].astype(str).str.lower().eq("nan")]

    # This table’s last four numeric columns are percentage fields:
    # (8) Govt ICT labs %, (9) Govt Functional ICT labs %, (10) Aided ICT labs %, (11) Aided Functional ICT labs %
    if df.shape[1] < 11:
        raise ValueError(f"Unexpected Table 9.9 width for {year}: {df.shape[1]} in {file_path}")

    pct_gov_ict = pd.to_numeric(df.iloc[:, 7], errors="coerce")
    pct_gov_func = pd.to_numeric(df.iloc[:, 8], errors="coerce")
    pct_aided_ict = pd.to_numeric(df.iloc[:, 9], errors="coerce")
    pct_aided_func = pd.to_numeric(df.iloc[:, 10], errors="coerce")

    out = pd.DataFrame(
        {
            "year": year,
            "state_ut": df["state_ut"],
            "pct_gov_ict_labs": pct_gov_ict,
            "pct_gov_functional_ict_labs": pct_gov_func,
            "pct_aided_ict_labs": pct_aided_ict,
            "pct_aided_functional_ict_labs": pct_aided_func,
        }
    )
    return out, {f"ict_labs::{year}": schema}
