/* The Fifth Kind — interaction layer (all pages).
   Deliberately small: a silent 5-second preview fades in when you hover a film,
   so visitors see the work move before they press play. Nothing else animates on scroll. */
(function () {
  var fine = window.matchMedia && matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (!fine) return;
  document.querySelectorAll(".show-card[data-preview], .vid[data-preview]").forEach(function (card) {
    var v;
    card.addEventListener("mouseenter", function () {
      if (card.classList.contains("playing")) return;
      if (!v) {
        v = document.createElement("video");
        v.className = "m-prev"; v.muted = true; v.loop = true; v.playsInline = true; v.preload = "auto";
        v.setAttribute("muted", ""); v.setAttribute("aria-hidden", "true");
        var src = card.dataset.preview;
        v.src = src.charAt(0) === "/" || src.indexOf("http") === 0 ? src : "/" + src;
        v.addEventListener("playing", function () { if (card.matches(":hover")) card.classList.add("m-live"); });
        var img = card.querySelector("img");
        img && img.parentNode ? img.parentNode.insertBefore(v, img.nextSibling) : card.appendChild(v);
      }
      var p = v.play(); if (p && p.catch) p.catch(function () {});
    });
    card.addEventListener("mouseleave", function () { if (v) v.pause(); card.classList.remove("m-live"); });
    card.addEventListener("click", function () { if (v) v.pause(); card.classList.remove("m-live"); });
  });
})();

/* Click a static post to see it full size (all devices). */
(function () {
  var links = document.querySelectorAll("a[data-zoom]");
  if (!links.length || !window.HTMLDialogElement) return;
  var box = document.createElement("dialog");
  box.className = "zoom-box";
  box.innerHTML = '<button type="button" aria-label="Close">×</button><img alt="">';
  document.body.appendChild(box);
  var img = box.querySelector("img");
  box.querySelector("button").addEventListener("click", function () { box.close(); });
  box.addEventListener("click", function (e) { if (e.target === box) box.close(); });
  links.forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      var i = a.querySelector("img");
      img.src = a.getAttribute("href"); img.alt = i ? i.alt : "";
      box.showModal();
    });
  });
})();
