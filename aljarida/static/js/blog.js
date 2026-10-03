/**
 * blog.js — Reader Blog module (templates/news/blog_list.html)
 * -----------------------------------------------------------------
 * Self-contained JS layer for the reader blog:
 *   1. Auth: Sign In / Sign Up modal, backed by the real Django
 *      session (see api_login/api_signup/api_logout in news/views.py).
 *      LocalStorage only *caches* the signed-in user for instant
 *      show/hide of the Write section and cross-tab awareness — it is
 *      never trusted as proof of identity. Every mutating API call is
 *      re-checked against request.user / post ownership server-side.
 *   2. Blog CRUD: the post list, composer, and Edit/Delete controls
 *      are all rendered and wired here, talking to the JSON endpoints
 *      under /api/blog/posts/.
 *   3. RTL: each field's `dir` is detected live as the reader types
 *      (window.AljaridaDirection, from direction.js) and each
 *      rendered post uses the *server-computed* title_dir/content_dir
 *      — the same single source of truth BlogPost.save() uses — so
 *      typed input and rendered output can never disagree.
 * -----------------------------------------------------------------
 */
(function () {
  "use strict";

  var STORAGE_KEY = "aljarida_blog_user";

  var state = {
    user: null,
    posts: [],
  };

  // ---------------------------------------------------------------
  // DOM refs (elements always present in blog_list.html)
  // ---------------------------------------------------------------
  var els = {};

  function cacheEls() {
    els.authActions = document.getElementById("blogAuthActions");
    els.feed = document.getElementById("blogFeed");
    els.emptyTemplate = document.getElementById("blogEmptyTemplate");

    els.composer = document.getElementById("blogComposer");
    els.composerHeading = document.getElementById("blogComposerHeading");
    els.form = document.getElementById("blogPostForm");
    els.postId = document.getElementById("blogPostId");
    els.titleInput = document.getElementById("blogTitleInput");
    els.contentInput = document.getElementById("blogContentInput");
    els.titleBadge = document.getElementById("titleDirBadge");
    els.contentBadge = document.getElementById("contentDirBadge");
    els.titleError = document.getElementById("blogTitleError");
    els.contentError = document.getElementById("blogContentError");
    els.formError = document.getElementById("blogFormError");
    els.authorDisplay = document.getElementById("blogAuthorDisplay");
    els.dateDisplay = document.getElementById("blogDateDisplay");
    els.composerCancel = document.getElementById("blogComposerCancel");
    els.composerSubmit = document.getElementById("blogComposerSubmit");

    els.modalBackdrop = document.getElementById("authModalBackdrop");
    els.modalClose = document.getElementById("authModalClose");
    els.signInPane = document.getElementById("authModalSignIn");
    els.signUpPane = document.getElementById("authModalSignUp");
    els.signInForm = document.getElementById("signInForm");
    els.signUpForm = document.getElementById("signUpForm");
    els.signInError = document.getElementById("signInError");
    els.signUpError = document.getElementById("signUpError");

    els.i18n = document.getElementById("blogI18nStrings");
  }

  /** Reads one of the pre-translated strings stashed on #blogI18nStrings
   *  (see blog_list.html) — keeps every user-facing string sourced from
   *  the .po catalogs instead of hardcoded in this file. */
  function str(key, fallback) {
    var value = els.i18n && els.i18n.dataset[key];
    return value || fallback;
  }

  // ---------------------------------------------------------------
  // Small helpers
  // ---------------------------------------------------------------
  function escapeHtml(value) {
    var div = document.createElement("div");
    div.textContent = value == null ? "" : String(value);
    return div.innerHTML;
  }

  function getCookie(name) {
    var match = document.cookie.match("(^|;\\s*)" + name + "=([^;]*)");
    return match ? decodeURIComponent(match[2]) : null;
  }

  function showError(el, message) {
    if (!el) return;
    if (message) {
      el.textContent = message;
      el.hidden = false;
    } else {
      el.textContent = "";
      el.hidden = true;
    }
  }

  function clearFormErrors(form) {
    form.querySelectorAll(".flash.error").forEach(function (el) {
      el.hidden = true;
      el.textContent = "";
    });
  }

  /** fetch() wrapper: JSON body, CSRF header on unsafe methods, same-origin
   *  cookies (the real session). Resolves to the parsed body even on 4xx/5xx
   *  so callers can read {error}/{errors} without a try/catch per call. */
  function apiFetch(url, options) {
    options = options || {};
    var method = (options.method || "GET").toUpperCase();
    var headers = { Accept: "application/json" };
    var opts = {
      method: method,
      headers: headers,
      credentials: "same-origin",
    };
    if (options.body !== undefined) {
      headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(options.body);
    }
    if (!/^(GET|HEAD|OPTIONS)$/.test(method)) {
      headers["X-CSRFToken"] = getCookie("csrftoken");
    }
    return fetch(url, opts).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (data) {
        return { ok: res.ok, status: res.status, data: data };
      });
    });
  }

  // ---------------------------------------------------------------
  // LocalStorage session cache
  // ---------------------------------------------------------------
  function loadCachedUser() {
    try {
      var raw = window.localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function saveCachedUser(user) {
    try {
      if (user) {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
      } else {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    } catch (e) { /* LocalStorage unavailable (private mode, quota) — auth
                     still works via the session cookie, just without the
                     cross-tab cache. */ }
  }

  // ---------------------------------------------------------------
  // Rendering
  // ---------------------------------------------------------------
  function renderAuthActions() {
    if (!els.authActions) return;
    if (state.user) {
      els.authActions.innerHTML =
        '<button type="button" class="btn btn--solid" data-blog-write>' +
        '<span class="material-symbols-outlined" style="font-size:16px">edit</span> ' +
        escapeHtml(str("write", "Write a post")) + "</button>" +
        '<button type="button" class="btn btn--outline" data-blog-signout>' +
        escapeHtml(str("signout", "Sign out")) + "</button>";
    } else {
      els.authActions.innerHTML =
        '<button type="button" class="btn btn--outline" data-blog-signin>' +
        escapeHtml(str("signin", "Sign In")) + "</button>" +
        '<button type="button" class="btn btn--solid" data-blog-signup>' +
        escapeHtml(str("signupToWrite", "Sign up to write")) + "</button>";
      closeComposer();
    }
  }

  function renderFeed() {
    if (!els.feed) return;
    if (!state.posts.length) {
      els.feed.innerHTML = "";
      els.feed.appendChild(els.emptyTemplate.content.cloneNode(true));
      return;
    }
    els.feed.innerHTML = state.posts.map(renderCard).join("");
  }

  function renderCard(post) {
    var langTag = post.content_dir === "rtl"
      ? '<span class="lang-tag is-rtl">' + escapeHtml(str("langUr", "Urdu")) + "</span>"
      : '<span class="lang-tag">' + escapeHtml(str("langEn", "English")) + "</span>";
    var actions = post.is_owner
      ? '<div class="blog-card__actions">' +
        '<button type="button" class="btn btn--outline" data-edit="' + post.id + '">' + escapeHtml(str("edit", "Edit")) + "</button>" +
        '<button type="button" class="btn btn--outline btn--danger" data-delete="' + post.id + '">' + escapeHtml(str("delete", "Delete")) + "</button>" +
        "</div>"
      : "";
    return (
      '<article class="blog-card" data-post="' + post.id + '">' +
        '<div class="blog-card__meta">' +
          '<span class="blog-card__author">' + escapeHtml(post.author_name) + "</span>" +
          '<span class="dot">&middot;</span>' +
          "<time>" + escapeHtml(post.created_at_display) + "</time>" +
          langTag +
        "</div>" +
        '<h3 class="blog-card__title" dir="' + post.title_dir + '">' + escapeHtml(post.title) + "</h3>" +
        '<p class="blog-card__content" dir="' + post.content_dir + '">' + escapeHtml(post.content) + "</p>" +
        actions +
      "</article>"
    );
  }

  // ---------------------------------------------------------------
  // Composer (create / edit)
  // ---------------------------------------------------------------
  function openComposer(post) {
    if (!state.user) { openAuthModal("signin"); return; }
    clearFormErrors(els.form);
    if (post) {
      els.composerHeading.textContent = els.composerHeading.dataset.editLabel || els.composerHeading.textContent;
      els.postId.value = post.id;
      els.titleInput.value = post.title;
      els.contentInput.value = post.content;
      els.dateDisplay.value = post.created_at_display;
      els.composerSubmit.textContent = els.composerSubmit.dataset.saveLabel || els.composerSubmit.textContent;
    } else {
      els.composerHeading.textContent = els.composerHeading.dataset.writeLabel || els.composerHeading.textContent;
      els.postId.value = "";
      els.titleInput.value = "";
      els.contentInput.value = "";
      els.dateDisplay.value = new Date().toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
      els.composerSubmit.textContent = els.composerSubmit.dataset.publishLabel || els.composerSubmit.textContent;
    }
    els.authorDisplay.value = state.user.display_name;
    window.AljaridaDirection.bindLiveDetection(els.titleInput, els.titleBadge);
    window.AljaridaDirection.bindLiveDetection(els.contentInput, els.contentBadge);
    els.composer.hidden = false;
    els.composer.scrollIntoView({ behavior: "smooth", block: "start" });
    els.titleInput.focus();
  }

  function closeComposer() {
    if (!els.composer) return;
    els.composer.hidden = true;
    els.form.reset();
    els.postId.value = "";
    clearFormErrors(els.form);
  }

  function handleComposerSubmit(e) {
    e.preventDefault();
    clearFormErrors(els.form);
    var payload = { title: els.titleInput.value.trim(), content: els.contentInput.value.trim() };
    var id = els.postId.value;
    var url = id ? "/api/blog/posts/" + id + "/" : "/api/blog/posts/";
    var method = id ? "PUT" : "POST";

    apiFetch(url, { method: method, body: payload }).then(function (res) {
      if (res.ok) {
        closeComposer();
        fetchPosts();
        return;
      }
      if (res.status === 401) { openAuthModal("signin"); return; }
      if (res.data.errors) {
        showError(els.titleError, (res.data.errors.title || [])[0]);
        showError(els.contentError, (res.data.errors.content || [])[0]);
      } else {
        showError(els.formError, res.data.error || str("errorGeneric", "Something went wrong. Please try again."));
      }
    });
  }

  // ---------------------------------------------------------------
  // Auth modal
  // ---------------------------------------------------------------
  function openAuthModal(mode) {
    els.signInForm.reset();
    els.signUpForm.reset();
    clearFormErrors(els.signInForm);
    clearFormErrors(els.signUpForm);
    els.signInPane.hidden = mode !== "signin";
    els.signUpPane.hidden = mode !== "signup";
    els.modalBackdrop.hidden = false;
    document.body.style.overflow = "hidden";
    var focusEl = mode === "signup"
      ? document.getElementById("signUpUsername")
      : document.getElementById("signInUsername");
    if (focusEl) focusEl.focus();
  }

  function closeAuthModal() {
    els.modalBackdrop.hidden = true;
    document.body.style.overflow = "";
  }

  function handleSignIn(e) {
    e.preventDefault();
    showError(els.signInError, "");
    var payload = {
      username: document.getElementById("signInUsername").value.trim(),
      password: document.getElementById("signInPassword").value,
    };
    apiFetch("/api/auth/login/", { method: "POST", body: payload }).then(function (res) {
      if (res.ok) {
        onAuthenticated(res.data.user);
        closeAuthModal();
      } else {
        showError(els.signInError, res.data.error);
      }
    });
  }

  function handleSignUp(e) {
    e.preventDefault();
    clearFormErrors(els.signUpForm);
    var payload = {
      username: document.getElementById("signUpUsername").value.trim(),
      email: document.getElementById("signUpEmail").value.trim(),
      password1: document.getElementById("signUpPassword1").value,
      password2: document.getElementById("signUpPassword2").value,
    };
    apiFetch("/api/auth/signup/", { method: "POST", body: payload }).then(function (res) {
      if (res.ok) {
        onAuthenticated(res.data.user);
        closeAuthModal();
        return;
      }
      var errors = res.data.errors || {};
      showError(document.getElementById("signUpUsernameError"), (errors.username || [])[0]);
      showError(document.getElementById("signUpEmailError"), (errors.email || [])[0]);
      showError(document.getElementById("signUpPassword1Error"), (errors.password1 || [])[0]);
      showError(document.getElementById("signUpPassword2Error"), (errors.password2 || [])[0]);
      showError(els.signUpError, (errors.__all__ || [])[0]);
    });
  }

  function onAuthenticated(user) {
    state.user = user;
    saveCachedUser(user);
    renderAuthActions();
    fetchPosts();
  }

  function handleSignOut() {
    apiFetch("/api/auth/logout/", { method: "POST" }).then(function () {
      state.user = null;
      saveCachedUser(null);
      closeComposer();
      renderAuthActions();
      fetchPosts();
    });
  }

  // ---------------------------------------------------------------
  // Data loading
  // ---------------------------------------------------------------
  function syncUser() {
    // Optimistic paint from the LocalStorage cache first (instant, no
    // flash of the signed-out state), then reconcile against the real
    // session — the only source of truth — and correct if they differ
    // (e.g. the session expired, or the user signed out in another tab).
    var cached = loadCachedUser();
    if (cached) {
      state.user = cached;
      renderAuthActions();
    }
    return apiFetch("/api/auth/me/").then(function (res) {
      var user = res.ok ? res.data.user : null;
      if (JSON.stringify(user) !== JSON.stringify(cached)) {
        state.user = user;
        saveCachedUser(user);
        renderAuthActions();
      }
    });
  }

  function fetchPosts() {
    return apiFetch("/api/blog/posts/").then(function (res) {
      if (res.ok) {
        state.posts = res.data.posts;
        renderFeed();
      }
    });
  }

  // ---------------------------------------------------------------
  // Wiring
  // ---------------------------------------------------------------
  function bindEvents() {
    els.authActions.addEventListener("click", function (e) {
      if (e.target.closest("[data-blog-write]")) openComposer(null);
      else if (e.target.closest("[data-blog-signin]")) openAuthModal("signin");
      else if (e.target.closest("[data-blog-signup]")) openAuthModal("signup");
      else if (e.target.closest("[data-blog-signout]")) handleSignOut();
    });

    els.feed.addEventListener("click", function (e) {
      var editBtn = e.target.closest("[data-edit]");
      var deleteBtn = e.target.closest("[data-delete]");
      if (editBtn) {
        var post = state.posts.filter(function (p) { return String(p.id) === editBtn.dataset.edit; })[0];
        if (post) openComposer(post);
      } else if (deleteBtn) {
        if (!window.confirm(str("deleteConfirm", "Delete this post? This cannot be undone."))) return;
        apiFetch("/api/blog/posts/" + deleteBtn.dataset.delete + "/", { method: "DELETE" }).then(function (res) {
          if (res.ok) fetchPosts();
        });
      }
    });

    els.composerCancel.addEventListener("click", closeComposer);
    els.form.addEventListener("submit", handleComposerSubmit);

    els.signInForm.addEventListener("submit", handleSignIn);
    els.signUpForm.addEventListener("submit", handleSignUp);
    document.querySelectorAll("[data-show-signup]").forEach(function (btn) {
      btn.addEventListener("click", function () { openAuthModal("signup"); });
    });
    document.querySelectorAll("[data-show-signin]").forEach(function (btn) {
      btn.addEventListener("click", function () { openAuthModal("signin"); });
    });

    els.modalClose.addEventListener("click", closeAuthModal);
    els.modalBackdrop.addEventListener("click", function (e) {
      if (e.target === els.modalBackdrop) closeAuthModal();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !els.modalBackdrop.hidden) closeAuthModal();
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    cacheEls();
    if (!els.feed) return; // not on the blog page
    bindEvents();
    syncUser();
    fetchPosts();
  });
})();
