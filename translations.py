# translations.py
import streamlit as st

TEXTS = {
    "ES": {
        # --- App Routing & Navigation (app.py) ---
        "nav_b2g_title": "B2G - Gobernanza de Red",
        "nav_desc_title": "Descripción de la Red",
        "nav_cat_product": "Producto / Gobernanza",
        "nav_cat_presentation": "Presentación & Análisis",
        
        # --- App Config & Header (b2g_governance.py & network_description.py) ---
        "app_title": "Endolla B2G — Gobernanza de Red",
        "header_title": "Gobernanza de Datos - Red ENDOLLA Barcelona (B2G)",
        "header_subtitle": "Cuadro de mando para la gestión pública: monitorización de la integridad telemétrica, fallos de sensores y gobernanza de catálogos desincronizados.",
        "net_title": "ENDOLLA BARCELONA — Pipeline Analítico y Gobernanza de Infraestructura",

        # --- KPIs ---
        "kpi_active": "🟢 Puertos Activos Sanos",
        "kpi_active_sub": "({pct:.1f}% de {total:,} históricos)",
        "kpi_orphan": "🔴 Registros Huérfanos",
        "kpi_orphan_sub": "({events:,} eventos en cuarentena)",
        "kpi_epoch": "⚙️ Fallos de Sensor Epoch",
        "kpi_epoch_sub": "({events:,} eventos detectados)",
        "kpi_desync": "🟡 Gobernanza Desincronizada",
        "kpi_desync_sub": "(Catálogo vs Telemetría Lag)",
        
        # --- Sidebar ---
        "sidebar_header": "🔍 Filtros de Gobernanza",
        "sidebar_radio_label": "Seleccione la Capa a Inspeccionar:",
        "layer_active": "🟢 Red Activa Sana",
        "layer_orphan": "🔴 Registros Telemétricos Huérfanos",
        "layer_epoch": "⚙️ Fallos de Sensor Epoch",
        "layer_desync": "🟡 Activos Silenciosos (Desincronizados)",
        
        # --- Layer Names & Badges ---
        "lname_active": "Red Activa",
        "lname_orphan": "Registros Huérfanos",
        "lname_epoch": "Fallos Epoch",
        "lname_desync": "Gobernanza Desincronizada",
        
        "badge_active": "🟢 Activo / Sano",
        "badge_orphan": "🔴 Cuarentena / Huérfano",
        "badge_epoch": "⚙️ Fallo Epoch",
        "badge_desync": "🟡 SKU Desincronizado / Lag",
        
        # --- Summary Banner ---
        "layer_view_prefix": "Capa Visualización:",
        "banner_title": "Resumen de la Capa Seleccionada ({layer_name}):",
        "banner_time": "Horizonte Temporal:",
        "banner_no_time": "Sin registro temporal",
        "banner_scope": "Alcance Físico:",
        "banner_scope_detail": "{locations} Ubicaciones Únicas | {stations} Estaciones | {ports} Puertos Únicos",
        "banner_power": "Rango de Potencia (Mín / Mediana / Máx):",
        
        # --- Map ---
        "map_title": "### Mapa de Infraestructura",
        "map_street": "Calle",
        "map_parking": "Parking",
        "map_audit": "Calle / Auditoría",
        "map_car_ports": "Coche:",
        "map_moto_ports": "Moto:",
        "map_ports": "puertos",
        "map_affected_ports": "Puertos Afectados:",
        "map_no_addr": "Ubicación sin dirección explícita",
        
        # --- Charts & Categorizations ---
        "infra_details_title": "### Detalle de Atributos de Infraestructura",
        "val_motorcycle": "Motocicleta",
        "val_car": "Coche / VE",
        "val_street": "Calle",
        "val_parking": "Parking",
        "val_unknown": "Desconocido",
        "chart_uc_title": "<b>Casos de uso (Puertos Únicos)</b>",
        "chart_uc_y": "Puertos Únicos",
        "chart_pie_title": "<b>Puertos Únicos por Tipo de Conector</b>",
        "chart_pie_hover": "<b>%{label}</b><br>Puertos: %{value}<br>Cuota: %{percent}<extra></extra>",
        "chart_legend_loc_type": "Tipo de Ubicación",
        "info_no_uc": "Sin datos o atributos de caso de uso disponibles para esta capa.",
        "info_no_conn": "ℹ️️ Tipos de conector no disponibles para esta capa.",
        
        # --- Power Distribution Section ---
        "power_dist_title": "3.3. Distribución de Puertos por Conector y Potencia Nominal",
        "chart_power_conn": "Tipo de Conector",
        "chart_power_legend": "Potencia Nominal",
        "chart_power_label": "Potencia Instalada",
        "chart_active_ports_count": "Cantidad de Puertos Activos",
        
        # --- Top Locations Section ---
        "top_loc_title": "### Análisis de Afectación por Ubicación",
        "top_loc_chart_title": "<b>Top 10 Ubicaciones Afectadas ({layer_name})</b>",
        "top_loc_x_title": "Total de Registros",
        "top_loc_prefix": "Ubicación ",
        
        # --- Quarantine Audit Section ---
        "audit_title": "### Auditoría de Causa Raíz (Cuarentena)",
        "audit_table_title": "#### Tabla Resumen de Cuarentena",
        "col_audit_case": "Caso de Auditoría / Causa Raíz",
        "col_total_events": "Eventos Totales",
        "col_pct": "Porcentaje (%)",
        "col_map_status": "Estado en Mapa",
        "col_affected_ports": "Puertos Afectados",
        "status_map_yes": "✅ Sí (Geolocalizado)",
        "status_map_no": "No (Coordenadas no mapeadas)",
        "audit_breakdown_header": "<br>**Desglose Agrupado por Causa Raíz**",
        
        "tab_case_a": "📌 Caso A: Estación Válida | Puerto no Registrado",
        "tab_case_b": "📌 Caso B: Ubicación Válida | Estación y Puerto no Registrados",
        "tab_case_c": "📌 Caso C: Coordenadas No Mapeadas",
        
        "desc_case_a": "**Diagnóstico:** La ubicación y estación existen en el catálogo maestro, pero la telemetría emite valores de `port_id` no registrados.",
        "desc_case_b": "**Diagnóstico:** La ubicación física existe en el catálogo, pero los IDs de estación y puerto no están registrados en el inventario activo.",
        "desc_case_c": "**Diagnóstico:** Eventos emitidos con IDs de ubicación/estación inexistentes o coordenadas geográficas inválidas.",
        
        "metric_affected_events": "Eventos Afectados",
        "metric_stations_involved": "Estaciones Involucradas",
        "metric_locations_involved": "Ubicaciones Involucradas",
        
        "tbl_loc_id": "ID Ubicación",
        "tbl_station_id": "ID Estación",
        "tbl_emitted_ports": "Puertos Emitidos en Cuarentena",
        "tbl_total_events": "Eventos Totales",
        
        # --- Silent / Desynced Assets Section ---
        "desync_audit_title": "### Auditoría de Causa Raíz — Activos Silenciosos / Desincronizados",

        # --- Network Description Tabs & Medallion Architecture ---
        "tab_medallion": "1. Contexto & Arquitectura",
        "tab_estruc": "2. Evolución & Estructura de Datos",
        "tab_eda": "3. Red Activa Consolidada",

        "med_intro": "Los datos fueron extraídos desde la plataforma [Open Data BCN](https://opendata-ajuntament.barcelona.cat/) en formato JSON, correspondientes a los datasets de:\n- [Estat dels punts de recàrrega elèctrica](https://opendata-ajuntament.barcelona.cat/data/ca/dataset/estat-ports-recarrega-electric).\n- [Informació dels punts de recàrrega elèctrica](https://opendata-ajuntament.barcelona.cat/data/ca/dataset/informacio-punts-recarrega-electric).\n\nEl procesamiento se estructuró siguiendo la arquitectura Medallion.",

        "bronze_title": "BRONZE: Ingesta e Integración",
        "bronze_hierarchy": "**Jerarquía:** Ubicación (Locations) $\\longrightarrow$ Estaciones (Stations) $\\longrightarrow$ Enchufes/Puertos (Ports)",
        "bronze_coords": "Las coordenadas geográficas (latitud y longitud) están informadas a nivel de **Ubicación**.",
        "cap_parking_multi": "Múltiples puertos de recarga en parking",
        "cap_parking_use": "Puerto de recarga en uso",
        "err_img_not_found": "No se encontró la imagen '{img}' en la carpeta raíz del proyecto.",

        "silver_title": "SILVER: Tratamiento, Limpieza y Gobernanza de Datos",
        "tbl_dim_title": "#### Tabla de Dimensiones",
        "err_dim_empty": "El dataset de dimensiones está vacío o no se pudo cargar.",
        "silver_dim_bullets": "- Clave subrogada compuesta:<br>`station_port_sk` = `station_id`_`port_id`\n- Eliminación del 53.19% de columnas por varianza nula.\n- Generación de un histórico de cambios (SCD Type 2).\n- Identificación de puertos del catálogo sin telemetría asociada.",

        "vars_key_title": "#### Variables Clave del Puerto de Recarga",
        "cap_port_img": "Puerto de la red Endolla",
        "vars_key_bullets": "- **`port_notes`**: Restricciones de uso\n   - **Motocicletas**   |   **Coches**\n- **`onstreet_location`**: Emplazamiento físico\n   - **Calle**   |   **Parking**\n- **`port_connector_type`**: Tipo de conector físico:\n  - **Wall Outlet**: Enchufe doméstico estándar.\n  - **Mennekes**: Estándar europeo (en desuso).\n  - **Chademo**: Carga rápida para vehículos asiáticos.\n  - **CSS Type 2**: Carga rápida estándar europeo/americano.\n- **`port_power_kw`**: Potencia instalada (**3.6** a **50 kW**).",

        "tbl_fact_title": "#### Tabla de Hechos",
        "err_fact_empty": "El dataset de hechos está vacío o no se pudo cargar.",
        "silver_fact_bullets": "- Clave subrogada compuesta:<br>`station_port_sk` = `station_id`_`port_id`\n- Derivación de la variable `target_is_available` desde `port_status_value`.\n- Cuarentena de inconsistencias (registros huérfanos y con error de timestamp).",

        "tbl_master_title": "#### Tabla Maestra",
        "err_master_empty": "El dataset maestro está vacío o no se pudo cargar.",
        "silver_master_bullets": "- Merge de tabla de hechos y dimensión mediante clave compuesta `station_port_sk`.",

        "summary_datasets_title": "#### Resumen Datasets",
        "ds_dim_hist": "Dimensión Histórica",
        "ds_dim_rec": "Dimensión Reciente",
        "ds_fact": "Hechos",
        "ds_master": "Tabla Maestra",

        "col_ds_table": "Dataset / Tabla",
        "col_ds_regs": "Registros",
        "col_ds_cols": "Columnas",
        "col_ds_locs": "Ubicaciones",
        "col_ds_stations": "Estaciones",
        "col_ds_ports": "Puertos Únicos",

        "gold_title": "GOLD: Inteligencia de Negocio & Auditoría de Red",
        "gold_bullets": "1. Catálogo de Dimensiones y Evolución Histórica de la Red.\n2. Telemetría y Control de Calidad de Datos.\n3. Análisis de la Red Operativa.",

        # --- Section 2 & Subtabs ---
        "subtab_evo": "1. Evolución Histórica Dimensiones",
        "subtab_cat": "2. Dimensión Reciente - Catálogo",
        "subtab_fact": "3. Telemetría & Tabla de Hechos",

        "sec2_intro": "Caracterización de la infraestructura física, evolución temporal de la red y análisis geoespacial.",
        "sec2_fact_intro": "Análisis de eventos de telemetría, cobertura histórica y patrones temporales de disponibilidad.",

        "chart_title_evo": "Incorporación de Puertos y Potencia Instalada Acumulada",
        "chart_title_conn": "Evolución Histórica por Tipo de Conector",
        "chart_title_uc": "Evolución Histórica por Caso de Uso",
        "chart_title_split": "Análisis de Dispersión y Estructura Cuartílica de Puertos por Ubicación",
        "chart_title_map": "Distribución y Capacidad de Ubicaciones (Red Endolla)",
        "chart_legend_loc_type": "Tipo de Ubicación",

        "legend_ports": "Puertos",
        "legend_power": "Potencia [kW]",
        "axis_year": "Año",
        "axis_num_ports": "Número de Puertos",
        "axis_installed_power": "Potencia Instalada (kW)",
        "axis_conn_type": "Tipo de Conector",
        "axis_use_case": "Caso de Uso",
        "axis_location": "Ubicación",
        "axis_num_ports_zoom": "Número de Puertos (Zoom)",

        "uc_parking_car": "Parking Coche",
        "uc_parking_moto": "Parking Moto",
        "uc_street_car": "Calle Coche",
        "uc_street_moto": "Calle Moto",

        "sub_global_view": "1. Vista Global",
        "sub_zoom_box": "2. Zoom Boxplot",

        "metric_total_events": "Total Eventos",
        "metric_active_ports": "Puertos Activos",
        "metric_stations": "Estaciones",
        "metric_locations": "Ubicaciones",
        "metric_global_avail": "Disponibilidad Global",

        # --- Section 3 & Telemetry Charts ---
        "select_temp_level": "Selecciona el nivel de agregación temporal para la distribución de eventos:",
        "temp_opt_monthly": "Mensual (Meses del año)",
        "temp_opt_weekly": "Semanal (Días de la semana)",
        "temp_opt_hourly": "Horario (Horas del día)",

        "chart_temp_monthly": "⏱️ Distribución Porcentual de Eventos por Mes",
        "chart_temp_weekly": "⏱️ Distribución Porcentual de Eventos por Día de la Semana",
        "chart_temp_hourly": "⏱️ Distribución Porcentual de Eventos por Hora del Día",

        "axis_month": "Mes",
        "axis_day_of_week": "Día de la Semana",
        "axis_hour_of_day": "Hora del Día",
        "axis_telemetry_events_pct": "Eventos Telemétricos (%)",

        "day_monday": "Lunes",
        "day_tuesday": "Martes",
        "day_wednesday": "Miércoles",
        "day_thursday": "Jueves",
        "day_friday": "Viernes",
        "day_saturday": "Sábado",
        "day_sunday": "Domingo",

        "chart_annual_coverage": "📈 Cobertura Anual de Eventos de Telemetría vs. Puertos Activos",
        "axis_num_events": "Número de Eventos",
        "legend_events_year": "Eventos por Año",

        "chart_heatmap_avail": "Mapa de Calor de Disponibilidad",
        "heatmap_z_title": "Disponibilidad (%)",

        "sec3_intro": "Análisis del crecimiento histórico acumulado, distribución por casos de uso y perfil técnico de conectores y potencias nominales.",
        "sec3_power_dist_title": "Distribución de Puertos por Conector y Potencia Nominal",
        "val_unknown": "Desconocido",
        "err_master_not_found": "El DataFrame 'df_master' no está disponible en el entorno actual para procesar la telemetría."
    },
    
    "EN": {
        # --- App Routing & Navigation (app.py) ---
        "nav_b2g_title": "B2G - Network Governance",
        "nav_desc_title": "Network Description",
        "nav_cat_product": "Product / Governance",
        "nav_cat_presentation": "Presentation & Analysis",
        
        # --- App Config & Header (b2g_governance.py & network_description.py) ---
        "app_title": "Endolla B2G — Network Governance",
        "header_title": "Data Governance - ENDOLLA Barcelona Network (B2G)",
        "header_subtitle": "Public management dashboard: monitoring telemetry integrity, sensor faults, and desynchronized catalog governance.",
        "net_title": "ENDOLLA BARCELONA — Analytical Pipeline & Infrastructure Governance",

        # --- KPIs ---
        "kpi_active": "🟢 Healthy Active Ports",
        "kpi_active_sub": "({pct:.1f}% of {total:,} historical)",
        "kpi_orphan": "🔴 Orphan Records",
        "kpi_orphan_sub": "({events:,} events in quarantine)",
        "kpi_epoch": "⚙️ Epoch Sensor Faults",
        "kpi_epoch_sub": "({events:,} events detected)",
        "kpi_desync": "🟡 Desynchronized Governance",
        "kpi_desync_sub": "(Catalog vs Telemetry Lag)",
        
        # --- Sidebar ---
        "sidebar_header": "🔍 Governance Filters",
        "sidebar_radio_label": "Select Layer to Inspect:",
        "layer_active": "🟢 Healthy Active Network",
        "layer_orphan": "🔴 Orphan Telemetry Records",
        "layer_epoch": "⚙️ Epoch Sensor Faults",
        "layer_desync": "🟡 Silent Assets (Desynchronized)",
        
        # --- Layer Names & Badges ---
        "lname_active": "Active Network",
        "lname_orphan": "Orphan Records",
        "lname_epoch": "Epoch Faults",
        "lname_desync": "Desynchronized Governance",
        
        "badge_active": "🟢 Active / Healthy",
        "badge_orphan": "🔴 Quarantine / Orphan",
        "badge_epoch": "⚙️ Epoch Fault",
        "badge_desync": "🟡 SKU Desynced / Lag",
        
        # --- Summary Banner ---
        "layer_view_prefix": "Visualization Layer:",
        "banner_title": "Selected Layer Summary ({layer_name}):",
        "banner_time": "Time Horizon:",
        "banner_no_time": "No temporal record",
        "banner_scope": "Physical Scope:",
        "banner_scope_detail": "{locations} Unique Locations | {stations} Stations | {ports} Unique Ports",
        "banner_power": "Power Range (Min / Median / Max):",
        
        # --- Map ---
        "map_title": "### Infrastructure Map",
        "map_street": "On-Street",
        "map_parking": "Parking",
        "map_audit": "On-Street / Audit",
        "map_car_ports": "Car:",
        "map_moto_ports": "Motorcycle:",
        "map_ports": "ports",
        "map_affected_ports": "Affected Ports:",
        "map_no_addr": "Location without explicit address",
        
        # --- Charts & Categorizations ---
        "infra_details_title": "### Infrastructure Attribute Details",
        "val_motorcycle": "Motorcycle",
        "val_car": "Car / EV",
        "val_street": "On-Street",
        "val_parking": "Parking",
        "val_unknown": "Unknown",
        "chart_uc_title": "<b>Use Cases (Unique Ports)</b>",
        "chart_uc_y": "Unique Ports",
        "chart_pie_title": "<b>Unique Ports by Connector Type</b>",
        "chart_pie_hover": "<b>%{label}</b><br>Ports: %{value}<br>Share: %{percent}<extra></extra>",
        "chart_legend_loc_type": "Location Type",
        "info_no_uc": "No use case data or attributes available for this layer.",
        "info_no_conn": "ℹ️ Connector types not available for this layer.",
        
        # --- Power Distribution Section ---
        "power_dist_title": "3.3. Distribution of Ports by Connector and Nominal Power",
        "chart_power_conn": "Connector Type",
        "chart_power_legend": "Nominal Power",
        "chart_power_label": "Installed Power",
        "chart_active_ports_count": "Active Ports Count",
        
        # --- Top Locations Section ---
        "top_loc_title": "### Location Impact Analysis",
        "top_loc_chart_title": "<b>Top 10 Affected Locations ({layer_name})</b>",
        "top_loc_x_title": "Total Records",
        "top_loc_prefix": "Location ",
        
        # --- Quarantine Audit Section ---
        "audit_title": "### Root Cause Audit (Quarantine)",
        "audit_table_title": "#### Quarantine Summary Table",
        "col_audit_case": "Audit Case / Root Cause",
        "col_total_events": "Total Events",
        "col_pct": "Percentage (%)",
        "col_map_status": "Map Status",
        "col_affected_ports": "Affected Ports",
        "status_map_yes": "✅ Yes (Geolocated)",
        "status_map_no": "No (Unmapped Coordinates)",
        "audit_breakdown_header": "<br>**Breakdown Grouped by Root Cause**",
        
        "tab_case_a": "📌 Case A: Valid Station | Unregistered Port",
        "tab_case_b": "📌 Case B: Valid Location | Unregistered Station & Port",
        "tab_case_c": "📌 Case C: Unmapped Coordinates",
        
        "desc_case_a": "**Diagnosis:** Location and station exist in master catalog, but telemetry emits unregistered `port_id` values.",
        "desc_case_b": "**Diagnosis:** Physical location exists in catalog, but station and port IDs are not registered in active inventory.",
        "desc_case_c": "**Diagnosis:** Events emitted with non-existent location/station IDs or invalid geographical coordinates.",
        
        "metric_affected_events": "Affected Events",
        "metric_stations_involved": "Stations Involved",
        "metric_locations_involved": "Locations Involved",
        
        "tbl_loc_id": "Location ID",
        "tbl_station_id": "Station ID",
        "tbl_emitted_ports": "Emitted Ports in Quarantine",
        "tbl_total_events": "Total Events",
        
        # --- Silent / Desynced Assets Section ---
        "desync_audit_title": "### Root Cause Audit — Silent / Desynchronized Assets",

        # --- Network Description Tabs & Medallion Architecture ---
        "tab_medallion": "1. Context & Architecture",
        "tab_estruc": "2. Data Structure & Evolution",
        "tab_eda": "3. Consolidated Active Network",

        "med_intro": "Data was extracted from the [Open Data BCN](https://opendata-ajuntament.barcelona.cat/) platform in JSON format, corresponding to datasets:\n- [Estat dels punts de recàrrega elèctrica](https://opendata-ajuntament.barcelona.cat/data/ca/dataset/estat-ports-recarrega-electric).\n- [Informació dels punts de recàrrega elèctrica](https://opendata-ajuntament.barcelona.cat/data/ca/dataset/informacio-punts-recarrega-electric).\n\nProcessing was structured following the Medallion architecture.",

        "bronze_title": "BRONZE: Ingestion & Integration",
        "bronze_hierarchy": "**Hierarchy:** Location (Locations) $\\longrightarrow$ Stations (Stations) $\\longrightarrow$ Plugs/Ports (Ports)",
        "bronze_coords": "Geographical coordinates (latitude and longitude) are reported at the **Location** level.",
        "cap_parking_multi": "Multiple EV charging ports in parking facility",
        "cap_parking_use": "EV charging port in use",
        "err_img_not_found": "Image '{img}' was not found in the project root directory.",

        "silver_title": "SILVER: Processing, Cleaning & Data Governance",
        "tbl_dim_title": "#### Dimension Table",
        "err_dim_empty": "The dimension dataset is empty or could not be loaded.",
        "silver_dim_bullets": "- Composite surrogate key:<br>`station_port_sk` = `station_id`_`port_id`\n- Removal of 53.19% of columns due to zero variance.\n- Historical change tracking generation (SCD Type 2).\n- Identification of catalog ports without associated telemetry.",

        "vars_key_title": "#### EV Port Key Variables",
        "cap_port_img": "Endolla network port",
        "vars_key_bullets": "- **`port_notes`**: Usage restrictions\n   - **Motorcycles**   |   **Cars**\n- **`onstreet_location`**: Physical placement\n   - **On-Street**   |   **Parking**\n- **`port_connector_type`**: Physical connector type:\n  - **Wall Outlet**: Standard domestic plug.\n  - **Mennekes**: European standard (deprecated).\n  - **Chademo**: Rapid charging for Asian vehicles.\n  - **CSS Type 2**: Standard European/American rapid charging.\n- **`port_power_kw`**: Installed power (**3.6** to **50 kW**).",

        "tbl_fact_title": "#### Fact Table",
        "err_fact_empty": "The fact dataset is empty or could not be loaded.",
        "silver_fact_bullets": "- Composite surrogate key:<br>`station_port_sk` = `station_id`_`port_id`\n- Derivation of `target_is_available` variable from `port_status_value`.\n- Quarantine of inconsistencies (orphan records and timestamp errors).",

        "tbl_master_title": "#### Master Table",
        "err_master_empty": "The master dataset is empty or could not be loaded.",
        "silver_master_bullets": "- Merge of fact and dimension tables using composite key `station_port_sk`.",

        "summary_datasets_title": "#### Dataset Summary",
        "ds_dim_hist": "Historical Dimension",
        "ds_dim_rec": "Recent Dimension",
        "ds_fact": "Facts",
        "ds_master": "Master Table",

        "col_ds_table": "Dataset / Table",
        "col_ds_regs": "Records",
        "col_ds_cols": "Columns",
        "col_ds_locs": "Locations",
        "col_ds_stations": "Stations",
        "col_ds_ports": "Unique Ports",

        "gold_title": "GOLD: Business Intelligence & Network Audit",
        "gold_bullets": "1. Dimension Catalog and Historical Network Evolution.\n2. Telemetry and Data Quality Control.\n3. Operational Network Analysis.",

        # --- Section 2 & Subtabs ---
        "subtab_evo": "1. Dimensions Historical Evolution",
        "subtab_cat": "2. Recent Dimension - Catalog",
        "subtab_fact": "3. Telemetry & Fact Table",

        "sec2_intro": "Physical infrastructure characterization, temporal network evolution, and geospatial analysis.",
        "sec2_fact_intro": "Telemetry event analysis, historical coverage, and availability time patterns.",

        "chart_title_evo": "Port Additions and Cumulative Installed Power",
        "chart_title_conn": "Historical Evolution by Connector Type",
        "chart_title_uc": "Historical Evolution by Use Case",
        "chart_title_split": "Port Dispersion and Quartile Structure Analysis by Location",
        "chart_title_map": "Location Distribution and Capacity (Endolla Network)",
        "chart_legend_loc_type": "Location Type",

        "legend_ports": "Ports",
        "legend_power": "Power [kW]",
        "axis_year": "Year",
        "axis_num_ports": "Number of Ports",
        "axis_installed_power": "Installed Power (kW)",
        "axis_conn_type": "Connector Type",
        "axis_use_case": "Use Case",
        "axis_location": "Location",
        "axis_num_ports_zoom": "Number of Ports (Zoom)",

        "uc_parking_car": "Parking Car",
        "uc_parking_moto": "Parking Motorcycle",
        "uc_street_car": "On-Street Car",
        "uc_street_moto": "On-Street Motorcycle",

        "sub_global_view": "1. Global View",
        "sub_zoom_box": "2. Zoom Boxplot",

        "metric_total_events": "Total Events",
        "metric_active_ports": "Active Ports",
        "metric_stations": "Stations",
        "metric_locations": "Locations",
        "metric_global_avail": "Global Availability",

        # --- Section 3 & Telemetry Charts ---
        "select_temp_level": "Select temporal aggregation level for event distribution:",
        "temp_opt_monthly": "Monthly (Months of year)",
        "temp_opt_weekly": "Weekly (Days of week)",
        "temp_opt_hourly": "Hourly (Hours of day)",

        "chart_temp_monthly": "⏱️ Event Percentage Distribution by Month",
        "chart_temp_weekly": "⏱️ Event Percentage Distribution by Day of Week",
        "chart_temp_hourly": "⏱️ Event Percentage Distribution by Hour of Day",

        "axis_month": "Month",
        "axis_day_of_week": "Day of Week",
        "axis_hour_of_day": "Hour of Day",
        "axis_telemetry_events_pct": "Telemetry Events (%)",

        "day_monday": "Monday",
        "day_tuesday": "Tuesday",
        "day_wednesday": "Wednesday",
        "day_thursday": "Thursday",
        "day_friday": "Friday",
        "day_saturday": "Saturday",
        "day_sunday": "Sunday",

        "chart_annual_coverage": "📈 Annual Coverage of Telemetry Events vs. Active Ports",
        "axis_num_events": "Number of Events",
        "legend_events_year": "Events per Year",

        "chart_heatmap_avail": "Availability Heatmap",
        "heatmap_z_title": "Availability (%)",

        "sec3_intro": "Analysis of historical cumulative growth, distribution by use cases, and technical profile of connectors and nominal power.",
        "sec3_power_dist_title": "Port Distribution by Connector and Nominal Power",
        "val_unknown": "Unknown",
        "err_master_not_found": "DataFrame 'df_master' is not available in the current environment to process telemetry."
    }
}

def t(key: str, **kwargs) -> str:
    """Helper function to fetch translated text based on session state."""
    lang = st.session_state.get("lang", "ES")
    text = TEXTS.get(lang, {}).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text