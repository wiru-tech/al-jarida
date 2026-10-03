/* AL-JARIDA — interactive layer (vanilla ES6+) */
(function () {
  "use strict";

  /* ---- Search overlay toggle ---- */
  const searchToggle = document.querySelector("[data-search-toggle]");
  const searchBar = document.querySelector("[data-search-bar]");
  if (searchToggle && searchBar) {
    searchToggle.addEventListener("click", () => {
      searchBar.classList.toggle("open");
      if (searchBar.classList.contains("open")) {
        searchBar.querySelector("input")?.focus();
      }
    });
  }

  /* ---- Live search (debounced fetch to JSON endpoint) ---- */
  const liveInput = document.querySelector("[data-live-search]");
  const liveResults = document.querySelector("[data-live-results]");
  if (liveInput && liveResults) {
    let timer = null;
    liveInput.addEventListener("input", () => {
      clearTimeout(timer);
      const q = liveInput.value.trim();
      if (q.length < 2) { liveResults.innerHTML = ""; return; }
      timer = setTimeout(async () => {
        try {
          const res = await fetch(`/api/search/?q=${encodeURIComponent(q)}`);
          const data = await res.json();
          if (!data.results.length) {
            liveResults.innerHTML =
              '<div style="padding:.6rem;color:#76777d;font-size:14px">No matches found.</div>';
            return;
          }
          liveResults.innerHTML = data.results.map(r =>
            `<a href="${r.url}"><span class="rk">${r.kicker || r.category}</span>${r.title}</a>`
          ).join("");
        } catch (e) { console.error(e); }
      }, 220);
    });
  }

  /* ---- Language switcher dropdown ---- */
  const langSwitch = document.querySelector("[data-lang-switch]");
  if (langSwitch) {
    langSwitch.querySelector("[data-lang-btn]")?.addEventListener("click", (e) => {
      e.stopPropagation();
      langSwitch.classList.toggle("open");
    });
    document.addEventListener("click", () => langSwitch.classList.remove("open"));
  }

  /* ---- Currency converter widget ---- */
  const calc = document.querySelector("[data-currency-calc]");
  if (calc) {
    const amount = calc.querySelector("[data-amount]");
    const from = calc.querySelector("[data-from]");
    const to = calc.querySelector("[data-to]");
    const out = calc.querySelector("[data-calc-out]");
    const liveTag = calc.querySelector("[data-calc-live]");

    // Fallback table (units per 1 USD), used until /api/markets/ resolves
    // and for any currency the live feed doesn't cover (e.g. SAR).
    let rates = { USD: 1, EUR: 0.92, GBP: 0.79, AED: 3.67, PKR: 278.5, SAR: 3.75 };

    // Market pairs are "A/B" meaning 1 A = rate B. Normalize every pair
    // that's anchored on USD into "units of X per 1 USD" and merge over
    // the fallback table, so the live feed overrides matching currencies.
    function ratesFromPairs(pairs) {
      const table = {};
      for (const [pair, rate] of Object.entries(pairs)) {
        const [a, b] = pair.split("/");
        if (!a || !b || !rate) continue;
        if (a === "USD") table[b] = rate;
        else if (b === "USD") table[a] = 1 / rate;
      }
      return table;
    }

    function convert() {
      const a = parseFloat(amount.value) || 0;
      const f = rates[from.value] || 1;
      const t = rates[to.value] || 1;
      const result = (a / f) * t;
      out.textContent = result.toLocaleString(undefined, {
        minimumFractionDigits: 2, maximumFractionDigits: 2
      }) + " " + to.value;
    }
    [amount, from, to].forEach(el => el.addEventListener("input", convert));
    convert();

    fetch("/api/markets/").then(r => r.json()).then(d => {
      rates = Object.assign({}, rates, ratesFromPairs(d.rates || {}));
      convert();
      if (liveTag) { liveTag.textContent = "Live rates"; liveTag.classList.remove("stale"); }
    }).catch(() => {
      if (liveTag) { liveTag.textContent = "Reference rates"; liveTag.classList.add("stale"); }
    });
  }

  /* ---- Live TV widget(s): swap thumbnail for a playing embed ----
     Multiple streams can appear on one page (e.g. the Live TV hub), so
     every instance is wired independently rather than just the first. */
  document.querySelectorAll("[data-live-tv]").forEach(liveTv => {
    const playBtn = liveTv.querySelector("[data-live-tv-play]");
    const stream = liveTv.dataset.stream;
    if (playBtn && stream) {
      playBtn.addEventListener("click", () => {
        const iframe = document.createElement("iframe");
        iframe.src = stream + (stream.includes("?") ? "&" : "?") + "autoplay=1";
        iframe.setAttribute("allow", "autoplay; encrypted-media; picture-in-picture");
        iframe.setAttribute("allowfullscreen", "");
        iframe.setAttribute("loading", "lazy");
        liveTv.innerHTML = "";
        liveTv.appendChild(iframe);
      }, { once: true });
    }
  });

  /* ---- Share buttons (native share fallback) ---- */
  document.querySelectorAll("[data-share]").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const net = btn.dataset.share;
      // On list pages (home/category) the button shares a specific article,
      // not the current page — data-url/data-title carry that target.
      const targetUrl = btn.dataset.url
        ? new URL(btn.dataset.url, window.location.origin).href
        : window.location.href;
      const url = encodeURIComponent(targetUrl);
      const title = encodeURIComponent(btn.dataset.title || document.title);
      const map = {
        whatsapp: `https://wa.me/?text=${title}%20${url}`,
        twitter: `https://twitter.com/intent/tweet?text=${title}&url=${url}`,
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}`,
        linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${url}`,
      };
      if (map[net]) { e.preventDefault(); window.open(map[net], "_blank", "width=600,height=500"); }
    });
  });

  /* ---- Reply-to-comment: scroll form + set parent id ---- */
  document.querySelectorAll("[data-reply]").forEach(btn => {
    btn.addEventListener("click", () => {
      const pid = btn.dataset.reply;
      const parentField = document.querySelector("#id_parent");
      if (parentField) parentField.value = pid;
      document.querySelector("[data-comment-form]")?.scrollIntoView({ behavior: "smooth" });
    });
  });

})();
