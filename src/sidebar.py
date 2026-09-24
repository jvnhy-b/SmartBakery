from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Mapping, Sequence

import streamlit as st

from src.auth import current_user, logout


ASSETS = Path(__file__).resolve().parents[1] / "assets"
LOGO = ASSETS / "smartbakery-logo.svg"


@st.cache_data(show_spinner=False)
def _logo_sidebar_html(ruta: str) -> str:
    encoded = base64.b64encode(Path(ruta).read_bytes()).decode("ascii")
    return (
        '<div class="sb-logo">'
        f'<img src="data:image/svg+xml;base64,{encoded}" alt="SmartBakery" />'
        "</div>"
    )


def _user_identity() -> tuple[str, str]:
    username = (current_user() or "Usuario").strip()
    display_name = "Usuario" if username.casefold() == "demo" else username
    parts = [part for part in display_name.split() if part]
    initials = "U" if not parts else "".join(part[0] for part in parts[:2]).upper()
    return html.escape(display_name), html.escape(initials)


def _render_user_block() -> None:
    display_name, initials = _user_identity()
    st.markdown(
        f"""
        <div class="sb-user">
            <div class="sb-avatar" aria-hidden="true">
                <span class="sb-avatar-initials">{initials}</span>
            </div>
            <div class="sb-user-meta">
                <div class="sb-user-name" title="{display_name}">{display_name}</div>
                <div class="sb-user-suc">SmartBakery</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _sidebar_css() -> str:
    return """
    <style>
    :root {
        --sb-canvas: #ffffff;
        --sb-surface: var(--app-surface, #ffffff);
        --sb-surface-soft: var(--app-surface-subtle, #f8fafb);
        --sb-hover: var(--app-nav-hover, #f1f5f8);
        --sb-active-bg: var(--app-nav-active, #e1edf6);
        --sb-active: var(--app-nav, #2d6f9c);
        --sb-section: #176f9e;
        --sb-section-strong: #0b5f87;
        --sb-section-bg: rgba(23, 111, 158, 0.055);
        --sb-section-bg-open: rgba(23, 111, 158, 0.10);
        --sb-section-border: rgba(23, 111, 158, 0.12);
        --sb-text: var(--app-text-muted, #526873);
        --sb-text-strong: var(--app-text, #24313a);
        --sb-muted: var(--app-text-soft, #60727d);
        --sb-border: var(--app-border-subtle, #e4eaf0);
        --sb-focus: var(--app-nav-focus, rgba(11, 120, 181, 0.28));
        --sb-shadow: 0 10px 32px rgba(31, 50, 67, 0.10),
                     0 2px 8px rgba(31, 50, 67, 0.06);
    }

    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {
        background: var(--sb-canvas) !important;
        background-color: #ffffff !important;
        background-image: none !important;
        border-right: 0 !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        box-sizing: border-box !important;
        position: relative !important;
        width: calc(100% - 22px) !important;
        height: calc(100% - 24px) !important;
        margin: 12px 10px 12px 12px !important;
        padding: 0.3rem 0.72rem 1rem !important;
        gap: 0.18rem !important;
        background: var(--sb-surface) !important;
        border: 1px solid var(--sb-border) !important;
        border-radius: 18px !important;
        box-shadow: var(--sb-shadow) !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarContent"],
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] > div,
    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        background-color: #ffffff !important;
        background-image: none !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        position: absolute !important;
        top: 0.55rem !important;
        right: 0.55rem !important;
        z-index: 5 !important;
        width: auto !important;
        min-height: 0 !important;
        padding: 0 !important;
        background: transparent !important;
    }

    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button {
        width: 2.35rem !important;
        min-width: 2.35rem !important;
        height: 2.35rem !important;
        min-height: 2.35rem !important;
        padding: 0 !important;
        color: #647b88 !important;
        background: #ffffff !important;
        border: 1px solid var(--sb-border) !important;
        border-radius: 999px !important;
        box-shadow: 0 3px 10px rgba(31, 50, 67, 0.10) !important;
    }

    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="collapsedControl"] button:hover {
        color: var(--sb-active) !important;
        background: var(--sb-hover) !important;
        border-color: #cddbe5 !important;
    }

    [data-testid="stSidebarCollapseButton"] button:focus-visible,
    [data-testid="stSidebarCollapsedControl"] button:focus-visible,
    [data-testid="collapsedControl"] button:focus-visible {
        outline: 3px solid var(--sb-focus) !important;
        outline-offset: 2px !important;
    }

    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg {
        color: currentColor !important;
        fill: currentColor !important;
    }

    [data-testid="stSidebar"] .sb-logo {
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 6.5rem;
        padding: 0.8rem 2.6rem 0.7rem;
        margin: 0 0.1rem 0.55rem;
        border-bottom: 1px solid var(--sb-border);
    }

    [data-testid="stSidebar"] .sb-logo img {
        display: block;
        width: auto;
        max-width: 145px;
        max-height: 42px;
        margin: 0 auto;
        object-fit: contain;
    }

    [data-testid="stSidebar"] .sb-user {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        min-width: 0;
        padding: 0.68rem 0.72rem;
        margin: 0.15rem 0.1rem 0.65rem;
        background: var(--sb-surface-soft);
        border: 1px solid var(--sb-border);
        border-radius: 13px;
    }

    [data-testid="stSidebar"] .sb-avatar {
        display: grid;
        place-items: center;
        flex: 0 0 2.25rem;
        width: 2.25rem;
        height: 2.25rem;
        color: #ffffff;
        background: linear-gradient(145deg, #1683bd, #2d6f9c);
        border: 2px solid #ffffff;
        border-radius: 50%;
        box-shadow: 0 2px 7px rgba(45, 111, 156, 0.24);
    }

    [data-testid="stSidebar"] .sb-avatar-initials {
        font-size: 0.78rem;
        font-weight: 700;
        line-height: 1;
        letter-spacing: 0.02em;
    }

    [data-testid="stSidebar"] .sb-user-meta {
        min-width: 0;
        flex: 1;
    }

    [data-testid="stSidebar"] .sb-user-name {
        overflow: hidden;
        color: var(--sb-text-strong);
        font-size: 0.88rem;
        font-weight: 650;
        line-height: 1.25;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    [data-testid="stSidebar"] .sb-user-suc {
        overflow: hidden;
        margin-top: 0.16rem;
        color: var(--sb-muted);
        font-size: 0.75rem;
        font-weight: 450;
        line-height: 1.2;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] {
        margin: 0.16rem 0 0.08rem !important;
        background: transparent !important;
        border: 0 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] details,
    [data-testid="stSidebar"] [data-testid="stExpander"] details:hover {
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        min-height: 2.85rem !important;
        padding: 0.62rem 0.72rem !important;
        color: var(--sb-section) !important;
        background: var(--sb-section-bg) !important;
        border: 1px solid var(--sb-section-border) !important;
        border-radius: 12px !important;
        transition: color 120ms ease, background-color 120ms ease,
                    border-color 120ms ease !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] details:not([open]) > summary {
        color: var(--sb-section) !important;
        background: var(--sb-section-bg) !important;
        border-color: var(--sb-section-border) !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
        color: var(--sb-section-strong) !important;
        background: var(--sb-section-bg-open) !important;
        border-color: rgba(23, 111, 158, 0.20) !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary:focus-visible {
        outline: 3px solid var(--sb-focus) !important;
        outline-offset: 1px !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] details[open] > summary {
        color: var(--sb-section-strong) !important;
        background: var(--sb-section-bg-open) !important;
        border-color: rgba(23, 111, 158, 0.16) !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary p,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary span {
        color: currentColor !important;
        font-size: 0.98rem !important;
        font-weight: 720 !important;
        letter-spacing: 0.005em !important;
        text-transform: none !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
        color: currentColor !important;
        font-size: 1.12rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary svg {
        color: currentColor !important;
        fill: currentColor !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
        padding: 0.35rem 0 0.42rem 0.18rem !important;
        background: transparent !important;
        border: 0 !important;
    }

    [data-testid="stSidebar"] [class*="st-key-sb_nav_"] {
        margin: 0.08rem 0 !important;
    }

    [data-testid="stSidebar"] [class*="st-key-sb_nav_"] [data-testid="stPageLink"] {
        width: 100% !important;
    }

    [data-testid="stSidebar"] [class*="st-key-sb_nav_"] a[data-testid="stPageLink-NavLink"] {
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        min-height: 2.7rem !important;
        padding: 0.55rem 0.72rem !important;
        color: var(--sb-text) !important;
        text-decoration: none !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        transition: color 120ms ease, background-color 120ms ease,
                    border-color 120ms ease, box-shadow 120ms ease !important;
    }

    [data-testid="stSidebar"] [class*="st-key-sb_nav_"] a[data-testid="stPageLink-NavLink"] p,
    [data-testid="stSidebar"] [class*="st-key-sb_nav_"] a[data-testid="stPageLink-NavLink"] span {
        color: currentColor !important;
        font-size: 0.92rem !important;
        font-weight: 580 !important;
        line-height: 1.35 !important;
    }

    [data-testid="stSidebar"] [class*="st-key-sb_nav_"] a[data-testid="stPageLink-NavLink"] [data-testid="stIconMaterial"] {
        flex: 0 0 1.2rem !important;
        width: 1.2rem !important;
        margin-right: 0.08rem !important;
        color: #668491 !important;
        font-size: 1.08rem !important;
        line-height: 1 !important;
    }

    [data-testid="stSidebar"] [class*="st-key-sb_nav_"] a[data-testid="stPageLink-NavLink"] svg {
        flex: 0 0 auto !important;
        width: 1.08rem !important;
        height: 1.08rem !important;
        color: currentColor !important;
        fill: currentColor !important;
    }

    [data-testid="stSidebar"] [class*="st-key-sb_nav_"] a[data-testid="stPageLink-NavLink"]:hover {
        color: var(--sb-text-strong) !important;
        background: var(--sb-hover) !important;
    }

    [data-testid="stSidebar"] [class*="st-key-sb_nav_"] a[data-testid="stPageLink-NavLink"]:focus-visible {
        outline: 3px solid var(--sb-focus) !important;
        outline-offset: 1px !important;
    }

    [data-testid="stSidebar"] [class*="st-key-sb_nav_"][class*="_active"] a[data-testid="stPageLink-NavLink"] {
        color: #176f9e !important;
        background: rgba(0, 175, 239, 0.07) !important;
        border-color: transparent !important;
        border-radius: 6px !important;
        box-shadow: inset 3px 0 0 #00afef !important;
    }

    [data-testid="stSidebar"] [class*="st-key-sb_nav_"][class*="_active"] a[data-testid="stPageLink-NavLink"] p,
    [data-testid="stSidebar"] [class*="st-key-sb_nav_"][class*="_active"] a[data-testid="stPageLink-NavLink"] span {
        font-weight: 680 !important;
    }

    [data-testid="stSidebar"] [class*="st-key-sb_nav_"][class*="_active"] a[data-testid="stPageLink-NavLink"] [data-testid="stIconMaterial"] {
        color: #00a6df !important;
    }

    [data-testid="stSidebar"] .sb-logout-sep {
        height: 1px;
        margin: 0.72rem 0.18rem 0.58rem;
        background: var(--sb-border);
    }

    [data-testid="stSidebar"] .st-key-sb_logout_btn button {
        width: 100% !important;
        min-height: 2.7rem !important;
        padding: 0.55rem 0.75rem !important;
        color: #a40e26 !important;
        background: #fff1f2 !important;
        border: 1px solid #fecaca !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        font-size: 0.84rem !important;
        font-weight: 620 !important;
    }

    [data-testid="stSidebar"] .st-key-sb_logout_btn button:hover {
        color: #82071e !important;
        background: #ffe4e6 !important;
        border-color: #fda4af !important;
    }

    [data-testid="stSidebar"] .st-key-sb_logout_btn button:focus-visible {
        outline: 3px solid rgba(207, 34, 46, 0.20) !important;
        outline-offset: 2px !important;
    }

    [data-testid="stSidebar"] *::-webkit-scrollbar { width: 6px; }
    [data-testid="stSidebar"] *::-webkit-scrollbar-track { background: transparent; }
    [data-testid="stSidebar"] *::-webkit-scrollbar-thumb {
        background: #d5dfe6;
        border-radius: 999px;
    }
    [data-testid="stSidebar"] *::-webkit-scrollbar-thumb:hover {
        background: #b8c7d1;
    }

    @media (max-width: 900px) {
        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            width: 100% !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0.35rem 0.78rem 1rem !important;
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        [data-testid="stSidebar"] * {
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """


def _render_links(
    pages: Sequence[st.Page], section_key: str, active_page: st.Page
) -> None:
    for index, page in enumerate(pages):
        state = "active" if page is active_page else "idle"
        # El CSS resalta el enlace activo leyendo "_active" en la clave.
        with st.container(key=f"sb_nav_{section_key}_{index}_{state}_icon"):
            st.page_link(page, label=page.title, icon=page.icon, width="stretch")


def render_sidebar(
    sections: Mapping[str, Sequence[st.Page]], active_page: st.Page
) -> None:
    st.markdown(_sidebar_css(), unsafe_allow_html=True)

    section_icons = {
        "Aplicaciones": ":material/apps:",
        "Herramientas": ":material/build:",
        "Configuración": ":material/settings:",
    }

    with st.sidebar:
        st.markdown(_logo_sidebar_html(str(LOGO)), unsafe_allow_html=True)
        _render_user_block()

        for index, (section, pages) in enumerate(sections.items()):
            with st.expander(
                section,
                expanded=active_page in pages,
                icon=section_icons.get(section, ":material/folder:"),
            ):
                _render_links(pages, f"section_{index}", active_page)

        st.markdown('<div class="sb-logout-sep"></div>', unsafe_allow_html=True)
        with st.container(key="sb_logout_btn"):
            if st.button(
                "Salir",
                type="primary",
                width="stretch",
                icon=":material/power_settings_new:",
                key="sidebar_logout_action",
            ):
                logout()
                st.rerun()
