# Stage 1: Installing the Hardware Agent Skills

LLMs working without domain tooling tend to hallucinate KiCad S-expression syntax, guess footprint pinouts, overlook mechanical bushing offsets, verify BOM parts from stale memory, or pick out-of-stock LCSC components. Installing dedicated **hardware agent skills** gives your coding agent verified reference docs, datasheet extractors, live JLCPCB/LCSC catalog search tools, and deterministic Python PCB/Gerber analyzers inside `.agents/skills/`.

Install all **7 hardware design and fabrication skills** from [`domesticmouse/skills`](https://github.com/domesticmouse/skills) and [`aklofas/kicad-happy`](https://github.com/aklofas/kicad-happy) (tracked in [`skills-lock.json`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/skills-lock.json)):

```bash
npx skills add domesticmouse/skills --skill skidl --skill eurorack-panel
npx skills add aklofas/kicad-happy --skill kicad --skill bom --skill datasheets --skill jlcpcb --skill lcsc
```

Verify the installed directory layout:

```text
.agents/skills/
├── bom/               # BOM lifecycle management, KiCad symbol properties & fab export
├── datasheets/        # Structured pinout & electrical spec extraction from PDF datasheets
├── eurorack-panel/    # Main-PCB inspection, 3U panel generation, zone fill & DRC
├── jlcpcb/            # JLCPCB PCBA Basic vs. Extended selection, BOM/CPL & DFM rules
├── kicad/             # Schematic, PCB, Gerber, cross-domain & DFM analyzers
├── lcsc/              # Live LCSC stock/pricing lookup (Cxxxxx / MPN) & datasheet sync
└── skidl/             # SKiDL circuit coding, symbol search & JLCPCB/LCSC catalog search
```

Each installed skill equips the agent with specialized reference documentation and deterministic helper scripts used across the tutorial stages:

- **`skidl` (`domesticmouse/skills`)**: Provides `scripts/jlcpcb_search.py` for live stock and Basic vs. Extended catalog lookups, KiCad 10 symbol and footprint idioms, electrical rules checking (`ERC()`), and automated BOM export during [Stage 4](stage-4-skidl.md) and [Stage 5](stage-5-schematic-and-pcb.md).
- **`eurorack-panel` (`domesticmouse/skills`)**: Supplies `scripts/generate_eurorack_panel.py` (`--inspect`, `--drc`, `--gerber-dir`, `--zip`) along with Doepfer A-100 3U mechanical specifications to generate and verify the mated front panel in [Stage 6](stage-6-front-panel.md).
- **`kicad` (`aklofas/kicad-happy`)**: Bundles deterministic Python analyzers—`scripts/analyze_schematic.py`, `scripts/analyze_pcb.py`, `scripts/cross_analysis.py`, and `scripts/analyze_gerbers.py`—to audit schematic-to-PCB parity, copper routing, and Gerbers in [Stage 5](stage-5-schematic-and-pcb.md) and [Stage 6](stage-6-front-panel.md).
- **`bom` (`aklofas/kicad-happy`)**: Handles BOM deduplication, `DNP` component filtering, KiCad symbol property synchronization, and grouped fabrication CSV generation across [Stage 3](stage-3-bom-and-dfm.md) and [Stage 4](stage-4-skidl.md).
- **`datasheets` (`aklofas/kicad-happy`)**: Extracts verified pinouts, absolute maximum ratings, and package footprints from IC and diode PDF datasheets (`TL074H`, `BAT54S`, `RH-5001`) during [Stage 2](stage-2-circuit-upgrades.md), [Stage 3](stage-3-bom-and-dfm.md), and [Stage 4](stage-4-skidl.md).
- **`jlcpcb` (`aklofas/kicad-happy`)**: Optimizes component choices for JLCPCB Economic single-sided PCBA (`Basic` vs. `Extended` feeder fees), footprint rotation offsets, and dual-sided silkscreen DFM rules in [Stage 3](stage-3-bom-and-dfm.md), [Stage 5](stage-5-schematic-and-pcb.md), and [Stage 7](stage-7-manufacturing.md).
- **`lcsc` (`aklofas/kicad-happy`)**: Queries live LCSC Electronics stock and pricing by `Cxxxxx` part number or MPN and verifies drop-in fallback components in [Stage 3](stage-3-bom-and-dfm.md) and [Stage 4](stage-4-skidl.md).

!!! tip "Keep `README.md` as a Living Build Log"
    As you work through Stages 2–7 across separate agent sessions, treat your repository's `README.md` as a **living build log**: after each step, record the prompt you used, key design choices (such as THT vs. SMD decisions or test-point parts), and links to the generated files, then commit right away. When you open a fresh conversation for the next stage, your agent reads `README.md` and automatically inherits the full project context without repeating earlier prompts.
