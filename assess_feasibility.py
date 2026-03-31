from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "analysis" / "feasibility_assessment.json"


def _exists_any(patterns: list[str]) -> list[str]:
    matches: list[str] = []
    for pat in patterns:
        matches.extend([str(p.relative_to(ROOT)) for p in sorted(ROOT.glob(pat))])
    return matches


def main() -> None:
    ROOT.joinpath("analysis").mkdir(parents=True, exist_ok=True)

    # Semantic tables (numbers shift across years)
    dropout = _exists_any([
        "udise_csv_data/**/csv_files/*Table 5.13*Dropout Rate*gender*.csv",
        "udise_csv_data/**/csv_files/*Table 6.13*Dropout Rate*gender*.csv",
    ])
    promotion = _exists_any([
        "udise_csv_data/**/csv_files/*Table 5.11*Promotion Rate*gender*.csv",
        "udise_csv_data/**/csv_files/*Table 6.11*Promotion Rate*gender*.csv",
    ])
    repetition = _exists_any([
        "udise_csv_data/**/csv_files/*Table 5.12*Repetition Rate*gender*.csv",
        "udise_csv_data/**/csv_files/*Table 6.12*Repetition Rate*gender*.csv",
    ])

    infra_25 = _exists_any([
        "udise_csv_data/**/csv_files/*Table 2.5*Infrastructure*page*.csv",
        "udise_csv_data/**/csv_files/*Table 2.5*Infrastructure*.csv",
    ])

    ger = _exists_any([
        "udise_csv_data/**/csv_files/*Gross Enrolment Ratio (GER)*.csv",
    ])

    single_teacher = _exists_any([
        "udise_csv_data/**/csv_files/*Table 2.2*Schools, Enrolments and Teachers*.csv",
    ])

    female_teachers = _exists_any([
        "udise_csv_data/**/csv_files/*Table 4.13*Number of teachers by management, gender and classes taught*All Management*.csv",
    ])

    incentives = _exists_any([
        "udise_csv_data/**/csv_files/*incentive*.csv",
        "udise_csv_data/**/csv_files/*cycle*.csv",
        "udise_csv_data/**/csv_files/*uniform*.csv",
        "udise_csv_data/**/csv_files/*Table 5.18*Incentive*.csv",
    ])

    district_level = _exists_any([
        "udise_csv_data/**/csv_files/*District*.csv",
    ])

    vocational_ict = _exists_any([
        "udise_csv_data/**/csv_files/*ICT*.csv",
        "udise_csv_data/**/csv_files/*Vocational*.csv",
        "udise_csv_data/**/csv_files/*Table 6.2*ICT*.csv",
    ])

    social_category_dropout = _exists_any([
        "udise_csv_data/**/csv_files/*Dropout*SC*.csv",
        "udise_csv_data/**/csv_files/*Dropout*ST*.csv",
        "udise_csv_data/**/csv_files/*Dropout*Social*.csv",
    ])

    tasks = {
        "task_1_peak_attrition": {
            "feasible": bool(dropout and promotion and repetition),
            "requires": ["dropout", "promotion", "repetition"],
            "evidence": {
                "dropout_files": dropout[:5],
                "promotion_files": promotion[:5],
                "repetition_files": repetition[:5],
            },
            "granularity": "State/UT x year x level x gender",
        },
        "task_2_infrastructure_roi": {
            "feasible": bool(dropout and infra_25),
            "requires": ["dropout", "infrastructure"],
            "evidence": {"infra_files": infra_25[:5], "dropout_files": dropout[:5]},
            "granularity": "State/UT x year (for dropout) + State/UT x year (infra, 2022-23+)",
        },
        "task_3_female_teacher_multiplier": {
            "feasible": bool(dropout and female_teachers),
            "requires": ["dropout", "female_teacher_share"],
            "evidence": {"female_teacher_files": female_teachers[:3]},
            "notes": "Feasible using Table 4.13 (teachers by gender). In this repo, Table 2.4 is NOT female teachers.",
        },
        "task_4_peer_benchmarking": {
            "feasible": bool(dropout and ger),
            "requires": ["dropout", "ger"],
            "evidence": {"ger_files": ger[:5]},
        },
        "task_5_equity_gap": {
            "feasible": bool(social_category_dropout),
            "requires": ["dropout_by_social_category"],
            "evidence": {"candidate_files": social_category_dropout[:10]},
            "notes": "Not found in current dump (dropout appears by gender/level, not social category).",
        },
        "task_6_incentive_efficiency": {
            "feasible": bool(incentives),
            "requires": ["incentives_table"],
            "evidence": {"candidate_files": incentives[:10]},
            "notes": "The only Table 5.18 present is 'Gifted Children' (2021-22), not incentives.",
        },
        "task_7_single_teacher_risk": {
            "feasible": bool(dropout and single_teacher),
            "requires": ["dropout", "single_teacher"],
            "evidence": {"single_teacher_files": single_teacher[:3]},
        },
        "task_8_digital_hope": {
            "feasible": bool(dropout and infra_25 and vocational_ict),
            "requires": ["dropout", "infra_ict", "vocational_or_ict_table"],
            "evidence": {"vocational_ict_files": vocational_ict[:10]},
            "notes": "We have infra computer/internet coverage, but no separate vocational/ICT outcomes table in this dump.",
        },
        "task_9_red_zone_hotspots": {
            "feasible": bool(dropout),
            "requires": ["dropout"],
            "granularity": "State/UT only (no district series found)",
            "notes": "Feasible at State/UT level; district-level clustering requires district-wise dropout tables (not found).",
        },
        "task_10_sdg_forecast": {
            "feasible": bool(dropout),
            "requires": ["dropout"],
            "granularity": "Per state linear trend using 2018–2025",
        },
    }

    payload = {
        "generated_from": str(ROOT),
        "task_feasibility": tasks,
        "table_presence_summary": {
            "dropout_rate_files": len(dropout),
            "promotion_rate_files": len(promotion),
            "repetition_rate_files": len(repetition),
            "infrastructure_files": len(infra_25),
            "ger_files": len(ger),
            "single_teacher_files": len(single_teacher),
            "female_teacher_files": len(female_teachers),
            "district_level_files": len(district_level),
        },
    }

    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
