import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

from translations import t

# Global color mapping for connector types
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

# 1. Page configuration and custom CSS
st.set_page_config(
    page_title=t("app_title"),
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

st.title(t("header_title"))
st.markdown(t("header_subtitle"))

# 2. Data loading
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
    st.error(f"Error loading production artifacts: {loading_error}")
    st.info("Verify that necessary .parquet files exist in the root directory.")
    is_data_loaded = False

# Helper functions
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

# 3. Active Network Filtering & KPIs
if is_data_loaded:
    date_fact_col = 'event_timestamp' if 'event_timestamp' in df_active.columns else ('event_timestamp_dt' if 'event_timestamp_dt' in df_active.columns else None)
    
    if date_fact_col and not df_active.empty:
        df_active[date_fact_col] = pd.to_datetime(df_active[date_fact_col])
        max_dt = df_active[date_fact_col].max()
        active_threshold_dt = max_dt - pd.Timedelta(days=365)
        
        port_last_seen = df_active.groupby('station_port_sk')[date_fact_col].max()
        active_ports_365_sk = port_last_seen[port_last_seen >= active_threshold_dt].index
        
        df_active_sane = df_active[
            (df_active['station_port_sk'].isin(active_ports_365_sk)) & 
            (df_active[date_fact_col] >= active_threshold_dt)
        ].copy()
    else:
        df_active_sane = df_active.copy()

    # Official counts
    active_ports_count = df_active_sane['station_port_sk'].nunique() if 'station_port_sk' in df_active_sane.columns else get_unique_ports_count(df_active_sane)
    total_historical_ports = df_active['station_port_sk'].nunique() if 'station_port_sk' in df_active.columns else active_ports_count
    
    orphan_ports_count = get_unique_ports_count(df_orphans)
    orphan_events_count = len(df_orphans)
    epoch_ports_count = get_unique_ports_count(df_epoch)
    epoch_events_count = len(df_epoch)
    desynced_ports_count = get_unique_ports_count(df_desynced)

    # KPI Cards rendering
    col_active, col_orphan, col_epoch, col_desync = st.columns(4)
    
    pct_active = (active_ports_count / total_historical_ports * 100) if total_historical_ports > 0 else 0
    col_active.metric(t("kpi_active"), f"{active_ports_count:,}")
    col_active.markdown(f"<div class='kpi-card-subtext'>{t('kpi_active_sub', pct=pct_active, total=total_historical_ports)}</div>", unsafe_allow_html=True)
    
    col_orphan.metric(t("kpi_orphan"), f"{orphan_ports_count:,} ports")
    col_orphan.markdown(f"<div class='kpi-card-subtext'>{t('kpi_orphan_sub', events=orphan_events_count)}</div>", unsafe_allow_html=True)
    
    col_epoch.metric(t("kpi_epoch"), f"{epoch_ports_count:,} ports")
    col_epoch.markdown(f"<div class='kpi-card-subtext'>{t('kpi_epoch_sub', events=epoch_events_count)}</div>", unsafe_allow_html=True)

    col_desync.metric(t("kpi_desync"), f"{desynced_ports_count:,} ports")
    col_desync.markdown(f"<div class='kpi-card-subtext'>{t('kpi_desync_sub')}</div>", unsafe_allow_html=True)

    # 4. Control Sidebar Panel
    st.sidebar.header(t("sidebar_header"))
    
    layer_options = [
        t("layer_active"),
        t("layer_orphan"),
        t("layer_epoch"),
        t("layer_desync")
    ]
    
    selected_view_mode = st.sidebar.radio(
        t("sidebar_radio_label"),
        layer_options
    )

    if selected_view_mode == t("layer_active"):
        current_df = df_active_sane
        layer_color = "green"
        layer_name = t("lname_active")
        badge = t("badge_active")
    elif selected_view_mode == t("layer_orphan"):
        current_df = df_orphans
        layer_color = "red"
        layer_name = t("lname_orphan")
        badge = t("badge_orphan")
    elif selected_view_mode == t("layer_epoch"):
        current_df = df_epoch
        layer_color = "purple"
        layer_name = t("lname_epoch")
        badge = t("badge_epoch")
    else:
        current_df = df_desynced
        layer_color = "orange"
        layer_name = t("lname_desync")
        badge = t("badge_desync")

    st.subheader(f"{t('layer_view_prefix')} {selected_view_mode}")

    # 5. Summary Banner
    temporal_range = t("banner_no_time")
    found_date_col = next((col for col in ['event_timestamp', 'event_timestamp_dt', 'port_last_updated', 'last_updated'] if col in current_df.columns), None) if not current_df.empty else None
    
    if found_date_col and not current_df.empty:
        try:
            time_series = pd.to_datetime(current_df[found_date_col], errors='coerce').dropna()
            if selected_view_mode == t("layer_orphan"):
                time_series = time_series[time_series >= "1971-01-01"]
                
            if not time_series.empty:
                min_date_str = time_series.min().strftime('%Y-%m-%d')
                max_date_str = time_series.max().strftime('%Y-%m-%d')
                temporal_range = f"{min_date_str} to {max_date_str}"
        except Exception:
            pass

    if selected_view_mode == t("layer_active"):
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

    scope_detail = t("banner_scope_detail", locations=unique_locations, stations=unique_stations, ports=unique_ports)

    st.markdown(
        f"""
        <div class="metric-banner">
            <b>{t('banner_title', layer_name=layer_name)}</b><br>
            • <b>{t('banner_time')}</b> {temporal_range}<br>
            • <b>{t('banner_scope')}</b> {scope_detail}<br>
            • <b>{t('banner_power')}</b> {power_info}
        </div>
        """,
        unsafe_allow_html=True
    )

    # 6. Folium Map Rendering
    st.markdown(t("map_title"))
    map_object = folium.Map(location=[41.3851, 2.1734], zoom_start=13, tiles="OpenStreetMap")

    if selected_view_mode == t("layer_active"):
        for idx, loc_row in df_gold.iterrows():
            loc_address = loc_row.get('address_address_string', f"Location ID: {loc_row.get('location_id')}")
            car_pts = int(loc_row.get('car_ports_count', 0))
            moto_pts = int(loc_row.get('moto_ports_count', 0))
            onstreet = loc_row.get('onstreet_location', True)
            
            location_type_label = t("map_street") if onstreet else t("map_parking")
            specific_icon = "tree" if onstreet else "parking"
            
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; width: 210px;">
                <span style="font-size: 11px; color: #555; font-weight: bold; text-transform: uppercase;">{location_type_label}</span>
                <h4 style="margin: 4px 0 8px 0; color: #2C3E50; font-size: 13px;">{loc_address}</h4>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 5px 0;">
                <ul style="padding-left: 15px; margin: 5px 0; font-size: 12px; color: #333;">
                    <li><b>{t('map_car_ports')}</b> {car_pts} {t('map_ports')}</li>
                    <li><b>{t('map_moto_ports')}</b> {moto_pts} {t('map_ports')}</li>
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
                address = loc_row.get('address', t('map_no_addr'))
                
                specific_icon = "tree"
                location_type_label = t("map_audit")
                
                popup_html = f"""
                <div style="font-family: Arial, sans-serif; width: 230px;">
                    <span style="font-size: 11px; color: #555; font-weight: bold; text-transform: uppercase;">{location_type_label}</span>
                    <p style="font-size: 12px; color: #2C3E50; font-weight: bold; margin: 4px 0;">{address}</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 5px 0;">
                    <p style="font-size: 12px; color: #333; margin: 5px 0;"><b>{t('map_affected_ports')}</b> {total_ports}</p>
                    <div style="margin-top: 8px; padding: 4px; background-color: #f8f9fa; border-radius: 4px; text-align: center;">
                        <span style="font-size: 11px; font-weight: bold;">{badge}</span>
                    </div>
                </div>
                """
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=250),
                    icon=folium.Icon(color=layer_color, icon=specific_icon, prefix="fa"),
                    tooltip=f"{address} — {total_ports} {t('map_ports')}"
                ).add_to(map_object)

    st_folium(map_object, width=None, use_container_width=True, height=500)

    # 7. Visualizations
    if selected_view_mode != t("layer_orphan"):
        st.markdown(t("infra_details_title"))
        
        port_col = next((col for col in ['station_port_sk', 'port_id', 'port_sk'] if col in current_df.columns), current_df.columns[0] if not current_df.empty else None)
        
        if port_col and not current_df.empty:
            df_ports_unique = current_df.drop_duplicates(subset=[port_col]).copy()
            
            cols_to_merge = [c for c in ['use_case', 'onstreet_location'] if c in df_gold.columns and c not in df_ports_unique.columns]
            if cols_to_merge and 'location_id' in df_ports_unique.columns and 'location_id' in df_gold.columns:
                df_ports_unique = df_ports_unique.merge(
                    df_gold[['location_id'] + cols_to_merge].drop_duplicates(subset=['location_id']), 
                    on='location_id', 
                    how='left'
                )

            def parse_use_case_attributes(row):
                uc = str(row.get('use_case', ''))
                
                if 'Off-Street' in uc:
                    location_type = t("val_parking")
                elif 'On-Street' in uc:
                    location_type = t("val_street")
                else:
                    location_type = t("val_street") if bool(row.get('onstreet_location', True)) else t("val_parking")
                    
                if 'Moto' in uc:
                    vehicle_type = t("val_motorcycle")
                elif 'General' in uc:
                    vehicle_type = t("val_car")
                else:
                    conn = str(row.get('port_connector_type', '')).upper()
                    vehicle_type = t("val_motorcycle") if 'MOTO' in conn else t("val_car")
                    
                return pd.Series([vehicle_type, location_type], index=['Tipo_Vehiculo', 'Tipo_Ubicacion'])

            df_ports_unique[['Tipo_Vehiculo', 'Tipo_Ubicacion']] = df_ports_unique.apply(parse_use_case_attributes, axis=1)
        else:
            df_ports_unique = pd.DataFrame()

        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            if not df_ports_unique.empty:
                uc_summary = df_ports_unique.groupby(['Tipo_Vehiculo', 'Tipo_Ubicacion']).size().reset_index(name='Puertos_Unicos')

                color_map = {
                    t("val_parking"): '#1E40AF', 
                    t("val_street"): '#10B981',
                    'Parking': '#1E40AF',
                    'Calle': '#10B981',
                    'On-Street': '#10B981'
                }

                fig_uc = px.bar(
                    uc_summary, 
                    x='Tipo_Vehiculo', 
                    y='Puertos_Unicos', 
                    color='Tipo_Ubicacion',
                    barmode='group', 
                    title=t("chart_uc_title"),
                    color_discrete_map=color_map,
                    labels={
                        'Puertos_Unicos': t("chart_uc_y"), 
                        'Tipo_Vehiculo': '',
                        'Tipo_Ubicacion': t("chart_legend_loc_type")
                    },
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
                    title=t("chart_uc_y"),
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
                st.info(t("info_no_uc"))

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
                    title=t("chart_pie_title"), 
                    hole=0.4,
                    color='Tipo_Conector', 
                    color_discrete_map=CONNECTOR_COLOR_MAP
                )
                fig_pie.update_traces(hovertemplate=t("chart_pie_hover"))
                fig_pie.update_layout(
                    margin=dict(l=10, r=10, t=50, b=20),
                    height=350,
                    font=dict(color='black'),
                    legend_title_font=dict(color='black'),
                    legend_font=dict(color='black')
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info(t("info_no_conn"))

    # Power breakdown by connector type (Healthy Active Network exclusive)
    if selected_view_mode == t("layer_active"):
        st.markdown("---")
        st.subheader(t("power_dist_title"))

        port_col = 'station_port_sk' if 'station_port_sk' in df_active_sane.columns else df_active_sane.columns[0]
        power_col = next((c for c in ['port_power_kw', 'power_kw', 'max_power_kw'] if c in df_active_sane.columns), None)
        connector_col = next((c for c in ['port_connector_type', 'connector_type'] if c in df_active_sane.columns), None)

        if power_col and connector_col and not df_active_sane.empty:
            df_active_ports = df_active_sane.drop_duplicates(subset=[port_col], keep='last').copy()

            def standardize_power(kw):
                try:
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
                    return t("val_unknown")

            df_active_ports['power_clean'] = df_active_ports[power_col].apply(standardize_power)

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
                    connector_col: t("chart_power_conn"), 
                    'count': '', 
                    'power_clean': t("chart_power_label")
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
                    title=dict(text=t("chart_power_legend"), font=dict(size=12, color="black")),
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
                title=dict(text=t("chart_power_conn"), font=dict(size=14, color="black")), 
                tickfont=dict(size=12, color="black"), 
                linecolor="black", showline=True
            )

            st.plotly_chart(fig_power_conn_clean, use_container_width=True)

    # 8. Top Affected Locations
    if selected_view_mode != t("layer_active"):
        st.markdown("---")
        st.markdown(t("top_loc_title"))
        if not current_df.empty and 'location_id' in current_df.columns:
            top_locs = current_df['location_id'].value_counts().head(10).reset_index()
            top_locs.columns = ['ID_Ubicacion', 'Total_Registros']
            top_locs['ID_Ubicacion'] = t("top_loc_prefix") + top_locs['ID_Ubicacion'].astype(str)
            top_locs = top_locs.iloc[::-1]

            fig_top_loc = px.bar(
                top_locs, x='Total_Registros', y='ID_Ubicacion', orientation='h',
                title=t("top_loc_chart_title", layer_name=layer_name),
                color_discrete_sequence=['#e74c3c' if layer_color == 'red' else ('#f39c12' if layer_color == 'orange' else '#9b59b6')],
                labels={'ID_Ubicacion': ''},
                text_auto=True
            )
            fig_top_loc.update_traces(textposition='outside')
            fig_top_loc.update_xaxes(
                title=t("top_loc_x_title"),
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

    # 9. Orphan Events Audit
    if selected_view_mode == t("layer_orphan") and not current_df.empty:
        st.markdown("---")
        st.markdown(t("audit_title"))
        
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
                .rename(columns={case_col: t('col_audit_case')})
                .sort_values(by='event_count', ascending=False)
            )
            
            total_events = len(df_audit)
            audit_summary[t('col_pct')] = (audit_summary['event_count'] / total_events) * 100
            audit_summary[t('col_map_status')] = audit_summary[t('col_audit_case')].apply(
                lambda x: t('status_map_no') if str(x).startswith('Case C') else t('status_map_yes')
            )
            
            audit_summary = audit_summary[[
                t('col_audit_case'),
                'event_count',
                t('col_pct'),
                t('col_map_status'),
                'unique_ports'
            ]].rename(columns={
                'event_count': t('col_total_events'),
                'unique_ports': t('col_affected_ports')
            })

            st.markdown(t("audit_table_title"))
            st.dataframe(
                audit_summary.style.format({
                    t('col_total_events'): '{:,}',
                    t('col_pct'): '{:.2f}%',
                    t('col_affected_ports'): '{:,}'
                }),
                use_container_width=True,
                hide_index=True
            )

            st.markdown(t("audit_breakdown_header"), unsafe_allow_html=True)
            unique_cases = sorted(df_audit[case_col].unique())
            
            tab_titles = []
            for c in unique_cases:
                if "Case A" in c:
                    tab_titles.append(t("tab_case_a"))
                elif "Case B" in c:
                    tab_titles.append(t("tab_case_b"))
                elif "Case C" in c:
                    tab_titles.append(t("tab_case_c"))
                else:
                    tab_titles.append(f"📌 {c}")
                    
            tabs = st.tabs(tab_titles)
            
            case_descriptions = {
                "Case A": t("desc_case_a"),
                "Case B": t("desc_case_b"),
                "Case C": t("desc_case_c")
            }

            for tab, case_name in zip(tabs, unique_cases):
                with tab:
                    df_case = df_audit[df_audit[case_col] == case_name].copy()
                    
                    desc_key = next((k for k in case_descriptions if k in case_name), None)
                    if desc_key:
                        st.info(case_descriptions[desc_key])
                    
                    m_col1, m_col2, m_col3 = st.columns(3)
                    m_col1.metric(t("metric_affected_events"), f"{len(df_case):,}")
                    m_col2.metric(t("metric_stations_involved"), f"{df_case['station_id'].nunique() if 'station_id' in df_case.columns else 'N/A'}")
                    m_col3.metric(t("metric_locations_involved"), f"{df_case['location_id'].nunique() if 'location_id' in df_case.columns else 'N/A'}")
                    
                    case_grouped = df_case.groupby(['location_id', 'station_id']).agg(
                        quarantine_emitted_ports=('port_id', lambda x: sorted(list(set(str(p) for p in x.dropna())))),
                        quarantine_events=('location_id', 'count')
                    ).reset_index()
                    
                    case_grouped['quarantine_emitted_ports'] = case_grouped['quarantine_emitted_ports'].astype(str)
                    
                    case_grouped = case_grouped.rename(columns={
                        'location_id': t('tbl_loc_id'),
                        'station_id': t('tbl_station_id'),
                        'quarantine_emitted_ports': t('tbl_emitted_ports'),
                        'quarantine_events': t('tbl_total_events')
                    }).sort_values(by=t('tbl_total_events'), ascending=False)

                    st.dataframe(
                        case_grouped,
                        use_container_width=True,
                        hide_index=True
                    )

    # 10. Audit for Desynchronized Governance
    if selected_view_mode == t("layer_desync") and not current_df.empty:
        st.markdown("---")
        st.markdown(t("desync_audit_title"))
        
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
