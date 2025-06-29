# find_data_files.py
# Helper script to locate your data files

import os
import glob
from pathlib import Path

def find_data_files():
    """Search for data files in common locations"""
    
    target_files = [
        "motorvehiclesregisteredbytypedivisionanddistrictthepunjabuptil2021.csv",
        "accidentsdistrictwisepunjab.xlsx",
        "numberofhospitalsdispensariesmaternityruralhealthcentreandnumberofbedsinpakistan2.csv",
        "trafficaccidentsannual.xlsx"
    ]
    
    # Search locations
    search_paths = [
        ".",  # Current directory
        "..",  # Parent directory
        "data",  # Data subdirectory
        "data/raw",  # Raw data subdirectory
        os.path.expanduser("~/Downloads"),  # Downloads folder
        os.path.expanduser("~/Desktop"),  # Desktop
        os.path.expanduser("~/Documents")  # Documents
    ]
    
    print("🔍 Searching for data files...")
    print("=" * 50)
    
    found_files = {}
    
    for file_name in target_files:
        print(f"\n📁 Looking for: {file_name}")
        found_locations = []
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                # Search in directory
                full_path = os.path.join(search_path, file_name)
                if os.path.exists(full_path):
                    abs_path = os.path.abspath(full_path)
                    found_locations.append(abs_path)
                    print(f"   ✅ Found: {abs_path}")
                
                # Also search with wildcards for partial matches
                pattern = os.path.join(search_path, f"*{file_name[:20]}*")
                matches = glob.glob(pattern)
                for match in matches:
                    if match not in found_locations:
                        abs_path = os.path.abspath(match)
                        found_locations.append(abs_path)
                        print(f"   🔍 Similar: {abs_path}")
        
        if not found_locations:
            print(f"   ❌ Not found in common locations")
        
        found_files[file_name] = found_locations
    
    # Summary and commands
    print("\n" + "=" * 50)
    print("📋 SUMMARY & NEXT STEPS")
    print("=" * 50)
    
    all_found = True
    copy_commands = []
    
    for file_name, locations in found_files.items():
        if locations:
            print(f"✅ {file_name}")
            if len(locations) == 1:
                source_path = locations[0]
                if os.path.dirname(source_path) != os.getcwd():
                    copy_commands.append(f'Copy-Item "{source_path}" "."')
            else:
                print(f"   Multiple copies found:")
                for i, loc in enumerate(locations):
                    print(f"   {i+1}. {loc}")
        else:
            print(f"❌ {file_name}")
            all_found = False
    
    if copy_commands:
        print(f"\n📋 COPY COMMANDS TO RUN:")
        print("Run these PowerShell commands to copy files to project root:")
        for cmd in copy_commands:
            print(f"   {cmd}")
        
        print(f"\nOr run all at once:")
        for cmd in copy_commands:
            print(cmd)
    
    if not all_found:
        print(f"\n🔍 MANUAL SEARCH SUGGESTIONS:")
        print(f"If files not found automatically, try:")
        print(f"1. Check your Downloads folder")
        print(f"2. Search Windows Explorer for '*.csv' and '*.xlsx'")
        print(f"3. Look in email attachments or cloud storage")
        print(f"4. Check if files have different names")
    
    return found_files

def generate_search_commands():
    """Generate Windows search commands"""
    print(f"\n🔍 WINDOWS SEARCH COMMANDS:")
    print("Run these in PowerShell to search your entire system:")
    
    files_to_find = [
        "motorvehiclesregisteredbytypedivisionanddistrictthepunjabuptil2021.csv",
        "accidentsdistrictwisepunjab.xlsx", 
        "numberofhospitalsdispensariesmaternityruralhealthcentreandnumberofbedsinpakistan2.csv"
    ]
    
    for file_name in files_to_find:
        short_name = file_name[:30] + "..."
        print(f'Get-ChildItem -Path C:\\ -Recurse -Name "*{file_name[:20]}*" -ErrorAction SilentlyContinue')
    
    print(f"\nOr search for any CSV/Excel files:")
    print(f'Get-ChildItem -Path C:\\Users\\user -Recurse -Include "*.csv","*.xlsx" -ErrorAction SilentlyContinue | Where-Object {{$_.Name -like "*punjab*" -or $_.Name -like "*accident*" -or $_.Name -like "*vehicle*"}}')

if __name__ == "__main__":
    found_files = find_data_files()
    generate_search_commands()
    
    # Quick test
    total_found = sum(1 for locations in found_files.values() if locations)
    print(f"\n🎯 RESULT: Found {total_found}/4 data files")
    
    if total_found >= 2:
        print("✅ Enough files found to run basic pipeline!")
    else:
        print("⚠️ Need to locate more data files before running pipeline")