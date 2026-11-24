# Stage 1: Installing the Hardware Agent Skills & Repo Setup

LLMs working without domain tooling tend to hallucinate KiCad S-expression syntax, guess footprint pinouts, overlook mechanical bushing offsets, verify BOM parts from stale memory, or pick out-of-stock LCSC components. Installing dedicated **hardware agent skills**—and setting up a few lightweight repository habits before touching schematics—keeps every downstream stage grounded, deterministic, and easy to resume across chat sessions.

---

## Step 1.1: Installing the Core Hardware Skills (Plus Optional `vectorcraft-cli`)

Install the **9 core hardware design and fabrication skills** from the [`domesticmouse/skills` hardware pack](https://github.com/domesticmouse/skills/tree/main/packs/hardware) and [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy) (recorded in `skills-lock.json`):

```bash
npx skills add domesticmouse/skills/packs/hardware --skill skidl --skill kicad-pcbnew-layout --skill kicad-silkscreen-markup --skill eurorack-panel
npx skills add aklofas/kicad-happy --skill kicad --skill bom --skill datasheets --skill jlcpcb --skill lcsc
```

### Optional Front-Panel Artwork Skill (`vectorcraft-cli`)

If you plan to design custom **Matte Black + ENIG Gold + White Silkscreen** front-panel artwork in [Stage 6](stage-6-front-panel.md) instead of using the standard auto-labeled faceplate, also install the `vectorcraft-cli` skill (alongside the `vectorcraft-cli` binary):

```bash
npx skills add domesticmouse/skills --skill vectorcraft-cli
```

Verify the installed directory layout:

```text
.agents/skills/
├── bom/                      # BOM deduplication, DNP filtering & JLCPCB PnP translation
├── datasheets/               # Structured pinout & electrical spec extraction from PDF datasheets
├── edit-silkscreen/          # (Created locally in Stage 5 via /agy-customizations)
├── eurorack-panel/           # Main-PCB inspection, 3U panel generation, --blank-front, --spec-md & DRC
├── jlcpcb/                   # JLCPCB Economic PCBA Basic vs. Extended rules, rotations & DFM checks
├── kicad/                    # Schematic, PCB, Gerber, cross-domain parity & DFM analyzers
├── kicad-pcbnew-layout/      # Programmatic KiCad 10 pcbnew layout, A* routing & stitched GND pours
├── kicad-silkscreen-markup/  # Density-adaptive silkscreen (value-only passives), polarity & fab notes
├── lcsc/                     # Live LCSC stock/pricing lookup (Cxxxxx / MPN) & datasheet sync
├── skidl/                    # SKiDL circuit coding, symbol search & JLCPCB/LCSC catalog search
└── vectorcraft-cli/          # (Optional) Scripted SVG/artwork generation & Pathfinder knockouts
```

Each installed skill equips the agent with specialized reference documentation and deterministic helper scripts:

- **`skidl` (`domesticmouse/skills/packs/hardware`)**: Supplies `scripts/jlcpcb_search.py` for live stock and Basic vs. Extended catalog lookups, KiCad 10 symbol/footprint idioms, `ERC()`, and BOM export in [Stage 4](stage-4-skidl.md).
- **`kicad-pcbnew-layout` (`domesticmouse/skills/packs/hardware`)**: Supplies `scripts/pcbnew_layout_template.py` and KiCad 10 API/DFM reference guides (`references/kicad10_pcbnew_api.md`, `references/routing_and_dfm_patterns.md`) for programmatic `.net`-to-`.kicad_pcb` placement, routing, and stitched `GND` zones in [Stage 5](stage-5-schematic-and-pcb.md).
- **`kicad-silkscreen-markup` (`domesticmouse/skills/packs/hardware`)**: Supplies `scripts/silk_annotator.py` (`SilkGrid` pad/outline/`.Fab` keepouts, stroke-font measurement, `place_ref_val_pair()`, `compact_passive_value()`, `add_standard_fab_notes()`, and `--inspect` collision/tether auditing) in [Stage 5](stage-5-schematic-and-pcb.md).
- **`eurorack-panel` (`domesticmouse/skills/packs/hardware`)**: Supplies `scripts/generate_eurorack_panel.py` (`--inspect`, `--blank-front`, `--spec-md`, `--drill`, `--drc`, obstacle-aware rear `B.SilkS`) and Doepfer A-100 3U specifications in [Stage 6](stage-6-front-panel.md).
- **`kicad` (`aklofas/kicad-happy`)**: Bundles deterministic Python analyzers (`analyze_schematic.py`, `analyze_pcb.py`, `cross_analysis.py`, `analyze_gerbers.py`) across [Stages 4–7](stage-7-manufacturing.md).
- **`bom`, `datasheets`, `jlcpcb`, `lcsc` (`aklofas/kicad-happy`)**: Handle live LCSC lookups (`search_lcsc.py`), datasheet pinout validation (`TL074H`, `BAT54S`, `B5819W`, `RH-5001`), Economic PCBA rules, and `translate_bom_pnp.py` CPL generation across [Stages 2–7](stage-7-manufacturing.md).

---

## Step 1.2: Repo Bootstrap Habits (Before Stage 2)

Before extracting your first circuit from a sketch, adopt two habits observed across every trace in `prompts/`:

### 1. Maintain `README.md` as a "Living Context Map"

Fresh chat sessions start with zero memory of what files you generated earlier. Initialize `README.md` right after installing your skills so it indexes every source file, script, skill, and preview render in your workspace:

!!! prompt "AI Agent Prompt"
    Please update `@[README.md]` to track the files and skills in this directory so future prompts know where to look for things.

From [Stage 2](stage-2-circuit-upgrades.md) onward, end every major stage or iteration prompt with **"update `@[README.md]` and git commit"**. Keeping `README.md` current turns `@[README.md]` into a compact, zero-hallucination context anchor for any new conversation.

### 2. Configure `.gitignore` & Git Checkpointing Up Front

KiCad 10, SKiDL, and Python skill scripts generate lockfiles, autosave histories, and bytecode caches that should never clutter diffs or get staged accidentally. Create `.gitignore` in Stage 1:

```gitignore
__pycache__/
.venv/
.history/
*.kicad_prl
~*.lck
skidl_REPL.*
*.log
.agents/skills/**/__pycache__/
```

When working through later stages, follow two Git hygiene habits:

- **Checkpoint clean baselines before major refactors:** Always `git commit` working generated outputs before structural shifts (for example, after verifying the initial PCB before introducing `silk_layout.json` in [Stage 5](stage-5-schematic-and-pcb.md), and after approving `panel_art/` PNG previews before importing SVG polygons into KiCad in [Stage 6](stage-6-front-panel.md)).
- **Stage explicit file paths (`git add <paths>`):** Never blind-run `git add -A` when KiCad GUI is open (`*.kicad_pro` auto-touches `"top_level_sheets"` or GUI state) or while iterating on local skills—stage explicit paths and inspect `git diff --cached --stat`.

---

## Step 1.3: Authoring vs. Extending Skills (`/agy-customizations`)

As your hardware workflow matures, you will hit two distinct customization needs—both handled via `/agy-customizations` rather than bloating always-on workspace rules:

| Need | Pattern | Example in This Tutorial | Key Verification |
| :--- | :--- | :--- | :--- |
| **Project-specific interactive UX** | **Author a repo-local skill** (`.agents/skills/<name>/SKILL.md`) | [Stage 5](stage-5-schematic-and-pcb.md) creates **`/edit-silkscreen`** (`SKILL.md` + `render_silk_preview.py`) for moving labels one-by-one in `silk_layout.json`. | Progressive disclosure: `0` context overhead until you type `/edit-silkscreen`. |
| **Reusable tool capability** | **Extend an existing skill generically & upstream it** | [Stage 6](stage-6-front-panel.md) extends **`eurorack-panel`** (`--blank-front`, `--spec-md`, `--drill`, `switch_submini`, obstacle-aware `B.SilkS`) and syncs it to `../skills/`. | Test under **KiCad's bundled Python 3.9** (catching Python 3.10+ syntax like `zip(..., strict=True)`), then run `ruff` + `diff -ru` parity checks against upstream. |

---

## Step 1.4: Post-Upgrade Skill Smoke-Testing

Whenever you pull upstream skill updates (`npx skills update`), **smoke-test read-only verification commands before committing `skills-lock.json`**. Upstream hardware skills tighten DFM and keepout rules over time; running a smoke test immediately reveals whether your existing board triggers newly enforced checks:

```bash
# Re-verify read-only silkscreen & inspection scripts after updating skills
python3 generate_kicad_pcb.py --show-silk U1 RV1
python3 generate_kicad_pcb.py --check-silk
```

For example, in the reference build ([Trace 07 Turn 7](https://github.com/domesticmouse/EnvelopeFollower/blob/main/prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md)), running `/edit-silkscreen` and `--check-silk` right after syncing upstream `kicad-silkscreen-markup` confirmed all script signatures remained intact while immediately catching **39 newly enforced THT `.Fab` / expanded pad keepout hits** and **9 QR via/track hits**—letting the builder triage and resolve them cleanly before committing `skills-lock.json`.
