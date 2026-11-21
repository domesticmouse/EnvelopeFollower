# Envelope Follower — Improved Netlist, JLCPCB BOM, Capture Guide & Silkscreen Schedule

This reference provides the complete Bill of Materials (`49` `B.Cu` SMD + `11` populated Manual/Consigned THT + `8` optional `DNP` test points + `3` `DNP` `B.Cu` optical fiducials = `71` footprints), ready-to-upload 19-line `jlcpcb_bom.csv`, **42-net** connection list, 7-step manual KiCad capture guide, and dual-sided silkscreen schedule for the improved Eurorack Envelope Follower ([Stage 2](../tutorial/stage-2-circuit-upgrades.md) & [Stage 3](../tutorial/stage-3-bom-and-dfm.md)).

---

## 1. Analog Improvements & Eurorack Protections Summary

1. **Dual `TL074HIDR` Layout (All 8 Op-Amp Channels Active)**:
   - **`U1` (`TL074H`)**: `U1A` Protected Inverting Preamp (`-0.10×` to `-9.17×`), `U1B` Precision Half-Wave Rectifier (`BAT54S`), `U1C` `0.1%`-Matched `1.000×` Summing Rectifier (`R8A+R8B = 20 kΩ`), `U1D` Output Buffer & Linearized `OFFSET` Summer (`1.476×–1.529×`, `±5.09 V`).
   - **`U2` (`TL074H`)**: `U2A` Unity-Gain Inverting Output (`INV_OUT`), `U2B` Active In-Loop Precision LED Current Sink (`R_LED = 2.2 kΩ` + `D_LED_CLAMP`), `U2C` Active Zero-Deadzone Peak Detector (`D3 = 1N4148WS`, `< 5 mV` deadband), `U2D` `101 kΩ` Unity-Gain Input Buffer.
2. **Power Entry, Reverse-Polarity & RC Bus Filtering (`J4`, `D_PWR_P`, `D_PWR_N`, `R_PWR_P`, `R_PWR_N`, `C3`, `C4`, `C_DEC1`–`C_DEC4`)**:
   - Shrouded keyed `2×5` IDC header `J4` (`B.Cu`), series `B5819W` Schottky diodes + `10 Ω` `250 mW` (`1206`) series resistors feeding `22 µF 50 V` SMD electrolytics (`C3`, `C4`, $f_c = 723\text{ Hz}$, internal `≈ ±11.55 V`), plus `4× 100 nF 50 V X7R` local IC decoupling caps (`C_DEC1`–`C_DEC4`) within `< 3–5 mm` of `U1`/`U2` pins `4` and `11`.
3. **Input Impedance, Gain Floor & HF Roll-Off (`R_IN_PROT`, `C1`, `R1`, `D_IN`, `R_IN_BUF`, `R_GAIN_MIN`, `R_GAIN_FAIL`, `C_HF`)**:
   - `J1.TN → GND` eliminates unpatched hum; `U2D` isolates `C1` (`1 µF` PET film) + `R1` (`100 kΩ`) for $Z_{\text{in}} = 101\text{ k}\Omega$ and $f_c = 1.58\text{ Hz}$, clamped by `D_IN` (`BAV99`). `R_GAIN_MIN` (`1 kΩ`) + `R_GAIN_FAIL` (`1 MΩ`) + `C_HF` (`47 pF C0G`) establish a `-0.10×` floor, bounded `-100×` open-wiper fail-safe, and `36.9 kHz` HF pole.
4. **Low-Impedance Linear `OFFSET` & Zero-Droop Envelope Hold (`RV4`, `R11`–`R13`, `R15`, `C2`, `R_ATK_MIN`, `R_ENV_PROT`)**:
   - Deleting `R9` eliminates the `9.1%` release-dependent droop on `C2` (`1 µF` PET film, zero microphonics/bias collapse), while `R_ATK_MIN` (`470 Ω`) limits peak surge current. Deleting `R14` and scaling `RV4` to `B10k` (`R11 = R12 = 1 kΩ`, `R13 = 18 kΩ`) yields `3.5%` gain variation across `±5.09 V` linear offset (`CW = +OUT`).
5. **Clash-Rated Outputs, Midpoint ESD Clamps & In-Loop Feedback (`R16A/B`, `R19A/B`, `D_OUT`, `D_INV_OUT`, `C_OUT1`, `C_OUT2`)**:
   - Split `470 Ω + 470 Ω` `0.5 W` (`1210`) resistors survive continuous `±12 V` output-to-output clashes (`1.86×` margin), midpoint `BAV99` clamps (`OUT_CLAMP`, `INV_OUT_CLAMP`) shunt ESD spikes to `±12V`, and in-loop `10 kΩ` feedback (`R15`/`R18`) with `100 pF C0G` HF caps (`C_OUT1`/`C_OUT2`) locks `0.00%` `OUT`/`INV_OUT` mismatch.

---

## 2. Full Bill of Materials (JLCPCB `B.Cu` SMD + Manual THT)

### Integrated Circuits (JLCPCB `B.Cu` SMD)

| Ref | Qty | Value / Part | Package | KiCad Footprint | MPN | Manufacturer | LCSC # | Class | Unit Price (USD) | Circuit Role |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| `U1`, `U2` | 2 | `TL074H` Quad Op-Amp | `SOIC-14` | `Package_SO:SOIC-14_3.9x8.7mm_P1.27mm` | `TL074HIDR` | Texas Instruments | **`C2878713`** | Extended | \$0.2552 | All 8 op-amp stages (`U1A`–`U1D`, `U2A`–`U2D`) |

*Pin-compatible `SOIC-14` fallbacks if `C2878713` is out of stock: TI `TL074CDR` (`C12594`, Extended) or STMicroelectronics `TL074CDT` (`C6963`, Extended).*

### Diodes (JLCPCB `B.Cu` SMD)

| Ref | Qty | Value / Spec | Package | KiCad Footprint | MPN | Manufacturer | LCSC # | Class | Unit Price (USD) | Circuit Role |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| `D_PWR_P`, `D_PWR_N` | 2 | `B5819W` (`40 V`, `1 A` Schottky) | `SOD-123` | `Diode_SMD:D_SOD-123` | `B5819W SL` | Changjing Elec | **`C8598`** | **Basic** | \$0.0250 | `+12V` and `-12V` series reverse-polarity protection |
| `D1_D2` | 1 | `BAT54S` (`30 V`, `200 mA` dual series) | `SOT-23` | `Package_TO_SOT_SMD:SOT-23` | `BAT54S,215` | Nexperia | **`C47546`** | Extended | \$0.0200 | Precision half-wave rectifier (`D1` + `D2`) |
| `D3`, `D_LED_CLAMP` | 2 | `1N4148WS` (`100 V` low-leakage) | `SOD-323` | `Diode_SMD:D_SOD-323` | `1N4148WS` | Changjing Elec | **`C2128`** | **Basic** | \$0.0100 | Active peak detector (`D3`), `D4` reverse clamp (`D_LED_CLAMP`) |
| `D_IN`, `D_OUT`, `D_INV_OUT` | 3 | `BAV99` (`100 V` dual series) | `SOT-23` | `Package_TO_SOT_SMD:SOT-23` | `BAV99,215` | Nexperia | **`C2500`** | **Basic** | \$0.0108 | Dual series `±12V` ESD/overvoltage clamps (`IN_AC`, `OUT_CLAMP`, `INV_OUT_CLAMP`) |

### Capacitors (JLCPCB `B.Cu` SMD)

| Ref | Qty | Value / Spec | Package | KiCad Footprint | MPN | Manufacturer | LCSC # | Class | Unit Price (USD) | Circuit Role |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| `C_DEC1`–`C_DEC4` | 4 | `100 nF` `50 V` X7R $\pm 10\%$ | `0603` | `Capacitor_SMD:C_0603_1608Metric` | `CC0603KRX7R9BB104` | YAGEO | **`C14663`** | **Basic** | \$0.0055 | Local `V+`/`V-` decoupling (`< 3–5 mm` from `U1`/`U2`) |
| `C_HF` | 1 | `47 pF` `50 V` C0G/NP0 $\pm 5\%$ | `0603` | `Capacitor_SMD:C_0603_1608Metric` | `CL10C470JB8NNNC` | Samsung | **`C1671`** | **Basic** | \$0.0063 | `U1A` preamp ultrasonic/RF compensation (`36.9 kHz`) |
| `C_OUT1`, `C_OUT2` | 2 | `100 pF` `50 V` C0G/NP0 $\pm 5\%$ | `0603` | `Capacitor_SMD:C_0603_1608Metric` | `CL10C101JB8NNNC` | Samsung | **`C14858`** | **Basic** | \$0.0084 | `U1D` & `U2A` local HF compensation for in-loop feedback |
| `C3`, `C4` | 2 | `22 µF` `50 V` Al Electrolytic $\pm 20\%$ | `D6.3×L5.4mm` | `Capacitor_SMD:CP_Elec_6.3x5.4` | `RVT22UF50V67RV0028` | KNSCHA | **`C2836438`** | Extended | \$0.0405 | `+12V` (`C3`) and `-12V` (`C4`, `+` to `GND`) bulk supply filtering |

### Fixed Resistors (JLCPCB `B.Cu` SMD — 30 Total Across 10 Lines)

| Ref | Qty | Value / Spec | Package | KiCad Footprint | MPN | Manufacturer | LCSC # | Class | Unit Price (USD) | Circuit Role |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| `R_PWR_P`, `R_PWR_N` | 2 | `10 Ω` `1%` `250 mW` | `1206` | `Resistor_SMD:R_1206_3216Metric` | `1206W4F100JT5E` | UNI-ROYAL | **`C17903`** | **Basic** | \$0.0061 | `+12V` and `-12V` series rail RC filter & inrush damping |
| `R_ATK_MIN` | 1 | `470 Ω` `1%` `100 mW` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF4700T5E` | UNI-ROYAL | **`C23179`** | **Basic** | \$0.0019 | Minimum attack surge/ringing limiter (`0.47 ms` floor) |
| `R16A`, `R16B`, `R19A`, `R19B` | 4 | `470 Ω` `1%` `0.5 W` | `1210` | `Resistor_SMD:R_1210_3225Metric` | `RTT124700FTP` | RALEC | **`C333193`** | Extended | \$0.0172 | Split clash-rated `0.5 W` isolation on `OUT` & `INV_OUT` |
| `R_IN_PROT`, `R_IN_BUF`, `R_GAIN_MIN`, `R11`, `R12` | 5 | `1 kΩ` `1%` `100 mW` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1001T5E` | UNI-ROYAL | **`C21190`** | **Basic** | \$0.0016 | Input ESD, `U2D+`, `GAIN` floor, `OFFSET` end limits |
| `R_LED` | 1 | `2.2 kΩ` `1%` `100 mW` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF2201T5E` | UNI-ROYAL | **`C4190`** | **Basic** | \$0.0018 | Active LED current-setting sink resistor (`0–4.5 mA`) |
| `R2`, `R10`, `R_ENV_PROT`, `R15`, `R17`, `R18`, `R20` | 7 | `10 kΩ` `1%` `100 mW` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1002T5E` | UNI-ROYAL | **`C25804`** | **Basic** | \$0.0017 | Preamp in, `Release` floor, `U1D+` prot, `U1D`/`U2A`/`U2B` networks |
| `R3`, `R4`, `R5`, `R6`, `R7`, `R8A`, `R8B` | 7 | `10 kΩ` `±0.1%` `25 ppm/°C` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `RT0603BRD0710KL` | YAGEO | **`C95204`** | Extended | \$0.0255 | Precision `0.1%` matched `1.000×` full-wave rectifier |
| `R13` | 1 | `18 kΩ` `1%` `100 mW` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1802T5E` | UNI-ROYAL | **`C25810`** | **Basic** | \$0.0027 | `OFFSET` summing resistor (`±5.09 V` range) |
| `R1` | 1 | `100 kΩ` `1%` `100 mW` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1003T5E` | UNI-ROYAL | **`C25803`** | **Basic** | \$0.0029 | Input AC-coupling `GND` bias ($Z_{\text{in}} = 101\text{ k}\Omega$) |
| `R_GAIN_FAIL` | 1 | `1 MΩ` `1%` `100 mW` | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1004T5E` | UNI-ROYAL | **`C22935`** | **Basic** | \$0.0018 | Open-pot-wiper fail-safe across `RV1` (`-100×` bound) |

### Manual Through-Hole (THT), Optional `DNP` Test Points & Fiducials

| Ref | Qty | Value / Spec | Component Type | KiCad Footprint / Mounting Side | LCSC # / Source | Circuit Role |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| `C1`, `C2` | 2 | `1 µF` `100 V` `±5%` PET Film | Box Film (`P=5mm`, Non-Pol.) | `Capacitor_THT:C_Rect_L7.2mm_W6.0mm_P5.00mm` (`B.Cu`) | `C125397` (TDK `B32529D1105J000`) | `C1`: input AC coupling; `C2`: hold cap (zero microphonics/droop) |
| `J4` | 1 | `IDC 2x5P 2.54mm` | Shrouded Keyed IDC Header | `Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical` (`B.Cu`) | `C53207560` (`IDC2.54-2*5PZ`) | Eurorack $\pm 12\text{ V}$ power entry (`-12V` Pins 1–2) |
| `D4` | 1 | `3 mm` Red LED | Radial THT LED | `LED_THT:LED_D3.0mm` (`F.Cu`) | `C99771` (`204-10SURD/S530-A3-L`) | Active envelope level indicator |
| `J1`–`J3` | 3 | `WQP-PJ398SM` (`3.5 mm` Mono TS) | Vertical THT Thonkiconn | `Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` (`F.Cu`) | Consigned | `J1`: `IN` (`TN → GND`), `J2`: `OUT` (`TN = NC`), `J3`: `INV_OUT` (`TN = NC`) |
| `RV1` | 1 | `A100k` (`100 kΩ` Audio/Log) | 9 mm Vertical Pot (`RK09K`) | `Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical` (`F.Cu`) | Consigned (`RV09AF-40-20K-A104`) | `GAIN` (`-0.10×` to `-9.17×`) |
| `RV2` | 1 | `A50k` (`50 kΩ` Audio/Log) | 9 mm Vertical Pot (`RK09K`) | `Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical` (`F.Cu`) | Consigned (`RV09AF-40-20K-A503`) | `ATK` (`0.47 ms` to `50.5 ms`) |
| `RV3` | 1 | `A1M` (`1 MΩ` Audio/Log) | 9 mm Vertical Pot (`RK09K`) | `Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical` (`F.Cu`) | Consigned (`RV09AF-40-20K-A105`) | `REL` (`10 ms` to `1.01 s`) |
| `RV4` | 1 | `B10k` (`10 kΩ` Linear) | 9 mm Vertical Pot (`RK09K`) | `Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical` (`F.Cu`) | Consigned (`RV09AF-40-20K-B103`) | `OFFSET` (`±5.09 V`, `CW = +OUT`) |
| `TP1`–`TP8` (**`DNP`**) | 8 (`DNP`) | `RH-5001` (`2.5 mm` Pin) | Miniature THT Test Loop (`1.0 mm` drill) | `TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm` (`B.Cu`, **`DNP`**) | `C5199801` (Ronghe, **`DNP`**) | `TP1`: `GND`; `TP2`: `+12V`; `TP3`: `-12V`; `TP4`: `IN_BUF`; `TP5`: `PREAMP_OUT`; `TP6`: `RECT_OUT`; `TP7`: `OUT_CLAMP`; `TP8`: `INV_OUT_CLAMP` |
| `FID1`–`FID3` (**`DNP`**) | 3 (`DNP`) | `Fiducial` (`1 mm / 2 mm`) | Optical SMT Fiducial | `Fiducial:Fiducial_1mm_Mask2mm` (`B.Cu`, **`DNP`**) | — (Copper/Mask only) | Pick-and-place vision alignment on `B.Cu` (excluded from BOM/CPL) |

### Ready-to-Upload `jlcpcb_bom.csv` (49 SMD Parts Across 19 Lines)

```csv
Comment,Designator,Footprint,LCSC Part #
TL074H,"U1, U2",SOIC-14_3.9x8.7mm_P1.27mm,C2878713
B5819W,"D_PWR_P, D_PWR_N",D_SOD-123,C8598
BAT54S,D1_D2,SOT-23,C47546
1N4148WS,"D3, D_LED_CLAMP",D_SOD-323,C2128
BAV99,"D_IN, D_OUT, D_INV_OUT",SOT-23,C2500
10R,"R_PWR_P, R_PWR_N",R_1206_3216Metric,C17903
470R,R_ATK_MIN,R_0603_1608Metric,C23179
470R 0.5W,"R16A, R16B, R19A, R19B",R_1210_3225Metric,C333193
1k,"R_IN_PROT, R_IN_BUF, R_GAIN_MIN, R11, R12",R_0603_1608Metric,C21190
2.2k,R_LED,R_0603_1608Metric,C4190
10k,"R2, R10, R_ENV_PROT, R15, R17, R18, R20",R_0603_1608Metric,C25804
10k 0.1%,"R3, R4, R5, R6, R7, R8A, R8B",R_0603_1608Metric,C95204
18k,R13,R_0603_1608Metric,C25810
100k,R1,R_0603_1608Metric,C25803
1M,R_GAIN_FAIL,R_0603_1608Metric,C22935
100nF,"C_DEC1, C_DEC2, C_DEC3, C_DEC4",C_0603_1608Metric,C14663
47pF C0G,C_HF,C_0603_1608Metric,C1671
100pF C0G,"C_OUT1, C_OUT2",C_0603_1608Metric,C14858
22uF 50V,"C3, C4",CP_Elec_6.3x5.4,C2836438
```

---

## 3. Complete 42-Net Node Connectivity Table

*(Pin conventions: `U1`/`U2` = `TL074H`; 2-pin passives = `.1`, `.2`; polarized caps = `.+` (pin 1), `.-` (pin 2); 2-pin diodes & LED = `.K` (pin 1), `.A` (pin 2); `SOT-23` dual diodes (`BAT54S`, `BAV99`) = `.1` (`A1`), `.2` (`K2`), `.3` (`COM`); pots = `.1` (CCW), `.2` (wiper), `.3` (CW); jacks = `.S` (sleeve), `.T` (tip), `.TN` (tip-normal); test points = `.1`. `J2.TN` and `J3.TN` connect to `NC`.)*

| Net Name | Connected Component Terminals (with IC Pin Numbers) |
| :--- | :--- |
| `+12V_IN` | `J4` (pins `9`, `10`), `D_PWR_P` (`.A` / pin `2`) |
| `+12V_PROT` | `D_PWR_P` (`.K` / pin `1`), `R_PWR_P` (pin `1`) |
| `+12V` | `R_PWR_P` (pin `2`), `C3` (`+` / pin `1`), `C_DEC1` (pin `1`), `C_DEC3` (pin `1`), `U1` (pin `4` / $V_{CC+}$), `U2` (pin `4` / $V_{CC+}$), `D_IN` (pin `2` / `K2`), `D_OUT` (pin `2` / `K2`), `D_INV_OUT` (pin `2` / `K2`), `R11` (pin `1`), `TP2` (pin `1`) |
| `-12V_IN` | `J4` (pins `1`, `2`), `D_PWR_N` (`.K` / pin `1`) |
| `-12V_PROT` | `D_PWR_N` (`.A` / pin `2`), `R_PWR_N` (pin `1`) |
| `-12V` | `R_PWR_N` (pin `2`), `C4` (`-` / pin `2`), `C_DEC2` (pin `1`), `C_DEC4` (pin `1`), `U1` (pin `11` / $V_{CC-}$), `U2` (pin `11` / $V_{CC-}$), `D_IN` (pin `1` / `A1`), `D_OUT` (pin `1` / `A1`), `D_INV_OUT` (pin `1` / `A1`), `R12` (pin `1`), `TP3` (pin `1`) |
| `GND` | `J4` (pins `3`–`8`), `C3` (`-` / pin `2`), `C4` (`+` / pin `1`), `C_DEC1`–`C_DEC4` (pin `2`), `J1` (sleeve & `TN`), `R1` (pin `2`), `U1A` (pin `3` / `+`), `U1B` (pin `5` / `+`), `U1C` (pin `10` / `+`), `C2` (pin `2`), `RV3` (pins `2`, `3`), `J2` (sleeve), `U2A` (pin `3` / `+`), `J3` (sleeve), `R_LED` (pin `2`), `TP1` (pin `1`) |
| `IN_TIP` | `J1` (`T`), `R_IN_PROT` (pin `1`) |
| `IN_AC_PRE` | `R_IN_PROT` (pin `2`), `C1` (pin `1`) |
| `IN_AC` | `C1` (pin `2`), `R1` (pin `1`), `D_IN` (pin `3` / `COM`), `R_IN_BUF` (pin `1`) |
| `U2D_IN` | `R_IN_BUF` (pin `2`), `U2D` (pin `12` / `+`) |
| `IN_BUF` | `U2D` (pin `14` / out), `U2D` (pin `13` / `-`), `R2` (pin `1`), `TP4` (pin `1`) |
| `U1A_INV` | `R2` (pin `2`), `U1A` (pin `2` / `-`), `R_GAIN_MIN` (pin `1`), `R_GAIN_FAIL` (pin `1`), `C_HF` (pin `1`) |
| `GAIN_POT_1` | `R_GAIN_MIN` (pin `2`), `RV1` (pin `1`) |
| `PREAMP_OUT` | `U1A` (pin `1` / out), `RV1` (pins `2`, `3`), `R_GAIN_FAIL` (pin `2`), `C_HF` (pin `2`), `R3` (pin `1`), `R4` (pin `1`), `TP5` (pin `1`) |
| `U1B_INV` | `R3` (pin `2`), `U1B` (pin `6` / `-`), `R6` (pin `1`), `D1_D2` (pin `2` / `K2`) |
| `U1B_OUT` | `U1B` (pin `7` / out), `D1_D2` (pin `3` / `COM`) |
| `RECT_HW` | `D1_D2` (pin `1` / `A1`), `R6` (pin `2`), `R7` (pin `1`) |
| `FF_MID` | `R4` (pin `2`), `R5` (pin `1`) |
| `U1C_INV` | `R5` (pin `2`), `R7` (pin `2`), `U1C` (pin `9` / `-`), `R8A` (pin `1`) |
| `RECT_FB_MID` | `R8A` (pin `2`), `R8B` (pin `1`) |
| `RECT_OUT` | `U1C` (pin `8` / out), `R8B` (pin `2`), `U2C` (pin `10` / `+`), `TP6` (pin `1`) |
| `U2C_OUT` | `U2C` (pin `8` / out), `D3` (`.A` / pin `2`) |
| `ATK_IN` | `D3` (`.K` / pin `1`), `U2C` (pin `9` / `-`), `R_ATK_MIN` (pin `1`) |
| `ATK_POT_1` | `R_ATK_MIN` (pin `2`), `RV2` (pin `1`) |
| `ENV_NODE` | `RV2` (pins `2`, `3`), `C2` (pin `1`), `R10` (pin `1`), `R_ENV_PROT` (pin `1`), `R20` (pin `1`) |
| `REL_POT_TOP` | `R10` (pin `2`), `RV3` (pin `1`) |
| `U1D_IN` | `R_ENV_PROT` (pin `2`), `U1D` (pin `12` / `+`) |
| `OFF_TOP` | `R11` (pin `2`), `RV4` (pin `1`) |
| `OFF_BOT` | `R12` (pin `2`), `RV4` (pin `3`) |
| `OFF_WIPER` | `RV4` (pin `2`), `R13` (pin `1`) |
| `U1D_INV` | `R13` (pin `2`), `R15` (pin `1`), `C_OUT1` (pin `1`), `U1D` (pin `13` / `-`) |
| `U1D_OUT` | `U1D` (pin `14` / out), `C_OUT1` (pin `2`), `R16A` (pin `1`) |
| `OUT_CLAMP` | `R16A` (pin `2`), `R15` (pin `2`), `D_OUT` (pin `3` / `COM`), `R16B` (pin `1`), `R17` (pin `1`), `TP7` (pin `1`) |
| `OUT_TIP` | `R16B` (pin `2`), `J2` (`T`) |
| `U2A_INV` | `R17` (pin `2`), `R18` (pin `1`), `C_OUT2` (pin `1`), `U2A` (pin `2` / `-`) |
| `U2A_OUT` | `U2A` (pin `1` / out), `C_OUT2` (pin `2`), `R19A` (pin `1`) |
| `INV_OUT_CLAMP` | `R19A` (pin `2`), `R18` (pin `2`), `D_INV_OUT` (pin `3` / `COM`), `R19B` (pin `1`), `TP8` (pin `1`) |
| `INV_OUT_TIP` | `R19B` (pin `2`), `J3` (`T`) |
| `U2B_IN` | `R20` (pin `2`), `U2B` (pin `5` / `+`) |
| `U2B_OUT` | `U2B` (pin `7` / out), `D4` (`.A` / pin `2`), `D_LED_CLAMP` (`.K` / pin `1`) |
| `LED_K` | `D4` (`.K` / pin `1`), `D_LED_CLAMP` (`.A` / pin `2`), `U2B` (pin `6` / `-`), `R_LED` (pin `1`) |

---

## 4. Manual KiCad Schematic Capture Checklist

If capturing the schematic manually in KiCad instead of generating the netlist via SKiDL in [Stage 4](../tutorial/stage-4-skidl.md):

### Step 1: Project Setup & Op-Amp Allocation
- [ ] Create `EnvelopeFollower.kicad_pro` and open `EnvelopeFollower.kicad_sch` in KiCad 10.
- [ ] Place `+12V`, `-12V`, and `GND` power symbols (plus `PWR_FLAG` as needed for ERC).
- [ ] Place **`U1`** (`TL074`) and **`U2`** (`TL074`) including both power units (`Pin 4 = +12V`, `Pin 11 = -12V`).

### Step 2: Power Protection, Filtering & Decoupling (`Stage 0`)
- [ ] Place `J4` (`2x5` IDC header): Pins `1–2` (`-12V_IN`), Pins `3–8` (`GND`), Pins `9–10` (`+12V_IN`).
- [ ] Wire `+12V_IN` $\rightarrow$ `D_PWR_P` (`B5819W`, anode-to-cathode) $\rightarrow$ `R_PWR_P` (`10 Ω`) $\rightarrow$ `+12V`; wire `-12V_IN` $\rightarrow$ `D_PWR_N` (`B5819W`, cathode-to-anode) $\rightarrow$ `R_PWR_N` (`10 Ω`) $\rightarrow$ `-12V`.
- [ ] Wire bulk caps `C3` (`22 µF 50 V`: `+` to `+12V`, `-` to `GND`) and `C4` (`22 µF 50 V`: **`+` to `GND`**, `-` to `-12V`).
- [ ] Wire `100 nF` bypass caps `C_DEC1`/`C_DEC2` at `U1` pins `4`/`11` and `C_DEC3`/`C_DEC4` at `U2` pins `4`/`11`.
- [ ] Attach `DNP` test points `TP1` (`GND`), `TP2` (`+12V`), `TP3` (`-12V`).

### Step 3: Input Buffer (`U2D`) & Protected Preamp (`U1A`) (`Stages 1A & 1B`)
- [ ] Wire `J1.TN` to `GND`. Wire `J1.T` $\rightarrow$ `R_IN_PROT` (`1 kΩ`) $\rightarrow$ `C1` (`1 µF` PET film) $\rightarrow$ `IN_AC` (`R1` `100 kΩ` to `GND`, `D_IN` `BAV99` pins `1=-12V`, `2=+12V`, `3=IN_AC`) $\rightarrow$ `R_IN_BUF` (`1 kΩ`) $\rightarrow$ `U2D` pin `12` (`+`); tie pin `13` (`-`) to pin `14` (`IN_BUF`) and attach `TP4` (`IN_BUF`).
- [ ] Wire `IN_BUF` $\rightarrow$ `R2` (`10 kΩ`) $\rightarrow$ `U1A` pin `2` (`-`), with `U1A` pin `3` (`+`) to `GND`.
- [ ] Wire `R_GAIN_MIN` (`1 kΩ`) in series with `RV1` (`A100k`, pin `2` wiper tied to pin `3`), paralleled by `R_GAIN_FAIL` (`1 MΩ`) and `C_HF` (`47 pF` `C0G`), from `U1A` pin `2` to pin `1` (`PREAMP_OUT`). Attach `TP5` (`PREAMP`).

### Step 4: `0.1%`-Matched Precision Full-Wave Rectifier (`U1B`, `U1C`, `D1_D2`) (`Stages 2 & 3`)
- [ ] **Half-Wave (`U1B`)**: Wire `PREAMP_OUT` $\rightarrow$ `R3` (`10 kΩ 0.1%`) $\rightarrow$ `U1B` pin `6` (`-`); `U1B` pin `5` (`+`) to `GND`; `D1_D2` (`BAT54S`) pin `1` (`A1`) to `RECT_HW`, pin `2` (`K2`) to pin `6`, pin `3` (`COM`) to pin `7`; `R6` (`10 kΩ 0.1%`) from pin `6` to `RECT_HW`.
- [ ] **Summing (`U1C`)**: Wire `PREAMP_OUT` $\rightarrow$ `R4` (`10 kΩ 0.1%`) $\rightarrow$ `R5` (`10 kΩ 0.1%`) $\rightarrow$ `U1C` pin `9` (`-`); `RECT_HW` $\rightarrow$ `R7` (`10 kΩ 0.1%`) $\rightarrow$ `U1C` pin `9`; `U1C` pin `10` (`+`) to `GND`; `R8A` + `R8B` (`2 × 10 kΩ 0.1%`) from pin `9` to pin `8` (`RECT_OUT`). Attach `TP6` (`RECT`).

### Step 5: Active Zero-Deadzone Peak Detector (`U2C`) (`Stage 4`)
- [ ] Wire `RECT_OUT` to `U2C` pin `10` (`+`). Wire `U2C` pin `8` (`U2C_OUT`) $\rightarrow$ `D3` (`1N4148WS`, anode-to-cathode) $\rightarrow$ `ATK_IN` (`U2C` pin `9` `-` and `R_ATK_MIN` `470 Ω`) $\rightarrow$ `RV2` (`ATK`, `A50k`, wiper tied to pin `3`) $\rightarrow$ `ENV_NODE`.
- [ ] Wire `C2` (`1 µF` PET film) from `ENV_NODE` to `GND`, and `R10` (`10 kΩ`) $\rightarrow$ `RV3` (`REL`, `A1M`, wiper tied to pin `3`) to `GND`.

### Step 6: Linearized `OFFSET`, Protected Outputs & Precision LED Sink (`U1D`, `U2A`, `U2B`) (`Stages 5 & 6`)
- [ ] Wire `ENV_NODE` $\rightarrow$ `R_ENV_PROT` (`10 kΩ`) $\rightarrow$ `U1D` pin `12` (`+`). Wire `+12V` $\rightarrow$ `R11` (`1 kΩ`) $\rightarrow$ `RV4` (`B10k`) $\rightarrow$ `R12` (`1 kΩ`) $\rightarrow$ `-12V`; wire `OFF_WIPER` via `R13` (`18 kΩ`) to `U1D` pin `13` (`-`).
- [ ] Wire `U1D` pin `14` $\rightarrow$ `R16A` (`470 Ω 0.5 W`) $\rightarrow$ `OUT_CLAMP` (`D_OUT` `BAV99` pin `1=-12V`, pin `2=+12V`, pin `3=OUT_CLAMP`, plus `R15` `10 kΩ` feedback to pin `13`, `C_OUT1` `100 pF` across pins `13–14`, and `TP7` `OUT`) $\rightarrow$ `R16B` (`470 Ω 0.5 W`) $\rightarrow$ `J2` (`OUT` tip). Leave `J2.TN` `NC`.
- [ ] Wire `OUT_CLAMP` $\rightarrow$ `R17` (`10 kΩ`) $\rightarrow$ `U2A` pin `2` (`-`), `U2A` pin `3` (`+`) to `GND`, `U2A` pin `1` $\rightarrow$ `R19A` (`470 Ω 0.5 W`) $\rightarrow$ `INV_OUT_CLAMP` (`D_INV_OUT` `BAV99`, `R18` `10 kΩ` feedback, `C_OUT2` `100 pF` across pins `1–2`, and `TP8` `INV_OUT`) $\rightarrow$ `R19B` (`470 Ω 0.5 W`) $\rightarrow$ `J3` (`INV_OUT` tip). Leave `J3.TN` `NC`.
- [ ] Wire `ENV_NODE` $\rightarrow$ `R20` (`10 kΩ`) $\rightarrow$ `U2B` pin `5` (`+`), `U2B` pin `7` (`U2B_OUT`) $\rightarrow$ `D4` (`.A`) & `D_LED_CLAMP` (`.K`), and `LED_K` (`D4.K`, `D_LED_CLAMP.A`, `U2B` pin `6` `-`) $\rightarrow$ `R_LED` (`2.2 kΩ`) $\rightarrow$ `GND`.

### Step 7: ERC, Footprints & Silkscreen Prep
- [ ] Mark `TP1`–`TP8` and `FID1`–`FID3` with `Exclude from BOM` / `Exclude from position files` / `Do not populate`.
- [ ] Run **ERC** (`0` errors, `0` warnings), assign footprints from Section 2, and export netlist.

---

## 5. Complete Component-by-Component Silkscreen Schedule

Follow these exact layer assignments (`B.SilkS` for single-sided `B.Cu` SMT assembly—concise value-only tokens for all `41` fixed `R*`/`C*` passives with `<REF>` kept on `.Fab`, and `<REF> + <VAL>` for ICs and diodes; dual-sided `F.SilkS` + `B.SilkS` for manual THT hardware, `C1`/`C2`, and `TP1`–`TP8` test points; zero text on `FID1`–`FID3`):

| Ref | Package / Side | `F.SilkS` Label | `B.SilkS` Label | Required Polarity / Orientation Mark |
| :--- | :--- | :--- | :--- | :--- |
| `U1`, `U2` | `SOIC-14` (`B.Cu`) | — | `U1 TL074H`, `U2 TL074H` | Solid Pin-1 dot (`r = 0.25 mm`) outside `.Fab` body |
| `D_PWR_P`, `D_PWR_N` | `SOD-123` (`B.Cu`) | — | `D_PWR_P B5819W`, `D_PWR_N B5819W` | External `0.25 mm` cathode bar (`\|`) beyond Pad `1` (`D_PWR_N` reversed on `-12V_IN`) |
| `D1_D2` | `SOT-23` (`B.Cu`) | — | `D1_D2 BAT54S` | Solid Pin-1 (`A1`) dot (`r = 0.22 mm`) outside Pad `1` |
| `D3`, `D_LED_CLAMP` | `SOD-323` (`B.Cu`) | — | `D3 1N4148WS`, `D_LED_CLAMP 1N4148WS` | External `0.25 mm` cathode bar (`\|`) beyond Pad `1` |
| `D_IN`, `D_OUT`, `D_INV_OUT` | `SOT-23` (`B.Cu`) | — | `D_IN BAV99`, `D_OUT BAV99`, `D_INV_OUT BAV99` | Solid Pin-1 (`A1` / `-12V`) dot (`r = 0.22 mm`) outside Pad `1` |
| `C3` | `CP_Elec_6.3x5.4` (`B.Cu`) | — | `22uF` *(`C3` on `B.Fab`)* | `+` outside anode (`+12V`) pad + chamfered base outline |
| `C4` | `CP_Elec_6.3x5.4` (`B.Cu`) | — | `22uF` *(`C4` on `B.Fab`)* | `+` outside anode (**`GND`**) pad + chamfered base outline |
| `C_DEC1`–`C_DEC4` | `0603` (`B.Cu`) | — | `100nF` *(`C_DEC*` on `B.Fab`)* | Non-polarized |
| `C_HF` | `0603` (`B.Cu`) | — | `47pF` *(`C_HF` on `B.Fab`)* | Non-polarized |
| `C_OUT1`, `C_OUT2` | `0603` (`B.Cu`) | — | `100pF` *(`C_OUT*` on `B.Fab`)* | Non-polarized |
| `R_PWR_P`, `R_PWR_N` | `1206` (`B.Cu`) | — | `10R` *(`R_PWR_*` on `B.Fab`)* | Non-polarized (`1206` `250 mW` outline) |
| `R_ATK_MIN` | `0603` (`B.Cu`) | — | `470R` *(`R_ATK_MIN` on `B.Fab`)* | Non-polarized |
| `R16A`, `R16B`, `R19A`, `R19B` | `1210` (`B.Cu`) | — | `470R` *(`R16A/B`, `R19A/B` on `B.Fab`)* | Non-polarized (`1210` `0.5 W` outline) |
| `R_IN_PROT`, `R_IN_BUF`, `R_GAIN_MIN`, `R11`, `R12` | `0603` (`B.Cu`) | — | `1k` *(refs on `B.Fab`)* | Non-polarized |
| `R_LED` | `0603` (`B.Cu`) | — | `2.2k` *(`R_LED` on `B.Fab`)* | Non-polarized |
| `R2`, `R10`, `R_ENV_PROT`, `R15`, `R17`, `R18`, `R20` | `0603` (`B.Cu`) | — | `10k` *(refs on `B.Fab`)* | Non-polarized |
| `R3`–`R7`, `R8A`, `R8B` | `0603` (`B.Cu`) | — | `10k` *(`0.1%` refs on `B.Fab`)* | Non-polarized (`0.1%` cluster at `U1B`/`U1C`) |
| `R13` | `0603` (`B.Cu`) | — | `18k` *(`R13` on `B.Fab`)* | Non-polarized |
| `R1` | `0603` (`B.Cu`) | — | `100k` *(`R1` on `B.Fab`)* | Non-polarized |
| `R_GAIN_FAIL` | `0603` (`B.Cu`) | — | `1M` *(`R_GAIN_FAIL` on `B.Fab`)* | Non-polarized |
| `C1`, `C2` | `P=5mm` Film (THT, `B.Cu`) | `1uF` *(`C1`/`C2` on `B.Fab`)* | `1uF` *(`C1`/`C2` on `B.Fab`)* | Non-polarized; echoed on both sides |
| `J4` | `IDC 2x5` (THT, `B.Cu`) | `J4 PWR` + `-12V Pin 1` | `J4 PWR` + `RED STRIPE / -12V` | `0.85 mm` stripe bar, keyway notch, `-12V`/`GND`/`+12V` |
| `J1`–`J3` | `WQP-PJ398SM` (THT, `F.Cu`) | `J1 IN`, `J2 OUT`, `J3 INV_OUT` | `J1 IN`, `J2 OUT`, `J3 INV_OUT` | Jack body outline on `F.SilkS` |
| `RV1`–`RV4` | `Alps RK09K` (THT, `F.Cu`) | `RV1 GAIN A100k`, `RV2 ATK A50k`, `RV3 REL A1M`, `RV4 OFF B10k` | `RV1 GAIN A100k`, `RV2 ATK A50k`, `RV3 REL A1M`, `RV4 OFF B10k` | Pin `1` (`"1"`) marker on **both** `F.SilkS` and `B.SilkS` |
| `D4` | `LED_D3.0mm` (THT, `F.Cu`) | `D4 LED` (`+` / `-`) | `D4 LED` (`+` / `-`) | `+` (anode) and `-` (cathode) on **both** layers |
| `TP1`–`TP8` (`DNP`) | `RH-5001` (`DNP` THT, `B.Cu`) | `TP1 GND` … `TP8 INV_OUT` | `TP1 GND` … `TP8 INV_OUT` | Dual-sided labels + `"DNP"` on `B.Fab` |
| `FID1`–`FID3` (`DNP`) | `Fiducial 1mm/2mm` (`B.Cu`) | — | — | `±1.25 mm` silkscreen keepout; zero `.SilkS` text |
