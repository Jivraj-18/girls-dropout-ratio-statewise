# Girls' Education Dropout Analysis

**India's Data-Driven Analysis of Secondary Girls' Dropout Rates (2015-16 to 2021-22)**

## ⚡ TL;DR — The Headline

🎯 **Confirmed Data (2015-22):** India improved girls' secondary education retention by 32% in 7 years (18.26% → 12.46%).

📊 **Forecast (extrapolation only):** At current -1.4 pp/year rate, would reach 9.17% by 2024-25 IF trend continues. [Note: Actual 2023-24/2024-25 data not yet released by UDISE+]

🚨 **Action needed:** 5 states still lose 20%+ of girls — requiring targeted intervention now.

**For a 5-minute summary:** Start with [POLICY_BRIEF.md](POLICY_BRIEF.md)  
**For implementation action:** Start with [CRISIS_STATE_PLAYBOOK.md](CRISIS_STATE_PLAYBOOK.md)  
**For full analysis:** Start with [PRESENTATION.md](PRESENTATION.md)  

---

## 🎯 START HERE (Choose Your Path)

### 👔 **You're a Minister / Senior IAS Officer**
**Goal:** Understand the issue and approve action in 5 minutes  
**Read:**
1. [POLICY_BRIEF.md](POLICY_BRIEF.md) ← **Print this** (1 page, ₹425cr plan, ready to sign off)
2. 3 charts from `outputs/charts/` (for your slide deck)
3. Questions? See [PRESENTATION.md](PRESENTATION.md) Section 1-3

---

### 🔨 **You're a Collector / State Education Officer (IAS)**
**Goal:** Implement girls' dropout reduction in your state/district  
**Read:**
1. [CRISIS_STATE_PLAYBOOK.md](CRISIS_STATE_PLAYBOOK.md) ← **Complete action framework**
2. Fill out the 2-minute action plan template (in playbook)
3. Deep dive: [PRESENTATION.md](PRESENTATION.md) Sections 4-6 (driver analysis)
4. Track progress: Use RAG dashboard metrics (in playbook)

---

### 📊 **You're an Analyst / Researcher**
**Goal:** Understand methods and replicate analysis  
**Read:**
1. [METHODOLOGY.md](METHODOLOGY.md) — Full technical documentation
2. [docs/ANALYSIS_GUIDE.md](docs/ANALYSIS_GUIDE.md) — Deep methodology
3. Run: `python udise_pipeline.py all --skip-fetch`
4. Explore: `outputs/udise_state_caste_year_flow_rates.parquet` or `.csv`

---

### 🎓 **You're Curious / Want Full Context**
**Goal:** Understand the complete story (data → insights → recommendations)  
**Read:**
1. [PRESENTATION.md](PRESENTATION.md) — Full 11-section analysis
2. Review: Charts in `outputs/charts/`
3. Reference: [docs/DATASET_ASSESSMENT.md](docs/DATASET_ASSESSMENT.md) (data quality)

---

## 📈 The Findings (30-Second Read)

| What | Data | Why It Matters |
|:---|:---|:---|
| **Current Status** | 12.46% dropout (2021-22) | Down from 18.26% (32% improvement) |
| **Trend** | -1.40 pp/year consistently | System is working; can be maintained |
| **3-Year Outlook** | 9.17% by 2024-25 | Single digits reachable |
| **Critical Problem** | Odisha 25.28%; Bihar 21.45%; Assam 21.23% | 5 states lose >20% of girls at secondary |
| **Success Model** | Tripura -33pp; MP -23pp; CG -17pp | Rapid improvement IS possible with focus |
| **Key Insight** | Institutional capacity > Wealth | Punjab (rich) stagnates; Tripura (smaller) thrives |

---

## 📁 Repository Structure

```
📦 girl-dropout-rate-analysis
│
├── 📋 FOR PRESENTATIONS (Start here!)
│   ├── POLICY_BRIEF.md                ← 1-page for ministers (print-ready)
│   ├── CRISIS_STATE_PLAYBOOK.md       ← Action framework for IAS officers
│   └── PRESENTATION.md                ← Full analysis (11 sections)
│
├── 📊 FOR DATA EXPLORATION
│   ├── outputs/
│   │   ├── findings_udise_secondary_girls.md      (summary statistics)
│   │   ├── status_quo_forecast_secondary_girls.csv (3-year projection)
│   │   ├── udise_state_caste_year_flow_rates.csv  (full panel data)
│   │   └── charts/
│   │       ├── national_girls_dropout_trend.png
│   │       ├── state_ranking_secondary_girls_dropout_latest.png
│   │       └── heatmap_secondary_girls_dropout_top25.png
│
├── 🔧 FOR REPLICATION
│   ├── udise_pipeline.py              ← Main analysis script
│   ├── requirements.txt               ← Python dependencies
│   ├── METHODOLOGY.md                 ← How calculations work
│   └── docs/
│       ├── ANALYSIS_GUIDE.md          (detailed methods)
│       └── DATASET_ASSESSMENT.md      (data quality report)
│
└── 📝 REFERENCE
    └── DELIVERABLES.md               (what each file contains)
```

---

## 🚀 Quick Commands

### **Just Want to View Results (No Setup)**
Click the folder `outputs/` → see charts, CSV data, markdown findings

### **Want to Regenerate Analysis + Charts**
```bash
# Setup (one-time)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium

# Run analysis (uses existing data)
python udise_pipeline.py all --skip-fetch

# Output appears in: outputs/ folder
```

### **Want Fresh Data from UDISE**
```bash
python udise_pipeline.py fetch --years 16,17,18,19,20,21,22
python udise_pipeline.py build
python udise_pipeline.py charts
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
| **Best Improver** | Tripura -33.25 pp |
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
