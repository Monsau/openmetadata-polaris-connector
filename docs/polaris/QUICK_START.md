# Quick Start - Connecteur Polaris

## 🚀 Démarrage Rapide en 5 Minutes

---

## Étape 1 : Installation

```bash
# Copier le connecteur dans le conteneur OpenMetadata
cd /path/to/polaris
docker cp polaris_connector/ openmetadata_ingestion:/opt/airflow/custom_connectors/

# Redémarrer le service d'ingestion
docker compose restart ingestion

# Vérifier les logs
docker logs -f openmetadata_ingestion | grep Polaris
```

---

## Étape 2 : Configuration OpenMetadata

### 2.1 Créer un Nouveau Service

1. Ouvrir OpenMetadata UI : `http://localhost:8585`
2. **Settings** → **Services** → **Databases**
3. **Add New Service** → **Custom Database**

### 2.2 Configuration

**Service Name** : `PolarisProduction`

**Connection Config** :
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
    "clientSecret": "your-secret",
    "tokenUrl": "/v1/oauth/token",
    "catalogFilter": "production",
    "classificationEnabled": "true",
    "defaultTags": "Source.Polaris,Tier.Gold"
  }
}
```

### 2.3 Test de Connexion

**Test Connection** → Doit afficher :
```
✅ Polaris connection test successful
✅ OAuth2 authentication successful
```

---

## Étape 3 : Ingestion

### 3.1 Créer Pipeline

1. **Ingestion** → **Add Ingestion**
2. **Name** : `polaris-metadata-ingestion`
3. **Type** : `Metadata`
4. **Schedule** : `0 */12 * * *` (toutes les 12h)

### 3.2 Lancer l'Ingestion

**Run** → Suivre les logs

### Logs Attendus

```
✅ PolarisSource initialized for polaris.company.com:8181
Catalog filter: ['production']
Discovered 1 catalogs
Found 8 namespaces in catalog production
Found 156 tables in production.sales
✅ Table created/updated: PolarisProduction.production.sales.orders
Total tables discovered: 156
```

---

## Étape 4 : Vérifier les Métadonnées

### Explorer les Tables

1. **Explore** → **Tables**
2. Filtrer par **Service** : `PolarisProduction`
3. Cliquer sur une table (ex: `orders`)

### Vérifier le Schema Iceberg

- **Columns** : Types Iceberg convertis (STRING, BIGINT, TIMESTAMP, etc.)
- **Tags** : `Source.Polaris`, `Tier.Gold`
- **Table Type** : `Iceberg`

---

## 🎯 Exemples Avancés

### Multi-Catalog

```json
{
  "catalogFilter": "production,staging,dev"
}
```

### Filtrage Namespace

```json
{
  "catalogFilter": "production",
  "namespaceFilter": "sales,finance"
}
```

---

## 🔧 Troubleshooting

### "Authentication failed"

Vérifier :
- `clientId` et `clientSecret` corrects
- `tokenUrl` accessible
- Polaris accessible depuis le conteneur

### "No catalogs discovered"

Vérifier :
- Permissions du client OAuth2
- `catalogFilter` correct

---

## 📚 Prochaines Étapes

- [Configuration Complète](./CONFIGURATION.md)
- [Architecture](./ARCHITECTURE.md)

---

**Version** : 2.0.0  
**Support** : mfonsau@talentys.eu
