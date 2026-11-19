# KiCad PCB & Fabrication Checklist

The improved SKiDL circuit definition (`envelope_follower.py`), KiCad netlist (`envelope_follower.net`), XML BOM (`envelope_follower_bom.xml`), and JLCPCB SMT BOM (`jlcpcb_bom.csv`) cover **54 populated components + 8 optional `DNP` test points (62 footprints total) across 36 nets** (`45` SMD components across `18` BOM lines + `9` manual THT parts).

Follow this checklist to take the improved design through KiCad PCB layout, dual-sided silkscreen verification, front-panel generation, and JLCPCB manufacturing.

---

## Step 1: Create Project & Import Netlist into KiCad PCB Editor

### Option A — Via the KiCad GUI
- [ ] Open KiCad (v10) and create a new project: **File → New Project...** (`EnvelopeFollower.kicad_pro`).
- [ ] Open **PCB Editor** (`EnvelopeFollower.kicad_pcb`).
- [ ] Import the netlist via **File → Import → Netlist...** and select `envelope_follower.net`.
- [ ] Click **Update PCB** and **Close** to load all 62 footprints (`54` populated + `8` `DNP`) and 36 nets onto the canvas.

### Option B — Automated `.kicad_pcb` Generation (Recommended)
- [x] Generate `EnvelopeFollower.kicad_pcb` directly from `envelope_follower.net` via `generate_kicad_pcb.py` (`Edge.Cuts`, panel bushing grid, `B.Cu` SMT grouping, `DNP` test points, and dual-sided silkscreen markup).

---

## Step 2: Main Circuit PCB Layout (`EnvelopeFollower.kicad_pcb`)

- [x] **Board Outline (`Edge.Cuts`)**: `29.60 × 107.00 mm` for 6 HP (`30.0 mm` panel width) with `10.75 mm` vertical 3U rail/M3 screw clearance.
- [x] **Front-Panel Controls (`F.Cu`)**: Arrange the 8 vertical panel-mounted parts on the ergonomic bushing grid:
    - [x] Potentiometers (`RV1` `GAIN A100k`, `RV2` `ATK A50k`, `RV3` `REL A1M`, `RV4` `OFFSET B10k`)
    - [x] Status Indicator (`D4` `LED_D3.0mm`)
    - [x] 3.5mm Jacks (`J1` `IN`, `J2` `OUT`, `J3` `INV_OUT` — `WQP-PJ398SM`)
- [x] **Rear Power Connector & Optional Test Points (`B.Cu`)**:
    - [x] Flip `J_PWR` (`IDC-Header_2x05_P2.54mm_Vertical`) to `B.Cu` with Pin 1/Pin 2 (`-12V / RED STRIPE`) at the bottom.
    - [ ] Place optional `TP1`–`TP8` (`Ronghe RH-5001` / `TestPoint_Keystone_5000-5004_Miniature`, `1.0 mm` drill) marked **`DNP`** (`exclude_from_pos_files`, `exclude_from_bom`) near their target nodes (`TP7` on buffered `ENV_SIG`, never raw `ENV_CAP`).
- [ ] **SMT Placement (Single-Sided `B.Cu` for JLCPCB Economic PCBA)**:
    - [ ] Place `U1` and `U2` (`TL074HIDR`, `SOIC-14`) centrally with local `100 nF` bypass caps (`C5`–`C8`) within `2 mm` of Pin 4 (`+12V`) and Pin 11 (`-12V`).
    - [ ] Place `D5`/`D6` (`B5819W`), `R26`/`R27` (`10 Ω` `1/4 W` `1206`), and `C3`/`C4` (`10 µF` `50 V`, checking `C4` `+` on `GND`) next to `J_PWR`.
    - [ ] Place `D8`/`D9` (`BAT54SLT1G` `SOT-23`) and `R16`/`R19` (`1 kΩ` `1/4 W` `1206`) near `J2` (`OUT`) and `J3` (`INV_OUT`).
    - [ ] Place `C10`/`C11` (`47 pF` C0G), `D7` (`1N4148W`), `R24` (`100 kΩ`), `C9` (`100 nF`), and remaining `0603`/`0805`/`SOD-123` passives near their respective stages, keeping `ENV_CAP` (`C2` `220 nF`) compact and away from power rails.
- [ ] **Silkscreen Markup (`F.SilkS` & `B.SilkS`)**:
    - [ ] Display both Reference and Value on `B.SilkS` outside component courtyards for all 45 SMD parts (`U1 TL074H`, `R8 20k`, `C10 47pF`, `D8 BAT54S`, etc.).
    - [ ] Label `TP1 GND`–`TP8 OFS` and all 9 THT parts (`RV1 GAIN A100k`, `RV2 ATK A50k`, `RV3 REL A1M`, `RV4 OFFSET B10k`, `J1 IN`, `J2 OUT`, `J3 INV_OUT`, `D4 LED +/-`, `J_PWR +/-12V`) on **both `F.SilkS` and `B.SilkS`**.
    - [ ] Verify external Pin-1 dots (`U1`, `U2`), diode cathode bars (`|`), electrolytic `+` marks, `>= 0.8 mm` text height, `>= 0.15 mm` stroke, `>= 0.20 mm` pad clearance, and `5 × 5 mm` JLCPCB QR placeholder square.
- [ ] **Routing, Ground Pour & DRC** (see [Stage 5](../tutorial/stage-5-schematic-and-pcb.md)):
    - [ ] Route `Power` netclass (`+12V_IN`, `+12V_PROT`, `+12V`, `-12V_IN`, `-12V_PROT`, `-12V`) at `0.60 mm` width and analog signal nets at `0.25 mm` width.
    - [ ] Add `GND` copper pours on both `F.Cu` and `B.Cu` with stitching vias.
    - [ ] Run **DRC** (`0` errors, `0` clearance violations, `0` unrouted nets) and run `kicad` skill analyzer (`analyze_pcb.py`).

---

## Step 3: Mated 3U Eurorack Front Panel PCB

- [x] Generate the mated 3U front panel (`panel/EnvelopeFollower_Panel.kicad_pcb`) from the main PCB's finalized coordinates (see [Stage 6](../tutorial/stage-6-front-panel.md)):
    - [x] Extract exact `(x, y)` positions of `RV1`–`RV4`, `D4`, and `J1`–`J3`, applying footprint-to-bushing mechanical offsets (`+6.48 mm` for `WQP-PJ398SM`, `(+2.50, -7.50)` for `RD901F` at `90°`, `+1.27 mm` for `LED_D3.0mm`).
    - [x] Place standard Doepfer A-100 3U (`128.5 mm` height) M3 mounting slots (`5.5 × 3.2 mm` NPTH).
    - [x] Add front-panel labels (`GAIN`, `ATK`, `REL`, `OFFSET`, boxed `IN`, `OUT`, `INV OUT`, `ENV`) and grounded `F.Cu`/`B.Cu` shield planes.
    - [x] Pass DRC (`0 violations, 0 unconnected items`) and verify with `analyze_pcb.py` & `analyze_gerbers.py`.

---

## Step 4: Export Fabrication, JLCPCB PCBA & Bench Bring-Up

- [ ] Export fabrication **Gerbers** and **Excellon drill** files for `EnvelopeFollower.kicad_pcb` (panel Gerbers are packaged in `production/EnvelopeFollower_Panel.zip`).
- [ ] Export the **Bottom-Side SMD Centroid (`.pos` / CPL)** file with `--side back --smd-only --exclude-dnp` so only the `45` `B.Cu` SMD components appear (`TP1`–`TP8` `DNP` and `9` THT parts excluded).
- [ ] Upload the Gerber ZIP, 18-line `jlcpcb_bom.csv` (`15` Basic + `3` Extended), and CPL `.pos` file to JLCPCB; inspect every part's orientation and `B.SilkS` value label in the 3D/DFM preview (`U1`, `U2`, `D1`–`D3`, `D5`–`D9`, `C3`, `C4`).
- [ ] Hand-solder `J_PWR` (`B.Cu`), optional `TP1`–`TP8` (`Ronghe RH-5001` on `B.Cu`), dry-fit `RV1`–`RV4`, `J1`–`J3`, `D4` against the 3U front panel before soldering, and verify rails/signals across `TP1`–`TP8`.
