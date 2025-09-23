"""
Polaris Table Creator

Utility for creating demo tables in Apache Polaris catalogs with proper schema structure.
"""

import requests
import json
from typing import Dict, Any, List
from ..utils.config_manager import IngestionConfig


class PolarisTableCreator:
    """
    Creates and manages demo tables in Apache Polaris catalogs.
    
    This class handles:
    - Catalog and namespace creation
    - Table schema definition and creation
    - Proper metadata attribution for OpenMetadata ingestion
    """
    
    def __init__(self, config: IngestionConfig):
        """
        Initialize the table creator.
        
        Args:
            config: Complete ingestion configuration
        """
        self.config = config
        self.polaris_url = config.polaris.rest_endpoint.rstrip('/')
        self.session = requests.Session()
        
        # Set up authentication if configured
        if hasattr(config.polaris, 'token') and config.polaris.token:
            self.session.headers.update({
                'Authorization': f'Bearer {config.polaris.token}'
            })
    
    def create_catalog(self, catalog_name: str, description: str) -> bool:
        """
        Create a catalog in Apache Polaris.
        
        Args:
            catalog_name: Name of the catalog to create
            description: Description of the catalog
            
        Returns:
            bool: True if creation succeeded
        """
        try:
            catalog_config = {
                "type": "CATALOG",
                "name": catalog_name,
                "properties": {
                    "warehouse": f"s3://demo-warehouse/{catalog_name}/",
                    "catalog-impl": "org.apache.iceberg.rest.RESTCatalog",
                    "description": description
                }
            }
            
            response = self.session.post(
                f"{self.polaris_url}/api/catalog/v1/catalogs",
                json=catalog_config,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Created catalog: {catalog_name}")
                return True
            elif response.status_code == 409:
                print(f"ℹ️ Catalog already exists: {catalog_name}")
                return True
            else:
                print(f"❌ Failed to create catalog {catalog_name}: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating catalog {catalog_name}: {e}")
            return False
    
    def create_namespace(self, catalog_name: str, namespace: str, description: str) -> bool:
        """
        Create a namespace (schema) in a Polaris catalog.
        
        Args:
            catalog_name: Name of the parent catalog
            namespace: Name of the namespace to create
            description: Description of the namespace
            
        Returns:
            bool: True if creation succeeded
        """
        try:
            namespace_config = {
                "namespace": [namespace],
                "properties": {
                    "description": description
                }
            }
            
            response = self.session.post(
                f"{self.polaris_url}/api/catalog/v1/catalogs/{catalog_name}/namespaces",
                json=namespace_config,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Created namespace: {catalog_name}.{namespace}")
                return True
            elif response.status_code == 409:
                print(f"ℹ️ Namespace already exists: {catalog_name}.{namespace}")
                return True
            else:
                print(f"❌ Failed to create namespace {catalog_name}.{namespace}: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating namespace {catalog_name}.{namespace}: {e}")
            return False
    
    def create_table(self, catalog_name: str, namespace: str, table_name: str, 
                    schema: List[Dict[str, Any]], description: str) -> bool:
        """
        Create a table in a Polaris catalog.
        
        Args:
            catalog_name: Name of the parent catalog
            namespace: Name of the parent namespace
            table_name: Name of the table to create
            schema: Table schema definition
            description: Table description
            
        Returns:
            bool: True if creation succeeded
        """
        try:
            table_config = {
                "name": table_name,
                "schema": {
                    "type": "struct",
                    "fields": schema
                },
                "properties": {
                    "description": description
                }
            }
            
            response = self.session.post(
                f"{self.polaris_url}/api/catalog/v1/catalogs/{catalog_name}/namespaces/{namespace}/tables",
                json=table_config,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Created table: {catalog_name}.{namespace}.{table_name}")
                return True
            elif response.status_code == 409:
                print(f"ℹ️ Table already exists: {catalog_name}.{namespace}.{table_name}")
                return True
            else:
                print(f"❌ Failed to create table {catalog_name}.{namespace}.{table_name}: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating table {catalog_name}.{namespace}.{table_name}: {e}")
            return False
    
    def create_demo_structure(self) -> bool:
        """
        Create the complete demo table structure in Polaris.
        
        Returns:
            bool: True if all structures were created successfully
        """
        print("🏗️ Creating Demo Table Structure in Apache Polaris...")
        print("-" * 50)
        
        # Define the demo structure
        catalogs = [
            {
                "name": "analytics_data",
                "description": "Analytics data warehouse containing reporting and business intelligence tables",
                "namespaces": [
                    {
                        "name": "reporting", 
                        "description": "Reporting and analytics namespace",
                        "tables": [
                            {
                                "name": "monthly_sales",
                                "description": "Monthly aggregated sales data for reporting and analytics",
                                "schema": [
                                    {"id": 1, "name": "month", "type": "date", "required": True},
                                    {"id": 2, "name": "region", "type": "string", "required": True},
                                    {"id": 3, "name": "total_sales", "type": "double", "required": True},
                                    {"id": 4, "name": "total_orders", "type": "int", "required": True},
                                    {"id": 5, "name": "created_at", "type": "timestamp", "required": True}
                                ]
                            },
                            {
                                "name": "customer_segmentation",
                                "description": "Customer segmentation analysis for marketing campaigns",
                                "schema": [
                                    {"id": 1, "name": "customer_id", "type": "int", "required": True},
                                    {"id": 2, "name": "segment", "type": "string", "required": True},
                                    {"id": 3, "name": "ltv", "type": "double", "required": True},
                                    {"id": 4, "name": "segment_score", "type": "double", "required": True},
                                    {"id": 5, "name": "last_updated", "type": "timestamp", "required": True}
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "name": "production_data",
                "description": "Production operational data containing sales and customer information",
                "namespaces": [
                    {
                        "name": "sales",
                        "description": "Sales operational data namespace", 
                        "tables": [
                            {
                                "name": "orders",
                                "description": "Customer orders from e-commerce platform and point-of-sale systems",
                                "schema": [
                                    {"id": 1, "name": "order_id", "type": "int", "required": True},
                                    {"id": 2, "name": "customer_id", "type": "int", "required": True},
                                    {"id": 3, "name": "order_date", "type": "date", "required": True},
                                    {"id": 4, "name": "total_amount", "type": "double", "required": True},
                                    {"id": 5, "name": "status", "type": "string", "required": True}
                                ]
                            },
                            {
                                "name": "customers",
                                "description": "Customer information and profiles from CRM systems",
                                "schema": [
                                    {"id": 1, "name": "customer_id", "type": "int", "required": True},
                                    {"id": 2, "name": "first_name", "type": "string", "required": True},
                                    {"id": 3, "name": "last_name", "type": "string", "required": True},
                                    {"id": 4, "name": "email", "type": "string", "required": True},
                                    {"id": 5, "name": "registration_date", "type": "date", "required": True}
                                ]
                            },
                            {
                                "name": "products",
                                "description": "Product catalog and inventory information",
                                "schema": [
                                    {"id": 1, "name": "product_id", "type": "int", "required": True},
                                    {"id": 2, "name": "name", "type": "string", "required": True},
                                    {"id": 3, "name": "category", "type": "string", "required": True},
                                    {"id": 4, "name": "price", "type": "double", "required": True},
                                    {"id": 5, "name": "stock_quantity", "type": "int", "required": True}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        
        # Create the structure
        success = True
        total_catalogs = 0
        total_namespaces = 0 
        total_tables = 0
        
        for catalog in catalogs:
            # Create catalog
            if not self.create_catalog(catalog["name"], catalog["description"]):
                success = False
                continue
            total_catalogs += 1
            
            # Create namespaces and tables
            for namespace in catalog["namespaces"]:
                if not self.create_namespace(catalog["name"], namespace["name"], namespace["description"]):
                    success = False
                    continue
                total_namespaces += 1
                
                # Create tables
                for table in namespace["tables"]:
                    if not self.create_table(
                        catalog["name"], 
                        namespace["name"], 
                        table["name"],
                        table["schema"],
                        table["description"]
                    ):
                        success = False
                        continue
                    total_tables += 1
        
        # Print summary
        print(f"\n📊 Demo Structure Creation Summary:")
        print(f"   • Catalogs: {total_catalogs}")
        print(f"   • Namespaces: {total_namespaces}")
        print(f"   • Tables: {total_tables}")
        
        if success:
            print(f"✅ Demo structure created successfully!")
        else:
            print(f"⚠️ Some components failed to create. Check logs above.")
        
        return success
    
    def list_catalogs(self) -> List[Dict[str, Any]]:
        """
        List all catalogs in Polaris.
        
        Returns:
            List of catalog information
        """
        try:
            response = self.session.get(f"{self.polaris_url}/api/catalog/v1/catalogs")
            if response.status_code == 200:
                data = response.json()
                return data.get('catalogs', [])
            else:
                print(f"❌ Failed to list catalogs: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error listing catalogs: {e}")
            return []
    
    def list_tables(self, catalog_name: str, namespace: str) -> List[Dict[str, Any]]:
        """
        List all tables in a specific namespace.
        
        Args:
            catalog_name: Name of the catalog
            namespace: Name of the namespace
            
        Returns:
            List of table information
        """
        try:
            response = self.session.get(
                f"{self.polaris_url}/api/catalog/v1/catalogs/{catalog_name}/namespaces/{namespace}/tables"
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('identifiers', [])
            else:
                print(f"❌ Failed to list tables in {catalog_name}.{namespace}: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error listing tables in {catalog_name}.{namespace}: {e}")
            return []