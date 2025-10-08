
# Polaris ↔ OpenMetadata Connector

Welcome to the Polaris ↔ OpenMetadata connector! This project provides a professional, enterprise-grade solution for automated metadata ingestion from Apache Polaris (Iceberg catalog) into OpenMetadata.

---

##  Documentation

- **[Full Technical Documentation (multi-language)](./full_documentation.md)**
- [Français](./README-fr.md) | [Español](./README-es.md) | [العربية](./README-ar.md)

---

##  Quick Start

1. **Clone the repository**
   ```powershell
   git clone <repository-url>
   cd polaris
   ```
2. **Set up Python environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. **Configure your connection**
   - Copy and edit `config/polaris-config.yaml.example` to `config/polaris-config.yaml`.
   - Set your Polaris and OpenMetadata endpoints and credentials.
4. **Start infrastructure (optional)**
   ```powershell
   docker-compose up -d
   ```
5. **Run health check**
   ```powershell
   python -m src.polaris_ingestion.main --health-check-only
   ```
6. **Ingest metadata**
   ```powershell
   python -m src.polaris_ingestion.main
   ```

For advanced configuration, troubleshooting, and architecture details, see [full_documentation.md](./full_documentation.md).

---

## ️ Project Structure

- `full_documentation.md` — Complete technical guide (EN, FR, ES, AR)
- `README-fr.md`, `README-es.md`, `README-ar.md` — Language-specific quickstart and links
- `requirements.txt`, `requirements-dev.txt` — Python dependencies
- `docker-compose.yml` — Infrastructure services
- `config/` — Configuration files
- `src/` — Source code
- `tests/` — Test suites
- `docs/` — Additional documentation

---

##  Contributing & Support

We welcome contributions in all languages! For details, see the [contribution guidelines](./full_documentation.md#-contributing--contribution--contribución--المساهمة).

For support, open a GitHub issue or see the [Support section](./full_documentation.md#-support--assistance--soporte--الدعم).

---

**Built with ️ for the global data community**