## DATA VALIDATION FRAMEWORK

This directory contains **regeneratable scripts** that verify all claims in the "Girls Secondary Dropout" briefing are correct and sourced from UDISE+ data.

### 🎯 Purpose
- **No false claims**: Every statistic can be re-generated from raw data
- **Transparency**: IAS officers can verify numbers themselves
- **Reproducibility**: Run scripts anytime to confirm data integrity

---

## 📋 Scripts Available

### 1. `validate_all.py` (Master Script)
**Most comprehensive validation - START HERE**

```bash
cd validation/
python validate_all.py
```

Validates:
- National secondary dropout rates (boys vs girls)
- Gender gap prevalence across 35 states
- Promotion/Repetition/Dropout formula (sums to 100%)
- State rankings (top/bottom performers)
- Regional patterns (Northeast vs South)

Output (saved in `validation/` directory):
- `validation_summary.txt` - Human-readable report
- `validation_results.json` - Machine-readable results

---

### 2. `validate_gender_gap.py` (Gender Paradox)
**Focused validation on gender gap finding**

```bash
cd validation/
python validate_gender_gap.py
```

Validates:
- "34 out of 35 states have boys dropout > girls"
- Identifies the one exception (Lakshadweep)
- Shows top 5 largest gender gaps by state

---

### 3. `validate_formula.py` (Promotion/Repetition Formula)
**Checks internal consistency of data**

```bash
cd validation/
python validate_formula.py
```

Validates:
- Promotion + Repetition + Dropout = 100%
- Why boys dropout more (decomposition)
- Source correlation between tables

---

## 🔍 What Gets Validated?

| Claim | Source | Validation Script |
|-------|--------|------------------|
| Boys dropout more than girls nationally | Table 6.13 | `validate_all.py` |
| 34/35 states have boys > girls | Table 6.13 | `validate_gender_gap.py` |
| Promotion rate: Boys 89.9%, Girls 95.2% | Table 6.11 | `validate_formula.py` |
| Repetition rate: Boys 2.9%, Girls 1.3% | Table 6.12 | `validate_formula.py` |
| Dropout rate: Boys 7.3%, Girls 3.5% | Table 6.13 | Both |
| Promotion + Repetition + Dropout = 100% | All three | `validate_formula.py` |

---

## ⚙️ Requirements

```bash
pip install pandas  # Only external dependency
```

Python 3.7+

---

## 📁 Data Directory Structure

```
project_root/
├── validation/           <- You are here
│   ├── validate_all.py
│   ├── validate_gender_gap.py
│   ├── validate_formula.py
│   ├── README.md         <- This file
│   ├── validation_summary.txt      (generated)
│   └── validation_results.json     (generated)
├── udise_csv_data/
│   ├── 2024-25/
│   │   └── csv_files/
│   │       ├── Table 6.11 Promotion Rate...
│   │       ├── Table 6.12 Repetition Rate...
│   │       └── Table 6.13 Dropout Rate...
│   ├── 2023-24/
│   │   └── csv_files/ ...
│   └── [2018-19 through 2022-23]
└── index.html
```

---

## 🚀 How to Use

### Quick Start (Recommended)
```bash
# From the validation/ directory
cd validation/
python validate_all.py

# Check results
cat validation_summary.txt
cat validation_results.json
```

### From Project Root
```bash
# Run from anywhere in the project
cd validation/
python validate_all.py
```

### Step-by-Step Verification
```bash
cd validation/

# 1. Validate gender gap claim
python validate_gender_gap.py

# 2. Check internal formula consistency
python validate_formula.py

# 3. Run comprehensive check
python validate_all.py
```

### Integration with CI/CD
```bash
cd validation/
python validate_all.py && echo "✅ Data valid"
```

---

## 📊 Output Examples

### `validate_all.py` produces:

**validation_summary.txt** (excerpt):
```
1. SECONDARY (CLASSES 9-10) DROPOUT RATES - 2024-25
─────────────────────────────────
National Figures:
  • Boys dropout:    7.3%
  • Girls dropout:   3.5%
  • Gender gap:      +3.8pp (Boys higher)
  • Source: Table 6.13 (UDISE+ 2024-25)

2. GENDER GAP PATTERN ACROSS STATES
─────────────────────────────────
  • States where boys dropout > girls:  34 / 35
  • States where girls dropout > boys:  1 / 35
  • Exception states (girls > boys):    ['Lakshadweep']

✅ All data points verified and regeneratable from raw UDISE+ sources
```

**validation_results.json** (excerpt):
```json
{
  "national_dropout_2024_25": {
    "boys_pct": 7.3,
    "girls_pct": 3.5,
    "gender_gap_pp": 3.8
  },
  "gender_gap_pattern": {
    "states_boys_higher": 34,
    "states_girls_higher": 1,
    "total_states": 35,
    "exception_states": ["Lakshadweep"]
  }
}
```

---

## ✅ Validation Checklist for IAS Officers

- [ ] Navigate to `validation/` directory
- [ ] Run `python validate_all.py`
- [ ] Check `validation_summary.txt` for key statistics
- [ ] Verify gender gap in your state from output
- [ ] Review `validation_results.json` for JSON export
- [ ] Confirm all figures match those in the briefing
- [ ] Cross-check with official UDISE+ portal if needed

---

## ⚠️ Important Notes

1. **Data Source**: All scripts source from raw UDISE+ CSVs in `../udise_csv_data/`
2. **Run Location**: Must be run from `validation/` directory (scripts use relative paths)
3. **Rounding**: Figures displayed as rounded (e.g., 7.3%) but maintain full precision in JSON
4. **Secondary Level**: All validations are for **Classes 9-10 (secondary)** unless otherwise noted
5. **2024-25 Year**: Current scripts validate 2024-25 data. Modify `validate_all.py` line ~15 to validate other years
6. **State Names**: UDISE+ uses official state names; update scripts if state name format differs

---

## 🔧 Extending Validation

To validate additional claims:

1. Edit `validate_all.py`
2. Add new data loading section (copy `load_secondary_data()` pattern)
3. Add validation logic
4. Add output lines to `output_lines` list
5. Run and verify

Example (adding primary level validation):
```python
# Load primary (1-5) data
prim_dropout = load_secondary_data(
    'dropout_primary',
    'Table 6.13...',  # Use primary cols: 1, 2, 3
    columns=[0, 1, 2, 3]  # Adjust columns for primary
)
```

---

## 📞 Support

If scripts fail:
1. Check that `../udise_csv_data/` directory exists with proper structure
2. Verify UDISE+ CSV files are not corrupted
3. Ensure pandas is installed: `pip install pandas`
4. Run with verbose output: `python validate_all.py 2>&1 | less`
5. Verify you are running from the `validation/` directory

---

**Last Updated**: 2026-03-31
**Data Year**: UDISE+ 2024-25
**Validation Status**: ✅ All checks passing
