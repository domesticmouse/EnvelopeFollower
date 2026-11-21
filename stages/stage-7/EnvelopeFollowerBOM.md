# Envelope Follower (Improved Eurorack Revision) — Bill of Materials (BOM)

Complete, production-ready Bill of Materials for [EnvelopeFollowerImproved.md](./EnvelopeFollowerImproved.md).

- **Live JLCPCB / LCSC Verification Date:** `2026-11-21` (verified directly against JLCPCB's live SMT catalog API `selectSmtComponentList/v2`, LCSC's live product API `wmsc.lcsc.com` / `jlcsearch`, and the `RH-5001` manufacturer datasheet PDF).
- **Verification Coverage:** **100% of JLCPCB/LCSC components verified live** (zero unverified or `PENDING_VERIFY` entries).
- **Assembly Architecture:**
  - **`B.Cu` Single-Sided JLCPCB Economic PCBA (`49` SMT parts, `20` unique BOM lines):** All ICs (`2 × TL074HIDR`), diodes, ESD clamps, SMD resistors, decoupling capacitors, and SMD bulk electrolytics are placed strictly on **`B.Cu`** (`0` SMT parts on `F.Cu`).
  - **`B.Cu` Rear Manual THT (`3` populated parts + `8` `DNP` test points):** `J4` (`2×5` shrouded Eurorack power header) and `C1`, `C2` (`1 µF 63 V` `P=5mm` box film capacitors) — LCSC-verified, hand-soldered on the rear after PCBA; plus `TP1`–`TP8` (`Ronghe RH-5001`, **`DNP`**) optional rear-side test points.
  - **`F.Cu` Front-Panel Manual THT (`8` parts):** `J1`–`J3` (3.5 mm mono jacks), `RV1`–`RV4` (`A100k`, `A50k`, `A1M`, `B10k` 9 mm vertical potentiometers), and `D4` (3 mm indicator LED) — excluded from JLCPCB SMT BOM, fitted into the front panel and hand-soldered later.

---

## 1. BOM & Cost Summary (Live JLCPCB / LCSC Pricing)

| Assembly Group | Side / Process | Unique BOM Lines | Total Qty / Board | Raw Parts Cost / Board (USD) | JLCPCB Feeder Fees / Order (USD) | Notes |
|---|---|---:|---:|---:|---:|---|
| **JLCPCB Basic SMT** | `B.Cu` Economic PCBA | `15` | `39` | `$0.1654` | `$0.00` | Pre-loaded (`$0` feeder setup fee) |
| **JLCPCB Preferred Extended SMT** | `B.Cu` Economic PCBA | `1` | `1` | `$0.0041` | `$0.00` | `R14` (`4.7 MΩ` `0603`, `$0` setup fee) |
| **JLCPCB Extended SMT** | `B.Cu` Economic PCBA | `4` | `9` | `$0.7060` | `$12.00` | `4 × $3.00` (`TL074HIDR`, `BAT54S`, `47 µF`, `1 kΩ 2512`) |
| **Subtotal — JLCPCB SMT PCBA (`B.Cu`)** | **Single-Sided Reflow** | **`20`** | **`49`** | **`$0.8755`** | **`$12.00`** | **`$3.2755/board` @ 5 pcs · `$2.0755/board` @ 10 pcs** *(excl. bare PCB & base assembly/stencil)* |
| **Rear Manual THT (`B.Cu`)** | Hand-Solder (LCSC) | `2` | `3` | `$0.6555` | `—` | `J4` (`C53207560`) + `C1`, `C2` (`C328852` film) |
| **Rear Test Points (`B.Cu`, `DNP`)** | Optional Hand-Solder (LCSC) | `1` (`DNP`) | `8` (`DNP`) | `$0.0000` *(DNP)* | `—` | `TP1`–`TP8` (`C5199801` `Ronghe RH-5001`, `DNP`; `+$0.6704` @ 1+ or `+$0.6440` @ 5+ if populated) |
| **Front Panel LED (`F.Cu`)** | Hand-Solder (LCSC) | `1` | `1` | `$0.0360` | `—` | `D4` (`C85161` 3 mm green LED) |
| **Front Panel Controls (`F.Cu`)** | Hand-Solder (Eurorack) | `5` | `7` | *Vendor-dependent* | `—` | `3 × WQP-PJ398SM` jacks + `4 × Alpha RD901F` pots (`A100k`, `A50k`, `A1M`, `B10k`) |
| **Grand Total (Populated Build)** | `B.Cu` + `F.Cu` | **`28`** *(+1 DNP)* | **`60`** *(+8 DNP)* | **`$1.5670` + jacks/pots** | **`$12.00`** | `60` populated parts (`68` total footprints incl. `TP1`–`TP8` `DNP`, `170` pins) |

> **Cost-Saving Note (Optional `$3.00` Feeder Reduction):** Replacing `R21`, `R24` (`1 kΩ 2512 1 W`, Extended `C54315`, `$3.00` fee) with two `2 kΩ 1206 250 mW 1%` Basic resistors (`C17944`, `1206W4F2001T5E`, `$0.0077`, `1,578,804` in stock) in parallel per output (`4 ×` total) saves `$3.00` in feeder fees, though total power headroom drops from `1.00 W` (`51%` fault load) to `0.50 W` (`~102%` worst-case `22.5 V` continuous fault). Keeping `C54315` (`1 W 2512`) is recommended for Eurorack fault durability.

---

## 2. JLCPCB Single-Sided Economic PCBA BOM (`B.Cu` SMT Parts — `49` Placements)

All parts in this section are placed on **`B.Cu`** for automated single-sided JLCPCB Economic PCBA.

| Designator(s) | Qty | Comment / Value | Package / KiCad Footprint | LCSC Part # | MPN | Manufacturer | JLCPCB Class | Live JLCPCB Stock | Unit Price (USD) | Ext. Price (1×) | Feeder Fee | Circuit Role |
|---|---:|---|---|---|---|---|---|---:|---:|---:|---:|---|
| `U1`, `U2` | 2 | `TL074H` | `SOIC-14` (`Package_SO:SOIC-14_3.9x8.7mm_P1.27mm`) | `C2878713` | `TL074HIDR` | Texas Instruments | Extended | `465` | `$0.2558` | `$0.5116` | `$3.00` | Quad 40 V FET-input op-amps (`U1A`–`U1D`, `U2A`–`U2D`) |
| `D1`, `D2`, `D3`, `D5`, `D6` | 5 | `1N4148WS` | `SOD-323` (`Diode_SMD:D_SOD-323`) | `C2128` | `1N4148WS` | Jiangsu Changjing (JSCJ) | **Basic** | `3,310,175` | `$0.0100` | `$0.0500` | `$0.00` | `D1`/`D2` rectifier, `D3` peak diode, `D5` anti-sat clamp, `D6` LED clamp |
| `D7`, `D8` | 2 | `1N5819WS` | `SOD-323` (`Diode_SMD:D_SOD-323`) | `C191023` | `1N5819WS` | Guangdong Hottech | **Basic** | `5,672,689` | `$0.0119` | `$0.0238` | `$0.00` | `±12 V` reverse-polarity Schottky protection (`40 V, 1 A`) |
| `D9`, `D10`, `D11` | 3 | `BAT54S` | `SOT-23` (`Package_TO_SOT_SMD:SOT-23`) | `C47546` | `BAT54S,215` | Nexperia | Extended | `430,138` | `$0.0200` | `$0.0600` | `$3.00` | Dual series Schottky ESD/rail clamps (`IN`, `OUT`, `INV_OUT`) |
| `R1`, `R4`, `R6`, `R7`, `R9`, `R13`, `R22`, `R23`, `R25`, `R26` | 10 | `10k` | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C25804` | `0603WAF1002T5E` | UNI-ROYAL | **Basic** | `42,821,833` | `$0.0017` | `$0.0170` | `$0.00` | `10 kΩ ±1% 100 mW` input prot, gain gnd, rect, release min, `-1×` inv, LED div |
| `R5`, `R15`, `R16`, `R19`, `R20` | 5 | `100k` | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C25803` | `0603WAF1003T5E` | UNI-ROYAL | **Basic** | `13,100,877` | `$0.0029` | `$0.0145` | `$0.00` | `100 kΩ ±1% 100 mW` `U1A` gain fb (`R5`) + `U1D` diff amp (`R15`, `R16`, `R19`, `R20`) |
| `R8`, `R10` | 2 | `20k` | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C4184` | `0603WAF2002T5E` | UNI-ROYAL | **Basic** | `4,914,296` | `$0.0018` | `$0.0036` | `$0.00` | `20 kΩ ±1% 100 mW` `1.00×` rectifier feedforward (`R8`) & feedback (`R10`) |
| `R17`, `R18` | 2 | `6.8k` | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C23212` | `0603WAF6801T5E` | UNI-ROYAL | **Basic** | `1,285,991` | `$0.0018` | `$0.0036` | `$0.00` | `6.8 kΩ ±1% 100 mW` `OFFSET` (`B10k`) rail dividers (`±4.69 V` sweep) |
| `R28`, `R29` | 2 | `10R` | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C22859` | `0603WAF100JT5E` | UNI-ROYAL | **Basic** | `5,425,289` | `$0.0018` | `$0.0036` | `$0.00` | `10 Ω ±1% 100 mW` `±12 V` inrush/ripple RC damping resistors |
| `R21`, `R24` | 2 | `1k 1W` | `2512` (`Resistor_SMD:R_2512_6332Metric`) | `C54315` | `25121WF1001T4E` | UNI-ROYAL | Extended | `52,582` | `$0.0336` | `$0.0672` | `$3.00` | `1 kΩ ±1% 1 W` fault-rated `OUT`/`INV_OUT` build-out resistors |
| `R27` | 1 | `1k` | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C21190` | `0603WAF1001T5E` | UNI-ROYAL | **Basic** | `40,728,395` | `$0.0016` | `$0.0016` | `$0.00` | `1 kΩ ±1% 100 mW` LED constant-current sense resistor (`0.5 mA/V`) |
| `R2` | 1 | `4.7k` | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C23162` | `0603WAF4701T5E` | UNI-ROYAL | **Basic** | `19,374,141` | `$0.0028` | `$0.0028` | `$0.00` | `4.7 kΩ ±1% 100 mW` `GAIN` pot floor (`+0.45×` minimum gain) |
| `R12` | 1 | `150R` | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C22808` | `0603WAF1500T5E` | UNI-ROYAL | **Basic** | `1,027,005` | `$0.0015` | `$0.0015` | `$0.00` | `150 Ω ±1% 100 mW` minimum attack current-limiting resistor |
| `R11` | 1 | `200k` | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C25811` | `0603WAF2003T5E` | UNI-ROYAL | **Basic** | `1,659,651` | `$0.0019` | `$0.0019` | `$0.00` | `200 kΩ ±1% 100 mW` `U2C` peak-detector feedback from `U2D` buffer |
| `R3` | 1 | `1M` | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C22935` | `0603WAF1004T5E` | UNI-ROYAL | **Basic** | `5,686,105` | `$0.0018` | `$0.0018` | `$0.00` | `1 MΩ ±1% 100 mW` `U1A +` open-wiper pull-down |
| `R14` | 1 | `4.7M` | `0603` (`Resistor_SMD:R_0603_1608Metric`) | `C23163` | `0603WAF4704T5E` | UNI-ROYAL | **Pref. Ext.** | `185,543` | `$0.0041` | `$0.0041` | `$0.00` | `4.7 MΩ ±1% 100 mW` `Release` open-wiper safety bleed |
| `C3`, `C4` | 2 | `47uF 35V` | `SMD,D6.3xL5.4mm` (`Capacitor_SMD:CP_Elec_6.3x5.4`) | `C2836440` | `RVT47UF35V67RV0039` | KNSCHA | Extended | `332,900` | `$0.0336` | `$0.0672` | `$3.00` | `47 µF 35 V ±20%` protected `±12 V` bulk rail electrolytic caps |
| `C5`, `C6`, `C7`, `C8` | 4 | `100nF 50V` | `0603` (`Capacitor_SMD:C_0603_1608Metric`) | `C14663` | `CC0603KRX7R9BB104` | YAGEO | **Basic** | `53,435,508` | `$0.0056` | `$0.0224` | `$0.00` | `100 nF 50 V X7R ±10%` local IC decoupling at `U1` & `U2` pins `4`/`11` |
| `C9` | 1 | `22pF 50V` | `0603` (`Capacitor_SMD:C_0603_1608Metric`) | `C1653` | `CL10C220JB8NNNC` | Samsung Electro-Mechanics | **Basic** | `2,750,711` | `$0.0089` | `$0.0089` | `$0.00` | `22 pF 50 V C0G ±5%` `U1A` HF compensation (`f_-3dB = 72 kHz`) |
| `C10` | 1 | `100pF 50V` | `0603` (`Capacitor_SMD:C_0603_1608Metric`) | `C14858` | `CL10C101JB8NNNC` | Samsung Electro-Mechanics | **Basic** | `3,044,717` | `$0.0084` | `$0.0084` | `$0.00` | `100 pF 50 V C0G ±5%` `U2C` peak-detector loop stabilization (`>70°` PM) |

### Verified Drop-In SMT Alternatives
- **`D1`–`D3`, `D5`, `D6` (`SOD-123` larger alt):** `C81598` (`1N4148W`, ST/Semtech, `SOD-123`, **Basic**, `4,501,771` stock, `$0.0123`).
- **`D7`, `D8` (`SOD-123` larger alt):** `C8598` (`B5819W SL`, JSCJ, `SOD-123`, **Basic**, `823,629` stock, `$0.0251`).
- **`D9`–`D11` (`BAT54S` alt MPNs):** `C19726` (`BAT54SLT1G`, onsemi, `SOT-23`, Extended, `406,747` stock, `$0.0231`) or `C12765` (`LBAT54SLT1G`, LRC, `SOT-23`, Extended, `227,898` stock, `$0.0135`).
- **`C3`, `C4` (`22 µF 50 V` alt):** `C2836438` (`RVT22UF50V67RV0028`, KNSCHA, `SMD,D6.3xL5.4mm`, Extended, `124,555` stock, `$0.0406`).

---

## 3. Rear `B.Cu` Manual Through-Hole BOM (`3` Populated + `8` `DNP` Test Points — Hand-Soldered Later)

Excluded from the JLCPCB SMT PCBA BOM (`JLCPCB_Class = "Manual THT"`). Placed on **`B.Cu`** (rear side) so `F.Cu` stays exclusively reserved for front-panel controls.

| Designator(s) | Qty | Status | Value / Spec | Package / KiCad Footprint | LCSC Part # | MPN | Manufacturer | Live JLCPCB / LCSC Stock | Unit Price (USD) | Ext. Price (1×) | Circuit Role |
|---|---:|---|---|---|---|---|---|---:|---:|---:|---|
| `J4` | 1 | Populate | `2×5P 2.54mm` Shrouded Keyed IDC Header | `Plugin, P=2.54mm` (`Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical`) | `C53207560` | `IDC2.54-2*5PZ` | JXTCONN | `2,060` / `1,920` | `$0.1241` | `$0.1241` | Standard 10-pin Doepfer A-100 Eurorack power header on `B.Cu` |
| `C1`, `C2` | 2 | Populate | `1uF 63V` ±5% Box Film (PET) | `Plugin, P=5mm` (`Capacitor_THT:C_Rect_L7.2mm_W5.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2`) | `C328852` | `C241J105J2SA201` | Xiamen Faratronic | `20,135` / `18,180` | `$0.2657` | `$0.5314` | `C1` AC input coupling; `C2` envelope timing cap (zero DC-bias loss/microphonics; no `1 µF` SMD film stocked at JLCPCB) |
| `TP1`–`TP8` | 8 | **`DNP`** | `2.5mm` Black Pin-Type Test Point (`4.6 mm` H, `Ø 1.0 mm` drill) | Through-Board (`TestPoint:TestPoint_Keystone_5000-5004_Miniature`) | `C5199801` | `RH-5001` | Ronghe | `100,860` / `98,140` | `$0.0838` *(`$0.0805` @ 5+)* | `$0.0000` *(`$0.6704` if pop.)* | Optional rear `B.Cu` test points (`+12V_PROT`, `-12V_PROT`, `GND`, `V_GAIN`, `V_RECT`, `V_ENV_BUF`, `V_OUT_BUF`, `V_INV_BUF`) — **marked `DNP`** |

- **`RH-5001` (`C5199801`) Verification & Mechanical Notes:**
  - Verified live via JLCPCB (`100,860` stock) and LCSC (`98,140` stock; [LCSC Datasheet PDF](https://datasheet.lcsc.com/datasheet/pdf/4adec3e10718fa4444bfddc0d5622733.pdf?productCode=C5199801)): `2.5 mm` OD black high-temperature nylon bead (`3.0 mm` bead height, `4.6 mm` above-board height, `7.6 ± 0.4 mm` overall length), silver-plated phosphor-bronze `0.25 mm` split spring pins splayed to `1.4 mm` for snap-fit retention into `TestPoint:TestPoint_Keystone_5000-5004_Miniature` (`Ø 2.0 mm` pad, `Ø 1.0 mm` drill, `Ø 3.3 mm` courtyard).
  - Marked **`DNP`** (`dnp=True`, `exclude_from_bom=True`) so standard PCBA orders skip them and bare `1.0 mm` plated holes remain probeable from `B.Cu`; if soldering `RH-5001` in optionally, order `8 × C5199801` per board, insert from `B.Cu`, solder on `F.Cu`, and trim the `~3.0 mm` protruding spring legs flush on `F.Cu`.

- **Verified `1 µF 63 V P=5mm` Film Alternatives:**
  - Budget: `C3975271` (`MEB105J63V82CB0235`, KNSCHA, `10,677` JLCPCB / `8,610` LCSC stock, `$0.1911`).
  - Premium: `C92673` (`MKS2C041001F00JSSD`, WIMA, `5,573` stock, `$1.1437`).

---

## 4. Front `F.Cu` Panel-Facing Manual Through-Hole BOM (`8` Parts — Hand-Soldered Later)

Placed strictly on **`F.Cu`** facing the `3U` front panel and excluded from the JLCPCB SMT PCBA BOM.

| Designator(s) | Qty | Value / Taper | KiCad Footprint | LCSC Status | Primary MPN / Sourcing | Unit Price (Est.) | Circuit Role & Pinout Notes |
|---|---:|---|---|---|---|---|---|
| `J1`, `J2`, `J3` | 3 | `3.5mm Mono Jack` (Switched) | `Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | `0` stock on JLCPCB/LCSC *(Manual Eurorack)* | QingPu `WQP-PJ398SM` ("Thonkiconn", M6 bushing; Thonk / SynthCube / Tayda) | `~$0.45–$0.65` | `J1` (`IN`, `TN→GND`), `J2` (`OUT`, `TN=NC`), `J3` (`INV_OUT`, `TN=NC`) |
| `RV1` | 1 | `A100k` (100 kΩ Log) | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | `0` stock on JLCPCB/LCSC *(Manual Eurorack)* | Taiwan Alpha `RD901F-40-15F-A100K` (or `RV09AF-40-15F-A100K`; Thonk / Tayda / LoveMySwitches) | `~$0.80–$1.20` | `GAIN` input attenuator (`+0.45×` to `+10.04×`) |
| `RV2` | 1 | `A50k` (50 kΩ Log) | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | `0` stock on JLCPCB/LCSC *(Manual Eurorack)* | Taiwan Alpha `RD901F-40-15F-A50K` (or `RV09AF-40-15F-A50K`) | `~$0.80–$1.20` | `ATK` attack time control (`0.15 ms`–`50.15 ms`) |
| `RV3` | 1 | `A1M` (1 MΩ Log) | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | `0` stock on JLCPCB/LCSC *(Manual Eurorack)* | Taiwan Alpha `RD901F-40-15F-A1M` (or `RV09AF-40-15F-A1M`) | `~$0.80–$1.20` | `Release` decay time control (`10 ms`–`835 ms` `τ`) |
| `RV4` | 1 | `B10k` (10 kΩ Linear) | `Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` | `0` stock on JLCPCB/LCSC *(Manual Eurorack)* | Taiwan Alpha `RD901F-40-15F-B10K` (or center-detent `-00D` variant; `RV09AF-40-15F-B10K`) | `~$0.80–$1.20` | `OFFSET` DC shift control (`-4.69 V` CCW to `+4.69 V` CW) |
| `D4` | 1 | `3mm LED` (Green) | `LED_THT:LED_D3.0mm` | **Verified LCSC: `C85161`** (`36,941` JLCPCB stock) | Everlight `204-10SYGD/S530-E3` (`573 nm`, `100 mcd`, `2 V` — or any 3 mm LED) | `$0.0360` | Envelope indicator (`0–5 mA` constant-current sink; `Pin 1` rect = Cathode) |

- **Verified `D4` `3 mm` LED Alternatives on LCSC:** `C84774` (Everlight `204-10SDRD/S530-A3-L`, Red, `46,956` JLCPCB stock, `$0.0356`) or `C85160` (Everlight `204-10UYD/S530-A3-L`, Yellow, `36,051` JLCPCB stock, `$0.0365`). Because `U2B` regulates current (`0.5 mA/V`) independent of `V_f`, any LED color behaves identically without changing resistor values.

---

## 5. JLCPCB SMT Assembly CSV Export Preview (`B.Cu` Only)

Matches JLCPCB's required 4-column upload schema (`Comment,Designator,Footprint,LCSC Part #`), containing only the `49` `B.Cu` SMT placements (`Manual THT` and `DNP` parts `J1`–`J4`, `RV1`–`RV4`, `C1`, `C2`, `D4`, `TP1`–`TP8` omitted):

```csv
Comment,Designator,Footprint,LCSC Part #
TL074H,"U1, U2",SOIC-14_3.9x8.7mm_P1.27mm,C2878713
1N4148WS,"D1, D2, D3, D5, D6",D_SOD-323,C2128
1N5819WS,"D7, D8",D_SOD-323,C191023
BAT54S,"D9, D10, D11",SOT-23,C47546
10k,"R1, R4, R6, R7, R9, R13, R22, R23, R25, R26",R_0603_1608Metric,C25804
100k,"R5, R15, R16, R19, R20",R_0603_1608Metric,C25803
20k,"R8, R10",R_0603_1608Metric,C4184
6.8k,"R17, R18",R_0603_1608Metric,C23212
10R,"R28, R29",R_0603_1608Metric,C22859
1k 1W,"R21, R24",R_2512_6332Metric,C54315
1k,R27,R_0603_1608Metric,C21190
4.7k,R2,R_0603_1608Metric,C23162
150R,R12,R_0603_1608Metric,C22808
200k,R11,R_0603_1608Metric,C25811
1M,R3,R_0603_1608Metric,C22935
4.7M,R14,R_0603_1608Metric,C23163
47uF 35V,"C3, C4",CP_Elec_6.3x5.4,C2836440
100nF 50V,"C5, C6, C7, C8",C_0603_1608Metric,C14663
22pF 50V,C9,C_0603_1608Metric,C1653
100pF 50V,C10,C_0603_1608Metric,C14858
```

---

## 6. JLCPCB Ordering & Hand-Assembly Checklist

1. **JLCPCB Order Options:** Select **2-layer PCB**, **Economic PCBA**, **Assembly Side: Bottom (`B.Cu`) only**, and upload the `B.Cu`-only BOM CSV and filtered `B.Cu` CPL (`--bom` filtered to exclude `J1`–`J4`, `RV1`–`RV4`, `C1`, `C2`, `D4`, `TP1`–`TP8` (`DNP`), fiducials, and mounting holes).
2. **Verify `TL074HIDR` (`C2878713`) Stock Before Ordering:** Live stock was `465` pcs at verification time; if ordering a large batch (`> 200` boards), confirm live inventory or pre-book stock on JLCPCB.
3. **Verify Component Rotations in JLCPCB 3D Preview:** Confirm Pin `1` orientation for `SOIC-14` (`U1`, `U2`), `SOT-23` (`D9`–`D11`), `SOD-323` cathode bars (`D1`–`D3`, `D5`–`D8`), and `CP_Elec_6.3x5.4` polarity stripes (`C3`, `C4`).
4. **Post-PCBA Hand Soldering:**
   - First solder rear `B.Cu` THT parts (`J4`, `C1`, `C2`) and, if populating the optional `DNP` test points, snap `TP1`–`TP8` (`Ronghe RH-5001`, `C5199801`) in from `B.Cu`, solder on `F.Cu`, and trim all leads flush on `F.Cu`.
   - Next place front `F.Cu` panel components (`J1`–`J3`, `RV1`–`RV4`, `D4`) loosely, mount the `3U` front panel with M6/M7 hardware to set exact alignment and `~10.5 mm` standoff, seat `D4` into its `3.2 mm` cutout, and solder all `F.Cu` pins from `B.Cu`.
