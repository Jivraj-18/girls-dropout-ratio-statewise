# Girls Dropout Rate Analysis - India

**Status:** JSON-first analysis pipeline + static dashboard ready.  
**Date:** April 2026

## 📊 Interactive Dashboard (Start Here)

This repo now follows a **JSON-first** architecture:
- Python computes and writes JSON into `docs/data/`
- JavaScript renders charts in the browser from those JSON files

Open the dashboard:
- `docs/index.html`

## 🐍 Reproducible Analysis

Regenerate everything from raw UDISE+ CSV extracts:

Install dependencies (only needed if regenerating locally):

```bash
python -m pip install -r requirements.txt
```

```bash
./.venv/bin/python run_analysis.py
```

Because the dashboard uses `fetch()` to load JSON, serve `docs/` via a local HTTP server:

```bash
python3 -m http.server -d docs 8000
```

Then open `http://localhost:8000/`.

## GitHub Pages

This repo is ready for GitHub Pages using the `docs/` folder.

1) GitHub repo → **Settings** → **Pages**
2) **Build and deployment** → **Source**: Deploy from a branch
3) **Branch**: `main` (or your default branch) · **Folder**: `/docs`
4) Save, then open the URL GitHub shows

## 📁 Data Source

- **udise_csv_data/** — UDISE+ official education data (Ministry of Education, 2018-25)

## Key Outputs

- `docs/analysis_summary.json` — manifest of tasks + schema snapshots
- `docs/data/task_*.json` — per-task outputs (numbers + checksums + chart-ready data)
- `docs/audit_report.txt` — matched source filenames and join coverage notes

## Key Findings

- **Crisis:** Mizoram (worsening +5.9pp), West Bengal (worsening +1.5pp)
- **Opportunity:** Jharkhand (90% improvement: 22.4% → 2.4%)
- **Budget:** ₹420 Cr Year 1 for 5 crisis states
- **Impact:** 7-13pp dropout reduction possible with coordinated interventions

## 📎 See Also

