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

# pastel palette used for language ranks (and tiles)
PALETTE = ["#B9A6F5", "#FFB8D6", "#9FD3F5", "#9ADBBB", "#FFCBA4", "#E3C8F7", "#CFCFE8"]
TILES = [
    ("#B9A6F5", "#F4EEFF", "#4F3FA0"),
    ("#FFB8D6", "#FFEAF2", "#A8426F"),
    ("#9FD3F5", "#E8F5FE", "#2A6A9B"),
    ("#9ADBBB", "#E6F7EE", "#2A7352"),
]


def esc(s):
    return html.escape(str(s), quote=True)


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "pastel-profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise SystemExit(f"GitHub API error: {payload['errors']}")
    return payload["data"]["user"]


def demo_user():
    import random
    random.seed(7)
    today = dt.date.today()
    days = []
    for i in range(365, -1, -1):
        d = today - dt.timedelta(days=i)
        n = 0 if random.random() < 0.55 else random.randint(1, 9)
        if i < 9:
            n = max(n, 1)
        days.append({"date": d.isoformat(), "contributionCount": n})
    weeks = [{"contributionDays": days}]
    return {
        "followers": {"totalCount": 3}, "following": {"totalCount": 17},
        "allPublic": {"totalCount": 18},
        "repositories": {"nodes": [
            {"stargazerCount": 1, "languages": {"edges": [
                {"size": 78000, "node": {"name": "Python"}}, {"size": 9000, "node": {"name": "Jupyter Notebook"}},
                {"size": 3000, "node": {"name": "Shell"}}]}},
            {"stargazerCount": 1, "languages": {"edges": [
                {"size": 26000, "node": {"name": "Python"}}, {"size": 9000, "node": {"name": "SQL"}},
                {"size": 5000, "node": {"name": "HTML"}}, {"size": 2000, "node": {"name": "Dockerfile"}}]}},
        ]},
        "contributionsCollection": {"contributionCalendar": {
            "totalContributions": sum(d["contributionCount"] for d in days), "weeks": weeks}},
    }


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
      .sans {{ font-family: {FONT_SANS}; }}
      .mono {{ font-family: {FONT_MONO}; }}
      .rise {{ animation: rise .8s ease-out both; }}
      @keyframes rise {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
      @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""


def render_stats(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    active = sum(1 for d in days if d["contributionCount"] > 0)
    cur, best = streaks(days)
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    tiles = [
        (f'{cal["totalContributions"]:,}', "contributions", "last 12 months"),
        (f"{active}", "active days", "days with a commit"),
        (f"{cur}", "current streak", "consecutive days"),
        (f"{best}", "best streak", "longest run"),
    ]
    chips = [
        f'public repos {u["allPublic"]["totalCount"]}',
        f"stars {stars}",
        f'followers {u["followers"]["totalCount"]}',
        f'following {u["following"]["totalCount"]}',
    ]
    w, h = 1000, 232
    tw, gap = 226, 16
    parts = []
    for i, ((big, label, sub), (accent, bg, ink)) in enumerate(zip(tiles, TILES)):
        x = 24 + i * (tw + gap)
        parts.append(f"""
  <g class="rise" style="animation-delay:{i * 0.12:.2f}s">
    <rect x="{x}" y="62" width="{tw}" height="104" rx="18" fill="{bg}"/>
    <rect x="{x + 18}" y="62" width="46" height="5" rx="2.5" fill="{accent}"/>
    <text class="sans" x="{x + 18}" y="112" font-size="40" font-weight="800" fill="#3B3552">{esc(big)}</text>
    <text class="sans" x="{x + 18}" y="136" font-size="13.5" font-weight="700" fill="{ink}">{esc(label)}</text>
    <text class="mono" x="{x + 18}" y="154" font-size="10.5" fill="#8D86A6">{esc(sub)}</text>
  </g>""")
    cx = 24
    for c in chips:
        cw = len(c) * 7 + 28
        parts.append(
            f'<rect x="{cx}" y="184" width="{cw:.0f}" height="28" rx="14" fill="#FFFFFF" stroke="#E4DAFF"/>'
            f'<text class="mono" x="{cx + cw / 2:.0f}" y="202" font-size="11.5" fill="#6B5FA8" text-anchor="middle">{esc(c)}</text>'
        )
        cx += cw + 10
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="GitHub activity">
  <defs><style>{SHARED}</style></defs>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="28" fill="#FFFFFF" stroke="#EDE6FF" stroke-width="2"/>
  <rect x="24" y="20" width="148" height="26" rx="13" fill="#F4EEFF"/>
  <text class="mono" x="40" y="38" font-size="12" font-weight="700" fill="#7B68C8" letter-spacing="1">github.activity</text>
  <text class="mono" x="{w - 24}" y="38" font-size="11" fill="#A39CBB" text-anchor="end">updated {dt.date.today().isoformat()}</text>
  {"".join(parts)}
</svg>
"""
    (OUT / "stats.svg").write_text(svg, encoding="utf-8")


def render_languages(u):
    totals = defaultdict(int)
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            totals[e["node"]["name"]] += e["size"]
    top = sorted(totals.items(), key=lambda kv: -kv[1])[:6]
    total = sum(v for _, v in top) or 1
    w = 1000
    rows = (len(top) + 1) // 2
    h = 116 + rows * 34
    bar_x, bar_w = 24, w - 48
    segs, x = [], bar_x
    for i, (name, size) in enumerate(top):
        sw = bar_w * size / total
        segs.append(f'<rect x="{x:.1f}" y="64" width="{sw:.1f}" height="20" fill="{PALETTE[i % len(PALETTE)]}"/>')
        x += sw
    legend = []
    for i, (name, size) in enumerate(top):
        col, row = i % 2, i // 2
        lx = 24 + col * 480
        ly = 118 + row * 34
        legend.append(f"""
  <g class="rise" style="animation-delay:{i * 0.08:.2f}s">
    <circle cx="{lx + 8}" cy="{ly - 5}" r="6" fill="{PALETTE[i % len(PALETTE)]}"/>
    <text class="sans" x="{lx + 26}" y="{ly}" font-size="15" font-weight="600" fill="#3B3552">{esc(name)}</text>
    <text class="mono" x="{lx + 440}" y="{ly}" font-size="13" fill="#7A7394" text-anchor="end">{size / total * 100:.1f}%</text>
  </g>""")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Language spread">
  <defs>
    <clipPath id="bar"><rect x="{bar_x}" y="64" width="{bar_w}" height="20" rx="10"/></clipPath>
    <clipPath id="reveal"><rect class="wipe" x="{bar_x}" y="60" width="{bar_w}" height="28"/></clipPath>
    <style>{SHARED}
      .wipe {{ transform-box: fill-box; transform-origin: left; animation: wipe 1.6s cubic-bezier(.2,.8,.2,1) both; }}
      @keyframes wipe {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
    </style>
  </defs>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="28" fill="#FFFFFF" stroke="#EDE6FF" stroke-width="2"/>
  <rect x="24" y="20" width="168" height="26" rx="13" fill="#FFEAF2"/>
  <text class="mono" x="40" y="38" font-size="12" font-weight="700" fill="#A8426F" letter-spacing="1">language.spread</text>
  <text class="mono" x="{w - 24}" y="38" font-size="11" fill="#A39CBB" text-anchor="end">owned public repos</text>
  <rect x="{bar_x}" y="64" width="{bar_w}" height="20" rx="10" fill="#F4EEFF"/>
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
