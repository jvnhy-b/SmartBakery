"""Acceso local de demostración: NO es autenticación de producción."""

import hmac

import streamlit as st

from src.login_ui import render_bread_animation, render_login_styles

SESSION_KEY = "authenticated_user"

def _credentials() -> tuple[str, str] | None:
    try:
        auth = st.secrets["auth"]
        return str(auth["username"]), str(auth["password"])
    except (KeyError, FileNotFoundError):
        return None


def current_user() -> str | None:
    return st.session_state.get(SESSION_KEY)


def is_authenticated() -> bool:
    return current_user() is not None


def logout() -> None:
    st.session_state.pop(SESSION_KEY, None)


def _check(username: str, password: str) -> bool:
    # Comparación en tiempo constante (evita ataques de temporización).
    expected = _credentials()
    if expected is None:
        return False
    user_ok = hmac.compare_digest(username.strip(), expected[0])
    password_ok = hmac.compare_digest(password, expected[1])
    return user_ok and password_ok


def render_login() -> None:
    render_login_styles()
    animation_slot = st.empty()

    credentials_ready = _credentials() is not None
    with st.form("login", border=False):
        st.title("Inicia sesión")
        st.markdown(
            '<p class="login-subtitle">Ingresa tus credenciales para continuar.</p>',
            unsafe_allow_html=True,
        )

        if not credentials_ready:
            st.error(
                "No hay credenciales configuradas. Copia "
                "`.streamlit/secrets.toml.example` a `.streamlit/secrets.toml`.",
                icon=":material/key_off:",
            )

        username = st.text_input("Usuario", placeholder="Ingresa tu usuario")
        password = st.text_input(
            "Contraseña", type="password", placeholder="Ingresa tu contraseña"
        )
        submitted = st.form_submit_button(
            "Iniciar sesión",
            type="primary",
            icon=":material/login:",
            width="stretch",
            disabled=not credentials_ready,
        )
        login_feedback = st.empty()

    with animation_slot.container():
        render_bread_animation()

    st.markdown(
        '<div class="login-footer">SmartBakery © 2026 · Uso autorizado</div>',
        unsafe_allow_html=True,
    )

    if submitted:
        with login_feedback:
            if _check(username, password):
                st.session_state[SESSION_KEY] = username.strip()
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.", icon=":material/error:")
