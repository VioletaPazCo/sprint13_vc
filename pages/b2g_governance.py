import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# Mapeo global de colores para tipos de conector
CONNECTOR_COLOR_MAP = {
    'MENNEKES': '#6baed6',
    'Mennekes (AC)': '#6baed6',
    'WALL_OUTLET': '#1f77b4',
    'Wall Outlet (Schuko)': '#1f77b4',
    'CCS_TYPE_2': "#f3acb8",
    'CCS Combo 2 (DC)': '#f3acb8',
    'CHADEMO': '#d62728',
    'CHAdeMO (DC)': '#d62728',
    'Unknown': '#7f7f7f'
}

# 1. Configuración de la página y CSS personalizado
st.set_page_config(
    page_title="Endolla B2G — Gobernanza de Red",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none; }
        .kpi-card-subtext {
            font-size: 12px;
            color: #6c757d;
            margin-top: -10px;
            margin-bottom: 10px;
        }
        .metric-banner {
            background-color: #f8f9fa;
            border-left: 4px solid #1f77b4;
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Gobernanza de Datos - Red ENDOLLA Barcelona (B2G)")
st.markdown("Cuadro de mando para la gestión pública: monitorización de la integridad telemétrica, fallos de sensores y gobernanza de catálogos desincronizados.")

# 2. Carga de datos
@st.cache_data
def load_b2g_data():
    df_gold_metadata = pd.read_parquet("stations_metadata.parquet")
    df_active_ports = pd.read_parquet("b2c_active_master_ports.parquet")
    df_orphan_events = pd.read_parquet("b2g_quarantine_orphans.parquet")
    df_epoch_faults = pd.read_parquet("b2g_quarantine_epoch.parquet")
    df_desynced_assets = pd.read_parquet("b2g_desynced_ghost_ports.parquet")
    
    try:
        df_orphaned_catalog = pd.read_parquet("b2g_orphaned_catalog_entities.parquet")
    except Exception:
        df_orphaned_catalog = pd.DataFrame()
    
    return df_gold_metadata, df_active_ports, df_orphan_events, df_epoch_faults, df_desynced_assets, df_orphaned_catalog

try:
    df_gold, df_active, df_orphans, df_epoch, df_desynced, df_orphaned_cat = load_b2g_data()
    is_data_loaded = True
except Exception as loading_error:
    st.error(f"Error al cargar los artefactos de producción: {loading_error}")
    st.info("Verifica que los archivos .parquet necesarios se encuentren en el directorio raíz.")
    is_data_loaded = False

# Funciones auxiliares
def get_unique_ports_count(df):
    if df.empty or len(df.columns) == 0:
        return 0
    for col in ['station_port_sk', 'port_id', 'port_sk']:
        if col in df.columns:
            return df[col].nunique()
    return len(df)

def aggregate_other_layer_locations(df):
    if df.empty or len(df.columns) == 0:
        return pd.DataFrame()
        
    lat_col = 'latitude' if 'latitude' in df.columns else ('station_coordinates_latitude' if 'station_coordinates_latitude' in df.columns else None)
    lon_col = 'longitude' if 'longitude' in df.columns else ('station_coordinates_longitude' if 'station_coordinates_longitude' in df.columns else None)
    loc_col = 'location_id' if 'location_id' in df.columns else None
    
    if not lat_col or not lon_col:
        return pd.DataFrame()
        
    df_valid = df.dropna(subset=[lat_col, lon_col]).copy()
    if df_valid.empty:
        return pd.DataFrame()

    port_col = 'station_port_sk' if 'station_port_sk' in df_valid.columns else df_valid.columns[0]
    
    agg_dict = {
        'latitude': (lat_col, 'first'),
        'longitude': (lon_col, 'first'),
        'total_ports': (port_col, 'nunique'),
        'total_records': (port_col, 'count'),
    }
    
    if loc_col:
        agg_dict['unique_locations_count'] = (loc_col, 'nunique')
        
    if 'address_address_string' in df_valid.columns:
        agg_dict['address'] = ('address_address_string', 'first')

    grouped = df_valid.groupby([lat_col, lon_col]).agg(**agg_dict).reset_index(drop=True)
    return grouped

# 3. Filtrado de Red Activa a la Ventana Deslizante (365 Días) & KPIs
if is_data_loaded:
    date_fact_col = 'event_timestamp' if 'event_timestamp' in df_active.columns else ('event_timestamp_dt' if 'event_timestamp_dt' in df_active.columns else None)
    
    if date_fact_col and not df_active.empty:
        df_active[date_fact_col] = pd.to_datetime(df_active[date_fact_col])
        max_dt = df_active[date_fact_col].max()
        active_threshold_dt = max_dt - pd.Timedelta(days=365)
        
        port_last_seen = df_active.groupby('station_port_sk')[date_fact_col].max()
        active_ports_365_sk = port_last_seen[port_last_seen >= active_threshold_dt].index
        
        # Ajuste horizonte temporal: Filtrar registros de la ventana activa de 365 días
        df_active_sane = df_active[
            (df_active['station_port_sk'].isin(active_ports_365_sk)) & 
            (df_active[date_fact_col] >= active_threshold_dt)
        ].copy()
    else:
        df_active_sane = df_active.copy()

    # Conteos oficiales
    active_ports_count = df_active_sane['station_port_sk'].nunique() if 'station_port_sk' in df_active_sane.columns else get_unique_ports_count(df_active_sane)
    total_historical_ports = df_active['station_port_sk'].nunique() if 'station_port_sk' in df_active.columns else active_ports_count
    
    orphan_ports_count = get_unique_ports_count(df_orphans)
    orphan_events_count = len(df_orphans)
    epoch_ports_count = get_unique_ports_count(df_epoch)
    epoch_events_count = len(df_epoch)
    desynced_ports_count = get_unique_ports_count(df_desynced)

    # Render de Tarjetas KPI
    col_active, col_orphan, col_epoch, col_desync = st.columns(4)
    
    col_active.metric("🟢 Puertos Activos Sanos", f"{active_ports_count:,}")
    col_active.markdown(f"<div class='kpi-card-subtext'>({active_ports_count / total_historical_ports * 100:.1f}% de {total_historical_ports:,} históricos)</div>", unsafe_allow_html=True)
    
    col_orphan.metric("🔴 Registros Huérfanos", f"{orphan_ports_count:,} puertos")
    col_orphan.markdown(f"<div class='kpi-card-subtext'>({orphan_events_count:,} eventos en cuarentena)</div>", unsafe_allow_html=True)
    
    col_epoch.metric("⚙️ Fallos de Sensor Epoch", f"{epoch_ports_count:,} puertos")
    col_epoch.markdown(f"<div class='kpi-card-subtext'>({epoch_events_count:,} eventos detectados)</div>", unsafe_allow_html=True)

    col_desync.metric("🟡 Gobernanza Desincronizada", f"{desynced_ports_count:,} puertos")
    col_desync.markdown("<div class='kpi-card-subtext'>(Catálogo vs Telemetría Lag)</div>", unsafe_allow_html=True)

    # 4. Panel Lateral de Control (Sidebar)
    st.sidebar.header("🔍 Filtros de Gobernanza")
    selected_view_mode = st.sidebar.radio(
        "Seleccione la Capa a Inspeccionar:",
        [
            "🟢 Red Activa Sana",
            "🔴 Registros Telemétricos Huérfanos",
            "⚙️ Fallos de Sensor Epoch",
            "🟡 Activos Silenciosos (Desincronizados)"
        ]
    )

    if "Red Activa Sana" in selected_view_mode:
        current_df = df_active_sane
        layer_color = "green"
        layer_name = "Red Activa"
        badge = "🟢 Activo / Sano"
    elif "Registros Telemétricos Huérfanos" in selected_view_mode:
        current_df = df_orphans
        layer_color = "red"
        layer_name = "Registros Huérfanos"
        badge = "🔴 Cuarentena / Huérfano"
    elif "Fallos de Sensor Epoch" in selected_view_mode:
        current_df = df_epoch
        layer_color = "purple"
        layer_name = "Fallos Epoch"
        badge = "⚙️ Fallo Epoch"
    else:
        current_df = df_desynced
        layer_color = "orange"
        layer_name = "Gobernanza Desincronizada"
        badge = "🟡 SKU Desincronizado / Lag"

    st.subheader(f"Capa Visualización: {selected_view_mode}")

    # 5. Banner de Resumen
    temporal_range = "Sin registro temporal"
    found_date_col = next((col for col in ['event_timestamp', 'event_timestamp_dt', 'port_last_updated', 'last_updated'] if col in current_df.columns), None) if not current_df.empty else None
    
    if found_date_col and not current_df.empty:
        try:
            time_series = pd.to_datetime(current_df[found_date_col], errors='coerce').dropna()
            if "Registros Telemétricos Huérfanos" in selected_view_mode:
                time_series = time_series[time_series >= "1971-01-01"]
                
            if not time_series.empty:
                min_date_str = time_series.min().strftime('%Y-%m-%d')
                max_date_str = time_series.max().strftime('%Y-%m-%d')
                temporal_range = f"{min_date_str} a {max_date_str}"
        except Exception:
            pass

    if "Red Activa Sana" in selected_view_mode:
        unique_locations = df_gold['location_id'].nunique() if 'location_id' in df_gold.columns else len(df_gold)
        unique_stations = current_df['station_id'].nunique() if 'station_id' in current_df.columns else "N/A"
        unique_ports = active_ports_count
        power_info = f"{df_gold['min_power_kw'].min():.1f} kW / {df_gold['max_power_kw'].median():.1f} kW / {df_gold['max_power_kw'].max():.1f} kW" if 'max_power_kw' in df_gold.columns else "N/A"
    else:
        unique_locations = current_df['location_id'].nunique() if ('location_id' in current_df.columns and not current_df.empty) else "N/A"
        unique_stations = current_df['station_id'].nunique() if ('station_id' in current_df.columns and not current_df.empty) else "N/A"
        unique_ports = get_unique_ports_count(current_df)
        power_info = "N/A"
        if 'port_power_kw' in current_df.columns and current_df['port_power_kw'].notnull().any():
            min_p = current_df['port_power_kw'].min()
            med_p = current_df['port_power_kw'].median()
            max_p = current_df['port_power_kw'].max()
            power_info = f"{min_p:.1f} kW / {med_p:.1f} kW / {max_p:.1f} kW"

    st.markdown(
        f"""
        <div class="metric-banner">
            <b>Resumen de la Capa Seleccionada ({layer_name}):</b><br>
            • <b>Horizonte Temporal:</b> {temporal_range}<br>
            • <b>Alcance Físico:</b> {unique_locations} Ubicaciones Únicas | {unique_stations} Estaciones | {unique_ports} Puertos Únicos<br>
            • <b>Rango de Potencia (Mín / Mediana / Máx):</b> {power_info}
        </div>
        """,
        unsafe_allow_html=True
    )

    # 6. Renderizado del Mapa Folium
    st.markdown("### Mapa de Infraestructura")
    map_object = folium.Map(location=[41.3851, 2.1734], zoom_start=13, tiles="OpenStreetMap")

    if "Red Activa Sana" in selected_view_mode:
        for idx, loc_row in df_gold.iterrows():
            loc_address = loc_row.get('address_address_string', f"Ubicación ID: {loc_row.get('location_id')}")
            car_pts = int(loc_row.get('car_ports_count', 0))
            moto_pts = int(loc_row.get('moto_ports_count', 0))
            onstreet = loc_row.get('onstreet_location', True)
            
            location_type_label = "Calle" if onstreet else "Parking"
            specific_icon = "tree" if onstreet else "parking"
            
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; width: 210px;">
                <span style="font-size: 11px; color: #555; font-weight: bold; text-transform: uppercase;">{location_type_label}</span>
                <h4 style="margin: 4px 0 8px 0; color: #2C3E50; font-size: 13px;">{loc_address}</h4>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 5px 0;">
                <ul style="padding-left: 15px; margin: 5px 0; font-size: 12px; color: #333;">
                    <li><b>Coche:</b> {car_pts} puertos</li>
                    <li><b>Moto:</b> {moto_pts} puertos</li>
                </ul>
                <div style="margin-top: 8px; padding: 4px; background-color: #f8f9fa; border-radius: 4px; text-align: center;">
                    <span style="font-size: 11px; font-weight: bold;">{badge}</span>
                </div>
            </div>
            """
            
            folium.Marker(
                location=[loc_row['latitude'], loc_row['longitude']],
                popup=folium.Popup(popup_html, max_width=240),
                icon=folium.Icon(color=layer_color, icon=specific_icon, prefix="fa"),
                tooltip=f"{loc_address} ({location_type_label})"
            ).add_to(map_object)
    else:
        df_layer_agg = aggregate_other_layer_locations(current_df)
        if not df_layer_agg.empty:
            for idx, loc_row in df_layer_agg.iterrows():
                lat = loc_row['latitude']
                lon = loc_row['longitude']
                total_ports = int(loc_row['total_ports'])
                address = loc_row.get('address', 'Ubicación sin dirección explícita')
                
                specific_icon = "tree"
                location_type_label = "Calle / Auditoría"
                
                popup_html = f"""
                <div style="font-family: Arial, sans-serif; width: 230px;">
                    <span style="font-size: 11px; color: #555; font-weight: bold; text-transform: uppercase;">{location_type_label}</span>
                    <p style="font-size: 12px; color: #2C3E50; font-weight: bold; margin: 4px 0;">{address}</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 5px 0;">
                    <p style="font-size: 12px; color: #333; margin: 5px 0;"><b>Puertos Afectados:</b> {total_ports}</p>
                    <div style="margin-top: 8px; padding: 4px; background-color: #f8f9fa; border-radius: 4px; text-align: center;">
                        <span style="font-size: 11px; font-weight: bold;">{badge}</span>
                    </div>
                </div>
                """
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=250),
                    icon=folium.Icon(color=layer_color, icon=specific_icon, prefix="fa"),
                    tooltip=f"{address} — {total_ports} puertos"
                ).add_to(map_object)

    st_folium(map_object, width=None, use_container_width=True, height=500)

# 7. Visualizaciones
    if "Registros Telemétricos Huérfanos" not in selected_view_mode:
        st.markdown("### Detalle de Atributos de Infraestructura")
        
        # Identificar la columna clave del puerto
        port_col = next((col for col in ['station_port_sk', 'port_id', 'port_sk'] if col in current_df.columns), current_df.columns[0] if not current_df.empty else None)
        
        if port_col and not current_df.empty:
            # Deduplicar a nivel de puerto único activo
            df_ports_unique = current_df.drop_duplicates(subset=[port_col]).copy()
            
            # Enriquecer atributos 'use_case' y 'onstreet_location' desde df_gold si no están presentes
            cols_to_merge = [c for c in ['use_case', 'onstreet_location'] if c in df_gold.columns and c not in df_ports_unique.columns]
            if cols_to_merge and 'location_id' in df_ports_unique.columns and 'location_id' in df_gold.columns:
                df_ports_unique = df_ports_unique.merge(
                    df_gold[['location_id'] + cols_to_merge].drop_duplicates(subset=['location_id']), 
                    on='location_id', 
                    how='left'
                )

            # Mapeo directo usando el atributo oficial 'use_case'
            def parse_use_case_attributes(row):
                uc = str(row.get('use_case', ''))
                
                # 1. Clasificación por Ubicación
                if 'Off-Street' in uc:
                    location_type = 'Parking'
                elif 'On-Street' in uc:
                    location_type = 'Calle'
                else:
                    location_type = 'Calle' if bool(row.get('onstreet_location', True)) else 'Parking'
                    
                # 2. Clasificación por Tipo de Vehículo
                if 'Moto' in uc:
                    vehicle_type = 'Motocicleta'
                elif 'General' in uc:
                    vehicle_type = 'Coche / VE'
                else:
                    conn = str(row.get('port_connector_type', '')).upper()
                    vehicle_type = 'Motocicleta' if 'MOTO' in conn else 'Coche / VE'
                    
                return pd.Series([vehicle_type, location_type], index=['Tipo_Vehiculo', 'Tipo_Ubicacion'])

            df_ports_unique[['Tipo_Vehiculo', 'Tipo_Ubicacion']] = df_ports_unique.apply(parse_use_case_attributes, axis=1)
        else:
            df_ports_unique = pd.DataFrame()

        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            if not df_ports_unique.empty:
                # Resumen con conteo exacto de puertos únicos
                uc_summary = df_ports_unique.groupby(['Tipo_Vehiculo', 'Tipo_Ubicacion']).size().reset_index(name='Puertos_Unicos')

                fig_uc = px.bar(
                    uc_summary, 
                    x='Tipo_Vehiculo', 
                    y='Puertos_Unicos', 
                    color='Tipo_Ubicacion',
                    barmode='group', 
                    title="<b>Casos de uso (Puertos Únicos)</b>",
                    color_discrete_map={'Parking': '#1E40AF', 'Calle': '#10B981'},
                    labels={'Puertos_Unicos': 'Puertos Únicos', 'Tipo_Vehiculo': ''},
                    text_auto=True
                )
                fig_uc.update_traces(textposition='outside')
                fig_uc.update_xaxes(showline=True, linewidth=1, linecolor='black', tickfont=dict(color='black'), title_font=dict(color='black'))
                fig_uc.update_yaxes(
                    showticklabels=False, 
                    showgrid=False, 
                    showline=True, 
                    linewidth=1, 
                    linecolor='black', 
                    title="Puertos Únicos",
                    title_font=dict(color='black')
                )
                fig_uc.update_layout(
                    margin=dict(l=10, r=10, t=50, b=20),
                    height=350,
                    font=dict(color='black'),
                    legend_title_font=dict(color='black'),
                    legend_font=dict(color='black')
                )
                st.plotly_chart(fig_uc, use_container_width=True)
            else:
                st.info("Sin datos o atributos de caso de uso disponibles para esta capa.")

        with row1_col2:
            conn_col = next((c for c in ['port_connector_type', 'connector_type'] if c in df_ports_unique.columns), None)
            if not df_ports_unique.empty and conn_col:
                conn_series = df_ports_unique[conn_col].fillna('Unknown')
                connector_counts = conn_series.value_counts().reset_index()
                connector_counts.columns = ['Tipo_Conector', 'Cantidad']
                
                fig_pie = px.pie(
                    connector_counts, 
                    names='Tipo_Conector', 
                    values='Cantidad', 
                    title="<b>Puertos Únicos por Tipo de Conector</b>", 
                    hole=0.4,
                    color='Tipo_Conector', 
                    color_discrete_map=CONNECTOR_COLOR_MAP
                )
                fig_pie.update_traces(hovertemplate="<b>%{label}</b><br>Puertos: %{value}<br>Cuota: %{percent}<extra></extra>")
                fig_pie.update_layout(
                    margin=dict(l=10, r=10, t=50, b=20),
                    height=350,
                    font=dict(color='black'),
                    legend_title_font=dict(color='black'),
                    legend_font=dict(color='black')
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("ℹ️ Tipos de conector no disponibles para esta capa.")


# Destalle de potencia por tipo de conector (Exclusivo de Red Activa Sana)
    if "Red Activa Sana" in selected_view_mode:
        st.markdown("---")
        st.subheader("3.3. Distribución de Puertos por Conector y Potencia Nominal")

        port_col = 'station_port_sk' if 'station_port_sk' in df_active_sane.columns else df_active_sane.columns[0]
        power_col = next((c for c in ['port_power_kw', 'power_kw', 'max_power_kw'] if c in df_active_sane.columns), None)
        connector_col = next((c for c in ['port_connector_type', 'connector_type'] if c in df_active_sane.columns), None)

        if power_col and connector_col and not df_active_sane.empty:
            df_active_ports = df_active_sane.drop_duplicates(subset=[port_col], keep='last').copy()

            def standardize_power(kw):
                try:
                    # Ajuste 1: Redondeo a 2 decimales
                    val = round(float(kw), 2)
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

            # Cálculo de totales por conector para ordenar de mayor a menor
            conn_totals = df_active_ports.groupby(connector_col).size().reset_index(name='total')
            connector_order = conn_totals.sort_values(by='total', ascending=True)[connector_col].tolist()

            power_category_order = ['3.6 kW', '7.2 kW', '22.0 kW', '50.0 kW', '43-44 kW']

            fig_power_conn_clean = px.histogram(
                df_active_ports, 
                y=connector_col, 
                color='power_clean',
                orientation='h',
                category_orders={
                    connector_col: connector_order,
                    'power_clean': power_category_order
                },
                labels={
                    connector_col: 'Tipo de Conector', 
                    'count': '', 
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
                title="", 
                showticklabels=True,
                range=[0, max_conn_ports * 1.15],
                linecolor="black", showline=True
            )
            fig_power_conn_clean.update_yaxes(
                title=dict(text="Tipo de Conector", font=dict(size=14, color="black")), 
                tickfont=dict(size=12, color="black"), 
                linecolor="black", showline=True
            )

            st.plotly_chart(fig_power_conn_clean, use_container_width=True)

    # 8. Top Ubicaciones Afectadas
    if "Red Activa Sana" not in selected_view_mode:
        st.markdown("---")
        st.markdown("### Análisis de Afectación por Ubicación")
        if not current_df.empty and 'location_id' in current_df.columns:
            top_locs = current_df['location_id'].value_counts().head(10).reset_index()
            top_locs.columns = ['ID_Ubicacion', 'Total_Registros']
            top_locs['ID_Ubicacion'] = "Ubicación " + top_locs['ID_Ubicacion'].astype(str)
            top_locs = top_locs.iloc[::-1]

            fig_top_loc = px.bar(
                top_locs, x='Total_Registros', y='ID_Ubicacion', orientation='h',
                title=f"<b>Top 10 Ubicaciones Afectadas ({layer_name})</b>",
                color_discrete_sequence=['#e74c3c' if layer_color == 'red' else ('#f39c12' if layer_color == 'orange' else '#9b59b6')],
                labels={'ID_Ubicacion': ''},
                text_auto=True
            )
            fig_top_loc.update_traces(textposition='outside')
            fig_top_loc.update_xaxes(
                title="Total de Registros",
                title_font=dict(color='black', size=12),
                showline=True, 
                showticklabels=False,
                linewidth=1, 
                linecolor='black'
            )
            fig_top_loc.update_yaxes(
                showline=True, 
                linewidth=1, 
                linecolor='black', 
                tickfont=dict(color='black')
            )
            fig_top_loc.update_layout(
                margin=dict(l=10, r=10, t=50, b=30),
                height=350,
                font=dict(color='black')
            )
            st.plotly_chart(fig_top_loc, use_container_width=True)

    # 9. Auditoría de Eventos Huérfanos
    if "Registros Telemétricos Huérfanos" in selected_view_mode and not current_df.empty:
        st.markdown("---")
        st.markdown("### Auditoría de Causa Raíz (Cuarentena)")
        
        df_audit = current_df.copy()
        case_col = 'quarantine_audit_case' if 'quarantine_audit_case' in df_audit.columns else 'orphan_reason'
        
        if case_col in df_audit.columns:
            audit_summary = (
                df_audit.groupby(case_col)
                .agg(
                    event_count=('station_port_sk' if 'station_port_sk' in df_audit.columns else df_audit.columns[0], 'count'),
                    unique_ports=('station_port_sk' if 'station_port_sk' in df_audit.columns else df_audit.columns[0], 'nunique')
                )
                .reset_index()
                .rename(columns={case_col: 'Caso de Auditoría / Causa Raíz'})
                .sort_values(by='event_count', ascending=False)
            )
            
            total_events = len(df_audit)
            audit_summary['Porcentaje (%)'] = (audit_summary['event_count'] / total_events) * 100
            audit_summary['Estado en Mapa'] = audit_summary['Caso de Auditoría / Causa Raíz'].apply(
                lambda x: 'No (Coordenadas no mapeadas)' if str(x).startswith('Case C') else '✅ Sí (Geolocalizado)'
            )
            
            audit_summary = audit_summary[[
                'Caso de Auditoría / Causa Raíz',
                'event_count',
                'Porcentaje (%)',
                'Estado en Mapa',
                'unique_ports'
            ]].rename(columns={
                'event_count': 'Eventos Totales',
                'unique_ports': 'Puertos Afectados'
            })

            st.markdown("#### Tabla Resumen de Cuarentena")
            st.dataframe(
                audit_summary.style.format({
                    'Eventos Totales': '{:,}',
                    'Porcentaje (%)': '{:.2f}%',
                    'Puertos Afectados': '{:,}'
                }),
                use_container_width=True,
                hide_index=True
            )

            st.markdown("<br>**Desglose Agrupado por Causa Raíz**", unsafe_allow_html=True)
            unique_cases = sorted(df_audit[case_col].unique())
            
            tab_titles = []
            for c in unique_cases:
                if "Case A" in c:
                    tab_titles.append("📌 Caso A: Estación Válida | Puerto no Registrado")
                elif "Case B" in c:
                    tab_titles.append("📌 Caso B: Ubicación Válida | Estación y Puerto no Registrados")
                elif "Case C" in c:
                    tab_titles.append("📌 Caso C: Coordenadas No Mapeadas")
                else:
                    tab_titles.append(f"📌 {c}")
                    
            tabs = st.tabs(tab_titles)
            
            case_descriptions = {
                "Case A": "**Diagnóstico:** La ubicación y estación existen en el catálogo maestro, pero la telemetría emite valores de `port_id` no registrados.",
                "Case B": "**Diagnóstico:** La ubicación física existe en el catálogo, pero los IDs de estación y puerto no están registrados en el inventario activo.",
                "Case C": "**Diagnóstico:** Eventos emitidos con IDs de ubicación/estación inexistentes o coordenadas geográficas inválidas."
            }

            for tab, case_name in zip(tabs, unique_cases):
                with tab:
                    df_case = df_audit[df_audit[case_col] == case_name].copy()
                    
                    desc_key = next((k for k in case_descriptions if k in case_name), None)
                    if desc_key:
                        st.info(case_descriptions[desc_key])
                    
                    m_col1, m_col2, m_col3 = st.columns(3)
                    m_col1.metric("Eventos Afectados", f"{len(df_case):,}")
                    m_col2.metric("Estaciones Involucradas", f"{df_case['station_id'].nunique() if 'station_id' in df_case.columns else 'N/A'}")
                    m_col3.metric("Ubicaciones Involucradas", f"{df_case['location_id'].nunique() if 'location_id' in df_case.columns else 'N/A'}")
                    
                    case_grouped = df_case.groupby(['location_id', 'station_id']).agg(
                        quarantine_emitted_ports=('port_id', lambda x: sorted(list(set(str(p) for p in x.dropna())))),
                        quarantine_events=('location_id', 'count')
                    ).reset_index()
                    
                    case_grouped['quarantine_emitted_ports'] = case_grouped['quarantine_emitted_ports'].astype(str)
                    
                    case_grouped = case_grouped.rename(columns={
                        'location_id': 'ID Ubicación',
                        'station_id': 'ID Estación',
                        'quarantine_emitted_ports': 'Puertos Emitidos en Cuarentena',
                        'quarantine_events': 'Eventos Totales'
                    }).sort_values(by='Eventos Totales', ascending=False)

                    st.dataframe(
                        case_grouped,
                        use_container_width=True,
                        hide_index=True
                    )

    # 10. Auditoría para Gobernanza Desincronizada
    if "Activos Silenciosos" in selected_view_mode and not current_df.empty:
        st.markdown("---")
        st.markdown("### Auditoría de Causa Raíz — Activos Silenciosos / Desincronizados")
        
        drilldown_cols = [
            'location_id', 'station_id', 'port_id', 'station_port_sk', 
            'port_connector_type', 'port_power_kw', 'port_notes', 
            'active_stations_in_loc', 'active_ports_in_loc', 'active_connectors_in_loc'
        ]
        
        existing_drilldown_cols = [c for c in drilldown_cols if c in current_df.columns]
        if not existing_drilldown_cols:
            existing_drilldown_cols = current_df.columns.tolist()
            
        st.dataframe(
            current_df[existing_drilldown_cols],
            use_container_width=True,
            hide_index=True
        )