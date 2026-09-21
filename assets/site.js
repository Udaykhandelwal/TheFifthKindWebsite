/* The Fifth Kind — shared site script (all pages, including the homepage).
   1) Analytics: paste IDs below and every page starts tracking. Nothing loads while they're empty.
   2) Conversion events: WhatsApp / call / email clicks and form submits.
   3) Lead capture: every form submit is emailed (FormSubmit) AND opens WhatsApp prefilled.
   4) Click-to-play video cards (.vid). */
(function () {
  var GA4_ID = "";          // e.g. "G-XXXXXXXXXX"  (analytics.google.com → Admin → Data streams)
  var CLARITY_ID = "";      // e.g. "abcd1234ef"    (clarity.microsoft.com → Settings → Setup)
  var LEAD_EMAIL = "uday.khandelwal@the5thkind.in"; // FormSubmit sends one activation email the first time

  // ---------- analytics ----------
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { dataLayer.push(arguments); };
  if (GA4_ID) {
    var s = document.createElement("script");
    s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA4_ID;
    document.head.appendChild(s);
    gtag("js", new Date()); gtag("config", GA4_ID);
  }
  if (CLARITY_ID) {
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.src = "https://www.clarity.ms/tag/" + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, "clarity", "script", CLARITY_ID);
  }
  function track(name, params) {
    try { gtag("event", name, params || {}); } catch (e) {}
    try { window.clarity && clarity("event", name); } catch (e) {}
  }
  window.tfkTrack = track;

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a) return;
    var h = a.getAttribute("href") || "";
    var where = { page: location.pathname, label: (a.textContent || "").trim().slice(0, 60) };
    if (h.indexOf("wa.me/") > -1) track("whatsapp_click", where);
    else if (h.indexOf("tel:") === 0) track("phone_click", where);
    else if (h.indexOf("mailto:") === 0) track("email_click", where);
  });

  // ---------- lead capture ----------
  // Called by forms. Opens WhatsApp immediately (so pop-up blockers allow it)
  // and saves the lead by email in the background.
  window.tfkCapture = function (fields) {
    fields = fields || {};
    fields._subject = "New website lead — " + (fields.service || "the5thkind.in");
    fields.page = location.href;
    fields._template = "table";
    try {
      fetch("https://formsubmit.co/ajax/" + LEAD_EMAIL, {
        method: "POST", keepalive: true,
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(fields)
      }).catch(function () {});
    } catch (e) {}
    track("generate_lead", { service: fields.service || "", page: location.pathname });
  };

  window.tfkLead = function (ev) {
    ev.preventDefault();
    var f = ev.target, d = {};
    Array.prototype.forEach.call(f.elements, function (el) { if (el.name) d[el.name] = el.value; });
    var msg = "Hi! I'm " + d.name + " (" + d.phone + ")" + (d.business ? ", " + d.business : "") +
      ". I'm interested in: " + d.service + ". " + (d.message || "");
    window.open("https://wa.me/918296008838?text=" + encodeURIComponent(msg), "_blank");
    window.tfkCapture(d);
    f.innerHTML = '<p style="color:#10b981;font-weight:600">Thanks, ' + (d.name || "") +
      '! WhatsApp should have opened with your message. If it didn\'t, we\'ll call you on ' + d.phone + '.</p>';
    return false;
  };

  // ---------- click-to-play videos ----------
  var playing = null;
  document.querySelectorAll(".vid[data-src]").forEach(function (card) {
    card.setAttribute("tabindex", "0");
    card.setAttribute("role", "button");
    function start() {
      if (card.classList.contains("playing")) {
        var cv = card.querySelector("video"); if (cv) { cv.paused ? cv.play() : cv.pause(); } return;
      }
      if (playing) { var pv = playing.querySelector("video"); if (pv) pv.remove(); playing.classList.remove("playing"); }
      var v = document.createElement("video");
      v.src = card.dataset.src; v.controls = true; v.playsInline = true; v.autoplay = true;
      card.appendChild(v); card.classList.add("playing"); playing = card;
      track("video_play", { video: card.dataset.src });
    }
    card.addEventListener("click", start);
    card.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); start(); } });
  });
})();
