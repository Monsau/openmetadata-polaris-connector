# 🚀 Démarrage rapide - Connecteur Polaris

> Version "j'ai 5 minutes" pour faire fonctionner le connecteur

## Installation express

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Tester la configuration
python validate.py

# 3. Configurer votre connexion dans playbooks/ingestion.yaml
# 4. Lancer l'ingestion
metadata ingest -c playbooks/ingestion.yaml
```

## Configuration minimale

Dans `playbooks/ingestion.yaml`, changez juste ces valeurs :

```yaml
connectionOptions:
  host: "VOTRE_SERVEUR_POLARIS"
  client_id: "VOTRE_CLIENT_ID"
  client_secret: "VOTRE_CLIENT_SECRET"

workflowConfig:
  openMetadataServerConfig:
    hostPort: http://VOTRE_OPENMETADATA:8585/api
    securityConfig:
      jwtToken: "VOTRE_JWT_TOKEN"
```

## Problèmes fréquents

- **Module not found** → Vous n'êtes pas dans le bon dossier
- **Auth failed** → Vérifiez vos credentials Polaris
- **Pas de résultats** → Vérifiez que Polaris a des données

📖 **Documentation complète :** Voir [README.md](README.md)