#!/usr/bin/env python3
"""
Polaris Structure and Content Explorer

This script explores and displays the complete structure and content 
of Apache Polaris catalogs, including catalogs, namespaces, tables,
and their schemas in a hierarchical view.
"""

import json
import requests
import sys
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PolarisExplorer:
    """Explores and displays Polaris catalog structure and content."""
    
    def __init__(self, polaris_url: str = "http://localhost:8181"):
        self.polaris_url = polaris_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Data storage
        self.catalog_data = {}
        self.exploration_results = {
            "timestamp": datetime.now().isoformat(),
            "polaris_url": polaris_url,
            "catalogs": {},
            "summary": {},
            "errors": []
        }
    
    def check_polaris_health(self) -> bool:
        """Check if Polaris is accessible and healthy."""
        try:
            logger.info("🔍 Checking Polaris health...")
            # Try the management health endpoint on port 8182
            health_url = self.polaris_url.replace("8181", "8182") + "/q/health"
            response = self.session.get(health_url, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Polaris is healthy and accessible")
                return True
            else:
                logger.error(f"❌ Polaris health check failed: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.error(f"❌ Cannot connect to Polaris: {e}")
            return False
    
    def get_catalogs(self) -> List[str]:
        """Retrieve all available catalogs."""
        try:
            logger.info("📁 Discovering catalogs...")
            # Try different possible endpoints for catalog discovery
            endpoints_to_try = [
                f"{self.polaris_url}/v1/config",  # Standard Iceberg endpoint
                f"{self.polaris_url}/api/v1/catalogs",  # Alternative API
                f"{self.polaris_url}/catalogs"  # Simple endpoint
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    response = self.session.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"✅ Got response from {endpoint}")
                        
                        # Handle config response (might contain defaults)
                        if 'defaults' in data:
                            # This is likely a config response, extract catalog info
                            catalogs = []
                            if 'catalog' in data.get('defaults', {}):
                                catalogs.append('default')  # Default catalog
                            logger.info(f"✅ Found config-based catalogs: {catalogs}")
                            return catalogs
                        
                        # Handle direct catalog list
                        catalogs = []
                        if isinstance(data, dict):
                            if 'catalogs' in data:
                                catalogs = [cat.get('name', cat) for cat in data['catalogs']]
                            elif 'data' in data:
                                catalogs = [cat.get('name', cat) for cat in data['data']]
                            else:
                                catalogs = list(data.keys())
                        elif isinstance(data, list):
                            catalogs = [cat.get('name', cat) if isinstance(cat, dict) else cat for cat in data]
                        
                        if catalogs:
                            logger.info(f"✅ Found {len(catalogs)} catalogs: {', '.join(catalogs)}")
                            return catalogs
                            
                except requests.RequestException:
                    continue  # Try next endpoint
            
            # If no standard endpoints work, try to infer from sample data structure
            logger.warning("⚠️ Standard catalog endpoints not responding, checking for sample data structure...")
            
            # Based on the sample data creation, try these catalog names
            sample_catalogs = ['main', 'analytics', 'staging', 'production_data', 'analytics_data']
            existing_catalogs = []
            
            for catalog in sample_catalogs:
                try:
                    # Try to get namespaces for this catalog to see if it exists
                    ns_response = self.session.get(f"{self.polaris_url}/v1/catalogs/{catalog}/namespaces", timeout=5)
                    if ns_response.status_code == 200:
                        existing_catalogs.append(catalog)
                        logger.info(f"✅ Confirmed catalog exists: {catalog}")
                except:
                    continue
            
            if existing_catalogs:
                logger.info(f"✅ Found {len(existing_catalogs)} catalogs via inference: {', '.join(existing_catalogs)}")
                return existing_catalogs
            
            logger.error("❌ No catalogs found via any method")
            return []
                
        except Exception as e:
            logger.error(f"❌ Error retrieving catalogs: {e}")
            return []
    
    def get_namespaces(self, catalog_name: str) -> List[str]:
        """Retrieve all namespaces in a catalog."""
        try:
            logger.info(f"📂 Discovering namespaces in catalog '{catalog_name}'...")
            response = self.session.get(
                f"{self.polaris_url}/v1/catalogs/{catalog_name}/namespaces", 
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                namespaces = []
                
                # Handle different response formats
                if isinstance(data, dict):
                    if 'namespaces' in data:
                        # Extract namespace names from complex structure
                        for ns in data['namespaces']:
                            if isinstance(ns, dict) and 'namespace' in ns:
                                if isinstance(ns['namespace'], list):
                                    namespaces.extend(ns['namespace'])
                                else:
                                    namespaces.append(ns['namespace'])
                            elif isinstance(ns, list):
                                namespaces.extend(ns)
                            else:
                                namespaces.append(str(ns))
                    elif 'data' in data:
                        namespaces = data['data']
                elif isinstance(data, list):
                    namespaces = data
                
                logger.info(f"✅ Found {len(namespaces)} namespaces in '{catalog_name}': {', '.join(namespaces)}")
                return namespaces
            else:
                logger.warning(f"⚠️ Failed to get namespaces for '{catalog_name}': {response.status_code}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"❌ Error retrieving namespaces for '{catalog_name}': {e}")
            return []
    
    def get_tables(self, catalog_name: str, namespace: str) -> List[Dict[str, Any]]:
        """Retrieve all tables in a namespace."""
        try:
            logger.info(f"📊 Discovering tables in '{catalog_name}.{namespace}'...")
            response = self.session.get(
                f"{self.polaris_url}/v1/catalogs/{catalog_name}/namespaces/{namespace}/tables",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                tables = []
                
                # Handle different response formats
                if isinstance(data, dict):
                    if 'identifiers' in data:
                        # Convert identifiers to table info
                        for identifier in data['identifiers']:
                            if isinstance(identifier, dict) and 'name' in identifier:
                                tables.append({
                                    'name': identifier['name'],
                                    'namespace': identifier.get('namespace', [namespace])
                                })
                            elif isinstance(identifier, list) and len(identifier) > 0:
                                tables.append({
                                    'name': identifier[-1],  # Last element is usually table name
                                    'namespace': identifier[:-1] if len(identifier) > 1 else [namespace]
                                })
                    elif 'tables' in data:
                        tables = data['tables']
                    elif 'data' in data:
                        tables = data['data']
                elif isinstance(data, list):
                    tables = data
                
                # Ensure all table entries have names
                formatted_tables = []
                for table in tables:
                    if isinstance(table, dict):
                        formatted_tables.append(table)
                    else:
                        formatted_tables.append({'name': str(table), 'namespace': [namespace]})
                
                logger.info(f"✅ Found {len(formatted_tables)} tables in '{catalog_name}.{namespace}'")
                return formatted_tables
            else:
                logger.warning(f"⚠️ Failed to get tables for '{catalog_name}.{namespace}': {response.status_code}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"❌ Error retrieving tables for '{catalog_name}.{namespace}': {e}")
            return []
    
    def get_table_schema(self, catalog_name: str, namespace: str, table_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve detailed schema for a specific table."""
        try:
            logger.info(f"🔍 Getting schema for table '{catalog_name}.{namespace}.{table_name}'...")
            response = self.session.get(
                f"{self.polaris_url}/v1/catalogs/{catalog_name}/namespaces/{namespace}/tables/{table_name}",
                timeout=10
            )
            
            if response.status_code == 200:
                schema_data = response.json()
                logger.info(f"✅ Retrieved schema for '{table_name}'")
                return schema_data
            else:
                logger.warning(f"⚠️ Failed to get schema for '{table_name}': {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"❌ Error retrieving schema for '{table_name}': {e}")
            return None
    
    def explore_catalog_structure(self) -> Dict[str, Any]:
        """Explore the complete Polaris catalog structure."""
        logger.info("🚀 Starting Polaris structure exploration...")
        
        # Check health first
        if not self.check_polaris_health():
            self.exploration_results["errors"].append("Polaris is not accessible")
            return self.exploration_results
        
        # Get all catalogs
        catalogs = self.get_catalogs()
        if not catalogs:
            self.exploration_results["errors"].append("No catalogs found")
            return self.exploration_results
        
        # Explore each catalog
        for catalog_name in catalogs:
            logger.info(f"\n📁 Exploring catalog: {catalog_name}")
            catalog_info = {
                "name": catalog_name,
                "namespaces": {},
                "total_tables": 0,
                "total_namespaces": 0,
                "created_at": datetime.now().isoformat()
            }
            
            # Get namespaces in this catalog
            namespaces = self.get_namespaces(catalog_name)
            catalog_info["total_namespaces"] = len(namespaces)
            
            for namespace in namespaces:
                logger.info(f"  📂 Exploring namespace: {namespace}")
                namespace_info = {
                    "name": namespace,
                    "tables": {},
                    "table_count": 0
                }
                
                # Get tables in this namespace
                tables = self.get_tables(catalog_name, namespace)
                namespace_info["table_count"] = len(tables)
                catalog_info["total_tables"] += len(tables)
                
                for table in tables:
                    table_name = table.get('name', str(table))
                    logger.info(f"    📊 Exploring table: {table_name}")
                    
                    # Get table schema
                    schema = self.get_table_schema(catalog_name, namespace, table_name)
                    
                    table_info = {
                        "name": table_name,
                        "namespace_path": table.get('namespace', [namespace]),
                        "schema": schema,
                        "column_count": 0,
                        "columns": []
                    }
                    
                    # Extract column information from schema
                    if schema and 'schema' in schema:
                        table_schema = schema['schema']
                        if 'fields' in table_schema:
                            table_info["columns"] = table_schema['fields']
                            table_info["column_count"] = len(table_schema['fields'])
                    
                    namespace_info["tables"][table_name] = table_info
                
                catalog_info["namespaces"][namespace] = namespace_info
            
            self.exploration_results["catalogs"][catalog_name] = catalog_info
        
        # Generate summary
        self.exploration_results["summary"] = self._generate_summary()
        
        logger.info("✅ Exploration completed!")
        return self.exploration_results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the exploration results."""
        total_catalogs = len(self.exploration_results["catalogs"])
        total_namespaces = 0
        total_tables = 0
        total_columns = 0
        
        for catalog_info in self.exploration_results["catalogs"].values():
            total_namespaces += catalog_info["total_namespaces"]
            total_tables += catalog_info["total_tables"]
            
            for namespace_info in catalog_info["namespaces"].values():
                for table_info in namespace_info["tables"].values():
                    total_columns += table_info["column_count"]
        
        return {
            "total_catalogs": total_catalogs,
            "total_namespaces": total_namespaces,
            "total_tables": total_tables,
            "total_columns": total_columns,
            "exploration_time": datetime.now().isoformat()
        }
    
    def print_structure_tree(self):
        """Print a hierarchical tree view of the Polaris structure."""
        print("\n" + "=" * 80)
        print("🏗️  POLARIS CATALOG STRUCTURE")
        print("=" * 80)
        
        if not self.exploration_results["catalogs"]:
            print("❌ No catalog data available")
            return
        
        # Print summary
        summary = self.exploration_results["summary"]
        print(f"\n📊 Summary:")
        print(f"   📁 Catalogs: {summary['total_catalogs']}")
        print(f"   📂 Namespaces: {summary['total_namespaces']}")
        print(f"   📊 Tables: {summary['total_tables']}")
        print(f"   📋 Columns: {summary['total_columns']}")
        
        # Print detailed structure
        for catalog_name, catalog_info in self.exploration_results["catalogs"].items():
            print(f"\n📁 {catalog_name}")
            print(f"   ├── Namespaces: {catalog_info['total_namespaces']}")
            print(f"   └── Total Tables: {catalog_info['total_tables']}")
            
            for namespace_name, namespace_info in catalog_info["namespaces"].items():
                print(f"   📂 {namespace_name}")
                print(f"      ├── Tables: {namespace_info['table_count']}")
                
                for table_name, table_info in namespace_info["tables"].items():
                    print(f"      📊 {table_name}")
                    print(f"         ├── Columns: {table_info['column_count']}")
                    
                    # Print column details
                    for i, column in enumerate(table_info["columns"]):
                        is_last = i == len(table_info["columns"]) - 1
                        connector = "└──" if is_last else "├──"
                        column_name = column.get('name', 'unknown')
                        column_type = column.get('type', 'unknown')
                        required = "required" if column.get('required', False) else "optional"
                        print(f"         {connector} {column_name} ({column_type}) [{required}]")
    
    def print_detailed_content(self):
        """Print detailed content including schemas and metadata."""
        print("\n" + "=" * 80)
        print("📋 DETAILED POLARIS CONTENT")
        print("=" * 80)
        
        for catalog_name, catalog_info in self.exploration_results["catalogs"].items():
            print(f"\n{'='*60}")
            print(f"📁 CATALOG: {catalog_name}")
            print(f"{'='*60}")
            
            for namespace_name, namespace_info in catalog_info["namespaces"].items():
                print(f"\n📂 NAMESPACE: {namespace_name}")
                print("-" * 40)
                
                for table_name, table_info in namespace_info["tables"].items():
                    print(f"\n📊 TABLE: {table_name}")
                    print(f"   Namespace Path: {' → '.join(table_info['namespace_path'])}")
                    print(f"   Column Count: {table_info['column_count']}")
                    
                    if table_info["columns"]:
                        print(f"   Columns:")
                        for column in table_info["columns"]:
                            column_id = column.get('id', 'N/A')
                            column_name = column.get('name', 'unknown')
                            column_type = column.get('type', 'unknown')
                            required = "✓" if column.get('required', False) else "✗"
                            print(f"     [{column_id:2}] {column_name:20} {column_type:15} Required: {required}")
                    
                    # Print schema metadata if available
                    if table_info["schema"]:
                        schema = table_info["schema"]
                        if 'properties' in schema:
                            print(f"   Properties:")
                            for key, value in schema['properties'].items():
                                print(f"     {key}: {value}")
    
    def save_results_to_file(self, filename: str = None):
        """Save exploration results to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"polaris_structure_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.exploration_results, f, indent=2, default=str, ensure_ascii=False)
            
            print(f"\n💾 Results saved to: {filename}")
            print(f"   File size: {self._get_file_size(filename)}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")
    
    def _get_file_size(self, filename: str) -> str:
        """Get human-readable file size."""
        try:
            import os
            size = os.path.getsize(filename)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown size"
    
    def run_interactive_exploration(self):
        """Run an interactive exploration session."""
        print("🚀 Polaris Interactive Structure Explorer")
        print("=" * 50)
        
        while True:
            print("\n📋 Options:")
            print("1. Explore complete structure")
            print("2. Show structure tree")
            print("3. Show detailed content")
            print("4. Save results to file")
            print("5. Refresh data")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-5): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                print("\n🔍 Exploring Polaris structure...")
                self.explore_catalog_structure()
                print("✅ Exploration completed!")
            elif choice == '2':
                self.print_structure_tree()
            elif choice == '3':
                self.print_detailed_content()
            elif choice == '4':
                filename = input("Enter filename (or press Enter for auto): ").strip()
                self.save_results_to_file(filename if filename else None)
            elif choice == '5':
                print("\n🔄 Refreshing data...")
                self.exploration_results["catalogs"] = {}
                self.explore_catalog_structure()
                print("✅ Data refreshed!")
            else:
                print("❌ Invalid choice. Please try again.")


def main():
    """Main entry point for the Polaris structure explorer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Explore Polaris catalog structure and content")
    parser.add_argument("--url", default="http://localhost:8181", help="Polaris URL")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--tree-only", action="store_true", help="Show only structure tree")
    parser.add_argument("--detailed", action="store_true", help="Show detailed content")
    
    args = parser.parse_args()
    
    # Initialize explorer
    explorer = PolarisExplorer(args.url)
    
    if args.interactive:
        # Interactive mode
        explorer.run_interactive_exploration()
    else:
        # Batch mode
        print("🚀 Starting Polaris structure exploration...")
        
        # Explore structure
        results = explorer.explore_catalog_structure()
        
        if results["errors"]:
            print("\n❌ Errors encountered:")
            for error in results["errors"]:
                print(f"   • {error}")
        
        # Show results based on options
        if args.tree_only:
            explorer.print_structure_tree()
        elif args.detailed:
            explorer.print_structure_tree()
            explorer.print_detailed_content()
        else:
            # Default: show tree
            explorer.print_structure_tree()
        
        # Save results if requested
        if args.output:
            explorer.save_results_to_file(args.output)
        
        print(f"\n🎉 Exploration completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()