"""
Polaris REST API client for interacting with Apache Polaris catalog
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .connection import PolarisConnection, PolarisOAuth2Config


logger = logging.getLogger(__name__)


class PolarisApiException(Exception):
    """Exception raised for Polaris API errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class PolarisClient:
    """
    Client for interacting with Apache Polaris REST API
    
    This client handles authentication, request management, and provides
    methods for discovering catalogs, namespaces, and tables.
    """
    
    def __init__(self, connection: PolarisConnection):
        """
        Initialize Polaris client
        
        Args:
            connection: Polaris connection configuration
        """
        self.connection = connection
        self.base_url = self._build_base_url()
        self.session = self._create_session()
        self.token = None
        self.token_expires_at = 0
        
        logger.info(f"Initialized Polaris client for {self.base_url}")
    
    def _build_base_url(self) -> str:
        """Build base URL from connection configuration"""
        protocol = "https" if self.connection.sslEnabled else "http"
        return f"{protocol}://{self.connection.hostPort}"
    
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
        
        # Set timeouts
        session.timeout = (self.connection.connectionTimeout, self.connection.requestTimeout)
        
        return session
    
    def _authenticate(self) -> str:
        """
        Authenticate with Polaris and return access token
        
        Returns:
            Access token string
            
        Raises:
            PolarisApiException: If authentication fails
        """
        if self.connection.authType == "oauth2":
            return self._oauth2_authenticate()
        elif self.connection.authType == "api_key":
            return self._api_key_authenticate()
        elif self.connection.authType == "basic":
            return self._basic_authenticate()
        else:
            raise PolarisApiException(f"Unsupported auth type: {self.connection.authType}")
    
    def _oauth2_authenticate(self) -> str:
        """Authenticate using OAuth2"""
        if not self.connection.oauthConfig:
            raise PolarisApiException("OAuth2 config is required for oauth2 auth type")
        
        oauth_config = PolarisOAuth2Config(**self.connection.oauthConfig)
        
        token_url = oauth_config.token_url
        if not token_url.startswith("http"):
            token_url = urljoin(self.base_url, token_url)
        
        data = {
            "grant_type": "client_credentials",
            "client_id": oauth_config.client_id,
            "client_secret": oauth_config.client_secret,
        }
        
        if oauth_config.scope:
            data["scope"] = oauth_config.scope
        
        try:
            response = self.session.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            
            if not access_token:
                raise PolarisApiException("No access token in OAuth2 response")
            
            self.token_expires_at = time.time() + expires_in - 60  # Refresh 1 minute early
            
            logger.info("Successfully authenticated with OAuth2")
            return access_token
            
        except requests.RequestException as e:
            raise PolarisApiException(f"OAuth2 authentication failed: {str(e)}")
    
    def _api_key_authenticate(self) -> str:
        """Authenticate using API key"""
        if not self.connection.apiKey:
            raise PolarisApiException("API key config is required for api_key auth type")
        
        return self.connection.apiKey.token
    
    def _basic_authenticate(self) -> str:
        """Authenticate using basic auth"""
        if not self.connection.basicAuth:
            raise PolarisApiException("Basic auth config is required for basic auth type")
        
        # For basic auth, we'll use the credentials directly in request headers
        # Return a placeholder token
        return "basic_auth_placeholder"
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests"""
        if self.connection.authType == "basic":
            if not self.connection.basicAuth:
                raise PolarisApiException("Basic auth config is required")
            
            import base64
            credentials = f"{self.connection.basicAuth.username}:{self.connection.basicAuth.password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            return {"Authorization": f"Basic {encoded_credentials}"}
        
        else:
            # For OAuth2 and API key, ensure we have a valid token
            if not self.token or time.time() >= self.token_expires_at:
                self.token = self._authenticate()
            
            return {"Authorization": f"Bearer {self.token}"}
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make authenticated request to Polaris API
        
        Args:
            method: HTTP method
            endpoint: API endpoint (relative to base URL)
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            PolarisApiException: If request fails
        """
        url = urljoin(self.base_url, endpoint)
        headers = kwargs.pop("headers", {})
        headers.update(self._get_auth_headers())
        headers["Content-Type"] = "application/json"
        
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            response_data = None
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    response_data = e.response.json()
                except ValueError:
                    response_data = {"text": e.response.text}
            
            raise PolarisApiException(f"API request failed: {str(e)}", status_code, response_data)
    
    def get_catalogs(self) -> List[Dict[str, Any]]:
        """
        Get list of catalogs from Polaris
        
        Returns:
            List of catalog dictionaries
        """
        logger.info("Fetching catalogs from Polaris")
        
        try:
            response = self._make_request("GET", "/v1/catalogs")
            catalogs = response.json().get("catalogs", [])
            
            logger.info(f"Found {len(catalogs)} catalogs")
            return catalogs
            
        except PolarisApiException:
            logger.error("Failed to fetch catalogs")
            raise
    
    def get_namespaces(self, catalog_name: str) -> List[Dict[str, Any]]:
        """
        Get list of namespaces in a catalog
        
        Args:
            catalog_name: Name of the catalog
            
        Returns:
            List of namespace dictionaries
        """
        logger.info(f"Fetching namespaces for catalog: {catalog_name}")
        
        try:
            endpoint = f"/v1/catalogs/{catalog_name}/namespaces"
            response = self._make_request("GET", endpoint)
            namespaces = response.json().get("namespaces", [])
            
            logger.info(f"Found {len(namespaces)} namespaces in catalog {catalog_name}")
            return namespaces
            
        except PolarisApiException:
            logger.error(f"Failed to fetch namespaces for catalog {catalog_name}")
            raise
    
    def get_tables(self, catalog_name: str, namespace_name: str) -> List[Dict[str, Any]]:
        """
        Get list of tables in a namespace
        
        Args:
            catalog_name: Name of the catalog
            namespace_name: Name of the namespace
            
        Returns:
            List of table dictionaries
        """
        logger.info(f"Fetching tables for catalog: {catalog_name}, namespace: {namespace_name}")
        
        try:
            endpoint = f"/v1/catalogs/{catalog_name}/namespaces/{namespace_name}/tables"
            response = self._make_request("GET", endpoint)
            tables = response.json().get("identifiers", [])
            
            logger.info(f"Found {len(tables)} tables in {catalog_name}.{namespace_name}")
            return tables
            
        except PolarisApiException:
            logger.error(f"Failed to fetch tables for {catalog_name}.{namespace_name}")
            raise
    
    def get_table_metadata(self, catalog_name: str, namespace_name: str, table_name: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific table
        
        Args:
            catalog_name: Name of the catalog
            namespace_name: Name of the namespace
            table_name: Name of the table
            
        Returns:
            Table metadata dictionary
        """
        logger.info(f"Fetching metadata for table: {catalog_name}.{namespace_name}.{table_name}")
        
        try:
            endpoint = f"/v1/catalogs/{catalog_name}/namespaces/{namespace_name}/tables/{table_name}"
            response = self._make_request("GET", endpoint)
            table_metadata = response.json()
            
            logger.info(f"Retrieved metadata for table {catalog_name}.{namespace_name}.{table_name}")
            return table_metadata
            
        except PolarisApiException:
            logger.error(f"Failed to fetch metadata for table {catalog_name}.{namespace_name}.{table_name}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test connection to Polaris
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            logger.info("Testing connection to Polaris")
            response = self._make_request("GET", "/v1/config")
            logger.info("Connection test successful")
            return True
            
        except PolarisApiException as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def close(self):
        """Close the client session"""
        if self.session:
            self.session.close()
            logger.info("Polaris client session closed")