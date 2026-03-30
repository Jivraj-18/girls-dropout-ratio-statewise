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