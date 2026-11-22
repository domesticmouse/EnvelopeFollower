# From Sketch to Eurorack Module: End-to-End Hardware Design Tutorial

This tutorial walks through the complete, interactive workflow of turning **Hagiwo's hand-drawn [\$4 Envelope Follower circuit sketch](https://note.com/solder_state/n/n110e9ba066b3?hl=en)** into a manufacturable **6 HP Eurorack Envelope Follower with Skew Limiter** (`2× TL074HIDR`, `30.0 × 108.0 mm` main PCB) and a **mated 3U Matte Black + ENIG Gold FR4 front panel** (`30.0 × 128.5 mm`) using **Python (SKiDL)**, **KiCad 10**, **VectorCraft**, and **AI hardware agent skills**.

| Matte Black + ENIG Front Panel | Main PCB Front (`F.Cu` Controls) | Main PCB Rear (`B.Cu` 50-SMD PCBA) |
| :---: | :---: | :---: |
| ![6 HP Matte Black and ENIG Gold Front Panel](images/panel_front.png){ width="230" } | ![Main PCB Front Controls F.Cu](images/pcb_front.png){ width="230" } | ![Main PCB Rear 50 SMD PCBA B.Cu](images/pcb_back.png){ width="230" } |

!!! info "Interactive Human-in-the-Loop Workflow (Not Unattended Replay)"
    Instead of automating everything behind brittle one-shot prompts, this tutorial teaches an **interactive human-in-the-loop engineering workflow** validated across [16 exported build sessions](https://github.com/domesticmouse/EnvelopeFollower/tree/main/prompts) of the companion [**EnvelopeFollowerWithSkewLimiter**](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter) module (pinned in this repository's `reference/` submodule):

    - **One-at-a-time architectural Q&A** grounded by your hard physical constraints and musical goals (`DesignSpec.md`).
    - **Skill authoring & upstreaming** via `/agy-customizations` (`edit-silkscreen` locally; generic extensions to `eurorack-panel`).
    - **Visual feedback & hybrid GUI + AI co-editing loops** for schematic crops, calibrated mm-ruler silkscreen polishing, and `vectorcraft-cli` panel artwork critiques.
    - **PCB-verified manufacturing artifacts** (`manufacturing/` Gerbers/CPL, THT-only `bom/ibom.html`, and `checklists/` `01`–`05` + `01b`).

---

## Architecture Pipeline

```mermaid
flowchart TD
    S0["0. Hagiwo Sketch<br/>EnvelopeFollower.webp"] --> S1["1. Hardware Agent Skills & Repo Setup<br/>9 core skills + optional vectorcraft-cli,<br/>Living README.md, .gitignore, /agy-customizations"]
    S1 --> S2["2. Multi-Scale Extraction & Critique<br/>EnvelopeFollower.md + EnvelopeFollowerImprovements.md<br/>(KCL checks & Python phase-margin sweeps)"]
    S2 --> S3["3. Interactive DesignSpec & DFT Pass<br/>One-at-a-time Q&A + TP1-TP12 (DNP) -> DesignSpec.md"]
    S3 --> S4["4. SKiDL Capture & KiCad Schematic<br/>envelope_follower.py (80 footprints, 48 nets, 17-row BOM)<br/>+ generate_schematic.py (9-section A3 .kicad_sch & PDF)"]
    S4 --> S5["5. 6 HP Main PCB & Silkscreen Co-Editing<br/>generate_kicad_pcb.py + silk_layout.json<br/>+ /edit-silkscreen Hybrid GUI/AI Polish"]
    S4 --> S6["6. Mated 3U Panel & VectorCraft Artwork<br/>eurorack-panel --blank-front + panel_svg_spec.md<br/>-> /vectorcraft-cli Art -> KiCad SVG Import"]
    S5 --> S6
    S5 --> S7["7. Dual-Board Fab, IBOM & Bring-Up<br/>manufacturing/ Gerbers & CPL, THT bom/ibom.html,<br/>checklists/ (01, 01b, 02-05) & Bench Bring-Up"]
    S6 --> S7
```

---

## Prerequisites

| Tool | Purpose | Notes |
| :--- | :--- | :--- |
| **[KiCad 10.0+](https://www.kicad.org/)** | Schematic/PCB CAD, bundled `pcbnew` Python API, and `kicad-cli` | Installed at `/Applications/KiCad/KiCad.app` on macOS |
| **[`uv`](https://docs.astral.sh/uv/)** | Fast Python environment and package manager | Pin `.venv` to Python `3.12`–`3.14` for prebuilt `skidl` / `h5py` wheels |
| **Node.js (`npx`)** | Installs agent hardware skills from GitHub | Populates `.agents/skills/` and `skills-lock.json` |
| **[`ruff`](https://docs.astral.sh/ruff/)** | Python linter and formatter | Keeps SKiDL, PCB, panel, and artwork scripts clean |
| **`vectorcraft-cli`** *(Optional)* | Scriptable vector graphics engine for Stage 6 front-panel artwork | Needed only for custom Matte Black + ENIG Gold SVG artwork |
| **[`InteractiveHtmlBom`](https://github.com/openscopeproject/InteractiveHtmlBom)** *(v2.11+)* | KiCad PCB Editor plugin for Stage 7 THT assembly map | Generates `bom/ibom.html` filtered to `Manual THT` |

---

## Controls, I/O & Test Points Summary

| Reference | Component / Value | Taper / Type | Function |
| :--- | :--- | :--- | :--- |
| **`RV1`** (`GAIN`) | $100\text{ k}\Omega$ Potentiometer (`Tayda A-1855`) | Audio / Log (`A100K`, `RD901F`) | Input attenuator feeding switchless `×2.00` `U1A` preamp ($Z_{\text{in}} = 90.9\,\text{k}\Omega$) |
| **`RV2`** (`ATK`) | $1\text{ M}\Omega$ Potentiometer (`Tayda A-1672`) | Audio / Log (`A1M`, `RD901F`) | Fail-safe attack rheostat (`0.29–289 ms` `FAST` / `3.0 ms–3.00 s` `SLOW`, $0\rightarrow 5\text{ V}$) |
| **`RV3`** (`REL`) | $1\text{ M}\Omega$ Potentiometer (`Tayda A-1672`) | Audio / Log (`A1M`, `RD901F`) | Fail-safe release rheostat (`0.18–178 ms` `FAST` / `1.84 ms–1.84 s` `SLOW`, $5\rightarrow 0\text{ V}$) |
| **`RV4`** (`OFFSET`) | $10\text{ k}\Omega$ Potentiometer (`Tayda A-8401`) | Linear Center-Detent (`B10K`, `RD901F`) | RC-filtered `±4.98 V` linear offset (`0.00%` gain modulation, `CW = +OUT`) |
| **`SW1`** (`SMOOTH`) | Sub-Mini Vertical SPDT (`Tayda A-6087`) | `Dailywell 2MS1T1B1M2QES` (`2.54 mm`) | UP = `SMOOTH` (`29.0 Hz` split-$R_{\text{env}}$ T-filter, `−11.1 dB @ 100 Hz`, `0.00%` DC loss); DOWN = `RAW` |
| **`SW2`** (`FAST / SLOW`) | Sub-Mini Vertical SPDT (`Tayda A-6087`) | `Dailywell 2MS1T1B1M2QES` (`2.54 mm`) | UP = `SLOW` (`C12+C13` `4.4 µF` $\parallel$ `C11` `470 nF` = `4.87 µF`); DOWN = `FAST` (`470 nF`) |
| **`LED1`** (`OUT`) | `3 mm` 2-Pin Anti-Parallel Red/Green (`Tayda A-1076`) | Bipolar THT (In-Loop `U2D`) | Post-offset active $V$-to-$I$ indicator (`R33 = 2.2 kΩ`, `+V = Green`, `−V = Red`, `0.00 mA` idle) |
| **`J1`** (`IN`) | `3.5 mm` Mono Jack (`WQP-PJ398SM`) | Switched THT (`TN → GND`) | AC-coupled audio input (`C7 = 470 nF` film, $f_c = 3.72\,\text{Hz}$, $Z_{\text{in}} = 90.9\,\text{k}\Omega$) |
| **`J2`** (`SLEW IN`) | `3.5 mm` Mono Jack (`WQP-PJ398SM`) | Switched THT (Normaled to FWR) | Unpatched = `U1C` FWR via `R15` (`1 kΩ`); patched = DC-coupled `1.00 MΩ` bipolar slew input |
| **`J3`** (`OUT`) | `3.5 mm` Mono Jack (`WQP-PJ398SM`) | Switched THT (`TN = NC`) | Non-inverted envelope/skew output $+(V_{\text{env}} + V_{\text{off}})$ via `R32` (`1 kΩ`) |
| **`J4`** (`INV_OUT`) | `3.5 mm` Mono Jack (`WQP-PJ398SM`) | Switched THT (`TN = NC`) | Inverted sidechain ducking output $-(V_{\text{env}} + V_{\text{off}})$ via `R25` (`1 kΩ`) |
| **`J_PWR`** (`PWR`) | `2×5` Shrouded IDC Header (`2.54 mm`) | `10-Pin` Eurorack (`B.Cu`) | $\pm 12\text{ V}$ & `GND` entry (`B5819W` + `10 Ω` / `47 µF` RC → `±11.54 V`) |
| **`TP1`–`TP12`** (`DNP`) | `Ronghe RH-5001` (`LCSC C5199801`) | Optional THT Loops (`1.0 mm` drill) | Rear `B.Cu` probing (`GND`, `+12V`, `-12V`, `PRE`, `RECT`, `ENV`, `INV`, `OUT`, `HWR`, `DRV`, `OFF`, `GND2`) |

---

## Stage-by-Stage Guide

1. **[Stage 1: Hardware Agent Skills & Repo Setup](tutorial/stage-1-agent-skills.md)** — Install the 9 core hardware skills (plus optional `vectorcraft-cli`), set up `.gitignore` and a living `README.md` context map, learn when to author repo-local skills vs. extend/upstream existing skills with `/agy-customizations`, and smoke-test skill upgrades before committing `skills-lock.json`.
2. **[Stage 2: Sketch Extraction & Circuit Critique](tutorial/stage-2-circuit-upgrades.md)** — Extract Hagiwo's sketch (`EnvelopeFollower.md`) with multi-scale Pillow crops, KCL cross-checks, and a Python BOM↔netlist pin-completeness assertion; then audit the analog circuit (`EnvelopeFollowerImprovements.md`) with Tier 1–3 triage and Python Bode/Nyquist phase-margin stability sweeps.
3. **[Stage 3: Interactive DesignSpec & Test Points](tutorial/stage-3-bom-and-dfm.md)** — Walk through `EnvelopeFollowerImprovements.md` one improvement at a time via interactive Q&A (upfront 6 HP / `2× TL074H` / musical context constraints, strategic UI deferral, live vendor checks) and add 12 probe-safe `DNP` test points (`TP1`–`TP12`) directly into a unified `DesignSpec.md`.
4. **[Stage 4: SKiDL Capture & KiCad Schematic](tutorial/stage-4-skidl.md)** — Hand off `DesignSpec.md` to `/skidl`, build a project-local `Dailywell 2MS1` switch footprint (`Eurorack_Custom.pretty`), enforce a strict 3-Extended-SKU budget across `50` SMDs (`17` BOM rows, `80` netlist components, `48` nets), and drive a 9-section A3 `.kicad_sch` + PDF from `build_circuit()` with 4-layer netlist parity and visual crop verification.
5. **[Stage 5: 6 HP PCB, `silk_layout.json` & `/edit-silkscreen`](tutorial/stage-5-schematic-and-pcb.md)** — Generate the `30.00 × 108.00 mm` main PCB (`83` footprints including `3` fiducials) with cross-layer collision checks, BFS routing debugging, and 3D render gates; extract silkscreen coordinates into declarative `silk_layout.json` (`--silk-only`, `--sync-silk`, `--check-silk`, `--show-silk`); and mint `/edit-silkscreen` for hybrid KiCad GUI + AI ruler-preview polishing.
6. **[Stage 6: Mated 3U Front Panel & VectorCraft Artwork](tutorial/stage-6-front-panel.md)** — Audit hardware switch drill mismatches (`5.2 mm` sub-mini toggle vs. `6.2 mm` default), extend and upstream `eurorack-panel` (`--blank-front`, `--spec-md`, `--drill`, obstacle-aware `B.SilkS`), design Matte Black + ENIG Gold front artwork with `/vectorcraft-cli` (`40 px/mm` clearance audit + multi-turn visual critique), and import `F.SilkS`/`F.Mask` polygons into KiCad via `SHAPE_POLY_SET` with `(stackup ...)` injection.
7. **[Stage 7: Checklists, IBOM, Fabrication & Bring-Up](tutorial/stage-7-manufacturing.md)** — Export upload-ready dual-board Gerbers, routed-slot Excellon drills, and bottom-side CPL (`manufacturing/`), filter `InteractiveHtmlBom` strictly to the `18` `Manual THT` parts (`bom/ibom.html`), generate PCB-verified `checklists/` (`01`, `01b`, `02`–`05`), and finish with reproducible `images/` renders and automated link verification.

### Optional Explorations

- **[Optional Direction: AC/DC Input Coupling Mode](tutorial/optional-dc-coupled-mode.md)** — How to branch off `EnvelopeFollowerImprovements.md` when exploring optional features, and how adding a `C7` AC/DC bypass switch (`SW3`) complements the main build's dedicated `J2` (`SLEW IN`) jack by unlocking DC-coupled precision full-wave CV rectification (`2×` LFO frequency doubling).

### Technical References

- **[Netlist, BOM & Capture Guide](reference/netlist-and-bom.md)** — Complete BOM (`50` `B.Cu` SMD + `18` Manual THT + `12` `DNP` test points + `3` fiducials = `83` PCB footprints), exact 17-row `jlcpcb_bom.csv`, all `48` active nets with IC pin numbers, manual KiCad capture checklist, and full silkscreen schedule.
- **[PCB & Fabrication Checklist](reference/build-checklist.md)** — End-to-end engineering checklist covering SKiDL capture, 9-section schematic parity, `silk_layout.json` + `/edit-silkscreen`, Matte Black + ENIG front-panel SVG import, `bom/ibom.html`, and dual-board `manufacturing/` export.
- **[GitHub Repository](https://github.com/domesticmouse/EnvelopeFollower)** — Tutorial source, [16 conversation traces](https://github.com/domesticmouse/EnvelopeFollower/tree/main/prompts), pinned [`reference/`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter) companion build, and [Apache 2.0 License](https://github.com/domesticmouse/EnvelopeFollower/blob/main/LICENSE).
