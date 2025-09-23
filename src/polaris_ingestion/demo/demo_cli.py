"""
Demo CLI Tool

Command line interface for setting up and managing Polaris demo environment.
"""

import argparse
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from polaris_ingestion.utils.config_manager import ConfigManager
from polaris_ingestion.demo.table_creator import PolarisTableCreator
from polaris_ingestion.demo.sample_data_generator import SampleDataGenerator


def main():
    """Main entry point for the demo CLI."""
    parser = argparse.ArgumentParser(
        description='Apache Polaris Demo Environment Setup Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create-tables                # Create demo table structure in Polaris
  %(prog)s generate-data               # Generate sample data files
  %(prog)s generate-data --save        # Generate and save data to files
  %(prog)s list-catalogs              # List all Polaris catalogs
  %(prog)s full-setup                 # Complete demo setup (tables + data)
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config/polaris-config.yaml',
        help='Path to configuration file (default: config/polaris-config.yaml)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create tables command
    subparsers.add_parser(
        'create-tables',
        help='Create demo table structure in Polaris catalogs'
    )
    
    # Generate data command
    generate_parser = subparsers.add_parser(
        'generate-data',
        help='Generate sample data for demo tables'
    )
    generate_parser.add_argument(
        '--save', action='store_true',
        help='Save generated data to JSON files'
    )
    generate_parser.add_argument(
        '--output-dir', default='data',
        help='Directory to save data files (default: data)'
    )
    generate_parser.add_argument(
        '--preview', action='store_true',
        help='Show a preview of generated data'
    )
    
    # List catalogs command
    subparsers.add_parser(
        'list-catalogs',
        help='List all catalogs in Polaris'
    )
    
    # Full setup command
    subparsers.add_parser(
        'full-setup',
        help='Complete demo setup: create tables and generate data'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Validate configuration file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return 1
    
    try:
        # Load configuration
        config_manager = ConfigManager(str(config_path))
        config = config_manager.load_config()
        
        # Execute commands
        if args.command == 'create-tables':
            return create_tables_command(config)
        
        elif args.command == 'generate-data':
            return generate_data_command(config, args)
        
        elif args.command == 'list-catalogs':
            return list_catalogs_command(config)
        
        elif args.command == 'full-setup':
            return full_setup_command(config)
        
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1


def create_tables_command(config) -> int:
    """Execute the create tables command."""
    print("🏗️ Creating Demo Table Structure...")
    
    creator = PolarisTableCreator(config)
    success = creator.create_demo_structure()
    
    if success:
        print("\n✅ Demo table structure created successfully!")
        print(f"🌐 Polaris REST API: {config.polaris.rest_endpoint}")
        return 0
    else:
        print("\n❌ Failed to create demo table structure.")
        return 1


def generate_data_command(config, args) -> int:
    """Execute the generate data command."""
    print("🎲 Generating Sample Data...")
    
    generator = SampleDataGenerator(config)
    sample_data = generator.generate_all_sample_data()
    
    if args.preview:
        generator.print_sample_preview(sample_data)
    
    if args.save:
        success = generator.save_sample_data(sample_data, args.output_dir)
        if success:
            print(f"\n✅ Sample data saved to {args.output_dir}/ directory")
        else:
            print(f"\n❌ Failed to save sample data")
            return 1
    
    print("\n✅ Sample data generation completed!")
    return 0


def list_catalogs_command(config) -> int:
    """Execute the list catalogs command."""
    print("📊 Listing Polaris Catalogs...")
    
    creator = PolarisTableCreator(config)
    catalogs = creator.list_catalogs()
    
    if catalogs:
        print(f"\n📂 Found {len(catalogs)} catalogs:")
        for catalog in catalogs:
            name = catalog.get('name', 'Unknown')
            catalog_type = catalog.get('type', 'Unknown')
            print(f"   • {name} ({catalog_type})")
    else:
        print("\n📂 No catalogs found or unable to connect to Polaris")
        return 1
    
    return 0


def full_setup_command(config) -> int:
    """Execute the full setup command."""
    print("🚀 Running Full Demo Setup...")
    print("=" * 40)
    
    # Step 1: Create table structure
    print("\n1️⃣ Creating Demo Table Structure...")
    creator = PolarisTableCreator(config)
    if not creator.create_demo_structure():
        print("❌ Failed to create table structure")
        return 1
    
    # Step 2: Generate sample data
    print("\n2️⃣ Generating Sample Data...")
    generator = SampleDataGenerator(config)
    sample_data = generator.generate_all_sample_data()
    
    # Step 3: Save sample data
    print("\n3️⃣ Saving Sample Data...")
    if not generator.save_sample_data(sample_data, 'data'):
        print("❌ Failed to save sample data")
        return 1
    
    # Step 4: Summary
    print("\n🎉 Full Demo Setup Completed!")
    print("=" * 40)
    print(f"🌐 Polaris REST API: {config.polaris.rest_endpoint}")
    print(f"💾 Sample data saved to: data/ directory")
    print(f"📋 Next steps:")
    print(f"   1. Run: python src/polaris_ingestion/main.py")
    print(f"   2. Visit OpenMetadata UI: http://localhost:8585")
    print(f"   3. Explore ingested tables with Polaris source information")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())