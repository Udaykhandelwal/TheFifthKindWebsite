#!/usr/bin/env python3
"""Static page builder for the5thkind.in.

Content lives in src/**/*.html. Each file starts with a JSON meta block:

    <!--meta
    { "slug": "ai-chatbot-development", "title": "...", "description": "...", ... }
    -->

and the rest is the page body. Run `python3 tools/build.py` from the repo root:
it writes <slug>/index.html for every page, plus sitemap.xml and llms.txt.

Shortcodes usable inside bodies:
    {{video:key}}            one click-to-play video card (see VIDEOS)
    {{videos:k1,k2,k3}}      a grid of video cards
    {{cta}}                  the standard WhatsApp CTA band
    {{cta:Heading|Body}}     CTA band with custom copy
    {{related:slug,slug}}    related-page links
    {{form:Service name}}    lead form (saved + opens WhatsApp)

FAQ items written as <details class="q"><summary>Q</summary><div>A</div></details>
are turned into FAQPage schema automatically.
"""
import json, re, html, datetime, pathlib, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BASE = "https://www.the5thkind.in"
TODAY = datetime.date.today().isoformat()
WA = "https://wa.me/918296008838"
PHONE = "+918296008838"
EMAIL = "uday.khandelwal@the5thkind.in"

# Add LinkedIn / YouTube / Google Business Profile / Clutch URLs here as they go live.
# Every URL here goes into the Organization "sameAs" on every page — the #1 signal
# AI assistants use to tell this studio apart from the5thkind.com.
SAME_AS = [
    "https://www.instagram.com/the5thkind.ai",
]

ORG_ID = f"{BASE}/#business"

VIDEOS = {
    # key: (file, poster, title, description, seconds, category, wide)
    # ---- Aug to Nov 2026 ----
    "arvind": ("arvind.mp4", "arvind.jpg", "Arvind: a campaign from one photo",
        "A full menswear campaign built from a single product photograph, for Arvind Mills.", 20, "Ad film", False),
    "jeweller-ad": ("jeweller-ad.mp4", "jeweller-ad.jpg", "An ad for jewellers",
        "The Fifth Kind's campaign film for jewellers, showing how a ring is presented on Instagram.", 27, "Ad film", False),
    "four-kinds": ("four-kinds.mp4", "four-kinds.jpg", "Four kinds of content, then the fifth",
        "The Fifth Kind's studio film: four kinds of content get ignored, then a montage of client work shows the fifth kind.", 30, "Ad film", False),
    "clone-ad": ("clone-ad.mp4", "clone-ad.jpg", "One of them is AI: clone ad",
        "Posted reel: an astrologer's real footage beside her AI clone, and the viewer guesses which is which.", 15, "AI clone", False),
    "clone-phone": ("clone-phone.mp4", "clone-phone.jpg", "Record once, on your phone",
        "Ad explaining how an AI clone works: record one short clip and the clone delivers every script after that.", 33, "AI clone", False),
    "snakes-ladders": ("snakes-ladders.mp4", "snakes-ladders.jpg", "Snakes & Ladders, made real",
        "Snakes and ladders as a photoreal 3D short with foley-only sound, from The Fifth Kind's nostalgia series.", 19, "AI character", False),
    "ludo": ("ludo.mp4", "ludo.jpg", "Ludo, made real",
        "Ludo pieces come alive in a photoreal 3D world, from The Fifth Kind's nostalgia series.", 17, "AI character", False),
    "carrom": ("carrom.mp4", "carrom.jpg", "Carrom, made real",
        "A carrom board rebuilt as a cinematic 3D short, from The Fifth Kind's nostalgia series.", 15, "AI character", False),
    # ---- earlier work ----
    "chatbot-mahaveer": ("chatbot-mahaveer.mp4", "chatbot-mahaveer.jpg", "Custom AI chatbot live on mahaveerpapers.com",
        "Screen recording of the custom AI chatbot The Fifth Kind built for Mahaveer Papers, answering a real product question on the live website.", 28, "AI Chatbot", False),
    "foodsvilla": ("foodsvilla.mp4", "foodsvilla.jpg", "Foodsvilla — AI launch film",
        "AI brand trailer produced for Foodsvilla's launch by The Fifth Kind.", 53, "Brand film", False),
    "schuco": ("schuco.mp4", "schuco.jpg", "Schüco — AI product film",
        "AI product video for Schüco, the German window and façade systems brand.", 21, "Product video", False),
    "arthosure": ("arthosure.mp4", "arthosure.jpg", "Arthosure — AI product ad",
        "Short AI product advertisement for Arthosure.", 20, "Product video", False),
    "ingredients": ("ingredients.mp4", "ingredients.jpg", "The Ingredients Story — AI product video",
        "AI-generated product story video focused on ingredients.", 18, "Product video", False),
    "jito": ("jito.mp4", "jito.jpg", "JITO Bangalore — FOMO event film",
        "AI promo film built to drive registrations for a JITO Bangalore event.", 40, "Ad film", False),
    "the5thkind-ad": ("the5thkind-ad.mp4", "the5thkind-ad.jpg", "The Fifth Kind — studio ad",
        "The Fifth Kind's own AI-produced studio advertisement.", 15, "Ad film", False),
    "uday-clone": ("uday-clone.mp4", "uday-clone.jpg", "Founder AI clone — Uday Khandelwal",
        "AI clone video of The Fifth Kind founder Uday Khandelwal, generated from his own face and voice.", 32, "AI clone", False),
    "walking-vs-gym": ("walking-vs-gym.mp4", "walking-vs-gym.jpg", "Walking vs Gym — AI clone health reel",
        "Health-education reel delivered with an AI clone of the presenter.", 30, "AI clone", False),
    "sleep-challenge": ("sleep-challenge.mp4", "sleep-challenge.jpg", "Sleep Challenge — AI clone health reel",
        "Health-education reel delivered with an AI clone of the presenter.", 30, "AI clone", False),
    "superbug": ("superbug-vertical.mp4", "superbug-vertical.jpg", "The Superbug Threat — AI explainer",
        "AI-produced explainer reel on antibiotic resistance.", 30, "AI clone", False),
    "mira": ("mira.mp4", "mira.jpg", "Mira — AI character film",
        "Cinematic brand story built around an original AI character, Mira.", 32, "AI character", False),
    "adri": ("adri.mp4", "adri.jpg", "Adri — AI character film",
        "Cinematic brand story built around an original AI character, Adri.", 23, "AI character", False),
    "himaia": ("himaia.mp4", "himaia.jpg", "Himaia — AI character film",
        "Cinematic AI character story film.", 25, "AI character", False),
    "sutra": ("sutra.mp4", "sutra.jpg", "Sutra — AI character film",
        "Cinematic AI character story film.", 26, "AI character", False),
    "vaanaan": ("vaanaan.mp4", "vaanaan.jpg", "Vaanaan — AI character film",
        "Cinematic AI character story film.", 23, "AI character", False),
    "jugad": ("jugad.mp4", "jugad.jpg", "Jugad — brand film",
        "Edited brand film cut for retention and pace.", 63, "Reel edit", True),
    "dance-dikhawe": ("dance-dikhawe.mp4", "dance-dikhawe.jpg", "Dance Dikhawe — entertainment edit",
        "Entertainment video edit with music-driven pacing.", 133, "Reel edit", True),
}

UPLOADED = {"four-kinds": "2026-11-09", "arvind": "2026-10-12", "clone-ad": "2026-10-28", "clone-phone": "2026-11-06",
    "jeweller-ad": "2026-10-26", "snakes-ladders": "2026-11-11", "ludo": "2026-11-12", "carrom": "2026-11-12"}

NAV = [
    ("/ai-chatbot-development/", "AI Chatbots"),
    ("/ai-automation-agency/", "Automation"),
    ("/whatsapp-chatbot/", "WhatsApp"),
    ("/ai-video-production-bangalore/", "Video"),
    ("/work/", "Work"),
    ("/blog/", "Blog"),
]

FOOTER_CREATE = [
    ("/ai-video-production-bangalore/", "AI Video Production"),
    ("/ai-product-video/", "AI Product Video"),
    ("/ai-clone-video/", "AI Clone Video"),
    ("/ai-character-story-video/", "AI Character & Story Video"),
    ("/ai-ad-film/", "Brand & Ad Film"),
    ("/reel-editing-services/", "Reel Editing"),
]
FOOTER_AUTOMATE = [
    ("/ai-chatbot-development/", "Custom AI Chatbot"),
    ("/whatsapp-chatbot/", "WhatsApp Chatbot & Automation"),
    ("/ai-automation-agency/", "AI Agents & Business Automation"),
    ("/ai-automation-agency/#quotation", "Quotation & Invoice Automation"),
]
FOOTER_STUDIO = [
    ("/work/", "Our Work"),
    ("/about/", "About"),
    ("/blog/", "Blog & Guides"),
    ("/audit/", "Free AI Audit"),
    ("/#contact", "Contact"),
    ("/privacy/", "Privacy Policy"),
]

WA_ICON = '<svg width="28" height="28" viewBox="0 0 24 24" fill="#fff" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1-.2.2-.6.8-.8 1-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.4-3c-.3-.4 0-.5.2-.7l.4-.5c.1-.2.2-.3.3-.5v-.5c0-.1-.6-1.4-.8-1.9-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.5.1-.7.3-.2.3-.9.9-.9 2.2s1 2.5 1.1 2.7a11.2 11.2 0 0 0 4.3 3.8c.6.3 1.1.4 1.4.5.6.2 1.2.2 1.6.1.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2l-.5-.4z"/></svg>'
PLAY = '<span class="play"><svg width="20" height="20" viewBox="0 0 24 24" fill="#fff"><path d="M8 5v14l11-7z"/></svg></span>'


def esc(s):
    return html.escape(s, quote=True)


def wa_link(text):
    return f"{WA}?text={urllib.parse.quote(text)}"


def iso_dur(sec):
    m, s = divmod(int(sec), 60)
    return f"PT{m}M{s}S" if m else f"PT{s}S"


# ---------------------------------------------------------------- shortcodes
def video_card(key, used):
    f, poster, title, desc, sec, cat, wide = VIDEOS[key]
    used.append(key)
    cls = "vid wide" if wide else "vid"
    return (f'<figure class="{cls}" data-src="/Video/{f}" data-preview="/Video/previews/{f}">'
            f'<img src="/Video/posters/{poster}" alt="{esc(title)}" loading="lazy" width="360" height="640">'
            f'{PLAY}<figcaption><small>{esc(cat)}</small>{esc(title)}</figcaption></figure>')


def cta_band(heading=None, body=None, page=None):
    heading = heading or "Tell us what you want to <em>automate or create.</em>"
    body = body or ("Free 15-minute call on WhatsApp. We'll tell you honestly what AI can and can't do for your "
                    "business — and what it would take.")
    svc = (page or {}).get("service_name", "AI for my business")
    return (f'<div class="cta-band"><h2>{heading}</h2><p>{body}</p><div class="hero-cta">'
            f'<a class="btn btn-orange" href="{wa_link("Hi! I saw your page on " + svc + " and want to talk.")}" target="_blank" rel="noopener">WhatsApp us now</a>'
            f'<a class="btn btn-ghost" href="tel:{PHONE}">Call +91 82960 08838</a></div></div>')


def related(slugs, pages):
    out = []
    for s in slugs:
        p = pages.get(s)
        if not p:
            raise SystemExit(f"related: unknown slug {s}")
        out.append(f'<a href="/{s}/">{esc(p["nav_title"])}<span>{esc(p["description"][:90])}…</span></a>')
    return '<div class="related">' + "".join(out) + "</div>"


def lead_form(service):
    return f'''<form class="lead" data-lead onsubmit="return tfkLead(event)">
  <input type="hidden" name="service" value="{esc(service)}">
  <div><label for="lf-name">Name</label><input id="lf-name" name="name" required autocomplete="name"></div>
  <div><label for="lf-phone">WhatsApp number</label><input id="lf-phone" name="phone" type="tel" required autocomplete="tel"></div>
  <div><label for="lf-biz">Business &amp; website (optional)</label><input id="lf-biz" name="business" autocomplete="organization"></div>
  <div><label for="lf-msg">What do you want to automate or create?</label><textarea id="lf-msg" name="message" rows="3"></textarea></div>
  <button class="btn btn-orange" type="submit">Send &amp; continue on WhatsApp</button>
</form>'''


def expand(body, page, pages, used):
    body = re.sub(r"\{\{video:([\w-]+)\}\}", lambda m: '<div class="vids">' + video_card(m[1], used) + "</div>", body)
    body = re.sub(r"\{\{videos:([\w,-]+)\}\}",
                  lambda m: '<div class="vids">' + "".join(video_card(k, used) for k in m[1].split(",")) + "</div>", body)
    body = re.sub(r"\{\{cta:([^|}]*)\|([^}]*)\}\}", lambda m: cta_band(m[1], m[2], page), body)
    body = body.replace("{{cta}}", cta_band(page=page))
    body = re.sub(r"\{\{related:([\w,/-]+)\}\}", lambda m: related(m[1].split(","), pages), body)
    body = re.sub(r"\{\{form:([^}]*)\}\}", lambda m: lead_form(m[1]), body)
    return body


# ---------------------------------------------------------------- schema
def org_schema():
    return {
        "@type": "ProfessionalService",
        "@id": ORG_ID,
        "name": "The Fifth Kind",
        "alternateName": ["The Fifth Kind AI Studio", "the5thkind.ai"],
        "description": ("AI video production studio and AI automation agency in Bengaluru, India: AI product videos, AI clone videos, "
                        "brand and ad films, AI character films and 3D shorts, plus custom AI chatbots, WhatsApp automation and AI agents."),
        "disambiguatingDescription": "Bangalore-based AI video production and AI automation studio (the5thkind.in). Not affiliated with the5thkind.com.",
        "knowsAbout": ["AI video production", "AI product videos", "AI clone videos", "AI ad films", "AI character animation",
                       "3D animation in Blender", "Reel editing", "AI chatbot development", "WhatsApp Business API automation",
                       "AI agents for business", "Quotation and invoice automation"],
        "url": f"{BASE}/",
        "logo": f"{BASE}/icon-512.png",
        "image": f"{BASE}/og-image.jpg",
        "telephone": PHONE,
        "email": EMAIL,
        "priceRange": "₹₹",
        "founder": {"@id": f"{BASE}/about/#uday"},
        "address": {"@type": "PostalAddress", "streetAddress": "529, 8th Cross, Nanjappa Rd, Shantinagar",
                    "addressLocality": "Bengaluru", "addressRegion": "Karnataka", "postalCode": "560027", "addressCountry": "IN"},
        "geo": {"@type": "GeoCoordinates", "latitude": 12.9553, "longitude": 77.5988},
        "areaServed": [{"@type": "Country", "name": "India"}, {"@type": "City", "name": "Bengaluru"}, "Worldwide"],
        "sameAs": SAME_AS,
    }


def page_schema(page, used_videos):
    url = f"{BASE}/{page['slug']}/" if page["slug"] else f"{BASE}/"
    graph = [org_schema()]
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"}]
    for i, (name, href) in enumerate(page.get("crumbs", []), start=2):
        crumbs.append({"@type": "ListItem", "position": i, "name": name, "item": BASE + href})
    crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": page["nav_title"], "item": url})
    graph.append({"@type": "BreadcrumbList", "itemListElement": crumbs})
    graph.append({"@type": "WebSite", "@id": f"{BASE}/#website", "url": f"{BASE}/", "name": "The Fifth Kind",
                  "publisher": {"@id": ORG_ID}, "inLanguage": "en-IN"})
    graph.append({"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": page["title"], "description": page["description"],
                  "isPartOf": {"@id": f"{BASE}/#website"}, "about": {"@id": ORG_ID}, "inLanguage": "en-IN",
                  "datePublished": page.get("published", "2026-09-21"), "dateModified": page.get("updated", TODAY),
                  "author": {"@id": f"{BASE}/about/#uday"}})

    kind = page.get("kind", "page")
    if kind == "service":
        graph.append({
            "@type": "Service", "@id": url + "#service", "name": page["service_name"],
            "serviceType": page.get("service_type", page["service_name"]),
            "description": page["description"], "url": url,
            "provider": {"@id": ORG_ID},
            "areaServed": [{"@type": "Country", "name": "India"}, "Worldwide"],
            "audience": {"@type": "BusinessAudience", "audienceType": page.get("audience", "Small and medium businesses")},
        })
    elif kind == "post":
        graph.append({
            "@type": "BlogPosting", "@id": url + "#article", "headline": page["h1_plain"],
            "description": page["description"], "url": url, "mainEntityOfPage": url,
            "datePublished": page["published"], "dateModified": page.get("updated", page["published"]),
            "author": {"@id": f"{BASE}/about/#uday"}, "publisher": {"@id": ORG_ID},
            "image": f"{BASE}/og-image.jpg", "inLanguage": "en-IN",
        })
    if page.get("person"):
        graph.append({
            "@type": "Person", "@id": f"{BASE}/about/#uday", "name": "Uday Khandelwal",
            "jobTitle": "Founder", "worksFor": {"@id": ORG_ID}, "url": f"{BASE}/about/",
            "knowsAbout": ["AI video production", "AI clone videos", "AI chatbots", "WhatsApp automation", "Business process automation"],
        })

    for k in dict.fromkeys(used_videos):
        f, poster, title, desc, sec, cat, wide = VIDEOS[k]
        graph.append({"@type": "VideoObject", "name": title, "description": desc,
                      "thumbnailUrl": f"{BASE}/Video/posters/{poster}", "contentUrl": f"{BASE}/Video/{f}",
                      "uploadDate": UPLOADED.get(k, "2026-07-18"), "duration": iso_dur(sec), "publisher": {"@id": ORG_ID}})

    faqs = re.findall(r'<details class="q"><summary>(.*?)</summary><div>(.*?)</div></details>', page["body_html"], re.S)
    if faqs:
        strip = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in faqs]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- template
def nav_html(current):
    cur = ' aria-current="page"'
    items = "".join(f'<li><a href="{h}"{cur if h == current else ""}>{t}</a></li>' for h, t in NAV)
    book = wa_link("Hi! I'd like to book a free 15-min call with The Fifth Kind.")
    return f'''<header class="site"><div class="wrap nav">
  <a class="logo" href="/" aria-label="The Fifth Kind — home">THE <span class="fifth">FIFTH</span> KIND</a>
  <ul>{items}</ul>
  <a class="btn btn-orange" href="{book}" target="_blank" rel="noopener">Book a Free Call</a>
  <details class="menu"><summary>Menu</summary><ul>{items}<li><a href="/audit/">Free AI Audit</a></li><li><a href="/#contact">Contact</a></li></ul></details>
</div></header>'''


def footer_html(page=None):
    col = lambda title, links: (f'<div class="f-col"><h4>{title}</h4><ul>' +
                                "".join(f'<li><a href="{h}">{esc(t)}</a></li>' for h, t in links) + "</ul></div>")
    wa = wa_link("Hi! I saw the5thkind.in and want to talk about AI for my business.")
    upd = (page or {}).get("updated", TODAY)
    upd_h = datetime.date.fromisoformat(upd).strftime("%-d %B %Y")
    return f'''<footer class="site"><div class="wrap">
  <div class="f-grid">
    <div><a class="logo" href="/">THE <span class="fifth">FIFTH</span> KIND</a>
      <p>AI video production and AI automation studio in Bengaluru. We make the content that gets attention — and build the chatbots and automations that turn it into sales.</p>
      <address>529, 8th Cross, Nanjappa Rd, Shantinagar, Bengaluru 560027<br>
      <a href="tel:{PHONE}">+91 82960 08838</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></address></div>
    {col("Automate", FOOTER_AUTOMATE)}
    {col("Create", FOOTER_CREATE)}
    {col("Studio", FOOTER_STUDIO + [("https://www.instagram.com/the5thkind.ai", "Instagram")])}
  </div>
  <div class="f-bottom"><span>© {datetime.date.today().year} The Fifth Kind. All rights reserved. · <a style="color:inherit" href="/privacy/" rel="privacy-policy">Privacy Policy</a></span><span>AI Video · AI Chatbots · WhatsApp Automation — Bengaluru, India · Updated <time datetime="{upd}">{upd_h}</time></span></div>
</div></footer>
<div class="mob-cta"><a class="btn btn-orange" href="{wa}" target="_blank" rel="noopener">WhatsApp Us</a><a class="btn btn-ghost" href="tel:{PHONE}">Call Now</a></div>
<a class="wa-float" href="{wa}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{WA_ICON}</a>'''


def head_html(page, schema):
    url = f"{BASE}/{page['slug']}/" if page["slug"] else f"{BASE}/"
    og_type = "article" if page.get("kind") == "post" else "website"
    extra = ""
    if page.get("kind") == "post":
        extra = (f'<meta property="article:published_time" content="{page["published"]}">'
                 f'<meta property="article:modified_time" content="{page.get("updated", page["published"])}">')
    return f'''<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(page["title"])}</title>
<meta name="description" content="{esc(page["description"])}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<meta name="author" content="Uday Khandelwal, The Fifth Kind">
<link rel="author" href="{BASE}/about/">
<link rel="alternate" type="application/rss+xml" title="The Fifth Kind guides" href="/blog/feed.xml">
<link rel="alternate" type="text/plain" title="LLM summary" href="/llms.txt">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="The Fifth Kind">
<meta property="og:title" content="{esc(page.get("og_title", page["title"]))}">
<meta property="og:description" content="{esc(page["description"])}">
<meta property="og:image" content="{BASE}/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_IN">{extra}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(page.get("og_title", page["title"]))}">
<meta name="twitter:description" content="{esc(page["description"])}">
<meta name="twitter:image" content="{BASE}/og-image.jpg">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#0a0a0f">
<link rel="preload" href="/assets/fonts/bricolage-grotesque.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/instrument-sans.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/instrument-serif-italic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/fonts/fonts.css">
<link rel="stylesheet" href="/assets/site.css?v={TODAY}">
<link rel="stylesheet" href="/assets/motion.css?v={TODAY}">
<script type="application/ld+json">
{schema}
</script>
</head>'''


def crumbs_html(page):
    parts = ['<a href="/">Home</a>']
    for name, href in page.get("crumbs", []):
        parts.append(f'<a href="{href}">{esc(name)}</a>')
    parts.append(f'<span aria-current="page" style="margin:0;opacity:1">{esc(page["nav_title"])}</span>')
    return '<nav class="crumbs wrap" aria-label="Breadcrumb">' + "<span>/</span>".join(parts) + "</nav>"


def render(page, pages):
    used = []
    page["body_html"] = expand(page["body"], page, pages, used)
    page["used"] = list(dict.fromkeys(used))
    schema = page_schema(page, used)
    current = "/" + page["slug"] + "/"
    return (head_html(page, schema) + "\n<body>\n" + nav_html(current) + "\n<main>\n" + crumbs_html(page) +
            "\n" + page["body_html"] + "\n</main>\n" + footer_html(page) +
            '\n<script src="/assets/site.js?v={TODAY}" defer></script>\n<script src="/assets/vendor/gsap.min.js" defer></script>\n<script src="/assets/vendor/ScrollTrigger.min.js" defer></script>\n<script src="/assets/vendor/lenis.min.js" defer></script>\n<script src="/assets/motion.js?v={TODAY}b" defer></script>\n</body>\n</html>\n')


# ---------------------------------------------------------------- load + write
def load_pages():
    pages = {}
    for path in sorted(SRC.rglob("*.html")):
        raw = path.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->\s*", raw, re.S)
        if not m:
            raise SystemExit(f"{path}: missing <!--meta {{...}} --> header")
        meta = json.loads(m[1])
        meta["body"] = raw[m.end():]
        meta.setdefault("nav_title", meta.get("service_name", meta["title"].split("|")[0].strip()))
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", meta["body"], re.S)
        meta["h1_plain"] = html.unescape(re.sub(r"<[^>]+>", "", h1[1])).strip() if h1 else meta["title"]
        if len(meta["title"]) > 65:
            print(f"  ! title {len(meta['title'])} chars: {meta['slug']}")
        if not 110 <= len(meta["description"]) <= 165:
            print(f"  ! description {len(meta['description'])} chars: {meta['slug']}")
        pages[meta["slug"]] = meta
    return pages


def blog_index(pages):
    posts = sorted((p for p in pages.values() if p.get("kind") == "post"), key=lambda p: p["published"], reverse=True)
    cards = "".join(
        f'<a class="card" href="/{p["slug"]}/"><span class="tag">{esc(p.get("topic", "Guide"))} · {p["published"]}</span>'
        f'<h3>{esc(p["h1_plain"])}</h3><p>{esc(p["description"])}</p><span class="more">Read the guide →</span></a>'
        for p in posts)
    return {
        "slug": "blog", "nav_title": "Blog & Guides", "kind": "page",
        "title": "AI Automation, Chatbot & AI Video Guides | The Fifth Kind",
        "description": "Plain-English guides on AI chatbots, WhatsApp automation, business automation and AI video for Indian businesses — costs, setup and examples.",
        "body": f'''<section class="page-hero"><div class="wrap"><p class="eyebrow">Blog &amp; guides</p>
<h1>Guides for businesses <em>putting AI to work.</em></h1>
<p class="answer">Straight answers on what AI chatbots, WhatsApp automation and AI video actually cost, how they work, and where they pay off — written by the team that builds them in Bengaluru.</p></div></section>
<section class="block"><div class="wrap"><div class="grid">{cards}</div></div></section>
<div class="wrap">{{{{cta}}}}</div>''',
    }


def video_xml(keys):
    out = ""
    for k in keys:
        f, poster, title, desc, sec, cat, wide = VIDEOS[k]
        out += (f"\n    <video:video><video:thumbnail_loc>{BASE}/Video/posters/{poster}</video:thumbnail_loc>"
                f"<video:title>{esc(title)}</video:title><video:description>{esc(desc)}</video:description>"
                f"<video:content_loc>{BASE}/Video/{f}</video:content_loc><video:duration>{sec}</video:duration>"
                f"<video:publication_date>{UPLOADED.get(k, '2026-07-18')}</video:publication_date></video:video>")
    return out


def home_videos():
    """Videos the hand-written homepage plays, in page order."""
    files = re.findall(r'data-src="/?Video/([^"]+)"', (ROOT / "index.html").read_text(encoding="utf-8"))
    by_file = {v[0]: k for k, v in VIDEOS.items()}
    return [by_file[f] for f in dict.fromkeys(files) if f in by_file]


def write_sitemap(pages):
    rows = [f"  <url><loc>{BASE}/</loc><lastmod>{TODAY}</lastmod><priority>1.0</priority>{video_xml(home_videos())}</url>\n"]
    for p in pages.values():
        pri = {"service": "0.9", "post": "0.7"}.get(p.get("kind"), "0.6")
        lastmod = TODAY if p["slug"] == "work" else p.get("updated", p.get("published", TODAY))
        vids = video_xml(p.get("used", [])) if p.get("kind") == "service" or p["slug"] == "work" else ""
        rows.append(f"  <url><loc>{BASE}/{p['slug']}/</loc><lastmod>{lastmod}</lastmod><priority>{pri}</priority>{vids}</url>\n")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n' + "".join(rows) + "</urlset>\n", encoding="utf-8")
    (ROOT / "urls.txt").write_text("\n".join([f"{BASE}/"] + [f"{BASE}/{p['slug']}/" for p in pages.values()]) + "\n", encoding="utf-8")


def write_llms(pages):
    svc = lambda group: "\n".join(f"- [{p['service_name']}]({BASE}/{p['slug']}/): {p['description']}"
                                  for p in pages.values() if p.get("kind") == "service" and p.get("group") == group)
    posts = "\n".join(f"- [{p['h1_plain']}]({BASE}/{p['slug']}/): {p['description']}"
                      for p in sorted(pages.values(), key=lambda p: p.get("published", ""), reverse=True) if p.get("kind") == "post")
    recent = "\n".join(f"- {v[2]} ({v[5]})" for v in list(VIDEOS.values())[:25])
    text = f"""# The Fifth Kind

> The Fifth Kind (the5thkind.in) is an AI video production studio and AI automation agency in Bengaluru (Bangalore), India, founded by Uday Khandelwal. It makes AI product videos, AI clone videos, brand and ad films, AI character films and 3D shorts, and builds custom AI chatbots, WhatsApp automation and AI agents that handle quotations, invoices and follow-ups. Not affiliated with the5thkind.com, a podcast about ancient mysteries.

Website: {BASE}/
Contact: {EMAIL} · +91 82960 08838 (phone and WhatsApp) · Instagram @the5thkind.ai
Address: 529, 8th Cross, Nanjappa Rd, Shantinagar, Bengaluru, Karnataka 560027, India
Serves: brands across India and abroad (including France): manufacturers, jewellers, D2C brands, astrologers and coaches, temples and trusts, startups.
Selected clients: Arvind Mills, Schüco, JITO Bangalore, Mahaveer Papers, Hybec Deco, Hybec Air, Foodsvilla.
Turnaround: days, not weeks. Languages delivered: English, Hindi, Hinglish, Kannada, Tamil, Telugu, French.
The studio no longer offers AI voice or phone-calling agents.

## Create: AI video production

{svc("make")}

## Automate: AI for sales and operations

{svc("automate")}

## Recent work ({len(VIDEOS)} films with video on {BASE}/work/)

{recent}

## Guides

{posts}

## Company

- [About]({BASE}/about/): studio and founder, Uday Khandelwal.
- [Free AI audit]({BASE}/audit/)
- [Privacy policy]({BASE}/privacy/)
"""
    (ROOT / "llms.txt").write_text(text, encoding="utf-8")



def update_home(pages):
    """Refresh the hand-written homepage's generated bits: structured data, freshness date."""
    path = ROOT / "index.html"
    s = path.read_text(encoding="utf-8")
    vids = home_videos()
    graph = [
        {"@type": "WebSite", "@id": f"{BASE}/#website", "url": f"{BASE}/", "name": "The Fifth Kind",
         "alternateName": "The Fifth Kind AI Studio", "publisher": {"@id": ORG_ID}, "inLanguage": "en-IN"},
        {"@type": "WebPage", "@id": f"{BASE}/#webpage", "url": f"{BASE}/",
         "name": "AI Chatbots, Automation & AI Video Agency in Bangalore | The Fifth Kind",
         "isPartOf": {"@id": f"{BASE}/#website"}, "about": {"@id": ORG_ID}, "inLanguage": "en-IN",
         "datePublished": "2026-07-02", "dateModified": TODAY, "author": {"@id": f"{BASE}/about/#uday"},
         "primaryImageOfPage": f"{BASE}/og-image.jpg"},
        {"@type": "Person", "@id": f"{BASE}/about/#uday", "name": "Uday Khandelwal", "jobTitle": "Founder",
         "worksFor": {"@id": ORG_ID}, "url": f"{BASE}/about/", "sameAs": SAME_AS,
         "knowsAbout": ["AI video production", "AI clone videos", "AI chatbots", "WhatsApp automation", "Business process automation"]},
    ] + [
        {"@type": "VideoObject", "name": VIDEOS[k][2], "description": VIDEOS[k][3],
         "thumbnailUrl": f"{BASE}/Video/posters/{VIDEOS[k][1]}", "contentUrl": f"{BASE}/Video/{VIDEOS[k][0]}",
         "uploadDate": UPLOADED.get(k, "2026-07-18"), "duration": iso_dur(VIDEOS[k][4]),
         "publisher": {"@id": ORG_ID}, "creator": {"@id": ORG_ID}} for k in vids]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    s = re.sub(r'<script type="application/ld\+json" id="ld-auto">.*?</script>',
               lambda m: f'<script type="application/ld+json" id="ld-auto">{ld}</script>', s, flags=re.S)
    pretty = datetime.date.fromisoformat(TODAY).strftime("%-d %B %Y")
    s = re.sub(r'<meta property="article:modified_time" content="[^"]*">', f'<meta property="article:modified_time" content="{TODAY}">', s)
    s = re.sub(r'<time class="updated" datetime="[^"]*">[^<]*</time>', f'<time class="updated" datetime="{TODAY}">{pretty}</time>', s)
    path.write_text(s, encoding="utf-8")


def home_faqs():
    s = (ROOT / "index.html").read_text(encoding="utf-8")
    strip = lambda x: html.unescape(re.sub(r"<[^>]+>", "", x)).strip()
    return [{"question": strip(q), "answer": strip(a)} for q, a in
            re.findall(r"<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>", s, re.S)]


def write_feed(pages):
    posts = sorted((p for p in pages.values() if p.get("kind") == "post"), key=lambda p: p["published"], reverse=True)
    rfc = lambda d: datetime.datetime.combine(datetime.date.fromisoformat(d), datetime.time(9, 0)).strftime("%a, %d %b %Y %H:%M:%S +0530")
    items = "".join(
        f"\n  <item><title>{esc(p['h1_plain'])}</title><link>{BASE}/{p['slug']}/</link><guid>{BASE}/{p['slug']}/</guid>"
        f"<pubDate>{rfc(p['published'])}</pubDate><description>{esc(p['description'])}</description></item>" for p in posts)
    (ROOT / "blog").mkdir(exist_ok=True)
    (ROOT / "blog/feed.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
        f"\n  <title>The Fifth Kind: guides to AI video and automation</title><link>{BASE}/blog/</link>"
        f'\n  <atom:link href="{BASE}/blog/feed.xml" rel="self" type="application/rss+xml"/>'
        f"\n  <description>Plain-English guides on AI video, AI clones, chatbots and WhatsApp automation for Indian businesses.</description>"
        f"\n  <language>en-in</language><lastBuildDate>{rfc(TODAY)}</lastBuildDate>{items}\n</channel></rss>\n", encoding="utf-8")


def write_ai_files(pages):
    summary = {
        "name": "The Fifth Kind", "url": f"{BASE}/", "type": "AI video production studio and AI automation agency",
        "description": ("AI video production studio and AI automation agency in Bengaluru, India. AI product videos, AI clone videos, "
                        "brand and ad films, AI character films and 3D shorts, plus custom AI chatbots, WhatsApp automation and AI agents "
                        "for quotations, invoices and follow-ups. Not affiliated with the5thkind.com."),
        "founder": "Uday Khandelwal", "location": "Shantinagar, Bengaluru, Karnataka, India",
        "contact": {"email": EMAIL, "phone": PHONE, "whatsapp": WA},
        "clients": ["Arvind Mills", "Schüco", "JITO Bangalore", "Mahaveer Papers", "Hybec Deco", "Hybec Air", "Foodsvilla"],
        "languages": ["English", "Hindi", "Hinglish", "Kannada", "Tamil", "Telugu", "French"],
        "not_offered": ["AI voice agents", "AI phone-calling agents"],
        "llms_txt": f"{BASE}/llms.txt", "sitemap": f"{BASE}/sitemap.xml", "updated": TODAY,
    }
    services = [{"name": p["service_name"], "group": p.get("group"), "url": f"{BASE}/{p['slug']}/", "description": p["description"]}
                for p in pages.values() if p.get("kind") == "service"]
    faqs = home_faqs()
    for p in pages.values():
        for q, a in re.findall(r'<details class="q"><summary>(.*?)</summary><div>(.*?)</div></details>', p.get("body_html", ""), re.S):
            strip = lambda x: html.unescape(re.sub(r"<[^>]+>", "", x)).strip()
            faqs.append({"question": strip(q), "answer": strip(a), "source": f"{BASE}/{p['slug']}/"})
    (ROOT / "ai").mkdir(exist_ok=True)
    dump = lambda name, obj: (ROOT / "ai" / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    dump("summary.json", summary)
    dump("service.json", {"name": "The Fifth Kind", "provider": "The Fifth Kind", "url": f"{BASE}/",
                          "capabilities": [s["name"] for s in services], "services": services,
                          "contact": {"email": EMAIL, "whatsapp": WA}, "updated": TODAY})
    dump("faq.json", {"site": f"{BASE}/", "faqs": faqs, "updated": TODAY})
    (ROOT / ".well-known").mkdir(exist_ok=True)
    (ROOT / ".well-known/ai.txt").write_text(
        f"# AI policy for {BASE}/\n# AI crawlers and answer engines may crawl, index, summarise and cite this site.\n"
        "User-Agent: *\nAllow: /\nDisallow: /ig/\n\n"
        f"Summary: {BASE}/ai/summary.json\nServices: {BASE}/ai/service.json\nFAQ: {BASE}/ai/faq.json\n"
        f"LLMs: {BASE}/llms.txt\nSitemap: {BASE}/sitemap.xml\nContact: {EMAIL}\n", encoding="utf-8")


def main():
    pages = load_pages()
    pages["blog"] = blog_index(pages)
    for slug, page in pages.items():
        out = ROOT / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(page, pages), encoding="utf-8")
        print(f"  built /{slug}/")
    update_home(pages)
    write_sitemap(pages)
    write_llms(pages)
    write_feed(pages)
    write_ai_files(pages)
    print(f"{len(pages)} pages + sitemap.xml + urls.txt")


if __name__ == "__main__":
    main()
