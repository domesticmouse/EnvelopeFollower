# Envelope Follower — Improved Netlist, JLCPCB BOM, Capture Guide & Silkscreen Schedule

This reference provides the complete Bill of Materials (`45` SMD + `9` Manual THT + `8` optional `DNP` test points), ready-to-upload `jlcpcb_bom.csv`, **36-net** connection list, 8-step manual KiCad capture guide, and dual-sided silkscreen schedule for the improved Eurorack Envelope Follower ([Stage 2](../tutorial/stage-2-circuit-upgrades.md)).

---

## 1. Analog Improvements & Eurorack Protections Summary

1. **Dual `TL074HIDR` Layout (All 8 Op-Amp Channels Active)**:
   - **`U1` (`TL074H`)**: `U1A` Input Gain Stage, `U1B` Precision Half-Wave Rectifier, `U1C` `1.0×` Summing Rectifier (`R8 = 20k` 1%), `U1D` Output Gain (`~2.98×`) & Linear DC Offset Stage.
   - **`U2` (`TL074H`)**: `U2A` Unity-Gain Inverting Output, `U2B` Active Voltage-to-Current LED Driver (eliminating legacy `R20`, `R22`, `R23`), `U2C` Active Zero-Deadzone Peak Driver (with catch diode `D7` & loop compensation `C11 = 47 pF` C0G), `U2D` Zero-Load JFET `ENV_CAP` Buffer.
2. **Power Entry, Reverse-Polarity & RC Bus Filtering (`J_PWR`, `D5`, `D6`, `R26`, `R27`, `C3`–`C8`)**:
   - Series `B5819W` Schottky diodes (`D5`, `D6`) + `10 Ω` `1/4 W` (`1206`) series resistors (`R26`, `R27`) feeding `10 µF` `50 V` SMD electrolytics (`C3`, `C4`, $f_c \approx 1.59\text{ kHz}$), plus `4× 100 nF` `0603` X7R local IC decoupling caps (`C5`–`C8`) within `2 mm` of `U1`/`U2` pins 4 and 11.
3. **Gain-Floor Limiting & HF Roll-Off (`R25`, `C10`)**:
   - `R25` (`1 kΩ`) in series with `RV1` (`A100k`) sets a `-0.1×` minimum gain floor so hot Eurorack audio can be padded down without muting or shorting `C10` (`47 pF` C0G, $f_c \approx 33.5\text{ kHz}$ at max gain).
4. **Low-Impedance Linear `OFFSET` & Ripple Bypass (`R11`–`R15`, `RV4`, `C9`)**:
   - Scaling `RV4` to `B10k` (`R11 = R12 = 1k`) driving `R13 = R14 = R15 = 100k` holds envelope gain steady at `2.97×–2.99×` across a full `±9.8 V` linear offset range, while `C9` (`100 nF`) bypasses rail ripple on `OFFSET_WIPER` to `GND`.
5. **Output Short-Circuit, Back-Drive & ESD Clamping (`R16`, `R19`, `D8`, `D9`)**:
   - `1 kΩ` `1/4 W` (`1206`) output resistors (`R16`, `R19`) plus `BAT54SLT1G` (`SOT-23`) dual series Schottky rail clamps (`D8`, `D9`) on `AMP_OUT` and `INV_AMP_OUT`.

---

## 2. Full Bill of Materials (JLCPCB SMD + Manual THT)

### Integrated Circuits (JLCPCB `B.Cu` SMD)

| Ref | Qty | Value / Part | Package | KiCad Footprint | MPN | Manufacturer | LCSC # | Class | Unit Price (USD) | Circuit Role |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| `U1`, `U2` | 2 | `TL074H` Quad Op-Amp | `SOIC-14` | `Package_SO:SOIC-14_3.9x8.7mm_P1.27mm` | `TL074HIDR` | Texas Instruments | **`C2878713`** | Extended | \$0.2559 | All 8 op-amp stages (`U1A`–`U1D`, `U2A`–`U2D`) |

*Pin-compatible `SOIC-14` fallbacks if `C2878713` is out of stock: TI `TL074CDR` (`C12594`, Extended) or STMicroelectronics `TL074CDT` (`C6963`, Extended).*

### Diodes (JLCPCB `B.Cu` SMD)

| Ref | Qty | Value / Spec | Package | KiCad Footprint | MPN | Manufacturer | LCSC # | Class | Unit Price (USD) | Circuit Role |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| `D1`, `D2`, `D3`, `D7` | 4 | `1N4148W` (`75 V`, `150 mA`) | `SOD-123` | `Diode_SMD:D_SOD-123` | `1N4148W` | ST (Semtech) | **`C81598`** | **Basic** | \$0.0124 | Half-wave rectifier (`D1`, `D2`), peak charge (`D3`), catch diode (`D7`) |
| `D5`, `D6` | 2 | `B5819W` (`40 V`, `1 A` Schottky) | `SOD-123` | `Diode_SMD:D_SOD-123` | `B5819W SL` | CJ | **`C8598`** | **Basic** | \$0.0256 | `+12V` and `-12V` series reverse-polarity protection |
| `D8`, `D9` | 2 | `BAT54S` (`30 V`, `200 mA` dual series) | `SOT-23` | `Package_TO_SOT_SMD:SOT-23` | `BAT54SLT1G` | onsemi | **`C19726`** | Extended | \$0.0231 | Dual series rail clamps (`-12V` to `+12V`) on `AMP_OUT` (`D8`), `INV_AMP_OUT` (`D9`) |

### Capacitors (JLCPCB `B.Cu` SMD)

| Ref | Qty | Value / Spec | Package | KiCad Footprint | MPN | Manufacturer | LCSC # | Class | Unit Price (USD) | Circuit Role |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| `C1` | 1 | `1 µF` `50 V` X5R $\pm 10\%$ | `0603` | `Capacitor_SMD:C_0603_1608Metric` | `CL10A105KB8NNNC` | Samsung | **`C15849`** | **Basic** | \$0.0095 | Input AC coupling ($f_c \approx 15.9\text{ Hz}$ into `10 kΩ`) |
| `C2` | 1 | `220 nF` `50 V` X7R $\pm 10\%$ | `0805` | `Capacitor_SMD:C_0805_2012Metric` | `CL21B224KBFNNNE` | Samsung | **`C5378`** | **Basic** | \$0.0150 | Envelope hold / smoothing capacitor |
| `C3`, `C4` | 2 | `10 µF` `50 V` Al Electrolytic | `D6.3×L5.4mm` | `Capacitor_SMD:CP_Elec_6.3x5.4` | `RVT1H100M0605` | ROQANG | **`C72488`** | Extended | \$0.0290 | `+12V` and `-12V` bulk supply filter caps |
| `C5`–`C9` | 5 | `100 nF` `50 V` X7R $\pm 10\%$ | `0603` | `Capacitor_SMD:C_0603_1608Metric` | `CC0603KRX7R9BB104` | YAGEO | **`C14663`** | **Basic** | \$0.0049 | `C5`–`C8`: `U1`/`U2` decoupling; `C9`: `OFFSET_WIPER` ripple bypass |
| `C10`, `C11` | 2 | `47 pF` `50 V` C0G/NP0 $\pm 5\%$ | `0603` | `Capacitor_SMD:C_0603_1608Metric` | `CL10C470JB8NNNC` | Samsung | **`C1671`** | **Basic** | \$0.0063 | `C10`: preamp HF roll-off; `C11`: peak-detector loop compensation |

### Fixed Resistors (JLCPCB `B.Cu` SMD — 100% Basic Parts)

| Ref | Qty | Value / Spec | Package | KiCad Footprint | MPN | Manufacturer | LCSC # | Class | Unit Price (USD) | Circuit Role |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| `R1` | 1 | `1 MΩ` `1%` `1/10 W` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1004T5E` | UNI-ROYAL | **`C22935`** | **Basic** | \$0.0018 | Input AC-coupling pulldown to `GND` |
| `R2`–`R7`, `R17`, `R18` | 8 | `10 kΩ` `1%` `1/10 W` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1002T5E` | UNI-ROYAL | **`C25804`** | **Basic** | \$0.0019 | Preamp input (`R2`), full-wave rectifier (`R3`–`R7`), inv. out (`R17`, `R18`) |
| `R8` | 1 | `20 kΩ` `1%` `1/10 W` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF2002T5E` | UNI-ROYAL | **`C4184`** | **Basic** | \$0.0018 | Rectifier summing feedback (`1.0×` symmetry) |
| `R9`, `R11`, `R12`, `R25` | 4 | `1 kΩ` `1%` `1/10 W` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1001T5E` | UNI-ROYAL | **`C21190`** | **Basic** | \$0.0017 | Min attack (`R9`), `OFFSET` limits (`R11`, `R12`), gain floor (`R25`) |
| `R10` | 1 | `47 kΩ` `1%` `1/10 W` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF4702T5E` | UNI-ROYAL | **`C25819`** | **Basic** | \$0.0016 | Minimum release discharge resistor (`~10.3 ms` min release) |
| `R13`–`R15`, `R24` | 4 | `100 kΩ` `1%` `1/10 W` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1003T5E` | UNI-ROYAL | **`C25803`** | **Basic** | \$0.0029 | Stage 5 offset/gain (`R13`–`R15`), peak-detector feedback (`R24`) |
| `R16`, `R19` | 2 | `1 kΩ` `1%` `1/4 W` | `1206` | `Resistor_SMD:R_1206_3216Metric` | `1206W4F1001T5E` | UNI-ROYAL | **`C4410`** | **Basic** | \$0.0085 | `OUT` (`R16`) & `INV_OUT` (`R19`) `250 mW` output protection |
| `R21` | 1 | `1.5 kΩ` `1%` `1/10 W` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1501T5E` | UNI-ROYAL | **`C22843`** | **Basic** | \$0.0020 | Active LED current-setting resistor (`2.2 kΩ` Basic alt: `C4190`) |
| `R26`, `R27` | 2 | `10 Ω` `1%` `1/4 W` | `1206` | `Resistor_SMD:R_1206_3216Metric` | `1206W4F100JT5E` | UNI-ROYAL | **`C17903`** | **Basic** | \$0.0061 | `+12V` (`R26`) & `-12V` (`R27`) series rail RC filter / inrush protection |

### Manual Through-Hole (THT) & Optional `DNP` Test Points (Mounted After PCBA)

| Ref | Qty | Value / Spec | Component Type | KiCad Footprint / Mounting Side | Circuit Role |
| :--- | :---: | :--- | :--- | :--- | :--- |
| `J_PWR` | 1 | `2x5` Shrouded IDC (`2.54 mm`) | Vertical THT Box Header | `Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical` (`B.Cu`) | Eurorack $\pm 12\text{ V}$ power entry |
| `J1`–`J3` | 3 | `WQP-PJ398SM` (`3.5 mm` Mono TS) | Vertical THT Thonkiconn | `Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` (`F.Cu`) | `J1`: `IN`, `J2`: `OUT`, `J3`: `INV_OUT` |
| `RV1` | 1 | `100 kΩ` Audio/Log (`A100k`) | 9 mm Vertical Pot (`RD901F`) | `Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` (`F.Cu`) | `GAIN` (`-0.1×` to `-10.1×`) |
| `RV2` | 1 | `50 kΩ` Audio/Log (`A50k`) | 9 mm Vertical Pot (`RD901F`) | `Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` (`F.Cu`) | `ATK` (attack charging time) |
| `RV3` | 1 | `1 MΩ` Audio/Log (`A1M`) | 9 mm Vertical Pot (`RD901F`) | `Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` (`F.Cu`) | `Release` (decay time) |
| `RV4` | 1 | `10 kΩ` Linear (`B10k`) | 9 mm Vertical Pot (`RD901F`) | `Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` (`F.Cu`) | `OFFSET` (`±9.8 V` DC offset) |
| `D4` | 1 | `3 mm` THT LED (any color) | Radial THT LED | `LED_THT:LED_D3.0mm` (`F.Cu`) | Active envelope level indicator |
| `TP1`–`TP8` (**`DNP`**) | 8 (`DNP`) | `Ronghe RH-5001` (`C5199801`) | Miniature THT Test Loop (`1.0 mm` drill) | `TestPoint:TestPoint_Keystone_5000-5004_Miniature` (`B.Cu`, **`DNP`**) | `TP1`: `GND`; `TP2`: `+12V`; `TP3`: `-12V`; `TP4`: `PREAMP_OUT`; `TP5`: `HALF_RECT`; `TP6`: `FULL_RECT`; `TP7`: `ENV_SIG`; `TP8`: `OFFSET_WIPER` |

### Ready-to-Upload `jlcpcb_bom.csv` (45 SMD Parts Across 18 Lines)

```csv
Comment,Designator,Footprint,LCSC Part #
TL074HIDR,"U1, U2",SOIC-14_3.9x8.7mm_P1.27mm,C2878713
1N4148W,"D1, D2, D3, D7",D_SOD-123,C81598
B5819W,"D5, D6",D_SOD-123,C8598
BAT54SLT1G,"D8, D9",SOT-23,C19726
1uF 50V,C1,C_0603_1608Metric,C15849
220nF 50V,C2,C_0805_2012Metric,C5378
10uF 50V,"C3, C4",CP_Elec_6.3x5.4,C72488
100nF 50V,"C5, C6, C7, C8, C9",C_0603_1608Metric,C14663
47pF 50V,"C10, C11",C_0603_1608Metric,C1671
1M,R1,R_0603_1608Metric,C22935
10k,"R2, R3, R4, R5, R6, R7, R17, R18",R_0603_1608Metric,C25804
20k,R8,R_0603_1608Metric,C4184
1k,"R9, R11, R12, R25",R_0603_1608Metric,C21190
47k,R10,R_0603_1608Metric,C25819
100k,"R13, R14, R15, R24",R_0603_1608Metric,C25803
1k 1/4W,"R16, R19",R_1206_3216Metric,C4410
1.5k,R21,R_0603_1608Metric,C22843
10R 1/4W,"R26, R27",R_1206_3216Metric,C17903
```

---

## 3. Complete 36-Net Node Connectivity Table

| Net Name | Connected Component Terminals (with IC Pin Numbers) |
| :--- | :--- |
| `+12V_IN` | `J_PWR` (pins 9, 10), `D5` (anode) |
| `+12V_PROT` | `D5` (cathode), `R26` (pin 1) |
| `+12V` | `R26` (pin 2), `C3` (`+`), `C5` (pin 1), `C7` (pin 1), `U1` (pin 4 / $V_{CC+}$), `U2` (pin 4 / $V_{CC+}$), `R11` (pin 1), `D8` (pin 2), `D9` (pin 2), `TP2` (pin 1) |
| `-12V_IN` | `J_PWR` (pins 1, 2), `D6` (cathode) |
| `-12V_PROT` | `D6` (anode), `R27` (pin 1) |
| `-12V` | `R27` (pin 2), `C4` (`-`), `C6` (pin 1), `C8` (pin 1), `U1` (pin 11 / $V_{CC-}$), `U2` (pin 11 / $V_{CC-}$), `R12` (pin 2), `D8` (pin 1), `D9` (pin 1), `TP3` (pin 1) |
| `GND` | `J_PWR` (pins 3–8), `C3` (`-`), `C4` (`+`), `C5` (pin 2), `C6` (pin 2), `C7` (pin 2), `C8` (pin 2), `C9` (pin 2), `J1` (sleeve), `J2` (sleeve), `J3` (sleeve), `R1` (pin 2), `U1A` (pin 3 / `+`), `U1B` (pin 5 / `+`), `U1C` (pin 10 / `+`), `C2` (pin 2), `RV3` (pin 2 & pin 3), `R14` (pin 2), `U2A` (pin 3 / `+`), `R21` (pin 2), `TP1` (pin 1) |
| `IN_TIP` | `J1` (`IN` tip), `C1` (pin 1) |
| `AC_IN` | `C1` (pin 2), `R1` (pin 1), `R2` (pin 1) |
| `PREAMP_INV` | `R2` (pin 2), `U1A` (pin 2 / `-`), `R25` (pin 1), `C10` (pin 1) |
| `GAIN_FLOOR` | `R25` (pin 2), `RV1` (pin 1) |
| `PREAMP_OUT` | `U1A` (pin 1 / out), `RV1` (pin 2 & pin 3), `C10` (pin 2), `R3` (pin 1), `R6` (pin 1), `TP4` (pin 1) |
| `RECT1_INV` | `R3` (pin 2), `U1B` (pin 6 / `-`), `D1` (cathode), `R4` (pin 1) |
| `RECT1_OUT` | `U1B` (pin 7 / out), `D1` (anode), `D2` (cathode) |
| `HALF_RECT` | `D2` (anode), `R4` (pin 2), `R5` (pin 1), `TP5` (pin 1) |
| `FF_MID` | `R6` (pin 2), `R7` (pin 1) |
| `RECT2_INV` | `R7` (pin 2), `R5` (pin 2), `U1C` (pin 9 / `-`), `R8` (pin 1) |
| `FULL_RECT` | `U1C` (pin 8 / out), `R8` (pin 2), `U2C` (pin 10 / `+`), `TP6` (pin 1) |
| `PK_FB_INV` | `U2C` (pin 9 / `-`), `R24` (pin 2), `D7` (anode), `C11` (pin 1) |
| `PK_DRV_OUT` | `U2C` (pin 8 / out), `D3` (anode), `D7` (cathode), `C11` (pin 2) |
| `ATK_IN` | `D3` (cathode), `R9` (pin 1) |
| `ATK_MID` | `R9` (pin 2), `RV2` (pin 1) |
| `ENV_CAP` | `RV2` (pin 2 & pin 3), `C2` (pin 1), `R10` (pin 1), `U2D` (pin 12 / `+`) |
| `REL_MID` | `R10` (pin 2), `RV3` (pin 1) |
| `ENV_SIG` | `U2D` (pin 14 / out), `U2D` (pin 13 / `-`), `R24` (pin 1), `U1D` (pin 12 / `+`), `U2B` (pin 5 / `+`), `TP7` (pin 1) |
| `OFFSET_TOP` | `R11` (pin 2), `RV4` (pin 1 / CW) |
| `OFFSET_BOT` | `RV4` (pin 3 / CCW), `R12` (pin 1) |
| `OFFSET_WIPER` | `RV4` (pin 2 / wiper), `C9` (pin 1), `R13` (pin 1), `TP8` (pin 1) |
| `AMP_INV` | `R13` (pin 2), `R14` (pin 1), `R15` (pin 1), `U1D` (pin 13 / `-`) |
| `AMP_OUT` | `U1D` (pin 14 / out), `R15` (pin 2), `D8` (pin 3), `R16` (pin 1), `R17` (pin 1) |
| `OUT_TIP` | `R16` (pin 2), `J2` (`OUT` tip) |
| `INV_STAGE_IN` | `R17` (pin 2), `U2A` (pin 2 / `-`), `R18` (pin 1) |
| `INV_AMP_OUT` | `U2A` (pin 1 / out), `R18` (pin 2), `D9` (pin 3), `R19` (pin 1) |
| `INV_OUT_TIP` | `R19` (pin 2), `J3` (`INV_OUT` tip) |
| `LED_A` | `U2B` (pin 7 / out), `D4` (anode) |
| `LED_K` | `D4` (cathode), `U2B` (pin 6 / `-`), `R21` (pin 1) |

---

## 4. Manual KiCad Schematic Capture Checklist

If capturing the schematic manually in KiCad instead of generating it via SKiDL in [Stage 3](../tutorial/stage-3-skidl.md):

### Step 1: Project Setup & Op-Amp Allocation
- [ ] Create `EnvelopeFollower.kicad_pro` and open `EnvelopeFollower.kicad_sch` in KiCad 10.
- [ ] Place `+12V`, `-12V`, and `GND` power symbols (plus `PWR_FLAG` as needed for ERC).
- [ ] Place **`U1`** (`TL074`) and **`U2`** (`TL074`) including both power units (`Pin 4 = +12V`, `Pin 11 = -12V`).

### Step 2: Power Protection, Filtering & Decoupling
- [ ] Place `J_PWR` (`2x5` IDC header): Pins 1–2 (`-12V_IN`), Pins 3–8 (`GND`), Pins 9–10 (`+12V_IN`).
- [ ] Wire `+12V_IN` $\rightarrow$ `D5` (`B5819W` anode-to-cathode) $\rightarrow$ `R26` (`10 Ω`) $\rightarrow$ `+12V`; wire `-12V_IN` $\rightarrow$ `D6` (`B5819W` cathode-to-anode) $\rightarrow$ `R27` (`10 Ω`) $\rightarrow$ `-12V`.
- [ ] Wire bulk caps `C3` (`10 µF`: `+` to `+12V`, `-` to `GND`) and `C4` (`10 µF`: **`+` to `GND`**, `-` to `-12V`).
- [ ] Wire `100 nF` bypass caps `C5`/`C6` at `U1` pins 4/11 and `C7`/`C8` at `U2` pins 4/11.
- [ ] Attach `DNP` test points `TP1` (`GND`), `TP2` (`+12V`), `TP3` (`-12V`).

### Step 3: Input Coupling & Gain Stage (`U1A`)
- [ ] Wire `J1` (`IN` tip) $\rightarrow$ `C1` (`1 µF`) $\rightarrow$ `R1` (`1 MΩ` to `GND`) & `R2` (`10 kΩ`) $\rightarrow$ `U1A` pin 2 (`-`), with `U1A` pin 3 (`+`) to `GND`.
- [ ] Wire `R25` (`1 kΩ`) in series with `RV1` (`A100k`, pin 2 wiper tied to pin 3) from `U1A` pin 2 to `U1A` pin 1 (`PREAMP_OUT`), with `C10` (`47 pF`) spanning pin 2 to pin 1. Attach `TP4` (`PRE`).

### Step 4: Precision Full-Wave Rectifier (`U1B`, `U1C`)
- [ ] **Half-Wave (`U1B`)**: Wire `PREAMP_OUT` $\rightarrow$ `R3` (`10 kΩ`) $\rightarrow$ `U1B` pin 6 (`-`); `U1B` pin 5 (`+`) to `GND`; `D1` (`1N4148W`) anode to pin 7, cathode to pin 6; `D2` (`1N4148W`) cathode to pin 7, anode to `HALF_RECT`; `R4` (`10 kΩ`) from pin 6 to `HALF_RECT`. Attach `TP5` (`HALF`).
- [ ] **Summing (`U1C`)**: Wire `PREAMP_OUT` $\rightarrow$ `R6` (`10 kΩ`) $\rightarrow$ `R7` (`10 kΩ`) $\rightarrow$ `U1C` pin 9 (`-`); `HALF_RECT` $\rightarrow$ `R5` (`10 kΩ`) $\rightarrow$ `U1C` pin 9; `U1C` pin 10 (`+`) to `GND`; `R8` (`20 kΩ`) from pin 9 to pin 8 (`FULL_RECT`). Attach `TP6` (`RECT`).

### Step 5: Active Zero-Deadzone Peak Detector & Buffer (`U2C`, `U2D`)
- [ ] Wire `FULL_RECT` to `U2C` pin 10 (`+`). Wire `U2C` pin 8 (`PK_DRV_OUT`) $\rightarrow$ `D3` (anode-to-cathode) $\rightarrow$ `R9` (`1 kΩ`) $\rightarrow$ `RV2` (`ATK`, `A50k`, wiper tied to pin 3) $\rightarrow$ `ENV_CAP`.
- [ ] Wire `C2` (`220 nF`) from `ENV_CAP` to `GND`, and `R10` (`47 kΩ`) $\rightarrow$ `RV3` (`Release`, `A1M`, wiper tied to pin 3) to `GND`.
- [ ] Wire `U2D` pin 12 (`+`) to `ENV_CAP`, and tie pin 13 (`-`) to pin 14 (`ENV_SIG`).
- [ ] Wire `R24` (`100 kΩ`) from `ENV_SIG` to `U2C` pin 9 (`PK_FB_INV`), and wire catch diode `D7` (anode to pin 9, cathode to pin 8) + compensation `C11` (`47 pF`) across pins 9 and 8. Attach `TP7` (`ENV`) to `ENV_SIG`.

### Step 6: Output Amplifier, Offset, Inverter & Active LED (`U1D`, `U2A`, `U2B`)
- [ ] Wire `+12V` $\rightarrow$ `R11` (`1 kΩ`) $\rightarrow$ `RV4` (`B10k`) $\rightarrow$ `R12` (`1 kΩ`) $\rightarrow$ `-12V`; bypass `OFFSET_WIPER` with `C9` (`100 nF`) to `GND`, attach `TP8` (`OFS`), and connect via `R13` (`100 kΩ`) to `U1D` pin 13 (`-`). Wire `R14` (`100 kΩ`) to `GND`, `R15` (`100 kΩ`) from pin 14 (`AMP_OUT`), and `ENV_SIG` to `U1D` pin 12 (`+`).
- [ ] Wire `D8` (`BAT54S`: pin 1 `-12V`, pin 2 `+12V`, pin 3 `AMP_OUT`) and `R16` (`1 kΩ` `1/4 W`) to `J2` (`OUT`).
- [ ] Wire `AMP_OUT` $\rightarrow$ `R17` (`10 kΩ`) $\rightarrow$ `U2A` pin 2 (`-`), `U2A` pin 3 (`+`) to `GND`, `R18` (`10 kΩ`) feedback to `U2A` pin 1 (`INV_AMP_OUT`), `D9` (`BAT54S`), and `R19` (`1 kΩ` `1/4 W`) to `J3` (`INV_OUT`).
- [ ] Wire `ENV_SIG` to `U2B` pin 5 (`+`), `U2B` pin 7 (`LED_A`) $\rightarrow$ `D4` (anode), `D4` (cathode) $\rightarrow$ `U2B` pin 6 (`-`) & `R21` (`1.5 kΩ`) $\rightarrow$ `GND`.

### Step 7: ERC, Footprints & Silkscreen Prep
- [ ] Mark `TP1`–`TP8` with `Exclude from BOM` / `Exclude from position files` / `Do not populate`.
- [ ] Run **ERC** (`0` errors, `0` warnings), assign footprints from Section 2, and export netlist.

---

## 5. Complete Component-by-Component Silkscreen Schedule

Follow these exact layer assignments (`B.SilkS` for single-sided `B.Cu` SMD assembly; dual-sided `F.SilkS` + `B.SilkS` for manual THT controls and `TP1`–`TP8` test points):

| Ref | Package / Side | `F.SilkS` Label | `B.SilkS` Label | Required Polarity / Orientation Mark |
| :--- | :--- | :--- | :--- | :--- |
| `U1`, `U2` | `SOIC-14` (`B.Cu`) | — | `U1 TL074H`, `U2 TL074H` | Pin-1 dot + notch outside body |
| `D1`–`D3`, `D7` | `SOD-123` (`B.Cu`) | — | `D1 1N4148W` … `D7 1N4148W` | External cathode bar (`\|`) beyond cathode pad |
| `D5`, `D6` | `SOD-123` (`B.Cu`) | — | `D5 B5819W`, `D6 B5819W` | External cathode bar (`\|`) (`D5`: `+12V_PROT`; `D6`: `-12V_IN`) |
| `D8`, `D9` | `SOT-23` (`B.Cu`) | — | `D8 BAT54S`, `D9 BAT54S` | Open `SOT-23` corners; pin-1 (`-12V`) mark if space allows |
| `C1` | `0603` (`B.Cu`) | — | `C1 1uF` | Non-polarized |
| `C2` | `0805` (`B.Cu`) | — | `C2 220nF` | Non-polarized |
| `C3` | `CP_Elec_6.3x5.4` (`B.Cu`) | — | `C3 10uF 50V` | `+` outside anode (`+12V`) pad + chamfered base outline |
| `C4` | `CP_Elec_6.3x5.4` (`B.Cu`) | — | `C4 10uF 50V` | `+` outside anode (**`GND`**) pad + chamfered base outline |
| `C5`–`C9` | `0603` (`B.Cu`) | — | `C5 100nF` … `C9 100nF` | Non-polarized |
| `C10`, `C11` | `0603` (`B.Cu`) | — | `C10 47pF`, `C11 47pF` | Non-polarized |
| `R1` | `0603` (`B.Cu`) | — | `R1 1M` | Non-polarized |
| `R2`–`R7`, `R17`, `R18` | `0603` (`B.Cu`) | — | `R2 10k` … `R18 10k` | Non-polarized |
| `R8` | `0603` (`B.Cu`) | — | `R8 20k` | Non-polarized |
| `R9`, `R11`, `R12`, `R25` | `0603` (`B.Cu`) | — | `R9 1k`, `R11 1k`, `R12 1k`, `R25 1k` | Non-polarized |
| `R10` | `0603` (`B.Cu`) | — | `R10 47k` | Non-polarized |
| `R13`–`R15`, `R24` | `0603` (`B.Cu`) | — | `R13 100k` … `R15 100k`, `R24 100k` | Non-polarized |
| `R16`, `R19` | `1206` (`B.Cu`) | — | `R16 1k`, `R19 1k` | Non-polarized (`1/4 W` `1206` outline) |
| `R21` | `0603` (`B.Cu`) | — | `R21 1.5k` | Non-polarized |
| `R26`, `R27` | `1206` (`B.Cu`) | — | `R26 10R`, `R27 10R` | Non-polarized (`1/4 W` `1206` outline) |
| `J_PWR` | `IDC 2x5` (THT, `B.Cu`) | `J_PWR +/-12V` + `-12V` bar | `J_PWR +/-12V` + `-12V / RED STRIPE` | Pin-1 dot, keyway notch on `B.SilkS`, `-12V`/`GND`/`+12V` on **both** layers |
| `J1`–`J3` | `WQP-PJ398SM` (THT, `F.Cu`) | `J1 IN`, `J2 OUT`, `J3 INV_OUT` | `J1 IN`, `J2 OUT`, `J3 INV_OUT` | Jack body outline on `F.SilkS` |
| `RV1`–`RV4` | `9mm Pot` (THT, `F.Cu`) | `RV1 GAIN A100k`, `RV2 ATK A50k`, `RV3 REL A1M`, `RV4 OFFSET B10k` | `RV1 GAIN A100k`, `RV2 ATK A50k`, `RV3 REL A1M`, `RV4 OFFSET B10k` | Pin-1 (`1`) square pad / marker on **both** layers |
| `D4` | `LED_D3.0mm` (THT, `F.Cu`) | `D4 LED` (`+` / `-`) | `D4 LED` (`+` / `-`) | `+` (anode) and `-` / flat side (cathode) on **both** layers |
| `TP1`–`TP8` (`DNP`) | `RH-5001` (`DNP` THT, `B.Cu`) | `TP1 GND` … `TP8 OFS` | `TP1 GND` … `TP8 OFS` | Identical designator + mnemonic on **both** `F.SilkS` and `B.SilkS` |
