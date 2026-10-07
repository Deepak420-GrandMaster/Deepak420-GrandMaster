#!/usr/bin/env python3
"""Builds the static pastel cards: stack.svg, project-*.svg and footer.svg.

Run from the repo root:  python scripts/build_static.py
Edit the STACK / PROJECTS lists below, re-run, commit the SVGs.
"""
import html
import textwrap
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

FONT_SANS = "'Segoe UI', -apple-system, 'Helvetica Neue', Arial, sans-serif"
FONT_MONO = "'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# name, chip fill, chip stroke, chip text, label colour
TONES = {
    "lavender": ("#F1EBFF", "#CDBDFB", "#4F3FA0", "#7B68C8"),
    "pink":     ("#FFEAF2", "#FFBFD8", "#A8426F", "#C45A88"),
    "sky":      ("#E8F5FE", "#B5DBF5", "#2A6A9B", "#4B8DBD"),
    "mint":     ("#E6F7EE", "#B0E3CA", "#2A7352", "#4BA67C"),
    "peach":    ("#FFF1E6", "#FFD3B3", "#9A5A2A", "#CC8452"),
}

STACK = [
    ("data.cloud", "lavender", ["BigQuery", "GA4 · GTM", "SQL", "GCP", "Azure Synapse",
                                "Databricks", "Spark", "dbt", "PostgreSQL"]),
    ("ai.ml",      "pink",     ["Python", "LangChain", "ChromaDB", "RAG · RAGAS",
                                "PyTorch", "LLM fine-tuning", "Streamlit"]),
    ("bi.viz",     "sky",      ["Looker Studio", "Power BI", "Apache Superset", "Tableau"]),
    ("tooling",    "mint",     ["Docker", "Git", "Jenkins", "Jira · Scrum"]),
]

# repo, description, tags, metric (or None), tone
PROJECTS = [
    ("Airbnb-agentic-rag",
     "Agentic RAG travel assistant over Airbnb data: retrieval plus an evaluation harness, with a live demo.",
     ["Python", "RAG", "RAGAS"], "faithfulness 0.60 → 0.92", "pink"),
    ("Agentic-AI",
     "Multi-agent AI workflows and reusable tooling patterns.",
     ["Agents", "Tooling"], None, "lavender"),
    ("Stock-Market-Analysis",
     "MLP neural network predicting the Nifty next-day price.",
     ["Python", "Deep learning"], "R² 0.97 · MAPE 0.52%", "sky"),
    ("Fraud-Detection",
     "Hybrid supervised + unsupervised fraud detection with Random Forest and Isolation Forest.",
     ["Python", "scikit-learn"], None, "mint"),
    ("Flight-Fare-Prediction",
     "Power BI dashboard predicting flight fares from historical data.",
     ["Power BI", "Forecasting"], None, "peach"),
    ("SQL-Project",
     "SQL analytics on automotive and call-centre data: pricing trends, window functions, CTEs.",
     ["SQL", "Window functions", "CTEs"], None, "lavender"),
]

SHARED_STYLE = f"""
      .sans {{ font-family: {FONT_SANS}; }}
      .mono {{ font-family: {FONT_MONO}; }}
      .rise {{ animation: rise .8s ease-out both; }}
      @keyframes rise {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
      @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""

CHAR_W = 7.3   # px per character at 12.5px semi-bold, deliberately generous
CHIP_PAD = 30


def esc(s):
    return html.escape(s, quote=True)


def build_stack():
    width = 1000
    left = 24
    label_w = 120
    x0 = left + 24 + label_w
    x_max = width - 40
    row_gap = 14
    chip_h = 32
    y = 66
    parts = []
    delay = 0.0
    for label, tone, items in STACK:
        fill, stroke, text, lab = TONES[tone]
        # layout chips with wrapping
        x = x0
        rows = [[]]
        for it in items:
            w = len(it) * CHAR_W + CHIP_PAD
            if x + w > x_max:
                rows.append([])
                x = x0
            rows[-1].append((it, x, w))
            x += w + 10
        block_h = len(rows) * chip_h + (len(rows) - 1) * 10
        parts.append(
            f'<text class="mono" x="{left + 24}" y="{y + 21}" font-size="12.5" font-weight="700" '
            f'fill="{lab}" letter-spacing="1">{esc(label)}</text>'
        )
        ry = y
        for row in rows:
            for it, cx, w in row:
                parts.append(
                    f'<g class="rise" style="animation-delay:{delay:.2f}s">'
                    f'<rect x="{cx:.1f}" y="{ry}" width="{w:.1f}" height="{chip_h}" rx="16" fill="{fill}" stroke="{stroke}"/>'
                    f'<text class="sans" x="{cx + w / 2:.1f}" y="{ry + 21}" font-size="12.5" font-weight="600" '
                    f'fill="{text}" text-anchor="middle">{esc(it)}</text></g>'
                )
                delay += 0.04
            ry += chip_h + 10
        y += block_h + row_gap + 8
        parts.append(f'<line x1="{left + 24}" y1="{y - 12}" x2="{width - 48}" y2="{y - 12}" stroke="#F1ECFF"/>')
    height = y + 14
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Tech stack">
  <defs><style>{SHARED_STYLE}</style></defs>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="28" fill="#FFFFFF" stroke="#EDE6FF" stroke-width="2"/>
  <rect x="24" y="22" width="86" height="26" rx="13" fill="#F4EEFF"/>
  <text class="mono" x="40" y="40" font-size="12" font-weight="700" fill="#7B68C8" letter-spacing="1">stack.map</text>
  {chr(10).join("  " + p for p in parts)}
</svg>
"""
    (OUT / "stack.svg").write_text(svg, encoding="utf-8")


def build_projects():
    w, h = 310, 236
    for i, (name, desc, tags, metric, tone) in enumerate(PROJECTS, 1):
        fill, stroke, text, lab = TONES[tone]
        lines = textwrap.wrap(desc, 38)[:3]
        desc_svg = "".join(
            f'<text class="sans" x="26" y="{94 + n * 19}" font-size="13" fill="#6F6888">{esc(l)}</text>'
            for n, l in enumerate(lines)
        )
        tx = 26
        tag_svg = []
        for t in tags:
            tw = len(t) * 6.6 + 22
            tag_svg.append(
                f'<rect x="{tx:.1f}" y="{h - 52}" width="{tw:.1f}" height="24" rx="12" fill="{fill}" stroke="{stroke}"/>'
                f'<text class="mono" x="{tx + tw / 2:.1f}" y="{h - 36}" font-size="11" font-weight="600" fill="{text}" text-anchor="middle">{esc(t)}</text>'
            )
            tx += tw + 8
        metric_svg = ""
        if metric:
            mw = len(metric) * 6.7 + 22
            metric_svg = (
                f'<rect x="26" y="{h - 92}" width="{mw:.1f}" height="22" rx="11" fill="#FFFFFF" stroke="{stroke}"/>'
                f'<text class="mono" x="{26 + mw / 2:.1f}" y="{h - 77}" font-size="11" font-weight="700" fill="{text}" text-anchor="middle">{esc(metric)}</text>'
            )
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(name)}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{fill}"/><stop offset="1" stop-color="#FFFFFF"/>
    </linearGradient>
    <filter id="s" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#8B7BC8" flood-opacity="0.16"/>
    </filter>
    <style>{SHARED_STYLE}
      .card {{ animation: rise .8s ease-out both; }}
      .dot {{ animation: bob 3.2s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
      @keyframes bob {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-3px); }} }}
    </style>
  </defs>
  <g class="card" filter="url(#s)">
    <rect x="6" y="4" width="{w - 12}" height="{h - 12}" rx="20" fill="url(#g)" stroke="{stroke}"/>
  </g>
  <circle class="dot" cx="46" cy="44" r="15" fill="{stroke}" fill-opacity="0.55"/>
  <path d="M40 40l-5 4 5 4M52 40l5 4-5 4" fill="none" stroke="{text}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <text class="mono" x="70" y="49" font-size="14.5" font-weight="700" fill="#3B3552">{esc(name)}</text>
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
      <stop offset="0" stop-color="#FFEAF2"/><stop offset="0.5" stop-color="#F1EBFF"/><stop offset="1" stop-color="#E4F4FD"/>
    </linearGradient>
    <clipPath id="c"><rect width="1000" height="140" rx="28"/></clipPath>
    <style>{SHARED_STYLE}
      .w1 {{ animation: sway 8s ease-in-out infinite; }}
      .w2 {{ animation: sway 11s ease-in-out infinite reverse; }}
      @keyframes sway {{ 0%,100% {{ transform: translateX(0); }} 50% {{ transform: translateX(-60px); }} }}
    </style>
  </defs>
  <g clip-path="url(#c)">
    <rect width="1000" height="140" fill="url(#bg)"/>
    <path class="w1" d="M0 96 C 100 70, 200 120, 300 96 S 500 70, 600 96 S 800 120, 900 96 S 1100 70, 1200 96 V140 H0Z" fill="#FFFFFF" fill-opacity="0.55"/>
    <path class="w2" d="M0 112 C 120 90, 220 132, 340 112 S 560 90, 680 112 S 900 132, 1020 112 S 1140 96, 1200 112 V140 H0Z" fill="#FFFFFF" fill-opacity="0.7"/>
  </g>
  <rect x="1" y="1" width="998" height="138" rx="27" fill="none" stroke="#E4DAFF" stroke-width="2"/>
  <text class="sans" x="500" y="58" font-size="20" font-weight="700" fill="#3B3552" text-anchor="middle">Building calm, precise systems</text>
  <text class="mono" x="500" y="84" font-size="13" fill="#7A7394" text-anchor="middle">whether a data pipeline, an AI agent, or my own career path</text>
</svg>
"""
    (OUT / "footer.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    build_stack()
    build_projects()
    build_footer()
    print("built static cards in", OUT)
