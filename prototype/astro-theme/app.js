// Three structurally different ENV / SKEW Astro Build Tutorial theme variants (A: Hardware Blueprint, B: Studio Editorial, C: Patchbay Workbench), switchable via ?variant=A|B|C (&page=stage5|overview).

import {
  ENV_SKEW_SLAB_SVG,
  FACEPLATE_PREVIEW_SVG,
  GAIN_BARS_SVG,
  HERO_ENVELOPE_SVG,
  LED_OCTAGON_SVG,
  NORMAL_ARROW_SVG,
  PCB_TRACE_DIVIDER_SVG,
} from "./svg-motifs.js";

const STORAGE_KEY = "env-proto-color-scheme";

const VARIANT_META = {
  A: { key: "A", name: "Hardware Blueprint", summary: "Companion-site twin · TP4-TP11 PCB rail · Command Cartridges" },
  B: { key: "B", name: "Studio Editorial", summary: "Reading-first manual · SVG slab header · Console Decks" },
  C: { key: "C", name: "Patchbay Workbench", summary: "3U rack modules · 3-state switch · Split Patch-Strips" },
};

const CURRICULUM_GROUPS = [
  {
    id: "overview",
    label: "Overview",
    items: [
      { slug: "/", navTitle: "Overview", badge: "00", order: 0, pageKey: "overview", sectionLabel: "Overview" },
    ],
  },
  {
    id: "hardware",
    label: "Hardware Build",
    items: [
      { slug: "/stages/01-hardware-agent-skills/", navTitle: "Hardware Agent Skills", badge: "01", order: 1, sectionLabel: "Hardware Build" },
      { slug: "/stages/02-sketch-extraction-and-critique/", navTitle: "Sketch & Circuit Critique", badge: "02", order: 2, sectionLabel: "Hardware Build" },
      { slug: "/stages/03-design-spec-and-dft/", navTitle: "DesignSpec & DFT", badge: "03", order: 3, sectionLabel: "Hardware Build" },
      { slug: "/stages/04-skidl-and-schematic/", navTitle: "SKiDL & Schematic", badge: "04", order: 4, sectionLabel: "Hardware Build" },
      { slug: "/stages/05-main-pcb-and-silkscreen/", navTitle: "6 HP PCB & Silkscreen", badge: "05", order: 5, pageKey: "stage5", sectionLabel: "Hardware Build" },
      { slug: "/stages/06-front-panel-and-artwork/", navTitle: "Front Panel & Artwork", badge: "06", order: 6, sectionLabel: "Hardware Build" },
      { slug: "/stages/07-fabrication-checklists-and-patches/", navTitle: "Fab, Checklists & Patches", badge: "07", order: 7, sectionLabel: "Hardware Build" },
    ],
  },
  {
    id: "companion-site",
    label: "Companion Site",
    items: [
      { slug: "/stages/08-wayfinder-site-planning/", navTitle: "Wayfinder Site Planning", badge: "08", order: 8, sectionLabel: "Companion Site" },
      { slug: "/stages/09-companion-site-delivery/", navTitle: "Companion Site Delivery", badge: "09", order: 9, sectionLabel: "Companion Site" },
    ],
  },
  {
    id: "optional",
    label: "Optional Exploration",
    items: [
      { slug: "/optional/ac-dc-input-coupling/", navTitle: "AC/DC Input Coupling", badge: "OPT", order: 10, sectionLabel: "Optional" },
    ],
  },
  {
    id: "appendix",
    label: "Tutorial Appendix",
    items: [
      { slug: "/appendix/netlist-and-bom/", navTitle: "Netlist, BOM & Silkscreen", badge: "APP", order: 11, sectionLabel: "Appendix" },
      { slug: "/appendix/engineering-sign-off-checklist/", navTitle: "Engineering Sign-Off", badge: "APP", order: 12, sectionLabel: "Appendix" },
    ],
  },
];

const SEARCH_CORPUS = [
  { title: "Overview — ENV / SKEW Build Tutorial", section: "Overview", pageKey: "overview", text: "Hagiwo Sketch 6 HP Eurorack module Two Sites One Palette SKiDL KiCad 10 VectorCraft Wayfinder Astro Core" },
  { title: "Stage 1: Hardware Agent Skills & Repo Setup", section: "Hardware Build", pageKey: "stage5", text: "9 core skills Living Context Map /agy-customizations skills-lock.json vectorcraft-cli" },
  { title: "Stage 4: SKiDL Capture & KiCad Schematic", section: "Hardware Build", pageKey: "stage5", text: "envelope_follower.py 80 parts 48 nets Dailywell 2MS1 3 Extended SKU budget" },
  { title: "Stage 5: 6 HP Main PCB, silk_layout.json & /edit-silkscreen", section: "Hardware Build", pageKey: "stage5", text: "generate_kicad_pcb.py silk_layout.json /edit-silkscreen 83 footprints TP4 TP7 TP11 F.Cu B.Cu 50 SMD" },
  { title: "Stage 6: Mated 3U Front Panel & VectorCraft Artwork", section: "Hardware Build", pageKey: "stage5", text: "eurorack-panel Matte Black ENIG Gold VectorCraft front_soldermask.svg SHAPE_POLY_SET" },
  { title: "Stage 8: Planning the Companion Site with /wayfinder", section: "Companion Site", pageKey: "overview", text: "/wayfinder GLOSSARY.md ADR 0001 Map #4 research grilling prototype" },
  { title: "Optional: AC/DC Input Coupling Mode", section: "Optional", pageKey: "stage5", text: "SW3 across C7 DC-coupled precision full-wave rectification J2 SLEW IN" },
  { title: "Netlist, BOM & Silkscreen Schedule", section: "Appendix", pageKey: "overview", text: "50 B.Cu SMD 18 Manual THT 12 DNP test points jlcpcb_bom.csv silk_layout.json" },
];

const STAGE5_TOC = [
  { id: "step-5-1", label: "Step 5.1: Automated 6 HP Main PCB", depth: 2 },
  { id: "board-partitioning", label: "Board Partitioning (83 Footprints)", depth: 3 },
  { id: "pcb-renders", label: "Main PCB Renders", depth: 3 },
  { id: "step-5-2", label: "Step 5.2: Declarative silk_layout.json", depth: 2 },
  { id: "cli-modes", label: "Six CLI Modes", depth: 3 },
  { id: "step-5-3", label: "Step 5.3: /edit-silkscreen Loop", depth: 2 },
];

const OVERVIEW_TOC = [
  { id: "two-sites", label: "Two Sites, One Palette", depth: 2 },
  { id: "hardware-renders", label: "Fabricated Hardware Renders", depth: 2 },
  { id: "stage-guide", label: "Stage-by-Stage Guide", depth: 2 },
];

const COPY_ICONS_SVG = `
  <svg class="prompt-copy-icon prompt-icon-copy" viewBox="0 0 24 24" aria-hidden="true"><path d="M19 21H8V7h11m0-2H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2m-3-4H4a2 2 0 0 0-2 2v14h2V3h12z"/></svg>
  <svg class="prompt-copy-icon prompt-icon-check" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 7 9 19l-5.5-5.5 1.41-1.41L9 16.17 19.59 5.59z"/></svg>
  <svg class="prompt-copy-icon prompt-icon-error" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2m1 15h-2v-2h2zm0-4h-2V7h2z"/></svg>
`;

const GITHUB_ICON_SVG = `<svg width="15" height="15" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg>`;

// ============================================================================
// STATE & THEME CONTROLLER (follows modern-web-guidance dark-mode-toggle)
// ============================================================================
const state = {
  variant: "A",
  page: "stage5",
  storedScheme: readStoredScheme(),
  activeSearchIndex: 0,
};

function readStoredScheme() {
  try {
    const val = localStorage.getItem(STORAGE_KEY);
    return val === "dark" || val === "light" ? val : null;
  } catch {
    return null;
  }
}

function getSystemScheme() {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function getEffectiveScheme() {
  if (state.storedScheme) return state.storedScheme;
  const metaContent = document.querySelector('meta[name="color-scheme"]')?.getAttribute("content");
  if (metaContent === "dark" || metaContent === "light") return metaContent;
  return getSystemScheme();
}

function applyColorScheme(nextStored) {
  state.storedScheme = nextStored;
  try {
    if (nextStored === "dark" || nextStored === "light") {
      localStorage.setItem(STORAGE_KEY, nextStored);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  } catch {
    // storage disabled; still apply to document <meta>
  }
  const meta = document.querySelector('meta[name="color-scheme"]');
  if (meta) {
    meta.setAttribute("content", nextStored ?? "light dark");
  }
}

// 2-state toggle: target is opposite of currently rendered scheme; undo stores nothing if matching OS
function toggleTwoStateScheme() {
  const current = getEffectiveScheme();
  const target = current === "dark" ? "light" : "dark";
  const sys = getSystemScheme();
  applyColorScheme(target === sys ? null : target);
  renderApp();
}

function setThreeStateScheme(mode) {
  applyColorScheme(mode === "system" ? null : mode);
  renderApp();
}

function readParamsFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const v = (params.get("variant") || "A").toUpperCase();
  const p = (params.get("page") || "stage5").toLowerCase();
  state.variant = VARIANT_META[v] ? v : "A";
  state.page = p === "overview" ? "overview" : "stage5";
}

function syncUrlParams() {
  const url = new URL(window.location.href);
  url.searchParams.set("variant", state.variant);
  url.searchParams.set("page", state.page);
  window.history.replaceState(null, "", url);
}

// ============================================================================
// COPY CONTROLLER (Invoker Commands + CommandEvent fallback + VoiceOver dedup)
// ============================================================================
const copyTimers = new WeakMap();
let lastCopyMessage = "";

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

function reportCopyFeedback(button, ok) {
  const tip = button.nextElementSibling;
  if (!tip) return;
  clearTimeout(copyTimers.get(button));
  button.removeAttribute("data-copied");
  button.removeAttribute("data-failed");

  let message = ok ? "Copied" : "Copy failed";
  if (message === lastCopyMessage) {
    message += "\u00A0";
  }
  lastCopyMessage = message;

  tip.textContent = "";
  void button.offsetWidth;
  button.setAttribute(ok ? "data-copied" : "data-failed", "");
  requestAnimationFrame(() => {
    tip.textContent = message;
  });

  copyTimers.set(
    button,
    setTimeout(() => {
      button.removeAttribute("data-copied");
      button.removeAttribute("data-failed");
      tip.textContent = "";
    }, 2000)
  );
}

async function handleCopyCommand(button, target) {
  if (!button || !target) return;
  const text = target.innerText.trim();
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    reportCopyFeedback(button, true);
  } catch {
    if (legacyCopy(text)) {
      reportCopyFeedback(button, true);
    } else {
      reportCopyFeedback(button, false);
    }
  }
}

function initCopyListeners() {
  document.addEventListener(
    "command",
    (event) => {
      if (typeof event.command === "string" && event.command.startsWith("--copy")) {
        handleCopyCommand(event.source, event.target);
      }
    },
    true
  );

  if (!("CommandEvent" in window)) {
    document.addEventListener("click", (event) => {
      if (event.defaultPrevented) return;
      const btn = event.target.closest('button[command^="--copy"]');
      if (!btn) return;
      const targetId = btn.getAttribute("commandfor");
      const target = targetId ? document.getElementById(targetId) : null;
      if (target) {
        handleCopyCommand(btn, target);
      }
    });
  }
}

// ============================================================================
// PROMPT & PROSE CONTENT HELPERS
// ============================================================================
function renderCopyWidget(targetId, labelText, ariaLabel, extraWrapClass = "") {
  const btn = `<button type="button" class="prompt-copy-btn${extraWrapClass === "chamfer" ? " chamfer-sm" : ""}" command="--copy" commandfor="${targetId}" aria-label="${ariaLabel}">${COPY_ICONS_SVG}<span>${labelText}</span></button>`;
  const wrappedBtn = extraWrapClass === "chamfer" ? `<span class="chamfer-focus-wrap">${btn}</span>` : btn;
  return `<span class="prompt-copy-wrap">${wrappedBtn}<span class="prompt-copy-tip" role="status"></span></span>`;
}

function renderPromptSingle(variant, id, title, traceRef, bodyHtml) {
  if (variant === "A") {
    return `
      <div class="a-prompt-card">
        <div class="a-prompt-head">
          <span class="a-prompt-label">${title} · ${traceRef}</span>
          ${renderCopyWidget(id, "Copy", `Copy ${title}`, "chamfer")}
        </div>
        <div class="a-prompt-body" id="${id}">${bodyHtml}</div>
      </div>
    `;
  }
  if (variant === "B") {
    return `
      <div class="b-prompt-card">
        <div class="b-prompt-head">
          <span>${title}</span>
          <span class="mono">${traceRef}</span>
        </div>
        <div class="b-prompt-body" id="${id}">${bodyHtml}</div>
        <div class="b-prompt-actions">
          ${renderCopyWidget(id, "Copy Prompt", `Copy ${title}`)}
        </div>
      </div>
    `;
  }
  return `
    <div class="c-patch-strip">
      <div class="c-patch-spine">
        <span class="mono" style="font-size:0.7rem;font-weight:700;">PROMPT</span>
        <span class="c-patch-led" aria-hidden="true">${LED_OCTAGON_SVG}</span>
        ${renderCopyWidget(id, "Copy", `Copy ${title}`)}
      </div>
      <div class="c-patch-payload">
        <div class="c-patch-title">${title} · ${traceRef}</div>
        <div class="c-patch-text" id="${id}">${bodyHtml}</div>
      </div>
    </div>
  `;
}

function renderPromptMultiTurn(variant, turns) {
  if (variant === "A") {
    return `
      <div class="a-prompt-group">
        ${turns
          .map(
            (t, idx) => `
          <div class="a-prompt-card" data-turn-index="${idx + 1}">
            <div class="a-prompt-head">
              <span class="a-prompt-label">Turn ${idx + 1} · ${t.title}</span>
              ${renderCopyWidget(t.id, "Copy", `Copy Turn ${idx + 1} ${t.title}`, "chamfer")}
            </div>
            <div class="a-prompt-body" id="${t.id}">${t.body}</div>
          </div>`
          )
          .join("")}
      </div>
    `;
  }
  if (variant === "B") {
    return `
      <div class="b-prompt-group">
        <div class="b-prompt-group-head">Multi-Turn Exchange · ${turns.length} Turns · Trace 07</div>
        ${turns
          .map(
            (t, idx) => `
          <div class="b-prompt-card" style="margin-block:0.65rem;">
            <div class="b-prompt-head">
              <span>Turn ${idx + 1} — ${t.title}</span>
            </div>
            <div class="b-prompt-body" id="${t.id}">${t.body}</div>
            <div class="b-prompt-actions">
              ${renderCopyWidget(t.id, "Copy Turn", `Copy Turn ${idx + 1} ${t.title}`)}
            </div>
          </div>`
          )
          .join("")}
      </div>
    `;
  }
  return `
    <div class="c-patch-chain">
      ${turns
        .map(
          (t, idx) => `
        ${
          idx > 0
            ? `<div class="c-patch-connector">${NORMAL_ARROW_SVG}<span>PATCHED TO TURN ${idx + 1}</span></div>`
            : ""
        }
        <div class="c-patch-strip" style="margin-block:0;">
          <div class="c-patch-spine">
            <span class="mono" style="font-size:0.74rem;font-weight:700;">T${idx + 1}</span>
            <span class="c-patch-led" aria-hidden="true">${LED_OCTAGON_SVG}</span>
            ${renderCopyWidget(t.id, "Copy", `Copy Turn ${idx + 1} ${t.title}`)}
          </div>
          <div class="c-patch-payload">
            <div class="c-patch-title">${t.title}</div>
            <div class="c-patch-text" id="${t.id}">${t.body}</div>
          </div>
        </div>`
        )
        .join("")}
    </div>
  `;
}

function renderDivider(variant, label = "") {
  if (variant === "A") {
    return `<div class="a-hr" role="separator">${PCB_TRACE_DIVIDER_SVG}</div>`;
  }
  if (variant === "B") {
    return `<div class="b-hr" role="separator">${HERO_ENVELOPE_SVG}</div>`;
  }
  return `<div class="c-wing-hr" role="separator"><span>${label || "SECTION"}</span></div>`;
}

function renderStage5Article(variant) {
  const prompt1Body = `<span class="chip-skill">/kicad-pcbnew-layout</span> <span class="chip-skill">/kicad-silkscreen-markup</span> <span class="chip-skill">/eurorack-panel</span> <span class="chip-skill">/kicad</span> Please create and run <code>generate_kicad_pcb.py</code> to generate a 6 HP main PCB (<code>envelope_follower.kicad_pcb</code>) from <span class="chip-file">@[envelope_follower.net]</span>, following <span class="chip-file">@[DesignSpec.md]</span>.`;

  const turns = [
    {
      id: "proto-prompt-t1",
      title: "Declarative Silkscreen Strategy",
      body: `How should I move silkscreen entries such that they can be updated in the generate script?`,
    },
    {
      id: "proto-prompt-t2",
      title: "Extract silk_layout.json",
      body: `Git commit the current state. Then update the script so that I can work with it to move things around in a new chat. Assume I am going to want to move most silkscreen entries, one by one.`,
    },
  ];

  const hero =
    variant === "A"
      ? `
        <header class="a-stage-head">
          <div class="chamfer-sm a-stage-kicker">STAGE 05 · HARDWARE BUILD</div>
          <h1>Stage 5: 6 HP Main PCB, <code>silk_layout.json</code> &amp; <code>/edit-silkscreen</code></h1>
        </header>`
      : variant === "B"
      ? `
        <header class="b-stage-head">
          <div class="b-stage-meta">${GAIN_BARS_SVG}<span>Stage 05 of 09 · Hardware Build</span></div>
          <h1>6 HP Main PCB, <code>silk_layout.json</code> &amp; <code>/edit-silkscreen</code></h1>
        </header>`
      : `
        <header class="c-output-bay">
          <div class="c-bay-main">
            <div class="mono" style="font-size:0.74rem;color:var(--accent-gold-link);">HARDWARE BUILD · STAGE 05</div>
            <h1>6 HP Main PCB &amp; Silkscreen Polish</h1>
          </div>
          <div class="c-bay-spine" aria-hidden="true"></div>
          <div class="c-bay-specs">
            <div><strong>BOARD:</strong> 30.0 × 108.0 mm</div>
            <div><strong>PARTS:</strong> 83 footprints · 48 nets</div>
            <div><strong>TRACE:</strong> Session Trace 07</div>
          </div>
        </header>`;

  return `
    ${hero}
    <p>Because <code>envelope_follower.net</code> and <code>envelope_follower.kicad_sch</code> (Stage 4) already capture every net, custom field, <code>DNP</code> test point, and unit-1 symbol UUID, <code>generate_kicad_pcb.py</code> automates the full <code>30.00 × 108.00 mm</code> 2-layer PCB—and then pairs with a declarative <strong><code>silk_layout.json</code></strong> sidecar and a repo-local <strong><code>/edit-silkscreen</code></strong> skill for fast, iterative human + AI silkscreen polishing.</p>

    ${renderDivider(variant, "STEP 5.1")}

    <h2 id="step-5-1">Step 5.1: Automated 6 HP Main PCB Generation &amp; Layout Debugging</h2>
    <p>Generate the 6 HP main PCB from the verified netlist and design spec (Trace 07 Turn 1):</p>

    ${renderPromptSingle(variant, "proto-prompt-1", "AI Agent Prompt — Generate 6 HP Main PCB", "Trace 07 · Turn 1", prompt1Body)}

    <h3 id="board-partitioning">Board Partitioning &amp; 6 HP Mechanical Grid (83 PCB Footprints, 48 Nets)</h3>
    <div class="table-scroll">
      <table class="proto-table">
        <thead>
          <tr><th>Side</th><th>Count</th><th>Components</th><th>Layout Role</th></tr>
        </thead>
        <tbody>
          <tr><td><code>F.Cu</code></td><td>11</td><td><code>RV1</code>–<code>RV4</code>, <code>SW1</code>/<code>LED1</code>/<code>SW2</code>, <code>J1</code>–<code>J4</code></td><td>Front-panel THT controls aligned to the 3U faceplate</td></tr>
          <tr><td><code>B.Cu</code></td><td>50</td><td><code>U1</code>–<code>U2</code> (<code>TL074HIDR</code>), <code>D1</code>–<code>D5</code>, <code>C3</code>–<code>C16</code>, <code>R1</code>–<code>R33</code></td><td>Single-sided SMD PCBA (0°/180° horizontal passives)</td></tr>
          <tr><td><code>B.Cu</code></td><td>7</td><td><code>J_PWR</code> (2×5 IDC), <code>C1</code>–<code>C2</code>, <code>C7</code>, <code>C11</code>–<code>C13</code></td><td>Tall non-panel THT components clear of panel standoff</td></tr>
          <tr><td><code>B.Cu</code></td><td>12</td><td><code>TP1</code>–<code>TP12</code> (<code>Ronghe RH-5001</code>, 1.0 mm drill, <code>DNP</code>)</td><td>Rear bring-up test points (<code>TP4</code>–<code>TP11</code> signal rail)</td></tr>
          <tr><td><code>B.Cu</code></td><td>3</td><td><code>FID1</code>–<code>FID3</code> (<code>Fiducial_1mm_Mask2mm</code>, <code>DNP</code>)</td><td>Asymmetric pick-and-place optical alignment fiducials</td></tr>
        </tbody>
      </table>
    </div>

    <h3 id="pcb-renders">Main PCB Renders</h3>
    <div class="render-grid">
      <figure class="render-figure">
        <img src="/docs/images/pcb_front.png" alt="Main PCB Front Controls F.Cu" />
        <figcaption>Main PCB Front (F.Cu — Panel Controls)</figcaption>
      </figure>
      <figure class="render-figure">
        <img src="/docs/images/pcb_back.png" alt="Main PCB Rear 50 SMD PCBA B.Cu" />
        <figcaption>Main PCB Rear (B.Cu — 50 SMD PCBA &amp; Power)</figcaption>
      </figure>
    </div>

    ${renderDivider(variant, "STEP 5.2")}

    <h2 id="step-5-2">Step 5.2: Declarative Silkscreen Sidecar (<code>silk_layout.json</code>)</h2>
    <p>Extract board silkscreen positions into a declarative sidecar so one-by-one label tweaks never risk unintended copper diffs (Trace 07 Turns 2–3):</p>

    ${renderPromptMultiTurn(variant, turns)}

    <div class="code-block">
      <div class="code-block-head"><span>silk_layout.json (excerpt)</span><span>JSON</span></div>
      <pre><code>{
  "version": 1,
  "coordinate_system": "board-local mm relative to (BOARD_X0=100.0, BOARD_Y0=40.0)",
  "footprints": {
    "R1": {"ref": null, "texts": [{"layer": "B.SilkS", "text": "10R", "x": 13.0, "y": 18.75, "deg": 0.0}]},
    "RV1": {"ref": {"layer": "F.SilkS", "x": 5.4, "y": 14.888, "deg": 90.0}, "texts": [{"text": "GAIN A100K", "x": 5.4, "y": 9.531}]}
  }
}</code></pre>
    </div>

    <h3 id="cli-modes">Six CLI Modes on <code>generate_kicad_pcb.py</code></h3>
    <div class="callout callout-warn">
      <div class="callout-title">▲ Full Rebuild <code>.kicad_pro</code> Guardrail</div>
      <p>Whenever you run a full rebuild (<code>pcbnew.NewBoard</code> / <code>board.Save</code>, e.g., after swapping <code>TP2</code> +12V and <code>TP3</code> −12V), KiCad drops <code>"top_level_sheets"</code> from <code>envelope_follower.kicad_pro</code>. Inspect <code>git diff</code> and restore it if needed.</p>
    </div>

    ${renderDivider(variant, "STEP 5.3")}

    <h2 id="step-5-3">Step 5.3: Minting <code>/edit-silkscreen</code> &amp; Hybrid Human + AI Visual Polish</h2>
    <p>Ask <code>/agy-customizations</code> to create <code>.agents/skills/edit-silkscreen/SKILL.md</code> and <code>scripts/render_silk_preview.py</code>, then alternate rough KiCad GUI label drags (Save with <code>Cmd+S</code>) with <code>--sync-silk</code> → <code>--silk-only</code> → <code>File → Revert</code>.</p>

    <nav class="prev-next-nav" aria-label="Stage navigation">
      <a class="prev-next-card" href="?variant=${variant}&page=stage5" data-nav-page="stage5">
        <span class="prev-next-kicker">← Previous · Stage 04</span>
        <span class="prev-next-title">SKiDL Capture &amp; KiCad Schematic</span>
      </a>
      <a class="prev-next-card" href="?variant=${variant}&page=overview" data-nav-page="overview" style="text-align:end;">
        <span class="prev-next-kicker">Preview Overview · Page 00 →</span>
        <span class="prev-next-title">Overview (Front Panel &amp; Guide)</span>
      </a>
    </nav>
  `;
}

function renderOverviewArticle(variant) {
  return `
    <div class="overview-hero">
      <div>
        <div class="mono" style="font-size:0.78rem;color:var(--accent-gold-link);margin-block-end:0.35rem;">6 HP EURORACK · HAGIWO NO. 43 → ASTRO</div>
        <h1 style="margin:0 0 0.7rem;font-size:1.95rem;">ENV / SKEW Build Tutorial</h1>
        <p style="margin:0;">Walks through the complete human-in-the-loop workflow of turning the <strong>Hagiwo Sketch</strong> into the manufacturable 6 HP Eurorack <code>ENV / SKEW</code> module, a mated 3U Matte Black + ENIG Gold front panel, and a 25-route Companion Site.</p>
      </div>
      <div class="faceplate-wrap">
        ${FACEPLATE_PREVIEW_SVG}
        <span class="mono" style="font-size:0.68rem;color:var(--ink-muted);">30.0 × 128.5 mm · ENIG + Silk</span>
      </div>
    </div>

    <div class="callout" id="two-sites">
      <div class="callout-title">Two Sites, One Palette — Build Tutorial vs. ENV / SKEW Companion Site</div>
      <p>Both repositories share <code>ENV / SKEW</code>'s Matte Black + ENIG Gold palette. You are in the <strong>Build Tutorial</strong> (9-stage AI-assisted engineering curriculum); the finished module's interactive Patch Guides and 211-step Build Checklists live on the <strong>Companion Site ↗</strong>.</p>
    </div>

    ${renderDivider(variant, "HARDWARE")}

    <h2 id="hardware-renders">Fabricated Hardware Renders</h2>
    <div class="render-grid">
      <figure class="render-figure">
        <img src="/docs/images/panel_front.png" alt="6 HP Matte Black and ENIG Gold Front Panel" />
        <figcaption>Matte Black + ENIG Front Panel</figcaption>
      </figure>
      <figure class="render-figure">
        <img src="/docs/images/pcb_front.png" alt="Main PCB Front Controls F.Cu" />
        <figcaption>Main PCB Front (F.Cu Controls)</figcaption>
      </figure>
      <figure class="render-figure">
        <img src="/docs/images/pcb_back.png" alt="Main PCB Rear 50 SMD PCBA B.Cu" />
        <figcaption>Main PCB Rear (B.Cu 50-SMD)</figcaption>
      </figure>
    </div>

    ${renderDivider(variant, "STAGES")}

    <h2 id="stage-guide">Stage-by-Stage Guide</h2>
    <div class="table-scroll">
      <table class="proto-table">
        <thead><tr><th>Stage</th><th>Section</th><th>Focus</th></tr></thead>
        <tbody>
          <tr><td><code>01</code></td><td>Hardware Build</td><td>9 core skills, Living Context Map &amp; <code>/agy-customizations</code></td></tr>
          <tr><td><code>02</code>–<code>04</code></td><td>Hardware Build</td><td>Sketch critique, <code>DesignSpec.md</code>, SKiDL &amp; 9-section schematic</td></tr>
          <tr><td><code>05</code></td><td>Hardware Build</td><td><a href="?variant=${variant}&page=stage5" data-nav-page="stage5">6 HP PCB, <code>silk_layout.json</code> &amp; <code>/edit-silkscreen</code></a></td></tr>
          <tr><td><code>06</code>–<code>07</code></td><td>Hardware Build</td><td>Mated 3U panel, VectorCraft SVG art, Gerbers &amp; 81 checklist cards</td></tr>
          <tr><td><code>08</code>–<code>09</code></td><td>Companion Site</td><td><code>/wayfinder</code> planning, Astro Core delivery &amp; Pages OIDC launch</td></tr>
        </tbody>
      </table>
    </div>

    <nav class="prev-next-nav" aria-label="Stage navigation">
      <a class="prev-next-card" href="?variant=${variant}&page=stage5" data-nav-page="stage5" style="text-align:end;">
        <span class="prev-next-kicker">Jump to Prototype Showcase · Stage 05 →</span>
        <span class="prev-next-title">6 HP Main PCB, silk_layout.json &amp; /edit-silkscreen</span>
      </a>
    </nav>
  `;
}

// ============================================================================
// THREE STRUCTURALLY DIFFERENT VARIANT SHELLS
// ============================================================================
function renderTocList(tocItems) {
  return tocItems
    .map((item) => `<a class="toc-link" data-depth="${item.depth}" href="#${item.id}">${item.label}</a>`)
    .join("");
}

function renderMobileToc(tocItems) {
  return `
    <details class="toc-mobile">
      <summary>On this page</summary>
      <div class="toc-list">${renderTocList(tocItems)}</div>
    </details>
  `;
}

function renderFooter() {
  return `
    <footer class="site-footer">
      <div class="site-footer-inner">
        <div>ENV / SKEW Build Tutorial · HAGIWO/ハギヲ No. 43 · Apache License 2.0</div>
        <div class="footer-links">
          <a href="https://domesticmouse.github.io/EnvelopeFollowerWithSkewLimiter/" target="_blank" rel="noopener noreferrer">Live Companion Site ↗</a>
          <a href="https://github.com/domesticmouse/EnvelopeFollower" target="_blank" rel="noopener noreferrer">Tutorial Repo ↗</a>
          <a href="https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter" target="_blank" rel="noopener noreferrer">Hardware Repo ↗</a>
        </div>
      </div>
    </footer>
  `;
}

function renderVariantA(articleHtml, tocItems) {
  const effective = getEffectiveScheme();
  const activeOrder = state.page === "overview" ? 0 : 5;
  const jumpLinks = [
    { label: "Overview", page: "overview", active: state.page === "overview" },
    { label: "Hardware", page: "stage5", active: state.page === "stage5" },
    { label: "Companion Site", page: "stage5", active: false },
    { label: "Appendix", page: "overview", active: false },
  ];

  return `
    <header class="a-header">
      <div class="a-header-inner">
        <div class="a-brand">
          <button type="button" class="menu-btn" data-open-drawer aria-label="Open navigation menu">☰ Menu</button>
          <span class="chamfer-focus-wrap">
            <a href="?variant=A&page=overview" data-nav-page="overview" class="slab-logo chamfer-sm">ENV / SKEW</a>
          </span>
          <span class="a-qualifier">BUILD TUTORIAL</span>
          ${HERO_ENVELOPE_SVG}
        </div>
        <nav class="a-nav desktop-jump-nav" aria-label="Primary">
          ${jumpLinks
            .map(
              (l) =>
                `<a href="?variant=A&page=${l.page}" data-nav-page="${l.page}" class="a-nav-link" ${
                  l.active ? 'aria-current="page"' : ""
                }>${l.label}</a>`
            )
            .join("")}
        </nav>
        <div class="a-actions">
          <button type="button" class="header-btn" data-open-search aria-label="Search tutorial">⌕ Search <kbd>⌘K</kbd></button>
          <button type="button" class="header-btn" data-toggle-2state aria-label="Toggle color theme">${
            effective === "dark" ? "☀ Light" : "☾ Dark"
          }</button>
          <a class="header-btn" href="https://domesticmouse.github.io/EnvelopeFollowerWithSkewLimiter/" target="_blank" rel="noopener noreferrer">Companion Site ↗</a>
          <a class="header-btn" href="https://github.com/domesticmouse/EnvelopeFollower" target="_blank" rel="noopener noreferrer">${GITHUB_ICON_SVG}<span>GitHub ↗</span></a>
        </div>
      </div>
    </header>

    <div class="a-shell">
      <aside class="a-rail left-rail" aria-label="Curriculum rail">
        ${CURRICULUM_GROUPS.map(
          (g) => `
          <div class="a-rail-group-title">${g.label}</div>
          <ul class="a-tp-list">
            ${g.items
              .map((item) => {
                const isCurrent = item.order === activeOrder;
                const completed = item.order > 0 && item.order < activeOrder;
                const targetPage = item.pageKey ?? (item.order === 0 ? "overview" : "stage5");
                return `
                  <li>
                    <a class="a-rail-link" href="?variant=A&page=${targetPage}" data-nav-page="${targetPage}" ${
                  isCurrent ? 'aria-current="page"' : ""
                } data-completed="${completed}">
                      <span class="a-badge">${item.badge}</span>
                      <span>${item.navTitle}</span>
                    </a>
                  </li>`;
              })
              .join("")}
          </ul>`
        ).join("")}
      </aside>

      <main id="main-content" class="proto-article">
        ${renderMobileToc(tocItems)}
        ${articleHtml}
      </main>

      <aside class="a-toc right-toc" aria-label="On this page">
        <div class="a-toc-title">On This Page</div>
        <div class="toc-list">${renderTocList(tocItems)}</div>
      </aside>
    </div>
    ${renderFooter()}
  `;
}

function renderVariantB(articleHtml, tocItems) {
  const effective = getEffectiveScheme();
  const activeOrder = state.page === "overview" ? 0 : 5;
  const activeSection = state.page === "overview" ? "overview" : "hardware";

  return `
    <header class="b-header">
      <div class="b-header-inner">
        <a class="b-brand" href="?variant=B&page=overview" data-nav-page="overview">
          ${ENV_SKEW_SLAB_SVG}
          <span class="b-subtitle">Build Tutorial</span>
        </a>
        <nav class="b-nav desktop-jump-nav" aria-label="Primary">
          <a class="b-nav-link" href="?variant=B&page=overview" data-nav-page="overview" ${
            state.page === "overview" ? 'aria-current="page"' : ""
          }>Overview</a>
          <a class="b-nav-link" href="?variant=B&page=stage5" data-nav-page="stage5" ${
            state.page === "stage5" ? 'aria-current="page"' : ""
          }>Hardware</a>
          <a class="b-nav-link" href="?variant=B&page=stage5" data-nav-page="stage5">Companion Site</a>
          <a class="b-nav-link" href="?variant=B&page=overview" data-nav-page="overview">Appendix</a>
        </nav>
        <div class="b-actions">
          <button type="button" class="menu-btn" data-open-drawer aria-label="Open navigation menu">☰ Menu</button>
          <button type="button" class="b-action-btn" data-open-search>⌕ Search <kbd>⌘K</kbd></button>
          <a class="b-action-btn" href="https://domesticmouse.github.io/EnvelopeFollowerWithSkewLimiter/" target="_blank" rel="noopener noreferrer">Companion Site ↗</a>
          <a class="b-action-btn" href="https://github.com/domesticmouse/EnvelopeFollower" target="_blank" rel="noopener noreferrer">${GITHUB_ICON_SVG}</a>
        </div>
      </div>
    </header>

    <div class="b-shell">
      <aside class="b-rail left-rail" aria-label="Curriculum rail">
        ${CURRICULUM_GROUPS.map(
          (g) => `
          <div class="b-rail-section" data-active-section="${g.id === activeSection}">
            <div class="b-rail-heading">${g.label}</div>
            <ul class="b-rail-list">
              ${g.items
                .map((item) => {
                  const isCurrent = item.order === activeOrder;
                  const targetPage = item.pageKey ?? (item.order === 0 ? "overview" : "stage5");
                  return `
                    <li>
                      <a class="b-rail-link" href="?variant=B&page=${targetPage}" data-nav-page="${targetPage}" ${
                    isCurrent ? 'aria-current="page"' : ""
                  }>
                        <span class="b-rail-num">${item.badge}</span>
                        <span>${item.navTitle}</span>
                      </a>
                    </li>`;
                })
                .join("")}
            </ul>
          </div>`
        ).join("")}
        <div class="b-rail-footer">
          <button type="button" class="b-theme-btn" data-toggle-2state>
            <span>Appearance</span>
            <span>${effective === "dark" ? "Dark Studio ☾" : "Warm Paper ☀"}</span>
          </button>
        </div>
      </aside>

      <main id="main-content" class="proto-article">
        ${renderMobileToc(tocItems)}
        ${articleHtml}
      </main>

      <aside class="b-toc right-toc" aria-label="On this page">
        <div class="b-rail-heading">On this page</div>
        <div class="toc-list">${renderTocList(tocItems)}</div>
      </aside>
    </div>
    ${renderFooter()}
  `;
}

function renderVariantC(articleHtml, tocItems) {
  const activeOrder = state.page === "overview" ? 0 : 5;
  const metaContent = document.querySelector('meta[name="color-scheme"]')?.getAttribute("content");
  const tristateMode =
    state.storedScheme ?? (metaContent === "dark" || metaContent === "light" ? metaContent : "system");
  const sysLabel = getSystemScheme();

  return `
    <div class="c-telemetry">
      <div class="c-telemetry-inner">
        <span>DM // R1.0 · BUILD TUTORIAL WORKBENCH</span>
        <div style="display:flex;align-items:center;gap:0.85rem;">
          <a href="https://domesticmouse.github.io/EnvelopeFollowerWithSkewLimiter/" target="_blank" rel="noopener noreferrer">Companion Site ↗</a>
          <a href="https://github.com/domesticmouse/EnvelopeFollower" target="_blank" rel="noopener noreferrer">GitHub ↗</a>
          <div class="c-tristate" role="group" aria-label="Color theme mode">
            <button type="button" class="c-tristate-btn" data-set-3state="system" aria-pressed="${tristateMode === "system"}">SYS (${sysLabel})</button>
            <button type="button" class="c-tristate-btn" data-set-3state="dark" aria-pressed="${tristateMode === "dark"}">DARK</button>
            <button type="button" class="c-tristate-btn" data-set-3state="light" aria-pressed="${tristateMode === "light"}">LIGHT</button>
          </div>
        </div>
      </div>
    </div>

    <header class="c-header">
      <div class="c-header-inner">
        <a class="c-brand" href="?variant=C&page=overview" data-nav-page="overview">
          ${HERO_ENVELOPE_SVG}
          <span class="c-brand-name">ENV / SKEW</span>
        </a>
        <nav class="c-nav desktop-jump-nav" aria-label="Primary">
          <a class="c-nav-link" href="?variant=C&page=overview" data-nav-page="overview" ${
            state.page === "overview" ? 'aria-current="page"' : ""
          }>${state.page === "overview" ? LED_OCTAGON_SVG : ""}<span>00 OVERVIEW</span></a>
          <a class="c-nav-link" href="?variant=C&page=stage5" data-nav-page="stage5" ${
            state.page === "stage5" ? 'aria-current="page"' : ""
          }>${state.page === "stage5" ? LED_OCTAGON_SVG : ""}<span>01–07 HARDWARE</span></a>
          <a class="c-nav-link" href="?variant=C&page=stage5" data-nav-page="stage5"><span>08–09 SITE</span></a>
          <a class="c-nav-link" href="?variant=C&page=overview" data-nav-page="overview"><span>APPENDIX</span></a>
        </nav>
        <div style="display:flex;gap:0.45rem;">
          <button type="button" class="menu-btn" data-open-drawer aria-label="Open navigation menu">☰ Rack</button>
          <button type="button" class="c-nav-link" style="cursor:pointer;" data-open-search>⌕ SEARCH <kbd>⌘K</kbd></button>
        </div>
      </div>
    </header>

    <div class="c-shell">
      <aside class="c-rail left-rail" aria-label="Modular curriculum rack">
        <div class="c-progress-module">
          <span>PROGRESS · STAGE ${state.page === "overview" ? "00" : "05"} / 09</span>
          ${GAIN_BARS_SVG}
        </div>
        ${CURRICULUM_GROUPS.map(
          (g) => `
          <details class="c-rack-module" open>
            <summary>${g.label}</summary>
            <ul class="c-rack-list">
              ${g.items
                .map((item) => {
                  const isCurrent = item.order === activeOrder;
                  const targetPage = item.pageKey ?? (item.order === 0 ? "overview" : "stage5");
                  return `
                    <li>
                      <a class="c-rack-link" href="?variant=C&page=${targetPage}" data-nav-page="${targetPage}" ${
                    isCurrent ? 'aria-current="page"' : ""
                  }>
                        ${isCurrent ? NORMAL_ARROW_SVG : `<span class="mono" style="font-size:0.7rem;color:var(--ink-muted);">${item.badge}</span>`}
                        <span>${item.navTitle}</span>
                      </a>
                    </li>`;
                })
                .join("")}
            </ul>
          </details>`
        ).join("")}
      </aside>

      <main id="main-content" class="proto-article">
        ${renderMobileToc(tocItems)}
        ${articleHtml}
      </main>

      <aside class="c-toc right-toc" aria-label="On this page">
        <div class="mono" style="font-size:0.7rem;font-weight:700;color:var(--accent-gold-link);margin-block-end:0.4rem;">SIGNAL OUTLINE</div>
        <div class="toc-list">${renderTocList(tocItems)}</div>
      </aside>
    </div>
    ${renderFooter()}
  `;
}

// ============================================================================
// FLOATING PROTOTYPE SWITCHER & SEARCH/DRAWER DIALOGS
// ============================================================================
function renderSwitcher() {
  const el = document.getElementById("prototype-switcher");
  const meta = VARIANT_META[state.variant];
  const effective = getEffectiveScheme();
  const metaContent = document.querySelector('meta[name="color-scheme"]')?.getAttribute("content");
  const modeDisplay = metaContent === "light dark" ? `auto:${effective}` : effective;

  el.innerHTML = `
    <button type="button" class="proto-btn" data-cycle-variant="-1" aria-label="Previous variant">←</button>
    <span class="proto-label">${meta.key} (${meta.name})</span>
    <button type="button" class="proto-btn" data-cycle-variant="1" aria-label="Next variant">→</button>
    <span class="proto-divider" aria-hidden="true"></span>
    <button type="button" class="proto-btn" data-switch-page="stage5" aria-pressed="${state.page === "stage5"}">Stage 5</button>
    <button type="button" class="proto-btn" data-switch-page="overview" aria-pressed="${state.page === "overview"}">Overview</button>
    <span class="proto-state-pill">Scheme: ${modeDisplay} · Page: ${state.page}</span>
  `;
}

function renderDrawerLinks() {
  const list = document.getElementById("mobile-nav-list");
  const activeOrder = state.page === "overview" ? 0 : 5;
  list.innerHTML = CURRICULUM_GROUPS.flatMap((g) => g.items)
    .map((item) => {
      const targetPage = item.pageKey ?? (item.order === 0 ? "overview" : "stage5");
      const current = item.order === activeOrder ? 'aria-current="page"' : "";
      return `<li><button type="button" class="nav-drawer-link" data-drawer-page="${targetPage}" ${current}><span>${item.navTitle}</span><span class="mono" style="font-size:0.72rem;color:var(--accent-gold-link);">${item.badge}</span></button></li>`;
    })
    .join("");
}

function appendHighlightedExcerpt(container, text, query) {
  container.textContent = "";
  if (!query) {
    container.textContent = text;
    return;
  }
  const lowerText = text.toLowerCase();
  const lowerQuery = query.toLowerCase();
  let cursor = 0;
  let idx = lowerText.indexOf(lowerQuery);
  while (idx !== -1) {
    if (idx > cursor) {
      container.appendChild(document.createTextNode(text.slice(cursor, idx)));
    }
    const mark = document.createElement("mark");
    mark.textContent = text.slice(idx, idx + query.length);
    container.appendChild(mark);
    cursor = idx + query.length;
    idx = lowerText.indexOf(lowerQuery, cursor);
  }
  if (cursor < text.length) {
    container.appendChild(document.createTextNode(text.slice(cursor)));
  }
}

function renderSearchResults(query) {
  const resultsEl = document.getElementById("search-results");
  const statusEl = document.getElementById("search-status");
  const q = query.trim();
  const matches = q
    ? SEARCH_CORPUS.filter(
        (item) =>
          item.title.toLowerCase().includes(q.toLowerCase()) ||
          item.text.toLowerCase().includes(q.toLowerCase()) ||
          item.section.toLowerCase().includes(q.toLowerCase())
      )
    : SEARCH_CORPUS.slice(0, 5);

  statusEl.textContent = q
    ? `${matches.length} result${matches.length === 1 ? "" : "s"} for "${q}"`
    : "Showing 5 of 13 tutorial pages (type SKiDL, silk_layout.json, /wayfinder, TP7)…";

  state.activeSearchIndex = 0;
  resultsEl.textContent = "";

  matches.forEach((item, idx) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "search-result-btn";
    btn.setAttribute("role", "option");
    btn.setAttribute("aria-selected", idx === 0 ? "true" : "false");
    btn.dataset.pageKey = item.pageKey;

    const top = document.createElement("div");
    top.className = "search-result-top";
    const badge = document.createElement("span");
    badge.className = "search-section-badge";
    badge.textContent = item.section;
    const title = document.createElement("span");
    title.className = "search-result-title";
    title.textContent = item.title;
    top.append(badge, title);

    const excerpt = document.createElement("div");
    excerpt.className = "search-result-excerpt";
    appendHighlightedExcerpt(excerpt, item.text, q);

    btn.append(top, excerpt);
    btn.addEventListener("click", () => {
      state.page = item.pageKey;
      syncUrlParams();
      document.getElementById("site-search-dialog").close();
      renderApp();
    });

    li.appendChild(btn);
    resultsEl.appendChild(li);
  });
}

// ============================================================================
// DIALOGS, SCROLL-SPY & MAIN RENDER
// ============================================================================
let tocObserver = null;

function setupScrollSpy() {
  if (tocObserver) tocObserver.disconnect();
  const links = Array.from(document.querySelectorAll(".toc-link"));
  const headings = Array.from(document.querySelectorAll(".proto-article h2[id], .proto-article h3[id]"));
  if (!links.length || !headings.length) return;

  tocObserver = new IntersectionObserver(
    (entries) => {
      const visible = entries.find((e) => e.isIntersecting);
      if (!visible) return;
      links.forEach((l) => {
        l.classList.toggle("is-active", l.getAttribute("href") === `#${visible.target.id}`);
      });
    },
    { rootMargin: "-20% 0px -65% 0px" }
  );
  headings.forEach((h) => tocObserver.observe(h));
}

function addClosedByFallback(dialog) {
  if ("closedBy" in HTMLDialogElement.prototype) return;
  dialog.addEventListener("click", (event) => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    const inside =
      rect.top <= event.clientY &&
      event.clientY <= rect.top + rect.height &&
      rect.left <= event.clientX &&
      event.clientX <= rect.left + rect.width;
    if (!inside) dialog.close();
  });
}

function renderApp() {
  const root = document.getElementById("app");
  root.dataset.variant = state.variant;
  root.className = "proto-fade-in";

  const articleHtml =
    state.page === "overview" ? renderOverviewArticle(state.variant) : renderStage5Article(state.variant);
  const tocItems = state.page === "overview" ? OVERVIEW_TOC : STAGE5_TOC;

  if (state.variant === "A") root.innerHTML = renderVariantA(articleHtml, tocItems);
  else if (state.variant === "B") root.innerHTML = renderVariantB(articleHtml, tocItems);
  else root.innerHTML = renderVariantC(articleHtml, tocItems);

  renderSwitcher();
  renderDrawerLinks();
  setupScrollSpy();
}

function cycleVariant(delta) {
  const order = ["A", "B", "C"];
  const idx = order.indexOf(state.variant);
  state.variant = order[(idx + delta + order.length) % order.length];
  syncUrlParams();
  renderApp();
}

function bindGlobalEvents() {
  const searchDialog = document.getElementById("site-search-dialog");
  const searchInput = document.getElementById("site-search-input");
  const drawerDialog = document.getElementById("mobile-nav-drawer");

  addClosedByFallback(searchDialog);
  addClosedByFallback(drawerDialog);

  function openSearch() {
    renderSearchResults(searchInput.value);
    searchDialog.showModal();
    searchInput.focus();
  }

  document.addEventListener("click", (event) => {
    const cycleBtn = event.target.closest("[data-cycle-variant]");
    if (cycleBtn) {
      cycleVariant(Number(cycleBtn.dataset.cycleVariant));
      return;
    }
    const pageBtn = event.target.closest("[data-switch-page]");
    if (pageBtn) {
      state.page = pageBtn.dataset.switchPage;
      syncUrlParams();
      renderApp();
      window.scrollTo({ top: 0 });
      return;
    }
    const navLink = event.target.closest("[data-nav-page]");
    if (navLink) {
      event.preventDefault();
      state.page = navLink.dataset.navPage;
      syncUrlParams();
      renderApp();
      window.scrollTo({ top: 0 });
      return;
    }
    const drawerBtn = event.target.closest("[data-drawer-page]");
    if (drawerBtn) {
      state.page = drawerBtn.dataset.drawerPage;
      syncUrlParams();
      drawerDialog.close();
      renderApp();
      window.scrollTo({ top: 0 });
      return;
    }
    if (event.target.closest("[data-open-search]")) {
      openSearch();
      return;
    }
    if (event.target.closest("[data-open-drawer]")) {
      drawerDialog.showModal();
      return;
    }
    if (event.target.closest("[data-toggle-2state]")) {
      toggleTwoStateScheme();
      return;
    }
    const threeBtn = event.target.closest("[data-set-3state]");
    if (threeBtn) {
      setThreeStateScheme(threeBtn.dataset.set3state);
    }
  });

  document.getElementById("search-close-btn").addEventListener("click", () => searchDialog.close());
  document.getElementById("drawer-close-btn").addEventListener("click", () => drawerDialog.close());

  let debounceId = null;
  searchInput.addEventListener("input", () => {
    clearTimeout(debounceId);
    debounceId = setTimeout(() => renderSearchResults(searchInput.value), 120);
  });

  searchInput.addEventListener("keydown", (event) => {
    const options = Array.from(document.querySelectorAll("#search-results .search-result-btn"));
    if (!options.length) return;
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const delta = event.key === "ArrowDown" ? 1 : -1;
      state.activeSearchIndex = (state.activeSearchIndex + delta + options.length) % options.length;
      options.forEach((opt, i) => opt.setAttribute("aria-selected", i === state.activeSearchIndex ? "true" : "false"));
    } else if (event.key === "Enter") {
      event.preventDefault();
      options[state.activeSearchIndex]?.click();
    }
  });

  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      openSearch();
      return;
    }
    const tag = event.target.tagName;
    const isEditable = tag === "INPUT" || tag === "TEXTAREA" || event.target.isContentEditable;
    if (isEditable || searchDialog.open || drawerDialog.open) return;

    if (event.key === "/") {
      event.preventDefault();
      openSearch();
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      cycleVariant(-1);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      cycleVariant(1);
    }
  });

  window.addEventListener("storage", (event) => {
    if (event.key === STORAGE_KEY) {
      applyColorScheme(readStoredScheme());
      renderApp();
    }
  });

  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if (!state.storedScheme) {
      renderSwitcher();
    }
  });
}

readParamsFromUrl();
syncUrlParams();
initCopyListeners();
bindGlobalEvents();
renderApp();
