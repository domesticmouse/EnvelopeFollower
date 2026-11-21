# Envelope Follower (Improved) — Bill of Materials (BOM) & JLCPCB Sourcing

Complete Bill of Materials for [EnvelopeFollowerImproved.md](./EnvelopeFollowerImproved.md), partitioned for **single-sided JLCPCB Economic PCBA on the bottom side (`B.Cu`)**, post-PCBA **rear (`B.Cu`) hand-soldered THT**, post-PCBA **front (`F.Cu`) panel-facing hand-soldered THT controls**, and **rear (`B.Cu`) optional `DNP` through-hole test points (`TP1`–`TP8`)**.

> **Verification Status:** All JLCPCB/LCSC parts listed below are live-verified (zero unverified placeholders). All SMT components, rear THT film capacitors, the shrouded `2×5` IDC header, the `3 mm` panel LED, and the optional `RH-5001` through-hole test points (`C5199801`) were live-verified against JLCPCB/LCSC stock, pricing, and Basic/Extended library status during this session. Front-panel jacks (`J1`–`J3`) and 9 mm vertical potentiometers (`RV1`–`RV4`) are explicitly designated as **Manual / Consigned THT (External Synth-DIY Hardware)** aligned to the front panel using KiCad Eurorack footprints documented in [eurorack_mechanical_spec.md](./.agents/skills/eurorack-panel/references/eurorack_mechanical_spec.md).

---

## BOM Partitioning & Cost Overview

| Bucket | Side | Assembly Method | Qty Parts | Unique Lines | Basic / Ext / Consigned | Unit Parts Cost / Board |
|---|---|---|---:|---:|---|---:|
| **1. JLCPCB Economic PCBA (SMT)** | `B.Cu` | JLCPCB Single-Sided SMT (`--side back`) | `44` | `17` | `14` Basic / `3` Extended | **`$0.9078`** |
| **2A. Rear Manual THT** | `B.Cu` | Hand-soldered after PCBA (LCSC-sourced) | `3` | `2` | `2` LCSC Extended (Manual THT — `$0` PCBA fee) | **`$0.6555`** |
| **2B. Front Panel LED (THT)** | `F.Cu` | Hand-soldered w/ panel (LCSC-sourced) | `1` | `1` | `1` LCSC Extended (Manual THT — `$0` PCBA fee) | **`$0.0364`** |
| **2C. Front Panel Controls (THT)** | `F.Cu` | Hand-soldered w/ panel (User-consigned) | `7` | `5` | `5` External / Synth-DIY Hardware | *External* |
| **Populated Subtotal** | `B.Cu` + `F.Cu` | Mixed (`B.Cu` SMT + `B.Cu`/`F.Cu` THT) | **`55`** | **`25`** | **`14` Basic / `3` PCBA Ext / `3` THT LCSC / `5` Consigned** | **`$1.5997` (LCSC subtotal)** |
| **3. Optional / `DNP` Test Points (THT)** | `B.Cu` | **DNP** / Optional post-PCBA hand-solder (`TP1`–`TP8`) | `8` (`DNP`) | `1` | `1` LCSC Extended (`DNP` — `$0` PCBA fee) | **`$0.0000` bare** *(`$0.6704` if all 8 fitted)* |

* **JLCPCB Extended Feeder Fees (PCBA only):** `3` Extended SMT lines (`TL074HIDR` `C2878713`, `1 kΩ 1 W 2512` `C54315`, `22 µF 50 V SMD` `C2836438`) × `$3.00` = **`$9.00` per batch** (`$1.80/board` over a 5-board minimum order). Manual THT parts and **`DNP` test points (`TP1`–`TP8`)** are excluded from `jlcpcb_bom.csv` and the PCBA CPL (`--smd-only --exclude-dnp`), incurring `$0` PCBA loading fees.
* **Removed Original Designators:** `R14`, `R22`, and `R23` from [EnvelopeFollower.md](./EnvelopeFollower.md) are intentionally removed (zero-attenuation `U1D` gain/offset scaling and active `U2B` LED feedback sink).

---

## 1. Bucket 1 — JLCPCB Economic Single-Sided SMT Assembly (`B.Cu`)

All 44 components below are placed on **`B.Cu`** and included in `jlcpcb_bom.csv` and the back-side CPL (`--side back --smd-only --exclude-dnp`).

| Ref(s) | Qty | Value / Rating | MPN | Manufacturer | LCSC Package / KiCad Footprint | LCSC # | Class | Stock | Unit USD | Ext USD | Datasheet |
|---|---:|---|---|---|---|---|---|---:|---:|---:|---|
| `U1`, `U2` | 2 | `TL074H` Quad JFET/CMOS Op-Amp (`4.5–40 V`, `±20 V`) | `TL074HIDR` | Texas Instruments | `SOIC-14` / `Package_SO:SOIC-14_3.9x8.7mm_P1.27mm` | `C2878713` | Extended | `465` | `$0.2558` | `$0.5116` | [PDF](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2302282300_Texas-Instruments-TL074HIDR_C2878713.pdf) |
| `R2`–`R7`, `R9`, `R10`, `R15`, `R17`, `R18`, `R20`, `R27` | 13 | `10 kΩ` `±1%` `100 mW` `75 V` | `0603WAF1002T5E` | UNI-ROYAL | `0603` / `Resistor_SMD:R_0603_1608Metric` | `C25804` | **Basic** | `42,582,187` | `$0.0017` | `$0.0221` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010045_UNI-ROYAL-Uniroyal-Elec-0603WAF1002T5E_C25804.pdf) |
| `R11`, `R12` | 2 | `1 kΩ` `±1%` `100 mW` `75 V` | `0603WAF1001T5E` | UNI-ROYAL | `0603` / `Resistor_SMD:R_0603_1608Metric` | `C21190` | **Basic** | `40,562,224` | `$0.0016` | `$0.0032` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010130_UNI-ROYAL-Uniroyal-Elec-0603WAF1001T5E_C21190.pdf) |
| `R16`, `R19`, `R26` | 3 | `1 kΩ` `±1%` **`1 W`** `200 V` | `25121WF1001T4E` | UNI-ROYAL | `2512` / `Resistor_SMD:R_2512_6332Metric` | `C54315` | Extended | `52,554` | `$0.0336` | `$0.1008` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010000_UNI-ROYAL-Uniroyal-Elec-25121WF1001T4E_C54315.pdf) |
| `R1` | 1 | `100 kΩ` `±1%` `100 mW` `75 V` | `0603WAF1003T5E` | UNI-ROYAL | `0603` / `Resistor_SMD:R_0603_1608Metric` | `C25803` | **Basic** | `13,049,690` | `$0.0029` | `$0.0029` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010045_UNI-ROYAL-Uniroyal-Elec-0603WAF1003T5E_C25803.pdf) |
| `R8` | 1 | `20 kΩ` `±1%` `100 mW` `75 V` | `0603WAF2002T5E` | UNI-ROYAL | `0603` / `Resistor_SMD:R_0603_1608Metric` | `C4184` | **Basic** | `4,869,831` | `$0.0018` | `$0.0018` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010230_UNI-ROYAL-Uniroyal-Elec-0603WAF2002T5E_C4184.pdf) |
| `R13` | 1 | `22 kΩ` `±1%` `100 mW` `75 V` | `0603WAF2202T5E` | UNI-ROYAL | `0603` / `Resistor_SMD:R_0603_1608Metric` | `C31850` | **Basic** | `2,203,056` | `$0.0042` | `$0.0042` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010030_UNI-ROYAL-Uniroyal-Elec-0603WAF2202T5E_C31850.pdf) |
| `R24` | 1 | `4.7 kΩ` `±1%` `100 mW` `75 V` | `0603WAF4701T5E` | UNI-ROYAL | `0603` / `Resistor_SMD:R_0603_1608Metric` | `C23162` | **Basic** | `19,312,230` | `$0.0028` | `$0.0028` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010116_UNI-ROYAL-Uniroyal-Elec-0603WAF4701T5E_C23162.pdf) |
| `R21` | 1 | `3.3 kΩ` `±1%` `100 mW` `75 V` | `0603WAF3301T5E` | UNI-ROYAL | `0603` / `Resistor_SMD:R_0603_1608Metric` | `C22978` | **Basic** | `4,036,281` | `$0.0020` | `$0.0020` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010116_UNI-ROYAL-Uniroyal-Elec-0603WAF3301T5E_C22978.pdf) |
| `R25` | 1 | `330 Ω` `±1%` `100 mW` `75 V` | `0603WAF3300T5E` | UNI-ROYAL | `0603` / `Resistor_SMD:R_0603_1608Metric` | `C23138` | **Basic** | `2,614,499` | `$0.0015` | `$0.0015` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010116_UNI-ROYAL-Uniroyal-Elec-0603WAF3300T5E_C23138.pdf) |
| `C5`–`C8` | 4 | `100 nF` `50 V` `X7R` `±10%` | `CC0603KRX7R9BB104` | YAGEO | `0603` / `Capacitor_SMD:C_0603_1608Metric` | `C14663` | **Basic** | `53,170,848` | `$0.0056` | `$0.0224` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2211101700_YAGEO-CC0603KRX7R9BB104_C14663.pdf) |
| `C9` | 1 | `22 pF` `50 V` `C0G` `±5%` | `CL10C220JB8NNNC` | Samsung Electro-Mechanics | `0603` / `Capacitor_SMD:C_0603_1608Metric` | `C1653` | **Basic** | `2,736,905` | `$0.0089` | `$0.0089` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL10C220JB8NNNC_C1653.pdf) |
| `C10`, `C11` | 2 | `47 pF` `50 V` `C0G` `±5%` | `CL10C470JB8NNNC` | Samsung Electro-Mechanics | `0603` / `Capacitor_SMD:C_0603_1608Metric` | `C1671` | **Basic** | `1,100,428` | `$0.0053` | `$0.0106` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL10C470JB8NNNC_C1671.pdf) |
| `C3`, `C4` | 2 | `22 µF` `50 V` `±20%` Alum. Elec. | `RVT22UF50V67RV0028` | KNSCHA | `SMD,D6.3xL5.4mm` / `Capacitor_SMD:CP_Elec_6.3x5.4` | `C2836438` | Extended | `124,542` | `$0.0406` | `$0.0812` | [PDF](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2105281608_KNSCHA-RVT22UF50V67RV0028_C2836438.pdf) |
| `D1`–`D3`, `D10` | 4 | `1N4148W` `75 V` `150 mA` Fast Diode | `1N4148W` | ST (Semtech) | `SOD-123` / `Diode_SMD:D_SOD-123` | `C81598` | **Basic** | `4,489,926` | `$0.0123` | `$0.0492` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_1811061725_ST-Semtech-1N4148W_C81598.pdf) |
| `D5`, `D6` | 2 | `40 V` `1 A` Schottky Diode | `B5819W SL` | Jiangsu Changjing | `SOD-123` / `Diode_SMD:D_SOD-123` | `C8598` | **Basic** | `820,298` | `$0.0251` | `$0.0502` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Jiangsu-Changjing-Electronics-Technology-Co---Ltd--B5819W-SL_C8598.pdf) |
| `D7`–`D9` | 3 | `BAV99` `100 V` `125 mA` Dual Series | `BAV99,215` | Nexperia | `SOT-23` / `Package_TO_SOT_SMD:SOT-23` | `C2500` | **Basic** | `2,113,716` | `$0.0108` | `$0.0324` | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2407250951_Nexperia-BAV99-215_C2500.pdf) |

---

## 2. Bucket 2A — Rear Hand-Soldered THT (`B.Cu`, Post-PCBA)

Mounted on the rear (`B.Cu`) side and hand-soldered after JLCPCB SMT assembly (excluded from `jlcpcb_bom.csv` and PCBA CPL).

| Ref(s) | Qty | Value / Spec | MPN | Manufacturer | LCSC Package / KiCad Footprint | LCSC # | Stock | Unit USD | Ext USD | Notes & Datasheet |
|---|---:|---|---|---|---|---|---:|---:|---:|---|
| `C1`, `C2` | 2 | `1 µF` `63 V` `±5%` Metallized Polyester Film | `C241J105J2SA201` | XIAMEN FARATRONIC | `Plugin,P=5mm` / `5.00 mm` radial box film (`B.Cu`) | `C328852` | `20,135` | `$0.2657` | `$0.5314` | Non-MLCC timing/coupling cap; verify exact body width from [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_XIAMEN-FARATRONIC-C241J105J2SA201_C328852.pdf) |
| `J4` | 1 | `2×5` `2.54 mm` Shrouded Box Header (`250 V`, `3 A`) | `IDC2.54-2*5PZ` | JXTCONN | `Plugin,P=2.54mm` / `Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical` | `C53207560` | `2,060` | `$0.1241` | `$0.1241` | Eurorack keyed power (`1–2 = -12V_IN`, `3–8 = GND`, `9–10 = +12V_IN`); no LCSC PDF linked |

---

## 3. Bucket 2B — Front Panel-Facing Hand-Soldered THT (`F.Cu`, Post-PCBA)

Placed on **`F.Cu`**, mechanically aligned to the `10.5 mm` standoff Eurorack front panel prior to hand-soldering, and excluded from `jlcpcb_bom.csv` / PCBA CPL.

### 3.1 LCSC-Verified Indicator LED (`F.Cu`)

| Ref | Qty | Value / Spec | MPN | Manufacturer | LCSC Package / KiCad Footprint | LCSC # | Stock | Unit USD | Notes & Datasheet |
|---|---:|---|---|---|---|---|---:|---:|---|
| `D4` | 1 | `3 mm` Yellow-Green Diffused LED (`2.0 V` `V_F`, `100 mcd @ 20 mA`, `573 nm`) | `204-10SYGD/S530-E3` | Everlight Elec | `Plugin,D=3mm` / `LED_THT:LED_D3.0mm` | `C85161` | `166,421` | `$0.0364` | Pad `1` = Cathode (`LED_K`), Pad `2` = Anode (`LED_A`); `3.2 mm` NPTH panel hole; [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_1811141531_Everlight-Elec-204-10SYGD-S530-E3_C85161.pdf) |

### 3.2 User-Sourced / Consigned Synth-DIY Panel Hardware (`F.Cu`)

Per Eurorack mechanical standards ([eurorack_mechanical_spec.md](./.agents/skills/eurorack-panel/references/eurorack_mechanical_spec.md)), panel jacks and 9 mm vertical potentiometers are sourced externally from synth-DIY vendors (e.g., Thonk, Tayda, Modular Addict, Mouser/DigiKey) and marked **`Manual / Consigned THT`**:

| Ref | Qty | Panel Label | Value / Taper | Standard Synth-DIY Part | KiCad Footprint (`F.Cu`) | Panel Drill / Nut Keepout | Sourcing & Wiring Notes |
|---|---:|---|---|---|---|---|---|
| `J1` | 1 | `IN` | `3.5 mm` Mono Jack | QingPu `WQP-PJ398SM` (`PJ301M-12`) | `Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | `6.2–6.3 mm` / `9.5 mm` (`+6.48 mm` Y-offset) | **External / Consigned THT** (`T=IN_TIP`, `TN=GND`, `S=GND`) |
| `J2` | 1 | `OUT` | `3.5 mm` Mono Jack | QingPu `WQP-PJ398SM` (`PJ301M-12`) | `Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | `6.2–6.3 mm` / `9.5 mm` (`+6.48 mm` Y-offset) | **External / Consigned THT** (`T=OUT_TIP`, **`TN=NC`**, `S=GND`) |
| `J3` | 1 | `INV_OUT` | `3.5 mm` Mono Jack | QingPu `WQP-PJ398SM` (`PJ301M-12`) | `Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | `6.2–6.3 mm` / `9.5 mm` (`+6.48 mm` Y-offset) | **External / Consigned THT** (`T=INV_OUT_TIP`, **`TN=NC`**, `S=GND`) |
| `RV1` | 1 | `GAIN` | **`A100k`** (`100 kΩ` Audio/Log) | Alpha `RD901F-40-00D` / Alps `RK09K` 9 mm Vertical | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` *(or `Alps_RK09K`)* | `7.2–7.5 mm` / `10.5–11.0 mm` | **External / Consigned THT** (`1=GAIN_MID`, `2+3=V_AMP`; CW = higher gain) |
| `RV2` | 1 | `ATK` | **`A50k`** (`50 kΩ` Audio/Log) | Alpha `RD901F-40-00D` / Alps `RK09K` 9 mm Vertical | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` *(or `Alps_RK09K`)* | `7.2–7.5 mm` / `10.5–11.0 mm` | **External / Consigned THT** (`1=ATK_POT_IN`, `2+3=ENV_CAP`; CW = slower attack) |
| `RV3` | 1 | `Release` | **`A1M`** (`1 MΩ` Audio/Log) | Alpha `RD901F-40-00D` / Alps `RK09K` 9 mm Vertical | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` *(or `Alps_RK09K`)* | `7.2–7.5 mm` / `10.5–11.0 mm` | **External / Consigned THT** (`1=REL_MID`, `2+3=GND`; CW = longer release) |
| `RV4` | 1 | `OFFSET` | **`B10k`** (`10 kΩ` Linear) | Alpha `RD901F-40-00D` / Alps `RK09K` 9 mm Vertical | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` *(or `Alps_RK09K`)* | `7.2–7.5 mm` / `10.5–11.0 mm` | **External / Consigned THT** (`1=OFFSET_TOP`, `2=OFFSET_WIPER`, `3=OFFSET_BOT`; CW = `+OUT`) |

---

## 4. Bucket 3 — Optional / `DNP` Rear Test Points (`B.Cu` THT, Post-PCBA)

Placed on the **rear (`B.Cu`)** side so test rings protrude behind the board away from the `10.5 mm` front-panel standoff. All `8` test points (`TP1`–`TP8`) MUST be marked **`DNP`**, **`Exclude from BOM`**, and **`Exclude from Position Files`** in KiCad/SKiDL so they incur `$0` JLCPCB PCBA fees and never leak into `jlcpcb_bom.csv` or the bottom-side CPL. Left unsoldered, the `2.0 mm` copper annular rings (`1.0 mm` plated drills) remain directly probeable from either side.

| Ref(s) | Qty | Value / Spec | MPN | Manufacturer | LCSC Package / KiCad Footprint | LCSC # | Stock | Unit USD | Ext USD | Notes & Datasheet |
|---|---:|---|---|---|---|---|---:|---:|---:|---|
| `TP1`–`TP8` | 8 (`DNP`) | `2.5 mm` Black Pin-Type THT Test Point (`1.0 mm` PCB drill) | `RH-5001` | ronghe | `-` (Through-Board) / `TestPoint:TestPoint_Keystone_5000-5004_Miniature` *(or `TestPoint_Loop_D2.50mm_Drill1.0mm`)* | `C5199801` | `98,835` | `$0.0838` *(`$0.0805` @ `5+`)* | `$0.6704` *(`$0.00` bare)* | **DNP / Optional THT (`B.Cu`):** `TP1=GND`, `TP2=+12V`, `TP3=-12V`, `TP4=IN_BUF`, `TP5=V_AMP`, `TP6=V_FWR`, `TP7=ENV_CAP`, `TP8=V_OUT_PRE`. `"2.5mm"` is the insulated bead OD; verify PCB drill (`1.0 mm`) & height from [PDF](https://datasheet.lcsc.com/datasheet/pdf/4adec3e10718fa4444bfddc0d5622733.pdf?productCode=C5199801) |

---

## 5. Complete Itemized Component List (55 Populated + 8 Optional `DNP` Test Points)

| Ref | Value | Function / Stage | Side | Assembly | LCSC # / Source | MPN |
|---|---|---|---|---|---|---|
| `R1` | `100 kΩ` (`0603`, 1%) | `IN` Impedance / DC Pull-Down | `B.Cu` | JLCPCB SMT | `C25803` (Basic) | `0603WAF1003T5E` |
| `R2` | `10 kΩ` (`0603`, 1%) | `U1A` Gain Input | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `R3` | `10 kΩ` (`0603`, 1%) | `U1B` Half-Wave Input | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `R4` | `10 kΩ` (`0603`, 1%) | `U1B` Half-Wave Feedback | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `R5` | `10 kΩ` (`0603`, 1%) | `U1C` Full-Wave Rectified Sum | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `R6` | `10 kΩ` (`0603`, 1%) | `U1C` Feed-Forward #1 (`20 kΩ` pair) | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `R7` | `10 kΩ` (`0603`, 1%) | `U1C` Feed-Forward #2 (`20 kΩ` pair) | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `R8` | `20 kΩ` (`0603`, 1%) | `U1C` Unity Rectifier Feedback | `B.Cu` | JLCPCB SMT | `C4184` (Basic) | `0603WAF2002T5E` |
| `R9` | `10 kΩ` (`0603`, 1%) | `U1D +` ESD/Power-Off Isolation | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `R10` | `10 kΩ` (`0603`, 1%) | Minimum Release Resistor | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `R11` | `1 kΩ` (`0603`, 1%) | `OFFSET` Divider (`+12V` end) | `B.Cu` | JLCPCB SMT | `C21190` (Basic) | `0603WAF1001T5E` |
| `R12` | `1 kΩ` (`0603`, 1%) | `OFFSET` Divider (`-12V` end) | `B.Cu` | JLCPCB SMT | `C21190` (Basic) | `0603WAF1001T5E` |
| `R13` | `22 kΩ` (`0603`, 1%) | `OFFSET` Summing (`1.400×–1.436×`) | `B.Cu` | JLCPCB SMT | `C31850` (Basic) | `0603WAF2202T5E` |
| `R15` | `10 kΩ` (`0603`, 1%) | `U1D` Output Stage Feedback | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `R16` | `1 kΩ` (`2512`, `1 W`, 1%) | `OUT` Fault-Proof Protection | `B.Cu` | JLCPCB SMT | `C54315` (Extended) | `25121WF1001T4E` |
| `R17` | `10 kΩ` (`0603`, 1%) | `U2A` `INV_OUT` Input | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `R18` | `10 kΩ` (`0603`, 1%) | `U2A` `INV_OUT` Feedback | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `R19` | `1 kΩ` (`2512`, `1 W`, 1%) | `INV_OUT` Fault-Proof Protection | `B.Cu` | JLCPCB SMT | `C54315` (Extended) | `25121WF1001T4E` |
| `R20` | `10 kΩ` (`0603`, 1%) | `U2B +` `LED` Input Isolation | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `R21` | `3.3 kΩ` (`0603`, 1%) | `LED` Linear Current Sense | `B.Cu` | JLCPCB SMT | `C22978` (Basic) | `0603WAF3301T5E` |
| `R24` | `4.7 kΩ` (`0603`, 1%) | `GAIN` Minimum Floor (`0.47×`) | `B.Cu` | JLCPCB SMT | `C23162` (Basic) | `0603WAF4701T5E` |
| `R25` | `330 Ω` (`0603`, 1%) | Attack Peak Current Limiter (`0.33 ms`) | `B.Cu` | JLCPCB SMT | `C23138` (Basic) | `0603WAF3300T5E` |
| `R26` | `1 kΩ` (`2512`, `1 W`, 1%) | `IN` ESD / Hot-Plug Surge Limiter | `B.Cu` | JLCPCB SMT | `C54315` (Extended) | `25121WF1001T4E` |
| `R27` | `10 kΩ` (`0603`, 1%) | `U2C` Clamp Current Limiter | `B.Cu` | JLCPCB SMT | `C25804` (Basic) | `0603WAF1002T5E` |
| `C1` | `1 µF` (`63 V`, Film) | Input AC Coupling (`1.58 Hz`) | `B.Cu` | Manual THT | `C328852` (Extended) | `C241J105J2SA201` |
| `C2` | `1 µF` (`63 V`, Film) | Envelope Storage Timing Cap | `B.Cu` | Manual THT | `C328852` (Extended) | `C241J105J2SA201` |
| `C3` | `22 µF` (`50 V`, Elec SMD) | `+12V` Bulk Filter (`+`=`+12V`, `-`=`GND`) | `B.Cu` | JLCPCB SMT | `C2836438` (Extended) | `RVT22UF50V67RV0028` |
| `C4` | `22 µF` (`50 V`, Elec SMD) | `-12V` Bulk Filter (`+`=`GND`, `-`=`-12V`) | `B.Cu` | JLCPCB SMT | `C2836438` (Extended) | `RVT22UF50V67RV0028` |
| `C5` | `100 nF` (`50 V`, X7R, `0603`) | `U1.4` (`+12V`) Local Bypass | `B.Cu` | JLCPCB SMT | `C14663` (Basic) | `CC0603KRX7R9BB104` |
| `C6` | `100 nF` (`50 V`, X7R, `0603`) | `U1.11` (`-12V`) Local Bypass | `B.Cu` | JLCPCB SMT | `C14663` (Basic) | `CC0603KRX7R9BB104` |
| `C7` | `100 nF` (`50 V`, X7R, `0603`) | `U2.4` (`+12V`) Local Bypass | `B.Cu` | JLCPCB SMT | `C14663` (Basic) | `CC0603KRX7R9BB104` |
| `C8` | `100 nF` (`50 V`, X7R, `0603`) | `U2.11` (`-12V`) Local Bypass | `B.Cu` | JLCPCB SMT | `C14663` (Basic) | `CC0603KRX7R9BB104` |
| `C9` | `22 pF` (`50 V`, C0G, `0603`) | `U1A` Ultrasonic Comp (`69.1 kHz`) | `B.Cu` | JLCPCB SMT | `C1653` (Basic) | `CL10C220JB8NNNC` |
| `C10` | `47 pF` (`50 V`, C0G, `0603`) | `U1D` Output Stage Stabilization | `B.Cu` | JLCPCB SMT | `C1671` (Basic) | `CL10C470JB8NNNC` |
| `C11` | `47 pF` (`50 V`, C0G, `0603`) | `U2A` Inverter Stabilization | `B.Cu` | JLCPCB SMT | `C1671` (Basic) | `CL10C470JB8NNNC` |
| `D1` | `1N4148W` (`SOD-123`) | `U1B` Rectifier Feedback Clamp | `B.Cu` | JLCPCB SMT | `C81598` (Basic) | `1N4148W` |
| `D2` | `1N4148W` (`SOD-123`) | `U1B` Rectifier Output | `B.Cu` | JLCPCB SMT | `C81598` (Basic) | `1N4148W` |
| `D3` | `1N4148W` (`SOD-123`) | `U2D` Active Zero-Deadzone Peak Diode | `B.Cu` | JLCPCB SMT | `C81598` (Basic) | `1N4148W` |
| `D4` | `3 mm` Yellow-Green LED | Active Envelope Indicator | `F.Cu` | Manual THT | `C85161` (Extended) | `204-10SYGD/S530-E3` |
| `D5` | `B5819W SL` (`SOD-123`, `40 V`) | `+12V` Reverse-Polarity Schottky | `B.Cu` | JLCPCB SMT | `C8598` (Basic) | `B5819W SL` |
| `D6` | `B5819W SL` (`SOD-123`, `40 V`) | `-12V` Reverse-Polarity Schottky | `B.Cu` | JLCPCB SMT | `C8598` (Basic) | `B5819W SL` |
| `D7` | `BAV99,215` (`SOT-23`) | `OUT` ESD / Overvoltage Rail Clamp | `B.Cu` | JLCPCB SMT | `C2500` (Basic) | `BAV99,215` |
| `D8` | `BAV99,215` (`SOT-23`) | `INV_OUT` ESD / Overvoltage Rail Clamp | `B.Cu` | JLCPCB SMT | `C2500` (Basic) | `BAV99,215` |
| `D9` | `BAV99,215` (`SOT-23`) | `IN` Buffer ESD / Overvoltage Clamp | `B.Cu` | JLCPCB SMT | `C2500` (Basic) | `BAV99,215` |
| `D10` | `1N4148W` (`SOD-123`) | `D4` Anti-Parallel Reverse Clamp | `B.Cu` | JLCPCB SMT | `C81598` (Basic) | `1N4148W` |
| `U1` | `TL074HIDR` (`SOIC-14`) | `U1A` Gain, `U1B`/`U1C` FWR, `U1D` Out | `B.Cu` | JLCPCB SMT | `C2878713` (Extended) | `TL074HIDR` |
| `U2` | `TL074HIDR` (`SOIC-14`) | `U2A` Inv, `U2B` LED, `U2C` Buf, `U2D` Peak | `B.Cu` | JLCPCB SMT | `C2878713` (Extended) | `TL074HIDR` |
| `RV1` | `A100k` (9 mm Vertical) | `GAIN` Control | `F.Cu` | Consigned THT | External Synth-DIY | Alpha `RD901F` / Alps `RK09K` |
| `RV2` | `A50k` (9 mm Vertical) | `ATK` Control | `F.Cu` | Consigned THT | External Synth-DIY | Alpha `RD901F` / Alps `RK09K` |
| `RV3` | `A1M` (9 mm Vertical) | `Release` Control | `F.Cu` | Consigned THT | External Synth-DIY | Alpha `RD901F` / Alps `RK09K` |
| `RV4` | `B10k` (9 mm Vertical) | `OFFSET` Control | `F.Cu` | Consigned THT | External Synth-DIY | Alpha `RD901F` / Alps `RK09K` |
| `J1` | `3.5 mm` Mono Jack | `IN` Panel Jack (`TN` to `GND`) | `F.Cu` | Consigned THT | External Synth-DIY | `WQP-PJ398SM` |
| `J2` | `3.5 mm` Mono Jack | `OUT` Panel Jack (`TN` = `NC`) | `F.Cu` | Consigned THT | External Synth-DIY | `WQP-PJ398SM` |
| `J3` | `3.5 mm` Mono Jack | `INV_OUT` Panel Jack (`TN` = `NC`) | `F.Cu` | Consigned THT | External Synth-DIY | `WQP-PJ398SM` |
| `J4` | `2×5` `2.54 mm` Box Header | Eurorack Shrouded Power Header | `B.Cu` | Manual THT | `C53207560` (Extended) | `IDC2.54-2*5PZ` |
| `TP1` | `RH-5001` (`DNP` Test Point) | `GND` Reference Ground Clip | `B.Cu` | **DNP** / Optional THT | `C5199801` (Optional) | `RH-5001` |
| `TP2` | `RH-5001` (`DNP` Test Point) | `+12V` Protected Rail (`+11.65 V`) | `B.Cu` | **DNP** / Optional THT | `C5199801` (Optional) | `RH-5001` |
| `TP3` | `RH-5001` (`DNP` Test Point) | `-12V` Protected Rail (`-11.65 V`) | `B.Cu` | **DNP** / Optional THT | `C5199801` (Optional) | `RH-5001` |
| `TP4` | `RH-5001` (`DNP` Test Point) | `IN_BUF` (`U2C` Buffer Output) | `B.Cu` | **DNP** / Optional THT | `C5199801` (Optional) | `RH-5001` |
| `TP5` | `RH-5001` (`DNP` Test Point) | `V_AMP` (`U1A` Gain Stage Output) | `B.Cu` | **DNP** / Optional THT | `C5199801` (Optional) | `RH-5001` |
| `TP6` | `RH-5001` (`DNP` Test Point) | `V_FWR` (`U1C` Full-Wave Rectifier) | `B.Cu` | **DNP** / Optional THT | `C5199801` (Optional) | `RH-5001` |
| `TP7` | `RH-5001` (`DNP` Test Point) | `ENV_CAP` (`C2` Envelope Storage) | `B.Cu` | **DNP** / Optional THT | `C5199801` (Optional) | `RH-5001` |
| `TP8` | `RH-5001` (`DNP` Test Point) | `V_OUT_PRE` (`U1D` Pre-`R16` Output) | `B.Cu` | **DNP** / Optional THT | `C5199801` (Optional) | `RH-5001` |

*(Removed from original circuit: `R14`, `R22`, `R23`.)*

---

## 6. JLCPCB Single-Sided PCBA BOM CSV (`B.Cu` SMT Only)

Exact 4-column JLCPCB PCBA CSV structure (`44` SMT parts; upload alongside `B.Cu` CPL exported with `--side back --smd-only --exclude-dnp` and select **Bottom Side** under JLCPCB Economic PCBA — `TP1`–`TP8` are `DNP` and excluded from both `jlcpcb_bom.csv` and the CPL):

```csv
Comment,Designator,Footprint,LCSC Part #
TL074HIDR,"U1, U2",SOIC-14_3.9x8.7mm_P1.27mm,C2878713
10k,"R2, R3, R4, R5, R6, R7, R9, R10, R15, R17, R18, R20, R27",R_0603_1608Metric,C25804
1k,"R11, R12",R_0603_1608Metric,C21190
1k 1W,"R16, R19, R26",R_2512_6332Metric,C54315
100k,R1,R_0603_1608Metric,C25803
20k,R8,R_0603_1608Metric,C4184
22k,R13,R_0603_1608Metric,C31850
4.7k,R24,R_0603_1608Metric,C23162
3.3k,R21,R_0603_1608Metric,C22978
330R,R25,R_0603_1608Metric,C23138
100nF,"C5, C6, C7, C8",C_0603_1608Metric,C14663
22pF,C9,C_0603_1608Metric,C1653
47pF,"C10, C11",C_0603_1608Metric,C1671
22uF 50V,"C3, C4",CP_Elec_6.3x5.4,C2836438
1N4148W,"D1, D2, D3, D10",D_SOD-123,C81598
B5819W,"D5, D6",D_SOD-123,C8598
BAV99,"D7, D8, D9",SOT-23,C2500
```

---

## 7. Verified Alternate Parts & 5-Board Prototype Budget

### Live-Verified Alternate LCSC Options (from Batch 1)

| Target Ref(s) | Primary Selected | Verified LCSC Alternate | MPN / Package | Class | Stock | Unit USD | Trade-off |
|---|---|---|---|---|---:|---:|---|
| `D1`–`D3`, `D10` | `C81598` (`SOD-123`) | `C2128` (`1N4148WS`, Jiangsu Changjing) | `SOD-323` | **Basic** | `3,287,956` | `$0.0100` | Smaller `SOD-323` footprint |
| `D5`, `D6` | `C8598` (`SOD-123`) | `C191023` (`1N5819WS`, Hottech) | `SOD-323` | **Basic** | `5,666,945` | `$0.0119` | `-38%` footprint area vs. `SOD-123` |
| `D5`, `D6` | `C8598` (`SOD-123`) | `C2480` (`SS14`, MDD) | `SMA(DO-214AC)` | **Basic** | `1,218,607` | `$0.0192` | Larger `SMA` package (`6.5×3.5 mm`) |
| `C3`, `C4` | `C2836438` (`22 µF 50 V`) | `C970678` (`RVT1V470M0605 47UF 35V`) | `SMD,D6.3xL5.4mm` | Extended | `12,150` | `$0.0346` | `2.1×` capacitance (`35 V` vs. `50 V`) |
| `C1`, `C2` | `C328852` (Faratronic) | `C92673` (`MKS2C041001F00JSSD`, WIMA) | `Plugin,P=5mm` | Extended | `5,573` | `$1.1437` | Premium WIMA MKS2 (`4.3×` cost) |
| `C1`, `C2` | `C328852` (Faratronic) | `C3975271` (`MEB105J63V82CB0235`, KNSCHA) | `Plugin,P=5mm` | Extended | `10,566` | `$0.1911` | Lower-cost polyester film (`P=5mm`) |
| `D4` | `C85161` (Yellow-Green) | `C99761` (`204-10SUGD/S400-A5`) | `3 mm` Emerald Green | Extended | `83,190` | `$0.0457` | `500–1000 mcd` high brightness (`3.4 V` `V_F`) |
| `D4` | `C85161` (Yellow-Green) | `C99771` (`204-10SURD/S530-A3-L`) | `3 mm` Red | Extended | `155,197` | `$0.0329` | Classic red diffused lens |
| `R16`, `R19`, `R26` | `C54315` (`2512`, `1 W`) | `C52444` (`1210W2F1001T5E`, `500 mW`) | `1210` | Extended | `25,757` | `$0.0143` | Compact `1210` (`0.5 W` tight at `24 V` `0.58 W`) |

### Cost Summary (LCSC-Verified Parts, `5`-Board Economic PCBA Run)

- **SMT PCBA Parts (`44` parts/board × 5):** `$0.9078 × 5 = $4.54`
- **JLCPCB Extended Feeder Setup Fees (`3` lines × `$3.00`):** `$9.00`
- **Manual LCSC THT Parts (`C1`, `C2`, `J4`, `D4`, 5× boards):** `$0.6919 × 5 = $3.46`
- **LCSC Parts + Extended Fee Subtotal (5 populated boards, excl. bare PCB fab, SMT placement/stencil, shipping, consigned jacks/pots, and optional `DNP` test points):** **`$17.00`** (`~$3.40/board`).
- **Optional `DNP` Test Points (`RH-5001` `C5199801`, `B.Cu`):** **`$0.00`** if probed as bare THT pads (`1.0 mm` drill); **`+$3.22`** if populating all `8` TPs across `5` boards (`40 × $0.0805` at `5+` break, or `$3.28` for a `50`-pack at `$0.0656/ea`).
