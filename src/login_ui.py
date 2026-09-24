from __future__ import annotations

import base64
import json
from pathlib import Path

import streamlit as st


_ASSETS = Path(__file__).resolve().parents[1] / "assets"
_BREAD = _ASSETS / "bread-svgrepo-com.svg"
_CROISSANT = _ASSETS / "croissant-bread-svgrepo-com.svg"


_LOGIN_PAGE_CSS = """
<style>
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
footer { display: none !important; }

.stApp {
    color: #172033;
    background:
        radial-gradient(ellipse at 86% 88%, rgba(36, 91, 219, .045), transparent 42%),
        linear-gradient(118deg, #fbfcfe 0%, #ffffff 52%, #f7f9fc 100%);
}
section[data-testid="stMain"] {
    min-height: 100vh;
    position: relative;
    overflow: hidden;
}
section[data-testid="stMain"]::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background-image:
        linear-gradient(rgba(23, 32, 51, .025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(23, 32, 51, .025) 1px, transparent 1px);
    background-size: 76px 76px;
}
[data-testid="stMainBlockContainer"],
section.main > .block-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    min-height: 100vh;
    position: relative;
    z-index: 1;
}

@media (min-width: 901px) {
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"],
    section.main > .block-container > [data-testid="stVerticalBlock"] {
        min-height: 100vh;
        padding: clamp(40px, 6vh, 80px) clamp(32px, 5vw, 96px)
                 clamp(40px, 6vh, 80px) calc(54vw + clamp(30px, 4vw, 76px)) !important;
        justify-content: center;
        gap: 0 !important;
    }
}

.stForm,
[data-testid="stForm"] {
    max-width: 440px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: clamp(30px, 4vw, 42px) !important;
    position: relative !important;
    overflow: hidden !important;
    background: rgba(255, 255, 255, .96) !important;
    border: 1px solid rgba(23, 32, 51, .11) !important;
    border-radius: 12px !important;
    box-shadow: 0 24px 64px rgba(23, 32, 51, .09), 0 2px 5px rgba(23, 32, 51, .04) !important;
    backdrop-filter: blur(14px);
}
.stForm h1,
[data-testid="stForm"] h1 {
    margin: 0 0 7px !important;
    color: #172033 !important;
    text-align: center !important;
    font-size: 1.8rem !important;
    font-weight: 650 !important;
    line-height: 1.15 !important;
    letter-spacing: -.025em !important;
}
.login-subtitle {
    margin: 0 0 28px !important;
    color: #6b778c !important;
    text-align: center !important;
    font-size: .92rem !important;
    line-height: 1.5 !important;
}
[data-testid="stForm"] label p {
    color: #334155 !important;
    font-size: .82rem !important;
    font-weight: 650 !important;
}
[data-testid="stForm"] [data-testid="stTextInput"] { margin-bottom: 14px !important; }
[data-testid="stForm"] [data-testid="stTextInput"]
    :is([data-baseweb="input"], [data-testid="stTextInputRootElement"]) {
    min-height: 44px !important;
    background: #f7f9fc !important;
    border: 1px solid #dce3ee !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    transition: border-color .18s ease, box-shadow .18s ease, background .18s ease;
}
[data-testid="stForm"] [data-testid="stTextInput"]
    :is([data-baseweb="input"], [data-testid="stTextInputRootElement"]):hover {
    border-color: #c4cfdf !important;
    background: #fff !important;
}
[data-testid="stForm"] [data-testid="stTextInput"]
    :is([data-baseweb="input"], [data-testid="stTextInputRootElement"]):focus-within {
    border-color: #245bdb !important;
    background: #fff !important;
    box-shadow: 0 0 0 3px rgba(36, 91, 219, .13) !important;
}
[data-testid="stForm"] [data-testid="stTextInput"]
    :is([data-baseweb="input"], [data-testid="stTextInputRootElement"]) > div,
[data-testid="stForm"] [data-testid="stTextInput"] [data-baseweb="base-input"] {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}
[data-testid="stForm"] [data-testid="stTextInput"] input {
    height: 42px !important;
    padding: 0 12px !important;
    color: #172033 !important;
    font-size: .94rem !important;
}
[data-testid="stForm"] [data-testid="stTextInput"] input::placeholder {
    color: #9aa5b5 !important;
    opacity: 1 !important;
}
[data-testid="stForm"] [data-testid="stFormSubmitButton"] { margin-top: 17px !important; }
[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {
    min-height: 46px !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    box-shadow: 0 9px 22px rgba(36, 91, 219, .18) !important;
}
.login-footer {
    max-width: 440px;
    margin: 20px auto 0;
    color: #7b8798;
    text-align: center;
    font-size: .76rem;
    letter-spacing: .025em;
}

/* En escritorio la animación (st.iframe) ocupa fija la mitad izquierda. */
@media (min-width: 901px) {
    div[data-testid="stElementContainer"]:has(iframe.stIFrame[title="st.iframe"]) {
        height: 0 !important;
        min-height: 0 !important;
        max-height: 0 !important;
        flex: 0 0 0 !important;
        margin: 0 !important;
        overflow: visible !important;
    }
    iframe.stIFrame[title="st.iframe"] {
        position: fixed !important;
        inset: 0 auto 0 0 !important;
        width: 54vw !important;
        height: 100vh !important;
        z-index: 10 !important;
        display: block !important;
        border: 0 !important;
        background: transparent !important;
    }
}

@media (max-width: 900px) {
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"],
    section.main > .block-container > [data-testid="stVerticalBlock"] {
        min-height: 100vh;
        padding: 22px 20px 48px !important;
        justify-content: center;
        gap: 0 !important;
    }
    div[data-testid="stElementContainer"]:has(iframe.stIFrame[title="st.iframe"]) {
        display: none !important;
    }
    .stForm,
    [data-testid="stForm"] {
        padding: 30px 24px !important;
        box-shadow: 0 16px 44px rgba(23, 32, 51, .08) !important;
    }
}
</style>
"""


_ANIMATION_HTML = r"""
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* { box-sizing: border-box; }
html, body {
    width: 100%;
    height: 100%;
    margin: 0;
    overflow: hidden;
    background: transparent;
    font-family: "Space Grotesk", "Segoe UI", sans-serif;
}
.bread-panel {
    position: relative;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background:
        radial-gradient(circle at 50% 48%, rgba(36, 91, 219, .08), transparent 34%),
        radial-gradient(circle at 42% 55%, rgba(234, 173, 106, .10), transparent 38%);
}
.bread-panel::before {
    content: "";
    position: absolute;
    inset: clamp(32px, 5vw, 64px);
    border: 1px solid rgba(23, 32, 51, .055);
    border-radius: 14px;
    pointer-events: none;
    -webkit-mask-image: linear-gradient(125deg, #000 0%, #000 55%, transparent 88%);
    mask-image: linear-gradient(125deg, #000 0%, #000 55%, transparent 88%);
}
.bread-panel::after {
    content: "";
    position: absolute;
    width: min(70vw, 650px);
    aspect-ratio: 1;
    left: 50%;
    top: 49%;
    transform: translate(-50%, -50%);
    border: 1px dashed rgba(36, 91, 219, .12);
    border-radius: 50%;
    pointer-events: none;
}
.signal-ring,
.signal-ring::before,
.signal-ring::after {
    position: absolute;
    left: 50%;
    top: 49%;
    transform: translate(-50%, -50%);
    border: 1px solid rgba(36, 91, 219, .08);
    border-radius: 50%;
    content: "";
    pointer-events: none;
}
.signal-ring { width: min(54vw, 500px); aspect-ratio: 1; }
.signal-ring::before { width: 76%; aspect-ratio: 1; }
.signal-ring::after { width: 124%; aspect-ratio: 1; border-style: dotted; }
.bread-fallback {
    position: absolute;
    left: 50%;
    top: 49%;
    width: min(44vw, 410px);
    height: min(44vw, 410px);
    object-fit: contain;
    transform: translate(-50%, -50%);
    filter: drop-shadow(0 24px 30px rgba(23, 32, 51, .12));
    opacity: .9;
    transition: opacity .35s ease;
}
.bread-panel.is-ready .bread-fallback { opacity: 0; }
#breadParticles {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 2;
}
.cursor-glow {
    position: absolute;
    width: 360px;
    height: 360px;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    background: radial-gradient(circle, rgba(36, 91, 219, .08), transparent 66%);
    opacity: 0;
    pointer-events: none;
    transition: opacity .22s ease;
}
.cursor-glow.active { opacity: 1; }
@media (prefers-reduced-motion: reduce) {
    .cursor-glow { display: none; }
}
</style>
</head>
<body>
<main class="bread-panel" id="breadPanel" aria-hidden="true">
    <div class="signal-ring"></div>
    <img class="bread-fallback" src=__BREAD_SRC__ alt="">
    <div class="cursor-glow" id="cursorGlow"></div>
    <canvas id="breadParticles"></canvas>
</main>

<script>
(() => {
    const BREAD_SRC = __BREAD_SRC__;
    const CROISSANT_SRC = __CROISSANT_SRC__;
    const panel = document.getElementById("breadPanel");
    const canvas = document.getElementById("breadParticles");
    const ctx = canvas.getContext("2d", { alpha: true });
    const cursorGlow = document.getElementById("cursorGlow");
    const mask = document.createElement("canvas");
    const maskCtx = mask.getContext("2d", { willReadFrequently: true });
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const particles = [];
    const ambient = [];
    const pointer = { x: 0, y: 0, active: false };
    let width = 0;
    let height = 0;
    let dpr = 1;
    let breadImage = null;
    let croissantImage = null;
    let shapes = [[], []];
    let activeShape = 0;
    let frame = 0;
    let resizeTimer = 0;

    function randomEdge() {
        const edge = Math.floor(Math.random() * 4);
        if (edge === 0) return { x: -30, y: Math.random() * height };
        if (edge === 1) return { x: width + 30, y: Math.random() * height };
        if (edge === 2) return { x: Math.random() * width, y: -30 };
        return { x: Math.random() * width, y: height + 30 };
    }

    function configureCanvas() {
        const rect = canvas.getBoundingClientRect();
        width = Math.max(1, Math.round(rect.width));
        height = Math.max(1, Math.round(rect.height));
        dpr = Math.min(1.5, window.devicePixelRatio || 1);
        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round(height * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function buildAmbient() {
        ambient.length = 0;
        const count = Math.max(34, Math.min(76, Math.round((width * height) / 11000)));
        for (let i = 0; i < count; i += 1) {
            ambient.push({
                x: Math.random() * width,
                y: Math.random() * height,
                r: .6 + Math.random() * 1.5,
                vy: .06 + Math.random() * .16,
                phase: Math.random() * Math.PI * 2,
                color: Math.random() > .68 ? "36,91,219" : "209,145,82"
            });
        }
    }

    function sampleShape(sourceImage, isCroissant = false) {
        mask.width = width;
        mask.height = height;
        maskCtx.clearRect(0, 0, width, height);

        const size = isCroissant
            ? Math.min(width * .66, height * .67, 550)
            : Math.min(width * .58, height * .62, 500);
        const left = (width - size) / 2;
        const top = height * .49 - size / 2;
        maskCtx.drawImage(sourceImage, left, top, size, size);
        const data = maskCtx.getImageData(0, 0, width, height).data;
        const step = width < 620 ? 6 : 5;
        const points = [];

        for (let y = 0; y < height; y += step) {
            for (let x = 0; x < width; x += step) {
                const offset = (y * width + x) * 4;
                if (data[offset + 3] < 82) continue;
                if (Math.random() > .88) continue;

                let red = data[offset];
                let green = data[offset + 1];
                let blue = data[offset + 2];
                if (isCroissant) {
                    const light = (x + y) % 29;
                    const navyAccent = ((x * 7 + y * 11) % 101) < 9;
                    if (navyAccent) {
                        [red, green, blue] = [0, 67, 100];
                    } else if (light < 9) {
                        [red, green, blue] = [255, 198, 97];
                    } else if (light < 18) {
                        [red, green, blue] = [234, 173, 106];
                    } else {
                        [red, green, blue] = [209, 145, 82];
                    }
                }

                points.push({
                    x: x + (Math.random() - .5) * 1.8,
                    y: y + (Math.random() - .5) * 1.8,
                    red,
                    green,
                    blue
                });
            }
        }
        return points;
    }

    function applyShape(index) {
        const target = shapes[index];
        if (!target.length) return;
        activeShape = index;
        panel.dataset.shape = index === 0 ? "bread" : "croissant";
        for (let i = 0; i < particles.length; i += 1) {
            const point = target[(i + index * 131) % target.length];
            const particle = particles[i];
            particle.homeX = point.x;
            particle.homeY = point.y;
            particle.targetRed = point.red;
            particle.targetGreen = point.green;
            particle.targetBlue = point.blue;
        }
    }

    function buildShapes() {
        if (!breadImage || !croissantImage) return;
        shapes = [
            sampleShape(breadImage, false),
            sampleShape(croissantImage, true)
        ];
        const initial = shapes[activeShape];
        const count = Math.max(shapes[0].length, shapes[1].length);
        particles.length = 0;
        panel.dataset.shape = activeShape === 0 ? "bread" : "croissant";

        for (let i = 0; i < count; i += 1) {
            const point = initial[i % initial.length];
            const start = reducedMotion ? { x: point.x, y: point.y } : randomEdge();
            particles.push({
                x: start.x,
                y: start.y,
                vx: 0,
                vy: 0,
                homeX: point.x,
                homeY: point.y,
                radius: 1.05 + Math.random() * 1.05,
                alpha: .66 + Math.random() * .3,
                phase: Math.random() * Math.PI * 2,
                delay: Math.random() * 90,
                red: point.red,
                green: point.green,
                blue: point.blue,
                targetRed: point.red,
                targetGreen: point.green,
                targetBlue: point.blue
            });
        }
        panel.classList.add("is-ready");
    }

    function drawAmbient(time) {
        for (const dot of ambient) {
            if (!reducedMotion) {
                dot.y -= dot.vy;
                if (dot.y < -8) { dot.y = height + 8; dot.x = Math.random() * width; }
            }
            const alpha = .10 + (Math.sin(time * .0007 + dot.phase) + 1) * .05;
            ctx.fillStyle = `rgba(${dot.color},${alpha})`;
            ctx.beginPath();
            ctx.arc(dot.x, dot.y, dot.r, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function render(time = 0) {
        frame += 1;
        ctx.clearRect(0, 0, width, height);
        drawAmbient(time);

        for (const particle of particles) {
            if (!reducedMotion && frame > particle.delay) {
                const driftX = Math.sin(time * .00075 + particle.phase) * 1.5;
                const driftY = Math.cos(time * .00062 + particle.phase) * 1.35;
                particle.vx += (particle.homeX + driftX - particle.x) * .052;
                particle.vy += (particle.homeY + driftY - particle.y) * .052;

                if (pointer.active) {
                    const dx = particle.x - pointer.x;
                    const dy = particle.y - pointer.y;
                    const distanceSq = dx * dx + dy * dy;
                    const radius = 128;
                    if (distanceSq > .01 && distanceSq < radius * radius) {
                        const distance = Math.sqrt(distanceSq);
                        const force = (1 - distance / radius) * .72;
                        particle.vx += (dx / distance) * force;
                        particle.vy += (dy / distance) * force;
                    }
                }

                particle.vx *= .83;
                particle.vy *= .83;
                particle.x += particle.vx;
                particle.y += particle.vy;
            }

            particle.red += (particle.targetRed - particle.red) * .04;
            particle.green += (particle.targetGreen - particle.green) * .04;
            particle.blue += (particle.targetBlue - particle.blue) * .04;
            ctx.globalAlpha = particle.alpha;
            ctx.fillStyle = `rgb(${particle.red | 0},${particle.green | 0},${particle.blue | 0})`;
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.globalAlpha = 1;

        if (!reducedMotion) requestAnimationFrame(render);
    }

    function rebuild() {
        configureCanvas();
        buildAmbient();
        buildShapes();
        if (reducedMotion) render(0);
    }

    canvas.addEventListener("pointermove", (event) => {
        const rect = canvas.getBoundingClientRect();
        pointer.x = event.clientX - rect.left;
        pointer.y = event.clientY - rect.top;
        pointer.active = true;
        cursorGlow.style.left = `${pointer.x}px`;
        cursorGlow.style.top = `${pointer.y}px`;
        cursorGlow.classList.add("active");
    }, { passive: true });
    canvas.addEventListener("pointerleave", () => {
        pointer.active = false;
        cursorGlow.classList.remove("active");
    }, { passive: true });
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(rebuild, 140);
    });

    function loadImage(source) {
        return new Promise((resolve, reject) => {
            const loader = new Image();
            loader.onload = () => resolve(loader);
            loader.onerror = reject;
            loader.src = source;
        });
    }

    Promise.all([loadImage(BREAD_SRC), loadImage(CROISSANT_SRC)]).then(([bread, croissant]) => {
        breadImage = bread;
        croissantImage = croissant;
        rebuild();
        if (!reducedMotion) requestAnimationFrame(render);
        if (!reducedMotion) {
            window.setTimeout(() => {
                applyShape(1);
                window.setInterval(
                    () => applyShape(activeShape === 0 ? 1 : 0),
                    7200
                );
            }, 5200);
        }
    });
})();
</script>
</body>
</html>
"""


@st.cache_data(show_spinner=False)
def _asset_data_uri(path: Path) -> str:
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError:
        return ""
    return f"data:image/svg+xml;base64,{encoded}"


def render_login_styles() -> None:
    st.markdown(_LOGIN_PAGE_CSS, unsafe_allow_html=True)


def render_bread_animation() -> None:
    # Las partículas se forman muestreando los píxeles de los dos SVG.
    bread_source = json.dumps(_asset_data_uri(_BREAD))
    croissant_source = json.dumps(_asset_data_uri(_CROISSANT))
    st.iframe(
        _ANIMATION_HTML.replace("__BREAD_SRC__", bread_source).replace(
            "__CROISSANT_SRC__", croissant_source
        ),
        height=360,
        tab_index=-1,
    )
