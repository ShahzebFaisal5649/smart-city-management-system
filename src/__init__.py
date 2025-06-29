# src/__init__.py
# Day 1: Smart City Management System - Source Package

"""
Lahore Smart City Management System - Day 1 Data Collection Pipeline

This package contains modules for:
- Real government data collection (Punjab datasets)
- Synthetic data generation (energy, emergency services)
- Data validation and quality assessment
- Complete pipeline integration and export

Modules:
    data_collection: Real data collection from Punjab government sources
    synthetic_generators: Energy and emergency data generation
    data_validation: Comprehensive data quality validation
    main_pipeline: Complete Day 1 pipeline integration
    utils: Utility functions for data processing
"""

__version__ = "1.0.0"
__author__ = "Smart City Development Team"
__description__ = "Lahore Smart City Management System - Data Collection Pipeline"

# Import main classes for easy access
from .data_collection import LahoreDataCollector
from .synthetic_generators import LahoreSyntheticGenerator
from .data_validation import SmartCityDataValidator
from .main_pipeline import Day1Pipeline

__all__ = [
    'LahoreDataCollector',
    'LahoreSyntheticGenerator', 
    'SmartCityDataValidator',
    'Day1Pipeline'
]