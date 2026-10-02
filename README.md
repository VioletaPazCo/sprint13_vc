# ⚡ Endolla Barcelona — B2G Data Governance & Assurance Dashboard

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://b2g-governance-endolla-bcn.streamlit.app)

🚀 **Live Demo:** [https://b2g-governance-endolla-bcn.streamlit.app](https://b2g-governance-endolla-bcn.streamlit.app)


---

## 📌 Project Overview

**Business-to-Government (B2G) Data Governance** dashboard and analytics infrastructure for **Endolla Barcelona**, the public electric vehicle (EV) charging network in Barcelona.

The primary objective of this project is to audit telemetry data quality and integrity, detect operational anomalies (ghost ports, status desynchronizations, orphaned records), and provide an interactive analytical platform to support municipal decision-making and service SLA monitoring.

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
* **Data Modeling & Assurance:** Medallion Architecture, governance audit notebooks, automated quarantine isolation (`b2g_quarantine_*.parquet`).

---

## 🔍 Data Quality & Governance Audit Findings

Through the automated data assurance pipeline, the system detects and isolates the following operational anomalies:

* **Desynchronized & Ghost Ports (`b2g_desynced_ghost_ports.parquet`):** Connectors reporting active telemetry without a valid master catalog entity.
* **Orphaned Records (`b2g_quarantine_orphans.parquet`):** Status logs disconnected from the station master metadata.
* **Timestamp / Epoch Anomalies (`b2g_quarantine_epoch.parquet`):** Telemetry records containing corrupted time stamps or epoch values.
* **Silver/Gold Optimization:** Cleaned master dimensions and facts (`silver_dim_ports.parquet`, `silver_fact_status.parquet`, `stations_metadata.parquet`) engineered for sub-second dashboard rendering.

---

## 📂 Repository Structure

    .
    ├── .devcontainer/                                  # Development container configuration
    ├── pages/                                          # Secondary dashboard pages
    ├── app.py                                          # Main Streamlit application entry point
    ├── b2g_data_profiling_and_integrity_audit_01.ipynb # Notebook 01: Data Profiling & Audit
    ├── b2g_medallion_pipeline_etl_02.ipynb             # Notebook 02: Medallion ETL & Quarantine
    ├── b2g_quarantine_*.parquet                       # Automated data quality quarantine tables
    ├── silver_*.parquet / stations_metadata.parquet   # Processed Parquet analytical datasets
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
