"""
Script to populate Apache Polaris with sample data for demonstration
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PolarisSetup:
    """Setup class for populating Polaris with sample data"""
    
    def __init__(self, base_url: str = "http://localhost:8181"):
        """
        Initialize Polaris setup
        
        Args:
            base_url: Polaris base URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def wait_for_polaris(self, max_retries: int = 30) -> bool:
        """
        Wait for Polaris to be ready
        
        Args:
            max_retries: Maximum number of connection attempts
            
        Returns:
            True if Polaris is ready, False otherwise
        """
        logger.info(f"Waiting for Polaris at {self.base_url} to be ready...")
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(f"{self.base_url}/v1/config", timeout=5)
                if response.status_code == 200:
                    logger.info("Polaris is ready!")
                    return True
            except requests.RequestException:
                pass
            
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Polaris not ready, waiting...")
            time.sleep(2)
        
        logger.error("Polaris did not become ready within the timeout period")
        return False
    
    def create_catalog(self, catalog_name: str, properties: Dict = None) -> bool:
        """
        Create a catalog in Polaris
        
        Args:
            catalog_name: Name of the catalog
            properties: Optional catalog properties
            
        Returns:
            True if successful, False otherwise
        """
        if properties is None:
            properties = {}
        
        catalog_data = {
            "catalog": {
                "type": "iceberg",
                "properties": {
                    "warehouse": f"s3://demo-warehouse/{catalog_name}",
                    "catalog-impl": "org.apache.iceberg.rest.RESTCatalog",
                    **properties
                }
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/catalogs/{catalog_name}",
                json=catalog_data
            )
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Created catalog: {catalog_name}")
                return True
            else:
                logger.error(f"Failed to create catalog {catalog_name}: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error creating catalog {catalog_name}: {str(e)}")
            return False
    
    def create_namespace(self, catalog_name: str, namespace_name: str, properties: Dict = None) -> bool:
        """
        Create a namespace in a catalog
        
        Args:
            catalog_name: Name of the catalog
            namespace_name: Name of the namespace
            properties: Optional namespace properties
            
        Returns:
            True if successful, False otherwise
        """
        if properties is None:
            properties = {}
        
        namespace_data = {
            "namespace": [namespace_name],
            "properties": {
                "owner": "demo-team",
                "created_at": datetime.now().isoformat(),
                **properties
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/catalogs/{catalog_name}/namespaces",
                json=namespace_data
            )
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Created namespace: {catalog_name}.{namespace_name}")
                return True
            else:
                logger.error(f"Failed to create namespace {catalog_name}.{namespace_name}: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error creating namespace {catalog_name}.{namespace_name}: {str(e)}")
            return False
    
    def create_table(self, catalog_name: str, namespace_name: str, table_name: str, schema: Dict) -> bool:
        """
        Create a table in a namespace
        
        Args:
            catalog_name: Name of the catalog
            namespace_name: Name of the namespace
            table_name: Name of the table
            schema: Table schema definition
            
        Returns:
            True if successful, False otherwise
        """
        table_data = {
            "name": table_name,
            "schema": schema,
            "partition-spec": {
                "spec-id": 0,
                "fields": []
            },
            "write-order": {
                "order-id": 1,
                "fields": []
            },
            "stage-create": True,
            "properties": {
                "owner": "demo-team",
                "created_at": datetime.now().isoformat(),
                "format-version": "2"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/catalogs/{catalog_name}/namespaces/{namespace_name}/tables",
                json=table_data
            )
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Created table: {catalog_name}.{namespace_name}.{table_name}")
                return True
            else:
                logger.error(f"Failed to create table {catalog_name}.{namespace_name}.{table_name}: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error creating table {catalog_name}.{namespace_name}.{table_name}: {str(e)}")
            return False
    
    def setup_sample_data(self) -> bool:
        """
        Set up complete sample data structure
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting sample data setup...")
        
        # Define sample data structure
        sample_data = {
            "main": {
                "properties": {
                    "description": "Main production catalog",
                    "environment": "production"
                },
                "namespaces": {
                    "sales": {
                        "properties": {
                            "description": "Sales department data",
                            "team": "sales"
                        },
                        "tables": {
                            "customers": self._get_customers_schema(),
                            "orders": self._get_orders_schema(),
                            "products": self._get_products_schema()
                        }
                    },
                    "marketing": {
                        "properties": {
                            "description": "Marketing department data",
                            "team": "marketing"
                        },
                        "tables": {
                            "campaigns": self._get_campaigns_schema(),
                            "leads": self._get_leads_schema()
                        }
                    }
                }
            },
            "analytics": {
                "properties": {
                    "description": "Analytics and reporting catalog",
                    "environment": "analytics"
                },
                "namespaces": {
                    "reporting": {
                        "properties": {
                            "description": "Business intelligence reports",
                            "team": "data-analytics"
                        },
                        "tables": {
                            "sales_summary": self._get_sales_summary_schema(),
                            "customer_metrics": self._get_customer_metrics_schema()
                        }
                    }
                }
            },
            "staging": {
                "properties": {
                    "description": "Staging environment for development",
                    "environment": "staging"
                },
                "namespaces": {
                    "raw_data": {
                        "properties": {
                            "description": "Raw ingested data",
                            "team": "data-engineering"
                        },
                        "tables": {
                            "events": self._get_events_schema(),
                            "logs": self._get_logs_schema()
                        }
                    }
                }
            }
        }
        
        success = True
        
        # Create catalogs, namespaces, and tables
        for catalog_name, catalog_config in sample_data.items():
            # Create catalog
            if not self.create_catalog(catalog_name, catalog_config["properties"]):
                success = False
                continue
            
            # Create namespaces and tables
            for namespace_name, namespace_config in catalog_config["namespaces"].items():
                if not self.create_namespace(catalog_name, namespace_name, namespace_config["properties"]):
                    success = False
                    continue
                
                for table_name, table_schema in namespace_config["tables"].items():
                    if not self.create_table(catalog_name, namespace_name, table_name, table_schema):
                        success = False
        
        if success:
            logger.info("Sample data setup completed successfully!")
        else:
            logger.warning("Sample data setup completed with some errors")
        
        return success
    
    def _get_customers_schema(self) -> Dict:
        """Get schema for customers table"""
        return {
            "type": "struct",
            "schema-id": 1,
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
                {"id": 10, "name": "created_at", "required": True, "type": "timestamp"},
                {"id": 11, "name": "updated_at", "required": True, "type": "timestamp"}
            ]
        }
    
    def _get_orders_schema(self) -> Dict:
        """Get schema for orders table"""
        return {
            "type": "struct",
            "schema-id": 1,
            "fields": [
                {"id": 1, "name": "order_id", "required": True, "type": "long"},
                {"id": 2, "name": "customer_id", "required": True, "type": "long"},
                {"id": 3, "name": "order_date", "required": True, "type": "date"},
                {"id": 4, "name": "total_amount", "required": True, "type": "decimal(10,2)"},
                {"id": 5, "name": "status", "required": True, "type": "string"},
                {"id": 6, "name": "shipping_address", "required": False, "type": "string"},
                {"id": 7, "name": "created_at", "required": True, "type": "timestamp"},
                {"id": 8, "name": "updated_at", "required": True, "type": "timestamp"}
            ]
        }
    
    def _get_products_schema(self) -> Dict:
        """Get schema for products table"""
        return {
            "type": "struct",
            "schema-id": 1,
            "fields": [
                {"id": 1, "name": "product_id", "required": True, "type": "long"},
                {"id": 2, "name": "name", "required": True, "type": "string"},
                {"id": 3, "name": "description", "required": False, "type": "string"},
                {"id": 4, "name": "price", "required": True, "type": "decimal(10,2)"},
                {"id": 5, "name": "category", "required": True, "type": "string"},
                {"id": 6, "name": "sku", "required": True, "type": "string"},
                {"id": 7, "name": "in_stock", "required": True, "type": "boolean"},
                {"id": 8, "name": "created_at", "required": True, "type": "timestamp"},
                {"id": 9, "name": "updated_at", "required": True, "type": "timestamp"}
            ]
        }
    
    def _get_campaigns_schema(self) -> Dict:
        """Get schema for campaigns table"""
        return {
            "type": "struct",
            "schema-id": 1,
            "fields": [
                {"id": 1, "name": "campaign_id", "required": True, "type": "long"},
                {"id": 2, "name": "name", "required": True, "type": "string"},
                {"id": 3, "name": "description", "required": False, "type": "string"},
                {"id": 4, "name": "start_date", "required": True, "type": "date"},
                {"id": 5, "name": "end_date", "required": False, "type": "date"},
                {"id": 6, "name": "budget", "required": True, "type": "decimal(12,2)"},
                {"id": 7, "name": "channel", "required": True, "type": "string"},
                {"id": 8, "name": "created_at", "required": True, "type": "timestamp"}
            ]
        }
    
    def _get_leads_schema(self) -> Dict:
        """Get schema for leads table"""
        return {
            "type": "struct",
            "schema-id": 1,
            "fields": [
                {"id": 1, "name": "lead_id", "required": True, "type": "long"},
                {"id": 2, "name": "email", "required": True, "type": "string"},
                {"id": 3, "name": "first_name", "required": False, "type": "string"},
                {"id": 4, "name": "last_name", "required": False, "type": "string"},
                {"id": 5, "name": "source", "required": True, "type": "string"},
                {"id": 6, "name": "campaign_id", "required": False, "type": "long"},
                {"id": 7, "name": "score", "required": False, "type": "integer"},
                {"id": 8, "name": "status", "required": True, "type": "string"},
                {"id": 9, "name": "created_at", "required": True, "type": "timestamp"}
            ]
        }
    
    def _get_sales_summary_schema(self) -> Dict:
        """Get schema for sales_summary table"""
        return {
            "type": "struct",
            "schema-id": 1,
            "fields": [
                {"id": 1, "name": "date", "required": True, "type": "date"},
                {"id": 2, "name": "total_orders", "required": True, "type": "long"},
                {"id": 3, "name": "total_revenue", "required": True, "type": "decimal(15,2)"},
                {"id": 4, "name": "avg_order_value", "required": True, "type": "decimal(10,2)"},
                {"id": 5, "name": "new_customers", "required": True, "type": "long"},
                {"id": 6, "name": "created_at", "required": True, "type": "timestamp"}
            ]
        }
    
    def _get_customer_metrics_schema(self) -> Dict:
        """Get schema for customer_metrics table"""
        return {
            "type": "struct",
            "schema-id": 1,
            "fields": [
                {"id": 1, "name": "customer_id", "required": True, "type": "long"},
                {"id": 2, "name": "total_orders", "required": True, "type": "long"},
                {"id": 3, "name": "total_spent", "required": True, "type": "decimal(15,2)"},
                {"id": 4, "name": "avg_order_value", "required": True, "type": "decimal(10,2)"},
                {"id": 5, "name": "first_order_date", "required": True, "type": "date"},
                {"id": 6, "name": "last_order_date", "required": True, "type": "date"},
                {"id": 7, "name": "customer_lifetime_value", "required": False, "type": "decimal(15,2)"},
                {"id": 8, "name": "updated_at", "required": True, "type": "timestamp"}
            ]
        }
    
    def _get_events_schema(self) -> Dict:
        """Get schema for events table"""
        return {
            "type": "struct",
            "schema-id": 1,
            "fields": [
                {"id": 1, "name": "event_id", "required": True, "type": "string"},
                {"id": 2, "name": "user_id", "required": False, "type": "string"},
                {"id": 3, "name": "session_id", "required": False, "type": "string"},
                {"id": 4, "name": "event_type", "required": True, "type": "string"},
                {"id": 5, "name": "event_properties", "required": False, "type": "string"},  # JSON as string
                {"id": 6, "name": "timestamp", "required": True, "type": "timestamp"},
                {"id": 7, "name": "ip_address", "required": False, "type": "string"},
                {"id": 8, "name": "user_agent", "required": False, "type": "string"}
            ]
        }
    
    def _get_logs_schema(self) -> Dict:
        """Get schema for logs table"""
        return {
            "type": "struct",
            "schema-id": 1,
            "fields": [
                {"id": 1, "name": "log_id", "required": True, "type": "string"},
                {"id": 2, "name": "timestamp", "required": True, "type": "timestamp"},
                {"id": 3, "name": "level", "required": True, "type": "string"},
                {"id": 4, "name": "service", "required": True, "type": "string"},
                {"id": 5, "name": "message", "required": True, "type": "string"},
                {"id": 6, "name": "exception", "required": False, "type": "string"},
                {"id": 7, "name": "request_id", "required": False, "type": "string"},
                {"id": 8, "name": "user_id", "required": False, "type": "string"}
            ]
        }


def main():
    """Main function to run the setup"""
    setup = PolarisSetup()
    
    # Wait for Polaris to be ready
    if not setup.wait_for_polaris():
        logger.error("Polaris is not available. Please ensure it's running.")
        return
    
    # Setup sample data
    setup.setup_sample_data()
    
    logger.info("Sample data setup completed!")
    logger.info("You can now test the Polaris connector with OpenMetadata.")


if __name__ == "__main__":
    main()