/**
 * direction.js
 * -----------------------------------------------------------------
 * Live LTR/RTL detection, shared by the legacy composer
 * (templates/news/blog_form.html) and the JS-driven blog module
 * (static/js/blog.js). As the reader types, a field's `dir` attribute
 * — and an optional status badge next to it — update in real time,
 * based on the script of the text actually typed (Latin -> ltr,
 * Arabic/Urdu script -> rtl). The *stored* direction is recomputed
 * server-side on save (see news/direction.py) so it can never drift
 * from what was actually submitted — this file only drives the live
 * UI and is exposed as `window.AljaridaDirection` for reuse.
 * -----------------------------------------------------------------
 */
(function (window) {
  "use strict";

  // Arabic, Arabic Supplement, Arabic Extended-A, Arabic Presentation Forms
  // (covers standard Urdu text as well as Arabic).
  var RTL_CHAR = /[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]/;
  var LTR_CHAR = /[A-Za-z]/;

  function detectDirection(text) {
    if (!text) return "ltr";
    for (var i = 0; i < text.length; i++) {
      var ch = text[i];
      if (RTL_CHAR.test(ch)) return "rtl";
      if (LTR_CHAR.test(ch)) return "ltr";
    }
    return "ltr";
  }

  function bindLiveDetection(field, badge) {
    if (!field) return;
    function update() {
      var dir = detectDirection(field.value);
      field.setAttribute("dir", dir);
      if (badge) {
        badge.textContent = dir.toUpperCase();
        badge.classList.toggle("is-rtl", dir === "rtl");
      }
    }
    field.addEventListener("input", update);
    update();
  }

  window.AljaridaDirection = {
    detect: detectDirection,
    bindLiveDetection: bindLiveDetection,
  };

  document.addEventListener("DOMContentLoaded", function () {
    // Legacy full-page composer (templates/news/blog_form.html), if present.
    bindLiveDetection(document.getElementById("id_title"), document.getElementById("titleDirBadge"));
    bindLiveDetection(document.getElementById("id_content"), document.getElementById("contentDirBadge"));
  });
})(window);
