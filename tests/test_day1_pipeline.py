# test_day1_pipeline.py
# Day 1: Complete pipeline testing and verification

import os
import sys
import pandas as pd
from datetime import datetime

def test_file_structure():
    """Test Day 1 file structure"""
    required_files = [
        "src/data_collection.py",
        "src/synthetic_generators.py", 
        "src/data_validation.py",
        "src/main_pipeline.py",
        "src/utils.py",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    return len(missing_files) == 0, missing_files

def test_data_files():
    """Test required data files exist"""
    data_files = [
        "motorvehiclesregisteredbytypedivisionanddistrictthepunjabuptil2021.csv",
        "accidentsdistrictwisepunjab.xlsx",
        "numberofhospitalsdispensariesmaternityruralhealthcentreandnumberofbedsinpakistan2.csv"
    ]
    
    existing_files = []
    missing_files = []
    
    for file in data_files:
        if os.path.exists(file):
            existing_files.append(file)
        else:
            missing_files.append(file)
    
    return len(missing_files) == 0, existing_files, missing_files

def test_imports():
    """Test Day 1 module imports"""
    try:
        # Test basic imports
        import pandas as pd
        import numpy as np
        import requests
        
        # Test custom modules
        sys.path.append('src')
        from data_collection import LahoreDataCollector
        from synthetic_generators import LahoreSyntheticGenerator
        from data_validation import SmartCityDataValidator
        from main_pipeline import Day1Pipeline
        import utils
        
        return True, "All imports successful"
        
    except Exception as e:
        return False, f"Import error: {str(e)}"

def test_data_collection():
    """Test data collection functionality"""
    try:
        sys.path.append('src')
        from data_collection import LahoreDataCollector
        
        # Test initialization
        collector = LahoreDataCollector("test_api_key")
        
        # Test vehicle data loading if file exists
        if os.path.exists("motorvehiclesregisteredbytypedivisionanddistrictthepunjabuptil2021.csv"):
            vehicle_data = collector.collect_traffic_data()
            if vehicle_data and 'vehicles' in vehicle_data:
                return True, f"Vehicle data loaded: {len(vehicle_data['vehicles'])} records"
        
        return True, "Data collection module functional"
        
    except Exception as e:
        return False, f"Data collection error: {str(e)}"

def test_synthetic_generation():
    """Test synthetic data generation"""
    try:
        sys.path.append('src')
        from synthetic_generators import LahoreSyntheticGenerator
        
        generator = LahoreSyntheticGenerator()
        
        # Test energy generation
        energy_data = generator.generate_energy_data(6663603)
        if len(energy_data) == 0:
            return False, "No energy data generated"
        
        # Test emergency generation
        emergency_data = generator.generate_emergency_data()
        if len(emergency_data) == 0:
            return False, "No emergency data generated"
        
        return True, f"Synthetic data: {len(energy_data)} energy, {len(emergency_data)} emergency records"
        
    except Exception as e:
        return False, f"Synthetic generation error: {str(e)}"

def test_validation():
    """Test data validation functionality"""
    try:
        sys.path.append('src')
        from data_validation import SmartCityDataValidator
        
        validator = SmartCityDataValidator()
        
        # Test with sample data
        sample_df = pd.DataFrame({
            'Division/ District': ['Lahore', 'Karachi'],
            'Total': [1000000, 2000000],
            'Motor Cars, Jeeps and Station Wagons': [500000, 800000]
        })
        
        validation_result = validator.validate_vehicle_data(sample_df)
        
        if 'quality_score' not in validation_result:
            return False, "Validation missing quality score"
        
        return True, f"Validation functional, quality score: {validation_result['quality_score']}"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def test_complete_pipeline():
    """Test complete Day 1 pipeline"""
    try:
        sys.path.append('src')
        from main_pipeline import Day1Pipeline
        
        # Test pipeline initialization
        pipeline = Day1Pipeline("a43d06572c2fb3c2b1b6ccd76a8ce7e4")
        
        # Test individual components
        collected_data = pipeline.execute_data_collection()
        synthetic_data = pipeline.execute_synthetic_generation()
        
        return True, f"Pipeline functional: {len(collected_data)} real, {len(synthetic_data)} synthetic datasets"
        
    except Exception as e:
        return False, f"Pipeline error: {str(e)}"

def run_day1_tests():
    """Run all Day 1 tests"""
    print("🧪 Day 1 Pipeline Testing")
    print("=" * 40)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Data Files", test_data_files),
        ("Module Imports", test_imports),
        ("Data Collection", test_data_collection),
        ("Synthetic Generation", test_synthetic_generation),
        ("Data Validation", test_validation),
        ("Complete Pipeline", test_complete_pipeline)
    ]
    
    results = {}
    
    for test_name, test_function in tests:
        try:
            if test_name == "Data Files":
                success, existing, missing = test_function()
                results[test_name] = success
                if success:
                    print(f"✅ {test_name}: All required files found")
                else:
                    print(f"❌ {test_name}: Missing files: {missing}")
            else:
                success, message = test_function()
                results[test_name] = success
                status = "✅" if success else "❌"
                print(f"{status} {test_name}: {message}")
                
        except Exception as e:
            results[test_name] = False
            print(f"❌ {test_name}: Test crashed - {str(e)}")
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 TEST SUMMARY")
    print("=" * 40)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("Day 1 pipeline is ready for execution")
        print("\nNext steps:")
        print("1. Run: python src/main_pipeline.py")
        print("2. Check: day1_summary.json")
        print("3. Verify: data/processed/ directory")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("Please fix issues before proceeding")
    
    return passed == total

if __name__ == "__main__":
    success = run_day1_tests()
    sys.exit(0 if success else 1)