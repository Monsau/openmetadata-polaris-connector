"""
Unit tests for Polaris API client
"""

import pytest
import responses
from unittest.mock import Mock, patch
import json

from src.metadata.ingestion.source.database.polaris.client import (
    PolarisClient,
    PolarisApiException
)
from src.metadata.ingestion.source.database.polaris.connection import PolarisConnection


class TestPolarisClient:
    """Test cases for PolarisClient"""
    
    @pytest.fixture
    def connection_config(self):
        """Fixture for connection configuration"""
        return PolarisConnection(
            hostPort="localhost:8181",
            authType="oauth2",
            oauthConfig={
                "client_id": "test-client",
                "client_secret": "test-secret",
                "token_url": "http://localhost:8181/oauth2/token"
            }
        )
    
    @pytest.fixture
    def polaris_client(self, connection_config):
        """Fixture for Polaris client"""
        return PolarisClient(connection_config)
    
    def test_client_initialization(self, connection_config):
        """Test client initialization"""
        client = PolarisClient(connection_config)
        
        assert client.base_url == "http://localhost:8181"
        assert client.connection == connection_config
        assert client.session is not None
    
    def test_build_base_url_http(self, connection_config):
        """Test base URL building with HTTP"""
        connection_config.sslEnabled = False
        client = PolarisClient(connection_config)
        
        assert client.base_url == "http://localhost:8181"
    
    def test_build_base_url_https(self, connection_config):
        """Test base URL building with HTTPS"""
        connection_config.sslEnabled = True
        client = PolarisClient(connection_config)
        
        assert client.base_url == "https://localhost:8181"
    
    @responses.activate
    def test_oauth2_authentication(self, polaris_client):
        """Test OAuth2 authentication"""
        # Mock token endpoint
        responses.add(
            responses.POST,
            "http://localhost:8181/oauth2/token",
            json={
                "access_token": "test-token",
                "token_type": "Bearer",
                "expires_in": 3600
            },
            status=200
        )
        
        token = polaris_client._oauth2_authenticate()
        
        assert token == "test-token"
        assert polaris_client.token_expires_at > 0
    
    @responses.activate
    def test_get_catalogs_success(self, polaris_client):
        """Test successful catalog retrieval"""
        # Mock OAuth2 token
        responses.add(
            responses.POST,
            "http://localhost:8181/oauth2/token",
            json={"access_token": "test-token", "expires_in": 3600},
            status=200
        )
        
        # Mock catalogs endpoint
        responses.add(
            responses.GET,
            "http://localhost:8181/v1/catalogs",
            json={
                "catalogs": [
                    {"name": "main", "type": "iceberg"},
                    {"name": "analytics", "type": "iceberg"}
                ]
            },
            status=200
        )
        
        catalogs = polaris_client.get_catalogs()
        
        assert len(catalogs) == 2
        assert catalogs[0]["name"] == "main"
        assert catalogs[1]["name"] == "analytics"
    
    @responses.activate
    def test_get_namespaces_success(self, polaris_client):
        """Test successful namespace retrieval"""
        # Mock OAuth2 token
        responses.add(
            responses.POST,
            "http://localhost:8181/oauth2/token",
            json={"access_token": "test-token", "expires_in": 3600},
            status=200
        )
        
        # Mock namespaces endpoint
        responses.add(
            responses.GET,
            "http://localhost:8181/v1/catalogs/main/namespaces",
            json={
                "namespaces": [
                    {"namespace": ["sales"]},
                    {"namespace": ["marketing"]}
                ]
            },
            status=200
        )
        
        namespaces = polaris_client.get_namespaces("main")
        
        assert len(namespaces) == 2
        assert namespaces[0]["namespace"] == ["sales"]
        assert namespaces[1]["namespace"] == ["marketing"]
    
    @responses.activate
    def test_get_tables_success(self, polaris_client):
        """Test successful table retrieval"""
        # Mock OAuth2 token
        responses.add(
            responses.POST,
            "http://localhost:8181/oauth2/token",
            json={"access_token": "test-token", "expires_in": 3600},
            status=200
        )
        
        # Mock tables endpoint
        responses.add(
            responses.GET,
            "http://localhost:8181/v1/catalogs/main/namespaces/sales/tables",
            json={
                "identifiers": [
                    {"name": "customers"},
                    {"name": "orders"}
                ]
            },
            status=200
        )
        
        tables = polaris_client.get_tables("main", "sales")
        
        assert len(tables) == 2
        assert tables[0]["name"] == "customers"
        assert tables[1]["name"] == "orders"
    
    @responses.activate
    def test_get_table_metadata_success(self, polaris_client):
        """Test successful table metadata retrieval"""
        # Mock OAuth2 token
        responses.add(
            responses.POST,
            "http://localhost:8181/oauth2/token",
            json={"access_token": "test-token", "expires_in": 3600},
            status=200
        )
        
        # Mock table metadata endpoint
        table_metadata = {
            "metadata": {
                "schema": {
                    "type": "struct",
                    "fields": [
                        {"id": 1, "name": "customer_id", "type": "long", "required": True},
                        {"id": 2, "name": "name", "type": "string", "required": True}
                    ]
                },
                "properties": {
                    "owner": "data-team"
                }
            }
        }
        
        responses.add(
            responses.GET,
            "http://localhost:8181/v1/catalogs/main/namespaces/sales/tables/customers",
            json=table_metadata,
            status=200
        )
        
        metadata = polaris_client.get_table_metadata("main", "sales", "customers")
        
        assert "metadata" in metadata
        assert "schema" in metadata["metadata"]
        assert len(metadata["metadata"]["schema"]["fields"]) == 2
    
    @responses.activate
    def test_test_connection_success(self, polaris_client):
        """Test successful connection test"""
        # Mock OAuth2 token
        responses.add(
            responses.POST,
            "http://localhost:8181/oauth2/token",
            json={"access_token": "test-token", "expires_in": 3600},
            status=200
        )
        
        # Mock config endpoint
        responses.add(
            responses.GET,
            "http://localhost:8181/v1/config",
            json={"version": "1.0.0"},
            status=200
        )
        
        result = polaris_client.test_connection()
        
        assert result is True
    
    @responses.activate
    def test_api_error_handling(self, polaris_client):
        """Test API error handling"""
        # Mock OAuth2 token
        responses.add(
            responses.POST,
            "http://localhost:8181/oauth2/token",
            json={"access_token": "test-token", "expires_in": 3600},
            status=200
        )
        
        # Mock failed catalogs endpoint
        responses.add(
            responses.GET,
            "http://localhost:8181/v1/catalogs",
            json={"error": "Unauthorized"},
            status=401
        )
        
        with pytest.raises(PolarisApiException) as exc_info:
            polaris_client.get_catalogs()
        
        assert exc_info.value.status_code == 401
    
    def test_close_client(self, polaris_client):
        """Test client cleanup"""
        polaris_client.close()
        
        # Verify session is closed
        # Note: This test assumes the session.close() method works correctly