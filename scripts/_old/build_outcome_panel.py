from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


DUMPS_DIR = Path("udise_api_dumps")
OUT_DIR = Path("outputs")


@dataclass(frozen=True)
class FlowKeys:
    prev: str
    next_total: str
    next_fresh: str
    repeat: str


def safe_div(numer: pd.Series, denom: pd.Series) -> pd.Series:
    denom = denom.astype("float64")
    numer = numer.astype("float64")
    out = numer / denom
    return out.where(denom.ne(0))


def compute_flow(df: pd.DataFrame, keys: FlowKeys, prefix: str) -> pd.DataFrame:
    prev = df[keys.prev].astype("float64")
    next_total = df[keys.next_total].astype("float64")
    next_fresh = df[keys.next_fresh].astype("float64")
    repeat = df[keys.repeat].astype("float64")

    promoted = next_total - next_fresh
    dropout = prev - promoted - repeat

    # avoid negative artifacts from reporting/rounding
    dropout = dropout.clip(lower=0)
    promoted = promoted.clip(lower=0)
    repeat = repeat.clip(lower=0)

    out = pd.DataFrame(
        {
            f"{prefix}_prev": prev,
            f"{prefix}_promoted": promoted,
            f"{prefix}_repeat": repeat,
            f"{prefix}_dropout": dropout,
            f"{prefix}_promotion_rate": safe_div(promoted, prev),
            f"{prefix}_repetition_rate": safe_div(repeat, prev),
            f"{prefix}_dropout_rate": safe_div(dropout, prev),
        }
    )
    return out


def load_tabular(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def year_from_name(path: Path) -> str:
    m = re.search(r"year(\d+)\.json$", path.name)
    if not m:
        raise ValueError(f"Could not parse year from filename: {path}")
    return m.group(1)


def build_panel() -> pd.DataFrame:
    files = sorted(DUMPS_DIR.glob("tabular_map117_stateall_year*.json"))
    if not files:
        raise SystemExit(
            "No multi-year dumps found. Run fetch_udise_via_playwright.py first."
        )

    frames: list[pd.DataFrame] = []

    for fp in files:
        y = year_from_name(fp)
        obj = load_tabular(fp)
        rows = obj.get("rowValue") or []
        if not rows:
            continue

        df = pd.DataFrame(rows)
        df.insert(0, "year_id", y)

        # Normalize identifiers
        # location_name: state/UT name; sometimes None for national row
        id_cols = ["year_id", "location_name", "caste_id", "caste_name"]
        missing = [c for c in id_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing expected id cols {missing} in {fp.name}")

        # Compute flows for each stage and each gender/total
        stage_defs: dict[str, dict[str, FlowKeys]] = {
            "primary": {
                "boy": FlowKeys(
                    prev="pri_boy_c1_c5_previous",
                    next_total="pri_boy_c2_c6_current",
                    next_fresh="pri_boy_c2_c6_current_fresh",
                    repeat="pri_boy_c1_c5_current_rptr",
                ),
                "girl": FlowKeys(
                    prev="pri_girl_c1_c5_previous",
                    next_total="pri_girl_c2_c6_current",
                    next_fresh="pri_girl_c2_c6_current_fresh",
                    repeat="pri_girl_c1_c5_current_rptr",
                ),
                "total": FlowKeys(
                    prev="pri_c1_c5_previous",
                    next_total="pri_c2_c6_current",
                    next_fresh="pri_c2_c6_current_fresh",
                    repeat="pri_c1_c5_current_rptr",
                ),
            },
            "upper_primary": {
                "boy": FlowKeys(
                    prev="upper_pri_boy_c6_c8_previous",
                    next_total="upper_pri_boy_c7_c9_current",
                    next_fresh="upper_pri_boy_c7_c9_current_fresh",
                    repeat="upper_pri_boy_c6_c8_current_rptr",
                ),
                "girl": FlowKeys(
                    prev="upper_pri_girl_c6_c8_previous",
                    next_total="upper_pri_girl_c7_c9_current",
                    next_fresh="upper_pri_girl_c7_c9_current_fresh",
                    repeat="upper_pri_girl_c6_c8_current_rptr",
                ),
                "total": FlowKeys(
                    prev="upper_pri_c6_c8_previous",
                    next_total="upper_pri_c7_c9_current",
                    next_fresh="upper_pri_c7_c9_current_fresh",
                    repeat="upper_pri_c6_c8_current_rptr",
                ),
            },
            "secondary": {
                "boy": FlowKeys(
                    prev="secondary_boy_c9_c10_previous",
                    next_total="secondary_boy_c10_c11_current",
                    next_fresh="secondary_boy_c10_c11_current_fresh",
                    repeat="secondary_boy_c9_c10_current_rptr",
                ),
                "girl": FlowKeys(
                    prev="secondary_girl_c9_c10_previous",
                    next_total="secondary_girl_c10_c11_current",
                    next_fresh="secondary_girl_c10_c11_current_fresh",
                    repeat="secondary_girl_c9_c10_current_rptr",
                ),
                "total": FlowKeys(
                    prev="secondary_c9_c10_previous",
                    next_total="secondary_c10_c11_current",
                    next_fresh="secondary_c10_c11_current_fresh",
                    repeat="secondary_c9_c10_current_rptr",
                ),
            },
        }

        computed: list[pd.DataFrame] = []
        for stage, genders in stage_defs.items():
            for gender, keys in genders.items():
                prefix = f"{stage}_{gender}"
                computed.append(compute_flow(df, keys, prefix))

        out = pd.concat([df[id_cols], *computed], axis=1)
        frames.append(out)

    panel = pd.concat(frames, ignore_index=True)

    # Add a friendlier year label for plots (heuristic)
    # UDISE archive uses tokens like 22 for 2022-23.
    panel["acad_year"] = panel["year_id"].apply(lambda y: f"20{int(y):02d}-20{int(y)+1:02d}")

    return panel


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    panel = build_panel()
    out_csv = OUT_DIR / "udise_state_caste_year_flow_rates.csv"
    out_parquet = OUT_DIR / "udise_state_caste_year_flow_rates.parquet"

    panel.to_csv(out_csv, index=False)
    panel.to_parquet(out_parquet, index=False)

    # Small sanity print
    print("rows", len(panel), "cols", len(panel.columns))
    print("years", sorted(panel["year_id"].unique().tolist()))
    print("locations", panel["location_name"].nunique(dropna=False))


if __name__ == "__main__":
    main()
