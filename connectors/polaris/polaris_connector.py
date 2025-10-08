"""
Apache Polaris Source Connector for OpenMetadata

This module defines a custom OpenMetadata source connector for Apache Polaris,
capable of discovering catalogs, namespaces, and tables, and ingesting their
metadata into OpenMetadata.
"""

import logging
from typing import Iterable, Optional, List, Dict, Any
from dataclasses import dataclass

from .connector import PolarisConnector

# OpenMetadata imports
from metadata.generated.schema.entity.services.databaseService import DatabaseService
from metadata.generated.schema.entity.data.table import Column, DataType, TableData
from metadata.generated.schema.entity.data.database import Database
from metadata.generated.schema.entity.data.databaseSchema import DatabaseSchema
from metadata.generated.schema.type.tagLabel import TagLabel, LabelType, State, TagSource
from metadata.generated.schema.api.data.createDatabase import CreateDatabaseRequest
from metadata.generated.schema.api.data.createDatabaseSchema import CreateDatabaseSchemaRequest
from metadata.generated.schema.api.data.createTable import CreateTableRequest
from metadata.generated.schema.api.services.createDatabaseService import CreateDatabaseServiceRequest
from metadata.generated.schema.metadataIngestion.workflow import Source as WorkflowSource
from metadata.ingestion.api.models import Either, StackTraceError
from metadata.ingestion.api.steps import Source
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()

# Mapping from Iceberg/Polaris data types to OpenMetadata DataTypes
POLARIS_TO_OM_TYPE = {
    "string": DataType.STRING,
    "int": DataType.INT,
    "integer": DataType.INT,
    "long": DataType.BIGINT,
    "float": DataType.FLOAT,
    "double": DataType.DOUBLE,
    "boolean": DataType.BOOLEAN,
    "timestamp": DataType.TIMESTAMP,
    "timestamptz": DataType.TIMESTAMPZ,
    "date": DataType.DATE,
    "time": DataType.TIME,
    "binary": DataType.BINARY,
    "decimal": DataType.DECIMAL,
    "uuid": DataType.UUID,
    "list": DataType.ARRAY,
    "map": DataType.MAP,
    "struct": DataType.STRUCT,
}


@dataclass
class PolarisTable:
    """Represents a Polaris table with metadata"""
    catalog_name: str
    namespace_name: str
    table_name: str
    metadata: Dict[str, Any]
    schema_fields: List[Dict[str, Any]]


class PolarisSource(Source):
    """
    Custom OpenMetadata Source for Apache Polaris catalogs.

    Key Features:
    1. Catalog Discovery: Discovers available Polaris catalogs
    2. Namespace Discovery: Discovers namespaces within catalogs
    3. Table Discovery: Discovers tables within namespaces
    4. Schema Parsing: Extracts table schema from Iceberg metadata
    5. Metadata Ingestion: Creates databases, schemas, and tables in OpenMetadata
    """

    def __init__(self, config: WorkflowSource, metadata: OpenMetadata):
        """
        Initialize the Polaris connector with configuration from workflow YAML.
        
        Args:
            config: Workflow configuration
            metadata: OpenMetadata client instance
        """
        super().__init__()
        self.config = config
        self.metadata = metadata
        
        # Extract connection configuration
        service_connection_config = config.serviceConnection.root.config
        connection_options = service_connection_config.connectionOptions.root
        
        # Required connection parameters
        self.host = connection_options.get("host")
        self.port = int(connection_options.get("port", 8181))
        self.use_ssl = connection_options.get("use_ssl", "false").lower() == "true"
        
        # Authentication configuration
        self.auth_type = connection_options.get("auth_type", "oauth2")
        self.client_id = connection_options.get("client_id")
        self.client_secret = connection_options.get("client_secret")
        self.token_url = connection_options.get("token_url", "/v1/oauth/token")
        self.api_key = connection_options.get("api_key")
        self.username = connection_options.get("username")
        self.password = connection_options.get("password")
        
        # Optional configuration
        self.connection_timeout = int(connection_options.get("connection_timeout", 30))
        self.request_timeout = int(connection_options.get("request_timeout", 60))
        
        # Filter configuration
        catalog_filter_str = connection_options.get("catalog_filter", "")
        self.catalog_filter = [c.strip() for c in catalog_filter_str.split(",") if c.strip()] if catalog_filter_str else []
        
        namespace_filter_str = connection_options.get("namespace_filter", "")
        self.namespace_filter = [n.strip() for n in namespace_filter_str.split(",") if n.strip()] if namespace_filter_str else []
        
        # Tagging configuration
        self.default_tags = []
        default_tags_str = connection_options.get("default_tags", "")
        if default_tags_str:
            tag_fqns = [tag.strip() for tag in default_tags_str.split(",") if tag.strip()]
            for tag_fqn in tag_fqns:
                self.default_tags.append(TagLabel(
                    tagFQN=tag_fqn,
                    source=TagSource.Classification,
                    labelType=LabelType.Manual,
                    state=State.Confirmed
                ))
        
        self.service_name = self.config.serviceName
        
        logger.info(f"Polaris connector configuration:")
        logger.info(f"  Host: {self.host}:{self.port}")
        logger.info(f"  SSL: {self.use_ssl}")
        logger.info(f"  Auth Type: {self.auth_type}")
        logger.info(f"  Catalog Filter: {self.catalog_filter}")
        logger.info(f"  Namespace Filter: {self.namespace_filter}")
        logger.info(f"  Default Tags: {len(self.default_tags)}")
        
        # Initialize Polaris connector
        self.polaris_connector = PolarisConnector(
            host=self.host,
            port=self.port,
            use_ssl=self.use_ssl,
            auth_type=self.auth_type,
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_url=self.token_url,
            api_key=self.api_key,
            username=self.username,
            password=self.password,
            connection_timeout=self.connection_timeout,
            request_timeout=self.request_timeout
        )
        
        logger.info("Polaris connector initialized successfully")

    @classmethod
    def create(cls, config_dict: dict, metadata: OpenMetadata, pipeline_name: Optional[str] = None) -> "PolarisSource":
        """Factory method called by OpenMetadata to create an instance."""
        config = WorkflowSource.model_validate(config_dict)
        return cls(config, metadata)

    def prepare(self):
        """Preliminary checks before ingestion starts."""
        if not self.host:
            raise ValueError("host is a required field for Polaris connector")
        
        if self.auth_type == "oauth2" and (not self.client_id or not self.client_secret):
            raise ValueError("client_id and client_secret are required for OAuth2 authentication")
        
        if self.auth_type == "api_key" and not self.api_key:
            raise ValueError("api_key is required for API key authentication")
        
        if self.auth_type == "basic" and (not self.username or not self.password):
            raise ValueError("username and password are required for basic authentication")

    def _convert_iceberg_schema_to_columns(self, schema_fields: List[Dict[str, Any]]) -> List[Column]:
        """
        Convert Iceberg schema fields to OpenMetadata columns
        
        Args:
            schema_fields: List of Iceberg schema field dictionaries
            
        Returns:
            List of OpenMetadata Column objects
        """
        columns = []
        
        for field in schema_fields:
            field_name = field.get("name", "unknown")
            field_type = field.get("type", "string")
            field_required = field.get("required", True)
            field_doc = field.get("doc", "")
            
            # Handle complex types
            if isinstance(field_type, dict):
                if field_type.get("type") == "list":
                    om_type = DataType.ARRAY
                elif field_type.get("type") == "map":
                    om_type = DataType.MAP
                elif field_type.get("type") == "struct":
                    om_type = DataType.STRUCT
                else:
                    om_type = DataType.STRING
            else:
                # Handle primitive types
                om_type = POLARIS_TO_OM_TYPE.get(str(field_type).lower(), DataType.STRING)
            
            column = Column(
                name=field_name,
                dataType=om_type,
                description=field_doc if field_doc else None
            )
            columns.append(column)
        
        return columns

    def _discover_tables(self) -> List[PolarisTable]:
        """
        Discover all tables from Polaris catalogs
        
        Returns:
            List of PolarisTable objects
        """
        discovered_tables = []
        
        try:
            # Get all catalogs
            catalogs = self.polaris_connector.get_catalogs()
            logger.info(f"Discovered {len(catalogs)} catalogs")
            
            for catalog in catalogs:
                catalog_name = catalog.get("name")
                if not catalog_name:
                    continue
                
                # Apply catalog filter if specified
                if self.catalog_filter and catalog_name not in self.catalog_filter:
                    logger.debug(f"Skipping catalog {catalog_name} due to filter")
                    continue
                
                logger.info(f"Processing catalog: {catalog_name}")
                
                # Get namespaces in catalog
                namespaces = self.polaris_connector.get_namespaces(catalog_name)
                logger.info(f"Found {len(namespaces)} namespaces in catalog {catalog_name}")
                
                for namespace in namespaces:
                    namespace_name = None
                    if isinstance(namespace, dict):
                        namespace_name = namespace.get("namespace", namespace.get("name"))
                    elif isinstance(namespace, list):
                        namespace_name = ".".join(namespace)
                    else:
                        namespace_name = str(namespace)
                    
                    if not namespace_name:
                        continue
                    
                    # Apply namespace filter if specified
                    if self.namespace_filter and namespace_name not in self.namespace_filter:
                        logger.debug(f"Skipping namespace {namespace_name} due to filter")
                        continue
                    
                    logger.info(f"Processing namespace: {catalog_name}.{namespace_name}")
                    
                    # Get tables in namespace
                    tables = self.polaris_connector.get_tables(catalog_name, namespace_name)
                    logger.info(f"Found {len(tables)} tables in {catalog_name}.{namespace_name}")
                    
                    for table in tables:
                        table_name = table.get("name") if isinstance(table, dict) else str(table)
                        if not table_name:
                            continue
                        
                        logger.info(f"Processing table: {catalog_name}.{namespace_name}.{table_name}")
                        
                        # Get table metadata
                        table_metadata = self.polaris_connector.get_table_metadata(
                            catalog_name, namespace_name, table_name
                        )
                        
                        if not table_metadata:
                            logger.warning(f"Could not get metadata for table {catalog_name}.{namespace_name}.{table_name}")
                            continue
                        
                        # Extract schema fields from metadata
                        schema_fields = []
                        if "metadata" in table_metadata:
                            metadata_section = table_metadata["metadata"]
                            if "schema" in metadata_section and "fields" in metadata_section["schema"]:
                                schema_fields = metadata_section["schema"]["fields"]
                        
                        polaris_table = PolarisTable(
                            catalog_name=catalog_name,
                            namespace_name=namespace_name,
                            table_name=table_name,
                            metadata=table_metadata,
                            schema_fields=schema_fields
                        )
                        
                        discovered_tables.append(polaris_table)
        
        except Exception as e:
            logger.error(f"Error during table discovery: {str(e)}")
            raise
        
        logger.info(f"Discovered {len(discovered_tables)} tables total")
        return discovered_tables

    def next_record(self) -> Iterable[Either[dict]]:
        """
        Main generator that orchestrates the ingestion.
        """
        try:
            # Create or get the service
            service_entity = self._get_or_create_service()
            if not service_entity:
                raise Exception("Could not create or retrieve database service")
            
            # Discover tables
            discovered_tables = self._discover_tables()
            
            # Group tables by catalog (database) and namespace (schema)
            catalog_cache = {}
            schema_cache = {}
            
            for polaris_table in discovered_tables:
                try:
                    # Create or get database (catalog)
                    if polaris_table.catalog_name not in catalog_cache:
                        catalog_cache[polaris_table.catalog_name] = self._get_or_create_database(
                            service_entity, polaris_table.catalog_name
                        )
                    
                    database_entity = catalog_cache[polaris_table.catalog_name]
                    
                    # Create or get schema (namespace)
                    schema_key = f"{polaris_table.catalog_name}.{polaris_table.namespace_name}"
                    if schema_key not in schema_cache:
                        schema_cache[schema_key] = self._get_or_create_schema(
                            database_entity, polaris_table.namespace_name
                        )
                    
                    schema_entity = schema_cache[schema_key]
                    
                    # Convert schema fields to columns
                    columns = self._convert_iceberg_schema_to_columns(polaris_table.schema_fields)
                    
                    # Create table description
                    table_description = f"Polaris table from catalog {polaris_table.catalog_name}"
                    if polaris_table.metadata.get("metadata", {}).get("properties"):
                        properties = polaris_table.metadata["metadata"]["properties"]
                        if properties.get("comment"):
                            table_description = properties["comment"]
                    
                    # Create table request
                    create_table_request = CreateTableRequest(
                        name=polaris_table.table_name,
                        databaseSchema=schema_entity.fullyQualifiedName,
                        columns=columns,
                        tags=self.default_tags,
                        description=table_description,
                        tableType="Regular"
                    )
                    
                    # Create table in OpenMetadata
                    created_table = self.metadata.create_or_update(create_table_request)
                    logger.info(f"Table created/updated: {created_table.fullyQualifiedName.root}")
                    
                    self.status.scanned(created_table.fullyQualifiedName.root)
                
                except Exception as e:
                    error_msg = f"Could not process table {polaris_table.catalog_name}.{polaris_table.namespace_name}.{polaris_table.table_name}: {str(e)}"
                    logger.error(error_msg)
                    yield Either(left=StackTraceError(
                        name=f"{polaris_table.catalog_name}.{polaris_table.namespace_name}.{polaris_table.table_name}",
                        error=error_msg
                    ))
                    continue
        
        except Exception as e:
            yield Either(left=StackTraceError(
                name=self.service_name,
                error=f"Major error during Polaris ingestion: {str(e)}"
            ))

    def _iter(self) -> Iterable[Either]:
        """Required method that runs the next_record generator."""
        yield from self.next_record()

    def _get_or_create_service(self) -> DatabaseService:
        """Get or create the DatabaseService entity."""
        service = self.metadata.get_by_name(entity=DatabaseService, fqn=self.service_name)
        if service:
            return service
        
        service_request = CreateDatabaseServiceRequest(
            name=self.service_name,
            serviceType="CustomDatabase",
            connection=self.config.serviceConnection.root
        )
        return self.metadata.create_or_update(service_request)

    def _get_or_create_database(self, service: DatabaseService, catalog_name: str) -> Database:
        """Get or create the Database entity (represents a Polaris catalog)."""
        db_fqn = f"{service.fullyQualifiedName.root}.{catalog_name}"
        database = self.metadata.get_by_name(entity=Database, fqn=db_fqn)
        if database:
            return database
        
        db_request = CreateDatabaseRequest(
            name=catalog_name,
            service=service.fullyQualifiedName,
            description=f"Polaris catalog: {catalog_name}"
        )
        return self.metadata.create_or_update(db_request)

    def _get_or_create_schema(self, database: Database, namespace_name: str) -> DatabaseSchema:
        """Get or create the DatabaseSchema entity (represents a Polaris namespace)."""
        schema_fqn = f"{database.fullyQualifiedName.root}.{namespace_name}"
        schema = self.metadata.get_by_name(entity=DatabaseSchema, fqn=schema_fqn)
        if schema:
            return schema
        
        schema_request = CreateDatabaseSchemaRequest(
            name=namespace_name,
            database=database.fullyQualifiedName,
            description=f"Polaris namespace: {namespace_name}"
        )
        return self.metadata.create_or_update(schema_request)

    def test_connection(self) -> None:
        """Test the connection to Polaris."""
        if not self.polaris_connector.connect():
            raise Exception("Failed to connect to Polaris")
        
        logger.info("Polaris connection test successful")

    def close(self):
        """Close any open resources."""
        if self.polaris_connector:
            self.polaris_connector.close()