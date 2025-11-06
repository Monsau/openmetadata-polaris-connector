# 🚀 Guide d'Installation Rapide - Polaris Connector v2.0

**Date:** 6 novembre 2025  
**Version:** 2.0.0  
**Commit:** d088624

---

## ✅ Problèmes Corrigés

1. ✅ **`'NoneType' object has no attribute 'prepare'`**
   - Ajout méthode `create()` factory
   - Correction du logger OpenMetadata
   - Initialisation de `self.status`
   - Déplacement de l'authentification vers `prepare()`

2. ✅ **`error in 'egg_base' option: 'connectors' does not exist`**
   - Ajout `pyproject.toml` (PEP 517/518)
   - Correction `setup.py` (package structure)
   - Mise à jour entry_points

---

## 📦 Installation sur Serveur OpenMetadata

### Étape 1: Se connecter au serveur

```bash
ssh user@openmetadata-server
```

### Étape 2: Activer l'environnement Python

```bash
# Environnement Airflow (chemin courant)
source /opt/airflow/ingestion/bin/activate

# OU environnement OpenMetadata
source /opt/openmetadata/venv/bin/activate
```

### Étape 3: Désinstaller l'ancienne version

```bash
pip uninstall -y openmetadata-polaris-connector
```

### Étape 4: Cloner/Mettre à jour le repository

**Nouvelle installation:**
```bash
cd /opt/airflow/ingestion
git clone https://github.com/Monsau/openmetadata-polaris-connector.git polaris
cd polaris
```

**Mise à jour existante:**
```bash
cd /opt/airflow/ingestion/polaris
git pull origin main
```

### Étape 5: Installer le connecteur v2.0

```bash
# Installation moderne (pip >= 21.3)
pip install -e .

# OU si erreur, forcer PEP 517
pip install --use-pep517 -e .
```

**Sortie attendue:**
```
Building editable for openmetadata-polaris-connector (pyproject.toml): finished
Successfully built openmetadata-polaris-connector
Successfully installed openmetadata-polaris-connector-2.0.0
```

### Étape 6: Vérifier l'installation

```bash
python -c "from polaris_connector import PolarisSource; print('✅ Import OK'); print('Version: 2.0.0'); print('Has create:', hasattr(PolarisSource, 'create')); print('Has prepare:', hasattr(PolarisSource, 'prepare'))"
```

**Sortie attendue:**
```
✅ Import OK
Version: 2.0.0
Has create: True
Has prepare: True
```

### Étape 7: Redémarrer les services OpenMetadata

```bash
# Docker Compose
docker-compose restart ingestion

# OU Systemd
sudo systemctl restart airflow-scheduler
sudo systemctl restart airflow-worker
sudo systemctl restart openmetadata-ingestion
```

---

## 🧪 Test de Connexion

### Via UI OpenMetadata

1. Aller sur `https://your-openmetadata.com`
2. `Settings` → `Services` → `Database Services` → `Polaris`
3. Cliquer sur `Test Connection`
4. Devrait afficher: ✅ **Connection successful**

### Via CLI (optionnel)

```bash
# Test dry-run (depuis le répertoire du connecteur)
cd /opt/airflow/ingestion/polaris
python test_polaris_dry_run.py
```

**Résultats attendus:**
```
✅ PASS - Extraction connectionOptions
✅ PASS - Fallback __root__
✅ PASS - Types d'authentification
✅ PASS - Parsing des filtres
✅ PASS - Conversion timeouts
✅ PASS - Configuration SSL
```

---

## 🔄 Relancer le Pipeline d'Ingestion

### Option 1: Via UI OpenMetadata

1. `Settings` → `Services` → `Database Services` → `Polaris`
2. Onglet `Ingestions`
3. Cliquer sur votre pipeline de métadonnées
4. Bouton `Re-run` en haut à droite

### Option 2: Via Airflow UI

1. Aller sur `http://your-airflow:8080`
2. Rechercher le DAG du pipeline Polaris
3. Trigger manuellement le DAG

### Option 3: Via CLI

```bash
# Trigger via airflow CLI
airflow dags trigger <polaris_dag_id>

# Voir les logs en temps réel
airflow tasks logs <dag_id> <task_id> <execution_date> -f
```

---

## 📊 Vérification Post-Installation

### Checklist

- [ ] Connecteur installé (`pip show openmetadata-polaris-connector`)
- [ ] Version 2.0.0 confirmée
- [ ] Import Python fonctionne
- [ ] Services redémarrés
- [ ] Test Connection réussi dans UI
- [ ] Pipeline relancé
- [ ] Logs montrent `✅ PolarisSource initialized`
- [ ] Tables apparaissent dans OpenMetadata

### Commande de validation complète

```bash
#!/bin/bash
echo "=== Validation Polaris Connector v2.0 ==="

# 1. Version installée
echo -e "\n1. Version installée:"
pip show openmetadata-polaris-connector | grep Version

# 2. Import Python
echo -e "\n2. Import Python:"
python -c "from polaris_connector import PolarisSource; print('✅ OK')" 2>&1

# 3. Méthodes requises
echo -e "\n3. Méthodes requises:"
python -c "
from polaris_connector import PolarisSource
for m in ['create', 'prepare', '_iter', 'next_record']:
    print(f'✅ {m}' if hasattr(PolarisSource, m) else f'❌ {m}')
" 2>&1

# 4. Services actifs
echo -e "\n4. Services OpenMetadata:"
systemctl is-active airflow-scheduler && echo "✅ Scheduler" || echo "❌ Scheduler"
systemctl is-active airflow-worker && echo "✅ Worker" || echo "❌ Worker"

echo -e "\n=== Validation terminée ==="
```

---

## 🐛 Troubleshooting

### Problème: `error in 'egg_base' option: 'connectors' does not exist`

**Solution:**
```bash
cd /opt/airflow/ingestion/polaris
git pull origin main  # S'assurer d'avoir commit d088624 ou ultérieur
pip install --use-pep517 -e .
```

### Problème: `DEPRECATION: Legacy editable install`

**Cause:** Ancienne version de pip ou setuptools

**Solution:**
```bash
pip install --upgrade pip setuptools wheel
pip install --use-pep517 -e .
```

### Problème: `ModuleNotFoundError: No module named 'polaris_connector'`

**Solution:**
```bash
# Vérifier l'environnement virtuel actif
which python
pip list | grep polaris

# Réinstaller dans le bon environnement
source /opt/airflow/ingestion/bin/activate
pip install -e /opt/airflow/ingestion/polaris
```

### Problème: Pipeline reste en "Running"

**Solution:**
```bash
# Vérifier les workers
airflow celery worker list

# Redémarrer le scheduler
sudo systemctl restart airflow-scheduler

# Vérifier la queue Celery
airflow tasks list <dag_id> --tree
```

---

## 📝 Configuration OpenMetadata

### Paramètres Requis dans l'UI

**Connection Details:**
- **Host:** `polaris.company.com` (votre serveur Polaris)
- **Port:** `8181` (port par défaut)
- **Use SSL:** `true` (si HTTPS)

**Authentication (OAuth2):**
- **Auth Type:** `oauth2`
- **Client ID:** Votre client ID OAuth2
- **Client Secret:** Votre client secret
- **Token URL:** `/v1/oauth/token` (ou votre endpoint)

**Filters (optionnels):**
- **Catalog Filter:** `prod_catalog,staging_catalog` (virgule-séparée)
- **Namespace Filter:** `sales.*,finance.*` (patterns regex)

**Tags (optionnels):**
- **Default Tags:** `Source.Polaris,Type.Iceberg`
- **Classification Enabled:** `true`

---

## 🆘 Support

**En cas de problème:**

1. **Vérifier la version Git:**
   ```bash
   cd /opt/airflow/ingestion/polaris
   git log --oneline -1
   # Doit afficher: d088624 fix: update packaging configuration
   ```

2. **Collecter les logs:**
   ```bash
   # Installation
   pip install -e . 2>&1 | tee install.log
   
   # Pipeline
   tail -n 200 /opt/airflow/logs/dag_id=*/task_id=*/latest.log > pipeline.log
   ```

3. **Contacter le support:**
   - **Email:** mfonsau@talentys.eu
   - **GitHub Issues:** https://github.com/Monsau/openmetadata-polaris-connector/issues

---

## 📚 Documentation

- **README:** [README.md](https://github.com/Monsau/openmetadata-polaris-connector#readme)
- **Configuration:** [docs/polaris/CONFIGURATION.md](docs/polaris/CONFIGURATION.md)
- **Quick Start:** [docs/polaris/QUICK_START.md](docs/polaris/QUICK_START.md)

---

**Version du Guide:** 2.0  
**Dernière mise à jour:** 6 novembre 2025  
**Commit:** d088624
