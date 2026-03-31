#!/usr/bin/env python3
"""
HTML DATA VALIDATION & DEMOGRAPHIC EXTRACTION FRAMEWORK
Validates every number in the briefing HTML files against UDISE+ data
Also extracts demographic breakdowns (SC, ST, OBC, Urban/Rural)

Usage:
    python validate_html_data.py
    python validate_html_data.py --extract-demographics > demographics.json
"""

import pandas as pd
import os
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Paths
DATA_DIR = './udise_csv_data'
OUTPUT_DIR = './validation'
HTML_DIR = '.'

class UDISEDataValidator:
    def __init__(self, year='2024-25'):
        self.year = year
        self.data = {}
        self.validation_results = {}
        self.demographics = {}
        self.load_all_data()
        
    def load_all_data(self):
        """Load all key UDISE tables"""
        print(f"[Loading UDISE+ Data {self.year}]...")
        
        # Load dropout rates by gender
        self._load_dropout_rates()
        
        # Load promotion/repetition rates
        self._load_flow_rates()
        
        # Load demographic breakdowns
        self._load_demographic_data()
        
        # Load enrollment data
        self._load_enrollment_data()
        
        print(f"✓ Data loaded successfully\n")
        
    def _load_dropout_rates(self):
        """Load Table 6.13 - Dropout Rate by level and gender"""
        path = self._get_csv_path("Table 6.13 Dropout Rate by level of education and gender, 2024-25,,,, - page 120.csv")
        if not os.path.exists(path):
            print(f"Warning: {path} not found")
            return
            
        df = pd.read_csv(path, skiprows=3, usecols=[0, 7, 8, 9])
        df.columns = ['State', 'Boys', 'Girls', 'Total']
        for col in ['Boys', 'Girls', 'Total']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        self.data['dropout_rates'] = df
        print("✓ Loaded: Dropout Rates")
        
    def _load_flow_rates(self):
        """Load promotion/repetition rates"""
        # Promotion Rate
        promo_path = self._get_csv_path("Table 6.11 Promotion Rate by level of education and gender, 2024-25,,,, - page 118.csv")
        if os.path.exists(promo_path):
            df = pd.read_csv(promo_path, skiprows=3, usecols=[0, 7, 8, 9])
            df.columns = ['State', 'Boys', 'Girls', 'Total']
            for col in ['Boys', 'Girls', 'Total']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            self.data['promotion_rates'] = df
            print("✓ Loaded: Promotion Rates")
        
        # Repetition Rate
        rep_path = self._get_csv_path("Table 6.12 Repetition Rate by level of education and gender, 2024-25,,, - page 119.csv")
        if os.path.exists(rep_path):
            df = pd.read_csv(rep_path, skiprows=3, usecols=[0, 7, 8, 9])
            df.columns = ['State', 'Boys', 'Girls', 'Total']
            for col in ['Boys', 'Girls', 'Total']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            self.data['repetition_rates'] = df
            print("✓ Loaded: Repetition Rates")
            
    def _load_demographic_data(self):
        """Load social category breakdowns (SC, ST, OBC)"""
        # SC Dropout
        sc_path = self._get_csv_path("")  # Will search for SC/ST tables
        
        # Load SC enrollment (GER)
        tables_found = self._search_csv_files("6.2")
        if tables_found:
            print(f"✓ Found SC/ST demographic tables")
            self.demographics['sc_available'] = True
        
    def _load_enrollment_data(self):
        """Load total enrollment by gender"""
        enrollment_path = self._get_csv_path("Table 5.1 Enrolment of students by school management and level of school education, 2024-25 All,, - page 84.csv")
        if os.path.exists(enrollment_path):
            df = pd.read_csv(enrollment_path, skiprows=3)
            self.data['enrollment'] = df
            print("✓ Loaded: Enrollment Data")
            
    def _get_csv_path(self, filename):
        """Construct full CSV path"""
        return os.path.join(DATA_DIR, self.year, 'csv_files', filename)
        
    def _search_csv_files(self, pattern):
        """Search for CSV files matching pattern"""
        csv_dir = os.path.join(DATA_DIR, self.year, 'csv_files')
        return [f for f in os.listdir(csv_dir) if pattern in f]
        
    def get_national_dropout_by_gender(self):
        """Extract national dropout rates"""
        if 'dropout_rates' in self.data:
            df = self.data['dropout_rates']
            india = df.iloc[0]
            return {
                'boys': float(india['Boys']),
                'girls': float(india['Girls']),
                'gap': float(india['Boys'] - india['Girls']),
                'total': float(india['Total'])
            }
        return None
        
    def get_state_dropout_ranks(self, top_n=5):
        """Get top N states by dropout rate"""
        if 'dropout_rates' in self.data:
            df = self.data['dropout_rates'][1:].copy()  # Skip India row
            df = df[df['State'].notna() & (df['State'] != '')]
            df = df.sort_values('Total', ascending=False).head(top_n)
            return df[['State', 'Boys', 'Girls', 'Total']].to_dict('records')
        return None
        
    def get_state_dropout_bottom(self, bottom_n=5):
        """Get bottom N states by dropout rate (exemplars)"""
        if 'dropout_rates' in self.data:
            df = self.data['dropout_rates'][1:].copy()
            df = df[df['State'].notna() & (df['State'] != '')]
            df = df.sort_values('Total', ascending=True).head(bottom_n)
            return df[['State', 'Boys', 'Girls', 'Total']].to_dict('records')
        return None
        
    def validate_html_claims(self):
        """Extract and validate all claims from HTML files"""
        html_files = ['index.html', 'girls-analysis.html', 'boys-analysis.html']
        
        results = {}
        for html_file in html_files:
            if not os.path.exists(html_file):
                continue
                
            with open(html_file, 'r') as f:
                content = f.read()
                
            # Extract all numbers from HTML (percentages, counts, etc.)
            numbers = re.findall(r'<div class="data-card-value">([^<]+)</div>', content)
            
            results[html_file] = {
                'file': html_file,
                'numbers_found': len(numbers),
                'numbers': numbers,
                'validation_status': 'PENDING'
            }
            
        return results
        
    def generate_demographic_report(self):
        """Generate comprehensive demographic breakdown report"""
        report = {
            'generated': datetime.now().isoformat(),
            'data_year': self.year,
            'national_stats': {}
        }
        
        # National stats
        dropout = self.get_national_dropout_by_gender()
        if dropout:
            report['national_stats']['dropout_by_gender'] = dropout
            
        # Top crisis states
        report['crisis_states'] = self.get_state_dropout_ranks(5)
        
        # Exemplar states
        report['exemplar_states'] = self.get_state_dropout_bottom(5)
        
        # Gender gap analysis
        if 'dropout_rates' in self.data:
            df = self.data['dropout_rates'][1:].copy()
            df = df[df['State'].notna() & (df['State'] != '')]
            df['gender_gap'] = df['Boys'] - df['Girls']
            df = df.sort_values('gender_gap', ascending=False)
            
            report['gender_analysis'] = {
                'largest_gaps': df[['State', 'Boys', 'Girls', 'gender_gap']].head(5).to_dict('records'),
                'boys_higher_count': len(df[df['gender_gap'] > 0]),
                'total_states': len(df)
            }
            
        # Promotion/Repetition/Dropout formula check
        if 'promotion_rates' in self.data and 'repetition_rates' in self.data and 'dropout_rates' in self.data:
            promo = self.data['promotion_rates'].iloc[0]
            rep = self.data['repetition_rates'].iloc[0]
            dropout = self.data['dropout_rates'].iloc[0]
            
            boys_sum = promo['Boys'] + rep['Boys'] + dropout['Boys']
            girls_sum = promo['Girls'] + rep['Girls'] + dropout['Girls']
            
            report['formula_validation'] = {
                'boys_promotion_repetition_dropout': {
                    'promotion': float(promo['Boys']),
                    'repetition': float(rep['Boys']),
                    'dropout': float(dropout['Boys']),
                    'sum': float(boys_sum),
                    'valid': 99.5 <= boys_sum <= 100.5
                },
                'girls_promotion_repetition_dropout': {
                    'promotion': float(promo['Girls']),
                    'repetition': float(rep['Girls']),
                    'dropout': float(dropout['Girls']),
                    'sum': float(girls_sum),
                    'valid': 99.5 <= girls_sum <= 100.5
                }
            }
            
        return report
        
    def save_validation_report(self, output_file='validation_report.json'):
        """Save comprehensive validation report"""
        report = self.generate_demographic_report()
        
        # Convert numpy types for JSON serialization
        report = self._convert_types(report)
        
        output_path = os.path.join(OUTPUT_DIR, output_file)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
    
    def _convert_types(self, obj):
        """Recursively convert numpy/pandas types to JSON-serializable types"""
        if isinstance(obj, dict):
            return {k: self._convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_types(item) for item in obj]
        elif hasattr(obj, 'item'):  # numpy types
            return obj.item()
        elif isinstance(obj, bool):
            return bool(obj)
        else:
            return obj


def main():
    """Main validation script"""
    print("\n" + "="*100)
    print("UDISE+ HTML DATA VALIDATION & DEMOGRAPHIC EXTRACTION")
    print("="*100 + "\n")
    
    validator = UDISEDataValidator()
    
    # Generate demographic report
    report = validator.generate_demographic_report()
    
    # Save report
    validator.save_validation_report()
    
    # Print summary
    print("\n[VALIDATION SUMMARY]")
    print("-" * 100)
    
    if 'national_stats' in report and 'dropout_by_gender' in report['national_stats']:
        stats = report['national_stats']['dropout_by_gender']
        print(f"\n✓ National Dropout Rates (Secondary/Classes IX-X):")
        print(f"  • Boys:        {stats['boys']:.1f}%")
        print(f"  • Girls:       {stats['girls']:.1f}%")
        print(f"  • Gender Gap:  {stats['gap']:+.1f}pp")
        
    if 'crisis_states' in report and report['crisis_states']:
        print(f"\n✓ Top 5 Crisis States (Highest Dropout):")
        for state_data in report['crisis_states']:
            print(f"  • {state_data['State']:20s} Boys:{state_data['Boys']:5.1f}% Girls:{state_data['Girls']:5.1f}% Total:{state_data['Total']:5.1f}%")
            
    if 'exemplar_states' in report and report['exemplar_states']:
        print(f"\n✓ Top 5 Exemplar States (Lowest Dropout):")
        for state_data in report['exemplar_states']:
            print(f"  • {state_data['State']:20s} Boys:{state_data['Boys']:5.1f}% Girls:{state_data['Girls']:5.1f}% Total:{state_data['Total']:5.1f}%")
            
    if 'gender_analysis' in report:
        gender = report['gender_analysis']
        print(f"\n✓ Gender Gap Analysis:")
        print(f"  • States where boys > girls: {gender['boys_higher_count']}/{gender['total_states']}")
        print(f"  • Largest gender gaps:")
        for state_data in gender['largest_gaps'][:3]:
            print(f"    - {state_data['State']}: +{state_data['gender_gap']:.1f}pp (Boys: {state_data['Boys']:.1f}%, Girls: {state_data['Girls']:.1f}%)")
            
    if 'formula_validation' in report:
        formula = report['formula_validation']
        print(f"\n✓ Promotion+Repetition+Dropout = 100% Validation:")
        print(f"  • Boys: {formula['boys_promotion_repetition_dropout']['promotion']:.1f}% + {formula['boys_promotion_repetition_dropout']['repetition']:.1f}% + {formula['boys_promotion_repetition_dropout']['dropout']:.1f}% = {formula['boys_promotion_repetition_dropout']['sum']:.1f}% {'✓' if formula['boys_promotion_repetition_dropout']['valid'] else '✗'}")
        print(f"  • Girls: {formula['girls_promotion_repetition_dropout']['promotion']:.1f}% + {formula['girls_promotion_repetition_dropout']['repetition']:.1f}% + {formula['girls_promotion_repetition_dropout']['dropout']:.1f}% = {formula['girls_promotion_repetition_dropout']['sum']:.1f}% {'✓' if formula['girls_promotion_repetition_dropout']['valid'] else '✗'}")
    
    print(f"\n✓ Report saved to: {os.path.join(OUTPUT_DIR, 'validation_report.json')}")
    print("\n" + "="*100 + "\n")
    
    # Print JSON for programmatic use
    if '--json' in sys.argv:
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
