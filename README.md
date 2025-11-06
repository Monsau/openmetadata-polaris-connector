# 🌌 Polaris Connector pour OpenMetadata v2.0.0

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/Monsau/openmetadata-polaris-connector)
[![Architecture](https://img.shields.io/badge/architecture-Dremio--like-blue.svg)](docs/polaris/ARCHITECTURE.md)
[![Status](https://img.shields.io/badge/status-bugfixed-success.svg)](BUGFIX_SUMMARY.md)

> Connecteur OpenMetadata enterprise-grade pour l'ingestion de métadonnées depuis Apache Polaris avec architecture simplifiée (modèle Dremio).

## 🐛 Important - Bugfix du 6 Nov 2025

**Si vous avez l'erreur:** `AttributeError: 'NoneType' object has no attribute 'prepare'`  
**OU:** `error in 'egg_base' option: 'connectors' does not exist`

➡️ **Solution:** [Guide d'installation v2.0](INSTALL.md)

**Correctifs v2.0:**
- ✅ Pipeline OpenMetadata qui échoue à l'instanciation
- ✅ Logs montrant `'NoneType' object has no attribute 'prepare'`
- ✅ Erreur de packaging `'connectors' does not exist`
- ✅ Ajout `pyproject.toml` (PEP 517/518)
- ✅ Architecture modernisée

**Action requise:** Mettre à jour vers commit `aaedd92` ou ultérieur

---

## 📋 Table des Matières

- [Vue d'ensemble](#-vue-densemble)
- [Architecture v2.0](#-architecture-v20)
- [Quick Start](#-quick-start-5-minutes)
- [Configuration](#-configuration)
- [Dry-Run & Tests](#-dry-run--tests)
- [Fonctionnalités](#-fonctionnalités)
- [Documentation](#-documentation)

---

## 🎯 Vue d'ensemble

### Qu'est-ce que ce connecteur ?

Le **Polaris Connector v2.0** est un connecteur OpenMetadata simplifié qui permet d'ingérer automatiquement les métadonnées de votre catalog Apache Polaris (Iceberg REST Catalog).

### Qu'est-ce qu'Apache Polaris ?

Apache Polaris est un **catalog REST Iceberg** open-source créé par Snowflake :
- Gère les métadonnées de tables Iceberg
- Support multi-cloud (AWS, Azure, GCP)
- RBAC natif (role-based access control)
- Compatible avec Spark, Trino, Flink

### Points clés

✅ **Architecture simplifiée** : 4 fichiers Python (modèle Dremio)  
✅ **Configuration via UI** : 100% via `connectionOptions` (pas de YAML)  
✅ **Multi-auth** : OAuth2, Basic Auth, Token  
✅ **Catalog multi-tenant** : Namespaces et filtering  
✅ **Classification** : Tagging automatique configurable  
✅ **Dry-run** : Scripts de test sans modification  

---

## 🏗️ Architecture v2.0

```
polaris_connector/
├── polaris_source.py         # Agent unifié 4-en-1
├── manifest.json             # Déclaration OpenMetadata
├── __init__.py               # Exports (v2.0.0)
└── core/
    ├── sync_engine.py        # Client REST + découverte
    └── __init__.py           # Exports core
```

### Comparaison v1 → v2

| Aspect | v1.x (Ancienne) | v2.0 (Nouvelle) |
|--------|-----------------|-----------------|
| Fichiers Python | 12+ | **4** |
| Lignes de code | ~2500 | **~580** |
| Configuration | YAML files | **100% UI (connectionOptions)** |
| Documentation | README only | **3 guides pro** |

---

## 🚀 Quick Start (5 Minutes)

### Prérequis

- OpenMetadata 1.3+ installé
- Python 3.10+
- Docker (pour Polaris local)
- Accès à un catalog Polaris

### Installation

```bash
# 1. Copier le connecteur dans OpenMetadata
docker cp polaris_connector/ openmetadata_ingestion:/opt/airflow/custom_connectors/

# 2. Redémarrer le service d'ingestion
docker compose restart ingestion

# 3. Vérifier les logs
docker logs -f openmetadata_ingestion | grep PolarisSource
```

### Configuration Polaris Local (Test)

```bash
# 1. Démarrer Polaris en local
docker run -d \
  -p 8181:8181 \
  -p 8182:8182 \
  -e POLARIS_ROOT_USERNAME=admin \
  -e POLARIS_ROOT_PASSWORD=admin123 \
  --name polaris \
  apache/polaris:latest

# 2. Créer un catalog de test
curl -X POST http://localhost:8181/api/catalog/v1/catalogs \
  -H "Content-Type: application/json" \
  -u admin:admin123 \
  -d '{
    "name": "test_catalog",
    "type": "ICEBERG",
    "properties": {
      "warehouse": "s3://my-bucket/warehouse/"
    }
  }'

# 3. Créer un namespace
curl -X POST http://localhost:8181/api/catalog/v1/catalogs/test_catalog/namespaces \
  -H "Content-Type: application/json" \
  -u admin:admin123 \
  -d '{
    "namespace": ["sales"],
    "properties": {}
  }'
```

---

## ⚙️ Configuration

### Configuration via OpenMetadata UI

1. **Settings** → **Services** → **Databases** → **Add Service**
2. Sélectionner **Custom Database**
3. Utiliser cette configuration :

```json
{
  "type": "Polaris",
  "sourcePythonClass": "polaris_connector.polaris_source.PolarisSource",
  "connectionOptions": {
    "host": "polaris",
    "port": "8181",
    "useSSL": "false",
    "authType": "basic",
    "username": "admin",
    "password": "admin123",
    "catalogFilter": "test_catalog",
    "namespaceFilter": "sales.*",
    "classificationEnabled": "true",
    "defaultTags": "Source.Polaris,Type.Iceberg"
  }
}
```

### Paramètres connectionOptions

#### Obligatoires

| Paramètre | Type | Description |
|-----------|------|-------------|
| `host` | string | Hostname du serveur Polaris |
| `port` | string | Port (défaut: `8181`) |
| `authType` | string | `basic`, `oauth2`, `token` |

#### Authentification Basic Auth

| Paramètre | Type | Description |
|-----------|------|-------------|
| `username` | string | Nom d'utilisateur |
| `password` | string | Mot de passe |

#### Authentification OAuth2

| Paramètre | Type | Description |
|-----------|------|-------------|
| `clientId` | string | Client ID OAuth2 |
| `clientSecret` | string | Client Secret OAuth2 |
| `tokenUrl` | string | URL du token endpoint |

#### Authentification Token

| Paramètre | Type | Description |
|-----------|------|-------------|
| `bearerToken` | string | JWT ou Bearer token |

#### Optionnels

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `useSSL` | `"true"` | Utiliser HTTPS |
| `verifyCertificate` | `"true"` | Vérifier certificat SSL |
| `catalogFilter` | `"*"` | Regex pour filtrer catalogs |
| `namespaceFilter` | `"*"` | Regex pour filtrer namespaces |
| `classificationEnabled` | `"true"` | Activer auto-tagging |
| `defaultTags` | `""` | Tags par défaut (séparés par virgules) |
| `timeout` | `"30"` | Timeout requêtes (secondes) |
| `maxRetries` | `"3"` | Nombre de retry en cas d'erreur |

### Exemples de Configuration

#### 1. Polaris Local (Dev)

```json
{
  "connectionOptions": {
    "host": "localhost",
    "port": "8181",
    "useSSL": "false",
    "authType": "basic",
    "username": "admin",
    "password": "admin123",
    "catalogFilter": "*",
    "namespaceFilter": "*"
  }
}
```

#### 2. Polaris Production (OAuth2)

```json
{
  "connectionOptions": {
    "host": "polaris.company.com",
    "port": "443",
    "useSSL": "true",
    "verifyCertificate": "true",
    "authType": "oauth2",
    "clientId": "openmetadata-client",
    "clientSecret": "secret123",
    "tokenUrl": "https://auth.company.com/oauth2/token",
    "catalogFilter": "prod_.*",
    "namespaceFilter": "(sales|finance)\\..+",
    "classificationEnabled": "true",
    "defaultTags": "Environment.Production,Compliance.GDPR"
  }
}
```

#### 3. Polaris AWS (Bearer Token)

```json
{
  "connectionOptions": {
    "host": "polaris.us-east-1.amazonaws.com",
    "port": "443",
    "useSSL": "true",
    "authType": "token",
    "bearerToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "catalogFilter": "analytics.*",
    "timeout": "60",
    "maxRetries": "5"
  }
}
```

---

## 🧪 Dry-Run & Tests

### Script de Test (Dry-Run)

Créez `test_polaris_connector.py` :

```python
"""
Dry-run test pour Polaris Connector
Test la configuration sans modifier OpenMetadata
"""

import sys
sys.path.insert(0, 'polaris_connector')

from polaris_connector.core.sync_engine import PolarisRestClient, PolarisAutoDiscovery

def test_connection():
    """Test connexion Polaris"""
    print("🧪 Test de connexion Polaris...")
    
    # Configuration
    client = PolarisRestClient(
        host="localhost",
        port=8181,
        use_ssl=False,
        auth_type="basic",
        username="admin",
        password="admin123"
    )
    
    # Test connexion
    if client.test_connection():
        print("✅ Connexion Polaris réussie")
        return True
    else:
        print("❌ Connexion Polaris échouée")
        return False

def test_list_catalogs():
    """Test listage des catalogs"""
    print("\n📂 Test de listage des catalogs...")
    
    # Créer client
    client = PolarisRestClient(
        host="localhost",
        port=8181,
        use_ssl=False,
        auth_type="basic",
        username="admin",
        password="admin123"
    )
    
    discovery = PolarisAutoDiscovery(client)
    
    # Lister catalogs
    catalogs = discovery.list_catalogs()
    print(f"✅ Découvert {len(catalogs)} catalog(s)")
    
    for catalog in catalogs:
        print(f"  - {catalog.get('name')} (type: {catalog.get('type', 'ICEBERG')})")
    
    return len(catalogs) > 0

def test_list_namespaces():
    """Test listage des namespaces"""
    print("\n🗂️  Test de listage des namespaces...")
    
    # Créer client
    client = PolarisRestClient(
        host="localhost",
        port=8181,
        use_ssl=False,
        auth_type="basic",
        username="admin",
        password="admin123"
    )
    
    discovery = PolarisAutoDiscovery(client)
    
    # Lister catalogs
    catalogs = discovery.list_catalogs()
    
    if not catalogs:
        print("⚠️  Aucun catalog trouvé")
        return False
    
    # Prendre le premier catalog
    catalog_name = catalogs[0]['name']
    namespaces = discovery.list_namespaces(catalog_name)
    
    print(f"✅ Découvert {len(namespaces)} namespace(s) dans '{catalog_name}'")
    
    for ns in namespaces[:5]:  # Afficher les 5 premiers
        print(f"  - {'.'.join(ns)}")
    
    return len(namespaces) > 0

def test_list_tables():
    """Test listage des tables"""
    print("\n📊 Test de listage des tables...")
    
    # Créer client
    client = PolarisRestClient(
        host="localhost",
        port=8181,
        use_ssl=False,
        auth_type="basic",
        username="admin",
        password="admin123"
    )
    
    discovery = PolarisAutoDiscovery(client)
    
    # Lister catalogs
    catalogs = discovery.list_catalogs()
    
    if not catalogs:
        print("⚠️  Aucun catalog trouvé")
        return False
    
    # Prendre le premier catalog
    catalog_name = catalogs[0]['name']
    namespaces = discovery.list_namespaces(catalog_name)
    
    if not namespaces:
        print("⚠️  Aucun namespace trouvé")
        return False
    
    # Prendre le premier namespace
    namespace = namespaces[0]
    tables = discovery.list_tables(catalog_name, namespace)
    
    print(f"✅ Découvert {len(tables)} table(s) dans '{catalog_name}.{'.'.join(namespace)}'")
    
    for table in tables:
        print(f"  - {table}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 DRY-RUN TEST - Polaris Connector v2.0")
    print("=" * 60)
    
    # Tests
    results = []
    results.append(("Connexion Polaris", test_connection()))
    results.append(("Liste catalogs", test_list_catalogs()))
    results.append(("Liste namespaces", test_list_namespaces()))
    results.append(("Liste tables", test_list_tables()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    # Exit code
    all_passed = all(result[1] for result in results)
    sys.exit(0 if all_passed else 1)
```

### Exécution du Dry-Run

```bash
# Installer les dépendances
pip install requests

# Lancer le test
python test_polaris_connector.py
```

### Résultat Attendu

```
============================================================
🧪 DRY-RUN TEST - Polaris Connector v2.0
============================================================
🧪 Test de connexion Polaris...
✅ Connexion Polaris réussie

📂 Test de listage des catalogs...
✅ Découvert 2 catalog(s)
  - test_catalog (type: ICEBERG)
  - prod_catalog (type: ICEBERG)

🗂️  Test de listage des namespaces...
✅ Découvert 3 namespace(s) dans 'test_catalog'
  - sales
  - finance
  - marketing

📊 Test de listage des tables...
✅ Découvert 5 table(s) dans 'test_catalog.sales'
  - orders
  - customers
  - products
  - transactions
  - inventory

============================================================
📊 RÉSUMÉ DES TESTS
============================================================
✅ PASS - Connexion Polaris
✅ PASS - Liste catalogs
✅ PASS - Liste namespaces
✅ PASS - Liste tables
```

---

## ✨ Fonctionnalités

### Métadonnées Iceberg Ingérées

- ✅ **Catalogs** : Tous les catalogs Polaris
- ✅ **Namespaces** : Hiérarchies de namespaces
- ✅ **Tables** : Tables Iceberg avec schema
- ✅ **Colonnes** : Types, contraintes, commentaires
- ✅ **Partitions** : Stratégies de partitionnement
- ✅ **Snapshots** : Historique des versions

### Authentification

- ✅ **Basic Auth** : Username + Password
- ✅ **OAuth2** : Client Credentials Flow
- ✅ **Bearer Token** : JWT statique

### Fonctionnalités Avancées

- ✅ **Filtering** : Regex pour catalogs/namespaces
- ✅ **Classification** : Tags automatiques
- ✅ **RBAC** : Respecte les permissions Polaris
- ✅ **Timeout/Retry** : Configuration réseau avancée
- ✅ **SSL/TLS** : Support certificats custom

---

## 📚 Documentation

### Guides Complets

1. **[ARCHITECTURE.md](docs/polaris/ARCHITECTURE.md)** - Architecture technique v2.0
   - Vue d'ensemble et principes
   - Composants et responsabilités
   - Flux d'ingestion (diagrammes)
   - Modèle REST API

2. **[CONFIGURATION.md](docs/polaris/CONFIGURATION.md)** - Guide configuration
   - Tous les paramètres `connectionOptions`
   - Exemples par use case
   - Troubleshooting

3. **[QUICK_START.md](docs/polaris/QUICK_START.md)** - Démarrage rapide
   - Installation en 2 min
   - Configuration en 3 min
   - Premier test

---

## 🔧 Troubleshooting

### Erreur : "Polaris connection test failed"

**Solution** :
- Vérifier `host` et `port`
- Vérifier credentials (`username`/`password` ou `clientId`/`clientSecret`)
- Vérifier SSL : `useSSL` doit correspondre au serveur (http vs https)

### Erreur : "No catalogs discovered"

**Solution** :
- Vérifier permissions utilisateur dans Polaris
- Vérifier `catalogFilter` (regex valide)
- Lister manuellement : `curl -u admin:admin123 http://localhost:8181/api/catalog/v1/catalogs`

### Erreur : "SSL certificate verification failed"

**Solution** :
- Si certificat self-signed : `"verifyCertificate": "false"`
- Sinon, installer certificat CA : `pip install certifi && export REQUESTS_CA_BUNDLE=/path/to/ca.crt`

### Logs de Debug

```bash
# Voir les logs du connecteur
docker logs -f openmetadata_ingestion | grep -A 10 "PolarisSource"

# Activer logs verbeux (dans connectionOptions)
"enableVerboseLogging": "true"
```

---

## 🤝 Support & Contribution

- **Issues** : [GitHub Issues](https://github.com/Monsau/openmetadata-polaris-connector/issues)
- **Discussions** : [GitHub Discussions](https://github.com/Monsau/openmetadata-polaris-connector/discussions)
- **Email** : mfonsau@talentys.eu

### Contribuer

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📄 License

Apache License 2.0 - Voir [LICENSE](LICENSE) pour plus de détails.

---

**Version** : 2.0.0  
**Dernière mise à jour** : Octobre 2025  
**Auteur** : Mustapha Fonsau (mfonsau@talentys.eu)  
**Architecture** : Modèle Dremio simplifié
