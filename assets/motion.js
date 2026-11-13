/* The Fifth Kind — motion layer (every page). Pure enhancement: nothing here is needed to read or use the site. */
(function () {
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (/[?&]motion=1/.test(location.search)) { reduce = false; document.documentElement.classList.add("m-force"); } // QA switch
  var fine = window.matchMedia && matchMedia("(hover: hover) and (pointer: fine)").matches;
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var raf = window.requestAnimationFrame || function (f) { return setTimeout(f, 16); };

  // ---- hover previews: a silent 5-second loop over the poster (works even with reduced motion off-hover) ----
  if (fine) {
    $$(".show-card[data-preview], .vid[data-preview]").forEach(function (card) {
      var v;
      card.addEventListener("mouseenter", function () {
        if (card.classList.contains("playing")) return;
        if (!v) {
          v = document.createElement("video");
          v.className = "m-prev"; v.muted = true; v.loop = true; v.playsInline = true; v.preload = "auto";
          v.setAttribute("muted", ""); v.setAttribute("aria-hidden", "true");
          v.src = card.dataset.preview.charAt(0) === "/" || card.dataset.preview.indexOf("http") === 0 ? card.dataset.preview : "/" + card.dataset.preview;
          v.addEventListener("playing", function () { if (card.matches(":hover")) card.classList.add("m-live"); });
          var img = card.querySelector("img");
          img && img.parentNode ? img.parentNode.insertBefore(v, img.nextSibling) : card.appendChild(v);
        }
        var p = v.play(); if (p && p.catch) p.catch(function () {});
      });
      card.addEventListener("mouseleave", function () { if (v) { v.pause(); } card.classList.remove("m-live"); });
      card.addEventListener("click", function () { if (v) { v.pause(); } card.classList.remove("m-live"); });
    });
  }

  if (reduce) return;

  // ---- scroll progress ----
  var bar = document.createElement("div");
  bar.className = "m-progress"; bar.setAttribute("aria-hidden", "true");
  document.body.appendChild(bar);
  var ticking = false;
  function onScroll() {
    if (ticking) return; ticking = true;
    raf(function () {
      var h = document.documentElement.scrollHeight - innerHeight;
      bar.style.transform = "scaleX(" + (h > 0 ? Math.min(1, scrollY / h) : 0) + ")";
      ticking = false;
    });
  }
  addEventListener("scroll", onScroll, { passive: true }); onScroll();

  // ---- hero headline: words rise out of a blur ----
  $$(".h1-look, .page-hero h1").forEach(function (h) {
    var i = 0;
    (function split(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/([ \t\n\r]+)/).forEach(function (part) {
            if (!part) return;
            if (/^[ \t\n\r]+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var s = document.createElement("span"); s.className = "m-w"; s.style.setProperty("--i", i++); s.textContent = part;
            frag.appendChild(s);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.tagName === "EM") {
          // gradient text: animate the phrase as one piece so the gradient clip survives
          n.classList.add("m-w"); n.style.setProperty("--i", i++);
        } else if (n.nodeType === 1 && n.tagName !== "BR") { split(n); }
      });
    })(h);
    h.classList.remove("rise"); h.style.opacity = 1; h.style.transform = "none";
    h.classList.add("m-words");
  });

  // ---- reveals on inner pages (the homepage has its own .reveal) ----
  if (!document.querySelector(".reveal")) {
    var targets = $$(".block h2, .block .lede, .block > .wrap > p, .card, .vid, .faq details, .related a, .cta-band, .checks li, .steps li, .prose > *, .table-wrap, .lead");
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("m-in"); io.unobserve(e.target); } });
    }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });
    targets.forEach(function (el) {
      if (el.getBoundingClientRect().top < innerHeight) return; // already on screen: leave it alone
      var sib = el.parentNode ? Array.prototype.indexOf.call(el.parentNode.children, el) : 0;
      el.style.setProperty("--d", Math.min(sib, 6) * 70 + "ms");
      el.classList.add("m-rv"); io.observe(el);
    });
  }

  // ---- scene labels draw their line ----
  $$(".slate").forEach(function (s) { s.classList.add("m-draw"); });
  var sio = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); sio.unobserve(e.target); } });
  }, { threshold: 0.5 });
  $$(".slate.m-draw").forEach(function (s) { sio.observe(s); });

  if (!fine) return;

  // ---- cursor light ----
  var glow = document.createElement("div");
  glow.className = "m-glow"; glow.setAttribute("aria-hidden", "true");
  document.body.appendChild(glow);
  var gx = innerWidth / 2, gy = innerHeight / 2, tx = gx, ty = gy, gRun = false;
  function glowLoop() {
    gx += (tx - gx) * 0.12; gy += (ty - gy) * 0.12;
    glow.style.transform = "translate3d(" + gx + "px," + gy + "px,0)";
    if (Math.abs(tx - gx) > 0.5 || Math.abs(ty - gy) > 0.5) raf(glowLoop); else gRun = false;
  }
  addEventListener("pointermove", function (e) {
    tx = e.clientX; ty = e.clientY; glow.classList.add("on");
    if (!gRun) { gRun = true; raf(glowLoop); }
  }, { passive: true });
  document.addEventListener("pointerleave", function () { glow.classList.remove("on"); });

  // ---- spotlight edges on cards ----
  $$(".svc, .aud, .step, .guide, .auto-list li, .consult, .magnet, .card, .related a, .faq-list details, .c-item, .stat").forEach(function (c) {
    c.classList.add("m-spot");
    c.addEventListener("pointermove", function (e) {
      var r = c.getBoundingClientRect();
      c.style.setProperty("--mx", (e.clientX - r.left) + "px");
      c.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
  });

  // ---- 3D tilt + shine on film cards ----
  $$(".show-card, .vid").forEach(function (c) {
    c.classList.add("m-tilt");
    var shine = document.createElement("span"); shine.className = "m-shine"; c.appendChild(shine);
    c.addEventListener("pointermove", function (e) {
      if (c.classList.contains("playing")) { c.style.transform = ""; return; }
      var r = c.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      c.classList.add("m-tilting");
      c.style.setProperty("--mx", x * 100 + "%"); c.style.setProperty("--my", y * 100 + "%");
      c.style.transform = "perspective(900px) rotateX(" + ((0.5 - y) * 7).toFixed(2) + "deg) rotateY(" + ((x - 0.5) * 9).toFixed(2) + "deg) translateY(-4px)";
    });
    c.addEventListener("pointerleave", function () { c.classList.remove("m-tilting"); c.style.transform = ""; });
  });

  // ---- magnetic buttons ----
  $$(".btn").forEach(function (b) {
    if (b.closest("form")) return;
    b.classList.add("m-mag");
    b.addEventListener("pointermove", function (e) {
      var r = b.getBoundingClientRect();
      var x = e.clientX - r.left - r.width / 2, y = e.clientY - r.top - r.height / 2;
      b.style.transform = "translate(" + (x * 0.22).toFixed(1) + "px," + (y * 0.32).toFixed(1) + "px)";
    });
    b.addEventListener("pointerleave", function () { b.style.transform = ""; });
  });
})();
scenes();

/* ===================== scroll scenes (GSAP + ScrollTrigger + Lenis) ===================== */
function scenes() {
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches && !/[?&]motion=1/.test(location.search);
  var fine = window.matchMedia && matchMedia("(hover: hover) and (pointer: fine)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var wide = function () { return innerWidth > 900; };
  var root = document.documentElement;
  if (reduce || !window.gsap || !window.ScrollTrigger) { root.classList.add("no-gsap", "no-pin"); return; }
  gsap.registerPlugin(ScrollTrigger);
  root.classList.add("m-ready");

  // ---- smooth scroll ----
  var lenis = null;
  if (window.Lenis && fine) {
    lenis = new Lenis({ lerp: 0.1, wheelMultiplier: 1 });
    lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
    gsap.ticker.lagSmoothing(0);
    document.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest('a[href^="#"]');
      if (!a) return;
      var id = a.getAttribute("href"); if (id.length < 2) return;
      var el = document.querySelector(id); if (!el) return;
      e.preventDefault(); lenis.scrollTo(el, { offset: -70 });
    });
    var dlg = $("dialog"); if (dlg) { dlg.addEventListener("close", function () { lenis.start(); }); }
  }

  // ---- 1. hero shrinks into a cinema screen ----
  var hero = $(".hero");
  if (hero && $(".hero-bg") && wide()) {
    var tl = gsap.timeline({ scrollTrigger: { trigger: hero, start: "top top", end: "+=85%", scrub: 0.8, pin: true, anticipatePin: 1 } });
    tl.to(".hero-bg", { scale: 0.74, borderRadius: 28, yPercent: 4, ease: "none" }, 0)
      .to(".hero-bg video", { opacity: 0.95, ease: "none" }, 0)
      .to(".hero > .wrap", { yPercent: -28, opacity: 0, ease: "none" }, 0)
      .to(".hero-foot", { opacity: 0, ease: "none" }, 0);
  }

  // ---- 2. statement words light up ----
  $$(".scrub").forEach(function (p) {
    var i = 0;
    (function split(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var f = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (w) {
            if (!w) return;
            if (/^\s+$/.test(w)) { f.appendChild(document.createTextNode(w)); return; }
            var s = document.createElement("span"); s.className = "sw"; s.textContent = w; f.appendChild(s); i++;
          });
          n.parentNode.replaceChild(f, n);
        } else if (n.tagName === "EM") { n.classList.add("sw"); }
        else if (n.nodeType === 1) split(n);
      });
    })(p);
    gsap.to(p.querySelectorAll(".sw"), { opacity: 1, stagger: 0.08, ease: "none",
      scrollTrigger: { trigger: p, start: "top 80%", end: "bottom 40%", scrub: true } });
  });

  // ---- 3. pinned horizontal film reel ----
  var reel = $(".reel-section"), track = $(".reel-track");
  if (reel && track) {
    if (wide()) {
      var dist = function () { return Math.max(0, track.scrollWidth - innerWidth); };
      gsap.to(track, { x: function () { return -dist(); }, ease: "none",
        scrollTrigger: { trigger: reel, start: "top top", end: function () { return "+=" + dist(); }, scrub: 0.6, pin: true,
          invalidateOnRefresh: true, anticipatePin: 1,
          onUpdate: function (st) { var b = $(".reel-bar i"); if (b) b.style.transform = "scaleX(" + st.progress + ")"; } } });
      // cards ease in from a slight angle as they arrive
      gsap.from(track.children, { yPercent: 12, rotate: 3, opacity: 0, stagger: 0.05, duration: 1, ease: "power3.out",
        scrollTrigger: { trigger: reel, start: "top 75%" } });
    } else { root.classList.add("no-pin"); }
  }

  // ---- 4. ticker reacts to scroll speed and direction ----
  var mq = $(".marquee-track");
  if (mq && mq.getAnimations) {
    var anim = mq.getAnimations()[0], skewTo = gsap.quickTo(".marquee", "skewX", { duration: 0.4, ease: "power3" });
    ScrollTrigger.create({ onUpdate: function (st) {
      var v = st.getVelocity();
      if (anim) anim.playbackRate = (st.direction < 0 ? -1 : 1) * (1 + Math.min(Math.abs(v) / 400, 5));
      skewTo(gsap.utils.clamp(-8, 8, v / -300));
    } });
  }

  // ---- 5. headings rise out of a mask ----
  $$("main h2").forEach(function (h) {
    if (h.closest(".magnet, .chat-demo, .consult, .cta-band")) return;
    h.classList.remove("reveal"); h.classList.add("m-split");
    (function wrap(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var f = document.createDocumentFragment();
          n.textContent.split(/([ \t\n\r]+)/).forEach(function (w) {
            if (!w) return;
            if (/^[ \t\n\r]+$/.test(w)) { f.appendChild(document.createTextNode(w)); return; }
            var o = document.createElement("span"); o.className = "mw"; var s = document.createElement("span"); s.textContent = w; o.appendChild(s); f.appendChild(o);
          });
          n.parentNode.replaceChild(f, n);
        } else if (n.tagName === "EM") {
          var o2 = document.createElement("span"); o2.className = "mw"; n.parentNode.insertBefore(o2, n); var s2 = document.createElement("span"); o2.appendChild(s2); s2.appendChild(n);
        }
      });
    })(h);
    gsap.from(h.querySelectorAll(".mw > span"), { yPercent: 110, rotate: 4, duration: 1.05, stagger: 0.05, ease: "power4.out",
      scrollTrigger: { trigger: h, start: "top 88%" } });
  });

  // ---- 6. film cards on inner pages wipe open ----
  $$(".vids .vid").forEach(function (c) {
    c.classList.add("m-wipe"); c.classList.remove("m-rv");
    gsap.fromTo(c, { clipPath: "inset(100% 0% 0% 0% round 14px)" }, { clipPath: "inset(0% 0% 0% 0% round 14px)", duration: 1.1, ease: "power4.inOut",
      scrollTrigger: { trigger: c, start: "top 92%" } });
    var img = c.querySelector("img"); if (img) gsap.fromTo(img, { scale: 1.3 }, { scale: 1, duration: 1.4, ease: "power3.out", scrollTrigger: { trigger: c, start: "top 92%" } });
  });

  // ---- 7. process line, stats, footer wordmark ----
  if ($(".steps-line i")) gsap.to(".steps-line i", { scaleX: 1, ease: "none", scrollTrigger: { trigger: ".steps", start: "top 85%", end: "bottom 55%", scrub: true } });
  $$(".stat").forEach(function (s, i) { gsap.from(s, { y: 50, opacity: 0, duration: 1, delay: i * 0.08, ease: "power3.out", scrollTrigger: { trigger: s, start: "top 92%" } }); });
  if ($(".mega")) {
    gsap.from(".mega span", { yPercent: 105, duration: 1.2, stagger: 0.1, ease: "power4.out", scrollTrigger: { trigger: ".mega", start: "top 95%" } });
    gsap.fromTo(".mega", { letterSpacing: "0.04em" }, { letterSpacing: "-0.05em", ease: "none", scrollTrigger: { trigger: ".mega", start: "top bottom", end: "bottom bottom", scrub: true } });
  }
  $$(".aud, .auto-list li, .guide").forEach(function (el) { el.classList.remove("reveal"); });
  ScrollTrigger.batch(".aud, .auto-list li, .guide", { start: "top 90%", onEnter: function (b) { gsap.from(b, { y: 60, opacity: 0, rotate: 1.5, stagger: 0.08, duration: 0.9, ease: "power3.out" }); } });

  if (!fine) { ScrollTrigger.refresh(); return; }

  // ---- 8. services: film beside the cursor ----
  var float = document.createElement("div"); float.className = "svc-float"; float.setAttribute("aria-hidden", "true");
  var fv = document.createElement("video"); fv.muted = true; fv.loop = true; fv.playsInline = true; fv.setAttribute("muted", ""); float.appendChild(fv);
  document.body.appendChild(float);
  var fx = gsap.quickTo(float, "x", { duration: 0.45, ease: "power3" }), fy = gsap.quickTo(float, "y", { duration: 0.45, ease: "power3" });
  $$(".svc[data-film]").forEach(function (row) {
    row.addEventListener("mouseenter", function () {
      var src = "/" + row.dataset.film.replace(/^\//, "");
      if (fv.getAttribute("src") !== src) fv.setAttribute("src", src);
      var p = fv.play(); if (p && p.catch) p.catch(function () {});
      float.classList.add("on"); float.style.transform = "translate3d(-50%,-50%,0) scale(1) rotate(-4deg)";
    });
    row.addEventListener("mousemove", function (e) { fx(Math.min(e.clientX + 260, innerWidth - 130)); fy(e.clientY); });
    row.addEventListener("mouseleave", function () { float.classList.remove("on"); float.style.transform = ""; fv.pause(); });
  });

  // ---- 9. cursor ----
  var dot = document.createElement("div"); dot.className = "m-cursor";
  var ring = document.createElement("div"); ring.className = "m-ring"; ring.innerHTML = "<b>Play</b>";
  [dot, ring].forEach(function (n) { n.setAttribute("aria-hidden", "true"); document.body.appendChild(n); });
  var dx = gsap.quickTo(dot, "x", { duration: 0.08 }), dy = gsap.quickTo(dot, "y", { duration: 0.08 });
  var rx = gsap.quickTo(ring, "x", { duration: 0.45, ease: "power3" }), ry = gsap.quickTo(ring, "y", { duration: 0.45, ease: "power3" });
  var shown = false;
  addEventListener("pointermove", function (e) {
    if (!shown) { shown = true; gsap.set([dot, ring], { x: e.clientX, y: e.clientY }); gsap.to([dot, ring], { opacity: 1, duration: 0.3 }); }
    dx(e.clientX); dy(e.clientY); rx(e.clientX); ry(e.clientY);
    var t = e.target;
    var film = t.closest && t.closest(".show-card:not(.playing), .vid:not(.playing)");
    ring.classList.toggle("play", !!film);
    ring.classList.toggle("link", !film && !!(t.closest && t.closest("a, button, summary, .svc")));
  }, { passive: true });
  document.addEventListener("pointerleave", function () { gsap.to([dot, ring], { opacity: 0, duration: 0.2 }); });
  document.addEventListener("pointerenter", function () { gsap.to([dot, ring], { opacity: 1, duration: 0.2 }); });

  addEventListener("load", function () { ScrollTrigger.refresh(); });
}
