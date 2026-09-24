from __future__ import annotations

import html
import re
from datetime import datetime

import streamlit as st


HOME_MESSAGES: tuple[str, ...] = (
    "Del mostrador a una mejor decisión",
    "Ventas y productos bajo control",
    "Cada ticket cuenta una historia",
    "Datos claros para hacer crecer el negocio",
)

_DAYS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
_MONTHS = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)

_MODULES: tuple[tuple[str, str], ...] = (
    ("fa-cash-register", "sales"),
    ("fa-bread-slice", "products"),
    ("fa-boxes-stacked", "inventory"),
    ("fa-users", "customers"),
    ("fa-chart-line", "analytics"),
    ("fa-arrow-trend-up", "forecast"),
)


def _compact(fragment: str) -> str:
    return re.sub(r"\n\s*", "", fragment).strip()


def _greeting(now: datetime) -> str:
    if 5 <= now.hour < 12:
        return "Buenos días"
    if 12 <= now.hour < 19:
        return "Buenas tardes"
    return "Buenas noches"


def _date_label(now: datetime) -> str:
    return f"{_DAYS[now.weekday()]} {now.day} de {_MONTHS[now.month - 1]} de {now.year}"


def _display_name(username: str | None) -> str:
    if not username:
        return "Usuario"
    first = username.strip().split()[0]
    return first[:1].upper() + first[1:] if first else "Usuario"


def _typing_block(messages: tuple[str, ...], seconds_per_message: float = 4.2) -> str:
    """Efecto de máquina de escribir en CSS puro que alterna los mensajes."""
    messages =tuple(message for message in messages if message)
    if not messages:
        return ""

    count = len(messages)
    total = round(seconds_per_message * count, 2)
    window = 100 / count
    keyframes: list[str] = []
    bindings: list[str] = []
    lines: list[str] = []

    for index, message in enumerate(messages):
        chars = len(message)
        start = index * window
        typed = start + 0.36 * window
        held = start + 0.62 * window
        erased = start + 0.90 * window
        animation = f"sbHomeType{index}"

        if index == 0:
            opening = (
                f"0%{{width:0;visibility:visible;border-right-width:.1em;"
                f"animation-timing-function:steps({chars});}}"
            )
        else:
            opening = (
                "0%{width:0;visibility:hidden;border-right-width:0;"
                "animation-timing-function:steps(1);}"
                f"{start:.3f}%{{width:0;visibility:visible;border-right-width:.1em;"
                f"animation-timing-function:steps({chars});}}"
            )

        keyframes.append(
            f"@keyframes {animation}{{{opening}"
            f"{typed:.3f}%{{width:{chars}ch;border-right-width:.1em;animation-timing-function:linear;}}"
            f"{held:.3f}%{{width:{chars}ch;border-right-width:.1em;animation-timing-function:steps({chars});}}"
            f"{erased:.3f}%{{width:0;visibility:visible;border-right-width:0;}}"
            f"{erased + 0.2:.3f}%{{width:0;visibility:hidden;border-right-width:0;}}"
            "100%{width:0;visibility:hidden;border-right-width:0;}}"
        )
        bindings.append(
            f".sb-home-type-line:nth-child({index + 1}){{"
            f"animation:sbHomeCaret 1.05s steps(1) infinite,{animation} {total}s infinite;}}"
        )
        lines.append(f'<span class="sb-home-type-line">{html.escape(message)}</span>')

    max_chars = max(len(message) for message in messages)
    styles = "<style>" + "".join(keyframes + bindings) + f".sb-home-type{{width:{max_chars}ch;}}</style>"
    return styles + f'<span class="sb-home-type">{"".join(lines)}</span>'


def _scene() -> str:
    satellites = "".join(
        f'<div class="sb-home-satellite sb-home-satellite-{index} sb-home-satellite--{kind}">'
        f'<i class="fa-solid {icon}"></i></div>'
        for index, (icon, kind) in enumerate(_MODULES, start=1)
    )
    particles = "".join('<span class="sb-home-particle"></span>' for _ in range(7))
    dots = "".join(f'<span class="sb-home-dot sb-home-dot-{index}"></span>' for index in (1, 2, 3))
    faces = "".join(
        f'<div class="sb-home-face sb-home-face-{face}"></div>'
        for face in ("front", "back", "right", "left", "top", "bottom")
    )
    return (
        '<div class="sb-home-scene" aria-hidden="true">'
        '<div class="sb-home-glow"></div>'
        '<div class="sb-home-ring"></div>'
        '<div class="sb-home-ring sb-home-ring--inner"></div>'
        f'<div class="sb-home-particles">{particles}</div>'
        f'<div class="sb-home-cube">{faces}</div>'
        f'{dots}{satellites}'
        '</div>'
    )


def _styles() -> None:
    st.markdown(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<style>
@keyframes sbHomeFadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes sbHomeCaret {
    0%, 100% { border-right-color: var(--sb-home-brand); }
    50% { border-right-color: transparent; }
}
@keyframes sbHomeSpin {
    from { transform: rotateX(-22deg) rotateY(0deg); }
    to { transform: rotateX(-22deg) rotateY(360deg); }
}
@keyframes sbHomeOrbit {
    from { transform: rotate(0deg) translateX(var(--radius)) rotate(0deg); }
    to { transform: rotate(360deg) translateX(var(--radius)) rotate(-360deg); }
}
@keyframes sbHomeGlow {
    0%, 100% { opacity: .48; transform: scale(1); }
    50% { opacity: .78; transform: scale(1.08); }
}
@keyframes sbHomeRise {
    0% { opacity: 0; transform: translateY(24px) scale(.6); }
    15%, 85% { opacity: 1; }
    100% { opacity: 0; transform: translateY(-120px) scale(1); }
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] { background: #fff !important; }
[data-testid="stHeader"] { background: rgba(255, 255, 255, .92) !important; }

.sb-home {
    --sb-home-brand: #245bdb;
    --sb-home-brand-deep: #173e9f;
    --sb-home-text: #172033;
    --sb-home-muted: #64748b;
    width: 100%;
    max-width: min(1480px, calc(100vw - 300px));
    margin: 0 auto;
    padding: clamp(6px, 1.5vh, 18px) clamp(4px, 1vw, 12px) 24px;
}
.sb-home-hero {
    position: relative;
    min-height: calc(100vh - 240px);
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: clamp(24px, 4.5vh, 48px);
}
.sb-home-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image: radial-gradient(rgba(36, 91, 219, .12) 1px, transparent 1.5px);
    background-size: 26px 26px;
    -webkit-mask-image: radial-gradient(ellipse at 55% 42%, #000 20%, transparent 78%);
    mask-image: radial-gradient(ellipse at 55% 42%, #000 20%, transparent 78%);
}
.sb-home-hero > * { position: relative; }
.sb-home-main {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: clamp(24px, 5vw, 80px);
}
.sb-home-copy {
    min-width: 0;
    flex: 1 1 auto;
    animation: sbHomeFadeUp .5s cubic-bezier(.22, .61, .36, 1) both;
}
.sb-home-date {
    margin: 0 0 14px;
    color: var(--sb-home-muted);
    font-size: .82rem;
    font-weight: 650;
    letter-spacing: .16em;
    text-transform: uppercase;
}
.sb-home-title {
    margin: 0;
    color: var(--sb-home-text);
    font-size: clamp(2.4rem, 5.2vw, 4.1rem);
    font-weight: 700;
    line-height: 1.05;
    letter-spacing: -.045em;
}
.sb-home-title span { color: var(--sb-home-brand); }
.sb-home-typeline {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: clamp(18px, 3vh, 28px);
    min-height: 2em;
}
.sb-home-prompt,
.sb-home-type {
    font-family: ui-monospace, "Cascadia Code", "SF Mono", Menlo, Consolas, monospace;
    font-size: clamp(1.05rem, 1.9vw, 1.45rem);
}
.sb-home-prompt { color: var(--sb-home-brand); font-weight: 700; }
.sb-home-type {
    position: relative;
    display: block;
    height: 1.7em;
    max-width: 100%;
    color: var(--sb-home-text);
}
.sb-home-type-line {
    position: absolute;
    inset: 0 auto auto 0;
    width: 0;
    visibility: hidden;
    white-space: nowrap;
    overflow: hidden;
    border-right: 0 solid var(--sb-home-brand);
}
.sb-home-quote {
    margin: 0;
    align-self: center;
    max-width: 720px;
    text-align: center;
    color: var(--sb-home-muted);
    font-size: clamp(1rem, 1.5vw, 1.18rem);
    font-style: italic;
    line-height: 1.6;
    animation: sbHomeFadeUp .5s ease .25s both;
}

.sb-home-scene {
    --orbit-outer: clamp(128px, 15vw, 205px);
    --orbit-inner: calc(var(--orbit-outer) * .56);
    position: relative;
    flex: 0 0 auto;
    width: clamp(310px, 36vw, 520px);
    aspect-ratio: 1;
    perspective: 900px;
    display: grid;
    place-items: center;
    animation: sbHomeFadeUp .6s cubic-bezier(.22, .61, .36, 1) .1s both;
}
.sb-home-glow {
    position: absolute;
    inset: 0;
    margin: auto;
    width: 58%;
    height: 58%;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(36, 91, 219, .24), transparent 68%);
    filter: blur(8px);
    animation: sbHomeGlow 6s ease-in-out infinite;
}
.sb-home-ring {
    position: absolute;
    inset: 0;
    margin: auto;
    width: calc(var(--orbit-outer) * 2);
    height: calc(var(--orbit-outer) * 2);
    border: 1.5px dashed rgba(36, 91, 219, .28);
    border-radius: 50%;
}
.sb-home-ring--inner {
    width: calc(var(--orbit-inner) * 2);
    height: calc(var(--orbit-inner) * 2);
    border: 1px solid rgba(36, 91, 219, .14);
}
.sb-home-dot,
.sb-home-satellite {
    position: absolute;
    top: 50%;
    left: 50%;
    border-radius: 50%;
    animation: sbHomeOrbit 26s linear infinite reverse;
}
.sb-home-dot {
    --radius: var(--orbit-inner);
    width: 9px;
    height: 9px;
    margin: -4.5px 0 0 -4.5px;
    background: var(--sb-home-brand);
}
.sb-home-dot-1 { transform: rotate(0deg) translateX(var(--radius)) rotate(0deg); }
.sb-home-dot-2 { transform: rotate(120deg) translateX(var(--radius)) rotate(-120deg); animation-delay: -8.66s; background: #7367a8; }
.sb-home-dot-3 { transform: rotate(240deg) translateX(var(--radius)) rotate(-240deg); animation-delay: -17.33s; background: #0e7490; }
.sb-home-cube {
    position: relative;
    width: 118px;
    height: 118px;
    --half: 59px;
    transform-style: preserve-3d;
    animation: sbHomeSpin 17s linear infinite;
}
.sb-home-face {
    position: absolute;
    inset: 0;
    border: 1.5px solid rgba(36, 91, 219, .78);
    background: rgba(36, 91, 219, .09);
    box-shadow: inset 0 0 22px rgba(36, 91, 219, .16);
}
.sb-home-face-front { transform: translateZ(var(--half)); }
.sb-home-face-back { transform: rotateY(180deg) translateZ(var(--half)); }
.sb-home-face-right { transform: rotateY(90deg) translateZ(var(--half)); }
.sb-home-face-left { transform: rotateY(-90deg) translateZ(var(--half)); }
.sb-home-face-top { transform: rotateX(90deg) translateZ(var(--half)); }
.sb-home-face-bottom { transform: rotateX(-90deg) translateZ(var(--half)); }
.sb-home-satellite {
    --radius: var(--orbit-outer);
    width: 46px;
    height: 46px;
    margin: -23px 0 0 -23px;
    display: grid;
    place-items: center;
    background: #fff;
    border: 1px solid #dce3ee;
    box-shadow: 0 12px 28px rgba(23, 32, 51, .12);
    color: var(--sb-home-brand);
    font-size: .95rem;
    z-index: 2;
    animation: sbHomeOrbit 48s linear infinite;
}
.sb-home-satellite-1 { transform: rotate(0deg) translateX(var(--radius)) rotate(0deg); animation-delay: 0s; }
.sb-home-satellite-2 { transform: rotate(60deg) translateX(var(--radius)) rotate(-60deg); animation-delay: -8s; }
.sb-home-satellite-3 { transform: rotate(120deg) translateX(var(--radius)) rotate(-120deg); animation-delay: -16s; }
.sb-home-satellite-4 { transform: rotate(180deg) translateX(var(--radius)) rotate(-180deg); animation-delay: -24s; }
.sb-home-satellite-5 { transform: rotate(240deg) translateX(var(--radius)) rotate(-240deg); animation-delay: -32s; }
.sb-home-satellite-6 { transform: rotate(300deg) translateX(var(--radius)) rotate(-300deg); animation-delay: -40s; }
.sb-home-satellite--products i { color: #b66a50; }
.sb-home-satellite--inventory i { color: #294a73; }
.sb-home-satellite--customers i { color: #7367a8; }
.sb-home-satellite--analytics i { color: #0e7490; }
.sb-home-satellite--forecast i { color: #c28a32; }
.sb-home-particles { position: absolute; inset: 0; pointer-events: none; }
.sb-home-particle {
    position: absolute;
    bottom: 14%;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--sb-home-brand);
    opacity: 0;
    animation: sbHomeRise 6s ease-in-out infinite;
}
.sb-home-particle:nth-child(1) { left: 22%; animation-delay: 0s; }
.sb-home-particle:nth-child(2) { left: 34%; animation-delay: 1.4s; background: #7367a8; }
.sb-home-particle:nth-child(3) { left: 48%; animation-delay: 2.7s; width: 5px; height: 5px; }
.sb-home-particle:nth-child(4) { left: 60%; animation-delay: .8s; background: #0e7490; }
.sb-home-particle:nth-child(5) { left: 72%; animation-delay: 3.4s; width: 4px; height: 4px; }
.sb-home-particle:nth-child(6) { left: 80%; animation-delay: 2s; background: #b66a50; }
.sb-home-particle:nth-child(7) { left: 28%; animation-delay: 4.1s; width: 5px; height: 5px; background: #294a73; }

@media (max-width: 980px) {
    .sb-home { max-width: 100%; }
    .sb-home-hero { min-height: 0; gap: 30px; }
    .sb-home-main { flex-direction: column-reverse; align-items: flex-start; gap: 26px; }
    .sb-home-scene { align-self: center; }
}
@media (max-width: 640px) {
    .sb-home { padding: 14px 4px 26px; }
    .sb-home-scene { width: min(80vw, 310px); --orbit-outer: clamp(94px, 27vw, 118px); }
    .sb-home-satellite { width: 40px; height: 40px; margin: -20px 0 0 -20px; font-size: .84rem; }
    .sb-home-cube { width: 86px; height: 86px; --half: 43px; }
    .sb-home-type { max-width: calc(100vw - 86px); font-size: .92rem; }
}
@media (prefers-reduced-motion: reduce) {
    .sb-home-copy, .sb-home-scene, .sb-home-quote { animation: none; }
    .sb-home-cube { animation: none; transform: rotateX(-22deg) rotateY(-32deg); }
    .sb-home-satellite, .sb-home-dot, .sb-home-glow { animation: none; }
    .sb-home-particle { animation: none; opacity: 0; }
    .sb-home-type-line { animation: none !important; visibility: visible; width: auto; border-right-width: .1em; }
    .sb-home-type-line:nth-child(n + 2) { display: none; }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_home(username: str | None) -> None:
    now = datetime.now()
    name = html.escape(_display_name(username), quote=True)
    typing = _typing_block(HOME_MESSAGES)
    content = _compact(
        f"""
        <main class="sb-home">
            <section class="sb-home-hero">
                <div class="sb-home-main">
                    <div class="sb-home-copy">
                        <p class="sb-home-date">{_date_label(now)}</p>
                        <h1 class="sb-home-title">{_greeting(now)}, <span>{name}</span></h1>
                        <div class="sb-home-typeline">
                            <span class="sb-home-prompt">&gt;</span>
                            {typing}
                        </div>
                    </div>
                    {_scene()}
                </div>
                <p class="sb-home-quote">“Cada venta deja una señal; entenderla es el primer paso para crecer.”</p>
            </section>
        </main>
        """
    )
    _styles()
    st.markdown(content, unsafe_allow_html=True)
