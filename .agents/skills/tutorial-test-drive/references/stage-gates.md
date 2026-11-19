# Stage-by-Stage Clean-Room Gates & Pitfalls (`Stages 1–7`)

Always read the corresponding `docs/tutorial/stage-N-*.md` file at runtime to extract exact prompts verbatim. Do **not** hardcode prompt text from memory when dispatching subagents.

---

## Stage 1: Hardware Agent Skills (`docs/tutorial/stage-1-agent-skills.md`)

- **Init:** `python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py init-stage 1`
- **Output directory:** `stages/stage-1/`
- **Execution:** `tutorial-runner` runs both `npx skills add` commands inside `stages/stage-1/`.
- **Expected layout:**
  - `stages/stage-1/skills-lock.json` (9 entries)
  - `stages/stage-1/.agents/skills/` containing 9 copied directories (`bom`, `datasheets`, `eurorack-panel`, `jlcpcb`, `kicad`, `kicad-pcbnew-layout`, `kicad-silkscreen-markup`, `lcsc`, `skidl`), each with `SKILL.md`
  - All 10 referenced helper scripts/docs present (`check_stage.py check-stage1` verifies all of them + `0` symlinks)
- **Watch-outs:**
  - Verify root `.agents/skills/` and root `skills-lock.json` remain untouched immediately after the first `npx skills add` call (`check_stage.py check-clean-root`).
  - Pass `-y` / `--agent` only if running outside an auto-detected agent TTY causes interactive prompts (log if needed).

---

## Stage 2: Sketch Extraction & Circuit Upgrades (`docs/tutorial/stage-2-circuit-upgrades.md`)

- **Init:** `python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py init-stage 2` (clones full `stages/stage-1/` directory, including `.agents/skills/` and `skills-lock.json`, into `stages/stage-2/`)
- **Output directory:** `stages/stage-2/`
- **Prep:** Download `EnvelopeFollower.webp` inside `stages/stage-2/` using the `curl -LO` command in Stage 2; verify with `file` (`Web/P image`, not `HTML document`).
- **Turns (3 fresh subagents):**
  1. Step `2.1` → `EnvelopeFollower.md` (6 op-amp stages, 23 fixed resistors, 4 caps, 4 pots, 3× `1N4148`, 1× LED, 3 jacks).
  2. Step `2.2` → `EnvelopeFollowerImprovements.md` (`OFFSET` loading/skew, passive peak-detector deadzone & `ATK`/`Release` divider collapse, `R9` sag, `ATK = 0 Ω` shorting, `-2.79 V` LED quiescent glow, rectifier symmetry, pot tapers).
  3. Step `2.3` → updates `EnvelopeFollowerImprovements.md` (reverse-polarity protection, local `100 nF` IC decoupling, gain-floor limiting, output protection, unused op-amp termination).
- **Gate checks:** Both files created; `C4` (`-12V`) polarized orientation (`+` on `GND`, `-` on `-12V`) and diode orientations (`D1`–`D3`) match `EnvelopeFollower.webp`.

---

## Stage 3: JLCPCB BOM, Walkthrough & DFM (`docs/tutorial/stage-3-bom-and-dfm.md`)

- **Init:** `python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py init-stage 3` (clones full `stages/stage-2/` directory, including `.agents/skills/`, `EnvelopeFollower.webp`, `EnvelopeFollower.md`, and `EnvelopeFollowerImprovements.md`, into `stages/stage-3/`)
- **Output directory:** `stages/stage-3/`
- **Turns:**
  1. Step `3.1` (fresh subagent) → `EnvelopeFollowerImproved.md` and `EnvelopeFollowerBOM.md` (run live `stages/stage-3/.agents/skills/skidl/scripts/jlcpcb_search.py` / `stages/stage-3/.agents/skills/lcsc/...`).
  2. Step `3.2` (fresh subagent) → `EnvelopeFollowerExplanation.md` (7-stage audio signal arc + power/dielectrics).
  3. Step `3.3` (ONE subagent, 3 sequential turns via `send_message`):
     - `3.3a`: Test-point recommendations (must avoid raw `ENV_CAP`/`ENV_RAW` and virtual-ground `IN-` nodes).
     - `3.3b`: Add `TP1`–`TP8` (`RH-5001`, `DNP`) to `EnvelopeFollowerImproved.md` and `EnvelopeFollowerBOM.md` (live-verify `RH-5001` via LCSC/JLCPCB).
     - `3.3c`: Create `SilkscreenInstructions.md` (Ref+Value via `fp_text user` with `fp.Value()` hidden on `.Fab`, `B.SilkS` mirroring, dual-sided TPs/THTs, external Pin-1/cathode/`+` marks, `5 × 5 mm` QR square, `B.Fab` fab notes).
- **Gate checks:** Zero `PENDING_VERIFY` strings in `EnvelopeFollowerBOM.md` before starting Stage 4; `15pF`/`47pF`/`100pF` queried via short tokens (`"15pF"`, `"47pF"`, `"100pF"`) if multi-word `"NP0 0603"` returns wrong capacitance.

---

## Stage 4: SKiDL Circuit & ERC (`docs/tutorial/stage-4-skidl.md`)

- **Init:** `python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py init-stage 4` (clones full `stages/stage-3/` directory, including `.agents/skills/`, `EnvelopeFollowerImproved.md`, `EnvelopeFollowerBOM.md`, and `SilkscreenInstructions.md`, into `stages/stage-4/`)
- **Output directory:** `stages/stage-4/`
- **Turns (1 fresh subagent):** Run `/skidl` prompt using `stages/stage-4/.agents/skills/skidl/`.
- **Expected outputs:** `.venv/` (gitignored), `envelope_follower.py`, `envelope_follower_sklib.py`, `envelope_follower.erc`, `envelope_follower.log`, `envelope_follower.net`, `envelope_follower_bom.xml`, `jlcpcb_bom.csv`.
- **Gate checks:**
  - `python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py check-stage4`
  - `ruff check` and `ruff format --check` on `stages/stage-4/*.py`
  - `python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py check-clean-root`
- **Pitfalls to verify in `envelope_follower.py`:**
  - `os.chdir(Path(__file__).resolve().parent)` placed **before** `from skidl import ...`.
  - `Diode:BAV99` (if used instead of `BAT54S`) has swapped hidden KiCad pin names (`1="K"`, `2="A"`, `3="K"`), so `D8`/`D9` must index by pin numbers `1` (`-12V`), `2` (`+12V`), `3` (output midpoint).
  - `Device:C_Polarized` (`C3`, `C4`) uses pin `1` (`+`) and pin `2` (`-`): `C4[1]` → `GND`, `C4[2]` → `-12V`.
  - Diodes/LEDs wired by pin names `"A"`/`"K"` (KiCad pin `1` = `K`, pin `2` = `A`).
  - Confirm whether `part.fields["Silkscreen"]` is emitted into `envelope_follower.net`.

---

## Stage 5: 6 HP Main PCB (`docs/tutorial/stage-5-schematic-and-pcb.md`)

- **Init:** `python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py init-stage 5` (clones full `stages/stage-4/` directory, including `.agents/skills/`, `.venv/`, `envelope_follower.net`, and Stage 3 specs, into `stages/stage-5/`)
- **Output directory:** `stages/stage-5/`
- **Turns:**
  1. Step `5.1` (fresh subagent) → `generate_kicad_pcb.py` and `EnvelopeFollower.kicad_pcb` using `stages/stage-5/.agents/skills/`.
  2. Verify:
     - `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc --refill-zones --exit-code-violations --format json --output /tmp/stage5_drc.json stages/stage-5/EnvelopeFollower.kicad_pcb`
     - `python3 stages/stage-5/.agents/skills/kicad/scripts/analyze_pcb.py stages/stage-5/EnvelopeFollower.kicad_pcb --full --analysis-dir stages/stage-5/analysis/`
     - `python3 stages/stage-5/.agents/skills/kicad-silkscreen-markup/scripts/silk_annotator.py --inspect stages/stage-5/EnvelopeFollower.kicad_pcb`
     - Top/bottom `kicad-cli pcb render` checks.
  3. Step `5.2` (ONE fresh subagent for Audit → conditional Fix via `send_message`):
     - Audit `generate_kicad_pcb.py` and `EnvelopeFollower.kicad_pcb` against `SilkscreenInstructions.md` and `envelope_follower.net`.
     - If discrepancies exist, send the Fix prompt to the same subagent and re-run DRC + `analyze_pcb.py` + `silk_annotator.py --inspect` + 3D renders.
- **Watch-outs:** Seed `SilkGrid` with SMD `.Fab` body bounding boxes (`SOIC-14` `U1`/`U2` label placement); confirm `DNP` flags (`exclude_from_pos_files`, `exclude_from_bom`) on `TP1`–`TP8`; confirm `F.Cu` panel controls (`RV1`–`RV4`, `J1`–`J3`, `D4`) and `B.Cu` SMT + `J_PWR` + `TP1`–`TP8`.

---

## Stage 6: Mated 3U Front Panel (`docs/tutorial/stage-6-front-panel.md`)

- **Init:** `python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py init-stage 6` (clones full `stages/stage-5/` directory, including `.agents/skills/`, `.venv/`, and `EnvelopeFollower.kicad_pcb`, into `stages/stage-6/`)
- **Output directory:** `stages/stage-6/`
- **Turns (1 subagent; conditional `send_message` if `JLCJLCJLC` appears):**
  - Run `/eurorack-panel` prompt using `stages/stage-6/.agents/skills/eurorack-panel/` producing `panel/EnvelopeFollower_Panel.kicad_pcb`, `production/panel/`, and `production/EnvelopeFollower_Panel.zip`.
- **Verify:**
  - `kicad-cli pcb drc --refill-zones --exit-code-violations` on `panel/EnvelopeFollower_Panel.kicad_pcb`
  - `python3 stages/stage-6/.agents/skills/kicad/scripts/analyze_pcb.py stages/stage-6/panel/EnvelopeFollower_Panel.kicad_pcb --full --output /tmp/stage6_panel_pcb.json`
  - `python3 stages/stage-6/.agents/skills/kicad/scripts/analyze_gerbers.py stages/stage-6/production/panel/ --full --output /tmp/stage6_panel_gerbers.json`
  - Top/bottom `kicad-cli pcb render` checks (`IN` boxed, `INV OUT` unboxed, `5 × 5 mm` `B.SilkS` QR square, no `JLCJLCJLC`).

---

## Stage 7: Manufacturing & Assembly (`docs/tutorial/stage-7-manufacturing.md`)

- **Init:** `python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py init-stage 7` (clones full `stages/stage-6/` directory, including `.agents/skills/`, `jlcpcb_bom.csv`, `EnvelopeFollower.kicad_pcb`, `panel/EnvelopeFollower_Panel.kicad_pcb`, and `production/panel/`, into `stages/stage-7/`)
- **Output directory:** `stages/stage-7/`
- **Turns (1 fresh subagent):** Run the `/kicad` `/jlcpcb` Stage 7 prompt using `stages/stage-7/.agents/skills/` producing `production/main/`, `production/main/EnvelopeFollower_cpl.csv`, `production/EnvelopeFollower_Main.zip`, `production/EnvelopeFollower_Panel.zip`, and `OrderingNotes.md`.
- **Gate checks:**
  - `python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py check-stage7`
  - `python3 stages/stage-7/.agents/skills/kicad/scripts/analyze_gerbers.py stages/stage-7/production/main/ --full --output /tmp/stage7_main_gerbers.json` (`9/9` Gerber layers, `0` paste on `F.Paste`, `0` errors).
