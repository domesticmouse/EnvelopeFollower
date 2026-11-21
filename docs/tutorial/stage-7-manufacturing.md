# Stage 7: JLCPCB PCBA Export, Assembly & Bench Bring-Up

## AI Agent Prompt

> *"`/kicad` `/jlcpcb` Please export Gerbers, Excellon drills, and the bottom-side SMD centroid CSV (`--side back --smd-only --exclude-dnp`) from `@EnvelopeFollower.kicad_pcb` to `production/main/`, convert `production/main/EnvelopeFollower_cpl.csv` to JLCPCB's required `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer` header format (`Layer=Bottom`), package `production/main/` into `production/EnvelopeFollower_Main.zip` and `production/panel/` into `production/EnvelopeFollower_Panel.zip`, verify `production/main/` with `analyze_gerbers.py`, and write `OrderingNotes.md` covering both `@EnvelopeFollower.kicad_pcb` and `@panel/EnvelopeFollower_Panel.kicad_pcb`, referencing `@jlcpcb_bom.csv` and `production/main/EnvelopeFollower_cpl.csv` for upload, and replacing the `5 × 5 mm` `B.SilkS` square with a JLCPCB QR code."*

!!! note "One Prompt Exports, Audits & Documents Both Boards"
    Sending the single prompt above executes Steps 7.1 and 7.2 automatically—converting KiCad's `.pos` output into JLCPCB CPL format, packaging both `14`-file Gerber upload ZIPs, auditing the main PCB Gerbers with `analyze_gerbers.py`, and writing `OrderingNotes.md`. The shell commands below document what runs under the hood and let you re-export manually after any late layout tweak.

---

## Step 7.1: Export, Format & Verify Main PCB Manufacturing Files

Once `EnvelopeFollower.kicad_pcb` is generated, routed, and verified with `0` DRC violations ([Stage 5](stage-5-schematic-and-pcb.md)), export Gerbers, Excellon drills, and the bottom-side SMD Centroid (`.pos`) file, convert the CPL headers for JLCPCB, package both Gerber ZIP archives, and audit `production/main/` with `analyze_gerbers.py`:

```bash
mkdir -p production/main

# 1. Export Gerbers (standard 2-layer PCB layers + .gbrjob)
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb export gerbers \
    --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
    --output production/main/ EnvelopeFollower.kicad_pcb

# 2. Export Excellon drill files
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb export drill \
    --format excellon --excellon-separate-th --generate-map --map-format gerberx2 \
    --output production/main/ EnvelopeFollower.kicad_pcb

# 3. Export SMD placement file (B.Cu only, automatically excluding THT, DNP TP1-TP8 & FID1-FID3)
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb export pos \
    --side back --format csv --units mm --use-drill-file-origin --smd-only --exclude-dnp \
    --output production/main/EnvelopeFollower_cpl_raw.csv EnvelopeFollower.kicad_pcb

# 4. Convert KiCad .pos headers to JLCPCB CPL format, normalize rotations, and assert all 49 B.Cu SMD rows
python3 - <<'PY'
import csv, pathlib

raw = pathlib.Path("production/main/EnvelopeFollower_cpl_raw.csv")
out = pathlib.Path("production/main/EnvelopeFollower_cpl.csv")
with raw.open(newline="") as f:
    rows = list(csv.DictReader(f))

assert len(rows) == 49, f"Expected 49 SMD rows, got {len(rows)}"
assert all(not r["Ref"].startswith(("TP", "FID")) for r in rows), "DNP TP/FID leaked into CPL"

with out.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"])
    for r in rows:
        rot = int(round(float(r["Rot"]) % 360.0))
        layer = "Bottom" if r["Side"].lower() == "bottom" else "Top"
        writer.writerow([
            r["Ref"],
            r["Val"],
            r["Package"],
            f"{float(r['PosX']):.4f}mm",
            f"{float(r['PosY']):.4f}mm",
            rot,
            layer,
        ])
raw.unlink()
PY

# 5. Package main and front-panel Gerber ZIPs (14 files each, excluding _cpl.csv)
python3 - <<'PY'
import pathlib, zipfile

def zip_gerbers(src_dir: pathlib.Path, zip_path: pathlib.Path) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(src_dir.iterdir()):
            if p.is_file() and not p.name.endswith("_cpl.csv"):
                zf.write(p, p.name)

zip_gerbers(pathlib.Path("production/main"), pathlib.Path("production/EnvelopeFollower_Main.zip"))
if pathlib.Path("production/panel").is_dir():
    zip_gerbers(pathlib.Path("production/panel"), pathlib.Path("production/EnvelopeFollower_Panel.zip"))
PY

# 6. Verify main PCB Gerbers & drills with the kicad skill
python3 .agents/skills/kicad/scripts/analyze_gerbers.py production/main/ --full --output /tmp/main_gerbers.json
```

Notice how `--smd-only --exclude-dnp` skips all `11` populated manual THT parts, `8` `DNP` test points (`TP1`–`TP8`), and `3` `DNP` optical fiducials (`FID1`–`FID3`), leaving strictly the **49 `B.Cu` SMD components** (`49/49` exact parity with `jlcpcb_bom.csv`) in `production/main/EnvelopeFollower_cpl.csv` with JLCPCB's required `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer` header row and `Layer=Bottom`.

Confirm the `analyze_gerbers.py` report (`production/main/`):

- **Layer & Drill Completeness**: `9/9` Gerber layers (`B.Cu`, `B.Mask`, `B.Paste`, `B.SilkS`, `Edge.Cuts`, `F.Cu`, `F.Mask`, `F.Paste`, `F.SilkS`) plus `PTH`/`NPTH` drill files and `.gbrjob` complete (`completeness.complete: True`), **`0` errors**.
- **Layer Alignment**: `F.Cu`, `B.Cu` (via the full-board `GND` copper pours from [Stage 5](stage-5-schematic-and-pcb.md)), and `Edge.Cuts` share aligned `30.00 × 108.00 mm` extents (`alignment.aligned: True`).
- **Single-Sided Paste Apertures & Expected `GR-004` Warning**: All `126` SMD pads across the `49` `B.Cu` SMD components appear strictly on `B.Paste` (`126/126` = `100%` pasted), with **`0` solder paste flashes on `F.Paste`**. `analyze_gerbers.py` reports a single heuristic warning (`GR-004`: `"B paste layer: 126 flashes vs 394 copper (32%)"`) solely because `B.Cu` copper flashes also include `212` vias + `53` THT holes + `3` fiducials (`126 + 212 + 53 + 3 = 394`); `0` errors.
- **Drills (`EnvelopeFollower-PTH.drl`)**: `265` PTH holes (`212 × 0.30 mm` stitching/signal vias + `53` THT component holes across `7` drill tool sizes `0.75–1.80 mm`: `J4`, `J1`–`J3`, `RV1`–`RV4`, `D4`, `C1`/`C2`, and `8` `DNP` `1.0 mm` `TP1`–`TP8` holes), `0` NPTH holes.

---

## Step 7.2: Ordering on JLCPCB, `OrderingNotes.md` & Cost Breakdown

### Standalone `OrderingNotes.md` Prompt

If you only need to generate or refresh `OrderingNotes.md` independently of the full Stage 7 export prompt above:

> *"Create a file for ordering notes (`OrderingNotes.md`) covering both `EnvelopeFollower.kicad_pcb` and `panel/EnvelopeFollower_Panel.kicad_pcb`. Include which Gerber ZIP, BOM, and CPL files to use (`production/EnvelopeFollower_Main.zip`, `jlcpcb_bom.csv`, `production/main/EnvelopeFollower_cpl.csv`, and `production/EnvelopeFollower_Panel.zip`), Bottom Side Economic PCBA settings, and the requirement to replace the `5 × 5 mm` solid `B.SilkS` square with a JLCPCB QR code during board entry on both boards."*

### Main Circuit PCB (`EnvelopeFollower.kicad_pcb`)

- **Gerbers & Stackup**: Upload `production/EnvelopeFollower_Main.zip` (`14` files, `30.00 × 108.00 mm`, `2` layers, `1.6 mm` FR-4, `1 oz` copper, **Black** solder mask, **White** silkscreen, **ENIG** recommended or **LeadFree HASL**).
- **QR Code Placement**: Under **Mark on PCB / Order Number / QR Code**, select **Specify a location** to replace the **`5.0 × 5.0 mm` solid silkscreen square** on `B.SilkS` at `(12.50, 7.80)–(17.50, 12.80)` (center `(15.00, 10.30)` above `ENVELOPE FOLLOWER`) with a JLCPCB 2D QR code—JLCPCB's legacy `JLCJLCJLC` text string is obsolete and no longer used, and do not confuse the QR square with `J4`'s `9.00 × 0.85 mm` `RED STRIPE / -12V` bar at the bottom edge.
- **Assembly**: Enable **Economic PCB Assembly** on **Bottom Side** only (`B.Cu`, `Confirm Production File: Yes` recommended for verifying bottom-side rotations before reflow). `3` optical fiducials (`FID1`–`FID3`) are already on `B.Cu`.
- **BOM & CPL**: Upload `jlcpcb_bom.csv` (`19` BOM lines, `49` SMD components) and `production/main/EnvelopeFollower_cpl.csv` (`49` `Bottom` rows, `49/49` parity).

!!! warning "Do Not Upload `envelope_follower_bom.xml` to JLCPCB"
    Always upload **`jlcpcb_bom.csv`** (`Comment,Designator,Footprint,LCSC Part #`) for JLCPCB Economic PCBA. Do **not** upload `envelope_follower_bom.xml`: that file is the raw KiCad XML BOM containing all 71 footprints (including the `11` manual THT parts, `8` `DNP` test points, and `3` `DNP` fiducials) and will pull unpopulated THT parts or fail CPL parity checks.

#### Feeder Tier & Cost Summary

- **Per-Board SMD Component Cost**: **~$1.05 USD (`$1.0494`)** across all `49` SMD components (`$5.25` for a 5-board prototype batch).
- **14 JLCPCB Basic Lines (`33` parts, \$0 setup fee, ~\$0.19/board)**: `C8598` (`B5819W`), `C2128` (`1N4148WS`), `C2500` (`BAV99`), `C17903` (`10R` `1206`), `C23179` (`470R` `0603`), `C21190` (`1k` `0603`), `C4190` (`2.2k`), `C25804` (`10k` `1%`), `C25810` (`18k`), `C25803` (`100k`), `C22935` (`1M`), `C14663` (`100nF`), `C1671` (`47pF C0G`), and `C14858` (`100pF C0G`).
- **5 JLCPCB Extended Lines (`16` parts, \$3.00/line = \$15.00 batch setup, ~\$0.86/board)**:
  1. `TL074HIDR` (`C2878713`, `2×`/board — pin-compatible `SOIC-14` fallbacks: `TL074CDR` `C12594` or `TL074CDT` `C6963`).
  2. `BAT54S,215` (`C47546`, `1×`/board — `D1_D2`).
  3. `RT0603BRD0710KL` (`C95204`, `7×`/board — `10 kΩ ±0.1%` `25 ppm` consolidated rectifier network `R3`–`R8B`).
  4. `RTT124700FTP` (`C333193`, `4×`/board — `470 Ω 0.5 W` `1210` clash resistors `R16A/B`, `R19A/B`; alt `2010` `C341646`).
  5. `RVT22UF50V67RV0028` (`C2836438`, `2×`/board — `22 µF 50 V` SMD electrolytic `C3`/`C4`; alt `22 µF 35 V` `C2887274`).
- **LCSC-Verified Populated THT Parts (`$0.83`/board = `$4.13`/5 boards)**: `C1`, `C2` (`1 µF 100 V` PET film `C125397`), `J4` (`2×5` shrouded IDC `C53207560`), `D4` (`3 mm` Red LED `C99771`), plus consigned `J1`–`J3` and `RV1`–`RV4` (`~$4.75`/board). Optional `DNP` `TP1`–`TP8` (`C5199801`) add `$0.00` by default.

#### Verifying the JLCPCB Placement Preview Against `B.SilkS`

Because every SMD part carries its value or `<Ref> <Value>` label and external orientation marks on `B.SilkS` ([Stage 5](stage-5-schematic-and-pcb.md)), you can verify JLCPCB's 3D assembly preview directly against the board image. Note that JLCPCB's component reel zero-orientations often differ from KiCad library footprints (and `Layer=Bottom` parts may need inspection in the JLCPCB 3D/CPL viewer before paying):

| BOM Value | `B.SilkS` Label | Designators | Package | LCSC # | What to Verify in JLCPCB Preview / CPL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TL074H` | `U1 TL074H`, `U2 TL074H` | `U1`, `U2` | `SOIC-14` | `C2878713` | `U1` (`90°` CPL) / `U2` (`0°` CPL): Pin-1 bevel/dot aligns with `r = 0.25 mm` `B.SilkS` dot (**likely `+90°` or `+270°` JLC offset**) |
| `B5819W` | `D_PWR_P B5819W`, `D_PWR_N B5819W` | `D_PWR_P`, `D_PWR_N` | `SOD-123` | `C8598` | `D_PWR_P` (`270°`): cathode bar at **top**; `D_PWR_N` (`90°`): cathode bar at **bottom** (reversed on `-12V`) |
| `BAT54S` | `D1_D2 BAT54S` | `D1_D2` | `SOT-23` | `C47546` | `0°` CPL: verify 1-pin `COM` vs. 2-pad side and external Pin-1 (`A1`) dot (**likely `+180°` JLC offset**) |
| `1N4148WS` | `D3 1N4148WS`, `D_LED_CLAMP 1N4148WS` | `D3`, `D_LED_CLAMP` | `SOD-323` | `C2128` | `D3` (`0°`): cathode bar at **right** in rear view; `D_LED_CLAMP` (`90°`): cathode bar at **bottom** |
| `BAV99` | `D_IN BAV99`, `D_OUT BAV99`, `D_INV_OUT BAV99` | `D_IN`, `D_OUT`, `D_INV_OUT` | `SOT-23` | `C2500` | `D_IN`/`D_OUT` (`90°`, `COM` top); `D_INV_OUT` (`0°`, `COM` left): verify `COM` & Pin-1 dot (**likely `+180°` JLC offset**) |
| `10R` | `10R` *(`R_PWR_*` on `B.Fab`)* | `R_PWR_P`, `R_PWR_N` | `1206` | `C17903` | Marked `10R0`/`100` on `1206` body; verify pads span cleanly (`90°`) |
| `470R` | `470R` *(`R_ATK_MIN` on `B.Fab`)* | `R_ATK_MIN` | `0603` | `C23179` | Verify body spans pads at top edge (`0°`) & CPL `C23179` |
| `470R 0.5W` | `470R` *(`R16A/B`, `R19A/B` on `B.Fab`)* | `R16A`, `R16B`, `R19A`, `R19B` | `1210` | `C333193` | Marked `4700`/`471` on wide `1210` body; verify `1210` size & `C333193` |
| `1k` | `1k` | `R_IN_PROT`, `R_IN_BUF`, `R_GAIN_MIN`, `R11`, `R12` | `0603` | `C21190` | Verify bodies span pads & CPL `C21190` |
| `2.2k` | `2.2k` *(`R_LED` on `B.Fab`)* | `R_LED` | `0603` | `C4190` | Verify body spans pads (`90°`) & CPL `C4190` |
| `10k` | `10k` | `R2`, `R10`, `R_ENV_PROT`, `R15`, `R17`, `R18`, `R20` | `0603` | `C25804` | Standard `1%` `10k` (`C25804`); verify vs. `0.1%` cluster |
| `10k 0.1%` | `10k` *(`R3`–`R8B` on `B.Fab`)* | `R3`, `R4`, `R5`, `R6`, `R7`, `R8A`, `R8B` | `0603` | `C95204` | Thin-film `0.1%` (`C95204`) clustered around `U1B`/`U1C` — verify `C95204` in BOM/CPL |
| `18k` | `18k` *(`R13` on `B.Fab`)* | `R13` | `0603` | `C25810` | Verify body spans pads (`90°`) & CPL `C25810` |
| `100k` | `100k` *(`R1` on `B.Fab`)* | `R1` | `0603` | `C25803` | Verify body spans pads (`90°`) & CPL `C25803` |
| `1M` | `1M` *(`R_GAIN_FAIL` on `B.Fab`)* | `R_GAIN_FAIL` | `0603` | `C22935` | Verify body spans pads (`0°`) & CPL `C22935` |
| `100nF` | `100nF` *(`C_DEC1`–`C_DEC4` on `B.Fab`)* | `C_DEC1`, `C_DEC2`, `C_DEC3`, `C_DEC4` | `0603` | `C14663` | Unmarked ceramic body next to `U1`/`U2` — verify `C14663` |
| `47pF C0G` | `47pF` *(`C_HF` on `B.Fab`)* | `C_HF` | `0603` | `C1671` | Unmarked C0G ceramic body — verify `C1671` |
| `100pF C0G` | `100pF` *(`C_OUT1`, `C_OUT2` on `B.Fab`)* | `C_OUT1`, `C_OUT2` | `0603` | `C14858` | Unmarked C0G ceramic body — verify `C14858` |
| `22uF 50V` | `22uF` *(`C3`, `C4` on `B.Fab`)* | `C3`, `C4` | `CP_Elec_6.3x5.4` | `C2836438` | Both `270°` CPL: chamfer/`+` faces **top** (`C3` `+` on `+12V`; **`C4` `+` on `GND`**); black half-moon faces **bottom** |

### Front Panel PCB (`production/EnvelopeFollower_Panel.zip`)

- Upload `production/EnvelopeFollower_Panel.zip` (`14` files, `30.00 × 128.50 mm`, `1.6 mm` FR-4, **Black** matte solder mask with **White** silkscreen, **ENIG** recommended for the exposed rear `B.Mask` grounding rings; under **Mark on PCB / Order Number / QR Code**, select **Specify a location** to place the order QR code over the `5.0 × 5.0 mm` white square on `B.SilkS` at panel-local `(12.50, 60.50)–(17.50, 65.50)` verified in [Stage 6](stage-6-front-panel.md)). No PCBA needed.

---

## Step 7.3: Stress-Free Mechanical Assembly & Bench Bring-Up

When your assembled PCBs arrive, hand-solder the `11` populated `Manual/Consigned THT` parts (plus optional `TP1`–`TP8` wire-loop test points):

1. **Rear-Side (`B.Cu`) THT Components (`J4`, `C1`, `C2`, optional `TP1`–`TP8`)**:
   - Solder `C1` and `C2` (`1 µF 100 V` `P=5mm` box PET film, `C125397`, non-polarized) onto `B.Cu` so `F.Cu` stays clear behind the front panel.
   - Solder `J4` (`2×5` shrouded keyed Eurorack IDC header, `C53207560`) onto `B.Cu`, confirming Pins `1–2` (`-12V`) align with the `RED STRIPE / -12V` bar and keyway notch on `B.SilkS`.
   - If you want clip-on oscilloscope probe loops, solder `Ronghe RH-5001` (`C5199801`) pins into `TP1`–`TP8` from `B.Cu` (or leave them unpopulated as bare plated probe pads).
2. **Dry-Fit Front-Panel Controls (`F.Cu`)**:
   Insert all 8 front-side parts **unsoldered** into `F.Cu`, matching each component to the main PCB's dual-sided `F.SilkS`/`B.SilkS` assembly labels and pot Pin `1` markers (noting how those map onto the [Stage 6](stage-6-front-panel.md) front-panel legends):
   - `RV1` (`RV1 GAIN A100k`) $\rightarrow$ panel legend **`GAIN`**
   - `RV2` (`RV2 ATK A50k`) $\rightarrow$ panel legend **`ATK`**
   - `RV3` (`RV3 REL A1M`) $\rightarrow$ panel legend **`REL`**
   - `RV4` (`RV4 OFF B10k`) $\rightarrow$ panel legend **`OFFSET`**
   - `J1` (`J1 IN`), `J2` (`J2 OUT`), `J3` (`J3 INV_OUT`) $\rightarrow$ `WQP-PJ398SM` jacks (mating to boxed **`IN`**, **`OUT`**, and unboxed **`INV OUT`** on the front panel)
   - `D4` (`D4 LED`) $\rightarrow$ `3 mm` LED (`C99771`, mating to **`ENV`** on the front panel; verify long lead `+` anode and flat edge `-` cathode match the dual-sided `+`/`-` marks)
3. **Align Against Front Panel & Solder**:
   Seat the 3U front panel (`panel/EnvelopeFollower_Panel.kicad_pcb`) over the shafts, jack bushings, and LED, tighten the M6/M7 panel nuts finger-tight against the exposed rear `B.Mask` grounding rings so every part sits flush and square, position `D4` inside its `3.2 mm` **`ENV`** bezel hole, and **only after the front panel aligns everything mechanically**, solder all pot lugs, jack pins, and LED leads on `B.Cu`.
4. **Bench Bring-Up Using `TP1`–`TP8`**:
   - Power the module via a current-limited $\pm 12\text{ V}$ bench supply (or Eurorack skiff), clip ground to **`TP1` (`GND`)**, and confirm **`≈ +11.55 V`** on **`TP2` (`+12V`)** and **`≈ -11.55 V`** on **`TP3` (`-12V`)**.
   - With nothing patched into `J1` (`IN`), verify `J1.TN → GND` keeps noise dark (`D4` completely off, `0.00 mA`) and check **`TP7` (`OUT`)** sweeps smoothly across **`≈ ±5.09 V`** (with **`TP8` (`INV_OUT`)** tracking at exact `-1.000×`) as you turn `RV4` (`OFFSET` CW = more positive `OUT`).
   - Feed a `1 kHz` `2 Vpp` (`±1.0 V`) sine wave into `J1` (`IN`) with `OFFSET` centered (`0 V`) and probe:
     - **`TP4` (`IN_BUF`)**: clean `±1.0 V` AC (`0 V` DC, $f_c = 1.58\text{ Hz}$).
     - **`TP5` (`PREAMP`)**: inverted `-0.10×` to `-9.17×` gain sweep as you turn `RV1` (`GAIN`).
     - **`TP6` (`RECT`)**: `+1.000× |PREAMP_OUT|` symmetric full-wave rectified bumps (`≤ 0.80%` half-cycle mismatch).
     - **`TP7` (`OUT`)** & **`TP8` (`INV_OUT`)**: smooth positive and inverted `~1.48× ENV_NODE` envelopes tracking cleanly down to `< 5 mV` without diode deadzone.
