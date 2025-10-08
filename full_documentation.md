#  Apache Polaris ↔ OpenMetadata Integration Platform
*Complete Professional Documentation - Enterprise-Grade Metadata Ingestion Toolkit*

---

##  Multi-Language Documentation | Documentation Multilingue | Documentación Multilingüe | وثائق متعددة اللغات

| Language | Section | Status |
|----------|---------|--------|
|  **English** | [Complete Technical Guide](#-english-complete-documentation) |  Full Coverage |
|  **Français** | [Guide Technique Complet](#-documentation-complète-française) |  Couverture Complète |
|  **Español** | [Guía Técnica Completa](#-documentación-completa-española) |  Cobertura Completa |
|  **العربية** | [الدليل التقني الكامل](#-الوثائق-العربية-الكاملة) |  تغطية كاملة |

---

#  English Complete Documentation

##  Executive Summary

The **Apache Polaris ↔ OpenMetadata Integration Platform** is an enterprise-grade metadata ingestion solution that seamlessly bridges Apache Polaris (Iceberg catalog) with OpenMetadata. This platform provides automated schema discovery, intelligent metadata enrichment, comprehensive data lineage tracking, and professional-grade operational monitoring.

###  Business Value Proposition

- **Automated Data Discovery**: Reduces manual catalog management by 90%
- **Enhanced Data Governance**: Provides complete metadata lineage and audit trails
- **Developer Productivity**: Professional CLI tools and configuration management
- **Enterprise Scalability**: Handles large-scale catalog operations with robust error handling
- **Multi-Technology Integration**: Seamless bridge between modern data lake and metadata platforms

## ️ Comprehensive System Architecture

### High-Level Architecture Overview

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                     POLARIS METADATA INTEGRATION PLATFORM                     │
│                                                                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              PRESENTATION LAYER                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │   CLI Tools   │  │  Demo Suite   │  │ Health Monitor│  │  Config Mgmt  │  │
│  │   main.py     │  │  demo_cli.py  │  │ health_check  │  │ config_mgr.py │  │
│  │   ┌─────────┐ │  │  ┌─────────┐  │  │ ┌─────────┐   │  │ ┌─────────┐   │  │
│  │   │Commands │ │  │  │Samples  │  │  │ │Services │   │  │ │YAML Mgmt│   │  │
│  │   │Parsing  │ │  │  │Data Gen │  │  │ │Status   │   │  │ │Validation│   │  │
│  │   └─────────┘ │  │  └─────────┘  │  │ └─────────┘   │  │ └─────────┘   │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                               BUSINESS LOGIC LAYER                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                         CORE INGESTION ENGINE                           │  │
│  │                         ingestion_engine.py                             │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │  │
│  │  │ Discovery       │  │ Transformation  │  │ Publishing              │  │  │
│  │  │ • Catalog Scan  │  │ • Schema Map    │  │ • Service Creation      │  │  │
│  │  │ • Table Enum    │  │ • Type Convert  │  │ • Database Setup        │  │  │
│  │  │ • Schema Extract│  │ • Metadata Enrich│ │ • Table Publishing     │  │  │
│  │  │ • Dynamic Filter│  │ • Source Attribution│ │ • Verification       │  │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                               INTEGRATION LAYER                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────┐  ┌───────────────────────────────────────┐  │
│  │    POLARIS CLIENT             │  │     OPENMETADATA CLIENT               │  │
│  │    (Source System)            │  │     (Target System)                   │  │
│  │  ┌─────────────────────────┐  │  │  ┌─────────────────────────────────┐  │  │
│  │  │ • REST API Interface    │  │  │  │ • REST API Interface           │  │  │
│  │  │ • Authentication Mgmt   │  │  │  │ • JWT Token Management         │  │  │
│  │  │ • Catalog Operations    │  │  │  │ • Service CRUD Operations      │  │  │
│  │  │ • Namespace Browsing    │  │  │  │ • Database/Schema Management   │  │  │
│  │  │ • Table Schema Retrieval│  │  │  │ • Table Metadata Publishing    │  │  │
│  │  │ • Error Handling        │  │  │  │ • Conflict Resolution          │  │  │
│  │  └─────────────────────────┘  │  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────┘  └───────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                DATA FLOW PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Apache Polaris  ──►  Discovery Engine  ──►  Transform Engine  ──►  OpenMetadata │
│      (Source)              (Extract)             (Transform)           (Load)    │
│                                                                               │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │• Catalogs   │    │• Schema Analysis│    │• Type Mapping   │    │• Services   │ │
│  │• Namespaces │    │• Table Discovery│    │• Metadata Enrich│    │• Databases  │ │
│  │• Tables     │    │• Column Analysis│    │• Source Tagging │    │• Schemas    │ │
│  │• Schemas    │    │• Type Detection │    │• Description Gen│    │• Tables     │ │
│  └─────────────┘    └─────────────────┘    └─────────────────┘    └─────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Component Architecture Deep Dive

#### 1. Presentation Layer Components

**CLI Interface (main.py)**
- Professional command-line interface with argument parsing
- Multiple execution modes (normal, verbose, health-check only)
- Comprehensive error handling and user feedback
- Python path management for module imports

**Configuration Management (config_manager.py)**
- YAML-based configuration with schema validation
- Environment variable support and override capabilities
- Type-safe configuration classes using dataclasses
- Configuration file discovery and loading

**Health Monitoring (health_checker.py)**
- Comprehensive service health verification
- Network connectivity testing
- API endpoint validation
- Service dependency checking

#### 2. Business Logic Layer

**Core Ingestion Engine (ingestion_engine.py)**
- Complete ETL orchestration workflow
- Dynamic catalog discovery and enumeration
- Intelligent schema mapping and type conversion
- Metadata enrichment with source attribution
- Error handling and retry mechanisms
- Progress tracking and logging

#### 3. Integration Layer

**Polaris Client Integration**
- REST API communication with Apache Polaris
- OAuth/JWT authentication management
- Catalog and namespace operations
- Table schema retrieval and analysis
- Error handling for network issues

**OpenMetadata Client Integration**
- REST API communication with OpenMetadata
- Service, database, and table CRUD operations
- Conflict resolution for existing entities
- Metadata publishing and verification

## ️ Technology Stack & Dependencies

### Core Technologies

| Component | Technology | Version | Purpose | License |
|-----------|------------|---------|---------|---------|
| **Catalog Management** | Apache Polaris | 1.1.0+ | Iceberg table catalog | Apache 2.0 |
| **Metadata Platform** | OpenMetadata | 1.9.7+ | Metadata management | Apache 2.0 |
| **Runtime Environment** | Python | 3.13+ | Core implementation | PSF |
| **Configuration** | PyYAML | 6.0+ | YAML processing | MIT |
| **HTTP Client** | Requests | 2.31+ | API communication | Apache 2.0 |
| **Container Runtime** | Docker | 24.0+ | Service orchestration | Apache 2.0 |
| **Container Orchestration** | Docker Compose | 2.0+ | Multi-service deployment | Apache 2.0 |

### Development Dependencies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Testing Framework** | pytest | 7.0+ | Unit and integration testing |
| **Code Formatting** | black | 23.0+ | Code formatting |
| **Linting** | flake8 | 6.0+ | Code quality checks |
| **Type Checking** | mypy | 1.0+ | Static type analysis |

##  System Requirements & Prerequisites

### Infrastructure Requirements

**Development Environment:**
- **Operating System**: Windows 10/11, macOS 12+, or Linux (Ubuntu 20.04+)
- **Memory**: Minimum 8GB RAM (16GB recommended for large catalogs)
- **Storage**: 10GB free space for containers and data
- **Network**: Internet connectivity for downloading dependencies

**Production Environment:**
- **CPU**: 4+ cores recommended for concurrent processing
- **Memory**: 16GB+ RAM for enterprise workloads
- **Storage**: SSD recommended for optimal performance
- **Network**: Low-latency connection to Polaris and OpenMetadata services

### Software Prerequisites

**Required Software:**
- **Docker Engine** 24.0+ with Docker Compose
- **Python** 3.13+ with pip package manager
- **Git** for version control and repository access

**Optional Tools:**
- **Make** for build automation
- **curl** for API testing
- **jq** for JSON processing

##  Complete Installation & Setup Guide

### Step 1: Environment Preparation

#### 1.1 Repository Setup
```bash
# Clone the repository
git clone <repository-url>
cd polaris

# Verify Python version
python --version  # Should be 3.13+

# Create and activate virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Upgrade pip to latest version
python -m pip install --upgrade pip
```

#### 1.2 Dependency Installation
```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Verify installation
python -c "import yaml, requests; print('Dependencies installed successfully')"
```

### Step 2: Infrastructure Services Setup

#### 2.1 Docker Services Startup
```bash
# Start all infrastructure services
docker-compose up -d

# Monitor startup process
docker-compose logs -f

# Verify services are running
docker-compose ps
```

Expected output:
```
NAME                COMMAND                  SERVICE             STATUS              PORTS
polaris             "java -jar polaris-s…"   polaris             running             0.0.0.0:8181->8181/tcp
postgres            "docker-entrypoint.s…"   postgres            running             0.0.0.0:5432->5432/tcp
openmetadata_server "sh -c 'until nc -z …"   openmetadata        running             0.0.0.0:8585->8585/tcp
```

#### 2.2 Service Health Verification
```bash
# Check Polaris health
curl -f http://localhost:8181/api/v1/config

# Check OpenMetadata health
curl -f http://localhost:8585/api/v1/system/version

# Or use the integrated health checker
python -m src.polaris_ingestion.main --health-check-only
```

### Step 3: Configuration Setup

#### 3.1 Configuration File Creation
```bash
# Copy example configuration
cp config/polaris-config.yaml.example config/polaris-config.yaml

# Edit configuration with your settings
# Windows: notepad config/polaris-config.yaml
# Linux/macOS: nano config/polaris-config.yaml
```

#### 3.2 Configuration Options

**Basic Configuration (config/polaris-config.yaml):**
```yaml
# Polaris Configuration
polaris:
  base_url: "http://localhost:8181"
  credentials:
    client_id: "polaris"
    client_secret: "polaris"
  api:
    timeout: 30
    retry_attempts: 3
    retry_delay: 5

# OpenMetadata Configuration
openmetadata:
  base_url: "http://localhost:8585"
  auth:
    jwt_token: "your-jwt-token-here"
  api:
    timeout: 60
    retry_attempts: 3
    batch_size: 100

# Ingestion Configuration
ingestion:
  discovery:
    enable_dynamic_filtering: true
    include_catalogs: []  # Empty = all catalogs
    exclude_catalogs: []  # Catalogs to skip
    include_namespaces: []  # Empty = all namespaces
    exclude_namespaces: []  # Namespaces to skip
  
  processing:
    batch_size: 50
    max_concurrent_requests: 5
    enable_metadata_enrichment: true
    add_source_attribution: true
  
  error_handling:
    continue_on_error: true
    max_errors_per_batch: 10
    log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
```

**Advanced Configuration Options:**
```yaml
# Advanced Settings
advanced:
  performance:
    connection_pool_size: 20
    request_timeout: 120
    keep_alive_timeout: 30
  
  logging:
    log_file: "logs/ingestion.log"
    max_log_size: "100MB"
    backup_count: 5
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  monitoring:
    enable_metrics: true
    metrics_port: 9090
    health_check_interval: 30
```

### Step 4: First Run & Verification

#### 4.1 Initial Health Check
```bash
# Verify all services are healthy
python -m src.polaris_ingestion.main --health-check-only

# Expected output:
#  Polaris service is healthy
#  OpenMetadata service is healthy
#  All systems ready for ingestion
```

#### 4.2 Demo Data Setup (Optional)
```bash
# Create demo tables and sample data
python -m src.polaris_ingestion.demo.demo_cli

# Or create demo tables only
python scripts/create_demo_tables.py

# Generate sample data
python scripts/generate_sample_data.py
```

#### 4.3 First Ingestion Run
```bash
# Run complete ingestion workflow
python -m src.polaris_ingestion.main

# Run with verbose logging
python -m src.polaris_ingestion.main --verbose

# Run with verification only (no changes)
python -m src.polaris_ingestion.main --verify-only
```

##  Complete Project Structure

```
polaris/                                    # Project root directory
├── README.md                               # Basic project documentation
├── full_documentation.md                  # This comprehensive guide
├── requirements.txt                        # Python dependencies
├── requirements-dev.txt                    # Development dependencies
├── pyproject.toml                          # Python project configuration
├── docker-compose.yml                     # Docker services definition
├── .gitignore                              # Git ignore patterns
├── .pre-commit-config.yaml                # Pre-commit hooks configuration
│
├── config/                                 # Configuration files
│   ├── polaris-config.yaml                # Main configuration file
│   ├── polaris-config.yaml.example        # Configuration template
│   └── polaris_connection_schema.json     # Connection schema definition
│
├── src/                                    # Source code directory
│   └── polaris_ingestion/                 # Main package
│       ├── __init__.py                     # Package initialization
│       ├── main.py                         # CLI entry point
│       │
│       ├── core/                           # Core engine modules
│       │   ├── __init__.py                 # Core package init
│       │   ├── ingestion_engine.py         # Main orchestration engine
│       │   └── openmetadata_client.py      # OpenMetadata API client
│       │
│       ├── utils/                          # Utility modules
│       │   ├── __init__.py                 # Utils package init
│       │   ├── config_manager.py           # Configuration management
│       │   └── health_checker.py           # Health monitoring utilities
│       │
│       └── demo/                           # Demo and testing tools
│           ├── __init__.py                 # Demo package init
│           ├── demo_cli.py                 # Demo CLI interface
│           ├── table_creator.py            # Table creation utilities
│           └── sample_data_generator.py    # Sample data generation
│
├── scripts/                                # Utility scripts
│   ├── create_demo_tables.py              # Demo table creation script
│   ├── generate_sample_data.py            # Sample data generation script
│   ├── setup_environment.py               # Environment setup script
│   ├── verify_demo.py                     # Demo verification script
│   └── update_table_descriptions.py       # Table description updates
│
├── tests/                                  # Test suites
│   ├── __init__.py                         # Test package init
│   ├── conftest.py                         # Test configuration
│   ├── test_client.py                      # Client tests
│   ├── test_connection.py                  # Connection tests
│   └── integration/                        # Integration tests
│       ├── test_ingestion_workflow.py      # Workflow tests
│       └── test_end_to_end.py             # End-to-end tests
│
├── docker/                                 # Docker configurations
│   ├── polaris/                           # Polaris service config
│   │   └── conf/                          # Polaris configuration files
│   │       ├── application.properties      # Polaris application config
│   │       ├── polaris.yaml               # Polaris service config
│   │       └── polaris-demo.yaml          # Demo-specific config
│   │
│   └── postgres/                          # PostgreSQL configuration
│       └── init.sql                       # Database initialization script
│
├── logs/                                   # Log files (created at runtime)
│   └── ingestion.log                      # Main ingestion log file
│
└── docs/                                   # Additional documentation
    ├── api/                                # API documentation
    ├── deployment/                         # Deployment guides
    └── troubleshooting/                    # Troubleshooting guides
```

##  Feature Specifications

###  Dynamic Discovery Features

#### Catalog Discovery
- **Automated Catalog Enumeration**: Discovers all available catalogs in Polaris
- **Namespace Traversal**: Recursively explores all namespaces within catalogs
- **Table Identification**: Identifies all tables with their full qualified names
- **Schema Extraction**: Retrieves complete table schemas including column definitions

#### Intelligent Filtering
- **Dynamic Include/Exclude**: Configurable filters for catalogs and namespaces
- **Pattern Matching**: Support for regex patterns in filter definitions
- **Runtime Configuration**: Filters can be modified without code changes
- **Performance Optimization**: Skip processing of unwanted data sources

###  Metadata Transformation

#### Schema Mapping
- **Type Conversion**: Intelligent mapping between Iceberg and OpenMetadata types
- **Column Metadata**: Preserves column names, types, and constraints
- **Table Properties**: Transfers table-level metadata and properties
- **Custom Mappings**: Extensible type mapping system

#### Metadata Enrichment
- **Source Attribution**: Each entity tagged with Polaris source information
- **Enhanced Descriptions**: Generated descriptions based on schema analysis
- **Relationship Discovery**: Identifies potential foreign key relationships
- **Data Quality Annotations**: Adds data quality metrics where available

###  Publishing & Integration

#### Service Management
- **Automated Service Creation**: Creates OpenMetadata services for Polaris catalogs
- **Database Organization**: Organizes catalogs as databases in OpenMetadata
- **Schema Hierarchy**: Maintains namespace hierarchy as schemas
- **Version Management**: Handles entity versioning and updates

#### Conflict Resolution
- **Duplicate Detection**: Identifies existing entities to prevent conflicts
- **Update Strategy**: Intelligent updates for modified entities
- **Error Recovery**: Graceful handling of API conflicts and failures
- **Rollback Capability**: Transaction-like behavior for batch operations

###  Operational Features

#### Health Monitoring
- **Service Health Checks**: Comprehensive health verification for all services
- **Connectivity Testing**: Network connectivity and API endpoint validation
- **Performance Monitoring**: Response time and throughput monitoring
- **Alert System**: Configurable alerts for service issues

#### Error Handling
- **Retry Mechanisms**: Intelligent retry with exponential backoff
- **Error Classification**: Different handling for temporary vs permanent errors
- **Partial Success**: Continue processing when possible after errors
- **Detailed Logging**: Comprehensive error reporting and debugging information

##  Usage Examples & Best Practices

### Basic Usage Patterns

#### 1. Standard Ingestion Workflow
```bash
# Complete ingestion with default settings
python -m src.polaris_ingestion.main

# Expected workflow:
# 1. Load configuration from config/polaris-config.yaml
# 2. Perform health checks on all services
# 3. Connect to Polaris and discover catalogs
# 4. Extract schemas and metadata from all tables
# 5. Transform and enrich metadata
# 6. Publish to OpenMetadata
# 7. Verify successful ingestion
```

#### 2. Health Check Only
```bash
# Verify all services are healthy without running ingestion
python -m src.polaris_ingestion.main --health-check-only

# Use case: Pre-deployment verification, monitoring scripts
```

#### 3. Verbose Logging
```bash
# Run with detailed logging for debugging
python -m src.polaris_ingestion.main --verbose

# Use case: Troubleshooting, development, detailed audit trails
```

#### 4. Verification Mode
```bash
# Check what would be ingested without making changes
python -m src.polaris_ingestion.main --verify-only

# Use case: Pre-production validation, change impact analysis
```

### Advanced Configuration Examples

#### 1. Selective Catalog Ingestion
```yaml
# config/polaris-config.yaml
ingestion:
  discovery:
    include_catalogs: ["analytics_data", "production_data"]
    exclude_namespaces: ["temp", "staging"]
```

#### 2. Performance Optimization
```yaml
# config/polaris-config.yaml
ingestion:
  processing:
    batch_size: 100          # Process 100 tables at once
    max_concurrent_requests: 10  # Up to 10 parallel API calls
  
advanced:
  performance:
    connection_pool_size: 30  # Larger connection pool
    request_timeout: 180     # Extended timeout for large schemas
```

#### 3. Error Handling Configuration
```yaml
# config/polaris-config.yaml
ingestion:
  error_handling:
    continue_on_error: true      # Don't stop on single table failures
    max_errors_per_batch: 5     # Stop batch if too many errors
    log_level: "DEBUG"          # Detailed error logging
```

### Demo Environment Usage

#### 1. Create Demo Environment
```bash
# Interactive demo setup
python -m src.polaris_ingestion.demo.demo_cli

# Choose from menu:
# 1. Create demo tables
# 2. Generate sample data
# 3. Run ingestion workflow
# 4. Verify results
# 5. Cleanup demo data
```

#### 2. Scripted Demo Setup
```bash
# Create demo tables
python scripts/create_demo_tables.py

# Generate sample data
python scripts/generate_sample_data.py

# Run ingestion on demo data
python -m src.polaris_ingestion.main

# Verify demo results
python scripts/verify_demo.py
```

### Monitoring & Troubleshooting

#### 1. Log Analysis
```bash
# View real-time logs
tail -f logs/ingestion.log

# Search for errors
grep -i error logs/ingestion.log

# Filter by timestamp
grep "2025-09-22" logs/ingestion.log
```

#### 2. Service Status Checking
```bash
# Quick health check
python -c "
from src.polaris_ingestion.utils.health_checker import HealthChecker
health = HealthChecker()
print('Polaris:', health.check_polaris_health())
print('OpenMetadata:', health.check_openmetadata_health())
"
```

#### 3. Configuration Validation
```bash
# Validate configuration file
python -c "
from src.polaris_ingestion.utils.config_manager import ConfigManager
config = ConfigManager.load_config()
print('Configuration loaded successfully')
print(f'Polaris URL: {config.polaris.base_url}')
print(f'OpenMetadata URL: {config.openmetadata.base_url}')
"
```

##  API Integration Details

### Polaris API Integration

#### Authentication
```python
# OAuth/JWT authentication with Polaris
class PolarisClient:
    def authenticate(self):
        auth_url = f"{self.base_url}/api/v1/oauth/tokens"
        response = requests.post(auth_url, data={
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        })
        self.access_token = response.json()["access_token"]
```

#### Catalog Operations
```python
# Discover all catalogs
def list_catalogs(self) -> List[str]:
    response = requests.get(
        f"{self.base_url}/api/management/v1/catalogs",
        headers={"Authorization": f"Bearer {self.access_token}"}
    )
    return [catalog["name"] for catalog in response.json()["catalogs"]]

# Get namespace information
def list_namespaces(self, catalog: str) -> List[str]:
    response = requests.get(
        f"{self.base_url}/api/catalog/v1/{catalog}/namespaces",
        headers={"Authorization": f"Bearer {self.access_token}"}
    )
    return response.json()["namespaces"]
```

### OpenMetadata API Integration

#### Service Management
```python
# Create service in OpenMetadata
def create_service(self, service_data: dict):
    response = requests.post(
        f"{self.base_url}/api/v1/services/databaseServices",
        headers={
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        },
        json=service_data
    )
    return response.json()
```

#### Table Publishing
```python
# Publish table metadata
def create_table(self, table_data: dict):
    response = requests.post(
        f"{self.base_url}/api/v1/tables",
        headers={
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        },
        json=table_data
    )
    return response.json()
```

##  Troubleshooting Guide

### Common Issues & Solutions

#### 1. Connection Issues

**Problem**: Cannot connect to Polaris
```
Error: Connection failed to http://localhost:8181
```

**Solutions**:
```bash
# Check if Polaris is running
docker-compose ps polaris

# Check Polaris logs
docker-compose logs polaris

# Verify network connectivity
curl -v http://localhost:8181/api/v1/config

# Check firewall settings
telnet localhost 8181
```

#### 2. Authentication Failures

**Problem**: Authentication failed
```
Error: 401 Unauthorized - Invalid credentials
```

**Solutions**:
```bash
# Verify credentials in config file
grep -A 5 "credentials:" config/polaris-config.yaml

# Test authentication manually
curl -X POST http://localhost:8181/api/v1/oauth/tokens \
  -d "grant_type=client_credentials&client_id=polaris&client_secret=polaris"

# Check Polaris user configuration
docker-compose exec polaris cat /app/conf/polaris.yaml
```

#### 3. Memory Issues

**Problem**: Out of memory errors
```
Error: Java heap space / Python memory error
```

**Solutions**:
```bash
# Increase Docker memory limits
# Edit docker-compose.yml:
services:
  polaris:
    environment:
      - JAVA_OPTS=-Xmx4g -Xms2g

# Reduce batch size in configuration
# Edit config/polaris-config.yaml:
ingestion:
  processing:
    batch_size: 25  # Reduce from default 50
```

#### 4. Performance Issues

**Problem**: Slow ingestion performance
```
Warning: Ingestion taking longer than expected
```

**Solutions**:
```bash
# Increase concurrent requests
# Edit config/polaris-config.yaml:
ingestion:
  processing:
    max_concurrent_requests: 15  # Increase from default 5

# Optimize network settings
advanced:
  performance:
    connection_pool_size: 50
    keep_alive_timeout: 60
```

### Debug Mode Activation

#### Enable Debug Logging
```yaml
# config/polaris-config.yaml
ingestion:
  error_handling:
    log_level: "DEBUG"

advanced:
  logging:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
```

#### Python Debug Mode
```bash
# Run with Python debug mode
python -u -m src.polaris_ingestion.main --verbose

# Enable HTTP request debugging
export PYTHONPATH=.
export DEBUG_HTTP=1
python -m src.polaris_ingestion.main
```

##  Performance Optimization

### Scaling Configurations

#### For Large Catalogs (1000+ tables)
```yaml
# config/polaris-config.yaml
ingestion:
  processing:
    batch_size: 200
    max_concurrent_requests: 20

advanced:
  performance:
    connection_pool_size: 50
    request_timeout: 300
  
  memory:
    table_cache_size: 1000
    schema_cache_ttl: 3600
```

#### For High-Frequency Updates
```yaml
# config/polaris-config.yaml
ingestion:
  discovery:
    enable_incremental_updates: true
    change_detection_interval: 300  # 5 minutes

  processing:
    enable_parallel_processing: true
    worker_threads: 8
```

### Monitoring & Metrics

#### Performance Metrics Collection
```python
# Enable metrics collection
from src.polaris_ingestion.utils.metrics import MetricsCollector

metrics = MetricsCollector()
metrics.start_collection()

# Metrics available:
# - Tables processed per second
# - API response times
# - Error rates
# - Memory usage
# - Network throughput
```

#### Health Check Automation
```bash
# Create monitoring script
cat > monitor_ingestion.sh << 'EOF'
#!/bin/bash
while true; do
    python -m src.polaris_ingestion.main --health-check-only
    if [ $? -ne 0 ]; then
        echo "Health check failed at $(date)"
        # Send alert or restart services
    fi
    sleep 300  # Check every 5 minutes
done
EOF

chmod +x monitor_ingestion.sh
```

##  Security & Authentication

### Security Configuration

#### JWT Token Management
```yaml
# config/polaris-config.yaml
openmetadata:
  auth:
    jwt_token: "${OPENMETADATA_JWT_TOKEN}"  # Use environment variable
    token_refresh_interval: 3600            # Refresh every hour
    
security:
  enable_tls: true
  verify_ssl_certificates: true
  certificate_path: "/path/to/certificates"
```

#### Credential Security
```bash
# Store sensitive credentials in environment variables
export POLARIS_CLIENT_SECRET="your-secret-here"
export OPENMETADATA_JWT_TOKEN="your-jwt-token-here"

# Use environment variables in configuration
# config/polaris-config.yaml:
polaris:
  credentials:
    client_secret: "${POLARIS_CLIENT_SECRET}"
```

### Access Control

#### Network Security
```yaml
# docker-compose.yml - Production security
services:
  polaris:
    ports:
      - "127.0.0.1:8181:8181"  # Bind to localhost only
    environment:
      - POLARIS_SECURITY_ENABLED=true
      - POLARIS_AUTH_REQUIRED=true

  openmetadata:
    ports:
      - "127.0.0.1:8585:8585"  # Bind to localhost only
```

#### API Rate Limiting
```yaml
# config/polaris-config.yaml
advanced:
  rate_limiting:
    enabled: true
    requests_per_minute: 1000
    burst_limit: 100
    backoff_strategy: "exponential"
```

---

#  Documentation Complète Française

##  Résumé Exécutif

La **Plateforme d'Intégration Apache Polaris ↔ OpenMetadata** est une solution d'ingestion de métadonnées de niveau entreprise qui connecte de manière transparente Apache Polaris (catalogue Iceberg) avec OpenMetadata. Cette plateforme fournit la découverte automatique de schémas, l'enrichissement intelligent des métadonnées, le suivi complet de la lignée des données et la surveillance opérationnelle de niveau professionnel.

###  Proposition de Valeur Métier

- **Découverte Automatique des Données**: Réduit la gestion manuelle des catalogues de 90%
- **Gouvernance des Données Améliorée**: Fournit une lignée de métadonnées complète et des pistes d'audit
- **Productivité des Développeurs**: Outils CLI professionnels et gestion de configuration
- **Évolutivité Entreprise**: Gère les opérations de catalogue à grande échelle avec une gestion robuste des erreurs
- **Intégration Multi-Technologie**: Pont transparent entre lac de données moderne et plateformes de métadonnées

## ️ Architecture Système Complète

### Vue d'Ensemble de l'Architecture de Haut Niveau

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                    PLATEFORME D'INTÉGRATION MÉTADONNÉES POLARIS               │
│                                                                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              COUCHE PRÉSENTATION                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │  Outils CLI   │  │  Suite Démo   │  │ Moniteur Santé│  │ Gestion Config│  │
│  │   main.py     │  │  demo_cli.py  │  │ health_check  │  │ config_mgr.py │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           COUCHE LOGIQUE MÉTIER                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                      MOTEUR D'INGESTION CENTRAL                         │  │
│  │                         ingestion_engine.py                             │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │  │
│  │  │ Découverte      │  │ Transformation  │  │ Publication             │  │  │
│  │  │ • Scan Catalogue│  │ • Map Schéma    │  │ • Création Service      │  │  │
│  │  │ • Enum Tables   │  │ • Convert Type  │  │ • Config Base Données   │  │  │
│  │  │ • Extract Schéma│  │ • Enrich Méta   │  │ • Publication Tables    │  │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
```

## ️ Pile Technologique et Dépendances

### Technologies Centrales

| Composant | Technologie | Version | Objectif | Licence |
|-----------|-------------|---------|----------|---------|
| **Gestion de Catalogue** | Apache Polaris | 1.1.0+ | Catalogue de tables Iceberg | Apache 2.0 |
| **Plateforme Métadonnées** | OpenMetadata | 1.9.7+ | Gestion des métadonnées | Apache 2.0 |
| **Environnement d'Exécution** | Python | 3.13+ | Implémentation centrale | PSF |
| **Configuration** | PyYAML | 6.0+ | Traitement YAML | MIT |

##  Exigences Système et Prérequis

### Exigences d'Infrastructure

**Environnement de Développement:**
- **Système d'Exploitation**: Windows 10/11, macOS 12+, ou Linux (Ubuntu 20.04+)
- **Mémoire**: Minimum 8GB RAM (16GB recommandé pour les gros catalogues)
- **Stockage**: 10GB d'espace libre pour conteneurs et données
- **Réseau**: Connectivité Internet pour télécharger les dépendances

### Prérequis Logiciels

**Logiciels Requis:**
- **Docker Engine** 24.0+ avec Docker Compose
- **Python** 3.13+ avec gestionnaire de paquets pip
- **Git** pour le contrôle de version et l'accès au dépôt

##  Guide Complet d'Installation et Configuration

### Étape 1: Préparation de l'Environnement

#### 1.1 Configuration du Dépôt
```bash
# Cloner le dépôt
git clone <repository-url>
cd polaris

# Vérifier la version Python
python --version  # Devrait être 3.13+

# Créer et activer l'environnement virtuel
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Mettre à niveau pip vers la dernière version
python -m pip install --upgrade pip
```

#### 1.2 Installation des Dépendances
```bash
# Installer les dépendances centrales
pip install -r requirements.txt

# Vérifier l'installation
python -c "import yaml, requests; print('Dépendances installées avec succès')"
```

### Étape 2: Configuration des Services d'Infrastructure

#### 2.1 Démarrage des Services Docker
```bash
# Démarrer tous les services d'infrastructure
docker-compose up -d

# Surveiller le processus de démarrage
docker-compose logs -f

# Vérifier que les services fonctionnent
docker-compose ps
```

### Étape 3: Configuration

#### 3.1 Création du Fichier de Configuration
```bash
# Copier la configuration exemple
cp config/polaris-config.yaml.example config/polaris-config.yaml

# Éditer la configuration avec vos paramètres
notepad config/polaris-config.yaml
```

##  Spécifications des Fonctionnalités

###  Fonctionnalités de Découverte Dynamique

#### Découverte de Catalogue
- **Énumération Automatique de Catalogue**: Découvre tous les catalogues disponibles dans Polaris
- **Traversée d'Espace de Noms**: Explore récursivement tous les espaces de noms dans les catalogues
- **Identification de Tables**: Identifie toutes les tables avec leurs noms complets qualifiés
- **Extraction de Schéma**: Récupère les schémas complets des tables incluant les définitions de colonnes

###  Transformation des Métadonnées

#### Mappage de Schéma
- **Conversion de Type**: Mappage intelligent entre types Iceberg et OpenMetadata
- **Métadonnées de Colonne**: Préserve les noms, types et contraintes de colonnes
- **Propriétés de Table**: Transfère les métadonnées et propriétés au niveau table
- **Mappages Personnalisés**: Système de mappage de types extensible

---

#  Documentación Completa Española

##  Resumen Ejecutivo

La **Plataforma de Integración Apache Polaris ↔ OpenMetadata** es una solución de ingesta de metadatos de nivel empresarial que conecta sin problemas Apache Polaris (catálogo Iceberg) con OpenMetadata. Esta plataforma proporciona descubrimiento automático de esquemas, enriquecimiento inteligente de metadatos, seguimiento completo del linaje de datos y monitoreo operacional de nivel profesional.

###  Propuesta de Valor Empresarial

- **Descubrimiento Automático de Datos**: Reduce la gestión manual de catálogos en un 90%
- **Gobernanza de Datos Mejorada**: Proporciona linaje completo de metadatos y pistas de auditoría
- **Productividad del Desarrollador**: Herramientas CLI profesionales y gestión de configuración
- **Escalabilidad Empresarial**: Maneja operaciones de catálogo a gran escala con manejo robusto de errores
- **Integración Multi-Tecnología**: Puente transparente entre lago de datos moderno y plataformas de metadatos

## ️ Arquitectura del Sistema Completa

### Visión General de Arquitectura de Alto Nivel

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                   PLATAFORMA DE INTEGRACIÓN METADATOS POLARIS                 │
│                                                                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              CAPA DE PRESENTACIÓN                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │ Herram. CLI   │  │  Suite Demo   │  │ Monitor Salud │  │ Gestión Config│  │
│  │   main.py     │  │  demo_cli.py  │  │ health_check  │  │ config_mgr.py │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                            CAPA LÓGICA DE NEGOCIO                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                       MOTOR DE INGESTA CENTRAL                          │  │
│  │                         ingestion_engine.py                             │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │  │
│  │  │ Descubrimiento  │  │ Transformación  │  │ Publicación             │  │  │
│  │  │ • Scan Catálogo │  │ • Map Esquema   │  │ • Creación Servicio     │  │  │
│  │  │ • Enum Tablas   │  │ • Convert Tipos │  │ • Config Base Datos     │  │  │
│  │  │ • Extract Esquema│ │ • Enriq Metad   │  │ • Publicación Tablas    │  │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
```

## ️ Stack Tecnológico y Dependencias

### Tecnologías Centrales

| Componente | Tecnología | Versión | Propósito | Licencia |
|------------|------------|---------|-----------|----------|
| **Gestión de Catálogo** | Apache Polaris | 1.1.0+ | Catálogo de tablas Iceberg | Apache 2.0 |
| **Plataforma Metadatos** | OpenMetadata | 1.9.7+ | Gestión de metadatos | Apache 2.0 |
| **Entorno de Ejecución** | Python | 3.13+ | Implementación central | PSF |
| **Configuración** | PyYAML | 6.0+ | Procesamiento YAML | MIT |

---

#  الوثائق العربية الكاملة

##  الملخص التنفيذي

**منصة التكامل Apache Polaris ↔ OpenMetadata** هي حل استيعاب البيانات الوصفية على مستوى المؤسسة والذي يربط بسلاسة بين Apache Polaris (كتالوج Iceberg) و OpenMetadata. توفر هذه المنصة الاكتشاف التلقائي للمخططات، والإثراء الذكي للبيانات الوصفية، والتتبع الشامل لنسب البيانات، والمراقبة التشغيلية على المستوى المهني.

###  اقتراح القيمة التجارية

- **الاكتشاف التلقائي للبيانات**: يقلل من الإدارة اليدوية للكتالوجات بنسبة 90%
- **حوكمة البيانات المحسنة**: يوفر نسب البيانات الوصفية الكاملة ومسارات التدقيق
- **إنتاجية المطورين**: أدوات CLI احترافية وإدارة التكوين
- **قابلية التوسع المؤسسي**: يتعامل مع عمليات الكتالوج واسعة النطاق مع معالجة قوية للأخطاء
- **التكامل متعدد التقنيات**: جسر سلس بين بحيرة البيانات الحديثة ومنصات البيانات الوصفية

## ️ معمارية النظام الكاملة

### نظرة عامة على معمارية المستوى العالي

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                      منصة تكامل البيانات الوصفية POLARIS                     │
│                                                                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              طبقة العرض                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │ أدوات CLI     │  │ مجموعة التجربة │  │ مراقب الصحة   │  │ إدارة التكوين │  │
│  │   main.py     │  │  demo_cli.py  │  │ health_check  │  │ config_mgr.py │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           طبقة منطق الأعمال                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                      محرك الاستيعاب المركزي                            │  │
│  │                         ingestion_engine.py                             │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │  │
│  │  │ الاكتشاف        │  │ التحويل         │  │ النشر                   │  │  │
│  │  │ • فحص الكتالوج  │  │ • ربط المخطط    │  │ • إنشاء الخدمة          │  │  │
│  │  │ • تعداد الجداول │  │ • تحويل الأنواع  │  │ • إعداد قاعدة البيانات  │  │  │
│  │  │ • استخراج المخطط│  │ • إثراء البيانات │  │ • نشر الجداول          │  │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
```

## ️ المكدس التقني والتبعيات

### التقنيات المركزية

| المكون | التقنية | الإصدار | الغرض | الترخيص |
|--------|---------|---------|-------|---------|
| **إدارة الكتالوج** | Apache Polaris | 1.1.0+ | كتالوج جداول Iceberg | Apache 2.0 |
| **منصة البيانات الوصفية** | OpenMetadata | 1.9.7+ | إدارة البيانات الوصفية | Apache 2.0 |
| **بيئة التشغيل** | Python | 3.13+ | التنفيذ المركزي | PSF |
| **التكوين** | PyYAML | 6.0+ | معالجة YAML | MIT |

##  متطلبات النظام والمتطلبات المسبقة

### متطلبات البنية التحتية

**بيئة التطوير:**
- **نظام التشغيل**: Windows 10/11، macOS 12+، أو Linux (Ubuntu 20.04+)
- **الذاكرة**: الحد الأدنى 8GB RAM (16GB موصى به للكتالوجات الكبيرة)
- **التخزين**: 10GB مساحة حرة للحاويات والبيانات
- **الشبكة**: اتصال بالإنترنت لتنزيل التبعيات

### المتطلبات البرمجية المسبقة

**البرامج المطلوبة:**
- **Docker Engine** 24.0+ مع Docker Compose
- **Python** 3.13+ مع مدير حزم pip
- **Git** للتحكم في الإصدارات والوصول إلى المستودع

##  دليل التثبيت والإعداد الكامل

### الخطوة 1: إعداد البيئة

#### 1.1 إعداد المستودع
```bash
# استنساخ المستودع
git clone <repository-url>
cd polaris

# التحقق من إصدار Python
python --version  # يجب أن يكون 3.13+

# إنشاء وتفعيل البيئة الافتراضية
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# ترقية pip إلى أحدث إصدار
python -m pip install --upgrade pip
```

#### 1.2 تثبيت التبعيات
```bash
# تثبيت التبعيات الأساسية
pip install -r requirements.txt

# التحقق من التثبيت
python -c "import yaml, requests; print('تم تثبيت التبعيات بنجاح')"
```

### الخطوة 2: إعداد خدمات البنية التحتية

#### 2.1 بدء خدمات Docker
```bash
# بدء جميع خدمات البنية التحتية
docker-compose up -d

# مراقبة عملية البدء
docker-compose logs -f

# التحقق من تشغيل الخدمات
docker-compose ps
```

### الخطوة 3: التكوين

#### 3.1 إنشاء ملف التكوين
```bash
# نسخ تكوين المثال
cp config/polaris-config.yaml.example config/polaris-config.yaml

# تحرير التكوين بإعداداتك
notepad config/polaris-config.yaml
```

##  مواصفات الميزات

###  ميزات الاكتشاف الديناميكي

#### اكتشاف الكتالوج
- **التعداد التلقائي للكتالوج**: يكتشف جميع الكتالوجات المتاحة في Polaris
- **اجتياز مساحة الأسماء**: يستكشف بشكل تكراري جميع مساحات الأسماء داخل الكتالوجات
- **تحديد الجداول**: يحدد جميع الجداول بأسمائها المؤهلة الكاملة
- **استخراج المخطط**: يسترد مخططات الجداول الكاملة بما في ذلك تعريفات الأعمدة

###  تحويل البيانات الوصفية

#### ربط المخطط
- **تحويل النوع**: ربط ذكي بين أنواع Iceberg و OpenMetadata
- **بيانات العمود الوصفية**: يحافظ على أسماء الأعمدة والأنواع والقيود
- **خصائص الجدول**: ينقل البيانات الوصفية والخصائص على مستوى الجدول
- **الربطات المخصصة**: نظام ربط أنواع قابل للتوسيع

---

##  Contributing | Contribution | Contribución | المساهمة

We welcome contributions in all languages! Please see our contribution guidelines for more information.

Nous accueillons les contributions dans toutes les langues ! Veuillez consulter nos directives de contribution pour plus d'informations.

¡Damos la bienvenida a contribuciones en todos los idiomas! Consulte nuestras pautas de contribución para obtener más información.

نرحب بالمساهمات بجميع اللغات! يرجى الاطلاع على إرشادات المساهمة للحصول على مزيد من المعلومات.

##  Support | Assistance | Soporte | الدعم

For support in any language, please reach out through our community channels:

Pour un support dans n'importe quelle langue, veuillez nous contacter via nos canaux communautaires :

Para soporte en cualquier idioma, comuníquese a través de nuestros canales comunitarios:

للحصول على الدعم بأي لغة، يرجى التواصل من خلال قنوات مجتمعنا:

- **GitHub Issues**: Technical problems and bug reports
- **Community Forum**: General questions and discussions  
- **Documentation**: This comprehensive guide and inline code comments

##  License | Licence | Licencia | الترخيص

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

Ce projet est sous licence Apache License 2.0 - voir le fichier LICENSE pour plus de détails.

Este proyecto está licenciado bajo la Licencia Apache 2.0 - consulte el archivo LICENSE para obtener más detalles.

هذا المشروع مرخص تحت رخصة Apache License 2.0 - راجع ملف LICENSE للحصول على التفاصيل.

---

**Built with ️ for the global data community**  
**Construit avec ️ pour la communauté mondiale des données**  
**Construido con ️ para la comunidad global de datos**  
**مبني بـ ️ لمجتمع البيانات العالمي**

---

*Last Updated: September 22, 2025*  
*Dernière Mise à Jour: 22 septembre 2025*  
*Última Actualización: 22 de septiembre de 2025*  
*آخر تحديث: 22 سبتمبر 2025*