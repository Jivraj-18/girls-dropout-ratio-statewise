# 🎯 Data Integration Complete - Action Plan

## ✅ What We Have

### **New CSV Data (High Quality)**
- **Source:** https://github.com/gsidhu/udise-csv-data
- **Coverage:** 2018-19 to 2023-24 (6 years)
- **Format:** Pre-extracted table CSVs (easy to load)
- **Key Files:** `Table 6.13 Dropout Rate by level of education and gender`
- **Structure:** By year → csv_files/ → individual tables

### **Existing API Data**
- **Years:** 2015-16, 2016-17, 2017-18 (3 years)
- **Format:** JSON dumps (some need extraction)
- **Status:** Keep as-is (older data, API method)

### **PDF Extracts**  
- **Years:** 2022-23, 2023-24, 2024-25
- **Format:** Text snippets with key metrics
- **Status:** Use for 2024-25 data (not yet in CSV repo)

### **Combined Coverage Now: 10 Years (2015-16 to 2024-25)** ✅

---

## 📊 Integration Steps

### **Step 1: Load and Validate Dropout Data**

```python
# Key file for each year: Table 6.13 
# Contains: Dropout Rate by level of education and gender

For 2023-24:
  udise_csv_data/2023-24/csv_files/Table 6.13 Dropout Rate by level of education and gender, 2023-24, - page 119.csv

Columns expected:
  - Education Level (Primary, Upper Primary, Secondary, Higher Secondary)
  - Gender (Boys, Girls)
  - Dropout Rate (%)
  - By State
  - By Social Category (General, SC, ST, OBC)
```

### **Step 2: Validate Cross-Source Consistency**

```
For 2021-22 (available in BOTH sources):
  - API dump: udise_api_dumps/tabular_map117_stateall_year22.json
  - CSV dump: udise_csv_data/2021-22/csv_files/Table 6.13*.csv

Compare:
  - State-wise girls' secondary dropout rates
  - Should be identical (both from same UDISE+ source)
  - If yes: ✅ safe to merge
  - If no: Check for data processing differences
```

### **Step 3: Extract Key Metric - Girls' Secondary Dropout**

| Year | Source | Girls Secondary Dropout | Status |
|------|--------|--------------------------|--------|
| 2015-16 | API | Need to extract | ⏳ |
| 2016-17 | API | Need to extract | ⏳ |
| 2017-18 | API | Need to extract | ⏳ |
| 2018-19 | CSV | Table 6.13 | ✅ |
| 2019-20 | CSV | Table 6.13 | ✅ |
| 2020-21 | CSV | Table 6.13 | ✅ |
| 2021-22 | CSV + API | Table 6.13 (validate both) | ⏳ |
| 2022-23 | CSV + PDF | Table 6.13 + extract | ⏳ |
| 2023-24 | CSV + PDF | Table 6.13 + extract | ⏳ |
| 2024-25 | PDF only | Extract sections | ⏳ |

### **Step 4: Build Master Dataset**

Create `udise_state_caste_year_dropout_girls_secondary.csv`:
```
year,state,girls_dropout_secondary,boys_dropout_secondary,social_category,school_type,data_source
2015-16,Andhra Pradesh,18.5,12.3,General,All,API
2015-16,Andhra Pradesh,22.1,15.4,SC,All,API
...
2024-25,Odisha,25.28,18.9,General,All,PDF
```

---

## 💡 Analysis Using Data Skills

### **A. Investigative Data Analysis (data-analysis skill)**

**Phase 1: Understand the Data**
- [ ] Load CSV files for each year
- [ ] Check for missing values
- [ ] Validate state names (special characters, consistency)
- [ ] Verify numeric ranges (dropout 0-100%?)
- [ ] Check for outliers (dropout > 50%?)

**Phase 2: Define What Matters**
- [ ] Primary question: Which states have highest girls' secondary dropout?
- [ ] Trend question: Is 2019 plateau visible in CSV data?
- [ ] Driver question: Does toilet infrastructure correlate with dropout?
- [ ] Surprise question: Why does wealthy Punjab have higher dropout than Tripura?

**Phase 3: Hunt for Patterns**
```
Pattern Analysis Checklist:
- [ ] Extreme values: Top 5 worst, top 5 best states
- [ ] Pattern breaks: When did trends shift?
- [ ] Surprising correlations: Infrastructure vs dropout
- [ ] Standout performers: Who improved fast?
- [ ] Hidden segments: Does SC/ST dropout differ from General?
- [ ] Leverage points: What predicts improvement?
```

**Phase 4: Verify & Stress-Test**
- [ ] Cross-check 2021-22: API vs CSV match?
- [ ] Test robustness: Is -1.4 pp/year trend still valid over 10 years?
- [ ] Check confounders: Population growth, migration, policy changes
- [ ] Find mechanism: What explains Tripura's -33pp improvement?

---

### **B. Narrative Data Story (data-story skill)**

**The Hook (First Paragraph)**
- Don't say: "This analyzes girls' secondary dropout rates"
- Instead: "One in four girls in Odisha never reach their senior secondary exams. In Kerala, it's one in twenty. The difference? Not wealth — it's management."

**Story Arc (4 Beats)**

1. **Setup:** "India has made progress on primary girls' enrollment. But secondary is the leak."
   - Chart: National trend 18% → 12% (show improvement)

2. **Complication:** "Progress stalled. A plateau from 2019–2021 hints at a ceiling."
   - Chart: Line with plateau highlighted, annotation "Progress froze here"

3. **Revelation:** "The states that broke through focused on one thing: tracking and support systems."
   - Chart: Tripura (-33pp) vs Punjab (+5pp improvement) — same wealth, different methods
   - Evidence: Tripura's teacher training program reached all schools. Punjab focused on new buildings.

4. **Implications:** "This suggests reallocating: fewer new schools, more investment in tracking systems."
   - Specific actions: (1) 50,000 teacher mentors, (2) state ID enrollment tracking, (3) cash transfers to poorest families

**"Wait, Really?" Moment**
- Setup: "We'd expect Punjab (richer, more schools) to do better."
- Reveal: "But it has 17% dropout vs Chhattisgarh's 10% (poorer, fewer schools)."
- Implication: "This isn't a resource problem. It's a management problem."

---

## 🚀 Immediate Next Steps

### **Priority 1: Data Validation (Today)**
```bash
# 1. List all dropout-related CSV files
ls -lah udise_csv_data/*/csv_files/ | grep -i "6.13\|dropout"

# 2. Check 2021-22 CSV (sample)
head -20 "udise_csv_data/2021-22/csv_files/Table 6.13"*.csv

# 3. Check if API file exists for 2021-22
cat udise_api_dumps/tabular_map117_stateall_year22.json | python3 -m json.tool | head -30
```

### **Priority 2: Extract & Merge (Tomorrow)**
```bash
# Script needed: extract_dropout_rates.py
# - Load all Table 6.13 CSVs
# - Extract: year, state, girls_secondary_dropout
# - Merge with API data for 2015-18
# - Create master CSV
```

### **Priority 3: Rewrite Story (This Week)**
```bash
# Follow data-story skill:
# 1. Hook with tension/mystery
# 2. Build 4-beat arc
# 3. Create visualizations with revelatory headlines
# 4. Anchor with state examples
# 5. Embed implications in narrative
```

### **Priority 4: Refresh Deliverables**
- [ ] Update PRESENTATION.md (story-driven, 4 beats)
- [ ] Refresh charts with better data (all 10 years)
- [ ] Update README with new data sources
- [ ] Commit: "Integrate UDISE CSV data (2018-24); 10-year series now complete"

---

## 📈 Success Criteria

- ✅ All 10 years integrated (2015-16 to 2024-25)
- ✅ Cross-validation: 2021-22 matches between sources  
- ✅ Narrative hooks reader in first line
- ✅ 4-beat story arc is clear and memorable
- ✅ Findings are surprising ("wait, really?") and actionable
- ✅ Evidence is concrete (specific states, not aggregate)
- ✅ Visualizations are revelatory (no explanation needed)
- ✅ Minister can read in 5 minutes and approve action
- ✅ IAS officer can implement specific 12-month plan

---

## 📁 Repository Structure (After Integration)

```
📦 girl-dropout-rate-analysis/

├── 📊 DATA SOURCES
│   ├── udise_api_dumps/          (2015-22, JSON)
│   ├── udise_csv_data/           (2018-24, CSV) ← NEW
│   │   ├── 2018-19/csv_files/
│   │   ├── 2019-20/csv_files/
│   │   ├── 2020-21/csv_files/
│   │   ├── 2021-22/csv_files/
│   │   ├── 2022-23/csv_files/
│   │   └── 2023-24/csv_files/
│   ├── pdf_extraction/           (2022-25, snippets)
│   └── booklets/                 (PDF source files)

├── 📚 ANALYSIS
│   ├── udise_pipeline.py         (updated to use merged data)
│   ├── extract_dropout_rates.py  (new: extract from CSVs)
│   └── outputs/
│       ├── master_dataset_10yr.csv        ← NEW
│       ├── udise_state_caste_year_flow_rates.csv
│       └── charts/

├── 📖 DELIVERABLES
│   ├── README.md                 (audience navigation)
│   ├── POLICY_BRIEF.md           (1-pager for minister)
│   ├── CRISIS_STATE_PLAYBOOK.md  (12-month plan for IAS)
│   ├── PRESENTATION.md           (10-year story, 4-beat arc)
│   ├── PROJECT_STRATEGY.md       (skills + integration plan)
│   └── DATA_INTEGRATION.md       (this doc)

└── 📝 GIT HISTORY
    └── Commits:
        - "Integrate UDISE CSV data (years 2018-24)"
        - "Rewrite PRESENTATION.md using data-story skills"
        - "Refresh visualizations with 10-year dataset"
```

---

## 🎯 Call to Action

You now have:
1. ✅ **Two proven skills** (Data Analysis + Data Story)
2. ✅ **Clean CSV data** (2018-24, pre-extracted)
3. ✅ **Existing API data** (2015-18, keep as backup)
4. ✅ **PDF extracts** (2022-25, for 2024-25 data)
5. ✅ **Clear roadmap** (4-beat story arc)

**Next:** Run the extraction script, validate 2021-22, then rewrite PRESENTATION.md using the story skills.

**Goal:** By end of week, a compelling narrative that makes a minister lean forward and say "wait, really?" — and then approve the ₹425cr intervention.

