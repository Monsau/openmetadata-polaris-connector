# 🔧 Guide de Réinstallation - Polaris Connector

**Suite au bugfix du 6 novembre 2025**

---

## 📋 Prérequis

- OpenMetadata 1.3+ installé
- Accès SSH/shell au serveur OpenMetadata
- Droits d'administration OpenMetadata

---

## 🚀 Étapes de Réinstallation

### 1. Se connecter au serveur OpenMetadata

```bash
ssh user@openmetadata-server
```

### 2. Activer l'environnement Python d'OpenMetadata

```bash
# Localiser l'environnement virtuel OpenMetadata
# Chemins courants:
source /opt/airflow/ingestion/bin/activate
# OU
source /opt/openmetadata/venv/bin/activate
# OU
source ~/.local/share/virtualenvs/openmetadata-*/bin/activate
```

### 3. Désinstaller l'ancienne version (si installée)

```bash
pip uninstall -y polaris-connector
```

### 4. Cloner/Mettre à jour le repository

**Option A: Nouvelle installation**
```bash
cd /opt/openmetadata/connectors/
git clone https://github.com/Monsau/openmetadata-polaris-connector.git
cd openmetadata-polaris-connector
```

**Option B: Mise à jour existante**
```bash
cd /opt/openmetadata/connectors/openmetadata-polaris-connector
git pull origin main
```

### 5. Installer le connecteur corrigé

```bash
pip install -e .
```

**Sortie attendue:**
```
Successfully installed polaris-connector-2.0.0
```

### 6. Vérifier l'installation

```bash
python -c "from polaris_connector import PolarisSource; print('✅ Import OK'); print('Has create:', hasattr(PolarisSource, 'create')); print('Has prepare:', hasattr(PolarisSource, 'prepare'))"
```

**Sortie attendue:**
```
✅ Import OK
Has create: True
Has prepare: True
```

### 7. Redémarrer les services OpenMetadata

```bash
# Pour installation Docker
docker-compose restart ingestion

# Pour installation systemd
sudo systemctl restart openmetadata-ingestion
sudo systemctl restart airflow-scheduler
sudo systemctl restart airflow-worker

# Vérifier les logs
tail -f /opt/airflow/logs/scheduler/latest/*.log
```

---

## 🔍 Vérification du Pipeline

### 1. Accéder à l'interface OpenMetadata

```
https://your-openmetadata-url.com
```

### 2. Naviguer vers le service Polaris

```
Settings → Services → Database Services → Polaris
```

### 3. Vérifier la configuration

- ✅ Connection Details affichées
- ✅ Test Connection réussit
- ✅ Onglet "Ingestions" accessible

### 4. Relancer l'ingestion

```
Ingestions → Metadata → [Nom du pipeline] → Re-run
```

**Pipeline ID:** `60407c96-87fe-4da8-bf42-84f98a1b1151`

### 5. Surveiller l'exécution

```bash
# Logs Airflow
tail -f /opt/airflow/logs/dag_id=*/run_id=*/task_id=*/attempt=*.log

# OU via UI OpenMetadata
Ingestions → View Logs
```

**Messages attendus:**
```
INFO - ✅ PolarisSource initialized for polaris.company.com:8181
INFO - ✅ Preparing to ingest metadata from Polaris...
INFO - Discovered X catalogs
INFO - Found Y tables in catalog.namespace
INFO - ✅ Table yielded: catalog.namespace.table
```

---

## 🐛 Troubleshooting

### Problème: "ModuleNotFoundError: No module named 'polaris_connector'"

**Solution:**
```bash
# Vérifier l'environnement virtuel
which python
pip list | grep polaris

# Réinstaller
pip install -e /opt/openmetadata/connectors/openmetadata-polaris-connector
```

### Problème: "AttributeError: 'NoneType' object has no attribute 'prepare'"

**Cause:** Version non corrigée encore installée

**Solution:**
```bash
# Forcer la réinstallation
pip uninstall -y polaris-connector
cd /opt/openmetadata/connectors/openmetadata-polaris-connector
git pull origin main
pip install -e .

# Redémarrer les services
sudo systemctl restart airflow-scheduler airflow-worker
```

### Problème: "Polaris authentication failed"

**Cause:** Configuration d'authentification incorrecte

**Solution:**
```bash
# Vérifier la configuration dans OpenMetadata UI
Settings → Services → Polaris → Edit Connection

# Paramètres requis selon authType:
# - oauth2: clientId, clientSecret, tokenUrl
# - basic: username, password
# - api_key: apiKey
```

### Problème: Pipeline reste en "Running" indéfiniment

**Solution:**
```bash
# Vérifier les workers Airflow
airflow celery worker status

# Relancer le scheduler
sudo systemctl restart airflow-scheduler

# Vérifier la queue
airflow tasks list <dag_id> --tree
```

---

## 📊 Validation Post-Installation

### Checklist

- [ ] Connecteur réinstallé (`pip list | grep polaris`)
- [ ] Import Python fonctionne
- [ ] Services OpenMetadata redémarrés
- [ ] Test Connection réussit dans UI
- [ ] Pipeline relancé manuellement
- [ ] Logs montrent authentification réussie
- [ ] Catalogs découverts dans les logs
- [ ] Tables apparaissent dans OpenMetadata UI

### Commande de validation complète

```bash
#!/bin/bash
echo "🔍 Validation Polaris Connector..."

# 1. Check installation
echo "1. Checking installation..."
pip show polaris-connector || echo "❌ Not installed"

# 2. Check import
echo "2. Checking import..."
python -c "from polaris_connector import PolarisSource; print('✅ Import OK')" || echo "❌ Import failed"

# 3. Check methods
echo "3. Checking required methods..."
python -c "
from polaris_connector import PolarisSource
methods = ['create', 'prepare', '_iter', 'next_record']
for m in methods:
    status = '✅' if hasattr(PolarisSource, m) else '❌'
    print(f'{status} {m}')
"

# 4. Check services
echo "4. Checking OpenMetadata services..."
systemctl is-active airflow-scheduler || echo "⚠️  Scheduler not running"
systemctl is-active airflow-worker || echo "⚠️  Worker not running"

echo "✅ Validation complete!"
```

---

## 🆘 Support

**En cas de problème persistant:**

1. Collecter les logs:
```bash
# Logs installation
pip install -e . 2>&1 | tee install.log

# Logs pipeline
tail -n 500 /opt/airflow/logs/dag_id=*/run_id=latest/task_id=*/attempt=*.log > pipeline.log

# Logs système
journalctl -u airflow-scheduler -n 200 > scheduler.log
```

2. Vérifier la version Git:
```bash
cd /opt/openmetadata/connectors/openmetadata-polaris-connector
git log --oneline -1
# Doit afficher: 223c35f fix: correct OpenMetadata Source implementation
```

3. Contacter le support:
- **Email:** mfonsau@talentys.eu
- **GitHub:** https://github.com/Monsau/openmetadata-polaris-connector/issues

---

## 📝 Notes

- La correction corrige le bug `'NoneType' has no attribute 'prepare'`
- Aucune modification de configuration n'est nécessaire
- Le connecteur est rétrocompatible avec les anciennes configurations
- Les métadonnées déjà ingérées ne seront pas affectées

---

**Version du Guide:** 1.0  
**Date:** 6 novembre 2025  
**Commit:** 223c35f
