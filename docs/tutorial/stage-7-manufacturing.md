# Stage 7: JLCPCB PCBA Export, Assembly & Bench Bring-Up

## AI Agent Prompt

> *"`/kicad` `/jlcpcb` Please export Gerbers, Excellon drills, and the bottom-side SMD centroid CSV (`--side back --smd-only --exclude-dnp`) from `@EnvelopeFollower.kicad_pcb` to `production/main/`, convert `production/main/EnvelopeFollower_cpl.csv` to JLCPCB's required `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer` header format (`Layer=Bottom`), package `production/EnvelopeFollower_Main.zip` and `production/EnvelopeFollower_Panel.zip`, verify `production/main/` with `analyze_gerbers.py`, and write `OrderingNotes.md` covering both boards, which BOM/CPL files to upload, and replacing the `5 × 5 mm` `B.SilkS` square with a JLCPCB QR code."*

!!! note "One Prompt Exports, Audits & Documents Both Boards"
    Sending the single prompt above executes Steps 7.1 and 7.2 automatically—converting KiCad's `.pos` output into JLCPCB CPL format, packaging both upload ZIPs, auditing the main PCB Gerbers with `analyze_gerbers.py`, and writing `OrderingNotes.md`. The shell commands below document what runs under the hood and let you re-export manually after any late layout tweak.

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

# 3. Export SMD placement file (B.Cu only, automatically excluding Manual THT & DNP TP1-TP8)
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb export pos \
    --side back --format csv --units mm --use-drill-file-origin --smd-only --exclude-dnp \
    --output production/main/EnvelopeFollower_cpl_raw.csv EnvelopeFollower.kicad_pcb

# 4. Convert KiCad .pos headers to JLCPCB CPL format and assert all 45 B.Cu SMD rows
python3 - <<'PY'
import csv, pathlib

raw = pathlib.Path("production/main/EnvelopeFollower_cpl_raw.csv")
out = pathlib.Path("production/main/EnvelopeFollower_cpl.csv")
with raw.open(newline="") as f:
    rows = list(csv.DictReader(f))

assert len(rows) == 45, f"Expected 45 SMD rows, got {len(rows)}"
assert all(not r["Ref"].startswith("TP") for r in rows), "DNP test point leaked into CPL"

with out.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"])
    for r in rows:
        layer = "Bottom" if r["Side"].lower() == "bottom" else "Top"
        writer.writerow([r["Ref"], r["Val"], r["Package"], r["PosX"], r["PosY"], r["Rot"], layer])
raw.unlink()
PY

# 5. Package main and front-panel Gerber ZIPs for JLCPCB upload
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

Notice how `--smd-only` skips the `9` manual THT parts while `--exclude-dnp` omits `TP1`–`TP8` (`Ronghe RH-5001`), leaving strictly the **45 `B.Cu` SMD components** in `production/main/EnvelopeFollower_cpl.csv` with JLCPCB's required `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer` header row and `Layer=Bottom`.

Confirm the `analyze_gerbers.py` report (`production/main/`):

- **Layer & Drill Completeness**: `9/9` Gerber layers (`B.Cu`, `B.Mask`, `B.Paste`, `B.SilkS`, `Edge.Cuts`, `F.Cu`, `F.Mask`, `F.Paste`, `F.SilkS`) plus `PTH`/`NPTH` drill files complete (`completeness.complete: True` via `.gbrjob`), with `0` errors (`GR-001`, `GR-003`, `GR-005`).
- **Layer Alignment**: `F.Cu`, `B.Cu` (via the full-board `GND` copper pours from [Stage 5](stage-5-schematic-and-pcb.md)), and `Edge.Cuts` share aligned `29.60 × 107.00 mm` extents (`alignment.aligned: True`).
- **Single-Sided Paste Apertures**: All `116` SMD pads across the `45` `B.Cu` SMD components (`2×14` `SOIC-14` + `6×2` `SOD-123` + `2×3` `SOT-23` + `11×2` SMD caps + `24×2` SMD resistors) appear strictly on `B.Paste`, with `0` solder paste openings on `F.Paste`.
- **Drills (`EnvelopeFollower-PTH.drl`)**: `49` THT component holes (`10` `J_PWR` + `9` `J1`–`J3` + `20` `RV1`–`RV4` + `2` `D4` + `8` `DNP` `1.0 mm` `TP1`–`TP8` test-point holes) plus stitching and signal vias.

---

## Step 7.2: Ordering on JLCPCB, `OrderingNotes.md` & Cost Breakdown

### Standalone `OrderingNotes.md` Prompt

If you only need to generate or refresh `OrderingNotes.md` independently of the full Stage 7 export prompt above:

> *"Create a file for ordering notes (`OrderingNotes.md`) covering both `EnvelopeFollower.kicad_pcb` and `panel/EnvelopeFollower_Panel.kicad_pcb`. Include which Gerber ZIP, BOM, and CPL files to use (`production/EnvelopeFollower_Main.zip`, `jlcpcb_bom.csv`, `production/main/EnvelopeFollower_cpl.csv`, and `production/EnvelopeFollower_Panel.zip`), Bottom Side Economic PCBA settings, and the requirement to replace the `5 × 5 mm` solid `B.SilkS` square with a JLCPCB QR code during board entry on both boards."*

### Main Circuit PCB (`EnvelopeFollower.kicad_pcb`)

- Upload `production/EnvelopeFollower_Main.zip` (`1.6 mm` FR4, 2 layers; under **Mark on PCB / Order Number / QR Code**, select **Specify a location** to replace the **`5 × 5 mm` solid silkscreen square** on `B.SilkS` with a JLCPCB 2D QR code—JLCPCB's legacy `JLCJLCJLC` text string is obsolete and no longer used).
- Enable **Economic PCB Assembly** on **Bottom Side** only (`B.Cu`).
- Upload `jlcpcb_bom.csv` (`18` BOM lines, `45` SMD components) and `production/main/EnvelopeFollower_cpl.csv`.

!!! warning "Do Not Upload `envelope_follower_bom.xml` to JLCPCB"
    Always upload **`jlcpcb_bom.csv`** (`Comment,Designator,Footprint,LCSC Part #`) for JLCPCB Economic PCBA. Do **not** upload `envelope_follower_bom.xml`: that file is the raw KiCad XML BOM containing all 62 parts (including the 9 manual THT parts and 8 `DNP` test points) and will be rejected or pull unpopulated THT parts into assembly.

#### Feeder Tier & Cost Summary

- **Per-Board SMD Component Cost**: **~\$0.85 USD** across all 45 SMD components.
- **15 JLCPCB Basic Lines (\$0 setup fee)**: `C81598` (`1N4148W`), `C8598` (`B5819W`), `C15849` (`1uF`), `C5378` (`220nF`), `C14663` (`100nF`), `C1671` (`47pF`), `C22935` (`1M`), `C25804` (`10k`), `C4184` (`20k`), `C21190` (`1k` `0603`), `C25819` (`47k`), `C25803` (`100k`), `C4410` (`1k` `1206`), `C22843` (`1.5k`), and `C17903` (`10R` `1206`).
- **3 JLCPCB Extended Lines (\$3.00/line = \$9.00 batch total)**:
  1. `TL074HIDR` (`C2878713`, `2×`/board — pin-compatible `SOIC-14` fallbacks if stock runs out: TI `TL074CDR` `C12594` or ST `TL074CDT` `C6963`).
  2. `BAT54SLT1G` (`C19726`, `2×`/board — drop-in alts: Nexperia `C47546`, CJ `C8592`).
  3. `10 µF 50V` SMD Al Electrolytic (`C72488`, `2×`/board — alts: `C14162`, or `22 µF 35V` `C2887274`).

#### Verifying the JLCPCB Placement Preview Against `B.SilkS`

Because every SMD part carries its `<Ref> <Value>` label and external orientation marks on `B.SilkS` ([Stage 5](stage-5-schematic-and-pcb.md)), you can verify JLCPCB's 3D assembly preview and post-assembly DFM report directly against the board image without cross-referencing every unmarked `0603`/`0805` MLCC line by line:

| BOM Value | `B.SilkS` Label | Designators | Package | LCSC # | What to Verify in JLCPCB Preview / Report |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TL074HIDR` | `U1 TL074H`, `U2 TL074H` | `U1`, `U2` | `SOIC-14` | `C2878713` | Pin-1 dot/bevel aligns with `B.SilkS` Pin-1 dot/notch; label sits outside `B.Fab` IC body |
| `1N4148W` | `D1 1N4148W` … `D7 1N4148W` | `D1`–`D3`, `D7` | `SOD-123` | `C81598` | Package cathode band aligns with external `B.SilkS` cathode bar (`\|`) |
| `B5819W` | `D5 B5819W`, `D6 B5819W` | `D5`, `D6` | `SOD-123` | `C8598` | Package cathode band aligns with external `B.SilkS` cathode bar (`\|`) |
| `BAT54SLT1G` | `D8 BAT54S`, `D9 BAT54S` | `D8`, `D9` | `SOT-23` | `C19726` | 2-pad side (`-12V`, `+12V`) vs. single-pad side (`AMP_OUT` / `INV_AMP_OUT`) and external `B.SilkS` Pin-1 dot match `SOT-23` outline |
| `1uF 50V` | `C1 1uF` | `C1` | `0603` | `C15849` | Unmarked ceramic body — verify against BOM/CPL `C15849` & `B.SilkS` value |
| `220nF 50V` | `C2 220nF` | `C2` | `0805` | `C5378` | Unmarked ceramic body — verify `0805` size against `C5378` & `B.SilkS` value |
| `10uF 50V` (`+12V`) | `C3 10uF 50V` | `C3` | `CP_Elec_6.3x5.4` | `C72488` | Black cathode stripe sits opposite external `+` mark (`+` pad on `+12V`, `-` on `GND`) |
| `10uF 50V` (`-12V`) | `C4 10uF 50V` | `C4` | `CP_Elec_6.3x5.4` | `C72488` | Black cathode stripe on `-12V` sits opposite external `+` mark (**`+` pad on `GND`**, `-` on `-12V`) |
| `100nF 50V` | `C5 100nF` … `C9 100nF` | `C5`–`C9` | `0603` | `C14663` | Unmarked ceramic body — verify against `C14663` & `B.SilkS` value |
| `47pF 50V` | `C10 47pF`, `C11 47pF` | `C10`, `C11` | `0603` | `C1671` | Unmarked C0G ceramic body — verify against `C1671` & `B.SilkS` value |
| `1M` | `R1 1M` | `R1` | `0603` | `C22935` | `1004` / EIA-96 code (if marked) or CPL `C22935` |
| `10k` | `R2 10k` … `R18 10k` | `R2`–`R7`, `R17`, `R18` | `0603` | `C25804` | `1002` / `01C` (if marked) or CPL `C25804` |
| `20k` | `R8 20k` | `R8` | `0603` | `C4184` | `2002` / `30C` (if marked) or CPL `C4184` |
| `1k` | `R9 1k`, `R11 1k`, `R12 1k`, `R25 1k` | `R9`, `R11`, `R12`, `R25` | `0603` | `C21190` | `1001` / `01B` (if marked) or CPL `C21190` |
| `47k` | `R10 47k` | `R10` | `0603` | `C25819` | `4702` / `65C` (if marked) or CPL `C25819` |
| `100k` | `R13 100k` … `R24 100k` | `R13`–`R15`, `R24` | `0603` | `C25803` | `1003` / `01D` (if marked) or CPL `C25803` |
| `1k 1/4W` | `R16 1k`, `R19 1k` | `R16`, `R19` | `1206` | `C4410` | Marked `1001`/`102` on `1206` body; verify `1206` size & CPL `C4410` |
| `1.5k` | `R21 1.5k` | `R21` | `0603` | `C22843` | `1501` / `18B` (if marked) or CPL `C22843` |
| `10R 1/4W` | `R26 10R`, `R27 10R` | `R26`, `R27` | `1206` | `C17903` | Marked `10R0`/`100` on `1206` body; verify `1206` size & CPL `C17903` |

### Front Panel PCB (`production/EnvelopeFollower_Panel.zip`)

- Upload `production/EnvelopeFollower_Panel.zip` (`1.6 mm` FR4, **Black** solder mask with **White** silkscreen; under **Mark on PCB / Order Number / QR Code**, select **Specify a location** to place the order QR code over the `5 × 5 mm` white square on `B.SilkS` verified in [Stage 6](stage-6-front-panel.md)). No PCBA needed.

---

## Step 7.3: Stress-Free Mechanical Assembly & Bench Bring-Up

When your assembled PCBs arrive, hand-solder the `9` required `Manual THT` parts (plus optional `TP1`–`TP8` wire-loop test points):

1. **Rear Power Header (`J_PWR` on `B.Cu`)**:
    Solder `J_PWR` (`2×5` shrouded IDC header) first, confirming Pin 1 / Pin 2 (`-12V`) sits at the bottom aligned with the `-12V / RED STRIPE` bar and keyway notch on `B.SilkS`.
2. **Optional Wire-Loop Test Points (`TP1`–`TP8` on `B.Cu`)**:
    If you want clip-on oscilloscope probe loops, solder `Ronghe RH-5001` (`C5199801`) loops into `TP1`–`TP8` from `B.Cu` so every node stays accessible from behind even after the front panel is bolted on.
3. **Dry-Fit Front-Panel Controls (`F.Cu`)**:
    Insert all 8 front-side parts **unsoldered** into `F.Cu`, matching each component to the main PCB's dual-sided `F.SilkS`/`B.SilkS` assembly labels and pot Pin-1 (`"1"`) markers (noting how those map onto the derived legends on the [Stage 6](stage-6-front-panel.md) front panel):
    - `RV1` (`RV1 GAIN A100k`) $\rightarrow$ panel legend **`GAIN`**
    - `RV2` (`RV2 ATK A50k`) $\rightarrow$ panel legend **`ATK`**
    - `RV3` (`RV3 REL A1M`) $\rightarrow$ panel legend **`REL`**
    - `RV4` (`RV4 OFFSET B10k`) $\rightarrow$ panel legend **`OFFSET`**
    - `J1` (`J1 IN`), `J2` (`J2 OUT`), `J3` (`J3 INV_OUT`) $\rightarrow$ `WQP-PJ398SM` jacks (mating to boxed **`IN`**, **`OUT`**, and unboxed **`INV OUT`** on the front panel)
    - `D4` (`D4 LED`) $\rightarrow$ `3 mm` LED (mating to **`ENV`** on the front panel; verify long lead `+` anode and flat edge `-` cathode match the dual-sided `+`/`-` marks)
4. **Align Against Front Panel & Solder**:
    Seat the 3U front panel (`panel/EnvelopeFollower_Panel.kicad_pcb`) over the shafts and bushings, tighten the M6/M7 panel nuts finger-tight against the exposed rear `B.Mask` grounding rings, position `D4` flush inside its `3.2 mm` **`ENV`** bezel hole, and **only after the front panel aligns everything mechanically**, solder all pot lugs, jack pins, and LED leads on `B.Cu`.
5. **Bench Bring-Up Using `TP1`–`TP8`**:
    - Power the module via a current-limited $\pm 12\text{ V}$ bench supply (or Eurorack skiff), clip ground to **`TP1` (`GND`)**, and confirm **`~+11.78 V`** on **`TP2` (`+12V`)** and **`~-11.78 V`** on **`TP3` (`-12V`)**.
    - With nothing patched into `J1` (`IN`), verify `D4` (`LED` / **`ENV`**) is completely dark (`0 mA`) and check **`TP8` (`OFS`)** sweeps smoothly from `~-9.8 V` to `~+9.8 V` as you turn `RV4` (`OFFSET`).
    - Feed a `1 kHz` `5 Vpp` sine wave into `J1` (`IN`) and probe **`TP4` (`PRE`)** (`-0.1×` to `-10.1×` gain), **`TP5` (`HALF`)** (clean negative half-wave), **`TP6` (`RECT`)** (`+1.0× |PRE|` full-wave), and **`TP7` (`ENV`)** (smooth positive envelope tracking down to millivolts without deadzone).
