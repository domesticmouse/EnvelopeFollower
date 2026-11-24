/* PROTOTYPE (Issue #8): Click-to-copy enhancement for !!! prompt blocks and multi-turn exchanges */

(function () {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";
  const timers = new WeakMap();
  let lastMessage = "";
  let promptCounter = 0;
  let groupCounter = 0;

  function createIcon(pathData, className) {
    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("class", `prompt-copy-icon ${className}`);
    const path = document.createElementNS(SVG_NS, "path");
    path.setAttribute("d", pathData);
    svg.appendChild(path);
    return svg;
  }

  function legacyCopy(text) {
    const previousFocus = document.activeElement;
    const field = Object.assign(document.createElement("textarea"), { value: text });
    field.setAttribute("readonly", "");
    field.style.cssText = "position:fixed;inset-block-start:0;opacity:0";
    document.body.append(field);
    field.select();
    try {
      return document.execCommand("copy");
    } finally {
      field.remove();
      if (previousFocus && typeof previousFocus.focus === "function") {
        previousFocus.focus({ preventScroll: true });
      }
    }
  }

  function report(button, ok) {
    const tip = button.nextElementSibling;
    if (!tip) return;
    clearTimeout(timers.get(button));
    button.removeAttribute("data-copied");
    button.removeAttribute("data-failed");

    let message = ok ? "Copied" : "Copy failed";
    if (message === lastMessage) {
      message += "\u00A0";
    }
    lastMessage = message;

    tip.textContent = "";
    void button.offsetWidth;
    button.setAttribute(ok ? "data-copied" : "data-failed", "");
    requestAnimationFrame(() => {
      tip.textContent = message;
    });

    timers.set(
      button,
      setTimeout(() => {
        button.removeAttribute("data-copied");
        button.removeAttribute("data-failed");
        tip.textContent = "";
      }, 2000)
    );
  }

  async function copyPrompt(button, target) {
    if (!button || !target) return;
    const text = target.matches("input, textarea")
      ? target.value
      : target.innerText.trim();
    if (!text) return;

    try {
      await navigator.clipboard.writeText(text);
      report(button, true);
    } catch {
      if (legacyCopy(text)) {
        report(button, true);
      } else {
        report(button, false);
      }
    }
  }

  if (!window.__envPromptCopyBound) {
    window.__envPromptCopyBound = true;

    document.addEventListener(
      "command",
      (event) => {
        if (event.command === "--copy") {
          copyPrompt(event.source, event.target);
        }
      },
      true
    );

    if (!("CommandEvent" in window)) {
      document.addEventListener("click", (event) => {
        if (event.defaultPrevented) return;
        const button = event.target.closest('button[command="--copy"]');
        if (!button) return;
        const targetId = button.getAttribute("commandfor");
        const target = targetId ? document.getElementById(targetId) : null;
        if (target) {
          copyPrompt(button, target);
        }
      });
    }
  }

  function activateTurn(group, nextIndex) {
    const tabs = Array.from(
      group.querySelectorAll(':scope > .prompt-group-tabs > [role="tab"]')
    );
    const panels = Array.from(group.querySelectorAll(":scope > .admonition.prompt"));
    if (!tabs.length || !panels.length) return;

    const clamped = ((nextIndex % panels.length) + panels.length) % panels.length;
    group.dataset.activeTurn = String(clamped);

    const isTabbed = (document.documentElement.dataset.protoVariant || "A") === "C";
    panels.forEach((panel, idx) => {
      const active = idx === clamped;
      panel.hidden = isTabbed ? !active : false;
    });

    tabs.forEach((tab, idx) => {
      const active = idx === clamped;
      tab.setAttribute("aria-selected", active ? "true" : "false");
      tab.setAttribute("tabindex", active ? "0" : "-1");
    });
  }

  function syncPromptGroups(variantKey) {
    const isTabbed = variantKey === "C";
    document.querySelectorAll('.prompt-group[data-multi-turn="true"]').forEach((group) => {
      const activeIndex = Number(group.dataset.activeTurn || 0);
      const tabs = Array.from(
        group.querySelectorAll(':scope > .prompt-group-tabs > [role="tab"]')
      );
      const panels = Array.from(group.querySelectorAll(":scope > .admonition.prompt"));

      panels.forEach((panel, idx) => {
        const tab = tabs[idx];
        if (isTabbed) {
          panel.setAttribute("role", "tabpanel");
          if (tab && tab.id) {
            panel.setAttribute("aria-labelledby", tab.id);
          }
          panel.hidden = idx !== activeIndex;
        } else {
          panel.removeAttribute("role");
          panel.removeAttribute("aria-labelledby");
          panel.hidden = false;
        }
      });

      tabs.forEach((tab, idx) => {
        const active = idx === activeIndex;
        tab.setAttribute("aria-selected", active ? "true" : "false");
        tab.setAttribute("tabindex", active ? "0" : "-1");
      });
    });
  }

  function enhanceSinglePrompt(card) {
    if (card.dataset.promptBound === "true") return;
    card.dataset.promptBound = "true";
    promptCounter += 1;
    const bodyId = `prompt-body-${promptCounter}`;

    const titleEl = card.querySelector(":scope > .admonition-title");
    const titleText = titleEl ? titleEl.textContent.trim() : "AI Agent Prompt";

    const bodyEl = document.createElement("div");
    bodyEl.className = "prompt-body";
    bodyEl.id = bodyId;

    const nodesToMove = Array.from(card.childNodes).filter((node) => node !== titleEl);
    nodesToMove.forEach((node) => bodyEl.appendChild(node));
    card.appendChild(bodyEl);

    const actionsEl = document.createElement("div");
    actionsEl.className = "prompt-actions";

    const wrapEl = document.createElement("span");
    wrapEl.className = "prompt-copy-wrap";

    const buttonEl = document.createElement("button");
    buttonEl.type = "button";
    buttonEl.className = "prompt-copy-btn";
    buttonEl.setAttribute("command", "--copy");
    buttonEl.setAttribute("commandfor", bodyId);

    buttonEl.appendChild(
      createIcon(
        "M19 21H8V7h11m0-2H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2m-3-4H4a2 2 0 0 0-2 2v14h2V3h12z",
        "prompt-icon-copy"
      )
    );
    buttonEl.appendChild(
      createIcon(
        "M21 7 9 19l-5.5-5.5 1.41-1.41L9 16.17 19.59 5.59z",
        "prompt-icon-check"
      )
    );
    buttonEl.appendChild(
      createIcon(
        "M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2m1 15h-2v-2h2zm0-4h-2V7h2z",
        "prompt-icon-error"
      )
    );

    const visibleLabel = document.createElement("span");
    visibleLabel.textContent = "Copy";
    buttonEl.appendChild(visibleLabel);

    const srSuffix = document.createElement("span");
    srSuffix.className = "sr-only";
    srSuffix.textContent = ` ${titleText}`;
    buttonEl.appendChild(srSuffix);

    const tipEl = document.createElement("span");
    tipEl.className = "prompt-copy-tip";
    tipEl.setAttribute("role", "status");

    wrapEl.appendChild(buttonEl);
    wrapEl.appendChild(tipEl);
    actionsEl.appendChild(wrapEl);
    card.appendChild(actionsEl);
  }

  function groupConsecutivePrompts() {
    const cards = Array.from(document.querySelectorAll(".md-typeset .admonition.prompt"));
    const visited = new Set();

    cards.forEach((card) => {
      if (visited.has(card)) return;
      if (card.parentElement && card.parentElement.classList.contains("prompt-group")) {
        visited.add(card);
        return;
      }

      const run = [card];
      visited.add(card);
      let cursor = card.nextElementSibling;
      while (cursor && cursor.matches(".admonition.prompt")) {
        run.push(cursor);
        visited.add(cursor);
        cursor = cursor.nextElementSibling;
      }

      if (run.length < 2) return;

      groupCounter += 1;
      const gId = groupCounter;
      const group = document.createElement("div");
      group.className = "prompt-group";
      group.dataset.multiTurn = "true";
      group.dataset.activeTurn = "0";

      const header = document.createElement("div");
      header.className = "prompt-group-header";
      header.textContent = `Multi-turn exchange · ${run.length} turns`;

      const tablist = document.createElement("div");
      tablist.className = "prompt-group-tabs";
      tablist.setAttribute("role", "tablist");
      tablist.setAttribute("aria-label", "Prompt turns");

      run[0].parentNode.insertBefore(group, run[0]);
      group.appendChild(header);
      group.appendChild(tablist);

      run.forEach((turnCard, idx) => {
        const turnNum = idx + 1;
        turnCard.dataset.turnIndex = String(turnNum);
        if (!turnCard.id) {
          turnCard.id = `prompt-turn-${gId}-${turnNum}`;
        }
        group.appendChild(turnCard);

        const tab = document.createElement("button");
        tab.type = "button";
        tab.className = "prompt-group-tab";
        tab.setAttribute("role", "tab");
        tab.id = `prompt-tab-${gId}-${turnNum}`;
        tab.setAttribute("aria-controls", turnCard.id);
        tab.setAttribute("aria-selected", idx === 0 ? "true" : "false");
        tab.setAttribute("tabindex", idx === 0 ? "0" : "-1");
        tab.textContent = `Turn ${turnNum}`;
        tab.addEventListener("click", () => {
          activateTurn(group, idx);
        });
        tablist.appendChild(tab);
      });

      tablist.addEventListener("keydown", (event) => {
        const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));
        const currentIdx = tabs.indexOf(document.activeElement);
        if (currentIdx === -1) return;

        let targetIdx = null;
        if (event.key === "ArrowRight") {
          targetIdx = (currentIdx + 1) % tabs.length;
        } else if (event.key === "ArrowLeft") {
          targetIdx = (currentIdx - 1 + tabs.length) % tabs.length;
        } else if (event.key === "Home") {
          targetIdx = 0;
        } else if (event.key === "End") {
          targetIdx = tabs.length - 1;
        }

        if (targetIdx !== null) {
          event.preventDefault();
          event.stopPropagation();
          activateTurn(group, targetIdx);
          tabs[targetIdx].focus();
        }
      });
    });
  }

  function enhancePrompts() {
    document
      .querySelectorAll(".md-typeset .admonition.prompt:not([data-prompt-bound])")
      .forEach(enhanceSinglePrompt);
    groupConsecutivePrompts();
    syncPromptGroups(document.documentElement.dataset.protoVariant || "A");
  }

  window.__syncPromptGroups = syncPromptGroups;

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(enhancePrompts);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", enhancePrompts);
  } else {
    enhancePrompts();
  }
})();
