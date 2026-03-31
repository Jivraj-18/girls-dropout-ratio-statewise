# Girls' Secondary Dropout in India: 2018-25

Facts-only analysis using verified UDISE+ data from the Ministry of Education.

## View the Briefing

👉 **[Click here to read the briefing](https://jivraj.github.io/girl-dropout-rate-analysis)**

Or open `index.html` locally in your browser.

## What's Inside

- **National trend**: 17.1% → 9.6% (2018-19 to 2024-25)
- **State spread**: 1.1% (best) to 17.7% (worst) in 2024-25
- **Persistent problem**: 5 states still above 15%, 2 stuck there for all 7 years
- **Improvement variability**: Bihar down 22.7pp, Meghalaya down only 1.7pp

## Design

- Clean, minimal aesthetic
- Light/dark theme toggle
- No external dependencies
- Responsive on all devices
- Self-contained HTML file

## Deeper Analysis Documents

For IAS officers and policy makers requiring detailed insights:

### 📊 [GIRL_CHILD_DEEP_DIVE.md](GIRL_CHILD_DEEP_DIVE.md)
**Focus: Understanding and addressing girls' dropout specifically**
- Girl dropout hotspots (5 Tier-1 crisis states identified)
- Root causes: Infrastructure, early marriage, labor, distance, safety
- State-by-state action matrix with specific interventions
- Validated data vs. research gaps
- IAS officer checklist for implementation

### 📈 [DEEPER_ANALYSIS_REPORT.md](DEEPER_ANALYSIS_REPORT.md)
**Focus: Comprehensive gender analysis with boys/girls breakdown**
- Why boys are at-risk in secondary level (gender reversal finding)
- Root cause decomposition: Promotion vs. Repetition vs. Dropout
- Regional patterns: Northeast, South, Central, Eastern regions
- State-level disparities and benchmarking opportunities
- Caveats and limitations of current analysis

### ✅ [validation/](validation/)
**Validation scripts and reproducibility**
- All claims regeneratable from UDISE+ raw CSV data
- `validate_all.py` - Master validation framework
- `validate_gender_gap.py` - Gender paradox verification
- `validate_formula.py` - Formula consistency checks
- See [validation/README.md](validation/README.md) for usage

## Data Source

- UDISE+ official CSV data, Ministry of Education, Government of India
- Verified extraction, no unsupported claims
- All data points regeneratable from raw source files
- See validation scripts for reproducible verification
