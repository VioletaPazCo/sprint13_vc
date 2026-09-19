import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración global de la página
st.set_page_config(
    page_title="Endolla Network Architecture & Analytics",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown(
    """
    <style>
    /* Estilo del texto base (párrafos, viñetas, listas) */
    p, li, span, div.stMarkdown {
        font-family: 'Segoe UI', Roboto, Arial, sans-serif !important;
        font-size: 18px !important;
        line-height: 1.6 !important;
    }

    /* Estilo para subtítulos explicativos o capturas menores */
    .stCaption {
        font-size: 15px !important;
    }

    /* Estilo para el contenido de las tablas nativas de Streamlit */
    [data-testid="stDataFrame"] {
        font-size: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Carga de archivos ---
@st.cache_data
def load_production_artifacts():
    try:
        df_history = pd.read_parquet('silver_dim_ports_history.parquet')
    except Exception:
        df_history = pd.DataFrame()
        
    try:
        df_dim = pd.read_parquet('silver_dim_ports.parquet')
    except Exception:
        df_dim = pd.DataFrame()
        
    try:
        df_fact_status = pd.read_parquet('silver_fact_status.parquet')
    except Exception:
        df_fact_status = pd.DataFrame()
        
    try:
        df_master = pd.read_parquet('b2c_active_master_ports.parquet')
    except Exception:
        df_master = pd.DataFrame()
        
    return df_history, df_dim, df_fact_status, df_master

df_history, df_dim, df_fact_status, df_master = load_production_artifacts()

st.title("ENDOLLA BARCELONA — Pipeline Analítico y Gobernanza de Infraestructura")

# Pestañas principales
tab_medallion, tab_estruc, tab_eda = st.tabs([
    "1. Contexto & Arquitectura", 
    "2. Evolución & Estructura de Datos", 
    "3. Red Activa Consolidada", 
])

# SECCIÓN 1: CONTEXTO DE DATOS Y ARQUITECTURA MEDALLION
with tab_medallion:
    st.markdown(
        "Los datos fueron extraídos desde la plataforma [Open Data BCN](https://opendata-ajuntament.barcelona.cat/) "
        "en formato JSON, correspondientes a los datasets de: \n "
        "- [Estat dels punts de recàrrega elèctrica](https://opendata-ajuntament.barcelona.cat/data/ca/dataset/estat-ports-recarrega-electric).\n"
        "- [Informació dels punts de recàrrega elèctrica](https://opendata-ajuntament.barcelona.cat/data/ca/dataset/informacio-punts-recarrega-electric). \n\n "
        " El procesamiento se estructuró siguiendo la arquitectura Medallion."
    )
    
    st.markdown("---")

# BRONZE: Ingesta e Integración
    st.subheader("BRONZE: Ingesta e Integración")
    
    col_b1, col_b2 = st.columns([4, 6])
    
    with col_b1:
        df_bronze_orig = pd.DataFrame({
            "Año": [2023, 2024, 2025, 2026],
            "Locations [Dimensión]": [4, 4, 4, 2],
            "Estats Ports [Hechos]": [2, 4, 4, 2]
        })
        st.dataframe(df_bronze_orig, use_container_width=True, hide_index=True)
    
    with col_b2:
        st.markdown(
            "**Jerarquía:** "
            "Ubicación (Locations) $\\longrightarrow$ Estaciones (Stations) $\\longrightarrow$ Enchufes/Puertos (Ports)"
        )

        ruta_imagen = "foto_connectors.jpg"
        if os.path.exists(ruta_imagen):
            subcol_izq, subcol_centro, subcol_der = st.columns([1, 4, 1])
            with subcol_centro:
                st.image(ruta_imagen, use_container_width=True)
        else:
            st.warning("No se encontró la imagen 'foto_connectors.jpg' en la carpeta raíz del proyecto.")

        st.markdown("Las coordenadas geográficas (latitud y longitud) están informadas a nivel de **Ubicación**.")

    # Columnas de imágenes
    st.markdown("<br>", unsafe_allow_html=True)
    col_img_left, col_img_right = st.columns(2)

    with col_img_left:
        ruta_parking = "parking.jpg"
        if os.path.exists(ruta_parking):
            st.image(ruta_parking, use_container_width=True, caption="Múltiples puertos de recarga en parking")
        else:
            st.warning("No se encontró la imagen 'parking.jpg' en la carpeta raíz del proyecto.")

    with col_img_right:
        ruta_parking_1 = "parking_1.png"
        if os.path.exists(ruta_parking_1):
            st.image(ruta_parking_1, use_container_width=True, caption="Puerto de recarga en uso")
        else:
            st.warning("No se encontró la imagen 'mapa_red_endolla_hd.png' en la carpeta raíz del proyecto.")



    st.markdown("---")

    # SILVER: Tratamiento, Limpieza y Gobernanza de Datos
    st.subheader("SILVER: Tratamiento, Limpieza y Gobernanza de Datos")

    # Tabla Dimensiones 
    col_t1, col_t2 = st.columns([6, 4])
    with col_t1:
        st.markdown("#### Tabla de Dimensiones")

    col_s1, col_s2 = st.columns([6, 4])
    
    with col_s1:
        if not df_dim.empty:
            columnas_deseadas_dim = [c for c in ["station_port_sk", "onstreet_location", "port_connector_type", "port_power_kw", "port_notes"] if c in df_dim.columns]
            df_muestra_dim = df_dim[columnas_deseadas_dim].sample(min(5, len(df_dim)))
            st.dataframe(df_muestra_dim, use_container_width=True, hide_index=True)
        else:
            st.warning("El dataset de dimensiones está vacío o no se pudo cargar.")
    
    with col_s2:
        st.markdown(
            "- Clave subrogada compuesta:<br>"
            "`station_port_sk` = `station_id`_`port_id`\n"
            "- Eliminación del 53.19% de columnas por varianza nula.\n"
            "- Generación de un histórico de cambios (SCD Type 2).\n"
            "- Identificación de puertos del catálogo sin telemetría asociada.",
            unsafe_allow_html=True
        )

    # Caracterización Puerto
    st.markdown("#### Variables Clave del Puerto de Recarga")
    
    col_anat_1, col_anat_2 = st.columns([5, 5])

    with col_anat_1:
        ruta_puerto = "puerto_1.jpg"
        if os.path.exists(ruta_puerto):
            st.image(ruta_puerto, use_container_width=True, caption="Puerto de la red Endolla")
        else:
            st.warning("No se encontró la imagen 'puerto_1.jpg' en la carpeta raíz del proyecto.")

    with col_anat_2:
        st.markdown(
            "- **`port_notes`**: Restricciones de uso \n"
            "   - **Motocicletas**   |   **Coches**\n"
            "- **`onstreet_location`**: Emplazamiento físico \n"
            "   - **Calle**   |   **Parking**\n"
            "- **`port_connector_type`**: Tipo de conector físico:\n"
            "  - **Wall Outlet**: Enchufe doméstico estándar.\n"
            "  - **Mennekes**: Estándar europeo (en desuso).\n"
            "  - **Chademo**: Carga rápida para vehículos asiáticos.\n"
            "  - **CSS Type 2**: Carga rápida estándar europeo/americano.\n"
            "- **`port_power_kw`**: Potencia instalada (**3.6** a **50 kW**).\n"
        )

    st.markdown("<hr style='border: none; border-top: 2px dashed #cccccc; margin: 25px 0;'>", unsafe_allow_html=True)

    # Tabla Hechos
    col_t3, col_t4 = st.columns([6, 4])
    with col_t3:
        st.markdown("#### Tabla de Hechos")

    col_h1, col_h2 = st.columns([6, 4])
    
    with col_h1: 
        if not df_fact_status.empty:
            columnas_deseadas_fact = [c for c in ['station_port_sk', 'event_timestamp', 'port_status_value', 'target_is_available'] if c in df_fact_status.columns]
            df_muestra_fact = df_fact_status[columnas_deseadas_fact].sample(min(5, len(df_fact_status)))
            st.dataframe(df_muestra_fact, use_container_width=True, hide_index=True)
        else:
            st.warning("El dataset de hechos está vacío o no se pudo cargar.")
    
    with col_h2:
        st.markdown(
            "- Clave subrogada compuesta:<br>"
            "`station_port_sk` = `station_id`_`port_id`\n"            
            "- Derivación de la variable `target_is_available` desde `port_status_value`.\n"
            "- Cuarentena de inconsistencias (registros huérfanos y con error de timestamp).",
            unsafe_allow_html=True
        )

    st.markdown("<hr style='border: none; border-top: 2px dashed #cccccc; margin: 25px 0;'>", unsafe_allow_html=True)

    # Tabla Maestra (Hechos + Dimensiones)
    col_t5, col_t6 = st.columns([6, 4])
    with col_t5:
        st.markdown("#### Tabla Maestra")

    col_s_m1, col_s_m2 = st.columns([6, 4]) 
    
    with col_s_m1: 
        if not df_master.empty:
            columnas_deseadas_master = [c for c in ['station_port_sk', 'event_timestamp', 'target_is_available', 'port_connector_type','use_case' ] if c in df_master.columns]
            df_muestra_master = df_master[columnas_deseadas_master].sample(min(5, len(df_master)))
            st.dataframe(df_muestra_master, use_container_width=True, hide_index=True)
        else:
            st.warning("El dataset maestro está vacío o no se pudo cargar.")
    
    with col_s_m2:
        st.markdown(
            "- Merge de tabla de hechos y dimensión mediante clave compuesta `station_port_sk`.\n",
            unsafe_allow_html=True
        )

    st.markdown("<hr style='border: none; border-top: 2px dashed #cccccc; margin: 25px 0;'>", unsafe_allow_html=True)

    # Resumen tablas principales
    st.markdown("#### Resumen Datasets")

    datasets_config = [
        ("Dimensión Histórica", df_history),
        ("Dimensión Reciente", df_dim),
        ("Hechos", df_fact_status),
        ("Tabla Maestra", df_master)
    ]

    summary_data = []

    for tipo, df in datasets_config:
        if df is not None and not df.empty:
            regs, cols = df.shape
            locs = df['location_id'].nunique() if 'location_id' in df.columns else "N/A"
            stations = df['station_id'].nunique() if 'station_id' in df.columns else "N/A"
            
            ports = 0
            for port_col in ['station_port_sk', 'port_id', 'port_sk']:
                if port_col in df.columns:
                    ports = df[port_col].nunique()
                    break
            if ports == 0:
                ports = "N/A"
        else:
            regs, cols, locs, stations, ports = 0, 0, 0, 0, 0

        summary_data.append({
            "Dataset / Tabla": tipo,
            "Registros": regs,
            "Columnas": cols,
            "Ubicaciones": locs,
            "Estaciones": stations,
            "Puertos Únicos": ports
        })

    data_summary = pd.DataFrame(summary_data)

    st.dataframe(
        data_summary.style.format({
            'Registros': lambda x: f"{x:,}" if isinstance(x, int) else x,
            'Columnas': lambda x: f"{x:,}" if isinstance(x, int) else x,
            'Ubicaciones': lambda x: f"{x:,}" if isinstance(x, int) else x,
            'Estaciones': lambda x: f"{x:,}" if isinstance(x, int) else x,
            'Puertos Únicos': lambda x: f"{x:,}" if isinstance(x, int) else x,
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # GOLD: Inteligencia de Negocio & Auditoría de Red
    st.subheader("GOLD: Inteligencia de Negocio & Auditoría de Red")
    st.markdown(
        "1. Catálogo de Dimensiones y Evolución Histórica de la Red.\n"
        "2. Telemetría y Control de Calidad de Datos.\n"
        "3. Análisis de la Red Operativa."
    )

# ESTILOS GLOBALES DE TITULOS
st.markdown("""
    <style>
    /* ***** FONT: Título Principal de Sección (20px - Límite Máximo) */
    .title-size-main {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    
    /* ***** FONT: Título de Subsección / Subpestaña (17px) */
    .title-size-sub {
        font-size: 17px !important;
        font-weight: 700 !important;
        color: #1E293B !important;
        margin-top: 12px !important;
        margin-bottom: 12px !important;
    }

    /* ***** FONT: Título Único del Gráfico Centrado (15px) - MARGIN BOTTOM AUMENTADO */
    .chart-title-single {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #0F172A !important;
        text-align: center !important;
        margin-top: 20px !important;
        margin-bottom: 24px !important; /* Espacio mayor hacia la figura */
    }
    
    /* ***** FONT: Tamaño de texto en las pestañas de Streamlit (15px) */
    button[data-baseweb="tab"] p {
        font-size: 15px !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)


# SECCIÓN 2: EVOLUCIÓN & ESTRUCTURA DE DATOS
with tab_estruc:
    st.markdown("Caracterización de la infraestructura física, evolución temporal de la red y análisis geoespacial.")

    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        "1. Evolución Histórica Dimensiones", 
        "2. Dimensión Reciente - Catálogo", 
        "3. Telemetría & Tabla de Hechos"
    ])
    
    # SUBTAB 1: EVOLUCIÓN HISTÓRICA DIMENSIONES
    with sub_tab1:
        df_hist = df_history.copy()
        df_hist['year_updated'] = df_hist['last_updated'].dt.year

        years = sorted(df_hist['year_updated'].dropna().unique())
        yearly_snapshots = []
        for yr in years:
            mask = df_hist['year_updated'] <= yr
            df_until_yr = df_hist[mask].sort_values('last_updated')
            latest_ports_yr = df_until_yr.groupby('station_port_sk').last().reset_index()
            latest_ports_yr['snapshot_year'] = int(yr)
            yearly_snapshots.append(latest_ports_yr)

        df_cumulative_snapshots = pd.concat(yearly_snapshots, ignore_index=True)

        first_seen_port = df_hist.groupby('station_port_sk')['year_updated'].min().reset_index()
        first_seen_location = df_hist.groupby('location_id')['year_updated'].min().reset_index()

        locations_by_year = first_seen_location.groupby('year_updated').size().reset_index(name='new_locations_added').rename(columns={'year_updated': 'year'})
        locations_by_year['cum_unique_locations'] = locations_by_year['new_locations_added'].cumsum()

        new_ports_by_year = first_seen_port.groupby('year_updated').size().reset_index(name='new_ports_added').rename(columns={'year_updated': 'year'})
        new_ports_by_year['cum_total_ports'] = new_ports_by_year['new_ports_added'].cumsum()

        power_evolution = df_cumulative_snapshots.groupby('snapshot_year').agg(total_installed_kw=('port_power_kw', 'sum')).reset_index().rename(columns={'snapshot_year': 'year'})

        summary_table_gold = locations_by_year[['year', 'cum_unique_locations']].merge(new_ports_by_year, on='year').merge(power_evolution, on='year')
        summary_table_gold['year_str'] = summary_table_gold['year'].astype(str)

        # 1. Gráfico Combinado: Puertos y Potencia
        fig_evo = go.Figure()
        fig_evo.add_trace(go.Bar(
            x=summary_table_gold['year_str'], 
            y=summary_table_gold['cum_total_ports'], 
            name="Puertos",
            marker_color="#3B82F6",  
            text=summary_table_gold['cum_total_ports'],
            textposition='outside',
            textfont=dict(color="black", size=12, family="Arial")
        ))
        fig_evo.add_trace(go.Scatter(
            x=summary_table_gold['year_str'], 
            y=summary_table_gold['total_installed_kw'], 
            name="Potencia [kW]", 
            yaxis="y2",
            mode="lines+markers+text",
            line=dict(color="#DC2626", width=2.5),
            marker=dict(size=7),
            text=[f"{val/1000:.1f}k kW" for val in summary_table_gold['total_installed_kw']],
            textposition="top center",
            textfont=dict(color="black", size=12, family="Arial")
        ))
        fig_evo.update_layout(
            font=dict(color="black", family="Arial"),
            title="",
            xaxis=dict(
                type='category', 
                title=dict(text="Año", font=dict(size=14, color="black", family="Arial")),
                tickfont=dict(size=12, color="black"),
                linecolor="black", showline=True, linewidth=1
            ),
            yaxis=dict(
                title=dict(text="Número de Puertos", font=dict(size=14, color="black", family="Arial")),
                tickfont=dict(size=12, color="black"),
                range=[0, 2100],
                showgrid=True, gridcolor="rgba(0,0,0,0.08)",
                linecolor="black", showline=True, linewidth=1
            ),
            yaxis2=dict(
                title=dict(text="Potencia Instalada (kW)", font=dict(size=14, color="black", family="Arial")),
                tickfont=dict(size=12, color="black"),
                overlaying="y", side="right", showgrid=False,
                range=[11000, 16000],
                linecolor="black", showline=True, linewidth=1
            ),
            template="plotly_white",
            legend=dict(
                orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.15,  
                bgcolor="white", bordercolor="rgba(0,0,0,0.2)", borderwidth=1, 
                font=dict(color="black", size=12)
            ),
            height=430,
            margin=dict(t=25, l=40, r=140, b=30)
        )
        
        _, col_center_1, _ = st.columns([0.2, 5.6, 0.2])
        with col_center_1:
            st.markdown('<div class="chart-title-single">Incorporación de Puertos y Potencia Instalada Acumulada</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_evo, use_container_width=True)

        st.markdown("---")
        
        # 2. Gráfico Tipo Conector
        df_connector = pd.crosstab(
            df_cumulative_snapshots['snapshot_year'],
            df_cumulative_snapshots['port_connector_type']
        ).reset_index()
        df_connector['snapshot_year'] = df_connector['snapshot_year'].astype(str)
        
        df_conn_melted = df_connector.melt(id_vars='snapshot_year', var_name='Connector_Type', value_name='Port_Count')
        
        connector_palette = {
            'MENNEKES': '#6baed6', 'Mennekes (AC)': '#6baed6',
            'WALL_OUTLET': '#1f77b4', 'Wall Outlet (Schuko)': '#1f77b4',
            'CCS_TYPE_2': "#f3acb8", 'CCS Combo 2 (DC)': '#f3acb8',
            'CHADEMO': '#d62728', 'CHAdeMO (DC)': '#d62728', 'Unknown': '#7f7f7f'
        }
        
        fig_conn = px.line(
            df_conn_melted, x='snapshot_year', y='Port_Count', color='Connector_Type',
            color_discrete_map=connector_palette, markers=True,
            labels={'snapshot_year': 'Año', 'Port_Count': 'Número de Puertos', 'Connector_Type': 'Tipo de Conector'}
        )
        fig_conn.update_layout(
            font=dict(color="black", family="Arial"),
            title="",
            xaxis=dict(
                type='category', title=dict(text="Año", font=dict(size=14, color="black")),
                tickfont=dict(size=12, color="black"), linecolor="black", showline=True, linewidth=1
            ),
            yaxis=dict(
                title=dict(text="Número de Puertos", font=dict(size=14, color="black")),
                tickfont=dict(size=12, color="black"), showgrid=True, gridcolor="rgba(0,0,0,0.08)",
                linecolor="black", showline=True, linewidth=1
            ),
            template="plotly_white", 
            height=430,
            legend=dict(
                orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, 
                bgcolor="white", bordercolor="rgba(0,0,0,0.2)", borderwidth=1, font=dict(color="black", size=12)
            ),
            margin=dict(t=25, l=40, r=120, b=30)
        )
        
        _, col_center_2, _ = st.columns([0.2, 5.6, 0.2])
        with col_center_2:
            st.markdown('<div class="chart-title-single">Evolución Histórica por Tipo de Conector</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_conn, use_container_width=True)

        st.markdown("---")
        
        # 3. Gráfico Caso de Uso
        df_usecase = pd.crosstab(
            df_cumulative_snapshots['snapshot_year'],
            df_cumulative_snapshots['use_case']
        ).reset_index()
        df_usecase['snapshot_year'] = df_usecase['snapshot_year'].astype(str)
        
        df_uc_melted = df_usecase.melt(id_vars='snapshot_year', var_name='Use_Case', value_name='Port_Count')
        
        use_case_map = {
            'Off-Street General': 'Parking Coche',
            'Off-Street Moto': 'Parking Moto',
            'On-Street General': 'Calle Coche',
            'On-Street Moto': 'Calle Moto'
        }
        df_uc_melted['Use_Case'] = df_uc_melted['Use_Case'].replace(use_case_map)

        color_uc_palette = {
            'Parking Coche': '#1E40AF',
            'Parking Moto':  '#1E40AF',
            'Calle Coche':   '#10B981',
            'Calle Moto':    '#10B981'
        }
        
        dash_uc_palette = {
            'Parking Coche': 'solid',
            'Parking Moto':  'dash',
            'Calle Coche':   'solid',
            'Calle Moto':    'dash'
        }
        
        fig_uc = px.line(
            df_uc_melted, 
            x='snapshot_year', 
            y='Port_Count', 
            color='Use_Case',
            line_dash='Use_Case',
            color_discrete_map=color_uc_palette,
            line_dash_map=dash_uc_palette,
            markers=True,
            labels={'snapshot_year': 'Año', 'Port_Count': 'Número de Puertos', 'Use_Case': 'Caso de Uso'}
        )
        
        fig_uc.update_traces(marker=dict(size=7))

        fig_uc.update_layout(
            font=dict(color="black", family="Arial"),
            title="",
            xaxis=dict(
                type='category', title=dict(text="Año", font=dict(size=14, color="black")),
                tickfont=dict(size=12, color="black"), linecolor="black", showline=True, linewidth=1
            ),
            yaxis=dict(
                title=dict(text="Número de Puertos", font=dict(size=14, color="black")),
                tickfont=dict(size=12, color="black"), showgrid=True, gridcolor="rgba(0,0,0,0.08)",
                linecolor="black", showline=True, linewidth=1
            ),
            template="plotly_white", 
            height=430,
            legend=dict(
                orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, 
                bgcolor="white", bordercolor="rgba(0,0,0,0.2)", borderwidth=1, font=dict(color="black", size=12)
            ),
            margin=dict(t=25, l=40, r=140, b=30)
        )
        
        _, col_center_3, _ = st.columns([0.2, 5.6, 0.2])
        with col_center_3:
            st.markdown('<div class="chart-title-single">Evolución Histórica por Caso de Uso</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_uc, use_container_width=True)

    # SUBTAB 2: DIMENSIÓN RECIENTE - CATÁLOGO
    with sub_tab2:
        df_colab = df_dim.copy() if not df_dim.empty else df_master.copy()

        if not df_colab.empty:
            if 'location_id' in df_colab.columns and 'port_id' in df_colab.columns:
                df_location_density = df_colab.groupby('location_id').agg(
                    total_ports=('port_id', 'count')
                ).reset_index()

                fig_location_split = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=("1. Vista Global", "2. Zoom Boxplot"),
                    horizontal_spacing=0.14
                )

                fig_location_split.add_trace(
                    go.Scatter(
                        x=[''] * len(df_location_density), y=df_location_density['total_ports'],
                        mode='markers', marker=dict(size=5, color='#3B82F6', opacity=0.5),
                        showlegend=False, hovertemplate="Ubicación: %{x}<br>Puertos: %{y}<extra></extra>"
                    ),
                    row=1, col=1
                )

                fig_location_split.add_trace(
                    go.Box(
                        y=df_location_density['total_ports'], boxpoints=False,
                        marker_color='#10B981', line=dict(color='#047857'),
                        showlegend=False, name=""
                    ),
                    row=1, col=2
                )

                fig_location_split.update_yaxes(
                    title_text="Número de Puertos", title_font=dict(size=14, color="black"),
                    tickfont=dict(size=12, color="black"), linecolor="black", showline=True, linewidth=1, row=1, col=1
                )
                fig_location_split.update_yaxes(
                    title_text="Número de Puertos (Zoom)", title_font=dict(size=14, color="black"),
                    tickfont=dict(size=12, color="black"), range=[-0.5, 20.5],
                    linecolor="black", showline=True, linewidth=1, row=1, col=2
                )
                
                fig_location_split.update_xaxes(
                    title_text="Ubicación", title_font=dict(size=14, color="black"),
                    showticklabels=False, linecolor="black", showline=True, linewidth=1, row=1, col=1
                )
                fig_location_split.update_xaxes(
                    title_text="Ubicación (zoom)", title_font=dict(size=14, color="black"),
                    showticklabels=False, linecolor="black", showline=True, linewidth=1, row=1, col=2
                )

                fig_location_split.update_layout(
                    font=dict(color="black", family="Arial"),
                    title="",
                    template='plotly_white', 
                    height=430,
                    margin=dict(t=35, l=40, r=20, b=25)
                )

                st.markdown('<div class="chart-title-single">Análisis de Dispersión y Estructura Cuartílica de Puertos por Ubicación</div>', unsafe_allow_html=True)
                st.plotly_chart(fig_location_split, use_container_width=True)

            st.markdown("---")

            lat_col = next((c for c in ['station_coordinates_latitude', 'latitude', 'lat'] if c in df_colab.columns), None)
            lon_col = next((c for c in ['station_coordinates_longitude', 'longitude', 'lon'] if c in df_colab.columns), None)
            addr_col = next((c for c in ['address_address_string', 'address', 'location_address'] if c in df_colab.columns), None)
            loc_id_col = next((c for c in ['location_id', 'station_id'] if c in df_colab.columns), None)
            onstreet_col = next((c for c in ['onstreet_location'] if c in df_colab.columns), None)

            if lat_col and lon_col and loc_id_col:
                agg_dict = {
                    'total_ports': ('port_id' if 'port_id' in df_colab.columns else df_colab.columns[0], 'count'),
                    'lat': (lat_col, 'first'), 'lon': (lon_col, 'first')
                }
                if addr_col: agg_dict['address'] = (addr_col, 'first')
                if onstreet_col: agg_dict['onstreet_location'] = (onstreet_col, 'first')

                df_location_density = df_colab.groupby(loc_id_col).agg(**agg_dict).reset_index().dropna(subset=['lat', 'lon'])
                
                if 'address' not in df_location_density.columns: df_location_density['address'] = "Ubicación Endolla"

                if 'onstreet_location' in df_location_density.columns:
                    df_location_density['ubicacion_tipo'] = df_location_density['onstreet_location'].map({
                        True: 'Calle', False: 'Parking'
                    }).fillna('Desconocido')
                    color_arg = 'ubicacion_tipo'
                else:
                    color_arg = None
                    
                fig_loc_map = px.scatter_mapbox(
                    df_location_density, lat='lat', lon='lon', size='total_ports', color=color_arg, size_max=24,
                    color_discrete_map={'Parking': "#1F56EC", 'Calle': "#F80909"},
                    hover_name='address', hover_data={'lat': False, 'lon': False, 'total_ports': True, 'ubicacion_tipo': False},
                    zoom=12.65,
                    center={'lat': 41.4020, 'lon': 2.1620},
                    opacity=0.85
                )

                fig_loc_map.update_layout(
                    font=dict(color="black", family="Arial"),
                    title="",
                    mapbox_style="open-street-map", 
                    height=530,
                    margin=dict(t=20, l=0, r=0, b=0)
                )

                config_hd = {
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'mapa_red_endolla_hd',
                        'height': 850,
                        'width': 1300,
                        'scale': 3
                    }
                }

                st.markdown('<div class="chart-title-single">Distribución y Capacidad de Ubicaciones (Red Endolla)</div>', unsafe_allow_html=True)
                st.plotly_chart(fig_loc_map, use_container_width=True, config=config_hd)

    # SUBTAB 3: TELEMETRÍA & TABLA DE HECHOS
    with sub_tab3:
        st.markdown("Análisis de eventos de telemetría, cobertura histórica y patrones temporales de disponibilidad.")

        if 'df_master' in locals() or 'df_master' in globals():
            df_fact = df_master.copy()
            if 'event_timestamp' in df_fact.columns:
                df_fact['event_timestamp'] = pd.to_datetime(df_fact['event_timestamp'])
                df_fact['year'] = df_fact['event_timestamp'].dt.year
                df_fact['month'] = df_fact['event_timestamp'].dt.month
                df_fact['hour'] = df_fact['event_timestamp'].dt.hour
                df_fact['day_of_week_name'] = df_fact['event_timestamp'].dt.day_name()
                
            col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
            col_b1.metric("Total Eventos", f"{len(df_fact):,}")
            col_b2.metric("Puertos Activos", f"{df_fact['station_port_sk'].nunique():,}" if 'station_port_sk' in df_fact.columns else "N/A")
            col_b3.metric("Estaciones", f"{df_fact['station_id'].nunique():,}" if 'station_id' in df_fact.columns else "N/A")
            col_b4.metric("Ubicaciones", f"{df_fact['location_id'].nunique():,}" if 'location_id' in df_fact.columns else "N/A")
            avail_global_pct = (df_fact['target_is_available'].sum() / len(df_fact)) * 100 if 'target_is_available' in df_fact.columns and len(df_fact) > 0 else 0
            col_b5.metric("Disponibilidad Global", f"{avail_global_pct:.1f}%")

            st.markdown("---")

            # 1. ANÁLISIS DE FRECUENCIA TEMPORAL
            temporal_level = st.selectbox(
                "Selecciona el nivel de agregación temporal para la distribución de eventos:",
                ["Mensual (Meses del año)", "Semanal (Días de la semana)", "Horario (Horas del día)"],
                key="telemetry_temporal_level"
            )

            if "Mensual" in temporal_level:
                month_dist_df = df_fact['month'].value_counts().sort_index().reset_index()
                month_dist_df.columns = ['month_num', 'Event_Count']
                import calendar
                month_dist_df['Month_Name'] = month_dist_df['month_num'].apply(lambda m: calendar.month_name[m])
                month_dist_df['Percentage'] = (month_dist_df['Event_Count'] / len(df_fact)) * 100

                current_title = "⏱️ Distribución Porcentual de Eventos por Mes"
                fig_temp = px.bar(
                    month_dist_df, x='Month_Name', y='Percentage',
                    text=month_dist_df['Percentage'].apply(lambda x: f"{x:.1f}%"),
                    labels={'Month_Name': 'Mes', 'Percentage': 'Eventos Telemétricos (%)'}
                )

            elif "Semanal" in temporal_level:
                dow_dist_df = df_fact['day_of_week_name'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index()
                dow_dist_df.columns = ['Day', 'Event_Count']
                dow_dist_df['Day_ES'] = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                dow_dist_df['Percentage'] = (dow_dist_df['Event_Count'] / len(df_fact)) * 100

                current_title = "⏱️ Distribución Porcentual de Eventos por Día de la Semana"
                fig_temp = px.bar(
                    dow_dist_df, x='Day_ES', y='Percentage',
                    text=dow_dist_df['Percentage'].apply(lambda x: f"{x:.1f}%"),
                    labels={'Day_ES': 'Día de la Semana', 'Percentage': 'Eventos Telemétricos (%)'}
                )
            else:
                hour_dist_df = df_fact['hour'].value_counts().sort_index().reset_index()
                hour_dist_df.columns = ['Hour', 'Event_Count']
                hour_dist_df['Hour_Str'] = hour_dist_df['Hour'].apply(lambda h: f"{h:02d}:00")
                hour_dist_df['Percentage'] = (hour_dist_df['Event_Count'] / len(df_fact)) * 100

                current_title = "⏱️ Distribución Porcentual de Eventos por Hora del Día"
                fig_temp = px.bar(
                    hour_dist_df, x='Hour_Str', y='Percentage',
                    text=hour_dist_df['Percentage'].apply(lambda x: f"{x:.1f}%"),
                    labels={'Hour_Str': 'Hora del Día', 'Percentage': 'Eventos Telemétricos (%)'}
                )

            fig_temp.update_traces(
                textposition='outside', 
                marker_color='#2b5c8f',
                textfont=dict(color="black", size=12, family="Arial")
            )
            
            if "Horario" in temporal_level:
                fig_temp.update_xaxes(tickangle=-45)

            fig_temp.update_layout(
                font=dict(color="black", family="Arial"),
                title="",
                template='plotly_white', 
                height=430,
                margin=dict(t=25, l=40, r=20, b=40)
            )
            
            fig_temp.update_xaxes(
                title_font=dict(size=14, color="black"),
                tickfont=dict(size=12, color="black"),
                linecolor="black", showline=True, linewidth=1 
            )
            
            fig_temp.update_yaxes(
                title_text="Eventos Telemétricos (%)",
                title_font=dict(size=14, color="black"),
                showticklabels=False, 
                ticks='',
                showgrid=False,
                showline=True, 
                linecolor="black",
                linewidth=1
            )
            
            _, col_c_temp, _ = st.columns([0.2, 5.6, 0.2])
            with col_c_temp:
                st.markdown(f'<div class="chart-title-single">{current_title}</div>', unsafe_allow_html=True)
                st.plotly_chart(fig_temp, use_container_width=True)

            st.markdown("---")

            # 2. COBERTURA ANUAL DE EVENTOS Y PUERTOS
            if 'year' in df_fact.columns:
                annual_telemetry = (
                    df_fact.groupby('year')
                    .agg(
                        total_events=('event_timestamp', 'count') if 'event_timestamp' in df_fact.columns else ('target_is_available', 'count'),
                        unique_active_ports=('station_port_sk', 'nunique') if 'station_port_sk' in df_fact.columns else ('year', 'count'),
                        unique_stations=('station_id', 'nunique') if 'station_id' in df_fact.columns else ('year', 'count')
                    ).reset_index()
                )
                
                fig_annual_cov = go.Figure()
                
                fig_annual_cov.add_trace(go.Bar(
                    x=annual_telemetry['year'].astype(str), y=annual_telemetry['total_events'],
                    name='Eventos por Año', marker_color='#2b5c8f',
                    text=annual_telemetry['total_events'].apply(lambda x: f"{x:,}"),
                    textposition='outside', textfont=dict(color="black", size=12, family="Arial")
                ))
                
                fig_annual_cov.add_trace(go.Scatter(
                    x=annual_telemetry['year'].astype(str), y=annual_telemetry['unique_active_ports'],
                    name='Puertos Activos', yaxis='y2', mode='lines+markers+text',
                    line=dict(color='#10B981', width=2.5), marker=dict(size=7),
                    text=annual_telemetry['unique_active_ports'].apply(lambda x: f"{x:,}"),
                    textposition='top center', textfont=dict(color="black", size=12, family="Arial")
                ))
                
                fig_annual_cov.update_layout(
                    font=dict(color="black", family="Arial"),
                    title="",
                    xaxis=dict(
                        title=dict(text='Año', font=dict(size=14, color="black")),
                        tickfont=dict(size=12, color="black"), 
                        type='category', 
                        linecolor="black", showline=True, linewidth=1 
                    ),
                    yaxis=dict(
                        title=dict(text='Número de Eventos', font=dict(size=14, color="black")),
                        showticklabels=False,  
                        ticks='',              
                        range=[0, 8500], 
                        showgrid=True, gridcolor='rgba(0,0,0,0.08)',
                        linecolor="black", showline=True, linewidth=1 
                    ),
                    yaxis2=dict(
                        title=dict(text='Puertos Activos', font=dict(size=14, color="black")),
                        showticklabels=False,  
                        ticks='',              
                        overlaying='y', side='right', showgrid=False,
                        range=[0, 1650],
                        linecolor="black", showline=True, linewidth=1 
                    ),
                    template='plotly_white', 
                    height=430,
                    legend=dict(
                        orientation="v", 
                        yanchor="middle", y=0.5, 
                        xanchor="left", x=1.12, 
                        bgcolor="white", bordercolor="rgba(0,0,0,0.2)", borderwidth=1,
                        font=dict(color="black", size=12)
                    ),
                    margin=dict(t=25, l=40, r=180, b=40)
                )
                
                _, col_c_ann, _ = st.columns([0.2, 5.6, 0.2])
                with col_c_ann:
                    st.markdown('<div class="chart-title-single">📈 Cobertura Anual de Eventos de Telemetría vs. Puertos Activos</div>', unsafe_allow_html=True)
                    st.plotly_chart(fig_annual_cov, use_container_width=True)

            st.markdown("---")

            # 3. MAPA DE CALOR: DISPONIBILIDAD
            if 'target_is_available' in df_fact.columns and 'hour' in df_fact.columns and 'day_of_week_name' in df_fact.columns:
                df_fact['hour_str'] = df_fact['hour'].apply(lambda h: f"{h:02d}:00")
                heatmap_data = pd.crosstab(
                    df_fact['day_of_week_name'], df_fact['hour_str'], 
                    values=df_fact['target_is_available'], 
                    aggfunc=lambda x: (x.sum() / len(x)) * 100
                ).reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).fillna(0)

                fig_heatmap = px.imshow(
                    heatmap_data, labels=dict(x="Hora del Día", y="Día de la Semana", color="Disponibilidad (%)"),
                    x=heatmap_data.columns, y=['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
                    color_continuous_scale="Viridis", zmin=50, zmax=100, aspect="auto"
                )

                fig_heatmap.update_layout(
                    font=dict(color="black", family="Arial"),
                    title="",
                    template='plotly_white', 
                    height=430,
                    margin=dict(t=25, l=0, r=0, b=40),
                    legend=dict(font=dict(color="black", size=12))
                )

                fig_heatmap.update_xaxes(
                    tickangle=-45, 
                    title_font=dict(size=14, color="black"),
                    tickfont=dict(size=12, color="black"),
                    linecolor="black", showline=True, linewidth=1 
                )

                fig_heatmap.update_yaxes(
                    title_font=dict(size=14, color="black"),
                    tickfont=dict(size=12, color="black"),
                    linecolor="black", showline=True, linewidth=1 
                )
        else:
            st.warning("El DataFrame 'df_master' no está disponible en el entorno actual para procesar la telemetría.")

# SECCIÓN 3: RED ACTIVA CONSOLIDADA
with tab_eda:
    st.markdown("Análisis del crecimiento histórico acumulado, distribución por casos de uso y perfil técnico de conectores y potencias nominales.")

    # 1. PREPARACIÓN AUTOMÁTICA DE DATOS DESDE df_master
    df = df_master.copy()

    if 'year' not in df.columns:
        if 'event_timestamp' in df.columns:
            df['year'] = pd.to_datetime(df['event_timestamp']).dt.year
        elif 'timestamp' in df.columns:
            df['year'] = pd.to_datetime(df['timestamp']).dt.year

    port_col = 'station_port_sk' if 'station_port_sk' in df.columns else ('port_id' if 'port_id' in df.columns else 'station_id')
    power_col = 'port_power_kw' if 'port_power_kw' in df.columns else ('power_kw' if 'power_kw' in df.columns else 'kw')
    connector_col = 'port_connector_type' if 'port_connector_type' in df.columns else ('connector_type' if 'connector_type' in df.columns else 'conector')
    uc_col = 'use_case' if 'use_case' in df.columns else ('caso_uso' if 'caso_uso' in df.columns else 'access_type')

    df_active_by_year = df.drop_duplicates(subset=['year', port_col]).copy()

    # 2. DETALLE DE POTENCIAS POR TIPO DE CONECTOR
    st.subheader("Distribución de Puertos por Conector y Potencia Nominal")
    df_active_ports = df.drop_duplicates(subset=[port_col], keep='last').copy()

    def standardize_power(kw):
        try:
            val = float(kw)
            if val in [3.20, 3.60, 3.68]:
                return '3.6 kW'
            elif val in [7.20, 7.36]:
                return '7.2 kW'
            elif val == 22.00:
                return '22.0 kW'
            elif val == 50.00:
                return '50.0 kW'
            elif val in [43.00, 44.00]:
                return '43-44 kW'
            else:
                return f'{val} kW'
        except (ValueError, TypeError):
            return 'Desconocido'

    df_active_ports['power_clean'] = df_active_ports[power_col].apply(standardize_power)

    # Conteo total por tipo de conector
    conn_totals = df_active_ports.groupby(connector_col).size().reset_index(name='total')

    # Ordenar de menor a mayor para que el menor quede en la parte superior en Plotly
    conn_totals_sorted = conn_totals.sort_values(by='total', ascending=True)
    connector_order = conn_totals_sorted[connector_col].tolist()

    category_order = ['3.6 kW', '7.2 kW', '22.0 kW', '50.0 kW', '43-44 kW']

    fig_power_conn_clean = px.histogram(
        df_active_ports, 
        y=connector_col, 
        color='power_clean',
        orientation='h',
        category_orders={
            'power_clean': category_order,
            connector_col: connector_order
        },
        labels={
            connector_col: 'Tipo de Conector', 
            'count': 'Cantidad de Puertos Activos', 
            'power_clean': 'Potencia Instalada'
        },
        color_discrete_map={
            '3.6 kW': '#1f77b4',
            '7.2 kW': "#62a5d4",
            '22.0 kW': "#b0c7fc",
            '50.0 kW': '#d62728',
            '43-44 kW': '#f3acb8'
        }
    )
    fig_power_conn_clean.add_trace(go.Scatter(
        x=conn_totals['total'],
        y=conn_totals[connector_col],
        mode="text",
        text=[f" {val}" for val in conn_totals['total']],
        textposition="middle right",
        textfont=dict(color="black", size=12, family="Arial"),
        showlegend=False,
        hoverinfo="skip"
    ))

    max_conn_ports = conn_totals['total'].max()

    fig_power_conn_clean.update_layout(
        font=dict(color="black", family="Arial"),
        template="plotly_white",
        height=380,
        margin=dict(t=20, l=40, r=160, b=40),
        legend=dict(
            title=dict(text="Potencia Nominal", font=dict(size=12, color="black")),
            font=dict(color="black", size=12),
            bgcolor="white", 
            bordercolor="rgba(0,0,0,0.2)", 
            borderwidth=1,
            x=1.02,
            y=0.5,
            yanchor="middle"
        )
    )
    fig_power_conn_clean.update_xaxes(
        title=dict(text="Cantidad de Puertos Activos", font=dict(size=14, color="black")), 
        showticklabels=False,
        range=[0, max_conn_ports * 1.15],
        linecolor="black", showline=True
    )
    fig_power_conn_clean.update_yaxes(
        title=dict(text="Tipo de Conector", font=dict(size=14, color="black")), 
        tickfont=dict(size=12, color="black"), 
        linecolor="black", showline=True
    )

    st.plotly_chart(fig_power_conn_clean, use_container_width=True)