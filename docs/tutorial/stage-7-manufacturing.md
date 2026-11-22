# Stage 7: Gerbers, Ordering Checklists, Interactive BOM & Renders

Passing DRC and liking your 3D renders is not the finish line — manufacturing failures most often happen between "DRC passes" and "boxes arrive on the bench." A missing paste check, an unrouted NPTH slot, a rotated diode in the CPL preview, an unwashed high-impedance flux residue around the slew capacitor, or a forgotten pair of oversized knobs colliding on a `15.50 mm` pot spacing can turn a clean layout into a rework weekend. In Stage 7 — captured across traces [`10-a47d447e` (`prompts/10-a47d447e-please-create-markdown-checklists-main-board-order.md`)](https://github.com/domesticmouse/EnvelopeFollower/blob/main/prompts/10-a47d447e-please-create-markdown-checklists-main-board-order.md), [`12-0e25fc0a` (`prompts/12-0e25fc0a-please-update-readme-md.md`)](https://github.com/domesticmouse/EnvelopeFollower/blob/main/prompts/12-0e25fc0a-please-update-readme-md.md), [`14-f42ac6f5` (`prompts/14-f42ac6f5-i-m-attempting-to-create-a-bom.md`)](https://github.com/domesticmouse/EnvelopeFollower/blob/main/prompts/14-f42ac6f5-i-m-attempting-to-create-a-bom.md), and [`16-cd7d0409` (`prompts/16-cd7d0409-i-d-like-to-design-a-front.md`)](https://github.com/domesticmouse/EnvelopeFollower/blob/main/prompts/16-cd7d0409-i-d-like-to-design-a-front.md) — you generate upload-ready fabrication archives for both boards, build PCB-verified ordering/assembly/bring-up checklists, produce a THT-only interactive assembly map, and automate reproducible documentation renders.

```mermaid
flowchart LR
    PCB["Verified Main PCB<br/>+ Mated Panel PCB"] --> S71["7.1 manufacturing/ Exports<br/>Dual Gerbers, Routed Slots & CPL"]
    S71 --> S72["7.2 PCB-Verified checklists/<br/>01, 01b, 02, 03, 04, 05"]
    S72 --> S73["7.3 THT-Only bom/ibom.html<br/>14 Rows / 18 Hand-Soldered Parts"]
    S73 --> S74["7.4 README Sync & Renders<br/>sips + kicad-cli + Pillow Crop"]
```

---

## Step 7.1: Dual-Board `manufacturing/` Exports & Gerber/CPL Verification

Your finished module ships as **two separate JLCPCB items inside one shared cart**: a **2-layer FR-4 main board with Bottom-Side Economic PCBA** (`envelope_follower.kicad_pcb`, `30.0 × 108.0 mm`) and a **2-layer FR-4 bare front panel** (`envelope_follower_panel.kicad_pcb`, `30.0 × 128.5 mm`, Matte Black + ENIG). Generating both fabrication sets deterministically inside [`manufacturing/`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/main/manufacturing) prevents stale archives from accumulating ([Trace 16](https://github.com/domesticmouse/EnvelopeFollower/blob/main/prompts/16-cd7d0409-i-d-like-to-design-a-front.md)):

| Artifact Path | Contents | Purpose at Fabrication |
| :--- | :--- | :--- |
| `manufacturing/gerbers/` & `envelope_follower_gerbers.zip` | `F.Cu`, `B.Cu`, `F.Paste`, `B.Paste`, `F.SilkS`, `B.SilkS`, `F.Mask`, `B.Mask`, `Edge.Cuts`, separated `PTH`/`NPTH` Excellon + GerberX2 drill map | Main board PCB + bottom-side SMT stencil |
| `manufacturing/jlcpcb_cpl.csv` | `50` translated SMD rows (`Designator,Mid X,Mid Y,Layer,Rotation`, every row `Layer = B`) | JLCPCB Pick-and-Place alignment |
| `manufacturing/panel_gerbers/` & `envelope_follower_panel_gerbers.zip` | `F.Cu`, `B.Cu`, `F.SilkS`, `B.SilkS`, `F.Mask`, `B.Mask`, `Edge.Cuts`, separated `PTH`/`NPTH` Excellon with **routed oval slots** `H1`/`H2` | Bare Matte Black + ENIG 6 HP panel |

### Exporting Gerbers, Routed Excellon Slots & Translated CPL

After re-running clean DRC checks on both boards (`0` errors on main PCB; `0` non-library violations on panel PCB after filtering the `13` expected `lib_footprint_issues` warnings), export both fabrication packages with identical origin conventions (`--use-drill-file-origin` + `--drill-origin plot`):

```bash
# 1. Main board Gerbers & separated Excellon drills
mkdir -p manufacturing/gerbers
kicad-cli pcb export gerbers --output manufacturing/gerbers/ \
  --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --use-drill-file-origin --check-zones \
  envelope_follower.kicad_pcb
kicad-cli pcb export drill --output manufacturing/gerbers/ \
  --format excellon --drill-origin plot --excellon-units mm \
  --excellon-separate-th --excellon-oval-format route \
  --generate-map --map-format gerberx2 \
  envelope_follower.kicad_pcb
(cd manufacturing/gerbers && zip -r ../envelope_follower_gerbers.zip .)

# 2. Back-side SMD CPL translated & parity-filtered against jlcpcb_bom.csv (50/50)
kicad-cli pcb export pos --format csv --units mm --side back --smd-only --exclude-dnp \
  --use-drill-file-origin --output /tmp/raw_cpl.csv envelope_follower.kicad_pcb
.venv/bin/python .agents/skills/bom/scripts/translate_bom_pnp.py pnp \
  /tmp/raw_cpl.csv -o manufacturing/jlcpcb_cpl.csv \
  --units mm --bom jlcpcb_bom.csv

# 3. Front panel Gerbers & routed M3 oval slots (no paste layers needed on bare panel)
mkdir -p manufacturing/panel_gerbers
kicad-cli pcb export gerbers --output manufacturing/panel_gerbers/ \
  --layers F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --use-drill-file-origin --check-zones \
  envelope_follower_panel.kicad_pcb
kicad-cli pcb export drill --output manufacturing/panel_gerbers/ \
  --format excellon --drill-origin plot --excellon-units mm \
  --excellon-separate-th --excellon-oval-format route \
  --generate-map --map-format gerberx2 \
  envelope_follower_panel.kicad_pcb
(cd manufacturing/panel_gerbers && zip -r ../envelope_follower_panel_gerbers.zip .)
```

Notice two critical KiCad 10 CLI flags here:

- **`--excellon-oval-format route` + `--excellon-separate-th`:** Exports the front panel's top and bottom M3 mounting slots (`H1`, `H2`, `5.50 × 3.20 mm`) as routed `G00 ... M15 / G01 ... M16` slot toolpaths inside `envelope_follower_panel-NPTH.drl` alongside the `3.20 mm` `LED1` NPTH bore, cleanly separated from `envelope_follower_panel-PTH.drl` (`10` grounded control cutouts).
- **`translate_bom_pnp.py pnp --bom jlcpcb_bom.csv`:** Rewrites KiCad's `Pos` columns into JLCPCB's exact `Designator,Mid X,Mid Y,Layer,Rotation` format while asserting `rows_out: 50`, `bom_designators: 50`, `filtered_orphans: 0`, and `set(Layer) == {"B"}`.

### Running `analyze_gerbers.py` & Understanding `B.Paste` Heuristic Parity

Verify both output directories with `.agents/skills/kicad/scripts/analyze_gerbers.py`:

```bash
.venv/bin/python .agents/skills/kicad/scripts/analyze_gerbers.py manufacturing/gerbers/ --full --output /tmp/main_gerbers.json
.venv/bin/python .agents/skills/kicad/scripts/analyze_gerbers.py manufacturing/panel_gerbers/ --full --output /tmp/panel_gerbers.json
```

When auditing `manufacturing/gerbers/`, automated Gerber analyzers sometimes emit a paste-coverage warning (`~37%` of all `B.Cu` features) if they compare total `B.Paste` flashes against *every* copper feature on `B.Cu` (including through-hole component pads and `133` vias). Do not blindly dismiss or blindly panic over that number — verify **SMD pad-to-paste parity** directly: across all `50` SMD parts (`34× 2-pad passives/diodes` + `1× 3-pad SOT-23` + `2× 14-pad SOIC-14` + ... wait: count exact SMD pads: `47× 2-pin = 94` + `1× 3-pin D3 = 3` + `2× 14-pin U1/U2 = 28` = **`125` total SMD pads**), `B.Paste` contains **`125 / 125`** exact stencil flashes while `F.Paste` contains `0`.

!!! warning "Upload `jlcpcb_bom.csv` — NEVER `envelope_follower_bom.xml`"
    Always upload [`jlcpcb_bom.csv`](stage-4-skidl.md#step-43-anatomy-of-envelope_followerpy-multi-layer-netlist-verification) (`17` rows, `50` SMDs, `` `$9` `` total Extended feeder fees) paired with `manufacturing/jlcpcb_cpl.csv` and `manufacturing/envelope_follower_gerbers.zip`. `envelope_follower_bom.xml` is the master `80`-part KiCad/SKiDL database containing `18` Tayda/panel THT components and `12` DNP Keystone test points (`TP1`–`TP12`); uploading it forces expensive manual-soldering surcharges or bogus missing-part flags.

---

## Step 7.2: PCB-Verified Manufacturing & Bring-Up Checklists (`checklists/`)

Rather than trusting hand-written checklists typed from memory, generate all seven operational documents under [`checklists/`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/tree/main/checklists) directly against `envelope_follower.kicad_pcb`, `envelope_follower_panel.kicad_pcb`, and `jlcpcb_bom.csv`, and enforce completeness with a short KiCad Python assertion checking:

- `50 / 50` SMD RefDes, values, LCSC SKUs, and both `board=(X, Y)` and back-flipped `back=(30.0 - X, Y)` coordinates match `.kicad_pcb` (`0` mismatches).
- `18 / 18` populated THT designators (`C1`, `C2`, `C7`, `C11`–`C13`, `RV1`–`RV4`, `SW1`–`SW2`, `LED1`, `J1`–`J4`, `J_PWR`) appear explicitly in both the Tayda BOM (`03`) and hand-assembly (`04`) checklists.
- `12 / 12` Keystone test points (`TP1`–`TP12`) and their exact silkscreen names (`GND`, `+12V`, `-12V`, `PRE`, `RECT`, `ENV`, `INV`, `OUT`, `HWR`, `DRV`, `OFF`, `GND2`) appear in the bring-up guide (`05`).

### What Each Checklist Verifies

1. **[`01-main-board-ordering.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/01-main-board-ordering.md) — Main PCB & Economic Bottom-Side PCBA:**
   - Fabrication settings: `FR-4`, `2` layers, `30.0 × 108.0 mm`, `1.6 mm`, `Black` soldermask (note: Matte Black can force Standard PCBA pricing — keep standard Black on the hidden main board to preserve Economic PCBA), `White` silkscreen, **`LeadFree HASL (RoHS)`** or **`ENIG-RoHS`**, and **`Tented`** vias.
   - PCBA settings: **Bottom Side** only, **`SAC305` lead-free** solder, **Specify a location** for QR placement (`JLCJLCJLCJLC`) on the solid `5.0 × 5.0 mm` **`F.SilkS`** box at top-right (`X = 23.8–28.8 mm, Y = 1.0–6.0 mm`), and strictly **`3` Extended SKUs** (`` `$3` ``/SKU = `` `$9` `` feeder fees total): **`C2878713`** (`TL074HIDR` `×2`), **`C83935`** (`BAT54S` `×1`), and **`C95204`** (`10k 0.1%` `RT0603BRD0710KL` `×14`). Pre-order CLI steps stay marked `[x]`; interactive web/cart checks remain `[ ]`.
2. **[`01b-front-panel-ordering.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/01b-front-panel-ordering.md) — Mated 6 HP Front Panel (Same JLCPCB Cart):**
   - Fabrication settings: `FR-4`, `2` layers, `30.0 × 128.5 mm`, `1.6 mm` (or `2.0 mm`), **`Matte Black`** soldermask, **`White`** silkscreen, **`ENIG-RoHS`** surface finish (required so all `33` `F.Mask` openings gleam over `F.Cu`), `PCB Assembly = OFF`, and QR/order number placed exclusively on **`B.SilkS`** (`(22.50, 121.00)`) with a PCB remark forbidding any stamp on `F.SilkS`.
   - Combine in the same JLCPCB checkout cart as `envelope_follower_gerbers.zip` to share international shipping.
3. **[`02-pcba-part-alignment.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/02-pcba-part-alignment.md) — JLCPCB 2D/3D Viewer Sign-Off (Dual Coordinates):**
   - When staring straight at JLCPCB's **Bottom Side** viewer with top (`Y = 0`) up, horizontal coordinates mirror left-to-right (`back_X = 30.0 - board_X`). Printing **both** `back=(X, Y)` and `board=(X, Y)` on every one of the `50` items lets you inspect directly without mental mirroring.
   - Highlights the **"WATCH FOR JLCPCB ROTATION OFFSET"** table for all `7` polarized / multi-pin SMDs — expect to inspect (and rotate in JLCPCB's viewer if shifted by `90°`/`180°`):

   | Ref | Part / Package | LCSC | `jlcpcb_cpl.csv` Rot | Expected Visual Alignment in JLCPCB Bottom Viewer (`Y=0` Up) |
   | :--- | :--- | :---: | :---: | :--- |
   | **`U1`** | `TL074HIDR` (`SOIC-14`) | `C2878713` | `0.0°` | **Pin 1 bevel/dot at bottom-right** (`+12V` pin `4` upper side, `-12V` pin `11` lower side) |
   | **`U2`** | `TL074HIDR` (`SOIC-14`) | `C2878713` | `180.0°` | **Pin 1 bevel/dot at top-left** (`U2C`/`U2D` pins face output jacks & LED) |
   | **`D3`** | `BAT54S` (`SOT-23`) | `C83935` | `0.0°` | **2 pins on right (`D3.1` top-right, `D3.2` bottom-right), 1 common pin on left (`D3.3`)** |
   | **`D1`**, **`D2`** | `B5819W` (`SOD-123`) | `C8598` | `180.0°` | **Cathode band facing left** (vertical rail protection polarity) |
   | **`D4`** | `1N4148W` (`SOD-123`) | `C81598` | `0.0°` | **Cathode band facing right** (charges `NET_ATK_DIODE` toward `RV2`) |
   | **`D5`** | `1N4148W` (`SOD-123`) | `C81598` | `180.0°` | **Cathode band facing left** (discharges `NET_REL_DIODE` toward `RV3`) |

4. **[`03-tayda-ordering.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/03-tayda-ordering.md) — Explicit `18`-Part THT Shopping List & Knob Constraint:**
   - Lists explicit RefDes alongside verified Tayda SKUs (`A-1855` `A100K` `RV1`, `A-1672` `2× A1M` `RV2`/`RV3`, `A-8401` `B10K` center-detent `RV4`, `A-6087` `2× Dailywell 2MS1` `SW1`/`SW2`, `A-1076` `3 mm` anti-parallel Red/Green `LED1`, `A-7257` `2× 47 µF / 35 V` `C1`/`C2`, `4× WIMA MKS2` `5.0 mm` box film caps [`2× 470 nF` `C7`/`C11`, `2× 2.2 µF` `C12`/`C13`], `4× WQP-PJ398SM` jacks `J1`–`J4`, and `1× 2×5` shrouded `2.54 mm` Eurorack power header `J_PWR`).
   - Enforces the **`15.50 mm` pot pitch geometry guard**: because `RV1`–`RV4` shafts sit `15.50 mm` apart vertically (`Y = 11.0, 26.5, 42.0, 57.5 mm` on PCB), select knobs with outer skirt diameter **`<= 14.0 mm`** and verify shaft style against Tayda (`T18` splined vs round/D) before checkout.
5. **[`04-hand-assembly.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/04-hand-assembly.md) — THT Build Sequence (`ibom.html` + Matte Black Panel Hygiene):**
   - Links directly to `../bom/ibom.html` for visual click-to-highlight placement.
   - **Solder `B.Cu` parts first** (`J_PWR` notch toward right board edge / `-12V` white bar on `B.SilkS`, **`C1`/`C2` opposite polarities** — `C1` `+` -> `+12V`, `C2` `+` -> `GND`, then `C7`, `C11`–`C13`) and trim leads flush on `F.Cu` so nothing shorts against the metal panel shells or PCB standoffs.
   - **Test `LED1` (`A-1076`) before soldering:** Connect `5 V + 1 kΩ` across its two pins to identify which lead lights Green vs Red so positive envelope (`+OUT`) glows Green and negative offset/inverted swing glows Red consistently with `+ / -` panel marks.
   - **Dry-fit panel hardware cleanly:** Snap off Alpha potentiometer anti-rotation tabs (`envelope_follower_panel.kicad_pcb` intentionally omits tab holes to keep the matte black face unblemished), seat `RV1`–`RV4`, `SW1`–`SW2`, `J1`–`J4`, and `LED1` hand-tight into the panel using **nylon M3 mounting washers** on the front screw slots `H1`/`H2`, verify square alignment, then solder all `11` panel controls.
   - **Clean high-impedance nodes with IPA:** Thoroughly flush flux around `U2A.3`, `C11`, `C12`, `C13`, and `SW2` using isopropyl alcohol so surface leakage cannot skew slow `3.0 s` release times (`RV2`/`RV3` up to `1 MΩ`). Confirm toggle states: `SW1` UP = `SMOOTH` / DOWN = `RAW`, `SW2` UP = `SLOW` / DOWN = `FAST`.
6. **[`05-board-bringup.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/05-board-bringup.md) — Bench Bring-Up, `12`-TP Map & Musical Testing:**
   - Perform cold ohmmeter rail-to-rail and rail-to-GND checks before applying power, set bench supplies to `±12.0 V` current-limited at **`40–50 mA`**, and initialize **`SW1` DOWN (`RAW/OFF`)**, **`SW2` DOWN (`FAST`)**, and `RV4` at center detent.
   - Verify every DC and AC signal stage across all `12` test points (`TP1` `GND`, `TP2` `+12V` `~+11.5–11.8 V`, `TP3` `-12V` `~-11.5–11.8 V`, `TP4` `PRE` `×2` preamp, `TP9` `HWR`, `TP5` `RECT` `|preamp|`, `TP10` `DRV`, `TP6` `ENV`, `TP11` `OFF` `±4.98 V`, `TP7` `INV`, `TP8` `OUT`, `TP12` `GND2`), test normalled breakout behavior on `J2` (`SLEW IN` breaks normalization from internal FWR), run kick-ducking patches on `J4` (`INV OUT`), and follow decision-tree troubleshooting steps if any rail or stage deviates.

---

## Step 7.3: Generating the THT-Only Interactive HTML BOM (`bom/ibom.html`)

JLCPCB handles all `50` rear SMDs automatically, so using an unfiltered KiCad interactive BOM during hand assembly clutters the table with resistors and `0603` capacitors you will never touch with an iron. Using **`InteractiveHtmlBom` (`v2.11.1+`)** inside KiCad PCB Editor ([Trace 14](https://github.com/domesticmouse/EnvelopeFollower/blob/main/prompts/14-f42ac6f5-i-m-attempting-to-create-a-bom.md)), filter the HTML output strictly to the `18` manually soldered parts by reading the `JLCPCB_Class` footprint field embedded by `generate_kicad_pcb.py`:

- Open `envelope_follower.kicad_pcb` in KiCad PCB Editor -> launch **Generate Interactive HTML BOM**.
- **General / Html** tabs: output to `bom/ibom.html`, default to **F** (or Front & Back) view showing silkscreen, fabrication, and pads.
- **Fields** tab:
  - Set **Board variant field** = `JLCPCB_Class`.
  - Set **Variants whitelist** = `Manual THT`.
  - Include extra columns: **`Value`**, **`Footprint`**, **`MPN`**, and **`Manufacturer`**.
- **Output scope check:** Inspect the generated `bom/ibom.html` header/BOM table and confirm **`14` grouped rows covering `18` THT components** (`11` `F.Cu` panel controls + `7` `B.Cu` components), with `0` SMDs, `0` DNP `TP1`–`TP12`, and `0` `FID1`–`FID3`. Link `../bom/ibom.html` inside [`checklists/04-hand-assembly.md`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/checklists/04-hand-assembly.md) so builders click straight from checkboxes to interactive pad highlighting.

---

## Step 7.4: Living `README.md` Sync & Reproducible `images/` Render Pipeline

Finally ([Trace 12](https://github.com/domesticmouse/EnvelopeFollower/blob/main/prompts/12-0e25fc0a-please-update-readme-md.md) & [Trace 16](https://github.com/domesticmouse/EnvelopeFollower/blob/main/prompts/16-cd7d0409-i-d-like-to-design-a-front.md)), synchronize your repository's root `README.md` so its quick-start CLI flags (`--silk-only`, `--sync-silk`, `--check-silk`, `--show-silk`, `--auto-silk`), `/edit-silkscreen` skill workflow, `panel_art/`, `manufacturing/`, `bom/ibom.html`, `checklists/`, and rendered screenshots reflect what is actually on disk.

### Reproducible `images/` Export, Cropping & Link Audit

Generate uniform, tight-cropped renders for both the main PCB and mated Matte Black + ENIG panel directly from the command line:

```bash
mkdir -p images
# 1. Schematic preview (rasterize KiCad PDF at max edge 2400 px on macOS)
sips -s format png -Z 2400 envelope_follower.pdf --out images/schematic.png

# 2. High-quality raytraced 3D renders with transparent backgrounds
kicad-cli pcb render --side top --width 900 --height 2400 --background transparent --quality high \
  --output images/pcb_front.png envelope_follower.kicad_pcb
kicad-cli pcb render --side bottom --width 900 --height 2400 --background transparent --quality high \
  --output images/pcb_back.png envelope_follower.kicad_pcb
kicad-cli pcb render --side top --width 900 --height 2400 --background transparent --quality high \
  --output images/panel_front.png envelope_follower_panel.kicad_pcb
kicad-cli pcb render --side bottom --width 900 --height 2400 --background transparent --quality high \
  --output images/panel_back.png envelope_follower_panel.kicad_pcb
```

!!! note "Headless `kicad-cli pcb render` displays bare boards unless 3D models resolve"
    If 3D STEP/WRL libraries are not installed or mapped under `KICAD10_3DMODEL_DIR`, headless `kicad-cli pcb render` renders the bare copper, soldermask, silkscreen, and plated pads cleanly without throwing errors — which is ideal for inspecting silkscreen readability, ENIG finish color, and pad geometry.

Normalize pairs (`pcb_front.png`/`pcb_back.png` and `panel_front.png`/`panel_back.png`) onto matching canvases using Pillow `getbbox()` with `16 px` padding and `optimize=True` so side-by-side comparison tables align edge-for-edge, and always run a quick Python check verifying zero dead relative Markdown links or `<img src>` attributes before pushing:

```python
import pathlib, re

text = pathlib.Path("README.md").read_text(encoding="utf-8")
targets = [m.group(1) for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text)]
targets += [m.group(1) for m in re.finditer(r'(?:src|href)="([^"]+)"', text)]
missing = [
    t for t in targets
    if not t.startswith(("http://", "https://", "#"))
    and not pathlib.Path(t.split("#", 1)[0]).exists()
]
assert not missing, f"Broken local links in README.md: {missing}"
```

---

## Pitfalls Caught in Stage 7

| Pitfall Discovered | Symptom | Fix Applied |
| :--- | :--- | :--- |
| **Default Excellon ovals without `route`** | JLCPCB flags `H1`/`H2` M3 oval NPTH slots or converts them to round drills | Pass `--drill-origin plot --excellon-separate-th --excellon-oval-format route` on both boards |
| **Raw `B.Paste` coverage heuristic (`~37%`)** | Static Gerber analyzer warns on paste-to-copper ratio when comparing paste against `133` vias + THT pads | Verify exact **`125 / 125`** paste-flash parity against the `50` SMD footprints (`0` on `F.Paste`) |
| **Uploading `envelope_follower_bom.xml`** | JLCPCB tries to source THT jacks/pots/film caps and DNP Keystone test points (`TP1`–`TP12`) | Upload `jlcpcb_bom.csv` (`17` rows, `50` SMDs, `3` Extended SKUs) paired with `manufacturing/jlcpcb_cpl.csv` |
| **Mentally flipping `B.Cu` viewer coordinates** | Misreading left/right cathode bands (`D1`–`D5`) or Pin 1 (`U1`/`U2`) in JLCPCB's bottom viewer | Print both `board=(X, Y)` and mirrored `back=(30.0 - X, Y)` coordinates in `02-pcba-part-alignment.md` |
| **Oversized knobs on `15.50 mm` pot spacing** | Skirted knobs wider than `14.0 mm` rub against neighbors on `RV1`–`RV4` | Cap knob outer skirt at `<= 14.0 mm` in `03-tayda-ordering.md` and snap off Alpha pot anti-rotation tabs |
| **Unwashed flux around slow-mode nodes** | `SLOW` `3.0 s` release sags prematurely when flux leakage shunts `1 MΩ` (`RV2`/`RV3`) | Scrub `U2A.3`, `C11`–`C13`, and `SW2` thoroughly with IPA during hand assembly |

---

## Next Reference Pages

You now have the complete interactive end-to-end hardware engineering workflow from initial sketch critique to factory-ready Gerbers and bench bring-up:

- **[Netlist, BOM & Silkscreen Schedule](../reference/netlist-and-bom.md)** — Complete `80`-component (`+ 3` fiducials) BOM, verbatim `17`-row `jlcpcb_bom.csv`, all `48` active nets, `9`-section schematic capture checklist, and full `silk_layout.json` schedule.
- **[Complete Build Checklist](../reference/build-checklist.md)** — Printable end-to-end summary tying Phases 1–4 directly to the `EnvelopeFollowerWithSkewLimiter` repository deliverables.
