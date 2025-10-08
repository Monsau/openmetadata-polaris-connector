"""
Tests for the Polaris connector
"""

import pytest
from unittest.mock import Mock, patch
from connectors.polaris.connector import PolarisConnector
from connectors.polaris.polaris_connector import PolarisSource


class TestPolarisConnector:
    """Test cases for PolarisConnector class"""
    
    def test_init_oauth2(self):
        """Test connector initialization with OAuth2"""
        connector = PolarisConnector(
            host="localhost",
            port=8181,
            auth_type="oauth2",
            client_id="test_client",
            client_secret="test_secret"
        )
        
        assert connector.host == "localhost"
        assert connector.port == 8181
        assert connector.auth_type == "oauth2"
        assert connector.client_id == "test_client"
        assert connector.client_secret == "test_secret"
        assert connector.base_url == "http://localhost:8181"
    
    def test_init_with_ssl(self):
        """Test connector initialization with SSL enabled"""
        connector = PolarisConnector(
            host="polaris.example.com",
            port=443,
            use_ssl=True
        )
        
        assert connector.base_url == "https://polaris.example.com:443"
    
    def test_init_api_key(self):
        """Test connector initialization with API key"""
        connector = PolarisConnector(
            host="localhost",
            auth_type="api_key",
            api_key="test_api_key"
        )
        
        assert connector.auth_type == "api_key"
        assert connector.api_key == "test_api_key"
    
    def test_init_basic_auth(self):
        """Test connector initialization with basic auth"""
        connector = PolarisConnector(
            host="localhost",
            auth_type="basic",
            username="test_user",
            password="test_pass"
        )
        
        assert connector.auth_type == "basic"
        assert connector.username == "test_user"
        assert connector.password == "test_pass"
    
    @patch('connectors.polaris.connector.requests.Session')
    def test_oauth2_connect_success(self, mock_session_class):
        """Test successful OAuth2 connection"""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock token response
        mock_token_response = Mock()
        mock_token_response.json.return_value = {"access_token": "test_token"}
        mock_token_response.raise_for_status = Mock()
        
        # Mock config response
        mock_config_response = Mock()
        mock_config_response.raise_for_status = Mock()
        
        mock_session.post.return_value = mock_token_response
        mock_session.get.return_value = mock_config_response
        
        connector = PolarisConnector(
            host="localhost",
            auth_type="oauth2",
            client_id="test_client",
            client_secret="test_secret"
        )
        
        result = connector.connect()
        
        assert result is True
        assert connector.access_token == "test_token"
        mock_session.post.assert_called_once()
        mock_session.get.assert_called_once()
    
    @patch('connectors.polaris.connector.requests.Session')
    def test_get_catalogs(self, mock_session_class):
        """Test getting catalogs"""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "catalogs": [
                {"name": "catalog1"},
                {"name": "catalog2"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_session.request.return_value = mock_response
        
        connector = PolarisConnector(
            host="localhost",
            auth_type="api_key",
            api_key="test_key"
        )
        connector.access_token = "test_token"  # Set token directly
        
        catalogs = connector.get_catalogs()
        
        assert len(catalogs) == 2
        assert catalogs[0]["name"] == "catalog1"
        assert catalogs[1]["name"] == "catalog2"
    
    @patch('connectors.polaris.connector.requests.Session')
    def test_get_namespaces(self, mock_session_class):
        """Test getting namespaces"""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "namespaces": [
                "namespace1",
                "namespace2"
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_session.request.return_value = mock_response
        
        connector = PolarisConnector(
            host="localhost",
            auth_type="api_key",
            api_key="test_key"
        )
        connector.access_token = "test_token"
        
        namespaces = connector.get_namespaces("catalog1")
        
        assert len(namespaces) == 2
        assert "namespace1" in namespaces
        assert "namespace2" in namespaces


class TestPolarisSource:
    """Test cases for PolarisSource class"""
    
    def test_data_type_mapping(self):
        """Test Iceberg to OpenMetadata data type mapping"""
        from connectors.polaris.polaris_connector import POLARIS_TO_OM_TYPE
        from metadata.generated.schema.entity.data.table import DataType
        
        # Test common mappings
        assert POLARIS_TO_OM_TYPE["string"] == DataType.STRING
        assert POLARIS_TO_OM_TYPE["int"] == DataType.INT
        assert POLARIS_TO_OM_TYPE["long"] == DataType.BIGINT
        assert POLARIS_TO_OM_TYPE["float"] == DataType.FLOAT
        assert POLARIS_TO_OM_TYPE["double"] == DataType.DOUBLE
        assert POLARIS_TO_OM_TYPE["boolean"] == DataType.BOOLEAN
        assert POLARIS_TO_OM_TYPE["timestamp"] == DataType.TIMESTAMP
    
    def test_convert_iceberg_schema_simple(self):
        """Test converting simple Iceberg schema to columns"""
        # Mock config and metadata
        mock_config = Mock()
        mock_config.serviceName = "test_service"
        mock_config.serviceConnection.root.config.connectionOptions.root = {}
        
        mock_metadata = Mock()
        
        source = PolarisSource(mock_config, mock_metadata)
        
        schema_fields = [
            {"name": "id", "type": "long", "required": True},
            {"name": "name", "type": "string", "required": True},
            {"name": "active", "type": "boolean", "required": False}
        ]
        
        columns = source._convert_iceberg_schema_to_columns(schema_fields)
        
        assert len(columns) == 3
        assert columns[0].name.root == "id"
        assert columns[1].name.root == "name"
        assert columns[2].name.root == "active"


if __name__ == "__main__":
    pytest.main([__file__])