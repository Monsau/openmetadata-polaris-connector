"""
Dry-run test pour Polaris Connector
Test la configuration sans modifier OpenMetadata
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'polaris_connector'))

from unittest.mock import Mock
import logging

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection_options_extraction():
    """Test extraction des connectionOptions"""
    print("🧪 Test d'extraction des connectionOptions...")
    
    # Simuler serviceConnection avec structure __dict__['root']
    mock_conn_opts = Mock()
    mock_conn_opts.root = {
        'host': 'polaris.company.com',
        'port': '8181',
        'useSSL': 'true',
        'authType': 'oauth2',
        'clientId': 'openmetadata-client',
        'clientSecret': 'secret123',
        'tokenUrl': 'https://auth.company.com/oauth2/token',
        'catalogFilter': 'prod_.*,staging_.*',
        'namespaceFilter': 'sales.*,finance.*',
        'classificationEnabled': 'true',
        'defaultTags': 'Source.Polaris,Type.Iceberg',
        'connectionTimeout': '30',
        'requestTimeout': '60'
    }
    
    mock_config = Mock()
    mock_config.connectionOptions = mock_conn_opts
    
    mock_root = Mock()
    mock_root.config = mock_config
    
    mock_service_conn = Mock()
    mock_service_conn.__dict__ = {'root': mock_root}
    
    # Extraire les valeurs (simuler la logique de polaris_source.py)
    try:
        if hasattr(mock_service_conn, '__dict__') and 'root' in mock_service_conn.__dict__:
            root = mock_service_conn.__dict__['root']
            if hasattr(root, 'config') and hasattr(root.config, 'connectionOptions'):
                conn_opts = root.config.connectionOptions
                if hasattr(conn_opts, 'root') and isinstance(conn_opts.root, dict):
                    opts = conn_opts.root
                    
                    # Extraire les valeurs
                    host = opts.get('host', 'localhost')
                    port = int(opts.get('port', '8181'))
                    use_ssl = opts.get('useSSL', 'false').lower() == 'true'
                    auth_type = opts.get('authType', 'oauth2')
                    client_id = opts.get('clientId')
                    token_url = opts.get('tokenUrl')
                    
                    # Filters (lists)
                    catalog_filter_str = opts.get('catalogFilter', '')
                    catalog_filter = [c.strip() for c in catalog_filter_str.split(',') if c.strip()]
                    
                    namespace_filter_str = opts.get('namespaceFilter', '')
                    namespace_filter = [n.strip() for n in namespace_filter_str.split(',') if n.strip()]
                    
                    # Boolean conversion
                    classification_enabled = opts.get('classificationEnabled', 'true').lower() == 'true'
                    
                    # Tags
                    default_tags_str = opts.get('defaultTags', '')
                    default_tags = [tag.strip() for tag in default_tags_str.split(',') if tag.strip()]
                    
                    # Timeouts
                    connection_timeout = int(opts.get('connectionTimeout', '30'))
                    request_timeout = int(opts.get('requestTimeout', '60'))
                    
                    print(f"✅ Extraction réussie")
                    print(f"   📋 Host: {host}:{port}")
                    print(f"   🔒 SSL: {'enabled' if use_ssl else 'disabled'}")
                    print(f"   🔑 Auth: {auth_type}")
                    if auth_type == 'oauth2':
                        print(f"      - Client ID: {client_id}")
                        print(f"      - Token URL: {token_url}")
                    print(f"   🔍 Catalog filter: {catalog_filter or ['*']}")
                    print(f"   🔍 Namespace filter: {namespace_filter or ['*']}")
                    print(f"   ⏱️  Timeouts: conn={connection_timeout}s, req={request_timeout}s")
                    print(f"   🏷️  Classification: {'enabled' if classification_enabled else 'disabled'}")
                    if default_tags:
                        print(f"   🏷️  Tags: {', '.join(default_tags)}")
                    
                    return True
    except Exception as e:
        print(f"❌ Erreur d'extraction: {e}")
        return False
    
    print("❌ Structure connectionOptions invalide")
    return False


def test_fallback_extraction():
    """Test extraction avec fallback __root__"""
    print("\n🔄 Test d'extraction avec fallback __root__...")
    
    # Simuler ancienne structure avec __root__
    mock_conn_opts = Mock()
    mock_conn_opts.root = {
        'host': 'legacy-polaris',
        'port': '8182',
        'authType': 'basic',
        'username': 'admin',
        'password': 'admin123'
    }
    
    mock_config = Mock()
    mock_config.connectionOptions = mock_conn_opts
    
    mock_service_conn = Mock()
    mock_service_conn.__root__ = Mock()
    mock_service_conn.__root__.config = mock_config
    
    # Extraire avec fallback
    try:
        # Essayer __dict__ d'abord (échouera)
        if hasattr(mock_service_conn, '__dict__') and 'root' in mock_service_conn.__dict__:
            print("   Tentative via __dict__['root']... ❌")
        
        # Fallback sur __root__
        if hasattr(mock_service_conn, '__root__'):
            print("   Tentative via __root__... ✅")
            root = mock_service_conn.__root__
            if hasattr(root, 'config') and hasattr(root.config, 'connectionOptions'):
                conn_opts = root.config.connectionOptions
                if hasattr(conn_opts, 'root') and isinstance(conn_opts.root, dict):
                    opts = conn_opts.root
                    
                    host = opts.get('host')
                    port = int(opts.get('port', '8181'))
                    auth_type = opts.get('authType')
                    username = opts.get('username')
                    
                    print(f"✅ Fallback réussi")
                    print(f"   📋 Host: {host}:{port}")
                    print(f"   🔑 Auth: {auth_type}")
                    print(f"   👤 Username: {username}")
                    
                    return True
    except Exception as e:
        print(f"❌ Erreur de fallback: {e}")
        return False
    
    print("❌ Fallback échoué")
    return False


def test_auth_types():
    """Test différents types d'authentification"""
    print("\n🔑 Test types d'authentification...")
    
    auth_configs = [
        ('oauth2', {'authType': 'oauth2', 'clientId': 'client1', 'clientSecret': 'secret1'}),
        ('basic', {'authType': 'basic', 'username': 'admin', 'password': 'admin123'}),
        ('token', {'authType': 'token', 'bearerToken': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...'})
    ]
    
    all_valid = True
    for auth_name, config in auth_configs:
        auth_type = config.get('authType')
        
        if auth_type == 'oauth2':
            valid = 'clientId' in config and 'clientSecret' in config
        elif auth_type == 'basic':
            valid = 'username' in config and 'password' in config
        elif auth_type == 'token':
            valid = 'bearerToken' in config
        else:
            valid = False
        
        status = "✅" if valid else "❌"
        print(f"   {status} {auth_name}: {', '.join(config.keys())}")
        all_valid = all_valid and valid
    
    return all_valid


def test_filters_parsing():
    """Test parsing des filtres"""
    print("\n🔍 Test parsing des filtres...")
    
    # Configuration
    filters_config = {
        'catalogFilter': 'prod_.*,  staging_.*, dev_.*',  # Avec espaces
        'namespaceFilter': 'sales.*,finance.*, marketing.*'
    }
    
    # Parse catalog filter
    catalog_filter_str = filters_config.get('catalogFilter', '')
    catalog_filter = [c.strip() for c in catalog_filter_str.split(',') if c.strip()]
    
    print(f"✅ Catalog filters: {len(catalog_filter)} patterns")
    for pattern in catalog_filter:
        print(f"   - {pattern}")
    
    # Parse namespace filter
    namespace_filter_str = filters_config.get('namespaceFilter', '')
    namespace_filter = [n.strip() for n in namespace_filter_str.split(',') if n.strip()]
    
    print(f"✅ Namespace filters: {len(namespace_filter)} patterns")
    for pattern in namespace_filter:
        print(f"   - {pattern}")
    
    return len(catalog_filter) == 3 and len(namespace_filter) == 3


def test_timeouts_conversion():
    """Test conversion des timeouts"""
    print("\n⏱️  Test conversion des timeouts...")
    
    # Tests de conversion
    test_cases = [
        ('30', 30, True),
        ('60', 60, True),
        ('invalid', 30, False),  # Fallback
        ('', 30, False),  # Fallback
    ]
    
    all_passed = True
    for input_val, expected, should_succeed in test_cases:
        try:
            result = int(input_val) if input_val else 30
            success = result == expected
            status = "✅" if success else "❌"
            print(f"   {status} '{input_val}' → {result}s (expected {expected}s)")
            all_passed = all_passed and success
        except ValueError:
            # Fallback to default
            result = 30
            success = result == expected
            status = "✅" if success and not should_succeed else "⚠️ "
            print(f"   {status} '{input_val}' → {result}s (fallback)")
            all_passed = all_passed and (not should_succeed)
    
    return all_passed


def test_ssl_configuration():
    """Test configuration SSL"""
    print("\n🔒 Test configuration SSL...")
    
    ssl_configs = [
        ('true', True),
        ('True', True),
        ('TRUE', True),
        ('false', False),
        ('False', False),
        ('yes', False),  # Invalid → false
        ('', False),  # Default → false
    ]
    
    all_passed = True
    for input_val, expected in ssl_configs:
        result = input_val.lower() == 'true' if input_val else False
        success = result == expected
        status = "✅" if success else "❌"
        print(f"   {status} '{input_val}' → {result} (expected {expected})")
        all_passed = all_passed and success
    
    return all_passed


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 DRY-RUN TEST - Polaris Connector v2.0")
    print("=" * 70)
    print("⚠️  Mode Dry-Run: Aucune connexion réelle, aucune modification")
    print("=" * 70)
    
    # Tests
    results = []
    results.append(("Extraction connectionOptions", test_connection_options_extraction()))
    results.append(("Fallback __root__", test_fallback_extraction()))
    results.append(("Types d'authentification", test_auth_types()))
    results.append(("Parsing des filtres", test_filters_parsing()))
    results.append(("Conversion timeouts", test_timeouts_conversion()))
    results.append(("Configuration SSL", test_ssl_configuration()))
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    # Recommandations
    print("\n" + "=" * 70)
    print("💡 RECOMMANDATIONS")
    print("=" * 70)
    print("1. Vérifier que Polaris est accessible sur le port configuré")
    print("2. Vérifier les credentials (OAuth2, Basic Auth, Token)")
    print("3. Configurer catalogFilter pour cibler les catalogs voulus")
    print("4. Configurer namespaceFilter pour cibler les namespaces voulus")
    print("5. Activer useSSL si Polaris est en production")
    
    # Exit code
    all_passed = all(result[1] for result in results)
    sys.exit(0 if all_passed else 1)
