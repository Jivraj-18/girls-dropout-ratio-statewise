# Dataset Assessment (Kozhikode 2024–25, DSP/UDISE-style)

## Can we go ahead with this dataset?
Yes — for *driver/lever* analysis and for building a school-level risk picture.

But: **this dataset alone cannot directly answer “girl dropout rate”** unless you add either:
1) an explicit dropout/retention outcome column from UDISE+/reports, or
2) the **same enrolment tables for multiple years** to compute an “apparent dropout” proxy across grades.

## What you have (confirmed from files + schema)
All tables share the join key `pseudocode` (unique school ID).

### 1) School profile (context)
- `3204_prof1.csv`: location + management + category/type + classes offered + medium, etc.
- `3204_prof2.csv`: program/implementation indicators like free textbooks/uniforms, inspections, SMC, etc.

### 2) Facilities (policy levers)
- `3204_fac.csv`: toilets (boys/girls + functional), water, electricity/solar, library, playground, ramps/handrails, labs, computers, internet, etc.

### 3) Teachers (policy levers)
- `3204_tch.csv`: total teachers, male/female, contract/regular, qualification, trained, CWSN-trained, etc.

### 4) Enrolment by grade and gender (required for any dropout proxy)
- `3204_enr1.csv` = “School Enrolment_1”: enrolment by grade (`cpp`, `c1`…`c12`) for multiple subgroups.
  - `item_group=1` with `item_id` mapping to General/SC/ST/OBC.
  - `item_group=2` with `item_id` mapping to Muslim/Christian/Sikh/Buddhist/Parsi/Jain.
  - `item_group=3` with `item_id=13` mapping to BPL.
  - `item_group=4` mapping to CWSN disability types.
  - `item_group=5, item_id=0` mapping to “Repeater student”.
- `3204_enr2.csv` = “Age Wise Enrolment_2”: enrolment by grade and gender, but split by `item_id` = age (schema says 2 to 22).

## What questions this dataset CAN answer well (today)
Within Kozhikode (district) for 2024–25:

1) **Where are the vulnerable schools?**
- Identify schools with low girls’ enrolment in secondary grades (especially 8–10) and poor infrastructure.

2) **Which controllable levers are associated with better girls’ participation?**
- Girls’ functional toilets + water + electricity
- Female teacher share
- Access indicators (road approachable)
- Ramps/handrails and special educator (inclusion)
- ICT availability (optional)

3) **Transition-risk flags (even without dropout):**
- Over-age patterns using `enr2` (age-wise enrolment) as a leading risk indicator.
- Repeater counts (item_group=5) as a stress indicator.

This is useful for a Secretary because it produces *actionable operational priorities* even without a formal dropout rate.

## What this dataset CANNOT answer by itself
1) **Cross-state variation**: you only have Kozhikode right now.
2) **“What drives girl dropout rate?”**: you don’t yet have a dropout outcome variable.
3) **Future forecast (“if nothing changes”)**: requires multiple years of the same measures.

## What you need next (minimum to make it a full dropout analysis)

### Option A (best): Get dropout/retention as an outcome
Acquire state/district/year dropout rates from UDISE+/official report cards (even if aggregated) and merge at the district-year or state-year level.
Then you can relate dropout to the drivers you have (facilities/teachers) at the same aggregation level.

### Option B: Compute “apparent dropout” from school enrolment across years
Collect the same module CSVs for at least **3–5 consecutive years** (e.g., 2019–20 to 2024–25) for the same geography.

Then compute (example) grade-transition loss for girls:
- Apparent dropout from Grade 8 to Grade 9 in year $t \to t+1$:
  $$1 - \frac{\text{girls	s enrolment in c9 at }(t+1)}{\text{girls\ts enrolment in c8 at }t}$$

Note: this is a proxy (migration, repetition, reporting issues can distort it), but it is often good enough for a policy deck if you clearly label it as “apparent dropout / transition loss”.

### Option C: Expand geography for cross-state story
To answer “how does this vary across states?”, you need the same tables for:
- all districts in a state, or
- at least a representative set of districts across multiple states.

## Recommendation
- **Go ahead** with this dataset as the core “drivers/levers” layer.
- To make it minister-ready on *dropout rates*, prioritize getting:
  - multi-year enrolment (Option B) and/or
  - official dropout/transition indicators from UDISE+ report cards (Option A).

## Note: National dropout/promotion/repetition report (Excel export)
You added a report export:
- `Promotion Rate , Repetition Rate , Dropout Rate by Gender, Level of School Education and Social Category_Report type - National_22.xlsx`

What it is:
- An NIC “ag-grid” export of UDISE+ report **Report Id: 4014** (from the file header).
- It contains **Promotion Rate, Repetition Rate, and Drop Out Rate** by **gender**, **education level** (Primary/Upper Primary/Secondary blocks), and **social category** (General/SC/ST/OBC/Overall).

What it’s good for:
- **National benchmark slide** and to show where the “dropout cliff” is.
- For example (All India, Overall): girls’ dropout is much higher at Secondary than Primary.

What it’s NOT good for:
- It is **not state/district-wise** in the version you exported (it only shows “All India”).
- It does not include a usable **year** column (it’s a snapshot export).

Cleaned output created in this repo:
- `national_22_promotion_repetition_dropout_clean.csv`

Cleaner utility:
- `clean_aggrid_report.py` (fixes multi-row merged headers typical of these exports).
