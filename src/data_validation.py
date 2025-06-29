# src/data_validation.py
# Day 1: Data Quality Validation Pipeline

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class SmartCityDataValidator:
    """Comprehensive data validation pipeline for Lahore Smart City data"""
    
    def __init__(self):
        self.validation_results = {}
        self.error_threshold = 0.05
        
        self.schemas = {
            'vehicles': ['Division/ District', 'Total', 'Motor Cars, Jeeps and Station Wagons'],
            'accidents': ['YEAR ', 'PROVINCE', 'DISTRICT', 'ACCIDENT/CAUSALITIES', 'NO OF CASES'],
            'healthcare': ['Year', 'Hospitals', 'Dispensaries', 'Total Beds'],
            'energy': ['timestamp', 'total_consumption_mw', 'residential_mw'],
            'emergency': ['request_id', 'timestamp', 'service_type', 'priority', 'status']
        }
    
    def validate_vehicle_data(self, df: pd.DataFrame) -> Dict:
        """Validate vehicle registration data quality"""
        validation = {
            'data_type': 'vehicles',
            'total_records': len(df),
            'issues': [],
            'quality_score': 100,
            'lahore_specific': {}
        }
        
        # Schema validation
        missing_cols = [col for col in self.schemas['vehicles'] if col not in df.columns]
        if missing_cols:
            validation['issues'].append(f"Missing columns: {missing_cols}")
            validation['quality_score'] -= 20
        
        # Lahore data validation
        lahore_records = df[df['Division/ District'].str.contains('Lahore', case=False, na=False)]
        validation['lahore_specific']['records_found'] = len(lahore_records)
        
        if len(lahore_records) == 0:
            validation['issues'].append("No Lahore records found")
            validation['quality_score'] -= 30
        else:
            # Validate numeric data
            numeric_cols = [col for col in df.columns if col != 'Division/ District']
            for col in numeric_cols:
                if col in lahore_records.columns:
                    try:
                        cleaned = lahore_records[col].astype(str).str.replace(',', '').str.replace('nan', '0')
                        numeric_values = pd.to_numeric(cleaned, errors='coerce')
                        null_count = numeric_values.isnull().sum()
                        
                        if null_count > 0:
                            validation['issues'].append(f"Invalid values in {col}: {null_count}")
                            validation['quality_score'] -= 5
                        
                        if col == 'Total' and not numeric_values.empty:
                            total_vehicles = numeric_values.iloc[0]
                            if total_vehicles < 1000000 or total_vehicles > 10000000:
                                validation['issues'].append(f"Unusual total vehicle count: {total_vehicles}")
                                validation['quality_score'] -= 10
                            
                            validation['lahore_specific']['total_vehicles'] = int(total_vehicles)
                    
                    except Exception as e:
                        validation['issues'].append(f"Error processing {col}: {str(e)}")
                        validation['quality_score'] -= 10
        
        return validation
    
    def validate_accident_data(self, df: pd.DataFrame) -> Dict:
        """Validate traffic accident data quality"""
        validation = {
            'data_type': 'accidents',
            'total_records': len(df),
            'issues': [],
            'quality_score': 100,
            'lahore_specific': {}
        }
        
        missing_cols = [col for col in self.schemas['accidents'] if col not in df.columns]
        if missing_cols:
            validation['issues'].append(f"Missing columns: {missing_cols}")
            validation['quality_score'] -= 20
        
        lahore_records = df[df['DISTRICT'].str.contains('Lahore', case=False, na=False)]
        validation['lahore_specific']['records_found'] = len(lahore_records)
        
        if len(lahore_records) == 0:
            validation['issues'].append("No Lahore accident records found")
            validation['quality_score'] -= 30
        else:
            if 'YEAR ' in lahore_records.columns:
                years = pd.to_numeric(lahore_records['YEAR '], errors='coerce')
                valid_years = years.dropna()
                
                if len(valid_years) != len(years):
                    validation['issues'].append("Invalid year values found")
                    validation['quality_score'] -= 10
                
                if not valid_years.empty:
                    year_range = f"{valid_years.min()}-{valid_years.max()}"
                    validation['lahore_specific']['year_range'] = year_range
                    
                    if valid_years.min() < 2000 or valid_years.max() > datetime.now().year:
                        validation['issues'].append(f"Unusual year range: {year_range}")
                        validation['quality_score'] -= 10
            
            if 'NO OF CASES' in lahore_records.columns:
                cases = pd.to_numeric(lahore_records['NO OF CASES'], errors='coerce')
                valid_cases = cases.dropna()
                
                if len(valid_cases) != len(cases):
                    validation['issues'].append("Invalid case count values")
                    validation['quality_score'] -= 10
                
                if not valid_cases.empty:
                    validation['lahore_specific']['total_cases'] = int(valid_cases.sum())
                    
                    if (valid_cases < 0).any():
                        validation['issues'].append("Negative case counts found")
                        validation['quality_score'] -= 15
        
        return validation
    
    def validate_healthcare_data(self, df: pd.DataFrame) -> Dict:
        """Validate healthcare infrastructure data quality"""
        validation = {
            'data_type': 'healthcare',
            'total_records': len(df),
            'issues': [],
            'quality_score': 100,
            'trends': {}
        }
        
        missing_cols = [col for col in self.schemas['healthcare'] if col not in df.columns]
        if missing_cols:
            validation['issues'].append(f"Missing columns: {missing_cols}")
            validation['quality_score'] -= 20
        
        if 'Year' in df.columns:
            years = sorted(df['Year'].unique())
            validation['trends']['year_range'] = f"{min(years)}-{max(years)}"
            
            expected_years = list(range(min(years), max(years) + 1))
            missing_years = set(expected_years) - set(years)
            if missing_years:
                validation['issues'].append(f"Missing years: {sorted(missing_years)}")
                validation['quality_score'] -= 10
        
        numeric_cols = ['Hospitals', 'Dispensaries', 'Total Beds']
        for col in numeric_cols:
            if col in df.columns:
                cleaned = df[col].astype(str).str.replace(',', '').str.replace('nan', '0')
                numeric_values = pd.to_numeric(cleaned, errors='coerce')
                
                null_count = numeric_values.isnull().sum()
                if null_count > 0:
                    validation['issues'].append(f"Invalid values in {col}: {null_count}")
                    validation['quality_score'] -= 5
                
                if len(numeric_values) > 1:
                    trend = numeric_values.iloc[-1] - numeric_values.iloc[0]
                    validation['trends'][col] = {
                        'start_value': int(numeric_values.iloc[0]),
                        'end_value': int(numeric_values.iloc[-1]),
                        'change': int(trend)
                    }
                    
                    if trend < 0:
                        validation['issues'].append(f"{col} shows negative trend")
                        validation['quality_score'] -= 5
        
        return validation
    
    def validate_synthetic_energy(self, df: pd.DataFrame) -> Dict:
        """Validate synthetic energy data quality"""
        validation = {
            'data_type': 'energy',
            'total_records': len(df),
            'issues': [],
            'quality_score': 100,
            'patterns': {}
        }
        
        missing_cols = [col for col in self.schemas['energy'] if col not in df.columns]
        if missing_cols:
            validation['issues'].append(f"Missing columns: {missing_cols}")
            validation['quality_score'] -= 20
        
        if 'timestamp' in df.columns:
            try:
                timestamps = pd.to_datetime(df['timestamp'])
                validation['patterns']['time_range'] = f"{timestamps.min()} to {timestamps.max()}"
                
                duplicates = timestamps.duplicated().sum()
                if duplicates > 0:
                    validation['issues'].append(f"Duplicate timestamps: {duplicates}")
                    validation['quality_score'] -= 10
                
                time_diff = timestamps.diff().dropna()
                expected_freq = timedelta(hours=1)
                irregular_intervals = (time_diff != expected_freq).sum()
                if irregular_intervals > 0:
                    validation['issues'].append(f"Irregular time intervals: {irregular_intervals}")
                    validation['quality_score'] -= 5
                    
            except Exception as e:
                validation['issues'].append(f"Timestamp parsing error: {str(e)}")
                validation['quality_score'] -= 15
        
        energy_cols = ['total_consumption_mw', 'residential_mw', 'commercial_mw', 'industrial_mw']
        for col in energy_cols:
            if col in df.columns:
                values = pd.to_numeric(df[col], errors='coerce')
                
                null_count = values.isnull().sum()
                if null_count > 0:
                    validation['issues'].append(f"Null values in {col}: {null_count}")
                    validation['quality_score'] -= 5
                
                negative_count = (values < 0).sum()
                if negative_count > 0:
                    validation['issues'].append(f"Negative values in {col}: {negative_count}")
                    validation['quality_score'] -= 10
                
                validation['patterns'][col] = {
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'mean': float(values.mean()),
                    'std': float(values.std())
                }
        
        return validation
    
    def validate_synthetic_emergency(self, df: pd.DataFrame) -> Dict:
        """Validate synthetic emergency data quality"""
        validation = {
            'data_type': 'emergency',
            'total_records': len(df),
            'issues': [],
            'quality_score': 100,
            'distribution': {}
        }
        
        missing_cols = [col for col in self.schemas['emergency'] if col not in df.columns]
        if missing_cols:
            validation['issues'].append(f"Missing columns: {missing_cols}")
            validation['quality_score'] -= 20
        
        if 'request_id' in df.columns:
            duplicate_ids = df['request_id'].duplicated().sum()
            if duplicate_ids > 0:
                validation['issues'].append(f"Duplicate request IDs: {duplicate_ids}")
                validation['quality_score'] -= 15
        
        categorical_cols = ['service_type', 'priority', 'status']
        for col in categorical_cols:
            if col in df.columns:
                unique_values = df[col].unique()
                validation['distribution'][col] = list(unique_values)
                
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    validation['issues'].append(f"Null values in {col}: {null_count}")
                    validation['quality_score'] -= 5
        
        if 'latitude' in df.columns and 'longitude' in df.columns:
            lat_values = pd.to_numeric(df['latitude'], errors='coerce')
            lon_values = pd.to_numeric(df['longitude'], errors='coerce')
            
            lahore_lat_bounds = (31.3, 31.8)
            lahore_lon_bounds = (74.0, 74.7)
            
            out_of_bounds = ((lat_values < lahore_lat_bounds[0]) | 
                           (lat_values > lahore_lat_bounds[1]) |
                           (lon_values < lahore_lon_bounds[0]) | 
                           (lon_values > lahore_lon_bounds[1])).sum()
            
            if out_of_bounds > 0:
                validation['issues'].append(f"Coordinates outside Lahore bounds: {out_of_bounds}")
                validation['quality_score'] -= 5
        
        return validation
    
    def run_comprehensive_validation(self, datasets: Dict) -> Dict:
        """Run complete validation pipeline on all datasets"""
        validation_results = {
            'validation_timestamp': datetime.now().isoformat(),
            'overall_quality': 100,
            'dataset_validations': {},
            'summary': {}
        }
        
        dataset_mapping = {
            'traffic_vehicles': 'validate_vehicle_data',
            'traffic_accidents': 'validate_accident_data', 
            'healthcare': 'validate_healthcare_data',
            'energy': 'validate_synthetic_energy',
            'emergency': 'validate_synthetic_emergency'
        }
        
        total_datasets = 0
        total_quality = 0
        
        for dataset_name, data in datasets.items():
            if data is not None and isinstance(data, pd.DataFrame):
                if dataset_name in dataset_mapping:
                    validator_method = getattr(self, dataset_mapping[dataset_name])
                    result = validator_method(data)
                    validation_results['dataset_validations'][dataset_name] = result
                    
                    total_datasets += 1
                    total_quality += result['quality_score']
        
        if total_datasets > 0:
            validation_results['overall_quality'] = total_quality / total_datasets
        
        validation_results['summary'] = {
            'datasets_validated': total_datasets,
            'average_quality_score': validation_results['overall_quality'],
            'total_issues': sum(len(v['issues']) for v in validation_results['dataset_validations'].values()),
            'quality_status': self._get_quality_status(validation_results['overall_quality'])
        }
        
        return validation_results
    
    def _get_quality_status(self, score: float) -> str:
        """Determine quality status based on score"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good" 
        elif score >= 70:
            return "Fair"
        else:
            return "Poor"