# Stage 6: Interactive KiCad Work (Routing, Ground Pours & Verification)

At this stage, [`EnvelopeFollower.kicad_pcb`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/EnvelopeFollower.kicad_pcb) has all 62 footprints (`54` populated + `8` `DNP` test points) positioned, `Edge.Cuts` defined, dual-sided silkscreen labels placed, and all 36 nets loaded as an unrouted ratsnest (`0` copper tracks, `0` copper zones). Open `EnvelopeFollower.kicad_pcb` in **KiCad 10 PCB Editor** to complete routing and verification.

## 6.1 Routing Strategy

1. **Verify Grid & Netclass Setup**:
    In **File → Board Setup → Design Rules → Net Classes**, confirm the `Power` netclass (`0.60 mm` track width, `0.25 mm` clearance, `0.80 mm` via diameter, `0.40 mm` drill) is assigned to `+12V_IN`, `+12V_PROT`, `+12V`, `-12V_IN`, `-12V_PROT`, `-12V`, and `GND`. Leave the `Default` netclass at `0.25 mm` width for analog signal nets.

2. **Route Power Rails First (`B.Cu`)**:
    - Route `+12V_IN` and `-12V_IN` from `J_PWR` through Schottky diodes `D5` and `D6` (`B5819W`) and series `10 Ω` `1/4 W` (`1206`) resistors `R26` and `R27` into bulk `10 µF` electrolytics `C3` and `C4` (confirm `C4`'s `+` pad connects to `GND` and `-` pad connects to `-12V`).
    - Route `+12V` and `-12V` at `0.60 mm` width to `U1` and `U2` (Pins 4 and 11), passing **through** the pads of local ceramic bypass capacitors `C5`–`C8` before reaching the IC pins.
    - Branch `+12V` and `-12V` to `BAT54S` rail clamps `D8` (`AMP_OUT`) and `D9` (`INV_AMP_OUT`), offset bias resistors `R11` and `R12`, and test points `TP2` (`+12V`) and `TP3` (`-12V`), with `TP1` anchored to `GND`.

3. **Route Sensitive Analog Summing & High-Impedance Nodes (`B.Cu` / `F.Cu`)**:
    - Keep inverting summing junctions as short and compact as possible to minimize parasitic capacitance and noise pickup:
      - `PREAMP_INV` (`U1A` Pin 2, `R2`, `R25`, `C10`)
      - `RECT1_INV` (`U1B` Pin 6, `R3`, `R4`, `D1`)
      - `RECT2_INV` (`U1C` Pin 9, `R5`, `R7`, `R8`)
      - `PK_FB_INV` (`U2C` Pin 9, `R24`, `D7`, `C11`)
      - `AMP_INV` (`U1D` Pin 13, `R13`–`R15`)
      - `INV_STAGE_IN` (`U2A` Pin 2, `R17`, `R18`)
      - `LED_K` (`U2B` Pin 6, `D4` cathode, `R21`)
    - **Protect High-Impedance `ENV_CAP`**: Keep the node connecting `RV2`, `C2` (`220 nF`), `R10` (`47k`), and `U2D` Pin 12 (`+`) short and routed away from power tracks to prevent leakage. Keep `TP7` (`ENV`) connected strictly to buffered `ENV_SIG` (`U2D` Pin 14), never to `ENV_CAP`.
    - Place `C9` (`100 nF`) directly at `RV4` wiper (`OFFSET_WIPER`) and `R13`, and keep `D8`/`R16` and `D9`/`R19` close to output jacks `J2` and `J3`.
    - Use `F.Cu` strictly for short jumpers or THT control interconnections so the front side stays clean beneath potentiometer bodies and jack housings.

4. **Add Ground Copper Pours & Stitching Vias (`F.Cu` + `B.Cu`)**:
    - Draw full-board filled copper zones (`Add Filled Zone`) assigned to net `GND` on both `F.Cu` and `B.Cu` (inset `0.30 mm` from `Edge.Cuts`, thermal relief spokes on THT/SMD pads).
    - Drop `GND` stitching vias (`0.4 mm` drill / `0.8 mm` pad) near `J_PWR`, `J1`–`J3`, `U1`, `U2`, decoupling caps `C5`–`C8`, and along the board perimeter, then press **`B`** to refill all zones.

5. **Verify Silkscreen Clearance & Run Design Rules Check (DRC)**:
    - Inspect `B.SilkS` and `F.SilkS` to confirm no value label (`R8 20k`, `C10 47pF`, `TP1 GND`–`TP8 OFS`, `RV1 GAIN A100k`, etc.) overlaps any solder mask opening or exposed pad (`>= 0.20 mm` clearance) so JLCPCB does not auto-clip text.
    - Run **Inspect → Design Rules Checker** (or CLI):

    ```bash
    /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc \
        --refill-zones --exit-code-violations --format json \
        --output /tmp/main_drc.json EnvelopeFollower.kicad_pcb
    ```

    Confirm `0` DRC errors, `0` clearance violations, and `0` unrouted nets.

## 6.2 Automated Design Audit with the `kicad` Skill

After routing, run the `kicad` skill analyzers on both the schematic and routed PCB to verify decoupling proximity, silkscreen-over-pad clearances, `DNP` test-point attributes, and cross-domain net parity:

```bash
python3 .agents/skills/kicad/scripts/analyze_schematic.py EnvelopeFollower.kicad_sch --analysis-dir analysis/
python3 .agents/skills/kicad/scripts/analyze_pcb.py EnvelopeFollower.kicad_pcb --full --analysis-dir analysis/
python3 .agents/skills/kicad/scripts/cross_analysis.py \
    --schematic analysis/<run_id>/schematic.json \
    --pcb analysis/<run_id>/pcb.json \
    --analysis-dir analysis/
```
