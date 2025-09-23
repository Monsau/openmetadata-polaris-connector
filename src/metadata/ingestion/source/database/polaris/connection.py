"""
Polaris connection configuration and models
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class BasicAuth(BaseModel):
    """Basic authentication configuration"""
    username: str
    password: str


class ApiAccessTokenAuth(BaseModel):
    """API access token authentication"""
    token: str


class DatabaseConnection(BaseModel):
    """Base database connection class"""
    pass


class PolarisConnection(DatabaseConnection):
    """
    Polaris connection configuration
    
    This class defines the connection parameters needed to connect to Apache Polaris catalog.
    """
    
    type: str = Field(default="Polaris", const=True)
    
    # Connection parameters
    hostPort: str = Field(
        ...,
        description="Polaris service host and port (e.g., localhost:8181)"
    )
    
    # Authentication
    authType: str = Field(
        default="oauth2",
        description="Authentication type (oauth2, api_key, basic)"
    )
    
    # OAuth2 configuration
    oauthConfig: Optional[dict] = Field(
        default=None,
        description="OAuth2 configuration including client_id, client_secret, token_url"
    )
    
    # API Key authentication
    apiKey: Optional[ApiAccessTokenAuth] = Field(
        default=None,
        description="API key authentication configuration"
    )
    
    # Basic authentication
    basicAuth: Optional[BasicAuth] = Field(
        default=None,
        description="Basic authentication configuration"
    )
    
    # SSL/TLS configuration
    sslEnabled: bool = Field(
        default=False,
        description="Enable SSL/TLS for connections"
    )
    
    sslCertificate: Optional[str] = Field(
        default=None,
        description="Path to SSL certificate file"
    )
    
    # Connection options
    connectionTimeout: int = Field(
        default=30,
        description="Connection timeout in seconds",
        ge=1,
        le=300
    )
    
    requestTimeout: int = Field(
        default=60,
        description="Request timeout in seconds",
        ge=1,
        le=600
    )
    
    # Catalog configuration
    catalogFilter: Optional[str] = Field(
        default=None,
        description="Regex pattern to filter catalogs (optional)"
    )
    
    namespaceFilter: Optional[str] = Field(
        default=None,
        description="Regex pattern to filter namespaces (optional)"
    )
    
    tableFilter: Optional[str] = Field(
        default=None,
        description="Regex pattern to filter tables (optional)"
    )
    
    @validator("hostPort")
    def validate_host_port(cls, v):
        """Validate host:port format"""
        if ":" not in v:
            raise ValueError("hostPort must be in format 'host:port'")
        
        host, port = v.split(":", 1)
        if not host.strip():
            raise ValueError("Host cannot be empty")
        
        try:
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                raise ValueError("Port must be between 1 and 65535")
        except ValueError:
            raise ValueError("Port must be a valid integer")
        
        return v
    
    @validator("authType")
    def validate_auth_type(cls, v):
        """Validate authentication type"""
        valid_types = {"oauth2", "api_key", "basic"}
        if v not in valid_types:
            raise ValueError(f"authType must be one of: {valid_types}")
        return v
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "type": "Polaris",
                "hostPort": "localhost:8181",
                "authType": "oauth2",
                "oauthConfig": {
                    "client_id": "polaris-client",
                    "client_secret": "secret",
                    "token_url": "http://localhost:8181/oauth2/token"
                },
                "sslEnabled": False,
                "connectionTimeout": 30,
                "requestTimeout": 60
            }
        }


class PolarisOAuth2Config(BaseModel):
    """OAuth2 configuration for Polaris"""
    
    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: str = Field(..., description="OAuth2 client secret")
    token_url: str = Field(..., description="OAuth2 token endpoint URL")
    scope: Optional[str] = Field(default=None, description="OAuth2 scope")
    
    class Config:
        schema_extra = {
            "example": {
                "client_id": "polaris-client",
                "client_secret": "your-secret",
                "token_url": "http://localhost:8181/oauth2/token",
                "scope": "catalog:read"
            }
        }