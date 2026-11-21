# Stage 6: Mated 3U Eurorack Front Panel Construction

Instead of buying costly custom-milled aluminum, you can fabricate a rigid `1.6 mm` FR4 PCB front panel (matte black solder mask with crisp white silkscreen) directly from the finalized coordinates in `EnvelopeFollower.kicad_pcb`.

## AI Agent Prompt

> *"`/eurorack-panel` Please inspect `@EnvelopeFollower.kicad_pcb` to extract every pot (`RV1`–`RV4`), jack (`J1`–`J3`), and LED (`D4`) bushing coordinate, generate the mated 6 HP × 3U front panel PCB at `panel/EnvelopeFollower_Panel.kicad_pcb` titled `ENV FOLLOW` (`6HP ANALOG`) with panel labels `GAIN`, `ATK`, `REL`, `OFFSET`, boxed `IN`, `ENV`, `OUT`, and `INV OUT`, refill `F.Cu`/`B.Cu` `GND` shield planes, run DRC, export Gerbers and drills to `production/panel/`, package `production/EnvelopeFollower_Panel.zip`, and verify the Gerbers with the `kicad` skill."*

## Step 6.1: Inspect Mechanical Coordinates & Panel Labels

Run `generate_eurorack_panel.py --inspect` against the main PCB:

```bash
python3 .agents/skills/eurorack-panel/scripts/generate_eurorack_panel.py \
    --main-pcb EnvelopeFollower.kicad_pcb \
    --label RV4=OFFSET \
    --label D4=ENV \
    --inspect
```

Observed coordinate alignment between the 8 front-panel THT controls (`RV1`–`RV4`, `J1`–`J3`, `D4`) and the `2 × 4` 3U front panel:

```text
=== Eurorack Panel Mechanical Report for EnvelopeFollower.kicad_pcb ===
Main PCB Outline   : 30.00 x 108.00 mm (X: 0.00..30.00, Y: 0.00..108.00)
Target Front Panel : 6HP x 3U (30.00 x 128.50 mm), Vertical rail overhang = 10.25 mm top/bottom
Panel Origin (0,0) : Global (0.00, -10.25) mm -> (30.00, 118.25) mm

Ref   Value      Label      FP Origin (X, Y)     Bushing Global (X, Y)   Panel-Local (X, Y)   Drill
---------------------------------------------------------------------------------------------------
RV1   A100k      GAIN       (  5.00,  22.50)     (  7.50,  15.00)        (  7.50,  25.25)     7.2 mm
RV2   A50k       ATK        ( 20.00,  22.50)     ( 22.50,  15.00)        ( 22.50,  25.25)     7.2 mm
RV3   A1M        REL        (  5.00,  50.00)     (  7.50,  42.50)        (  7.50,  52.75)     7.2 mm
RV4   B10k       OFFSET     ( 20.00,  50.00)     ( 22.50,  42.50)        ( 22.50,  52.75)     7.2 mm
J1    WQP-PJ398SM IN         (  7.50,  60.52)     (  7.50,  67.00)        (  7.50,  77.25)     6.2 mm
D4    3mm Red LED ENV        ( 21.23,  67.00)     ( 22.50,  67.00)        ( 22.50,  77.25)     3.2 mm
J2    WQP-PJ398SM OUT        (  7.50,  80.32)     (  7.50,  86.80)        (  7.50,  97.05)     6.2 mm
J3    WQP-PJ398SM INV OUT    ( 22.50,  80.32)     ( 22.50,  86.80)        ( 22.50,  97.05)     6.2 mm
```

`generate_eurorack_panel.py` automatically detects each footprint's rotated shaft/bushing `fp_circle` directly from `EnvelopeFollower.kicad_pcb` (`Alps RK09K` pots, `WQP-PJ398SM` jacks, and `LED_D3.0mm`) and keeps both boards in the same global KiCad coordinate space so every hole aligns 1:1.

!!! tip "Deriving Functional Panel Labels from `Silkscreen` & Avoiding the `INV OUT` Input-Box Trap"
    `generate_eurorack_panel.py` handles two subtle label rules cleanly:

    1. **`Silkscreen`-Driven Panel Labels (`derive_panel_label`) & `--label REF=TEXT`**: Because Stage 4/5 footprints store electrical values in `Value` (`A100k`, `A50k`, `A1M`, `B10k`, `3mm Red LED`, `WQP-PJ398SM`) and full assembly labels in `Silkscreen` (`"RV1 GAIN A100k"`, `"RV2 ATK A50k"`, `"RV3 REL A1M"`, `"RV4 OFF B10k"`, `"J1 IN"`, `"D4 LED"`, `"J2 OUT"`, `"J3 INV_OUT"`), `derive_panel_label()` strips the leading `<REF>` token and trailing `<Value>` tokens to isolate `"GAIN"`, `"ATK"`, `"REL"`, `"IN"`, `"OUT"`, and `"INV OUT"`, while `--label RV4=OFFSET --label D4=ENV` expands `"OFF"` to `"OFFSET"` and overrides `"LED"` to `"ENV"`.
    2. **Token-Based Input Callout Box Detection (`INV OUT` vs. `IN`)**: Checking whole tokens (`tokens[0] in ("IN", "INPUT") and "OUT" not in tokens and "OUTPUT" not in tokens`) draws the input callout box strictly around `"IN"` (`J1`) while keeping `"INV OUT"` (`J3`) unboxed.

## Step 6.2: Generate the Panel PCB, Run DRC & Package Gerbers

```bash
python3 .agents/skills/eurorack-panel/scripts/generate_eurorack_panel.py \
    --main-pcb EnvelopeFollower.kicad_pcb \
    --output panel/EnvelopeFollower_Panel.kicad_pcb \
    --title "ENV FOLLOW" \
    --subtitle "6HP ANALOG" \
    --label RV4=OFFSET \
    --label D4=ENV \
    --gerber-dir production/panel \
    --zip production/EnvelopeFollower_Panel.zip \
    --drc
```

Output:

```text
Generated panel/EnvelopeFollower_Panel.kicad_pcb (6HP / 30.0x128.5mm, 8 jack cutouts).
DRC Summary: 0 non-library violations, 0 unconnected items.
Exported Gerbers & Drills to production/panel
Packaged fabrication archive at production/EnvelopeFollower_Panel.zip
```

*(Note: Running raw `kicad-cli pcb drc` directly on embedded `Eurorack_Panel:*` footprints emits 10 expected `lib_footprint_issues` library-mismatch warnings and exits with code `5`; passing `--drc` to `generate_eurorack_panel.py` filters those expected embedded-footprint warnings and enforces `0` copper/silk/clearance/unconnected violations.)*

## Panel Engineering Highlights

- **Doepfer A-100 3U Mounting Slots (`H1`, `H2`)**: Oval `5.5 × 3.2 mm` NPTH slots centered at panel-local `(7.50, 3.00)` and `(7.50, 125.50)` fit both fixed threaded rail strips and sliding M3 nuts.
- **Blemish-Free Front Shielding (`(layers "*.Cu" "B.Mask")`)**: Pot (`7.2 mm`) and jack (`6.2 mm`) holes use plated through-hole pads (`9.6 mm` / `8.6 mm`) connected solidly to the `F.Cu` and `B.Cu` `GND` shield zones. Leaving `F.Mask` tented over the front copper ring yields a clean exterior surface around the M6/M7 nuts, while exposing `B.Mask` on the rear automatically grounds the entire front panel shield to chassis `GND` when the hardware nuts tighten against the back face.
- **Silkscreen Clarity & Input Callout Box**: Clear `F.SilkS` legends label `GAIN`, `ATK`, `REL`, `OFFSET`, boxed `IN`, `ENV`, `OUT`, and `INV OUT`, with `ENV FOLLOW 6HP` and a `5.0 × 5.0 mm` solid white square placed on `B.SilkS` at panel-local `(12.50, 60.50)` to `(17.50, 65.50)` (between `REL`/`OFFSET` and `IN`/`ENV`) that JLCPCB replaces with an order QR code during fabrication.

| 3U Front Panel (`F.Cu` / `F.SilkS`) | 3U Front Panel Rear (`B.Cu` / Grounding Rings) |
| :---: | :---: |
| ![3U Front Panel — Front Face](../images/panel_front.png) | ![3U Front Panel — Rear Grounding Face](../images/panel_back.png) |

## Step 6.3: Verify Panel PCB, Gerbers & 3D Renders with `kicad`

```bash
python3 .agents/skills/kicad/scripts/analyze_pcb.py panel/EnvelopeFollower_Panel.kicad_pcb --full --output /tmp/panel_pcb.json
python3 .agents/skills/kicad/scripts/analyze_gerbers.py production/panel/ --full --output /tmp/panel_gerbers.json

/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb render \
    --side top --width 800 --height 2400 --output /tmp/panel_front.png panel/EnvelopeFollower_Panel.kicad_pcb
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb render \
    --side bottom --width 800 --height 2400 --output /tmp/panel_back.png panel/EnvelopeFollower_Panel.kicad_pcb
```

!!! warning "Catching Obsolete `JLCJLCJLCJLC` Markings via 3D Render Inspection"
    Always inspect `/tmp/panel_back.png` to verify the rear silkscreen carries JLCPCB's modern **`5.0 × 5.0 mm` solid silkscreen square** (`gr_rect` with `(fill yes)` on `B.SilkS`) rather than the legacy `JLCJLCJLCJLC` text string. If an older generator template emitted `JLCJLCJLC`, replace it with:

    > *"Please remove the obsolete `JLCJLCJLC` marking from `panel/EnvelopeFollower_Panel.kicad_pcb`, add a `5 mm × 5 mm` filled square to `B.SilkS` for replacement with the JLCPCB QR code during ordering, and re-export `production/panel/` and `production/EnvelopeFollower_Panel.zip`."*

Verified analyzer results on `panel/EnvelopeFollower_Panel.kicad_pcb` and `production/panel/`:

- **PCB Analyzer (`analyze_pcb.py`)**: `0` errors, `0` warnings (`5` info items), `10` footprints (`8` controls + `2` M3 slots), `2` filled copper zones (`F.Cu`, `B.Cu`), `30.0 × 128.5 mm` outline, `routing_complete: True`.
- **Gerber Analyzer (`analyze_gerbers.py`)**: `0` findings across all severities (`0` errors, `0` warnings, `0` info); `9/9` Gerber layers complete (`B.Cu`, `B.Mask`, `B.Paste`, `B.SilkS`, `Edge.Cuts`, `F.Cu`, `F.Mask`, `F.Paste`, `F.SilkS`, `alignment.aligned: True`); `7` PTH component holes (`3 × 6.2 mm`, `4 × 7.2 mm`) and `3` NPTH mounting/LED holes (`1 × 3.2 mm` LED hole + `2 × 5.5 × 3.2 mm` M3 oval slots), packaged cleanly into `14` files inside `production/EnvelopeFollower_Panel.zip`.
- **3D Renders (`kicad-cli pcb render`)**: Confirms clean front solder mask tenting, boxed `IN` vs. unboxed `INV OUT`, exposed rear `B.Mask` grounding rings, mirrored `ENV FOLLOW 6HP`, and the `5.0 × 5.0 mm` solid QR square on `B.SilkS`.
