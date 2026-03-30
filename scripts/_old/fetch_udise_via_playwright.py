from __future__ import annotations

import json
from pathlib import Path

from datetime import datetime, timezone

from playwright.sync_api import sync_playwright


def post_text_plain(request, url: str, payload: dict) -> tuple[int, str]:
    resp = request.post(url, data=json.dumps(payload), headers=COMMON_HEADERS)
    return resp.status, resp.text()


def main() -> None:
    out_dir = Path("udise_api_dumps")
    out_dir.mkdir(exist_ok=True)

    run_meta = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "note": "Fetched via Playwright (browser context) and saved to disk.",
    }

    base = "https://dashboard.udiseplus.gov.in"
    archive_url = f"{base}/udiseplus-archive/"
    tabular_url = f"{base}/BackEnd-master/api/report/getTabularData"
    master_url = f"{base}/BackEnd-master/api/report/getMasterData"

    global COMMON_HEADERS
    COMMON_HEADERS = {
        "Content-Type": "text/plain; charset=utf-8",
        "Accept": "application/json, text/plain, */*",
    }

    # Years: "22" corresponds to 2022-23 in the archive UI.
    # We'll probe a reasonable recent span; adjust if you need older years.
    years = ["16", "17", "18", "19", "20", "21", "22"]

    payloads: list[tuple[str, str, dict]] = [
        (
            "tabular_map117_national_year22",
            tabular_url,
            {
                "mapId": 117,
                "dependencyValue": json.dumps(
                    {"year": "22", "state": "national", "dist": "none", "block": "none"}
                ),
                "isDependency": "",
                "paramName": "civilian",
                "paramValue": "",
                "schemaName": "national",
                "reportType": "T",
            },
        ),
        (
            "tabular_map113_national_year22",
            tabular_url,
            {
                "mapId": 113,
                "dependencyValue": json.dumps(
                    {"year": "22", "state": "national", "dist": "none", "block": "none"}
                ),
                "isDependency": "",
                "paramName": "civilian",
                "paramValue": "",
                "schemaName": "national",
                "reportType": "T",
            },
        ),
        # State-wise time series (core table)
        *[
            (
                f"tabular_map117_stateall_year{y}",
                tabular_url,
                {
                    "mapId": "117",
                    "dependencyValue": json.dumps(
                        {"year": y, "state": "all", "dist": "none", "block": "none"}
                    ),
                    "isDependency": "Y",
                    "paramName": "civilian",
                    "paramValue": "",
                    "schemaName": "national",
                    "reportType": "T",
                },
            )
            for y in years
        ],
        # NOTE: mapId=113 is redundant with 117 (kept for one-year verification only)
        (
            "tabular_map113_stateall_year22",
            tabular_url,
            {
                "mapId": "113",
                "dependencyValue": json.dumps(
                    {"year": "22", "state": "all", "dist": "none", "block": "none"}
                ),
                "isDependency": "Y",
                "paramName": "civilian",
                "paramValue": "",
                "schemaName": "national",
                "reportType": "T",
            },
        ),
        (
            "master_get_state_year22",
            master_url,
            {"extensionCall": "GET_STATE", "condition": " where year_id='22' order by state_name"},
        ),
        (
            "master_get_district_all_year22",
            master_url,
            {
                "extensionCall": "GET_DISTRICT",
                "condition": "where udise_state_code= 'all' and ac_year ='22' order by district_name ",
            },
        ),
        (
            "master_get_district_kerala_year22",
            master_url,
            {
                "extensionCall": "GET_DISTRICT",
                "condition": "where udise_state_code= '32' and ac_year ='22' order by district_name ",
            },
        ),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(archive_url, wait_until="domcontentloaded")

        results: dict[str, dict] = {"_run": run_meta, "_archive_url": archive_url}
        for name, url, payload in payloads:
            status, text = post_text_plain(context.request, url, payload)
            out_path = out_dir / f"{name}.json"
            out_path.write_text(text, encoding="utf-8")
            results[name] = {
                "method": "POST",
                "url": url,
                "headers": dict(COMMON_HEADERS),
                "payload": payload,
                "status": status,
                "bytes": len(text.encode("utf-8")),
                "out": str(out_path),
            }

        (out_dir / "_requests_and_responses.json").write_text(
            json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(json.dumps(results, indent=2))

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
