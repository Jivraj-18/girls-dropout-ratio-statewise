# Girls' Education Dropout Analysis

**India's Data-Driven Analysis of Secondary Girls' Dropout Rates (2015-16 to 2021-22)**

## Overview

This project analyzes girls' secondary education dropout rates across India using official UDISE+ data. It reveals a **32% improvement** in girls' retention over 7 years, identifies regional success stories, and provides actionable recommendations for policymakers.

**Key Finding:** National secondary girls' dropout rate improved from **18.26% (2015-16) to 12.46% (2021-22)** — a -1.40 percentage point annual improvement rate.

---

## ✨ Quick Start

### View the Analysis

**For a complete briefing:**
- [`PRESENTATION.md`](PRESENTATION.md) — Complete data story (8 sections, ministerial-ready)
- [`DELIVERABLES.md`](DELIVERABLES.md) — Guide to all outputs and how to use them

### Run the Analysis

**Prerequisites:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

**Generate outputs:**
```bash
# Full analysis (fetch data + build + charts + findings)
python udise_pipeline.py all

# Or fetch new data only
python udise_pipeline.py fetch --years 16,17,18,19,20,21,22

# Or rebuild from existing data (faster)
python udise_pipeline.py all --skip-fetch
```

---

## 📁 Repository Structure

**Key files to use:**
```
├── PRESENTATION.md              ← Main deliverable (read this!)
├── DELIVERABLES.md              ← Guide to using outputs
├── METHODOLOGY.md               ← Technical details of calculations
├── README.md                    ← This file
│
├── udise_pipeline.py            ← Main analysis script
├── requirements.txt             ← Python dependencies
├── .gitignore                   ← Excludes generated files
│
├── docs/                        ← Documentation
│   ├── ANALYSIS_GUIDE.md        ← Deep-dive methodology
│   ├── DATASET_ASSESSMENT.md    ← Data quality report
│   └── archive/                 ← Historical notes
│
├── outputs/ (generated)         ← Analysis outputs
│   ├── findings_udise_secondary_girls.md
│   ├── status_quo_forecast_secondary_girls.csv
│   ├── udise_state_caste_year_flow_rates.parquet
│   └── charts/                  ← PNG visualizations
│
└── udise_api_dumps/ (generated) ← Raw UDISE data
```

---

## 📊 Quick Facts

| Metric | Value |
|--------|-------|
| **Current Dropout Rate** | 12.46% (2021-22) |
| **Previous Dropout Rate** | 18.26% (2015-16) |
| **Improvement** | 5.8 pp (32% reduction) |
| **Annual Trend** | -1.40 pp/year |
| **3-yr Projection** | 9.17% by 2024-25 |
| **Highest State** | Odisha 25.28% |
| **Lowest State** | Chandigarh 0.00% |

---

## 🎯 For Different Users

### **Policy Makers / Presenters**
1. **[POLICY_BRIEF.md](POLICY_BRIEF.md)** ← Start here! (1 page, ₹425cr intervention plan, ready to print)
2. **[CRISIS_STATE_PLAYBOOK.md](CRISIS_STATE_PLAYBOOK.md)** ← For IAS officers (4-step framework, 12-month roadmap, implementation checklist)
3. [`PRESENTATION.md`](PRESENTATION.md) ← Full analysis (15 min read)
4. Use charts from `outputs/charts/` for slides
5. See [`DELIVERABLES.md`](DELIVERABLES.md) for 120-min briefing outline

### **Data Analysts**
1. Run `python udise_pipeline.py all --skip-fetch`
2. Open `outputs/udise_state_caste_year_flow_rates.parquet` or `.csv`
3. See [`METHODOLOGY.md`](METHODOLOGY.md) for calculation details

### **Researchers**
1. Read [`docs/ANALYSIS_GUIDE.md`](docs/ANALYSIS_GUIDE.md) (full methodology)
2. Review [`docs/DATASET_ASSESSMENT.md`](docs/DATASET_ASSESSMENT.md) (data quality)
3. Replicate calculations or extend analysis

---

## 🔧 Common Commands

```bash
# Generate all outputs (fetch + analysis + charts)
python udise_pipeline.py all

# Generate from existing data (faster)
python udise_pipeline.py all --skip-fetch

# Just fetch new UDISE data
python udise_pipeline.py fetch

# Just build analysis panel
python udise_pipeline.py build

# Just generate charts
python udise_pipeline.py charts

# Just generate findings
python udise_pipeline.py findings

# Get help
python udise_pipeline.py --help
```

---

## 📈 Analysis Highlights

### Regional Disparities
- **Crisis states** (>20% dropout): Odisha, Meghalaya, Bihar, Assam, West Bengal
- **Success states** (<3% dropout): Chandigarh, Lakshadweep, Himachal Pradesh, Manipur, Tamilnadu

### Success Stories
- **Tripura:** -33.25 pp improvement (most improved)
- **Madhya Pradesh:** -23.23 pp improvement
- **Himachal Pradesh:** 0.91% dropout (best performer)

### Trajectory
- 2015-16: 18.26%
- 2021-22: 12.46%
- Forecast 2024-25: 9.17% (if trend holds)

---

## ✅ Data Quality

✓ Source: UDISE+ (official Ministry of Education)  
✓ Method: Cohort-flow analysis (standard in education analytics)  
✓ Validation: Verified against raw microdata  
✓ Trend: Aligns with Ministry's published figures  

See [`METHODOLOGY.md`](METHODOLOGY.md) for full technical details.

---

## 📝 Files in This Repo

**Should be in Git:**
- PRESENTATION.md
- DELIVERABLES.md
- METHODOLOGY.md
- README.md
- udise_pipeline.py
- requirements.txt
- docs/
- .gitignore

**Should NOT be in Git (see .gitignore):**
- outputs/ (generated)
- udise_api_dumps/ (raw data, large)
- .venv/ (virtual environment)
- __pycache__/ (compiled Python)
- *.parquet, *.log, etc.

---

## 🚀 To Use on GitHub

1. **Clone the repo:**
   ```bash
   git clone https://github.com/[user]/girl-dropout-rate-analysis.git
   cd girl-dropout-rate-analysis
   ```

2. **Setup environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

3. **Generate analysis:**
   ```bash
   python udise_pipeline.py all
   ```

4. **View results:**
   - Open `PRESENTATION.md` for briefing
   - Check `outputs/charts/` for visualizations
   - Use `outputs/*.csv` for data

---

## 📞 More Information

- **How to present it?** → See [`DELIVERABLES.md`](DELIVERABLES.md)
- **How were calculations done?** → See [`METHODOLOGY.md`](METHODOLOGY.md)
- **What's in the detailed analysis?** → See [`docs/ANALYSIS_GUIDE.md`](docs/ANALYSIS_GUIDE.md)
- **How good is the data?** → See [`docs/DATASET_ASSESSMENT.md`](docs/DATASET_ASSESSMENT.md)

---

**Last Updated:** March 31, 2024  
**Current Data:** Academic Year 2021-22  
**Status:** Production-Ready
