# Tutorial Update TODO: Incorporating the `EnvelopeFollowerWithSkewLimiter` Workflow

This roadmap captures planned updates to [`docs/tutorial/`](docs/tutorial/), [`docs/index.md`](docs/index.md), [`docs/reference/`](docs/reference/), and [`mkdocs.yml`](mkdocs.yml) based on the 12 conversation traces in [`prompts/`](prompts/) (indexed in [`prompts/README.md`](prompts/README.md)) from the companion [`EnvelopeFollowerWithSkewLimiter`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter) build.

## Guiding Decisions

- **Adopt the interactive human-in-the-loop workflow:** Shift the codelab away from one-shot prompt automation toward the interactive workflow validated in [`prompts/01`–`12`](prompts/README.md): a living `README.md` index, interactive one-improvement-at-a-time Q&A producing a unified `DesignSpec.md`, a SKiDL-driven KiCad 10 `.kicad_sch` + PDF schematic, a declarative `silk_layout.json` sidecar + repo-local `/edit-silkscreen` hybrid GUI/AI co-editing loop, and PCB-verified `checklists/`.
- **Accept losing automated unattended replay:** Dropping one-shot replayability (such as `tutorial-test-drive` / clean-room unattended `stages/` replay) is an intentional trade-off so the tutorial can teach interactive engineering Q&A, visual inspection loops, and human + AI co-editing.
- **Prerequisite block — front panel first:** Hold edits to `docs/tutorial/`, `docs/index.md`, `docs/reference/`, and `mkdocs.yml` until the mated 6 HP × 3U front panel for `EnvelopeFollowerWithSkewLimiter` has been crafted and its trace, renders, and ordering checklist are in place.

---

## 1. Prerequisite Gate (Before Editing the Codelab)

- [ ] Craft the mated 6 HP × 3U front panel for `EnvelopeFollowerWithSkewLimiter` (`RV1`–`RV4` single-column pots, `SW1` `SMOOTH`, `SW2` `FAST/SLOW`, `LED1` bi-color `OUT`, `J1`–`J4` 2×2 jacks including `SLEW IN`).
- [ ] Export the front-panel session trace(s) into [`prompts/`](prompts/) (continuing from `13-...`) and add a front-panel ordering checklist (`checklists/06-front-panel-ordering.md` or integrated into `checklists/01-main-board-ordering.md`).
- [ ] Capture and curate visual assets for `docs/images/`: rendered schematic PDF/PNG preview, main PCB top/bottom 3D renders, zoomed `/edit-silkscreen` calibrated mm-ruler preview, and front-panel top/bottom 3D renders.
- [ ] Finalize the worked-example scope before editing docs: decide whether to switch all `docs/` circuit descriptions, BOMs, and reference tables end-to-end to `EnvelopeFollowerWithSkewLimiter`, or keep the baseline `EnvelopeFollower` circuit as the worked example while upgrading the workflow stages.
- [ ] Decide disposition of legacy automated-replay artifacts ([`stages/`](stages/), [`AuditReport.md`](AuditReport.md), [`SkillImprovementAuditReport.md`](SkillImprovementAuditReport.md), [`.agents/skills/tutorial-test-drive/SKILL.md`](.agents/skills/tutorial-test-drive/SKILL.md), and [`.agents/skills/skill-improvement-audit/SKILL.md`](.agents/skills/skill-improvement-audit/SKILL.md))—either archive, remove, or label as historical baseline replay artifacts.

---

## 2. Cross-Cutting Workflow & Repo Hygiene Updates

- [ ] **Maintain `README.md` as a "Living Context Map"** ([`01`](prompts/01-4b4ac404-please-update-readme-md.md), [`02`](prompts/02-7f75c0c1-please-review-envelopefollower-webp-i-d-like.md), [`03`](prompts/03-6a910d47-please-review-envelopefollower-md-are-there-improv.md), [`04`](prompts/04-4dfb0979-let-s-work-through-envelopefollowerimprovements-md.md), [`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md), [`10`](prompts/10-a47d447e-please-create-markdown-checklists-main-board-order.md), [`12`](prompts/12-0e25fc0a-please-update-readme-md.md)): Teach readers to initialize `README.md` before Stage 2 as a file/skills index and end every stage prompt with *"update `@[README.md]` and git commit"* so new sessions immediately locate every spec, schematic, PCB, and checklist.
- [ ] **Git checkpointing & `.gitignore` hygiene** ([`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md), [`07`](prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md), [`09`](prompts/09-8179ce18-on-back-silkscreen-remove-5mm-x-5mm.md), [`10`](prompts/10-a47d447e-please-create-markdown-checklists-main-board-order.md)): Instruct readers to ignore `.history/`, `*.kicad_prl`, `~*.lck`, `skidl_REPL.*`, `*.log`, and `.agents/skills/**/__pycache__/` in `.gitignore` during Stage 1, and commit clean generated baselines before major generator refactors (e.g., before introducing `silk_layout.json`).
- [ ] **Post-upgrade skill smoke-testing** ([`07`](prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md) Turn 7): Add a standard check after running `npx skills update` / syncing upstream hardware skills—re-run read-only verification (`--check-silk`, `--show-silk`, script imports/signatures) before committing `skills-lock.json` (caught 39 newly enforced keepout hits and 9 QR via/track hits after upstream `kicad-silkscreen-markup` tightened checks).

---

## 3. Stage-by-Stage Codelab Update Checklist

### Landing Page & Navigation ([`docs/index.md`](docs/index.md) & [`mkdocs.yml`](mkdocs.yml))
- [ ] Update the Architecture Pipeline Mermaid diagram, stage list, and `nav` titles in [`docs/index.md`](docs/index.md) and [`mkdocs.yml`](mkdocs.yml) to reflect the interactive workflow (interactive `DesignSpec.md` Q&A, DFT test-point pass, SKiDL-driven `.kicad_sch` + PDF schematic, `silk_layout.json` + `/edit-silkscreen` co-editing, and `checklists/`).
- [ ] Add an upfront note explaining that the tutorial emphasizes interactive human-in-the-loop prompts, engineering trade-offs, and visual QA loops rather than unattended one-shot stage replay.
- [ ] Update the Controls/I&O table and hero images once the `EnvelopeFollowerWithSkewLimiter` front panel and final worked-example scope are locked.

### Stage 1: Hardware Agent Skills ([`docs/tutorial/stage-1-agent-skills.md`](docs/tutorial/stage-1-agent-skills.md))
- [ ] Add repo bootstrap habits before Stage 2: create/update `README.md` as a living context map ([`01`](prompts/01-4b4ac404-please-update-readme-md.md)) and configure `.gitignore` for KiCad lock/history files, SKiDL logs, and Python `__pycache__` directories ([`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md), [`07`](prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md)).
- [ ] Introduce `/agy-customizations` as the built-in mechanism used later in Stage 5 to author project-local skills (such as `/edit-silkscreen` in [`07`](prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md) Turns 4–5) instead of bloating always-on workspace rules.
- [ ] Add the post-upgrade skill smoke-check workflow ([`07`](prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md) Turn 7) so readers catch stricter upstream DFM/keepout rules immediately after skill updates.

### Stage 2: Sketch Extraction & Circuit Critique ([`docs/tutorial/stage-2-circuit-upgrades.md`](docs/tutorial/stage-2-circuit-upgrades.md))
- [ ] Update **Step 2.1 (Extraction)** from [`02`](prompts/02-7f75c0c1-please-review-envelopefollower-webp-i-d-like.md):
  - Show multi-scale visual cropping (full-resolution quadrants + macro diode/polarity crops) rather than relying on a single downscaled read.
  - Show KCL cross-validation of visual diode/polarity reads, keeping the extracted baseline `EnvelopeFollower.md` immutable (separating faithful transcription from Eurorack build notes).
  - Add a Python BOM↔Netlist pin-completeness assertion script on the Markdown tables to catch dropped or orphaned pins before any critique begins.
- [ ] Update **Step 2.2 (Critique)** from [`03`](prompts/03-6a910d47-please-review-envelopefollower-md-are-there-improv.md):
  - Show independent visual re-verification of tricky areas (`EnvelopeFollower.webp` diode crops) before proposing fixes.
  - Teach structuring `EnvelopeFollowerImprovements.md` into **Tier 1 (Critical)**, **Tier 2 (Refinements)**, and **Tier 3 (Optional Features)** plus explicit **Op-Amp Budget Options** (`TL074H + TL072H` vs. `2× TL074H`).
  - Highlight backing analog critiques with Python math and Bode/Nyquist phase-margin stability sweeps (citing how a Python sweep caught the `C_comp = 100 pF` complex-zero notch at `12.2°` phase margin and proved `R_fb = 10 kΩ, C_comp = 2.2 nF` gives `~90.3°` phase margin across `100 Ω` to `1 MΩ`).
  - Include running an automated Markdown linter for local file links, heading anchor slugs, balanced KaTeX `$`/`$$` delimiters, and valid Mermaid edge syntax.
- [ ] Streamline **Step 2.3**: fold the standalone *"add Eurorack protections"* prompt cleanly into Step 2.2 / Stage 3's interactive walkthrough or clarify how protections are resolved during the interactive design Q&A.

### Stage 3: Interactive Design Spec & Design-for-Testability ([`docs/tutorial/stage-3-bom-and-dfm.md`](docs/tutorial/stage-3-bom-and-dfm.md))
- [ ] Replace the old one-shot 4-file spec prompt (`EnvelopeFollowerImproved.md`, `EnvelopeFollowerBOM.md`, `EnvelopeFollowerExplanation.md`, `SilkscreenInstructions.md`) with the **two-step interactive workflow** that produces a unified **`DesignSpec.md`**:
  1. **Step 3.1 — Interactive One-Improvement-at-a-Time Q&A → `DesignSpec.md`** ([`04`](prompts/04-4dfb0979-let-s-work-through-envelopefollowerimprovements-md.md)):
     - Showcase the exact prompt: *"Let's work through `@[EnvelopeFollowerImprovements.md]`, one improvement at a time. This is primarily for my education, but in cases where there are options or trade offs, I want to make informed decisions."*
     - Teach declaring upfront hard constraints (6 HP 3U panel, majority JLCPCB SMD PCBA, `2× TL074H`) and musical context (e.g., techno kick sidechain ducking + ambient swells) so trade-offs stay grounded.
     - Highlight **strategic deferral** of panel-space UI choices until all Tier 3 candidates are inventoried (preventing 6 HP overcrowding).
     - Document verifying real datasheets and vendor parts during Q&A (`TL074H` upper `VCM` rail range, `BAT54S` SOT-23 pinout, `1N4148W` vs Schottky leakage on hold caps, Tayda THT part dimensions), sequential RefDes renumbering, and Python BOM↔Netlist pin-completeness verification.
  2. **Step 3.2 — Design-for-Testability (DFT) Test-Point Pass** ([`05`](prompts/05-a4aff487-designspec-md-i-m-wondering-what-options.md)):
     - Show asking for tiered TP options (`Ronghe RH-5001`, `LCSC C5199801`, `DNP` for `` `$0` `` PCBA assembly cost).
     - Show resolving conflicting web specs authoritatively via `.agents/skills/lcsc/scripts/search_lcsc.py` + inspecting local KiCad `.kicad_mod` footprints (`TestPoint:TestPoint_Keystone_5000-5004_Miniature`).
     - Document probe-safe TP rules: omit high-Z hold capacitor and virtual-ground/inverting nodes, place **two `GND` TPs** at opposite ends of a tall `108 mm` Eurorack board for short scope ground leads, keep `B.Cu` THT test points outside front-panel pot/jack metal body footprints, and update `DesignSpec.md` directly.
- [ ] Keep `EnvelopeFollowerExplanation.md` as an optional educational add-on prompt rather than a mandatory Stage 3 gate.

### Stage 4: SKiDL Capture, Custom Footprints & KiCad PDF Schematic ([`docs/tutorial/stage-4-skidl.md`](docs/tutorial/stage-4-skidl.md))
- [ ] Show the single-sentence `/skidl` handoff enabled by a thorough `DesignSpec.md` (`"/skidl Please turn @[DesignSpec.md] into a circuit."`, [`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md) Turn 1) plus how single clarifying questions resolve remaining hardware choices (`SW1`/`SW2` SPDT symbol & footprint).
- [ ] Document **downstream-first alignment**: reading `kicad-pcbnew-layout` and `eurorack-panel` before writing SKiDL so custom fields (`LCSC`, `MPN`, `Manufacturer`, `JLCPCB_Class`, `Silkscreen`, `Notes`) and footprint origins match downstream PCB/panel generators.
- [ ] Document **budgeted JLCPCB Basic vs. Extended sourcing** via `jlcpcb_search.py --in-stock-only` (staying within a tight Extended-SKU budget such as 3 Extended SKUs while upgrading to Basic `50 V` `1206` MLCCs where DC-bias capacitance retention matters).
- [ ] Document authoring and validating **project-local custom footprints** when KiCad 10 lacks a part (e.g., `footprints/Eurorack_Custom.pretty/SW_Toggle_SPDT_Dailywell_2MS1.kicad_mod` + `fp-lib-table`, bushing centered at `(0, 0)` for `eurorack-panel`, verified via KiCad's `pcbnew.FootprintLoad()`).
- [ ] Document **multi-layer netlist verification**: checking every `(ref, pin)` against real `.kicad_mod` pad names and testing `parse_netlist()` *without* `dnp_prefixes` so genuine `.net` DNP properties are verified.
- [ ] Add a major new section: **Generating a Human-Readable KiCad 10 Schematic (`.kicad_sch`) & PDF (`envelope_follower.pdf`)** ([`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md) Turns 2 & 4):
  - Show the prompts: `"/skidl I'd like a KiCad schematic so I can visualise this circuit"` and `"Please generate a PDF version of the schematic. Add to @[README.md] and git commit"`.
  - Explicitly warn that built-in `skidl.generate_schematic()` (`schematizer 0.2.0`) fails or produces tangled, stub-exploded diagrams on non-trivial analog circuits.
  - Explain the **SKiDL-as-single-source-of-truth** `generate_schematic.py` architecture: importing `build_circuit()`, quote-preserving S-expression parser/dumper (not `simp_sexp`), flattening `(extends ...)` symbols while merging parent+child flags, omitting `(justify center)`, applying empirical `_text_transform(rot, mirror)` relative-angle rules for KiCad 10 `SCH_FIELD`s, adding `PWR_FLAG`s, and laying out clean titled sections clear of the A3 title block.
  - Document the 4-layer schematic verification loop: (1) `kicad-cli sch export netlist` 100% pin-for-pin parity diff against `envelope_follower.net`, (2) `kicad-cli sch erc --severity-all`, (3) `analyze_schematic.py`, and (4) `kicad-cli sch export pdf` → PNG → `PIL.Image.crop()` visual inspection of every section.
- [ ] Add a **SKiDL 3.0.0 & KiCad 10 Pitfalls Callout**: Python `<= 3.14` (avoiding 3.15 `h5py` failures), upstream `generate_xml()` bug (use `xml.etree.ElementTree`), Python 3 `eval()` comprehension scoping in `erc_assert()`, benign `default_circuit.root.tag = ""` warning, and cleaning stray `skidl_REPL.*` / `*.kicad_prl` files.

### Stage 5: 6 HP Main PCB, Layout Debugging, `silk_layout.json` & `/edit-silkscreen` ([`docs/tutorial/stage-5-schematic-and-pcb.md`](docs/tutorial/stage-5-schematic-and-pcb.md))
- [ ] Update **Step 5.1 (Automated PCB Generation & Layout Debugging)** from [`07`](prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md) Turn 1:
  - Keep the multi-skill upfront prompt (`/kicad-pcbnew-layout /kicad-silkscreen-markup /eurorack-panel /kicad`).
  - Show extracting unit-1 symbol UUIDs from `.kicad_sch` (`fp.SetPath(...)`) so `cross_analysis.py` achieves 100% schematic-to-PCB pairing.
  - Recommend setting KiCad `GridOrigin` and `AuxOrigin` to `(BOARD_X0, BOARD_Y0)` so KiCad's GUI coordinates match board-local `(0..30, 0..108)` mm 1:1.
  - Teach empirical KiCad Python footprint-geometry probing before placement (catches `fp.Flip()` X-axis mirroring vs. Y-axis, pot lug widths, and the `fp.Flip()`-before-`board.Add()` SIGSEGV).
  - Teach writing a pre-routing `verify_placements()` gate for **cross-layer physical collisions** (which KiCad DRC ignores).
  - Document practical routing techniques: 1-second BFS reachability + ASCII grid dumps to uncross passive cascades via 180° rotations, shared GND vias inside `SOIC-14` bellies, exact rectangular blockers for unconnected pads, pruning stitching vias via `zone.HitTestFilledArea`, and sorting set iterations for deterministic routing.
  - Make **3D render visual inspection** an explicit pass/fail gate (caught real label collisions and silent `try_silk_text()` drops even with 0 DRC violations and passing `silk_annotator --inspect`).
- [ ] Add **Step 5.2 (NEW): Declarative Silkscreen Sidecar (`silk_layout.json`) & Bidirectional CLI** ([`07`](prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md) Turns 2–3):
  - Show the motivating prompt sequence (*"How should I move silkscreen entries such that they can be updated in the generate script?"* → *"git commit the current state. Then update the script so that I can work with it to move things around in a new chat. Assume I am going to want to move most silkscreen entries, one by one."*).
  - Explain `silk_layout.json` (board-local mm coordinates, compact 1-line-per-passive JSON formatting for clean git diffs, pinning texts, `qr_rects`, `dots`, `segments`, and `board_texts` with `"auto"` fallback).
  - Document the 6 CLI modes on `generate_kicad_pcb.py`: default rebuild, `--silk-only` (~1s restamp preserving copper/vias/UUIDs and refreshing off-board `B.Fab` notes), `--sync-silk` (extracts KiCad GUI edits via `GetBoundingBox().GetCenter()`), `--check-silk`, `--show-silk [REF ...]`, and `--auto-silk`.
  - Highlight the boundary between `--silk-only` edits and **full rebuilds** (e.g., physically swapping `+12V`/`-12V` test points in [`09`](prompts/09-8179ce18-on-back-silkscreen-remove-5mm-x-5mm.md) Turn 4), plus restoring `"top_level_sheets"` in `*.kicad_pro` via `git checkout` after `pcbnew.NewBoard`/`board.Save`.
- [ ] Add **Step 5.3 (NEW): Minting `/edit-silkscreen` & Hybrid Human + AI Visual Polish** ([`07`](prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md) Turns 4–9, [`08`](prompts/08-b4ccc2bd-on-f-silkscreen-move-the-rv-labels.md), [`09`](prompts/09-8179ce18-on-back-silkscreen-remove-5mm-x-5mm.md), [`11`](prompts/11-f5ea080c-on-the-front-side-silkscreen-i-feel.md)):
  - Show using `/agy-customizations` to create `.agents/skills/edit-silkscreen/SKILL.md` and `scripts/render_silk_preview.py` (transparent `kicad-cli pcb render` + alpha-channel bounds detection + zoomed crops with calibrated mm rulers accounting for bottom-side X-inversion).
  - Document the **Human + AI Hybrid Co-Editing Loop**:
    1. Rough-drag labels visually in KiCad PCB Editor.
    2. **Hit Save (`Cmd+S`)** — explicit warning that KiCad `.history/` autosave is not saved to the board file (even after `git commit`!).
    3. Prompt `/edit-silkscreen` (*"Saved, please tidy/align"*): agent runs `--sync-silk`, aligns rows/columns (`dy = +1.60 mm` for 0603 passives, uniform pair spacing), normalizes angles (`180°→0°`, `270°→90°`), resolves hidden `F.Fab` hardware overhangs (`block_tht_fab=True`) and vias, restamps with `--silk-only`, checks DRC, and displays zoomed ruler previews.
    4. Reload in KiCad via **`File → Revert`** (warning that saving an un-reverted KiCad tab overwrites agent edits).
  - Add a **Practical Eurorack Silkscreen Polish Checklist** distilled from Sessions [`08`](prompts/08-b4ccc2bd-on-f-silkscreen-move-the-rv-labels.md), [`09`](prompts/09-8179ce18-on-back-silkscreen-remove-5mm-x-5mm.md), and [`11`](prompts/11-f5ea080c-on-the-front-side-silkscreen-i-feel.md):
    - Place pot labels with full function + taper (`GAIN A100K`, `OFFSET B10K`) cleanly outside `F.Fab` housing overhangs.
    - Add a `0.80 mm` white `-12V` stripe (`SHAPE_T_SEGMENT` in `segments`, avoiding `qr_rects`) + `"-12V"` label under `J_PWR`.
    - Add assembly-safety callouts for non-standard parts (`2-PIN R/G`, `TAYDA A-1076`) and explicit dual-sided `+` polarity indicators whenever wiring differs from KiCad's `LED_D3.0mm` square-cathode convention.
    - Use concise signal-only TP labels (`GND`, `+12V`, `-12V`, `PRE`, `RECT`, `ENV`, etc.) on both sides; strip redundant `TP?`, `D?`, and `J_PWR` ref prefixes on `B.SilkS` while keeping part values.
    - Keep only a single `5.0 × 5.0 mm` JLCPCB QR placeholder (removing the back QR square if the front square suffices).
    - Move `B.Fab` fab notes *outside* the board outline (`y_start = BOARD_Y1 + 5.0`) and verify via `kicad-cli pcb export pdf --layers Edge.Cuts,B.Fab,B.SilkS --mirror --include-border-title` (since `render_silk_preview.py` clips off-board layers).
    - Place board title/revision along the board edge and split the GitHub URL inside an unobstructed corridor visible after soldering.

### Stage 6: Mated 3U Eurorack Front Panel ([`docs/tutorial/stage-6-front-panel.md`](docs/tutorial/stage-6-front-panel.md))
- [ ] *(Blocked on Prerequisite Gate)* Update prompts, mechanical coordinate table, toggle-switch cutout handling (`SW1`/`SW2` Dailywell `2MS1` bushing), custom panel silkscreen/branding, DRC/Gerber analyzer outputs, and 3D front/rear panel renders once the `EnvelopeFollowerWithSkewLimiter` panel is crafted.

### Stage 7: Manufacturing Checklists, Bring-Up & Final Docs Sync ([`docs/tutorial/stage-7-manufacturing.md`](docs/tutorial/stage-7-manufacturing.md) & [`docs/reference/build-checklist.md`](docs/reference/build-checklist.md))
- [ ] Replace/expand the single `OrderingNotes.md` step with the **structured `checklists/` suite** ([`10`](prompts/10-a47d447e-please-create-markdown-checklists-main-board-order.md)), instructing readers to generate checklists directly from the **actual routed `.kicad_pcb` and `jlcpcb_bom.csv`** (never stale early spec docs) and verify coverage with a Python completeness script:
  - [ ] `checklists/01-main-board-ordering.md`: `kicad-cli` Gerber/Excellon/CPL export (`--use-drill-file-origin`), `translate_bom_pnp.py` validation, LeadFree HASL or ENIG finish, **SAC305 lead-free solder paste**, **Replace QR Code** (on the exact layer holding the 5×5 mm square), Bottom-Side Economic PCBA, Extended-SKU audit, and gating checkout on Checklist 02.
  - [ ] `checklists/02-pcba-part-alignment.md`: Individual checkboxes for every SMD component showing **both** KiCad `board=(X, Y)` and **mirrored Bottom Direct View** `back=(W - X, Y)` matching JLCPCB's interactive bottom viewer, plus explicit **"WATCH FOR JLCPCB ROTATION OFFSET"** callouts on every polarized/multi-pin SMD (especially opposite-oriented pairs like `U1`/`U2` and `D4`/`D5`).
  - [ ] `checklists/03-tayda-ordering.md`: Explicit RefDes listing (avoiding unexpanded ranges), hardware/cables/knobs sizing derived from the *routed PCB* (documenting how PCB inspection caught pot-pitch drift from `17.5 mm` in spec to `15.5 mm` on PCB, capping knob OD at `≤ 14.0 mm`).
  - [ ] `checklists/04-hand-assembly.md`: Incoming PCBA inspection, **back-side (`B.Cu`) THT first** with flush-trimmed leads and opposite-polarity warnings on `+12V`/`-12V` electrolytics, pre-solder `5 V + 1 kΩ` bench polarity test for bi-color LEDs, front-side dry-fit bolted to panel → 1-pin tack alignment → finish solder → IPA flux cleanup around high-Z hold nodes → knobs after bring-up.
  - [ ] `checklists/05-board-bringup.md`: Unpowered cold checks (resistance charging, diode mode, GND continuity), `40–50 mA` current-limited dual-PSU power-up with abort thresholds, quiescent TP voltage map, stage-by-stage signal trace, musical tests, and troubleshooting matrix.
  - [ ] *(After front panel is crafted)* Front-panel ordering checklist integration.
- [ ] Add **Final Step — `README.md` Sync & Automated Link Check** ([`10`](prompts/10-a47d447e-please-create-markdown-checklists-main-board-order.md) Turn 2 & [`12`](prompts/12-0e25fc0a-please-update-readme-md.md)): document adding all generated files (`silk_layout.json`, `generate_schematic.py`, `jlcpcb_bom.csv`, `checklists/`, `skills-lock.json`), `generate_kicad_pcb.py` CLI flags (`--silk-only`, `--sync-silk`, `--check-silk`, `--show-silk`, `--auto-silk`), `/edit-silkscreen`, DRC status, and optional rendered PCB/schematic previews, plus a Python relative-link audit before the final commit.

### Optional Mode & Technical References ([`optional-dc-coupled-mode.md`](docs/tutorial/optional-dc-coupled-mode.md), [`netlist-and-bom.md`](docs/reference/netlist-and-bom.md), [`build-checklist.md`](docs/reference/build-checklist.md))
- [ ] Review [`docs/tutorial/optional-dc-coupled-mode.md`](docs/tutorial/optional-dc-coupled-mode.md) once the worked-example circuit scope is finalized (keep as an example of branching from `Improvements.md`, or cross-link how `EnvelopeFollowerWithSkewLimiter` incorporates dedicated `SLEW IN` / `SMOOTH` / `FAST/SLOW` modes).
- [ ] Sync [`docs/reference/netlist-and-bom.md`](docs/reference/netlist-and-bom.md) and [`docs/reference/build-checklist.md`](docs/reference/build-checklist.md) with the finalized Stage 3–7 artifacts and checklists.

---

## 4. Technical Pitfalls & Guardrails Catalogue (Quick Reference for Authors)

| Area | Pitfall / Quirk Observed | Trace | Guardrail / Fix to Document |
| :--- | :--- | :---: | :--- |
| **Python Env** | System Python 3.15 lacks prebuilt `h5py` wheels needed by SKiDL | [`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md) | Pin `.venv` to Python `<= 3.14` (`uv venv --clear --python 3.14 .venv`) |
| **SKiDL XML** | Upstream SKiDL 3.0.0 `generate_xml()` emits invalid unparseable XML | [`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md) | Replace with custom `xml.etree.ElementTree` XML generator |
| **SKiDL `erc_assert`** | Python 3 generator comprehensions inside `eval()` fail on caller locals | [`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md) | Avoid comprehensions over local vars inside `erc_assert()` strings |
| **SKiDL Schematic** | `skidl.generate_schematic()` (`schematizer`) fails/tangles on non-trivial analog circuits | [`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md) | Drive a custom `.kicad_sch` generator from `build_circuit()` + netlist parity diff |
| **S-Expr AST** | `simp_sexp` strips quotes from strings containing spaces or parentheses | [`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md) | Use a custom quote-preserving `Quoted` S-expression parser/dumper |
| **KiCad `.kicad_sch`** | Explicit `(justify center)` aborts schematic loading in KiCad 10 | [`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md) | Omit `(justify ...)` when horizontal alignment is centered |
| **Symbol Rotation** | `SCH_FIELD` angles are relative to parent symbol rotation; mirror/180° flips justify | [`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md) | Probe in `/tmp` and apply empirical `_text_transform(rot, mirror)` rules |
| **Symbol `(extends)`** | Replacing parent flags drops `pin_names` / `in_bom` / `on_board` on `TL074` | [`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md) | Merge child flags onto parent flags during `_flatten()` |
| **KiCad Python `< 3.12`** | Backslashes inside `{...}` in f-strings raise `SyntaxError` in bundled Python | [`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md), [`10`](prompts/10-a47d447e-please-create-markdown-checklists-main-board-order.md) | Pull dict lookups into variables before formatting |
| **`fp.Flip()`** | Crashes (SIGSEGV) before `board.Add(fp)`; mirrors across X (`Y → -Y`), not Y | [`07`](prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md) | Always `board.Add(fp)` first; probe rotated/flipped pad bounds empirically |
| **KiCad 10 Layers** | `GetLayerName()` returns `"F.Silkscreen"` / `"B.Silkscreen"`, not `"F.SilkS"` / `"B.SilkS"` | [`10`](prompts/10-a47d447e-please-create-markdown-checklists-main-board-order.md) | Normalize layer-name checks against canonical KiCad 10 strings |
| **`pcbnew` Shapes** | `PCB_SHAPE.IsFilled()` missing; `board.Remove()` emits memory-leak warnings | [`07`](prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md) | Use `GetFillMode()` / `IsSolidFill()` and `board.Delete()` / `fp.Delete()` |
| **Silkscreen Sync** | Re-applying non-centered GUI-edited text via `GetPosition()` shifts anchor | [`07`](prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md) | Extract `GetBoundingBox().GetCenter()` during `--sync-silk` |
| **KiCad GUI Autosave** | Unsaved drags live only in RAM / `.history/` (missed by `--sync-silk` & git) | [`08`](prompts/08-b4ccc2bd-on-f-silkscreen-move-the-rv-labels.md), [`09`](prompts/09-8179ce18-on-back-silkscreen-remove-5mm-x-5mm.md) | Always hit `Cmd+S` before `--sync-silk` and `File → Revert` after `--silk-only` |
| **`F.Fab` Overhang** | Pot/jack plastic bodies extend past `F.SilkS` outlines and bury nearby text | [`08`](prompts/08-b4ccc2bd-on-f-silkscreen-move-the-rv-labels.md) | Enforce `block_tht_fab=True` in `SilkGrid` |
| **`.kicad_pro` Wipe** | Full rebuild (`pcbnew.NewBoard`/`board.Save`) drops `"top_level_sheets"` | [`09`](prompts/09-8179ce18-on-back-silkscreen-remove-5mm-x-5mm.md) | Inspect `git diff` after full rebuilds and restore `*.kicad_pro` via `git checkout` |
| **LED Pinout Trap** | KiCad `LED_D3.0mm` square Pad 1 defaults to Cathode, opposite bipolar `+` wiring | [`11`](prompts/11-f5ea080c-on-the-front-side-silkscreen-i-feel.md) | Print dual-sided `+` markers + bench-test LED leads before soldering |
| **Spec-vs-PCB Drift** | Early `DesignSpec.md` pot pitch (`17.5 mm`) shrank to `15.5 mm` in layout | [`10`](prompts/10-a47d447e-please-create-markdown-checklists-main-board-order.md) | Generate ordering checklists from `.kicad_pcb`, capping knob OD `≤ 14.0 mm` |
| **`SilkGrid` OOB** | Descender padding flags valid bottom-edge labels while KiCad DRC passes `0` errors | [`09`](prompts/09-8179ce18-on-back-silkscreen-remove-5mm-x-5mm.md) | Pair `--check-silk` triage with `kicad-cli pcb drc` + visual render review |
| **`zsh` Backticks** | Double-quoted `python3 -c "..."` executes embedded backticks as shell commands | [`02`](prompts/02-7f75c0c1-please-review-envelopefollower-webp-i-d-like.md) | Use single-quoted heredocs (`python3 - <<'EOF'`) |
| **`sips` Cropping** | `sips --cropOffset` behaves inconsistently from expected top-left origins | [`02`](prompts/02-7f75c0c1-please-review-envelopefollower-webp-i-d-like.md), [`06`](prompts/06-c0e24b1d-please-turn-designspec-md-into-a-circuit.md) | Use Pillow `PIL.Image.crop((left, top, right, bottom))` for image crops |
| **KaTeX `$` Collision** | Bare currency values (e.g. `$0`) open accidental LaTeX math spans in prose | [`05`](prompts/05-a4aff487-designspec-md-i-m-wondering-what-options.md) | Wrap dollar figures in backticks (`` `$0` ``) or escape `\$` in Markdown prose |

---

## 5. Final Verification Checklist (When Updating the Codelab)

- [ ] Run `mkdocs build --strict` locally (matching [`.github/workflows/docs.yml`](.github/workflows/docs.yml)) and verify zero warnings or broken links.
- [ ] Run a Python documentation audit across `docs/` and `README.md` verifying:
  - Every internal Markdown link and heading anchor slug resolves cleanly.
  - All image paths in `docs/images/` exist and match their captions/renders.
  - All KaTeX `$` / `$$` math delimiters are properly balanced (with no unescaped currency `$` pairs).
  - All Mermaid diagram blocks parse without raw `<`/`>` syntax errors in labels.
