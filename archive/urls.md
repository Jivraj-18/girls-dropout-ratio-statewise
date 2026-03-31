# UDISE+ Data Sources - Complete Guide

## 🎯 YOUR MAIN SOURCES FOR LATEST DATA

### 1. **STATE REPORT CARDS** (Best for Latest Data)
📊 https://dashboard.udiseplus.gov.in/udiseplus-archive/#/reportDashboard/sReport

**What it offers:**
- National & state-wise performance summaries
- Year-on-year comparisons
- District breakup available
- Key metrics: Dropout rates, enrollment, transitions, toilets, etc.

**How to use:**
1. Click "States and UTs" dropdown
2. Select a state → See full 7-year trend
3. Download as PDF or screenshot for slides/briefings

**Format:** Interactive dashboard + PDF export  
**Latest data:** 2021-22  
**Use for:** Presentations, quick reference, state comparisons

---

### 2. **DATA TABLES / CSV EXPORT** (Best for Your Analysis)
📥 https://dashboard.udiseplus.gov.in/udiseplus-archive/#/dataTab

**What it offers:**
- Raw enrollment, dropout, promotion data by state/district
- Download by year (2015-16 to latest available)
- Caste-wise breakdowns
- School type (co-ed, girls-only, boys-only)

**How to use:**
1. Select year from dropdown
2. Select state or "All States"
3. Click "Download CSV"
4. Use in your analysis pipeline

**Format:** CSV (machine-readable)  
**Latest data:** 2021-22  
**Use for:** Custom analysis, PowerBI, Python scripts (like your pipeline)

---

### 3. **ANALYSIS REPORTS** (Pre-made Analysis)
📄 https://dashboard.udiseplus.gov.in/udiseplus-archive/#/reports

**What it offers:**
- Pre-written analysis by education level (primary, upper primary, secondary)
- Gender breakdowns
- Caste-wise analysis
- Policy summaries

**How to use:**
1. Browse "Analysis Reports" section
2. Download PDF matching your topic
3. Use as reference/validation

**Format:** PDF (ready-made)  
**Use for:** Validating your findings, quick context

---

### 4. **OFFICIAL RELEASES / ANNOUNCEMENTS** (Know When Data Drops)
⭐ https://udiseplus.gov.in/#/home/

**What it offers:**
- Official press releases
- Data release announcements
- Methodology notes
- Archive of all years

**How to use:**
1. Check "What's New" section (appears at top)
2. Subscribe to notifications
3. Check when starting new analysis

**Format:** Web announcements  
**Use for:** Knowing when 2023-24 data is published

---

### 5. **GEOGRAPHIC HEAT MAP ANALYSIS** (Visual Impact)
🗺️ https://schoolgis.nic.in/

**What it offers:**
- Interactive map of enrollment, dropout by district
- Visual identification of crisis zones
- State and district-level analysis
- Filterable by multiple criteria

**How to use:**
1. Select state from dropdown
2. Select year (2021-22 latest available)
3. Select metric (dropout rate for girls)
4. Zoom to district level

**Format:** Interactive map  
**Use for:** Presentations (visual impact), identifying hotspots

---

## 📊 QUICK REFERENCE TABLE

| Purpose | URL | Format | Best For |
|:---|:---|:---|:---|
| State performance | reportDashboard | Interactive + PDF | Presentations, comparisons |
| **Raw data (YOUR USE)** | **#/dataTab** | **CSV** | **Analysis & pipeline** |
| Pre-made analysis | #/reports | PDF | Validation, context |
| Release dates | udiseplus.gov.in | Announcements | Knowing update schedule |
| Geographic view | schoolgis.nic.in | Map | Visual, hotspot identification |

---

## 🔄 WORKFLOW: When New Data Drops (2023-24+)

```
1. CHECK: Visit https://udiseplus.gov.in/#/home/
   → Look for "2023-24 Data Released" announcement

2. DOWNLOAD: Go to https://dashboard.udiseplus.gov.in/udiseplus-archive/#/dataTab
   → Select year 23 or 24
   → Download CSV

3. INTEGRATE: Run your pipeline
   python udise_pipeline.py fetch --years 23,24
   python udise_pipeline.py build
   python udise_pipeline.py charts

4. UPDATE: Modify PRESENTATION.md, POLICY_BRIEF.md with new numbers

5. SHARE: Push update to GitHub
   git add outputs/ *.md
   git commit -m "Update: UDISE+ 2023-24 data released"
```

---

## ⏱️ DATA RELEASE TIMELINE (Historical Pattern)

- **Academic Year ends:** May 31
- **UDISE+ publishes:** ~6-12 months after (typically Dec-Mar following year)
- **Example:** 2023-24 data likely available **by March 2025** (if on schedule)

**Current status (March 31, 2026):**
- ✅ 2021-22 data available (released Dec 2022)
- ❌ 2023-24 data NOT YET published
- ⏳ Keep checking official site

---

## 💡 Your Current URL

**What you have:** `https://dashboard.udiseplus.gov.in/udiseplus-archive/#/reportDashboard/sReport`

**What it does:** Shows summary report dashboard with state comparisons  
**Data available:** Up to 2021-22  
**Better option for your pipeline:** Use `#/dataTab` for CSV export instead

---

## 🚀 RECOMMENDED ACTION NOW

1. **For presentations:** Screenshot dashboard from reportDashboard URL
2. **For data updates:** Monitor reportDashboard/sReport to spot when 2023-24 appears
3. **For fresh data:** When available, download from #/dataTab as CSV 