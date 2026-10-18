"""Render the hardware cards from their editable SVG sources."""

from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
NS = {"s": "http://www.w3.org/2000/svg"}

CARDS = {
    "dev-pc": ("Dev PC", "WORKSTATION", [
        ("Processor", "AMD Ryzen 5 5600"),
        ("Graphics", "AMD Radeon RX 6800 XT · XFX MERC 319 D6 16GB"),
        ("Memory", "ESSENCORE KLEVV BOLT X · 32 GB (16 GB × 2) · DDR4-3200 CL16"),
        ("Motherboard", "GIGABYTE B450 AORUS ELITE"),
        ("Storage", "Samsung NVMe PM981a 512 GB + PM9a1 1 TB"),
        ("Cooling", "Noctua NH-U12A chromax.black"),
        ("Power supply", "Antec NeoECO 850W 80PLUS GOLD"),
    ]),
    "nas": ("NAS", "NETWORK ATTACHED STORAGE", [
        ("Processor", "Intel Core i7-4770"),
        ("Memory", "16 GB DDR3 · 8 GB × 2"),
        ("SSD", "SK Hynix Gold P31 512 GB"),
        ("HDD", "Toshiba P300 2 TB"),
        ("Motherboard", "ASRock B85M Pro4"),
        ("Cooling", "DeepCool GAMMAX GTE (White)"),
        ("Power supply", "Micronics Classic II 700W"),
    ]),
}


def build_sources():
    photo = ET.parse(ASSETS / "dev-pc-light.svg").getroot().find(".//s:image", NS)
    photo_href = photo.get("href")
    photo_height = int(photo.get("height"))
    for name, (title, kicker, rows) in CARDS.items():
        for theme in ("dark", "light"):
            dark = theme == "dark"
            bg, tile, border, muted, ink = (
                ("#0d1117", "#161b22", "#30363d", "#8b949e", "#f0f6fc")
                if dark else
                ("#ffffff", "#f6f8fa", "#d1d9e0", "#59636e", "#1f2328")
            )
            accent = (
                ("#5eead4" if dark else "#087f72") if name == "dev-pc"
                else ("#c4b5fd" if dark else "#7355b4")
            )
            panel_y = 96 + (photo_height + 24 if name == "dev-pc" else 0)
            panel_height = len(rows) * 40 + 24
            height = panel_y + panel_height + 24
            description = escape("; ".join(f"{label}: {value}" for label, value in rows))
            svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{height}" viewBox="0 0 800 {height}" fill="none" role="img" aria-labelledby="title description">
<title id="title">{title}</title>
<desc id="description">{description}</desc>
<rect x="0.5" y="0.5" width="799" height="{height - 1}" rx="20" fill="{bg}" stroke="{border}"/>
<path d="M28 34V64" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>
<g font-family="Segoe UI, Arial, sans-serif">
<text x="44" y="39" fill="{muted}" font-size="11" font-weight="600" letter-spacing="2">{kicker}</text>
<text x="43" y="69" fill="{ink}" font-size="27" font-weight="700">{title}</text>''']
            icon = (
                '<rect x="728" y="30" width="32" height="27" rx="4"/><path d="M736 66h16m-8-9v9M736 38h16m-16 7h9"/>'
                if name == "dev-pc" else
                '<rect x="728" y="28" width="32" height="18" rx="4"/><rect x="728" y="50" width="32" height="18" rx="4"/><path d="M735 37h.01m0 22h.01M745 37h8m-8 22h8"/>'
            )
            svg.append(f'<g stroke="{accent}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{icon}</g>')
            if name == "dev-pc":
                svg.append(f'<defs><clipPath id="photo-clip"><rect x="24" y="96" width="752" height="{photo_height}" rx="12"/></clipPath></defs>')
                svg.append(f'<image x="24" y="96" width="752" height="{photo_height}" preserveAspectRatio="xMidYMid meet" clip-path="url(#photo-clip)" href="{photo_href}"/>')
            svg.append(f'<g id="components"><rect x="24" y="{panel_y}" width="752" height="{panel_height}" rx="12" fill="{tile}"/>')
            for i, (label, value) in enumerate(rows):
                y = panel_y + 38 + i * 40
                if i:
                    svg.append(f'<path d="M42 {y - 25}H758" stroke="{border}" stroke-opacity="0.5"/>')
                svg.append(f'<text x="42" y="{y}" font-size="12" fill="{muted}">{escape(label)}</text>')
                svg.append(f'<text x="180" y="{y}" font-size="14" fill="{ink}">{escape(value)}</text>')
            svg.append('</g></g></svg>\n')
            source = "\n".join(svg)
            ET.fromstring(source)
            (ASSETS / f"{name}-{theme}.svg").write_text(source, encoding="utf-8")


def render():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 800, "height": 1400}, device_scale_factor=2)
        for name in CARDS:
            for theme in ("dark", "light"):
                page.goto((ASSETS / f"{name}-{theme}.svg").as_uri())
                overflow = page.locator("svg").evaluate('''svg => [...svg.querySelectorAll("text")].filter(t => {
                    const b = t.getBBox(); return b.x + b.width > 776;
                }).map(t => t.textContent)''')
                assert not overflow, overflow
                assert page.locator("#components text").count() == 14
                page.locator("svg").screenshot(path=str(ASSETS / f"{name}-list-{theme}.png"), omit_background=True)
        browser.close()


if __name__ == "__main__":
    build_sources()
    render()
    print("Rendered PC and NAS component lists in both themes; no text overflow.")
