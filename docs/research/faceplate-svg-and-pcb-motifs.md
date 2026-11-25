# Research: ENV / SKEW Faceplate SVG Motifs, PCB Trace Geometry, and `reference/site/` Design Tokens

- **Ticket:** [`domesticmouse/EnvelopeFollower#29`](https://github.com/domesticmouse/EnvelopeFollower/issues/29) (`wayfinder:research`)
- **Reference Pin Audited:** `domesticmouse/EnvelopeFollowerWithSkewLimiter` @ [`8ad81d0`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/8ad81d0) (in `/Users/brett/Documents/GitHub/EnvelopeFollower/reference/`)
- **Primary Sources Verified:**
  - Faceplate SVGs & generator: `reference/panel_art/front_soldermask.svg`, `reference/panel_art/front_silkscreen.svg`, `reference/panel_art/generate_panel_art.py`, `reference/panel_svg_spec.md`
  - Reference Astro components & tests: `reference/site/src/lib/panel-svg-shared.ts`, `reference/site/src/lib/panel-svg.ts`, `reference/site/src/lib/panel-layers-inline.ts`, `reference/site/src/lib/panel-keepouts.ts`, `reference/site/src/components/FaceplateIllustration.astro`, `reference/site/src/components/panel-layer-inspector.ts`, `reference/site/src/components/env-skew-panel.ts`, `reference/site/tests/panel-svg.test.ts`, `reference/site/tests/env-skew-panel.test.ts`, `reference/site/tests/panel-layer-inspector.test.ts`
  - Main PCB layout: `reference/envelope_follower.kicad_pcb`
  - Reference site & tutorial styles: `reference/site/src/styles/{tokens,fonts,global,docs,hardware,build,patches,curated}.css`, `reference/site/src/pages/index.astro`, `reference/LICENSE`, `reference/README.md`, `docs/stylesheets/extra.css`, `docs/stylesheets/fonts.css`, `docs/assets/fonts/`

---

## Executive Summary

1. **Both front-panel SVGs are clean, self-contained, 1:1 mm paths-only assets under Apache-2.0 (`~42 KB` combined):** `front_soldermask.svg` (`7,240` bytes, `33` vector shapes inside `_01_F_Mask_Gold`) and `front_silkscreen.svg` (`35,314` bytes, `102` vector shapes inside `_02_F_SilkS_White`) share `viewBox="0 0 30.00 128.50"` (`1 SVG user unit = 1.00 mm`), contain zero live `<text>` nodes, zero `stroke` attributes, and zero `transform` attributes, and separate cleanly from their `0.05 mm` `_03_Registration_Frame`. Every ENIG gold sculptural motif (hero envelope, kick-drum decay bars, chamfered `ENV / SKEW` slab, progressive gain bars, rising/falling slew steps, `[+]`/`[-]` offset blocks, octagonal LED bezel, normaling arrow, chamfered output bay) is a discrete top-level `<polygon>`, `<rect>`, or `<path>` element that can be extracted individually or rendered as a full layer.
2. **The main PCB (`envelope_follower.kicad_pcb`) uses pure `45°` octilinear routing with zero copper arcs and zero teardrops:** Across `703` copper segments (`515` on `B.Cu`, `188` on `F.Cu`) on a `30.00 × 108.00 mm` 2-layer board, `638` (`90.8%`) lie on exact `0° / 45° / 90° / 135°` headings (`0` curved traces, `(legacy_teardrops no)`), paired with `133` uniform `0.60 mm / 0.30 mm` vias (`0.15 mm` annular ring) and a vertical left-edge signal-flow test-point rail (`TP4`–`TP11` at `X = 103.2 mm`, `6.0–6.5 mm` pitch: `PRE → HWR → RECT → DRV → ENV → OFF → INV → OUT`). These translate naturally into low-clutter hairline stage rails, `45°` chamfered badges, and `TP`-style step markers.
3. **`reference/site/` locks a dark-only studio system with 4 font families, whereas `docs/stylesheets/extra.css` adds a warm-studio light mode and omits `Barlow Condensed`:** Both share the core Matte Black + ENIG Gold + Silkscreen White palette (`#141518` canvas, `#1b1d22` surface, `#090a0d` code well, `#e8eaef` primary ink `15.17:1` AAA, `#f4f5f7` silk ink `16.74:1` AAA, `#d8b154` gold `8.99:1` AAA), while `docs/stylesheets/extra.css` also provides a WCAG-AA/AAA warm-paper light mode (`#fbfaf7` canvas, `#7a5608` links `6.36:1`, `#94680a` accent `4.74:1`). Adopting `reference/`'s `.chamfer-sm` geometry, `Barlow Condensed` slab accents, and PCB/faceplate SVG motifs in the Astro Build Tutorial requires preserving dual-scheme token parity, `prefers-reduced-motion` guards, and `@media (forced-colors: active)` fallbacks.

---

## 1. ENV / SKEW Faceplate SVG Motifs (`reference/panel_art/`)

### 1.1 Coordinate System, `viewBox`, Dimensions & Licensing

- **Canvas & `viewBox` (`reference/panel_svg_spec.md:15-26`, `front_soldermask.svg:2`, `front_silkscreen.svg:2`):**
  - `width="30.00mm" height="128.50mm" viewBox="0 0 30.00 128.50"` (`6 HP × 3U` Eurorack, `30 : 128.5` aspect ratio).
  - Origin `(0, 0)` is top-left, `+X` right, `+Y` down, `1 SVG unit = 1.00 mm`.
  - Maps to KiCad global `(100.00, 29.75)..(130.00, 158.25) mm`, mating centered vertically over the `30.00 × 108.00 mm` main PCB (`10.25 mm` top/bottom rail overhang).
  - Safe artwork bounds: `X = 0.50..29.50 mm`, `Y = 0.50..128.00 mm`; Eurorack rail/washer keepouts: `Y = 0.00..6.50 mm` and `122.00..128.50 mm`.
- **File Sizes, Structure & Serialization (`panel_art/generate_panel_art.py:1196-1311`):**

| File | Size | Lines | Root `<g>` Layers | Primitive Counts | Fab Fill Hex | UI Recolor Hex |
| :--- | :---: | :---: | :--- | :--- | :---: | :---: |
| `front_soldermask.svg` | `7,240 B` | `43` | `Layer_1` (empty), `_01_F_Mask_Gold`, `_03_Registration_Frame` | `11` `<polygon>`, `17` `<rect>`, `6` `<path>` (`1` in reg frame) | `#C89B3C` | `#D8B154` |
| `front_silkscreen.svg` | `35,314 B` | `136` | `Layer_1` (empty), `_02_F_SilkS_White`, `_03_Registration_Frame` | `22` `<rect>`, `22` `<path>` (`1` in reg frame), `59` `<polygon>`, `12` glyph `<g>` | `#000000` | `#F4F5F7` |

- **Licensing & Font Provenance:**
  - `reference/LICENSE` (`1–201`) and `reference/README.md:122`: **Apache License 2.0** (`domesticmouse/EnvelopeFollowerWithSkewLimiter`).
  - All typography in `front_soldermask.svg` and `front_silkscreen.svg` is **pre-outlined to vector paths** via `type.createOutlines` (`generate_panel_art.py:268-296, 1287-1288`), so rendering the SVGs requires **zero font files** (`DIN Condensed Bold`, `DIN Alternate Bold`, and `Menlo Bold` are baked into `<path>` / `<polygon>` outlines).
- **Clean Extractability (`reference/site/src/lib/panel-svg-shared.ts:89-168`, `panel-svg.ts:12-29`, `panel-layers-inline.ts:1-16`):**
  - `reference/site/` already implements a zero-fetch, pure-string extractor (`parseFaceplateLayersFromStrings`) tested in `tests/panel-svg.test.ts:55-68`:
    1. Extracts `<g id="_01_F_Mask_Gold">` and `<g id="_02_F_SilkS_White">` via balanced `<g>` depth tracking (`extractGroupById`).
    2. Drops `<g id="_03_Registration_Frame">` for standard illustration (`FaceplateIllustration.astro:89-90`, `env-skew-panel.ts:310-327`), or recolors it `#4ADE80` for the layer inspector (`panel-layer-inspector.ts:104`).
    3. Recolors `fill` / `stroke` from fabrication `#C89B3C` → `#D8B154` (ENIG Gold UI) and `#000000` → `#F4F5F7` (Silkscreen White UI).
    4. Tags the normaling arrow `<polygon points="13.45,95.47..."` with `data-normal-arrow="true"` for interactive state dimming.
  - Because `front_soldermask.svg` has **no nested groups inside `_01_F_Mask_Gold`** (each motif is an ungrouped sibling on lines `6–38`), individual motifs (e.g., hero waveform, gain bars, slew steps, `ENV / SKEW` slab, normaling arrow) can be sliced out by line/element index or reused via `<svg viewBox="...">` cropping.

### 1.2 Exact Catalog of Faceplate SVG Motifs

#### A. ENIG Gold Solder-Mask Layer (`_01_F_Mask_Gold` in `front_soldermask.svg`)

| Motif | Source Lines (`front_soldermask.svg` / `generate_panel_art.py`) | Exact `mm` Bounds / Geometry | UI Reuse Potential |
| :--- | :--- | :--- | :--- |
| **Hero Angular Envelope + 6 Decay Bars** | `front_soldermask.svg:6-12` / `generate_panel_art.py:430-458` | Envelope polygon `X=13.90..28.50, Y=1.35..5.70` (steep rise `15.20→16.85`, plateau `16.85..18.45`, sloped decay `18.45→24.15`, `0.80 mm` stroke body); `6` `1.30 mm`-wide bars underneath at `X=17.65, 19.56, 21.47, 23.38, 25.29, 27.20` (`h=2.69, 1.95, 1.22, 0.85, 0.85, 0.85 mm`, `Y_bottom=5.70`). | **High:** Clean `14.6 × 4.35 mm` brand mark / hero emblem / section header glyph (crop `viewBox="13.5 1.0 15.5 5.0"`). |
| **Chamfered `ENV / SKEW` Title Slab** | `front_soldermask.svg:13` / `generate_panel_art.py:460-478` | Compound `<path>`: `27.60 × 4.60 mm` (`X=1.20..28.80, Y=6.80..11.40`), `1.10 mm` `45°` chamfers at top-right & bottom-left, knocked-out `"ENV / SKEW"` (`DIN Condensed Bold`, `4.55 mm`, `tracking=65`). | **High:** Exact inspiration for `.slab-logo` & `.chamfer-sm` badges; usable directly as SVG wordmark (`viewBox="1.0 6.6 28.0 5.0"`). |
| **Segmented Side Edge Rails (4 pairs)** | `front_soldermask.svg:14-21` / `generate_panel_art.py:480-489` | `0.42 mm` wide vertical bars at `X=0.85` & `28.73`, 4 segments (`Y=13.60..28.40`, `29.10..43.90`, `44.60..59.40`, `60.10..73.60`, `0.70 mm` gaps aligned to pot rows). | **High:** Left/right tutorial stage rail or card accent motif representing discrete processing stages. |
| **Progressive Brutalist Gain Bars (`RV1`)** | `front_soldermask.svg:22-25` / `generate_panel_art.py:491-502` | `4` ascending bars (`X=23.90..27.94, Y=16.80..25.70`), `w=0.68 mm`, `gap=0.44 mm`, `h=[2.40, 4.40, 6.60, 8.90] mm`, each top-right chamfered `0.25 mm`. | **Medium-High:** Stage-progress meter / difficulty or gain indicator icon. |
| **Rising Slew Step `_/‾` (`RV2 ATK`)** | `front_soldermask.svg:26` / `generate_panel_art.py:504-517` | `8`-vertex polygon (`X=23.90..28.00, Y=32.35..41.15`), `0.80–0.90 mm` stroke thickness, `1.90 mm` horizontal run over `8.00 mm` rise (`~76.6°` slope). | **High:** Attack / rise-stage icon in tutorial stage headers or callouts. |
| **Falling Slew Step `‾\_` (`RV3 REL`)** | `front_soldermask.svg:27` / `generate_panel_art.py:519-532` | `8`-vertex mirrored polygon (`X=23.90..28.00, Y=47.85..56.65`), `0.90 mm` thickness. | **High:** Release / decay-stage icon paired with rising slew step. |
| **Offset Zero-Datum + Chamfered `[+]` / `[-]`** | `front_soldermask.svg:28-30` / `generate_panel_art.py:534-551` | `4.10 × 0.44 mm` datum bar at `Y=66.43`, flanked by `2.90 × 2.40 mm` chamfered blocks (`tr=0.35, bl=0.35` / `tl=0.35, br=0.35`) with knocked-out `+` and `−`. | **Medium:** Bipolar DC-offset / polarity visual cue in tutorial diagrams. |
| **Max-Drive Wedge (`RV1`) & Center-Detent Chevron (`RV4`)** | `front_soldermask.svg:31-32` / `generate_panel_art.py:553-587` | Wedge at `+150°` (`r=6.45..8.20 mm`, half-width `0.20→0.44 mm`); inverted triangle at `12 o'clock` (`14.30..15.70, Y=60.05..61.20`). | **Low-Medium:** Specific to rotary dial overlays. |
| **Octagonal LED Bezel (`LED1`)** | `front_soldermask.svg:33` / `generate_panel_art.py:589-600` | Regular octagon centered at `(15.00, 82.25)`, `R_mid=2.82 mm`, `stroke=0.52 mm`, `rot=22.5°` (flat top/bottom/sides). | **Medium-High:** Framing ring for status indicators / step numbers. |
| **Patchbay Gold Bus Bar** | `front_soldermask.svg:34` / `generate_panel_art.py:602-603` | `27.60 × 0.55 mm` solid horizontal bar (`X=1.20..28.80, Y=89.65`). | **High:** Section divider motif (`2px` ENIG Gold rule). |
| **Normaling Arrow (`J1 → J2`)** | `front_soldermask.svg:35` / `generate_panel_art.py:605-619` | `7`-vertex right-pointing arrow (`X=13.45..16.55, Y=94.85..96.65`, shaft `0.56 mm`, head `1.80 mm` tall); tagged `data-normal-arrow="true"` by `panel-svg-shared.ts:134-139`. | **High:** Signal-flow / normaling transition arrow between linked steps. |
| **Chamfered Output Bay Frame + Spine** | `front_soldermask.svg:36-37` / `generate_panel_art.py:621-633` | `27.70 × 16.00 mm` hollow frame (`X=1.15..28.85, Y=104.25..120.25`), `1.20 mm` `45°` corner chamfers, `0.50 mm` border, plus `0.50 × 8.90 mm` center divider at `X=14.75, Y=106.30`. | **High:** Two-column card/output frame pattern (mirrored in CSS `clip-path`). |
| **Bottom-Right Registration Badge** | `front_soldermask.svg:38` / `generate_panel_art.py:635-639` | `1.60 × 1.60 mm` square (`X=16.40..18.00, Y=124.70..126.30`) with `tr=0.45, bl=0.45` chamfers. | **Medium:** Tiny bullet / kicker square (`▪`) for metadata headers. |

#### B. White Silkscreen Layer (`_02_F_SilkS_White` in `front_silkscreen.svg`) & Synthesized Controls

- **Hairline Rules & Framing Wings (`front_silkscreen.svg:6, 76-77`):**
  - Sub-header rule: `26.80 × 0.24 mm` at `X=1.60, Y=12.03` (separates `ENV / SKEW` gold slab from `GAIN`).
  - Mode-row framing wings: `6.25 × 0.22 mm` left (`X=1.85`) and right (`X=21.90`) at `Y=74.64`, flanking the `RV4` knob clearance gap.
- **`300°` 11-Tick Rotary Dials (`front_silkscreen.svg:13-72`, `generate_panel_art.py:650-696`):**
  - `11` radial ticks from `-150°` to `+150°` at `30°` increments around `(15.00, py)` for `RV1`–`RV4`.
  - Major ticks (`-150°, -90°, 0°, 90°, 150°`): `0.28 mm` wide, `r=6.40..8.00 mm` (`7.60 mm` at `0°`); minor ticks (`±120°, ±60°, ±30°`): `0.20 mm` wide, `r=6.50..7.60 mm`.
  - `RV4` adds geometric `−` (`4.65, 71.93, 1.50×0.34 mm`) and `+` (`23.85, 71.93, 1.50×0.34 mm` + `24.43, 71.35, 0.34×1.50 mm`) polarity glyphs (`front_silkscreen.svg:73-75`).
- **Inverted Knockout Output Pills (`front_silkscreen.svg:120-121`, `generate_panel_art.py:795-831`):**
  - Left `OUT` pill (`X=2.30..13.70, Y=116.30..119.10`, `tr=0.45, bl=0.45`) and right `INV OUT` pill (`X=16.30..27.70, Y=116.30..119.10`, `tl=0.45, br=0.45`), inverting text as knockouts.
- **Typography & Maker Mark (`front_silkscreen.svg:7-119, 122-131`):**
  - Outlined text blocks (`GAIN`, `ATK`, `REL`, `OFFSET`, `SMOOTH`, `RAW`, `+ / −`, `SLOW`, `FAST`, `IN`, `SLEW IN`, and right-aligned `DM // R1.0` at `X=28.40, Y=126.08` in `Menlo Bold` `1.52 mm`).
- **Registration Frame (`_03_Registration_Frame`, `front_soldermask.svg:40-42`, `front_silkscreen.svg:133-135`):**
  - Outer `0.05 mm` hollow frame spanning `0..30.00 × 0..128.50 mm`. Must be stripped for decorative/faceplate rendering (`panel-svg.test.ts:62,67`) or explicitly toggled for engineering inspection (`panel-layer-inspector.ts:104`).
- **Synthesized Hardware Controls (`FaceplateIllustration.astro:35-217`, `env-skew-panel.ts:232-598`):**
  - The SVGs in `panel_art/` intentionally omit physical hardware silhouettes (drills are open). `reference/site/` layers crisp SVG controls on top using `PANEL_CONTROL_COORDS`:
    - **Knobs (`RV1`–`RV4`):** `r=4.75 mm` dark bezel (`#0B0C0F`, stroke `#3A3F4D`), `r=4.35 mm` radial-gradient cap (`#2E3340 → #191B22 → #101115`), rotating `#F4F5F7` pointer (`stroke-width="0.95"`, `tickToDeg(tick) = -150 + tick * 30`), and optional `r=5.65 mm` `#E2BE66` sweep arc (`describeSweepArc`).
    - **Toggle Switches (`SW1`, `SW2`):** `r=2.55 mm` metallic nut, `r=1.20 mm` bore, `1.30 mm` `#E2BE66` bat lever (`y ± 2.55 mm`) with `r=0.85 mm` `#F4F5F7` tip.
    - **Bi-Color LED (`LED1`):** `r=1.95 mm` bezel, `r=1.55 mm` dome (`#4ADE80` / `#F87171` / `#FBBF24` / `#1B1E25`), `r=4.60 mm` radial glow halo, `r=0.42 mm` specular glint.
    - **3.5 mm Jacks (`J1`–`J4`):** `r=3.10 mm` metallic nut, `r=2.35 mm` washer (`#1E222B`), `r=1.55 mm` bore (`#07080A`), optional `r=3.90 mm` active/dashed collar (`#E2BE66` / `#D8B154`) and `r=1.65 mm` gold plug.

---

## 2. Representative PCB Trace Geometry (`reference/envelope_follower.kicad_pcb`)

### 2.1 Board Envelope, Copper Layers & Routing Grammar

Parsed directly from `reference/envelope_follower.kicad_pcb` (`1,254,472` bytes, `39,071` lines, KiCad `10.0` format `(version 20260206)`):

- **Board Outline (`Edge.Cuts`):** Single `gr_rect` from `(100.0, 40.0)` to `(130.0, 148.0)` → **`30.00 × 108.00 mm`** (`1.6 mm` FR4, `83` footprints).
- **Copper Pours (`zone`):** Two full-board `GND` zones on `F.Cu` and `B.Cu` (`100.4..129.6 × 40.4..147.6 mm`, `0.20 mm` clearance, `0.20 mm` minimum thickness, `0.25 mm` thermal gap, `0.30 mm` thermal bridge width).
- **Copper Trace Segments (`703` total):**
  - **Layer Split:** `515` segments on `B.Cu` (`73.3%`, SMD & signal routing side) and `188` segments on `F.Cu` (`26.7%`, panel-control & bus side).
  - **Width Hierarchy:**
    - `0.25 mm` signal traces: `562` segments (`411` `B.Cu`, `151` `F.Cu`).
    - `0.30 mm` power/bias rails: `120` segments (`83` `B.Cu`, `37` `F.Cu`).
    - `0.40 mm` heavy power trunks: `21` segments (`B.Cu` only).
  - **Strict `45°` Octilinear Geometry:**
    - `0°` (horizontal): `187` segments (`26.6%`)
    - `90°` (vertical): `211` segments (`30.0%`)
    - `45°` diagonal: `125` segments (`17.8%`)
    - `135°` diagonal: `115` segments (`16.4%`)
    - Off-grid (`other`): `65` segments (`9.2%`) — exclusively short SMD pad-entry stubs (`median = 0.13 mm`, `max = 1.28 mm`).
    - **Arcs & Teardrops:** `0` copper `(arc ...)` segments, `0` `gr_arc` primitives, and `(legacy_teardrops no)` with `0` teardrop shapes. The PCB's visual language is strictly **straight octilinear segments + `45°` miters**, matching the front panel's `45°` chamfered aesthetic.
- **Vias & Annular Rings:**
  - `133` through-hole vias (`F.Cu` ↔ `B.Cu`), **100% uniform geometry**: `0.60 mm` pad diameter, `0.30 mm` drill diameter (`0.15 mm` copper annular ring, `2:1` pad-to-drill ratio).
- **Representative Bus & Corner Patterns:**
  - **Long vertical buses with `45°` dog-leg breakouts:** e.g., `NET_ENV_BUF` runs `30.25 mm` vertically along `X=102.25 mm` (`Y=140.5→110.25`) after a `45°` chamfered turn `(111.75, 143.0) → (104.75, 143.0) → (102.25, 140.5)`; `NET_PREAMP_OUT` runs `25.50 mm` vertically along `X=105.25 mm` (`Y=92.0→117.5`).
  - **Differential / parallel power trunks:** `-12V` (`56` segments) and `+12V` (`44` segments) routed primarily in `0.30 mm` / `0.40 mm` orthogonal + `45°` runs.
- **Auxiliary PCB Graphics (`F.SilkS` / `B.SilkS`):**
  - `5.00 × 5.00 mm` filled `F.SilkS` `gr_rect` QR blank at `(123.8, 41.0)..(128.8, 46.0)`.
  - `2×` `0.50 mm` Ø filled `B.SilkS` pin-1 dots (`gr_circle` `r=0.25 mm` at `(111.075, 127.31)` and `(118.925, 134.69)`).
  - `90°`-rotated `0.80 × 0.80 mm` (`0.15 mm` stroke) vertical edge `F.SilkS` labels (`ENV FOLLOWER`, `6HP REV 1.0`, `github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter`).

### 2.2 `TP1`–`TP12` Test-Point Rail & Annotations

All `12` test points (`envelope_follower.kicad_pcb`, `TestPoint_Keystone_5000-5004_Miniature`, marked `dnp` / `exclude_from_bom`) share identical pad geometry:
- **Pad:** `2.00 mm` circular PTH (`*.Cu`, `*.Mask`), `1.00 mm` drill (`0.50 mm` copper ring, `2:1` pad-to-drill ratio).
- **Silkscreen Ring:** `B.SilkS` `fp_circle` of radius `1.40 mm` (`2.80 mm` Ø, `0.12 mm` stroke).
- **Dual-Side Labels:** `0.80 × 0.80 mm` (`0.15 mm` stroke) on both `F.SilkS` and `B.SilkS`.

| Ref | Label (`Value`) | Net | KiCad `(X, Y)` mm | Role / Spatial Grouping |
| :-: | :--- | :--- | :---: | :--- |
| `TP12` | `GND2` | `GND` | `(103.2, 42.50)` | Top-left ground reference |
| `TP3` | `-12V` | `-12V` | `(111.2, 42.25)` | Top power rail (`-12 V`) |
| `TP2` | `+12V` | `+12V` | `(116.7, 42.25)` | Top power rail (`+12 V`) |
| `TP4` | `PRE` | `NET_PREAMP_OUT` | `(103.2, 60.00)` | **Signal-Flow Rail #1:** `×2` AC Preamp out |
| `TP9` | `HWR` | `NET_RECT_HALF` | `(103.2, 66.50)` | **Signal-Flow Rail #2:** Half-wave intermediate (`+6.5 mm`) |
| `TP5` | `RECT` | `NET_RECT_OUT` | `(103.2, 73.00)` | **Signal-Flow Rail #3:** Full-wave rectifier out (`+6.5 mm`) |
| `TP10` | `DRV` | `NET_U1D_OUT` | `(103.2, 79.50)` | **Signal-Flow Rail #4:** Slew comparator/driver (`+6.5 mm`) |
| `TP6` | `ENV` | `NET_ENV_BUF` | `(103.2, 86.00)` | **Signal-Flow Rail #5:** Buffered envelope (`+6.5 mm`) |
| `TP11` | `OFF` | `NET_OFF_WIPER` | `(103.2, 92.50)` | **Signal-Flow Rail #6:** Offset wiper voltage (`+6.5 mm`) |
| `TP7` | `INV` | `NET_INV_AMP` | `(103.2, 99.00)` | **Signal-Flow Rail #7:** Inverted output amp (`+6.5 mm`) |
| `TP8` | `OUT` | `NET_OUT_AMP` | `(103.2, 105.00)` | **Signal-Flow Rail #8:** Non-inverted output amp (`+6.0 mm`) |
| `TP1` | `GND` | `GND` | `(115.0, 145.60)` | Bottom-center ground test point |

**Architectural Insight:** `TP4 → TP9 → TP5 → TP10 → TP6 → TP11 → TP7 → TP8` forms a crisp, evenly spaced (`6.5 mm` pitch) vertical diagnostic spine along `X = 103.2 mm` (`3.2 mm` inset from the left PCB edge) that physically traces the module's analog signal chain top-to-bottom.

### 2.3 Recommended Subtle UI Accents (Zero Visual Clutter)

To preserve legibility in the Astro Build Tutorial while grounding the UI in `ENV / SKEW`'s hardware DNA:

1. **Section Dividers (Patchbay Bus + `45°` Trace Break):** Replace plain `<hr>` or flat borders with a `1–2 px` ENIG Gold / `--border-ui` horizontal rule terminating in a `45°` chamfered jog and a single `0.60/0.30`-proportioned via ring (`svg` `aria-hidden="true"`, `height: 12px`, low opacity `0.45–0.7` on subtle dividers, full `#d8b154` on major hero/section bands).
2. **Vertical Stage Progress Rail (`TP4`–`TP8` Test-Point Spine):** In the left navigation / stage rail (`docs.css` `.doc-rail`), render a `2 px` vertical trace spine (`45°` dog-leg into the active stage) with `2:1` annular via nodes (`10 px` outer ring, `5 px` hollow center) mimicking `TP` test points—inactive nodes in `--border-ui` (`#6e7485`), visited/completed in `--led-green` (`#4ade80`) or `--accent-gold` (`#d8b154`), active stage as a double-ringed `TP` pad (`1.4×` outer silkscreen halo).
3. **Cards & Prompt Containers (`45°` Chamfer + Segmented Side Rail):** Apply `reference/site/`'s `.chamfer-sm` (`6px` `45°` top-right & bottom-left clip-path, reverting to `border` in `@media (forced-colors: active)`) sparingly to primary badges, stage numbers (`.patch-num`), and hero/CTA buttons, while keeping prose cards rectangular with `1px` `--border-subtle` borders and optional `3px` vertical gold segment markers (`0.42 mm` side-rail echo) on active/callout blocks.
4. **Hero Frame & Stage Header Glyphs:** Pair the Stage 1–9 tutorial hero or section headers with lightweight cropped motifs from `front_soldermask.svg` (`aria-hidden="true"`):
   - Full `FaceplateIllustration` (`30:128.5` aspect) or cropped `ENV / SKEW` Hero Envelope (`viewBox="13.5 1.0 15.5 5.0"`) in the tutorial overview hero.
   - Cropped `_/‾` (`RV2 ATK`), `‾\_` (`RV3 REL`), gain bars (`RV1`), or normaling arrow (`J1 → J2`) as `18–24 px` inline stage/mode icons—never behind body text as tiled PCB trace wallpapers (which degrade contrast and cause visual fatigue).
5. **Test-Point Micro-Labels (`90°` or Monospace `TP` Chips):** Reuse `TP` / stage code badges (`0.72rem` `IBM Plex Mono`, `tabular-nums`, e.g., `TP4 · PRE`) for hardware bringup callouts and stage cross-references.

---

## 3. Design Tokens, Typography, WCAG Contrast & Motion Comparison

### 3.1 Token Comparison: `reference/site/src/styles/tokens.css` vs. `docs/stylesheets/extra.css`

| Concept | `reference/site/src/styles/tokens.css` (Dark-only) | `docs/stylesheets/extra.css` (`:root` + `slate`) | `docs/stylesheets/extra.css` (`default` Light Mode) | Notes / Alignment Gap |
| :--- | :--- | :--- | :--- | :--- |
| **Void Canvas** | `--bg-void: #0d0e11` | `--env-bg-void: #0d0e11` (header/tabs `#0d0e11`) | `#1b1d22` header (stays dark studio) | Identical dark value; `extra.css` keeps header `#0d0e11` in both modes. |
| **Primary Canvas** | `--bg-canvas: #141518` | `--md-default-bg-color: #141518` | `--md-default-bg-color: #fbfaf7` | Warm off-white `#fbfaf7` in light mode avoids harsh `#fff` glare. |
| **Elevated Surface** | `--bg-surface: #1b1d22`, `--bg-surface-elevated: #1d2028` | `--md-primary-fg-color: #1b1d22`, `--md-admonition-bg-color: #1b1d22` | `#efeae0` table th, `#f4f1e8` admonition | Exact match in dark mode. |
| **Code / Math Well** | `--bg-code: #090a0d`, `--bg-code-elevated: #101216` | `--md-code-bg-color: #090a0d`, `--md-code-bg-color--light: #101216` | `--md-code-bg-color: #f1efe9`, `--light: #e7e3d8` | Exact match in dark mode. |
| **Primary / Silk Ink** | `--ink-primary: #e8eaef`, `--ink-silk: #f4f5f7` | `--md-default-fg-color: #e8eaef`, `--md-primary-bg-color: #f4f5f7` | `#141518` fg, `#1a1c22` typeset | Exact match in dark mode. |
| **Muted Ink** | `--ink-muted: #a6acb8` | `--md-default-fg-color--light: #a6acb8` | `#4a505e` | Exact match in dark mode. |
| **ENIG Gold Accent** | `--accent-gold: #d8b154`, `--accent-gold-bright: #e2be66`, `--accent-gold-tint: #262013` | `--md-typeset-a-color: #d8b154`, `--md-accent-fg-color: #e2be66`, `--env-accent-gold-tint: #262013` | `--md-typeset-a-color: #7a5608`, `--md-accent-fg-color: #94680a` | **Note:** `front_soldermask.svg` fab export uses `#C89B3C`, which `panel-svg-shared.ts` recolors to `#D8B154`. |
| **UI & Subtle Borders** | `--border-ui: #6e7485`, `--border-subtle: #2b2f3b`, `--border-grid: #323642` | `--env-border-ui: #6e7485`, `--md-typeset-table-color: #2b2f3b` | `--md-typeset-table-color: #d1cdc2` | Exact match in dark mode. |
| **LED Status Tokens** | `--led-green: #4ade80` / `#102819`, `--led-red: #f87171` / `#2c1416`, `--led-dark: #c5cad4` / `#1e2128` (+ amber `#fbbf24` / `#291e09` in `global.css:515-518`) | `--env-led-green: #4ade80`, `--env-led-red: #f87171` (`#102819` / `#2c1416` hardcoded on `.prompt-copy-btn`) | Same `#102819` / `#2c1416` on copy confirmation pill | `extra.css` lacks `--led-green-bg`, `--led-red-bg`, `--led-dark`, `--led-amber` custom properties. |
| **Corner Geometry** | Rectangular (`0px`) / subtle `4–6px` + `.chamfer-sm` (`6px` `45°` clip-path) | Soft `8px` `border-radius` (`extra.css:273-282`) | Soft `8px` `border-radius` | Astro Build Tutorial can harmonize with `4–6px` + `.chamfer-sm` accents. |

### 3.2 Typography & Self-Hosted Font Assets

| Role | `reference/site/src/styles/fonts.css` + `tokens.css` | `docs/stylesheets/fonts.css` + `docs/assets/fonts/` | Impact for Astro Build Tutorial |
| :--- | :--- | :--- | :--- |
| **Slab Wordmark (`--font-slab`)** | `'Barlow Condensed', 'DIN Condensed', system-ui, sans-serif` (`latin-700`, `latin-800` via `@fontsource/barlow-condensed@5.3.0`) | **Missing** (no `barlow-condensed` in `docs/assets/fonts/` or `fonts.css`; header falls back to `Space Grotesk`) | Add `@fontsource/barlow-condensed` (`700`, `800`) if adopting `.slab-logo` or condensed hardware badges. |
| **Display (`--font-display`)** | `'Space Grotesk', system-ui, -apple-system, sans-serif` (`latin-500/600/700`) | `'Space Grotesk'` (`latin-500/600/700`, `woff2` in `docs/assets/fonts/`) | Identical (`font-size-adjust: cap-height from-font` in `reference/site/` headings). |
| **Body (`--font-body`)** | `'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif` (`latin-400/500/600/700`) | `'IBM Plex Sans'` (`latin-400`, `400-italic`, `500/600/700`, `woff2`) | `docs/` also includes `400-italic` (needed for tutorial prose emphasis). |
| **Mono (`--font-mono`)** | `'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace` (`latin-400/500/600`) | `'IBM Plex Mono'` (`latin-400/500/600/700`, `woff2`) | `docs/` includes `700` bold mono (`prompt-group-header`). |
| **License & Privacy** | Self-hosted `@fontsource@5.3.0` Latin subsets; zero external requests. | Self-hosted SIL OFL (`docs/assets/fonts/OFL.txt`); zero external requests. | Preserve zero-CDN self-hosted `@fontsource` bundling in Astro. |

### 3.3 Verified WCAG 2.1 Contrast Ratios

All ratios below were computed from exact sRGB relative luminance (`WCAG 2.1 §1.4.3 / §1.4.6 / §1.4.11`):

#### Dark Studio Palette (`tokens.css` & `extra.css` `slate`)

| Foreground / Background Pair | Ratio | WCAG 2.1 Level |
| :--- | :---: | :--- |
| `--ink-primary` (`#e8eaef`) on `--bg-canvas` (`#141518`) | **15.17 : 1** | AAA (`>= 7:1`) |
| `--ink-primary` (`#e8eaef`) on `--bg-void` (`#0d0e11`) | **16.04 : 1** | AAA |
| `--ink-silk` (`#f4f5f7`) on `--bg-canvas` (`#141518`) | **16.74 : 1** | AAA |
| `--ink-silk` (`#f4f5f7`) on `--bg-surface` (`#1b1d22`) | **15.46 : 1** | AAA |
| `--ink-muted` (`#a6acb8`) on `--bg-canvas` (`#141518`) | **8.01 : 1** | AAA |
| `--ink-muted` (`#a6acb8`) on `--bg-surface` (`#1b1d22`) | **7.40 : 1** | AAA |
| `--accent-gold` (`#d8b154`) on `--bg-canvas` (`#141518`) | **8.99 : 1** | AAA |
| `--accent-gold` (`#d8b154`) on `--bg-surface` (`#1b1d22`) | **8.30 : 1** | AAA |
| `--accent-gold` (`#d8b154`) on `--bg-code` (`#090a0d`) | **9.74 : 1** | AAA |
| Fab Gold (`#c89b3c`) on `--bg-canvas` (`#141518`) | **7.14 : 1** | AAA (prefer `#d8b154` for UI chrome) |
| `--accent-gold-bright` (`#e2be66`) on `--accent-gold-tint` (`#262013`) | **9.08 : 1** | AAA |
| `--accent-gold-ink` (`#141518`) on `--accent-gold` (`#d8b154`) | **8.99 : 1** | AAA |
| `--border-ui` (`#6e7485`) on `--bg-canvas` (`#141518`) | **3.91 : 1** | AA Non-Text (`>= 3:1`) |
| `--border-ui` (`#6e7485`) on `--bg-surface` (`#1b1d22`) | **3.61 : 1** | AA Non-Text (`>= 3:1`) |
| `--led-green` (`#4ade80`) on `--led-green-bg` (`#102819`) | **9.00 : 1** | AAA |
| `--led-red` (`#f87171`) on `--led-red-bg` (`#2c1416`) | **6.23 : 1** | AA Normal / AAA Large |
| Amber (`#fbbf24`) on `#291e09` (`global.css:515-518`) | **9.80 : 1** | AAA |
| `--led-dark` (`#c5cad4`) on `--led-dark-bg` (`#1e2128`) | **9.80 : 1** | AAA |

#### Warm-Studio Light Palette (`extra.css` `default`)

| Foreground / Background Pair | Ratio | WCAG 2.1 Level |
| :--- | :---: | :--- |
| `#141518` on `#fbfaf7` (`--md-default-fg-color` / `bg`) | **17.49 : 1** | AAA |
| `#1a1c22` on `#fbfaf7` (`--md-typeset-color` / `bg`) | **16.32 : 1** | AAA |
| `#4a505e` on `#fbfaf7` (`--md-default-fg-color--light` / `bg`) | **7.74 : 1** | AAA |
| `#7a5608` on `#fbfaf7` (`--md-typeset-a-color` / `bg`) | **6.36 : 1** | AA Normal / AAA Large |
| `#94680a` on `#fbfaf7` (`--md-accent-fg-color` / `bg`) | **4.74 : 1** | AA Normal (`>= 4.5:1`) |
| `#5c4309` on `#efe5cc` (`.prompt-body code` light mode) | **7.41 : 1** | AAA |
| `#7a5608` on `#f8f6f0` (`.admonition.prompt > .admonition-title`) | **6.15 : 1** | AA Normal |
| `#141518` on `#f1efe9` (`--md-code-fg-color` / `bg`) | **15.88 : 1** | AAA |

- **Key Contrast Guardrail:** Never place raw `#d8b154` ENIG Gold text or icons directly on the `#fbfaf7` light canvas (`~2.0:1`, fails WCAG); in light mode, decorative ENIG gold SVG motifs must either sit inside a dark `#141518` substrate frame (such as `FaceplateIllustration`) or remap to `--accent-gold` light-mode equivalents (`#94680a` for non-text icons/rules `>= 3:1`, `#7a5608` for interactive text `6.36:1`).

### 3.4 `prefers-reduced-motion`, `forced-colors` & Print Handling

- **`prefers-reduced-motion`:**
  - `docs/stylesheets/extra.css:596-602` uses `@media (prefers-reduced-motion: reduce)` to neutralize `transform` (`transform: none`) and shorten `.prompt-copy-btn` / `.prompt-copy-tip` to `transition: opacity 0.08s linear`.
  - `reference/site/src/styles/docs.css:71-84` gates `<details>` / disclosure transitions inside `@media (prefers-reduced-motion: no-preference)`.
  - `reference/site/src/components/env-skew-panel.ts:98-104` zeroes `.knob-rotator`, `.ctrl-group`, and `.ctrl-hit-ring` transitions under `@media (prefers-reduced-motion: reduce)`.
  - `reference/site/src/styles/tokens.css:27` explicitly warns: `Never transition/animate scrollbar-color`.
- **`@media (forced-colors: active)` (Windows High Contrast):**
  - Both `extra.css:747-780` and `reference/site/src/styles/*.css` + `FaceplateIllustration.astro:231-240` + `env-skew-panel.ts:105-115` strip `clip-path` chamfers (`clip-path: none`) and `filter: drop-shadow(...)`, replace custom borders with `1px solid CanvasText` / `2px solid ButtonText`, and map active tabs/buttons/SVG overlays to `Highlight` / `HighlightText`. Any new SVG dividers, stage rails, or `TP` badges in the Astro Build Tutorial should use `currentColor` or explicit `forced-colors: active` overrides (`CanvasText` / `Highlight`) so decorative copper/gold strokes remain visible.
- **`@media print`:**
  - Both `extra.css:782-817` and `global.css:865-933` reset surfaces to `#ffffff` / `#000000`, drop box/drop shadows, force open `<details>::details-content`, and hide interactive chrome (copy buttons, search triggers, jump navs).
