import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import datetime

# GPS geolocation component
try:
    from streamlit_geolocation import streamlit_geolocation
    HAS_GEOLOCATION_PKG = True
except ImportError:
    HAS_GEOLOCATION_PKG = False

# 1. Page Configuration & Custom CSS
st.set_page_config(
    page_title="Endolla Barcelona - Buscador EV",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI enhancements and expander header font scaling
st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none; }
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
            padding-top: 0.2rem !important;
            padding-bottom: 0.2rem !important;
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
        }
        iframe[title="streamlit_geolocation.streamlit_geolocation"] {
            display: block;
            margin: 0 auto;
            border: none;
        }
        /* Smaller location info alert */
        .custom-compact-alert {
            padding: 8px 12px;
            background-color: #d4edda;
            color: #155724;
            border-radius: 6px;
            font-size: 13px;
            margin-bottom: 15px;
            border: 1px solid #c3e6cb;
        }
        
        /* Prominent Expander Title Customization */
        [data-testid="stExpander"] details summary p {
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            color: #1E293B !important;
        }
        [data-testid="stExpander"] details summary {
            background-color: #F8FAFC !important;
            border-radius: 8px !important;
            padding: 10px 14px !important;
            border: 1px solid #E2E8F0 !important;
        }
        
        /* Larger font inside simulator */
        .simulator-container {
            font-size: 16px !important;
            padding: 10px 5px;
        }
        .stTable {
            font-size: 15px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Endolla Barcelona — Buscador de Carga EV")
st.markdown("Consulta en tiempo real la disponibilidad proyectada de puntos de recarga en la red de Barcelona.")

# 2. Artifact Loading with Cache
@st.cache_resource
def load_production_models():
    model_car = xgb.XGBClassifier()
    model_car.load_model("xgb_model_g.json")
    
    model_moto = xgb.XGBClassifier()
    model_moto.load_model("xgb_model_m.json")
    return model_car, model_moto

@st.cache_data
def load_station_metadata():
    return pd.read_parquet("stations_metadata.parquet")

model_car, model_moto = load_production_models()
df_stations = load_station_metadata()

# 3. Geolocation & Vehicle Filtering Logic
geolocator = Nominatim(user_agent="barcelona_ev_stochastic_app_v8")

def get_coords_from_address(address_string):
    try:
        location = geolocator.geocode(f"{address_string}, Barcelona, Spain")
        if location:
            return location.latitude, location.longitude, address_string
        return None
    except:
        return None

def find_stations_within_radius(user_lat, user_lon, stations_df, max_distance_m=1000, is_moto=False):
    df_temp = stations_df.copy()
    
    if is_moto:
        df_temp = df_temp[df_temp.get('total_moto_ports', df_temp.get('motorcycle_ports', 0)) > 0]
    else:
        df_temp = df_temp[df_temp.get('total_car_ports', df_temp.get('standard_ports', 0)) > 0]
        
    user_coords = (user_lat, user_lon)
    df_temp['distance_meters'] = df_temp.apply(
        lambda row: geodesic(user_coords, (row['station_coordinates_latitude'], row['station_coordinates_longitude'])).meters,
        axis=1
    )
    filtered_df = df_temp[df_temp['distance_meters'] <= max_distance_m]
    return filtered_df.sort_values('distance_meters').reset_index(drop=True)

def build_features(model, lat, lon, target_dt, is_onstreet=True):
    feature_names = model.get_booster().feature_names
    
    hour = target_dt.hour + (target_dt.minute / 60.0)
    month = target_dt.month
    day_of_week = target_dt.dayofweek
    
    base_data = {
        'station_coordinates_latitude': lat,
        'station_coordinates_longitude': lon,
        'port_power_kw': 7.20,
        'hour_sin': np.sin(2 * np.pi * hour / 24.0),
        'hour_cos': np.cos(2 * np.pi * hour / 24.0),
        'month_sin': np.sin(2 * np.pi * month / 12.0),
        'month_cos': np.cos(2 * np.pi * month / 12.0),
        'day_of_week_sin': np.sin(2 * np.pi * day_of_week / 7.0),
        'day_of_week_cos': np.cos(2 * np.pi * day_of_week / 7.0),
        'is_weekend': 1 if day_of_week in [5, 6] else 0,
        'onstreet_location_True': 1 if is_onstreet else 0,
        'port_reservable_True': 0
    }
    
    feature_row = {feat: base_data.get(feat, 0.0) for feat in feature_names}
    return pd.DataFrame([feature_row])[feature_names]

def predict_stochastic_status(model, feature_df, total_ports=1):
    p_single = float(model.predict_proba(feature_df)[:, 1][0])
    
    np.random.seed(42)
    total_ports = max(1, int(total_ports))
    sim_trials = np.random.binomial(n=1, p=p_single, size=(10000, total_ports))
    any_available = np.any(sim_trials == 1, axis=1)
    simulation_rate = float(np.mean(any_available))
    
    if simulation_rate >= 0.75:
        badge = '🟢 Alta Disponibilidad'
        color_hex = 'green'
    elif simulation_rate >= 0.50:
        badge = '🟡 Disponibilidad Media'
        color_hex = 'orange'
    else:
        badge = '🔴 Riesgo de Ocupación'
        color_hex = 'red'
        
    return simulation_rate, badge, color_hex

# 4. User Interface (Compact Sidebar)
st.sidebar.subheader("🔍 Filtros de Búsqueda")

sb_col1, sb_col2 = st.sidebar.columns(2)

with sb_col1:
    vehicle_choice = st.radio(
        "Vehículo:", 
        ["Coches", "Motos"], 
        key="sb_stream_choice"
    )

with sb_col2:
    location_method = st.radio(
        "Ubicación:",
        ["Dirección", "GPS"],
        key="sb_location_method"
    )

is_moto = "Motos" in vehicle_choice
selected_model = model_moto if is_moto else model_car

if location_method == "Dirección":
    address_input = st.sidebar.text_input(
        "Dirección:", 
        value="Avinguda del Paral·lel, 55", 
        key="sb_address_input",
        label_visibility="collapsed"
    )
else:
    if HAS_GEOLOCATION_PKG:
        gps_info = streamlit_geolocation()
        if gps_info and gps_info.get("latitude") and gps_info.get("longitude"):
            st.session_state.lat = gps_info["latitude"]
            st.session_state.lon = gps_info["longitude"]
            st.session_state.loc_name = "Ubicación GPS actual"
            st.sidebar.success("📍 GPS OK")
    else:
        st.sidebar.warning("⚠️ Instala `streamlit-geolocation`.")

col_date, col_time = st.sidebar.columns(2)
with col_date:
    target_date = st.date_input("Fecha:", pd.Timestamp.now(), key="sb_target_date")
with col_time:
    target_time = st.time_input(
        "Hora:", 
        value=datetime.time(12, 0), 
        step=datetime.timedelta(minutes=30),
        key="sb_target_time"
    )

max_distance_input = st.sidebar.slider(
    "Radio (metros):", 
    min_value=200, 
    max_value=3000, 
    value=800, 
    step=100, 
    key="sb_max_distance"
)

target_datetime = pd.Timestamp.combine(target_date, target_time)

if "search_executed" not in st.session_state:
    st.session_state.search_executed = False

if st.sidebar.button("🔎 Buscar Estaciones", use_container_width=True, type="primary"):
    st.session_state.search_executed = True
    if location_method == "Dirección":
        search_result = get_coords_from_address(address_input)
        if search_result:
            st.session_state.lat, st.session_state.lon, st.session_state.loc_name = search_result
        else:
            st.session_state.pop("lat", None)
            st.session_state.pop("lon", None)

# 5. Results Rendering & Simulator
if st.session_state.search_executed:
    if "lat" in st.session_state and "lon" in st.session_state:
        user_lat = st.session_state.lat
        user_lon = st.session_state.lon
        location_display_name = st.session_state.get("loc_name", "Ubicación seleccionada")
        
        # Compact custom location banner
        st.markdown(
            f"""<div class="custom-compact-alert">
                <b>Ubicación activa:</b> {location_display_name} ({user_lat:.4f}, {user_lon:.4f}) | 
                <b>Radio:</b> {max_distance_input} m | 
                <b>Hora consultada:</b> {target_time.strftime('%H:%M')}
            </div>""", 
            unsafe_allow_html=True
        )
        
        nearby_stations_df = find_stations_within_radius(user_lat, user_lon, df_stations, max_distance_m=max_distance_input, is_moto=is_moto)
        
        if nearby_stations_df.empty:
            vehicle_type_label = "motos" if is_moto else "coches"
            st.warning(f"⚠️ No se encontraron estaciones con conectores para **{vehicle_type_label}** a menos de **{max_distance_input} metros**.")
        else:
            map_object = folium.Map(
                location=[user_lat, user_lon], 
                zoom_start=15, 
                tiles="OpenStreetMap"
            )
            
            folium.Marker(
                location=[user_lat, user_lon],
                popup="<b>Tu Ubicación</b>",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(map_object)
            
            folium.Circle(
                radius=max_distance_input,
                location=[user_lat, user_lon],
                color="#3186cc",
                fill=True,
                fill_color="#3186cc",
                fill_opacity=0.1
            ).add_to(map_object)
            
            results_list = []
            
            for idx, station_row in nearby_stations_df.iterrows():
                car_ports = int(station_row.get('total_car_ports', station_row.get('standard_ports', 0)))
                moto_ports = int(station_row.get('total_moto_ports', station_row.get('motorcycle_ports', 0)))
                
                total_ports = moto_ports if is_moto else car_ports
                total_ports = max(1, total_ports)
                
                is_onstreet = bool(station_row.get('onstreet_location', True))
                location_type_label = "Superficie" if is_onstreet else "Parking"
                
                X_features = build_features(
                    selected_model, 
                    station_row['station_coordinates_latitude'], 
                    station_row['station_coordinates_longitude'], 
                    target_datetime,
                    is_onstreet=is_onstreet
                )
                
                sim_rate, badge, color_hex = predict_stochastic_status(selected_model, X_features, total_ports=total_ports)
                station_address = station_row.get('address_address_string', "Estación en Zona Cercana")
                
                popup_html = f"""
                <div style="font-family: Arial, sans-serif; width: 210px;">
                    <span style="font-size: 11px; color: #777; font-weight: bold; text-transform: uppercase;">{location_type_label}</span>
                    <h4 style="margin: 3px 0 8px 0; color: #2C3E50; font-size: 14px;">{station_address}</h4>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 5px 0;">
                    <ul style="padding-left: 15px; margin: 5px 0; font-size: 12px; color: #333;">
                        <li><b>Coche:</b> {car_ports} enchufes</li>
                        <li><b>Moto:</b> {moto_ports} enchufes</li>
                    </ul>
                    <div style="margin-top: 8px; padding: 4px; background-color: #f8f9fa; border-radius: 4px; text-align: center;">
                        <span style="font-size: 11px; font-weight: bold;">{badge}</span>
                    </div>
                </div>
                """
                
                folium.Marker(
                    location=[station_row['station_coordinates_latitude'], station_row['station_coordinates_longitude']],
                    popup=folium.Popup(popup_html, max_width=250),
                    icon=folium.Icon(color=color_hex, icon="plug", prefix="fa"),
                    tooltip=f"{station_address} ({badge})"
                ).add_to(map_object)
                
                results_list.append({
                    'Dirección / Referencia': station_address,
                    'Tipo Ubicación': location_type_label,
                    'Distancia (m)': round(station_row['distance_meters'], 1),
                    'Enchufes Coche': car_ports,
                    'Enchufes Moto': moto_ports,
                    'Estado de Carga Recomendado': badge
                })
                
            results_df = pd.DataFrame(results_list)
            
            st.subheader(f"📍 Mapa de Estaciones (Encontradas: {len(results_df)})")
            st_folium(map_object, width=None, height=450, use_container_width=True, key="endolla_map")
            
            st.subheader("📊 Diagnóstico de Disponibilidad")
            st.dataframe(
                results_df[['Dirección / Referencia', 'Tipo Ubicación', 'Distancia (m)', 'Enchufes Coche', 'Enchufes Moto', 'Estado de Carga Recomendado']], 
                use_container_width=True
            )
            
            # Charge Time Simulator with prominent expander title & styling
            with st.expander("⏱️ Simulador de Tiempo de Carga"):
                st.markdown('<div class="simulator-container">', unsafe_allow_html=True)
                st.markdown("##### Cálculo estimado del tiempo de recarga según batería y potencia del conector")
                
                col_sim1, col_sim2, col_sim3 = st.columns(3)
                
                min_battery = 0.5 if is_moto else 5.0
                max_battery = 15.0 if is_moto else 150.0
                default_battery = 4.0 if is_moto else 50.0
                step_battery = 0.5 if is_moto else 5.0
                
                with col_sim1:
                    battery_capacity = st.number_input(
                        "Capacidad Batería (kWh):", 
                        min_value=min_battery, 
                        max_value=max_battery, 
                        value=default_battery, 
                        step=step_battery, 
                        key="sim_bat"
                    )
                with col_sim2:
                    initial_soc = st.slider("Carga Inicial (%):", 0, 90, 20, key="sim_ini")
                with col_sim3:
                    target_soc = st.slider("Carga Deseada (%):", 10, 100, 80, key="sim_tgt")
                    
                if target_soc > initial_soc:
                    energy_needed_kwh = battery_capacity * ((target_soc - initial_soc) / 100.0)
                    charging_efficiency = 0.90
                    
                    if is_moto:
                        power_options = [
                            {"real_power_kw": 3.60, "description": "Carga Lenta (AC)"},
                            {"real_power_kw": 7.20, "description": "Semirápida Estándar (AC)"}
                        ]
                    else:
                        power_options = [
                            {"real_power_kw": 3.60, "description": "Carga Lenta (AC)"},
                            {"real_power_kw": 7.20, "description": "Semirápida Estándar (AC)"},
                            {"real_power_kw": 22.00, "description": "Semirápida Alta (AC)"},
                            {"real_power_kw": 50.00, "description": "Rápida (DC)"}
                        ]
                    
                    simulation_results = []
                    for option in power_options:
                        power_kw = option["real_power_kw"]
                        estimated_hours = energy_needed_kwh / (power_kw * charging_efficiency)
                        hours_int = int(estimated_hours)
                        minutes_int = int((estimated_hours - hours_int) * 60)
                        
                        time_display = f"{hours_int}h {minutes_int}m" if hours_int > 0 else f"{minutes_int} min"
                        simulation_results.append({
                            "Categoría y Corriente": option["description"],
                            "Potencia Conector": f"{power_kw:.2f} kW",
                            "Tiempo Estimado": time_display
                        })
                    
                    sim_table_df = pd.DataFrame(simulation_results)
                    st.markdown(f"### **Energía requerida:** `{energy_needed_kwh:.2f} kWh` *(del {initial_soc}% al {target_soc}%)*")
                    st.table(sim_table_df)
                else:
                    st.warning("⚠️ El porcentaje de carga deseada debe ser mayor que la carga inicial.")
                st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.error("❌ Por favor define una ubicación válida (dirección o GPS) y pulsa 'Buscar Estaciones'.")