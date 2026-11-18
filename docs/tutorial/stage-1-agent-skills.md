# Stage 1: Installing the Hardware Agent Skills

LLMs working without domain tooling tend to hallucinate KiCad S-expression syntax, guess footprint pinouts, overlook mechanical bushing offsets, or pick out-of-stock parts. Installing dedicated **agent skills** gives your coding agent verified reference docs, CLI wrappers, and deterministic Python analyzers inside `.agents/skills/`.

Install the three hardware skills recorded in [`skills-lock.json`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/skills-lock.json):

```bash
npx skills add domesticmouse/skills --skill skidl --skill eurorack-panel
npx skills add aklofas/kicad-happy --skill kicad
```

Verify the installed directory layout:

```text
.agents/skills/
├── skidl/             # SKiDL circuit coding, symbol search & JLCPCB/LCSC catalog search
├── kicad/             # Schematic, PCB, Gerber, cross-domain & DFM analyzers
└── eurorack-panel/    # Main-PCB inspection, 3U panel generation, zone fill & DRC
```

| Skill | Key Scripts & Capabilities | When It Runs |
| :--- | :--- | :--- |
| [`skidl`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/.agents/skills/skidl/SKILL.md) | `scripts/jlcpcb_search.py` for live LCSC stock/Basic vs. Extended tier lookup; KiCad 10 symbol/footprint idioms; `ERC()` + BOM export | [Stage 3](stage-3-skidl.md) & [Stage 4](stage-4-schematic-and-pcb.md) |
| [`kicad`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/.agents/skills/kicad/SKILL.md) | `scripts/analyze_schematic.py`, `scripts/analyze_pcb.py`, `scripts/cross_analysis.py`, `scripts/analyze_gerbers.py` | [Stage 5](stage-5-routing-and-drc.md) & [Stage 6](stage-6-front-panel.md) |
| [`eurorack-panel`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/.agents/skills/eurorack-panel/SKILL.md) | `scripts/generate_eurorack_panel.py` (`--inspect`, `--drc`, `--gerber-dir`, `--zip`) and Doepfer A-100 mechanical spec | [Stage 6](stage-6-front-panel.md) |
