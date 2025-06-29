# src/main_pipeline.py
# Day 1: Complete Data Collection and Validation Pipeline Integration

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, Optional

from data_collection import LahoreDataCollector
from synthetic_generators import LahoreSyntheticGenerator  
from data_validation import SmartCityDataValidator

class Day1Pipeline:
    """Complete Day 1 pipeline for Lahore Smart City"""
    
    def __init__(self, weather_api_key: str):
        self.weather_api_key = weather_api_key
        self.collector = LahoreDataCollector(weather_api_key)
        self.generator = LahoreSyntheticGenerator()
        self.validator = SmartCityDataValidator()
        
        self.results = {
            'pipeline_start': datetime.now().isoformat(),
            'collected_data': {},
            'synthetic_data': {},
            'validation_results': {},
            'export_paths': {}
        }
    
    def execute_data_collection(self) -> Dict:
        """Execute complete data collection from real sources"""
        collection_results = self.collector.run_collection_pipeline()
        
        datasets = {}
        
        if collection_results['traffic']:
            if collection_results['traffic'].get('vehicles') is not None:
                datasets['traffic_vehicles'] = collection_results['traffic']['vehicles']
            if collection_results['traffic'].get('accidents') is not None:
                datasets['traffic_accidents'] = collection_results['traffic']['accidents']
        
        if collection_results['healthcare'] is not None:
            datasets['healthcare'] = collection_results['healthcare']
        
        if collection_results['weather'] is not None:
            self.results['weather_data'] = collection_results['weather']
        
        self.results['collected_data'] = datasets
        self.results['collection_status'] = collection_results['status']
        
        return datasets
    
    def execute_synthetic_generation(self, vehicle_count: Optional[int] = None) -> Dict:
        """Generate synthetic data for missing smart city components"""
        
        if vehicle_count is None and 'traffic_vehicles' in self.results['collected_data']:
            vehicles_df = self.results['collected_data']['traffic_vehicles']
            vehicle_count = int(vehicles_df['Total'].sum())
        elif vehicle_count is None:
            vehicle_count = 6663603
        
        synthetic_results = self.generator.generate_all_synthetic_data(vehicle_count)
        
        self.results['synthetic_data'] = {
            'energy': synthetic_results['energy'],
            'emergency': synthetic_results['emergency']
        }
        self.results['generation_parameters'] = synthetic_results['parameters']
        
        return self.results['synthetic_data']
    
    def execute_data_validation(self) -> Dict:
        """Run comprehensive data validation on all datasets"""
        
        all_datasets = {}
        all_datasets.update(self.results['collected_data'])
        all_datasets.update(self.results['synthetic_data'])
        
        validation_results = self.validator.run_comprehensive_validation(all_datasets)
        self.results['validation_results'] = validation_results
        
        return validation_results
    
    def export_datasets(self, output_dir: str = "data/processed") -> Dict:
        """Export all datasets to files for Day 2 processing"""
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        export_paths = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for dataset_name, df in self.results['collected_data'].items():
            if df is not None:
                file_path = os.path.join(output_dir, f"{dataset_name}_{timestamp}.csv")
                df.to_csv(file_path, index=False)
                export_paths[dataset_name] = file_path
        
        for dataset_name, df in self.results['synthetic_data'].items():
            if df is not None:
                file_path = os.path.join(output_dir, f"synthetic_{dataset_name}_{timestamp}.csv")
                df.to_csv(file_path, index=False)
                export_paths[f"synthetic_{dataset_name}"] = file_path
        
        if 'weather_data' in self.results:
            weather_path = os.path.join(output_dir, f"weather_data_{timestamp}.json")
            with open(weather_path, 'w') as f:
                json.dump(self.results['weather_data'], f, indent=2)
            export_paths['weather'] = weather_path
        
        validation_path = os.path.join(output_dir, f"validation_results_{timestamp}.json")
        with open(validation_path, 'w') as f:
            json.dump(self.results['validation_results'], f, indent=2)
        export_paths['validation'] = validation_path
        
        self.results['export_paths'] = export_paths
        return export_paths
    
    def generate_day1_summary(self) -> Dict:
        """Generate comprehensive Day 1 summary report"""
        
        summary = {
            'pipeline_execution': {
                'start_time': self.results['pipeline_start'],
                'end_time': datetime.now().isoformat(),
                'duration_minutes': self._calculate_duration_minutes()
            },
            'data_collection': {
                'real_datasets_collected': len(self.results['collected_data']),
                'synthetic_datasets_generated': len(self.results['synthetic_data']),
                'weather_data_available': 'weather_data' in self.results
            },
            'data_quality': {},
            'lahore_insights': {},
            'day2_readiness': {}
        }
        
        if 'validation_results' in self.results:
            validation = self.results['validation_results']
            summary['data_quality'] = {
                'overall_quality_score': validation.get('overall_quality', 0),
                'quality_status': validation.get('summary', {}).get('quality_status', 'Unknown'),
                'total_issues': validation.get('summary', {}).get('total_issues', 0),
                'datasets_validated': validation.get('summary', {}).get('datasets_validated', 0)
            }
        
        if 'traffic_vehicles' in self.results['collected_data']:
            vehicles_df = self.results['collected_data']['traffic_vehicles']
            total_vehicles = int(vehicles_df['Total'].sum())
            summary['lahore_insights']['total_vehicles'] = total_vehicles
            
            vehicle_types = {}
            for col in vehicles_df.columns:
                if col != 'Division/ District' and col != 'Total':
                    count = int(vehicles_df[col].sum())
                    if count > 0:
                        vehicle_types[col] = count
            summary['lahore_insights']['vehicle_distribution'] = vehicle_types
        
        if 'traffic_accidents' in self.results['collected_data']:
            accidents_df = self.results['collected_data']['traffic_accidents']
            summary['lahore_insights']['accident_records'] = len(accidents_df)
            
            years = accidents_df['YEAR '].unique()
            summary['lahore_insights']['accident_year_range'] = f"{min(years)}-{max(years)}"
        
        required_components = ['traffic_vehicles', 'traffic_accidents', 'energy', 'emergency']
        available_components = list(self.results['collected_data'].keys()) + \
                             [f"synthetic_{k}" for k in self.results['synthetic_data'].keys()]
        
        summary['day2_readiness'] = {
            'required_components': required_components,
            'available_components': available_components,
            'readiness_score': len([c for c in required_components 
                                   if c in available_components or f"synthetic_{c}" in available_components]) / len(required_components),
            'export_files_created': len(self.results.get('export_paths', {}))
        }
        
        return summary
    
    def _calculate_duration_minutes(self) -> float:
        """Calculate pipeline execution duration in minutes"""
        start_time = datetime.fromisoformat(self.results['pipeline_start'])
        end_time = datetime.now()
        duration = end_time - start_time
        return round(duration.total_seconds() / 60, 2)
    
    def run_complete_pipeline(self, output_dir: str = "data/processed") -> Dict:
        """Execute complete Day 1 pipeline"""
        
        collected_datasets = self.execute_data_collection()
        synthetic_datasets = self.execute_synthetic_generation()
        validation_results = self.execute_data_validation()
        export_paths = self.export_datasets(output_dir)
        summary = self.generate_day1_summary()
        
        final_results = {
            'summary': summary,
            'datasets': {
                'collected': list(collected_datasets.keys()),
                'synthetic': list(synthetic_datasets.keys())
            },
            'quality_score': validation_results.get('overall_quality', 0),
            'export_files': export_paths,
            'pipeline_success': True
        }
        
        return final_results

# CLI execution for Day 1
if __name__ == "__main__":
    import sys
    
    API_KEY = "a43d06572c2fb3c2b1b6ccd76a8ce7e4"
    
    if not API_KEY:
        print("Error: OpenWeatherMap API key required")
        sys.exit(1)
    
    pipeline = Day1Pipeline(weather_api_key=API_KEY)
    
    try:
        results = pipeline.run_complete_pipeline()
        
        print(f"Day 1 Pipeline Completed Successfully")
        print(f"Quality Score: {results['quality_score']:.1f}%")
        print(f"Datasets: {len(results['datasets']['collected'])} real, {len(results['datasets']['synthetic'])} synthetic")
        print(f"Export Files: {len(results['export_files'])}")
        
        with open("day1_summary.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print("Summary saved to day1_summary.json")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
        sys.exit(1)