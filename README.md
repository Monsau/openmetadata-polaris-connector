# Apache Polaris Connector for OpenMetadata

This project provides a custom OpenMetadata connector for Apache Polaris, enabling seamless metadata ingestion from Polaris catalogs into OpenMetadata. Apache Polaris is an open-source catalog service that implements the Apache Iceberg REST API specification.

---

## 🚀 Key Features

- **Catalog Discovery**: Automatically discovers all available Polaris catalogs
- **Namespace Enumeration**: Explores namespaces within each catalog
- **Table Metadata Extraction**: Retrieves comprehensive table schema and metadata
- **Iceberg Schema Support**: Full support for Iceberg table schemas including complex data types
- **Flexible Authentication**: Supports OAuth2, API Key, and Basic authentication methods
- **Filtering Capabilities**: Configure which catalogs and namespaces to include/exclude
- **Auto-Tagging**: Apply default tags to all ingested tables for better data governance
- **Connection Testing**: Built-in connection validation and health checks

---

## 📁 Project Structure

```
polaris/
├── connectors/
│   └── polaris/
│       ├── __init__.py
│       ├── connector.py              # Polaris API client helper
│       └── polaris_connector.py      # Main OpenMetadata source connector
├── playbooks/
│   └── ingestion.yaml               # Workflow configuration
├── requirements.txt                 # Python dependencies
├── setup.py                        # Package setup configuration
├── Dockerfile                      # Container build configuration
└── README.md                       # This file
```

---

## 🛠 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Apache Polaris instance running and accessible
- OpenMetadata instance (version 1.4.0 or higher)
- Valid authentication credentials for Polaris

### 1. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Or install OpenMetadata ingestion with additional components
pip install "openmetadata-ingestion[pandas]" requests urllib3
```

### 2. Package Structure Setup

Ensure all directories contain `__init__.py` files for Python package recognition:

```bash
# These should already exist, but verify:
ls connectors/__init__.py
ls connectors/polaris/__init__.py
```

---

## ⚙️ Configuration

### Authentication Methods

The connector supports three authentication methods:

#### OAuth2 (Recommended)
```yaml
auth_type: "oauth2"
client_id: "your_client_id"
client_secret: "your_client_secret"
token_url: "/v1/oauth/token"  # Optional, defaults to this value
```

#### API Key
```yaml
auth_type: "api_key"
api_key: "your_api_key_token"
```

#### Basic Authentication
```yaml
auth_type: "basic"
username: "your_username"
password: "your_password"
```

### Complete Configuration Example

Edit `playbooks/ingestion.yaml`:

```yaml
source:
  type: customDatabase
  serviceName: polaris-catalog
  serviceConnection:
    config:
      type: CustomDatabase
      sourcePythonClass: connectors.polaris.polaris_connector.PolarisSource
      connectionOptions:
        # === Required Connection Settings ===
        host: "polaris.example.com"
        port: "8181"
        use_ssl: "true"
        
        # === Authentication (OAuth2 Example) ===
        auth_type: "oauth2"
        client_id: "polaris-client"
        client_secret: "your-secret-here"
        
        # === Optional Settings ===
        connection_timeout: "30"
        request_timeout: "60"
        
        # === Filtering ===
        catalog_filter: "prod_catalog,staging_catalog"  # Empty = all catalogs
        namespace_filter: ""                            # Empty = all namespaces
        
        # === Tagging ===
        default_tags: "Tier.Bronze,Source.Polaris"

sink:
  type: metadata-rest
  config: {}

workflowConfig:
  loggerLevel: INFO
  openMetadataServerConfig:
    hostPort: http://openmetadata:8585/api
    authProvider: openmetadata
    securityConfig:
      jwtToken: "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIs..."
```

---

## 🏃‍♂️ Running the Connector

### Command Line Execution

**Important**: Run commands from the project root directory.

#### Linux/macOS
```bash
export PYTHONPATH="."
metadata ingest -c playbooks/ingestion.yaml
```

#### Windows PowerShell
```powershell
$env:PYTHONPATH = "."
metadata ingest -c playbooks/ingestion.yaml
```

#### Windows Command Prompt
```cmd
set PYTHONPATH=.
metadata ingest -c playbooks/ingestion.yaml
```

### Docker Execution

Build and run using Docker:

```bash
# Build the Docker image
docker build -t polaris-connector:latest .

# Run the connector
docker run --rm \
  -v $(pwd)/playbooks:/app/playbooks \
  polaris-connector:latest
```

---

## 🔧 Configuration Options

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `host` | ✅ | - | Polaris server hostname |
| `port` | ❌ | `8181` | Polaris server port |
| `use_ssl` | ❌ | `false` | Enable HTTPS |
| `auth_type` | ❌ | `oauth2` | Authentication method |
| `client_id` | ⚠️ | - | OAuth2 client ID (required for oauth2) |
| `client_secret` | ⚠️ | - | OAuth2 client secret (required for oauth2) |
| `token_url` | ❌ | `/v1/oauth/token` | OAuth2 token endpoint |
| `api_key` | ⚠️ | - | API key (required for api_key auth) |
| `username` | ⚠️ | - | Username (required for basic auth) |
| `password` | ⚠️ | - | Password (required for basic auth) |
| `connection_timeout` | ❌ | `30` | Connection timeout (seconds) |
| `request_timeout` | ❌ | `60` | Request timeout (seconds) |
| `catalog_filter` | ❌ | `""` | Comma-separated list of catalogs to include |
| `namespace_filter` | ❌ | `""` | Comma-separated list of namespaces to include |
| `default_tags` | ❌ | `""` | Comma-separated list of default tags |

---

## 🧪 Testing Connection

Test your Polaris connection before running full ingestion:

```python
from connectors.polaris.connector import PolarisConnector

# Create connector
connector = PolarisConnector(
    host="your-polaris-host",
    port=8181,
    use_ssl=True,
    auth_type="oauth2",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Test connection
if connector.connect():
    print("✅ Connection successful!")
    
    # Test API calls
    catalogs = connector.get_catalogs()
    print(f"Found {len(catalogs)} catalogs")
    
    connector.close()
else:
    print("❌ Connection failed!")
```

---

## 📊 Data Type Mapping

The connector automatically maps Iceberg data types to OpenMetadata types:

| Iceberg Type | OpenMetadata Type |
|--------------|-------------------|
| `string` | `STRING` |
| `int`, `integer` | `INT` |
| `long` | `BIGINT` |
| `float` | `FLOAT` |
| `double` | `DOUBLE` |
| `boolean` | `BOOLEAN` |
| `timestamp` | `TIMESTAMP` |
| `timestamptz` | `TIMESTAMPZ` |
| `date` | `DATE` |
| `time` | `TIME` |
| `binary` | `BINARY` |
| `decimal` | `DECIMAL` |
| `uuid` | `UUID` |
| `list` | `ARRAY` |
| `map` | `MAP` |
| `struct` | `STRUCT` |

---

## 🐛 Troubleshooting

### Common Issues

#### `ModuleNotFoundError: No module named 'connectors'`
**Solution**: 
- Ensure you're running the command from the project root directory
- Set `PYTHONPATH` environment variable correctly
- Verify all `__init__.py` files exist

#### Authentication Failures
**Solutions**:
- Verify credentials are correct
- Check if Polaris server is accessible
- Ensure authentication method matches server configuration
- For OAuth2, verify token endpoint URL

#### Connection Timeouts
**Solutions**:
- Increase `connection_timeout` and `request_timeout` values
- Check network connectivity to Polaris server
- Verify firewall settings

#### Empty Results
**Solutions**:
- Check if catalogs/namespaces exist in Polaris
- Verify filter configurations aren't too restrictive
- Ensure proper permissions for the authenticated user

### Debugging

Enable debug logging by setting `loggerLevel: DEBUG` in the workflow configuration:

```yaml
workflowConfig:
  loggerLevel: DEBUG
```

### Log Files

The connector uses OpenMetadata's logging system. Logs are typically found in:
- Container: `/tmp/openmetadata_logs/`
- Local: `~/.local/share/openmetadata/logs/`

---

## 🔒 Security Best Practices

1. **Never commit credentials**: Use environment variables or secure vaults
2. **Use SSL/HTTPS**: Enable `use_ssl: true` for production
3. **Rotate tokens**: Regularly rotate API keys and OAuth2 credentials
4. **Least privilege**: Use accounts with minimal required permissions
5. **Network security**: Restrict network access between components

### Environment Variables Example

```bash
export POLARIS_CLIENT_ID="your-client-id"
export POLARIS_CLIENT_SECRET="your-client-secret"
export OPENMETADATA_JWT_TOKEN="your-jwt-token"
```

Update your YAML configuration to use environment variables:

```yaml
connectionOptions:
  client_id: "${POLARIS_CLIENT_ID}"
  client_secret: "${POLARIS_CLIENT_SECRET}"
```

---

## 🚀 Advanced Usage

### Custom Filtering

Implement complex filtering logic by modifying the `_discover_tables` method:

```python
# Example: Filter tables by naming pattern
def _discover_tables(self) -> List[PolarisTable]:
    tables = super()._discover_tables()
    return [t for t in tables if t.table_name.startswith("prod_")]
```

### Custom Tagging

Add intelligent tagging based on table metadata:

```python
def _get_table_tags(self, polaris_table: PolarisTable) -> List[TagLabel]:
    tags = []
    
    # Tag based on namespace
    if "sensitive" in polaris_table.namespace_name:
        tags.append(TagLabel(tagFQN="PII.Sensitive"))
    
    # Tag based on table properties
    properties = polaris_table.metadata.get("metadata", {}).get("properties", {})
    if properties.get("data_classification") == "critical":
        tags.append(TagLabel(tagFQN="Tier.Gold"))
    
    return tags
```

---

## 📝 Development

### Setup Development Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd polaris-connector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e .
```

### Running Tests

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=connectors tests/
```

### Code Quality

```bash
# Format code
black connectors/

# Lint code
flake8 connectors/

# Type checking
mypy connectors/
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run code quality checks: `black`, `flake8`, `mypy`
5. Commit your changes: `git commit -am 'Add your feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Create a Pull Request

---

## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

---

## 📞 Support & Contact

- **Author**: Mustapha Fonsau
- **Email**: mfonsau@talentys.eu
- **LinkedIn**: https://www.linkedin.com/in/mustapha-fonsau/

For issues and feature requests, please use the GitHub Issues page.

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-08 | Initial release with full Polaris support |
| | | - OAuth2, API Key, and Basic authentication |
| | | - Comprehensive schema mapping |
| | | - Filtering and tagging capabilities |

---

## 🙏 Acknowledgments

- [Apache Polaris](https://polaris.apache.org/) for providing the catalog service
- [OpenMetadata](https://open-metadata.org/) for the metadata management platform  
- [Apache Iceberg](https://iceberg.apache.org/) for the table format specification