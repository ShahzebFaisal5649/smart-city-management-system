# src/utils.py  
# Day 1: Utility Functions for Data Processing and Validation

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple

class DataUtils:
    """Utility functions for data processing and manipulation"""
    
    @staticmethod
    def clean_numeric_column(series: pd.Series, default_value: float = 0) -> pd.Series:
        """Clean numeric column by removing commas and converting to numeric"""
        cleaned = (series.astype(str)
                  .str.replace(',', '')
                  .str.replace('nan', str(default_value))
                  .str.strip())
        return pd.to_numeric(cleaned, errors='coerce').fillna(default_value)
    
    @staticmethod
    def filter_lahore_data(df: pd.DataFrame, district_column: str) -> pd.DataFrame:
        """Filter DataFrame for Lahore-specific records"""
        return df[df[district_column].str.contains('Lahore', case=False, na=False)].copy()
    
    @staticmethod
    def calculate_percentage_change(start_value: float, end_value: float) -> float:
        """Calculate percentage change between two values"""
        if start_value == 0:
            return 0 if end_value == 0 else 100
        return ((end_value - start_value) / start_value) * 100
    
    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> Dict:
        """Generate summary statistics for DataFrame"""
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            'null_counts': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.astype(str).to_dict()
        }
        
        # Numeric columns summary
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        return summary

class FileUtils:
    """Utility functions for file operations"""
    
    @staticmethod
    def ensure_directory(path: str) -> str:
        """Ensure directory exists, create if not"""
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict:
        """Get file information"""
        if not os.path.exists(file_path):
            return {'exists': False}
        
        stat = os.stat(file_path)
        return {
            'exists': True,
            'size_mb': round(stat.st_size / 1024 / 1024, 2),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': os.path.splitext(file_path)[1].lower()
        }
    
    @staticmethod
    def save_json(data: Dict, file_path: str, indent: int = 2) -> bool:
        """Save dictionary to JSON file"""
        try:
            FileUtils.ensure_directory(os.path.dirname(file_path))
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=indent, default=str)
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_json(file_path: str) -> Optional[Dict]:
        """Load JSON file to dictionary"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None

class WeatherUtils:
    """Utility functions for weather data processing"""
    
    @staticmethod
    def kelvin_to_celsius(kelvin_temp: float) -> float:
        """Convert Kelvin to Celsius"""
        return round(kelvin_temp - 273.15, 2)
    
    @staticmethod
    def get_air_quality_description(aqi: int) -> str:
        """Get air quality description from AQI value"""
        if aqi == 1:
            return "Good"
        elif aqi == 2:
            return "Fair" 
        elif aqi == 3:
            return "Moderate"
        elif aqi == 4:
            return "Poor"
        elif aqi == 5:
            return "Very Poor"
        else:
            return "Unknown"
    
    @staticmethod
    def categorize_weather_condition(description: str) -> str:
        """Categorize weather condition for analysis"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['rain', 'drizzle', 'shower']):
            return "Rainy"
        elif any(word in description_lower for word in ['cloud', 'overcast']):
            return "Cloudy"
        elif any(word in description_lower for word in ['clear', 'sunny']):
            return "Clear"
        elif any(word in description_lower for word in ['mist', 'fog', 'haze']):
            return "Misty"
        elif any(word in description_lower for word in ['storm', 'thunder']):
            return "Stormy"
        else:
            return "Other"

class ValidationUtils:
    """Utility functions for data validation"""
    
    @staticmethod
    def check_required_columns(df: pd.DataFrame, required_cols: List[str]) -> Tuple[bool, List[str]]:
        """Check if DataFrame has required columns"""
        missing_cols = [col for col in required_cols if col not in df.columns]
        return len(missing_cols) == 0, missing_cols
    
    @staticmethod
    def validate_coordinate_bounds(lat: float, lon: float, 
                                 lat_bounds: Tuple[float, float], 
                                 lon_bounds: Tuple[float, float]) -> bool:
        """Validate if coordinates are within specified bounds"""
        return (lat_bounds[0] <= lat <= lat_bounds[1] and 
                lon_bounds[0] <= lon <= lon_bounds[1])
    
    @staticmethod
    def check_data_completeness(df: pd.DataFrame, threshold: float = 0.95) -> Dict:
        """Check data completeness against threshold"""
        total_cells = len(df) * len(df.columns)
        non_null_cells = total_cells - df.isnull().sum().sum()
        completeness_ratio = non_null_cells / total_cells if total_cells > 0 else 0
        
        return {
            'completeness_ratio': round(completeness_ratio, 4),
            'meets_threshold': completeness_ratio >= threshold,
            'total_cells': total_cells,
            'non_null_cells': non_null_cells,
            'null_cells': total_cells - non_null_cells
        }
    
    @staticmethod
    def validate_year_range(years: pd.Series, min_year: int = 2000, 
                          max_year: Optional[int] = None) -> Dict:
        """Validate year values are within reasonable range"""
        if max_year is None:
            max_year = datetime.now().year
        
        valid_years = years.dropna()
        invalid_count = len(years) - len(valid_years)
        out_of_range = ((valid_years < min_year) | (valid_years > max_year)).sum()
        
        return {
            'total_years': len(years),
            'valid_years': len(valid_years),
            'invalid_count': invalid_count,
            'out_of_range_count': out_of_range,
            'year_range': f"{valid_years.min()}-{valid_years.max()}" if len(valid_years) > 0 else "No valid years",
            'is_valid': invalid_count == 0 and out_of_range == 0
        }

class DateTimeUtils:
    """Utility functions for date/time operations"""
    
    @staticmethod
    def generate_time_series(start_date: datetime, end_date: datetime, 
                           freq: str = 'H') -> pd.DatetimeIndex:
        """Generate time series between dates"""
        return pd.date_range(start=start_date, end=end_date, freq=freq)
    
    @staticmethod
    def get_hour_category(hour: int) -> str:
        """Categorize hour into time periods"""
        if 6 <= hour <= 9:
            return "Morning Peak"
        elif 10 <= hour <= 16:
            return "Day"
        elif 17 <= hour <= 20:
            return "Evening Peak" 
        elif 21 <= hour <= 23:
            return "Evening"
        else:
            return "Night"
    
    @staticmethod
    def get_day_type(date: datetime) -> str:
        """Determine if date is weekday or weekend"""
        return "Weekend" if date.weekday() >= 5 else "Weekday"
    
    @staticmethod
    def calculate_time_difference_hours(start_time: datetime, end_time: datetime) -> float:
        """Calculate time difference in hours"""
        diff = end_time - start_time
        return round(diff.total_seconds() / 3600, 2)

class ConfigUtils:
    """Utility functions for configuration management"""
    
    LAHORE_COORDS = {"lat": 31.5497, "lon": 74.3436}
    LAHORE_BOUNDS = {"lat": (31.3, 31.8), "lon": (74.0, 74.7)}
    
    @staticmethod
    def get_default_config() -> Dict:
        """Get default configuration for Lahore Smart City"""
        return {
            'city': {
                'name': 'Lahore',
                'country': 'Pakistan',
                'coordinates': ConfigUtils.LAHORE_COORDS,
                'bounds': ConfigUtils.LAHORE_BOUNDS,
                'timezone': 'Asia/Karachi',
                'population_estimate': 13000000
            },
            'data_sources': {
                'vehicles': 'motorvehiclesregisteredbytypedivisionanddistrictthepunjabuptil2021.csv',
                'accidents': 'accidentsdistrictwisepunjab.xlsx',
                'healthcare': 'numberofhospitalsdispensariesmaternityruralhealthcentreandnumberofbedsinpakistan2.csv'
            },
            'validation': {
                'completeness_threshold': 0.95,
                'quality_threshold': 80,
                'year_range': {'min': 2000, 'max': datetime.now().year}
            },
            'synthetic_data': {
                'energy_base_mw': 2970,
                'emergency_daily_requests': 1000,
                'random_seed': 42
            }
        }
    
    @staticmethod
    def validate_config(config: Dict) -> Tuple[bool, List[str]]:
        """Validate configuration structure"""
        required_sections = ['city', 'data_sources', 'validation', 'synthetic_data']
        missing_sections = [section for section in required_sections if section not in config]
        
        errors = []
        if missing_sections:
            errors.append(f"Missing configuration sections: {missing_sections}")
        
        # Validate city coordinates
        if 'city' in config and 'coordinates' in config['city']:
            coords = config['city']['coordinates']
            if not isinstance(coords, dict) or 'lat' not in coords or 'lon' not in coords:
                errors.append("Invalid city coordinates format")
        
        return len(errors) == 0, errors