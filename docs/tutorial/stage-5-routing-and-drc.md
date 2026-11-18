# Stage 5: Interactive KiCad Work (Routing, Ground Pours & Verification)

At this stage, [`EnvelopeFollower.kicad_pcb`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/EnvelopeFollower.kicad_pcb) has all 48 footprints positioned, `Edge.Cuts` defined, and all 35 nets loaded as an unrouted ratsnest (`0` copper tracks, `0` copper zones). Open `EnvelopeFollower.kicad_pcb` in **KiCad 10 PCB Editor** to complete routing and verification.

## 5.1 Routing Strategy

1. **Verify Grid & Netclass Setup**:
    In **File → Board Setup → Design Rules → Net Classes**, confirm the `Power` netclass (`0.60 mm` track width, `0.25 mm` clearance, `0.80 mm` via diameter, `0.40 mm` drill) is assigned to `+12V_RAW`, `-12V_RAW`, `+12V`, `-12V`, and `GND`. Leave the `Default` netclass at `0.25 mm` width for analog signal nets.
2. **Route Power Rails First (`B.Cu`)**:
    - Route `+12V_RAW` and `-12V_RAW` from `J_PWR` through Schottky diodes `D4` and `D5` into bulk electrolytics `C3` and `C4`.
    - Route `+12V` and `-12V` at `0.60 mm` width to `U1` and `U2` (Pins 4 and 11), passing **through** the pads of local ceramic bypass capacitors `C5`–`C8` before reaching the IC pins.
    - Branch `+12V` to `R11` and `-12V` to `R12` and `R23` (`RV_OFFSET` and `LED1` cathode bias).
3. **Route Sensitive Analog Summing Nodes (`B.Cu` / `F.Cu`)**:
    - Keep inverting summing junctions (`GAIN_FB_IN` at `U1` Pin 2, `HALF_WAVE_IN` at `U1` Pin 6, `SUM_IN` at `U1` Pin 9, `OFFSET_SUM_IN` at `U1` Pin 13, and `INV_SUM_IN` at `U2` Pin 2) as short and compact as possible to minimize parasitic capacitance and noise pickup.
    - Use `F.Cu` strictly for short jumpers or THT control interconnections so the front side stays clean beneath potentiometer bodies and jack housings.
4. **Add Ground Copper Pours & Stitching Vias (`F.Cu` + `B.Cu`)**:
    - Draw full-board filled copper zones (`Add Filled Zone`) assigned to net `GND` on both `F.Cu` and `B.Cu` (inset `0.30 mm` from `Edge.Cuts`, thermal relief spokes on THT/SMD pads).
    - Drop `GND` stitching vias (`0.4 mm` drill / `0.8 mm` pad) near `J_PWR`, `J_IN`, `J_OUT`, `J_INV_OUT`, `U1`, `U2`, and along the board perimeter, then press **`B`** to refill all zones.
5. **Run Design Rules Check (DRC)**:
    Run **Inspect → Design Rules Checker** (or CLI):

    ```bash
    /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc \
        --refill-zones --exit-code-violations --format json \
        --output /tmp/main_drc.json EnvelopeFollower.kicad_pcb
    ```

    Confirm `0` DRC errors, `0` clearance violations, and `0` unrouted nets.

## 5.2 Automated Design Audit with the `kicad` Skill

After routing, run the `kicad` skill analyzers on both the schematic and routed PCB to catch decoupling gaps, silkscreen overlaps, or cross-domain mismatches:

```bash
python3 .agents/skills/kicad/scripts/analyze_schematic.py EnvelopeFollower.kicad_sch --analysis-dir analysis/
python3 .agents/skills/kicad/scripts/analyze_pcb.py EnvelopeFollower.kicad_pcb --full --analysis-dir analysis/
python3 .agents/skills/kicad/scripts/cross_analysis.py \
    --schematic analysis/<run_id>/schematic.json \
    --pcb analysis/<run_id>/pcb.json \
    --analysis-dir analysis/
```
