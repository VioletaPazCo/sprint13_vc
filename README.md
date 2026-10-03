# ⚡ Endolla Barcelona — B2G Data Governance & Assurance Dashboard

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://b2g-governance-endolla-bcn.streamlit.app)

🚀 **Live Demo:** [https://b2g-governance-endolla-bcn.streamlit.app](https://b2g-governance-endolla-bcn.streamlit.app)

---

## 📌 Project Overview

**Business-to-Government (B2G) Data Governance**: dashboard and analytics infrastructure for **Endolla Barcelona**, the public electric vehicle (EV) charging network in Barcelona.

The primary objective of this project is to audit telemetry data quality and integrity, detect operational anomalies (ghost ports, status desynchronizations, orphaned records), and provide an interactive, bilingual (Spanish/English) analytical platform to support municipal decision-making and service SLA monitoring.

---

## 🌐 Internationalization & Localization (i18n)

The application features native multi-language support (Spanish 🇪🇸 / English 🇬🇧) designed for international stakeholders, public administrators, and technical auditors:
* **Centralized Translation Engine:** Driven by a modular `translations.py` architecture for dictionary-based text mapping and dynamic UI rendering.
* **Seamless Language Toggle:** Real-time state persistence across pages via Streamlit sidebar context.
* **Localized Analytics:** Dynamic label formatting across interactive Plotly charts, spatial Folium maps, and data tables.

---

## ⚙️ Data Architecture & Medallion Pipeline

The data pipeline follows a **Medallion Architecture (Bronze ➔ Silver ➔ Gold)** to ensure complete data traceability, auditability, and high-performance querying:

    [ Raw Telemetry Logs / Open Data BCN ]
                         │
                         ▼
     [ 01_data_profiling_and_integrity_audit.ipynb ] ➔ Ingestion & Integrity Audit
                         │
                         ▼
     [ 02_medallion_pipeline_etl.ipynb ] ➔ Cleaning, Type Casting & Quarantine (Bronze to Silver)
                         │
                         ├───────► [ Quarantine Tables (.parquet) ] (Orphans, Desynced & Ghost Ports)
                         │
                         ▼
          [ Gold Analytics / Parquet ] ➔ Clean master tables for reporting & downstream app
                         │
                         ▼
          [ Streamlit Application ] ➔ Live Interactive Dashboard

---

## 🛠️ Tech Stack & Tools

* **Core Language & Data Processing:** Python (`Pandas`, `NumPy`, `PyArrow` for high-performance `.parquet` storage).
* **Data Visualization:** `Plotly`, `Folium` (interactive spatial maps for urban mobility analysis).
* **Web App & Deployment:** `Streamlit` (Community Cloud).
* **Architecture & i18n:** Centralized Translation Dictionary Module (`translations.py`), Medallion Pipeline, Automated Quarantine Isolation.

---

## 🔍 Data Quality & Governance Audit Findings

Through the automated data assurance pipeline, the system detects and isolates the following operational anomalies:

* **Orphaned Telemetry Records (`b2g_quarantine_orphans.parquet`):** Telemetry status events referenced to connectors, stations, or locations missing from the active master catalog (classified into Case A, Case B, and non-geolocatable Case C orphans).
* **Silent Infrastructure & Ghost Ports (`b2g_desynced_ghost_ports.parquet`):** Master catalog infrastructure that remains inactive or desynchronized with no telemetry events registered during the auditing period.
* **Timestamp & Epoch Anomalies (`b2g_quarantine_epoch.parquet`):** Corrupted telemetry logs containing default Unix epoch timestamps (`1970-12-31 23:00:00+00:00`).
* **Silver/Gold Optimization:** Cleaned master dimensions and facts (`silver_dim_ports.parquet`, `silver_fact_status.parquet`, `stations_metadata.parquet`) engineered for sub-second dashboard rendering.
---

## 📂 Repository Structure

    .
    ├── .devcontainer/                                  # Development container configuration
    ├── pages/                                          # Secondary dashboard pages
    │   ├── b2g_governance.py                           # B2G Governance & Audit module
    │   └── network_description.py                      # Network evolution & EDA module
    ├── app.py                                          # Main Streamlit application entry point & router
    ├── translations.py                                 # Centralized i18n translation dictionary & helper
    ├── b2g_data_profiling_and_integrity_audit_01.ipynb # Notebook 01: Data Profiling & Audit
    ├── b2g_medallion_pipeline_etl_02.ipynb              # Notebook 02: Medallion ETL & Quarantine
    ├── b2g_quarantine_*.parquet                        # Automated data quality quarantine tables
    ├── silver_*.parquet / stations_metadata.parquet    # Processed Parquet analytical datasets
    ├── sprint13_informe_violeta_correa.pdf             # Executive report on governance findings
    ├── requirements.txt                                # Python project dependencies
    └── README.md                                       # Main documentation

---

## 🚀 How to Run Locally

### Requirements

* Python 3.10 or higher
* Dependencies listed in `requirements.txt`

### Terminal Commands

    git clone https://github.com/VioletaPazCo/b2g-governance-endolla-bcn.git
    cd b2g-governance-endolla-bcn
    pip install -r requirements.txt
    streamlit run app.py

---

## 👤 Author

**Violeta Correa** — Data Analyst & Data Assurance Engineer  
[LinkedIn](https://www.linkedin.com/in/violeta-correa) | [GitHub](https://github.com/VioletaPazCo)
