"""
OpenMetadata Client

Handles all interactions with the OpenMetadata API for service and        response = requests.post(
            f"{self.base_ur        response = requests.post(
            f"{self.base_ur        response = requests.post(
            f"{self.base_url}/api/v1/databaseSch        response = requests.post(
            f"{self.base_url}/api/v1/tables",
            headers=self.headers,
            json=table_config,
            timeout=self.timeout
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Created table '{table_def.name}'")
            return True
        elif response.status_code == 409:
            print(f"✅ Table '{table_def.name}' already exists")
            return True
        else:
            print(f"❌ Failed to create table '{table_def.name}': {response.status_code}")
            print(f"Response: {response.text}")
            return False      headers=self.headers,
            json=schema_config,
            timeout=self.timeout
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Created schema '{schema_name}'")
            return True
        elif response.status_code == 409:
            print(f"✅ Schema '{schema_name}' already exists")
            return True
        else:
            print(f"❌ Failed to create schema '{schema_name}': {response.status_code}")
            print(f"Response: {response.text}")
            return Falsebases",
            headers=self.headers,
            json=database_config,
            timeout=self.timeout
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Created database '{database_name}'")
            return True
        elif response.status_code == 409:
            print(f"✅ Database '{database_name}' already exists")
            return True
        else:
            print(f"❌ Failed to create database '{database_name}': {response.status_code}")
            print(f"Response: {response.text}")
            return Falseices/databaseServices",
            headers=self.headers,
            json=service_config,
            timeout=self.timeout
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Created database service '{service_name}'")
            return True
        elif response.status_code == 409:
            print(f"✅ Database service '{service_name}' already exists")
            return True
        else:
            print(f"❌ Failed to create service '{service_name}': {response.status_code}")
            print(f"Response: {response.text}")
            return Falseent.
"""

import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from ..utils.config_manager import IngestionConfig


@dataclass
class TableColumn:
    """Table column definition."""
    name: str
    data_type: str
    description: str = ""
    data_length: Optional[int] = None


@dataclass
class TableDefinition:
    """Complete table definition for creation."""
    name: str
    display_name: str
    description: str
    database_schema_fqn: str
    columns: List[TableColumn]
    table_type: str = "Regular"
    source_url: Optional[str] = None
    tags: Optional[List[Dict[str, str]]] = None
    extension: Optional[Dict[str, Any]] = None


class OpenMetadataClient:
    """Client for interacting with OpenMetadata API."""
    
    def __init__(self, config: IngestionConfig, timeout: int = 30):
        """
        Initialize OpenMetadata client.
        
        Args:
            config: Ingestion configuration
            timeout: Request timeout in seconds
        """
        self.config = config
        self.timeout = timeout
        self.base_url = config.openmetadata.host_port.replace('/api', '')
        self.headers = {
            'Authorization': f'Bearer {config.openmetadata.jwt_token}',
            'Content-Type': 'application/json'
        }
    
    def create_database_service(self, service_name: str, description: str) -> bool:
        """
        Create or verify database service exists.
        
        Args:
            service_name: Name of the service
            description: Service description
            
        Returns:
            bool: True if service exists or was created successfully
        """
        # Check if service exists
        response = requests.get(
            f"{self.base_url}/api/v1/services/databaseServices/name/{service_name}",
            headers=self.headers,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            print(f"✅ Database service '{service_name}' already exists")
            return True
        
        # Create new service
        service_config = {
            "name": service_name,
            "displayName": service_name.replace('-', ' ').title(),
            "description": description,
            "serviceType": "CustomDatabase",
            "connection": {
                "config": {
                    "type": "CustomDatabase",
                    "sourcePythonClass": "metadata.ingestion.source.database.customdatabase.metadata.CustomDatabaseSource",
                    "connectionOptions": {
                        "host": self.config.polaris.host,
                        "port": self.config.polaris.port
                    }
                }
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/services/databaseServices",
            headers=self.headers,
            json=service_config,
            timeout=self.timeout
        )
        
        if response.status_code == 201:
            print(f"✅ Created database service '{service_name}'")
            return True
        else:
            print(f"❌ Failed to create service '{service_name}': {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def create_database(self, database_name: str, description: str, service_name: str) -> bool:
        """
        Create or verify database exists.
        
        Args:
            database_name: Name of the database
            description: Database description
            service_name: Name of the parent service
            
        Returns:
            bool: True if database exists or was created successfully
        """
        # Check if database exists
        response = requests.get(
            f"{self.base_url}/api/v1/databases/name/{database_name}",
            headers=self.headers,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            print(f"✅ Database '{database_name}' already exists")
            return True
        
        # Create new database
        database_config = {
            "name": database_name,
            "displayName": database_name.replace('_', ' ').title(),
            "description": description,
            "service": service_name
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/databases",
            headers=self.headers,
            json=database_config,
            timeout=self.timeout
        )
        
        if response.status_code == 201:
            print(f"✅ Created database '{database_name}'")
            return True
        else:
            print(f"❌ Failed to create database '{database_name}': {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def create_schema(self, schema_name: str, database_fqn: str) -> bool:
        """
        Create or verify database schema exists.
        
        Args:
            schema_name: Name of the schema
            database_fqn: Fully qualified name of the parent database
            
        Returns:
            bool: True if schema exists or was created successfully
        """
        schema_fqn = f"{database_fqn}.{schema_name}"
        
        # Check if schema exists
        response = requests.get(
            f"{self.base_url}/api/v1/databaseSchemas/name/{schema_fqn}",
            headers=self.headers,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            print(f"✅ Schema '{schema_name}' already exists")
            return True
        
        # Create new schema
        schema_config = {
            "name": schema_name,
            "displayName": schema_name.replace('_', ' ').title(),
            "database": database_fqn
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/databaseSchemas",
            headers=self.headers,
            json=schema_config,
            timeout=self.timeout
        )
        
        if response.status_code == 201:
            print(f"✅ Created schema '{schema_name}'")
            return True
        else:
            print(f"❌ Failed to create schema '{schema_name}': {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def create_table(self, table_def: TableDefinition) -> bool:
        """
        Create or verify table exists.
        
        Args:
            table_def: Complete table definition
            
        Returns:
            bool: True if table exists or was created successfully
        """
        table_fqn = f"{table_def.database_schema_fqn}.{table_def.name}"
        
        # Check if table exists
        response = requests.get(
            f"{self.base_url}/api/v1/tables/name/{table_fqn}",
            headers=self.headers,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            print(f"✅ Table '{table_def.name}' already exists")
            return True
        
        # Prepare columns
        columns = []
        for col in table_def.columns:
            column_config = {
                "name": col.name,
                "dataType": col.data_type,
                "description": col.description
            }
            if col.data_length:
                column_config["dataLength"] = col.data_length
            columns.append(column_config)
        
        # Create table configuration
        table_config = {
            "name": table_def.name,
            "displayName": table_def.display_name,
            "description": table_def.description,
            "tableType": table_def.table_type,
            "columns": columns,
            "databaseSchema": table_def.database_schema_fqn
        }
        
        # Add optional fields (excluding extension which contains unsupported fields)
        if table_def.source_url:
            table_config["sourceUrl"] = table_def.source_url
        
        if table_def.tags:
            table_config["tags"] = table_def.tags
        
        response = requests.post(
            f"{self.base_url}/api/v1/tables",
            headers=self.headers,
            json=table_config,
            timeout=self.timeout
        )
        
        if response.status_code == 201:
            print(f"✅ Created table '{table_def.name}'")
            return True
        else:
            print(f"❌ Failed to create table '{table_def.name}': {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def list_databases(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all databases, optionally filtered by service.
        
        Args:
            service_name: Optional service name filter
            
        Returns:
            List[Dict[str, Any]]: List of database information
        """
        response = requests.get(
            f"{self.base_url}/api/v1/databases",
            headers=self.headers,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            databases = response.json().get('data', [])
            
            if service_name:
                return [
                    db for db in databases 
                    if db.get('service', {}).get('name') == service_name
                ]
            return databases
        else:
            print(f"❌ Failed to list databases: {response.status_code}")
            return []
    
    def list_tables(self, database_fqn: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all tables, optionally filtered by database.
        
        Args:
            database_fqn: Optional database FQN filter
            
        Returns:
            List[Dict[str, Any]]: List of table information
        """
        response = requests.get(
            f"{self.base_url}/api/v1/tables",
            headers=self.headers,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            tables = response.json().get('data', [])
            
            if database_fqn:
                return [
                    table for table in tables 
                    if table.get('fullyQualifiedName', '').startswith(database_fqn)
                ]
            return tables
        else:
            print(f"❌ Failed to list tables: {response.status_code}")
            return []
    
    def get_table_details(self, table_fqn: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a table.
        
        Args:
            table_fqn: Fully qualified table name
            
        Returns:
            Optional[Dict[str, Any]]: Table details or None if not found
        """
        response = requests.get(
            f"{self.base_url}/api/v1/tables/name/{table_fqn}",
            headers=self.headers,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None