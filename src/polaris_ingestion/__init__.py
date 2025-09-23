"""
Polaris Ingestion Package

Professional Apache Polaris to OpenMetadata ingestion toolkit.

This package provides a comprehensive solution for ingesting metadata from Apache Polaris
catalogs into OpenMetadata with proper lineage, source attribution, and governance controls.

Key Components:
- Core ingestion engine with health checks and verification
- Configuration management with type safety
- Demo environment setup tools
- OpenMetadata API client with full CRUD operations

Usage:
    # Run full ingestion
    python src/polaris_ingestion/main.py
    
    # Set up demo environment
    python src/polaris_ingestion/demo/demo_cli.py full-setup
    
    # Health checks only
    python src/polaris_ingestion/main.py --health-check-only
"""

__version__ = "1.0.0"
__author__ = "Polaris Integration Team"

from .core.ingestion_engine import IngestionEngine
from .core.openmetadata_client import OpenMetadataClient
from .utils.config_manager import ConfigManager
from .utils.health_checker import HealthChecker

__all__ = [
    "IngestionEngine",
    "OpenMetadataClient", 
    "ConfigManager",
    "HealthChecker"
]