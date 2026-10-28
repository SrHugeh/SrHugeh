"""Transforma o arco-iris do gerador 3D numa onda verde-agua."""
import colorsys, re, sys

path = sys.argv[1]
svg = open(path, encoding="utf-8").read()

DARK = {"top": 0, "left": 0.5, "right": 1}
LIGHT = [0.12, 0.28, 0.40, 0.52, 0.64]   # mesmo que contribLightness
# (posicao %, matiz, saturacao, ganho de luz) -> a onda passa e "acende"
STOPS = [(0, 172, .70, 0), (35, 168, .75, 0), (50, 182, .90, .22), (65, 168, .75, 0), (100, 172, .70, 0)]

def color(h, s, l, k):
    r, g, b = colorsys.hls_to_rgb(h / 360, min(l, .92), s)
    f = 0.7 ** k
    return "#%02x%02x%02x" % tuple(round(max(0, min(1, c * f)) * 255) for c in (r, g, b))

def frames(m):
    lvl, face = int(m.group(1)), m.group(2)
    base = LIGHT[lvl]
    boost = 0.35 if lvl == 0 else 1
    body = "".join(f"{p}%{{fill:{color(h, s * (0.5 if lvl == 0 else 1), base + g * boost, DARK[face])}}}" for p, h, s, g in STOPS)
    return f"@keyframes rb-l{lvl}-{face}{{{body}}}"

svg = re.sub(r"@keyframes rb-l(\d)-(top|left|right)\{.*?\}\}", frames, svg)
svg = svg.replace('font-family: "Ubuntu", "Helvetica", "Arial", sans-serif;',
                  "font-family: 'JetBrains Mono','Fira Code',Menlo,Consolas,'DejaVu Sans Mono',monospace;")

overlay = (
    '<defs><pattern id="aq-scan" width="4" height="4" patternUnits="userSpaceOnUse">'
    '<rect width="4" height="2" fill="#000" opacity=".22"/></pattern>'
    '<radialGradient id="aq-vig" cx="50%" cy="45%" r="75%">'
    '<stop offset="55%" stop-color="#000" stop-opacity="0"/>'
    '<stop offset="100%" stop-color="#000" stop-opacity=".6"/></radialGradient>'
    '<linearGradient id="aq-sweep" x1="0" x2="1"><stop offset="0" stop-color="#3ee6c4" stop-opacity="0"/>'
    '<stop offset=".5" stop-color="#3ee6c4" stop-opacity=".08"/><stop offset="1" stop-color="#3ee6c4" stop-opacity="0"/></linearGradient></defs>'
    '<rect x="-400" y="0" width="400" height="100%" fill="url(#aq-sweep)" pointer-events="none">'
    '<animate attributeName="x" from="-400" to="1280" dur="7s" repeatCount="indefinite"/></rect>'
    '<rect width="100%" height="100%" fill="url(#aq-scan)" pointer-events="none"/>'
    '<rect width="100%" height="100%" fill="url(#aq-vig)" pointer-events="none"/>'
)
# pizza de linguagens nos tons verde-agua (mesma ordem, maior primeiro)
SHADES = ["#3ee6c4", "#a7f3e4", "#22a88f", "#7fd8c6", "#13705f", "#5fbfae", "#0f5a50", "#cdf7ee"]
seen = []
for c in re.findall(r'fill="(#[0-9a-fA-F]{6})"', svg):
    if c not in seen:
        seen.append(c)
for i, c in enumerate(seen):
    new = "#1d3b39" if c.lower() == "#444444" else SHADES[i % len(SHADES)]
    svg = svg.replace(f'fill="{c}"', f'fill="{new}"').replace(f"fill: {c};", f"fill: {new};")

svg = svg[: svg.rfind("</svg>")] + overlay + "</svg>"
open(path, "w", encoding="utf-8").write(svg)
print("ok:", path)
