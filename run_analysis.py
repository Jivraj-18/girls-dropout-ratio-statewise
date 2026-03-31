from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.udise_loaders import (
    load_dropout_rates_all_years,
    load_female_teacher_share,
    load_ger_all_years,
    load_ict_labs_table,
    load_infrastructure_table,
    load_promotion_or_repetition_rates,
    load_single_teacher_risk,
)
from src.udise_numbers import (
    task10_sdg_forecast,
    task1_peak_attrition,
    task2_infrastructure_roi,
    task3_female_teacher_multiplier,
    task4_peer_benchmarking,
    task7_single_teacher_risk,
    task8_digital_hope,
    task9_red_zone_hotspots,
)


ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
DATA_DIR = DOCS / "data"
KNOWN_ANOMALIES_PATH = ROOT / "analysis" / "known_anomalies.json"

PIPELINE_VERSION = "2026-04-01"
SCHEMA_VERSION = 1


def _json_default(obj: Any) -> Any:
    # Make numpy/pandas scalars JSON serializable.
    if hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            pass
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _sanitize_for_json(obj: Any) -> Any:
    """Return a JSON-safe structure.

    Browsers reject NaN/Infinity in JSON (JSON.parse fails). Python's json.dumps
    allows them by default, so we proactively convert them to null.
    """

    # Common scalar normalizations
    if obj is None or isinstance(obj, (str, bool, int)):
        return obj

    # Numpy/pandas scalars
    if hasattr(obj, "item"):
        try:
            obj = obj.item()
        except Exception:
            pass

    # Float sanitization
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    # Pandas NA / NaT, etc. (guard against array return)
    try:
        is_na = pd.isna(obj)
        if isinstance(is_na, bool) and is_na:
            return None
    except Exception:
        pass

    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]

    return obj


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    safe = _sanitize_for_json(payload)
    path.write_text(
        json.dumps(
            safe,
            indent=2,
            ensure_ascii=False,
            default=_json_default,
            allow_nan=False,
        ),
        encoding="utf-8",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _schema_to_dict(schema: object) -> dict:
    return {
        "file": getattr(schema, "file", None),
        "header_rows": getattr(schema, "header_rows", None),
        "detected_columns": getattr(schema, "detected_columns", None),
        "n_rows": getattr(schema, "n_rows", None),
        "n_cols": getattr(schema, "n_cols", None),
        "sample_states": getattr(schema, "sample_states", None),
    }


def _validate_outputs(
    *,
    infra_year: str,
    dropout_long: pd.DataFrame,
    infra: pd.DataFrame,
    task_payloads: list[dict],
    known_anomalies: list[dict] | None = None,
) -> tuple[dict, bool]:
    """Return (validation_report, has_failures).

    Philosophy:
    - Always write the report.
    - Fail only on hard breaks: missing data, empty joins, implausible checksums.
    """

    def _status(severity: str, message: str, details: dict | None = None) -> dict:
        return {
            "severity": severity,  # pass|warn|fail
            "message": message,
            "details": details or {},
        }

    tasks_by_id = {int(t.get("task_id")): t for t in task_payloads if t.get("task_id") is not None}
    checks: list[dict] = []

    known_anomalies = known_anomalies or []

    def _match_known_anomaly(*, task_id: int, check: str, row: dict) -> dict | None:
        for anomaly in known_anomalies:
            try:
                if int(anomaly.get("task_id")) != int(task_id):
                    continue
                if str(anomaly.get("check")) != str(check):
                    continue
                match = anomaly.get("match") or {}
                ok = True
                for k, v in match.items():
                    if row.get(k) != v:
                        ok = False
                        break
                if ok:
                    return anomaly
            except Exception:
                continue
        return None

    # Coverage: dropout years
    years = sorted(set(dropout_long["year"].dropna().astype(str).tolist()))
    checks.append(
        _status(
            "pass" if len(years) >= 6 else "fail",
            "Dropout time series coverage",
            {"years": years, "n_years": len(years)},
        )
    )

    # Join-key sanity: infra vs dropout state count (excluding India)
    dropout_states = set(
        dropout_long[dropout_long["year"].eq(infra_year)]["state_ut"].dropna().astype(str).tolist()
    )
    dropout_states = {s for s in dropout_states if s.strip() and s.lower() != "nan"}
    dropout_states.discard("India")
    infra_states = set(infra["state_ut"].dropna().astype(str).tolist())
    infra_states = {s for s in infra_states if s.strip() and s.lower() != "nan"}
    infra_states.discard("India")
    missing_in_infra = sorted(dropout_states - infra_states)

    checks.append(
        _status(
            "pass" if len(infra_states) >= 30 else "fail",
            "Infrastructure state coverage",
            {
                "infra_year": infra_year,
                "n_dropout_states": len(dropout_states),
                "n_infra_states": len(infra_states),
                "missing_in_infra": missing_in_infra[:25],
            },
        )
    )

    # Task 1 checksum (promotion + repetition + dropout ≈ 100)
    t1 = tasks_by_id.get(1)
    if t1 and isinstance(t1.get("checksums"), dict):
        chk = (t1["checksums"].get("promotion_dropout_repetition_sum") or {})
        rows = chk.get("rows_checked")
        max_dev = chk.get("max_abs_deviation")
        rows_over_1pct = chk.get("rows_over_1pct")
        p95 = chk.get("p95_abs_deviation")
        worst_rows = chk.get("worst_10_rows") or []
        extreme_rows = 0
        known_matches = 0
        annotated_worst_rows: list[dict] = []
        try:
            for r in worst_rows:
                row = dict(r)
                anomaly = _match_known_anomaly(task_id=1, check="rate_sum_checksum", row=row)
                if anomaly is not None:
                    row["known_anomaly"] = {
                        "id": anomaly.get("id"),
                        "note": anomaly.get("note"),
                    }
                    known_matches += 1
                annotated_worst_rows.append(row)
            extreme_rows = sum(1 for r in worst_rows if (r.get("abs_deviation") or 0) >= 20)
        except Exception:
            extreme_rows = 0

        if not rows or rows < 100:
            checks.append(_status("fail", "Task 1 checksum has too few rows", chk))
        else:
            # Hard fail only if the checksum is *systematically* broken.
            # Rare extremes can happen due to structural artifacts/missing encodings in small UTs.
            severity = "pass"
            if p95 is not None and p95 > 5.0:
                severity = "fail"
            elif rows_over_1pct is not None and rows_over_1pct > 150:
                severity = "fail"
            elif max_dev is not None and max_dev > 20.0:
                severity = "warn" if extreme_rows <= 10 and (p95 is None or p95 <= 2.0) else "fail"
            checks.append(
                _status(
                    severity,
                    "Task 1 rate-sum checksum (promotion+repetition+dropout ~= 100)",
                    {
                        **chk,
                        "worst_10_rows": annotated_worst_rows if annotated_worst_rows else worst_rows,
                        "extreme_rows_in_worst_10_ge_20pp": extreme_rows,
                        "known_anomalies_matched_in_worst_10": known_matches,
                    },
                )
            )
    else:
        checks.append(_status("fail", "Task 1 output missing or malformed"))

    # Task 2 join coverage
    t2 = tasks_by_id.get(2)
    if t2 and isinstance(t2.get("checksums"), dict):
        jc = (t2["checksums"].get("join_coverage") or {})
        merged_rows = jc.get("merged_rows")
        if merged_rows is None:
            checks.append(_status("warn", "Task 2 join coverage missing", jc))
        else:
            severity = "pass" if merged_rows >= 30 else "fail"
            checks.append(_status(severity, "Task 2 join coverage", jc))
    else:
        checks.append(_status("fail", "Task 2 output missing or malformed"))

    # Task 7 sample size
    t7 = tasks_by_id.get(7)
    if t7:
        n = ((t7.get("findings") or {}).get("n_states"))
        if n is None:
            checks.append(_status("warn", "Task 7 sample size missing"))
        else:
            checks.append(
                _status(
                    "pass" if int(n) >= 25 else "fail",
                    "Task 7 sample size (states)",
                    {"n_states": int(n)},
                )
            )

    # Task presence
    required = [1, 2, 3, 4, 7, 9, 10]
    missing_tasks = [tid for tid in required if tid not in tasks_by_id]
    if missing_tasks:
        checks.append(_status("fail", "Missing required task outputs", {"missing_task_ids": missing_tasks}))
    else:
        checks.append(_status("pass", "Required task outputs present", {"required_task_ids": required}))

    has_failures = any(c["severity"] == "fail" for c in checks)
    overall = "fail" if has_failures else ("warn" if any(c["severity"] == "warn" for c in checks) else "pass")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": PIPELINE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "overall": overall,
        "known_anomalies": {
            "source": str(KNOWN_ANOMALIES_PATH.relative_to(ROOT)) if KNOWN_ANOMALIES_PATH.exists() else None,
            "published": "data/known_anomalies.json" if KNOWN_ANOMALIES_PATH.exists() else None,
            "rules_loaded": len(known_anomalies),
        },
        "checks": checks,
    }
    return report, has_failures


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Load core tables (discovery-driven)
    dropout_long, dropout_schemas = load_dropout_rates_all_years(ROOT)
    promotion_long, promotion_schemas = load_promotion_or_repetition_rates(ROOT, kind="promotion")
    repetition_long, repetition_schemas = load_promotion_or_repetition_rates(ROOT, kind="repetition")
    ger_long, ger_schemas = load_ger_all_years(ROOT)

    # 2) Load infra + single-teacher + female-teacher for a year where infra exists
    infra_year_candidates = ["2024-25", "2023-24", "2022-23"]
    infra: pd.DataFrame | None = None
    infra_year: str | None = None
    infra_schemas: dict[str, object] = {}
    for year in infra_year_candidates:
        try:
            infra, infra_schemas = load_infrastructure_table(ROOT, year=year)
            infra_year = year
            break
        except FileNotFoundError:
            continue

    if infra is None or infra_year is None:
        raise FileNotFoundError(
            "No infrastructure Table 2.5 found for 2022-23+; cannot run infra-dependent tasks"
        )

    single_teacher, single_teacher_schemas = load_single_teacher_risk(ROOT, year=infra_year)
    female_teachers, female_teacher_schemas = load_female_teacher_share(ROOT, year=infra_year)

    # 3) ICT labs (Table 9.9) for years where present in this repo
    ict_frames: list[pd.DataFrame] = []
    ict_schemas: dict[str, object] = {}
    for year in ["2024-25", "2023-24", "2022-23", "2021-22", "2020-21", "2019-20", "2018-19"]:
        try:
            ict, sch = load_ict_labs_table(ROOT, year=year)
        except FileNotFoundError:
            continue
        ict_schemas.update(sch)
        ict_frames.append(
            ict.rename(
                columns={
                    "pct_gov_functional_ict_labs": "govt_pct_functional",
                    "pct_aided_functional_ict_labs": "aided_pct_functional",
                    "pct_gov_ict_labs": "govt_pct_any",
                    "pct_aided_ict_labs": "aided_pct_any",
                }
            )
        )

    ict_long = pd.concat(ict_frames, ignore_index=True) if ict_frames else None

    # 4) Execute feasible tasks (numbers-only; JSON outputs)
    task_payloads: list[dict] = [
        task1_peak_attrition(dropout_long, promotion_long, repetition_long, gender="Girls"),
        task2_infrastructure_roi(infra, dropout_long, year=infra_year, gender="Girls"),
        task3_female_teacher_multiplier(female_teachers, dropout_long, year=infra_year, gender="Girls"),
        task4_peer_benchmarking(ger_long, dropout_long, year=infra_year, gender="Girls"),
        task7_single_teacher_risk(single_teacher, infra, dropout_long, year=infra_year, gender="Girls"),
        task9_red_zone_hotspots(
            dropout_long,
            gender="Girls",
            level="Secondary (9-10)",
            threshold=15.0,
            min_years=3,
        ),
        task10_sdg_forecast(dropout_long, gender="Girls", level="Secondary (9-10)", forecast_year=2030),
    ]
    if ict_long is not None:
        task_payloads.append(task8_digital_hope(ict_long, dropout_long, gender="Girls"))

    # 5) Audit: join coverage + schema snapshots
    latest_dropout_states = set(
        dropout_long[dropout_long["year"].eq(infra_year)]["state_ut"].dropna().unique().tolist()
    )
    infra_states = set(infra["state_ut"].dropna().unique().tolist())
    missing_in_infra = sorted(latest_dropout_states - infra_states)
    missing_in_dropout = sorted(infra_states - latest_dropout_states)

    audit_lines: list[str] = []
    audit_lines.append("JSON-FIRST ANALYSIS AUDIT")
    audit_lines.append("=")
    audit_lines.append(f"Generated at (UTC): {datetime.now(timezone.utc).isoformat()}")
    audit_lines.append(f"Infra year used for joins: {infra_year}")
    audit_lines.append(f"Dropout states/UTs ({infra_year}): {len(latest_dropout_states)}")
    audit_lines.append(f"Infrastructure states/UTs ({infra_year}): {len(infra_states)}")
    audit_lines.append(f"In dropout but missing in infra (first 25): {missing_in_infra[:25]}")
    audit_lines.append(f"In infra but missing in dropout (first 25): {missing_in_dropout[:25]}")
    audit_lines.append("")

    all_schemas: dict[str, object] = {
        **dropout_schemas,
        **promotion_schemas,
        **repetition_schemas,
        **ger_schemas,
        **infra_schemas,
        **single_teacher_schemas,
        **female_teacher_schemas,
        **ict_schemas,
    }

    audit_lines.append("TABLE FILES USED (DISCOVERY-BASED, NOT HARD-CODED)")
    audit_lines.append("=")
    for k, v in all_schemas.items():
        audit_lines.append(f"{k}: {getattr(v, 'file', None)}")
    audit_lines.append("")

    # 6) Write per-task JSON + summary index
    manifest_tasks = []
    for task in sorted(task_payloads, key=lambda t: int(t.get("task_id"))):
        tid = int(task["task_id"])
        out_path = DATA_DIR / f"task_{tid}.json"
        _write_json(out_path, task)
        manifest_tasks.append({"task_id": tid, "title": task.get("title"), "path": f"data/task_{tid}.json"})

    summary_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": PIPELINE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "focus": {"gender": "Girls", "infra_year": infra_year},
        "tasks": manifest_tasks,
        "schemas": {k: _schema_to_dict(v) for k, v in all_schemas.items()},
        "audit_report": "audit_report.txt",
        "validation_report": "data/validation_report.json",
        "notes": {
            "table_number_drift": "Table numbers shift across years; loaders search by title patterns.",
            "no_python_html": "Python writes JSON only; docs/ is rendered by JavaScript from JSON.",
        },
    }

    _write_json(DOCS / "analysis_summary.json", summary_payload)
    _write_text(DOCS / "audit_report.txt", "\n".join(audit_lines) + "\n")

    known_anomalies: list[dict] = []
    if KNOWN_ANOMALIES_PATH.exists():
        try:
            payload = json.loads(KNOWN_ANOMALIES_PATH.read_text(encoding="utf-8"))
            known_anomalies = payload.get("anomalies") or []
            # Publish into docs/ for transparency and offline review.
            _write_json(DATA_DIR / "known_anomalies.json", payload)
        except Exception:
            known_anomalies = []

    validation_report, has_failures = _validate_outputs(
        infra_year=infra_year,
        dropout_long=dropout_long,
        infra=infra,
        task_payloads=task_payloads,
        known_anomalies=known_anomalies,
    )
    _write_json(DATA_DIR / "validation_report.json", validation_report)
    if has_failures:
        raise SystemExit(
            "Validation failed. See docs/data/validation_report.json and docs/audit_report.txt for details."
        )


if __name__ == "__main__":
    main()
