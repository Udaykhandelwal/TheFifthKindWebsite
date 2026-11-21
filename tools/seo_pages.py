"""Location SEO pages, generated from data/services.json, data/cities.json and data/industries.json.

build.py calls generate(existing_pages) and gets back page dicts in the same shape as
src/*.html pages (meta + "body" with shortcodes), so they share the template, schema,
sitemap, llms.txt and tracking. Edit the JSON files to add services, cities or wording.

Rules this generator follows (see docs/seo/SEO_PLAN.md):
- Only Bengaluru is described as having a studio. Other cities are served remotely.
- Each page mixes service facts with city-specific industries, languages, areas and
  seasons, so no two pages are the same text with only the city name swapped.
- No invented reviews, statistics or addresses.
"""
import html
import json
import pathlib
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
WA_NUM = "918296008838"
PHONE = "+918296008838"
PUBLISHED = "2026-11-20"


def load():
    rd = lambda n: {k: v for k, v in json.loads((DATA / n).read_text(encoding="utf-8")).items() if not k.startswith("_")}
    return rd("services.json"), rd("cities.json"), rd("industries.json")


def esc(s):
    return html.escape(str(s), quote=True)


def wa(text):
    return f"https://wa.me/{WA_NUM}?text=" + urllib.parse.quote(text)


def join_list(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def fill(s, city):
    return s.replace("{city}", city)


def city_url(svc, key, cslug):
    """URL of a service in a city, or None if we don't have a page for it."""
    if cslug not in svc.get("cities", []):
        return None
    if cslug == "bangalore" and svc.get("bangalore_page"):
        return svc["bangalore_page"]
    return f"/{svc['city_base']}/{cslug}/"


def mode_sentence(c):
    if c["in_person"]:
        return "We make them in our Shantinagar studio in Bengaluru, and you're welcome to visit by appointment."
    return (f"We work with {c['name']} businesses from our Bengaluru studio, over WhatsApp, calls and shared folders, "
            f"and travel to {c['name']} for shoots when a project needs one.")


# ------------------------------------------------------------------ service × city page
def service_city_page(key, svc, cslug, c, services, cities, inds):
    name, cname = svc["name"], c["name"]
    fam = svc["family"]
    langs = c["languages"]
    is_jewel = key == "jewellery-marketing"

    hero_facts = ["Studio in Shantinagar, Bengaluru" if c["in_person"] else f"Serving {cname} remotely",
                  join_list(langs[:3]), "Fixed quote after a free call", "Approved, published client work"]
    body = [f'''<section class="page-hero"><div class="wrap">
  <p class="eyebrow">{esc(name)} · {esc(c["full"])}</p>
  <h1>{fill(svc["h1"], esc(cname))}</h1>
  <p class="answer"><strong>{esc(svc["what"])}</strong> {esc(mode_sentence(c))}</p>
  <div class="hero-cta">
    <a class="btn btn-orange" href="{wa(f"Hi! I'm in {cname} and I'm interested in {name}.")}" target="_blank" rel="noopener">WhatsApp us</a>
    <a class="btn btn-ghost" href="tel:{PHONE}">Call +91 82960 08838</a>
    <a class="btn btn-ghost" href="#quote">Get a quote</a>
  </div>
  <div class="hero-facts">{"".join(f"<span>{esc(f)}</span>" for f in hero_facts)}</div>
</div></section>''']

    # city-specific: market / industries
    if is_jewel:
        seasons = "".join(f"<li>{esc(s)}</li>" for s in c["seasons"])
        body.append(f'''<section class="block"><div class="wrap">
  <h2>The {esc(cname)} jewellery market</h2>
  <p class="lede">{esc(c["jewellery_note"])} {esc(c["intro"])}</p>
  <h3 style="margin:26px 0 10px">Buying windows we plan for in {esc(cname)}</h3>
  <ul class="checks">{seasons}<li>Dhanteras and wedding-season launches</li></ul>
  <p style="margin-top:16px">For product stills and campaign films of your pieces, see <a href="/jewellery/">AI jewellery photography &amp; films</a>.</p>
</div></section>''')
        near = [i for i in c["industries"] if i in inds and i != "jewellery"][:3]
        cards = "".join(f'<div class="card"><h3>{esc(inds[i]["name"])}</h3><p>{esc(inds[i]["social"])}</p></div>' for i in near)
        body.append(f'''<section class="block"><div class="wrap">
  <h2>Beyond jewellery in {esc(cname)}</h2>
  <p class="lede">The same team also works with {esc(cname)}'s other trades, in {esc(join_list(langs))}. Business areas we know: {esc(c["areas"])}.</p>
  <div class="grid">{cards}</div>
</div></section>''')
    else:
        picks = [i for i in c["industries"] if i in inds][:4]
        cards = "".join(f'<div class="card"><h3>{esc(inds[i]["name"])}</h3><p>{esc(inds[i][fam])}</p></div>' for i in picks)
        body.append(f'''<section class="block"><div class="wrap">
  <h2>How {esc(cname)} businesses use {esc(svc.get("noun", name))}</h2>
  <p class="lede">{esc(c["intro"])}</p>
  <div class="grid">{cards}</div>
</div></section>''')

    # what you get
    dl = "".join(f'<div class="card"><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for t, d in svc["deliverables"])
    body.append(f'''<section class="block"><div class="wrap">
  <h2>What you get</h2>
  <div class="grid">{dl}</div>
</div></section>''')

    # proof
    proof = ""
    if svc.get("videos"):
        proof += "\n  {{videos:" + ",".join(svc["videos"]) + "}}"
    if svc.get("posts"):
        proof += '\n  <h3 style="margin:30px 0 12px">Static posts</h3>\n  {{posts:' + ",".join(svc["posts"]) + "}}"
    if proof:
        body.append(f'''<section class="block"><div class="wrap">
  <h2>Work you can check</h2>
  <p class="lede">Every film and post here was approved by the client and published. Tap a film to watch it with sound, or <a href="/work/">see the full portfolio</a>.</p>{proof}
</div></section>''')

    # working with us
    first = "Visit the studio or brief us on WhatsApp" if c["in_person"] else "Brief us on WhatsApp or a video call"
    season_line = {
        "video": f"For launches and festive campaigns in {cname}, we plan around {join_list(c['seasons'][:3])}.",
        "social": f"Your calendar is built around {cname}'s buying moments: {join_list(c['seasons'])}.",
        "chat": f"Enquiries spike around {join_list(c['seasons'][:3])}, so we aim to have your assistant live and tested before then.",
    }[fam]
    body.append(f'''<section class="block"><div class="wrap">
  <h2>Working with us from {esc(cname)}</h2>
  <ol class="steps">
    <li><h3>{esc(first)}</h3><p>Tell us what you sell, who buys it and what you want to happen. A free 15-minute call is enough to scope it.</p></li>
    <li><h3>Approve the plan</h3><p>You approve the script, calendar or chatbot flow before production starts.</p></li>
    <li><h3>We produce</h3><p>Made in-house by our team, with one round of changes built in.</p></li>
    <li><h3>Launch &amp; improve</h3><p>Delivered ready to post or go live, then tuned on real results.</p></li>
  </ol>
  <p style="margin-top:18px;color:var(--muted)">We deliver in {esc(join_list(langs))}. {esc(season_line)}</p>
</div></section>''')

    # quote form
    body.append(f'''<section class="block" id="quote"><div class="wrap narrow">
  <h2>Get a fixed quote</h2>
  <p class="lede">Send a few details. We reply on WhatsApp the same working day.</p>
  {{{{form:{name} – {cname}}}}}
</div></section>''')

    # FAQ
    if c["in_person"]:
        office = ("Yes. Our studio is at 529, 8th Cross, Nanjappa Rd, Shantinagar, Bengaluru 560027. "
                  "Clients are welcome to visit by appointment, and briefs can also happen on WhatsApp or a call.")
        oq = f"Can I meet your team in {cname}?"
    else:
        office = (f"No. Our only studio is in Bengaluru. We work with {cname} businesses remotely over WhatsApp, calls and shared folders, "
                  f"and travel to {cname} for shoots when a project needs one.")
        oq = f"Do you have an office in {cname}?"
    lang_a = (f"Yes. We work in {join_list(langs)}. Scripts, captions and voiceovers are written for each language, not translated word for word."
              if fam != "chat" else
              f"Yes. The assistant can understand and reply in {join_list(langs)}, and hands over to your team in any language they speak.")
    faqs = [
        (oq, office),
        (f"Can you work in {join_list(langs[:3])}?", lang_a),
        (f"How much {'do' if svc.get('noun', name).endswith('s') else 'does'} {svc.get('noun', name)} cost in {cname}?",
         "Pricing is the same wherever you are. It depends on scope: the number of films or posts, length, languages and integrations. "
         "We give a fixed quote after a free 15-minute call, with no obligation."),
        (f"Which {cname} businesses do you work with?",
         f"Mostly {join_list([inds[i]['name'].lower() for i in c['industries'][:5] if i in inds])}, along with founders and personal brands."),
    ] + [tuple(f) for f in svc["faqs"]]
    qa = "".join(f'<details class="q"><summary>{esc(q)}</summary><div>{esc(a)}</div></details>' for q, a in faqs)
    body.append(f'''<section class="block"><div class="wrap narrow">
  <h2>Frequently asked questions</h2>
  <div class="faq">{qa}</div>
</div></section>''')

    # internal links
    other_cities = [(cities[s]["name"], city_url(svc, key, s)) for s in svc["cities"] if s != cslug]
    same_city = []
    for k2, s2 in services.items():
        if k2 == key:
            continue
        u = city_url(s2, k2, cslug)
        if u:
            same_city.append((f"{s2['name']} in {cname}", u))
    links = "".join(f'<a href="{u}">{esc(t)}<span>{esc(svc["name"])} for {esc(t)} businesses</span></a>' for t, u in other_cities[:10])
    links2 = "".join(f'<a href="{u}">{esc(t)}<span>See the service</span></a>' for t, u in same_city[:8])
    blog = "".join(f'<li><a href="{b}">{esc(b.strip("/").split("/")[-1].replace("-", " ").capitalize())}</a></li>' for b in svc.get("blog", []))
    body.append(f'''<section class="block"><div class="wrap">
  <h2>{esc(name)} in other cities</h2>
  <div class="related">{links}<a href="{svc["page"]}">All of India<span>{esc(name)}, the full service page</span></a></div>
  {f'<h2 style="margin-top:40px">More for {esc(cname)} businesses</h2><div class="related">{links2}<a href="/locations/{cslug}/">Everything we do in {esc(cname)}<span>Services, industries and FAQs</span></a></div>' if links2 else f'<p style="margin-top:20px"><a href="/locations/{cslug}/">Everything we do for {esc(cname)} businesses →</a></p>'}
  {f'<h3 style="margin-top:30px">Read next</h3><ul>{blog}</ul>' if blog else ''}
</div></section>''')
    body.append(f'<div class="wrap">{{{{cta:{esc(name)} for your {esc(cname)} business, <em>quoted today.</em>|Message us on WhatsApp with what you sell and what you need. We reply the same working day.}}}}</div>')

    title = fill(svc["title"], cname)
    if len(title) > 65:
        title = title.replace(" | The Fifth Kind", " | 5th Kind")
    return {
        "slug": f"{svc['city_base']}/{cslug}",
        "kind": "service_city",
        "group": svc["family"],
        "service_name": f"{name} in {cname}",
        "service_type": svc["name"],
        "nav_title": f"{name} in {cname}",
        "audience": f"Businesses in {c['full']}",
        "title": title,
        "og_title": f"{name} in {cname} — The Fifth Kind",
        "description": fill(svc["desc"], cname),
        "published": PUBLISHED, "updated": PUBLISHED,
        "crumbs": [[name, svc["page"]]],
        "area": c, "service_key": key, "city_key": cslug,
        "track_service": key, "track_city": cslug,
        "body": "\n\n".join(body),
    }


# ------------------------------------------------------------------ city hub
def city_hub_page(cslug, c, services, cities, inds):
    cname = c["name"]
    rows = []
    for k, s in services.items():
        u = city_url(s, k, cslug) or s["page"]
        local = city_url(s, k, cslug) is not None
        rows.append(f'<a href="{u}">{esc(s["name"])}{" in " + esc(cname) if local else ""}<span>{"Page for " + esc(cname) if local else "Main service page"}</span></a>')
    ind_cards = "".join(
        f'<div class="card"><h3>{esc(inds[i]["name"])}</h3><p><b>Video:</b> {esc(inds[i]["video"])}</p>'
        f'<p style="margin-top:8px"><b>Social:</b> {esc(inds[i]["social"])}</p><p style="margin-top:8px;color:var(--muted)"><b>Chat:</b> {esc(inds[i]["chat"])}</p></div>'
        for i in c["industries"] if i in inds)
    jewel_city = "jewellery" in c["industries"] or "diamonds" in c["industries"]
    vids = "vs-the-mark,vs-three-grams,vs-dasara,kora-brand" if jewel_city else "kora-brand,arvind,clone-ad,snakes-ladders"
    post_block = ('<h3 style="margin:30px 0 12px">Static posts</h3>\n  {{posts:vs-signature-nose-pin-carousel,vs-signature-nath-origin-post,velvet-lite-gold-daylight-post}}'
                  if jewel_city else "")
    keys = list(cities)
    i0 = keys.index(cslug)
    near = [k for k in keys if k != cslug and cities[k]["state"] == c["state"]]
    near += [keys[(i0 + n) % len(keys)] for n in range(1, len(keys)) if keys[(i0 + n) % len(keys)] not in near + [cslug]]
    near = near[:6]
    seasons = "".join(f"<li>{esc(s)}</li>" for s in c["seasons"])
    jewel = f'<p style="margin-top:14px">{esc(c["jewellery_note"])} <a href="{city_url(services["jewellery-marketing"], "jewellery-marketing", cslug) or "/jewellery-marketing/"}">Jewellery marketing for {esc(cname)} →</a></p>' if c.get("jewellery_note") else ""
    office = ("Yes. Our studio is at 529, 8th Cross, Nanjappa Rd, Shantinagar, Bengaluru 560027, and clients can visit by appointment."
              if c["in_person"] else
              f"No. Our only studio is in Bengaluru. We work with {cname} businesses remotely and travel for shoots when a project needs one.")
    faqs = [
        (("Where is your studio in Bengaluru?" if c["in_person"] else f"Do you have an office in {cname}?"), office),
        (f"What services do you offer to {cname} businesses?",
         "AI video production (product films, AI clone videos, ad films, 3D and character films, reel editing), social media management, "
         "jewellery marketing, custom AI chatbots, WhatsApp chatbots and AI business automation."),
        (f"Which languages do you work in for {cname}?", f"{join_list(c['languages'])}, for scripts, captions, voiceovers and chatbot replies."),
        ("How quickly can you start?", "Usually within a week of a free 15-minute call and an approved scope. Short films are typically delivered within a week of an approved script."),
    ]
    qa = "".join(f'<details class="q"><summary>{esc(q)}</summary><div>{esc(a)}</div></details>' for q, a in faqs)
    others = "".join(f'<a href="/locations/{s}/">{esc(cities[s]["name"])}<span>{esc(cities[s]["state"])}</span></a>' for s in near)
    body = f'''<section class="page-hero"><div class="wrap">
  <p class="eyebrow">{esc(c["full"])} · {esc(c["state"])}</p>
  <h1>AI video, social media &amp; AI chatbots <em>for {esc(cname)} businesses.</em></h1>
  <p class="answer"><strong>The Fifth Kind is an AI video, social media and AI chatbot studio based in Bengaluru that works with {esc(cname)} businesses.</strong> {esc(c["intro"])} {esc(mode_sentence(c))}</p>
  <div class="hero-cta">
    <a class="btn btn-orange" href="{wa(f"Hi! I run a business in {cname} and want to talk to The Fifth Kind.")}" target="_blank" rel="noopener">WhatsApp us</a>
    <a class="btn btn-ghost" href="#quote">Get a quote</a>
  </div>
  <div class="hero-facts"><span>{esc(join_list(c["languages"][:3]))}</span><span>{"Studio in Bengaluru" if c["in_person"] else "Remote, with travel for shoots"}</span><span>Fixed quotes</span></div>
</div></section>

<section class="block"><div class="wrap">
  <h2>What we do for {esc(cname)} businesses</h2>
  <div class="related">{"".join(rows)}</div>
</div></section>

<section class="block"><div class="wrap">
  <h2>Industries we work with in {esc(cname)}</h2>
  <p class="lede">Business areas we know: {esc(c["areas"])}.</p>
  <div class="grid">{ind_cards}</div>{jewel}
</div></section>

<section class="block"><div class="wrap">
  <h2>Approved, published work</h2>
  {{{{videos:{vids}}}}}
  {post_block}
</div></section>

<section class="block"><div class="wrap narrow">
  <h2>{esc(cname)}'s calendar, planned ahead</h2>
  <p>Content and campaigns land better when they're ready before the moment, not on the day. For {esc(cname)} we plan around:</p>
  <ul class="checks">{seasons}</ul>
</div></section>

<section class="block" id="quote"><div class="wrap narrow">
  <h2>Get a fixed quote</h2>
  {{{{form:{cname} enquiry}}}}
</div></section>

<section class="block"><div class="wrap narrow">
  <h2>Frequently asked questions</h2>
  <div class="faq">{qa}</div>
</div></section>

<section class="block"><div class="wrap">
  <h2>Nearby and related cities</h2>
  <div class="related">{others}<a href="/locations/">All {len(cities)} cities<span>Full list and service matrix</span></a></div>
</div></section>
<div class="wrap">{{{{cta:Tell us what your {esc(cname)} business <em>needs next.</em>|Free 15-minute call on WhatsApp. We'll tell you honestly what AI can and can't do for you.}}}}</div>'''
    return {
        "slug": f"locations/{cslug}", "kind": "city_hub",
        "title": f"AI Video, Social Media & Chatbots in {cname} | The Fifth Kind" if len(cname) < 12 else f"AI Video & Social Media in {cname} | The Fifth Kind",
        "og_title": f"The Fifth Kind for {cname} businesses",
        "description": (f"AI video production, social media management, jewellery marketing and AI chatbots for {cname} businesses, "
                        f"from a Bengaluru studio. Languages: {join_list(c['languages'][:3])}.")[:165],
        "nav_title": cname, "published": PUBLISHED, "updated": PUBLISHED,
        "crumbs": [["Locations", "/locations/"]], "area": c, "city_key": cslug,
        "track_service": "city-hub", "track_city": cslug, "body": body,
    }


# ------------------------------------------------------------------ /locations/ index
def locations_index(services, cities):
    head = "".join(f"<th>{esc(cities[c]['name'])}</th>" for c in cities)
    rows = []
    for k, s in services.items():
        cells = []
        for cs in cities:
            u = city_url(s, k, cs)
            cells.append(f'<td><a href="{u}" aria-label="{esc(s["name"])} in {esc(cities[cs]["name"])}">✓</a></td>' if u else "<td></td>")
        rows.append(f'<tr><td><a href="{s["page"]}">{esc(s["name"])}</a></td>{"".join(cells)}</tr>')
    hubs = "".join(f'<a href="/locations/{c}/">{esc(cities[c]["name"])}<span>{esc(cities[c]["state"])}{" · our studio" if cities[c]["in_person"] else ""}</span></a>' for c in cities)
    body = f'''<section class="page-hero"><div class="wrap">
  <p class="eyebrow">Locations</p>
  <h1>Cities we work with <em>across India.</em></h1>
  <p class="answer"><strong>The Fifth Kind's studio is in Bengaluru (Shantinagar).</strong> We work with businesses in {len(cities)} Indian cities, in person in Bengaluru and remotely everywhere else, travelling for shoots when a project needs it. Pick your city to see the services, industries and languages we cover there.</p>
</div></section>
<section class="block"><div class="wrap">
  <h2>Choose your city</h2>
  <div class="related">{hubs}</div>
</div></section>
<section class="block"><div class="wrap">
  <h2>Service pages by city</h2>
  <div class="table-wrap"><table class="matrix"><thead><tr><th>Service</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>
</div></section>
<div class="wrap">{{{{cta}}}}</div>'''
    return {"slug": "locations", "kind": "page", "title": "Cities We Serve: AI Video, Social & Chatbots | The Fifth Kind",
            "description": "The Fifth Kind works with businesses across 20 Indian cities from its Bengaluru studio: AI video, social media management, jewellery marketing and AI chatbots.",
            "nav_title": "Locations", "published": PUBLISHED, "updated": PUBLISHED, "track_service": "locations", "body": body}


# ------------------------------------------------------------------ national hub for services without one
def national_hub(key, svc, cities, inds):
    """Used for ai-video-production, whose existing page is the Bengaluru page."""
    dl = "".join(f'<div class="card"><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for t, d in svc["deliverables"])
    cl = "".join(f'<a href="{city_url(svc, key, s)}">{esc(cities[s]["name"])}<span>{esc(svc["name"])} in {esc(cities[s]["name"])}</span></a>' for s in svc["cities"])
    faqs = [tuple(f) for f in svc["faqs"]] + [
        ("Where is The Fifth Kind based?", "Our studio is in Shantinagar, Bengaluru. We work with brands across India and abroad, in person in Bengaluru and remotely elsewhere."),
        ("Which industries do you make AI videos for?", "Paper and B2B suppliers, jewellers, textiles and fashion, D2C brands, education, healthcare, real estate, founders and personal brands.")]
    qa = "".join(f'<details class="q"><summary>{esc(q)}</summary><div>{esc(a)}</div></details>' for q, a in faqs)
    body = f'''<section class="page-hero"><div class="wrap">
  <p class="eyebrow">AI Video Production · India</p>
  <h1>AI video production company <em>for brands across India.</em></h1>
  <p class="answer"><strong>{esc(svc["what"])}</strong> The Fifth Kind is an AI video production studio in Bengaluru making product films, AI clone videos, ad films, 3D shorts and reels for brands across India, including Mahaveer Papers, Megha Jewellers and Arvind Mills.</p>
  <div class="hero-cta"><a class="btn btn-orange" href="{wa("Hi! I want an AI video for my brand.")}" target="_blank" rel="noopener">WhatsApp us</a><a class="btn btn-ghost" href="#quote">Get a quote</a></div>
</div></section>
<section class="block"><div class="wrap"><h2>What we make</h2><div class="grid">{dl}</div></div></section>
<section class="block"><div class="wrap"><h2>Approved, published films</h2>{{{{videos:{",".join(svc["videos"])},vs-the-mark,stump-kora}}}}</div></section>
<section class="block"><div class="wrap"><h2>AI video production by city</h2><div class="related">{cl}</div></div></section>
<section class="block" id="quote"><div class="wrap narrow"><h2>Get a fixed quote</h2>{{{{form:AI Video Production}}}}</div></section>
<section class="block"><div class="wrap narrow"><h2>Frequently asked questions</h2><div class="faq">{qa}</div></div></section>
<div class="wrap">{{{{cta}}}}<h2>Related services</h2>{{{{related:ai-clone-video,ai-product-video,ai-ad-film}}}}</div>'''
    return {"slug": key, "kind": "service", "group": "make", "service_name": "AI Video Production (India)",
            "service_type": "AI video production", "nav_title": "AI Video Production (India)",
            "audience": "Brands and businesses across India",
            "title": "AI Video Production Company in India | The Fifth Kind",
            "og_title": "AI Video Production Company in India — The Fifth Kind",
            "description": "AI video production company in India: product films, AI clone videos, ad films, 3D shorts and reels from a Bengaluru studio, for brands in every major city.",
            "published": PUBLISHED, "updated": PUBLISHED, "track_service": key, "body": body}


def available_in_block(svc, key, cities):
    """Links block injected into the hand-written national service pages."""
    links = "".join(f'<a href="{city_url(svc, key, s)}">{esc(cities[s]["name"])}<span>{esc(svc["name"])} in {esc(cities[s]["name"])}</span></a>'
                    for s in svc.get("cities", []))
    if not links:
        return ""
    return (f'<section class="block"><div class="wrap"><h2>{esc(svc["name"])} by city</h2>'
            f'<p class="lede">Our studio is in Bengaluru. We also work with businesses in these cities: <a href="/locations/">all locations →</a></p>'
            f'<div class="related">{links}</div></div></section>\n')


def generate(existing):
    services, cities, inds = load()
    pages = {}
    for key, svc in services.items():
        if svc["page"].strip("/") not in existing and key == "ai-video-production":
            p = national_hub(key, svc, cities, inds)
            pages[p["slug"]] = p
        for cs in svc.get("cities", []):
            if cs not in cities:
                raise SystemExit(f"services.json: {key} lists unknown city {cs}")
            if cs == "bangalore" and svc.get("bangalore_page"):
                continue
            p = service_city_page(key, svc, cs, cities[cs], services, cities, inds)
            pages[p["slug"]] = p
    for cs, c in cities.items():
        p = city_hub_page(cs, c, services, cities, inds)
        pages[p["slug"]] = p
    p = locations_index(services, cities)
    pages[p["slug"]] = p
    return pages, services, cities
