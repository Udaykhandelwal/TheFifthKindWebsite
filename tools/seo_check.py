#!/usr/bin/env python3
"""SEO checks on the BUILT site: metadata, canonicals, H1, JSON-LD validity, alt text,
internal links, sitemap coverage, and near-duplicate content between location pages.
Run after build.py. Exit code 1 if anything fails."""
import re, json, html, pathlib, itertools, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {"src", "tools", "node_modules", ".git", "ig", "docs", "data"}
pages = [p for p in ROOT.rglob("index.html") if not SKIP & set(p.relative_to(ROOT).parts)]
sitemap = (ROOT / "sitemap.xml").read_text()
issues, titles, descs, texts = [], {}, {}, {}
types = {}
def main_text(s):
    m = re.search(r"<main[^>]*>(.*)</main>", s, re.S)
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", m[1] if m else s, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t).strip().lower()
for p in sorted(pages):
    s = p.read_text(encoding="utf-8")
    rel = p.relative_to(ROOT).parent.as_posix()
    url = "/" if rel == "." else f"/{rel}/"
    t = html.unescape((re.search(r"<title>(.*?)</title>", s, re.S) or [None, ""])[1])
    d = html.unescape((re.search(r'<meta name="description" content="([^"]*)"', s) or [None, ""])[1])
    c = re.search(r'<link rel="canonical" href="([^"]*)"', s)
    if not 20 <= len(t) <= 66: issues.append(f"{url}: title length {len(t)}")
    if not 100 <= len(d) <= 165: issues.append(f"{url}: description length {len(d)}")
    if not c or not c[1].endswith(url): issues.append(f"{url}: canonical {c and c[1]}")
    if len(re.findall(r"<h1[\s>]", s)) != 1: issues.append(f"{url}: H1 count")
    if "og:image" not in s: issues.append(f"{url}: no og:image")
    if 'name="robots" content="index' not in s and url != "/": issues.append(f"{url}: robots meta missing")
    titles.setdefault(t, []).append(url); descs.setdefault(d, []).append(url)
    for m in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S):
        try:
            j = json.loads(m)
            for node in j.get("@graph", [j]):
                types[node.get("@type")] = types.get(node.get("@type"), 0) + 1
        except Exception as e: issues.append(f"{url}: invalid JSON-LD ({e})")
    for img in re.findall(r"<img\b[^>]*>", s):
        if 'alt="' not in img: issues.append(f"{url}: img without alt")
    for h in set(re.findall(r'href="(/[^"#?]*)', s)):
        f = ROOT / h.lstrip("/")
        if not (f.exists() or (f / "index.html").exists()): issues.append(f"{url}: broken link {h}")
    if f"https://www.the5thkind.in{url}" not in sitemap: issues.append(f"{url}: not in sitemap")
    texts[url] = main_text(s)
for t, us in titles.items():
    if len(us) > 1: issues.append(f"duplicate title on {us}")
for d, us in descs.items():
    if len(us) > 1: issues.append(f"duplicate description on {us}")
# near-duplicate check: 5-word shingles, Jaccard, between pages that share a parent folder
def sh(t):
    w = t.split(); return {" ".join(w[i:i+5]) for i in range(len(w) - 4)}
groups = {}
for u in texts:
    parts = u.strip("/").split("/")
    if len(parts) == 2: groups.setdefault(parts[0], []).append(u)
worst = []
for g, us in groups.items():
    for a, b in itertools.combinations(us, 2):
        A, B = sh(texts[a]), sh(texts[b])
        j = len(A & B) / max(1, len(A | B))
        worst.append((round(j, 2), a, b))
worst.sort(reverse=True)
print(f"{len(pages)} pages checked")
print("JSON-LD types:", dict(sorted(types.items(), key=lambda x: -x[1])))
words = sorted((len(t.split()), u) for u, t in texts.items())
print("thinnest pages (words):", words[:5])
if worst:
    avg = sum(w[0] for w in worst) / len(worst)
    print(f"location-page similarity: max {worst[0][0]} ({worst[0][1]} vs {worst[0][2]}), average {avg:.2f}")
    for w in worst[:5]: print("  ", w)
    if worst[0][0] > 0.6: issues.append(f"near-duplicate pages over 60% overlap: {worst[0]}")
print("\n".join(issues) if issues else "ALL CHECKS PASSED")
sys.exit(1 if issues else 0)
