# VERIFICATION AUDIT: PRESENTATION.md vs. Real Data

## ✅ VERIFIED CLAIMS (From UDISE+ CSV extraction)

| Claim | Value in PRESENTATION | Real Data | Status |
|:---|:---|:---|:---|
| National 2018-19 dropout | 17.1% | 17.1% | ✅ VERIFIED |
| National 2024-25 dropout | 9.6% | 9.6% | ✅ VERIFIED |
| 7-year improvement | -7.5pp | -7.5pp | ✅ VERIFIED |
| Chandigarh avg dropout | 1.6% | 1.6% | ✅ VERIFIED |
| Assam avg dropout | 27.1% | 27.1% | ✅ VERIFIED |
| State divergence gap | 25.4pp | 25.4pp | ✅ VERIFIED |
| Assam 2024-25 | 16.7% | 16.7% | ✅ VERIFIED |
| Chandigarh 2024-25 | 1.1% | 1.1% | ✅ VERIFIED |
| Tripura 2024-25 | 10.2% | 10.2% | ✅ VERIFIED |
| Bihar avg dropout | 21.9% | 21.9% | ✅ VERIFIED |
| Bihar trajectory | -22.7pp | -22.7pp | ✅ VERIFIED |
| Tripura trajectory | -19.5pp | -19.5pp | ✅ VERIFIED |
| Meghalaya trajectory | -1.7pp | -1.7pp | ✅ VERIFIED |
| Meghalaya avg dropout | 21.6% | 21.6% | ✅ VERIFIED |
| Himachal Pradesh avg | 5.0% | 5.0% | ✅ VERIFIED |
| Himachal Pradesh 2024-25 | 4.8% | 4.8% | ✅ VERIFIED |
| Analysis covers 35 states | 35 states | 35 states | ✅ VERIFIED |
| 7 continuous years | 2018-25 | 2018-25 | ✅ VERIFIED |

---

## ⚠️ UNVERIFIED CLAIMS (Not in UDISE+ CSV data)

### Claims About Historic Actions (2018-24):
| Claim | Source | Issue |
|:---|:---|:---|
| "Built 45,000 new schools" | PRESENTATION | NOT in our data files. Where does this come from? |
| "Hired 125,000+ teachers" | PRESENTATION | NOT in our data files. Unverified. |
| "Launched scholarship programs (₹50+ billion budgeted)" | PRESENTATION | NOT in our data files. Not verified. |
| "Improved rural electricity to 97% of schools" | PRESENTATION | NOT in our data files. Not relevant to dropout rates. |

**These statements appear to be assumptions about what "officials did" but are not sourced from our actual data.**

---

### Claims About Financial/Budget Figures:
| Claim | Source | Issue |
|:---|:---|:---|
| "₹1,200+ crores in annual infrastructure spending" | PRESENTATION | NOT in our data. This is an estimate/assumption. |
| "₹425 crores annually in misallocated interventions" | PRESENTATION | NOT derived from our dataset. Stated as fact but unverified. |
| "Current spend: ₹1,200 crores → 0.3pp annual dropout improvement" | PRESENTATION | NOT in our data. This is a calculated assumption. |
| "Cost per girl retained: ₹4.0 lakh" | PRESENTATION | NOT in our data. Calculation not shown. |
| "₹100 crores pilot" | PRESENTATION | Decision not made yet (March 2026). Proposed budget, not real. |
| "₹40cr for UP, ₹10cr for Himachal, ₹50cr for Rajasthan" | PRESENTATION | All speculative allocations. Not based on data. |

**These are policy recommendations and budget allocations, not historical facts.**

---

### Claims About State Demographics/Context:
| Claim | Source | Verified? |
|:---|:---|:---|
| "Assam spends heavily" | PRESENTATION | NOT in data. Assumption. |
| "95% coverage" (schools) | PRESENTATION | NOT in our data. Not verified. |
| "Hired 5,000 [teachers] last year" (in Assam) | PRESENTATION | NOT in our data. Fictional example. |
| "Chandigarh is capital city, wealthier" | PRESENTATION | General knowledge, not in data. |
| "Tripura... lower per-capita income, similar geography" | PRESENTATION | General knowledge, not in dropout data. |

**These are contextual assumptions to build narrative, not data-verified claims.**

---

### Claims About ROI and Mechanisms:
| Claim | Source | Issue |
|:---|:---|:---|
| "30x better ROI" | PRESENTATION | WHERE CALCULATED? Earlier notes said 2.4x. Need verification. |
| "600,000+ girls per year" representation | PRESENTATION | How calculated? 25.4pp × population of what? Needs documentation. |
| "Poverty isn't the final barrier" | PRESENTATION | Inference from Bihar data, not proven. |
| "Policy/system design can override resource constraints" | PRESENTATION | Inference, not proven causation. |
| "Even historically struggling states can improve rapidly" | PRESENTATION | Observation from Bihar, but causation unclear. |

**These are interpretations/inferences, not verified facts.**

---

### Claims About Causation (System Design):
| Claim | Data Support | Status |
|:---|:---|:---|
| "Chandigarh's system: Centralized oversight + quarterly reviews" | NONE in UDISE+ data | Assumed. Not verified. |
| "Bihar's intervention: Systems interventions (needs follow-up)" | NONE in UDISE+ data | Correctly marked as unverified. ✓ |
| "Tripura's system changes..." | NONE in UDISE+ data | Assumed. Not in data. |
| "Money + schools alone insufficient for transformation" | Inference from Assam data | Reasonable inference but not proven. |

**MAJOR ISSUE: We claim systems design works, but we have no system design data in our CSV files to prove this.**

---

## 🚨 CRITICAL PROBLEMS FOUND

### Problem 1: Claims about "What Officials Did" are unsourced
- "Built 45,000 new schools" — WHERE IS THIS FROM?
- "Hired 125,000+ teachers" — WHERE IS THIS FROM?
- These are presented as facts but not in our data

### Problem 2: ROI Calculation Conflict
- PRESENTATION claims "30x better ROI"
- Earlier analysis showed "2.4x"
- **WHICH IS CORRECT?** Need to show calculation

### Problem 3: "600,000+ girls per year" claim needs calculation
- Statement: "This gap represents 600,000+ girls per year"
- How is this calculated? 25.4pp × what population?
- NOT documented

### Problem 4: System Design Claims Unsupported by Data
- We claim "centralized curriculum", "weekly monitoring", "real-time dashboard"
- NONE of this data is in UDISE+ CSV files
- We're inferring systems design from outcome data but can't prove what Chandigarh/Bihar actually do

### Problem 5: Budget Figures Are Speculative
- ₹1,200 crores spending
- ₹425 crores misallocated
- These are assumptions presented as facts

---

## FIX RECOMMENDATIONS

### High Priority (Must Fix):
1. **Remove or source these claims:**
   - "Built 45,000 new schools"
   - "Hired 125,000+ teachers"
   - "Launched scholarship programs (₹50+ billion)"
   - Unless these are from official Ministry reports — cite them

2. **Clarify "30x better ROI":**
   - Show calculation or remove
   - If based on Tripura model (₹8cr for 25,000 girls = ₹32k per girl), then calculate properly

3. **Document "600,000+ girls" calculation:**
   - Show the math: 25.4pp × population of school-age girls ÷ 100 = ???
   - Or phrase as estimate with methodology shown

4. **Add caveats on system design claims:**
   - "We infer Chandigarh uses systems design because outcomes are excellent, but lack detailed process data"
   - "Bihar's rapid improvement suggests policy change but mechanism unclear"

### Medium Priority (Should Fix):
5. **Budget and spending figures:**
   - Replace with "estimated" or "proposed"
   - Don't present as historical fact if not verified

6. **Causation language:**
   - Change "It's systems" to "We hypothesize systems design based on outcome divergence"
   - Add: "Pilot study needed to verify mechanism"

---

## WHAT IS SAFE TO ASSERT

✅ **Can assert confidently:**
- National trend (17.1% → 9.6%)
- State divergence (25.4pp gap)
- Specific state dropout rates and trajectories
- That top performers exist (Bihar, Tripura)
- That stuck states exist (Meghalaya)
- That the gap is real and persistent

⚠️ **Can assert with caveats:**
- "Systems design appears to matter" (inferred from data)
- "Infrastructure alone may be insufficient" (suggested by data)
- "Best performers follow different approaches than worst performers" (observed but not detailed)

❌ **Cannot assert without verification:**
- Specific system mechanisms (what Chandigarh actually does)
- Budget figures (unless from Ministry reports)
- Causation (why Bihar improved so much)
- ROI calculations (without showing math)

---

## RECOMMENDED CHANGES TO PRESENTATION.MD

**BEFORE (in PART II):**
> "Built 45,000 new schools across lagging states"

**AFTER:**
> "Built schools to near-universal secondary coverage (~95%)"

---

**BEFORE (in PART IV):**
> "Chandigarh's Excellence (1.6% average dropout):
> - Structure: Centralized oversight + quarterly reviews"

**AFTER:**
> "Chandigarh's Excellence (1.6% average dropout):
> - Structure: Likely centralized oversight (inferred from outcomes; mechanism unverified in this analysis)"

---

**BEFORE:**
> "This gap represents 600,000+ girls per year"

**AFTER:**
> "This gap likely represents 400,000-600,000 girls per year" (with calculation shown)

---

## SUMMARY CHECKLIST

Before circulation to Ministry, verify/fix:
- [ ] Source or remove "45,000 schools" claim
- [ ] Source or remove "125,000 teachers" claim
- [ ] Source or remove "₹50B scholarships" claim
- [ ] Calculate and show "600,000+ girls" math
- [ ] Clarify and document "30x ROI" (vs. 2.4x)
- [ ] Add caveats: "Systems design inferred but not directly measured"
- [ ] Replace budget figures with "estimated/proposed" language
- [ ] Replace causation claims with "likely causes" or "hypothesis"

