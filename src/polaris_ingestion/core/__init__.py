"""
Core Ingestion Package

Provides the main orchestration and API client components for Polaris ingestion.
"""

from .ingestion_engine import IngestionEngine
from .openmetadata_client import OpenMetadataClient, TableDefinition, TableColumn

__all__ = [
    'IngestionEngine',
    'OpenMetadataClient', 
    'TableDefinition',
    'TableColumn'
]