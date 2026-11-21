# KiCad PCB & Fabrication Checklist

The improved SKiDL circuit definition (`envelope_follower.py`), KiCad netlist (`envelope_follower.net`), XML BOM (`envelope_follower_bom.xml`), and JLCPCB SMT BOM (`jlcpcb_bom.csv`) cover **60 populated components (`49` `B.Cu` SMD + `11` Manual/Consigned THT) plus `8` optional `DNP` test points (`TP1`–`TP8`) and `3` `DNP` optical fiducials (`FID1`–`FID3`) — `71` footprints total across `42` active nets**.

Follow this checklist to take the improved design through KiCad PCB layout, dual-sided silkscreen verification, front-panel generation, and JLCPCB manufacturing.

---

## Step 1: Create Project & Import Netlist into KiCad PCB Editor

### Option A — Via the KiCad GUI
- [ ] Open KiCad (v10) and create a new project: **File → New Project...** (`EnvelopeFollower.kicad_pro`).
- [ ] Open **PCB Editor** (`EnvelopeFollower.kicad_pcb`).
- [ ] Import the netlist via **File → Import → Netlist...** and select `envelope_follower.net`.
- [ ] Click **Update PCB** and **Close** to load all 71 footprints (`60` populated + `8` `DNP` test points + `3` `DNP` fiducials) and 42 active nets onto the canvas.

### Option B — Automated `.kicad_pcb` Generation (Recommended)
- [x] Generate `EnvelopeFollower.kicad_pcb` directly from `envelope_follower.net` via `generate_kicad_pcb.py` (`Edge.Cuts`, `2 × 4` front-panel bushing grid, `B.Cu` SMT corridors + `J4` + `C1`/`C2`, `DNP` test points & fiducials, dual-sided silkscreen markup, `HVGridRouter` routing, and stitched `GND` pours).

---

## Step 2: Main Circuit PCB Layout (`EnvelopeFollower.kicad_pcb`)

- [x] **Board Outline (`Edge.Cuts`)**: `30.00 × 108.00 mm` for 6 HP (`30.00 × 128.50 mm` panel) with `10.25 mm` vertical 3U rail/M3 screw overhang top and bottom.
- [x] **Front-Panel Controls (`F.Cu`, `2 × 4` Grid at `X = 7.50, 22.50 mm`)**:
    - [x] Potentiometers (`Potentiometer_Alps_RK09K_Single_Vertical`: `RV1 GAIN A100k`, `RV2 ATK A50k`, `RV3 REL A1M`, `RV4 OFF B10k`)
    - [x] Status Indicator (`D4 LED_D3.0mm`)
    - [x] 3.5mm Jacks (`J1 IN`, `J2 OUT`, `J3 INV_OUT` — `WQP-PJ398SM`)
- [x] **Rear THT Hardware, Film Caps, Fiducials & Optional Test Points (`B.Cu`)**:
    - [x] Flip `J4` (`IDC-Header_2x05_P2.54mm_Vertical`) to `B.Cu` with Pins `1–2` (`RED STRIPE / -12V`) at the bottom.
    - [x] Mount `C1` and `C2` (`1 µF 100 V` `P=5mm` TDK PET film, `C125397`) on `B.Cu` so `F.Cu` clears the `10.25 mm` front-panel standoff.
    - [x] Place optional `TP1`–`TP8` (`Ronghe RH-5001`, `1.0 mm` drill) marked **`DNP`** (`SetDNP`, `SetExcludedFromBOM`, `SetExcludedFromPosFiles`) on low-impedance rails and buffered/closed-loop outputs (`TP1 GND`, `TP2 +12V`, `TP3 -12V`, `TP4 IN_BUF`, `TP5 PREAMP`, `TP6 RECT`, `TP7 OUT`, `TP8 INV_OUT` — deliberately omitting `IN_AC`, virtual-ground summing pins, and `ENV_NODE`).
    - [x] Place `3` asymmetrical `B.Cu` optical fiducials (`FID1`–`FID3`, `1.0 mm` pad / `2.0 mm` mask, `±1.25 mm` silkscreen keepout) marked **`DNP`**, `exclude_from_bom`, and `exclude_from_pos_files`.
- [x] **SMT Placement (Single-Sided `B.Cu` for JLCPCB Economic PCBA — `49` SMDs across `19` lines)**:
    - [x] Place `U1` and `U2` (`TL074HIDR`, `SOIC-14`) with local `100 nF 50 V X7R` bypass caps (`C_DEC1`–`C_DEC4`) within `< 3–5 mm` of Pin `4` (`+12V`) and Pin `11` (`-12V`).
    - [x] Place `D_PWR_P`/`D_PWR_N` (`B5819W`), `R_PWR_P`/`R_PWR_N` (`10 Ω 1206`), and `C3`/`C4` (`22 µF 50 V`, checking `C4` `+` on `GND`) next to `J4`.
    - [x] Place `7 × 10 kΩ ±0.1%` (`C95204`) matched resistors and `D1_D2` (`BAT54S`) tightly around `U1B`/`U1C`.
    - [x] Place `D_IN`/`D_OUT`/`D_INV_OUT` (`BAV99`) and split `470 Ω + 470 Ω 0.5 W` (`1210`) clash resistors (`R16A/B`, `R19A/B`) with midpoint `R15`/`R18` feedback and `C_OUT1`/`C_OUT2` (`100 pF C0G`) near `U1D`, `U2A`, `J1`, `J2`, and `J3`.
    - [x] Place `D3` & `D_LED_CLAMP` (`1N4148WS`), `R_ATK_MIN` (`470 Ω`), `R_LED` (`2.2 kΩ`), `C_HF` (`47 pF C0G`), `R_GAIN_FAIL` (`1 MΩ`), and remaining `0603` passives near their respective stages.
- [x] **Silkscreen Markup (`F.SilkS` & `B.SilkS`)**:
    - [x] Display concise value-only tokens on `.SilkS` for all `41` fixed `R*`/`C*` passives (including suffixed refs `R_PWR_*`, `R16A/B`, `C_DEC*`, `C_HF`, `C_OUT*`, keeping `<REF>` on `.Fab`) and `<REF> + <VAL>` for ICs and diodes (`U1 TL074H`, `D1_D2 BAT54S`, `D3 1N4148WS`, `D_IN BAV99`), verified **`RESULT: PASS`** (`68/68` labeled, `0` tether drift) in `silk_annotator.py --inspect`.
    - [x] Label `TP1 GND`–`TP8 INV_OUT`, `C1`/`C2` (`1uF`), and all 9 THT interface parts (`RV1 GAIN A100k`, `RV2 ATK A50k`, `RV3 REL A1M`, `RV4 OFF B10k`, `J1 IN`, `J2 OUT`, `J3 INV_OUT`, `D4 LED +/-`, `J4 PWR` + `-12V Pin 1` / `RED STRIPE / -12V`) on **both `F.SilkS` and `B.SilkS`**.
    - [x] Verify external `SOIC-14`/`SOT-23` Pin-1 dots, `0.25 mm` discrete diode cathode bars, `C3`/`C4` `+` marks, `RV1`–`RV4` Pin `1` markers, `5.0 × 5.0 mm` via-free JLCPCB QR square on `B.SilkS`, and `100%` `B.Fab` fabrication notes.
- [x] **Routing, Ground Pour & DRC** (see [Stage 5](../tutorial/stage-5-schematic-and-pcb.md)):
    - [x] Route power nets at `0.30 mm` width and analog signal nets at `0.25 mm` width via `HVGridRouter`.
    - [x] Fill `GND` copper pours on `F.Cu` and `B.Cu` with `212` stitching/signal vias (`0` isolated copper pockets).
    - [x] Pass KiCad **DRC** (`0` violations, `0` unconnected items) and `analyze_pcb.py --full` (`0` errors, `42/42` nets routed).

---

## Step 3: Mated 3U Eurorack Front Panel PCB

- [x] Generate the mated 3U front panel (`panel/EnvelopeFollower_Panel.kicad_pcb`) from the main PCB's finalized coordinates (see [Stage 6](../tutorial/stage-6-front-panel.md)):
    - [x] Extract exact `(x, y)` positions of `RV1`–`RV4`, `D4`, and `J1`–`J3`, applying rotated `fp_circle` offsets (`+6.48 mm` for `WQP-PJ398SM`, `(+2.50, -7.50)` for `Alps RK09K` at `90°`, `+1.27 mm` for `LED_D3.0mm`).
    - [x] Place standard Doepfer A-100 3U (`128.5 mm` height) M3 mounting slots (`5.5 × 3.2 mm` NPTH).
    - [x] Add front-panel labels (`GAIN`, `ATK`, `REL`, `OFFSET` via `--label RV4=OFFSET`, boxed `IN`, `ENV` via `--label D4=ENV`, `OUT`, `INV OUT`), `5.0 × 5.0 mm` `B.SilkS` QR square, and grounded `F.Cu`/`B.Cu` shield planes.
    - [x] Pass `--drc` (`0` non-library violations, `0` unconnected items) and verify with `analyze_pcb.py` (`0` errors, `0` warnings) & `analyze_gerbers.py` (`0` findings).

---

## Step 4: Export Fabrication, JLCPCB PCBA & Bench Bring-Up

- [x] Export fabrication **Gerbers** (`9/9` layers) and **Excellon drill** files (`production/EnvelopeFollower_Main.zip` and `production/EnvelopeFollower_Panel.zip`, `14` files each, excluding `_cpl.csv`).
- [x] Export the **Bottom-Side SMD Centroid (`.pos` / CPL)** file (`production/main/EnvelopeFollower_cpl.csv`) with `--side back --smd-only --exclude-dnp`, confirming `49/49` `Layer=Bottom` rows match `jlcpcb_bom.csv` (`TP1`–`TP8`, `FID1`–`FID3`, and all `11` THT parts excluded).
- [ ] Upload `production/EnvelopeFollower_Main.zip`, 19-line `jlcpcb_bom.csv` (`14` Basic + `5` Extended), and `production/main/EnvelopeFollower_cpl.csv` to JLCPCB (Black mask, White silkscreen, **Bottom Side** Economic PCBA, specify QR over `5 × 5 mm` `B.SilkS` square); inspect every asymmetrical/polarized part's rotation in JLCPCB's 3D/CPL viewer (`U1`, `U2`, `D_PWR_P/N`, `D1_D2`, `D3`, `D_LED_CLAMP`, `D_IN`, `D_OUT`, `D_INV_OUT`, `C3`, `C4`).
- [ ] Upload `production/EnvelopeFollower_Panel.zip` (`1.6 mm` FR-4, matte Black mask, White silkscreen, ENIG recommended, specify QR over `5 × 5 mm` `B.SilkS` square).
- [ ] Hand-solder `J4`, `C1`/`C2`, and optional `TP1`–`TP8` (`RH-5001`) on `B.Cu`, dry-fit `RV1`–`RV4`, `J1`–`J3`, and `D4` against the 3U front panel before soldering, and verify rails/signals across `TP1`–`TP8`.
