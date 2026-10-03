import os
import calendar
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from translations import t

# Custom CSS styles
st.markdown(
    """
    <style>
    /* Base text styles (paragraphs, bullet points, lists) */
    p, li, span, div.stMarkdown {
        font-family: 'Segoe UI', Roboto, Arial, sans-serif !important;
        font-size: 18px !important;
        line-height: 1.6 !important;
    }

    /* Style for explanatory subtitles or smaller captions */
    .stCaption {
        font-size: 15px !important;
    }

    /* Style for Streamlit native DataFrames content */
    [data-testid="stDataFrame"] {
        font-size: 16px !important;
    }

    /* GLOBAL TITLE STYLES */
    .title-size-main {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    
    .title-size-sub {
        font-size: 17px !important;
        font-weight: 700 !important;
        color: #1E293B !important;
        margin-top: 12px !important;
        margin-bottom: 12px !important;
    }

    .chart-title-single {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #0F172A !important;
        text-align: center !important;
        margin-top: 20px !important;
        margin-bottom: 24px !important;
    }
    
    button[data-baseweb="tab"] p {
        font-size: 15px !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# File loading
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

st.title(t("net_title"))

# Main tabs
tab_medallion, tab_estruc, tab_eda = st.tabs([
    t("tab_medallion"), 
    t("tab_estruc"), 
    t("tab_eda"), 
])

# SECTION 1: DATA CONTEXT & MEDALLION ARCHITECTURE
with tab_medallion:
    st.markdown(t("med_intro"))
    st.markdown("---")

    # BRONZE: Ingestion & Integration
    st.subheader(t("bronze_title"))
    
    col_b1, col_b2 = st.columns([4, 6])
    
    with col_b1:
        df_bronze_orig = pd.DataFrame({
            t("axis_year"): [2023, 2024, 2025, 2026],
            "Locations [Dim]": [4, 4, 4, 2],
            "Estats Ports [Facts]": [2, 4, 4, 2]
        })
        st.dataframe(df_bronze_orig, use_container_width=True, hide_index=True)
    
    with col_b2:
        st.markdown(t("bronze_hierarchy"))

        ruta_imagen = "foto_connectors.jpg"
        if os.path.exists(ruta_imagen):
            subcol_izq, subcol_centro, subcol_der = st.columns([1, 4, 1])
            with subcol_centro:
                st.image(ruta_imagen, use_container_width=True)
        else:
            st.warning(t("err_img_not_found", img="foto_connectors.jpg"))

        st.markdown(t("bronze_coords"))

    # Image columns
    st.markdown("<br>", unsafe_allow_html=True)
    col_img_left, col_img_right = st.columns(2)

    with col_img_left:
        ruta_parking = "parking.jpg"
        if os.path.exists(ruta_parking):
            st.image(ruta_parking, use_container_width=True, caption=t("cap_parking_multi"))
        else:
            st.warning(t("err_img_not_found", img="parking.jpg"))

    with col_img_right:
        ruta_parking_1 = "parking_1.png"
        if os.path.exists(ruta_parking_1):
            st.image(ruta_parking_1, use_container_width=True, caption=t("cap_parking_use"))
        else:
            st.warning(t("err_img_not_found", img="parking_1.png"))

    st.markdown("---")

    # SILVER: Data Processing, Cleaning & Governance
    st.subheader(t("silver_title"))

    # Dimension Table 
    col_t1, col_t2 = st.columns([6, 4])
    with col_t1:
        st.markdown(t("tbl_dim_title"))

    col_s1, col_s2 = st.columns([6, 4])
    
    with col_s1:
        if not df_dim.empty:
            columnas_deseadas_dim = [c for c in ["station_port_sk", "onstreet_location", "port_connector_type", "port_power_kw", "port_notes"] if c in df_dim.columns]
            df_muestra_dim = df_dim[columnas_deseadas_dim].sample(min(5, len(df_dim)))
            st.dataframe(df_muestra_dim, use_container_width=True, hide_index=True)
        else:
            st.warning(t("err_dim_empty"))
    
    with col_s2:
        st.markdown(t("silver_dim_bullets"), unsafe_allow_html=True)

    # Port Characterization
    st.markdown(t("vars_key_title"))
    
    col_anat_1, col_anat_2 = st.columns([5, 5])

    with col_anat_1:
        ruta_puerto = "puerto_1.jpg"
        if os.path.exists(ruta_puerto):
            st.image(ruta_puerto, use_container_width=True, caption=t("cap_port_img"))
        else:
            st.warning(t("err_img_not_found", img="puerto_1.jpg"))

    with col_anat_2:
        st.markdown(t("vars_key_bullets"))

    st.markdown("<hr style='border: none; border-top: 2px dashed #cccccc; margin: 25px 0;'>", unsafe_allow_html=True)

    # Fact Table
    col_t3, col_t4 = st.columns([6, 4])
    with col_t3:
        st.markdown(t("tbl_fact_title"))

    col_h1, col_h2 = st.columns([6, 4])
    
    with col_h1: 
        if not df_fact_status.empty:
            columnas_deseadas_fact = [c for c in ['station_port_sk', 'event_timestamp', 'port_status_value', 'target_is_available'] if c in df_fact_status.columns]
            df_muestra_fact = df_fact_status[columnas_deseadas_fact].sample(min(5, len(df_fact_status)))
            st.dataframe(df_muestra_fact, use_container_width=True, hide_index=True)
        else:
            st.warning(t("err_fact_empty"))
    
    with col_h2:
        st.markdown(t("silver_fact_bullets"), unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 2px dashed #cccccc; margin: 25px 0;'>", unsafe_allow_html=True)

    # Master Table
    col_t5, col_t6 = st.columns([6, 4])
    with col_t5:
        st.markdown(t("tbl_master_title"))

    col_s_m1, col_s_m2 = st.columns([6, 4]) 
    
    with col_s_m1: 
        if not df_master.empty:
            columnas_deseadas_master = [c for c in ['station_port_sk', 'event_timestamp', 'target_is_available', 'port_connector_type','use_case' ] if c in df_master.columns]
            df_muestra_master = df_master[columnas_deseadas_master].sample(min(5, len(df_master)))
            st.dataframe(df_muestra_master, use_container_width=True, hide_index=True)
        else:
            st.warning(t("err_master_empty"))
    
    with col_s_m2:
        st.markdown(t("silver_master_bullets"), unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 2px dashed #cccccc; margin: 25px 0;'>", unsafe_allow_html=True)

    # Main tables summary
    st.markdown(t("summary_datasets_title"))

    datasets_config = [
        (t("ds_dim_hist"), df_history),
        (t("ds_dim_rec"), df_dim),
        (t("ds_fact"), df_fact_status),
        (t("ds_master"), df_master)
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
            t("col_ds_table"): tipo,
            t("col_ds_regs"): regs,
            t("col_ds_cols"): cols,
            t("col_ds_locs"): locs,
            t("col_ds_stations"): stations,
            t("col_ds_ports"): ports
        })

    data_summary = pd.DataFrame(summary_data)

    st.dataframe(
        data_summary.style.format({
            t("col_ds_regs"): lambda x: f"{x:,}" if isinstance(x, int) else x,
            t("col_ds_cols"): lambda x: f"{x:,}" if isinstance(x, int) else x,
            t("col_ds_locs"): lambda x: f"{x:,}" if isinstance(x, int) else x,
            t("col_ds_stations"): lambda x: f"{x:,}" if isinstance(x, int) else x,
            t("col_ds_ports"): lambda x: f"{x:,}" if isinstance(x, int) else x,
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # GOLD: Business Intelligence & Network Audit
    st.subheader(t("gold_title"))
    st.markdown(t("gold_bullets"))

# SECTION 2: DATA STRUCTURE & EVOLUTION
with tab_estruc:
    st.markdown(t("sec2_intro"))

    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        t("subtab_evo"), 
        t("subtab_cat"), 
        t("subtab_fact")
    ])
    
    # SUBTAB 1: Dimensions historical evolution
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

        # 1. Combined Chart: Ports and Power
        fig_evo = go.Figure()
        fig_evo.add_trace(go.Bar(
            x=summary_table_gold['year_str'], 
            y=summary_table_gold['cum_total_ports'], 
            name=t("legend_ports"),
            marker_color="#3B82F6",  
            text=summary_table_gold['cum_total_ports'],
            textposition='outside',
            textfont=dict(color="black", size=12, family="Arial")
        ))
        fig_evo.add_trace(go.Scatter(
            x=summary_table_gold['year_str'], 
            y=summary_table_gold['total_installed_kw'], 
            name=t("legend_power"), 
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
                title=dict(text=t("axis_year"), font=dict(size=14, color="black", family="Arial")),
                tickfont=dict(size=12, color="black"),
                linecolor="black", showline=True, linewidth=1
            ),
            yaxis=dict(
                title=dict(text=t("axis_num_ports"), font=dict(size=14, color="black", family="Arial")),
                tickfont=dict(size=12, color="black"),
                range=[0, 2100],
                showgrid=True, gridcolor="rgba(0,0,0,0.08)",
                linecolor="black", showline=True, linewidth=1
            ),
            yaxis2=dict(
                title=dict(text=t("axis_installed_power"), font=dict(size=14, color="black", family="Arial")),
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
            st.markdown(f'<div class="chart-title-single">{t("chart_title_evo")}</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_evo, use_container_width=True)

        st.markdown("---")
        
        # 2. Connector Type Chart
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
            labels={'snapshot_year': t("axis_year"), 'Port_Count': t("axis_num_ports"), 'Connector_Type': t("axis_conn_type")}
        )
        fig_conn.update_layout(
            font=dict(color="black", family="Arial"),
            title="",
            xaxis=dict(
                type='category', title=dict(text=t("axis_year"), font=dict(size=14, color="black")),
                tickfont=dict(size=12, color="black"), linecolor="black", showline=True, linewidth=1
            ),
            yaxis=dict(
                title=dict(text=t("axis_num_ports"), font=dict(size=14, color="black")),
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
            st.markdown(f'<div class="chart-title-single">{t("chart_title_conn")}</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_conn, use_container_width=True)

        st.markdown("---")
        
        # 3. Use Case Chart
        df_usecase = pd.crosstab(
            df_cumulative_snapshots['snapshot_year'],
            df_cumulative_snapshots['use_case']
        ).reset_index()
        df_usecase['snapshot_year'] = df_usecase['snapshot_year'].astype(str)
        
        df_uc_melted = df_usecase.melt(id_vars='snapshot_year', var_name='Use_Case', value_name='Port_Count')
        
        use_case_map = {
            'Off-Street General': t("uc_parking_car"),
            'Off-Street Moto': t("uc_parking_moto"),
            'On-Street General': t("uc_street_car"),
            'On-Street Moto': t("uc_street_moto")
        }
        df_uc_melted['Use_Case'] = df_uc_melted['Use_Case'].replace(use_case_map)

        color_uc_palette = {
            t("uc_parking_car"): '#1E40AF',
            t("uc_parking_moto"): '#1E40AF',
            t("uc_street_car"): '#10B981',
            t("uc_street_moto"): '#10B981'
        }
        
        dash_uc_palette = {
            t("uc_parking_car"): 'solid',
            t("uc_parking_moto"): 'dash',
            t("uc_street_car"): 'solid',
            t("uc_street_moto"): 'dash'
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
            labels={'snapshot_year': t("axis_year"), 'Port_Count': t("axis_num_ports"), 'Use_Case': t("axis_use_case")}
        )
        
        fig_uc.update_traces(marker=dict(size=7))

        fig_uc.update_layout(
            font=dict(color="black", family="Arial"),
            title="",
            xaxis=dict(
                type='category', title=dict(text=t("axis_year"), font=dict(size=14, color="black")),
                tickfont=dict(size=12, color="black"), linecolor="black", showline=True, linewidth=1
            ),
            yaxis=dict(
                title=dict(text=t("axis_num_ports"), font=dict(size=14, color="black")),
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
            st.markdown(f'<div class="chart-title-single">{t("chart_title_uc")}</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_uc, use_container_width=True)

    # SUBTAB 2: Recent dimension - Catalog
    with sub_tab2:
        df_colab = df_dim.copy() if not df_dim.empty else df_master.copy()

        if not df_colab.empty:
            if 'location_id' in df_colab.columns and 'port_id' in df_colab.columns:
                df_location_density = df_colab.groupby('location_id').agg(
                    total_ports=('port_id', 'count')
                ).reset_index()

                fig_location_split = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=(t("sub_global_view"), t("sub_zoom_box")),
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
                    title_text=t("axis_num_ports"), title_font=dict(size=14, color="black"),
                    tickfont=dict(size=12, color="black"), linecolor="black", showline=True, linewidth=1, row=1, col=1
                )
                fig_location_split.update_yaxes(
                    title_text=t("axis_num_ports_zoom"), title_font=dict(size=14, color="black"),
                    tickfont=dict(size=12, color="black"), range=[-0.5, 20.5],
                    linecolor="black", showline=True, linewidth=1, row=1, col=2
                )
                
                fig_location_split.update_xaxes(
                    title_text=t("axis_location"), title_font=dict(size=14, color="black"),
                    showticklabels=False, linecolor="black", showline=True, linewidth=1, row=1, col=1
                )
                fig_location_split.update_xaxes(
                    title_text=f"{t('axis_location')} (zoom)", title_font=dict(size=14, color="black"),
                    showticklabels=False, linecolor="black", showline=True, linewidth=1, row=1, col=2
                )

                fig_location_split.update_layout(
                    font=dict(color="black", family="Arial"),
                    title="",
                    template='plotly_white', 
                    height=430,
                    margin=dict(t=35, l=40, r=20, b=25)
                )

                st.markdown(f'<div class="chart-title-single">{t("chart_title_split")}</div>', unsafe_allow_html=True)
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
                        True: t("val_street"), False: t("val_parking")
                    }).fillna(t("val_unknown"))
                    color_arg = 'ubicacion_tipo'
                else:
                    color_arg = None
                    
                fig_loc_map = px.scatter_mapbox(
                    df_location_density, lat='lat', lon='lon', size='total_ports', color=color_arg, size_max=24,
                    color_discrete_map={t("val_parking"): "#1F56EC", t("val_street"): "#F80909"},
                    hover_name='address', hover_data={'lat': False, 'lon': False, 'total_ports': True, 'ubicacion_tipo': False},
                    zoom=12.65,
                    center={'lat': 41.4020, 'lon': 2.1620},
                    opacity=0.85
                )

                fig_loc_map.update_layout(
                    font=dict(color="black", family="Arial"),
                    title="",
                    legend_title_text=t("chart_legend_loc_type"),
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

                st.markdown(f'<div class="chart-title-single">{t("chart_title_map")}</div>', unsafe_allow_html=True)
                st.plotly_chart(fig_loc_map, use_container_width=True, config=config_hd)

    # SUBTAB 3: Telemetry and fact table
    with sub_tab3:
        st.markdown(t("sec2_fact_intro"))

        if 'df_master' in locals() or 'df_master' in globals():
            df_fact = df_master.copy()
            if 'event_timestamp' in df_fact.columns:
                df_fact['event_timestamp'] = pd.to_datetime(df_fact['event_timestamp'])
                df_fact['year'] = df_fact['event_timestamp'].dt.year
                df_fact['month'] = df_fact['event_timestamp'].dt.month
                df_fact['hour'] = df_fact['event_timestamp'].dt.hour
                df_fact['day_of_week_name'] = df_fact['event_timestamp'].dt.day_name()
                
            col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
            col_b1.metric(t("metric_total_events"), f"{len(df_fact):,}")
            col_b2.metric(t("metric_active_ports"), f"{df_fact['station_port_sk'].nunique():,}" if 'station_port_sk' in df_fact.columns else "N/A")
            col_b3.metric(t("metric_stations"), f"{df_fact['station_id'].nunique():,}" if 'station_id' in df_fact.columns else "N/A")
            col_b4.metric(t("metric_locations"), f"{df_fact['location_id'].nunique():,}" if 'location_id' in df_fact.columns else "N/A")
            avail_global_pct = (df_fact['target_is_available'].sum() / len(df_fact)) * 100 if 'target_is_available' in df_fact.columns and len(df_fact) > 0 else 0
            col_b5.metric(t("metric_global_avail"), f"{avail_global_pct:.1f}%")

            st.markdown("---")

            # 1. Temporal frequency analysis
            temporal_level = st.selectbox(
                t("select_temp_level"),
                [t("temp_opt_monthly"), t("temp_opt_weekly"), t("temp_opt_hourly")],
                key="telemetry_temporal_level"
            )

            if t("temp_opt_monthly") in temporal_level or "Mensual" in temporal_level or "Monthly" in temporal_level:
                month_dist_df = df_fact['month'].value_counts().sort_index().reset_index()
                month_dist_df.columns = ['month_num', 'Event_Count']
                month_dist_df['Month_Name'] = month_dist_df['month_num'].apply(lambda m: calendar.month_name[m])
                month_dist_df['Percentage'] = (month_dist_df['Event_Count'] / len(df_fact)) * 100

                current_title = t("chart_temp_monthly")
                fig_temp = px.bar(
                    month_dist_df, x='Month_Name', y='Percentage',
                    text=month_dist_df['Percentage'].apply(lambda x: f"{x:.1f}%"),
                    labels={'Month_Name': t("axis_month"), 'Percentage': t("axis_telemetry_events_pct")}
                )

            elif t("temp_opt_weekly") in temporal_level or "Semanal" in temporal_level or "Weekly" in temporal_level:
                dow_dist_df = df_fact['day_of_week_name'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index()
                dow_dist_df.columns = ['Day', 'Event_Count']
                dow_dist_df['Day_Translated'] = [
                    t("day_monday"), t("day_tuesday"), t("day_wednesday"), 
                    t("day_thursday"), t("day_friday"), t("day_saturday"), t("day_sunday")
                ]
                dow_dist_df['Percentage'] = (dow_dist_df['Event_Count'] / len(df_fact)) * 100

                current_title = t("chart_temp_weekly")
                fig_temp = px.bar(
                    dow_dist_df, x='Day_Translated', y='Percentage',
                    text=dow_dist_df['Percentage'].apply(lambda x: f"{x:.1f}%"),
                    labels={'Day_Translated': t("axis_day_of_week"), 'Percentage': t("axis_telemetry_events_pct")}
                )
            else:
                hour_dist_df = df_fact['hour'].value_counts().sort_index().reset_index()
                hour_dist_df.columns = ['Hour', 'Event_Count']
                hour_dist_df['Hour_Str'] = hour_dist_df['Hour'].apply(lambda h: f"{h:02d}:00")
                hour_dist_df['Percentage'] = (hour_dist_df['Event_Count'] / len(df_fact)) * 100

                current_title = t("chart_temp_hourly")
                fig_temp = px.bar(
                    hour_dist_df, x='Hour_Str', y='Percentage',
                    text=hour_dist_df['Percentage'].apply(lambda x: f"{x:.1f}%"),
                    labels={'Hour_Str': t("axis_hour_of_day"), 'Percentage': t("axis_telemetry_events_pct")}
                )

            fig_temp.update_traces(
                textposition='outside', 
                marker_color='#2b5c8f',
                textfont=dict(color="black", size=12, family="Arial")
            )
            
            if t("temp_opt_hourly") in temporal_level or "Horario" in temporal_level or "Hourly" in temporal_level:
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
                title_text=t("axis_telemetry_events_pct"),
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

            # 2. Annual coverage of events and ports
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
                    name=t("legend_events_year"), marker_color='#2b5c8f',
                    text=annual_telemetry['total_events'].apply(lambda x: f"{x:,}"),
                    textposition='outside', textfont=dict(color="black", size=12, family="Arial")
                ))
                
                fig_annual_cov.add_trace(go.Scatter(
                    x=annual_telemetry['year'].astype(str), y=annual_telemetry['unique_active_ports'],
                    name=t("metric_active_ports"), yaxis='y2', mode='lines+markers+text',
                    line=dict(color='#10B981', width=2.5), marker=dict(size=7),
                    text=annual_telemetry['unique_active_ports'].apply(lambda x: f"{x:,}"),
                    textposition='top center', textfont=dict(color="black", size=12, family="Arial")
                ))
                
                fig_annual_cov.update_layout(
                    font=dict(color="black", family="Arial"),
                    title="",
                    xaxis=dict(
                        title=dict(text=t("axis_year"), font=dict(size=14, color="black")),
                        tickfont=dict(size=12, color="black"), 
                        type='category', 
                        linecolor="black", showline=True, linewidth=1 
                    ),
                    yaxis=dict(
                        title=dict(text=t("axis_num_events"), font=dict(size=14, color="black")),
                        showticklabels=False,  
                        ticks='',              
                        range=[0, 8500], 
                        showgrid=True, gridcolor='rgba(0,0,0,0.08)',
                        linecolor="black", showline=True, linewidth=1 
                    ),
                    yaxis2=dict(
                        title=dict(text=t("metric_active_ports"), font=dict(size=14, color="black")),
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
                    st.markdown(f'<div class="chart-title-single">{t("chart_annual_coverage")}</div>', unsafe_allow_html=True)
                    st.plotly_chart(fig_annual_cov, use_container_width=True)

            st.markdown("---")

            # 3. Heatmap: Availability
            if 'target_is_available' in df_fact.columns and 'hour' in df_fact.columns and 'day_of_week_name' in df_fact.columns:
                df_fact['hour_str'] = df_fact['hour'].apply(lambda h: f"{h:02d}:00")
                heatmap_data = pd.crosstab(
                    df_fact['day_of_week_name'], df_fact['hour_str'], 
                    values=df_fact['target_is_available'], 
                    aggfunc=lambda x: (x.sum() / len(x)) * 100
                ).reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).fillna(0)

                days_labels = [
                    t("day_monday"), t("day_tuesday"), t("day_wednesday"), 
                    t("day_thursday"), t("day_friday"), t("day_saturday"), t("day_sunday")
                ]

                fig_heatmap = px.imshow(
                    heatmap_data, labels=dict(x=t("axis_hour_of_day"), y=t("axis_day_of_week"), color=t("heatmap_z_title")),
                    x=heatmap_data.columns, y=days_labels,
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
            st.warning(t("err_master_not_found"))

# SECTION 3: CONSOLIDATED ACTIVE NETWORK
with tab_eda:
    st.markdown(t("sec3_intro"))

    # 1. Automatic data preparation from df_master
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

    # 2. Power breakdown by connector type
    st.subheader(t("sec3_power_dist_title"))
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
            return t("val_unknown")

    df_active_ports['power_clean'] = df_active_ports[power_col].apply(standardize_power)

    # Total count by connector type
    conn_totals = df_active_ports.groupby(connector_col).size().reset_index(name='total')
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
            connector_col: t("chart_power_conn"), 
            'count': t("chart_active_ports_count"), 
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
        title=dict(text=t("chart_active_ports_count"), font=dict(size=14, color="black")), 
        showticklabels=False,
        range=[0, max_conn_ports * 1.15],
        linecolor="black", showline=True
    )
    fig_power_conn_clean.update_yaxes(
        title=dict(text=t("chart_power_conn"), font=dict(size=14, color="black")), 
        tickfont=dict(size=12, color="black"), 
        linecolor="black", showline=True
    )

    st.plotly_chart(fig_power_conn_clean, use_container_width=True)
