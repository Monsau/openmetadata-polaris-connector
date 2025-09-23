#!/usr/bin/env python3
"""
Simple Table Creation for Polaris Demo

Creates the 5 demo tables directly in OpenMetadata to simulate Polaris catalog structure.
"""

import requests
import json
import time

class SimpleTableCreator:
    def __init__(self):
        self.base_url = "http://localhost:8585"
        self.token = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImdlbmVyaWMtaW5nZXN0aW9uLWJvdCIsInJvbGVzIjpbXSwiZW1haWwiOiJnZW5lcmljLWluZ2VzdGlvbi1ib3RAdGFsZW50eXMuZXUiLCJpc0JvdCI6dHJ1ZSwidG9rZW5UeXBlIjoiQk9UIiwiaWF0IjoxNzU4MTM2NTI4LCJleHAiOm51bGx9.Hy4ed-YPdwKeZ71viL1G2JmQzo-gSdfa7MiKGj8ujgx4znEjuzFqRl15mhqsKjhSjnU-f6v_IV1Qe5kcxxaKScxq3HPPGF6snl2CgZBPXCu9QhSDQBLZO5FIY-vy8h9iLQXOYNoYj79-y7Xqu82O15vLpzHjh4_fOXJ59X0_oiq3NpIrv8eUv93K-nFqDwNPF00SwykEuoRcYNnhWueOy8e_MVkWv66kT74YKqS-iS-c6w18i0YXNnkUwt_RvzMf7-ZI6xuSV7A6xrWdFpC_2rIUJluBR2BWooLwDaA578KkjX8Rqe8VLA2vIBJlKw97Q1JY0a34lRGCiIk2HJBVHQ"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def create_schema_if_needed(self, database_fqn: str, schema_name: str):
        """Create a schema if it doesn't exist."""
        schema_config = {
            "name": schema_name,
            "displayName": schema_name,
            "database": database_fqn
        }
        
        # Check if schema exists
        schema_fqn = f"{database_fqn}.{schema_name}"
        response = requests.get(
            f"{self.base_url}/api/v1/databaseSchemas/name/{schema_fqn}",
            headers=self.headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Schema '{schema_name}' already exists")
            return True
        
        # Create the schema
        response = requests.post(
            f"{self.base_url}/api/v1/databaseSchemas",
            headers=self.headers,
            json=schema_config,
            timeout=10
        )
        
        if response.status_code == 201:
            print(f"✅ Created schema '{schema_name}'")
            return True
        else:
            print(f"❌ Failed to create schema '{schema_name}': {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def create_table_with_schema(self, database_fqn: str, schema_name: str, table_name: str, description: str, columns: list):
        """Create a table in a specific schema."""
        # First ensure the schema exists
        if not self.create_schema_if_needed(database_fqn, schema_name):
            return False
        
        table_config = {
            "name": table_name,
            "displayName": table_name,
            "description": description,
            "tableType": "Regular",
            "columns": columns,
            "databaseSchema": f"{database_fqn}.{schema_name}",
            "sourceUrl": "http://localhost:8181",
            "tags": [
                {
                    "tagFQN": "PolarisSource.ApachePolaris",
                    "description": "Table sourced from Apache Polaris catalog"
                },
                {
                    "tagFQN": "DataFormat.Iceberg",
                    "description": "Apache Iceberg table format"
                }
            ],
            "extension": {
                "sourceSystem": "Apache Polaris",
                "catalogVersion": "1.1.0",
                "tableFormat": "Apache Iceberg",
                "storageLayer": "File System",
                "governance": "Apache Polaris Access Control"
            }
        }
        
        # Check if table exists
        table_fqn = f"{database_fqn}.{schema_name}.{table_name}"
        response = requests.get(
            f"{self.base_url}/api/v1/tables/name/{table_fqn}",
            headers=self.headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Table '{table_name}' already exists")
            return True
        
        # Create the table
        response = requests.post(
            f"{self.base_url}/api/v1/tables",
            headers=self.headers,
            json=table_config,
            timeout=10
        )
        
        if response.status_code == 201:
            print(f"✅ Created table '{table_name}' in '{schema_name}'")
            return True
        else:
            print(f"❌ Failed to create table '{table_name}': {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def run(self):
        """Create all 5 demo tables."""
        print("🚀 Creating Polaris Demo Tables in OpenMetadata")
        print("=" * 55)
        
        success = True
        
        # Analytics data tables (reporting schema)
        analytics_db = "polaris-catalog.analytics_data"
        success &= self.create_table_with_schema(
            analytics_db, "reporting", "monthly_sales",
            """📊 SOURCE: Apache Polaris Iceberg Catalog

Monthly aggregated sales data for reporting and analytics.

🏗️ **Data Source**: Apache Polaris (analytics_data.reporting)
📁 **Storage Format**: Apache Iceberg tables 
🔄 **Update Frequency**: Monthly batch processing from production orders
🎯 **Business Purpose**: Executive reporting and sales trend analysis
🌐 **REST Endpoint**: http://localhost:8181/v1/catalogs/analytics_data
📋 **Governance**: Managed by Apache Polaris access control""",
            [
                {"name": "month", "dataType": "DATE", "description": "Reporting month"},
                {"name": "region", "dataType": "VARCHAR", "dataLength": 100, "description": "Sales region"},
                {"name": "total_sales", "dataType": "DOUBLE", "description": "Total sales amount"},
                {"name": "total_orders", "dataType": "INT", "description": "Number of orders"},
                {"name": "created_at", "dataType": "TIMESTAMP", "description": "Record creation timestamp"}
            ]
        )
        
        success &= self.create_table_with_schema(
            analytics_db, "reporting", "customer_segmentation",
            """📊 SOURCE: Apache Polaris Iceberg Catalog

Customer segmentation analysis for marketing campaigns and customer insights.

🏗️ **Data Source**: Apache Polaris (analytics_data.reporting)
📁 **Storage Format**: Apache Iceberg tables
🔄 **Update Frequency**: Weekly ML pipeline execution
🎯 **Business Purpose**: Marketing personalization and customer lifetime value
🌐 **REST Endpoint**: http://localhost:8181/v1/catalogs/analytics_data  
📋 **Governance**: Managed by Apache Polaris access control""",
            [
                {"name": "customer_id", "dataType": "INT", "description": "Unique customer identifier"},
                {"name": "segment", "dataType": "VARCHAR", "dataLength": 50, "description": "Customer segment category"},
                {"name": "ltv", "dataType": "DOUBLE", "description": "Customer lifetime value"},
                {"name": "segment_score", "dataType": "DOUBLE", "description": "Segmentation confidence score"},
                {"name": "last_updated", "dataType": "TIMESTAMP", "description": "Last update timestamp"}
            ]
        )
        
        # Production data tables (sales schema)
        production_db = "polaris-catalog.production_data"
        success &= self.create_table_with_schema(
            production_db, "sales", "orders",
            """📊 SOURCE: Apache Polaris Iceberg Catalog

Customer orders from e-commerce platform and point-of-sale systems.

🏗️ **Data Source**: Apache Polaris (production_data.sales)
📁 **Storage Format**: Apache Iceberg tables with ACID transactions
🔄 **Update Frequency**: Real-time streaming ingestion
🎯 **Business Purpose**: Order fulfillment and sales operations
🌐 **REST Endpoint**: http://localhost:8181/v1/catalogs/production_data
📋 **Governance**: Managed by Apache Polaris access control""",
            [
                {"name": "order_id", "dataType": "INT", "description": "Unique order identifier"},
                {"name": "customer_id", "dataType": "INT", "description": "Customer who placed the order"},
                {"name": "order_date", "dataType": "DATE", "description": "Date the order was placed"},
                {"name": "total_amount", "dataType": "DOUBLE", "description": "Total order amount"},
                {"name": "status", "dataType": "VARCHAR", "dataLength": 20, "description": "Order status"}
            ]
        )
        
        success &= self.create_table_with_schema(
            production_db, "sales", "customers",
            """📊 SOURCE: Apache Polaris Iceberg Catalog

Customer information and profiles from CRM and registration systems.

🏗️ **Data Source**: Apache Polaris (production_data.sales)
📁 **Storage Format**: Apache Iceberg tables with schema evolution
🔄 **Update Frequency**: Near real-time CDC from CRM systems
🎯 **Business Purpose**: Customer relationship management
🌐 **REST Endpoint**: http://localhost:8181/v1/catalogs/production_data
📋 **Governance**: Managed by Apache Polaris access control with PII protection""",
            [
                {"name": "customer_id", "dataType": "INT", "description": "Unique customer identifier"},
                {"name": "first_name", "dataType": "VARCHAR", "dataLength": 50, "description": "Customer first name"},
                {"name": "last_name", "dataType": "VARCHAR", "dataLength": 50, "description": "Customer last name"},
                {"name": "email", "dataType": "VARCHAR", "dataLength": 100, "description": "Customer email address"},
                {"name": "registration_date", "dataType": "DATE", "description": "Account registration date"}
            ]
        )
        
        success &= self.create_table_with_schema(
            production_db, "sales", "products",
            """📊 SOURCE: Apache Polaris Iceberg Catalog

Product catalog and inventory information from product management systems.

🏗️ **Data Source**: Apache Polaris (production_data.sales)
📁 **Storage Format**: Apache Iceberg tables with partitioning
🔄 **Update Frequency**: Hourly batch updates from inventory systems
🎯 **Business Purpose**: Product catalog management and inventory tracking
🌐 **REST Endpoint**: http://localhost:8181/v1/catalogs/production_data
📋 **Governance**: Managed by Apache Polaris access control""",
            [
                {"name": "product_id", "dataType": "INT", "description": "Unique product identifier"},
                {"name": "name", "dataType": "VARCHAR", "dataLength": 200, "description": "Product name"},
                {"name": "category", "dataType": "VARCHAR", "dataLength": 50, "description": "Product category"},
                {"name": "price", "dataType": "DOUBLE", "description": "Product price"},
                {"name": "stock_quantity", "dataType": "INT", "description": "Available stock quantity"}
            ]
        )
        
        print("\n🔍 Verifying created tables...")
        time.sleep(2)
        
        # Verify tables
        response = requests.get(
            f"{self.base_url}/api/v1/tables",
            headers=self.headers,
            timeout=10
        )
        
        if response.status_code == 200:
            tables = response.json().get('data', [])
            polaris_tables = [
                table for table in tables 
                if 'polaris-catalog' in table.get('fullyQualifiedName', '')
            ]
            
            print(f"📋 Found {len(polaris_tables)} Polaris tables:")
            table_names = []
            for table in polaris_tables:
                fqn = table.get('fullyQualifiedName', '')
                print(f"   - {fqn}")
                table_names.append(fqn.split('.')[-1])
            
            expected_tables = ['monthly_sales', 'customer_segmentation', 'orders', 'customers', 'products']
            found_expected = sum(1 for name in expected_tables if name in table_names)
            
            if found_expected == 5:
                print(f"\n🎉 SUCCESS! All 5 expected tables found!")
            else:
                print(f"\n⚠️  Found {found_expected}/5 expected tables")
        
        print("\n" + "=" * 55)
        print("🌐 Next steps:")
        print("1. Visit OpenMetadata UI: http://localhost:8585")
        print("2. Navigate to Databases → analytics_data or production_data")
        print("3. Explore the Polaris catalog structure and tables")
        
        return success

def main():
    creator = SimpleTableCreator()
    success = creator.run()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()