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
    {{proof:service-key}}    approved client quotes + starting price from data/proof.json (empty = nothing shown)

FAQ items written as <details class="q"><summary>Q</summary><div>A</div></details>
are turned into FAQPage schema automatically.
"""
import json, re, html, datetime, pathlib, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
import sys as _sys
_sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import seo_pages  # noqa: E402  location pages from data/*.json
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

# Runs in <head> before the page paints: a visit from a Google/Bing ad (click ID or paid UTM)
# marks the session, and site.css then hides menus and side links on service pages (focus mode).
AD_FLAG_JS = ('<script>(function(){try{var s=sessionStorage;'
              'if(/[?&](gclid|gbraid|wbraid|msclkid)=|[?&]utm_medium=(cpc|ppc|paid)(&|$)/i.test(location.search))s.setItem("tfk_ad","1");'
              'if(s.getItem("tfk_ad"))document.documentElement.classList.add("ad-visit")}catch(e){}})();</script>')

VIDEOS = {
    # key: (file, poster, title, description, seconds, category, wide)
    # Only final, client-approved, published work. Best first: llms.txt lists them in this order.
    "kora-brand": ("kora-brand.mp4", "kora-brand.jpg", "I'm Kora: brand film for Mahaveer Papers",
        "Brand and Meta-ad film for Kora, the AI paper expert The Fifth Kind built for Mahaveer Papers. Kora speaks in first person and answers real paper questions from designers, printers and brands.", 32, "Brand film", False),
    "kora-reveal": ("kora-reveal.mp4", "kora-reveal.jpg", "Meet Kora: launch film for Mahaveer Papers",
        "Launch film introducing Kora, the AI chatbot on mahaveerpapers.com, named after kora kaagaz, the blank sheet where every idea begins.", 34, "Launch film", False),
    "stump-kora": ("stump-kora.mp4", "stump-kora.jpg", "We tried to stump our AI: Kora for Mahaveer Papers",
        "Game-show reel for Mahaveer Papers: five paper questions, each harder, answered live by Kora, the AI paper expert The Fifth Kind built.", 29, "Campaign reel", False),
    "vs-the-mark": ("vs-the-mark.mp4", "vs-the-mark.jpg", "VS Signature: The Mark",
        "Jewellery film for VS Signature by Megha Jewellers: a gold ear cuff and the story of the mark a woman leaves.", 25, "Jewellery film", False),
    "vs-three-grams": ("vs-three-grams.mp4", "vs-three-grams.jpg", "VS Signature: three grams, six weeks",
        "Craft film for VS Signature by Megha Jewellers, showing the six weeks of hand work behind a three-gram piece.", 22, "Jewellery film", False),
    "vs-dasara": ("vs-dasara.mp4", "vs-dasara.jpg", "VS Signature: Dasara",
        "Festival film for VS Signature by Megha Jewellers, built around Dasara traditions at home.", 29, "Festival campaign", False),
    "velvet-festival": ("velvet-festival.mp4", "velvet-festival.jpg", "Velvet Lite 9KT: festival film",
        "Kannada festival film for Velvet Lite 9KT gold by Megha Jewellers.", 35, "Festival campaign", False),
    "vs-original-story": ("vs-original-story.mp4", "vs-original-story.jpg", "VS Signature: her original story",
        "Brand film for VS Signature by Megha Jewellers about women who sign their own story: a doctor, a teacher, an engineer.", 25, "Brand film", False),
    "amethyst": ("amethyst.mp4", "amethyst.jpg", "Amethyst: luxury jewellery film",
        "Macro jewellery film of an emerald-cut amethyst set in a halo of diamonds.", 23, "Jewellery film", False),
    "arvind": ("arvind.mp4", "arvind.jpg", "Arvind Mills: a campaign from one photo",
        "A full menswear campaign built from a single product photograph, for Arvind Mills.", 20, "AI campaign", False),
    "jeweller-ad": ("jeweller-ad.mp4", "jeweller-ad.jpg", "An ad film for jewellers",
        "The Fifth Kind's campaign film for jewellers, showing how a piece is presented on Instagram.", 27, "Ad film", False),
    "mira": ("mira.mp4", "mira.jpg", "Mira: fragrance film",
        "Cinematic AI product film for a fragrance, set in a lotus garden.", 32, "Product film", False),
    "clone-ad": ("clone-ad.mp4", "clone-ad.jpg", "One of them is AI: clone ad",
        "Posted reel: an astrologer's real footage beside her AI clone, and the viewer guesses which is which.", 15, "AI clone", False),
    "snakes-ladders": ("snakes-ladders.mp4", "snakes-ladders.jpg", "Snakes & Ladders, made real",
        "Snakes and ladders as a photoreal 3D short with foley-only sound. 885K reach on Instagram.", 19, "3D short", False),
    "ingredients": ("ingredients.mp4", "ingredients.jpg", "The ingredients story",
        "AI product film built around a product's ingredients, aloe and water in macro.", 18, "Product film", False),
    "adri": ("adri.mp4", "adri.jpg", "Adri: fragrance film",
        "Cinematic AI product film for a fragrance, with citrus and spice in a warm forest light.", 23, "Product film", False),
    "ludo": ("ludo.mp4", "ludo.jpg", "Ludo, made real",
        "Ludo pieces come alive in a photoreal 3D world, from The Fifth Kind's nostalgia series.", 17, "3D short", False),
    "vaanaan": ("vaanaan.mp4", "vaanaan.jpg", "Vaanaan: fragrance film",
        "Cinematic AI product film for a fragrance, set in desert light.", 23, "Product film", False),
    "schuco": ("schuco.mp4", "schuco.jpg", "Schüco: AI product film",
        "AI product video for Schüco, the German window and façade systems brand.", 21, "Product film", False),
    "jito": ("jito.mp4", "jito.jpg", "JITO Bangalore: event film",
        "AI promo film built to drive registrations for a JITO Bangalore event.", 40, "Event film", False),
    "clone-phone": ("clone-phone.mp4", "clone-phone.jpg", "Record once, on your phone",
        "Ad explaining how an AI clone works: record one short clip and the clone delivers every script after that.", 33, "AI clone", False),
    "uday-clone": ("uday-clone.mp4", "uday-clone.jpg", "Founder AI clone: Uday Khandelwal",
        "AI clone video of The Fifth Kind founder Uday Khandelwal, generated from his own face and voice.", 32, "AI clone", False),
    "foodsvilla": ("foodsvilla.mp4", "foodsvilla.jpg", "Foodsvilla: launch film",
        "AI brand trailer produced for Foodsvilla's launch by The Fifth Kind.", 53, "Brand film", False),
    "jugad": ("jugad.mp4", "jugad.jpg", "Jugad: brand film edit",
        "Edited brand film cut for retention and pace.", 63, "Reel edit", True),
    "dance-dikhawe": ("dance-dikhawe.mp4", "dance-dikhawe.jpg", "Dance Dikhawe: entertainment edit",
        "Entertainment video edit with music-driven pacing.", 133, "Reel edit", True),
}

UPLOADED = {"stump-kora": "2026-11-13", "vs-the-mark": "2026-10-29", "vs-three-grams": "2026-09-21", "vs-dasara": "2026-10-19",
    "velvet-festival": "2026-11-06", "vs-original-story": "2026-10-31", "amethyst": "2026-08-12", "kora-brand": "2026-11-16", "kora-reveal": "2026-10-17", "arvind": "2026-10-12", "clone-ad": "2026-10-28",
    "clone-phone": "2026-11-06", "jeweller-ad": "2026-10-26", "snakes-ladders": "2026-11-11", "ludo": "2026-11-12"}

# Static posts (finished, client-approved social posts). key: (file stem in /img/work/, alt text, caption, client)
POSTS = {
    "vs-signature-nose-pin-carousel": ("VS Signature nose pin carousel: a woman in a silk saree with the matching gold nose pin shown beside her",
        "Nose pin carousel", "VS Signature"),
    "vs-signature-nath-origin-post": ("Bride in red and gold with the headline Your nath isn't originally Indian, a VS Signature education post",
        "\u201cYour nath isn't originally Indian\u201d", "VS Signature"),
    "velvet-lite-gold-daylight-post": ("Velvet Lite 9KT gold chain and earrings on silk with the line Somewhere in this house is gold that hasn't seen daylight since 2019",
        "Gold that hasn't seen daylight", "Velvet Lite 9KT"),
    "vs-signature-mirror-post": ("A gold nose pin reflected in an antique mirror, VS Signature post asking where the nose pin came from",
        "Where did it come from?", "VS Signature"),
    "vs-signature-vedic-texts-post": ("Painting-style portrait with the headline It's not in the vedic texts, a VS Signature myth-busting post about nose piercing",
        "\u201cIt's not in the vedic texts\u201d", "VS Signature"),
    "velvet-lite-9kt-chain-post": ("Woman in an ivory saree wearing a Velvet Lite 9KT gold chain",
        "Velvet Lite 9KT chain", "Velvet Lite 9KT"),
    "vs-signature-middle-east-post": ("Woman by an arched window with the line It was one of the things that travelled from the Middle East, a VS Signature post",
        "The nose pin's journey", "VS Signature"),
    "velvet-lite-jewellery-daylight-post": ("Gold temple jewellery on silk with the line Somewhere in a house there is jewellery that hasn't seen you or daylight since 2019",
        "Jewellery that hasn't seen you", "Velvet Lite 9KT"),
}
POSTS_PUBLISHED = "2026-10-15"

NAV = [
    ("/ai-video-production-bangalore/", "AI Video"),
    ("/social-media-management/", "Social Media"),
    ("/jewellery/", "Jewellery"),
    ("/ai-chatbot-development/", "AI Chatbots"),
    ("/ai-automation-agency/", "Automation"),
    ("/whatsapp-chatbot/", "WhatsApp"),
    ("/work/", "Work"),
    ("/blog/", "Blog"),
]

FOOTER_CREATE = [
    ("/jewellery/", "AI for Jewellery Brands"),
    ("/social-media-management/", "Social Media Management"),
    ("/jewellery-marketing/", "Jewellery Marketing"),
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
    ("/locations/", "Cities We Serve"),
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
            f'<picture><source type="image/webp" srcset="/Video/posters/sm/{poster[:-4]}.webp 300w, /Video/posters/{poster[:-4]}.webp 540w" sizes="(max-width: 560px) 50vw, 260px">'
            f'<img src="/Video/posters/{poster}" alt="{esc(title)}" loading="lazy" decoding="async" width="360" height="640"></picture>'
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


def proof_block(key):
    """{{proof:service-key}}: approved client quotes and a starting price from data/proof.json.
    Renders nothing until real, approved content is added there."""
    path = ROOT / "data/proof.json"
    if not path.exists():
        return ""
    data = json.loads(path.read_text(encoding="utf-8"))
    quotes = [t for t in data.get("testimonials", [])
              if t.get("service") == key and t.get("approved") and t.get("quote", "").strip()]
    price = (data.get("prices") or {}).get(key, "").strip()
    if not quotes and not price:
        return ""
    out = ['<section class="block proof" data-proof><div class="wrap narrow">']
    if quotes:
        out.append("<h2>What clients say</h2>")
        for t in quotes:
            who = ", ".join(x for x in (t.get("name"), t.get("role"), t.get("company")) if x)
            out.append(f'<blockquote class="testimonial"><p>“{esc(t["quote"].strip())}”</p>'
                       f'{f"<cite>{esc(who)}</cite>" if who else ""}</blockquote>')
    if price:
        out.append(f'<p class="price-from"><strong>{esc(price)}</strong> · fixed quote after a free 15-minute call</p>')
    out.append("</div></section>")
    return "".join(out)


def post_card(key, used_posts):
    alt, cap, client = POSTS[key]
    used_posts.append(key)
    return (f'<figure class="post"><a href="/img/work/{key}.jpg" data-zoom>'
            f'<picture><source type="image/webp" srcset="/img/work/{key}-sm.webp 540w, /img/work/{key}.webp 1080w" sizes="(max-width: 760px) 50vw, 300px">'
            f'<img src="/img/work/{key}-sm.jpg" srcset="/img/work/{key}-sm.jpg 540w, /img/work/{key}.jpg 1080w" '
            f'sizes="(max-width: 760px) 50vw, 300px" alt="{esc(alt)}" loading="lazy" decoding="async"></picture></a>'
            f'<figcaption><small>{esc(client)}</small>{esc(cap)}</figcaption></figure>')


def expand(body, page, pages, used):
    page.setdefault("used_posts", [])
    if page.get("kind") == "service" and not page.get("generated"):
        for k, sv in SEO_SERVICES.items():
            if sv["page"].strip("/") == page["slug"] or sv.get("bangalore_page", "").strip("/") == page["slug"]:
                block = seo_pages.available_in_block(sv, k, SEO_CITIES)
                cut = body.rfind('<div class="wrap">')
                body = body[:cut] + block + body[cut:] if cut > 0 else body + block
                page["track_service"] = k
                break
    body = re.sub(r"\{\{posts:([\w,-]+)\}\}",
                  lambda m: '<div class="posts">' + "".join(post_card(k, page["used_posts"]) for k in m[1].split(",")) + "</div>", body)
    body = re.sub(r"\{\{video:([\w-]+)\}\}", lambda m: '<div class="vids">' + video_card(m[1], used) + "</div>", body)
    body = re.sub(r"\{\{videos:([\w,-]+)\}\}",
                  lambda m: '<div class="vids">' + "".join(video_card(k, used) for k in m[1].split(",")) + "</div>", body)
    body = re.sub(r"\{\{cta:([^|}]*)\|([^}]*)\}\}", lambda m: cta_band(m[1], m[2], page), body)
    body = body.replace("{{cta}}", cta_band(page=page))
    body = re.sub(r"\{\{related:([\w,/-]+)\}\}", lambda m: related(m[1].split(","), pages), body)
    body = re.sub(r"\{\{form:([^}]*)\}\}", lambda m: lead_form(m[1]), body)
    body = re.sub(r"\{\{proof:([\w-]+)\}\}", lambda m: proof_block(m[1]), body)
    return body


# ---------------------------------------------------------------- schema
def org_schema():
    return {
        "@type": "ProfessionalService",
        "@id": ORG_ID,
        "name": "The Fifth Kind",
        "alternateName": ["The Fifth Kind AI Studio", "the5thkind.ai"],
        "description": ("AI video production studio and AI automation agency in Bengaluru, India: AI product videos, AI clone videos, "
                        "brand and ad films, AI character films and 3D shorts, social media management and marketing strategy, plus custom AI chatbots, "
                        "WhatsApp automation and AI agents."),
        "disambiguatingDescription": "Bangalore-based AI video production and AI automation studio (the5thkind.in). Not affiliated with the5thkind.com.",
        "knowsAbout": ["AI video production", "AI product videos", "AI clone videos", "AI ad films", "AI character animation",
                       "3D animation in Blender", "Reel editing", "AI chatbot development", "WhatsApp Business API automation",
                       "AI agents for business", "Quotation and invoice automation", "Social media management",
                       "Instagram marketing", "Content strategy", "Meta ads", "Jewellery marketing", "Jewellery video production"],
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
        "areaServed": [{"@type": "Country", "name": "India"}] + [
            {"@type": "City", "name": c["full"]} for c in seo_pages.load()[1].values()] + ["Worldwide"],
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
    if kind == "service_city":
        c = page["area"]
        graph.append({
            "@type": "Service", "@id": url + "#service", "name": page["service_name"],
            "serviceType": page["service_type"], "description": page["description"], "url": url,
            "provider": {"@id": ORG_ID},
            "areaServed": {"@type": "City", "name": c["full"], "containedInPlace": {"@type": "State", "name": c["state"]}},
            "availableLanguage": c["languages"],
            "audience": {"@type": "BusinessAudience", "audienceType": page.get("audience", "Businesses")},
            "isRelatedTo": {"@id": f"{BASE}{seo_pages.load()[0][page['service_key']]['page']}#service"},
        })
    elif kind == "city_hub":
        c = page["area"]
        graph.append({"@type": "Place", "@id": url + "#place", "name": c["full"],
                      "containedInPlace": {"@type": "State", "name": c["state"]}})
        graph[3]["about"] = [{"@id": ORG_ID}, {"@id": url + "#place"}]
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

    for v in page.get("video_objects", []):
        graph.append({"@type": "VideoObject", "name": v["name"], "description": v["description"],
                      "thumbnailUrl": BASE + v["poster"], "contentUrl": BASE + v["file"],
                      "uploadDate": v.get("uploaded", "2026-11-13"), "duration": iso_dur(v["seconds"]), "publisher": {"@id": ORG_ID}})
    for k in dict.fromkeys(page.get("used_posts", [])):
        alt, cap, client = POSTS[k]
        graph.append({"@type": "ImageObject", "contentUrl": f"{BASE}/img/work/{k}.jpg", "thumbnailUrl": f"{BASE}/img/work/{k}-sm.jpg",
                      "name": f"{cap} ({client})", "description": alt, "datePublished": POSTS_PUBLISHED,
                      "creator": {"@id": ORG_ID}, "copyrightHolder": {"@type": "Organization", "name": "Megha Jewellers"}})

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
<link rel="canonical" href="{url}">\n{verification_meta()}<script src="/assets/tracking-config.js"></script>
{AD_FLAG_JS}
<meta name="robots" content="{page.get("robots", "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1")}">
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
<link rel="stylesheet" href="/assets/motion.css?v={TODAY}">{page.get("head_extra", "")}
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
    body_cls = f' class="{esc(page["body_class"])}"' if page.get("body_class") else ""
    script_extra = f'\n<script src="{esc(page["script_extra"])}" defer></script>' if page.get("script_extra") else ""
    attrs = f' data-page-type="{esc(page.get("kind", "page"))}" data-service="{esc(page.get("track_service", page.get("topic", "")))}" data-city="{esc(page.get("track_city", ""))}"'
    return (head_html(page, schema) + f"\n<body{body_cls}{attrs}>\n" + nav_html(current) + "\n<main>\n" + crumbs_html(page) +
            "\n" + page["body_html"] + "\n</main>\n" + footer_html(page) +
            f'\n<script src="/assets/site.js?v={TODAY}" defer></script>\n<script src="/assets/motion.js?v={TODAY}c" defer></script>' + script_extra + '\n</body>\n</html>\n')


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
        pri = {"service": "0.9", "service_city": "0.8", "post": "0.7", "city_hub": "0.7"}.get(p.get("kind"), "0.6")
        lastmod = TODAY if p["slug"] == "work" else p.get("updated", p.get("published", TODAY))
        vids = video_xml(p.get("used", [])) if p.get("kind") == "service" or p["slug"] == "work" else ""
        vids += "".join(f"\n    <image:image><image:loc>{BASE}/img/work/{k}.jpg</image:loc></image:image>" for k in dict.fromkeys(p.get("used_posts", [])))
        rows.append(f"  <url><loc>{BASE}/{p['slug']}/</loc><lastmod>{lastmod}</lastmod><priority>{pri}</priority>{vids}</url>\n")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "".join(rows) + "</urlset>\n", encoding="utf-8")
    (ROOT / "urls.txt").write_text("\n".join([f"{BASE}/"] + [f"{BASE}/{p['slug']}/" for p in pages.values()]) + "\n", encoding="utf-8")


def write_llms(pages):
    svc = lambda group: "\n".join(f"- [{p['service_name']}]({BASE}/{p['slug']}/): {p['description']}"
                                  for p in pages.values() if p.get("kind") == "service" and p.get("group") == group)
    posts = "\n".join(f"- [{p['h1_plain']}]({BASE}/{p['slug']}/): {p['description']}"
                      for p in sorted(pages.values(), key=lambda p: p.get("published", ""), reverse=True) if p.get("kind") == "post")
    recent = "\n".join(f"- {v[2]} ({v[5]})" for v in list(VIDEOS.values())[:25])
    locs = "\n".join(f"- [{p['nav_title']}]({BASE}/{p['slug']}/): {p['description']}" for p in pages.values() if p.get("kind") == "city_hub")
    text = f"""# The Fifth Kind

> The Fifth Kind (the5thkind.in) is an AI video production studio and AI automation agency in Bengaluru (Bangalore), India, founded by Uday Khandelwal. It makes AI product videos, AI clone videos, brand and ad films, AI character films and 3D shorts, runs social media and marketing strategy for brands, and builds custom AI chatbots, WhatsApp automation and AI agents that handle quotations, invoices and follow-ups. Not affiliated with the5thkind.com, a podcast about ancient mysteries.

Website: {BASE}/
Contact: {EMAIL} · +91 82960 08838 (phone and WhatsApp) · Instagram @the5thkind.ai
Address: 529, 8th Cross, Nanjappa Rd, Shantinagar, Bengaluru, Karnataka 560027, India
Serves: brands across India and abroad (including France): manufacturers, jewellers, D2C brands, astrologers and coaches, temples and trusts, startups.
Selected clients: Mahaveer Papers (social media, brand films, Kora AI chatbot and WhatsApp chatbot), Megha Jewellers (VS Signature and Velvet Lite 9KT reels and campaigns), Arvind Mills, Schüco, JITO Bangalore, Hybec Deco, Hybec Air, Foodsvilla, CAPTÉ (France).
Turnaround: days, not weeks. Languages delivered: English, Hindi, Hinglish, Kannada, Tamil, Telugu, French.
The studio no longer offers AI voice or phone-calling agents.

## Create: AI video production

{svc("make")}

## Grow: social media management

{svc("grow")}

## Automate: AI for sales and operations

{svc("automate")}

## Recent work ({len(VIDEOS)} films with video on {BASE}/work/)

{recent}

## Locations

Studio: Bengaluru (Shantinagar), the only office. Served remotely, with travel for shoots: {", ".join(c["name"] for k, c in SEO_CITIES.items() if k != "bangalore")}.
City pages: {BASE}/locations/ ({sum(1 for p in pages.values() if p.get("kind") == "service_city")} service-and-city pages, {sum(1 for p in pages.values() if p.get("kind") == "city_hub")} city overviews).

{locs}

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
         "name": "AI Video, Social Media & AI Chatbot Agency in Bangalore | The Fifth Kind",
         "isPartOf": {"@id": f"{BASE}/#website"}, "about": {"@id": ORG_ID}, "inLanguage": "en-IN",
         "datePublished": "2026-07-02", "dateModified": TODAY, "author": {"@id": f"{BASE}/about/#uday"},
         "primaryImageOfPage": f"{BASE}/og-image.jpg"},
        {"@type": "Person", "@id": f"{BASE}/about/#uday", "name": "Uday Khandelwal", "jobTitle": "Founder",
         "worksFor": {"@id": ORG_ID}, "url": f"{BASE}/about/", "sameAs": SAME_AS,
         "knowsAbout": ["AI video production", "AI clone videos", "Social media management", "AI chatbots", "WhatsApp automation", "Business process automation"]},
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
    # tracking + verification on the hand-written homepage (idempotent)
    if 'src="/assets/tracking-config.js"' not in s:
        s = s.replace('<script src="/assets/site.js"', '<script src="/assets/tracking-config.js"></script>\n  <script src="/assets/site.js"', 1)
    if "tfk_ad" not in s:
        s = s.replace('<script src="/assets/tracking-config.js"></script>', '<script src="/assets/tracking-config.js"></script>\n  ' + AD_FLAG_JS, 1)
    s = re.sub(r'<body[^>]*>', '<body data-page-type="home" data-service="home" data-city="">', s, count=1)
    s = re.sub(r'\n?<meta name="(google-site-verification|msvalidate\.01)" content="[^"]*">', "", s)
    vm = verification_meta().strip()
    if vm:
        s = s.replace('<link rel="canonical" href="https://www.the5thkind.in/">', '<link rel="canonical" href="https://www.the5thkind.in/">\n  ' + vm.replace("\n", "\n  "), 1)
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


def site_config():
    return {k: v for k, v in json.loads((ROOT / "data/site.json").read_text(encoding="utf-8")).items() if not k.startswith("_")}


def ensure_webp():
    """Every poster / post JPG gets a WebP twin (smaller, same look)."""
    try:
        from PIL import Image
    except ImportError:
        print("  ! Pillow missing: WebP versions not refreshed"); return
    for folder in ("Video/posters", "Video/posters/sm", "img/work"):
        for f in (ROOT / folder).glob("*.jpg"):
            w = f.with_suffix(".webp")
            if not w.exists() or w.stat().st_mtime < f.stat().st_mtime:
                Image.open(f).convert("RGB").save(w, "WEBP", quality=78, method=6)


def write_tracking_config():
    cfg = site_config()
    keep = {k: cfg[k] for k in ("gtm_id", "ga4_id", "google_ads_id", "google_ads_labels", "clarity_id", "bing_uet_id")}
    (ROOT / "assets/tracking-config.js").write_text(
        "/* Generated by tools/build.py from data/site.json. Do not edit by hand. */\nwindow.TFK_CONFIG = "
        + json.dumps(keep) + ";\n", encoding="utf-8")


def verification_meta():
    cfg = site_config(); out = ""
    if cfg.get("google_site_verification"):
        out += f'<meta name="google-site-verification" content="{esc(cfg["google_site_verification"])}">\n'
    if cfg.get("bing_site_verification"):
        out += f'<meta name="msvalidate.01" content="{esc(cfg["bing_site_verification"])}">\n'
    return out


def write_ai_files(pages):
    summary = {
        "name": "The Fifth Kind", "url": f"{BASE}/", "type": "AI video production studio and AI automation agency",
        "description": ("AI video production studio and AI automation agency in Bengaluru, India. AI product videos, AI clone videos, "
                        "brand and ad films, AI character films and 3D shorts, social media management and marketing strategy, "
                        "plus custom AI chatbots, WhatsApp automation and AI agents for quotations, invoices and follow-ups. Not affiliated with the5thkind.com."),
        "founder": "Uday Khandelwal", "location": "Shantinagar, Bengaluru, Karnataka, India",
        "contact": {"email": EMAIL, "phone": PHONE, "whatsapp": WA},
        "clients": ["Mahaveer Papers", "Megha Jewellers", "Arvind Mills", "Schüco", "JITO Bangalore", "Hybec Deco", "Hybec Air", "Foodsvilla", "CAPTÉ"],
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


SEO_SERVICES, SEO_CITIES = {}, {}


def main():
    ensure_webp()
    pages = load_pages()
    global SEO_SERVICES, SEO_CITIES
    gen, SEO_SERVICES, SEO_CITIES = seo_pages.generate(pages)
    for slug, gp in gen.items():
        if slug in pages:
            continue  # a hand-written page always wins
        gp["generated"] = True
        pages[slug] = gp
    pages["blog"] = blog_index(pages)
    # remove generated location pages that are no longer in the data files
    import shutil
    bases = {sv["city_base"] for sv in SEO_SERVICES.values()} | {"locations"}
    for base in bases:
        d = ROOT / base
        if not d.is_dir():
            continue
        for sub in d.iterdir():
            if sub.is_dir() and (sub / "index.html").exists() and f"{base}/{sub.name}" not in pages:
                shutil.rmtree(sub)
                print(f"  removed stale /{base}/{sub.name}/")
    for slug, page in pages.items():
        out = ROOT / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(page, pages), encoding="utf-8")
        print(f"  built /{slug}/")
    # custom 404 (Vercel serves /404.html with a real 404 status); noindex, not in sitemap
    nf = {"slug": "404", "kind": "page", "robots": "noindex, follow", "title": "Page not found | The Fifth Kind",
          "description": "This page doesn't exist. Find AI video, social media, jewellery marketing and AI chatbot services from The Fifth Kind, Bengaluru.",
          "nav_title": "Page not found", "track_service": "404",
          "body": ('<section class="page-hero"><div class="wrap"><p class="eyebrow">404</p><h1>That page <em>isn\'t here.</em></h1>'
                   '<p class="answer">The link may be old or mistyped. Here is where most people are heading:</p></div></section>'
                   '<section class="block"><div class="wrap"><div class="related">'
                   '<a href="/">Home<span>The Fifth Kind, Bengaluru</span></a>'
                   '<a href="/work/">Our work<span>Approved, published films and posts</span></a>'
                   '<a href="/social-media-management/">Social media management<span>We run your Instagram</span></a>'
                   '<a href="/ai-video-production/">AI video production<span>Films, clones and ads</span></a>'
                   '<a href="/ai-chatbot-development/">AI chatbots<span>Website and WhatsApp</span></a>'
                   '<a href="/locations/">Cities we serve<span>20 cities across India</span></a>'
                   '</div></div></section><div class="wrap">{{cta}}</div>')}
    (ROOT / "404.html").write_text(render(nf, pages), encoding="utf-8")
    update_home(pages)
    write_sitemap(pages)
    write_llms(pages)
    write_feed(pages)
    write_ai_files(pages)
    write_tracking_config()
    print(f"{len(pages)} pages + sitemap.xml + urls.txt")


if __name__ == "__main__":
    main()
