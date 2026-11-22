# Google Ads – Bangalore launch plan

Each service is its own campaign/ad group with its own landing page, so Quality Score and reporting stay clean. Location: Bengaluru + 25 km radius, presence (not 'interest'). Bids, budgets, ads and approvals are set in Google Ads, not on the website.

**Conversion actions to create in Google Ads** (labels go into `data/site.json` → `google_ads_labels`): `generate_lead` (form submit, primary), `whatsapp_click` (primary), `phone_click` (primary), `email_click` (secondary).

**Shared negative keywords:** free, generator, course, jobs, job, salary, internship, app, apk, tutorial, github, reddit, pdf, meaning, kya hota hai, online free, template, download, how to make, how to create, career, careers, hiring, vacancy, training, certification, ppt, project report, definition, wikipedia, quora, youtube

| Ad group | Landing page | Exact match | Phrase match |
|---|---|---|---|
| AI Video Production – Bangalore | https://www.the5thkind.in/ai-video-production-bangalore/ | [ai video production company bangalore], [ai video production bangalore], [ai video agency bangalore] | "ai video production company", "ai video agency", "ai video production services" |
| AI Clone Video – Bangalore | https://www.the5thkind.in/ai-clone-video/bangalore/ | [ai clone video bangalore], [ai avatar video bangalore], [ai clone video services] | "ai clone video", "ai avatar video for business" |
| AI Product Video – Bangalore | https://www.the5thkind.in/ai-product-video/bangalore/ | [product video bangalore], [ai product video bangalore], [product video shoot bangalore] | "ai product video", "product ad video" |
| AI Ad Film – Bangalore | https://www.the5thkind.in/ai-ad-film/bangalore/ | [ad film makers in bangalore], [ad film production house bangalore], [ai ad film bangalore] | "ad film makers", "ai ad film" |
| 3D & Character – Bangalore | https://www.the5thkind.in/ai-character-story-video/bangalore/ | [3d animation studio in bangalore], [3d animation company in bangalore] | "brand mascot animation", "3d product animation" |
| Reel Editing – Bangalore | https://www.the5thkind.in/reel-editing-services/ | [video editing services in bangalore], [reel editing bangalore], [video editing company bangalore] | "reel editing services", "instagram reel editing" |
| Social Media Management – Bangalore | https://www.the5thkind.in/social-media-management/bangalore/ | [social media management bangalore], [social media agency bangalore], [social media marketing agency bangalore] | "social media management agency", "instagram marketing agency" |
| Jewellery Marketing – Bangalore | https://www.the5thkind.in/jewellery-marketing/bangalore/ | [jewellery marketing agency bangalore], [jewellery digital marketing agency], [social media marketing for jewellery], [jewellery marketing bangalore], [jewellery digital marketing bangalore], [instagram marketing for jewellery] | "jewellery marketing agency", "jewellery advertising agency", "marketing agency for jewellers", "jewellery social media agency", "jewellery video production" |
| WhatsApp Chatbot – Bangalore | https://www.the5thkind.in/whatsapp-chatbot/bangalore/ | [whatsapp chatbot bangalore], [whatsapp chatbot for business], [whatsapp chatbot development], [whatsapp chatbot bengaluru], [whatsapp chatbot company], [whatsapp business api chatbot] | "whatsapp chatbot", "whatsapp business automation", "ai whatsapp chatbot", "whatsapp chatbot agency", "whatsapp chatbot development company" |
| AI Chatbot – Bangalore | https://www.the5thkind.in/ai-chatbot-development/bangalore/ | [ai chatbot development company bangalore], [chatbot development company bangalore], [ai chatbot for website] | "ai chatbot development", "custom ai chatbot" |
| AI Automation – Bangalore | https://www.the5thkind.in/ai-automation-agency/bangalore/ | [ai automation agency in bangalore], [ai automation agency bangalore], [business automation bangalore] | "ai automation agency", "invoice automation" |

**Landing-page checklist (all Bangalore pages):** H1 matches the ad group; WhatsApp + call buttons above the fold; quote form (#quote) on the page; proof films; FAQ answering price, office and language; page tagged `data-service`/`data-city` for GA4; mobile sticky WhatsApp/Call bar.

**Ad visitors (built in):** a visit with `gclid`, `gbraid`, `wbraid` or `utm_medium=cpc|ppc|paid` switches service pages to focus mode for the session (top menu, breadcrumbs, city/related link blocks and footer link columns are hidden; WhatsApp, call and the quote form stay). The click ID, UTM tags and landing page are added to every emailed form lead, so each lead shows whether it came from an ad. Turn on auto-tagging in Google Ads so `gclid` is present.

**Proof and prices:** add approved client quotes and starting prices to `data/proof.json`. Pages show them automatically; nothing appears while they are empty.

## Jewellery Marketing – Bangalore

**Ad-group negatives** (in addition to the shared list): buy, price, rate, gold rate, silver rate, near me, shop, online shopping, earrings, necklace, ring, rings, bangles, chain, mangalsutra, design, designs, images, photos, wholesale, manufacturer, hallmark, tanishq, kalyan, malabar, caratlane, bluestone, institute, photography course, logo, name ideas

**Responsive search ad: headlines** (max 30 characters; pin the first to position 1)

1. Jewellery Marketing Agency
2. Instagram for Jewellery Stores
3. Jewellery Reels That Sell
4. Free Instagram Audit + 3 Ideas
5. Festival & Wedding Campaigns
6. Meta Ads to Nearby Buyers
7. Bengaluru Jewellery Marketers
8. 25+ Reels for Megha Jewellers
9. Content in English & Kannada
10. Reels, Posts & Enquiry Replies
11. Send Your Handle, Get an Audit
12. Monthly Plans for Jewellers
13. Jewellery Social Media Agency
14. WhatsApp Catalogue Bot Too
15. Book a Free 15-Min Call

**Descriptions** (max 90 characters)

1. Instagram management, product reels and festival campaigns built for jewellery stores.
2. Free audit of your store's Instagram plus 3 reel ideas for your best-selling pieces.
3. 25+ reels and campaigns for Megha Jewellers, in English and Kannada. See the work.
4. Meta ads to nearby buyers, enquiry replies and monthly reports. WhatsApp us today.

## WhatsApp Chatbot – Bangalore

**Ad-group negatives** (in addition to the shared list): open source, python, code, whatsapp web, whatsapp login, whatsapp banned, unblock, wati, interakt, aisensy, gallabox, chatgpt

**Responsive search ad: headlines** (max 30 characters; pin the first to position 1)

1. WhatsApp Chatbot for Business
2. AI WhatsApp Bot in Bengaluru
3. Official WhatsApp Business API
4. 24/7 Replies in Hindi/English
5. Qualifies Leads Automatically
6. Sends Catalogues & Quotes
7. Human Handover Built In
8. Free 15-Min Consult Call
9. Bengaluru AI Chatbot Studio
10. Fixed Quote After a Free Call
11. See Kora, Our Live AI Bot
12. Stop Missing WhatsApp Leads
13. Trained on Your Product Data
14. Get a WhatsApp Chatbot

**Descriptions** (max 90 characters)

1. AI chatbot on your WhatsApp number that answers, qualifies leads & shares catalogues 24/7.
2. Built on the official WhatsApp Business API. English, Hindi & Hinglish. Human handover.
3. Bengaluru studio behind Kora, the AI paper expert for Mahaveer Papers. Book a free call.
4. Tell us your use case on WhatsApp. Free 15-minute call, then a fixed quote. No obligation.
