# Stage 5: 6 HP Main PCB, `silk_layout.json` & `/edit-silkscreen`

Because `envelope_follower.net` and `envelope_follower.kicad_sch` ([Stage 4](stage-4-skidl.md)) already capture every net, custom field, `DNP` test point, and unit-1 symbol UUID, `generate_kicad_pcb.py` automates the full `30.00 × 108.00 mm` 2-layer PCB—and then pairs with a declarative **`silk_layout.json`** sidecar and a repo-local **`/edit-silkscreen`** skill for fast, iterative human + AI silkscreen polishing.

---

## Step 5.1: Automated 6 HP Main PCB Generation & Layout Debugging

### AI Agent Prompt ([Trace 07 Turn 1](https://github.com/domesticmouse/EnvelopeFollower/blob/main/prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md))

> *"`/kicad-pcbnew-layout` `/kicad-silkscreen-markup` `/eurorack-panel` `/kicad` Please create and run `generate_kicad_pcb.py` to generate a 6 HP main PCB (`envelope_follower.kicad_pcb`) from `@[envelope_follower.net]`, following `@[DesignSpec.md]`."*

### Board Partitioning & 6 HP Mechanical Grid (`83` PCB Footprints, `48` Nets)

| Side | Count | Components | Layout Role |
| :--- | :---: | :--- | :--- |
| **`F.Cu`** | `11` | `RV1`–`RV4` (`X = 15.00 mm`, `15.50 mm` pitch), `SW1`/`LED1`/`SW2` (`Y = 72.00 mm`), `J1`–`J4` (`2 × 2` grid) | Front-panel THT controls aligned to the 3U faceplate |
| **`B.Cu`** | `50` | `U1`–`U2` (`TL074HIDR`), `D1`–`D5`, `C3`–`C6`, `C8`–`C10`, `C14`–`C16`, `R1`–`R33` | Single-sided SMD PCBA (`0°`/`180°` horizontal passives) |
| **`B.Cu`** | `7` | `J_PWR` (`2×5` IDC), `C1`–`C2` (`47 µF` radial), `C7`, `C11`–`C13` (`5 mm` box film) | Tall non-panel THT components clear of the panel standoff |
| **`B.Cu`** | `12` | `TP1`–`TP12` (`Ronghe RH-5001`, `1.0 mm` drill, `DNP` + `exclude_from_bom` + `exclude_from_pos_files`) | Rear bring-up test points (`TP1` bottom `GND`, `TP12` top `GND2`) |
| **`B.Cu`** | `3` | `FID1`–`FID3` (`Fiducial:Fiducial_1mm_Mask2mm`, `DNP` + `exclude_from_bom` + `exclude_from_pos_files`) | Asymmetric pick-and-place optical alignment fiducials |

Exact front-panel control coordinates (`BOARD_X0 = 100.00`, `BOARD_Y0 = 40.00`, `BOARD_W = 30.00`, `BOARD_H = 108.00 mm`):

| Ref | Panel Function | Footprint (`rot = 0°`) | Local Origin `(X, Y)` | Panel Shaft / Bushing `(X, Y)` on PCB |
| :--- | :--- | :--- | :---: | :---: |
| `RV1`–`RV4` | `GAIN`, `ATK`, `REL`, `OFFSET` | `Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | `(7.50, 8.50 / 24.00 / 39.50 / 55.00)` | `(15.00, 11.00 / 26.50 / 42.00 / 57.50)` |
| `SW1`, `SW2` | `SMOOTH`, `FAST/SLOW` | `Eurorack_Custom:SW_Toggle_SPDT_Dailywell_2MS1` | `(7.00, 72.00)`, `(23.00, 72.00)` | `(7.00, 72.00)`, `(23.00, 72.00)` |
| `LED1` | `OUT` (`2-Pin R/G A-1076`) | `LED_THT:LED_D3.0mm` | `(13.73, 72.00)` | `(15.00, 72.00)` |
| `J1`–`J4` | `IN`, `SLEW IN`, `OUT`, `INV_OUT` | `Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | `(8.00 / 22.00, 79.02 / 94.02)` | `(8.00 / 22.00, 85.50 / 100.50)` |

### Six Practical KiCad 10 PCB Layout Techniques (From Trace 07)

1. **Preserve Schematic UUID Parity (`fp.SetPath`)**: Extract unit-1 symbol UUIDs from `envelope_follower.kicad_sch` (`parse_schematic_unit1_uuids()`) and set `fp.SetPath(pcbnew.KIID_PATH(f"/{inst_uuid}"))` on every PCB footprint so `cross_analysis.py` reports `100%` schematic-to-PCB pairing (`0` parity issues).
2. **Match KiCad GUI Coordinates 1:1 to Board-Local Millimeters**: Set `GridOrigin` and `AuxOrigin` to `(BOARD_X0, BOARD_Y0)` (`100.0, 40.0 mm`) inside `DesignSettings` so KiCad's GUI rulers and `(0..30, 0..108) mm` script coordinates match 1:1.
3. **Probe KiCad `pcbnew` Footprint Geometry Empirically**: Before placing parts, inspect loaded pads and `.CrtYd`/`.Fab` bounds in `pcbnew`:
   - Always call `board.Add(fp)` **before** `fp.Flip(fp.GetPosition(), False)` (flipping before adding segfaults in KiCad 10 C++).
   - `fp.Flip()` mirrors across the **X axis (`Y → -Y`)**, not the Y axis.
   - `PCB_SHAPE.IsFilled()` does not exist in KiCad 10—use `IsSolidFill()` or `GetFillMode() == pcbnew.FILL_T_FILLED_SHAPE`, and delete items with `board.Delete()` / `fp.Delete()` instead of `board.Remove()` to avoid SWIG memory-leak warnings.
   - Normalize layer-name checks against canonical KiCad 10 strings (`GetLayerName()` returns `"F.Silkscreen"` / `"B.Silkscreen"`, not `"F.SilkS"` / `"B.SilkS"`).
4. **Enforce a Pre-Routing Cross-Layer Collision Gate (`verify_placements()`)**: KiCad's built-in `courtyards_overlap` DRC only checks `F.CrtYd ↔ F.CrtYd` and `B.CrtYd ↔ B.CrtYd`—it ignores a tall `B.Cu` THT housing or SMD pad colliding with an opposite-side `F.Cu` pot lug or jack body! Run `verify_placements()` *before* routing to catch cross-layer physical collisions early.
5. **Deterministic Routing & Clean Pours**:
   - Run a fast 1-second BFS reachability probe + ASCII grid dump when an `0603` cascade tangles (`180°` passive rotation uncrosses tracks cleanly).
   - Share `GND` vias inside `SOIC-14` bellies, register exact rectangular blockers for unconnected pads (`mark_via_block` / `StrictGridRouter`), sort `set` iterations deterministically, and prune isolated stitching vias via `zone.HitTestFilledArea()` after `pour_gnd_zones()`.
6. **Treat 3D Render Visual Inspection as a Pass/Fail Gate**: Even with `0` DRC violations and passing `silk_annotator --inspect`, visually inspect front and back `kicad-cli pcb render` PNGs—visual inspection caught real label collisions and silent `try_silk_text()` drops that metrics alone missed.

| Main PCB Front (`F.Cu` — Panel Controls) | Main PCB Rear (`B.Cu` — 50 SMD PCBA & Power) |
| :---: | :---: |
| ![Main PCB Front Controls F.Cu](../images/pcb_front.png){ width="240" } | ![Main PCB Rear 50 SMD PCBA B.Cu](../images/pcb_back.png){ width="240" } |

---

## Step 5.2: Declarative Silkscreen Sidecar (`silk_layout.json`) & Bidirectional CLI

### Motivating Prompts ([Trace 07 Turns 2–3](https://github.com/domesticmouse/EnvelopeFollower/blob/main/prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md))

> *"How should I move silkscreen entries such that they can be updated in the generate script?"*
>
> *"Git commit the current state. Then update the script so that I can work with it to move things around in a new chat. Assume I am going to want to move most silkscreen entries, one by one."*

Editing coordinates buried inside a 2,000-line Python script makes one-by-one label tweaks brittle and risks unintended copper diffs. Extracting all board silkscreen positions into **`silk_layout.json`** solves both problems:

- **Board-local mm coordinates & 1-line-per-passive formatting** keep `git diff` clean and readable.
- Pins `qr_rects`, `dots` (external `U1`/`U2` Pin-1 dots), `segments` (`-12V` white bar), `board_texts`, and `footprints` (supporting `"auto"` fallback on any entry to re-run `SilkGrid` around all pinned neighbors).

```json
{
  "version": 1,
  "coordinate_system": "board-local mm relative to (BOARD_X0=100.0, BOARD_Y0=40.0); matches KiCad Grid/Aux origin",
  "qr_rects": [
    {"layer": "F.SilkS", "x0": 23.8, "y0": 1.0, "x1": 28.8, "y1": 6.0, "filled": true, "width": 0.15}
  ],
  "segments": [
    {"layer": "F.SilkS", "x0": 22.5, "y0": 19.95, "x1": 26.54, "y1": 19.95, "width": 0.8}
  ],
  "footprints": {
    "R1": {"ref": null, "texts": [{"layer": "B.SilkS", "text": "10R", "x": 13.0, "y": 18.75, "deg": 0.0, "height": 0.8, "thickness": 0.15}]},
    "RV1": {
      "ref": {"layer": "F.SilkS", "x": 5.4, "y": 14.888, "deg": 90.0, "height": 0.8, "thickness": 0.15},
      "texts": [{"layer": "F.SilkS", "text": "GAIN A100K", "x": 5.4, "y": 9.531, "deg": 90.0, "height": 0.8, "thickness": 0.15}]
    }
  }
}
```

### Six CLI Modes on `generate_kicad_pcb.py`

| Command | Speed / Scope | When to Use |
| :--- | :--- | :--- |
| `python3 generate_kicad_pcb.py` | Full rebuild (~5–10 s) | After netlist, placement (`TP2`/`TP3` swap), or routing edits—rebuilds board from scratch using `silk_layout.json`. |
| `python3 generate_kicad_pcb.py --silk-only` | **~1 s** in-place restamp | Preserves all copper tracks, vias, zones, and UUIDs while restamping `silk_layout.json` and refreshing off-board `B.Fab` notes. |
| `python3 generate_kicad_pcb.py --sync-silk` | Instant JSON sync | Captures manual KiCad GUI label drags back into `silk_layout.json` via `item.GetBoundingBox().GetCenter()` (so non-centered GUI anchors never drift). |
| `python3 generate_kicad_pcb.py --show-silk [REF ...]` | Read-only inspect | Prints board-local coordinates, rotations, and neighbor clearances around `REF` without reading the 2,000-line script. |
| `python3 generate_kicad_pcb.py --check-silk` | Strict silk audit | Runs `SilkGrid` collision/keepout/tether checks (note: `SilkGrid` descender padding can flag valid bottom-edge labels while `kicad-cli pcb drc` passes `0` errors—always pair with `kicad-cli pcb drc` + visual review). |
| `python3 generate_kicad_pcb.py --auto-silk` | Full rebuild (auto) | Ignores `silk_layout.json` and computes fresh auto-placed silkscreen from `SilkGrid`. |

!!! warning "Full Rebuild `.kicad_pro` Guardrail"
    Whenever you run a **full rebuild** (`pcbnew.NewBoard` / `board.Save`, e.g., after swapping `TP2` `+12V` and `TP3` `-12V` physically in Trace 09 Turn 4), KiCad drops `"top_level_sheets"` from `envelope_follower.kicad_pro`. Always inspect `git diff` after full rebuilds and restore `envelope_follower.kicad_pro` via `git checkout` if needed.

---

## Step 5.3: Minting `/edit-silkscreen` & Hybrid Human + AI Visual Polish

### Authoring the Repo-Local Skill ([Trace 07 Turns 4–5](https://github.com/domesticmouse/EnvelopeFollower/blob/main/prompts/07-49155441-kicad-silkscreen-markup-eurorack-panel-kicad-pleas.md))

Ask `/agy-customizations` to create `.agents/skills/edit-silkscreen/SKILL.md` and `scripts/render_silk_preview.py`—a lightweight Pillow helper that runs transparent `kicad-cli pcb render`, auto-crops alpha bounds, and draws **calibrated millimeter rulers** around any `--ref` or `--full` board view (correctly inverting X ticks on `--side bottom` where **left = `+x` and right = `-x`**).

### The 4-Step Human + AI Hybrid Co-Editing Loop

1. **Rough-drag labels visually in KiCad PCB Editor** (getting close to open corridors between pots, jacks, and SMDs).
2. **Hit Save (`Cmd+S`) in KiCad!**
   *(Warning: Unsaved drags live only in RAM / `.history/` autosaves—even after you type `git commit`, `--sync-silk` only sees what you saved to `envelope_follower.kicad_pcb`!)*
3. **Prompt `/edit-silkscreen`** (e.g., *"Saved, please tidy/align"*): the agent runs `--sync-silk`, aligns rows/columns cleanly (such as `dy = +1.60 mm` above `0603` pads and matching pair gaps), normalizes angles (`180° → 0°`, `270° → 90°`), checks hidden `F.Fab` hardware overhangs (`block_tht_fab=True`) and vias, restamps with `--silk-only`, verifies `0` DRC errors, and renders zoomed mm-ruler PNG previews for your inspection.
4. **Reload in KiCad via `File → Revert`** before making more manual drags *(saving an un-reverted KiCad tab would overwrite the agent's `--silk-only` changes)*.

### Practical Eurorack Silkscreen Polish Checklist (From Traces 08, 09 & 11)

- **Move Pot Labels Outside `F.Fab` Overhangs**: Label `RV1 GAIN A100K`, `RV2 ATK A1M`, `RV3 REL A1M`, and `RV4 OFFSET B10K` along the clear outer corridor (`X = 5.4 mm`) rather than inside `Alpha 9 mm` / `Thonkiconn` `F.Fab` outlines where plastic bodies hide text after soldering.
- **Eurorack Power Polarity Bar**: Add a `0.80 mm` white `-12V` stripe (`SHAPE_T_SEGMENT` in `segments`, keeping clear of `qr_rects`) and `"-12V"` label directly beneath `J_PWR`.
- **Non-Standard Bi-Color LED Callouts**: Label `LED1 OUT` with **`2-PIN R/G`**, **`TAYDA A-1076`**, and **dual-sided (`F.SilkS` + `B.SilkS`) `+` polarity markers** at square Pad 1 (`+V = Green`, guarding against KiCad's default `LED_D3.0mm` square-cathode convention).
- **Concise Signal-Only Dual-Sided TPs & Clean `B.SilkS`**: Strip redundant `TP?`, `D?`, and `J_PWR` reference prefixes on `B.SilkS` (`GND`, `+12V`, `-12V`, `PRE`, `RECT`, `ENV`, `INV`, `OUT`, `HWR`, `DRV`, `OFF`, `GND2` on both sides; component values on `B.SilkS` passives and diodes).
- **Single JLCPCB QR Square**: Keep one `5.0 × 5.0 mm` white square on `F.SilkS` top-right (`(23.8, 1.0)–(28.8, 6.0)`) and remove any duplicate `B.SilkS` QR box to free dense rear routing space.
- **Off-Board `B.Fab` Notes & Exposed Board Edge**: Place `B.Fab` notes outside the board outline (`y_start = BOARD_Y1 + 5.0`) and verify with `kicad-cli pcb export pdf --layers Edge.Cuts,B.Fab,B.SilkS --mirror --include-border-title` (since `render_silk_preview.py` clips off-board layers), and put the module title/revision (`ENV FOLLOWER`, `6HP REV 1.0`) along the right edge and split GitHub URL inside the clear post-assembly corridor.
