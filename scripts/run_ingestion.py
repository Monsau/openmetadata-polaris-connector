#!/usr/bin/env python3
"""
Polaris to OpenMetadata Ingestion Runner

This script executes the Polaris connector ingestion workflow,
connecting to Apache Polaris and ingesting metadata into OpenMetadata.
"""

import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


class IngestionRunner:
    """Manages the execution of Polaris to OpenMetadata ingestion."""
    
    def __init__(self, config_path: str = "config/polaris-config.yaml"):
        self.config_path = Path(config_path)
        self.config = None
        self.base_url = "http://localhost:8585"
        
    def load_config(self) -> bool:
        """Load the ingestion configuration."""
        if not self.config_path.exists():
            print(f"❌ Configuration file not found: {self.config_path}")
            return False
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print(f"✅ Configuration loaded from {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            return False
    
    def check_services(self) -> bool:
        """Check if required services are running."""
        print("🔍 Checking service availability...")
        
        # Check Polaris
        try:
            polaris_response = requests.get("http://localhost:8182/q/health", timeout=5)
            if polaris_response.status_code == 200:
                print("✅ Polaris is running and healthy")
            else:
                print("❌ Polaris is not healthy")
                return False
        except requests.RequestException:
            print("❌ Polaris is not accessible")
            return False
        
        # Check OpenMetadata
        try:
            om_response = requests.get(f"{self.base_url}/api/v1/system/version", timeout=5)
            if om_response.status_code == 200:
                version_info = om_response.json()
                print(f"✅ OpenMetadata is running (version: {version_info.get('version', 'unknown')})")
            else:
                print("❌ OpenMetadata is not accessible")
                return False
        except requests.RequestException:
            print("❌ OpenMetadata is not accessible")
            return False
        
        return True
    
    def validate_authentication(self) -> bool:
        """Validate OpenMetadata authentication."""
        if not self.config:
            return False
        
        # Try multiple possible locations for the JWT token
        jwt_token = None
        
        # Check sink config first
        sink_config = self.config.get('sink', {}).get('config', {})
        openmetadata_config = sink_config.get('openMetadataServerConfig', {})
        security_config = openmetadata_config.get('securityConfig', {})
        
        if 'jwtToken' in security_config:
            jwt_token = security_config['jwtToken']
        
        # Also check workflow config
        if not jwt_token:
            workflow_config = self.config.get('workflowConfig', {})
            openmetadata_config = workflow_config.get('openMetadataServerConfig', {})
            security_config = openmetadata_config.get('securityConfig', {})
            if 'jwtToken' in security_config:
                jwt_token = security_config['jwtToken']
        
        if jwt_token:
            headers = {'Authorization': f'Bearer {jwt_token}'}
            
            try:
                response = requests.get(f"{self.base_url}/api/v1/users", headers=headers, timeout=10)
                if response.status_code == 200:
                    print("✅ OpenMetadata authentication successful")
                    return True
                else:
                    print(f"❌ OpenMetadata authentication failed: {response.status_code}")
                    return False
            except requests.RequestException as e:
                print(f"❌ Authentication check failed: {e}")
                return False
        else:
            print("❌ No JWT token found in configuration")
            return False
    
    def create_database_service(self) -> bool:
        """Create the database service in OpenMetadata if it doesn't exist."""
        if not self.config:
            return False
        
        # Get JWT token from either location
        jwt_token = None
        sink_config = self.config.get('sink', {}).get('config', {})
        openmetadata_config = sink_config.get('openMetadataServerConfig', {})
        security_config = openmetadata_config.get('securityConfig', {})
        
        if 'jwtToken' in security_config:
            jwt_token = security_config['jwtToken']
        
        if not jwt_token:
            workflow_config = self.config.get('workflowConfig', {})
            openmetadata_config = workflow_config.get('openMetadataServerConfig', {})
            security_config = openmetadata_config.get('securityConfig', {})
            if 'jwtToken' in security_config:
                jwt_token = security_config['jwtToken']
        
        if not jwt_token:
            print("❌ No authentication token available")
            return False
        
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        
        # Service configuration for Apache Polaris
        service_config = {
            "name": "apache-polaris-catalog",
            "displayName": "Apache Polaris Iceberg Catalog",
            "description": "Apache Polaris - Open source catalog for Apache Iceberg tables with multi-engine support and fine-grained access control. Stores metadata for analytics_data and production_data catalogs.",
            "serviceType": "CustomDatabase",
            "connection": {
                "config": {
                    "type": "CustomDatabase",
                    "sourcePythonClass": "src.metadata.ingestion.source.database.polaris.metadata.PolarisSource",
                    "connectionOptions": {
                        "host": "localhost",
                        "port": 8181,
                        "catalog_type": "apache_polaris",
                        "rest_endpoint": "http://localhost:8181",
                        "warehouse_location": "/tmp/polaris-warehouse",
                        "credentials": {
                            "client_id": "polaris_client",
                            "client_secret": "polaris_secret",
                            "scope": "PRINCIPAL_ROLE:ALL"
                        },
                        "metadata": {
                            "source_system": "Apache Polaris",
                            "catalog_version": "1.1.0",
                            "table_format": "Apache Iceberg",
                            "storage_layer": "File System (demo mode)",
                            "governance": "Apache Polaris Access Control"
                        }
                    }
                }
            },
            "tags": [
                {
                    "tagFQN": "PolarisSource.ApachePolaris",
                    "description": "Tables sourced from Apache Polaris catalog"
                },
                {
                    "tagFQN": "DataSource.Iceberg", 
                    "description": "Apache Iceberg table format"
                }
            ]
        }
        
        try:
            # Check if apache-polaris-catalog service exists first
            response = requests.get(
                f"{self.base_url}/api/v1/services/databaseServices/name/apache-polaris-catalog",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Database service 'apache-polaris-catalog' already exists")
                return True
            
            # Check if legacy polaris-catalog exists
            response = requests.get(
                f"{self.base_url}/api/v1/services/databaseServices/name/polaris-catalog",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Database service 'polaris-catalog' already exists (legacy)")
                return True
            
            # Create the service
            response = requests.post(
                f"{self.base_url}/api/v1/services/databaseServices",
                headers=headers,
                json=service_config,
                timeout=10
            )
            
            if response.status_code == 201:
                print("✅ Database service created successfully")
                return True
            else:
                print(f"❌ Failed to create database service: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Service creation failed: {e}")
            return False
    
    def run_metadata_ingestion(self) -> bool:
        """Execute the metadata ingestion workflow."""
        print("🚀 Starting metadata ingestion...")
        
        try:
            # Use the OpenMetadata CLI to run ingestion
            cmd = [
                "metadata", "ingest",
                "-c", str(self.config_path)
            ]
            
            print(f"Running command: {' '.join(cmd)}")
            
            # Run the ingestion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print("✅ Metadata ingestion completed successfully")
                print("📊 Ingestion output:")
                print(result.stdout)
                return True
            else:
                print("❌ Metadata ingestion failed")
                print("Error output:")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Ingestion timed out after 5 minutes")
            return False
        except subprocess.CalledProcessError as e:
            print(f"❌ Ingestion failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during ingestion: {e}")
            return False
    
    def verify_ingestion_results(self) -> bool:
        """Verify that metadata was successfully ingested."""
        if not self.config:
            return False
        
        # Get JWT token from either location
        jwt_token = None
        sink_config = self.config.get('sink', {}).get('config', {})
        openmetadata_config = sink_config.get('openMetadataServerConfig', {})
        security_config = openmetadata_config.get('securityConfig', {})
        
        if 'jwtToken' in security_config:
            jwt_token = security_config['jwtToken']
        
        if not jwt_token:
            workflow_config = self.config.get('workflowConfig', {})
            openmetadata_config = workflow_config.get('openMetadataServerConfig', {})
            security_config = openmetadata_config.get('securityConfig', {})
            if 'jwtToken' in security_config:
                jwt_token = security_config['jwtToken']
        
        if not jwt_token:
            return False
        
        headers = {'Authorization': f'Bearer {jwt_token}'}
        
        try:
            # Check for databases
            response = requests.get(
                f"{self.base_url}/api/v1/databases",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                databases = response.json().get('data', [])
                polaris_dbs = [db for db in databases if 'polaris' in db.get('name', '').lower()]
                
                if polaris_dbs:
                    print(f"✅ Found {len(polaris_dbs)} Polaris database(s) in OpenMetadata")
                    for db in polaris_dbs:
                        print(f"   📊 {db.get('name')} - {db.get('description', 'No description')}")
                    return True
                else:
                    print("⚠️ No Polaris databases found in OpenMetadata")
                    return False
            else:
                print(f"❌ Failed to retrieve databases: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def run(self) -> bool:
        """Execute the complete ingestion workflow."""
        print("🚀 Apache Polaris to OpenMetadata Ingestion")
        print("=" * 50)
        
        # Load configuration
        if not self.load_config():
            return False
        
        # Check services
        if not self.check_services():
            print("❌ Required services are not available")
            return False
        
        # Validate authentication
        if not self.validate_authentication():
            print("❌ Authentication validation failed")
            return False
        
        # Create database service
        if not self.create_database_service():
            print("❌ Failed to create database service")
            return False
        
        # Wait a moment for service to be ready
        print("⏳ Waiting for service to be ready...")
        time.sleep(3)
        
        # Run ingestion
        if not self.run_metadata_ingestion():
            print("❌ Metadata ingestion failed")
            return False
        
        # Verify results
        print("🔍 Verifying ingestion results...")
        time.sleep(5)  # Wait for indexing
        
        if not self.verify_ingestion_results():
            print("⚠️ Ingestion verification incomplete")
        
        print("\n" + "=" * 50)
        print("🎉 Ingestion workflow completed!")
        print("\n📋 Next steps:")
        print("1. Visit OpenMetadata UI: http://localhost:8585")
        print("2. Navigate to Databases to see Polaris catalogs")
        print("3. Explore the ingested tables and schemas")
        
        return True


def main():
    """Main entry point."""
    runner = IngestionRunner()
    
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        runner = IngestionRunner(config_path)
    
    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()