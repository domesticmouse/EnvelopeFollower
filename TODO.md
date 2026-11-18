# KiCad PCB & Fabrication TODO

The SKiDL circuit definition (`envelope_follower.py`), KiCad netlist (`envelope_follower.net`), XML BOM (`envelope_follower_bom.xml`), and JLCPCB SMT BOM (`jlcpcb_bom.csv`) are complete and ERC-clean (48 physical components, 35 nets).

Follow this checklist to take the circuit into KiCad PCB layout and manufacturing.

---

## Step 1: Create Project & Import Netlist into KiCad PCB Editor

### Option A — Via the KiCad GUI
- [ ] Open KiCad (v10) and create a new project: **File → New Project...** (`EnvelopeFollower.kicad_pro`).
- [ ] Open **PCB Editor** (`EnvelopeFollower.kicad_pcb`).
- [ ] Import the netlist via **File → Import → Netlist...** and select `envelope_follower.net`.
- [ ] Click **Update PCB** and **Close** to load all 48 footprints and 35 nets onto the PCB canvas.

### Option B — Automated `.kicad_pcb` Generation (Optional)
- [x] Generate an initial `EnvelopeFollower.kicad_pcb` directly from `envelope_follower.net` using KiCad's bundled `pcbnew` / `kinet2pcb` Python environment with a pre-sized `Edge.Cuts` outline and Eurorack control grid (`generate_kicad_pcb.py`), plus `EnvelopeFollower.kicad_sch` via `envelope_follower.py`.

---

## Step 2: Main Circuit PCB Layout (`EnvelopeFollower.kicad_pcb`)

- [x] **Board Outline (`Edge.Cuts`)**: Define the PCB width for your target Eurorack HP (e.g., **4 HP** = `20.0 mm` panel / `~19.6 mm` PCB width, or **6 HP** = `30.0 mm` panel / `~29.6 mm` PCB width) and height (`~100–107 mm` for 3U rail/M3 screw clearance).
- [x] **Front-Panel Controls (`F.Cu`)**: Arrange the vertical panel-mounted parts on an ergonomic grid:
  - [x] Potentiometers (`RV_GAIN`, `RV_ATK`, `RV_REL`, `RV_OFFSET` — `Potentiometer_Alpha_RD901F-40-00D_Single_Vertical`)
  - [x] Status Indicator (`LED1` — `LED_D3.0mm`)
  - [x] 3.5mm Jacks (`J_IN`, `J_OUT`, `J_INV_OUT` — `Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles`)
- [x] **Rear Power Connector (`B.Cu`)**:
  - [x] Flip `J_PWR` (`IDC-Header_2x05_P2.54mm_Vertical`) to `B.Cu` so the ribbon cable connects from behind the module.
  - [x] Add clear `-12V` (`Pin 1`/`Pin 2`, red stripe) silkscreen polarity markings on `B.SilkS`.
- [x] **SMT Placement (Single-Sided `B.Cu` or Open `F.Cu` Zones)**:
  - [x] Place `U1` and `U2` (`TL074HIDR`, `SOIC-14`) centrally with local `100 nF` bypass capacitors (`C5`–`C8`) directly adjacent to Pin 4 (`+12V`) and Pin 11 (`-12V`).
  - [x] Place Schottky protection diodes (`D4`, `D5` — `B5819W`) and bulk `4.7uF` 50V electrolytics (`C3`, `C4`) right next to `J_PWR`.
  - [x] Place remaining `0603`/`0805` passives and `SOD-123` signal diodes (`D1`–`D3`) near their respective op-amp stages, keeping analog input/rectifier traces short.
- [ ] **Routing, Ground Pour & DRC**:
  - [ ] Route `Power` class nets (`+12V_RAW`, `-12V_RAW`, `+12V`, `-12V`) at `0.5–0.6 mm` width and analog signal nets at `0.25 mm` width.
  - [ ] Add `GND` copper pours on both `F.Cu` and `B.Cu` with stitching vias.
  - [ ] Run **Design Rules Check (DRC)** and verify 0 errors, 0 clearance violations, and 0 unrouted nets.

---

## Step 3: Mated 3U Eurorack Front Panel PCB

- [ ] Generate the mated 3U front panel (`panel/EnvelopeFollower_Panel.kicad_pcb`) using the main PCB's finalized coordinates:
  - [ ] Extract exact `(x, y)` positions of `RV_GAIN`, `RV_ATK`, `RV_REL`, `RV_OFFSET`, `LED1`, `J_IN`, `J_OUT`, and `J_INV_OUT`, applying footprint-to-bushing mechanical offsets (e.g., `+6.48 mm` for `WQP-PJ398SM` Thonkiconn jacks).
  - [ ] Place standard Doepfer A-100 3U (`128.5 mm` height) M3 mounting slots.
  - [ ] Add panel silkscreen labels (`GAIN`, `ATK`, `REL`, `OFFSET`, `IN`, `OUT`, `INV OUT`, `ENV`), input callout badges, and grounded `F.Cu`/`B.Cu` shield planes.
  - [ ] Run DRC on the front panel PCB.

---

## Step 4: Export Fabrication & JLCPCB PCBA Files

- [ ] Export fabrication **Gerbers** and **Excellon drill** files for both `EnvelopeFollower.kicad_pcb` and the 3U front panel PCB.
- [ ] Export the **Component Placement / Centroid (`.pos` / CPL)** file from KiCad PCB Editor for JLCPCB SMT assembly.
- [ ] Upload the Gerber ZIP, `jlcpcb_bom.csv`, and CPL `.pos` file to JLCPCB, verify SMT part orientation in the 3D/assembly preview (especially `U1`, `U2`, `D1`–`D5`, `C3`, `C4`), and order!
