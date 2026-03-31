### 📋 Task: Girl Dropout Rate Analysis Project

**Objective:** Develop a data-driven strategy to reduce girl dropout rates in schools to be presented to Additional Secretary/IAS officers.

- [ ] **Data Collection & Sources**
    - [x] Download public datasets from **UDISE** (multi-year state tables via dashboard API).
- [ ] **Data Analysis**
    - [ ] Identify the primary drivers of girl dropout ratios.
    - [x] Analyze how these ratios vary across different states (state ranking + heatmap + national trend).
    - [ ] Determine which "levers" (policy/infrastructure/social) have the biggest impact when controlled.
    - [x] Perform a "Status Quo" projection (simple linear trend forecast from 2016–2022 series).
- [ ] **Strategic Refinement**
    - [ ] Utilize an advanced AI model to think "smarter" about the problem.
    - [ ] Reframe the original questions or add additional relevant questions to strengthen the case.
- [ ] **Deliverable**
    - [ ] Create a **self-readable slide deck** suitable for presentation to a Minister.
- [ ] **Timeline**
    - [ ] Final output due by **tomorrow**.

### Current outputs

- `outputs/udise_state_caste_year_flow_rates.csv` (analysis-ready panel; includes computed promotion/repetition/dropout rates)
- `outputs/charts/` (core figures for the deck)
- `outputs/findings_udise_secondary_girls.md` (slide-ready bullets/tables)
- `outputs/status_quo_forecast_secondary_girls.csv` (status-quo forecast table)





## ✅ Skills Integrated

### Narrative Data Story Skill (data-story/SKILL.md)
- [x] Loaded and analyzed: Hook, Arc, Visualizations, Evidence, Caveats framework
- [x] Applied to project strategy
- [x] Created PROJECT_STRATEGY.md with story-driven approach

### Investigative Data Analysis Skill (data-analysis/SKILL.md)
- [x] Loaded and analyzed: Understand Data, Define What Matters, Hunt for Signal, Verify & Stress-Test
- [x] Applied to project structure
- [x] Created comprehensive analysis plan

### Data Source Integration (UDISE CSV Data)
- [x] Downloaded full dataset: 2018-19 to 2023-24 from https://github.com/gsidhu/udise-csv-data
- [x] Located dropout rate tables: Table 6.13 in each year's CSV
- [x] Verified structure: ~40 CSV files per year, organized by csv_files/ subfolder
- [x] Ready for extraction and integration

## 📋 Work Remaining

### Data Integration (High Priority)
- [ ] Extract girls' secondary dropout rates from all CSV years (2018-24)
- [ ] Validate 2021-22: Cross-check API data vs CSV data (should match)
- [ ] Build master dataset spanning 10 years (2015-16 to 2024-25)
- [ ] Add 2024-25 data from PDF extracts
- [ ] Merge state-wise, by gender, by social category

### Story Rewrite (Using Skills)
- [ ] Rewrite PRESENTATION.md using 4-beat story arc:
  - [ ] Hook: Open with tension/mystery, not statistics
  - [ ] Setup: Show the world as it appears
  - [ ] Complication: Reveal the plateau/crack
  - [ ] Revelation: State-level breakthrough (Tripura model)
  - [ ] Implications: Specific, actionable next steps
- [ ] Refresh visualizations with revelatory headlines
- [ ] Add "wait, really?" moment (surprising finding)
- [ ] Embed evidence in narrative flow

### Validation & Testing
- [ ] Cross-validate 2021-22 between API and CSV sources
- [ ] Test robustness: Is -1.4pp/year trend still valid over 10 years?
- [ ] Check for pattern breaks: Verify 2019 plateau exists in full data
- [ ] Stress-test findings: Do they hold when controlling for confounders?