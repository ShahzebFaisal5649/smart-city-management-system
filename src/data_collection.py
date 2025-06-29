# src/data_collection.py
# Day 1: Data Collection Pipeline for Lahore Smart City
# Replaces NYC/US datasets with Punjab government data + synthetic generation

import pandas as pd
import numpy as np
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class LahoreDataCollector:
    """
    Data collection pipeline for Lahore Smart City Management
    Maps existing Punjab datasets to smart city categories:
    - Traffic: Vehicle registration + accident data  
    - Energy: Synthetic generation based on city patterns
    - Weather: OpenWeatherMap API for Lahore
    - Emergency: Synthetic 311-style data based on accidents
    """
    
    def __init__(self, weather_api_key: str):
        self.weather_api_key = weather_api_key
        self.lahore_coords = {"lat": 31.5497, "lon": 74.3436}
        self.data_sources = {
            "traffic_vehicles": "motorvehiclesregisteredbytypedivisionanddistrictthepunjabuptil2021.csv",
            "traffic_accidents": "accidentsdistrictwisepunjab.xlsx", 
            "healthcare": "numberofhospitalsdispensariesmaternityruralhealthcentreandnumberofbedsinpakistan2.csv",
            "traffic_annual": "trafficaccidentsannual.xlsx"
        }
        self.collected_data = {}
    
    def collect_traffic_data(self) -> Dict:
        """Collect traffic data from vehicle registration and accidents (replaces NYC traffic)"""
        traffic_data = {}
        
        # Vehicle registration data
        try:
            df_vehicles = pd.read_csv(self.data_sources["traffic_vehicles"])
            df_vehicles.columns = df_vehicles.columns.str.strip()
            
            lahore_vehicles = df_vehicles[
                df_vehicles['Division/ District'].str.contains('Lahore', case=False, na=False)
            ].copy()
            
            # Clean numeric columns
            numeric_cols = [col for col in lahore_vehicles.columns if col != 'Division/ District']
            for col in numeric_cols:
                lahore_vehicles[col] = (lahore_vehicles[col].astype(str)
                                      .str.replace(',', '')
                                      .str.replace('nan', '0'))
                lahore_vehicles[col] = pd.to_numeric(lahore_vehicles[col], errors='coerce').fillna(0)
            
            traffic_data['vehicles'] = lahore_vehicles
            
        except Exception as e:
            traffic_data['vehicles'] = None
        
        # Accident data  
        try:
            df_accidents = pd.read_excel(self.data_sources["traffic_accidents"], sheet_name=0)
            df_accidents.columns = df_accidents.columns.str.strip()
            
            lahore_accidents = df_accidents[
                df_accidents['DISTRICT'].str.contains('Lahore', case=False, na=False)
            ].copy()
            
            lahore_accidents['NO OF CASES'] = pd.to_numeric(lahore_accidents['NO OF CASES'], errors='coerce')
            lahore_accidents['YEAR '] = pd.to_numeric(lahore_accidents['YEAR '], errors='coerce')
            
            traffic_data['accidents'] = lahore_accidents
            
        except Exception as e:
            traffic_data['accidents'] = None
        
        self.collected_data['traffic'] = traffic_data
        return traffic_data
    
    def collect_weather_data(self) -> Optional[Dict]:
        """Collect weather data from OpenWeatherMap API"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': self.lahore_coords['lat'],
                'lon': self.lahore_coords['lon'], 
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            weather_data = response.json()
            
            # Try air quality
            try:
                air_url = f"http://api.openweathermap.org/data/2.5/air_pollution"
                air_response = requests.get(air_url, params=params, timeout=10)
                air_response.raise_for_status()
                air_data = air_response.json()
                weather_data['air_quality'] = air_data
            except:
                weather_data['air_quality'] = None
            
            self.collected_data['weather'] = weather_data
            return weather_data
            
        except Exception as e:
            self.collected_data['weather'] = None
            return None
    
    def collect_healthcare_data(self) -> Optional[pd.DataFrame]:
        """Collect healthcare infrastructure data (supporting emergency services)"""
        try:
            df = pd.read_csv(self.data_sources["healthcare"])
            
            # Clean numeric columns
            for col in df.columns:
                if col != 'Year':
                    df[col] = (df[col].astype(str)
                             .str.replace(',', '')
                             .str.replace('nan', '0'))
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            self.collected_data['healthcare'] = df
            return df
            
        except Exception as e:
            self.collected_data['healthcare'] = None
            return None
    
    def run_collection_pipeline(self) -> Dict:
        """Execute complete data collection pipeline"""
        collection_results = {
            'traffic': self.collect_traffic_data(),
            'weather': self.collect_weather_data(), 
            'healthcare': self.collect_healthcare_data(),
            'collection_timestamp': datetime.now().isoformat(),
            'status': {}
        }
        
        # Status tracking
        for key, data in collection_results.items():
            if key not in ['collection_timestamp', 'status']:
                if data is not None:
                    if key == 'traffic':
                        collection_results['status'][key] = {
                            'vehicles': data.get('vehicles') is not None,
                            'accidents': data.get('accidents') is not None
                        }
                    else:
                        collection_results['status'][key] = True
                else:
                    collection_results['status'][key] = False
        
        return collection_results
    
    def get_data_summary(self) -> Dict:
        """Generate summary of collected data"""
        summary = {
            'lahore_coordinates': self.lahore_coords,
            'data_sources': len(self.data_sources),
            'collection_status': {}
        }
        
        if 'traffic' in self.collected_data and self.collected_data['traffic']:
            traffic = self.collected_data['traffic']
            if traffic.get('vehicles') is not None:
                total_vehicles = traffic['vehicles']['Total'].sum()
                summary['traffic_vehicles'] = int(total_vehicles)
            
            if traffic.get('accidents') is not None:
                total_accidents = len(traffic['accidents'])
                summary['accident_records'] = total_accidents
        
        if 'weather' in self.collected_data and self.collected_data['weather']:
            weather = self.collected_data['weather']
            summary['current_temperature'] = weather['main']['temp']
            summary['weather_status'] = weather['weather'][0]['description']
        
        if 'healthcare' in self.collected_data and self.collected_data['healthcare'] is not None:
            healthcare = self.collected_data['healthcare']
            summary['healthcare_years'] = f"{healthcare['Year'].min()}-{healthcare['Year'].max()}"
        
        return summary