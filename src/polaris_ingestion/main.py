"""
Main Ingestion Script

Professional CLI interface for running Polaris to OpenMetadata ingestion.
"""

import argparse
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from polaris_ingestion.utils.config_manager import ConfigManager
from polaris_ingestion.core.ingestion_engine import IngestionEngine


def main():
    """Main entry point for the ingestion CLI."""
    parser = argparse.ArgumentParser(
        description='Apache Polaris to OpenMetadata Ingestion Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Run with default config
  %(prog)s --config custom-config.yaml  # Use custom configuration
  %(prog)s --health-check-only          # Only run health checks
  %(prog)s --verify-only                # Only verify existing ingestion
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config/polaris-config.yaml',
        help='Path to configuration file (default: config/polaris-config.yaml)'
    )
    
    parser.add_argument(
        '--health-check-only',
        action='store_true',
        help='Only perform health checks, do not run ingestion'
    )
    
    parser.add_argument(
        '--verify-only',
        action='store_true', 
        help='Only verify existing ingestion results'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate configuration file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        print(f"   Please ensure the file exists or specify a different path with --config")
        return 1
    
    try:
        # Load configuration
        if args.verbose:
            print(f"📁 Loading configuration from: {config_path}")
        
        config_manager = ConfigManager(str(config_path))
        config = config_manager.load_config()
        
        if args.verbose:
            print(f"✅ Configuration loaded successfully")
            print(f"   Service: {config.service_name}")
            print(f"   Polaris: {config.polaris.rest_endpoint}")
            print(f"   OpenMetadata: {config.openmetadata.host_port}")
        
        # Initialize ingestion engine
        engine = IngestionEngine(config)
        
        # Execute based on command line arguments
        if args.health_check_only:
            print("🏥 Running Health Checks Only...")
            success = engine.run_health_checks()
            
        elif args.verify_only:
            print("🔍 Running Verification Only...")
            success = engine.verify_ingestion()
            
        else:
            print("🚀 Running Full Ingestion Workflow...")
            success = engine.run_full_ingestion()
        
        if success:
            print("\n✅ Operation completed successfully!")
            return 0
        else:
            print("\n❌ Operation failed. Check the output above for details.")
            return 1
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())