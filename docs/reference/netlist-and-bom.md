# Netlist, BOM & Silkscreen Schedule

Complete electrical and physical reference for the finalized **`EnvelopeFollowerWithSkewLimiter`** build ([`reference/envelope_follower_bom.xml`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/envelope_follower_bom.xml), [`reference/jlcpcb_bom.csv`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/jlcpcb_bom.csv), and [`reference/silk_layout.json`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/silk_layout.json)).

---

## Summary Metrics

| Category | Count | Details |
| :--- | :---: | :--- |
| **Netlist Components** | `80` | `50` SMDs + `18` Manual THT + `12` DNP Test Points (`envelope_follower_bom.xml`) |
| **PCB Footprints** | `83` | `80` netlist footprints + `3` bare-copper `B.Cu` fiducials (`FID1`–`FID3`) |
| **Active Signal / Power Nets** | `48` | `+12V`, `-12V`, `GND`, plus `45` named signal/power nets (`NET_*`) |
| **JLCPCB Bottom PCBA (`jlcpcb_bom.csv`)** | `50` parts (`17` rows) | `14` **Basic** SKUs (`33` parts, `` `$0` `` feeder fees) + **`3` Extended** SKUs (`17` parts, `` `$9` `` feeder fees total) |
| **Manual Through-Hole (`Manual THT`)** | `18` parts (`14` rows in `ibom.html`) | `11` `F.Cu` panel controls (`RV1`–`RV4`, `SW1`–`SW2`, `LED1`, `J1`–`J4`) + `7` `B.Cu` parts (`C1`, `C2`, `C7`, `C11`–`C13`, `J_PWR`) |
| **Do-Not-Populate (`DNP THT`)** | `12` parts | `TP1`–`TP12` (`TestPoint_Keystone_5000-5004_Miniature` on `B.Cu`; bare test pads exposed even unstuffed) |

---

## Complete Bill of Materials (`80` Netlist Parts + `3` Fiducials)

### 1. Op-Amps (`U1`–`U2`) & Diodes (`D1`–`D5`, `LED1`) — `8` Parts

| RefDes | Qty | Value | Package / KiCad Footprint | MPN | Manufacturer | LCSC # | Class | Role in Circuit |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| `U1`, `U2` | 2 | `TL074HIDR` | `Package_SO:SOIC-14_3.9x8.7mm_P1.27mm` | `TL074HIDR` | Texas Instruments | **`C2878713`** | **Extended** | Quad JFET-input op-amps (`U1A`–`U1D`, `U2A`–`U2D`) |
| `D1`, `D2` | 2 | `B5819W` | `Diode_SMD:D_SOD-123` | `B5819W SL` | CJ | `C8598` | Basic | `+12V` (`D1`) & `-12V` (`D2`) reverse-polarity Schottky protection |
| `D3` | 1 | `BAT54S` | `Package_TO_SOT_SMD:SOT-23` | `BAT54S` | ST(Semtech) | **`C83935`** | **Extended** | Dual-series Schottky inside `U1B` precision half-wave rectifier (`1=A1`, `2=K2`, `3=K1/A2`) |
| `D4`, `D5` | 2 | `1N4148W` | `Diode_SMD:D_SOD-123` | `1N4148W` | ST(Semtech) | `C81598` | Basic | Low-leakage silicon attack (`D4`) & release (`D5`) steering diodes |
| `LED1` | 1 | `A-1076` | `LED_THT:LED_D3.0mm` | `A-1076` | Tayda | — | Manual THT | `3 mm` 2-pin anti-parallel Red/Green bipolar envelope LED (test polarity before soldering) |

### 2. Capacitors (`C1`–`C16`) — `16` Parts (`10` SMD + `6` Manual THT)

| RefDes | Qty | Value | Package / KiCad Footprint | MPN | Manufacturer | LCSC # | Class | Role in Circuit |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| `C1`, `C2` | 2 | `47uF 35V` | `Capacitor_THT:CP_Radial_D6.3mm_P2.50mm` | `A-7257` | Tayda | — | Manual THT | Bipolar rail bulk reservoirs (`C1` `+` -> `+12V`; `C2` `+` -> `GND`) |
| `C3`–`C6` | 4 | `100nF` | `Capacitor_SMD:C_0603_1608Metric` | `CC0603KRX7R9BB104` | YAGEO | `C14663` | Basic | Local ceramic decoupling (`U1` & `U2` pins `4` and `11`) |
| `C7`, `C11` | 2 | `470nF` | `Capacitor_THT:C_Rect_L7.2mm_W4.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2` | `WIMA MKS2 470nF 63V` | WIMA | — | Manual THT | `C7`: input AC coupling (`3.39 Hz` HPF); `C11`: `FAST` timing cap (`470 nF`) |
| `C8` | 1 | `33pF` | `Capacitor_SMD:C_0603_1608Metric` | `CL10C330JB8NNNC` | Samsung | `C1663` | Basic | `U1A` feedback stabilization (`~482 kHz` pole across `R6`) |
| `C9`, `C15`, `C16` | 3 | `10uF` | `Capacitor_SMD:C_1206_3216Metric` | `CL31A106KBHNNNE` | Samsung | `C13585` | Basic | `C9`: `U1A` `1.59 Hz` DC-gain block; `C15`/`C16`: `±12V` `OFFSET` RC filters |
| `C10` | 1 | `2.2nF` | `Capacitor_SMD:C_0805_2012Metric` | `CL21C222JBFNNNE` | Samsung | `C28260` | Basic | `U1D` skew-limiter loop compensation (`2.2 nF` C0G/NP0, `> 90°` phase margin) |
| `C12`, `C13` | 2 | `2.2uF` | `Capacitor_THT:C_Rect_L7.2mm_W7.2mm_P5.00mm_FKS2_FKP2_MKS2_MKP2` | `WIMA MKS2 2.2uF 50V` | WIMA | — | Manual THT | `SLOW` timing bank extension (`+4.40 µF` -> `4.87 µF` total via `SW2`) |
| `C14` | 1 | `220nF` | `Capacitor_SMD:C_0805_2012Metric` | `CL21B224KBFNNNE` | Samsung | `C5378` | Basic | Switchable `SMOOTH` `29.0 Hz` `2f` ripple T-filter capacitor (`SW1`) |

### 3. Resistors (`R1`–`R33`) — `33` SMD Parts (`0603`, `19` Basic + `14` Extended)

| RefDes | Qty | Value | Package / KiCad Footprint | MPN | Manufacturer | LCSC # | Class | Role in Circuit |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| `R1`, `R2` | 2 | `10R` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF100JT5E` | UNI-ROYAL | `C22859` | Basic | `+12V` (`R1`) and `-12V` (`R2`) RC power-rail damping |
| `R3`, `R5`, `R16` | 3 | `1M` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1004T5E` | UNI-ROYAL | `C22935` | Basic | High-Z DC bias paths (`J1.T` bleed, `U1A.+` bias, `J2` `SLEW IN` pulldown) |
| `R4`, `R6`–`R14`, `R17`–`R18`, `R30`–`R31` | 14 | `10k 0.1%` | `Resistor_SMD:R_0603_1608Metric` | `RT0603BRD0710KL` | YAGEO | **`C95204`** | **Extended** | Preamp (`R4`,`R6`,`R7`), `0.1%` FWR (`R8`–`R14`), slew loop (`R17`–`R18`), unity inv (`R30`–`R31`) |
| `R15`, `R19`, `R20`, `R25`, `R26`, `R28`, `R32` | 7 | `1k` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1001T5E` | UNI-ROYAL | `C21190` | Basic | `SLEW IN` normal (`R15`), `ATK`/`REL` safety floors (`R19`/`R20`), `OFFSET` RC (`R26`/`R28`), jack out prot (`R25`/`R32`) |
| `R21`, `R22` | 2 | `49.9k` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF4992T5E` | UNI-ROYAL | `C23184` | Basic | `SMOOTH` T-filter legs (`2× 49.9 kΩ = 99.8 kΩ`) |
| `R23`, `R24` | 2 | `100k` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1003T5E` | UNI-ROYAL | `C25803` | Basic | `U2B` virtual-ground offset summing input (`R23`) & feedback (`R24`) |
| `R27`, `R29` | 2 | `5.1k` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF5101T5E` | UNI-ROYAL | `C23186` | Basic | `RV4` (`OFFSET`) `±4.98 V` bipolar divider range resistors |
| `R33` | 1 | `2.2k` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF2201T5E` | UNI-ROYAL | `C4190` | Basic | `U2D` in-loop precision LED current-sense resistor (`I = V_out / 2.2 kΩ`) |

### 4. Controls, Connectors, DNP Test Points & Fiducials — `23` Netlist Parts + `3` PCB Fiducials

| RefDes | Qty | Value | KiCad Footprint | MPN | Manufacturer | LCSC # | Class | Notes |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| `RV1` | 1 | `A100K` | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | `RD901F-40-15R1-A100K` | Alpha (Tayda A-1855) | — | Manual THT | `GAIN` input attenuator (`F.Cu`) |
| `RV2`, `RV3` | 2 | `A1M` | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | `RD901F-40-15R1-A1M` | Alpha (Tayda A-1672) | — | Manual THT | `ATK` (`RV2`) & `REL` (`RV3`) fail-safe rheostats (`F.Cu`) |
| `RV4` | 1 | `B10K` | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | `RD901F-40-15R1-B10K-0CD` | Alpha (Tayda A-8401) | — | Manual THT | `OFFSET` center-detent linear pot (`F.Cu`) |
| `SW1`, `SW2` | 2 | `SMOOTH` / `FAST/SLOW` | `Eurorack_Custom:SW_Toggle_SPDT_Dailywell_2MS1` | `2MS1T1B1M2QES` | Dailywell (Tayda A-6087) | — | Manual THT | `5.2 mm` M5 panel drill; `SW1`=`SMOOTH`, `SW2`=`FAST/SLOW` (`F.Cu`) |
| `J1`–`J4` | 4 | `IN`, `SLEW IN`, `OUT`, `INV_OUT` | `Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | `WQP-PJ398SM` | QingPu | — | Manual THT | `J1.TN → GND`; `J2.TN` normalled to FWR; `J3`/`J4.TN = NC` (`F.Cu`) |
| `J_PWR` | 1 | `EURORACK_PWR` | `Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical` | `IDC 2x5P 2.54mm Shrouded` | Tayda | — | Manual THT | `B.Cu` keyed header (`Pins 1,2 = -12V`, `9,10 = +12V`) |
| `TP1`–`TP12` | 12 | `GND`, `+12V`, `-12V`, `PRE`, `RECT`, `ENV`, `INV`, `OUT`, `HWR`, `DRV`, `OFF`, `GND2` | `TestPoint:TestPoint_Keystone_5000-5004_Miniature` | `RH-5001` | Ronghe | `C5199801` | **DNP THT** | `B.Cu` bench probe loops (`DNP` in BOM/CPL) |
| `FID1`–`FID3` | 3 | *(PCB only)* | `Fiducial:Fiducial_1mm_Mask2mm` | — | — | — | Optical Align | Added on `B.Cu` by `generate_kicad_pcb.py` (`(6.80, 2.25)`, `(27.50, 72.00)`, `(26.45, 105.50)`) |

---

## Verbatim `jlcpcb_bom.csv` (`17` SMD Rows, `50` Parts)

Upload this exact file with [`manufacturing/jlcpcb_cpl.csv`](../tutorial/stage-7-manufacturing.md#step-71-dual-board-manufacturing-exports-gerbercpl-verification) for JLCPCB Bottom-Side Economic PCBA:

```csv
Comment,Designator,Footprint,LCSC Part #
100nF,"C3, C4, C5, C6",C_0603_1608Metric,C14663
33pF,C8,C_0603_1608Metric,C1663
10uF,"C9, C15, C16",C_1206_3216Metric,C13585
2.2nF,C10,C_0805_2012Metric,C28260
220nF,C14,C_0805_2012Metric,C5378
B5819W,"D1, D2",D_SOD-123,C8598
BAT54S,D3,SOT-23,C83935
1N4148W,"D4, D5",D_SOD-123,C81598
10R,"R1, R2",R_0603_1608Metric,C22859
1M,"R3, R5, R16",R_0603_1608Metric,C22935
10k 0.1%,"R4, R6, R7, R8, R9, R10, R11, R12, R13, R14, R17, R18, R30, R31",R_0603_1608Metric,C95204
1k,"R15, R19, R20, R25, R26, R28, R32",R_0603_1608Metric,C21190
49.9k,"R21, R22",R_0603_1608Metric,C23184
100k,"R23, R24",R_0603_1608Metric,C25803
5.1k,"R27, R29",R_0603_1608Metric,C23186
2.2k,R33,R_0603_1608Metric,C4190
TL074HIDR,"U1, U2",SOIC-14_3.9x8.7mm_P1.27mm,C2878713
```

---

## Complete `48`-Net Connectivity Table

Extracted directly from `reference/envelope_follower_bom.xml`. Pin notes for custom/polarized parts: `SW1`/`SW2` common is Pin `2` and thrown position is Pin `3` (`Pin 1 = NC`); `D1`/`D2`/`D4`/`D5` Pin `1` = Cathode (`K`), Pin `2` = Anode (`A`); `D3` (`BAT54S`) `1` = `A1`, `2` = `K2`, `3` = `K1/A2`; `C1`/`C2` Pin `1` = `+`, Pin `2` = `-`; `LED1` Pin `1` (`+` on silkscreen) = `NET_LED_DRV`, Pin `2` = `NET_LED_SENSE`.

| # | Net Name | Connected Nodes `(Ref.Pin)` |
| :---: | :--- | :--- |
| 1 | `+12V` | `C1.1`, `C3.1`, `C5.1`, `R1.2`, `R26.1`, `TP2.1`, `U1.4`, `U2.4` |
| 2 | `-12V` | `C2.2`, `C4.1`, `C6.1`, `R2.2`, `R28.1`, `TP3.1`, `U1.11`, `U2.11` |
| 3 | `GND` | `C1.2`, `C2.1`, `C3.2`, `C4.2`, `C5.2`, `C6.2`, `C9.2`, `C11.2`, `C12.2`, `C13.2`, `C14.2`, `C15.2`, `C16.2`, `J1.S`, `J1.TN`, `J2.S`, `J3.S`, `J4.S`, `J_PWR.3`, `J_PWR.4`, `J_PWR.5`, `J_PWR.6`, `J_PWR.7`, `J_PWR.8`, `R3.2`, `R5.2`, `R16.2`, `R33.2`, `RV1.1`, `TP1.1`, `TP12.1`, `U1.10`, `U1.5`, `U2.10`, `U2.5` |
| 4 | `NET_ATK_DIODE` | `D4.1`, `R19.1` |
| 5 | `NET_ATK_MIN` | `R19.2`, `RV2.1` |
| 6 | `NET_ENV_BUF` | `R18.1`, `R21.1`, `TP6.1`, `U2.1`, `U2.2` |
| 7 | `NET_ENV_CAP` | `C11.1`, `RV2.2`, `RV2.3`, `RV3.2`, `RV3.3`, `SW2.2`, `U2.3` |
| 8 | `NET_FF_MID` | `R11.2`, `R12.1` |
| 9 | `NET_FWR_FB_MID` | `R13.2`, `R14.1` |
| 10 | `NET_GAIN_WIPER` | `R4.1`, `RV1.2` |
| 11 | `NET_INV_AMP` | `R24.2`, `R25.1`, `R30.1`, `TP7.1`, `U2.7` |
| 12 | `NET_INV_OUT_JACK` | `J4.T`, `R25.2` |
| 13 | `NET_IN_AC` | `C7.2`, `RV1.3` |
| 14 | `NET_IN_JACK` | `C7.1`, `J1.T`, `R3.1` |
| 15 | `NET_LED_DRV` | `LED1.1`, `U2.14` |
| 16 | `NET_LED_SENSE` | `LED1.2`, `R33.1`, `U2.13` |
| 17 | `NET_NEG_PROT` | `D2.2`, `R2.1` |
| 18 | `NET_OFF_BOT` | `R29.2`, `RV4.1` |
| 19 | `NET_OFF_NEG_FILT` | `C16.1`, `R28.2`, `R29.1` |
| 20 | `NET_OFF_POS_FILT` | `C15.1`, `R26.2`, `R27.1` |
| 21 | `NET_OFF_TOP` | `R27.2`, `RV4.3` |
| 22 | `NET_OFF_WIPER` | `R23.1`, `RV4.2`, `TP11.1` |
| 23 | `NET_OUT_AMP` | `R31.2`, `R32.1`, `TP8.1`, `U2.12`, `U2.8` |
| 24 | `NET_OUT_JACK` | `J3.T`, `R32.2` |
| 25 | `NET_POS_PROT` | `D1.1`, `R1.1` |
| 26 | `NET_PREAMP_OUT` | `C8.2`, `R6.2`, `R8.1`, `R11.1`, `TP4.1`, `U1.1` |
| 27 | `NET_PWR_NEG_RAW` | `D2.1`, `J_PWR.1`, `J_PWR.2` |
| 28 | `NET_PWR_POS_RAW` | `D1.2`, `J_PWR.10`, `J_PWR.9` |
| 29 | `NET_RECT_HALF` | `D3.1`, `R9.2`, `R10.1`, `TP9.1` |
| 30 | `NET_RECT_OUT` | `R14.2`, `R15.1`, `TP5.1`, `U1.8` |
| 31 | `NET_RECT_SUM` | `R10.2`, `R12.2`, `R13.1`, `U1.9` |
| 32 | `NET_REL_DIODE` | `D5.2`, `R20.1` |
| 33 | `NET_REL_MIN` | `R20.2`, `RV3.1` |
| 34 | `NET_SLEW_JACK` | `J2.T`, `R16.1`, `R17.1` |
| 35 | `NET_SLEW_NORM` | `J2.TN`, `R15.2` |
| 36 | `NET_SLOW_CAPS` | `C12.1`, `C13.1`, `SW2.3` |
| 37 | `NET_SMOOTH_MID` | `R21.2`, `R22.1`, `SW1.2` |
| 38 | `NET_SMOOTH_SW` | `C14.1`, `SW1.3` |
| 39 | `NET_U1A_CG` | `C9.1`, `R7.2` |
| 40 | `NET_U1A_INV` | `C8.1`, `R6.1`, `R7.1`, `U1.2` |
| 41 | `NET_U1A_POS` | `R4.2`, `R5.1`, `U1.3` |
| 42 | `NET_U1B_INV` | `D3.2`, `R8.2`, `R9.1`, `U1.6` |
| 43 | `NET_U1B_OUT` | `D3.3`, `U1.7` |
| 44 | `NET_U1D_INV` | `C10.1`, `R18.2`, `U1.13` |
| 45 | `NET_U1D_OUT` | `C10.2`, `D4.2`, `D5.1`, `TP10.1`, `U1.14` |
| 46 | `NET_U1D_POS` | `R17.2`, `U1.12` |
| 47 | `NET_U2B_INV` | `R22.2`, `R23.2`, `R24.1`, `U2.6` |
| 48 | `NET_U2C_INV` | `R30.2`, `R31.1`, `U2.9` |

*No-connect pins (`NC`): `SW1.1`, `SW2.1`, `J3.TN`, and `J4.TN` carry explicit `no_connect` flags in KiCad ERC.*

---

## `9`-Section Manual KiCad Schematic Capture Checklist

Use this checklist when reconstructing or auditing `envelope_follower.kicad_sch` (structured cleanly in A3 landscape matching `generate_schematic.py`):

- [ ] **Section 1 — Input & ×2 Preamp (`U1A`)**: `J1` (`IN`, `J1.TN → GND`, `J1.S → GND`), `R3` (`1 MΩ` bleed to `GND`), `C7` (`470 nF` WIMA film), `RV1` (`GAIN`, `A100K`, `.1 = GND`, `.3 = NET_IN_AC`), `R4` (`10 kΩ 0.1%`), `R5` (`1 MΩ`), `U1A` (pins `1/2/3`), `R6`/`R7` (`10 kΩ 0.1%`), `C8` (`33 pF`), `C9` (`10 µF` to `GND`).
- [ ] **Section 2 — Precision Full-Wave Rectifier (`U1B`, `U1C`, `D3`)**: `R8`–`R14` (`7× 10 kΩ ±0.1%`), `D3` (`BAT54S` inside `U1B` feedback loop with `R9` clamping half-wave at `NET_RECT_HALF`), `U1C` differential/inverting summer (`R11+R12` feedforward `20 kΩ` + `R10` `10 kΩ` half-wave + `R13+R14` `20 kΩ` feedback -> `NET_RECT_OUT`).
- [ ] **Section 3 — Power Supply & IC Decoupling (`J_PWR`, `U1E`, `U2E`)**: `J_PWR` (`2×5` shrouded `2.54 mm`), `D1`/`D2` (`B5819W`), `R1`/`R2` (`10 Ω`), `C1`/`C2` (`47 µF / 35 V` — verify `C2.1` `+` -> `GND`), `U1E`/`U2E` power units (`+12V`/`-12V`), local ceramic bypasses `C3`–`C6` (`100 nF`).
- [ ] **Section 4 — `SLEW IN` & Active Skew Limiter (`J2`, `U1D`, `D4/D5`, `RV2/RV3`, `SW2`, `U2A`)**: `R15` (`1 kΩ`) normalled from `NET_RECT_OUT` into `J2.TN`; `R16` (`1 MΩ` to `GND`) + `R17` (`10 kΩ`) into `U1D.+`; `C10` (`2.2 nF`) local loop compensation across `U1D`; `D4` (`1N4148W`) + `R19` (`1 kΩ`) + `RV2` (`A1M` `ATK`); `D5` (`1N4148W`) + `R20` (`1 kΩ`) + `RV3` (`A1M` `REL`); timing bank `C11` (`470 nF`) + `SW2` (`Pin 2 = NET_ENV_CAP`, `Pin 3 = NET_SLOW_CAPS` -> `C12` `2.2 µF` || `C13` `2.2 µF`, `Pin 1 = NC`); unity buffer `U2A` with feedback `R18` (`10 kΩ 0.1%`).
- [ ] **Section 5 — `SMOOTH` T-Filter (`SW1`)**: Split `R21` (`49.9 kΩ`) + `R22` (`49.9 kΩ`) from `NET_ENV_BUF` to `NET_U2B_INV`, center node `NET_SMOOTH_MID` -> `SW1.2`, switched leg `SW1.3` -> `C14` (`220 nF` to `GND`), `SW1.1 = NC`.
- [ ] **Section 6 — Output Summer (`U2B`) & Unity Inverter (`U2C`)**: `R23` (`100 kΩ` from `NET_OFF_WIPER`) + `R22` feeding `U2B.-`, `R24` (`100 kΩ` feedback -> `NET_INV_AMP`), `R25` (`1 kΩ`) -> `J4` (`INV_OUT`); `R30`/`R31` (`10 kΩ ±0.1%`) around `U2C` -> `NET_OUT_AMP`, `R32` (`1 kΩ`) -> `J3` (`OUT`, `J3.TN`/`J4.TN = NC`).
- [ ] **Section 7 — RC-Filtered `OFFSET` Bias (`RV4`)**: `+12V` -> `R26` (`1 kΩ`) + `C15` (`10 µF`) -> `R27` (`5.1 kΩ`) -> `RV4.3`; `-12V` -> `R28` (`1 kΩ`) + `C16` (`10 µF`) -> `R29` (`5.1 kΩ`) -> `RV4.1`; wiper `RV4.2` -> `NET_OFF_WIPER`.
- [ ] **Section 8 — Active Bi-Color LED Driver (`U2D`)**: `NET_OUT_AMP` -> `U2D.12` (`+`), `U2D.14` -> `LED1.1`, `LED1.2` (`NET_LED_SENSE`) -> `U2D.13` (`-`) & `R33` (`2.2 kΩ` to `GND`).
- [ ] **Section 9 — DNP Test Points (`TP1`–`TP12`, `B.Cu`, `RH-5001`)**: Wire all `12` test points (`TP1`=`GND`, `TP2`=`+12V`, `TP3`=`-12V`, `TP4`=`PRE`, `TP5`=`RECT`, `TP6`=`ENV`, `TP7`=`INV`, `TP8`=`OUT`, `TP9`=`HWR`, `TP10`=`DRV`, `TP11`=`OFF`, `TP12`=`GND2`) with `DNP` flags set.

---

## Pinned Silkscreen Schedule (`silk_layout.json`)

Board-local coordinates relative to `(BOARD_X0 = 100.0, BOARD_Y0 = 40.0 mm)` on a `30.0 × 108.0 mm` PCB (from [`reference/silk_layout.json`](https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/blob/main/silk_layout.json)). Managed dynamically via `/edit-silkscreen` and `generate_kicad_pcb.py --sync-silk` / `--check-silk`:

### Board-Level Primitives, Dots & Banners (`F.SilkS` / `B.SilkS`)

| Type | Layer | Content / Dimensions | Board-Local `(X, Y)` mm | Rot (deg) | Size / Stroke |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **QR Square** | `F.SilkS` | `5.0 × 5.0 mm` filled `gr_rect` | `(23.80, 1.00)`..`(28.80, 6.00)` | `0` | Solid fill, `0.15 mm` edge |
| **`-12V` Stripe** | `F.SilkS` | Heavy polarity bar beside `J_PWR` | `(22.50, 19.95)` -> `(26.54, 19.95)` | `0` | `0.80 mm` segment width |
| **Board Title** | `F.SilkS` | `6HP REV 1.0` | `(28.55, 26.879)` | `90` | `h = 0.80 mm`, `t = 0.15 mm` |
| **Board Subtitle** | `F.SilkS` | `ENV FOLLOWER` | `(28.55, 36.512)` | `90` | `h = 0.80 mm`, `t = 0.15 mm` |
| **Repo Name** | `F.SilkS` | `EnvelopeFollowerWithSkewLimiter` | `(15.931, 87.95)` | `90` | `h = 0.80 mm`, `t = 0.15 mm` |
| **Repo Author** | `F.SilkS` | `github.com/domesticmouse/` | `(14.069, 89.112)` | `90` | `h = 0.80 mm`, `t = 0.15 mm` |
| **`U1` Pin 1 Dot** | `B.SilkS` | Filled circular marker (`r = 0.25 mm`) | `(11.075, 87.31)` | `0` | Bottom-right in bottom view |
| **`U2` Pin 1 Dot** | `B.SilkS` | Filled circular marker (`r = 0.25 mm`) | `(18.925, 94.69)` | `0` | Top-left in bottom view |

### Footprint Silkscreen Groups (`80` Entries, `0.80 mm` Height / `0.15 mm` Stroke)

- **`F.Cu` Controls (Show `Ref` + Value/Function on `F.SilkS` at `90°` along board edges):**
  - `RV1`–`RV4` along left column `X = 5.40 mm`: `RV1` (`GAIN A100K`), `RV2` (`ATK A1M`), `RV3` (`REL A1M`), `RV4` (`OFFSET B10K`).
  - `SW1` left toggle (`X = 2.80 mm`, `SMOOTH`); `SW2` right toggle (`X = 27.20 mm`, `FAST/SLOW`).
  - `J1`–`J4` jacks: `J1` (`IN`, `X = 1.85 mm`), `J2` (`SLEW IN`, `X = 28.15 mm`), `J3` (`OUT`, `X = 1.85 mm`), `J4` (`INV_OUT`, `X = 28.15 mm`).
  - `LED1` dual-annotated around lens: `LED1` + `OUT` above (`Y = 66.60`), `2-PIN R/G` (`Y = 68.40`), `TAYDA A-1076` (`Y = 75.45`), and `+` polarity marks on **both `F.SilkS`** (`11.70, 72.00`) and **`B.SilkS`** (`13.73, 69.85`).
- **`B.Cu` Active ICs (`U1`, `U2`):** Print both `Ref` and `TL074H` on `B.SilkS` (`U1` horiz at `Y = 89.20`; `U2` rot `90°` at `X = 10.50`).
- **`J_PWR` Header:** `PWR` on `B.SilkS` (`24.52, 1.40`) and `-12V` on `F.SilkS` (`24.52, 21.48`).
- **`DNP` Test Points (`TP1`–`TP12`):** Dual-sided labels (`GND`, `+12V`, `-12V`, `PRE`, `RECT`, `ENV`, `INV`, `OUT`, `HWR`, `DRV`, `OFF`, `GND2`) printed on **both `F.SilkS` and `B.SilkS`** (`ref: null`).
- **`50` SMDs (`R1`–`R33`, `C3`–`C10`, `C14`–`C16`, `D1`–`D5`) & `6` `B.Cu` THT Film/Electrolytics (`C1`, `C2`, `C7`, `C11`–`C13`):** Suppress `Ref` (`ref: null`) on dense `B.Cu` corridors and print only concise engineering values (`10k`, `100nF`, `BAT54S`, `47uF`, `470nF`, `2.2uF`, etc.) on `B.SilkS`, while leaving full Reference Designators on `B.Fab` (verified visually via generated PDF).
