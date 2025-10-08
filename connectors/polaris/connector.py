"""
Apache Polaris connector helper classes
"""

import json
import logging
from typing import Dict, List, Optional, Any, Iterator
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class PolarisConnector:
    """
    Helper class for connecting to Apache Polaris catalog service
    
    This class provides a simplified interface for connecting to Polaris
    and retrieving catalog metadata.
    """
    
    def __init__(
        self,
        host: str,
        port: int = 8181,
        use_ssl: bool = False,
        auth_type: str = "oauth2",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_url: Optional[str] = None,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        connection_timeout: int = 30,
        request_timeout: int = 60
    ):
        """
        Initialize Polaris connector
        
        Args:
            host: Polaris host
            port: Polaris port
            use_ssl: Whether to use SSL
            auth_type: Authentication type (oauth2, api_key, basic)
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            token_url: OAuth2 token URL
            api_key: API key for api_key auth
            username: Username for basic auth
            password: Password for basic auth
            connection_timeout: Connection timeout in seconds
            request_timeout: Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.auth_type = auth_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url or "/v1/oauth/token"
        self.api_key = api_key
        self.username = username
        self.password = password
        self.connection_timeout = connection_timeout
        self.request_timeout = request_timeout
        
        # Build base URL
        protocol = "https" if use_ssl else "http"
        self.base_url = f"{protocol}://{host}:{port}"
        
        # Create session
        self.session = self._create_session()
        self.access_token = None
        
        logger.info(f"Initialized Polaris connector for {self.base_url}")
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry configuration"""
        session = requests.Session()
        
        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def connect(self) -> bool:
        """
        Test connection and authenticate
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.auth_type == "oauth2":
                return self._oauth2_connect()
            elif self.auth_type == "api_key":
                return self._api_key_connect()
            elif self.auth_type == "basic":
                return self._basic_connect()
            else:
                logger.error(f"Unsupported auth type: {self.auth_type}")
                return False
                
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return False
    
    def _oauth2_connect(self) -> bool:
        """Connect using OAuth2"""
        if not self.client_id or not self.client_secret:
            logger.error("OAuth2 requires client_id and client_secret")
            return False
        
        token_url = urljoin(self.base_url, self.token_url)
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            response = self.session.post(
                token_url,
                data=data,
                timeout=(self.connection_timeout, self.request_timeout)
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            
            if not self.access_token:
                logger.error("No access token received")
                return False
            
            # Test the connection
            return self._test_authenticated_request()
            
        except Exception as e:
            logger.error(f"OAuth2 authentication failed: {str(e)}")
            return False
    
    def _api_key_connect(self) -> bool:
        """Connect using API key"""
        if not self.api_key:
            logger.error("API key auth requires api_key")
            return False
        
        self.access_token = self.api_key
        return self._test_authenticated_request()
    
    def _basic_connect(self) -> bool:
        """Connect using basic authentication"""
        if not self.username or not self.password:
            logger.error("Basic auth requires username and password")
            return False
        
        return self._test_authenticated_request()
    
    def _test_authenticated_request(self) -> bool:
        """Test an authenticated request"""
        try:
            headers = self._get_auth_headers()
            response = self.session.get(
                f"{self.base_url}/v1/config",
                headers=headers,
                timeout=(self.connection_timeout, self.request_timeout)
            )
            response.raise_for_status()
            logger.info("Connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        headers = {"Content-Type": "application/json"}
        
        if self.auth_type == "basic":
            import base64
            credentials = f"{self.username}:{self.password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded_credentials}"
        else:
            # OAuth2 or API key
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
        
        return headers
    
    def _make_request(self, endpoint: str, method: str = "GET", **kwargs) -> requests.Response:
        """Make authenticated request"""
        url = urljoin(self.base_url, endpoint)
        headers = kwargs.pop("headers", {})
        headers.update(self._get_auth_headers())
        
        response = self.session.request(
            method,
            url,
            headers=headers,
            timeout=(self.connection_timeout, self.request_timeout),
            **kwargs
        )
        response.raise_for_status()
        return response
    
    def get_catalogs(self) -> List[Dict[str, Any]]:
        """Get list of catalogs"""
        try:
            response = self._make_request("/v1/catalogs")
            return response.json().get("catalogs", [])
        except Exception as e:
            logger.error(f"Failed to get catalogs: {str(e)}")
            return []
    
    def get_namespaces(self, catalog_name: str) -> List[Dict[str, Any]]:
        """Get list of namespaces in a catalog"""
        try:
            endpoint = f"/v1/catalogs/{catalog_name}/namespaces"
            response = self._make_request(endpoint)
            return response.json().get("namespaces", [])
        except Exception as e:
            logger.error(f"Failed to get namespaces for {catalog_name}: {str(e)}")
            return []
    
    def get_tables(self, catalog_name: str, namespace_name: str) -> List[Dict[str, Any]]:
        """Get list of tables in a namespace"""
        try:
            endpoint = f"/v1/catalogs/{catalog_name}/namespaces/{namespace_name}/tables"
            response = self._make_request(endpoint)
            return response.json().get("identifiers", [])
        except Exception as e:
            logger.error(f"Failed to get tables for {catalog_name}.{namespace_name}: {str(e)}")
            return []
    
    def get_table_metadata(self, catalog_name: str, namespace_name: str, table_name: str) -> Optional[Dict[str, Any]]:
        """Get table metadata"""
        try:
            endpoint = f"/v1/catalogs/{catalog_name}/namespaces/{namespace_name}/tables/{table_name}"
            response = self._make_request(endpoint)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get metadata for {catalog_name}.{namespace_name}.{table_name}: {str(e)}")
            return None
    
    def close(self):
        """Close the connector session"""
        if self.session:
            self.session.close()
            logger.info("Polaris connector session closed")