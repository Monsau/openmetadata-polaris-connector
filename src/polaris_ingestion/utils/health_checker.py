"""
Health Checker

Validates connectivity and health of Polaris and OpenMetadata services.
"""

import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from ..utils.config_manager import IngestionConfig


@dataclass
class HealthStatus:
    """Service health status."""
    service_name: str
    is_healthy: bool
    status_code: Optional[int] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class HealthChecker:
    """Checks health and connectivity of services required for ingestion."""
    
    def __init__(self, config: IngestionConfig, timeout: int = 10):
        """
        Initialize HealthChecker.
        
        Args:
            config: Ingestion configuration
            timeout: Request timeout in seconds
        """
        self.config = config
        self.timeout = timeout
    
    def check_polaris_health(self) -> HealthStatus:
        """
        Check Apache Polaris health status.
        
        Returns:
            HealthStatus: Polaris health information
        """
        health_endpoint = f"http://{self.config.polaris.host}:8182/q/health"
        
        try:
            response = requests.get(health_endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                health_data = response.json()
                return HealthStatus(
                    service_name="Apache Polaris",
                    is_healthy=health_data.get('status') == 'UP',
                    status_code=response.status_code,
                    response_data=health_data
                )
            else:
                return HealthStatus(
                    service_name="Apache Polaris",
                    is_healthy=False,
                    status_code=response.status_code,
                    error_message=f"Health check failed with status {response.status_code}"
                )
                
        except requests.RequestException as e:
            return HealthStatus(
                service_name="Apache Polaris",
                is_healthy=False,
                error_message=f"Connection failed: {str(e)}"
            )
    
    def check_polaris_api(self) -> HealthStatus:
        """
        Check Polaris REST API connectivity.
        
        Returns:
            HealthStatus: Polaris API connectivity status
        """
        api_endpoint = f"{self.config.polaris.rest_endpoint}/v1/config"
        
        try:
            response = requests.get(api_endpoint, timeout=self.timeout)
            
            # 404 is expected for config endpoint, indicates API is responsive
            if response.status_code in [200, 404]:
                return HealthStatus(
                    service_name="Polaris REST API",
                    is_healthy=True,
                    status_code=response.status_code,
                    response_data={"message": "API is responsive"}
                )
            else:
                return HealthStatus(
                    service_name="Polaris REST API",
                    is_healthy=False,
                    status_code=response.status_code,
                    error_message=f"API check failed with status {response.status_code}"
                )
                
        except requests.RequestException as e:
            return HealthStatus(
                service_name="Polaris REST API",
                is_healthy=False,
                error_message=f"API connection failed: {str(e)}"
            )
    
    def check_openmetadata_health(self) -> HealthStatus:
        """
        Check OpenMetadata service health.
        
        Returns:
            HealthStatus: OpenMetadata health information
        """
        # Remove /api suffix for version endpoint
        base_url = self.config.openmetadata.host_port.replace('/api', '')
        version_endpoint = f"{base_url}/api/v1/system/version"
        
        try:
            response = requests.get(version_endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                version_data = response.json()
                return HealthStatus(
                    service_name="OpenMetadata",
                    is_healthy=True,
                    status_code=response.status_code,
                    response_data=version_data
                )
            else:
                return HealthStatus(
                    service_name="OpenMetadata",
                    is_healthy=False,
                    status_code=response.status_code,
                    error_message=f"Version check failed with status {response.status_code}"
                )
                
        except requests.RequestException as e:
            return HealthStatus(
                service_name="OpenMetadata",
                is_healthy=False,
                error_message=f"Connection failed: {str(e)}"
            )
    
    def check_openmetadata_auth(self) -> HealthStatus:
        """
        Check OpenMetadata authentication.
        
        Returns:
            HealthStatus: Authentication status
        """
        if not self.config.openmetadata.jwt_token:
            return HealthStatus(
                service_name="OpenMetadata Auth",
                is_healthy=False,
                error_message="No JWT token configured"
            )
        
        # Remove /api suffix for users endpoint
        base_url = self.config.openmetadata.host_port.replace('/api', '')
        users_endpoint = f"{base_url}/api/v1/users"
        
        headers = {
            'Authorization': f'Bearer {self.config.openmetadata.jwt_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(users_endpoint, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                return HealthStatus(
                    service_name="OpenMetadata Auth",
                    is_healthy=True,
                    status_code=response.status_code,
                    response_data={"message": "Authentication successful"}
                )
            else:
                return HealthStatus(
                    service_name="OpenMetadata Auth",
                    is_healthy=False,
                    status_code=response.status_code,
                    error_message=f"Authentication failed with status {response.status_code}"
                )
                
        except requests.RequestException as e:
            return HealthStatus(
                service_name="OpenMetadata Auth",
                is_healthy=False,
                error_message=f"Authentication check failed: {str(e)}"
            )
    
    def check_all_services(self) -> Dict[str, HealthStatus]:
        """
        Check health of all required services.
        
        Returns:
            Dict[str, HealthStatus]: Health status for all services
        """
        return {
            'polaris_health': self.check_polaris_health(),
            'polaris_api': self.check_polaris_api(),
            'openmetadata_health': self.check_openmetadata_health(),
            'openmetadata_auth': self.check_openmetadata_auth()
        }
    
    def are_all_services_healthy(self) -> bool:
        """
        Check if all services are healthy.
        
        Returns:
            bool: True if all services are healthy
        """
        health_results = self.check_all_services()
        return all(status.is_healthy for status in health_results.values())
    
    def print_health_report(self) -> None:
        """Print a formatted health report."""
        print("🏥 Service Health Check Report")
        print("=" * 50)
        
        health_results = self.check_all_services()
        
        for service_key, status in health_results.items():
            icon = "✅" if status.is_healthy else "❌"
            print(f"{icon} {status.service_name}")
            
            if status.status_code:
                print(f"   Status Code: {status.status_code}")
            
            if status.response_data:
                if 'version' in status.response_data:
                    print(f"   Version: {status.response_data['version']}")
                elif 'status' in status.response_data:
                    print(f"   Status: {status.response_data['status']}")
                elif 'message' in status.response_data:
                    print(f"   {status.response_data['message']}")
            
            if status.error_message:
                print(f"   Error: {status.error_message}")
            
            print()
        
        all_healthy = self.are_all_services_healthy()
        overall_icon = "🟢" if all_healthy else "🔴"
        overall_status = "All systems operational" if all_healthy else "Some services have issues"
        
        print(f"{overall_icon} Overall Status: {overall_status}")
        print("=" * 50)