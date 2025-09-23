#!/usr/bin/env python3
"""
Update Polaris Table Descriptions

Updates the descriptions of all 5 Polaris demo tables to include source information.
"""

import requests
import json

class TableDescriptionUpdater:
    def __init__(self):
        self.base_url = "http://localhost:8585"
        self.token = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImdlbmVyaWMtaW5nZXN0aW9uLWJvdCIsInJvbGVzIjpbXSwiZW1haWwiOiJnZW5lcmljLWluZ2VzdGlvbi1ib3RAdGFsZW50eXMuZXUiLCJpc0JvdCI6dHJ1ZSwidG9rZW5UeXBlIjoiQk9UIiwiaWF0IjoxNzU4MTM2NTI4LCJleHAiOm51bGx9.Hy4ed-YPdwKeZ71viL1G2JmQzo-gSdfa7MiKGj8ujgx4znEjuzFqRl15mhqsKjhSjnU-f6v_IV1Qe5kcxxaKScxq3HPPGF6snl2CgZBPXCu9QhSDQBLZO5FIY-vy8h9iLQXOYNoYj79-y7Xqu82O15vLpzHjh4_fOXJ59X0_oiq3NpIrv8eUv93K-nFqDwNPF00SwykEuoRcYNnhWueOy8e_MVkWv66kT74YKqS-iS-c6w18i0YXNnkUwt_RvzMf7-ZI6xuSV7A6xrWdFpC_2rIUJluBR2BWooLwDaA578KkjX8Rqe8VLA2vIBJlKw97Q1JY0a34lRGCiIk2HJBVHQ"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def update_table_description(self, table_fqn: str, new_description: str) -> bool:
        """Update a table's description."""
        try:
            # Get the current table data
            response = requests.get(
                f"{self.base_url}/api/v1/tables/name/{table_fqn}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to get table {table_fqn}: {response.status_code}")
                return False
            
            table_data = response.json()
            
            # Create clean update payload with only allowed fields
            update_payload = {
                "name": table_data["name"],
                "displayName": table_data.get("displayName", table_data["name"]),
                "description": new_description,
                "tableType": table_data.get("tableType", "Regular"),
                "columns": table_data.get("columns", []),
                "databaseSchema": table_data["databaseSchema"]["fullyQualifiedName"]
            }
            
            # Add optional fields if they exist
            if "tags" in table_data:
                update_payload["tags"] = table_data["tags"]
            if "owners" in table_data:
                update_payload["owners"] = table_data["owners"]
            
            # Use PUT to update the table
            response = requests.put(
                f"{self.base_url}/api/v1/tables",
                headers=self.headers,
                json=update_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Updated description for {table_fqn.split('.')[-1]}")
                return True
            else:
                print(f"❌ Failed to update {table_fqn}: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Error updating {table_fqn}: {e}")
            return False
    
    def run(self):
        """Update all table descriptions with source information."""
        print("🔄 Updating Polaris Table Descriptions with Source Information")
        print("=" * 65)
        
        # Define tables with enhanced descriptions including source information
        tables_to_update = [
            {
                "fqn": "polaris-catalog.analytics_data.reporting.monthly_sales",
                "description": """Monthly aggregated sales data for reporting and analytics.

📊 **Source**: Apache Polaris Iceberg Catalog (analytics_data.reporting)
🗂️ **Data Source**: Aggregated from production_data.sales.orders table
📅 **Update Frequency**: Monthly batch processing
🎯 **Purpose**: Business intelligence reporting and trend analysis
📋 **Schema**: Iceberg table format with partitioning by month and region"""
            },
            {
                "fqn": "polaris-catalog.analytics_data.reporting.customer_segmentation",
                "description": """Customer segmentation analysis for marketing campaigns and customer insights.

📊 **Source**: Apache Polaris Iceberg Catalog (analytics_data.reporting)
🗂️ **Data Source**: Derived from production_data.sales.customers and orders analysis
📅 **Update Frequency**: Weekly ML pipeline execution
🎯 **Purpose**: Marketing campaign targeting and customer lifetime value analysis
📋 **Schema**: Iceberg table with customer segments and scoring algorithms"""
            },
            {
                "fqn": "polaris-catalog.production_data.sales.orders",
                "description": """Customer orders from the e-commerce platform and point-of-sale systems.

📊 **Source**: Apache Polaris Iceberg Catalog (production_data.sales)
🗂️ **Data Source**: Real-time ingestion from e-commerce API and POS systems
📅 **Update Frequency**: Real-time streaming ingestion
🎯 **Purpose**: Operational order management and sales tracking
📋 **Schema**: Iceberg table with ACID transactions and change data capture"""
            },
            {
                "fqn": "polaris-catalog.production_data.sales.customers",
                "description": """Customer information and profiles from CRM and registration systems.

📊 **Source**: Apache Polaris Iceberg Catalog (production_data.sales)
🗂️ **Data Source**: CRM system, user registration, and profile management APIs
📅 **Update Frequency**: Near real-time CDC from CRM system
🎯 **Purpose**: Customer relationship management and personalization
📋 **Schema**: Iceberg table with PII data governance and data lineage tracking"""
            },
            {
                "fqn": "polaris-catalog.production_data.sales.products",
                "description": """Product catalog and inventory information from product management systems.

📊 **Source**: Apache Polaris Iceberg Catalog (production_data.sales)
🗂️ **Data Source**: Product Information Management (PIM) system and inventory APIs
📅 **Update Frequency**: Hourly batch updates from inventory management
🎯 **Purpose**: Product catalog management and inventory tracking
📋 **Schema**: Iceberg table with product hierarchy and inventory partitioning"""
            }
        ]
        
        success_count = 0
        for table in tables_to_update:
            if self.update_table_description(table["fqn"], table["description"]):
                success_count += 1
        
        print(f"\n📊 Summary: {success_count}/5 table descriptions updated")
        
        if success_count == 5:
            print("🎉 SUCCESS! All table descriptions now include source information!")
            print("\n📋 Enhanced Information Added:")
            print("   • Apache Polaris catalog source location")
            print("   • Data source systems and APIs")
            print("   • Update frequency and data freshness")
            print("   • Business purpose and use cases")
            print("   • Iceberg table schema details")
            
            print("\n🌐 View Updated Descriptions:")
            print("   • URL: http://localhost:8585")
            print("   • Navigate to any table to see the enhanced description")
            print("   • Each table now shows its complete data lineage")
        else:
            print("⚠️  Some descriptions failed to update. Check the errors above.")
        
        return success_count == 5

def main():
    updater = TableDescriptionUpdater()
    success = updater.run()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()