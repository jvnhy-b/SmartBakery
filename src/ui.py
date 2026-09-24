import html
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parents[1] / "assets"
LOGO = str(ASSETS / "smartbakery-logo.svg")
LOGO_ICON = str(ASSETS / "smartbakery-icon.svg")

# Alto fijo para que las tarjetas y el panel de IA queden alineados.
KPI_HEIGHT = 152

# Valores más largos (nombres de producto) se dibujan más chicos, a dos líneas.
LONG_VALUE = 14

# Evita que el contenedor de un <style> inyectado deje un hueco en blanco.
HIDDEN_STYLE_SLOT = (
    '[data-testid="stElementContainer"]:has(.stHtml > style){display:none}'
)

# Streamlit reserva 6rem arriba; con 3.5rem la barra superior sigue despejada.
TOP_SPACING = '[data-testid="stMainBlockContainer"]{padding-top:3.5rem}'


def inject_css(rules: str) -> None:
    st.html(f"<style>{rules}{HIDDEN_STYLE_SLOT}</style>")


@st.cache_data(show_spinner=False)
def _page_rules() -> str:
    # Los colores salen del tema de .streamlit/config.toml.
    surface = st.get_option("theme.backgroundColor")
    subtle = st.get_option("theme.secondaryBackgroundColor")
    edge = st.get_option("theme.borderColor")
    text = st.get_option("theme.textColor")
    muted = st.get_option("theme.grayColor")
    primary = st.get_option("theme.primaryColor")
    up = st.get_option("theme.greenColor")
    down = st.get_option("theme.redColor")
    tones = "".join(
        f".sb-kpi--t{index}{{--sb-tone:{color};}}"
        for index, color in enumerate(st.get_option("theme.chartCategoricalColors"))
    )
    return f"""
    .sb-kpi {{
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: {KPI_HEIGHT}px;
        padding: 1.2rem 1.3rem;
        text-align: center;
        background: {surface};
        border: 1px solid {edge};
        border-radius: 14px;
        transition: box-shadow 0.2s ease, transform 0.2s ease,
                    border-color 0.2s ease;
    }}
    .sb-kpi:hover {{
        transform: translateY(-1px);
        border-color: color-mix(in srgb, {text} 22%, transparent);
        box-shadow: 0 6px 18px color-mix(in srgb, {text} 10%, transparent);
    }}
    {tones}
    .sb-kpi-title {{
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        margin-bottom: 0.55rem;
        color: {muted};
        font-size: 0.7rem;
        font-weight: 750;
        letter-spacing: 0.055em;
        line-height: 1.25;
        text-transform: uppercase;
    }}
    .sb-kpi-help {{
        cursor: help;
        opacity: 0.7;
        font-family: "Material Symbols Rounded";
        font-size: 0.82rem;
        font-weight: 400;
        letter-spacing: normal;
    }}
    .sb-kpi-num {{
        color: var(--sb-tone);
        font-size: 2.15rem;
        font-weight: 750;
        font-variant-numeric: tabular-nums;
        letter-spacing: -0.025em;
        line-height: 1.05;
    }}
    .sb-kpi-num.is-long {{
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
        overflow: hidden;
        overflow-wrap: anywhere;
        font-size: 1.4rem;
        letter-spacing: -0.015em;
        line-height: 1.2;
    }}
    .sb-kpi-label {{
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        margin-top: 0.45rem;
        color: {muted};
        font-size: 0.79rem;
        font-weight: 600;
        line-height: 1.35;
    }}
    .sb-kpi-delta {{
        display: inline-flex;
        align-items: center;
        gap: 0.18rem;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
    }}
    .sb-kpi-delta::before {{
        font-family: "Material Symbols Rounded";
        font-size: 0.95rem;
        font-weight: 400;
    }}
    .sb-kpi-delta.is-up {{ color: {up}; }}
    .sb-kpi-delta.is-up::before {{ content: "trending_up"; }}
    .sb-kpi-delta.is-down {{ color: {down}; }}
    .sb-kpi-delta.is-down::before {{ content: "trending_down"; }}

    .sb-fbar {{
        position: fixed;
        top: 10px;
        left: 50%;
        z-index: 1000000;
        transform: translateX(-50%);
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        max-width: min(80vw, 820px);
        padding: 0.5rem 1.1rem;
        background: {surface};
        border: 1px solid {edge};
        border-radius: 999px;
        box-shadow: 0 10px 30px color-mix(in srgb, {text} 14%, transparent);
        font-size: 0.78rem;
    }}
    .sb-fbar-icon {{
        flex: 0 0 auto;
        color: {primary};
        font-family: "Material Symbols Rounded";
        font-size: 0.95rem;
    }}
    .sb-fbar-label {{
        flex: 0 0 auto;
        color: {muted};
        font-weight: 700;
    }}
    .sb-fbar-chip {{
        padding: 2px 11px;
        color: {muted};
        background: {subtle};
        border: 1px solid {edge};
        border-radius: 999px;
        font-weight: 600;
        white-space: nowrap;
    }}
    .sb-fbar-chip.is-on {{
        color: {primary};
        background: color-mix(in srgb, {primary} 10%, transparent);
        border-color: color-mix(in srgb, {primary} 28%, transparent);
    }}
    /* La pill es fija: su contenedor no debe ocupar espacio. */
    [data-testid="stElementContainer"]:has(.stHtml > .sb-fbar) {{
        height: 0 !important;
        min-height: 0 !important;
        margin-bottom: -1rem !important;
    }}
    """


def format_eur(value: float) -> str:
    """1234567.89 -> "1.234.567,89 €"."""
    formatted = f"{value:,.2f}"
    return formatted.replace(",", "@").replace(".", ",").replace("@", ".") + " €"


def format_units(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def format_delta(change: float | None) -> str | None:
    if change is None:
        return None
    return f"{change:+.1f} %".replace(".", ",")


def brand_logo() -> None:
    st.logo(LOGO, icon_image=LOGO_ICON, size="large")


def page_header(title: str, subtitle: str) -> None:
    inject_css(TOP_SPACING + _page_rules())
    st.title(title)
    st.caption(subtitle)


def filter_pill(items: list[tuple[str, bool]]) -> None:
    """``items``: pares ``(texto, activo)``; los activos se resaltan."""
    chips = "".join(
        f'<span class="sb-fbar-chip{" is-on" if active else ""}">'
        f"{html.escape(text)}</span>"
        for text, active in items
        if text
    )
    if not chips:
        return
    st.html(
        '<div class="sb-fbar">'
        '<span class="sb-fbar-icon" aria-hidden="true">filter_alt</span>'
        '<span class="sb-fbar-label">Mostrando:</span>'
        f"{chips}</div>"
    )


def kpi_card(
    label: str,
    value: str,
    *,
    tone: int = 0,
    delta: float | None = None,
    delta_context: str | None = None,
    note: str | None = None,
    help: str | None = None,
) -> None:
    """``tone`` indexa la paleta de gráficas del tema; ``delta`` (%) se dibuja
    con flecha y color, ``note`` es texto gris y ``help`` un tooltip."""
    change = format_delta(delta)
    if change is not None:
        direction = "is-up" if delta >= 0 else "is-down"
        context = f"<span>{html.escape(delta_context)}</span>" if delta_context else ""
        support = f'<span class="sb-kpi-delta {direction}">{change}</span>{context}'
    else:
        support = html.escape(note) if note else ""

    hint = (
        f'<span class="sb-kpi-help" title="{html.escape(help)}">help</span>'
        if help
        else ""
    )
    safe_value = html.escape(str(value))
    size = " is-long" if len(str(value)) > LONG_VALUE else ""

    st.html(
        f'<div class="sb-kpi sb-kpi--t{tone}">'
        f'<div class="sb-kpi-title">{html.escape(label)}{hint}</div>'
        f'<div class="sb-kpi-num{size}" title="{safe_value}">{safe_value}</div>'
        f'<div class="sb-kpi-label">{support}</div>'
        f"</div>"
    )


def coming_soon(module: str, icon: str, description: str) -> None:
    inject_css(TOP_SPACING)
    st.title(module)
    st.space("medium")

    _, center, _ = st.columns([1, 2, 1])
    with center:
        with st.container(border=True, horizontal_alignment="center"):
            st.space("small")
            st.markdown(f"## {icon}", text_alignment="center")
            st.badge("Próximamente", icon=":material/schedule:", color="orange")
            st.caption(description, text_alignment="center")
            st.space("small")
