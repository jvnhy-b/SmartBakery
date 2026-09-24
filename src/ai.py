"""Panel de IA: API Gateway (POST /sales/analyze) -> Lambda -> Amazon Bedrock."""

import json
import urllib.error
import urllib.request
from datetime import date

import streamlit as st

from src.analytics import ALL_PRODUCTS
from src.ui import inject_css

ANALYZE_ENDPOINT_PATH = "/sales/analyze"
SECRET_KEY = "AWS_API_URL"
REQUEST_TIMEOUT = 15  # segundos

NOT_CONFIGURED_MESSAGE = (
    "La integración con Amazon Bedrock todavía no está configurada."
)
CONNECTION_ERROR = "No fue posible conectar con el servicio de análisis."
BAD_RESPONSE_ERROR = (
    "El servicio de análisis respondió en un formato inesperado."
)
UNAVAILABLE_ERROR = "El servicio de análisis no está disponible en este momento."

HTTP_ERRORS = {
    400: "Los datos enviados no son válidos para el análisis.",
    401: "El servicio de análisis rechazó la solicitud.",
    403: "El servicio de análisis rechazó la solicitud.",
    404: "No se encontró el servicio de análisis en la URL configurada.",
    413: "Selecciona un periodo más corto para realizar el análisis con IA.",
    429: (
        "Se alcanzó temporalmente el límite de solicitudes. "
        "Intenta nuevamente en unos segundos."
    ),
}

STATES = {
    "disconnected": ("Sin conectar", ":material/cloud_off:", "orange"),
    "ready": ("Conectado", ":material/cloud_done:", "green"),
    "analyzing": ("Analizando", ":material/autorenew:", "blue"),
    "completed": ("Analysis completed", ":material/check_circle:", "green"),
    "error": ("Error", ":material/error:", "red"),
}

CHAT_KEY = "ai_conversation"

GREETING = (
    "Interpreto con inteligencia artificial generativa las métricas del periodo "
    "que tengas filtrado. Presiona **Analyze with AI** y te paso el resumen, los "
    "hallazgos y las recomendaciones."
)

# Alto que ocupan cabecera, botón y detalles; el resto es para el chat.
PANEL_CHROME = 205
MIN_CHAT_HEIGHT = 160
DEFAULT_CHAT_HEIGHT = 280


class AnalysisError(Exception):
    """Error del análisis con un mensaje ya apto para mostrar al usuario."""


def api_url() -> str:
    try:
        url = str(st.secrets[SECRET_KEY]).strip()
    except (KeyError, FileNotFoundError):
        return ""
    return url if url.startswith(("https://", "http://")) else ""


def is_ai_configured() -> bool:
    return bool(api_url())


def _validated_analysis(data: object) -> dict:
    analysis = data.get("analysis") if isinstance(data, dict) else None
    if not isinstance(analysis, dict):
        raise AnalysisError(BAD_RESPONSE_ERROR)

    summary = analysis.get("summary")
    insights = analysis.get("insights")
    recommendations = analysis.get("recommendations")
    if (
        not isinstance(summary, str)
        or not isinstance(insights, list)
        or not isinstance(recommendations, list)
    ):
        raise AnalysisError(BAD_RESPONSE_ERROR)

    return {
        "summary": summary,
        "insights": [str(item) for item in insights],
        "recommendations": [str(item) for item in recommendations],
    }


def analyze_sales_with_ai(payload: dict) -> dict:
    """Devuelve el bloque 'analysis'; los fallos se lanzan como AnalysisError."""
    url = api_url()
    if not url:
        raise AnalysisError(NOT_CONFIGURED_MESSAGE)

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            raw = response.read()
    except urllib.error.HTTPError as error:
        raise AnalysisError(HTTP_ERRORS.get(error.code, UNAVAILABLE_ERROR)) from error
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise AnalysisError(CONNECTION_ERROR) from error

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise AnalysisError(BAD_RESPONSE_ERROR) from error

    return _validated_analysis(data)


def status_badge(state: str, target=st) -> None:
    label, icon, color = STATES[state]
    target.badge(label, icon=icon, color=color)


@st.cache_data(show_spinner=False)
def _chat_rules() -> str:
    mine = st.get_option("theme.primaryColor")
    on_mine = st.get_option("theme.backgroundColor")
    theirs = st.get_option("theme.secondaryBackgroundColor")
    edge = st.get_option("theme.borderColor")
    return f"""
    [class*="st-key-ai_bubble_"] {{
        max-width: 88% !important;
        padding: 0.5rem 0.78rem !important;
        border-radius: 14px !important;
        gap: 0.4rem !important;
    }}
    [class*="st-key-ai_bubble_"] p,
    [class*="st-key-ai_bubble_"] li {{
        font-size: 0.82rem !important;
        line-height: 1.55 !important;
    }}
    [class*="st-key-ai_bubble_"] ul {{
        margin: 0.15rem 0 0 !important;
        padding-left: 1.1rem !important;
    }}
    [class*="st-key-ai_bubble_user"] {{
        background: {mine} !important;
        border-bottom-right-radius: 4px !important;
    }}
    [class*="st-key-ai_bubble_user"] * {{ color: {on_mine} !important; }}
    [class*="st-key-ai_bubble_bot"] {{
        background: {theirs} !important;
        border: 1px solid {edge} !important;
        border-bottom-left-radius: 4px !important;
    }}
    """


def _request_text(metrics: dict) -> str:
    period = metrics["period"]
    start = date.fromisoformat(period["start"]).strftime("%d/%m/%Y")
    end = date.fromisoformat(period["end"]).strftime("%d/%m/%Y")
    product = period["product_filter"]
    scope = "todos los productos" if product == ALL_PRODUCTS else product
    return f"Analiza **{scope}** del {start} al {end}."


def _answer_text(analysis: dict) -> str:
    blocks = [analysis["summary"].strip()]
    if analysis["insights"]:
        detail = "\n".join(f"- {item}" for item in analysis["insights"])
        blocks.append(f"**Hallazgos clave**\n{detail}")
    if analysis["recommendations"]:
        detail = "\n".join(f"- {item}" for item in analysis["recommendations"])
        blocks.append(f"**Recomendaciones**\n{detail}")
    return "\n\n".join(blocks)


def _bubble(role: str, text: str, index: int) -> None:
    align = "right" if role == "user" else "left"
    with st.container(
        horizontal=True, horizontal_alignment=align, key=f"ai_turn_{index}"
    ):
        with st.container(width="content", key=f"ai_bubble_{role}_{index}"):
            st.markdown(text)


def _chat_height(panel_height: int | str) -> int:
    if isinstance(panel_height, int):
        return max(MIN_CHAT_HEIGHT, panel_height - PANEL_CHROME)
    return DEFAULT_CHAT_HEIGHT


def _chat_slot(height: int):
    # Se reserva antes del botón para que la respuesta aparezca dentro del hilo.
    return st.container(
        height=height, border=False, gap="xsmall", autoscroll=True, key="ai_chat_log"
    )


def _render_chat(slot, chat: list[dict]) -> None:
    with slot:
        _bubble("bot", GREETING, 0)
        for index, message in enumerate(chat, start=1):
            _bubble(message["role"], message["text"], index)


def render_ai_panel(metrics: dict, height: int | str = "content") -> None:
    configured = is_ai_configured()
    if CHAT_KEY not in st.session_state:
        st.session_state[CHAT_KEY] = []
    chat = st.session_state[CHAT_KEY]

    inject_css(_chat_rules())

    with st.container(border=True, height=height):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.subheader("AI Business Analysis")
            badge_slot = st.empty()

        if not configured:
            st.warning(NOT_CONFIGURED_MESSAGE, icon=":material/info:")

        chat_slot = _chat_slot(_chat_height(height))

        analyze = st.button(
            "Analyze with AI",
            type="primary",
            icon=":material/auto_awesome:",
            width="stretch",
            disabled=not configured,
            key="analyze_with_ai",
        )

        if analyze:
            status_badge("analyzing", badge_slot)
            chat.append(
                {"role": "user", "text": _request_text(metrics), "error": False}
            )
            with st.spinner("Analizando ventas con Amazon Bedrock..."):
                try:
                    answer, failed = _answer_text(analyze_sales_with_ai(metrics)), False
                except AnalysisError as failure:
                    answer, failed = f":red[:material/error: {failure}]", True
            chat.append({"role": "bot", "text": answer, "error": failed})

        last = chat[-1] if chat else None
        if not configured:
            state = "disconnected"
        elif last is None:
            state = "ready"
        elif last["error"]:
            state = "error"
        else:
            state = "completed"
        status_badge(state, badge_slot)
        _render_chat(chat_slot, chat)

        with st.expander("Developer details", icon=":material/code:"):
            st.markdown("**Request payload**")
            st.code(f"POST {ANALYZE_ENDPOINT_PATH}", language="http")
            st.json(metrics, expanded=False)
