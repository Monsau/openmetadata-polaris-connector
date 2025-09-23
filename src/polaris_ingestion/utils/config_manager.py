"""
Configuration Manager

Handles loading and validation of Polaris ingestion configurations.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PolarisConfig:
    """Polaris connection configuration."""
    host: str = "localhost"
    port: int = 8181
    rest_endpoint: str = "http://localhost:8181"
    catalog_name: str = "polaris"
    warehouse_location: str = "/tmp/polaris-warehouse"


@dataclass  
class OpenMetadataConfig:
    """OpenMetadata connection configuration."""
    host_port: str = "http://localhost:8585/api"
    auth_provider: str = "openmetadata"
    jwt_token: Optional[str] = None


@dataclass
class IngestionConfig:
    """Complete ingestion configuration."""
    polaris: PolarisConfig
    openmetadata: OpenMetadataConfig
    service_name: str = "apache-polaris-catalog"
    include_tables: bool = True
    include_views: bool = True
    include_lineage: bool = True
    mark_deleted_tables: bool = True


class ConfigManager:
    """Manages configuration loading and validation for Polaris ingestion."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ConfigManager.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = config_path or "config/polaris-config.yaml"
        self.config: Optional[IngestionConfig] = None
    
    def load_config(self) -> IngestionConfig:
        """
        Load configuration from YAML file.
        
        Returns:
            IngestionConfig: Loaded configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
            ValueError: If required configuration is missing
        """
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                raw_config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML configuration: {e}")
        
        # Extract Polaris configuration
        source_config = raw_config.get('source', {})
        service_connection = source_config.get('serviceConnection', {}).get('config', {})
        
        polaris_config = PolarisConfig(
            host=self._extract_host(service_connection.get('hostPort', 'http://localhost:8181')),
            port=self._extract_port(service_connection.get('hostPort', 'http://localhost:8181')),
            rest_endpoint=service_connection.get('hostPort', 'http://localhost:8181'),
            catalog_name=service_connection.get('catalog', 'polaris'),
            warehouse_location=service_connection.get('warehouse', '/tmp/polaris-warehouse')
        )
        
        # Extract OpenMetadata configuration
        sink_config = raw_config.get('sink', {}).get('config', {})
        om_server_config = sink_config.get('openMetadataServerConfig', {})
        security_config = om_server_config.get('securityConfig', {})
        
        openmetadata_config = OpenMetadataConfig(
            host_port=om_server_config.get('hostPort', 'http://localhost:8585/api'),
            auth_provider=om_server_config.get('authProvider', 'openmetadata'),
            jwt_token=security_config.get('jwtToken')
        )
        
        # Extract source configuration
        source_config_details = source_config.get('sourceConfig', {}).get('config', {})
        
        self.config = IngestionConfig(
            polaris=polaris_config,
            openmetadata=openmetadata_config,
            service_name=source_config.get('serviceName', 'apache-polaris-catalog'),
            include_tables=source_config_details.get('includeTables', True),
            include_views=source_config_details.get('includeViews', True),
            include_lineage=source_config_details.get('includeTableLineage', True),
            mark_deleted_tables=source_config_details.get('markDeletedTables', True)
        )
        
        self._validate_config()
        return self.config
    
    def _extract_host(self, host_port: str) -> str:
        """Extract host from hostPort string."""
        if '://' in host_port:
            return host_port.split('://')[1].split(':')[0]
        return host_port.split(':')[0]
    
    def _extract_port(self, host_port: str) -> int:
        """Extract port from hostPort string."""
        try:
            if '://' in host_port:
                port_part = host_port.split('://')[1]
                if ':' in port_part:
                    return int(port_part.split(':')[1].split('/')[0])
            elif ':' in host_port:
                return int(host_port.split(':')[1])
            return 8181  # Default Polaris port
        except (ValueError, IndexError):
            return 8181
    
    def _validate_config(self) -> None:
        """Validate the loaded configuration."""
        if not self.config:
            raise ValueError("Configuration not loaded")
        
        if not self.config.openmetadata.jwt_token:
            raise ValueError("OpenMetadata JWT token is required")
        
        if not self.config.polaris.rest_endpoint:
            raise ValueError("Polaris REST endpoint is required")
    
    def get_config(self) -> Optional[IngestionConfig]:
        """Get the current configuration."""
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration parameters."""
        if not self.config:
            raise ValueError("Configuration not loaded. Call load_config() first.")
        
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            elif hasattr(self.config.polaris, key):
                setattr(self.config.polaris, key, value)
            elif hasattr(self.config.openmetadata, key):
                setattr(self.config.openmetadata, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        if not self.config:
            return {}
        
        return {
            'polaris': {
                'host': self.config.polaris.host,
                'port': self.config.polaris.port,
                'rest_endpoint': self.config.polaris.rest_endpoint,
                'catalog_name': self.config.polaris.catalog_name,
                'warehouse_location': self.config.polaris.warehouse_location
            },
            'openmetadata': {
                'host_port': self.config.openmetadata.host_port,
                'auth_provider': self.config.openmetadata.auth_provider,
                'jwt_token': self.config.openmetadata.jwt_token[:20] + "..." if self.config.openmetadata.jwt_token else None
            },
            'ingestion': {
                'service_name': self.config.service_name,
                'include_tables': self.config.include_tables,
                'include_views': self.config.include_views,
                'include_lineage': self.config.include_lineage,
                'mark_deleted_tables': self.config.mark_deleted_tables
            }
        }