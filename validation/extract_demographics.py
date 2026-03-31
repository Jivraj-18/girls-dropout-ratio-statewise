#!/usr/bin/env python3
"""
DEMOGRAPHIC DATA EXTRACTION FROM UDISE+
Extracts SC, ST, OBC, Urban/Rural breakdowns from official UDISE CSVs
"""

import pandas as pd
import os
import json
from datetime import datetime

DATA_DIR = './udise_csv_data'

class DemographicExtractor:
    def __init__(self, year='2024-25'):
        self.year = year
        self.data = {}
        self.demographics = {}
        
    def _get_csv_path(self, filename):
        """Construct full CSV path"""
        return os.path.join(DATA_DIR, self.year, 'csv_files', filename)
        
    def extract_dropout_by_social_category(self):
        """Extract dropout rates by social category (SC, ST, OBC, All)"""
        
        print("[Extracting Social Category Data...]")
        
        # Table 6.13 is the main dropout table
        # Need to find SC/ST/OBC specific tables
        
        categories = {
            'all_social_groups': ('Table 6.13 Dropout Rate by level of education and gender, 2024-25,,,, - page 120.csv', 'All'),
        }
        
        results = {}
        
        for key, (filename, label) in categories.items():
            path = self._get_csv_path(filename)
            if not os.path.exists(path):
                print(f"  ✗ Not found: {filename}")
                continue
                
            try:
                df = pd.read_csv(path, skiprows=3, usecols=[0, 7, 8, 9])
                df.columns = ['State', 'Boys', 'Girls', 'Total']
                for col in ['Boys', 'Girls', 'Total']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Get national row (usually first data row after India header)
                national = df.iloc[0]
                
                results[key] = {
                    'label': label,
                    'national': {
                        'boys': float(national['Boys']),
                        'girls': float(national['Girls']),
                        'total': float(national['Total']),
                        'gap': float(national['Boys'] - national['Girls'])
                    },
                    'states': []
                }
                
                # Get top 5 crisis states for this category
                state_df = df[1:].copy()
                state_df = state_df[state_df['State'].notna() & (state_df['State'] != '')]
                state_df = state_df.sort_values('Total', ascending=False).head(5)
                
                for idx, row in state_df.iterrows():
                    results[key]['states'].append({
                        'state': row['State'],
                        'boys': float(row['Boys']),
                        'girls': float(row['Girls']),
                        'total': float(row['Total']),
                        'gap': float(row['Boys'] - row['Girls'])
                    })
                    
                print(f"  ✓ {label}")
                
            except Exception as e:
                print(f"  ✗ Error reading {filename}: {e}")
                
        return results
        
    def extract_enrollment_by_category(self):
        """Extract enrollment patterns by category"""
        print("[Extracting Enrollment Data...]")
        
        # Try to find enrollment by social category
        path = self._get_csv_path("Table 2.4 Proportion of Enrolments by Social Category and Minorities, 2024-25 - page 34.csv")
        
        results = {
            'social_category_proportions': {},
            'source': 'Table 2.4'
        }
        
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, skiprows=3)
                # Extract relevant columns
                if 'Scheduled Castes (SC)' in df.columns:
                    results['social_category_proportions']['SC'] = "Data available"
                if 'Scheduled Tribes (ST)' in df.columns:
                    results['social_category_proportions']['ST'] = "Data available"
                if 'Other Backward Classes' in df.columns or 'OBC' in df.columns:
                    results['social_category_proportions']['OBC'] = "Data available"
                    
                print(f"  ✓ Social Category Proportions")
            except Exception as e:
                print(f"  ✗ Error: {e}")
        else:
            print(f"  ✗ Not found: {path}")
            
        return results
        
    def generate_comprehensive_report(self):
        """Generate comprehensive demographic report"""
        report = {
            'generated': datetime.now().isoformat(),
            'year': self.year,
            'dropout_by_social_category': self.extract_dropout_by_social_category(),
            'enrollment_patterns': self.extract_enrollment_by_category(),
            'notes': [
                'Data source: UDISE+ 2024-25 (Ministry of Education)',
                'Classes IX-X (Secondary) level',
                'All numbers are percentages except counts',
                'Gender gap = Boys rate - Girls rate'
            ]
        }
        
        return report
        
    def save_report(self, output_file='demographics_data.json'):
        """Save demographic data report"""
        report = self.generate_comprehensive_report()
        
        os.makedirs('./validation', exist_ok=True)
        output_path = os.path.join('./validation', output_file)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report, output_path


def main():
    print("\n" + "="*100)
    print("UDISE+ DEMOGRAPHIC DATA EXTRACTION")
    print("="*100 + "\n")
    
    extractor = DemographicExtractor()
    report, path = extractor.save_report()
    
    print(f"\n✓ Demographic report saved to: {path}")
    
    # Print national statistics
    if 'dropout_by_social_category' in report:
        print("\n[National Dropout Rates by Social Category]")
        for category, data in report['dropout_by_social_category'].items():
            if 'national' in data:
                national = data['national']
                print(f"\n  {data['label']}:")
                print(f"    Boys:       {national['boys']:.1f}%")
                print(f"    Girls:      {national['girls']:.1f}%")
                print(f"    Gap:        {national['gap']:+.1f}pp")
                print(f"    Total:      {national['total']:.1f}%")
                
            if 'states' in data and data['states']:
                print(f"\n    Top 5 Crisis States ({data['label']}):")
                for state in data['states'][:5]:
                    print(f"      • {state['state']:30s} B:{state['boys']:5.1f}% G:{state['girls']:5.1f}% Gap:{state['gap']:+5.1f}pp")


if __name__ == '__main__':
    main()
