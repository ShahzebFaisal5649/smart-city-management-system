# src/synthetic_generators.py
# Day 1: Synthetic Data Generators for Missing Smart City Components

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

class LahoreSyntheticGenerator:
    """Generate synthetic data for missing smart city components"""
    
    def __init__(self, base_population: int = 13000000):
        self.base_population = base_population
        self.random_seed = 42
        np.random.seed(self.random_seed)
        random.seed(self.random_seed)
    
    def generate_energy_data(self, vehicle_count: int = 6663603) -> pd.DataFrame:
        """Generate synthetic energy consumption data for Lahore"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        
        energy_data = []
        
        for timestamp in date_range:
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
            
            # Base consumption (MW) scaled by vehicle density
            base_consumption = (vehicle_count / 1000000) * 450
            
            # Hour-of-day pattern
            if 6 <= hour <= 9:  # Morning peak
                hour_factor = 1.3
            elif 18 <= hour <= 22:  # Evening peak  
                hour_factor = 1.4
            elif 0 <= hour <= 5:  # Night low
                hour_factor = 0.6
            else:
                hour_factor = 1.0
            
            # Day-of-week pattern
            if day_of_week < 5:  # Weekdays
                day_factor = 1.0
            else:  # Weekend
                day_factor = 0.85
            
            # Seasonal factor
            month = timestamp.month
            if month in [5, 6, 7, 8]:  # Summer
                seasonal_factor = 1.6
            elif month in [12, 1, 2]:  # Winter
                seasonal_factor = 1.2
            else:
                seasonal_factor = 1.0
            
            # Random variation
            noise = np.random.normal(1.0, 0.05)
            
            consumption = base_consumption * hour_factor * day_factor * seasonal_factor * noise
            
            energy_data.append({
                'timestamp': timestamp,
                'total_consumption_mw': round(consumption, 2),
                'residential_mw': round(consumption * 0.45, 2),
                'commercial_mw': round(consumption * 0.35, 2), 
                'industrial_mw': round(consumption * 0.20, 2),
                'grid_frequency_hz': round(50.0 + np.random.normal(0, 0.1), 2),
                'voltage_kv': round(132 + np.random.normal(0, 2), 1)
            })
        
        return pd.DataFrame(energy_data)
    
    def generate_emergency_data(self, accident_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Generate synthetic emergency/311 service requests for Lahore"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        emergency_data = []
        
        service_types = [
            'Traffic Signal Malfunction', 'Road Damage/Pothole', 'Street Light Out',
            'Water Main Break', 'Noise Complaint', 'Garbage Collection',
            'Tree Down/Damage', 'Electrical Hazard', 'Animal Control',
            'Public Health Concern', 'Infrastructure Damage', 'Emergency Response'
        ]
        
        priorities = ['High', 'Medium', 'Low']
        statuses = ['Open', 'In Progress', 'Closed', 'Pending']
        
        daily_requests = int((6663603 / 1000000) * 150)
        
        current_date = start_date
        request_id = 1000000
        
        while current_date <= end_date:
            day_requests = daily_requests + np.random.poisson(50)
            
            for _ in range(day_requests):
                # Fixed probability distribution for hours
                hour_probs = np.array([
                    0.02, 0.01, 0.01, 0.01, 0.02, 0.03,
                    0.05, 0.08, 0.10, 0.09, 0.08, 0.07,
                    0.06, 0.07, 0.08, 0.09, 0.10, 0.11,
                    0.09, 0.07, 0.05, 0.04, 0.03, 0.02
                ])
                # Normalize to ensure sum = 1.0
                hour_probs = hour_probs / hour_probs.sum()
                
                hour = np.random.choice(range(24), p=hour_probs)
                
                timestamp = current_date.replace(
                    hour=hour, 
                    minute=np.random.randint(0, 60),
                    second=np.random.randint(0, 60)
                )
                
                # Fixed probability distribution for service types
                service_probs = np.array([0.15, 0.12, 0.10, 0.08, 0.07, 0.08, 
                                        0.06, 0.05, 0.04, 0.06, 0.09, 0.10])
                # Normalize to ensure sum = 1.0
                service_probs = service_probs / service_probs.sum()
                
                service_type = np.random.choice(service_types, p=service_probs)
                
                if service_type in ['Emergency Response', 'Electrical Hazard', 'Water Main Break']:
                    priority = 'High'
                elif service_type in ['Traffic Signal Malfunction', 'Public Health Concern']:
                    priority = np.random.choice(['High', 'Medium'], p=[0.7, 0.3])
                else:
                    priority = np.random.choice(priorities, p=[0.1, 0.4, 0.5])
                
                days_old = (end_date - timestamp).days
                if days_old > 30:
                    status = np.random.choice(statuses, p=[0.1, 0.1, 0.7, 0.1])
                elif days_old > 7:
                    status = np.random.choice(statuses, p=[0.2, 0.3, 0.4, 0.1])
                else:
                    status = np.random.choice(statuses, p=[0.4, 0.4, 0.1, 0.1])
                
                lat = 31.5497 + np.random.normal(0, 0.1)
                lon = 74.3436 + np.random.normal(0, 0.1)
                
                emergency_data.append({
                    'request_id': f"LHR{request_id}",
                    'timestamp': timestamp,
                    'service_type': service_type,
                    'priority': priority,
                    'status': status,
                    'latitude': round(lat, 6),
                    'longitude': round(lon, 6),
                    'district': np.random.choice(['Lahore City', 'Lahore Cantonment', 
                                                'Model Town', 'Gulberg', 'DHA']),
                    'description': f"Service request for {service_type.lower()}",
                    'estimated_resolution_hours': self._get_resolution_time(service_type, priority)
                })
                
                request_id += 1
            
            current_date += timedelta(days=1)
        
        return pd.DataFrame(emergency_data)
    
    def _get_resolution_time(self, service_type: str, priority: str) -> int:
        """Estimate resolution time based on service type and priority"""
        base_times = {
            'Emergency Response': 1,
            'Electrical Hazard': 4,
            'Water Main Break': 8,
            'Traffic Signal Malfunction': 6,
            'Street Light Out': 24,
            'Road Damage/Pothole': 72,
            'Public Health Concern': 12,
            'Infrastructure Damage': 48,
            'Tree Down/Damage': 24,
            'Noise Complaint': 48,
            'Garbage Collection': 24,
            'Animal Control': 12
        }
        
        base_time = base_times.get(service_type, 24)
        
        if priority == 'High':
            return max(1, int(base_time * 0.5))
        elif priority == 'Medium':
            return base_time
        else:
            return int(base_time * 1.5)
    
    def generate_all_synthetic_data(self, vehicle_count: int = 6663603) -> Dict:
        """Generate all synthetic data components"""
        return {
            'energy': self.generate_energy_data(vehicle_count),
            'emergency': self.generate_emergency_data(),
            'generation_timestamp': datetime.now().isoformat(),
            'parameters': {
                'base_population': self.base_population,
                'vehicle_count': vehicle_count,
                'random_seed': self.random_seed
            }
        }