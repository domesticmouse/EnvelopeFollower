# Eurorack Mechanical Specification & KiCad Footprint Offsets

## 1. Doepfer A-100 3U Panel Dimensions & HP Width Table

- **Standard 3U Panel Height**: **`128.5 mm`**
- **Maximum Rear PCB Height (between rails)**: **`108.0 mm – 110.0 mm`** (`108.0 mm` recommended, giving `10.25 mm` top and bottom clearance when centered behind a `128.5 mm` panel).
- **Horizontal Pitch (1 HP)**: `5.08 mm` (`0.200"`). Actual manufactured panels are slightly narrower than $N \times 5.08\text{ mm}$ to allow tolerance between adjacent modules:

| HP | Nominal $N \times 5.08\text{ mm}$ | Doepfer Standard Width ($\text{mm}$) | Mounting Holes | Left Hole $X_{\text{local}}$ ($\text{mm}$) | Right Hole $X_{\text{local}}$ ($\text{mm}$) |
| --: | :---: | :---: | :---: | :---: | :---: |
| **1 HP** | `5.08` | `5.00` | 1 top, 1 bottom | `2.50` | — |
| **2 HP** | `10.16` | `9.80` | 1 top, 1 bottom | `7.50` (or `5.00` slot) | — |
| **3 HP** | `15.24` | `15.00` | 1 top, 1 bottom | `7.50` | — |
| **4 HP** | `20.32` | **`20.00`** | 1 top, 1 bottom | **`7.50`** | — |
| **6 HP** | `30.48` | `30.00` | 1 top, 1 bottom | `7.50` | — |
| **8 HP** | `40.64` | `40.30` | 1 top, 1 bottom | `7.50` | — |
| **10 HP** | `50.80` | `50.50` | 2 top, 2 bottom | `7.50` | `43.18` (`7.50 + 7 × 5.08`) |
| **12 HP** | `60.96` | `60.60` | 2 top, 2 bottom | `7.50` | `53.34` (`7.50 + 9 × 5.08`) |
| **14 HP** | `71.12` | `70.80` | 2 top, 2 bottom | `7.50` | `63.50` (`7.50 + 11 × 5.08`) |
| **16 HP** | `81.28` | `80.90` | 2 top, 2 bottom | `7.50` | `73.66` (`7.50 + 13 × 5.08`) |
| **20 HP** | `101.60` | `101.30` | 2 top, 2 bottom | `7.50` | `93.98` (`7.50 + 17 × 5.08`) |

### Rack Mounting Holes / Slots (M3)
- **Vertical Y Coordinates (from Top Edge of `128.5 mm` Panel)**:
  - **Top Mounting Hole/Slot**: **`Y = 3.00 mm`**
  - **Bottom Mounting Hole/Slot**: **`Y = 125.50 mm`** (`3.00 mm` from bottom edge; `122.50 mm` vertical center-to-center spacing)
- **Hole vs. Oval Slot**:
  - Circular M3 hole: **`3.2 mm`** diameter (`NPTH`).
  - Oval M3 slot (recommended for PCB panels): **`5.5 mm` wide × `3.2 mm` tall** (`NPTH` oval pad + drill), accommodating both fixed threaded strips (`5.08 mm` pitch) and sliding M3 nuts.

---

## 2. Panel-Mounted Component Cutouts, Standoffs & KiCad Offsets

Most vertical PCB-mounted panel components establish a **`~10.0 mm – 11.0 mm`** board-to-panel standoff height between `F.Cu` of the main PCB and `B.Cu` of the front panel:

| Component Type | Common Part / MPN | KiCad Footprint | Footprint Origin `(0, 0)` | Shaft / Bushing Offset `(dx, dy)` at `rot=0` | Panel Hole Drill ($\text{mm}$) | Nut / Bezel Keepout OD ($\text{mm}$) | Board-to-Panel Standoff ($\text{mm}$) |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **3.5mm Mono Jack (Thonkiconn)** | QingPu `WQP-PJ398SM` / `PJ301M-12` | `Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | Pad `S` (Sleeve) | **`(0.00, +6.48)`** | **`6.2` – `6.3`** (M6×0.5 bushing) | **`9.5`** (Knurled / Hex nut) | `10.5` |
| **9mm Vertical Potentiometer** | Alpha `RV09AF-40` / Alps `RK09K` | `Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical` | Pad `1` | **`(+2.50, -7.00)`** *(check `fp_circle`)* | **`7.2` – `7.5`** (M7×0.75) or **`6.3`** (D-shaft) | **`10.5` – `11.0`** (M7 nut + washer) | `10.0` – `10.5` |
| **Sub-Mini Toggle Switch** | Taiway `100-SP1-T1` / Dailywell `2M1` | `Button_Switch_THT:SW_CuK_JS202011JCQN_DPDT_Straight` | Center / Pin `1` | Inspect `F.Fab` center | **`5.2` – `6.2`** (`M5` or `1/4-40` bushing) | **`8.0` – `9.5`** | `10.5` |
| **3mm THT LED** | Standard 3mm LED | `LED_THT:LED_D3.0mm` | Pad `1` (Cathode) | **`(+1.27, 0.00)`** | **`3.2`** | `4.0` (flange) | Bend/spacer to `10.5` |
| **5mm THT LED** | Standard 5mm LED | `LED_THT:LED_D5.0mm` | Pad `1` (Cathode) | **`(+1.27, 0.00)`** | **`5.2`** | `6.0` (flange) | Bend/spacer to `10.5` |

### Computing Rotated Bushing Coordinates from KiCad Footprints
In KiCad's coordinate system ($X$ right, $Y$ down) where a footprint is placed at `(at X_fp Y_fp ROT_DEG)` on `F.Cu` and the shaft/bushing center inside the footprint definition is `(cx, cy)`:
- KiCad rotates footprints counter-clockwise by `ROT_DEG` in screen space:
  $$\Delta X = c_x \cos(\theta) + c_y \sin(\theta), \quad \Delta Y = -c_x \sin(\theta) + c_y \cos(\theta)$$
  where $\theta = \text{radians}(\text{ROT\_DEG})$.
- Always verify against the footprint's `fp_circle` on `F.Fab` or `F.SilkS`.

---

## 3. Eurorack Rear Power Header (`J_PWR`) Orientation & `B.Cu` Flip Geometry

By Doepfer A-100 convention, the rear 10-pin (`2×5`) or 16-pin (`2×8`) Eurorack IDC power header is mounted with **Pin 1 / Pin 2 (`-12V`, red ribbon stripe) at the bottom** and **`+12V` (`Pin 9/10` on 10-pin, `Pin 9/10` + `+5V`/`CV`/`Gate` above on 16-pin) at the top**.

### KiCad `pcbnew` `fp.Flip()` Behavior (`Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical`)
Inside KiCad's default `IDC-Header_2x05_P2.54mm_Vertical` footprint:
- Pin 1 is at `(0.00, 0.00)`, Pin 2 is at `(2.54, 0.00)`, and Pins 9–10 are at `(0.00, +10.16)` / `(2.54, +10.16)` on `F.Cu`.
- Calling `fp.Flip(VECTOR2I(0, 0), False)` in `pcbnew` moves the footprint to `B.Cu` and **mirrors local $Y$** across the X-axis:
  - Pin 1 / Pin 2 remain at `(0.00, 0.00)` and `(2.54, 0.00)`.
  - Pin 9 / Pin 10 move to `(0.00, -10.16)` and `(2.54, -10.16)`.
- **Correct Orientation on `B.Cu`**:
  - **`rot = 0°` (Correct Eurorack Standard)**: Pin 1/2 (`-12V RED`) sit at the **bottom** (larger global $Y$), while Pin 9/10 (`+12V`) sit `10.16 mm` above at the **top** (smaller global $Y$).
  - **`rot = 180°` (Upside Down — Avoid)**: Flips local $-Y$ back to $+Y$, placing Pin 1/2 at the top and `+12V` at the bottom.
- **Shroud & Pin-1 Arrow Clearances (`B.Cu`, `rot = 0°`)**:
  - Shroud silkscreen (`B.SilkS`) spans `X: [-3.29, +5.83]` mm and `Y: [-15.37, +5.21]` mm relative to Pin 1, with physical center at `(+1.27, -5.08)` mm.
  - The Pin 1 triangle marker on `B.SilkS` extends outward to `X = -3.68 .. -4.68 mm`, `Y = -0.50 .. +0.50 mm` relative to Pin 1. Keep it clear of bottom-row jack/pot THT pads and solder mask openings to prevent `silk_over_copper` DRC warnings.
