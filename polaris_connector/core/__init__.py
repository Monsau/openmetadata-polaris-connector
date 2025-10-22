"""
Polaris Connector Core Module

Exports core functionality for Polaris discovery and synchronization.
"""

from .sync_engine import (
    PolarisAutoDiscovery,
    PolarisOpenMetadataSync,
    sync_polaris_to_openmetadata
)

__all__ = [
    "PolarisAutoDiscovery",
    "PolarisOpenMetadataSync",
    "sync_polaris_to_openmetadata"
]
