#!/usr/bin/env python3
"""Pull Google autocomplete suggestions (India, English) for each service seed.
Writes docs/seo/autocomplete.json. Autocomplete reflects what people really type;
it does NOT give search volumes (that needs Google Keyword Planner access)."""
import json, time, urllib.parse, urllib.request, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SEEDS = {
 "ai-video-production": ["ai video production", "ai video production company", "ai video agency", "ai video making services", "ai video production bangalore"],
 "ai-clone-video": ["ai clone video", "ai avatar video", "ai clone video services", "ai digital twin video", "ai avatar video india"],
 "ai-product-video": ["ai product video", "product video ai", "ai product ad", "ai product video agency", "product video shoot bangalore"],
 "ai-character-story-video": ["ai character video", "ai animated video for brand", "3d animation studio bangalore", "ai mascot video"],
 "ai-ad-film": ["ai ad film", "ai ad film production", "ad film makers in bangalore", "ai commercial video", "ai tvc"],
 "reel-editing-services": ["reel editing services", "instagram reel editing", "reel editor for hire", "video editing services bangalore"],
 "social-media-management": ["social media management", "social media marketing agency", "social media agency bangalore", "instagram marketing agency", "social media management cost"],
 "jewellery-marketing": ["jewellery marketing", "jewellery marketing agency", "social media for jewellery", "jewellery reels", "jewellery shop instagram"],
 "whatsapp-chatbot": ["whatsapp chatbot", "whatsapp chatbot for business", "whatsapp business api", "whatsapp automation", "whatsapp chatbot india"],
 "ai-chatbot-development": ["ai chatbot development", "ai chatbot for website", "custom ai chatbot", "chatbot development company", "ai chatbot company"],
 "ai-automation-agency": ["ai automation agency", "business automation", "invoice automation", "quotation automation", "ai agents for business"],
}
MODS = ["", " in", " for", " cost", " near me", " india", " how"]
def suggest(q):
    url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode({"client": "firefox", "hl": "en", "gl": "in", "q": q})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (keyword-research script)"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=10).read().decode("utf-8", "ignore"))[1]
    except Exception as e:
        return []
out = {}
for svc, seeds in SEEDS.items():
    found = []
    for s in seeds:
        for m in MODS:
            for x in suggest(s + m):
                if x not in found: found.append(x)
            time.sleep(0.25)
    out[svc] = found
    print(svc, len(found))
(ROOT / "docs/seo/autocomplete.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
