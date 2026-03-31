# PDF Data Extraction Summary

## Source PDFs
Three UDISE+ booklets have been extracted:
1. **UDISE+2022_23_Booklet_nep.pdf** (170 pages, 11 MB)
2. **udise_report_nep_23_24.pdf** (173 pages, 12 MB)  
3. **UDISE+2024_25_Booklet_existing.pdf** (189 pages, 12 MB)

---

## Key Data Points Available

### 📊 **Dropout Rate Data** (Most Important for Your Analysis)
Located in **Section 6: Performance Indicators**

#### Dropout Rates - 2024-25 (All Categories)
- **Primary**: 0.3%
- **Upper Primary**: 3.5%
- **Secondary**: 11.5%

#### Data Mapped by:
- Gender (Boys vs Girls separately)
- Level of Education (Primary, Upper Primary, Secondary, Higher Secondary)
- Geographic coverage (State-wise, available in detailed tables)
- Maps and charts showing dropout rates by:
  - Primary level
  - Upper Primary level  
  - Secondary level

---

## Complete Table of Contents Available

### **Section 1: Data Highlights - National**
- Table 1: National Highlights of UDISE+ data
- National-level summary statistics

### **Section 2: Data Highlights** 
- Table 2.1-2.7: Distribution of Schools, Enrolments, Teachers by:
  - School Category (Government, Private, Aided)
  - State wise data
  - Infrastructure status
  - Aadhaar seeding status

### **Section 3: Details on Schools**
- Table 3.1-3.11: Number of schools by:
  - Level of education
  - Management type
  - Pre-primary sections

### **Section 4: Teaching & Non-Teaching Staff**
- Table 4.1-4.20: Teachers by:
  - School Category
  - Gender
  - Management type
  - Pupil Teacher Ratio (PTR)
  - Trained/Professionally Qualified teachers

### **Section 5: Enrolment Details**
- Table 5.1-5.16: Student enrolment by:
  - Gender (Boys, Girls separately)
  - School level
  - Management type
  - Pre-school experience
  - **GENDER-BASED DATA (Most relevant for girls' dropout analysis)**

### **Section 6: Performance Indicators** ⭐
**This is the section with your core data!**
- Table 6.1-6.7: Enrolment Ratios (GER, NER, ANER, ASER)
- Table 6.8-6.10: Minority enrolment (OBC, Muslim, all minorities)
- Table 6.11: **Promotion Rate by gender and education level**
- Table 6.12: **Repetition Rate by gender and education level**
- **Table 6.13: DROPOUT RATE BY LEVEL OF EDUCATION AND GENDER** ✓
- Table 6.14: Transition Rate by gender and education level
- Table 6.15: Retention Rate by gender and education level

### **Section 7: Infrastructure Facilities**
- Table 7.1-7.25: School infrastructure including:
  - Electricity, drinking water, toilets
  - Girl's toilets (specific)
  - Computer & Internet facilities
  - CWSN (Children with Special Needs) facilities
  - Kitchen gardens, Solar panels, Libraries

### **Section 8: Educational Parameters Summary**
- Table 8.1-8.14: Aggregated statistics by management type

### **Section 9: Computers & Digital Initiatives**
- Table 9.1-9.9: ICT facilities in schools

### **Section 10: Population Projections**
- Table 10.1-10.3: Population projections by gender, social groups, age

---

## Important Note: DATA METHODOLOGY CHANGE

**⚠️ Critical from Disclaimer (Page 7):**
- **NEP 2020 Alignment**: Post-2020, UDISE+ shifted from school-level consolidated data to **individual student-level data collection** (starting 2022-23)
- **Not directly comparable with 2021-22 and earlier**: Different methodology for tracking dropouts
- Data indicators (GER, NER, Dropout rate) for **2024-25 are NOT strictly comparable** with 2015-22 data
- Population projections updated based on latest SRS birth rate trends and Aadhaar seeding data

**Implication for Your Project:**
- You have two distinct data regimes:
  1. **2015-22**: School-level aggregated data (old methodology)
  2. **2022-23 onwards**: Individual student-level data (new methodology - more accurate for tracking dropouts)
- Need to note this methodology break in your analysis

---

## Girls' Secondary Dropout Data - What to Extract

Based on the table structure, for girls' secondary dropout analysis you should look for:

1. **State-wise girls' secondary dropout rates for years 23, 24, 25**
2. **Comparison points:**
   - Girls vs Boys dropout rates
   - By management type (Government, Private, Aided)
   - By social category (SC, ST, OBC)

3. **Related supporting data:**
   - Girls' enrolment numbers (Section 5)
   - Infrastructure (especially girl's toilets in Section 7)
   - Promotion/Retention/Transition rates

---

## Extracted Files Location

All extracted data saved in: `/home/jivraj/straive/girl-dropout-rate-analysis/pdf_extraction/`

- `year_2022_23.txt` (68 KB) - First 30 pages of 2022-23 booklet
- `year_2023_24.txt` (67 KB) - First 30 pages of 2023-24 booklet  
- `year_2024_25.txt` (66 KB) - First 30 pages of 2024-25 booklet

Each file contains readable text and all tables found in those pages.

---

## Next Steps

To extract the complete dropout rate data by state and gender, you can:

1. **Option A**: Manually review the extracted files and copy state-wise tables
2. **Option B**: Run OCR extraction on the full PDFs to get machine-readable tables
3. **Option C**: Access the official UDISE+ portal directly at **http://udiseplus.gov.in** for downloadable data tables

Would you like me to:
- Extract specific tables in CSV format?
- Search for particular state data?
- Convert the data into your analysis pipeline format?
