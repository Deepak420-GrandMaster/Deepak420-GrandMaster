#!/usr/bin/env python3
"""Generates assets/stats.svg and assets/languages.svg from live GitHub data.

Uses only the standard library.

    GITHUB_TOKEN=... python scripts/generate_stats.py --user Deepak420-GrandMaster
    python scripts/generate_stats.py --demo            # sample data, no network

Public data only. If you want private contributions counted, give the workflow a
personal access token (see README) and enable "Include private contributions" in
your GitHub profile settings.
"""
import argparse
import datetime as dt
import html
import json
import os
import urllib.request
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
FONT_SANS = "'Segoe UI', -apple-system, 'Helvetica Neue', Arial, sans-serif"
FONT_MONO = "'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    following { totalCount }
    allPublic: repositories(ownerAffiliations: OWNER, privacy: PUBLIC) { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

# Warm beige palette. Language shades run dark -> light.
SANS = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif"
PALETTE = ["#6F5638", "#9C7A54", "#BE9E78", "#D5BE9C", "#E3D3B9", "#EDE2CE"]
CARD, FRAME, TILE = "#FFFDF9", "#E4D9C6", "#F5EFE4"
INK, INK2, MUTED, FAINT, BRONZE = "#1D1B18", "#4A4339", "#6E675D", "#A39B8E", "#9C7A54"

# Notebook files are huge in bytes and swamp the real languages, so they are left out.
EXCLUDE_LANGUAGES = {"Jupyter Notebook"}


def esc(s):
    return html.escape(str(s), quote=True)


def streaks(days):
    days = sorted(days, key=lambda d: d["date"])
    best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        best = max(best, run)
    # current streak: walk back from today; today may still be empty
    cur = 0
    idx = len(days) - 1
    if idx >= 0 and days[idx]["contributionCount"] == 0:
        idx -= 1
    while idx >= 0 and days[idx]["contributionCount"] > 0:
        cur += 1
        idx -= 1
    return cur, best


SHARED = f"""
      .sf {{ font-family: {SANS}; }}
      .eyebrow {{ font-size: 12px; font-weight: 600; letter-spacing: 1.6px; }}
      .rise {{ animation: rise .8s cubic-bezier(.2,.8,.2,1) both; }}
      @keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
      @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""


def render_stats(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    active = sum(1 for d in days if d["contributionCount"] > 0)
    cur, best = streaks(days)
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    tiles = [
        (f'{cal["totalContributions"]:,}', "Contributions", "Last 12 months"),
        (f"{active}", "Active days", "Days with a commit"),
        (f"{cur}", "Current streak", "Consecutive days"),
        (f"{best}", "Best streak", "Longest run"),
    ]
    chips = [
        f'{u["allPublic"]["totalCount"]} public repos',
        f"{stars} stars",
        f'{u["followers"]["totalCount"]} followers',
        f'{u["following"]["totalCount"]} following',
    ]
    w, h = 1000, 236
    tw, gap = 226, 16
    parts = []
    for i, (big, label, sub) in enumerate(tiles):
        x = 28 + i * (tw + gap - 3.5)
        dark = i == 0
        bg = "#2B2620" if dark else TILE
        num = "#F5EFE4" if dark else INK
        lab = "#EBD9B8" if dark else INK2
        subc = "#A89F90" if dark else FAINT
        parts.append(f"""
  <g class="rise" style="animation-delay:{i * 0.1:.2f}s">
    <rect x="{x:.1f}" y="66" width="{tw - 4}" height="106" rx="22" fill="{bg}"/>
    <text class="sf" x="{x + 22:.1f}" y="118" font-size="42" font-weight="700" fill="{num}" letter-spacing="-1.2">{esc(big)}</text>
    <text class="sf" x="{x + 22:.1f}" y="142" font-size="14" font-weight="600" fill="{lab}">{esc(label)}</text>
    <text class="sf" x="{x + 22:.1f}" y="159" font-size="12" fill="{subc}">{esc(sub)}</text>
  </g>""")
    cx = 28
    for c in chips:
        cw = len(c) * 7.2 + 30
        parts.append(
            f'<rect x="{cx:.0f}" y="190" width="{cw:.0f}" height="28" rx="14" fill="{CARD}" stroke="#E6DCCB"/>'
            f'<text class="sf" x="{cx + cw / 2:.0f}" y="208" font-size="12.5" font-weight="500" fill="{MUTED}" text-anchor="middle">{esc(c)}</text>'
        )
        cx += cw + 10
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="GitHub activity">
  <defs><style>{SHARED}</style></defs>
  <rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="31.5" fill="{CARD}" stroke="{FRAME}" stroke-width="1.5"/>
  <text class="sf eyebrow" x="30" y="44" fill="{BRONZE}">GITHUB ACTIVITY</text>
  <text class="sf" x="{w - 30}" y="44" font-size="12" fill="{FAINT}" text-anchor="end">Updated {dt.date.today().isoformat()}</text>
  {"".join(parts)}
</svg>
"""
    (OUT / "stats.svg").write_text(svg, encoding="utf-8")


def render_languages(u):
    totals = defaultdict(int)
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            if e["node"]["name"] in EXCLUDE_LANGUAGES:
                continue
            totals[e["node"]["name"]] += e["size"]
    top = sorted(totals.items(), key=lambda kv: -kv[1])[:6]
    total = sum(v for _, v in top) or 1
    w = 1000
    rows = (len(top) + 1) // 2
    h = 118 + rows * 36
    bar_x, bar_w = 30, w - 60
    segs, x = [], bar_x
    for i, (name, size) in enumerate(top):
        sw = bar_w * size / total
        segs.append(f'<rect x="{x:.1f}" y="68" width="{sw + 0.5:.1f}" height="20" fill="{PALETTE[i % len(PALETTE)]}"/>')
        x += sw
    legend = []
    for i, (name, size) in enumerate(top):
        col, row = i % 2, i // 2
        lx = 30 + col * 480
        ly = 126 + row * 36
        legend.append(f"""
  <g class="rise" style="animation-delay:{i * 0.08:.2f}s">
    <circle cx="{lx + 7}" cy="{ly - 5}" r="6" fill="{PALETTE[i % len(PALETTE)]}"/>
    <text class="sf" x="{lx + 24}" y="{ly}" font-size="15" font-weight="500" fill="{INK}">{esc(name)}</text>
    <text class="sf" x="{lx + 430}" y="{ly}" font-size="14" fill="{MUTED}" text-anchor="end">{size / total * 100:.1f}%</text>
  </g>""")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Language spread">
  <defs>
    <clipPath id="bar"><rect x="{bar_x}" y="68" width="{bar_w}" height="20" rx="10"/></clipPath>
    <clipPath id="reveal"><rect class="wipe" x="{bar_x}" y="64" width="{bar_w}" height="28"/></clipPath>
    <style>{SHARED}
      .wipe {{ transform-box: fill-box; transform-origin: left; animation: wipe 1.6s cubic-bezier(.2,.8,.2,1) both; }}
      @keyframes wipe {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
    </style>
  </defs>
  <rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="31.5" fill="{CARD}" stroke="{FRAME}" stroke-width="1.5"/>
  <text class="sf eyebrow" x="30" y="44" fill="{BRONZE}">LANGUAGES</text>
  <text class="sf" x="{w - 30}" y="44" font-size="12" fill="{FAINT}" text-anchor="end">Owned public repos, notebooks excluded</text>
  <rect x="{bar_x}" y="68" width="{bar_w}" height="20" rx="10" fill="{TILE}"/>
  <g clip-path="url(#bar)"><g clip-path="url(#reveal)">{"".join(segs)}</g></g>
  {"".join(legend)}
</svg>
"""
    (OUT / "languages.svg").write_text(svg, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_USER", "Deepak420-GrandMaster"))
    ap.add_argument("--demo", action="store_true", help="use sample data instead of the API")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.demo:
        user = demo_user()
    else:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token:
            raise SystemExit("Set GITHUB_TOKEN (or GH_TOKEN), or run with --demo")
        user = fetch(args.user, token)
    render_stats(user)
    render_languages(user)
    print("wrote stats.svg and languages.svg")


if __name__ == "__main__":
    main()
