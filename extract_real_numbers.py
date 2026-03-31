#!/usr/bin/env python3
"""
REAL DATA EXTRACTION — From actual UDISE+ CSV files
Girls Secondary Dropout Rate (Column 8) across all years and states
"""

import pandas as pd
import numpy as np
from pathlib import Path

def extract_real_girls_secondary_dropout():
    """Extract actual girls' secondary dropout (Column 8) from UDISE+ files"""
    
    print("\n" + "="*80)
    print("EXTRACTING REAL DATA: Girls' Secondary Dropout Rate (2018-25)")
    print("="*80)
    
    years = ["2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
    state_trends = {}
    india_trend = {}
    
    for year in years:
        year_path = Path(f"udise_csv_data/{year}/csv_files")
        dropout_files = list(year_path.glob("*Dropout*"))
        
        if dropout_files:
            file_path = dropout_files[0]
            print(f"\n   Reading {year}: {file_path.name[:60]}...")
            
            try:
                df = pd.read_csv(file_path)
                
                # Skip header rows (0-2), data starts at row 3
                # Column 0 = State, Column 8 = Girls Secondary Dropout
                for idx in range(3, len(df)):
                    state_name = str(df.iloc[idx, 0]).strip() if pd.notna(df.iloc[idx, 0]) else None
                    
                    if state_name and state_name.lower() != 'nan':
                        try:
                            girls_secondary = float(str(df.iloc[idx, 8]).replace(',', '').strip())
                            
                            if 0 <= girls_secondary <= 100:
                                if state_name not in state_trends:
                                    state_trends[state_name] = {}
                                state_trends[state_name][year] = girls_secondary
                                
                                # Track India separately
                                if state_name == 'India':
                                    india_trend[year] = girls_secondary
                        except (ValueError, TypeError):
                            pass
                            
            except Exception as e:
                print(f"      ⚠ Error: {e}")
    
    print(f"\n✓ Extracted data for {len(state_trends)} states/UTs across {len(years)} years")
    return state_trends, india_trend


def show_national_trend(india_trend):
    """Display national trend"""
    
    print("\n" + "="*80)
    print("NATIONAL TREND — India's Girls' Secondary Dropout Rate")
    print("="*80)
    
    for year in sorted(india_trend.keys()):
        print(f"   {year}: {india_trend[year]:5.1f}%")
    
    # Calculate trend
    years_list = sorted(india_trend.keys())
    first = india_trend[years_list[0]]
    last = india_trend[years_list[-1]]
    change = last - first
    
    print(f"\n   2018-19 → 2024-25: {change:+.1f} percentage points")
    print(f"   Direction: {'↓ IMPROVING' if change < 0 else '↑ WORSENING'}")
    
    # Check for plateau
    recent_years = {k: v for k, v in india_trend.items() if k >= '2021-22'}
    if len(recent_years) >= 2:
        recent_vals = list(recent_years.values())
        recent_volatility = max(recent_vals) - min(recent_vals)
        print(f"   Recent volatility (2021-25): ±{recent_volatility:.1f}pp")


def show_state_divergence(state_trends):
    """Show best/worst states and divergence"""
    
    print("\n" + "="*80)
    print("STATE DIVERGENCE — Who's winning? Who's stuck?")
    print("="*80)
    
    # Filter states with 5+ years of data
    complete_states = {
        s: t for s, t in state_trends.items() 
        if len(t) >= 5 and s != 'India'
    }
    
    if not complete_states:
        print("   No states with 5+ years of data")
        return None, None
    
    # Calculate average and trajectories
    state_avgs = {
        s: np.mean(list(t.values())) 
        for s, t in complete_states.items()
    }
    
    sorted_states = sorted(state_avgs.items(), key=lambda x: x[1])
    
    print(f"\n   📊 Analysis covers {len(complete_states)} states with complete data")
    
    print("\n🟢 TOP PERFORMERS (Best outcomes - Lowest girls' secondary dropout):")
    for i, (state, avg) in enumerate(sorted_states[:8], 1):
        data = complete_states[state]
        first_yr = min(data.keys())
        last_yr = max(data.keys())
        first_val = data[first_yr]
        last_val = data[last_yr]
        change = last_val - first_val
        
        print(f"   {i}. {state:25s} | Avg: {avg:5.1f}% | {first_yr}: {first_val:5.1f}% → {last_yr}: {last_val:5.1f}% ({change:+.1f}pp)")
    
    print("\n🔴 STRUGGLING STATES (Worst outcomes - Highest girls' secondary dropout):")
    for i, (state, avg) in enumerate(sorted_states[-8:], 1):
        data = complete_states[state]
        first_yr = min(data.keys())
        last_yr = max(data.keys())
        first_val = data[first_yr]
        last_val = data[last_yr]
        change = last_val - first_val
        
        print(f"   {i}. {state:25s} | Avg: {avg:5.1f}% | {first_yr}: {first_val:5.1f}% → {last_yr}: {last_val:5.1f}% ({change:+.1f}pp)")
    
    # Divergence
    best_state, best_avg = sorted_states[0]
    worst_state, worst_avg = sorted_states[-1]
    gap = worst_avg - best_avg
    
    print(f"\n" + "="*80)
    print("DIVERGENCE MAGNITUDE:")
    print("="*80)
    print(f"\n   BEST:  {best_state:30s} {best_avg:5.1f}%")
    print(f"   WORST: {worst_state:30s} {worst_avg:5.1f}%")
    print(f"   ────────────────────────────────────────")
    print(f"   GAP:   {gap:5.1f} percentage points")
    
    print(f"\n   Interpretation: {worst_state} loses {gap:.1f}pp MORE girls than {best_state}")
    print(f"   (Same country, same education system, radically different outcomes)")
    
    return sorted_states, complete_states


def show_year_pair_comparison(state_trends):
    """Show specific state-to-state comparisons by year"""
    
    complete_states = {
        s: t for s, t in state_trends.items() 
        if len(t) >= 5 and s != 'India'
    }
    
    if len(complete_states) < 2:
        return
    
    state_avgs = {
        s: np.mean(list(t.values())) 
        for s, t in complete_states.items()
    }
    
    sorted_states = sorted(state_avgs.items(), key=lambda x: x[1])
    best_state, _ = sorted_states[0]
    worst_state, _ = sorted_states[-1]
    
    print(f"\n" + "="*80)
    print(f"YEAR-BY-YEAR COMPARISON: {best_state} vs {worst_state}")
    print("="*80)
    
    best_data = complete_states[best_state]
    worst_data = complete_states[worst_state]
    
    all_years = sorted(set(list(best_data.keys()) + list(worst_data.keys())))
    
    print(f"\n{' Year ':<10} {best_state:25s} {worst_state:25s} {'Gap':>10}")
    print("-" * 75)
    
    for year in all_years:
        best_val = best_data.get(year, np.nan)
        worst_val = worst_data.get(year, np.nan)
        
        if not np.isnan(best_val) and not np.isnan(worst_val):
            year_gap = worst_val - best_val
            print(f"{year:<10} {best_val:>24.1f}% {worst_val:>24.1f}% {year_gap:>9.1f}pp")


def main():
    # Extract real data
    state_trends, india_trend = extract_real_girls_secondary_dropout()
    
    if not state_trends:
        print("\n⚠ No data extracted. Check if CSV files exist.")
        return
    
    # Show national trend
    if india_trend:
        show_national_trend(india_trend)
    
    # Show state divergence
    sorted_states, complete_states = show_state_divergence(state_trends)
    
    # Show year-by-year comparison
    if sorted_states and complete_states:
        show_year_pair_comparison(state_trends)
    
    print("\n" + "="*80)
    print("✓ ALL DATA FROM OFFICIAL UDISE+ CSV FILES (2018-25)")
    print("✓ NO FICTIONAL NUMBERS, NO ESTIMATES, NO PROJECTIONS")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
