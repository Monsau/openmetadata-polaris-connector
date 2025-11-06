"""
Polaris Connector for OpenMetadata

A comprehensive connector for ingesting metadata from Apache Polaris catalogs.
Architecture suivant le modèle Dremio.

Version 2.0.0 - Architecture simplifiée
"""

__version__ = "2.0.0"
__author__ = "Mustapha Fonsau"
__email__ = "mfonsau@talentys.eu"

from .polaris_source import PolarisSource
from .core.sync_engine import (
    PolarisAutoDiscovery,
    PolarisOpenMetadataSync,
    sync_polaris_to_openmetadata
)

__all__ = [
    "PolarisSource",
    "PolarisAutoDiscovery",
    "PolarisOpenMetadataSync",
    "sync_polaris_to_openmetadata"
]
