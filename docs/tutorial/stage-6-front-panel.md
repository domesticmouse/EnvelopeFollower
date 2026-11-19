# Stage 6: Mated 3U Eurorack Front Panel Construction

Instead of buying costly custom-milled aluminum, you can fabricate a rigid `1.6 mm` FR4 PCB front panel (matte black solder mask with crisp white silkscreen) directly from the finalized coordinates in `EnvelopeFollower.kicad_pcb`.

## AI Agent Prompt

> *"Using the `eurorack-panel` skill, inspect `EnvelopeFollower.kicad_pcb` to extract every pot (`RV1`–`RV4`), jack (`J1`–`J3`), and LED (`D4`) bushing coordinate, generate the mated 6 HP × 3U front panel PCB at `panel/EnvelopeFollower_Panel.kicad_pcb` titled `ENV FOLLOW` (`6HP ANALOG`) with panel labels `GAIN`, `ATK`, `REL`, `OFFSET`, boxed `IN`, `ENV`, `OUT`, and `INV OUT`, refill `F.Cu`/`B.Cu` `GND` shield planes, run DRC, export Gerbers and drills to `production/panel/`, and verify the Gerbers with the `kicad` skill."*

## Step 6.1: Inspect Mechanical Coordinates

Run `generate_eurorack_panel.py --inspect` against the main PCB:

```bash
python3 .agents/skills/eurorack-panel/scripts/generate_eurorack_panel.py \
    --main-pcb EnvelopeFollower.kicad_pcb \
    --inspect
```

Observed coordinate alignment between the 8 front-panel THT controls (`RV1`–`RV4`, `J1`–`J3`, `D4`) and the 3U front panel:

```text
=== Eurorack Panel Mechanical Report for EnvelopeFollower.kicad_pcb ===
Main PCB Outline   : 29.60 x 107.00 mm (X: 100.20..129.80, Y: 20.75..127.75)
Target Front Panel : 6HP x 3U (30.00 x 128.50 mm), Vertical rail overhang = 10.75 mm top/bottom
Panel Origin (0,0) : Global (100.00, 10.00) mm -> (130.00, 138.50) mm

Ref   Panel Label / Role       FP Origin (X, Y)     Bushing Global (X, Y)   Panel-Local (X, Y)   Drill
-------------------------------------------------------------------------------------------------------
RV1   GAIN (A100k)             (112.50,  36.50)     (115.00,  29.00)        ( 15.00,  19.00)     7.2 mm
RV2   ATK (A50k)               (112.50,  53.00)     (115.00,  45.50)        ( 15.00,  35.50)     7.2 mm
RV3   REL (A1M)                (112.50,  69.50)     (115.00,  62.00)        ( 15.00,  52.00)     7.2 mm
RV4   OFFSET (B10k)            (112.50,  86.00)     (115.00,  78.50)        ( 15.00,  68.50)     7.2 mm
J1    IN (3.5mm_Jack)          (108.00,  91.52)     (108.00,  98.00)        (  8.00,  88.00)     6.2 mm
D4    ENV (LED_3mm)            (120.73,  98.00)     (122.00,  98.00)        ( 22.00,  88.00)     3.2 mm
J2    OUT (3.5mm_Jack)         (108.00, 109.52)     (108.00, 116.00)        (  8.00, 106.00)     6.2 mm
J3    INV_OUT (3.5mm_Jack)     (122.00, 109.52)     (122.00, 116.00)        ( 22.00, 106.00)     6.2 mm
```

Notice how sharing the same global KiCad coordinate space (`100.00, 10.00` to `130.00, 138.50`) ensures every hole cutout aligns to the exact micron with the main PCB's shaft and bushing centers.

!!! tip "Mapping Sequential References (`RV1`–`RV4`, `J1`–`J3`, `D4`) to Panel Labels"
    In `generate_eurorack_panel.py`, `clean_label(value, ref)` uses `Value` directly whenever `Value` is descriptive (e.g., `GAIN`, `ATK`, `REL`, `OFFSET`, `IN`, `ENV`, `OUT`, `INV_OUT`), and only falls back to `Reference` (stripping `RV_`/`J_`/`SW_` or mapping `LED*` $\rightarrow$ `ENV`) when `Value` is generic (`100k`, `50k`, `1M`, `3.5mm_Jack`, `LED_3mm`). Keeping functional names in each front-panel footprint's `Value` (or using `RV_GAIN` / `J_IN` style references) ensures `generate_eurorack_panel.py` automatically generates `GAIN`, `ATK`, `REL`, `OFFSET`, boxed `IN`, `ENV`, `OUT`, and `INV OUT` while `B.SilkS`/`F.SilkS` on the main PCB retains full build labels (`RV1 GAIN A100k`, `RV2 ATK A50k`, `RV3 REL A1M`, `RV4 OFFSET B10k`).

## Step 6.2: Generate the Panel PCB, Run DRC & Package Gerbers

```bash
python3 .agents/skills/eurorack-panel/scripts/generate_eurorack_panel.py \
    --main-pcb EnvelopeFollower.kicad_pcb \
    --output panel/EnvelopeFollower_Panel.kicad_pcb \
    --title "ENV FOLLOW" \
    --subtitle "6HP ANALOG" \
    --gerber-dir production/panel \
    --zip production/EnvelopeFollower_Panel.zip \
    --drc
```

Output:

```text
Generated panel/EnvelopeFollower_Panel.kicad_pcb (6HP / 30.0x128.5mm, 8 jack cutouts).
DRC Summary: 0 violations, 0 unconnected items.
Exported Gerbers & Drills to production/panel
Packaged fabrication archive at production/EnvelopeFollower_Panel.zip
```

## Panel Engineering Highlights

- **Doepfer A-100 3U Mounting Slots (`H1`, `H2`)**: Oval `5.5 x 3.2 mm` NPTH slots centered at panel-local `(7.50, 3.00)` and `(7.50, 125.50)` fit both fixed threaded rail strips and sliding M3 nuts.
- **Blemish-Free Front Shielding (`(layers "*.Cu" "B.Mask")`)**: Pot (`7.2 mm`) and jack (`6.2 mm`) holes use plated through-hole pads connected solidly to the `F.Cu` and `B.Cu` `GND` shield zones. Leaving `F.Mask` tented over the front copper ring yields a clean exterior surface around the M6/M7 nuts, while exposing `B.Mask` on the rear automatically grounds the entire front panel shield to chassis `GND` when the hardware nuts tighten against the back face.
- **Silkscreen Clarity & Input Callout Box**: Clear `F.SilkS` legends label `GAIN`, `ATK`, `REL`, `OFFSET`, boxed `IN`, `ENV`, `OUT`, and `INV OUT`, with a `5 × 5 mm` white square placed on `B.SilkS` that JLCPCB replaces with an order QR code during fabrication.

| 3U Front Panel (`F.Cu` / `F.SilkS`) | 3U Front Panel Rear (`B.Cu` / Grounding Rings) |
| :---: | :---: |
| ![3U Front Panel — Front Face](../images/panel_front.png) | ![3U Front Panel — Rear Grounding Face](../images/panel_back.png) |

## Step 6.3: Verify Panel PCB & Gerbers with `kicad` Analyzers

```bash
python3 .agents/skills/kicad/scripts/analyze_pcb.py panel/EnvelopeFollower_Panel.kicad_pcb --full --output /tmp/panel_pcb.json
python3 .agents/skills/kicad/scripts/analyze_gerbers.py production/panel/ --full --output /tmp/panel_gerbers.json
```

Verified analyzer results on [`panel/EnvelopeFollower_Panel.kicad_pcb`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/panel/EnvelopeFollower_Panel.kicad_pcb) and [`production/panel/`](https://github.com/domesticmouse/EnvelopeFollower/tree/main/production/panel):

- **PCB Analyzer**: `0` errors, `0` warnings, `10` footprints (`8` controls + `2` M3 slots), `2` filled copper zones (`F.Cu`, `B.Cu`), `30.0 x 128.5 mm` outline, `routing_complete: True`.
- **Gerber Analyzer**: `0` findings across all severities; `9/9` Gerber layers complete (`B.Cu`, `B.Mask`, `B.Paste`, `B.SilkS`, `Edge.Cuts`, `F.Cu`, `F.Mask`, `F.Paste`, `F.SilkS`); `7` PTH component holes (`3 × 6.2 mm`, `4 × 7.2 mm`) and `3` NPTH mounting/LED holes (`3.2 mm` LED hole + `2` M3 oval slots).
