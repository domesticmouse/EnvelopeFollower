# Envelope Follower — JLCPCB & Assembly Bill of Materials

Production and hand-assembly Bill of Materials for [`EnvelopeFollowerImproved.md`](./EnvelopeFollowerImproved.md), verified live against the JLCPCB SMT / LCSC component catalog (`selectSmtComponentList/v2` and `wmsc.lcsc.com`).

> **Verification Status:** **100% live-verified.** All **19 SMT line items (`49` components)**, the populated LCSC-sourced THT components (`C1`–`C2`, `J4`, `D4`), and the optional **DNP** test points (`TP1`–`TP8`, Ronghe `RH-5001` / `C5199801`) are verified live with active stock, Basic/Extended feeder status, and unit pricing. Panel-mounted jacks (`J1`–`J3`) and potentiometers (`RV1`–`RV4`) have `0` JLCPCB SMT stock and are tracked separately as manual user-sourced/consigned THT parts for post-PCBA mechanical alignment.

---

## 1. BOM & Cost Summary

| Metric | Count / Value | Notes |
|---|---:|---|
| **Populated Physical Parts** | **60** | `49` SMT (`81.7%`) + `11` populated THT (`18.3%`) across `27` active BOM lines |
| **Optional / DNP Footprints** | **8** | `TP1`–`TP8` (`1` DNP BOM line: Ronghe `RH-5001`, `C5199801`) — **Total PCB footprints: `68` (`28` BOM lines)** |
| **SMT Assembly Parts (JLCPCB Economic)** | **49** | `19` unique SMT BOM lines (`F.Cu` single-sided assembly) |
| **Basic SMT Lines (`$0` feeder fee)** | **14 lines (`33` parts)** | `$0.1907` / board in Basic passives and diodes |
| **Extended SMT Lines (`$3` feeder fee ea.)** | **5 lines (`16` parts)** | `TL074HIDR`, `BAT54S`, `10 kΩ ±0.1%`, `470 Ω 0.5 W`, `22 µF 50 V` (`$0.8587` / board + `$15.00` setup fee per order) |
| **THT Parts Mounted Later (Populated)** | **11 parts (`8` lines)** | `J1`–`J3` (`3`), `RV1`–`RV4` (`4`), `J4` (`1`), `D4` (`1`), plus `C1`–`C2` (`2` box film caps) |
| **DNP THT Hardware (Optional)** | **8 parts (`1` DNP line)** | `TP1`–`TP8` (`C5199801` `RH-5001`); omitted from PCBA/default build (bare `B.Cu` pads work unstuffed) |
| **SMT Parts Subtotal (1 board)** | **`$1.0494`** | Parts cost only (excludes PCB fab, shipping, and `$15.00` Extended feeder fees) |
| **LCSC-Verified THT Subtotal (1 board)** | **`$0.8259`** | Populated only: `C1`–`C2` (`C125397`), `J4` (`C53207560`), `D4` (`C99771`); DNP `TP1`–`TP8` = `$0.0000` default (`+$0.6664` @ 1+ or `+$0.6440` @ 5+ if installed) |

### Cost Optimization Notes
1. **Rectifier consolidation (`7 × 10 kΩ ±0.1%`, `C95204`)**: Implementing `R4+R5` (`20.00 kΩ` feedforward) and `R8A+R8B` (`20.00 kΩ` feedback) from two `10 kΩ ±0.1%` resistors in series eliminates a separate `20 kΩ ±0.1%` Extended feeder line (saving **`$3.00`** per order for `$0.05` in parts) while ensuring single-reel thermal tracking across all 7 rectifier resistors.
2. **Silicon & clamp diode Basic parts**: `D_PWR_P/N` (`C8598` `B5819W SL`), `D3`/`D_LED_CLAMP` (`C2128` `1N4148WS`), and `D_IN`/`D_OUT`/`D_INV_OUT` (`C2500` `BAV99,215`) are all **Basic** parts (`$0` feeder fee) with distinct packages (`SOD-123`, `SOD-323`, `SOT-23`).
3. **Why `C1` and `C2` (`1 µF` Film) are THT**: Per [`EnvelopeFollowerImprovements.md`](./EnvelopeFollowerImprovements.md) (§3.3), Class-2 MLCCs (`X7R`/`X5R`) cannot be used for `C2` due to piezoelectric microphonics and DC-bias capacitance loss. Live JLCPCB search confirmed `0` stock for `1 µF` SMD film (`ECWU1105KCV`, `C264044`), so `C1` and `C2` use compact `P=5mm` TDK metallized polyester box film (`C125397`, stock `1,288`) mounted manually with the other THT parts on `B.Cu`, keeping JLCPCB assembly 100% Economic single-sided SMT.

---

## 2. SMT Production BOM (JLCPCB Economic PCBA — Live Verified)

All 19 line items below are placed on `F.Cu` and populated by JLCPCB SMT assembly.

| Line | Designators | Qty | Value / Comment | Package (`KiCad Footprint`) | MPN | Manufacturer | LCSC Part # | Library Class | Live Stock | Unit ($) | Ext. ($) | Circuit Role |
|---:|---|---:|---|---|---|---|---|---|---:|---:|---:|---|
| **1** | `U1, U2` | 2 | `TL074H` | `SOIC-14` (`Package_SO:SOIC-14_3.9x8.7mm_P1.27mm`) | `TL074HIDR` | Texas Instruments | `C2878713` | **Extended** | 469 | $0.2552 | $0.5104 | Quad FET-input op-amps (`U1A`–`D`, `U2A`–`D`) |
| **2** | `D_PWR_P, D_PWR_N` | 2 | `B5819W` (`40V 1A`) | `SOD-123` (`Diode_SMD:D_SOD-123`) | `B5819W SL` | Changjing Elec | `C8598` | **Basic** | 834,005 | $0.0250 | $0.0500 | `±12V` reverse-polarity Schottky protection |
| **3** | `D1_D2` | 1 | `BAT54S` (`30V 200mA`) | `SOT-23` (`Package_TO_SOT_SMD:SOT-23`) | `BAT54S,215` | Nexperia | `C47546` | **Extended** | 430,826 | $0.0200 | $0.0200 | Dual series Schottky rectifier (`D1` + `D2`) |
| **4** | `D3, D_LED_CLAMP` | 2 | `1N4148WS` (`100V`) | `SOD-323` (`Diode_SMD:D_SOD-323`) | `1N4148WS` | Changjing Elec | `C2128` | **Basic** | 3,321,327 | $0.0100 | $0.0200 | `U2C` peak-detector diode; `D4` reverse clamp |
| **5** | `D_IN, D_OUT, D_INV_OUT` | 3 | `BAV99` (`100V`) | `SOT-23` (`Package_TO_SOT_SMD:SOT-23`) | `BAV99,215` | Nexperia | `C2500` | **Basic** | 1,433,918 | $0.0108 | $0.0324 | Dual series `±12V` ESD/overvoltage clamps |
| **6** | `R_PWR_P, R_PWR_N` | 2 | `10R` (`1% 250mW`) | `1206` (`Resistor_SMD:R_1206_3216Metric`) | `1206W4F100JT5E` | UNI-ROYAL | `C17903` | **Basic** | 1,203,413 | $0.0061 | $0.0122 | `±12V` rail RC damping & inrush limiters |
| **7** | `R_ATK_MIN` | 1 | `470R` (`1% 100mW`) | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `0603WAF4700T5E` | UNI-ROYAL | `C23179` | **Basic** | 4,114,467 | $0.0019 | $0.0019 | Minimum attack surge resistor (`0.47 ms` floor) |
| **8** | `R16A, R16B, R19A, R19B` | 4 | `470R 0.5W` (`1%`) | `1210` (`Resistor_SMD:R_1210_3225Metric`) | `RTT124700FTP` | RALEC | `C333193` | **Extended** | 49,959 | $0.0172 | $0.0688 | Clash-rated `0.5 W` split `OUT`/`INV_OUT` resistors |
| **9** | `R_IN_PROT, R_IN_BUF, R_GAIN_MIN, R11, R12` | 5 | `1k` (`1% 100mW`) | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `0603WAF1001T5E` | UNI-ROYAL | `C21190` | **Basic** | 29,814,196 | $0.0016 | $0.0080 | Input ESD, `U2D+`, `GAIN` floor, `OFFSET` ends |
| **10** | `R_LED` | 1 | `2.2k` (`1% 100mW`) | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `0603WAF2201T5E` | UNI-ROYAL | `C4190` | **Basic** | 4,173,209 | $0.0018 | $0.0018 | `U2B` LED current sink (`0–4.5 mA`) |
| **11** | `R2, R10, R_ENV_PROT, R15, R17, R18, R20` | 7 | `10k` (`1% 100mW`) | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `0603WAF1002T5E` | UNI-ROYAL | `C25804` | **Basic** | 42,213,070 | $0.0017 | $0.0119 | Preamp in, `Rel` min, `U1D`/`U2A`/`U2B` networks |
| **12** | `R3, R4, R5, R6, R7, R8A, R8B` | 7 | `10k 0.1%` (`25ppm`) | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `RT0603BRD0710KL` | YAGEO | `C95204` | **Extended** | 1,877,978 | $0.0255 | $0.1785 | Precision `0.1%` matched `1.000×` rectifier |
| **13** | `R13` | 1 | `18k` (`1% 100mW`) | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `0603WAF1802T5E` | UNI-ROYAL | `C25810` | **Basic** | 736,469 | $0.0027 | $0.0027 | `OFFSET` summing resistor (`±5.09 V` range) |
| **14** | `R1` | 1 | `100k` (`1% 100mW`) | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `0603WAF1003T5E` | UNI-ROYAL | `C25803` | **Basic** | 13,162,675 | $0.0029 | $0.0029 | Input `100 kΩ` `GND` bias (`Z_in = 101 kΩ`) |
| **15** | `R_GAIN_FAIL` | 1 | `1M` (`1% 100mW`) | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `0603WAF1004T5E` | UNI-ROYAL | `C22935` | **Basic** | 5,059,287 | $0.0018 | $0.0018 | `U1A` parallel open-pot-wire fail-safe |
| **16** | `C_DEC1, C_DEC2, C_DEC3, C_DEC4` | 4 | `100nF` (`50V X7R`) | `0603` (`Capacitor_SMD:C_0603_1608Metric`) | `CC0603KRX7R9BB104` | YAGEO | `C14663` | **Basic** | 53,512,065 | $0.0055 | $0.0220 | Local `V+`/`V-` decoupling on `U1`, `U2` |
| **17** | `C_HF` | 1 | `47pF` (`50V C0G`) | `0603` (`Capacitor_SMD:C_0603_1608Metric`) | `CL10C470JB8NNNC` | Samsung | `C1671` | **Basic** | 642,666 | $0.0063 | $0.0063 | `U1A` ultrasonic/RF compensation (`36.9 kHz`) |
| **18** | `C_OUT1, C_OUT2` | 2 | `100pF` (`50V C0G`) | `0603` (`Capacitor_SMD:C_0603_1608Metric`) | `CL10C101JB8NNNC` | Samsung | `C14858` | **Basic** | 3,006,881 | $0.0084 | $0.0168 | `U1D`/`U2A` local HF compensation (`§3.5`) |
| **19** | `C3, C4` | 2 | `22uF` (`50V ±20%`) | `SMD,D6.3xL5.4mm` (`Capacitor_SMD:CP_Elec_6.3x5.4`) | `RVT22UF50V67RV0028` | KNSCHA | `C2836438` | **Extended** | 124,641 | $0.0405 | $0.0810 | `±12V` bulk electrolytic decoupling (`4.2×` margin) |

---

## 3. THT / Manual Assembly BOM (Mounted Later & Optional DNP)

The **11 populated THT parts (`8` active line items)** plus the **8 optional DNP test points (`1` DNP line item: `TP1`–`TP8`)** are omitted from the JLCPCB SMT assembly CSV so JLCPCB executes an **Economic single-sided SMT** build without Standard-assembly THT surcharges. Front-panel hardware (`J1`–`J3`, `RV1`–`RV4`, `D4`) is dry-fitted into the 3U front panel before soldering; `J4`, `C1`/`C2`, and optional `TP1`–`TP8` pins mount on `B.Cu`.

| Line | Designators | Qty | Value / Part | Package (`KiCad Footprint`) | MPN / Spec | Manufacturer / Source | LCSC Part # | Sourcing Status & Live Stock | Unit ($) | Notes |
|---:|---|---:|---|---|---|---|---|---|---:|---|
| **20** | `C1, C2` | 2 | `1uF 100V ±5%` Film | `Plugin,P=5mm` (`Capacitor_THT:C_Rect_L7.2mm_W6.0mm_P5.00mm_FKS2_FKP2_MKS2_MKP2` / `W5.5mm`) | `B32529D1105J000` | TDK (via LCSC) | `C125397` | **Verified Live** (Extended, Stock: `1,288`) | $0.3346 | Non-polarized PET film (`f_c = 1.58 Hz`, zero microphonics/droop); mount on `B.Cu` |
| **21** | `J4` | 1 | `IDC 2x5P 2.54mm` | `Plugin,P=2.54mm` (`Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical`) | `IDC2.54-2*5PZ` | JXTCONN (via LCSC) | `C53207560` | **Verified Live** (Extended, Stock: `2,075`) | $0.1238 | Shrouded keyed Eurorack power header; mount on `B.Cu` |
| **22** | `D4` | 1 | `3mm` Red LED | `Plugin,D=3mm` (`LED_THT:LED_D3.0mm`) | `204-10SURD/S530-A3-L` | Everlight (via LCSC) | `C99771` | **Verified Live** (Extended, Stock: `155,614`) | $0.0329 | Frosted red 3 mm LED (any color/Vf works cleanly in `U2B` loop) |
| **23** | `J1, J2, J3` | 3 | `3.5mm` Mono Jack | `Thonkiconn THT` (`Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles`) | `WQP-PJ398SM` / `PJ301M-12` | QingPu / Thonk / SynthCube | — | **Consigned / User-Sourced** (`C9900009788` `stock=0` on JLC) | ~$0.45 | `J1.TN → GND`; `J2.TN`/`J3.TN = NC` |
| **24** | `RV1` | 1 | `A100k` 9mm Pot | `9mm Vertical THT` (`Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical`) | `RV09AF-40-20K-A104` (or `RD901F-40` `A100k`) | Alpha (Taiwan) / Tayda / Thonk | — | **Consigned / User-Sourced** (`RV09` `stock=0` on JLC) | ~$0.85 | `GAIN` (`-0.10×` to `-9.17×`); audio taper |
| **25** | `RV2` | 1 | `A50k` 9mm Pot | `9mm Vertical THT` (`Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical`) | `RV09AF-40-20K-A503` (`A50k`) | Alpha (Taiwan) / Tayda / Thonk | — | **Consigned / User-Sourced** (`RV09` `stock=0` on JLC) | ~$0.85 | `ATK` (`0.47 ms` to `50.5 ms`); audio taper |
| **26** | `RV3` | 1 | `A1M` 9mm Pot | `9mm Vertical THT` (`Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical`) | `RV09AF-40-20K-A105` (`A1M`) | Alpha (Taiwan) / Tayda / Thonk | — | **Consigned / User-Sourced** (`RV09` `stock=0` on JLC) | ~$0.85 | `Release` (`10 ms` to `1.01 s`); audio taper |
| **27** | `RV4` | 1 | `B10k` 9mm Pot | `9mm Vertical THT` (`Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical`) | `RV09AF-40-20K-B103` (`B10k`, opt. center detent) | Alpha (Taiwan) / Tayda / Thonk | — | **Consigned / User-Sourced** (`RV09` `stock=0` on JLC) | ~$0.85 | `OFFSET` (`±5.09 V`); linear taper |
| **28** | `TP1, TP2, TP3, TP4, TP5, TP6, TP7, TP8` | 8 *(DNP)* | `RH-5001` (`2.5mm` Pin, **DNP**) | `Through-Board Pin` (`TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm` / `TestPoint_Keystone_5000-5004_Miniature`) | `RH-5001` | Ronghe (via LCSC) | `C5199801` | **DNP — Verified Live** (Extended, LCSC Stock: `106,585`, JLC Stock: `102,504`) | $0.0833 | **DNP** (Do Not Populate by default; `$0.0805` @ 5+, `$0.0656` @ 50+ LCSC, `$0.0836` JLC). Optional `B.Cu` pins on `GND`, `+12V`, `-12V`, `IN_BUF`, `PREAMP_OUT`, `RECT_OUT`, `OUT_CLAMP`, `INV_OUT_CLAMP`; verify drill dia. in `C5199801` datasheet |

*(Cross-reference: LCSC carries `HYCW-PJ301M-197B` (`C56407602`, stock `27`, `$0.2534`) as a `PJ301M`-footprint alternative if sourcing jacks from LCSC, though `WQP-PJ398SM` from modular synth suppliers is standard for KiCad's `WQP-PJ398SM` footprint.)*

---

## 4. Ready-to-Upload JLCPCB SMT BOM CSV

Matches JLCPCB's required 4-column upload schema (`Comment,Designator,Footprint,LCSC Part #`) for the 19 Economic SMT lines (excludes manual THT parts and **DNP** test points `TP1`–`TP8`; in KiCad/SKiDL, set `dnp=True` / `exclude_from_bom=True` on `TP1`–`TP8` and filter the CPL with `--bom` before JLCPCB upload):

```csv
Comment,Designator,Footprint,LCSC Part #
TL074H,"U1,U2",SOIC-14_3.9x8.7mm_P1.27mm,C2878713
B5819W,"D_PWR_P,D_PWR_N",D_SOD-123,C8598
BAT54S,D1_D2,SOT-23,C47546
1N4148WS,"D3,D_LED_CLAMP",D_SOD-323,C2128
BAV99,"D_IN,D_OUT,D_INV_OUT",SOT-23,C2500
10R,"R_PWR_P,R_PWR_N",R_1206_3216Metric,C17903
470R,R_ATK_MIN,R_0603_1608Metric,C23179
470R 0.5W,"R16A,R16B,R19A,R19B",R_1210_3225Metric,C333193
1k,"R_IN_PROT,R_IN_BUF,R_GAIN_MIN,R11,R12",R_0603_1608Metric,C21190
2.2k,R_LED,R_0603_1608Metric,C4190
10k,"R2,R10,R_ENV_PROT,R15,R17,R18,R20",R_0603_1608Metric,C25804
10k 0.1%,"R3,R4,R5,R6,R7,R8A,R8B",R_0603_1608Metric,C95204
18k,R13,R_0603_1608Metric,C25810
100k,R1,R_0603_1608Metric,C25803
1M,R_GAIN_FAIL,R_0603_1608Metric,C22935
100nF,"C_DEC1,C_DEC2,C_DEC3,C_DEC4",C_0603_1608Metric,C14663
47pF C0G,C_HF,C_0603_1608Metric,C1671
100pF C0G,"C_OUT1,C_OUT2",C_0603_1608Metric,C14858
22uF 50V,"C3,C4",CP_Elec_6.3x5.4,C2836438
```

---

## 5. Production Cost Estimate (5-Board JLCPCB Prototype Batch)

| Cost Category | 5-Board Batch | Per Board | Basis |
|---|---:|---:|---|
| **JLCPCB SMT Parts (`49` pcs/bd)** | $5.25 | $1.05 | Live JLCPCB unit pricing (`14` Basic + `5` Extended lines) |
| **JLCPCB Extended Feeder Fees (`5 × $3`)** | $15.00 | $3.00 | `C2878713`, `C47546`, `C95204`, `C333193`, `C2836438` |
| **LCSC THT Parts (`C1/C2`, `J4`, `D4`)** | $4.13 | $0.83 | Live pricing (`C125397` ×2, `C53207560` ×1, `C99771` ×1) |
| **User-Sourced Panel Hardware (`J1`–`J3`, `RV1`–`RV4`)** | ~$23.75 | ~$4.75 | Est. ~$0.45/jack (`3×`), ~$0.85/pot (`4×`) |
| **Default Populated Subtotal (excl. PCB/PCBA/Shipping & DNP `TP1`–`TP8`)** | **~$48.13** | **~$9.63** | Add JLCPCB 2-layer PCB fab + Economic PCBA + shipping at checkout |
| *Optional DNP Test Points (`TP1`–`TP8`, `40 pcs` `C5199801` @ `$0.0805`)* | *$3.22* | *$0.64* | *Excluded by default (`DNP`); 50+ LCSC tier is `$3.28` (`$0.0656`/ea, 10 spares) → `~$51.35` (`~$10.27`/bd) if installed* |

---

## 6. Live-Verified Drop-In Alternatives

All alternatives below were verified live in the same JLCPCB catalog query batch:

| Primary Part | Verified Live Alternative | LCSC # | Class | Stock | Unit ($) | Difference / Trade-off |
|---|---|---|---:|---:|---:|---|
| `B5819W SL` (`C8598`) | `1N5819WS` (`SOD-323`) | `C191023` | **Basic** | 5,672,554 | $0.0119 | Smaller `SOD-323` courtyard (`-72%` vs. `SMA`) |
| `1N4148WS` (`C2128`) | `1N4148W` (`SOD-123`) | `C81598` | **Basic** | 4,497,322 | $0.0123 | Larger `SOD-123` package (`75 V`, `400 mW`) |
| `47pF C0G` (`C1671`) | `33pF C0G` / `22pF C0G` (`0603`) | `C1663` / `C1653` | **Basic** | 1.34M / 2.76M | $0.0091 / $0.0089 | Raises HF pole to `52.6 kHz` or `78.9 kHz` |
| `22uF 50V` (`C2836438`) | `RVT22UF35V67RV0104` (`35V`, `D5×5.4mm`) | `C2887274` | Extended | 18,614 | $0.0353 | Smaller `5.0 mm` diameter (`2.9×` margin on `12 V`) |
| `RTT124700FTP` (`C333193`) | `RS-10K4700FT` (`2010`, `0.75 W`) | `C341646` | Extended | 3,264 | $0.0294 | Higher `0.75 W` continuous rating (`2.79×` clash margin) |
| `B32529D1105J000` (`C125397`) | WIMA `MKS2C041001F00JSSD` (`63 V`) | `C92673` | Extended | 5,573 | $1.1409 | Premium WIMA `P=5mm` box film (`1 µF 63 V`) |
| `B32529D1105J000` (`C125397`) | TDK `B32529C0474J289` (`470 nF 63 V`) | `C125390` | Extended | 4,848 | $0.2261 | For `C1` only (`f_c = 3.35 Hz`); keep `1 µF` on `C2` |
