import streamlit as st

# 1. Page Configuration & Custom CSS (Debe ejecutarse antes de st.Page)
st.set_page_config(
    page_title="Endolla Barcelona — Data & Governance",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ocultar el botón de colapsar la barra lateral
st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# 2. Navigation Setup
b2g_page = st.Page(
    "pages/b2g_governance.py", 
    title="B2G - Gobernanza de Red", 
    icon="🏛️",
    default=True
)

network_desc_page = st.Page(
    "pages/network_description.py", 
    title="Descripción de la Red", 
    icon="📊"
)

# 3. Router Configuration
navigation_router = st.navigation({
    "Producto / Gobernanza": [b2g_page],
    "Presentación & Análisis": [network_desc_page]
})

# 4. Route Execution
navigation_router.run()