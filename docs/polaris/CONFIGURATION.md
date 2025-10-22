# Configuration du Connecteur Polaris pour OpenMetadata

## 📋 Paramètres de Configuration

### ⚙️ Paramètres Obligatoires

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `host` | string | Hostname Polaris | `"polaris.company.com"` |
| `authType` | string | Type d'auth | `"oauth2"`, `"api_key"`, `"basic"` |

### ⚙️ Paramètres OAuth2

| Paramètre | Type | Description |
|-----------|------|-------------|
| `clientId` | string | OAuth2 Client ID |
| `clientSecret` | string | OAuth2 Client Secret |
| `tokenUrl` | string | Token endpoint (default: `/v1/oauth/token`) |

### ⚙️ Paramètres Optionnels

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `port` | string | `"8181"` | Port Polaris |
| `useSSL` | string | `"false"` | Utiliser HTTPS |
| `catalogFilter` | string | `""` | Catalogs à ingérer (séparés par virgules) |
| `namespaceFilter` | string | `""` | Namespaces à ingérer (séparés par virgules) |
| `classificationEnabled` | string | `"true"` | Activer tagging automatique |
| `defaultTags` | string | `""` | Tags par défaut (séparés par virgules) |
| `connectionTimeout` | string | `"30"` | Timeout connexion (secondes) |
| `requestTimeout` | string | `"60"` | Timeout requêtes (secondes) |

---

## 🔐 Exemples de Configuration par Auth

### OAuth2 (Production Recommandé)

```json
{
  "type": "Polaris",
  "sourcePythonClass": "polaris_connector.polaris_source.PolarisSource",
  "connectionOptions": {
    "host": "polaris.company.com",
    "port": "8181",
    "useSSL": "true",
    "authType": "oauth2",
    "clientId": "openmetadata-client",
    "clientSecret": "your-secret-key",
    "tokenUrl": "/v1/oauth/token",
    "catalogFilter": "production,staging",
    "classificationEnabled": "true",
    "defaultTags": "Source.Polaris,Format.Iceberg"
  }
}
```

### API Key (Dev/Test)

```json
{
  "type": "Polaris",
  "sourcePythonClass": "polaris_connector.polaris_source.PolarisSource",
  "connectionOptions": {
    "host": "localhost",
    "port": "8181",
    "useSSL": "false",
    "authType": "api_key",
    "apiKey": "polaris-api-key-12345",
    "classificationEnabled": "true"
  }
}
```

### Basic Auth

```json
{
  "type": "Polaris",
  "sourcePythonClass": "polaris_connector.polaris_source.PolarisSource",
  "connectionOptions": {
    "host": "polaris-dev.local",
    "port": "8181",
    "useSSL": "false",
    "authType": "basic",
    "username": "admin",
    "password": "admin123",
    "catalogFilter": "dev_catalog",
    "namespaceFilter": "sandbox"
  }
}
```

---

## 🎯 Filtrage et Performance

### Filtrer par Catalog

```json
{
  "catalogFilter": "sales,finance,marketing"
}
```
Ingère uniquement les catalogs listés.

### Filtrer par Namespace

```json
{
  "namespaceFilter": "production,staging"
}
```
Ingère uniquement les namespaces listés (tous catalogs).

### Combinaison

```json
{
  "catalogFilter": "sales",
  "namespaceFilter": "production,staging"
}
```
Ingère uniquement `sales.production` et `sales.staging`.

### Optimisation Timeouts

```json
{
  "connectionTimeout": "60",
  "requestTimeout": "120"
}
```
Pour environnements à haute latence.

---

## ✅ Vérification Configuration

### Test dans les Logs

```
✅ Polaris connector initialized for polaris.company.com:8181
✅ OAuth2 authentication successful
✅ Polaris connection test successful
Discovered 3 catalogs
Found 5 namespaces in catalog production
Found 42 tables in production.sales
✅ Table created/updated: PolarisService.production.sales.orders
```

---

**Version** : 2.0.0  
**Auteur** : Mustapha Fonsau
