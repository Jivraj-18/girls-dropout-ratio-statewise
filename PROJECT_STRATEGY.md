# 🎯 Project Strategy: Data-Driven Girl Dropout Analysis

**Using:** Data Analysis Skill + Data Story Skill  
**Data Source:** https://github.com/gsidhu/udise-csv-data (2018-19 to 2023-24)  
**Current Data:** API pulls (2015-22) + PDF extracts (2022-25)

---

## 📊 Phase 1: Investigative Data Analysis (SKILL: data-analysis)

### Step 1.1 — Understand the Data

**Current State:**
- API dumps: Years 2015-22 (2.5 MB, 10 files)
- PDF extracts: Years 2022-23, 2023-24, 2024-25 (snippets only)
- Data granularity: State-wise, by gender, by caste/social category

**Target State:**
- CSV data from udise-csv-data: Years 2018-19 to 2023-24 (clean, pre-extracted)
- Add 2024-25 from PDFs if available
- Total span: 10-year dataset (2015-16 to 2024-25)

**Data Quality Checks Needed:**
- [ ] Completeness: Missing values by year, state, category?
- [ ] Consistency: Do state names match across sources?
- [ ] Validation: Do 2021-22 API numbers match 2021-22 CSV numbers?
- [ ] Outliers: Any suspicious state-level dropout rates?
- [ ] Encoding issues: Character encoding in state names (esp. special chars)?

### Step 1.2 — Structure Analysis

**For girls' secondary dropout analysis, need:**

| Dimension | Values | Status |
|-----------|--------|--------|
| **Year** | 2015-16 to 2024-25 | ✅ Have via API + PDF |
| **State** | 28 states + UTs | ✅ Available |
| **Education Level** | Primary, Upper Primary, Secondary, Higher Secondary | ✅ Available |
| **Gender** | Boys, Girls | ✅ Key for analysis |
| **Social Category** | General, SC, ST, OBC | ✅ Available |
| **School Type** | Government, Private, Aided | ⚠️ May need extraction |

**Derived Metrics to Calculate:**
- Dropout Rate = (Previous Year Total - Current Year Total) / Previous Year Total
- Gender Parity Index (GPI) = Girls Enrolment / Boys Enrolment
- Progress = Change in dropout rate year-over-year
- State Ranking = Percentile of states by dropout rate

### Step 1.3 — Data Quality Validation

**Action Items:**
```python
# 1. Load both data sources (API vs CSV)
# 2. For overlapping years (2018-22), validate row-by-row
# 3. Document any discrepancies
# 4. Flag outliers (dropout > 50% or < 0%)
# 5. Check for missing states/years
```

---

## 🔍 Phase 2: Hunt for Signal (SKILL: data-analysis)

### Step 2.1 — Define What Matters

**Key Questions (in priority order):**

1. **Main Question**: Which states have the highest girls' secondary dropout?
2. **Trend Question**: Is the trend improving or stagnating?
3. **Driver Question**: What distinguishes high-improvement states from stagnant ones?
4. **Surprise Question**: What hidden patterns break conventional wisdom?
5. **Action Question**: What specific levers move the needle?

**Audiences & Decisions:**
- 👔 **Minister**: "Should we fund a national intervention?" → Need trend + urgency
- 🔨 **IAS Officers**: "What do I implement in my state?" → Need state rankings + success models
- 📊 **Analysts**: "What's the mechanism?" → Need driver analysis + segmentation

### Step 2.2 — Hunt for Patterns

**Pattern Search Toolkit:**

| Pattern Type | Look For | Example Finding |
|---|---|---|
| **Extreme distributions** | Which states are 3σ from mean? | Odisha 25%, Kerala 5% |
| **Pattern breaks** | When did the trend shift? | Acceleration post-2020? |
| **Surprising correlations** | What moves with dropout? | Infrastructure investment? Wealth? |
| **Standout performers** | Who overperforms peers? | Tripura improving -33pp |
| **Hidden subgroups** | Does it vary by social category? | Do SC girls dropout more? |
| **Leverage points** | What small change moves the dial? | Girl's toilet facility 96% → still 12% dropout |

### Step 2.3 — Verify & Stress-Test

**Robustness Checks:**
- [ ] Does 2021-22 data match across API and CSV sources?
- [ ] Is the -1.4 pp/year trend robust over 10 years or artifact of outlier year?
- [ ] Do findings hold when excluding outlier states?
- [ ] Is improvement in one state due to policy or just natural mean reversion?
- [ ] Are we confusing correlation (wealth) with causation (institutions)?

**External Cross-Check:**
- [ ] Do NEP 2020 policy interventions align with observed improvements?
- [ ] Do state-level policy announcements match data inflection points?
- [ ] Are we missing confounders (migration, population shifts)?

---

## ✍️ Phase 3: Narrative Data Story (SKILL: data-story)

### Step 3.1 — The Hook

**Instead of:** "This report analyzes girls' secondary education dropout rates."

**Create tension/mystery:**
- 🧑 **Human angle**: "Meet Priya, a 14-year-old from Odisha. She attended school for 8 years. Then she vanished — one of 1 in 4 girls who never make it to secondary."
- ⚡ **Tension**: "India's primary girls' enrollment is climbing. Yet secondary dropout remains stuck at 12%. Why?"
- ❓ **Mystery**: "One state cut dropout by a third in 3 years. Another state, richer and with better infrastructure, is losing girls at the same rate. What's the difference?"

### Step 3.2 — Story Arc (≤4 beats)

**Setup (Beat 1):** The world as everyone assumes
- "India has made progress: primary enrollment is near-universal, girls are increasingly attending."
- Show: National trend 18% → 12% over 7 years. Sounds good.

**Complication (Beat 2):** The crack in conventional wisdom
- "But progress stalled. The trend froze in 2019, then resumed weakly."
- Show: Line chart with the plateau. Call out the pause.
- Add:** "And 1 in 3 girls still drops out at secondary—it's the leakiest stage of the funnel."

**Revelation (Beat 3):** The central insight
- "The breakthrough states didn't spend more money. They focused on institutional capacity."
- Show: Tripura vs Punjab comparison - same investment, different outcomes.
- Mechanism: "Infrastructure (toilets, electricity) is necessary but not sufficient. What matters is staff training, dropout tracking, and re-enrollment programs."

**Implications (Beat 4):** What changes
- "This means reallocating: fewer new schools, more investment in existing school quality."
- Actionable: "Three specific interventions show ROI: (1) economic support to poorest girls, (2) teacher training on gender, (3) dropout tracking systems."

### Step 3.3 — Integrated Visualizations

**Chart 1 - The Setup (National Trend)**
- **Headline**: "India's girls' secondary dropout has improved but plateaued"
- Line chart: Years 2015–2024, 18% → 12% (with plateau callout 2019–2021)
- Color: Red declining line (improvement), gray shaded area (plateau period)

**Chart 2 - The Complication (State Variance)**
- **Headline**: "But 5 states still lose 1 in 5 girls"
- Ranked bar chart: State names, dropout rates
- Color: Top 5 worst states in red, top 5 best states in green, rest gray
- Call out: Odisha (25%), Kerala (5%)

**Chart 3 - The Revelation (Tripura vs Punjab)**
- **Headline**: "Wealth doesn't explain the gap—institutional capacity does"
- Scatter: X-axis = per-capita education spend, Y-axis = girls' dropout rate
- Overlay: Tripura point (low spend, low dropout), Punjab point (high spend, high dropout)
- Pattern: Line of best fit shows money matters less than the dots show

**Chart 4 - The Implication (Driver Analysis)**
- **Headline**: "What moves the needle: focused interventions beat broad infrastructure"
- Heatmap: States × interventions (teacher training, dropout tracking, economic support, girl's toilets)
- Color: Intensity = % states where improvement correlates with this intervention
- Call out:** Best-improving states (Tripura, MP, CG) have high scores on training + tracking

### Step 3.4 — Concrete Examples & Evidence

**For each major finding, anchor with a specific case:**

✅ **Setup evidence:**
- "In 2015, 18.26% of Indian girls dropped out at secondary. Priya was one of millions."

✅ **Complication evidence:**
- "In Odisha, the number is 25.28%—one in four. In Kerala, it's 5%—one in twenty. Travel 2,000 km and the odds of staying in school triple."

✅ **Revelation evidence:**
- "Tripura reduced dropout by 33 percentage points in 4 years—the fastest improvement in the country. Punjab, richer and with more schools per capita, cut dropout by just 5 points. What's different? Tripura invested in tracking every single girl's enrollment status and retraining all teachers on gender-sensitive pedagogy."

✅ **Implication evidence:**
- "States with dropout tracking systems have 15pp lower dropout than states without. Teacher gender-sensitivity training correlates with 8pp reduction. Girl's toilet facilities? Present in 96% of schools nationally but dropout still at 12%—necessary but not sufficient."

### Step 3.5 — "Wait, Really?" Moment

**Set up the assumption:**
"We might assume: richer states do better."

**Reveal the contradiction:**
"But Gujarat (richer) has higher girls' dropout (17%) than Chhattisgarh (poorer, 10%)."

**Name the surprise:**
"This isn't a wealth problem. It's a management problem."

**Use contrast:**
- Poor state, well-managed → low dropout
- Rich state, poorly-managed → high dropout

### Step 3.6 — So What? (Embedded in flow, not a list)

"This finding reshapes the strategy. Instead of building 10,000 new schools, reallocate existing resources: (1) hire and train 50,000 teacher mentors to watch for girls at risk, (2) link school enrollment to state ID to automatically flag dropouts within 48 hours, (3) provide conditional cash transfers to the poorest 20% of families."

### Step 3.7 — Honest Caveats

"This analysis covers 2015–2024 and is based on state-aggregate data. Causation isn't proven—we can't say training *caused* improvements, only that it correlates. We also don't have granular cost data for each intervention, so ROI estimates are rough. What we'd want to confirm: does intensive dropout tracking actually prevent re-dropping?"

---

## 🚀 Phase 4: Implementation Plan

### Step 4.1 — Data Integration

**Priority order:**
1. ✅ Download 2022-23 and 2023-24 CSV data from udise-csv-data
2. ✅ Extract 2024-25 from PDF booklets (state-wise dropout rates)
3. ✅ Merge with existing API data (2015-22)
4. ✅ Validate: check 2021-22 overlap
5. ✅ Run data quality checks

### Step 4.2 — Analysis Execution

```
1. Load all 10 years into single dataframe
2. Calculate dropout rates for each state-year-gender-level
3. Hunt for patterns: extreme values, breaks, correlations
4. Identify standout performers: Tripura, MP, CG (improving) vs Odisha, Bihar (stuck)
5. Cross-analyze: infrastructure vs dropout (does toilet availability predict lower dropout?)
6. Segment by social category: is SC/ST dropout higher?
7. Verify findings: run against external benchmarks
```

### Step 4.3 — Story Construction

1. Write the hook (human angle, tension, mystery)
2. Draft 4-beat arc (setup → complication → revelation → implications)
3. Create visualizations with revelatory headlines
4. Anchor each finding with concrete state examples
5. Build "wait, really?" moment
6. Embed implications in narrative flow
7. Surface caveats honestly

### Step 4.4 — Deliverables (in priority order)

| Deliverable | Audience | Format | Status |
|---|---|---|---|
| POLICY_BRIEF.md | Minister | 1-pager, action-ready | ✅ Exists |
| CRISIS_STATE_PLAYBOOK.md | IAS Officers | 12-month roadmap | ✅ Exists |
| PRESENTATION.md (updated) | Analysts | 11 sections, story-driven | 🔄 Update with skills |
| Data dictionary | Analysts | Column meanings + sources | ⏳ New |
| Visualization deck | All | Charts with headlines | ✅ Exists (refresh) |

---

## 📈 Success Criteria

- ✅ Data spans 10 years (2015–2024-25)
- ✅ Narrative hooks a busy reader in first paragraph
- ✅ 4-beat story arc is clear and memorable
- ✅ Findings are surprising ("wait, really?") and actionable
- ✅ Evidence is concrete (specific states, not aggregate)
- ✅ Visualizations are revelatory (patterns are obvious, not needing explanation)
- ✅ Caveats are acknowledged without undermining confidence
- ✅ A smart, busy person reads to the end without asking

---

## 🎯 Next Actions

1. [ ] Download 2022-23, 2023-24 CSV data from udise-csv-data
2. [ ] Extract 2024-25 dropout rates from existing PDF snapshots
3. [ ] Merge all data sources into one master dataset
4. [ ] Run validation: does 2021-22 match across sources?
5. [ ] Hunt for signal: patterns, outliers, breakpoints
6. [ ] Rewrite PRESENTATION.md using story arc framework
7. [ ] Redesign charts with revelatory headlines
8. [ ] Test: would a minister stay engaged? Would an IAS officer say "I'll try this"?

