"""
Polaris Source Connector for OpenMetadata

Agent unifié pour l'ingestion de métadonnées depuis Apache Polaris.
Suit l'architecture simplifiée du connecteur Dremio.
"""

import logging
from typing import Iterable, Optional, List, Dict, Any
from dataclasses import dataclass

from .core.sync_engine import PolarisAutoDiscovery

# OpenMetadata imports
from metadata.generated.schema.entity.services.databaseService import DatabaseService
from metadata.generated.schema.entity.data.table import Column, DataType, Table
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

# Mapping Iceberg/Polaris types to OpenMetadata DataTypes
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
    """Represents a Polaris table with metadata."""
    catalog_name: str
    namespace_name: str
    table_name: str
    metadata: Dict[str, Any]
    schema_fields: List[Dict[str, Any]]


class PolarisSource(Source):
    """
    OpenMetadata Source for Apache Polaris catalogs.
    
    Fonctionnalités:
    1. Catalog Discovery: Découverte des catalogs Polaris
    2. Namespace Discovery: Découverte des namespaces
    3. Table Discovery: Découverte des tables Iceberg
    4. Schema Parsing: Extraction schema depuis metadata Iceberg
    5. Auto-Tagging: Tags automatiques configurables
    6. Multi-Auth: OAuth2, API Key, Basic Auth
    """

    def __init__(self, config: WorkflowSource, metadata: OpenMetadata):
        """Initialize Polaris connector with workflow configuration."""
        super().__init__()
        self.config = config
        self.metadata = metadata
        self.status = self.get_status()
        
        # Parse configuration from OpenMetadata
        self._parse_connection_config()
        
        # Initialize Polaris discovery engine
        self.discovery_engine = PolarisAutoDiscovery(
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
        
        logger.info(f"PolarisSource initialized for {self.host}:{self.port}")
        logger.info(f"Catalog filter: {self.catalog_filter}")
        logger.info(f"Namespace filter: {self.namespace_filter}")
    
    @classmethod
    def create(cls, config_dict: dict, metadata: OpenMetadata, pipeline_name: Optional[str] = None):
        """Factory method required by OpenMetadata framework."""
        config = WorkflowSource.parse_obj(config_dict)
        return cls(config, metadata)

    def _parse_connection_config(self):
        """
        Parse connection configuration from OpenMetadata connectionOptions.
        
        Supports both modern (__dict__['root']) and legacy (__root__) structures
        following the Dremio connector pattern for maximum robustness.
        
        Returns:
            None (sets instance variables)
        """
        service_conn = self.config.serviceConnection
        opts = {}
        
        # Modern structure (OpenMetadata 1.3+)
        if hasattr(service_conn, '__dict__') and 'root' in service_conn.__dict__:
            root = service_conn.__dict__['root']
            if hasattr(root, 'config') and hasattr(root.config, 'connectionOptions'):
                conn_opts = root.config.connectionOptions
                if hasattr(conn_opts, 'root') and isinstance(conn_opts.root, dict):
                    opts = conn_opts.root
                    logger.debug("✅ Using modern __dict__['root'] structure")
        # Fallback to legacy structure (OpenMetadata <1.3)
        elif hasattr(service_conn, '__root__'):
            root = service_conn.__root__
            if hasattr(root, 'config') and hasattr(root.config, 'connectionOptions'):
                conn_opts = root.config.connectionOptions
                if hasattr(conn_opts, 'root') and isinstance(conn_opts.root, dict):
                    opts = conn_opts.root
                    logger.debug("✅ Using legacy __root__ structure")
        else:
            logger.warning("⚠️  No connectionOptions found, using defaults")
        
        # Connection settings with robust type conversion
        self.host = opts.get("host", "localhost")
        
        port_str = opts.get("port", "8181")
        try:
            self.port = int(port_str)
        except (ValueError, TypeError):
            logger.warning(f"⚠️  Invalid port '{port_str}'. Defaulting to 8181.")
            self.port = 8181
        
        # Boolean conversion (Dremio pattern)
        self.use_ssl = opts.get("useSSL", "false").lower() == "true"
        self.classification_enabled = opts.get("classificationEnabled", "true").lower() == "true"
        
        self.service_name = self.config.serviceName
        
        # Authentication configuration
        self.auth_type = opts.get("authType", "oauth2")
        self.client_id = opts.get("clientId")
        self.client_secret = opts.get("clientSecret")
        self.token_url = opts.get("tokenUrl", "/v1/oauth/token")
        self.api_key = opts.get("apiKey")
        self.username = opts.get("username")
        self.password = opts.get("password")
        
        # Connection timeouts with robust conversion
        timeout_conn_str = opts.get("connectionTimeout", "30")
        try:
            self.connection_timeout = int(timeout_conn_str)
        except (ValueError, TypeError):
            logger.warning(f"⚠️  Invalid connectionTimeout '{timeout_conn_str}'. Defaulting to 30.")
            self.connection_timeout = 30
        
        timeout_req_str = opts.get("requestTimeout", "60")
        try:
            self.request_timeout = int(timeout_req_str)
        except (ValueError, TypeError):
            logger.warning(f"⚠️  Invalid requestTimeout '{timeout_req_str}'. Defaulting to 60.")
            self.request_timeout = 60
        
        # Filter configuration (lists)
        catalog_filter_str = opts.get("catalogFilter", "")
        self.catalog_filter = [c.strip() for c in catalog_filter_str.split(",") if c.strip()] if catalog_filter_str else []
        
        namespace_filter_str = opts.get("namespaceFilter", "")
        self.namespace_filter = [n.strip() for n in namespace_filter_str.split(",") if n.strip()] if namespace_filter_str else []
        
        # Default tags (list)
        default_tags_str = opts.get("defaultTags", "")
        self.default_tags_fqns = [tag.strip() for tag in default_tags_str.split(",") if tag.strip()]
        
        # Detailed logging (Dremio style)
        logger.info(f"📋 Found connectionOptions:")
        logger.info(f"   - Host: {self.host}:{self.port}")
        logger.info(f"   - SSL: {'enabled' if self.use_ssl else 'disabled'}")
        logger.info(f"   - Auth: {self.auth_type}")
        if self.auth_type == "oauth2":
            logger.info(f"   - Client ID: {self.client_id}")
        elif self.auth_type == "basic":
            logger.info(f"   - Username: {self.username}")
        logger.info(f"⏱️  Timeouts: connection={self.connection_timeout}s, request={self.request_timeout}s")
        logger.info(f"🔍 Filters:")
        logger.info(f"   - Catalogs: {self.catalog_filter or ['*']}")
        logger.info(f"   - Namespaces: {self.namespace_filter or ['*']}")
        logger.info(f"🏷️  Classification: {'enabled' if self.classification_enabled else 'disabled'}")
        if self.default_tags_fqns:
            logger.info(f"🏷️  Default tags: {', '.join(self.default_tags_fqns)}")

    def prepare(self):
        """Preliminary checks before ingestion starts."""
        if not self.host:
            raise ValueError("host is required for Polaris connector")
        
        if self.auth_type == "oauth2" and (not self.client_id or not self.client_secret):
            raise ValueError("clientId and clientSecret are required for OAuth2 authentication")
        
        if self.auth_type == "api_key" and not self.api_key:
            raise ValueError("apiKey is required for API key authentication")
        
        if self.auth_type == "basic" and (not self.username or not self.password):
            raise ValueError("username and password are required for basic authentication")
        
        # Test connection and authenticate
        if not self.discovery_engine.authenticate():
            raise ValueError("Polaris authentication failed")
        
        logger.info(f"✅ Preparing to ingest metadata from Polaris: {self.host}:{self.port}")

    def _convert_iceberg_schema_to_columns(self, schema_fields: List[Dict[str, Any]]) -> List[Column]:
        """
        Convert Iceberg schema fields to OpenMetadata columns.
        
        Args:
            schema_fields: List of Iceberg schema field dictionaries
        
        Returns:
            List of OpenMetadata Column objects
        """
        columns = []
        
        for field in schema_fields:
            field_name = field.get("name", "unknown")
            field_type = field.get("type", "string")
            field_doc = field.get("doc", "")
            
            # Handle complex types
            if isinstance(field_type, dict):
                type_name = field_type.get("type", "string")
                om_type = POLARIS_TO_OM_TYPE.get(type_name.lower(), DataType.STRING)
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
        Discover all tables from Polaris catalogs.
        
        Returns:
            List of PolarisTable objects
        """
        discovered_tables = []
        
        try:
            # Get all catalogs
            catalogs = self.discovery_engine.get_catalogs()
            logger.info(f"Discovered {len(catalogs)} catalogs")
            
            for catalog_name in catalogs:
                # Apply catalog filter
                if self.catalog_filter and catalog_name not in self.catalog_filter:
                    logger.debug(f"Skipping catalog {catalog_name} (filtered)")
                    continue
                
                logger.info(f"Processing catalog: {catalog_name}")
                
                # Get namespaces
                namespaces = self.discovery_engine.get_namespaces(catalog_name)
                logger.info(f"Found {len(namespaces)} namespaces in catalog {catalog_name}")
                
                for namespace_name in namespaces:
                    # Apply namespace filter
                    if self.namespace_filter and namespace_name not in self.namespace_filter:
                        logger.debug(f"Skipping namespace {namespace_name} (filtered)")
                        continue
                    
                    logger.info(f"Processing namespace: {catalog_name}.{namespace_name}")
                    
                    # Get tables
                    tables = self.discovery_engine.get_tables(catalog_name, namespace_name)
                    logger.info(f"Found {len(tables)} tables in {catalog_name}.{namespace_name}")
                    
                    for table_name in tables:
                        logger.info(f"Processing table: {catalog_name}.{namespace_name}.{table_name}")
                        
                        # Get table metadata
                        table_metadata = self.discovery_engine.get_table_metadata(
                            catalog_name, namespace_name, table_name
                        )
                        
                        if not table_metadata:
                            logger.warning(f"Could not get metadata for {catalog_name}.{namespace_name}.{table_name}")
                            continue
                        
                        # Extract schema fields
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
            
            logger.info(f"Total tables discovered: {len(discovered_tables)}")
            return discovered_tables
        
        except Exception as e:
            logger.error(f"Error during table discovery: {str(e)}")
            return []

    def _get_tags_for_table(self, table_name: str) -> List[TagLabel]:
        """Generate tags for a table based on classification rules."""
        if not self.classification_enabled:
            return []
        
        tags = []
        
        # Apply default tags
        for tag_fqn in self.default_tags_fqns:
            tags.append(TagLabel(
                tagFQN=tag_fqn,
                source=TagSource.Classification,
                labelType=LabelType.Manual,
                state=State.Confirmed
            ))
        
        return tags

    def next_record(self) -> Iterable[Either]:
        """Main generator that orchestrates the ingestion."""
        try:
            # Create or get service entity
            service_entity = self._get_or_create_service()
            if not service_entity:
                raise Exception("Service could not be created")
            
            # Discover all tables
            discovered_tables = self._discover_tables()
            
            # Cache for database and schema entities
            database_cache = {}
            schema_cache = {}
            
            # Process each table
            for polaris_table in discovered_tables:
                try:
                    # Get or create database (catalog)
                    if polaris_table.catalog_name not in database_cache:
                        database_cache[polaris_table.catalog_name] = self._get_or_create_database(
                            service_entity, polaris_table.catalog_name
                        )
                    database_entity = database_cache[polaris_table.catalog_name]
                    
                    # Get or create schema (namespace)
                    schema_key = f"{polaris_table.catalog_name}.{polaris_table.namespace_name}"
                    if schema_key not in schema_cache:
                        schema_cache[schema_key] = self._get_or_create_schema(
                            database_entity, polaris_table.namespace_name
                        )
                    schema_entity = schema_cache[schema_key]
                    
                    # Convert schema fields to columns
                    columns = self._convert_iceberg_schema_to_columns(polaris_table.schema_fields)
                    
                    # Get tags
                    tags = self._get_tags_for_table(polaris_table.table_name)
                    
                    # Create table request
                    create_table_request = CreateTableRequest(
                        name=polaris_table.table_name,
                        databaseSchema=schema_entity.fullyQualifiedName,
                        columns=columns,
                        tags=tags if tags else None,
                        description=f"Iceberg table from Polaris catalog {polaris_table.catalog_name}",
                        tableType="Iceberg"
                    )
                    
                    # Yield the create request
                    yield Either(right=create_table_request)
                    
                    logger.info(f"✅ Table yielded: {polaris_table.catalog_name}.{polaris_table.namespace_name}.{polaris_table.table_name}")
                    self.status.scanned(f"{polaris_table.catalog_name}.{polaris_table.namespace_name}.{polaris_table.table_name}")
                
                except Exception as e:
                    error_msg = f"Failed to process table {polaris_table.catalog_name}.{polaris_table.namespace_name}.{polaris_table.table_name}: {str(e)}"
                    logger.error(error_msg)
                    yield Either(left=StackTraceError(name=polaris_table.table_name, error=error_msg))
                    continue
        
        except Exception as e:
            error_msg = f"Major error during Polaris ingestion: {str(e)}"
            logger.error(error_msg)
            yield Either(left=StackTraceError(name="Polaris", error=error_msg))

    def _iter(self) -> Iterable[Either]:
        """Required method that runs the next_record generator."""
        yield from self.next_record()

    def _get_or_create_service(self) -> DatabaseService:
        """Get or create the DatabaseService entity."""
        try:
            service = self.metadata.get_by_name(entity=DatabaseService, fqn=self.service_name)
            if service:
                logger.info(f"✅ Service found: {self.service_name}")
                return service
        except Exception as e:
            logger.debug(f"Service not found, will create: {e}")
        
        logger.info(f"Creating new service: {self.service_name}")
        service_request = CreateDatabaseServiceRequest(
            name=self.service_name,
            serviceType="CustomDatabase",
            connection=self.config.serviceConnection
        )
        return self.metadata.create_or_update(service_request)

    def _get_or_create_database(self, service: DatabaseService, catalog_name: str) -> Database:
        """Get or create the Database entity (Polaris catalog)."""
        db_fqn = f"{service.fullyQualifiedName.root}.{catalog_name}"
        database = self.metadata.get_by_name(entity=Database, fqn=db_fqn)
        if database:
            return database
        
        db_request = CreateDatabaseRequest(
            name=catalog_name,
            service=service.fullyQualifiedName
        )
        return self.metadata.create_or_update(db_request)

    def _get_or_create_schema(self, database: Database, namespace_name: str) -> DatabaseSchema:
        """Get or create the DatabaseSchema entity (Polaris namespace)."""
        schema_fqn = f"{database.fullyQualifiedName.root}.{namespace_name}"
        schema = self.metadata.get_by_name(entity=DatabaseSchema, fqn=schema_fqn)
        if schema:
            return schema
        
        schema_request = CreateDatabaseSchemaRequest(
            name=namespace_name,
            database=database.fullyQualifiedName
        )
        return self.metadata.create_or_update(schema_request)

    def test_connection(self) -> None:
        """Test the connection to the Polaris source."""
        if not self.discovery_engine.authenticate():
            raise Exception("Polaris connection test failed")
        logger.info("✅ Polaris connection test successful")

    def close(self):
        """Close any open resources."""
        if self.discovery_engine:
            self.discovery_engine.close()
        logger.info("PolarisSource closed")
