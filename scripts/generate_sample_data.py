#!/usr/bin/env python3
"""
Polaris Sample Data Generator

This script generates realistic sample data for the Apache Polaris connector
demonstration, creating catalogs, namespaces, and tables with proper schemas.
"""

import json
import time
import requests
from typing import Dict, List, Any
from datetime import datetime


class PolarisDataGenerator:
    """Generates sample data for Polaris connector demonstration."""
    
    def __init__(self, polaris_url: str = "http://localhost:8181", 
                 openmetadata_url: str = "http://localhost:8585"):
        self.polaris_url = polaris_url
        self.openmetadata_url = openmetadata_url
        self.polaris_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer polaris-token'  # Default token
        }
        self.om_headers = None  # Will be set with JWT token
        
    def set_openmetadata_token(self, jwt_token: str):
        """Set the OpenMetadata JWT token for authentication."""
        self.om_headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
    
    def check_services(self) -> bool:
        """Check if required services are available."""
        print("🔍 Checking service availability...")
        
        # Check Polaris
        try:
            response = requests.get(f"{self.polaris_url}/management/health", timeout=5)
            if response.status_code == 200:
                print("✅ Polaris is running")
            else:
                print(f"❌ Polaris health check failed: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ Cannot connect to Polaris: {e}")
            return False
        
        # Check OpenMetadata
        try:
            response = requests.get(f"{self.openmetadata_url}/api/v1/system/version", timeout=5)
            if response.status_code == 200:
                print("✅ OpenMetadata is running")
            else:
                print(f"❌ OpenMetadata health check failed: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ Cannot connect to OpenMetadata: {e}")
            return False
        
        return True
    
    def create_catalog(self, catalog_name: str, properties: Dict[str, Any] = None) -> bool:
        """Create a catalog in Polaris."""
        print(f"📁 Creating catalog: {catalog_name}")
        
        catalog_config = {
            "type": "CATALOG",
            "name": catalog_name,
            "properties": properties or {
                "warehouse": f"s3://my-warehouse/{catalog_name}/",
                "catalog-impl": "org.apache.iceberg.rest.RESTCatalog"
            }
        }
        
        try:
            response = requests.post(
                f"{self.polaris_url}/api/catalog/v1/catalogs",
                headers=self.polaris_headers,
                json=catalog_config,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Catalog '{catalog_name}' created successfully")
                return True
            elif response.status_code == 409:
                print(f"ℹ️ Catalog '{catalog_name}' already exists")
                return True
            else:
                print(f"❌ Failed to create catalog '{catalog_name}': {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Error creating catalog '{catalog_name}': {e}")
            return False
    
    def create_namespace(self, catalog_name: str, namespace: str, properties: Dict[str, Any] = None) -> bool:
        """Create a namespace in a catalog."""
        print(f"📂 Creating namespace: {catalog_name}.{namespace}")
        
        namespace_config = {
            "namespace": [namespace],
            "properties": properties or {
                "location": f"s3://my-warehouse/{catalog_name}/{namespace}/",
                "created_by": "polaris-demo",
                "created_at": datetime.now().isoformat()
            }
        }
        
        try:
            response = requests.post(
                f"{self.polaris_url}/api/catalog/v1/{catalog_name}/namespaces",
                headers=self.polaris_headers,
                json=namespace_config,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Namespace '{catalog_name}.{namespace}' created successfully")
                return True
            elif response.status_code == 409:
                print(f"ℹ️ Namespace '{catalog_name}.{namespace}' already exists")
                return True
            else:
                print(f"❌ Failed to create namespace '{catalog_name}.{namespace}': {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Error creating namespace '{catalog_name}.{namespace}': {e}")
            return False
    
    def create_table(self, catalog_name: str, namespace: str, table_name: str, schema: Dict[str, Any]) -> bool:
        """Create a table with the given schema."""
        print(f"📊 Creating table: {catalog_name}.{namespace}.{table_name}")
        
        table_config = {
            "name": table_name,
            "schema": schema,
            "partition-spec": {
                "spec-id": 0,
                "fields": []
            },
            "sort-order": {
                "order-id": 0,
                "fields": []
            },
            "properties": {
                "created_by": "polaris-demo",
                "created_at": datetime.now().isoformat(),
                "table_type": "ICEBERG"
            }
        }
        
        try:
            response = requests.post(
                f"{self.polaris_url}/api/catalog/v1/{catalog_name}/namespaces/{namespace}/tables",
                headers=self.polaris_headers,
                json=table_config,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Table '{catalog_name}.{namespace}.{table_name}' created successfully")
                return True
            elif response.status_code == 409:
                print(f"ℹ️ Table '{catalog_name}.{namespace}.{table_name}' already exists")
                return True
            else:
                print(f"❌ Failed to create table '{catalog_name}.{namespace}.{table_name}': {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Error creating table '{catalog_name}.{namespace}.{table_name}': {e}")
            return False
    
    def get_sample_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get predefined sample table schemas."""
        return {
            "customers": {
                "type": "struct",
                "schema-id": 0,
                "fields": [
                    {"id": 1, "name": "customer_id", "required": True, "type": "long"},
                    {"id": 2, "name": "first_name", "required": True, "type": "string"},
                    {"id": 3, "name": "last_name", "required": True, "type": "string"},
                    {"id": 4, "name": "email", "required": True, "type": "string"},
                    {"id": 5, "name": "phone", "required": False, "type": "string"},
                    {"id": 6, "name": "address", "required": False, "type": "string"},
                    {"id": 7, "name": "city", "required": False, "type": "string"},
                    {"id": 8, "name": "state", "required": False, "type": "string"},
                    {"id": 9, "name": "zip_code", "required": False, "type": "string"},
                    {"id": 10, "name": "country", "required": True, "type": "string"},
                    {"id": 11, "name": "registration_date", "required": True, "type": "date"},
                    {"id": 12, "name": "last_login", "required": False, "type": "timestamp"},
                    {"id": 13, "name": "is_active", "required": True, "type": "boolean"}
                ]
            },
            "orders": {
                "type": "struct",
                "schema-id": 0,
                "fields": [
                    {"id": 1, "name": "order_id", "required": True, "type": "long"},
                    {"id": 2, "name": "customer_id", "required": True, "type": "long"},
                    {"id": 3, "name": "order_date", "required": True, "type": "date"},
                    {"id": 4, "name": "order_status", "required": True, "type": "string"},
                    {"id": 5, "name": "total_amount", "required": True, "type": "decimal(10,2)"},
                    {"id": 6, "name": "currency", "required": True, "type": "string"},
                    {"id": 7, "name": "payment_method", "required": False, "type": "string"},
                    {"id": 8, "name": "shipping_address", "required": False, "type": "string"},
                    {"id": 9, "name": "shipping_city", "required": False, "type": "string"},
                    {"id": 10, "name": "shipping_state", "required": False, "type": "string"},
                    {"id": 11, "name": "shipping_zip", "required": False, "type": "string"},
                    {"id": 12, "name": "created_at", "required": True, "type": "timestamp"},
                    {"id": 13, "name": "updated_at", "required": False, "type": "timestamp"}
                ]
            },
            "products": {
                "type": "struct",
                "schema-id": 0,
                "fields": [
                    {"id": 1, "name": "product_id", "required": True, "type": "long"},
                    {"id": 2, "name": "product_name", "required": True, "type": "string"},
                    {"id": 3, "name": "description", "required": False, "type": "string"},
                    {"id": 4, "name": "category", "required": True, "type": "string"},
                    {"id": 5, "name": "subcategory", "required": False, "type": "string"},
                    {"id": 6, "name": "brand", "required": False, "type": "string"},
                    {"id": 7, "name": "price", "required": True, "type": "decimal(10,2)"},
                    {"id": 8, "name": "cost", "required": False, "type": "decimal(10,2)"},
                    {"id": 9, "name": "weight", "required": False, "type": "decimal(8,3)"},
                    {"id": 10, "name": "dimensions", "required": False, "type": "string"},
                    {"id": 11, "name": "in_stock", "required": True, "type": "boolean"},
                    {"id": 12, "name": "stock_quantity", "required": False, "type": "long"},
                    {"id": 13, "name": "created_at", "required": True, "type": "timestamp"},
                    {"id": 14, "name": "updated_at", "required": False, "type": "timestamp"}
                ]
            },
            "sales_summary": {
                "type": "struct",
                "schema-id": 0,
                "fields": [
                    {"id": 1, "name": "report_date", "required": True, "type": "date"},
                    {"id": 2, "name": "region", "required": True, "type": "string"},
                    {"id": 3, "name": "product_category", "required": True, "type": "string"},
                    {"id": 4, "name": "total_sales", "required": True, "type": "decimal(15,2)"},
                    {"id": 5, "name": "total_orders", "required": True, "type": "long"},
                    {"id": 6, "name": "unique_customers", "required": True, "type": "long"},
                    {"id": 7, "name": "avg_order_value", "required": True, "type": "decimal(10,2)"},
                    {"id": 8, "name": "top_product", "required": False, "type": "string"},
                    {"id": 9, "name": "sales_growth", "required": False, "type": "decimal(5,2)"},
                    {"id": 10, "name": "created_at", "required": True, "type": "timestamp"}
                ]
            }
        }
    
    def generate_sample_data(self) -> bool:
        """Generate complete sample data structure."""
        print("🏗️ Generating Polaris sample data...")
        
        # Sample data structure
        catalogs = {
            "production_data": {
                "description": "Production data catalog for customer and sales data",
                "namespaces": {
                    "customers": ["customers"],
                    "sales": ["orders", "products"]
                }
            },
            "analytics_data": {
                "description": "Analytics data catalog for reporting and BI",
                "namespaces": {
                    "reports": ["sales_summary"]
                }
            }
        }
        
        schemas = self.get_sample_schemas()
        
        # Create catalogs, namespaces, and tables
        for catalog_name, catalog_info in catalogs.items():
            # Create catalog
            if not self.create_catalog(catalog_name, {"description": catalog_info["description"]}):
                return False
            
            # Create namespaces and tables
            for namespace, tables in catalog_info["namespaces"].items():
                if not self.create_namespace(catalog_name, namespace):
                    return False
                
                # Create tables in namespace
                for table_name in tables:
                    if table_name in schemas:
                        if not self.create_table(catalog_name, namespace, table_name, schemas[table_name]):
                            return False
                    else:
                        print(f"⚠️ No schema defined for table: {table_name}")
        
        return True
    
    def create_openmetadata_service(self, jwt_token: str) -> bool:
        """Create the Polaris service in OpenMetadata."""
        if not jwt_token:
            print("❌ JWT token is required for OpenMetadata operations")
            return False
        
        self.set_openmetadata_token(jwt_token)
        
        print("🔗 Creating Polaris service in OpenMetadata...")
        
        service_config = {
            "name": "polaris-iceberg-service",
            "displayName": "Polaris Iceberg Service",
            "description": "Apache Polaris Iceberg REST Catalog - Demo service with sample data",
            "serviceType": "Database",
            "connection": {
                "config": {
                    "type": "CustomDatabase",
                    "sourcePythonClass": "src.metadata.ingestion.source.database.polaris.metadata.PolarisSource",
                    "connectionOptions": {
                        "host": "localhost",
                        "port": 8181,
                        "credentials": {
                            "client_id": "polaris_client",
                            "client_secret": "polaris_secret"
                        }
                    }
                }
            },
            "tags": [
                {"tagFQN": "PII.None"},
                {"tagFQN": "Tier.Tier1"}
            ]
        }
        
        try:
            # Check if service exists
            response = requests.get(
                f"{self.openmetadata_url}/api/v1/services/databaseServices/name/polaris-iceberg-service",
                headers=self.om_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Polaris service already exists in OpenMetadata")
                return True
            
            # Create the service
            response = requests.post(
                f"{self.openmetadata_url}/api/v1/services/databaseServices",
                headers=self.om_headers,
                json=service_config,
                timeout=10
            )
            
            if response.status_code == 201:
                print("✅ Polaris service created successfully in OpenMetadata")
                return True
            else:
                print(f"❌ Failed to create service in OpenMetadata: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Error creating OpenMetadata service: {e}")
            return False
    
    def run(self, jwt_token: str = None) -> bool:
        """Run the complete sample data generation."""
        print("🚀 Polaris Sample Data Generation")
        print("=" * 40)
        
        # Check services
        if not self.check_services():
            return False
        
        # Generate Polaris data
        if not self.generate_sample_data():
            print("❌ Failed to generate Polaris sample data")
            return False
        
        # Create OpenMetadata service if token provided
        if jwt_token:
            if not self.create_openmetadata_service(jwt_token):
                print("⚠️ Failed to create OpenMetadata service (continuing anyway)")
        else:
            print("ℹ️ No JWT token provided, skipping OpenMetadata service creation")
        
        print("\n" + "=" * 40)
        print("🎉 Sample data generation completed!")
        print("\n📊 Generated Data:")
        print("📁 Catalogs: production_data, analytics_data")
        print("📂 Namespaces: customers, sales, reports")  
        print("📊 Tables: customers, orders, products, sales_summary")
        print("\n🔗 Endpoints:")
        print(f"   Polaris API: {self.polaris_url}")
        print(f"   OpenMetadata: {self.openmetadata_url}")
        
        return True


def main():
    """Main entry point."""
    import sys
    
    generator = PolarisDataGenerator()
    
    # Get JWT token from command line or use default
    jwt_token = None
    if len(sys.argv) > 1:
        jwt_token = sys.argv[1]
    else:
        # Try to read from config file
        try:
            import yaml
            from pathlib import Path
            config_path = Path("config/polaris-config.yaml")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    jwt_token = config.get('sink', {}).get('config', {}).get('securityConfig', {}).get('jwtToken')
        except Exception:
            pass
    
    success = generator.run(jwt_token)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()