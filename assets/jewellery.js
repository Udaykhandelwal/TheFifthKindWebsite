/* The Fifth Kind — /jewellery/ interactions. Vanilla, no dependencies.
   Film cards, silent loops, reveal, before/after, loupe, calendar, hover previews. */
(function () {
  "use strict";
  window.__jwOK = true;
  var doc = document, root = doc.documentElement;
  root.classList.add("jw-js");

  var mq = function (q) { return window.matchMedia ? window.matchMedia(q).matches : false; };
  var reduce = mq("(prefers-reduced-motion: reduce)");
  var fine = mq("(hover: hover) and (pointer: fine)");
  var hasIO = "IntersectionObserver" in window;
  var qa = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

  /* ---------------------------------------------------------------- reveal */
  var revealIO = null;
  function reveal(el) { el.classList.add("is-in"); }
  if (hasIO && !reduce) {
    revealIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { reveal(e.target); revealIO.unobserve(e.target); }
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -4% 0px" });
  }
  function watchReveal(el) {
    if (el.classList.contains("is-in")) return;
    if (revealIO) revealIO.observe(el); else reveal(el);
  }
  qa("[data-jw-reveal]").forEach(function (n) {
    // The hero is above the fold: reveal it on the first tick instead of waiting for the observer.
    if (n.closest(".jw-hero")) setTimeout(function () { reveal(n); }, 60);
    else watchReveal(n);
  });
  var jw = doc.querySelector(".jw");
  if (jw && "MutationObserver" in window) {
    new MutationObserver(function (muts) {
      muts.forEach(function (m) {
        Array.prototype.forEach.call(m.addedNodes, function (n) {
          if (n.nodeType !== 1) return;
          if (n.hasAttribute && n.hasAttribute("data-jw-reveal")) watchReveal(n);
          if (n.querySelectorAll) qa("[data-jw-reveal]", n).forEach(watchReveal);
        });
      });
    }).observe(jw, { childList: true, subtree: true });
  }

  /* ---------------------------------------------------------------- films + loops */
  var films = qa(".jw-film");
  var loops = qa(".jw-loop");

  function fromOf(v) {
    var host = v.closest(".jw-film");
    return host ? parseFloat(host.getAttribute("data-from")) || 0 : 0;
  }
  function safePlay(v) {
    var p = v.play();
    if (p && p.catch) p.catch(function () {});
  }
  function startSilent(v) {
    if (reduce || v.__sound) return;
    v.preload = "auto";
    var f = fromOf(v);
    if (f && v.currentTime < f) { try { v.currentTime = f; } catch (e) {} }
    safePlay(v);
  }
  function pauseSilent(v) { if (!v.__sound) v.pause(); }

  var mediaIO = hasIO ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var v = e.target.tagName === "VIDEO" ? e.target : e.target.querySelector("video");
      if (!v) return;
      if (e.isIntersecting) startSilent(v); else pauseSilent(v);
    });
  }, { rootMargin: "200px", threshold: 0.2 }) : null;

  loops.forEach(function (v) {
    v.addEventListener("playing", function () { v.classList.add("is-live"); });
    if (mediaIO) mediaIO.observe(v);
  });

  function silentState(host, v) {
    v.__sound = false;
    v.muted = true; v.loop = true; v.controls = false;
    host.classList.remove("is-playing");
  }
  function soundState(host, v) {
    v.__sound = true;
    v.loop = false; v.muted = false; v.controls = true;
    host.classList.add("is-playing");
  }

  films.forEach(function (host) {
    var v = host.querySelector("video");
    var pill = host.querySelector(".jw-film__pill");
    var from = parseFloat(host.getAttribute("data-from")) || 0;
    v.__sound = false;

    v.addEventListener("loadedmetadata", function () {
      if (!v.__sound && from && v.currentTime < from) { try { v.currentTime = from; } catch (e) {} }
    });
    v.addEventListener("timeupdate", function () {
      if (!v.__sound && from && v.currentTime < from - 0.1) { try { v.currentTime = from; } catch (e) {} }
    });
    v.addEventListener("ended", function () {
      if (!v.__sound) return;
      silentState(host, v);
      try { v.currentTime = from; } catch (e) {}
      var r = host.getBoundingClientRect();
      if (r.bottom > 0 && r.top < window.innerHeight) startSilent(v);
    });

    function playWithSound() {
      if (v.__sound) return;
      films.forEach(function (other) {
        if (other === host) return;
        var ov = other.querySelector("video");
        if (ov.__sound) silentState(other, ov);
        ov.pause();
      });
      soundState(host, v);
      try { v.currentTime = 0; } catch (e) {}
      v.preload = "auto";
      safePlay(v);
      try { window.tfkTrack && window.tfkTrack("jewellery_film_play", { film: host.getAttribute("data-film") }); } catch (e) {}
    }
    host.addEventListener("click", function (e) {
      if (v.__sound) return;
      if (e.target === v || e.target === host || (pill && pill.contains(e.target))) playWithSound();
    });
    if (mediaIO) mediaIO.observe(host);
  });

  /* ---------------------------------------------------------------- before / after */
  qa("[data-jw-ba]").forEach(function (ba) {
    var handle = ba.querySelector(".jw-ba__handle");
    var pos = 50, dragging = false;
    function set(p) {
      pos = clamp(p, 0, 100);
      ba.style.setProperty("--p", pos + "%");
      var r = Math.round(pos);
      handle.setAttribute("aria-valuenow", r);
      handle.setAttribute("aria-valuetext", r + "% counter, " + (100 - r) + "% campaign");
    }
    function fromEvent(e) {
      var rect = ba.getBoundingClientRect();
      set(((e.clientX - rect.left) / rect.width) * 100);
    }
    ba.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      dragging = true; ba.classList.add("is-drag");
      try { ba.setPointerCapture(e.pointerId); } catch (err) {}
      fromEvent(e);
      handle.focus({ preventScroll: true });
    });
    ba.addEventListener("pointermove", function (e) { if (dragging) fromEvent(e); });
    function end(e) {
      if (!dragging) return;
      dragging = false; ba.classList.remove("is-drag");
      try { ba.releasePointerCapture(e.pointerId); } catch (err) {}
    }
    ba.addEventListener("pointerup", end);
    ba.addEventListener("pointercancel", end);
    handle.addEventListener("keydown", function (e) {
      var step = 5, k = e.key, used = true;
      if (k === "ArrowLeft" || k === "ArrowDown") set(pos - step);
      else if (k === "ArrowRight" || k === "ArrowUp") set(pos + step);
      else if (k === "PageDown") set(pos - 15);
      else if (k === "PageUp") set(pos + 15);
      else if (k === "Home") set(0);
      else if (k === "End") set(100);
      else used = false;
      if (used) e.preventDefault();
    });
    set(50);
  });

  /* ---------------------------------------------------------------- loupe (fine pointers only) */
  if (fine) {
    qa("[data-jw-loupe]").forEach(function (box) {
      var img = box.querySelector("img"), lens = box.querySelector(".jw-loupe__lens");
      var Z = 2.4, R = 90, loaded = false;
      function move(e) {
        var r = img.getBoundingClientRect();
        var x = e.clientX - r.left, y = e.clientY - r.top;
        if (x < 0 || y < 0 || x > r.width || y > r.height) { box.classList.remove("is-on"); return; }
        if (!loaded) { lens.style.backgroundImage = "url(" + box.getAttribute("data-src") + ")"; loaded = true; }
        box.classList.add("is-on");
        lens.style.transform = "";
        lens.style.left = (x - R) + "px";
        lens.style.top = (y - R) + "px";
        lens.style.backgroundSize = (r.width * Z) + "px " + (r.height * Z) + "px";
        lens.style.backgroundPosition = (R - x * Z) + "px " + (R - y * Z) + "px";
      }
      box.addEventListener("pointermove", move);
      box.addEventListener("pointerenter", move);
      box.addEventListener("pointerleave", function () { box.classList.remove("is-on"); });
    });
  }

  /* ---------------------------------------------------------------- calendar */
  var DATES = [
    ["2026-11-21", "Wedding season opens", "India", false],
    ["2026-11-27", "Black Friday", "US · UK", false],
    ["2026-12-25", "Christmas & holiday gifting", "Global", false],
    ["2027-01-15", "Weddings resume after Kharmas", "India · approx.", true],
    ["2027-02-14", "Valentine's Day", "Global", false],
    ["2027-03-08", "Women's Day", "Global", false],
    ["2027-05-09", "Akshaya Tritiya", "India · approx.", true],
    ["2027-05-09", "Mother's Day", "US", false],
    ["2027-10-27", "Dhanteras", "India · approx.", true],
    ["2027-11-25", "Black Friday", "US · UK", false]
  ];
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function el(tag, cls, text) {
    var n = doc.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  qa("[data-jw-cal]").forEach(function (ol) {
    var now = new Date();
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    var items = DATES.map(function (d) {
      var p = d[0].split("-");
      return { date: new Date(+p[0], +p[1] - 1, +p[2]), iso: d[0], name: d[1], mk: d[2], approx: d[3] };
    });
    var upcoming = items.filter(function (i) { return i.date >= today; }).slice(0, 4);
    if (upcoming.length < 4) upcoming = items.slice(-4);
    ol.textContent = "";
    upcoming.forEach(function (i) {
      var li = el("li"); li.setAttribute("data-date", i.iso);
      var top = el("div", "jw-cal__date");
      top.appendChild(el("span", "jw-cal__d", String(i.date.getDate())));
      top.appendChild(el("span", "jw-cal__m", MONTHS[i.date.getMonth()] + " " + i.date.getFullYear()));
      li.appendChild(top);
      li.appendChild(el("h3", "jw-cal__n", i.name));
      li.appendChild(el("p", "jw-small jw-cal__k", i.mk));
      var days = Math.round((i.date - today) / 86400000);
      var txt = days <= 0 ? "Today" : days === 1 ? "Tomorrow" : "In " + days + " days";
      li.appendChild(el("p", "jw-cal__in", txt));
      ol.appendChild(li);
    });
  });

  /* ---------------------------------------------------------------- hover previews (fine pointers) */
  var rows = qa(".jw-make__row[data-peek]");
  if (fine && !reduce && rows.length && jw) {
    var peek = el("div", "jw-peek"); peek.setAttribute("aria-hidden", "true");
    var pImg = doc.createElement("img"); pImg.alt = ""; pImg.decoding = "async";
    var pVid = doc.createElement("video");
    pVid.muted = true; pVid.loop = true; pVid.playsInline = true; pVid.preload = "none";
    pImg.style.display = pVid.style.display = "none";
    peek.appendChild(pImg); peek.appendChild(pVid); jw.appendChild(peek);
    var tx = 0, ty = 0, cx = 0, cy = 0, raf = 0, active = false, first = true;
    function frame() {
      cx += (tx - cx) * 0.16; cy += (ty - cy) * 0.16;
      peek.style.transform = "translate3d(" + cx.toFixed(1) + "px," + cy.toFixed(1) + "px,0)";
      raf = active || Math.abs(tx - cx) > 0.5 || Math.abs(ty - cy) > 0.5 ? requestAnimationFrame(frame) : 0;
    }
    function track(e) {
      var w = peek.offsetWidth || 280, h = peek.offsetHeight || 187;
      tx = clamp(e.clientX + 28, 8, window.innerWidth - w - 8);
      ty = clamp(e.clientY - h / 2, 8, window.innerHeight - h - 8);
      if (first) { cx = tx; cy = ty; first = false; }
      if (!raf) raf = requestAnimationFrame(frame);
    }
    rows.forEach(function (row) {
      row.addEventListener("pointerenter", function (e) {
        var src = row.getAttribute("data-peek"), poster = row.getAttribute("data-peek-poster");
        if (/\.mp4$/.test(src)) {
          pImg.style.display = "none"; pVid.style.display = "block";
          if (pVid.getAttribute("src") !== src) { pVid.setAttribute("src", src); if (poster) pVid.poster = poster; }
          safePlay(pVid);
        } else {
          pVid.pause(); pVid.style.display = "none"; pImg.style.display = "block";
          if (pImg.getAttribute("src") !== src) pImg.setAttribute("src", src);
        }
        active = true; first = true; track(e);
        peek.classList.add("is-on");
      });
      row.addEventListener("pointermove", track);
      row.addEventListener("pointerleave", function () {
        active = false; peek.classList.remove("is-on"); pVid.pause();
      });
    });
  }
})();
