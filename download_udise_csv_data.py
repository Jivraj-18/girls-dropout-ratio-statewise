#!/usr/bin/env python3
"""
Download UDISE CSV data from GitHub and integrate with existing project.
Source: https://github.com/gsidhu/udise-csv-data

Years available: 2018-19 to 2023-24
Target years: 2018-19, 2019-20, 2020-21, 2021-22, 2022-23, 2023-24
(2015-16, 2016-17, 2017-18 kept from API)
"""

import os
import urllib.request
import zipfile
import shutil
from pathlib import Path

def download_udise_csv_data():
    """Download UDISE CSV data for specified years."""
    
    BASE_URL = "https://github.com/gsidhu/udise-csv-data/archive/refs/heads/main.zip"
    YEARS = ["2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]
    
    work_dir = Path("udise_csv_downloads")
    work_dir.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("DOWNLOADING UDISE CSV DATA")
    print("=" * 70)
    
    print(f"\n📥 Downloading entire repo...")
    zip_path = work_dir / "udise-data.zip"
    
    try:
        urllib.request.urlretrieve(BASE_URL, zip_path)
        print(f"✅ Downloaded to {zip_path}")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return
    
    # Extract
    print(f"\n📦 Extracting...")
    extract_dir = work_dir / "extracted"
    extract_dir.mkdir(exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f"✅ Extracted to {extract_dir}")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return
    
    # Find and copy relevant year folders
    print(f"\n📋 Copying relevant years...")
    source_root = extract_dir / "udise-csv-data-main"
    
    if not source_root.exists():
        print(f"⚠️  Couldn't find udise-csv-data-main folder")
        # List what we have
        for item in extract_dir.iterdir():
            print(f"   Found: {item.name}")
        return
    
    data_dir = Path("udise_csv_data")
    data_dir.mkdir(exist_ok=True)
    
    for year in YEARS:
        year_folder = source_root / f"UDISE {year}"
        if year_folder.exists():
            dest_folder = data_dir / year
            if dest_folder.exists():
                shutil.rmtree(dest_folder)
            shutil.copytree(year_folder, dest_folder)
            
            # Count files
            csv_count = len(list(dest_folder.glob("*.csv")))
            print(f"   ✅ {year}: {csv_count} CSV files")
        else:
            print(f"   ⚠️  {year}: folder not found")
    
    print(f"\n✅ Data downloaded to: udise_csv_data/")
    
    # Clean up
    shutil.rmtree(work_dir)
    print(f"✅ Cleaned up temp files")
    
    return data_dir

def analyze_csv_structure():
    """Analyze what's in the downloaded CSV files."""
    
    print("\n" + "=" * 70)
    print("ANALYZING CSV STRUCTURE")
    print("=" * 70)
    
    data_dir = Path("udise_csv_data")
    if not data_dir.exists():
        print("❌ No udise_csv_data folder found")
        return
    
    for year_folder in sorted(data_dir.iterdir()):
        if year_folder.is_dir():
            csv_files = list(year_folder.glob("*.csv"))
            print(f"\n📁 {year_folder.name}/")
            print(f"   {len(csv_files)} CSV files:")
            
            for csv_file in sorted(csv_files)[:5]:  # Show first 5
                print(f"   - {csv_file.name}")
            
            if len(csv_files) > 5:
                print(f"   ... and {len(csv_files) - 5} more")

def integration_notes():
    """Print integration notes."""
    
    print("\n" + "=" * 70)
    print("INTEGRATION NOTES")
    print("=" * 70)
    
    print("""
✅ NEW DATA AVAILABLE:
   - 2018-19 to 2023-24 (CSV format)
   - Pre-extracted dropout rates by state, gender, level
   - Social category breakdowns (SC, ST, OBC, General)

✅ DATA TO KEEP:
   - API dumps for 2015-16, 2016-17, 2017-18 (not in CSV repo)
   - PDF extraction for 2024-25 (when available)

⚠️  DATA INTEGRATION STEPS:
   1. Load CSV files for each year
   2. Extract state-wise girls' secondary dropout rate
   3. Validate: compare 2021-22 CSV vs 2021-22 API (should match)
   4. Merge into single master dataset
   5. Update analysis pipeline to use merged data

📊 ANALYSIS REFRESH:
   1. Recalculate trends with 10-year dataset (2015-2024-25)
   2. Hunt for patterns: did 2019 plateau still exist in CSV data?
   3. Rewrite PRESENTATION.md using data-story skills
   4. Create new visualizations with revelatory headlines
   5. Validate against external sources (NITI Aayog reports, etc.)

📝 NEXT:
   - Run: python3 download_udise_data.py
   - Check: ls -la udise_csv_data/
   - Inspect: head -20 udise_csv_data/2023-24/*.csv
   - Compare: 2021-22 values across API vs CSV
    """)

if __name__ == "__main__":
    print("UDISE CSV Data Download Tool")
    print("For girl dropout rate analysis project\n")
    
    download_udise_csv_data()
    analyze_csv_structure()
    integration_notes()
    
    print("\n" + "=" * 70)
    print("✅ Pipeline ready for data analysis!")
    print("=" * 70)
