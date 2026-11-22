# Eurorack Envelope Follower Tutorial

An end-to-end, interactive human-in-the-loop hardware engineering tutorial demonstrating how to take **Hagiwo's hand-drawn [\$4 Envelope Follower sketch](https://note.com/solder_state/n/n110e9ba066b3?hl=en)** ([`EnvelopeFollower.webp`](EnvelopeFollower.webp)) from initial circuit critique to a manufacturable **6 HP Eurorack Envelope Follower with Skew Limiter** (`2× TL074HIDR`, `30.0 × 108.0 mm` main PCB) and a **mated Matte Black + ENIG Gold 3U front panel** (`30.0 × 128.5 mm`) using **Python (SKiDL)**, **KiCad 10**, **VectorCraft**, and **AI hardware agent skills**.

> **Read the full interactive tutorial online:** **[domesticmouse.github.io/EnvelopeFollower](https://domesticmouse.github.io/EnvelopeFollower/)** *(or read from [`docs/index.md`](docs/index.md) / serve locally with MkDocs Material).*

<table align="center">
  <tr>
    <th>Matte Black + ENIG Front Panel</th>
    <th>Main PCB Front (<code>F.Cu</code> Controls)</th>
    <th>Main PCB Rear (<code>B.Cu</code> 50-SMD PCBA)</th>
  </tr>
  <tr>
    <td align="center"><img src="docs/images/panel_front.png" alt="6 HP Matte Black and ENIG Gold Front Panel" width="220" /></td>
    <td align="center"><img src="docs/images/pcb_front.png" alt="Main PCB Front Controls F.Cu" width="220" /></td>
    <td align="center"><img src="docs/images/pcb_back.png" alt="Main PCB Rear 50 SMD PCBA B.Cu" width="220" /></td>
  </tr>
</table>

---

## Companion Reference Hardware: `EnvelopeFollowerWithSkewLimiter`

Every BOM line, KiCad script, verification pitfall, Gerber archive, and assembly checklist in this tutorial comes directly from the completed companion module [**`domesticmouse/EnvelopeFollowerWithSkewLimiter`**](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter), pinned as a Git submodule at [`reference/`](reference) (commit `4a02c46`):

- **Analog Signal Flow:** `J1` (`IN`, `J1.TN → GND`, `3.39 Hz` `C7 = 470 nF` film HPF) -> `RV1` (`GAIN`, `A100K`) -> switchless `×2.00` AC / `×1.00` DC preamp (`U1A`, `C9 = 10 µF`) -> `0.1%`-matched `BAT54S` precision full-wave rectifier (`U1B`/`U1C`) -> **`J2` (`SLEW IN` normalled break-out)** -> active slew/skew limiter (`U1D`/`U2A`, `C10 = 2.2 nF`, `1N4148W` `D4`/`D5`, independent `RV2` `ATK` & `RV3` `REL` `A1M` fail-safe rheostats, `SW2` `FAST`/`SLOW`) -> switchable `29 Hz` **`SW1` (`SMOOTH`)** T-filter -> virtual-ground bipolar `RV4` (`OFFSET` `B10K` center-detent, `±4.98 V`) summer (`U2B` -> `J4` `INV OUT`) & unity inverter (`U2C` -> `J3` `OUT`) + active in-loop bi-color `LED1` (`U2D`, Tayda `A-1076`).
- **Parts & Manufacturability Breakdown:** `80` netlist components (`83` PCB footprints incl. `3` `B.Cu` fiducials `FID1`–`FID3`) across `48` active nets -> **`50` Bottom-Side Economic SMDs** across `17` rows in [`jlcpcb_bom.csv`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/jlcpcb_bom.csv) (strictly **`3` Extended SKUs**: `C2878713` `TL074HIDR`, `C83935` `BAT54S`, `C95204` `10k 0.1%`), **`18` Manual THT** parts ([`bom/ibom.html`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/bom/ibom.html)), and **`12` DNP Keystone test points** (`TP1`–`TP12`).
- **Mated 3U Front Panel:** Generated via `--blank-front` (`generate_eurorack_panel.py`), authored in Dark Techno / Brutalist style with `vectorcraft-cli` (`40 px/mm` `>= 0.60 mm` ink-to-mask clearance audit), fractured via `SHAPE_POLY_SET` into KiCad 10 (`104` `F.SilkS` + `33` `F.Mask` ENIG openings + `5` rear `B.SilkS` markings), and bundled with upload-ready dual-board fabrication files in [`manufacturing/`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/main/manufacturing) and PCB-verified [`checklists/`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/main/checklists).

---

## Tutorial Map

| Section | Focus | File |
| :--- | :--- | :--- |
| **Overview** | Pipeline flowchart, prerequisites & panel I/O summary | [`docs/index.md`](docs/index.md) |
| **Stage 1** | Core AI hardware skills, `/agy-customizations` & post-upgrade smoke testing | [`docs/tutorial/stage-1-agent-skills.md`](docs/tutorial/stage-1-agent-skills.md) |
| **Stage 2** | Sketch review, KCL audit, Python Bode/Nyquist analysis & doc linting | [`docs/tutorial/stage-2-circuit-upgrades.md`](docs/tutorial/stage-2-circuit-upgrades.md) |
| **Stage 3** | Interactive Q&A -> `DesignSpec.md`, `TP1`–`TP12` test strategy & BOM↔Netlist checks | [`docs/tutorial/stage-3-bom-and-dfm.md`](docs/tutorial/stage-3-bom-and-dfm.md) |
| **Stage 4** | SKiDL `80`-part capture, custom Dailywell `2MS1` footprint & `9`-section schematic | [`docs/tutorial/stage-4-skidl.md`](docs/tutorial/stage-4-skidl.md) |
| **Stage 5** | KiCad `83`-footprint PCB, hybrid `silk_layout.json` + `/edit-silkscreen` polish | [`docs/tutorial/stage-5-schematic-and-pcb.md`](docs/tutorial/stage-5-schematic-and-pcb.md) |
| **Stage 6** | Blank-front `5.2 mm` switch spec, `vectorcraft-cli` art & `SHAPE_POLY_SET` import | [`docs/tutorial/stage-6-front-panel.md`](docs/tutorial/stage-6-front-panel.md) |
| **Stage 7** | Dual-board `manufacturing/` Gerbers, PCB-verified `checklists/`, `ibom.html` & renders | [`docs/tutorial/stage-7-manufacturing.md`](docs/tutorial/stage-7-manufacturing.md) |
| **Optional Branch** | Adding `SW3` (`AC / DC`) across `C7` for `2×` LFO FWR waveshaping | [`docs/tutorial/optional-dc-coupled-mode.md`](docs/tutorial/optional-dc-coupled-mode.md) |
| **Reference** | Full `80`-part BOM, `17`-row `jlcpcb_bom.csv`, `48` nets & `silk_layout.json` | [`docs/reference/netlist-and-bom.md`](docs/reference/netlist-and-bom.md) |
| **Build Checklist** | Master 4-phase engineering & fabrication sign-off checklist | [`docs/reference/build-checklist.md`](docs/reference/build-checklist.md) |

---

## Repository Structure

```text
EnvelopeFollower/
├── docs/                                # MkDocs Material tutorial source & curated 8 renders
│   ├── index.md                         # Overview, controls/TP tables & workflow diagram
│   ├── images/                          # EnvelopeFollower.webp + 7 panel/PCB/schematic PNGs
│   ├── javascripts/mathjax.js           # KaTeX/Arithmatex math rendering config
│   ├── tutorial/                        # Stage 1–7 interactive guides + optional SW3 note
│   └── reference/                       # Complete BOM, 48-net connectivity, silk schedule & build checklist
├── prompts/                             # 16 exported AI-assisted hardware engineering session traces
│   ├── README.md                        # Chronological index of sessions 01–16
│   └── 01-*.md ... 16-*.md              # Step-by-step transcripts backing Stages 1–7
├── reference/                           # Git submodule -> domesticmouse/EnvelopeFollowerWithSkewLimiter (4a02c46)
├── .agents/skills/agy-brain-explorer/   # Session transcript explorer & Markdown exporter skill
├── analysis/capability_mode.json        # Capability metadata
├── EnvelopeFollower.webp                # Original Hagiwo hand-drawn schematic reference
├── PotentialImprovements.md             # Standalone engineering note on DC-coupled FWR bypass
├── TutorialUpdateTodo.md                # Living editorial roadmap & verification ledger for this rewrite
├── mkdocs.yml                           # MkDocs Material site configuration & strict nav
├── skills-lock.json                     # Pinned upstream hardware skill versions
└── LICENSE                              # Apache License 2.0
```

---

## Building & Serving Docs Locally

Requires Python and [`uv`](https://docs.astral.sh/uv/) (or `pip install mkdocs-material`):

```bash
# Clone with companion reference submodule
git clone --recurse-submodules https://github.com/domesticmouse/EnvelopeFollower.git
cd EnvelopeFollower

# Live-reload preview
uvx --with mkdocs-material mkdocs serve

# Strict verification build (catches broken links, missing images, invalid nav)
uvx --with mkdocs-material mkdocs build --strict
```

## Contributing & Exploration Resources

- **Session Traces ([`prompts/README.md`](prompts/README.md)):** Every recommendation, DRC discovery, VectorCraft batch loop, and silkscreen tweak in this tutorial cites the exact exported trace (`01`–`16`) exported via [`.agents/skills/agy-brain-explorer/SKILL.md`](.agents/skills/agy-brain-explorer/SKILL.md).
- **Standalone Notes:** See [`PotentialImprovements.md`](PotentialImprovements.md) for the original Hagiwo-RefDes `SW1`-across-`C1` analysis, [`docs/tutorial/optional-dc-coupled-mode.md`](docs/tutorial/optional-dc-coupled-mode.md) for its `EnvelopeFollowerWithSkewLimiter` translation (`SW3` across `C7`), and [`TutorialUpdateTodo.md`](TutorialUpdateTodo.md) for the completed rewrite ledger.

## License

Licensed under the [Apache License 2.0](LICENSE).
