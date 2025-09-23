"""
Unit tests for Polaris connection
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError

from src.metadata.ingestion.source.database.polaris.connection import (
    PolarisConnection,
    PolarisOAuth2Config
)


class TestPolarisConnection:
    """Test cases for PolarisConnection"""
    
    def test_valid_connection_config(self):
        """Test valid connection configuration"""
        config_data = {
            "type": "Polaris",
            "hostPort": "localhost:8181",
            "authType": "oauth2",
            "oauthConfig": {
                "client_id": "test-client",
                "client_secret": "test-secret",
                "token_url": "http://localhost:8181/oauth2/token"
            }
        }
        
        connection = PolarisConnection(**config_data)
        
        assert connection.type == "Polaris"
        assert connection.hostPort == "localhost:8181"
        assert connection.authType == "oauth2"
        assert connection.connectionTimeout == 30
        assert connection.requestTimeout == 60
    
    def test_invalid_host_port_format(self):
        """Test invalid host:port format"""
        config_data = {
            "hostPort": "invalid-format",
            "authType": "oauth2"
        }
        
        with pytest.raises(ValidationError):
            PolarisConnection(**config_data)
    
    def test_invalid_auth_type(self):
        """Test invalid authentication type"""
        config_data = {
            "hostPort": "localhost:8181",
            "authType": "invalid_auth"
        }
        
        with pytest.raises(ValidationError):
            PolarisConnection(**config_data)
    
    def test_oauth2_config(self):
        """Test OAuth2 configuration"""
        oauth_data = {
            "client_id": "test-client",
            "client_secret": "test-secret",
            "token_url": "http://localhost:8181/oauth2/token",
            "scope": "catalog:read"
        }
        
        oauth_config = PolarisOAuth2Config(**oauth_data)
        
        assert oauth_config.client_id == "test-client"
        assert oauth_config.client_secret == "test-secret"
        assert oauth_config.token_url == "http://localhost:8181/oauth2/token"
        assert oauth_config.scope == "catalog:read"
    
    def test_connection_with_filters(self):
        """Test connection with catalog/namespace/table filters"""
        config_data = {
            "hostPort": "localhost:8181",
            "authType": "oauth2",
            "catalogFilter": "main|analytics",
            "namespaceFilter": "sales.*",
            "tableFilter": "customer.*"
        }
        
        connection = PolarisConnection(**config_data)
        
        assert connection.catalogFilter == "main|analytics"
        assert connection.namespaceFilter == "sales.*"
        assert connection.tableFilter == "customer.*"
    
    def test_ssl_configuration(self):
        """Test SSL configuration"""
        config_data = {
            "hostPort": "polaris.example.com:8181",
            "authType": "oauth2",
            "sslEnabled": True,
            "sslCertificate": "/path/to/cert.pem"
        }
        
        connection = PolarisConnection(**config_data)
        
        assert connection.sslEnabled is True
        assert connection.sslCertificate == "/path/to/cert.pem"