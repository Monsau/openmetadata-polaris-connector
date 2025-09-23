#!/usr/bin/env python3
"""
Detailed Description Verification Script

Shows the full enhanced descriptions with source information for all Polaris tables.
"""

import requests

def show_enhanced_descriptions():
    """Show the detailed descriptions for all Polaris tables."""
    base_url = "http://localhost:8585"
    token = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImdlbmVyaWMtaW5nZXN0aW9uLWJvdCIsInJvbGVzIjpbXSwiZW1haWwiOiJnZW5lcmljLWluZ2VzdGlvbi1ib3RAdGFsZW50eXMuZXUiLCJpc0JvdCI6dHJ1ZSwidG9rZW5UeXBlIjoiQk9UIiwiaWF0IjoxNzU4MTM2NTI4LCJleHAiOm51bGx9.Hy4ed-YPdwKeZ71viL1G2JmQzo-gSdfa7MiKGj8ujgx4znEjuzFqRl15mhqsKjhSjnU-f6v_IV1Qe5kcxxaKScxq3HPPGF6snl2CgZBPXCu9QhSDQBLZO5FIY-vy8h9iLQXOYNoYj79-y7Xqu82O15vLpzHjh4_fOXJ59X0_oiq3NpIrv8eUv93K-nFqDwNPF00SwykEuoRcYNnhWueOy8e_MVkWv66kT74YKqS-iS-c6w18i0YXNnkUwt_RvzMf7-ZI6xuSV7A6xrWdFpC_2rIUJluBR2BWooLwDaA578KkjX8Rqe8VLA2vIBJlKw97Q1JY0a34lRGCiIk2HJBVHQ"
    headers = {'Authorization': f'Bearer {token}'}
    
    print("📋 Polaris Tables - Enhanced Descriptions with Source Information")
    print("=" * 80)
    
    tables = [
        "polaris-catalog.analytics_data.reporting.monthly_sales",
        "polaris-catalog.analytics_data.reporting.customer_segmentation",
        "polaris-catalog.production_data.sales.orders",
        "polaris-catalog.production_data.sales.customers",
        "polaris-catalog.production_data.sales.products"
    ]
    
    for i, table_fqn in enumerate(tables, 1):
        response = requests.get(
            f"{base_url}/api/v1/tables/name/{table_fqn}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            table_data = response.json()
            table_name = table_data['name']
            description = table_data.get('description', 'No description available')
            
            print(f"\n{i}. 📊 {table_name.upper()}")
            print(f"   FQN: {table_fqn}")
            print(f"   Columns: {len(table_data.get('columns', []))}")
            print(f"\n   Description:")
            # Print description with proper formatting
            for line in description.split('\n'):
                print(f"   {line}")
            print("-" * 80)
        else:
            print(f"\n❌ Failed to get {table_fqn}: {response.status_code}")
    
    print(f"\n🌐 Access Enhanced Descriptions:")
    print(f"   • OpenMetadata UI: http://localhost:8585")
    print(f"   • Navigate to any table to see complete source information")
    print(f"   • Each description now includes data lineage and source details")

if __name__ == "__main__":
    show_enhanced_descriptions()