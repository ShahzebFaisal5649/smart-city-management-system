# quick_fix_accident_data.py
# Fix the accident data column name issue

import pandas as pd

def fix_accident_data():
    """Fix the trailing space in YEAR column"""
    try:
        # Load the accident data
        df = pd.read_excel("data/processed/accidents-district-wise-punjab.xlsx", sheet_name=0)
        
        # Clean column names (remove trailing spaces)
        df.columns = df.columns.str.strip()
        
        print("Original columns:", list(df.columns))
        
        # Check for Lahore data
        lahore_data = df[df['DISTRICT'].str.contains('Lahore', case=False, na=False)]
        
        print(f"✅ Fixed column names")
        print(f"📊 Lahore accident records: {len(lahore_data)}")
        print(f"📅 Years available: {sorted(lahore_data['YEAR'].unique())}")
        
        # Show sample data
        print("\n📋 Sample Lahore accident data:")
        print(lahore_data[['YEAR', 'DISTRICT', 'ACCIDENT/CAUSALITIES', 'NO OF CASES']].head())
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_accident_data()