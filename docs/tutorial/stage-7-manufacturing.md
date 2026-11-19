# Stage 8: JLCPCB PCBA Export, Assembly & Bench Bring-Up

## 8.1 Export Main PCB Manufacturing Files

Once you finish routing [`EnvelopeFollower.kicad_pcb`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/EnvelopeFollower.kicad_pcb) in KiCad and pass DRC (`0` violations), export Gerbers, Excellon drills, and the bottom-side SMD Centroid (`.pos`) file for JLCPCB SMT assembly:

```bash
mkdir -p production/main

# 1. Export Gerbers (using standard PCB layers)
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
    --output production/main/EnvelopeFollower_cpl.csv EnvelopeFollower.kicad_pcb
```

Notice how `--smd-only` skips the 9 manual THT parts while `--exclude-dnp` automatically omits `TP1`–`TP8` (`Ronghe RH-5001`), leaving strictly the **45 `B.Cu` SMD components** in `EnvelopeFollower_cpl.csv`.

*(Note: JLCPCB's uploader expects CPL headers named `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer`—rename KiCad's `Ref,Val,Package,PosX,PosY,Rot,Side` header row or export via the KiCad JLCPCB plugin.)*

---

## 8.2 Ordering on JLCPCB & Cost Breakdown

### AI Agent Prompt (Capturing Ordering Notes)

Before uploading your Gerbers and BOM, have your agent write a concise ordering checklist (`OrderingNotes.md`) tied to your exact BOM and QR placeholder:

> *"Create a file for ordering notes. Include which BOM file to use, and the requirement to replace the 5mmx5mm solid square with a JLCPCB QR code during board entry."*

### Main Circuit PCB (`EnvelopeFollower.kicad_pcb`)

- Upload the zipped `production/main/` Gerbers (`1.6 mm` FR4, 2 layers; under **Mark on PCB / Order Number / QR Code**, select the option to **replace the `5 × 5 mm` solid silkscreen square** on `B.SilkS` with a JLCPCB 2D QR code—JLCPCB's legacy `JLCJLCJLC` text string is obsolete and no longer used).
- Enable **Economic PCB Assembly** on **Bottom Side** only (`B.Cu`).
- Upload [`jlcpcb_bom.csv`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/jlcpcb_bom.csv) (`18` BOM lines, `45` SMD components) and `EnvelopeFollower_cpl.csv`.

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

Because every SMD part carries both its reference and value on `B.SilkS` ([Stage 5](stage-5-schematic-and-pcb.md)), you can verify JLCPCB's 3D assembly preview and post-assembly DFM report directly against the board image without cross-referencing every unmarked `0603`/`0805` MLCC line by line:

| BOM Value | `B.SilkS` Label | Designators | Package | LCSC # | What to Verify in JLCPCB Preview / Report |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TL074HIDR` | `TL074H` | `U1`, `U2` | `SOIC-14` | `C2878713` | Pin-1 dot/bevel aligns with `B.SilkS` Pin-1 dot/notch |
| `1N4148W` | `1N4148W` | `D1`–`D3`, `D7` | `SOD-123` | `C81598` | Package cathode band aligns with external `B.SilkS` cathode bar (`\|`) |
| `B5819W` | `B5819W` | `D5`, `D6` | `SOD-123` | `C8598` | Package cathode band aligns with external `B.SilkS` cathode bar (`\|`) |
| `BAT54SLT1G` | `BAT54S` | `D8`, `D9` | `SOT-23` | `C19726` | 2-pad side (`-12V`, `+12V`) vs. single-pad side (`AMP_OUT` / `INV_AMP_OUT`) matches `SOT-23` outline |
| `1uF 50V` | `1uF` | `C1` | `0603` | `C15849` | Unmarked ceramic body — verify against BOM/CPL `C15849` & `B.SilkS` value |
| `220nF 50V` | `220nF` | `C2` | `0805` | `C5378` | Unmarked ceramic body — verify `0805` size against `C5378` & `B.SilkS` value |
| `10uF 50V` | `10uF 50V` | `C3`, `C4` | `CP_Elec_6.3x5.4` | `C72488` | Black cathode stripe on aluminum cap top sits opposite external `+` silkscreen mark |
| `100nF 50V` | `100nF` | `C5`–`C9` | `0603` | `C14663` | Unmarked ceramic body — verify against `C14663` & `B.SilkS` value |
| `47pF 50V` | `47pF` | `C10`, `C11` | `0603` | `C1671` | Unmarked C0G ceramic body — verify against `C1671` & `B.SilkS` value |
| `1M` | `1M` | `R1` | `0603` | `C22935` | `1004` / EIA-96 code (if marked) or CPL `C22935` |
| `10k` | `10k` | `R2`–`R7`, `R17`, `R18` | `0603` | `C25804` | `1002` / `01C` (if marked) or CPL `C25804` |
| `20k` | `20k` | `R8` | `0603` | `C4184` | `2002` / `30C` (if marked) or CPL `C4184` |
| `1k` | `1k` | `R9`, `R11`, `R12`, `R25` | `0603` | `C21190` | `1001` / `01B` (if marked) or CPL `C21190` |
| `47k` | `47k` | `R10` | `0603` | `C25819` | `4702` / `65C` (if marked) or CPL `C25819` |
| `100k` | `100k` | `R13`–`R15`, `R24` | `0603` | `C25803` | `1003` / `01D` (if marked) or CPL `C25803` |
| `1k 1/4W` | `1k` | `R16`, `R19` | `1206` | `C4410` | Marked `1001`/`102` on `1206` body; verify `1206` size & CPL `C4410` |
| `1.5k` | `1.5k` | `R21` | `0603` | `C22843` | `1501` / `18B` (if marked) or CPL `C22843` |
| `10R 1/4W` | `10R` | `R26`, `R27` | `1206` | `C17903` | Marked `10R0`/`100` on `1206` body; verify `1206` size & CPL `C17903` |

### Front Panel PCB ([`production/EnvelopeFollower_Panel.zip`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/production/EnvelopeFollower_Panel.zip))

- Upload `production/EnvelopeFollower_Panel.zip` (`1.6 mm` FR4, **Black** solder mask with **White** silkscreen, **Specify a location** for the order QR code over the `5 × 5 mm` white square on `B.SilkS`). No PCBA needed.

---

## 8.3 Stress-Free Mechanical Assembly & Bench Bring-Up

When your assembled PCBs arrive, hand-solder the `9` required `Manual THT` parts (plus optional `TP1`–`TP8` wire-loop test points):

1. **Rear Power Header (`J_PWR` on `B.Cu`)**:
    Solder `J_PWR` (`2×5` shrouded IDC header) first, confirming Pin 1 / Pin 2 (`-12V`) sits at the bottom aligned with the `-12V / RED STRIPE` bar and keyway notch on `B.SilkS`.
2. **Optional Wire-Loop Test Points (`TP1`–`TP8` on `B.Cu`)**:
    If you want clip-on oscilloscope probe loops, solder `Ronghe RH-5001` (`C5199801`) loops into `TP1`–`TP8` from `B.Cu` so every node stays accessible from behind even after the front panel is bolted on.
3. **Dry-Fit Front-Panel Controls (`F.Cu`)**:
    Insert all 8 front-side parts **unsoldered** into `F.Cu`, matching each component to the dual-sided `F.SilkS`/`B.SilkS` labels so identical-footprint pots are never swapped:
    - `RV1` $\rightarrow$ **`GAIN A100k`**
    - `RV2` $\rightarrow$ **`ATK A50k`**
    - `RV3` $\rightarrow$ **`REL A1M`**
    - `RV4` $\rightarrow$ **`OFFSET B10k`**
    - `J1` (`IN`), `J2` (`OUT`), `J3` (`INV_OUT`) $\rightarrow$ `WQP-PJ398SM` jacks
    - `D4` (`LED`) $\rightarrow$ `3 mm` LED (verify long lead `+` anode and flat edge `-` cathode match the dual-sided `+`/`-` marks)
4. **Align Against Front Panel & Solder**:
    Place the 3U front panel over the shafts and bushings, tighten the M6/M7 panel nuts finger-tight, position `D4` flush inside its `3.2 mm` bezel hole, and **only after the front panel aligns everything mechanically**, solder all pot lugs, jack pins, and LED leads on `B.Cu`.
5. **Bench Bring-Up Using `TP1`–`TP8`**:
    - Power the module via a current-limited $\pm 12\text{ V}$ bench supply (or Eurorack skiff), clip ground to **`TP1` (`GND`)**, and confirm **`~+11.78 V`** on **`TP2` (`+12V`)** and **`~-11.78 V`** on **`TP3` (`-12V`)**.
    - With nothing patched into `J1` (`IN`), verify `D4` (`LED`) is completely dark (`0 mA`) and check **`TP8` (`OFS`)** sweeps smoothly from `~-9.8 V` to `~+9.8 V` as you turn `RV4` (`OFFSET`).
    - Feed a `1 kHz` `5 Vpp` sine wave into `J1` (`IN`) and probe **`TP4` (`PRE`)** (`-0.1×` to `-10.1×` gain), **`TP5` (`HALF`)** (clean negative half-wave), **`TP6` (`RECT`)** (`+1.0× |PRE|` full-wave), and **`TP7` (`ENV`)** (smooth positive envelope tracking down to millivolts without deadzone).
