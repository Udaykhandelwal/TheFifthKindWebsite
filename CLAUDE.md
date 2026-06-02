# The Fifth Kind Website — Project Reference

## Project Overview

**Company:** The5thkind.ai — India's premier AI content studio (Bangalore)  
**Owner:** Uday Khandelwal  
**Type:** Single-page marketing website  
**Stack:** Vanilla HTML5 / CSS3 / JavaScript (no frameworks, no build tools)

---

## File Structure

```
TheFifthKindWebsite/
├── index.html        (853 lines) — entire site markup
├── style.css        (2532 lines) — all styles
├── script.js         (849 lines) — all interactivity
└── Video/                        — mp4 assets
    ├── aiProduct.mp4
    ├── aiCharacter.mp4
    ├── 100% AI. 🤯No Model...mp4
    ├── R.I.P Vecna 😭😭...mp4
    └── And this is how we make...mp4
```

No `package.json`, no build process, no preprocessors.

---

## External Dependencies (CDN only)

| Library | Version | Purpose |
|---------|---------|---------|
| Three.js | r128 | 3D hero sphere + globe |
| Google Fonts (Inter) | all weights | Typography |
| FormSubmit.co | — | Contact form backend |

CDN URLs:
- `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`
- `https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap`
- Form action: `https://formsubmit.co/ajax/uday.khandelwal@the5thkind.in`

---

## Design System

### CSS Custom Properties (`:root`)

```css
--bg:        #080808       /* primary background */
--bg2:       #0f0f0f       /* secondary background */
--bg3:       #151515       /* tertiary background */
--fg:        #ffffff        /* primary text */
--fg2:       #aaaaaa       /* secondary text */
--fg3:       #555555       /* tertiary text */
--accent:    #f97316       /* brand orange — primary CTA color */
--accent2:   #fb923c       /* lighter orange */
--accentDim: rgba(249,115,22,0.15)
--border:    rgba(255,255,255,0.07)
--borderHov: rgba(255,255,255,0.18)
--radius:    12px
--radiusLg:  22px
--ease:      cubic-bezier(0.16, 1, 0.3, 1)
--font:      'Inter', system-ui, sans-serif
```

### Typography Scale

| Element | Size | Weight | Notes |
|---------|------|--------|-------|
| h1 | clamp(2.8rem, 6.5vw, 6rem) | 900 | letter-spacing -0.04em |
| h2 | clamp(2rem, 4.5vw, 4rem) | 800 | letter-spacing -0.03em |
| h3 | clamp(1.1rem, 2vw, 1.35rem) | 600 | |
| body | 0.975rem | 400 | line-height 1.75 |
| labels | 0.7rem | — | uppercase, letter-spacing 0.18em |

### Supporting Colors
- Stars/ratings: `#fbbf24` (gold)
- WhatsApp CTA: `#25D366` (green)
- Globe satellite: `#5577ff`, `#88aaff` (blue)
- Background orbs: `rgba(120,60,255,0.10)` (purple), `rgba(0,180,160,0.45)` (teal)

---

## Page Sections (in order)

| # | Section | HTML Anchor | Description |
|---|---------|-------------|-------------|
| 1 | Preloader | — | Progress bar + counter, exits with slide-up |
| 2 | Navigation | — | Fixed sticky, scroll-hide/show, mobile burger |
| 3 | Hero | `#home` | 3D sphere, gradient headline, CTA buttons, ticker |
| 4 | Pillars | — | 3-col: Story First / Built to Convert / Fast & Premium |
| 5 | Showreel 2026 | `#work` | Video showcase section |
| 6 | Full Stack | `#about` | Services marquee + tech stack chips |
| 7 | Process | — | 6-step accordion: Brief→Concept→Script→AI Prod→Edit→Deliver |
| 8 | Services | `#services` | 8 service cards in 3-col grid |
| 9 | Why Us | — | Feature grid + tabs (SMEs / Enterprises / Startups / Traditional) |
| 10 | Global Reach | — | Interactive Three.js globe with city markers |
| 11 | Selected Work | — | 4 portfolio cards with video thumbnails |
| 12 | Testimonials | — | Slider with 4 testimonials + animated stats counters |
| 13 | Clients | — | Dual marquee of brand names + categories |
| 14 | FAQ | `#faq` | 6-item accordion |
| 15 | Contact | `#contact` | Form (name/email/company/message) + contact info |
| 16 | CTA Strip | — | Final conversion strip |
| 17 | Footer | — | Logo, social links, 3-col nav, copyright 2026 |

---

## JavaScript Modules (all in `script.js`)

| Function | What it does |
|----------|-------------|
| `initPreloader()` | Progress bar 0→100%, exits translateY(-100%) |
| `initScrollProgress()` | Top bar tracks scroll via scaleX |
| `initCursorEnhanced()` | 8px orange dot + 14-point particle trail (desktop only) |
| `initMagnetic()` | Buttons follow mouse (38% offset) with ripple on click |
| `initTiltCards()` | 3D tilt on `.svc-card`, `.work-card` via perspective |
| `TextScramble` (class) | Random char substitution on `.section-label` elements |
| `initHeroShader()` | Three.js icosahedron + FBM noise + 3 orbiting rings + stars |
| `initGlobeEnhanced()` | Three.js globe with 12 city markers, arcs, satellite, drag |
| `initProcess()` | Single-open accordion for process steps |
| `initFAQ()` | Single-open accordion for FAQ |
| `initSlider()` | Testimonials auto-advance (5500ms) + dot nav |
| `initCounters()` | Animated number counters triggered by IntersectionObserver |
| `initTabs()` | Why-Us tab button active state |
| `initForm()` | AJAX FormSubmit.co with honeypot + validation |
| `initVideoModal()` | Click `[data-video]` → modal player, ESC to close |
| `initActiveNav()` | IntersectionObserver highlights active nav link |

### Mobile/Performance Detection
```js
const IS_MOBILE  = window.innerWidth < 768;
const IS_LOW_END = IS_MOBILE || navigator.hardwareConcurrency <= 2;
```
Low-end: disables cursor, magnetic buttons, tilt, parallax. Three.js quality reduced.

---

## Contact & Company Details

| Field | Value |
|-------|-------|
| Email | uday.khandelwal@the5thkind.in |
| WhatsApp | +91 82960 08838 |
| Phone | +91 82960 08838 |
| Address | 529, 8th Cross Nanjappa Road, Shantinagar, Bangalore |
| Instagram | https://www.instagram.com/the5thkind.ai/ |
| YouTube | https://youtube.com/@the5thkind.ai |
| LinkedIn | https://linkedin.com/company/the5thkind.ai |

---

## Branding Rules

- **Logo text:** `The5thkind` + `<span>.ai</span>` (`.ai` in `--accent` orange)
- **Favicon:** Orange square (#f97316) with white "5K"
- **Never use frameworks** — stay vanilla HTML/CSS/JS
- **Color discipline:** Dark-mode only. `--accent` (#f97316) for all interactive/CTA elements
- **No images** — all visuals are CSS gradients, SVG inline, or Three.js 3D
- **Font:** Inter only. Georgia used only for testimonial quote marks

---

## Development Conventions

- **No build step** — edit files directly, refresh browser to preview
- **CSS architecture:** Single `style.css`, section-grouped with comments like `/* === HERO === */`
- **JS architecture:** Single `script.js`, one `init*` function per feature, all called at `DOMContentLoaded`
- **Responsive breakpoints:** `@media (max-width: 768px)` primary mobile, `@media (max-width: 1024px)` tablet
- **Animations:** Use `--ease` variable for consistent easing. Intersection Observer for scroll reveals
- **Class conventions:** BEM-ish (`.svc-card`, `.svc-icon`, `.svc-title`). No utility-first

---

## Form Handling

The contact form posts via AJAX to FormSubmit.co:
```js
fetch('https://formsubmit.co/ajax/uday.khandelwal@the5thkind.in', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
  body: JSON.stringify({ name, email, company, message,
    _subject: 'New inquiry from The Fifth Kind website',
    _template: 'table' })
})
```
Honeypot field `.hp-field` has `tabindex="-1"` and is visually hidden. If filled, submission is silently dropped.

---

## Three.js Details

### Hero Sphere (`initHeroShader`)
- Geometry: IcosahedronGeometry with FBM (Fractional Brownian Motion) noise vertex displacement
- Fragment: 3-point dynamic lighting, Fresnel rim (power 3.8), specular highlights
- Colors: orange (#f97316) ↔ dark blue (#020218)
- Extras: wireframe overlay (0.045 opacity), 3 dashed orbiting rings, particle swarms, 1800-star field
- Mouse tilt: lerp 0.048

### Interactive Globe (`initGlobeEnhanced`)
- 4000 Fibonacci-distributed surface dots
- 12 city markers with pulsing halos
- 8 arc routes with animated traveller particles
- Satellite ring + orbiting dot
- Drag-to-rotate with inertia (decay 0.82 dragging / 0.94 free)
- Atmosphere: subtle blue sphere glow
