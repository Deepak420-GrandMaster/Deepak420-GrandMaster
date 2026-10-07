#!/usr/bin/env python3
"""Builds the static cards: stack.svg, project-*.svg and footer.svg.

Warm beige palette, one bronze accent, system (SF) typography.

Run from the repo root:  python scripts/build_static.py
Edit the STACK / PROJECTS lists below, re-run, commit the SVGs.
"""
import html
import textwrap
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

SANS = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif"

# palette
CARD = "#FFFDF9"
FRAME = "#E4D9C6"
CHIP = "#F5EFE4"
CHIP_LINE = "#E6DCCB"
INK = "#1D1B18"
INK2 = "#4A4339"
MUTED = "#6E675D"
FAINT = "#A39B8E"
BRONZE = "#9C7A54"
BRONZE_DK = "#7A5C3A"
SAND = "#F3ECDF"

STACK = [
    ("DATA & CLOUD", ["BigQuery", "GA4 · GTM", "SQL", "GCP", "Azure Synapse",
                      "Databricks", "Spark", "dbt", "PostgreSQL"]),
    ("AI & ML", ["Python", "LangChain", "ChromaDB", "RAG · RAGAS",
                 "PyTorch", "LLM fine-tuning", "Streamlit"]),
    ("BI & VIZ", ["Looker Studio", "Power BI", "Apache Superset", "Tableau"]),
    ("TOOLING", ["Docker", "Git", "Jenkins", "Jira · Scrum"]),
]

# repo, description, tags, metric (or None)
PROJECTS = [
    ("Airbnb-agentic-rag",
     "Agentic RAG travel assistant over Airbnb data: retrieval plus an evaluation harness, with a live demo.",
     ["Python", "RAG", "RAGAS"], "Faithfulness 0.60 → 0.92"),
    ("Agentic-AI",
     "Multi-agent AI workflows and reusable tooling patterns.",
     ["Agents", "Tooling"], None),
    ("Stock-Market-Analysis",
     "MLP neural network predicting the Nifty next-day price.",
     ["Python", "Deep learning"], "R² 0.97 · MAPE 0.52%"),
    ("Fraud-Detection",
     "Hybrid supervised + unsupervised fraud detection with Random Forest and Isolation Forest.",
     ["Python", "scikit-learn"], None),
    ("Flight-Fare-Prediction",
     "Power BI dashboard predicting flight fares from historical data.",
     ["Power BI", "Forecasting"], None),
    ("SQL-Project",
     "SQL analytics on automotive and call-centre data: pricing trends, window functions, CTEs.",
     ["SQL", "Window functions", "CTEs"], None),
]

SHARED_STYLE = f"""
      .sf {{ font-family: {SANS}; }}
      .eyebrow {{ font-size: 12px; font-weight: 600; letter-spacing: 1.6px; }}
      .rise {{ animation: rise .8s cubic-bezier(.2,.8,.2,1) both; }}
      @keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
      @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""

CHAR_W = 6.6   # px per character at 13px medium, deliberately generous
CHIP_PAD = 28


def esc(s):
    return html.escape(s, quote=True)


def build_stack():
    width = 1000
    left = 28
    label_w = 150
    x0 = left + 24 + label_w
    x_max = width - 40
    chip_h = 32
    y = 74
    parts = []
    delay = 0.0
    for idx, (label, items) in enumerate(STACK):
        x = x0
        rows = [[]]
        for it in items:
            w = len(it) * CHAR_W + CHIP_PAD
            if x + w > x_max:
                rows.append([])
                x = x0
            rows[-1].append((it, x, w))
            x += w + 8
        block_h = len(rows) * chip_h + (len(rows) - 1) * 10
        parts.append(
            f'<text class="sf eyebrow" x="{left + 24}" y="{y + 21}" fill="{BRONZE}">{esc(label)}</text>'
        )
        ry = y
        for row in rows:
            for it, cx, w in row:
                parts.append(
                    f'<g class="rise" style="animation-delay:{delay:.2f}s">'
                    f'<rect x="{cx:.1f}" y="{ry}" width="{w:.1f}" height="{chip_h}" rx="16" fill="{CHIP}" stroke="{CHIP_LINE}"/>'
                    f'<text class="sf" x="{cx + w / 2:.1f}" y="{ry + 21}" font-size="13" font-weight="500" '
                    f'fill="{INK2}" text-anchor="middle">{esc(it)}</text></g>'
                )
                delay += 0.04
            ry += chip_h + 10
        y += block_h + 20
        if idx < len(STACK) - 1:
            parts.append(f'<line x1="{left + 24}" y1="{y - 10}" x2="{width - 52}" y2="{y - 10}" stroke="#F0E8DA"/>')
            y += 6
    height = y + 16
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Tech stack">
  <defs><style>{SHARED_STYLE}</style></defs>
  <rect x="0.75" y="0.75" width="{width - 1.5}" height="{height - 1.5}" rx="31.5" fill="{CARD}" stroke="{FRAME}" stroke-width="1.5"/>
  <text class="sf eyebrow" x="52" y="46" fill="{BRONZE_DK}">STACK</text>
  {chr(10).join("  " + p for p in parts)}
</svg>
"""
    (OUT / "stack.svg").write_text(svg, encoding="utf-8")


def build_projects():
    w, h = 310, 250
    for i, (name, desc, tags, metric) in enumerate(PROJECTS, 1):
        lines = textwrap.wrap(desc, 38)[:3]
        desc_svg = "".join(
            f'<text class="sf" x="28" y="{98 + n * 20}" font-size="13.5" fill="{MUTED}">{esc(l)}</text>'
            for n, l in enumerate(lines)
        )
        tx = 28
        tag_svg = []
        for t in tags:
            tw = len(t) * 6.9 + 24
            tag_svg.append(
                f'<rect x="{tx:.1f}" y="{h - 54}" width="{tw:.1f}" height="26" rx="13" fill="{CHIP}" stroke="{CHIP_LINE}"/>'
                f'<text class="sf" x="{tx + tw / 2:.1f}" y="{h - 37}" font-size="11.5" font-weight="500" fill="{INK2}" text-anchor="middle">{esc(t)}</text>'
            )
            tx += tw + 8
        metric_svg = ""
        if metric:
            mw = len(metric) * 6.6 + 24
            metric_svg = (
                f'<rect x="28" y="{h - 96}" width="{mw:.1f}" height="24" rx="12" fill="{SAND}"/>'
                f'<text class="sf" x="{28 + mw / 2:.1f}" y="{h - 80}" font-size="11.5" font-weight="700" fill="{BRONZE_DK}" text-anchor="middle">{esc(metric)}</text>'
            )
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(name)}">
  <defs>
    <filter id="s" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#6B5434" flood-opacity="0.10"/>
    </filter>
    <style>{SHARED_STYLE}
      .card {{ animation: rise .8s cubic-bezier(.2,.8,.2,1) both; }}
    </style>
  </defs>
  <g class="card" filter="url(#s)">
    <rect x="6" y="4" width="{w - 12}" height="{h - 14}" rx="22" fill="{CARD}" stroke="{FRAME}"/>
  </g>
  <circle cx="46" cy="48" r="16" fill="{SAND}"/>
  <path d="M40 44l-5 4 5 4M52 44l5 4-5 4" fill="none" stroke="{BRONZE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <text class="sf" x="72" y="53" font-size="15" font-weight="700" fill="{INK}" letter-spacing="-0.2">{esc(name)}</text>
  <path d="M{w - 40} {50}l10 -10m0 0h-7m7 0v7" fill="none" stroke="{FAINT}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  {desc_svg}
  {metric_svg}
  {"".join(tag_svg)}
</svg>
"""
        (OUT / f"project-{i}.svg").write_text(svg, encoding="utf-8")


def build_footer():
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="140" viewBox="0 0 1000 140" role="img" aria-label="Footer">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#F7F2EA"/><stop offset="1" stop-color="#ECE2D2"/>
    </linearGradient>
    <clipPath id="c"><rect width="1000" height="140" rx="32"/></clipPath>
    <style>{SHARED_STYLE}
      .w1 {{ animation: sway 12s ease-in-out infinite; }}
      .w2 {{ animation: sway 16s ease-in-out infinite reverse; }}
      @keyframes sway {{ 0%,100% {{ transform: translateX(0); }} 50% {{ transform: translateX(-60px); }} }}
    </style>
  </defs>
  <g clip-path="url(#c)">
    <rect width="1000" height="140" fill="url(#bg)"/>
    <path class="w1" d="M0 100 C 100 78, 200 118, 300 100 S 500 78, 600 100 S 800 118, 900 100 S 1100 78, 1200 100 V140 H0Z" fill="#FFFDF9" fill-opacity="0.5"/>
    <path class="w2" d="M0 116 C 120 98, 220 132, 340 116 S 560 98, 680 116 S 900 132, 1020 116 S 1140 102, 1200 116 V140 H0Z" fill="#FFFDF9" fill-opacity="0.75"/>
  </g>
  <rect x="0.75" y="0.75" width="998.5" height="138.5" rx="31.5" fill="none" stroke="{FRAME}" stroke-width="1.5"/>
  <text class="sf" x="500" y="60" font-size="24" font-weight="700" fill="{INK}" text-anchor="middle" letter-spacing="-0.6">Building calm, precise systems</text>
  <text class="sf" x="500" y="88" font-size="14" fill="{MUTED}" text-anchor="middle">Whether a data pipeline, an AI agent, or my own career path</text>
</svg>
"""
    (OUT / "footer.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    build_stack()
    build_projects()
    build_footer()
    print("built static cards in", OUT)
