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

| Skill | Source | Key Scripts & Capabilities | When It Runs |
| :--- | :--- | :--- | :--- |
| **`skidl`** | `domesticmouse/skills` | `scripts/jlcpcb_search.py` for live stock/Basic vs. Extended lookup; KiCad 10 symbol/footprint idioms; `ERC()` + BOM export | [Stage 3](stage-3-skidl.md) & [Stage 4](stage-4-schematic-and-pcb.md) |
| **`eurorack-panel`** | `domesticmouse/skills` | `scripts/generate_eurorack_panel.py` (`--inspect`, `--drc`, `--gerber-dir`, `--zip`) and Doepfer A-100 3U mechanical specs | [Stage 6](stage-6-front-panel.md) |
| **`kicad`** | `aklofas/kicad-happy` | `scripts/analyze_schematic.py`, `scripts/analyze_pcb.py`, `scripts/cross_analysis.py`, `scripts/analyze_gerbers.py` | [Stage 5](stage-5-routing-and-drc.md) & [Stage 6](stage-6-front-panel.md) |
| **`bom`** | `aklofas/kicad-happy` | BOM deduplication, `DNP` handling, KiCad property sync, and grouped fabrication CSV generation | [Stage 2](stage-2-circuit-upgrades.md) & [Stage 3](stage-3-skidl.md) |
| **`datasheets`** | `aklofas/kicad-happy` | Extracts verified pinouts, absolute maximum ratings, and package footprints from IC/diode datasheets (`TL074H`, `BAT54S`, `RH-5001`) | [Stage 2](stage-2-circuit-upgrades.md) & [Stage 3](stage-3-skidl.md) |
| **`jlcpcb`** | `aklofas/kicad-happy` | Optimizes part choices for JLCPCB Economic single-sided PCBA (`Basic` vs. `Extended` feeder fees), rotation offsets, and silkscreen DFM rules | [Stage 2](stage-2-circuit-upgrades.md), [Stage 4](stage-4-schematic-and-pcb.md) & [Stage 7](stage-7-manufacturing.md) |
| **`lcsc`** | `aklofas/kicad-happy` | Queries live LCSC Electronics stock/pricing by `Cxxxxx` or MPN and verifies drop-in fallback parts | [Stage 2](stage-2-circuit-upgrades.md) & [Stage 3](stage-3-skidl.md) |

!!! tip "Keep `README.md` as a Living Build Log"
    As you work through Stages 2–7 across separate agent sessions, treat your repository's `README.md` as a **living build log**: after each step, record the prompt you used, key design choices (such as THT vs. SMD decisions or test-point parts), and links to the generated files, then commit right away. When you open a fresh conversation for the next stage, your agent reads `README.md` and automatically inherits the full project context without repeating earlier prompts.
