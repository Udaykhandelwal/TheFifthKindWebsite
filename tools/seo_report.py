#!/usr/bin/env python3
"""Writes docs/seo/KEYWORDS.md, GOOGLE_ADS_BANGALORE.md and PAGES.md from data/*.json,
docs/seo/autocomplete.json and the built site. Run after build.py."""
import json, re, html, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "docs/seo"; D.mkdir(parents=True, exist_ok=True)
svc = {k: v for k, v in json.loads((ROOT / "data/services.json").read_text()).items() if not k.startswith("_")}
neg = json.loads((ROOT / "data/services.json").read_text())["_common_negatives"]
cities = {k: v for k, v in json.loads((ROOT / "data/cities.json").read_text()).items() if not k.startswith("_")}
ac = json.loads((D / "autocomplete.json").read_text())
B = "https://www.the5thkind.in"

def url_for(s, c):
    if c == "bangalore" and s.get("bangalore_page"): return s["bangalore_page"]
    return f"/{s['city_base']}/{c}/"

k = ["# Keyword research and mapping\n",
     "Source: Google autocomplete for India (gl=in, hl=en), pulled by `tools/kw_suggest.py` into `autocomplete.json`, plus SERP review. "
     "Autocomplete shows what people really type, but **not search volume**. Add Keyword Planner volumes once Google Ads is set up "
     "(see the Pending section of SEO_REPORT.md). DIY-tool searches (\"free\", \"generator\", \"app\", \"course\", \"jobs\") are deliberately not targeted.\n"]
for key, s in svc.items():
    kw = s["keywords"]
    k.append(f"\n## {s['name']}\n\n**Main page:** {B}{s['page']}  \n**Primary keyword:** {kw['primary']}\n")
    for label, field in [("Secondary", "secondary"), ("Long-tail", "long_tail"), ("Transactional", "transactional"), ("Commercial", "commercial"),
                         ("Informational (blog)", "informational"), ("Questions (FAQ)", "questions"), ("Low-competition opportunities", "low_competition")]:
        k.append(f"- **{label}:** {', '.join(kw.get(field, []))}")
    if s.get("cities"):
        k.append(f"- **Local pattern:** \"{kw['local']}\" → " + ", ".join(f"[{cities[c]['name']}]({url_for(s, c)})" for c in s["cities"]))
    real = [q for q in ac.get(key, []) if not any(n in q for n in ["free", "generator", "course", "job", "salary", "app", "github", "reddit", "kaise", "kya", "tutorial"])][:25]
    k.append(f"- **Autocomplete evidence (buyer-intent subset):** {', '.join(real)}")
(D / "KEYWORDS.md").write_text("\n".join(k) + "\n")

a = ["# Google Ads – Bangalore launch plan\n",
     "Each service is its own campaign/ad group with its own landing page, so Quality Score and reporting stay clean. "
     "Location: Bengaluru + 25 km radius, presence (not 'interest'). Bids, budgets, ads and approvals are set in Google Ads, not on the website.\n",
     "**Conversion actions to create in Google Ads** (labels go into `data/site.json` → `google_ads_labels`): "
     "`generate_lead` (form submit, primary), `whatsapp_click` (primary), `phone_click` (primary), `email_click` (secondary).\n",
     f"**Shared negative keywords:** {', '.join(neg)}\n",
     "| Ad group | Landing page | Exact match | Phrase match |", "|---|---|---|---|"]
for key, s in svc.items():
    lp = url_for(s, "bangalore") if "bangalore" in s.get("cities", []) else s["page"]
    a.append(f"| {s['ads']['ad_group']} | {B}{lp} | {', '.join('['+x+']' for x in s['ads']['exact'])} | {', '.join(chr(34)+x+chr(34) for x in s['ads']['phrase'])} |")
a += ["", "**Landing-page checklist (all Bangalore pages):** H1 matches the ad group; WhatsApp + call buttons above the fold; quote form (#quote) on the page; "
      "proof films; FAQ answering price, office and language; page tagged `data-service`/`data-city` for GA4; mobile sticky WhatsApp/Call bar."]
(D / "GOOGLE_ADS_BANGALORE.md").write_text("\n".join(a) + "\n")

rows = ["# Page inventory\n", "| URL | Type | Title | Words |", "|---|---|---|---|"]
for p in sorted(ROOT.rglob("index.html")):
    rel = p.relative_to(ROOT)
    if {"src", "tools", "docs", "data", "ig", ".git"} & set(rel.parts): continue
    s = p.read_text()
    t = html.unescape((re.search(r"<title>(.*?)</title>", s) or [0, ""])[1])
    kind = (re.search(r'data-page-type="([^"]*)"', s) or [0, "page"])[1]
    m = re.search(r"<main[^>]*>(.*)</main>", s, re.S)
    words = len(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", m[1] if m else s, flags=re.S)).split())
    u = "/" + str(rel.parent).replace(".", "") + ("/" if str(rel.parent) != "." else "")
    rows.append(f"| {u.replace('//','/')} | {kind} | {t} | {words} |")
(D / "PAGES.md").write_text("\n".join(rows) + "\n")
print("reports written:", [f.name for f in D.glob("*.md")])
