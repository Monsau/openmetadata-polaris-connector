#!/usr/bin/env python3
"""
Environment Setup Script for Apache Polaris to OpenMetadata Connector

This script automates the setup of the development and runtime environment
for the Polaris connector, including dependency installation, Docker setup,
and configuration validation.
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a shell command with proper error handling."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False


def check_docker():
    """Check if Docker is running."""
    print("🐳 Checking Docker status...")
    if run_command("docker --version", "Docker version check", check=False):
        if run_command("docker info", "Docker daemon check", check=False):
            print("✅ Docker is running")
            return True
    print("❌ Docker is not running or not installed")
    return False


def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible (requires Python 3.8+)")
        return False


def setup_virtual_environment():
    """Create and activate virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("🔧 Creating virtual environment...")
    if run_command("python -m venv venv", "Virtual environment creation"):
        print("✅ Virtual environment created successfully")
        return True
    return False


def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    
    # Determine the correct pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:  # Unix-like
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # Upgrade pip first
    if not run_command(f"{pip_path} install --upgrade pip", "Pip upgrade"):
        return False
    
    # Install core dependencies
    dependencies = [
        "openmetadata-ingestion[docker]",
        "requests>=2.28.0",
        "pydantic>=1.10.0",
        "PyYAML>=6.0",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0"
    ]
    
    for dep in dependencies:
        if not run_command(f"{pip_path} install {dep}", f"Installing {dep}"):
            return False
    
    return True


def start_docker_services():
    """Start Docker services for Polaris."""
    print("🚀 Starting Docker services...")
    
    if not run_command("docker-compose down", "Stopping existing containers", check=False):
        print("⚠️ No existing containers to stop")
    
    if run_command("docker-compose up -d", "Starting Docker services"):
        print("✅ Docker services started")
        return True
    return False


def wait_for_services():
    """Wait for services to be ready."""
    print("⏳ Waiting for services to be ready...")
    
    # Wait for Polaris
    polaris_url = "http://localhost:8181/management/health"
    for i in range(30):
        try:
            response = requests.get(polaris_url, timeout=5)
            if response.status_code == 200:
                print("✅ Polaris is ready")
                break
        except requests.RequestException:
            pass
        time.sleep(2)
        print(f"⏳ Waiting for Polaris... ({i+1}/30)")
    else:
        print("❌ Polaris failed to start within timeout")
        return False
    
    # Check OpenMetadata (if running)
    openmetadata_url = "http://localhost:8585/api/v1/system/version"
    try:
        response = requests.get(openmetadata_url, timeout=5)
        if response.status_code == 200:
            print("✅ OpenMetadata is accessible")
        else:
            print("⚠️ OpenMetadata is not accessible (this is optional)")
    except requests.RequestException:
        print("⚠️ OpenMetadata is not running (this is optional)")
    
    return True


def validate_configuration():
    """Validate configuration files."""
    print("🔍 Validating configuration...")
    
    config_file = Path("config/polaris-config.yaml")
    if config_file.exists():
        print("✅ Polaris configuration found")
    else:
        print("❌ Polaris configuration not found")
        return False
    
    docker_compose = Path("docker-compose.yml")
    if docker_compose.exists():
        print("✅ Docker Compose configuration found")
    else:
        print("❌ Docker Compose configuration not found")
        return False
    
    return True


def main():
    """Main setup function."""
    print("🚀 Starting Apache Polaris to OpenMetadata Connector Setup")
    print("=" * 60)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_docker():
        print("⚠️ Docker is required for running Polaris. Please install and start Docker.")
        sys.exit(1)
    
    # Setup Python environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    if not install_dependencies():
        sys.exit(1)
    
    # Validate configuration
    if not validate_configuration():
        sys.exit(1)
    
    # Start services
    if not start_docker_services():
        sys.exit(1)
    
    if not wait_for_services():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Run the ingestion script:")
    print("   python scripts/run_ingestion.py")
    print("3. Access OpenMetadata at http://localhost:8585")
    print("4. Access Polaris REST API at http://localhost:8181")
    print("\n🔧 For configuration updates, edit config/polaris-config.yaml")


if __name__ == "__main__":
    main()