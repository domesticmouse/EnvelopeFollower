# Envelope Follower (Improved Eurorack Revision) — Bill of Materials (BOM)

Live-verified JLCPCB/LCSC Bill of Materials for [`EnvelopeFollowerImproved.md`](./EnvelopeFollowerImproved.md). Every SMT component and LCSC-stockable THT component below was verified against JLCPCB's live catalog (`jlcpcb_search.py`) on **2026-11-20** with stock, pricing, package, and Basic/Extended library status confirmed.

---

## 1. JLCPCB SMT Assembly BOM (53 SMD Components, 20 Unique Lines)

These components are surface-mount (`SMT`) and placed automatically by JLCPCB PCBA.

| Qty | Designators | Value / Comment | MPN | Manufacturer | Package / KiCad Footprint | LCSC Part # | JLCPCB Class | Live Stock | Unit Price (USD) | Ext. Price (USD) | Specifications / Role |
|---:|---|---|---|---|---|---|---|---:|---:|---:|---|
| **2** | `U1, U2` | `TL074HIDR` | `TL074HIDR` | Texas Instruments | `SOIC-14` (`Package_SO:SOIC-14_3.9x8.7mm_P1.27mm`) | `C2878713` | **Extended** | 469 | $0.2559 | $0.5118 | Quad 40V JFET/CMOS-input op-amp, `5.25 MHz`, `20 V/µs`, `1 mV` typ `V_os` |
| **2** | `D4, D5` | `B5819W` | `B5819W SL` | Jiangsu Changjing | `SOD-123` (`Diode_SMD:D_SOD-123`) | `C8598` | **Basic** | 852,546 | $0.0251 | $0.0502 | `40 V / 1 A` Schottky reverse-polarity power diodes |
| **5** | `D1, D2, D3, D9, D10` | `1N4148W` | `1N4148W` | ST (Semtech) | `SOD-123` (`Diode_SMD:D_SOD-123`) | `C81598` | **Basic** | 2,912,346 | $0.0124 | $0.0620 | `75 V / 150 mA / 4 ns` switching diodes (FWR, peak det, clamps) |
| **1** | `D6` | `BAV99` | `BAV99,215` | Nexperia | `SOT-23` (`Package_TO_SOT_SMD:SOT-23`) | `C2500` | **Basic** | 1,621,836 | $0.0108 | $0.0108 | `100 V / 125 mA` dual series clamp (`IN_CLAMP` to `±12V`) |
| **2** | `D7, D8` | `BAT54S` | `BAT54S,215` | Nexperia | `SOT-23` (`Package_TO_SOT_SMD:SOT-23`) | `C47546` | **Extended** | 432,349 | $0.0200 | $0.0400 | `30 V / 200 mA` dual series Schottky output clamps (`OUT`, `INV_OUT`) |
| **4** | `C3, C4, C11, C13` | `22uF 50V` | `RVT1H220M0605` | DMBJ | `SMD,D6.3xL5.4mm` (`Capacitor_SMD:CP_Elec_6.3x5.4`) | `C970664` | **Extended** | 8,154 | $0.0418 | $0.1672 | `22 µF 50 V ±20%` SMD aluminum electrolytic (`5.4 mm` height) |
| **7** | `C5, C6, C7, C8, C12, C14, C15` | `100nF 50V` | `CC0603KRX7R9BB104` | YAGEO | `0603` (`Capacitor_SMD:C_0603_1608Metric`) | `C14663` | **Basic** | 53,956,915 | $0.0060 | $0.0420 | `100 nF 50 V X7R ±10%` local IC & `OFFSET` HF bypass |
| **2** | `C10, C17` | `15pF 50V` | `CL10C150JB8NNNC` | Samsung Electro-Mechanics | `0603` (`Capacitor_SMD:C_0603_1608Metric`) | `C1644` | **Basic** | 967,509 | $0.0111 | $0.0222 | `15 pF 50 V C0G ±5%` `U1A` & `U1C` feedback stability comp |
| **1** | `C16` | `47pF 50V` | `CL10C470JB8NNNC` | Samsung Electro-Mechanics | `0603` (`Capacitor_SMD:C_0603_1608Metric`) | `C1671` | **Basic** | 650,065 | $0.0063 | $0.0063 | `47 pF 50 V C0G ±5%` `U2C` active peak-detector lead comp |
| **8** | `R2, R13, R14, R15, R17, R18, R20, R27` | `10k` | `0603WAF1002T5E` | UNI-ROYAL | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C25804` | **Basic** | 42,570,991 | $0.0017 | $0.0136 | `10 kΩ ±1% 100 mW` thick film |
| **3** | `R11, R12, R28` | `1k` | `0603WAF1001T5E` | UNI-ROYAL | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C21190` | **Basic** | 30,422,775 | $0.0016 | $0.0048 | `1 kΩ ±1% 100 mW` thick film (`OFFSET` RC & `U1A+` clamp limit) |
| **2** | `R1, R26` | `1M` | `0603WAF1004T5E` | UNI-ROYAL | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C22935` | **Basic** | 5,141,884 | $0.0018 | $0.0036 | `1 MΩ ±1% 100 mW` thick film (bleed/reference resistors) |
| **1** | `R29` | `100k` | `0603WAF1003T5E` | UNI-ROYAL | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C25803` | **Basic** | 13,359,999 | $0.0029 | $0.0029 | `100 kΩ ±1% 100 mW` thick film (`U1A` `11×` feedback) |
| **1** | `R24` | `4.7k` | `0603WAF4701T5E` | UNI-ROYAL | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C23162` | **Basic** | 15,758,065 | $0.0028 | $0.0028 | `4.7 kΩ ±1% 100 mW` thick film (`GAIN` floor resistor) |
| **1** | `R9` | `470R` | `0603WAF4700T5E` | UNI-ROYAL | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C23179` | **Basic** | 4,182,512 | $0.0019 | $0.0019 | `470 Ω ±1% 100 mW` thick film (pre-`C2` attack surge limit) |
| **1** | `R10` | `22k` | `0603WAF2202T5E` | UNI-ROYAL | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C31850` | **Basic** | 2,245,153 | $0.0042 | $0.0042 | `22 kΩ ±1% 100 mW` thick film (`Release` minimum resistor) |
| **1** | `R21` | `1.5k` | `0603WAF1501T5E` | UNI-ROYAL | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C22843` | **Basic** | 2,756,332 | $0.0020 | $0.0020 | `1.5 kΩ ±1% 100 mW` thick film (`LED1` V-to-I `R_set`) |
| **5** | `R3, R4, R5, R6, R7` | `100k 0.1%` | `RT0603BRD07100KL` | YAGEO | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C122538` | **Extended** | 1,668,112 | $0.0221 | $0.1105 | `100 kΩ ±0.1% ±25ppm/°C` thin film (precision FWR network) |
| **1** | `R8` | `200k 0.1%` | `RT0603BRE07200KL` | YAGEO | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C136955` | **Extended** | 13,557 | $0.0307 | $0.0307 | `200 kΩ ±0.1% ±50ppm/°C` thin film (`1.000×` FWR feedback) |
| **3** | `R16, R19, R25` | `1k 1W` | `25121WF1001T4E` | UNI-ROYAL | `2512` (`Resistor_SMD:R_2512_6332Metric`) | `C54315` | **Extended** | 53,313 | $0.0336 | $0.1008 | `1 kΩ ±1% 1 W` `200 V` fault-rated `IN`/`OUT`/`INV_OUT` protection |

*Verified SMD Substitutes / Cost-Down Notes:*
- `D1, D2, D3, D9, D10`: `1N4148WS` (`C2128`, Changjing, `SOD-323`, **Basic**, stock `3,383,196`, `$0.0100`) is a smaller-footprint `100 V` Basic alternative.
- `C3, C4, C11, C13`: `RVT1H470M0607` (`C970679`, `47 µF 50 V`, `6.3×7.7 mm`, Extended, stock `32,485`, `$0.0374`) or `RVT1V470M0605` (`C970678`, `47 µF 35 V`, `6.3×5.4 mm`, Extended, stock `12,865`, `$0.0346`) are verified drop-in electrolytic alternates.
- `R8`: Using `2× RT0603BRD07100KL` (`C122538`) in series gives `200 kΩ ±0.1%` and eliminates the `$3.00` Extended feeder fee for `C136955`.

---

## 2. Through-Hole (THT) Parts — Mounted Later / User-Sourced (12 Components, 9 Unique Lines)

Per build requirements, panel hardware, the IDC power header, and the 3 mm LED are THT parts mounted manually after SMT assembly. In addition, JLCPCB carries `0` SMT stock of `470 nF–1 µF` film or high-value `C0G` capacitors (`1uF C0G`, `470nF C0G`, `220nF C0G` all `0` stock; `ECHU` PPS tops out at `22 nF`), so `C1`, `C2`, `C9` use the stocked `WIMA MKS2` THT box film capacitor (`C92673`).

| Qty | Designators | Value / Comment | MPN | Manufacturer | Package / KiCad Footprint | LCSC Part # | Sourcing / Assembly Status | Live JLCPCB Stock | Unit Price (USD) | Notes |
|---:|---|---|---|---|---|---|---|---:|---:|---|
| **3** | `C1, C2, C9` | `1uF 63V Film` | `MKS2C041001F00JSSD` | WIMA | `Plugin,P=5mm` (`Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm`) | `C92673` | **Manual THT** *(or JLC Standard THT)* | 5,578 | $1.1443 | `1 µF 63 V ±5%` PET box film (`7.2×5.0×10.0 mm`); zero DC-bias derating |
| **1** | `J4` | `IDC 2x5 Header` | `IDC2.54-2*5PZ` | JXTCONN | `Plugin,P=2.54mm` (`Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical`) | `C53207560` | **Manual THT** (mounted later on `B.Cu`) | 2,060 | $0.1241 | Keyed/shrouded `2×5` Eurorack power header (`3 A / 250 V`) |
| **1** | `LED1` | `3mm LED Yellow` | `204-10UYD/S530-A3-L` | Everlight Elec | `Plugin,D=3mm` (`LED_THT:LED_D3.0mm`) | `C85160` | **Manual THT** (mounted later) | 40,636 | $0.0366 | `3 mm` diffused yellow (`200 mcd`, `2.0 V` `V_f`); panel-aligned |
| **3** | `J1, J2, J3` | `3.5mm Mono Jack` | `WQP-PJ398SM` | QingPu | `SW-TH` (`Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles`) | `C9900009788` *(catalog ref)* | **User-Sourced / Manual THT** | 0 | — | Thonkiconn switched 3.5 mm jack; source via Thonk / Tayda / modular suppliers |
| **1** | `RV1` | `A100k` | `RV09AF-40-15K-A100K` *(or `RD901F-40-A100K`)* | Alpha (Taiwan) | `Through-Hole 9mm` (`Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical`) | `N/A (User-Sourced)` | **User-Sourced / Manual THT** | 0 | — | `100 kΩ` audio/log taper 9 mm vertical panel pot (`GAIN`) |
| **1** | `RV2` | `A50k` | `RV09AF-40-15K-A50K` *(or `RD901F-40-A50K`)* | Alpha (Taiwan) | `Through-Hole 9mm` (`Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical`) | `N/A (User-Sourced)` | **User-Sourced / Manual THT** | 0 | — | `50 kΩ` audio/log taper 9 mm vertical panel pot (`ATK`) |
| **1** | `RV3` | `A1M` | `RV09AF-40-15K-A1M` *(or `RD901F-40-A1M`)* | Alpha (Taiwan) | `Through-Hole 9mm` (`Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical`) | `N/A (User-Sourced)` | **User-Sourced / Manual THT** | 0 | — | `1 MΩ` audio/log taper 9 mm vertical panel pot (`Release`) |
| **1** | `RV4` | `B10k` | `RV09AF-40-15K-B10K` *(or center-detent `B10K`)* | Alpha (Taiwan) | `Through-Hole 9mm` (`Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical`) | `C2839839` *(catalog ref)* | **User-Sourced / Manual THT** | 0 | — | `10 kΩ` linear taper 9 mm vertical panel pot (`OFFSET`) |

*Verified LCSC 3 mm THT LED Color Alternates:*
- Green (`204-10SYGD/S530-E3`, `2.0 V`, `100 mcd`): `C85161` (stock `37,383`, `$0.0361`)
- Red (`204-10SDRD/S530-A3-L`, `1.7–2.4 V`, `40–80 mcd`): `C84774` (stock `56,245`, `$0.0356`)
- Blue (`204-10SUBC/S400-A4`, `3.4 V`, `800 mcd` water clear): `C86881` (stock `30,878`, `$0.0444`)

---

## 3. Complete Itemized Component Reference (All 65 Parts)

| Ref | Type | Value | MPN | LCSC # | Mount / Class | Footprint | Circuit Function |
|---|---|---|---|---|---|---|---|
| `U1` | Quad Op-Amp | `TL074H` | `TL074HIDR` | `C2878713` | SMT / Extended | `SOIC-14_3.9x8.7mm_P1.27mm` | `U1A` preamp, `U1B` HWR, `U1C` FWR sum, `U1D` `OUT` inverter |
| `U2` | Quad Op-Amp | `TL074H` | `TL074HIDR` | `C2878713` | SMT / Extended | `SOIC-14_3.9x8.7mm_P1.27mm` | `U2A` `INV_OUT` summer, `U2B` LED driver, `U2C` peak det, `U2D` buffer |
| `D1` | Diode | `1N4148W` | `1N4148W` | `C81598` | SMT / Basic | `D_SOD-123` | `U1B` negative-input clamp diode |
| `D2` | Diode | `1N4148W` | `1N4148W` | `C81598` | SMT / Basic | `D_SOD-123` | `U1B` rectifier output diode |
| `D3` | Diode | `1N4148W` | `1N4148W` | `C81598` | SMT / Basic | `D_SOD-123` | Active peak-detector charging diode (`U2C`) |
| `D4` | Schottky | `B5819W` | `B5819W SL` | `C8598` | SMT / Basic | `D_SOD-123` | `+12V` reverse-polarity protection (`40 V / 1 A`) |
| `D5` | Schottky | `B5819W` | `B5819W SL` | `C8598` | SMT / Basic | `D_SOD-123` | `-12V` reverse-polarity protection (`40 V / 1 A`) |
| `D6` | Dual Diode | `BAV99` | `BAV99,215` | `C2500` | SMT / Basic | `SOT-23` | `IN_CLAMP` ESD / over-voltage clamp to `±12V` |
| `D7` | Dual Schottky | `BAT54S` | `BAT54S,215` | `C47546` | SMT / Extended | `SOT-23` | `ENV_OUT` ESD / back-feed clamp to `±12V` |
| `D8` | Dual Schottky | `BAT54S` | `BAT54S,215` | `C47546` | SMT / Extended | `SOT-23` | `INV_OUT_RAW` ESD / back-feed clamp to `±12V` |
| `D9` | Diode | `1N4148W` | `1N4148W` | `C81598` | SMT / Basic | `D_SOD-123` | `U2C` anti-saturation clamp diode |
| `D10` | Diode | `1N4148W` | `1N4148W` | `C81598` | SMT / Basic | `D_SOD-123` | Anti-parallel reverse-protection clamp across `LED1` |
| `C1` | Film Cap | `1uF 63V` | `MKS2C041001F00JSSD` | `C92673` | THT / Manual | `C_Rect_L7.2mm_W5.0mm_P5.00mm` | Input AC coupling (`f_c = 1.52 Hz`) |
| `C2` | Film Cap | `1uF 63V` | `MKS2C041001F00JSSD` | `C92673` | THT / Manual | `C_Rect_L7.2mm_W5.0mm_P5.00mm` | Envelope peak-hold integration capacitor |
| `C3` | Elec Cap | `22uF 50V` | `RVT1H220M0605` | `C970664` | SMT / Extended | `CP_Elec_6.3x5.4` | `+12V` bulk rail decoupling (`+` to `+12V`, `-` to `GND`) |
| `C4` | Elec Cap | `22uF 50V` | `RVT1H220M0605` | `C970664` | SMT / Extended | `CP_Elec_6.3x5.4` | `-12V` bulk rail decoupling (`+` to `GND`, `-` to `-12V`) |
| `C5` | MLCC | `100nF 50V` | `CC0603KRX7R9BB104` | `C14663` | SMT / Basic | `C_0603_1608Metric` | `U1` local `+12V` bypass (Pin 4 → `GND`) |
| `C6` | MLCC | `100nF 50V` | `CC0603KRX7R9BB104` | `C14663` | SMT / Basic | `C_0603_1608Metric` | `U1` local `-12V` bypass (Pin 11 → `GND`) |
| `C7` | MLCC | `100nF 50V` | `CC0603KRX7R9BB104` | `C14663` | SMT / Basic | `C_0603_1608Metric` | `U2` local `+12V` bypass (Pin 4 → `GND`) |
| `C8` | MLCC | `100nF 50V` | `CC0603KRX7R9BB104` | `C14663` | SMT / Basic | `C_0603_1608Metric` | `U2` local `-12V` bypass (Pin 11 → `GND`) |
| `C9` | Film Cap | `1uF 63V` | `MKS2C041001F00JSSD` | `C92673` | THT / Manual | `C_Rect_L7.2mm_W5.0mm_P5.00mm` | Inter-stage AC coupling before FWR (`f_c = 2.55 Hz`) |
| `C10` | MLCC C0G | `15pF 50V` | `CL10C150JB8NNNC` | `C1644` | SMT / Basic | `C_0603_1608Metric` | `U1A` feedback compensation across `R29` (`106.1 kHz`) |
| `C11` | Elec Cap | `22uF 50V` | `RVT1H220M0605` | `C970664` | SMT / Extended | `CP_Elec_6.3x5.4` | `OFFSET_TOP` RC PSU filter (`+` to `OFFSET_TOP`, `-` to `GND`) |
| `C12` | MLCC | `100nF 50V` | `CC0603KRX7R9BB104` | `C14663` | SMT / Basic | `C_0603_1608Metric` | `OFFSET_TOP` HF bypass to `GND` |
| `C13` | Elec Cap | `22uF 50V` | `RVT1H220M0605` | `C970664` | SMT / Extended | `CP_Elec_6.3x5.4` | `OFFSET_BOT` RC PSU filter (`+` to `GND`, `-` to `OFFSET_BOT`) |
| `C14` | MLCC | `100nF 50V` | `CC0603KRX7R9BB104` | `C14663` | SMT / Basic | `C_0603_1608Metric` | `OFFSET_BOT` HF bypass to `GND` |
| `C15` | MLCC | `100nF 50V` | `CC0603KRX7R9BB104` | `C14663` | SMT / Basic | `C_0603_1608Metric` | `OFFSET_WIPER` noise suppression bypass to `GND` |
| `C16` | MLCC C0G | `47pF 50V` | `CL10C470JB8NNNC` | `C1671` | SMT / Basic | `C_0603_1608Metric` | `U2C` active peak-detector lead compensation (`338 kHz`) |
| `C17` | MLCC C0G | `15pF 50V` | `CL10C150JB8NNNC` | `C1644` | SMT / Basic | `C_0603_1608Metric` | `U1C` FWR feedback compensation across `R8` (`53.1 kHz`) |
| `R1` | Resistor | `1M` | `0603WAF1004T5E` | `C22935` | SMT / Basic | `R_0603_1608Metric` | `GAIN` wiper-lift safety bleed to `GND` |
| `R2` | Resistor | `10k` | `0603WAF1002T5E` | `C25804` | SMT / Basic | `R_0603_1608Metric` | `U1A` gain shunt resistor to `GND` |
| `R3` | Thin-Film | `100k 0.1%` | `RT0603BRD07100KL` | `C122538` | SMT / Extended | `R_0603_1608Metric` | `U1B` precision half-wave input resistor |
| `R4` | Thin-Film | `100k 0.1%` | `RT0603BRD07100KL` | `C122538` | SMT / Extended | `R_0603_1608Metric` | FWR feedforward resistor 1 (`R4 + R5 = 200 kΩ`) |
| `R5` | Thin-Film | `100k 0.1%` | `RT0603BRD07100KL` | `C122538` | SMT / Extended | `R_0603_1608Metric` | FWR feedforward resistor 2 to `FWR_SUM` |
| `R6` | Thin-Film | `100k 0.1%` | `RT0603BRD07100KL` | `C122538` | SMT / Extended | `R_0603_1608Metric` | `U1B` precision half-wave feedback resistor |
| `R7` | Thin-Film | `100k 0.1%` | `RT0603BRD07100KL` | `C122538` | SMT / Extended | `R_0603_1608Metric` | Half-wave summing resistor into `U1C` |
| `R8` | Thin-Film | `200k 0.1%` | `RT0603BRE07200KL` | `C136955` | SMT / Extended | `R_0603_1608Metric` | `U1C` FWR feedback resistor (`1.000×` gain) |
| `R9` | Resistor | `470R` | `0603WAF4700T5E` | `C23179` | SMT / Basic | `R_0603_1608Metric` | Pre-`C2` attack current-limiting resistor (`D3` → `RV2`) |
| `R10` | Resistor | `22k` | `0603WAF2202T5E` | `C31850` | SMT / Basic | `R_0603_1608Metric` | Minimum release discharge resistor (`22 ms` floor) |
| `R11` | Resistor | `1k` | `0603WAF1001T5E` | `C21190` | SMT / Basic | `R_0603_1608Metric` | `OFFSET` upper rail RC filter / divider (`+12V`) |
| `R12` | Resistor | `1k` | `0603WAF1001T5E` | `C21190` | SMT / Basic | `R_0603_1608Metric` | `OFFSET` lower rail RC filter / divider (`-12V`) |
| `R13` | Resistor | `10k` | `0603WAF1002T5E` | `C25804` | SMT / Basic | `R_0603_1608Metric` | `OFFSET_WIPER` summing resistor to `U2A` (`-`) |
| `R14` | Resistor | `10k` | `0603WAF1002T5E` | `C25804` | SMT / Basic | `R_0603_1608Metric` | `U1D` (`OUT`) unity inverter input resistor |
| `R15` | Resistor | `10k` | `0603WAF1002T5E` | `C25804` | SMT / Basic | `R_0603_1608Metric` | `U1D` (`OUT`) unity inverter feedback resistor |
| `R16` | Power Res | `1k 1W` | `25121WF1001T4E` | `C54315` | SMT / Extended | `R_2512_6332Metric` | `OUT` jack fault-rated series protection resistor |
| `R17` | Resistor | `10k` | `0603WAF1002T5E` | `C25804` | SMT / Basic | `R_0603_1608Metric` | `ENV_NODE` summing resistor into `U2A` (`-`) |
| `R18` | Resistor | `10k` | `0603WAF1002T5E` | `C25804` | SMT / Basic | `R_0603_1608Metric` | `U2A` (`INV_OUT`) inverting summer feedback resistor |
| `R19` | Power Res | `1k 1W` | `25121WF1001T4E` | `C54315` | SMT / Extended | `R_2512_6332Metric` | `INV_OUT` jack fault-rated series protection resistor |
| `R20` | Resistor | `10k` | `0603WAF1002T5E` | `C25804` | SMT / Basic | `R_0603_1608Metric` | `U2B` (`+`) input isolation resistor |
| `R21` | Resistor | `1.5k` | `0603WAF1501T5E` | `C22843` | SMT / Basic | `R_0603_1608Metric` | `LED1` transconductance current-setting resistor (`I_LED = V_env / 1.5k`) |
| `R24` | Resistor | `4.7k` | `0603WAF4701T5E` | `C23162` | SMT / Basic | `R_0603_1608Metric` | `GAIN` pot floor resistor (`0.494×` min preamp gain) |
| `R25` | Power Res | `1k 1W` | `25121WF1001T4E` | `C54315` | SMT / Extended | `R_2512_6332Metric` | `IN` jack series surge / ESD limiting resistor |
| `R26` | Resistor | `1M` | `0603WAF1004T5E` | `C22935` | SMT / Basic | `R_0603_1608Metric` | `AC_PRE` DC ground reference after `C9` |
| `R27` | Resistor | `10k` | `0603WAF1002T5E` | `C25804` | SMT / Basic | `R_0603_1608Metric` | `U2C` active peak-detector feedback (`ENV_NODE` → `DET_FB`) |
| `R28` | Resistor | `1k` | `0603WAF1001T5E` | `C21190` | SMT / Basic | `R_0603_1608Metric` | `U1A` (`+`) internal ESD clamp current limiter |
| `R29` | Resistor | `100k` | `0603WAF1003T5E` | `C25803` | SMT / Basic | `R_0603_1608Metric` | `U1A` non-inverting feedback resistor (`11.0×` stage gain) |
| `RV1` | Potentiometer | `A100k` | `RV09AF-40-15K-A100K` | `N/A (User-Sourced)` | THT / Manual | `Potentiometer_Alps_RK09K_Single_Vertical` | `GAIN` panel control (log/audio `100 kΩ`) |
| `RV2` | Potentiometer | `A50k` | `RV09AF-40-15K-A50K` | `N/A (User-Sourced)` | THT / Manual | `Potentiometer_Alps_RK09K_Single_Vertical` | `ATK` panel control (log/audio `50 kΩ`) |
| `RV3` | Potentiometer | `A1M` | `RV09AF-40-15K-A1M` | `N/A (User-Sourced)` | THT / Manual | `Potentiometer_Alps_RK09K_Single_Vertical` | `Release` panel control (log/audio `1 MΩ`) |
| `RV4` | Potentiometer | `B10k` | `RV09AF-40-15K-B10K` | `C2839839` *(ref)* | THT / Manual | `Potentiometer_Alps_RK09K_Single_Vertical` | `OFFSET` panel control (linear `10 kΩ`) |
| `LED1` | 3mm LED | `Yellow 200mcd` | `204-10UYD/S530-A3-L` | `C85160` | THT / Manual | `LED_D3.0mm` | Envelope level indicator (`2.0 V` `V_f` diffused) |
| `J1` | 3.5mm Jack | `PJ398SM` | `WQP-PJ398SM` | `C9900009788` *(ref)* | THT / Manual | `Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | `IN` signal jack (`TN → GND`) |
| `J2` | 3.5mm Jack | `PJ398SM` | `WQP-PJ398SM` | `C9900009788` *(ref)* | THT / Manual | `Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | `OUT` envelope CV jack (`TN → NC`) |
| `J3` | 3.5mm Jack | `PJ398SM` | `WQP-PJ398SM` | `C9900009788` *(ref)* | THT / Manual | `Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | `INV_OUT` inverted CV jack (`TN → NC`) |
| `J4` | IDC Header | `2x5 2.54mm` | `IDC2.54-2*5PZ` | `C53207560` | THT / Manual | `IDC-Header_2x05_P2.54mm_Vertical` | Keyed Eurorack `±12V` power header (`B.Cu`) |

*(Baseline `R22` and `R23` are intentionally removed per IMP-06 active V-to-I LED driver redesign.)*

---

## 4. JLCPCB PCBA Upload CSV (Economic SMT-Only Assembly)

Use the grouped CSV below for **JLCPCB Economic PCBA** (SMT only; omits THT parts `C1, C2, C9, J1–J4, RV1–RV4, LED1` which are mounted later). If ordering **JLCPCB Standard Assembly** with `C1, C2, C9` pre-mounted, append the `MKS2` row (`1uF 63V Film,"C1, C2, C9",C_Rect_L7.2mm_W5.0mm_P5.00mm,C92673`).

```csv
Comment,Designator,Footprint,LCSC Part #
TL074HIDR,"U1, U2",SOIC-14_3.9x8.7mm_P1.27mm,C2878713
B5819W,"D4, D5",D_SOD-123,C8598
1N4148W,"D1, D2, D3, D9, D10",D_SOD-123,C81598
BAV99,D6,SOT-23,C2500
BAT54S,"D7, D8",SOT-23,C47546
22uF 50V,"C3, C4, C11, C13",CP_Elec_6.3x5.4,C970664
100nF 50V,"C5, C6, C7, C8, C12, C14, C15",C_0603_1608Metric,C14663
15pF 50V,"C10, C17",C_0603_1608Metric,C1644
47pF 50V,C16,C_0603_1608Metric,C1671
10k,"R2, R13, R14, R15, R17, R18, R20, R27",R_0603_1608Metric,C25804
1k,"R11, R12, R28",R_0603_1608Metric,C21190
1M,"R1, R26",R_0603_1608Metric,C22935
100k,R29,R_0603_1608Metric,C25803
4.7k,R24,R_0603_1608Metric,C23162
470R,R9,R_0603_1608Metric,C23179
22k,R10,R_0603_1608Metric,C31850
1.5k,R21,R_0603_1608Metric,C22843
100k 0.1%,"R3, R4, R5, R6, R7",R_0603_1608Metric,C122538
200k 0.1%,R8,R_0603_1608Metric,C136955
1k 1W,"R16, R19, R25",R_2512_6332Metric,C54315
```

---

## 5. Assembly Cost Breakdown (5-Board Prototype Estimate)

```text
BOM Summary — Project: EnvelopeFollowerImproved (5 Boards, JLCPCB Economic SMT + Manual THT)
===========================================================================================
Unique lines:      29  (20 JLCPCB SMT [14 Basic, 6 Extended] + 9 THT mounted later)
Total components:  65  (53 JLCPCB SMT + 12 THT)

JLCPCB SMT Assembly (per board, excluding PCB fab & SMT labor):
  Basic SMT parts (14 lines, 36 pcs):     $0.2293 / board  ($0.00 feeder fees)
  Extended SMT parts (6 lines, 17 pcs):   $0.9610 / board  (+$18.00 batch feeder fee = $3.60/board @ 5 pcs)
  SMT Subtotal (5 boards):                ~$23.95 total    (~$4.79 / board incl. feeder fees)
  Tip — 2x C122538 in series for R8:      saves $3.00 feeder fee ($15.00 batch extended fee total)

LCSC-Stocked THT Parts (mounted later, per board):
  C1, C2, C9 (3x WIMA MKS2 C92673):       $3.4329 / board
  J4 (1x 2x5 IDC Header C53207560):       $0.1241 / board
  LED1 (1x 3mm Yellow LED C85160):        $0.0366 / board
  LCSC THT Subtotal:                      $3.5936 / board  ($17.97 for 5 boards)

Consigned / User-Sourced Panel Hardware (separate vendor order, per board):
  J1–J3 (3x WQP-PJ398SM Thonkiconn) + RV1–RV4 (4x 9mm pots: A100k, A50k, A1M, B10k)
```
