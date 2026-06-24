/* ============================================================
   THE5THKIND.AI — SCRIPT v4
   One Stop AI Studio — Complete Redesign
   ============================================================ */

'use strict';

const IS_MOBILE = window.innerWidth < 768;
const IS_LOW_END = IS_MOBILE || (navigator.hardwareConcurrency <= 2);

/* ── UTILS ─────────────────────────────────────────────────── */
function lerp(a, b, t) { return a + (b - a) * t; }
function clamp(v, min, max) { return Math.min(Math.max(v, min), max); }
function rand(a, b) { return a + Math.random() * (b - a); }
function map(v, a, b, c, d) { return c + ((v - a) / (b - a)) * (d - c); }

/* ── PRELOADER ─────────────────────────────────────────────── */
function initPreloader() {
  const el = document.getElementById('preloader');
  const bar = document.getElementById('pl-bar');
  const pct = document.getElementById('pl-pct');
  const canvas = document.getElementById('pl-canvas');
  if (!el) return;

  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  // Particle field for preloader
  const particles = Array.from({ length: IS_LOW_END ? 60 : 150 }, () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    vx: rand(-0.5, 0.5),
    vy: rand(-0.5, 0.5),
    size: rand(1, 3),
    alpha: rand(0.1, 0.6),
    color: Math.random() > 0.7 ? '#f97316' : '#ffffff'
  }));

  let animId;
  function drawPl() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = canvas.width;
      if (p.x > canvas.width) p.x = 0;
      if (p.y < 0) p.y = canvas.height;
      if (p.y > canvas.height) p.y = 0;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha;
      ctx.fill();
    });
    ctx.globalAlpha = 1;
    animId = requestAnimationFrame(drawPl);
  }
  drawPl();

  let prog = 0;
  const start = performance.now();
  const duration = IS_LOW_END ? 1800 : 2600;
  function tick() {
    const elapsed = performance.now() - start;
    prog = Math.min(1, elapsed / duration);
    const pctVal = Math.round(prog * 100);
    bar.style.width = pctVal + '%';
    pct.textContent = pctVal + '%';
    if (prog < 1) {
      requestAnimationFrame(tick);
    } else {
      setTimeout(() => {
        cancelAnimationFrame(animId);
        el.classList.add('exit');
        setTimeout(() => { el.style.display = 'none'; }, 900);
      }, 300);
    }
  }
  requestAnimationFrame(tick);
}

/* ── SCROLL PROGRESS ───────────────────────────────────────── */
function initScrollProgress() {
  const fill = document.getElementById('scroll-fill');
  if (!fill) return;
  window.addEventListener('scroll', () => {
    const total = document.body.scrollHeight - window.innerHeight;
    fill.style.width = (total > 0 ? (window.scrollY / total) * 100 : 0) + '%';
  }, { passive: true });
}

/* ── CURSOR ─────────────────────────────────────────────────── */
function initCursor() {
  if (IS_MOBILE) return;
  const dot = document.getElementById('cur-dot');
  const ring = document.getElementById('cur-ring');
  if (!dot || !ring) return;

  let mx = 0, my = 0, rx = 0, ry = 0;
  const TRAIL = 12;
  const trail = [];
  const canvas = document.createElement('canvas');
  canvas.style.cssText = 'position:fixed;top:0;left:0;pointer-events:none;z-index:9996;width:100%;height:100%;';
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  document.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');

  window.addEventListener('mousemove', e => {
    mx = e.clientX; my = e.clientY;
    trail.push({ x: mx, y: my, a: 1 });
    if (trail.length > TRAIL) trail.shift();
    dot.style.left = mx + 'px';
    dot.style.top = my + 'px';
  }, { passive: true });

  document.querySelectorAll('a,button,[data-magnetic]').forEach(el => {
    el.addEventListener('mouseenter', () => document.body.classList.add('cursor-hover'));
    el.addEventListener('mouseleave', () => document.body.classList.remove('cursor-hover'));
  });

  window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  });

  function animCursor() {
    rx = lerp(rx, mx, 0.15);
    ry = lerp(ry, my, 0.15);
    ring.style.left = rx + 'px';
    ring.style.top = ry + 'px';

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < trail.length; i++) {
      const t = trail[i];
      const alpha = (i / trail.length) * 0.4;
      const size = map(i, 0, trail.length, 2, 5);
      ctx.beginPath();
      ctx.arc(t.x, t.y, size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(249,115,22,${alpha})`;
      ctx.fill();
    }
    requestAnimationFrame(animCursor);
  }
  animCursor();
}

/* ── MAGNETIC BUTTONS ───────────────────────────────────────── */
function initMagnetic() {
  if (IS_MOBILE) return;
  document.querySelectorAll('[data-magnetic]').forEach(el => {
    el.addEventListener('mousemove', e => {
      const r = el.getBoundingClientRect();
      const dx = e.clientX - (r.left + r.width / 2);
      const dy = e.clientY - (r.top + r.height / 2);
      el.style.transform = `translate(${dx * 0.3}px, ${dy * 0.3}px)`;
    });
    el.addEventListener('mouseleave', () => { el.style.transform = ''; });
  });
}

/* ── TILT CARDS ─────────────────────────────────────────────── */
function initTilt() {
  if (IS_MOBILE) return;
  document.querySelectorAll('[data-tilt]').forEach(el => {
    el.addEventListener('mousemove', e => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      el.style.transform = `perspective(800px) rotateX(${-y * 10}deg) rotateY(${x * 10}deg) translateY(-8px)`;
    });
    el.addEventListener('mouseleave', () => {
      el.style.transform = '';
    });
  });
}

/* ── SCROLL REVEAL ──────────────────────────────────────────── */
function initReveal() {
  const els = document.querySelectorAll('[data-reveal]');
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const delay = parseInt(el.dataset.delay || 0);
      setTimeout(() => el.classList.add('revealed'), delay);
      obs.unobserve(el);
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });
  els.forEach(el => obs.observe(el));
}

/* ── NAV ────────────────────────────────────────────────────── */
function initNav() {
  const nav = document.getElementById('nav');
  const burger = document.getElementById('nav-burger');
  const mobile = document.getElementById('nav-mobile');
  if (!nav) return;

  let lastY = 0;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    nav.classList.toggle('scrolled', y > 60);
    nav.classList.toggle('hidden', y > lastY + 10 && y > 200);
    if (y < lastY || y < 100) nav.classList.remove('hidden');
    lastY = y;
  }, { passive: true });

  burger?.addEventListener('click', () => {
    mobile?.classList.toggle('open');
  });

  mobile?.querySelectorAll('.nm-link').forEach(a => {
    a.addEventListener('click', () => mobile.classList.remove('open'));
  });

  // Active nav
  const sections = document.querySelectorAll('section[id]');
  const links = document.querySelectorAll('.nav-link');
  const sectionObs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        links.forEach(l => l.classList.remove('active'));
        const active = document.querySelector(`.nav-link[href="#${entry.target.id}"]`);
        if (active) active.classList.add('active');
      }
    });
  }, { threshold: 0.4 });
  sections.forEach(s => sectionObs.observe(s));
}

/* ── COUNTERS ───────────────────────────────────────────────── */
function initCounters() {
  const els = document.querySelectorAll('[data-counter]');
  const obs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const target = parseInt(el.dataset.counter);
      const duration = 1800;
      const start = performance.now();
      function tick(now) {
        const progress = Math.min((now - start) / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(ease * target);
        if (progress < 1) requestAnimationFrame(tick);
        else el.textContent = target;
      }
      requestAnimationFrame(tick);
      obs.unobserve(el);
    });
  }, { threshold: 0.5 });
  els.forEach(el => obs.observe(el));
}

/* ── FAQ ────────────────────────────────────────────────────── */
function initFAQ() {
  document.querySelectorAll('.faq-item').forEach(item => {
    const q = item.querySelector('.faq-q');
    const a = item.querySelector('.faq-a');
    q?.addEventListener('click', () => {
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach(other => {
        other.classList.remove('open');
        const oa = other.querySelector('.faq-a');
        if (oa) oa.style.maxHeight = '0';
      });
      if (!isOpen) {
        item.classList.add('open');
        if (a) a.style.maxHeight = a.scrollHeight + 'px';
      }
    });
  });
}

/* ── TABS ───────────────────────────────────────────────────── */
function initTabs() {
  const nav = document.getElementById('tab-nav');
  const panels = document.getElementById('tab-panels');
  if (!nav || !panels) return;
  nav.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      nav.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const tab = btn.dataset.tab;
      panels.querySelectorAll('.tab-pane').forEach(p => {
        p.classList.toggle('active', p.dataset.pane === tab);
      });
    });
  });
}

/* ── TESTIMONIAL SLIDER ─────────────────────────────────────── */
function initSlider() {
  const track = document.getElementById('testi-track');
  const dots = document.getElementById('testi-dots');
  const prev = document.getElementById('tnav-prev');
  const next = document.getElementById('tnav-next');
  if (!track) return;

  let current = 0;
  const slides = track.children;
  const total = slides.length;
  let autoTimer;

  function goTo(n) {
    current = (n + total) % total;
    track.style.transform = `translateX(${-current * 100}%)`;
    dots?.querySelectorAll('.tdot').forEach((d, i) => d.classList.toggle('active', i === current));
  }

  function startAuto() {
    autoTimer = setInterval(() => goTo(current + 1), 5500);
  }

  prev?.addEventListener('click', () => { clearInterval(autoTimer); goTo(current - 1); startAuto(); });
  next?.addEventListener('click', () => { clearInterval(autoTimer); goTo(current + 1); startAuto(); });

  dots?.querySelectorAll('.tdot').forEach((d, i) => {
    d.addEventListener('click', () => { clearInterval(autoTimer); goTo(i); startAuto(); });
  });

  startAuto();
}

/* ── BOT CHAT ANIMATION ─────────────────────────────────────── */
function initBotChat() {
  const chat = document.getElementById('bot-chat');
  if (!chat) return;

  const conversation = [
    { type: 'send', text: 'Hi, I need help with my order #4892' },
    { type: 'recv', text: 'Found order #4892 for Rahul. Your package is out for delivery today. Expected by 4–6 PM. 📦' },
    { type: 'send', text: 'Can I change the delivery address?' },
    { type: 'recv', text: 'Sure! I\'ve updated your delivery address. You\'ll receive a confirmation SMS shortly. Is there anything else? ✅' },
    { type: 'send', text: 'That\'s all, thanks!' },
    { type: 'recv', text: 'Happy to help! Have a great day! 😊 Your issue has been resolved.' },
  ];

  let idx = 0;
  const obs = new IntersectionObserver(entries => {
    if (!entries[0].isIntersecting) return;
    obs.disconnect();
    function addMsg() {
      if (idx >= conversation.length) {
        setTimeout(() => {
          chat.innerHTML = '';
          idx = 0;
          // First message
          const first = document.createElement('div');
          first.className = 'bot-msg bot-recv';
          first.innerHTML = '<div class="bot-avatar-icon">AI</div><div class="bot-bubble">Hi! I\'m your AI assistant. How can I help you today? 👋</div>';
          chat.appendChild(first);
          setTimeout(addMsg, 2000);
        }, 4000);
        return;
      }
      const msg = conversation[idx++];
      const div = document.createElement('div');
      div.className = `bot-msg bot-${msg.type}`;
      if (msg.type === 'recv') {
        div.innerHTML = `<div class="bot-avatar-icon">AI</div><div class="bot-bubble"></div>`;
      } else {
        div.innerHTML = `<div class="bot-bubble"></div>`;
      }
      chat.appendChild(div);
      const bubble = div.querySelector('.bot-bubble');
      // Typing animation
      let charIdx = 0;
      const typing = setInterval(() => {
        bubble.textContent = msg.text.slice(0, ++charIdx);
        chat.scrollTop = chat.scrollHeight;
        if (charIdx >= msg.text.length) {
          clearInterval(typing);
          setTimeout(addMsg, 1200);
        }
      }, 30);
    }
    setTimeout(addMsg, 1500);
  }, { threshold: 0.5 });
  obs.observe(chat);
}

/* ── VIDEO MODAL ────────────────────────────────────────────── */
function initVideoModal() {
  const modal = document.getElementById('video-modal');
  const player = document.getElementById('vmodal-player');
  const closeBtn = document.getElementById('vmodal-close');
  if (!modal || !player) return;

  document.querySelectorAll('[data-video]').forEach(card => {
    card.addEventListener('click', () => {
      const src = card.dataset.video;
      player.src = src;
      player.play();
      modal.classList.add('open');
      document.body.style.overflow = 'hidden';
    });
  });

  function closeModal() {
    modal.classList.remove('open');
    player.pause();
    player.src = '';
    document.body.style.overflow = '';
  }

  closeBtn?.addEventListener('click', closeModal);
  modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

  // Video hover preview
  document.querySelectorAll('.work-video-bg').forEach(vid => {
    const card = vid.closest('.work-card');
    card?.addEventListener('mouseenter', () => {
      vid.load();
      vid.play().catch(() => {});
    });
    card?.addEventListener('mouseleave', () => {
      vid.pause();
      vid.currentTime = 0;
    });
  });
}

/* ── CONTACT FORM ───────────────────────────────────────────── */
function initForm() {
  const form = document.getElementById('contact-form');
  const msgEl = document.getElementById('form-msg');
  const btnText = document.getElementById('form-btn-text');
  if (!form) return;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const hp = form.querySelector('.hp-field');
    if (hp?.value) return;

    const name = form.querySelector('[name="name"]')?.value.trim();
    const email = form.querySelector('[name="email"]')?.value.trim();
    const message = form.querySelector('[name="message"]')?.value.trim();
    if (!name || !email || !message) {
      showMsg('Please fill in all required fields.', 'error');
      return;
    }

    if (btnText) btnText.textContent = 'Sending…';

    const data = {};
    new FormData(form).forEach((v, k) => { if (k !== '_hp') data[k] = v; });
    data._subject = 'New AI inquiry from The Fifth Kind website';
    data._template = 'table';

    try {
      const res = await fetch('https://formsubmit.co/ajax/uday.khandelwal@the5thkind.in', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      });
      const json = await res.json();
      if (json.success === 'true' || json.success === true) {
        showMsg("Message sent! We'll respond within 24 hours.", 'success');
        form.reset();
      } else {
        showMsg('Something went wrong. Please email us directly.', 'error');
      }
    } catch {
      showMsg('Network error. Please email uday.khandelwal@the5thkind.in directly.', 'error');
    }
    if (btnText) btnText.textContent = 'Send Message';
  });

  function showMsg(text, type) {
    if (!msgEl) return;
    msgEl.textContent = text;
    msgEl.className = `form-feedback show ${type}`;
    setTimeout(() => msgEl.classList.remove('show'), 6000);
  }
}

/* ── PROCESS STEP HIGHLIGHT ─────────────────────────────────── */
function initProcess() {
  const steps = document.querySelectorAll('.proc-step');
  if (!steps.length) return;
  const obs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      entry.target.classList.toggle('active', entry.isIntersecting);
    });
  }, { threshold: 0.6 });
  steps.forEach(s => obs.observe(s));
}

/* ── THREE.JS PREMIUM SPHERE BACKGROUND ─────────────────────── */
function initBgScene() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas || typeof THREE === 'undefined') return;

  const W = () => window.innerWidth;
  const H = () => window.innerHeight;

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: !IS_LOW_END, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, IS_LOW_END ? 1 : 1.5));
  renderer.setSize(W(), H());
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(65, W() / H(), 0.1, 600);
  camera.position.set(5, 0, 46);

  const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  let scrollProgress = 0;

  window.addEventListener('mousemove', e => {
    mouse.tx = (e.clientX / W() - 0.5) * 2;
    mouse.ty = (e.clientY / H() - 0.5) * 2;
  }, { passive: true });

  window.addEventListener('scroll', () => {
    const total = document.body.scrollHeight - window.innerHeight;
    scrollProgress = total > 0 ? Math.min(1, window.scrollY / total) : 0;
  }, { passive: true });

  // ── GLSL VERTEX SHADER (FBM noise displacement) ───────────────
  const vertexShader = `
    uniform float uTime;
    varying vec3 vNormal;
    varying vec3 vWorldPos;
    varying float vNoise;

    float hash(vec3 p) {
      p = fract(p * 0.3183099 + 0.1);
      p *= 17.0;
      return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
    }
    float n3(vec3 x) {
      vec3 i = floor(x), f = fract(x);
      f = f * f * (3.0 - 2.0 * f);
      return mix(
        mix(mix(hash(i),          hash(i+vec3(1,0,0)),f.x),
            mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),
        mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),
            mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);
    }
    float fbm(vec3 p) {
      float v=0.0,a=0.5;
      for(int i=0;i<6;i++){v+=a*n3(p);p=p*2.0+vec3(100.0);a*=0.5;}
      return v;
    }

    void main() {
      vNormal = normalize(normalMatrix * normal);
      float n = fbm(position * 0.26 + uTime * 0.07);
      vNoise = n;
      vec3 d = position + normal * ((n * 2.0 - 1.0) * 2.0);
      vWorldPos = (modelMatrix * vec4(d, 1.0)).xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(d, 1.0);
    }
  `;

  // ── GLSL FRAGMENT SHADER (Fresnel + multi-light) ──────────────
  const fragmentShader = `
    uniform float uTime;
    uniform float uMix;   /* 0=warm orange, 1=cool cyan */
    uniform float uPulse; /* 0-1, solar flare burst */

    varying vec3 vNormal;
    varying vec3 vWorldPos;
    varying float vNoise;

    void main() {
      vec3 N = normalize(vNormal);
      vec3 V = normalize(cameraPosition - vWorldPos);
      float cosA = max(dot(N, V), 0.0);
      float fresnel = pow(1.0 - cosA, 3.2);

      /* Colour palette */
      vec3 warmRim  = vec3(0.99, 0.46, 0.07);   /* orange   */
      vec3 coolRim  = vec3(0.0,  0.83, 1.0);    /* cyan     */
      vec3 hotRim   = vec3(1.0,  0.75, 0.3);    /* warm highlight */
      vec3 deepCore = vec3(0.01, 0.01, 0.09);   /* abyss    */
      vec3 midCore  = vec3(0.04, 0.01, 0.14);   /* deep purple */

      vec3 rim  = mix(warmRim, coolRim, uMix);
      vec3 core = mix(deepCore, midCore, uMix);

      /* Noise-driven surface texture */
      float n = smoothstep(0.28, 0.72, vNoise);
      vec3 surface = mix(core, rim * 0.35, n);

      /* Fresnel rim glow — the money shot */
      vec3 col = surface + rim * fresnel * 1.8;

      /* Key specular highlight */
      vec3 Lk = normalize(vec3(1.4, 1.0, 1.2));
      vec3 Hk = normalize(Lk + V);
      float spec = pow(max(dot(N, Hk), 0.0), 56.0);
      col += mix(hotRim, coolRim, uMix) * spec * 0.9;

      /* Warm fill from below */
      vec3 Lf = normalize(vec3(-0.5, -1.0, 0.3));
      float fill = max(dot(N, Lf), 0.0) * 0.1;
      col += rim * fill;

      /* Sub-surface scatter fake: thin orange glow inside */
      float sss = (1.0 - cosA) * n * 0.25;
      col += warmRim * sss;

      /* Solar flare pulse — whole surface floods with white-orange */
      col += (warmRim * 1.6 + vec3(1.0)) * uPulse * (fresnel * 2.0 + n * 0.8);

      float alpha = clamp(0.45 + fresnel * 0.55 + n * 0.15 + uPulse * 0.35, 0.0, 1.0);
      gl_FragColor = vec4(col, alpha);
    }
  `;

  // ── MAIN SPHERE ───────────────────────────────────────────────
  const DETAIL = IS_LOW_END ? 5 : 9;
  const sphereGeo = new THREE.IcosahedronGeometry(16, DETAIL);
  const sphereMat = new THREE.ShaderMaterial({
    vertexShader, fragmentShader,
    uniforms: { uTime: { value: 0 }, uMix: { value: 0 }, uPulse: { value: 0 } },
    transparent: true,
    depthWrite: false
  });
  const sphere = new THREE.Mesh(sphereGeo, sphereMat);
  sphere.position.set(7, 0, 0);
  scene.add(sphere);

  // Sparse wireframe overlay — gives structure without clutter
  if (!IS_LOW_END) {
    const wireGeo = new THREE.IcosahedronGeometry(16.3, 3);
    const wireMat = new THREE.MeshBasicMaterial({
      color: 0xf97316, wireframe: true,
      transparent: true, opacity: 0.035
    });
    const wire = new THREE.Mesh(wireGeo, wireMat);
    scene.add(wire);
    sphere.userData.wire = wire;
  }

  // ── ATMOSPHERIC OUTER GLOW ────────────────────────────────────
  const atmGeo = new THREE.SphereGeometry(19.5, 32, 32);
  const atmMat = new THREE.MeshBasicMaterial({
    color: 0xf97316, transparent: true,
    opacity: 0.055, side: THREE.BackSide
  });
  const atm = new THREE.Mesh(atmGeo, atmMat);
  atm.position.copy(sphere.position);
  scene.add(atm);

  // Second, wider very-faint glow layer
  const atm2Geo = new THREE.SphereGeometry(24, 24, 24);
  const atm2Mat = new THREE.MeshBasicMaterial({
    color: 0xf97316, transparent: true,
    opacity: 0.018, side: THREE.BackSide
  });
  const atm2 = new THREE.Mesh(atm2Geo, atm2Mat);
  atm2.position.copy(sphere.position);
  scene.add(atm2);

  // ── ORBITAL RINGS ─────────────────────────────────────────────
  function makeRing(R, tube, hex, opacity, rx, ry, rz, speed) {
    const grp = new THREE.Group();
    grp.position.copy(sphere.position);

    // Ring body
    const geo  = new THREE.TorusGeometry(R, tube, 8, IS_LOW_END ? 80 : 160);
    const mat  = new THREE.MeshBasicMaterial({ color: hex, transparent: true, opacity, side: THREE.DoubleSide });
    grp.add(new THREE.Mesh(geo, mat));

    // Bright traveling node
    const tGeo = new THREE.SphereGeometry(tube * 2.8, 8, 8);
    const tMat = new THREE.MeshBasicMaterial({ color: hex, transparent: true, opacity: 1.0 });
    const trav = new THREE.Mesh(tGeo, tMat);
    grp.add(trav);

    // Comet tail (line behind traveler)
    const tailPts = [];
    for (let i = 0; i < 20; i++) tailPts.push(new THREE.Vector3());
    const tailGeo = new THREE.BufferGeometry().setFromPoints(tailPts);
    const tailMat = new THREE.LineBasicMaterial({ color: hex, transparent: true, opacity: 0.3 });
    const tail = new THREE.Line(tailGeo, tailMat);
    grp.add(tail);

    grp.rotation.set(rx, ry, rz);
    scene.add(grp);
    return { grp, trav, tail, R, speed, tailBuf: tailPts };
  }

  const rings = [
    makeRing(21.5, 0.20, 0xf97316, 0.55,  0.42,  0.12,  0.20,  0.22),
    makeRing(26.0, 0.13, 0x00d4ff, 0.38, -0.28,  0.52, -0.14, -0.16),
    makeRing(18.5, 0.09, 0xb060ff, 0.28,  0.88, -0.18,  0.38,  0.31),
  ];

  // ── CRISP STAR FIELD ──────────────────────────────────────────
  const STAR_N = IS_LOW_END ? 500 : 1100;
  const sPos = new Float32Array(STAR_N * 3);
  const sCol = new Float32Array(STAR_N * 3);
  for (let i = 0; i < STAR_N; i++) {
    const r = rand(60, 160);
    const phi = Math.acos(2 * Math.random() - 1);
    const th = Math.random() * Math.PI * 2;
    sPos[i*3]   = r * Math.sin(phi) * Math.cos(th);
    sPos[i*3+1] = r * Math.sin(phi) * Math.sin(th);
    sPos[i*3+2] = r * Math.cos(phi);
    // Slightly vary star color (white to pale blue to pale warm)
    const rnd = Math.random();
    if (rnd > 0.85) { sCol[i*3]=1;sCol[i*3+1]=0.85;sCol[i*3+2]=0.6; }      // warm
    else if (rnd > 0.65) { sCol[i*3]=0.75;sCol[i*3+1]=0.85;sCol[i*3+2]=1; } // cool
    else { sCol[i*3]=1;sCol[i*3+1]=1;sCol[i*3+2]=1; }                        // white
  }
  const starGeo = new THREE.BufferGeometry();
  starGeo.setAttribute('position', new THREE.BufferAttribute(sPos, 3));
  starGeo.setAttribute('color',    new THREE.BufferAttribute(sCol, 3));
  const starMat = new THREE.PointsMaterial({
    size: 0.20, vertexColors: true, transparent: true, opacity: 0.65, sizeAttenuation: true
  });
  scene.add(new THREE.Points(starGeo, starMat));

  // Bright foreground star cluster — adds depth
  const fgN = 80;
  const fgPos = new Float32Array(fgN * 3);
  for (let i = 0; i < fgN; i++) {
    fgPos[i*3] = rand(-80, 80); fgPos[i*3+1] = rand(-50, 50); fgPos[i*3+2] = rand(10, 30);
  }
  const fgGeo = new THREE.BufferGeometry();
  fgGeo.setAttribute('position', new THREE.BufferAttribute(fgPos, 3));
  const fgMat = new THREE.PointsMaterial({ size: 0.35, color: 0xffffff, transparent: true, opacity: 0.18, sizeAttenuation: true });
  scene.add(new THREE.Points(fgGeo, fgMat));

  // ── PORTAL TRIGGER — first-scroll cinematic transition ────────
  let portalFired = false;
  const portalWaves = [];    // expanding torus shockwaves
  let pulseMag = 0;          // sphere solar-flare pulse 0→1→0
  let warpT = 0;             // warp streak timeline 0→1
  let warpActive = false;

  // Warp streak line-segments (invisible until trigger)
  const WARP_N = IS_LOW_END ? 120 : 380;
  const warpBuf = new Float32Array(WARP_N * 2 * 3); // 2 verts per streak
  const warpGeo = new THREE.BufferGeometry();
  warpGeo.setAttribute('position', new THREE.BufferAttribute(warpBuf, 3));
  const warpMat = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0 });
  scene.add(new THREE.LineSegments(warpGeo, warpMat));

  // Pre-compute each streak's radial direction + depth
  const warpDirs = Array.from({ length: WARP_N }, () => {
    const phi = Math.acos(2 * Math.random() - 1);
    const th  = Math.random() * Math.PI * 2;
    return {
      x: Math.sin(phi) * Math.cos(th),
      y: Math.sin(phi) * Math.sin(th),
      z: Math.cos(phi),
      near: rand(30, 65),
      len:  rand(10, 35)
    };
  });

  function firePortal() {
    if (portalFired) return;
    portalFired = true;
    pulseMag   = 1.0;
    warpActive = true;
    warpT      = 0;

    // CSS flash overlay
    const flash = document.getElementById('scroll-flash');
    if (flash) {
      flash.classList.add('active');
      setTimeout(() => flash.classList.remove('active'), 1100);
    }

    // Hero brightness burst — overexposure as portal opens
    const heroEl = document.querySelector('.hero');
    if (heroEl) {
      heroEl.classList.add('portal-exiting');
      setTimeout(() => heroEl.classList.remove('portal-exiting'), 300);
    }

    // 3 shockwave tori — staggered, different axes & colors
    const waveSpec = [
      { ms: 0,   color: 0xf97316, rx: 0.35,  ry: 0.15,  tube: 0.22, speed: 44 },
      { ms: 130, color: 0x00d4ff, rx: -0.5,  ry: 0.6,   tube: 0.14, speed: 38 },
      { ms: 270, color: 0xb060ff, rx: 0.9,   ry: -0.3,  tube: 0.10, speed: 50 }
    ];
    waveSpec.forEach(({ ms, color, rx, ry, tube, speed }) => {
      setTimeout(() => {
        const geo = new THREE.TorusGeometry(1, tube, 8, 100);
        const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.85, side: THREE.DoubleSide });
        const ring = new THREE.Mesh(geo, mat);
        ring.position.copy(sphere.position);
        ring.rotation.set(rx, ry, 0);
        scene.add(ring);
        portalWaves.push({ mesh: ring, s: 1, speed });
      }, ms);
    });
  }

  // Trigger once when user scrolls past 55px
  window.addEventListener('scroll', () => {
    if (!portalFired && window.scrollY > 55) firePortal();
  }, { passive: true });

  // ── ANIMATION LOOP ────────────────────────────────────────────
  const clock = new THREE.Clock();
  let colorMix = 0, colorMixTarget = 0;
  let camX = 5, camY = 0;

  const tailHistory = rings.map(() => []);

  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();

    // Mouse smoothing
    mouse.x = lerp(mouse.x, mouse.tx, 0.04);
    mouse.y = lerp(mouse.y, mouse.ty, 0.04);

    // Scroll-driven color temperature
    if (scrollProgress < 0.3)      colorMixTarget = 0;               // warm orange
    else if (scrollProgress < 0.6) colorMixTarget = map(scrollProgress, 0.3, 0.6, 0, 1); // orange → cyan
    else if (scrollProgress < 0.8) colorMixTarget = 1;               // cool cyan
    else                           colorMixTarget = map(scrollProgress, 0.8, 1, 1, 0.4); // cool → warm again
    colorMix = lerp(colorMix, colorMixTarget, 0.025);

    // Update shader uniforms
    sphereMat.uniforms.uTime.value = t;
    sphereMat.uniforms.uMix.value  = colorMix;

    // Sphere scroll drift — moves gently off-center as user scrolls
    const spTargX = 7 - scrollProgress * 5;
    const spTargY =   - scrollProgress * 10;
    sphere.position.x = lerp(sphere.position.x, spTargX, 0.025);
    sphere.position.y = lerp(sphere.position.y, spTargY, 0.025);

    // Very slow organic rotation on sphere
    sphere.rotation.y = t * 0.055;
    sphere.rotation.x = Math.sin(t * 0.04) * 0.08;
    if (sphere.userData.wire) {
      sphere.userData.wire.position.copy(sphere.position);
      sphere.userData.wire.rotation.copy(sphere.rotation);
    }

    // Atmosphere tracks sphere
    atm.position.copy(sphere.position);
    atm2.position.copy(sphere.position);
    // Atmosphere color shift
    const ac = new THREE.Color().lerpColors(new THREE.Color(0xf97316), new THREE.Color(0x00aaff), colorMix);
    atmMat.color = ac;
    atm2Mat.color = ac;
    // Pulse breathing
    const breathe = 1 + Math.sin(t * 0.7) * 0.015;
    atm.scale.setScalar(breathe);

    // Orbital rings
    rings.forEach((r, i) => {
      r.grp.position.copy(sphere.position);
      const angle = t * r.speed;
      // Traveler position in local ring XY plane
      const tx = Math.cos(angle) * r.R;
      const ty = Math.sin(angle) * r.R;
      r.trav.position.set(tx, ty, 0);

      // Comet tail: keep last 20 positions
      const hist = tailHistory[i];
      hist.unshift({ x: tx, y: ty });
      if (hist.length > 20) hist.pop();
      const tailPos = r.tail.geometry.attributes.position;
      if (tailPos) {
        for (let j = 0; j < Math.min(hist.length, 20); j++) {
          tailPos.setXYZ(j, hist[j].x, hist[j].y, 0);
        }
        tailPos.needsUpdate = true;
      }
    });

    // Camera parallax with mouse + slow drift
    camX = lerp(camX, 5 + mouse.x * 5, 0.03);
    camY = lerp(camY, -mouse.y * 3, 0.03);
    camera.position.x = camX;
    camera.position.y = camY;
    camera.lookAt(0, -scrollProgress * 3, 0);

    // ── Portal transition updates ────────────────────────────────
    // Sphere solar-flare pulse
    if (pulseMag > 0) {
      pulseMag = Math.max(0, pulseMag - 0.018);
      sphereMat.uniforms.uPulse.value = pulseMag < 0.001 ? 0 : pulseMag;
    }

    // Shockwave tori: scale up fast, fade out
    for (let i = portalWaves.length - 1; i >= 0; i--) {
      const w = portalWaves[i];
      w.s += 0.9;
      w.mesh.scale.setScalar(w.s);
      w.mesh.material.opacity = Math.max(0, 0.85 - w.s * 0.019);
      if (w.mesh.material.opacity <= 0) {
        scene.remove(w.mesh);
        portalWaves.splice(i, 1);
      }
    }

    // Warp star streaks: radial elongation that rises and falls
    if (warpActive) {
      warpT = Math.min(1, warpT + 0.022);
      // Smooth rise (0→0.5) and fall (0.5→1) — bell curve
      const phase = warpT < 0.5 ? warpT * 2 : (1 - warpT) * 2;
      const eased = phase * phase * (3 - 2 * phase); // smoothstep
      warpMat.opacity = eased * 0.75;
      const attr = warpGeo.attributes.position;
      warpDirs.forEach((d, i) => {
        const near = d.near;
        const far  = near + d.len * eased * 5;
        attr.setXYZ(i * 2,     d.x * near, d.y * near, d.z * near);
        attr.setXYZ(i * 2 + 1, d.x * far,  d.y * far,  d.z * far);
      });
      attr.needsUpdate = true;
      if (warpT >= 1) { warpActive = false; warpMat.opacity = 0; }
    }

    renderer.render(scene, camera);
  }

  animate();

  window.addEventListener('resize', () => {
    renderer.setSize(W(), H());
    camera.aspect = W() / H();
    camera.updateProjectionMatrix();
  });
}

/* ── THREE.JS GLOBE ─────────────────────────────────────────── */
function initGlobe() {
  const canvas = document.getElementById('globe-canvas');
  if (!canvas || typeof THREE === 'undefined') return;

  const size = canvas.parentElement?.clientWidth || 500;
  const W = size, H = 450;
  canvas.style.width = W + 'px';
  canvas.style.height = H + 'px';

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: !IS_LOW_END });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(W, H);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(55, W / H, 0.1, 200);
  camera.position.set(0, 0, 35);

  const GROUP = new THREE.Group();
  scene.add(GROUP);

  // Globe dot surface
  const DOT_COUNT = IS_LOW_END ? 1500 : 3500;
  const R = 13;
  const dotPositions = new Float32Array(DOT_COUNT * 3);
  const dotColors = new Float32Array(DOT_COUNT * 3);
  for (let i = 0; i < DOT_COUNT; i++) {
    const phi = Math.acos(1 - 2 * (i + 0.5) / DOT_COUNT);
    const theta = Math.PI * (1 + Math.sqrt(5)) * i;
    dotPositions[i * 3] = R * Math.sin(phi) * Math.cos(theta);
    dotPositions[i * 3 + 1] = R * Math.sin(phi) * Math.sin(theta);
    dotPositions[i * 3 + 2] = R * Math.cos(phi);
    dotColors[i * 3] = 0.1; dotColors[i * 3 + 1] = 0.6; dotColors[i * 3 + 2] = 0.9;
  }
  const dotGeo = new THREE.BufferGeometry();
  dotGeo.setAttribute('position', new THREE.BufferAttribute(dotPositions, 3));
  dotGeo.setAttribute('color', new THREE.BufferAttribute(dotColors, 3));
  const dotMat = new THREE.PointsMaterial({ size: 0.18, vertexColors: true, transparent: true, opacity: 0.7 });
  GROUP.add(new THREE.Points(dotGeo, dotMat));

  // Atmosphere
  const atmGeo = new THREE.SphereGeometry(R + 0.8, 32, 32);
  const atmMat = new THREE.MeshBasicMaterial({ color: 0x0044ff, transparent: true, opacity: 0.04, side: THREE.FrontSide });
  GROUP.add(new THREE.Mesh(atmGeo, atmMat));

  // City markers
  const cities = [
    { lat: 12.97, lng: 77.59, name: 'Bangalore' },
    { lat: 19.08, lng: 72.88, name: 'Mumbai' },
    { lat: 28.61, lng: 77.21, name: 'Delhi' },
    { lat: 25.20, lng: 55.27, name: 'Dubai' },
    { lat: 1.35, lng: 103.82, name: 'Singapore' },
    { lat: 51.51, lng: -0.13, name: 'London' },
    { lat: 40.71, lng: -74.01, name: 'New York' },
    { lat: 37.77, lng: -122.42, name: 'San Francisco' },
    { lat: 35.68, lng: 139.69, name: 'Tokyo' },
    { lat: -33.87, lng: 151.21, name: 'Sydney' },
    { lat: 48.85, lng: 2.35, name: 'Paris' },
    { lat: -26.20, lng: 28.04, name: 'Johannesburg' },
  ];

  function latLngToVec(lat, lng, r) {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lng + 180) * (Math.PI / 180);
    return new THREE.Vector3(
      -r * Math.sin(phi) * Math.cos(theta),
      r * Math.cos(phi),
      r * Math.sin(phi) * Math.sin(theta)
    );
  }

  const markerGeo = new THREE.SphereGeometry(0.25, 8, 8);
  cities.forEach(city => {
    const pos = latLngToVec(city.lat, city.lng, R + 0.3);
    const mat = new THREE.MeshBasicMaterial({ color: 0xf97316 });
    const mesh = new THREE.Mesh(markerGeo, mat);
    mesh.position.copy(pos);
    GROUP.add(mesh);

    // Halo ring
    const haloGeo = new THREE.RingGeometry(0.4, 0.7, 16);
    const haloMat = new THREE.MeshBasicMaterial({ color: 0xf97316, transparent: true, opacity: 0.4, side: THREE.DoubleSide });
    const halo = new THREE.Mesh(haloGeo, haloMat);
    halo.position.copy(pos);
    halo.lookAt(0, 0, 0);
    GROUP.add(halo);
  });

  // Arc routes
  const arcs = [
    [0, 3], [0, 5], [0, 6], [1, 4], [3, 8], [5, 6], [4, 9], [2, 10]
  ];
  arcs.forEach(([a, b]) => {
    const from = latLngToVec(cities[a].lat, cities[a].lng, R + 0.5);
    const to = latLngToVec(cities[b].lat, cities[b].lng, R + 0.5);
    const mid = new THREE.Vector3().addVectors(from, to).multiplyScalar(0.5);
    mid.normalize().multiplyScalar(R * 1.6);

    const curve = new THREE.QuadraticBezierCurve3(from, mid, to);
    const pts = curve.getPoints(40);
    const arcGeo = new THREE.BufferGeometry().setFromPoints(pts);
    const arcMat = new THREE.LineBasicMaterial({ color: 0xf97316, transparent: true, opacity: 0.3 });
    GROUP.add(new THREE.Line(arcGeo, arcMat));
  });

  // Drag rotate
  let isDragging = false, prevX = 0, prevY = 0, velX = 0, velY = 0;
  canvas.addEventListener('mousedown', e => { isDragging = true; prevX = e.clientX; prevY = e.clientY; velX = velY = 0; });
  window.addEventListener('mouseup', () => { isDragging = false; });
  window.addEventListener('mousemove', e => {
    if (!isDragging) return;
    const dx = e.clientX - prevX;
    const dy = e.clientY - prevY;
    velX = dx * 0.01; velY = dy * 0.01;
    GROUP.rotation.y += velX;
    GROUP.rotation.x += velY;
    prevX = e.clientX; prevY = e.clientY;
  });
  canvas.addEventListener('touchstart', e => { isDragging = true; prevX = e.touches[0].clientX; prevY = e.touches[0].clientY; });
  canvas.addEventListener('touchend', () => { isDragging = false; });
  canvas.addEventListener('touchmove', e => {
    if (!isDragging) return;
    const dx = e.touches[0].clientX - prevX;
    const dy = e.touches[0].clientY - prevY;
    velX = dx * 0.01; velY = dy * 0.01;
    GROUP.rotation.y += velX;
    GROUP.rotation.x += velY;
    prevX = e.touches[0].clientX; prevY = e.touches[0].clientY;
  });

  const clock = new THREE.Clock();
  function animateGlobe() {
    requestAnimationFrame(animateGlobe);
    const dt = clock.getDelta();
    if (!isDragging) {
      GROUP.rotation.y += 0.003;
      velX *= 0.94; velY *= 0.94;
    } else {
      velX *= 0.82; velY *= 0.82;
    }
    renderer.render(scene, camera);
  }
  animateGlobe();
}

/* ── SMOOTH SCROLL ──────────────────────────────────────────── */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

/* ── WORK CARD VIDEO HOVER ──────────────────────────────────── */
function initWorkCards() {
  document.querySelectorAll('.work-card').forEach(card => {
    const vid = card.querySelector('.work-video-bg');
    if (!vid) return;
    const io = new IntersectionObserver(entries => {
      if (!entries[0].isIntersecting) vid.pause();
    }, { threshold: 0.3 });
    io.observe(card);
  });
}

/* ── INIT ─────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initPreloader();
  initScrollProgress();
  initNav();
  initReveal();
  initCounters();
  initFAQ();
  initTabs();
  initSlider();
  initBotChat();
  initVideoModal();
  initForm();
  initProcess();
  initBgScene();
  initGlobe();
  initSmoothScroll();
  initWorkCards();
  if (!IS_MOBILE) {
    initCursor();
    initMagnetic();
    initTilt();
  }
});
