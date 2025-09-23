"""
OpenMetadata source implementation for Apache Polaris catalog
"""

import logging
import traceback
from typing import Iterable, List, Optional, Dict, Any
from pydantic import BaseModel

from .client import PolarisClient, PolarisApiException
from .connection import PolarisConnection
from .models import (
    PolarisCatalog, 
    PolarisNamespace, 
    PolarisTable, 
    PolarisColumn,
    PolarisMetrics
)


logger = logging.getLogger(__name__)


class CreateDatabaseRequest(BaseModel):
    """Create database request model"""
    name: str
    displayName: str
    description: str
    service: str


class CreateDatabaseSchemaRequest(BaseModel):
    """Create database schema request model"""
    name: str
    displayName: str
    description: str
    database: str


class CreateTableRequest(BaseModel):
    """Create table request model"""
    name: str
    displayName: str
    description: str
    tableType: str
    columns: List[Dict]
    databaseSchema: str
    tableConstraints: Optional[List[Dict]] = None
    tablePartition: Optional[Dict] = None


class Column(BaseModel):
    """Column model"""
    name: str
    displayName: str
    dataType: str
    dataTypeDisplay: str
    description: Optional[str] = None
    constraint: Optional[str] = None
    ordinalPosition: int


class WorkflowSource(BaseModel):
    """Workflow source model"""
    serviceName: str
    serviceConnection: Dict
    sourceConfig: Dict


from enum import Enum


class DataType(str, Enum):
    """Data type enumeration"""
    STRING = "STRING"
    BIGINT = "BIGINT"
    INT = "INT"
    DOUBLE = "DOUBLE"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    TIMESTAMP = "TIMESTAMP"
    BINARY = "BINARY"
    DECIMAL = "DECIMAL"
    UUID = "UUID"


class InvalidSourceException(Exception):
    """Exception for invalid source configuration"""
    pass


class PolarisSource:
    """
    OpenMetadata source for Apache Polaris catalog
    
    This source discovers catalogs, namespaces, and tables from Polaris
    and converts them to OpenMetadata entities.
    """
    
    def __init__(self, config: WorkflowSource, metadata_config):
        """
        Initialize Polaris source
        
        Args:
            config: Workflow source configuration
            metadata_config: OpenMetadata configuration
        """
        self.config = config
        self.source_config: PolarisConnection = config.serviceConnection["config"]
        self.metadata_config = metadata_config
        
        # Initialize Polaris client
        try:
            self.client = PolarisClient(self.source_config)
            logger.info("Polaris client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Polaris client: {str(e)}")
            raise InvalidSourceException(f"Failed to connect to Polaris: {str(e)}")
        
        # Metrics tracking
        self.metrics = PolarisMetrics()
        self.discovery_start_time = None
        
        # Context simulation for standalone operation
        self.context = type('Context', (), {})()
        self.context.database_service = type('Service', (), {'fullyQualifiedName': config.serviceName})()
        self.context.database = type('Database', (), {'name': type('Name', (), {'__root__': ''})()})()
        self.context.database_schema = type('Schema', (), {'name': type('Name', (), {'__root__': ''})()})()
    
    @classmethod
    def create(cls, config_dict: dict, metadata_config):
        """
        Create Polaris source instance
        
        Args:
            config_dict: Configuration dictionary
            metadata_config: OpenMetadata configuration
            
        Returns:
            PolarisSource instance
        """
        config = WorkflowSource(**config_dict)
        return cls(config, metadata_config)
    
    def get_database_names(self) -> Iterable[str]:
        """
        Get list of database names (catalogs in Polaris)
        
        Yields:
            Database names
        """
        logger.info("Discovering Polaris catalogs...")
        
        try:
            catalogs = self.client.get_catalogs()
            
            for catalog_data in catalogs:
                catalog_name = catalog_data.get("name")
                if catalog_name:
                    # Apply catalog filter if configured
                    if self.source_config.catalogFilter:
                        import re
                        if not re.match(self.source_config.catalogFilter, catalog_name):
                            logger.debug(f"Skipping catalog {catalog_name} due to filter")
                            continue
                    
                    logger.info(f"Found catalog: {catalog_name}")
                    self.metrics.total_catalogs += 1
                    yield catalog_name
                    
        except PolarisApiException as e:
            error_msg = f"Failed to get catalogs: {str(e)}"
            logger.error(error_msg)
            self.metrics.discovery_errors.append(error_msg)
    
    def get_database_schema_names(self) -> Iterable[str]:
        """
        Get list of database schema names (namespaces in Polaris)
        
        Yields:
            Schema names in format "catalog.namespace"
        """
        logger.info("Discovering Polaris namespaces...")
        
        for catalog_name in self.get_database_names():
            try:
                namespaces = self.client.get_namespaces(catalog_name)
                
                for namespace_data in namespaces:
                    namespace_name = namespace_data.get("namespace", [])
                    if namespace_name and isinstance(namespace_name, list):
                        # Polaris returns namespace as array, join with dots
                        namespace_str = ".".join(namespace_name)
                        
                        # Apply namespace filter if configured
                        if self.source_config.namespaceFilter:
                            import re
                            if not re.match(self.source_config.namespaceFilter, namespace_str):
                                logger.debug(f"Skipping namespace {namespace_str} due to filter")
                                continue
                        
                        schema_fqn = f"{catalog_name}.{namespace_str}"
                        logger.info(f"Found namespace: {schema_fqn}")
                        self.metrics.total_namespaces += 1
                        yield schema_fqn
                        
            except PolarisApiException as e:
                error_msg = f"Failed to get namespaces for catalog {catalog_name}: {str(e)}"
                logger.error(error_msg)
                self.metrics.discovery_errors.append(error_msg)
    
    def get_tables_name_and_type(self) -> Optional[Iterable[tuple]]:
        """
        Get list of table names and types
        
        Yields:
            Tuples of (table_name, table_type)
        """
        logger.info("Discovering Polaris tables...")
        
        for schema_fqn in self.get_database_schema_names():
            try:
                # Parse schema FQN
                parts = schema_fqn.split(".", 1)
                if len(parts) != 2:
                    logger.warning(f"Invalid schema FQN format: {schema_fqn}")
                    continue
                
                catalog_name, namespace_name = parts
                
                tables = self.client.get_tables(catalog_name, namespace_name)
                
                for table_data in tables:
                    table_name = table_data.get("name")
                    if table_name:
                        # Apply table filter if configured
                        if self.source_config.tableFilter:
                            import re
                            if not re.match(self.source_config.tableFilter, table_name):
                                logger.debug(f"Skipping table {table_name} due to filter")
                                continue
                        
                        # Polaris tables are typically Iceberg tables
                        table_type = "Regular"
                        
                        table_fqn = f"{schema_fqn}.{table_name}"
                        logger.info(f"Found table: {table_fqn}")
                        self.metrics.total_tables += 1
                        yield table_name, table_type
                        
            except PolarisApiException as e:
                error_msg = f"Failed to get tables for schema {schema_fqn}: {str(e)}"
                logger.error(error_msg)
                self.metrics.discovery_errors.append(error_msg)
    
    def yield_database(self, database_name: str) -> Iterable[CreateDatabaseRequest]:
        """
        Yield database entity for a catalog
        
        Args:
            database_name: Name of the database (catalog)
            
        Yields:
            CreateDatabaseRequest for the database
        """
        try:
            logger.info(f"Processing database: {database_name}")
            
            # Create database entity from Polaris catalog
            yield CreateDatabaseRequest(
                name=database_name,
                displayName=database_name,
                description=f"Polaris catalog: {database_name}",
                service=self.context.database_service.fullyQualifiedName,
            )
            
        except Exception as e:
            logger.error(f"Failed to yield database {database_name}: {str(e)}")
            logger.debug(traceback.format_exc())
    
    def yield_database_schema(self, schema_name: str) -> Iterable[CreateDatabaseSchemaRequest]:
        """
        Yield database schema entity for a namespace
        
        Args:
            schema_name: Name of the schema (catalog.namespace)
            
        Yields:
            CreateDatabaseSchemaRequest for the schema
        """
        try:
            logger.info(f"Processing schema: {schema_name}")
            
            # Parse schema name
            parts = schema_name.split(".", 1)
            if len(parts) != 2:
                logger.warning(f"Invalid schema name format: {schema_name}")
                return
            
            catalog_name, namespace_name = parts
            
            yield CreateDatabaseSchemaRequest(
                name=namespace_name,
                displayName=namespace_name,
                description=f"Polaris namespace: {namespace_name} in catalog {catalog_name}",
                database=f"{self.config.serviceName}.{catalog_name}",
            )
            
        except Exception as e:
            logger.error(f"Failed to yield schema {schema_name}: {str(e)}")
            logger.debug(traceback.format_exc())
    
    def yield_table(self, table_name_and_type: tuple) -> Iterable[CreateTableRequest]:
        """
        Yield table entity
        
        Args:
            table_name_and_type: Tuple of (table_name, table_type)
            
        Yields:
            CreateTableRequest for the table
        """
        try:
            table_name, table_type = table_name_and_type
            
            # Get current context (simulate database and schema context)
            # In a real implementation, this would come from the OpenMetadata workflow
            database_name = "unknown_catalog"  # This should be set by the workflow
            schema_name = "unknown_namespace"   # This should be set by the workflow
            
            logger.info(f"Processing table: {database_name}.{schema_name}.{table_name}")
            
            # Get detailed table metadata from Polaris
            table_metadata = self.client.get_table_metadata(database_name, schema_name, table_name)
            
            # Convert Polaris table to OpenMetadata table
            polaris_table = self._convert_to_polaris_table(
                table_metadata, database_name, schema_name, table_name
            )
            
            # Extract columns
            columns = self._extract_columns(polaris_table)
            
            yield CreateTableRequest(
                name=table_name,
                displayName=table_name,
                description=polaris_table.properties.get("comment", f"Polaris table: {table_name}"),
                tableType=table_type,
                columns=columns,
                databaseSchema=f"{self.config.serviceName}.{database_name}.{schema_name}",
                tableConstraints=self._extract_constraints(polaris_table),
                tablePartition=self._extract_partition_info(polaris_table),
            )
            
        except Exception as e:
            logger.error(f"Failed to yield table {table_name_and_type}: {str(e)}")
            logger.debug(traceback.format_exc())
    
    def _convert_to_polaris_table(self, metadata: Dict[str, Any], catalog_name: str, 
                                 namespace_name: str, table_name: str) -> PolarisTable:
        """
        Convert Polaris API response to PolarisTable model
        
        Args:
            metadata: Table metadata from Polaris API
            catalog_name: Catalog name
            namespace_name: Namespace name
            table_name: Table name
            
        Returns:
            PolarisTable instance
        """
        # Extract schema information
        schema_data = metadata.get("metadata", {}).get("schema", {})
        fields = schema_data.get("fields", [])
        
        # Convert fields to columns
        columns = []
        for field in fields:
            column = PolarisColumn(
                id=field.get("id", 0),
                name=field.get("name", ""),
                type=field.get("type", "string"),
                required=field.get("required", False),
                comment=field.get("doc")
            )
            columns.append(column)
        
        # Extract properties
        properties = metadata.get("metadata", {}).get("properties", {})
        
        return PolarisTable(
            name=table_name,
            catalog_name=catalog_name,
            namespace_name=namespace_name,
            schema=schema_data,
            columns=columns,
            properties=properties,
            table_type="TABLE"
        )
    
    def _extract_columns(self, polaris_table: PolarisTable) -> List[Column]:
        """
        Extract OpenMetadata columns from Polaris table
        
        Args:
            polaris_table: PolarisTable instance
            
        Returns:
            List of OpenMetadata Column objects
        """
        columns = []
        
        for polaris_column in polaris_table.columns:
            # Map Polaris data types to OpenMetadata data types
            data_type = self._map_data_type(polaris_column.type)
            
            column = Column(
                name=polaris_column.name,
                displayName=polaris_column.name,
                dataType=data_type,
                dataTypeDisplay=polaris_column.type,
                description=polaris_column.comment,
                constraint="NOT_NULL" if polaris_column.required else None,
                ordinalPosition=polaris_column.id,
            )
            
            columns.append(column)
        
        return columns
    
    def _map_data_type(self, polaris_type: str) -> DataType:
        """
        Map Polaris data type to OpenMetadata data type
        
        Args:
            polaris_type: Polaris data type string
            
        Returns:
            OpenMetadata DataType
        """
        type_mapping = {
            "string": DataType.STRING,
            "long": DataType.BIGINT,
            "integer": DataType.INT,
            "double": DataType.DOUBLE,
            "float": DataType.FLOAT,
            "boolean": DataType.BOOLEAN,
            "date": DataType.DATE,
            "timestamp": DataType.TIMESTAMP,
            "binary": DataType.BINARY,
            "decimal": DataType.DECIMAL,
            "uuid": DataType.UUID,
        }
        
        # Handle complex types with parentheses (e.g., "decimal(10,2)")
        base_type = polaris_type.split("(")[0].lower()
        
        return type_mapping.get(base_type, DataType.STRING)
    
    def _extract_constraints(self, polaris_table: PolarisTable) -> Optional[List[Dict]]:
        """
        Extract table constraints from Polaris table
        
        Args:
            polaris_table: PolarisTable instance
            
        Returns:
            List of constraint dictionaries or None
        """
        # Polaris/Iceberg doesn't have traditional constraints like primary keys
        # This would be implemented based on table properties or metadata
        return None
    
    def _extract_partition_info(self, polaris_table: PolarisTable) -> Optional[Dict]:
        """
        Extract partitioning information from Polaris table
        
        Args:
            polaris_table: PolarisTable instance
            
        Returns:
            Partition information dictionary or None
        """
        if polaris_table.partition_spec:
            return {
                "columns": [field.get("name") for field in polaris_table.partition_spec.fields],
                "intervalType": "COLUMN-VALUE"
            }
        return None
    
    def test_connection(self) -> None:
        """Test connection to Polaris"""
        try:
            success = self.client.test_connection()
            if not success:
                raise Exception("Connection test failed")
                
        except Exception as e:
            logger.error(f"Test connection failed: {str(e)}")
            raise e
    
    def close(self):
        """Close the source and cleanup resources"""
        try:
            if hasattr(self, 'client') and self.client:
                self.client.close()
                logger.info("Polaris client closed successfully")
        except Exception as e:
            logger.error(f"Error closing Polaris client: {str(e)}")