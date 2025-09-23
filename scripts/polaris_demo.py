#!/usr/bin/env python3
"""
Complete Polaris to OpenMetadata Integration Demonstration

This script provides a comprehensive demonstration of the Apache Polaris 
to OpenMetadata connector, showcasing the complete data pipeline from 
Polaris catalog setup to OpenMetadata visualization.
"""

import sys
import json
import time
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PolarisOpenMetadataDemo:
    """Complete demonstration of Polaris to OpenMetadata integration."""
    
    def __init__(self, 
                 polaris_url: str = "http://localhost:8181",
                 openmetadata_url: str = "http://localhost:8585",
                 config_file: str = "config/polaris-config.yaml"):
        self.polaris_url = polaris_url
        self.openmetadata_url = openmetadata_url
        self.config_file = config_file
        self.jwt_token = None
        
        # Session for API calls
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Demo data tracking
        self.demo_catalogs = []
        self.demo_namespaces = []
        self.demo_tables = []
        
    def load_jwt_token(self) -> bool:
        """Load JWT token from configuration file."""
        try:
            import yaml
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    self.jwt_token = config.get('sink', {}).get('config', {}).get('securityConfig', {}).get('jwtToken')
                    if self.jwt_token:
                        logger.info("✅ JWT token loaded from configuration")
                        return True
            logger.warning("⚠️ No JWT token found in configuration")
            return False
        except Exception as e:
            logger.error(f"❌ Error loading JWT token: {e}")
            return False
    
    def check_services(self) -> Dict[str, bool]:
        """Check if all required services are running."""
        logger.info("🔍 Checking service availability...")
        
        services = {
            'polaris': False,
            'openmetadata': False
        }
        
        # Check Polaris
        try:
            response = requests.get(f"{self.polaris_url}/management/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Polaris is running and healthy")
                services['polaris'] = True
            else:
                logger.error(f"❌ Polaris health check failed: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"❌ Cannot connect to Polaris: {e}")
        
        # Check OpenMetadata
        try:
            response = requests.get(f"{self.openmetadata_url}/api/v1/system/version", timeout=10)
            if response.status_code == 200:
                version_info = response.json()
                logger.info(f"✅ OpenMetadata is running (version: {version_info.get('version', 'unknown')})")
                services['openmetadata'] = True
            else:
                logger.error(f"❌ OpenMetadata health check failed: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"❌ Cannot connect to OpenMetadata: {e}")
        
        return services
    
    def setup_polaris_sample_data(self) -> bool:
        """Set up rich sample data in Polaris based on existing structure."""
        logger.info("🏗️ Setting up Polaris sample data...")
        
        # Sample data structure based on what's shown in OpenMetadata
        sample_structure = {
            "production_data": {
                "description": "Production Polaris catalog with customer and sales data",
                "namespaces": {
                    "customers": {
                        "description": "Customer information schema",
                        "tables": {
                            "customer_profiles": self._get_customer_profiles_schema(),
                        }
                    },
                    "sales": {
                        "description": "Sales transaction schema", 
                        "tables": {
                            "order_history": self._get_order_history_schema(),
                        }
                    }
                }
            },
            "analytics_data": {
                "description": "Analytics Polaris catalog for reporting",
                "namespaces": {
                    "reports": {
                        "description": "Business analytics schema",
                        "tables": {
                            "daily_metrics": self._get_daily_metrics_schema(),
                        }
                    }
                }
            }
        }
        
        success = True
        
        for catalog_name, catalog_config in sample_structure.items():
            # Create catalog
            if self._create_polaris_catalog(catalog_name, catalog_config["description"]):
                self.demo_catalogs.append(catalog_name)
                
                # Create namespaces and tables
                for namespace_name, namespace_config in catalog_config["namespaces"].items():
                    if self._create_polaris_namespace(catalog_name, namespace_name, namespace_config["description"]):
                        self.demo_namespaces.append(f"{catalog_name}.{namespace_name}")
                        
                        # Create tables
                        for table_name, table_schema in namespace_config["tables"].items():
                            if self._create_polaris_table(catalog_name, namespace_name, table_name, table_schema):
                                self.demo_tables.append(f"{catalog_name}.{namespace_name}.{table_name}")
                            else:
                                success = False
                    else:
                        success = False
            else:
                success = False
        
        if success:
            logger.info(f"✅ Sample data setup completed - {len(self.demo_catalogs)} catalogs, {len(self.demo_namespaces)} namespaces, {len(self.demo_tables)} tables")
        else:
            logger.warning("⚠️ Sample data setup completed with some errors")
        
        return success
    
    def _create_polaris_catalog(self, catalog_name: str, description: str) -> bool:
        """Create a catalog in Polaris."""
        catalog_config = {
            "type": "CATALOG",
            "name": catalog_name,
            "properties": {
                "warehouse": f"s3://demo-warehouse/{catalog_name}/",
                "catalog-impl": "org.apache.iceberg.rest.RESTCatalog",
                "description": description
            }
        }
        
        try:
            response = requests.post(
                f"{self.polaris_url}/api/catalog/v1/catalogs",
                json=catalog_config,
                timeout=10
            )
            
            if response.status_code in [200, 201, 409]:  # 409 = already exists
                logger.info(f"📁 Catalog '{catalog_name}' ready")
                return True
            else:
                logger.error(f"❌ Failed to create catalog '{catalog_name}': {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Error creating catalog '{catalog_name}': {e}")
            return False
    
    def _create_polaris_namespace(self, catalog_name: str, namespace: str, description: str) -> bool:
        """Create a namespace in Polaris."""
        namespace_config = {
            "namespace": [namespace],
            "properties": {
                "description": description,
                "created_by": "polaris-demo",
                "created_at": datetime.now().isoformat()
            }
        }
        
        try:
            response = requests.post(
                f"{self.polaris_url}/api/catalog/v1/{catalog_name}/namespaces",
                json=namespace_config,
                timeout=10
            )
            
            if response.status_code in [200, 201, 409]:
                logger.info(f"📂 Namespace '{catalog_name}.{namespace}' ready")
                return True
            else:
                logger.error(f"❌ Failed to create namespace '{catalog_name}.{namespace}': {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Error creating namespace '{catalog_name}.{namespace}': {e}")
            return False
    
    def _create_polaris_table(self, catalog_name: str, namespace: str, table_name: str, schema: Dict) -> bool:
        """Create a table in Polaris."""
        table_config = {
            "name": table_name,
            "schema": schema,
            "partition-spec": {"spec-id": 0, "fields": []},
            "sort-order": {"order-id": 0, "fields": []},
            "properties": {
                "created_by": "polaris-demo",
                "created_at": datetime.now().isoformat(),
                "table_type": "ICEBERG"
            }
        }
        
        try:
            response = requests.post(
                f"{self.polaris_url}/api/catalog/v1/{catalog_name}/namespaces/{namespace}/tables",
                json=table_config,
                timeout=10
            )
            
            if response.status_code in [200, 201, 409]:
                logger.info(f"📊 Table '{catalog_name}.{namespace}.{table_name}' ready")
                return True
            else:
                logger.error(f"❌ Failed to create table '{catalog_name}.{namespace}.{table_name}': {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Error creating table '{catalog_name}.{namespace}.{table_name}': {e}")
            return False
    
    def create_openmetadata_service(self) -> bool:
        """Create the Polaris service in OpenMetadata."""
        if not self.jwt_token:
            logger.error("❌ JWT token required for OpenMetadata operations")
            return False
        
        headers = {
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json'
        }
        
        service_config = {
            "name": "polaris-catalog",
            "displayName": "Polaris Catalog",
            "description": "Apache Polaris Iceberg REST Catalog - Complete demo with sample data",
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
            }
        }
        
        try:
            # Check if service exists
            response = requests.get(
                f"{self.openmetadata_url}/api/v1/services/databaseServices/name/polaris-catalog",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Polaris service already exists in OpenMetadata")
                return True
            
            # Create the service
            response = requests.post(
                f"{self.openmetadata_url}/api/v1/services/databaseServices",
                headers=headers,
                json=service_config,
                timeout=10
            )
            
            if response.status_code == 201:
                logger.info("✅ Polaris service created in OpenMetadata")
                return True
            else:
                logger.error(f"❌ Failed to create OpenMetadata service: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error creating OpenMetadata service: {e}")
            return False
    
    def run_connector_ingestion(self) -> bool:
        """Run the Polaris connector ingestion workflow."""
        logger.info("🚀 Running Polaris connector ingestion...")
        
        try:
            import subprocess
            
            # Run the ingestion script
            result = subprocess.run([
                sys.executable, "scripts/run_ingestion.py"
            ], capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                logger.info("✅ Connector ingestion completed successfully")
                return True
            else:
                logger.error(f"❌ Connector ingestion failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Connector ingestion timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error running connector ingestion: {e}")
            return False
    
    def verify_integration_results(self) -> Dict[str, Any]:
        """Verify the integration results in OpenMetadata."""
        logger.info("🔍 Verifying integration results...")
        
        results = {
            "databases": [],
            "tables": [],
            "total_entities": 0,
            "verification_successful": False
        }
        
        if not self.jwt_token:
            return results
        
        headers = {'Authorization': f'Bearer {self.jwt_token}'}
        
        try:
            # Check databases
            response = requests.get(
                f"{self.openmetadata_url}/api/v1/databases",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                databases = response.json().get('data', [])
                polaris_dbs = [db for db in databases if 'polaris' in db.get('name', '').lower() or 
                              'production' in db.get('name', '').lower() or 
                              'analytics' in db.get('name', '').lower()]
                
                results["databases"] = polaris_dbs
                results["total_entities"] += len(polaris_dbs)
                
                # Check tables for each database
                for db in polaris_dbs:
                    db_id = db.get('id')
                    table_response = requests.get(
                        f"{self.openmetadata_url}/api/v1/tables?database={db_id}",
                        headers=headers,
                        timeout=10
                    )
                    
                    if table_response.status_code == 200:
                        tables = table_response.json().get('data', [])
                        results["tables"].extend(tables)
                        results["total_entities"] += len(tables)
                
                if len(results["databases"]) > 0:
                    results["verification_successful"] = True
                    logger.info(f"✅ Verification completed - Found {len(results['databases'])} databases, {len(results['tables'])} tables")
                else:
                    logger.warning("⚠️ No Polaris data found in OpenMetadata")
            
        except Exception as e:
            logger.error(f"❌ Error during verification: {e}")
        
        return results
    
    def run_complete_demo(self) -> Dict[str, Any]:
        """Run the complete end-to-end demonstration."""
        logger.info("🎬 Starting Complete Polaris to OpenMetadata Demo")
        logger.info("=" * 60)
        
        demo_results = {
            "start_time": datetime.now().isoformat(),
            "services_available": {},
            "jwt_token_loaded": False,
            "sample_data_created": False,
            "openmetadata_service_created": False,
            "ingestion_successful": False,
            "verification_results": {},
            "demo_summary": {},
            "errors": []
        }
        
        try:
            # Step 1: Check services
            logger.info("📋 Step 1: Checking required services...")
            demo_results["services_available"] = self.check_services()
            
            if not all(demo_results["services_available"].values()):
                demo_results["errors"].append("Required services are not available")
                return demo_results
            
            # Step 2: Load JWT token
            logger.info("📋 Step 2: Loading authentication...")
            demo_results["jwt_token_loaded"] = self.load_jwt_token()
            
            # Step 3: Setup Polaris sample data
            logger.info("📋 Step 3: Setting up Polaris sample data...")
            demo_results["sample_data_created"] = self.setup_polaris_sample_data()
            
            # Step 4: Create OpenMetadata service
            if self.jwt_token:
                logger.info("📋 Step 4: Creating OpenMetadata service...")
                demo_results["openmetadata_service_created"] = self.create_openmetadata_service()
            
            # Step 5: Run connector ingestion
            logger.info("📋 Step 5: Running connector ingestion...")
            demo_results["ingestion_successful"] = self.run_connector_ingestion()
            
            # Step 6: Verify results
            logger.info("📋 Step 6: Verifying integration results...")
            time.sleep(5)  # Allow time for indexing
            demo_results["verification_results"] = self.verify_integration_results()
            
            # Generate summary
            demo_results["demo_summary"] = {
                "catalogs_created": len(self.demo_catalogs),
                "namespaces_created": len(self.demo_namespaces),
                "tables_created": len(self.demo_tables),
                "databases_in_openmetadata": len(demo_results["verification_results"].get("databases", [])),
                "tables_in_openmetadata": len(demo_results["verification_results"].get("tables", [])),
                "total_entities": demo_results["verification_results"].get("total_entities", 0)
            }
            
            demo_results["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Demo failed with unexpected error: {e}"
            logger.error(f"❌ {error_msg}")
            demo_results["errors"].append(error_msg)
        
        return demo_results
    
    def print_demo_report(self, results: Dict[str, Any]):
        """Print a comprehensive demo report."""
        print("\n" + "=" * 80)
        print("🎯 POLARIS TO OPENMETADATA INTEGRATION DEMO REPORT")
        print("=" * 80)
        
        # Services Status
        print("\n🔧 Services Status:")
        for service, status in results.get("services_available", {}).items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {service.title()}: {'Available' if status else 'Unavailable'}")
        
        # Authentication
        auth_icon = "✅" if results.get("jwt_token_loaded") else "❌"
        print(f"\n🔐 Authentication: {auth_icon} {'JWT Token Loaded' if results.get('jwt_token_loaded') else 'No JWT Token'}")
        
        # Sample Data
        data_icon = "✅" if results.get("sample_data_created") else "❌"
        print(f"\n🏗️ Sample Data Setup: {data_icon} {'Successful' if results.get('sample_data_created') else 'Failed'}")
        
        # OpenMetadata Service
        service_icon = "✅" if results.get("openmetadata_service_created") else "❌"
        print(f"\n🔗 OpenMetadata Service: {service_icon} {'Created' if results.get('openmetadata_service_created') else 'Failed/Skipped'}")
        
        # Ingestion
        ingestion_icon = "✅" if results.get("ingestion_successful") else "❌"
        print(f"\n🚀 Connector Ingestion: {ingestion_icon} {'Successful' if results.get('ingestion_successful') else 'Failed'}")
        
        # Summary Statistics
        summary = results.get("demo_summary", {})
        print(f"\n📊 Demo Summary:")
        print(f"   📁 Polaris Catalogs: {summary.get('catalogs_created', 0)}")
        print(f"   📂 Polaris Namespaces: {summary.get('namespaces_created', 0)}")
        print(f"   📋 Polaris Tables: {summary.get('tables_created', 0)}")
        print(f"   🗄️ OpenMetadata Databases: {summary.get('databases_in_openmetadata', 0)}")
        print(f"   📊 OpenMetadata Tables: {summary.get('tables_in_openmetadata', 0)}")
        print(f"   🎯 Total Entities: {summary.get('total_entities', 0)}")
        
        # Generated Data Structure
        if self.demo_catalogs:
            print(f"\n📁 Created Catalogs:")
            for catalog in self.demo_catalogs:
                print(f"   • {catalog}")
        
        if self.demo_tables:
            print(f"\n📋 Created Tables:")
            for table in self.demo_tables:
                print(f"   • {table}")
        
        # Verification Results
        verification = results.get("verification_results", {})
        if verification.get("verification_successful"):
            print(f"\n✅ Integration Verification: SUCCESSFUL")
            print(f"   🔗 Data successfully flowing from Polaris to OpenMetadata")
        else:
            print(f"\n⚠️ Integration Verification: INCOMPLETE")
        
        # Errors
        if results.get("errors"):
            print(f"\n❌ Errors Encountered:")
            for error in results["errors"]:
                print(f"   • {error}")
        
        # Next Steps
        print(f"\n📋 Next Steps:")
        print(f"   1. Visit OpenMetadata UI: {self.openmetadata_url}")
        print(f"   2. Navigate to Data Assets → Databases")
        print(f"   3. Explore the Polaris Catalog data")
        print(f"   4. Check table schemas and lineage")
        print(f"   5. Access Polaris REST API: {self.polaris_url}")
        
        print("\n" + "=" * 80)
    
    # Schema definitions for sample tables
    def _get_customer_profiles_schema(self) -> Dict:
        """Schema for customer profiles table."""
        return {
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
                {"id": 13, "name": "customer_segment", "required": False, "type": "string"},
                {"id": 14, "name": "is_active", "required": True, "type": "boolean"}
            ]
        }
    
    def _get_order_history_schema(self) -> Dict:
        """Schema for order history table."""
        return {
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
                {"id": 9, "name": "delivery_date", "required": False, "type": "date"},
                {"id": 10, "name": "created_at", "required": True, "type": "timestamp"},
                {"id": 11, "name": "updated_at", "required": False, "type": "timestamp"}
            ]
        }
    
    def _get_daily_metrics_schema(self) -> Dict:
        """Schema for daily metrics table."""
        return {
            "type": "struct",
            "schema-id": 0,
            "fields": [
                {"id": 1, "name": "report_date", "required": True, "type": "date"},
                {"id": 2, "name": "region", "required": True, "type": "string"},
                {"id": 3, "name": "total_sales", "required": True, "type": "decimal(15,2)"},
                {"id": 4, "name": "total_orders", "required": True, "type": "long"},
                {"id": 5, "name": "unique_customers", "required": True, "type": "long"},
                {"id": 6, "name": "avg_order_value", "required": True, "type": "decimal(10,2)"},
                {"id": 7, "name": "new_customers", "required": True, "type": "long"},
                {"id": 8, "name": "returning_customers", "required": True, "type": "long"},
                {"id": 9, "name": "conversion_rate", "required": False, "type": "decimal(5,4)"},
                {"id": 10, "name": "created_at", "required": True, "type": "timestamp"}
            ]
        }


def main():
    """Main entry point for the demo."""
    try:
        print("🎬 Polaris to OpenMetadata Integration Demo")
        print("This demo showcases the complete data pipeline from Apache Polaris to OpenMetadata")
        print("-" * 80)
        
        # Initialize and run demo
        demo = PolarisOpenMetadataDemo()
        results = demo.run_complete_demo()
        
        # Print comprehensive report
        demo.print_demo_report(results)
        
        # Save detailed results
        output_file = f"demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        
        # Return appropriate exit code
        if results.get("verification_results", {}).get("verification_successful", False):
            print("\n🎉 Demo completed successfully!")
            return 0
        else:
            print("\n⚠️ Demo completed with issues - check the report above")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Demo failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())