#!/usr/bin/env python3
"""
Polaris Connector Installation and Validation Script

This script helps with:
1. Installing dependencies
2. Validating configuration
3. Testing connections
4. Running the connector
"""

import os
import sys
import subprocess
import yaml
import importlib.util
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python version: {sys.version}")
    return True


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def validate_project_structure():
    """Validate project directory structure"""
    print("📁 Validating project structure...")
    
    required_files = [
        "connectors/__init__.py",
        "connectors/polaris/__init__.py",
        "connectors/polaris/connector.py",
        "connectors/polaris/polaris_connector.py",
        "playbooks/ingestion.yaml",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ Project structure is valid")
    return True


def validate_configuration(config_file="playbooks/ingestion.yaml"):
    """Validate ingestion configuration"""
    print(f"⚙️ Validating configuration: {config_file}")
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        if 'source' not in config:
            print("❌ Missing 'source' section in configuration")
            return False
        
        if 'sink' not in config:
            print("❌ Missing 'sink' section in configuration")
            return False
        
        if 'workflowConfig' not in config:
            print("❌ Missing 'workflowConfig' section in configuration")
            return False
        
        # Check source configuration
        source = config['source']
        if source.get('type') != 'customDatabase':
            print("❌ Source type must be 'customDatabase'")
            return False
        
        connection_options = (source
                            .get('serviceConnection', {})
                            .get('config', {})
                            .get('connectionOptions', {}))
        
        if not connection_options.get('host'):
            print("⚠️ Warning: 'host' not specified in connection options")
        
        # Check authentication
        auth_type = connection_options.get('auth_type', 'oauth2')
        if auth_type == 'oauth2':
            if not connection_options.get('client_id') or not connection_options.get('client_secret'):
                print("⚠️ Warning: OAuth2 requires client_id and client_secret")
        elif auth_type == 'api_key':
            if not connection_options.get('api_key'):
                print("⚠️ Warning: API key auth requires api_key")
        elif auth_type == 'basic':
            if not connection_options.get('username') or not connection_options.get('password'):
                print("⚠️ Warning: Basic auth requires username and password")
        
        # Check OpenMetadata configuration
        om_config = config.get('workflowConfig', {}).get('openMetadataServerConfig', {})
        if not om_config.get('hostPort'):
            print("⚠️ Warning: OpenMetadata hostPort not specified")
        
        if not om_config.get('securityConfig', {}).get('jwtToken'):
            print("⚠️ Warning: OpenMetadata JWT token not specified")
        
        print("✅ Configuration validation passed")
        return True
        
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
        return False
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML syntax: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False


def test_import():
    """Test importing the connector module"""
    print("🔍 Testing connector import...")
    
    try:
        # Test connector import
        spec = importlib.util.spec_from_file_location(
            "polaris_connector",
            "connectors/polaris/polaris_connector.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check if PolarisSource class exists
        if not hasattr(module, 'PolarisSource'):
            print("❌ PolarisSource class not found in connector module")
            return False
        
        print("✅ Connector import successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False


def test_polaris_connection(config_file="playbooks/ingestion.yaml"):
    """Test connection to Polaris"""
    print("🔌 Testing Polaris connection...")
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        connection_options = (config['source']
                            .get('serviceConnection', {})
                            .get('config', {})
                            .get('connectionOptions', {}))
        
        # Import the connector
        from connectors.polaris.connector import PolarisConnector
        
        connector = PolarisConnector(
            host=connection_options.get('host', 'localhost'),
            port=int(connection_options.get('port', 8181)),
            use_ssl=connection_options.get('use_ssl', 'false').lower() == 'true',
            auth_type=connection_options.get('auth_type', 'oauth2'),
            client_id=connection_options.get('client_id'),
            client_secret=connection_options.get('client_secret'),
            api_key=connection_options.get('api_key'),
            username=connection_options.get('username'),
            password=connection_options.get('password')
        )
        
        if connector.connect():
            print("✅ Polaris connection successful")
            
            # Test getting catalogs
            catalogs = connector.get_catalogs()
            print(f"📊 Found {len(catalogs)} catalogs")
            
            connector.close()
            return True
        else:
            print("❌ Polaris connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False


def run_ingestion(config_file="playbooks/ingestion.yaml"):
    """Run the ingestion process"""
    print(f"🚀 Running ingestion with config: {config_file}")
    
    try:
        # Set PYTHONPATH
        env = os.environ.copy()
        env['PYTHONPATH'] = '.'
        
        # Run metadata ingestion
        result = subprocess.run([
            'metadata', 'ingest', '-c', config_file
        ], env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Ingestion completed successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Ingestion failed")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ 'metadata' command not found. Make sure openmetadata-ingestion is installed.")
        return False
    except Exception as e:
        print(f"❌ Ingestion error: {e}")
        return False


def main():
    """Main validation and setup function"""
    print("🔧 Polaris Connector Setup and Validation")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success = True
    
    # Step 1: Check Python version
    if not check_python_version():
        success = False
    
    # Step 2: Validate project structure
    if not validate_project_structure():
        success = False
    
    # Step 3: Install dependencies (optional)
    if len(sys.argv) > 1 and sys.argv[1] == '--install':
        if not install_dependencies():
            success = False
    
    # Step 4: Validate configuration
    config_file = "playbooks/ingestion.yaml"
    if len(sys.argv) > 1 and sys.argv[1].endswith('.yaml'):
        config_file = sys.argv[1]
    
    if not validate_configuration(config_file):
        success = False
    
    # Step 5: Test imports
    if not test_import():
        success = False
    
    # Step 6: Test connection (optional)
    if len(sys.argv) > 1 and sys.argv[1] == '--test-connection':
        if not test_polaris_connection(config_file):
            success = False
    
    # Step 7: Run ingestion (optional)
    if len(sys.argv) > 1 and sys.argv[1] == '--run':
        if not run_ingestion(config_file):
            success = False
    
    print("=" * 50)
    if success:
        print("🎉 All validations passed!")
        print("\nNext steps:")
        print("1. Update playbooks/ingestion.yaml with your Polaris connection details")
        print("2. Run: python validate.py --test-connection")
        print("3. Run: python validate.py --run")
    else:
        print("❌ Some validations failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()