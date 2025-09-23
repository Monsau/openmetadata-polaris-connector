"""
Test configuration for pytest
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return {
        "polaris_host": "localhost",
        "polaris_port": 8181,
        "test_timeout": 30
    }


@pytest.fixture
def sample_catalog_data():
    """Sample catalog data for testing"""
    return [
        {"name": "main", "type": "iceberg"},
        {"name": "analytics", "type": "iceberg"},
        {"name": "staging", "type": "iceberg"}
    ]


@pytest.fixture
def sample_namespace_data():
    """Sample namespace data for testing"""
    return [
        {"namespace": ["sales"]},
        {"namespace": ["marketing"]},
        {"namespace": ["reporting"]}
    ]


@pytest.fixture
def sample_table_data():
    """Sample table data for testing"""
    return [
        {"name": "customers"},
        {"name": "orders"},
        {"name": "products"}
    ]


@pytest.fixture
def sample_table_metadata():
    """Sample table metadata for testing"""
    return {
        "metadata": {
            "schema": {
                "type": "struct",
                "schema-id": 1,
                "fields": [
                    {"id": 1, "name": "customer_id", "type": "long", "required": True},
                    {"id": 2, "name": "first_name", "type": "string", "required": True},
                    {"id": 3, "name": "last_name", "type": "string", "required": True},
                    {"id": 4, "name": "email", "type": "string", "required": True},
                    {"id": 5, "name": "created_at", "type": "timestamp", "required": True}
                ]
            },
            "properties": {
                "owner": "data-team",
                "created-by": "polaris-connector-demo"
            }
        }
    }