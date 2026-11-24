/* PROTOTYPE (Issue #8): Floating ?variant= switcher bar (Sub-shape A across MkDocs pages) */

(function () {
  "use strict";

  const params = new URLSearchParams(window.location.search);
  const isProtoContext =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1" ||
    window.location.protocol === "file:" ||
    params.has("variant");

  if (!isProtoContext) {
    return;
  }

  const VARIANTS = [
    {
      key: "A",
      name: "Studio Slab",
      summary: "Dark-only · Action-bar prompt · Stacked turns",
      darkOnly: true,
    },
    {
      key: "B",
      name: "Console Deck",
      summary: "Light toggle · Bottom CTA · Unified thread",
      darkOnly: false,
    },
    {
      key: "C",
      name: "Editorial Manual",
      summary: "Dark-only · Split-rail · Tabbed turns",
      darkOnly: true,
    },
  ];

  let variantBScheme = null;
  let bodyObserver = null;

  function normalizeVariant(raw) {
    const key = (raw || "A").toUpperCase();
    return VARIANTS.some((v) => v.key === key) ? key : "A";
  }

  function getCurrentVariant() {
    return normalizeVariant(document.documentElement.dataset.protoVariant);
  }

  function getVariantMeta(key) {
    return VARIANTS.find((v) => v.key === key) || VARIANTS[0];
  }

  // Stamp immediately to minimize flash before body paints
  const initialVariant = normalizeVariant(params.get("variant"));
  document.documentElement.dataset.protoVariant = initialVariant;

  function updateStatusBar(key) {
    const bar = document.getElementById("proto-switcher");
    if (!bar) return;
    const meta = getVariantMeta(key);
    const scheme = document.body?.getAttribute("data-md-color-scheme") || "slate";
    const labelEl = bar.querySelector(".proto-switcher-label");
    const metaEl = bar.querySelector(".proto-switcher-meta");
    if (labelEl) {
      labelEl.textContent = `${meta.key} (${meta.name})`;
    }
    if (metaEl) {
      metaEl.textContent = `${meta.summary} · scheme=${scheme}`;
    }
  }

  function applyPaletteForVariant(meta) {
    if (!document.body) return;
    if (meta.darkOnly) {
      document.body.setAttribute("data-md-color-scheme", "slate");
    } else {
      document.body.setAttribute("data-md-color-scheme", variantBScheme);
      const targetRadio = document.querySelector(
        `input.md-option[name="__palette"][data-md-color-scheme="${variantBScheme}"]`
      );
      if (targetRadio) {
        targetRadio.checked = true;
      }
    }
  }

  function applyVariant(rawKey, updateHistory = true) {
    const key = normalizeVariant(rawKey);
    const meta = getVariantMeta(key);

    document.documentElement.dataset.protoVariant = key;
    applyPaletteForVariant(meta);

    if (updateHistory) {
      const nextUrl = new URL(window.location.href);
      nextUrl.searchParams.set("variant", key);
      window.history.replaceState(null, "", nextUrl.toString());
    }

    if (typeof window.__syncPromptGroups === "function") {
      window.__syncPromptGroups(key);
    }

    updateStatusBar(key);
  }

  function stepVariant(delta) {
    const current = getCurrentVariant();
    const idx = VARIANTS.findIndex((v) => v.key === current);
    const nextIdx = (idx + delta + VARIANTS.length) % VARIANTS.length;
    applyVariant(VARIANTS[nextIdx].key, true);
  }

  function mountSwitcher() {
    if (!document.body) return;

    if (variantBScheme === null) {
      variantBScheme = document.body.getAttribute("data-md-color-scheme") || "slate";
    }

    if (!document.getElementById("proto-switcher")) {
      const bar = document.createElement("aside");
      bar.id = "proto-switcher";
      bar.className = "proto-switcher";
      bar.setAttribute("role", "region");
      bar.setAttribute("aria-label", "Prototype variant switcher");

      const prevBtn = document.createElement("button");
      prevBtn.type = "button";
      prevBtn.className = "proto-switcher-btn";
      prevBtn.setAttribute("aria-label", "Previous prototype variant");
      prevBtn.textContent = "\u2190";
      prevBtn.addEventListener("click", () => stepVariant(-1));

      const status = document.createElement("div");
      status.className = "proto-switcher-status";
      const label = document.createElement("span");
      label.className = "proto-switcher-label";
      const meta = document.createElement("span");
      meta.className = "proto-switcher-meta";
      status.appendChild(label);
      status.appendChild(meta);

      const nextBtn = document.createElement("button");
      nextBtn.type = "button";
      nextBtn.className = "proto-switcher-btn";
      nextBtn.setAttribute("aria-label", "Next prototype variant");
      nextBtn.textContent = "\u2192";
      nextBtn.addEventListener("click", () => stepVariant(1));

      bar.appendChild(prevBtn);
      bar.appendChild(status);
      bar.appendChild(nextBtn);
      document.body.appendChild(bar);
      document.body.dataset.protoMounted = "true";
    }

    if (!bodyObserver) {
      bodyObserver = new MutationObserver(() => {
        const current = getCurrentVariant();
        const meta = getVariantMeta(current);
        const scheme = document.body.getAttribute("data-md-color-scheme") || "slate";
        if (!meta.darkOnly) {
          variantBScheme = scheme;
        }
        updateStatusBar(current);
      });
      bodyObserver.observe(document.body, {
        attributes: true,
        attributeFilter: ["data-md-color-scheme"],
      });
    }

    applyVariant(normalizeVariant(new URLSearchParams(window.location.search).get("variant")), true);
  }

  if (!window.__envProtoEventsBound) {
    window.__envProtoEventsBound = true;

    document.addEventListener("keydown", (event) => {
      if (event.metaKey || event.ctrlKey || event.altKey) return;
      const ignoreSelector =
        'input, textarea, select, [contenteditable], [role="tablist"], [role="tab"]';
      if (
        (event.target && event.target.closest && event.target.closest(ignoreSelector)) ||
        (document.activeElement &&
          document.activeElement.closest &&
          document.activeElement.closest(ignoreSelector))
      ) {
        return;
      }
      const searchToggle = document.querySelector('[data-md-toggle="search"]');
      if (searchToggle && searchToggle.checked) return;

      if (event.key === "ArrowLeft") {
        event.preventDefault();
        stepVariant(-1);
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        stepVariant(1);
      }
    });

    // Preserve ?variant= across internal page navigation links
    document.addEventListener("click", (event) => {
      if (
        event.defaultPrevented ||
        event.button !== 0 ||
        event.metaKey ||
        event.ctrlKey ||
        event.shiftKey ||
        event.altKey
      ) {
        return;
      }
      const link = event.target.closest("a[href]");
      if (!link) return;
      const rawHref = link.getAttribute("href") || "";
      if (
        !rawHref ||
        rawHref.startsWith("#") ||
        link.hasAttribute("download") ||
        (link.target && link.target !== "_self")
      ) {
        return;
      }

      let dest;
      try {
        dest = new URL(link.href, window.location.href);
      } catch {
        return;
      }

      if (dest.origin !== window.location.origin) return;
      if (dest.pathname === window.location.pathname) return;

      dest.searchParams.set("variant", getCurrentVariant());
      event.preventDefault();
      window.location.assign(dest.toString());
    });
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(mountSwitcher);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountSwitcher);
  } else {
    mountSwitcher();
  }
})();
