#!/usr/bin/env python3
"""Generates the SVG assets for the GitHub profile README (hero banner, app cards, footer)."""
import base64
import json
import pathlib
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
OUT.mkdir(exist_ok=True)
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

STORE = json.loads((ROOT / "store.json").read_text())


def live(app_id):
    d = STORE.get(app_id)
    return f"v{d['version']} · updated {d['updated']}" if d else None


THEMES = {
    "dark": dict(card="#161b22", border="#30363d", text="#e6edf3", muted="#9198a1", chip="#21262d",
                 chip_text="#c9d1d9", hero_a="#0b1220", hero_b="#132a3e", hero_c="#1d1b3a",
                 hero_text="#f0f6fc", hero_muted="#a9b8c8", pill="#ffffff14", pill_border="#ffffff2e",
                 phone="#0d1117", phone_edge="#3d444d", glow=0.55),
    "light": dict(card="#ffffff", border="#d1d9e0", text="#1f2328", muted="#59636e", chip="#f0f3f6",
                  chip_text="#3d444d", hero_a="#e9f7f5", hero_b="#e8f0fe", hero_c="#f3ecff",
                  hero_text="#101828", hero_muted="#475467", pill="#ffffffb3", pill_border="#10182822",
                  phone="#101828", phone_edge="#344054", glow=0.35),
}


def data_uri(name):
    raw = (ROOT / "icons" / name).read_bytes()
    mime = "image/jpeg" if raw[:3] == b"\xff\xd8\xff" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def drawn_icon(kind, x, y, s):
    """Vector icons for apps that have no store icon."""
    r = s * 0.225
    if kind == "shiftskin":
        return f'''<g transform="translate({x},{y})">
  <rect width="{s}" height="{s}" rx="{r}" fill="url(#g-amber)"/>
  <circle cx="{s*0.5}" cy="{s*0.5}" r="{s*0.17}" fill="#fff"/>
  <g stroke="#fff" stroke-width="{s*0.06}" stroke-linecap="round">
    {''.join(f'<line x1="{s*0.5}" y1="{s*0.2}" x2="{s*0.5}" y2="{s*0.13}" transform="rotate({a} {s*0.5} {s*0.5})"/>' for a in range(0, 360, 45))}
  </g></g>'''
    return f'''<g transform="translate({x},{y})">
  <rect width="{s}" height="{s}" rx="{r}" fill="url(#g-blue)"/>
  <path d="M{s*0.5} {s*0.2} C{s*0.5} {s*0.2} {s*0.27} {s*0.47} {s*0.27} {s*0.6} a{s*0.23} {s*0.23} 0 0 0 {s*0.46} 0 C{s*0.73} {s*0.47} {s*0.5} {s*0.2} {s*0.5} {s*0.2}Z" fill="#fff"/>
  <path d="M{s*0.4} {s*0.62} a{s*0.1} {s*0.1} 0 0 0 {s*0.1} {s*0.1}" fill="none" stroke="#38bdf8" stroke-width="{s*0.045}" stroke-linecap="round"/></g>'''


COMMON_DEFS = '''<linearGradient id="g-amber" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fbbf24"/><stop offset="1" stop-color="#f97316"/></linearGradient>
<linearGradient id="g-blue" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#38bdf8"/><stop offset="1" stop-color="#2563eb"/></linearGradient>'''

APPS = [
    dict(id="fisiochecks", name="FisioChecks", icon="fisiochecks.png", accent="#2dd4bf",
         pitch=["Clinical calculator for respiratory", "physio and ICU, with 23 calculations."],
         chips=["KMP", "Compose", "SwiftUI"], platforms=["Android", "iOS"], meta="Solo build · 400+ commits"),
    dict(id="peaceful-dreams", name="Peaceful Dreams", icon="peaceful.png", accent="#8fb3d9",
         pitch=["Relaxing-sounds player with a 100%", "shared Compose Multiplatform UI."],
         chips=["Compose Multiplatform", "Room KMP", "Media3"], platforms=["Android", "iOS"], meta="One codebase, two stores"),
    dict(id="osiris", name="Osiris", icon="osiris.png", accent="#3fb950",
         pitch=["Diagnoses plant diseases from a", "photo, powered by Google Gemini."],
         chips=["Compose", "Hilt", "Gemini", "Play Billing"], platforms=["Android"], meta="1K+ downloads"),
    dict(id="my-daily-humour", name="My Daily Humour", icon="humour.png", accent="#fb7185",
         pitch=["Mood tracker to log how you feel,", "day after day."],
         chips=["Compose", "Hilt", "WorkManager"], platforms=["Android"], meta="5K+ downloads"),
    dict(id="shiftskin", name="ShiftSkin", icon=None, accent="#fbbf24",
         pitch=["AI skin analysis for people who work", "outdoors. Built solo in one week."],
         chips=["Compose Multiplatform", "YouCam AI"], platforms=["Android", "iOS"], meta="Hackathon · 284 tests"),
    dict(id="waterly", name="Waterly", icon=None, accent="#38bdf8",
         pitch=["Water-quality and biodiversity", "companion app."],
         chips=["Compose", "Hilt", "Google Maps"], platforms=["Android"], meta="Built in 2023"),
]


def chip_row(items, x, y, t, size=11, pad=9, h=22, fill=None, color=None, stroke=None):
    out, cx = [], x
    for label in items:
        w = round(len(label) * size * 0.58 + pad * 2)
        out.append(f'<rect x="{cx}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{fill or t["chip"]}"'
                   + (f' stroke="{stroke}"' if stroke else "") + "/>")
        out.append(f'<text x="{cx + w/2}" y="{y + h/2 + size*0.36}" font-size="{size}" font-weight="600" '
                   f'text-anchor="middle" fill="{color or t["chip_text"]}">{escape(label)}</text>')
        cx += w + 6
    return "\n".join(out), cx


def live_tag(app, t, W):
    txt = live(app["id"])
    if not txt:
        return ""
    return (f'<circle cx="{W-20-len(txt)*5.75-10}" cy="144.5" r="3" fill="#3fb950"><animate attributeName="opacity" values="1;0.35;1" dur="2.4s" repeatCount="indefinite"/></circle>'
            f'<text x="{W-20}" y="148" font-size="10.5" font-weight="600" text-anchor="end" fill="{t["muted"]}">{escape(txt)}</text>')


def card(app, theme):
    t = THEMES[theme]
    W, H = 420, 196
    a = app["accent"]
    icon = (f'<image href="{data_uri(app["icon"])}" x="20" y="22" width="72" height="72" clip-path="url(#ic)" preserveAspectRatio="xMidYMid slice"/>'
            f'<rect x="20" y="22" width="72" height="72" rx="17" fill="none" stroke="{t["border"]}"/>'
            if app["icon"] else drawn_icon(app["id"], 20, 22, 72))
    chips, _ = chip_row(app["chips"], 20, 114, t)
    plats, _ = chip_row(app["platforms"], 20, 154, t, size=10.5, h=20, pad=8, fill=a + "22", color=a if theme == "dark" else t["text"], stroke=a + "66")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" role="img" aria-label="{escape(app['name'])}: {escape(' '.join(app['pitch']))}">
<defs>
{COMMON_DEFS}
<clipPath id="ic"><rect x="20" y="22" width="72" height="72" rx="17"/></clipPath>
<clipPath id="cc"><rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14"/></clipPath>
<radialGradient id="gl" cx="1" cy="0" r="1"><stop offset="0" stop-color="{a}" stop-opacity="{0.22 if theme == 'dark' else 0.16}"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></linearGradient>
</defs>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{t['card']}" stroke="{t['border']}"/>
<g clip-path="url(#cc)">
<rect x="{W-260}" y="-10" width="270" height="200" fill="url(#gl)"/>
<rect x="0" y="0" width="{W}" height="3" fill="url(#bar)"/>
</g>
{icon}
<text x="108" y="48" font-size="19" font-weight="700" fill="{t['text']}">{escape(app['name'])}</text>
{live_tag(app, t, W)}
<text x="108" y="70" font-size="12.5" fill="{t['muted']}">{escape(app['pitch'][0])}</text>
<text x="108" y="87" font-size="12.5" fill="{t['muted']}">{escape(app['pitch'][1])}</text>
{chips}
{plats}
<text x="{W-20}" y="168" font-size="11.5" font-weight="600" text-anchor="end" fill="{t['muted']}">{escape(app['meta'])}</text>
</svg>'''


def phone(x, y, rot, icon, label, accent, t, delay, scale=1.0):
    w, h = 150, 300
    return f'''<g transform="translate({x},{y}) rotate({rot}) scale({scale})">
<g class="float" style="animation-delay:{delay}s">
<rect x="-6" y="6" width="{w+12}" height="{h+8}" rx="34" fill="#000" opacity="0.28" filter="url(#blur)"/>
<rect width="{w}" height="{h}" rx="30" fill="{t['phone']}" stroke="{t['phone_edge']}" stroke-width="2"/>
<rect x="7" y="7" width="{w-14}" height="{h-14}" rx="24" fill="url(#scr-{label})"/>
<rect x="{w/2-22}" y="15" width="44" height="12" rx="6" fill="{t['phone']}"/>
<image href="{icon}" x="{w/2-39}" y="88" width="78" height="78" clip-path="url(#pc)" preserveAspectRatio="xMidYMid slice"/>
<rect x="30" y="196" width="{w-60}" height="9" rx="4.5" fill="#fff" opacity="0.85"/>
<rect x="44" y="214" width="{w-88}" height="7" rx="3.5" fill="#fff" opacity="0.45"/>
<rect x="38" y="244" width="{w-76}" height="24" rx="12" fill="{accent}"/>
</g></g>'''


TAGLINES = ["I build mobile apps people can download today.", "From first sketch to the store, solo.",
            "One Kotlin core, native on Android and iOS.", "Spec-first, with AI agents on the team."]


def hero(theme):
    t = THEMES[theme]
    W, H = 1280, 400
    fc, pd, os_ = data_uri("fisiochecks.png"), data_uri("peaceful.png"), data_uri("osiris.png")
    pills, _ = chip_row(["7 apps on Google Play", "2 on the App Store", "Brasília, Brazil"], 72, 268, t,
                        size=15, pad=16, h=36, fill=t["pill"], color=t["hero_text"], stroke=t["pill_border"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" role="img" aria-label="Joaquim Gomes, Mobile Engineer: Android, iOS and Kotlin Multiplatform">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['hero_a']}"/><stop offset="0.55" stop-color="{t['hero_b']}"/><stop offset="1" stop-color="{t['hero_c']}"/></linearGradient>
<linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="#2dd4bf"/><stop offset="0.5" stop-color="#60a5fa"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>
<linearGradient id="scr-a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14532d"/><stop offset="1" stop-color="#166534"/></linearGradient>
<linearGradient id="scr-b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f2a2e"/><stop offset="1" stop-color="#115e59"/></linearGradient>
<linearGradient id="scr-c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1e293b"/><stop offset="1" stop-color="#3b5578"/></linearGradient>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>
<clipPath id="pc"><rect x="36" y="88" width="78" height="78" rx="18"/></clipPath>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
<pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{t['hero_text']}" opacity="0.07"/></pattern>
<style>
.float{{animation:float 7s ease-in-out infinite}}
.orb{{animation:drift 14s ease-in-out infinite alternate}}
.tg{{opacity:0;animation:tg 16s linear infinite}}
@keyframes tg{{0%{{opacity:0;transform:translateY(8px)}}3%{{opacity:1;transform:translateY(0)}}22%{{opacity:1;transform:translateY(0)}}25%{{opacity:0;transform:translateY(-8px)}}100%{{opacity:0}}}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-9px)}}}}
@keyframes drift{{from{{transform:translate(0,0)}}to{{transform:translate(40px,-24px)}}}}
@media (prefers-reduced-motion:reduce){{.float,.orb,.tg{{animation:none}}.tg:first-of-type{{opacity:1}}}}
</style>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<circle class="orb" cx="180" cy="60" r="170" fill="#2dd4bf" opacity="{t['glow']*0.5}" filter="url(#soft)"/>
<circle class="orb" cx="980" cy="360" r="200" fill="#8b5cf6" opacity="{t['glow']*0.6}" filter="url(#soft)" style="animation-delay:-5s"/>
<circle class="orb" cx="700" cy="20" r="130" fill="#3b82f6" opacity="{t['glow']*0.45}" filter="url(#soft)" style="animation-delay:-9s"/>
<rect width="{W}" height="{H}" fill="url(#dots)"/>
<text x="72" y="112" font-size="20" font-weight="600" letter-spacing="3" fill="{t['hero_muted']}">HI, I’M</text>
<text x="70" y="182" font-size="68" font-weight="800" letter-spacing="-1.5" fill="url(#name)">Joaquim Gomes</text>
{"".join(f'<text class="tg" style="animation-delay:{-((4 - i) % 4) * 4}s" x="72" y="226" font-size="24" font-weight="500" fill="{t["hero_text"]}">{escape(line)}</text>' for i, line in enumerate(TAGLINES))}
{pills}
<text x="72" y="346" font-size="17" fill="{t['hero_muted']}">Mobile Engineer  ·  Android  ·  iOS  ·  Kotlin Multiplatform</text>
{phone(820, 92, -9, os_, "a", "#4ade80", t, 0, 0.86).replace("#pc", "#pc")}
{phone(1068, 96, 9, pd, "c", "#93c5fd", t, -2.5, 0.86)}
{phone(928, 48, 0, fc, "b", "#2dd4bf", t, -4.5)}
</g>
</svg>'''


def footer(theme):
    t = THEMES[theme]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 70" width="1280" height="70" role="img" aria-label="">
<defs><linearGradient id="w" x1="0" x2="1"><stop offset="0" stop-color="#2dd4bf"/><stop offset="0.5" stop-color="#60a5fa"/><stop offset="1" stop-color="#a78bfa"/></linearGradient></defs>
<path d="M0 40 C 160 5, 320 70, 480 38 S 800 8, 960 36 S 1180 62, 1280 30" fill="none" stroke="url(#w)" stroke-width="3" stroke-linecap="round" opacity="0.9"/>
<path d="M0 52 C 180 22, 340 78, 520 48 S 820 24, 980 50 S 1190 70, 1280 44" fill="none" stroke="url(#w)" stroke-width="2" stroke-linecap="round" opacity="0.35"/>
</svg>'''


import re

def logo_path(name):
    f = ROOT / "logos" / f"{name}.svg"
    if not f.exists():
        return None
    m = re.search(r'<path d="([^"]+)"', f.read_text())
    return m.group(1) if m else None


STACK = [
    ("Android", "#3fb950", "android", [("Kotlin", "kotlin"), ("Jetpack Compose", "jetpackcompose"), ("Coroutines & Flow", None),
        ("Hilt", None), ("Koin", None), ("Room", None), ("WorkManager", None), ("CameraX", None), ("Material 3", None)]),
    ("iOS", "#60a5fa", "apple", [("Swift", "swift"), ("SwiftUI", None), ("Combine", None), ("async/await", None),
        ("Swift Charts", None), ("SwiftData", None), ("MapKit", None), ("XCTest", None)]),
    ("Multiplatform", "#a78bfa", "kotlin", [("Kotlin Multiplatform", "kotlin"), ("Compose Multiplatform", "jetpackcompose"),
        ("Ktor", "ktor"), ("SQLDelight", "sqlite"), ("Room KMP", None), ("SKIE", None), ("kotlinx.serialization", None)]),
    ("Platform", "#fbbf24", "firebase", [("Firebase", "firebase"), ("OAuth2 / PKCE", None), ("SignalR", None), ("BLE", None),
        ("GraphQL", "graphql"), ("Play Billing", "googleplay"), ("Sentry", "sentry")]),
    ("Quality & delivery", "#fb7185", "githubactions", [("GitHub Actions", "githubactions"), ("Paparazzi", None), ("Roborazzi", None),
        ("detekt", None), ("SwiftLint", None), ("SonarQube", "sonarqubeserver"), ("Gradle", "gradle"), ("Bitrise", "bitrise"), ("Bitbucket", "bitbucket")]),
    ("AI-assisted", "#2dd4bf", "claude", [("Claude Code", "claude"), ("Gemini", "googlegemini"), ("OpenSpec", None),
        ("Spec-driven development", None)]),
]


def stack(theme):
    t = THEMES[theme]
    W, LX, CX, CH, GAP, SIZE = 840, 24, 178, 28, 7, 12.5
    y, body = 18, []
    for label, accent, licon, items in STACK:
        ink = accent if theme == "dark" else t["text"]
        rows_start = y
        x = CX
        chips = []
        for name, logo in items:
            d = logo_path(logo) if logo else None
            w = round(len(name) * SIZE * 0.56 + 22 + (20 if d else 12))
            if x + w > W - LX:
                x, y = CX, y + CH + GAP
            chips.append(f'<rect x="{x}" y="{y}" width="{w}" height="{CH}" rx="{CH/2}" fill="{t["chip"]}" stroke="{t["border"]}"/>')
            if d:
                chips.append(f'<g transform="translate({x+11},{y+7}) scale({14/24})"><path d="{d}" fill="{ink}"/></g>')
                tx = x + 31
            else:
                chips.append(f'<circle cx="{x+13}" cy="{y+CH/2}" r="3" fill="{accent}"/>')
                tx = x + 23
            chips.append(f'<text x="{tx}" y="{y+CH/2+SIZE*0.36}" font-size="{SIZE}" font-weight="600" fill="{t["chip_text"]}">{escape(name)}</text>')
            x += w + GAP
        ld = logo_path(licon)
        mid = rows_start + CH / 2
        body.append(f'<rect x="{LX}" y="{rows_start}" width="30" height="{CH}" rx="8" fill="{accent}22" stroke="{accent}55"/>')
        if ld:
            body.append(f'<g transform="translate({LX+8},{rows_start+7}) scale({14/24})"><path d="{ld}" fill="{ink}"/></g>')
        body.append(f'<text x="{LX+40}" y="{mid+4.8}" font-size="13.5" font-weight="700" fill="{t["text"]}">{escape(label)}</text>')
        body.extend(chips)
        y += CH + 16
        body.append(f'<line x1="{LX}" y1="{y-8}" x2="{W-LX}" y2="{y-8}" stroke="{t["border"]}" opacity="0.6"/>')
    body.pop()
    H = y - 8 + 10
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" role="img" aria-label="Tech stack">
<defs><linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="#2dd4bf"/><stop offset="0.5" stop-color="#60a5fa"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>
<clipPath id="cc"><rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14"/></clipPath></defs>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{t['card']}" stroke="{t['border']}"/>
<g clip-path="url(#cc)"><rect width="{W}" height="3" fill="url(#bar)"/></g>
{chr(10).join(body)}
</svg>'''


for theme in THEMES:
    (OUT / f"hero-{theme}.svg").write_text(hero(theme), encoding="utf8")
    (OUT / f"stack-{theme}.svg").write_text(stack(theme), encoding="utf8")
    (OUT / f"footer-{theme}.svg").write_text(footer(theme), encoding="utf8")
    for app in APPS:
        (OUT / f"app-{app['id']}-{theme}.svg").write_text(card(app, theme), encoding="utf8")

for f in sorted(OUT.glob("*.svg")):
    print(f"{f.name:40} {f.stat().st_size/1024:7.1f} KB")


# ---------------------------------------------------------------- extra sections
GRAD = '<linearGradient id="tri" x1="0" x2="1"><stop offset="0" stop-color="#2dd4bf"/><stop offset="0.5" stop-color="#60a5fa"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>'


def shot_uri(i):
    return "data:image/jpeg;base64," + base64.b64encode((ROOT / "shots" / f"s{i}.jpg").read_bytes()).decode()


def frame(W, H, t, inner, extra_defs="", label=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" role="img" aria-label="{escape(label)}">
<defs>{GRAD}{COMMON_DEFS}<clipPath id="cc"><rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14"/></clipPath>{extra_defs}</defs>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{t['card']}" stroke="{t['border']}"/>
{inner}
</svg>'''


def spotlight(theme):
    t = THEMES[theme]
    W, H, a = 840, 352, "#2dd4bf"
    stats = [("23", "calculations"), ("~170", "test files"), ("57", "capability specs"), ("5-job", "CI pipeline")]
    tiles = []
    for i, (num, lab) in enumerate(stats):
        x, y = 28 + (i % 2) * 146, 182 + (i // 2) * 60
        tiles.append(f'<rect x="{x}" y="{y}" width="136" height="52" rx="10" fill="{t["chip"]}" stroke="{t["border"]}"/>'
                     f'<text x="{x+14}" y="{y+24}" font-size="19" font-weight="800" fill="url(#tri)">{num}</text>'
                     f'<text x="{x+14}" y="{y+41}" font-size="11" fill="{t["muted"]}">{lab}</text>')
    shots, defs = [], ""
    for k, i in enumerate([6, 1, 4]):
        x, y, w, h = 352 + k * 158, 34 + (0 if k == 1 else 14), 148, 264
        defs += f'<clipPath id="s{k}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/></clipPath>'
        shots.append(f'<g class="up" style="animation-delay:{-k*2.2}s"><rect x="{x-3}" y="{y+6}" width="{w+6}" height="{h}" rx="16" fill="#000" opacity="0.25" filter="url(#sh)"/>'
                     f'<image href="{shot_uri(i)}" x="{x}" y="{y}" width="{w}" height="{h}" clip-path="url(#s{k})" preserveAspectRatio="xMidYMid slice"/>'
                     f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="none" stroke="{a}" stroke-opacity="0.35"/></g>')
    defs += ('<filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>'
             f'<radialGradient id="gl" cx="0.72" cy="0.4" r="0.7"><stop offset="0" stop-color="{a}" stop-opacity="{0.2 if theme=="dark" else 0.14}"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>'
             '<clipPath id="ic"><rect x="28" y="30" width="60" height="60" rx="14"/></clipPath>'
             '<style>.up{animation:up 8s ease-in-out infinite}@keyframes up{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}@media (prefers-reduced-motion:reduce){.up{animation:none}}</style>')
    plats, _ = chip_row(["Android", "iOS"], 28, 312, t, size=10.5, h=20, pad=8, fill=a + "22", color=a if theme == "dark" else t["text"], stroke=a + "66")
    inner = f'''<g clip-path="url(#cc)"><rect width="{W}" height="{H}" fill="url(#gl)"/><rect width="{W}" height="3" fill="url(#tri)"/></g>
<image href="{data_uri("fisiochecks.png")}" x="28" y="30" width="60" height="60" clip-path="url(#ic)"/>
<rect x="102" y="32" width="74" height="19" rx="9.5" fill="{a}22" stroke="{a}66"/>
<text x="139" y="45.5" font-size="10" font-weight="700" letter-spacing="1.2" text-anchor="middle" fill="{a if theme=="dark" else t["text"]}">FLAGSHIP</text>
<circle cx="190" cy="41.5" r="3" fill="#3fb950"><animate attributeName="opacity" values="1;0.35;1" dur="2.4s" repeatCount="indefinite"/></circle>
<text x="199" y="45.5" font-size="10.5" font-weight="600" fill="{t['muted']}">{escape(live("fisiochecks"))}</text>
<text x="101" y="82" font-size="27" font-weight="800" letter-spacing="-0.5" fill="{t['text']}">FisioChecks</text>
<text x="28" y="116" font-size="13" fill="{t['muted']}">Clinical calculator for respiratory</text>
<text x="28" y="133" font-size="13" fill="{t['muted']}">physiotherapists and intensivists. Formulas</text>
<text x="28" y="150" font-size="13" fill="{t['muted']}">live once in shared Kotlin, with a native UI:</text>
<text x="28" y="167" font-size="13" fill="{t['muted']}">Compose on Android, SwiftUI on iOS.</text>
{''.join(tiles)}
{plats}
<text x="320" y="326" font-size="11.5" font-weight="600" text-anchor="end" fill="{t['muted']}">Solo · 400+ commits</text>
{''.join(shots)}'''
    return frame(W, H, t, inner, defs, "FisioChecks, my flagship app: clinical calculator for respiratory physiotherapists and intensivists")


def highlights(theme):
    t = THEMES[theme]
    items = [("7", "apps on Google Play"), ("2", "apps on the App Store"), ("5K+", "downloads on My Daily Humour")]
    W, H, g = 840, 88, 12
    w = (W - g * (len(items) - 1)) / len(items)
    out = []
    for i, (num, lab) in enumerate(items):
        x = i * (w + g)
        out.append(f'<rect x="{x+0.5}" y="0.5" width="{w-1}" height="{H-1}" rx="14" fill="{t["card"]}" stroke="{t["border"]}"/>'
                   f'<text x="{x+w/2}" y="42" font-size="28" font-weight="800" text-anchor="middle" fill="url(#tri)">{num}</text>'
                   f'<text x="{x+w/2}" y="66" font-size="11.5" font-weight="600" text-anchor="middle" fill="{t["muted"]}">{escape(lab)}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" role="img" aria-label="Highlights">
<defs><linearGradient id="tri" gradientUnits="userSpaceOnUse" x1="0" x2="{W}"><stop offset="0" stop-color="#2dd4bf"/><stop offset="0.5" stop-color="#60a5fa"/><stop offset="1" stop-color="#a78bfa"/></linearGradient></defs>
{''.join(out)}</svg>'''


def earlier(theme):
    t = THEMES[theme]
    W, H, a = 420, 196, "#a78bfa"
    apps = [("com.confradestech.meusatendimentos.png", "Meus Atendimentos"), ("com.confradestech.curatelafacil.png", "Curatela Fácil"),
            ("com.comocuidardesuamascara.png", "Como cuidar da minha máscara")]
    rows, defs = [], f'<radialGradient id="gl" cx="1" cy="0" r="1"><stop offset="0" stop-color="{a}" stop-opacity="0.2"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient><linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></linearGradient>'
    for i, (icon, name) in enumerate(apps):
        y = 58 + i * 42
        defs += f'<clipPath id="e{i}"><rect x="20" y="{y}" width="32" height="32" rx="8"/></clipPath>'
        rows.append(f'<image href="{data_uri(icon)}" x="20" y="{y}" width="32" height="32" clip-path="url(#e{i})"/>'
                    f'<rect x="20" y="{y}" width="32" height="32" rx="8" fill="none" stroke="{t["border"]}"/>'
                    f'<text x="64" y="{y+21}" font-size="13.5" font-weight="600" fill="{t["text"]}">{escape(name)}</text>')
    inner = f'''<g clip-path="url(#cc)"><rect x="{W-260}" y="-10" width="270" height="200" fill="url(#gl)"/><rect width="{W}" height="3" fill="url(#bar)"/></g>
<text x="20" y="38" font-size="19" font-weight="700" fill="{t['text']}">Where it started</text>
<text x="{W-20}" y="38" font-size="11.5" font-weight="600" text-anchor="end" fill="{t['muted']}">2020–21 · Android</text>
{''.join(rows)}'''
    return frame(W, H, t, inner, defs, "Earlier apps on Google Play: Meus Atendimentos, Curatela Fácil, Como cuidar da minha máscara")


def certs(theme):
    t = THEMES[theme]
    items = [("iOS Development Masterclass 2027", "SwiftUI, SwiftData, AI", "Udemy · Oct 2026", "#60a5fa"),
             ("AI Engineer Core Track", "LLM Engineering, RAG, QLoRA, Agents", "Udemy · Sep 2026", "#2dd4bf"),
             ("Compose Multiplatform Apps", "Building industry-level Android & iOS apps", "PL Coding · Aug 2026", "#a78bfa"),
             ("Claude Code: The Practical Guide", "Agentic coding in real projects", "Udemy · Aug 2026", "#fb7185")]
    W, g, h = 840, 12, 84
    w = (W - g) / 2
    out = []
    for i, (title, sub, meta, a) in enumerate(items):
        x, y = (i % 2) * (w + g), (i // 2) * (h + g)
        out.append(f'<rect x="{x+0.5}" y="{y+0.5}" width="{w-1}" height="{h-1}" rx="14" fill="{t["card"]}" stroke="{t["border"]}"/>'
                   f'<rect x="{x+16}" y="{y+18}" width="4" height="{h-36}" rx="2" fill="{a}"/>'
                   f'<text x="{x+34}" y="{y+33}" font-size="15" font-weight="700" fill="{t["text"]}">{escape(title)}</text>'
                   f'<text x="{x+34}" y="{y+52}" font-size="12" fill="{t["muted"]}">{escape(sub)}</text>'
                   f'<text x="{x+34}" y="{y+69}" font-size="11" font-weight="600" fill="{a if theme=="dark" else t["chip_text"]}">{escape(meta)}</text>')
    H = 2 * h + g
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" role="img" aria-label="Recent courses">{"".join(out)}</svg>'


def contact(theme):
    t = THEMES[theme]
    W, H = 1280, 250
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}" role="img" aria-label="Let's build something. Open to Android, iOS and Kotlin Multiplatform roles.">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['hero_a']}"/><stop offset="0.55" stop-color="{t['hero_b']}"/><stop offset="1" stop-color="{t['hero_c']}"/></linearGradient>
<linearGradient id="name" x1="0" x2="1"><stop offset="0.2" stop-color="#2dd4bf"/><stop offset="0.5" stop-color="#60a5fa"/><stop offset="0.8" stop-color="#a78bfa"/></linearGradient>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
<pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{t['hero_text']}" opacity="0.07"/></pattern>
<style>.orb{{animation:drift 14s ease-in-out infinite alternate}}@keyframes drift{{from{{transform:translate(0,0)}}to{{transform:translate(40px,-20px)}}}}@media (prefers-reduced-motion:reduce){{.orb{{animation:none}}}}</style></defs>
<g clip-path="url(#frame)"><rect width="{W}" height="{H}" fill="url(#bg)"/>
<circle class="orb" cx="240" cy="230" r="170" fill="#2dd4bf" opacity="{t['glow']*0.5}" filter="url(#soft)"/>
<circle class="orb" cx="1040" cy="20" r="190" fill="#8b5cf6" opacity="{t['glow']*0.6}" filter="url(#soft)" style="animation-delay:-6s"/>
<rect width="{W}" height="{H}" fill="url(#dots)"/>
<text x="{W/2}" y="112" font-size="58" font-weight="800" letter-spacing="-1.2" text-anchor="middle" fill="url(#name)">Let’s build something.</text>
<text x="{W/2}" y="160" font-size="23" font-weight="500" text-anchor="middle" fill="{t['hero_text']}">Open to Android, iOS and Kotlin Multiplatform roles</text>
<text x="{W/2}" y="196" font-size="17" text-anchor="middle" fill="{t['hero_muted']}">Remote from Brasília, Brazil  ·  UTC-3</text></g></svg>'''


for theme in THEMES:
    for name, fn in [("spotlight", spotlight), ("highlights", highlights), ("app-earlier", earlier), ("certs", certs), ("contact", contact)]:
        (OUT / f"{name}-{theme}.svg").write_text(fn(theme), encoding="utf8")
        print(f"{name}-{theme}.svg {(OUT / f'{name}-{theme}.svg').stat().st_size/1024:.1f} KB")


# ---------------------------------------------------------------- user reviews
REVIEWS = [
    ("my-daily-humour", "My Daily Humour", "#fb7185",
     "Perfeito para monitorar como a gente se sente no dia a dia. A opção de poder colocar comentários serve muito como um diário para vermos nossa evolução!",
     "Perfect for tracking how we feel day to day. Being able to add comments works like a diary to see our progress!"),
    ("my-daily-humour-2", "My Daily Humour", "#fb7185",
     "Ótima ideia de aplicativo e que funciona bem. […] Obrigada pelo APP e ótimo trabalho.",
     "Great app idea, and it works well. […] Thanks for the app and great work."),
]


def wrap(text, n):
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > n and cur:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    return lines + [cur]


def review(r, theme):
    t = THEMES[theme]
    _, app, a, quote, english = r
    W, y, body = 420, 70, []
    for line in wrap(quote, 54):
        body.append(f'<text x="24" y="{y}" font-size="13.5" font-weight="500" fill="{t["text"]}">{escape(line)}</text>')
        y += 20
    y += 4
    for line in wrap(english, 62):
        body.append(f'<text x="24" y="{y}" font-size="11.5" font-style="italic" fill="{t["muted"]}">{escape(line)}</text>')
        y += 16
    H = 196
    inner = f'''<g clip-path="url(#cc)"><rect x="{W-260}" y="-10" width="270" height="200" fill="url(#gl)"/><rect width="{W}" height="3" fill="url(#bar)"/></g>
<text x="20" y="56" font-size="46" font-weight="800" fill="{a}" opacity="0.55">“</text>
{"".join(body)}
<text x="24" y="{H-20}" font-size="11.5" font-weight="700" fill="{a if theme == "dark" else t["text"]}">{escape(app)}</text>
<text x="{W-20}" y="{H-20}" font-size="11" font-weight="600" text-anchor="end" fill="{t["muted"]}">Google Play review · Brazil</text>'''
    defs = (f'<radialGradient id="gl" cx="1" cy="0" r="1"><stop offset="0" stop-color="{a}" stop-opacity="0.18"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></linearGradient>')
    return frame(W, H, t, inner, defs, f"Google Play review of {app}: {english}")


for theme in THEMES:
    for r in REVIEWS:
        (OUT / f"review-{r[0]}-{theme}.svg").write_text(review(r, theme), encoding="utf8")
