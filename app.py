import streamlit as st
from translations import t

# 1. Page configuration and CSS styling
st.set_page_config(
    page_title="Endolla Barcelona — Data & Governance",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# 2. Global language selector in the sidebar
if "lang" not in st.session_state:
    st.session_state["lang"] = "ES"

selected_lang = st.sidebar.radio(
    "🌐 Idioma / Language",
    options=["ES", "EN"],
    format_func=lambda x: "🇪🇸 Español" if x == "ES" else "🇬🇧 English",
    horizontal=True
)
st.session_state["lang"] = selected_lang

# 3. Route setup using the translation function t()
b2g_page = st.Page(
    "pages/b2g_governance.py", 
    title=t("nav_b2g_title"), 
    icon="🏛️",
    default=True
)

network_desc_page = st.Page(
    "pages/network_description.py", 
    title=t("nav_desc_title"), 
    icon="📊"
)

# 4. Navigation router
navigation_router = st.navigation({
    t("nav_cat_product"): [b2g_page],
    t("nav_cat_presentation"): [network_desc_page]
})

# 5. Execution
navigation_router.run()
