import streamlit as st

from src.auth import is_authenticated, render_login
from src.sidebar import render_sidebar
from src.ui import coming_soon

st.set_page_config(
    page_title="SmartBakery · Sales Intelligence",
    page_icon=":material/bakery_dining:",
    layout="wide",
)

if not is_authenticated():
    render_login()
    st.stop()


def future_module(name: str, icon: str, description: str):
    def page() -> None:
        coming_soon(name, icon, description)

    return page


PLACEHOLDER_TEXT = "Este módulo formará parte de futuras versiones de SmartBakery."

pages = {
    "Aplicaciones": [
        st.Page(
            "app_pages/home.py",
            title="Inicio",
            icon=":material/home:",
            url_path="inicio",
            default=True,
        ),
        st.Page(
            future_module("Ventas", ":material/point_of_sale:", PLACEHOLDER_TEXT),
            title="Ventas",
            icon=":material/point_of_sale:",
            url_path="ventas",
        ),
        st.Page(
            future_module("Productos", ":material/bakery_dining:", PLACEHOLDER_TEXT),
            title="Productos",
            icon=":material/bakery_dining:",
            url_path="productos",
        ),
        st.Page(
            future_module("Inventario", ":material/inventory_2:", PLACEHOLDER_TEXT),
            title="Inventario",
            icon=":material/inventory_2:",
            url_path="inventario",
        ),
        st.Page(
            future_module("Clientes", ":material/group:", PLACEHOLDER_TEXT),
            title="Clientes",
            icon=":material/group:",
            url_path="clientes",
        ),
    ],
    "Herramientas": [
        st.Page(
            "app_pages/analytics.py",
            title="Analítica",
            icon=":material/analytics:",
            url_path="analitica",
        ),
        st.Page(
            future_module("Pronósticos", ":material/trending_up:", PLACEHOLDER_TEXT),
            title="Pronósticos",
            icon=":material/trending_up:",
            url_path="pronosticos",
        ),
        st.Page(
            future_module("Reportes", ":material/description:", PLACEHOLDER_TEXT),
            title="Reportes",
            icon=":material/description:",
            url_path="reportes",
        ),
    ],
    "Configuración": [
        st.Page(
            future_module("Configuración", ":material/settings:", PLACEHOLDER_TEXT),
            title="Configuración",
            icon=":material/settings:",
            url_path="configuracion",
        ),
    ],
}

navigation = st.navigation(pages, position="hidden")
render_sidebar(pages, navigation)
navigation.run()
