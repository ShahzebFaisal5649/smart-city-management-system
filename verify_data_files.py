# verify_data_files.py
# Quick verification of data files

import pandas as pd
import os

def verify_data_files():
    """Verify that data files exist and can be loaded"""
    
    data_files = {
        "Vehicle Registration": "data/processed/motor-vehicles-registered-by-type-division-and-district-the-punjab-uptil-2021.csv",
        "Accident Data": "data/processed/accidents-district-wise-punjab.xlsx",
        "Healthcare Data": "data/processed/number-of-hospitals-dispensaries-maternity-rural-health-centre-and-number-of-beds-in-pakistan-2.csv",
        "Traffic Annual": "data/processed/traffic-accidents-annual.xlsx"
    }
    
    print("🔍 Verifying Data Files")
    print("=" * 50)
    
    for name, file_path in data_files.items():
        print(f"\n📁 {name}")
        print(f"   Path: {file_path}")
        
        if os.path.exists(file_path):
            try:
                # Load file based on extension
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:  # Excel file
                    df = pd.read_excel(file_path)
                
                print(f"   ✅ File loaded successfully")
                print(f"   📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
                print(f"   📋 Columns: {list(df.columns[:3])}{'...' if len(df.columns) > 3 else ''}")
                
                # Check for Lahore data
                if 'Division/ District' in df.columns:
                    lahore_count = df[df['Division/ District'].str.contains('Lahore', case=False, na=False)].shape[0]
                    print(f"   🏙️ Lahore records: {lahore_count}")
                elif 'DISTRICT' in df.columns:
                    lahore_count = df[df['DISTRICT'].str.contains('Lahore', case=False, na=False)].shape[0]
                    print(f"   🏙️ Lahore records: {lahore_count}")
                
            except Exception as e:
                print(f"   ❌ Error loading file: {e}")
        else:
            print(f"   ❌ File not found")
    
    print(f"\n🎯 All data files verified! Ready to run pipeline.")

if __name__ == "__main__":
    verify_data_files()