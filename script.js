/* ============================================================
   THE5THKIND.AI — ENHANCED SCRIPT v2
   Advanced Three.js shader sphere · orbiting rings · enhanced
   globe with satellite · magnetic buttons · cursor particles
   · 3D card tilt · text scramble · preloader
   ============================================================ */
'use strict';

/* ──────────────────────────────────────────────────────────
   GLOBALS & UTILS
   ────────────────────────────────────────────────────────── */
const IS_MOBILE  = window.innerWidth < 768;
const IS_LOW_END = IS_MOBILE || (navigator.hardwareConcurrency || 4) <= 2;
const lerp  = (a, b, t) => a + (b - a) * t;
const clamp = (v, mn, mx) => Math.max(mn, Math.min(mx, v));

/* ──────────────────────────────────────────────────────────
   PRELOADER
   ────────────────────────────────────────────────────────── */
function initPreloader() {
  const pre  = document.getElementById('preloader');
  const fill = document.getElementById('preFill');
  const pct  = document.getElementById('prePct');
  if (!pre) return;
  let progress = 0;
  const timer = setInterval(() => {
    progress += Math.random() * 22 + 4;
    if (progress >= 100) {
      progress = 100;
      clearInterval(timer);
      if (fill) fill.style.width = '100%';
      if (pct)  pct.textContent  = '100%';
      setTimeout(() => {
        pre.classList.add('exit');
        setTimeout(() => pre.remove(), 900);
      }, 280);
    }
    if (fill) fill.style.width = Math.min(progress, 97) + '%';
    if (pct)  pct.textContent  = Math.floor(progress) + '%';
  }, 55);
}

/* ──────────────────────────────────────────────────────────
   SCROLL PROGRESS BAR
   ────────────────────────────────────────────────────────── */
function initScrollProgress() {
  const bar = document.getElementById('scrollProgress');
  if (!bar) return;
  window.addEventListener('scroll', () => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.transform = `scaleX(${window.scrollY / max})`;
  }, { passive: true });
}

/* ──────────────────────────────────────────────────────────
   ENHANCED CURSOR + PARTICLE TRAIL
   ────────────────────────────────────────────────────────── */
function initCursorEnhanced() {
  if (IS_MOBILE) return;
  const dot   = document.getElementById('cursor');
  const trail = document.getElementById('cursorTrail');
  if (!dot || !trail) return;

  let mx = 0, my = 0, tx = 0, ty = 0;

  const TRAIL = 14;
  const pts   = [];
  for (let i = 0; i < TRAIL; i++) {
    const p  = document.createElement('div');
    const sz = (1 - i / TRAIL) * 5 + 1;
    p.className = 'cursor-particle';
    p.style.cssText = `position:fixed;pointer-events:none;z-index:9997;
      width:${sz}px;height:${sz}px;border-radius:50%;
      background:rgba(249,115,22,${(1 - i / TRAIL) * 0.7});
      transform:translate(-50%,-50%);`;
    document.body.appendChild(p);
    pts.push({ el: p, x: 0, y: 0 });
  }

  document.addEventListener('mousemove', e => {
    mx = e.clientX; my = e.clientY;
    dot.style.left = mx + 'px'; dot.style.top = my + 'px';
  });

  document.querySelectorAll('a,button,.svc-card,.work-card,.faq-q,.step-head').forEach(el => {
    el.addEventListener('mouseenter', () => {
      dot.style.transform = 'translate(-50%,-50%) scale(0)';
      trail.style.width = trail.style.height = '52px';
      trail.style.borderColor = 'rgba(249,115,22,0.65)';
    });
    el.addEventListener('mouseleave', () => {
      dot.style.transform = 'translate(-50%,-50%) scale(1)';
      trail.style.width = trail.style.height = '30px';
      trail.style.borderColor = 'rgba(249,115,22,0.45)';
    });
  });

  (function loop() {
    tx = lerp(tx, mx, 0.13); ty = lerp(ty, my, 0.13);
    trail.style.left = tx + 'px'; trail.style.top = ty + 'px';
    let px = mx, py = my;
    pts.forEach(p => {
      p.x = lerp(p.x, px, 0.09); p.y = lerp(p.y, py, 0.09);
      p.el.style.left = p.x + 'px'; p.el.style.top = p.y + 'px';
      px = p.x; py = p.y;
    });
    requestAnimationFrame(loop);
  })();
}

/* ──────────────────────────────────────────────────────────
   MAGNETIC BUTTONS
   ────────────────────────────────────────────────────────── */
function initMagnetic() {
  if (IS_MOBILE) return;
  document.querySelectorAll('.btn-fill, .nav-cta, .btn-ghost').forEach(btn => {
    btn.addEventListener('mousemove', e => {
      const r  = btn.getBoundingClientRect();
      btn.style.transform = `translate(${(e.clientX - r.left - r.width/2)*0.38}px,${(e.clientY - r.top - r.height/2)*0.38}px)`;
    });
    btn.addEventListener('mouseleave', () => { btn.style.transform = ''; });
    btn.addEventListener('click', e => {
      const r = btn.getBoundingClientRect();
      btn.style.setProperty('--rx', ((e.clientX - r.left) / r.width  * 100) + '%');
      btn.style.setProperty('--ry', ((e.clientY - r.top)  / r.height * 100) + '%');
    });
  });
}

/* ──────────────────────────────────────────────────────────
   3D CARD TILT
   ────────────────────────────────────────────────────────── */
function initTiltCards() {
  if (IS_MOBILE) return;
  document.querySelectorAll('.svc-card, .work-card').forEach(card => {
    card.addEventListener('mousemove', e => {
      const r  = card.getBoundingClientRect();
      const dx = (e.clientX - r.left - r.width  / 2) / r.width;
      const dy = (e.clientY - r.top  - r.height / 2) / r.height;
      card.style.transition = 'transform 0.1s ease';
      card.style.transform  = `perspective(900px) rotateX(${dy*-11}deg) rotateY(${dx*11}deg) translateY(-5px) scale(1.015)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transition = 'transform 0.45s ease, border-color 0.25s ease, box-shadow 0.25s ease';
      card.style.transform  = '';
    });
  });
}

/* ──────────────────────────────────────────────────────────
   TEXT SCRAMBLE
   ────────────────────────────────────────────────────────── */
class TextScramble {
  constructor(el) {
    this.el = el; this.chars = '!<>-_\\/[]{}=+*^?#@$%&';
    this.frame = 0; this.queue = [];
    this.update = this.update.bind(this);
  }
  setText(newText) {
    const old = this.el.textContent;
    const len = Math.max(old.length, newText.length);
    this.resolve = null;
    const p = new Promise(r => (this.resolve = r));
    this.queue = Array.from({ length: len }, (_, i) => ({
      from: old[i] || '', to: newText[i] || '',
      start: Math.floor(Math.random() * 10),
      end:   Math.floor(Math.random() * 10) + 10, char: '',
    }));
    cancelAnimationFrame(this._raf);
    this.frame = 0; this._raf = requestAnimationFrame(this.update);
    return p;
  }
  update() {
    let out = '', done = 0;
    this.queue.forEach(q => {
      if (this.frame >= q.end) { done++; out += q.to; }
      else if (this.frame >= q.start) {
        if (!q.char || Math.random() < 0.28)
          q.char = this.chars[Math.floor(Math.random() * this.chars.length)];
        out += `<span class="scramble-char">${q.char}</span>`;
      } else { out += q.from; }
    });
    this.el.innerHTML = out;
    if (done === this.queue.length) this.resolve && this.resolve();
    else { this.frame++; this._raf = requestAnimationFrame(this.update); }
  }
}

/* ──────────────────────────────────────────────────────────
   NAV — auto-hide on scroll down, reveal on scroll up
   ────────────────────────────────────────────────────────── */
function initNavEnhanced() {
  const nav = document.getElementById('navbar');
  let last = 0;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    nav.classList.toggle('stuck',  y > 40);
    nav.classList.toggle('hidden', y > last + 12 && y > 240);
    if (y < last || y < 100) nav.classList.remove('hidden');
    last = y;
  }, { passive: true });
}

/* ──────────────────────────────────────────────────────────
   REVEAL + SECTION LABEL SCRAMBLE
   ────────────────────────────────────────────────────────── */
function initRevealEnhanced() {
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in-view');
      io.unobserve(e.target);
    });
  }, { threshold: 0.07, rootMargin: '0px 0px -44px 0px' });

  document.querySelectorAll('.reveal, .fade-section').forEach(el => {
    const parent = el.parentElement;
    if (parent && ['svc-grid','why-grid','work-grid'].some(c => parent.classList.contains(c)))
      el.style.transitionDelay = (Array.from(parent.children).indexOf(el) * 0.09) + 's';
    io.observe(el);
  });

  const labelIO = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const sc = new TextScramble(e.target);
      sc.setText(e.target.textContent.trim());
      labelIO.unobserve(e.target);
    });
  }, { threshold: 0.85 });
  document.querySelectorAll('.section-label').forEach(el => labelIO.observe(el));
}

/* ──────────────────────────────────────────────────────────
   PARALLAX — hero content + bg orbs on scroll
   ────────────────────────────────────────────────────────── */
function initParallaxEnhanced() {
  const hc   = document.querySelector('.hero-content');
  const orbs = document.querySelectorAll('.bg-orb');
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (hc && !IS_MOBILE) {
      hc.style.transform = `translateY(${y * 0.17}px)`;
      hc.style.opacity   = Math.max(0, 1 - y / 640);
    }
    orbs.forEach((o, i) => { o.style.transform = `translateY(${y * (0.06 + i * 0.04)}px)`; });
  }, { passive: true });
}

/* ============================================================
   THREE.JS — HERO SHADER SPHERE
   FBM noise-displaced icosahedron · 3-point dynamic lighting
   fresnel rim · specular · orbiting dashed rings · star field
   ============================================================ */
function initHeroShader() {
  if (typeof THREE === 'undefined') return;
  const canvas    = document.getElementById('heroCanvas');
  const container = document.getElementById('hero3d');
  if (!canvas || !container) return;

  let W = container.clientWidth  || window.innerWidth;
  let H = container.clientHeight || window.innerHeight;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: !IS_LOW_END, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, IS_LOW_END ? 1.5 : 2));
  renderer.setSize(W, H);
  renderer.toneMapping         = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;

  const scene  = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(44, W / H, 0.1, 100);
  camera.position.z = 4.6;

  /* ── VERTEX — FBM gradient noise displacement ── */
  const vertexShader = `
    uniform float uTime;
    varying vec3  vNormal;
    varying vec3  vWorldPos;
    varying float vNoise;

    vec3 hash3(vec3 p) {
      p = fract(p * vec3(0.1031, 0.1030, 0.0973));
      p += dot(p, p.yxz + 33.33);
      return fract((p.xxy + p.yxx) * p.zyx);
    }

    float gradNoise(vec3 p) {
      vec3 i = floor(p); vec3 f = fract(p);
      vec3 u = f * f * (3.0 - 2.0 * f);
      float n000 = dot(hash3(i)                * 2.0 - 1.0, f);
      float n100 = dot(hash3(i+vec3(1,0,0))   * 2.0 - 1.0, f-vec3(1,0,0));
      float n010 = dot(hash3(i+vec3(0,1,0))   * 2.0 - 1.0, f-vec3(0,1,0));
      float n110 = dot(hash3(i+vec3(1,1,0))   * 2.0 - 1.0, f-vec3(1,1,0));
      float n001 = dot(hash3(i+vec3(0,0,1))   * 2.0 - 1.0, f-vec3(0,0,1));
      float n101 = dot(hash3(i+vec3(1,0,1))   * 2.0 - 1.0, f-vec3(1,0,1));
      float n011 = dot(hash3(i+vec3(0,1,1))   * 2.0 - 1.0, f-vec3(0,1,1));
      float n111 = dot(hash3(i+vec3(1,1,1))   * 2.0 - 1.0, f-vec3(1,1,1));
      return mix(mix(mix(n000,n100,u.x),mix(n010,n110,u.x),u.y),
                 mix(mix(n001,n101,u.x),mix(n011,n111,u.x),u.y), u.z);
    }

    float fbm(vec3 p) {
      float v=0.0,a=0.55;
      v+=a*gradNoise(p); p=p*2.2+vec3(1.7,9.2,3.8); a*=0.48;
      v+=a*gradNoise(p); p=p*2.2+vec3(8.3,2.8,5.1); a*=0.48;
      v+=a*gradNoise(p); p=p*2.2+vec3(3.4,6.1,8.9); a*=0.48;
      v+=a*gradNoise(p); p=p*2.2+vec3(7.2,4.3,1.6); a*=0.48;
      v+=a*gradNoise(p);
      return v;
    }

    void main() {
      vNormal = normalize(normalMatrix * normal);
      float n = fbm(position * 1.5 + vec3(uTime*0.17, uTime*0.12, uTime*0.20));
      vNoise  = n;
      vec3 disp    = position + normal * (n * 0.28);
      vWorldPos    = (modelMatrix * vec4(disp, 1.0)).xyz;
      gl_Position  = projectionMatrix * modelViewMatrix * vec4(disp, 1.0);
    }
  `;

  /* ── FRAGMENT — 3-point lighting + fresnel rim + emissive peaks ── */
  const fragmentShader = `
    uniform float uTime;
    uniform vec3  uL1; uniform vec3 uL2; uniform vec3 uL3;
    varying vec3  vNormal; varying vec3 vWorldPos; varying float vNoise;

    void main() {
      vec3 n  = normalize(vNormal);
      vec3 v  = normalize(cameraPosition - vWorldPos);
      float fr = pow(1.0 - max(dot(v, n), 0.0), 3.8);

      vec3 l1 = normalize(uL1-vWorldPos);
      vec3 l2 = normalize(uL2-vWorldPos);
      vec3 l3 = normalize(uL3-vWorldPos);
      float d1=max(dot(n,l1),0.0), d2=max(dot(n,l2),0.0), d3=max(dot(n,l3),0.0);
      float sp1=pow(max(dot(reflect(-l1,n),v),0.0),90.0);
      float sp2=pow(max(dot(reflect(-l2,n),v),0.0),45.0);

      float  t     = clamp(vNoise*1.9+0.55, 0.0, 1.0);
      vec3 colA    = vec3(0.97, 0.35, 0.04);
      vec3 colB    = vec3(0.02, 0.02, 0.18);
      vec3 rimCol  = vec3(0.78, 0.48, 1.00);
      vec3 base    = mix(colB, colA, t);

      vec3 col = base * 0.04;
      col += base * d1 * vec3(1.00,0.52,0.08) * 2.4;
      col += base * d2 * vec3(0.18,0.42,1.00) * 1.5;
      col += base * d3 * vec3(0.40,0.85,0.50) * 0.55;
      col += sp1       * vec3(1.00,0.68,0.22) * 2.2;
      col += sp2       * vec3(0.50,0.70,1.00) * 0.85;
      col += fr        * rimCol               * 1.7;

      float e = pow(max(vNoise,0.0),4.5) * (sin(uTime*2.8)*0.5+0.5) * 3.0;
      col += e * colA;

      gl_FragColor = vec4(col, 0.9);
    }
  `;

  const heroMat = new THREE.ShaderMaterial({
    vertexShader, fragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uL1:   { value: new THREE.Vector3( 3.2, 1.8, 2.5) },
      uL2:   { value: new THREE.Vector3(-2.6,-1.1, 1.0) },
      uL3:   { value: new THREE.Vector3( 0.4,-3.2,-2.0) },
    },
    transparent: true,
  });

  const detail = IS_LOW_END ? 3 : 5;
  const sphere = new THREE.Mesh(new THREE.IcosahedronGeometry(1.1, detail), heroMat);
  scene.add(sphere);

  /* ── Wireframe overlay ── */
  scene.add(new THREE.Mesh(
    new THREE.IcosahedronGeometry(1.13, 2),
    new THREE.MeshBasicMaterial({ color: 0xf97316, wireframe: true, transparent: true, opacity: 0.045 })
  ));

  /* ── Core breathe glow ── */
  const coreM = new THREE.MeshBasicMaterial({ color: 0xff6810, transparent: true, opacity: 0.07 });
  const core  = new THREE.Mesh(new THREE.SphereGeometry(0.72, 16, 16), coreM);
  scene.add(core);

  /* ── Orbiting rings ── */
  function makeRing(r, segs, color, opacity, dashed) {
    const pts = [];
    for (let i = 0; i <= segs; i++) {
      const a = (i / segs) * Math.PI * 2;
      pts.push(new THREE.Vector3(Math.cos(a) * r, 0, Math.sin(a) * r));
    }
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    const mat = dashed
      ? new THREE.LineDashedMaterial({ color, transparent: true, opacity, dashSize: 0.18, gapSize: 0.10, blending: THREE.AdditiveBlending, depthWrite: false })
      : new THREE.LineBasicMaterial({  color, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false });
    const line = new THREE.Line(geo, mat);
    if (dashed) line.computeLineDistances();
    return line;
  }

  const ring1 = makeRing(1.78, 220, 0xff7722, 0.65, false);
  const ring2 = makeRing(2.18, 220, 0xff5500, 0.40, true);
  const ring3 = makeRing(2.62, 220, 0xffaa77, 0.22, true);
  ring1.rotation.x = Math.PI * 0.20; ring1.rotation.z = Math.PI * 0.07;
  ring2.rotation.x = Math.PI * 0.52; ring2.rotation.z = Math.PI * 0.17;
  ring3.rotation.x = Math.PI * 0.76; ring3.rotation.y = Math.PI * 0.32;
  scene.add(ring1, ring2, ring3);

  /* ── Orbital particle swarms ── */
  function makeOrbPts(r, n, color) {
    const pos = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2 + Math.random() * 0.25;
      const rr = r + (Math.random() - 0.5) * 0.08;
      pos[i*3]=Math.cos(a)*rr; pos[i*3+1]=(Math.random()-0.5)*0.055; pos[i*3+2]=Math.sin(a)*rr;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    return new THREE.Points(geo, new THREE.PointsMaterial({
      size: 0.028, color, transparent: true, opacity: 0.92,
      blending: THREE.AdditiveBlending, depthWrite: false, sizeAttenuation: true,
    }));
  }
  const cnt  = IS_LOW_END ? 80 : 220;
  const orb1 = makeOrbPts(1.78, cnt,                  0xff7722);
  const orb2 = makeOrbPts(2.18, Math.floor(cnt*0.7),  0xff9955);
  const orb3 = makeOrbPts(2.62, Math.floor(cnt*0.5),  0xffcc99);
  orb1.rotation.copy(ring1.rotation);
  orb2.rotation.copy(ring2.rotation);
  orb3.rotation.copy(ring3.rotation);
  scene.add(orb1, orb2, orb3);

  /* ── Background star field ── */
  if (!IS_LOW_END) {
    const N=1800, sp=new Float32Array(N*3), sc=new Float32Array(N*3);
    for (let i=0;i<N;i++) {
      const phi=Math.acos(2*Math.random()-1), th=Math.random()*Math.PI*2, r=7.5+Math.random()*4;
      sp[i*3]=r*Math.sin(phi)*Math.cos(th); sp[i*3+1]=r*Math.cos(phi); sp[i*3+2]=r*Math.sin(phi)*Math.sin(th);
      const b=0.3+Math.random()*0.7; sc[i*3]=b; sc[i*3+1]=b*0.9; sc[i*3+2]=b;
    }
    const sGeo=new THREE.BufferGeometry();
    sGeo.setAttribute('position',new THREE.BufferAttribute(sp,3));
    sGeo.setAttribute('color',   new THREE.BufferAttribute(sc,3));
    scene.add(new THREE.Points(sGeo, new THREE.PointsMaterial({
      size:0.018, vertexColors:true, transparent:true, opacity:0.5,
      blending:THREE.AdditiveBlending, depthWrite:false,
    })));
  }

  /* ── Mouse tilt ── */
  let mNX=0, mNY=0, tNX=0, tNY=0;
  document.addEventListener('mousemove', e => {
    mNX=(e.clientX/window.innerWidth -0.5)*2;
    mNY=(e.clientY/window.innerHeight-0.5)*2;
  });

  /* ── Animate ── */
  const clock = new THREE.Clock();
  const La    = { a1:0, a2:2.1, a3:4.2 };

  (function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();
    tNX = lerp(tNX, mNX, 0.048); tNY = lerp(tNY, mNY, 0.048);

    heroMat.uniforms.uTime.value = t;

    La.a1=t*0.62; La.a2=t*-0.43+2.1; La.a3=t*0.27+4.2;
    heroMat.uniforms.uL1.value.set(Math.cos(La.a1)*3.4, 1.9+Math.sin(t*0.38)*0.85, Math.sin(La.a1)*3.4);
    heroMat.uniforms.uL2.value.set(Math.cos(La.a2)*2.7,-1.1+Math.sin(t*0.29)*0.6,  Math.sin(La.a2)*2.7);
    heroMat.uniforms.uL3.value.set(Math.cos(La.a3)*3.9, 0.5+Math.sin(t*0.51)*1.1,  Math.sin(La.a3)*3.9);

    sphere.rotation.y = t*0.10 + tNX*0.32;
    sphere.rotation.x = t*0.04 + tNY*-0.18;

    ring1.rotation.z+=0.0055; ring2.rotation.y+=0.0040;
    ring3.rotation.x+=0.0032; ring3.rotation.z+=0.0018;
    orb1.rotation.z +=0.0055; orb2.rotation.y +=0.0040;
    orb3.rotation.x +=0.0032; orb3.rotation.z +=0.0018;

    coreM.opacity = 0.05 + Math.sin(t*2.1)*0.03;
    renderer.render(scene, camera);
  })();

  /* ── Resize ── */
  const ro = new ResizeObserver(() => {
    W=container.clientWidth; H=container.clientHeight;
    camera.aspect=W/H; camera.updateProjectionMatrix();
    renderer.setSize(W, H);
  });
  ro.observe(container);
}

/* ============================================================
   THREE.JS — ENHANCED INTERACTIVE GLOBE
   Dot surface · markers + pulsing halos · quadratic arcs
   with moving traveller particles · satellite orbit ring+dot
   drag-to-rotate with inertia
   ============================================================ */
function initGlobeEnhanced() {
  if (typeof THREE === 'undefined') return;
  const canvas = document.getElementById('globeCanvas');
  if (!canvas) return;

  const wrap = canvas.parentElement;
  const SIZE = Math.min(wrap.clientWidth || 400, 480);

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(SIZE, SIZE);

  const scene  = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
  camera.position.z = 2.65;

  const globeGroup = new THREE.Group();
  scene.add(globeGroup);

  /* ── Surface dots (Fibonacci) ── */
  const DOT_N = IS_LOW_END ? 2000 : 4000;
  const dPos  = new Float32Array(DOT_N * 3);
  const dCol  = new Float32Array(DOT_N * 3);
  const GR    = Math.PI * (1 + Math.sqrt(5));
  for (let i=0;i<DOT_N;i++) {
    const phi=Math.acos(1-2*(i+0.5)/DOT_N), theta=GR*i;
    const x=Math.sin(phi)*Math.cos(theta), y=Math.cos(phi), z=Math.sin(phi)*Math.sin(theta);
    dPos[i*3]=x; dPos[i*3+1]=y; dPos[i*3+2]=z;
    const b=0.42+Math.random()*0.48; dCol[i*3]=b; dCol[i*3+1]=b; dCol[i*3+2]=b*1.2;
  }
  const dg=new THREE.BufferGeometry();
  dg.setAttribute('position',new THREE.BufferAttribute(dPos,3));
  dg.setAttribute('color',   new THREE.BufferAttribute(dCol,3));
  globeGroup.add(new THREE.Points(dg, new THREE.PointsMaterial({
    size:0.011, vertexColors:true, transparent:true, opacity:0.75,
    blending:THREE.AdditiveBlending, depthWrite:false, sizeAttenuation:true,
  })));

  globeGroup.add(new THREE.Mesh(
    new THREE.SphereGeometry(1.003, 32, 32),
    new THREE.MeshBasicMaterial({ color:0x1a1a3a, wireframe:true, transparent:true, opacity:0.28 })
  ));

  /* ── lat/lon → Vec3 ── */
  function ll2v(lat, lon, r=1.0) {
    const phi=(90-lat)*(Math.PI/180), theta=(lon+180)*(Math.PI/180);
    return new THREE.Vector3(-r*Math.sin(phi)*Math.cos(theta), r*Math.cos(phi), r*Math.sin(phi)*Math.sin(theta));
  }

  /* ── City markers + halos ── */
  const CITIES=[[40.7,-74.0],[51.5,0.1],[48.9,2.3],[25.2,55.3],[19.1,72.9],[1.3,103.8],
                [35.7,139.8],[-33.9,151.2],[-23.5,-46.6],[43.7,-79.4],[55.7,37.6],[-26.2,28.0]];
  const mGeo=new THREE.SphereGeometry(0.017,8,8);
  const hGeo=new THREE.RingGeometry(0.024,0.036,16);
  const markers = CITIES.map(([lat,lon]) => {
    const v = ll2v(lat,lon,1.012);
    const dot = new THREE.Mesh(mGeo, new THREE.MeshBasicMaterial({color:0xf97316}));
    dot.position.copy(v); globeGroup.add(dot);
    const halo = new THREE.Mesh(hGeo, new THREE.MeshBasicMaterial({color:0xf97316,transparent:true,opacity:0.5,side:THREE.DoubleSide}));
    halo.position.copy(ll2v(lat,lon,1.016));
    halo.lookAt(v.clone().multiplyScalar(3)); globeGroup.add(halo);
    return { dot, halo };
  });

  /* ── Arcs with moving particles ── */
  const PAIRS=[[[40.7,-74.0],[51.5,0.1]],[[51.5,0.1],[25.2,55.3]],[[25.2,55.3],[19.1,72.9]],
               [[19.1,72.9],[1.3,103.8]],[[1.3,103.8],[35.7,139.8]],[[40.7,-74.0],[-23.5,-46.6]],
               [[55.7,37.6],[48.9,2.3]], [[43.7,-79.4],[40.7,-74.0]]];
  const arcMat = new THREE.LineBasicMaterial({color:0xf97316,transparent:true,opacity:0.35,blending:THREE.AdditiveBlending,depthWrite:false});
  const arcTravellers = PAIRS.map(([a,b]) => {
    const vA=ll2v(...a,1.022), vB=ll2v(...b,1.022);
    const mid=vA.clone().add(vB).normalize().multiplyScalar(1.38);
    const curve=new THREE.QuadraticBezierCurve3(vA,mid,vB);
    globeGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve.getPoints(56)), arcMat.clone()));
    const traveller=new THREE.Mesh(new THREE.SphereGeometry(0.014,6,6),
      new THREE.MeshBasicMaterial({color:0xffaa44,transparent:true,opacity:0.95,blending:THREE.AdditiveBlending}));
    globeGroup.add(traveller);
    return { curve, traveller, progress:Math.random(), speed:0.16+Math.random()*0.22 };
  });

  /* ── Satellite ring + dot ── */
  const SAT_R = 1.30;
  const satPts=[];
  for(let i=0;i<=140;i++){const a=(i/140)*Math.PI*2; satPts.push(new THREE.Vector3(Math.cos(a)*SAT_R,0,Math.sin(a)*SAT_R));}
  const satLine=new THREE.Line(new THREE.BufferGeometry().setFromPoints(satPts),
    new THREE.LineDashedMaterial({color:0x5577ff,transparent:true,opacity:0.40,dashSize:0.09,gapSize:0.06,blending:THREE.AdditiveBlending,depthWrite:false}));
  satLine.rotation.x=Math.PI*0.34; satLine.rotation.z=Math.PI*0.08;
  satLine.computeLineDistances(); scene.add(satLine);
  const satDot=new THREE.Mesh(new THREE.SphereGeometry(0.024,8,8),
    new THREE.MeshBasicMaterial({color:0x88aaff,transparent:true,opacity:0.9}));
  scene.add(satDot);

  /* ── Atmosphere ── */
  scene.add(new THREE.Mesh(new THREE.SphereGeometry(1.19,32,32),
    new THREE.MeshBasicMaterial({color:0x1144cc,transparent:true,opacity:0.045,side:THREE.BackSide})));

  /* ── Drag rotation ── */
  let drag=false, px=0, py=0, vx=0, vy=0.004, rotX=0, rotY=0;
  const onDown=(cx,cy)=>{drag=true;px=cx;py=cy;vx=vy=0;};
  const onMove=(cx,cy)=>{if(!drag)return;vx=(cy-py)*0.006;vy=(cx-px)*0.006;px=cx;py=cy;};
  const onUp=()=>{drag=false;};
  canvas.addEventListener('mousedown', e=>onDown(e.clientX,e.clientY));
  canvas.addEventListener('touchstart',e=>onDown(e.touches[0].clientX,e.touches[0].clientY),{passive:true});
  window.addEventListener('mousemove', e=>onMove(e.clientX,e.clientY));
  window.addEventListener('touchmove', e=>onMove(e.touches[0].clientX,e.touches[0].clientY),{passive:true});
  window.addEventListener('mouseup',onUp); window.addEventListener('touchend',onUp);

  /* ── Animate ── */
  const clock=new THREE.Clock();
  (function animate() {
    requestAnimationFrame(animate);
    const t=clock.getElapsedTime();

    if(drag){vx*=0.82;vy*=0.82;}else{vx*=0.94;vy=vy*0.94+0.004*0.06;}
    rotX=clamp(rotX+vx,-1.1,1.1); rotY+=vy;
    globeGroup.rotation.x=rotX; globeGroup.rotation.y=rotY;

    markers.forEach(({dot,halo},i)=>{
      const s=1+Math.sin(t*3.2+i*0.85)*0.28;
      dot.scale.setScalar(s);
      halo.material.opacity=0.28+Math.sin(t*3.2+i*0.85)*0.24;
      halo.scale.setScalar(1+Math.sin(t*3.2+i*0.85+0.5)*0.5);
    });

    arcTravellers.forEach(arc=>{
      arc.progress=(arc.progress+arc.speed*0.0038)%1;
      arc.traveller.position.copy(arc.curve.getPoint(arc.progress));
      arc.traveller.material.opacity=0.6+Math.sin(arc.progress*Math.PI)*0.35;
    });

    const sa=t*0.52;
    const local=new THREE.Vector3(Math.cos(sa)*SAT_R, 0, Math.sin(sa)*SAT_R);
    local.applyEuler(satLine.rotation);
    satDot.position.copy(local);
    satDot.material.opacity=0.75+Math.sin(t*4)*0.2;

    renderer.render(scene,camera);
  })();

  const ro=new ResizeObserver(()=>{const s=Math.min(wrap.clientWidth,480);renderer.setSize(s,s);});
  ro.observe(wrap);
}

/* ──────────────────────────────────────────────────────────
   MOBILE MENU
   ────────────────────────────────────────────────────────── */
function initMobileMenu() {
  const burger  = document.getElementById('burger');
  const mobMenu = document.getElementById('mobMenu');
  if (!burger || !mobMenu) return;
  burger.addEventListener('click', () => {
    const open = mobMenu.classList.toggle('open');
    burger.classList.toggle('open', open);
    document.body.style.overflow = open ? 'hidden' : '';
  });
  mobMenu.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      mobMenu.classList.remove('open');
      burger.classList.remove('open');
      document.body.style.overflow = '';
    });
  });
}

/* ──────────────────────────────────────────────────────────
   PROCESS ACCORDION
   ────────────────────────────────────────────────────────── */
function initProcess() {
  document.querySelectorAll('.step .step-head').forEach(head => {
    head.addEventListener('click', () => {
      const step   = head.parentElement;
      const isOpen = step.classList.contains('active');
      document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
      if (!isOpen) step.classList.add('active');
    });
  });
}

/* ──────────────────────────────────────────────────────────
   FAQ ACCORDION
   ────────────────────────────────────────────────────────── */
function initFAQ() {
  document.querySelectorAll('.faq-item').forEach(item => {
    item.querySelector('.faq-q').addEventListener('click', () => {
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });
}

/* ──────────────────────────────────────────────────────────
   TESTIMONIALS SLIDER
   ────────────────────────────────────────────────────────── */
function initSlider() {
  const slides = document.querySelectorAll('.testi');
  const dots   = document.querySelectorAll('.td');
  if (!slides.length) return;
  let cur = 0;
  function go(n) {
    slides[cur].classList.remove('active');
    dots[cur].classList.remove('active');
    cur = (n + slides.length) % slides.length;
    slides[cur].classList.add('active');
    dots[cur].classList.add('active');
  }
  dots.forEach((d, i) => d.addEventListener('click', () => go(i)));
  setInterval(() => go(cur + 1), 5500);
}

/* ──────────────────────────────────────────────────────────
   COUNTER ANIMATION
   ────────────────────────────────────────────────────────── */
function initCounters() {
  const counters = document.querySelectorAll('.stat-n');
  if (!counters.length) return;
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el     = e.target;
      const target = parseFloat(el.dataset.to);
      const isDec  = el.hasAttribute('data-dec');
      const suffix = el.dataset.suffix || '';
      const dur    = 2200;
      const start  = performance.now();
      (function tick(now) {
        const p    = Math.min((now - start) / dur, 1);
        const ease = 1 - Math.pow(1 - p, 4);
        const val  = isDec ? (target * ease).toFixed(1) : Math.floor(target * ease);
        el.innerHTML = val + (suffix ? `<span class="stat-suffix">${suffix}</span>` : '');
        if (p < 1) requestAnimationFrame(tick);
      })(start);
      io.unobserve(el);
    });
  }, { threshold: 0.6 });
  counters.forEach(el => io.observe(el));
}

/* ──────────────────────────────────────────────────────────
   WHY-US TABS
   ────────────────────────────────────────────────────────── */
function initTabs() {
  document.querySelectorAll('.w-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.w-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
    });
  });
}

/* ──────────────────────────────────────────────────────────
   CONTACT FORM
   ────────────────────────────────────────────────────────── */
function initForm() {
  const form = document.getElementById('contactForm');
  if (!form) return;
  const btn = form.querySelector('button[type="submit"]');
  const status = document.getElementById('formStatus');
  if (!btn || !status) return;

  form.addEventListener('submit', e => {
    if (!form.reportValidity()) {
      e.preventDefault();
      return;
    }

    status.textContent = 'Sending your inquiry...';
    status.classList.remove('is-success', 'is-error');
    btn.textContent = 'Sending...';
    btn.disabled = true;
  });
}

/* ──────────────────────────────────────────────────────────
   BOOT — initialise everything on DOMContentLoaded
   ────────────────────────────────────────────────────────── */
/* -- VIDEO MODAL ----------------------------------------------------------- */
function initVideoModal() {
  const modal  = document.getElementById('videoModal');
  const player = document.getElementById('vmPlayer');
  const closer = document.getElementById('vmClose');
  if (!modal || !player || !closer) return;

  function openModal(src) {
    player.src = src;
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
    player.play().catch(() => {});
  }

  function closeModal() {
    modal.classList.remove('open');
    document.body.style.overflow = '';
    player.pause();
    player.src = '';
  }

  closer.addEventListener('click', closeModal);
  modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

  document.querySelectorAll('[data-video]').forEach(el => {
    el.addEventListener('click', e => {
      e.preventDefault();
      openModal(el.dataset.video);
    });
  });
}

function initActiveNav() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');
  if (!sections.length || !navLinks.length) return;
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      navLinks.forEach(a => a.classList.remove('active'));
      const match = document.querySelector('.nav-links a[href="#' + e.target.id + '"]');
      if (match) match.classList.add('active');
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  sections.forEach(s => io.observe(s));
}

document.addEventListener('DOMContentLoaded', () => {
  initPreloader();
  initScrollProgress();
  initCursorEnhanced();
  initMagnetic();
  initNavEnhanced();
  initMobileMenu();
  initRevealEnhanced();
  initParallaxEnhanced();
  initProcess();
  initFAQ();
  initSlider();
  initCounters();
  initTabs();
  initForm();
  initTiltCards();
  initVideoModal();
  initActiveNav();
  /* Three.js scenes after a brief paint delay */
  setTimeout(() => {
    initHeroShader();
    initGlobeEnhanced();
  }, 60);
});
