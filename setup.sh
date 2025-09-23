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
pip install -e ".[dev]"

# Install pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install

echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start Polaris with Docker, run:"
echo "  docker-compose up -d polaris"
echo ""
echo "To populate sample data, run:"
echo "  python scripts/setup_sample_data.py"