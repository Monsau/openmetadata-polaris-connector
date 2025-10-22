"""
Polaris Sync Engine - Client API Polaris et moteur de découverte

Ce module contient la logique de connexion à Apache Polaris, découverte des catalogs/namespaces/tables.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import base64

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class PolarisAutoDiscovery:
    """
    Client for Apache Polaris catalog service.
    Provides connection and metadata discovery functionality.
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
        Initialize Polaris connector.
        
        Args:
            host: Polaris host
            port: Polaris port (default: 8181)
            use_ssl: Whether to use HTTPS
            auth_type: Authentication type (oauth2, api_key, basic)
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            token_url: OAuth2 token URL (default: /v1/oauth/token)
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
        
        # Create session with retry configuration
        self.session = self._create_session()
        self.access_token = None
        
        logger.info(f"Initialized Polaris connector for {self.base_url}")
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry configuration."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def authenticate(self) -> bool:
        """
        Authenticate to Polaris and test connection.
        
        Returns:
            True if authentication successful
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
            logger.error(f"Authentication failed: {str(e)}")
            return False
    
    def _oauth2_connect(self) -> bool:
        """Authenticate using OAuth2 client credentials."""
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
                logger.error("No access token received from OAuth2")
                return False
            
            logger.info("✅ OAuth2 authentication successful")
            return self._test_connection()
            
        except Exception as e:
            logger.error(f"OAuth2 authentication failed: {str(e)}")
            return False
    
    def _api_key_connect(self) -> bool:
        """Authenticate using API key."""
        if not self.api_key:
            logger.error("API key auth requires api_key")
            return False
        
        self.access_token = self.api_key
        logger.info("✅ API key configured")
        return self._test_connection()
    
    def _basic_connect(self) -> bool:
        """Authenticate using basic authentication."""
        if not self.username or not self.password:
            logger.error("Basic auth requires username and password")
            return False
        
        logger.info("✅ Basic auth configured")
        return self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test authenticated request."""
        try:
            headers = self._get_auth_headers()
            response = self.session.get(
                f"{self.base_url}/v1/config",
                headers=headers,
                timeout=(self.connection_timeout, self.request_timeout)
            )
            response.raise_for_status()
            logger.info("✅ Polaris connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ Polaris connection test failed: {str(e)}")
            return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        headers = {"Content-Type": "application/json"}
        
        if self.auth_type == "basic":
            credentials = f"{self.username}:{self.password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded_credentials}"
        else:
            # OAuth2 or API key
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
        
        return headers
    
    def _make_request(self, endpoint: str, method: str = "GET", **kwargs) -> requests.Response:
        """Make authenticated HTTP request."""
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
    
    def get_catalogs(self) -> List[str]:
        """
        Get list of catalog names.
        
        Returns:
            List of catalog names
        """
        try:
            response = self._make_request("/v1/catalogs")
            catalogs_data = response.json().get("catalogs", [])
            catalog_names = [cat.get("name") for cat in catalogs_data if cat.get("name")]
            logger.info(f"Discovered {len(catalog_names)} catalogs")
            return catalog_names
        except Exception as e:
            logger.error(f"Failed to get catalogs: {str(e)}")
            return []
    
    def get_namespaces(self, catalog_name: str) -> List[str]:
        """
        Get list of namespace names in a catalog.
        
        Args:
            catalog_name: Name of the catalog
        
        Returns:
            List of namespace names
        """
        try:
            endpoint = f"/v1/catalogs/{catalog_name}/namespaces"
            response = self._make_request(endpoint)
            namespaces_data = response.json().get("namespaces", [])
            namespace_names = [ns.get("namespace")[0] if isinstance(ns.get("namespace"), list) else ns.get("namespace") 
                             for ns in namespaces_data if ns.get("namespace")]
            logger.info(f"Discovered {len(namespace_names)} namespaces in catalog '{catalog_name}'")
            return namespace_names
        except Exception as e:
            logger.error(f"Failed to get namespaces for {catalog_name}: {str(e)}")
            return []
    
    def get_tables(self, catalog_name: str, namespace_name: str) -> List[str]:
        """
        Get list of table names in a namespace.
        
        Args:
            catalog_name: Name of the catalog
            namespace_name: Name of the namespace
        
        Returns:
            List of table names
        """
        try:
            endpoint = f"/v1/catalogs/{catalog_name}/namespaces/{namespace_name}/tables"
            response = self._make_request(endpoint)
            identifiers = response.json().get("identifiers", [])
            table_names = [ident.get("name") for ident in identifiers if ident.get("name")]
            logger.info(f"Discovered {len(table_names)} tables in {catalog_name}.{namespace_name}")
            return table_names
        except Exception as e:
            logger.error(f"Failed to get tables for {catalog_name}.{namespace_name}: {str(e)}")
            return []
    
    def get_table_metadata(self, catalog_name: str, namespace_name: str, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get table metadata including schema.
        
        Args:
            catalog_name: Name of the catalog
            namespace_name: Name of the namespace
            table_name: Name of the table
        
        Returns:
            Table metadata dictionary or None if error
        """
        try:
            endpoint = f"/v1/catalogs/{catalog_name}/namespaces/{namespace_name}/tables/{table_name}"
            response = self._make_request(endpoint)
            metadata = response.json()
            logger.debug(f"Retrieved metadata for {catalog_name}.{namespace_name}.{table_name}")
            return metadata
        except Exception as e:
            logger.error(f"Failed to get metadata for {catalog_name}.{namespace_name}.{table_name}: {str(e)}")
            return None
    
    def close(self):
        """Close HTTP session."""
        if self.session:
            self.session.close()
            logger.info("Polaris connector session closed")


class PolarisOpenMetadataSync:
    """
    High-level orchestration for Polaris to OpenMetadata synchronization.
    """
    
    def __init__(self, discovery_engine: PolarisAutoDiscovery):
        """
        Initialize sync orchestrator.
        
        Args:
            discovery_engine: Configured PolarisAutoDiscovery instance
        """
        self.discovery_engine = discovery_engine
    
    def discover_all_metadata(self, catalog_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Discover all metadata from Polaris catalogs.
        
        Args:
            catalog_filter: Optional list of catalog names to include
        
        Returns:
            Dictionary with discovery statistics
        """
        stats = {
            "catalogs": 0,
            "namespaces": 0,
            "tables": 0
        }
        
        # Get all catalogs
        all_catalogs = self.discovery_engine.get_catalogs()
        
        # Apply filter if provided
        if catalog_filter:
            catalogs = [cat for cat in all_catalogs if cat in catalog_filter]
        else:
            catalogs = all_catalogs
        
        stats["catalogs"] = len(catalogs)
        
        # Discover namespaces and tables
        for catalog in catalogs:
            namespaces = self.discovery_engine.get_namespaces(catalog)
            stats["namespaces"] += len(namespaces)
            
            for namespace in namespaces:
                tables = self.discovery_engine.get_tables(catalog, namespace)
                stats["tables"] += len(tables)
        
        logger.info(f"Discovery complete: {stats['catalogs']} catalogs, {stats['namespaces']} namespaces, {stats['tables']} tables")
        return stats


def sync_polaris_to_openmetadata(
    host: str,
    port: int,
    use_ssl: bool,
    auth_type: str,
    catalog_filter: Optional[List[str]] = None,
    **auth_credentials
) -> Dict[str, Any]:
    """
    Synchronize Polaris catalog metadata to OpenMetadata.
    
    Args:
        host: Polaris host
        port: Polaris port
        use_ssl: Whether to use HTTPS
        auth_type: Authentication type (oauth2, api_key, basic)
        catalog_filter: Optional list of catalogs to sync
        **auth_credentials: Authentication credentials (client_id, client_secret, etc.)
    
    Returns:
        Sync result dictionary with statistics
    """
    # Initialize discovery engine
    discovery = PolarisAutoDiscovery(
        host=host,
        port=port,
        use_ssl=use_ssl,
        auth_type=auth_type,
        **auth_credentials
    )
    
    # Authenticate
    if not discovery.authenticate():
        return {"success": False, "error": "Authentication failed"}
    
    # Initialize sync orchestrator
    sync = PolarisOpenMetadataSync(discovery)
    
    # Discover all metadata
    stats = sync.discover_all_metadata(catalog_filter)
    
    # Close connection
    discovery.close()
    
    return {
        "success": True,
        **stats
    }
