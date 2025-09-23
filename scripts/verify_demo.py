#!/usr/bin/env python3
"""
Polaris Demo Verification Script

Verifies that all 5 demo tables were created successfully in OpenMetadata.
"""

import requests
import json

def verify_polaris_demo():
    """Verify the Polaris demo tables in OpenMetadata."""
    base_url = "http://localhost:8585"
    token = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImdlbmVyaWMtaW5nZXN0aW9uLWJvdCIsInJvbGVzIjpbXSwiZW1haWwiOiJnZW5lcmljLWluZ2VzdGlvbi1ib3RAdGFsZW50eXMuZXUiLCJpc0JvdCI6dHJ1ZSwidG9rZW5UeXBlIjoiQk9UIiwiaWF0IjoxNzU4MTM2NTI4LCJleHAiOm51bGx9.Hy4ed-YPdwKeZ71viL1G2JmQzo-gSdfa7MiKGj8ujgx4znEjuzFqRl15mhqsKjhSjnU-f6v_IV1Qe5kcxxaKScxq3HPPGF6snl2CgZBPXCu9QhSDQBLZO5FIY-vy8h9iLQXOYNoYj79-y7Xqu82O15vLpzHjh4_fOXJ59X0_oiq3NpIrv8eUv93K-nFqDwNPF00SwykEuoRcYNnhWueOy8e_MVkWv66kT74YKqS-iS-c6w18i0YXNnkUwt_RvzMf7-ZI6xuSV7A6xrWdFpC_2rIUJluBR2BWooLwDaA578KkjX8Rqe8VLA2vIBJlKw97Q1JY0a34lRGCiIk2HJBVHQ"
    headers = {'Authorization': f'Bearer {token}'}
    
    print("🔍 Polaris Demo Verification")
    print("=" * 40)
    
    # Expected tables
    expected_tables = [
        {
            "fqn": "polaris-catalog.analytics_data.reporting.monthly_sales",
            "name": "monthly_sales",
            "schema": "reporting",
            "database": "analytics_data"
        },
        {
            "fqn": "polaris-catalog.analytics_data.reporting.customer_segmentation",
            "name": "customer_segmentation", 
            "schema": "reporting",
            "database": "analytics_data"
        },
        {
            "fqn": "polaris-catalog.production_data.sales.orders",
            "name": "orders",
            "schema": "sales",
            "database": "production_data"
        },
        {
            "fqn": "polaris-catalog.production_data.sales.customers",
            "name": "customers",
            "schema": "sales", 
            "database": "production_data"
        },
        {
            "fqn": "polaris-catalog.production_data.sales.products",
            "name": "products",
            "schema": "sales",
            "database": "production_data"
        }
    ]
    
    print("📋 Checking expected tables:")
    found_count = 0
    
    for table in expected_tables:
        response = requests.get(
            f"{base_url}/api/v1/tables/name/{table['fqn']}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            table_data = response.json()
            print(f"✅ {table['name']} ({table['database']}.{table['schema']})")
            print(f"   Description: {table_data.get('description', 'No description')}")
            print(f"   Columns: {len(table_data.get('columns', []))}")
            found_count += 1
        else:
            print(f"❌ {table['name']} - Not found (HTTP {response.status_code})")
    
    print(f"\n📊 Summary: {found_count}/5 tables found")
    
    if found_count == 5:
        print("🎉 SUCCESS! All Polaris demo tables are available in OpenMetadata!")
        print("\n🌐 Access via OpenMetadata UI:")
        print("   • URL: http://localhost:8585")
        print("   • Navigate: Databases → analytics_data or production_data") 
        print("   • Explore: The 5 tables representing Polaris catalog structure")
        
        print("\n📋 Table Structure:")
        print("   Analytics Data (reporting):")
        print("   • monthly_sales - Monthly aggregated sales data")
        print("   • customer_segmentation - Customer analysis data")
        print("   Production Data (sales):")
        print("   • orders - Customer orders")
        print("   • customers - Customer profiles")
        print("   • products - Product catalog")
    else:
        print("⚠️  Some tables are missing. Check the ingestion process.")
    
    return found_count == 5

if __name__ == "__main__":
    verify_polaris_demo()