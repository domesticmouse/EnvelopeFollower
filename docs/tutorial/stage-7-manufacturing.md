# Stage 7: Exporting for JLCPCB PCBA & Hardware Assembly

## 7.1 Export Main PCB Manufacturing Files

Once you finish routing [`EnvelopeFollower.kicad_pcb`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/EnvelopeFollower.kicad_pcb) in KiCad and pass DRC (`0` violations), export Gerbers, Excellon drills, and the SMD Centroid (`.pos`) file for JLCPCB SMT assembly:

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

# 3. Export SMD placement file (B.Cu only, relative to drill/aux origin)
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb export pos \
    --side back --format csv --units mm --use-drill-file-origin --smd-only --exclude-dnp \
    --output production/main/EnvelopeFollower_cpl.csv EnvelopeFollower.kicad_pcb
```

*(Note: JLCPCB's uploader expects CPL headers named `Designator,Val,Package,Mid X,Mid Y,Rotation,Layer`—rename KiCad's `Ref,Val,Package,PosX,PosY,Rot,Side` header row or export via the KiCad JLCPCB plugin.)*

## 7.2 Ordering on JLCPCB

1. **Main Circuit PCB (`EnvelopeFollower.kicad_pcb`)**:
    - Upload the zipped `production/main/` Gerbers (`1.6 mm` FR4, 2 layers).
    - Enable **PCB Assembly** on **Bottom Side** only (`B.Cu`).
    - Upload [`jlcpcb_bom.csv`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/jlcpcb_bom.csv) and `EnvelopeFollower_cpl.csv`.
    - Always inspect the 3D SMT assembly preview for Pin-1 / cathode orientation on `U1`, `U2` (`TL074HIDR`), `D1`–`D3` (`1N4148W`), `D4`–`D5` (`B5819W`), and polarized electrolytics `C3`–`C4`.
2. **Front Panel PCB ([`production/EnvelopeFollower_Panel.zip`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/production/EnvelopeFollower_Panel.zip))**:
    - Upload `production/EnvelopeFollower_Panel.zip` (`1.6 mm` FR4, **Black** solder mask with **White** silkscreen, **Specify a location** for the order QR code over the `5 × 5 mm` white square on `B.SilkS`, which JLCPCB replaces with a QR code during ordering). No assembly needed.

## 7.3 Stress-Free Mechanical Assembly

When your PCBs arrive and you hand-solder the 9 `Manual THT` parts (`J_PWR` on the rear, plus `RV_GAIN`, `RV_ATK`, `RV_REL`, `RV_OFFSET`, `J_IN`, `J_OUT`, `J_INV_OUT`, and `LED1` on the front):

1. Solder `J_PWR` on `B.Cu` first (confirming Pin 1/Pin 2 (`-12V`) is at the bottom, aligned with the `-12V RED` silkscreen label).
2. Insert all four pots, three jacks, and the 3mm LED **unsoldered** into `F.Cu` of the main PCB.
3. Place the 3U front panel over the shafts and bushings, tighten the M6/M7 panel nuts finger-tight, and position `LED1` flush inside its `3.2 mm` bezel hole.
4. **Only after the front panel aligns everything mechanically**, solder all pot lugs, jack pins, and LED leads on `B.Cu`. This guarantees zero mechanical stress on solder joints and perfectly centered front-panel controls.
