# Repository Cleanup Analysis

## ✅ COMPLETED CLEANUP

**Removed 9 empty API dump files (3.5 MB total):**
- `_requests_and_responses.json` (7.4 KB)
- `_summary.json` (1.6 KB)
- `master_get_district_*.json` (metadata files, all empty)
- `master_get_state_year24.json` (empty - year 24 data not available via API)
- `tabular_map117_national_year24.json` (empty - year 24 API returned nulls)
- `tabular_map117_stateall_year23.json` (empty - year 23 API returned nulls)
- `tabular_map117_stateall_year24.json` (empty - year 24 API returned nulls)

**Kept 10 files with actual data:**
- `tabular_map113_national_year22.json` (10.7 KB)
- `tabular_map113_stateall_year22.json` (300.3 KB)
- `tabular_map117_national_year22.json` (10.6 KB)
- `tabular_map117_stateall_year16-22.json` (Years 16-22, ~2.1 MB total)

---

## 🔍 ADDITIONAL CLEANUP CANDIDATES

### 1. **archive/ directory (2.9 MB)** - LIKELY UNUSED
Contains old exploratory files:
- Old CSV exports from Sept 2025 (3204_*.csv files)
- Kozhikode district-specific data zips (old downloads)
- Old Excel reports with promotion/repetition/dropout data
- Old reports.json file
- **Status:** These are from early exploration; Now replaced by:
  - PDF extraction data (pdf_extraction/)
  - API dumps with clean data (udise_api_dumps/)

**Recommendation:** ❌ Delete archive/ - 2.9 MB saved

### 2. **scripts/_old/ directory** - DEFINITELY UNUSED
Contains old/deprecated scripts
**Recommendation:** ❌ Delete scripts/_old/

### 3. **Single-use files to review:**
- `DSP_Schema.pdf` (76 KB) - Is this needed? If not used in docs, can delete
- `inspect_json.py` (726 B) - One-off utility script, probably not needed
- `Prompt.md` (8.5 KB) - Looks like old prompt/instructions from project setup
- `Transcript.md` (1.7 KB) - Old conversation transcript, can be archived

### 4. **Outputs directory (1.2 MB)**
Contains generated charts and CSVs - **KEEP** (needed for presentations)

---

## 📊 POTENTIAL SPACE SAVINGS

| If You Delete | Space Saved |
|---|---|
| archive/ | 2.9 MB |
| scripts/_old/ | ~50 KB |
| DSP_Schema.pdf | 76 KB |
| Prompt.md | 8.5 KB |
| inspect_json.py | 1 KB |
| **TOTAL** | **~3.0 MB** |

---

## ✅ WHAT TO KEEP

**Essential for the project:**
- ✅ `booklets/` (33 MB) - Raw UDISE+ PDFs - NEEDED
- ✅ `udise_api_dumps/` (2.5 MB) - Clean API data years 16-22 - NEEDED
- ✅ `pdf_extraction/` (28 KB) - Extracted data snippets - NEEDED
- ✅ `outputs/` (1.2 MB) - Generated charts & analysis - NEEDED
- ✅ All `.md` documentation files - NEEDED
- ✅ `udise_pipeline.py` - Core analysis script - NEEDED

---

## 🎯 RECOMMENDED CLEANUP ACTIONS

**Definitely delete (100% safe):**
```bash
rm -rf archive/
rm -rf scripts/_old/
rm inspect_json.py
```

**Review before deleting:**
- `DSP_Schema.pdf` - Check if referenced anywhere
- `Prompt.md` - Check if needed for documentation
- `Transcript.md` - Old notes, probably can archive

**Keep everything else**

