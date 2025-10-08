#!/bin/bash
# Setup script for macOS/Linux

echo "Setting up OpenMetadata Polaris Connector..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install package in development mode
echo "Installing connector package..."
pip install -e .

echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To test the connector configuration, run:"
echo "  python validate.py"
echo ""
echo "To run ingestion, run:"
echo "  metadata ingest -c playbooks/ingestion.yaml"