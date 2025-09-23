"""
Data models for Polaris entities and OpenMetadata integration
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class PolarisEntityType(str, Enum):
    """Types of entities in Polaris"""
    CATALOG = "catalog"
    NAMESPACE = "namespace"
    TABLE = "table"


class ColumnType(str, Enum):
    """Supported column data types"""
    STRING = "string"
    INTEGER = "integer"
    LONG = "long"
    DOUBLE = "double"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    BINARY = "binary"
    DECIMAL = "decimal"
    UUID = "uuid"
    FIXED = "fixed"
    LIST = "list"
    MAP = "map"
    STRUCT = "struct"


class PolarisColumn(BaseModel):
    """Represents a table column in Polaris"""
    
    id: int = Field(..., description="Column ID")
    name: str = Field(..., description="Column name")
    type: str = Field(..., description="Column data type")
    required: bool = Field(default=False, description="Whether column is required")
    comment: Optional[str] = Field(default=None, description="Column comment/description")
    
    # Additional metadata
    default_value: Optional[Any] = Field(default=None, description="Default value")
    precision: Optional[int] = Field(default=None, description="Decimal precision")
    scale: Optional[int] = Field(default=None, description="Decimal scale")
    length: Optional[int] = Field(default=None, description="String/binary length")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "customer_id",
                "type": "long",
                "required": True,
                "comment": "Unique customer identifier"
            }
        }


class PolarisPartitionSpec(BaseModel):
    """Represents table partitioning specification"""
    
    spec_id: int = Field(..., description="Partition spec ID")
    fields: List[Dict[str, Any]] = Field(default_factory=list, description="Partition fields")
    
    class Config:
        schema_extra = {
            "example": {
                "spec_id": 0,
                "fields": [
                    {
                        "source-id": 1,
                        "field-id": 1000,
                        "name": "year",
                        "transform": "year"
                    }
                ]
            }
        }


class PolarisSortOrder(BaseModel):
    """Represents table sort order specification"""
    
    order_id: int = Field(..., description="Sort order ID")
    fields: List[Dict[str, Any]] = Field(default_factory=list, description="Sort fields")
    
    class Config:
        schema_extra = {
            "example": {
                "order_id": 1,
                "fields": [
                    {
                        "source-id": 2,
                        "direction": "asc",
                        "null-order": "nulls-first"
                    }
                ]
            }
        }


class PolarisSnapshot(BaseModel):
    """Represents a table snapshot"""
    
    snapshot_id: int = Field(..., description="Snapshot ID")
    timestamp_ms: int = Field(..., description="Snapshot timestamp in milliseconds")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Snapshot summary")
    manifest_list: Optional[str] = Field(default=None, description="Manifest list location")
    schema_id: Optional[int] = Field(default=None, description="Schema ID")
    
    class Config:
        schema_extra = {
            "example": {
                "snapshot_id": 123456789,
                "timestamp_ms": 1634567890000,
                "summary": {
                    "operation": "append",
                    "spark.app.id": "local-1634567890123"
                },
                "schema_id": 1
            }
        }


class PolarisTable(BaseModel):
    """Represents a table in Polaris catalog"""
    
    # Basic information
    name: str = Field(..., description="Table name")
    catalog_name: str = Field(..., description="Catalog name")
    namespace_name: str = Field(..., description="Namespace name")
    
    # Metadata
    metadata_location: Optional[str] = Field(default=None, description="Table metadata location")
    table_type: str = Field(default="TABLE", description="Table type")
    format_version: int = Field(default=2, description="Iceberg format version")
    
    # Schema and structure
    schema: Dict[str, Any] = Field(default_factory=dict, description="Table schema")
    columns: List[PolarisColumn] = Field(default_factory=list, description="Table columns")
    
    # Partitioning and sorting
    partition_spec: Optional[PolarisPartitionSpec] = Field(default=None, description="Partition specification")
    sort_orders: List[PolarisSortOrder] = Field(default_factory=list, description="Sort orders")
    
    # Snapshots
    current_snapshot_id: Optional[int] = Field(default=None, description="Current snapshot ID")
    snapshots: List[PolarisSnapshot] = Field(default_factory=list, description="Table snapshots")
    
    # Properties
    properties: Dict[str, str] = Field(default_factory=dict, description="Table properties")
    
    # Timestamps
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    @property
    def fully_qualified_name(self) -> str:
        """Get fully qualified table name"""
        return f"{self.catalog_name}.{self.namespace_name}.{self.name}"
    
    class Config:
        schema_extra = {
            "example": {
                "name": "customers",
                "catalog_name": "main",
                "namespace_name": "sales",
                "table_type": "TABLE",
                "format_version": 2,
                "columns": [
                    {
                        "id": 1,
                        "name": "customer_id",
                        "type": "long",
                        "required": True
                    }
                ],
                "properties": {
                    "owner": "data-team",
                    "created-by": "spark-3.2.0"
                }
            }
        }


class PolarisNamespace(BaseModel):
    """Represents a namespace in Polaris catalog"""
    
    name: str = Field(..., description="Namespace name")
    catalog_name: str = Field(..., description="Catalog name")
    properties: Dict[str, str] = Field(default_factory=dict, description="Namespace properties")
    
    # Metadata
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    @property
    def fully_qualified_name(self) -> str:
        """Get fully qualified namespace name"""
        return f"{self.catalog_name}.{self.name}"
    
    class Config:
        schema_extra = {
            "example": {
                "name": "sales",
                "catalog_name": "main",
                "properties": {
                    "owner": "sales-team",
                    "description": "Sales data namespace"
                }
            }
        }


class PolarisCatalog(BaseModel):
    """Represents a catalog in Polaris"""
    
    name: str = Field(..., description="Catalog name")
    type: str = Field(default="iceberg", description="Catalog type")
    properties: Dict[str, str] = Field(default_factory=dict, description="Catalog properties")
    
    # Metadata
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "main",
                "type": "iceberg",
                "properties": {
                    "warehouse": "s3://my-bucket/warehouse",
                    "owner": "data-platform-team"
                }
            }
        }


class PolarisMetrics(BaseModel):
    """Metrics and statistics for Polaris entities"""
    
    total_catalogs: int = Field(default=0, description="Total number of catalogs")
    total_namespaces: int = Field(default=0, description="Total number of namespaces")
    total_tables: int = Field(default=0, description="Total number of tables")
    
    # Performance metrics
    discovery_duration_ms: int = Field(default=0, description="Discovery duration in milliseconds")
    last_discovery_time: Optional[datetime] = Field(default=None, description="Last discovery time")
    
    # Error tracking
    discovery_errors: List[str] = Field(default_factory=list, description="Discovery errors")
    
    class Config:
        schema_extra = {
            "example": {
                "total_catalogs": 3,
                "total_namespaces": 15,
                "total_tables": 127,
                "discovery_duration_ms": 2500,
                "discovery_errors": []
            }
        }


class OpenMetadataEntity(BaseModel):
    """Base class for OpenMetadata entity conversion"""
    
    id: Optional[str] = Field(default=None, description="Entity ID")
    name: str = Field(..., description="Entity name")
    display_name: Optional[str] = Field(default=None, description="Display name")
    description: Optional[str] = Field(default=None, description="Entity description")
    
    # Tags and classification
    tags: List[str] = Field(default_factory=list, description="Entity tags")
    
    # Custom properties
    custom_properties: Dict[str, Any] = Field(default_factory=dict, description="Custom properties")
    
    # Lineage
    upstream_entities: List[str] = Field(default_factory=list, description="Upstream entity references")
    downstream_entities: List[str] = Field(default_factory=list, description="Downstream entity references")


class DatabaseServiceMetadata(OpenMetadataEntity):
    """OpenMetadata database service representation"""
    
    service_type: str = Field(default="Polaris", description="Service type")
    connection_config: Dict[str, Any] = Field(default_factory=dict, description="Connection configuration")


class DatabaseMetadata(OpenMetadataEntity):
    """OpenMetadata database representation"""
    
    service: str = Field(..., description="Database service reference")
    database_schema: Optional[Dict[str, Any]] = Field(default=None, description="Database schema")


class DatabaseSchemaMetadata(OpenMetadataEntity):
    """OpenMetadata database schema representation"""
    
    database: str = Field(..., description="Database reference")
    schema_type: str = Field(default="Regular", description="Schema type")


class TableMetadata(OpenMetadataEntity):
    """OpenMetadata table representation"""
    
    database_schema: str = Field(..., description="Database schema reference")
    table_type: str = Field(default="Regular", description="Table type")
    columns: List[Dict[str, Any]] = Field(default_factory=list, description="Table columns")
    
    # Table constraints
    table_constraints: List[Dict[str, Any]] = Field(default_factory=list, description="Table constraints")
    
    # Partitioning
    table_partition: Optional[Dict[str, Any]] = Field(default=None, description="Table partitioning")
    
    # Profile and usage
    profile: Optional[Dict[str, Any]] = Field(default=None, description="Table profile")
    usage_summary: Optional[Dict[str, Any]] = Field(default=None, description="Usage summary")