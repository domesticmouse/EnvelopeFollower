# Envelope Follower — Verified Bill of Materials & JLCPCB Sourcing (Stage 3)

> **Circuit Spec:** [`EnvelopeFollowerImproved.md`](./EnvelopeFollowerImproved.md)  
> **Verification Method:** Live queries via `stages/stage-1/.agents/skills/skidl/scripts/jlcpcb_search.py --in-stock-only` (`selectSmtComponentList/v2`), plus KiCad 10 footprint verification in `/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/`.

---

## 1. Live Verification Coverage & Remaining Gap

| Category | Verified Live? | Notes |
|---|---|---|
| **ICs & Diodes (`U1`–`U2`, `D1`–`D3`, `D5`–`D11`)** | **Yes** | `TL074HIDR` (`C2878713`, Extended), `1N4148W` (`C81598`, Basic), `BAV99,215` (`C2500`, Basic), `B5819W SL` (`C8598`, Basic). |
| **All SMD Resistors (`R1`–`R8B`, `R10`–`R19`, `R24`–`R26`, `R28`–`R30`)** | **Yes** | 8 Basic lines (`0603` 1% + `10 Ω 1206`) + 1 Extended `2512 1 W 1%` line (`C54315`). |
| **MLCC Decoupling/Coupling & Electrolytics (`C1`, `C3`–`C8`)** | **Yes** | `100 nF` (`C14663`, Basic), `10 µF 50 V 1206` (`C5449000`, Extended), `22 µF 35 V D5×L5.4` (`C2887274`, Extended). |
| **`C2` Film & THT Parts (`C2`, `J_PWR`, `D4`, `J1`–`J3`, `RV1`–`RV4`)** | **Yes** | `1uF film` & `470nF film` returned **zero SMD film parts** on JLCPCB; resolved `C2` to **`WIMA MKS2` (`C92673`, `P=5mm`, Manual THT)**. `J_PWR` (`C53207560`) & `3 mm` LEDs (`C84774`/`C85161`/`C99761`) verified; `WQP-PJ398SM` THT jacks & `RK09` 9 mm pots absent on JLCPCB (source externally). |
| **Small `NP0` Feedback Caps (`C9`–`C13`: `15 pF`, `47 pF`, `100 pF`)** | **PENDING** | Query `"15pF/47pF/100pF 50V 0603 C0G"` matched only `1 nF NP0` (`C18255878`) because JLCPCB catalogs `NP0` rather than `C0G`. The follow-up `"15pF/47pF/100pF NP0 0603"` command timed out after `60 s` waiting on permission approval. Marked `PENDING_VERIFY` below (do not guess codes). |
| **Optional DNP THT Test Points (`TP1`–`TP8`: Ronghe `RH-5001`)** | **PENDING** | Live lookup via `search_lcsc.py "RH-5001" --details --json` failed in sandbox (`urlopen` DNS error) and timed out after `60 s` waiting on permission approval for `BypassSandbox: true`. Marked **`DNP`** and **`PENDING_VERIFY`** below (LCSC code, stock/price, and pin/drill dimensions must be verified before PCB footprint finalization). |

---

## 2. Complete Verified BOM (`59` Populated Components: `49` JLCPCB SMT + `10` Manual THT; plus `8` Optional DNP Test Points = `67` PCB Footprints)

### 2A. JLCPCB SMT Assembly Parts (`49` Components across `19` BOM Lines)

| Designator | Qty | Value / Spec | Package | KiCad Footprint | MPN | Manufacturer | LCSC Part # | JLCPCB Class | Live Stock | Unit Price (USD) | Line Cost (USD) |
|---|---:|---|---|---|---|---|---|---|---:|---:|---:|
| `U1, U2` | 2 | `TL074H` Quad Op-Amp | `SOIC-14` | `Package_SO:SOIC-14_3.9x8.7mm_P1.27mm` | `TL074HIDR` | Texas Instruments | **`C2878713`** | **Extended** | 469 | $0.2559 | $0.5118 |
| `D1, D2, D3, D5, D6, D7` | 6 | `1N4148W` 75V 150mA | `SOD-123` | `Diode_SMD:D_SOD-123` | `1N4148W` | ST (Semtech) | **`C81598`** | **Basic** | 2,914,864 | $0.0124 | $0.0744 |
| `D8, D9` | 2 | `BAV99` 100V Dual Series | `SOT-23` | `Package_TO_SOT_SMD:SOT-23` | `BAV99,215` | Nexperia | **`C2500`** | **Basic** | 1,621,895 | $0.0111 | $0.0222 |
| `D10, D11` | 2 | `B5819W` 40V 1A Schottky | `SOD-123` | `Diode_SMD:D_SOD-123` | `B5819W SL` | Jiangsu Changjing | **`C8598`** | **Basic** | 853,344 | $0.0256 | $0.0512 |
| `R11, R12, R28` | 3 | `470 Ω ±1%` 100mW | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF4700T5E` | UNI-ROYAL | **`C23179`** | **Basic** | 4,182,882 | $0.0019 | $0.0057 |
| `R26` | 1 | `1 kΩ ±1%` 100mW | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1001T5E` | UNI-ROYAL | **`C21190`** | **Basic** | 30,429,916 | $0.0017 | $0.0017 |
| `R29` | 1 | `2.2 kΩ ±1%` 100mW | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF2201T5E` | UNI-ROYAL | **`C4190`** | **Basic** | 4,225,475 | $0.0018 | $0.0018 |
| `R2, R6, R7, R14, R15, R17, R18` | 7 | `10 kΩ ±1%` 100mW | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1002T5E` | UNI-ROYAL | **`C25804`** | **Basic** | 42,590,828 | $0.0019 | $0.0133 |
| `R3, R4, R5, R8A, R8B, R13` | 6 | `20 kΩ ±1%` 100mW | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF2002T5E` | UNI-ROYAL | **`C4184`** | **Basic** | 5,137,458 | $0.0018 | $0.0108 |
| `R10` | 1 | `47 kΩ ±1%` 100mW | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF4702T5E` | UNI-ROYAL | **`C25819`** | **Basic** | 2,454,182 | $0.0016 | $0.0016 |
| `R1, R30` | 2 | `1 MΩ ±1%` 100mW | `0603` | `Resistor_SMD:R_0603_1608Metric` | `0603WAF1004T5E` | UNI-ROYAL | **`C22935`** | **Basic** | 5,144,682 | $0.0018 | $0.0036 |
| `R24, R25` | 2 | `10 Ω ±1%` 250mW | `1206` | `Resistor_SMD:R_1206_3216Metric` | `1206W4F100JT5E` | UNI-ROYAL | **`C17903`** | **Basic** | 1,217,347 | $0.0061 | $0.0122 |
| `R16, R19` | 2 | `1 kΩ ±1%` **1 W** | `2512` | `Resistor_SMD:R_2512_6332Metric` | `25121WF1001T4E` | UNI-ROYAL | **`C54315`** | **Extended** | 53,433 | $0.0336 | $0.0672 |
| `C5, C6, C7, C8` | 4 | `100 nF 50 V X7R ±10%` | `0603` | `Capacitor_SMD:C_0603_1608Metric` | `CC0603KRX7R9BB104` | YAGEO | **`C14663`** | **Basic** | 53,995,509 | $0.0060 | $0.0240 |
| `C1` | 1 | `10 µF 50 V X7R ±10%` | `1206` | `Capacitor_SMD:C_1206_3216Metric` | `TCC1206X7R106K500HT` | CCTC | **`C5449000`** | **Extended** | 40,854 | $0.1065 | $0.1065 |
| `C3, C4` | 2 | `22 µF 35 V ±20%` Elec | `D5×L5.4mm` | `Capacitor_SMD:CP_Elec_5x5.4` | `RVT22UF35V67RV0104` | KNSCHA | **`C2887274`** | **Extended** | 18,620 | $0.0354 | $0.0708 |
| `C10` | 1 | `15 pF 50 V NP0 ±5%` | `0603` | `Capacitor_SMD:C_0603_1608Metric` | `PENDING_VERIFY` | — | **`PENDING_VERIFY`** | *(Basic exp.)* | — | — | — |
| `C9, C11, C12` | 3 | `47 pF 50 V NP0 ±5%` | `0603` | `Capacitor_SMD:C_0603_1608Metric` | `PENDING_VERIFY` | — | **`PENDING_VERIFY`** | *(Basic exp.)* | — | — | — |
| `C13` | 1 | `100 pF 50 V NP0 ±5%` | `0603` | `Capacitor_SMD:C_0603_1608Metric` | `PENDING_VERIFY` | — | **`PENDING_VERIFY`** | *(Basic exp.)* | — | — | — |

**Alternate Verified SMD Options:**
- **`U1`, `U2` Stock Backup:** If `TL074HIDR` (`C2878713`, `469` stock) sells out before ordering, `TL074HIPWR` (`C4370424`, `TSSOP-14`, `10,585` stock, `$0.3396`) and `TL074HIDYYR` (`C5116353`, `SOT-23-14-THIN`, `10,398` stock, `$0.4158`) are in high stock (requires updating footprint).
- **`C1` Alternates:** `C132170` (`CC1206KKX7R9BB475`, YAGEO `4.7 µF 50 V X7R 1206`, `37,873` stock, `$0.1189`) or `C694197` (TDK `10 µF 50 V X7R 1206`, `9,310` stock, `$0.6647`).
- **`C3`, `C4` Alternates:** `C5246583` (`VT22UF35V167RV0131`, `D5×L5.4mm`, `10,056` stock, `$0.0362`) or `C48587226` (`22UF35V5x5.4VT`, `7,022` stock, `$0.0279`).
- **`R29` (`R_set`) Alternate:** If choosing a high-efficiency/ultrabright LED (`C99761` `500 mcd–1 cd`), substitute `4.7 kΩ 0603 1%` to cap full-scale current at `2.1 mA`.

---

### 2B. Manual Through-Hole (THT) Parts Mounted Later (`10` Components — Omit from JLCPCB SMT BOM)

| Designator | Qty | Value / Part | Package / Pitch | KiCad Footprint | Sourcing & Assembly Notes |
|---|---:|---|---|---|---|
| `C2` | 1 | `1 µF 63 V ±5%` Metallized Polyester Film | `Plugin, P=5.00mm` (`7.2×5.0×10.0mm`) | `Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm` | **Live-verified on LCSC:** **`C92673`** (`WIMA MKS2C041001F00JSSD`, `5,578` stock, `$1.1443`; or source from DigiKey/Mouser/Tayda). Mount on `B.Cu` (rear) to avoid `10.5 mm` front-panel standoff limit (`10.0 mm` tall). |
| `J_PWR` | 1 | `2×5P` `2.54 mm` Shrouded Keyed IDC Header | `THT 2×5 Vertical` | `Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical` | **Live-verified on LCSC:** **`C53207560`** (`JXTCONN IDC2.54-2*5PZ`, `2,060` stock, `$0.1241`). Mount on `B.Cu`; verify Pin 1 (`-12Vin` red stripe) matches key notch. |
| `D4` | 1 | `3 mm` THT Indicator LED | `Plugin, D=3mm` | `LED_THT:LED_D3.0mm` | **Live-verified Everlight options on LCSC:** Red `C84774` (`56,245` stock, `$0.0359`), Yellow `C85160` (`40,636` stock, `$0.0366`), Yellow-Green `C85161` (`37,383` stock, `$0.0361`), or Emerald Green ultrabright `C99761` (`86,132` stock, `$0.0457`). Stand off to `~10.5 mm` panel height (`3.2 mm` drill). |
| `J1, J2, J3` | 3 | `3.5 mm` Mono Switched Jack (`WQP-PJ398SM`) | `THT Vertical` | `Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | Not stocked as THT on JLCPCB (`PJ-398` returned only SMD `C707238`). Source QingPu `WQP-PJ398SM` / Thonkiconn externally (Thonk, Tayda, Mouser). `10.5 mm` panel standoff. |
| `RV1` | 1 | `A100k` 9 mm Vertical Pot (`GAIN`) | `THT Vertical` | `Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical` | `RK09` returned 0 results on JLCPCB. Source Audio/Log `A100k` 9 mm pot (Alpha `RD901F` / `RV09AF-40` or Bourns `PTV09A`) externally. |
| `RV2` | 1 | `A50k` 9 mm Vertical Pot (`ATK`) | `THT Vertical` | `Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical` | Audio/Log `A50k` 9 mm vertical pot; source externally. |
| `RV3` | 1 | `A1M` 9 mm Vertical Pot (`Release`) | `THT Vertical` | `Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical` | Audio/Log `A1M` 9 mm vertical pot; source externally. |
| `RV4` | 1 | `B10k` 9 mm Vertical Pot (`OFFSET`) | `THT Vertical` | `Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical` | Linear `B10k` 9 mm vertical pot (center detent recommended, e.g. Alpha `RD901F-40-15F-B10K-C`); source externally. |

---

### 2C. Optional / Do-Not-Populate (`DNP`) Through-Hole Test Points (`8` PCB Footprints — Excluded from JLCPCB SMT & Required BOMs)

| Designator | Qty | Value / Function | MPN | Manufacturer | LCSC Part # | DNP | KiCad Symbol & Footprint | Sourcing & Assembly Notes |
|---|---:|---|---|---|---|---|---|---|
| `TP1` (`GND`), `TP2` (`+12V_PROT`), `TP3` (`-12V_PROT`), `TP4` (`PREAMP_OUT`), `TP5` (`HALF_WAVE`), `TP6` (`RECT_OUT`), `TP7` (`PEAK_DET`), `TP8` (`ENV_RAW_BUF`) | 8 *(opt.)* | Bench Test Point (`RH-5001`) | `RH-5001` | Ronghe | **`PENDING_VERIFY`** | **Yes (`DNP`)** | `Connector:TestPoint` / `TestPoint:TestPoint_Keystone_5000-5004_Miniature` *(tentative `1.0 mm` drill / `2.0 mm` pad — verify `RH-5001` pin dimensions vs. drill before layout; or `TestPoint_THTPad_D2.0mm_Drill1.0mm`)* | **DNP / Exclude from BOM** (`dnp=True`, `exclude_from_bom=True`). Leave unpopulated to needle-probe plated pads from either side, or optionally hand-solder `RH-5001` loops on **`B.Cu`** (rear) to stay clear of the `10.5 mm` front-panel standoff. Verify LCSC code, stock, and exact `RH-5001` hole fit before ordering/layout. |

---

## 3. JLCPCB SMT BOM Upload Table (`Comment,Designator,Footprint,LCSC Part #`)

> Exported for **JLCPCB Economic Assembly** (SMD only; manual THT parts `C2`, `J_PWR`, `D4`, `J1`–`J3`, `RV1`–`RV4` and DNP test points `TP1`–`TP8` excluded — also filter `TP1`–`TP8` out of JLCPCB CPL before upload to avoid orphan-designator rejection). Populate the 3 `PENDING_VERIFY` `NP0` capacitor codes (`C9`–`C13`) before upload.

```csv
Comment,Designator,Footprint,LCSC Part #
TL074HIDR,"U1,U2",SOIC-14_3.9x8.7mm_P1.27mm,C2878713
1N4148W,"D1,D2,D3,D5,D6,D7",D_SOD-123,C81598
BAV99,"D8,D9",SOT-23,C2500
B5819W,"D10,D11",D_SOD-123,C8598
470R 1%,"R11,R12,R28",R_0603_1608Metric,C23179
1k 1%,R26,R_0603_1608Metric,C21190
2.2k 1%,R29,R_0603_1608Metric,C4190
10k 1%,"R2,R6,R7,R14,R15,R17,R18",R_0603_1608Metric,C25804
20k 1%,"R3,R4,R5,R8A,R8B,R13",R_0603_1608Metric,C4184
47k 1%,R10,R_0603_1608Metric,C25819
1M 1%,"R1,R30",R_0603_1608Metric,C22935
10R 1% 0.25W,"R24,R25",R_1206_3216Metric,C17903
1k 1% 1W,"R16,R19",R_2512_6332Metric,C54315
100nF 50V X7R,"C5,C6,C7,C8",C_0603_1608Metric,C14663
10uF 50V X7R,"C1",C_1206_3216Metric,C5449000
22uF 35V Elec,"C3,C4",CP_Elec_5x5.4,C2887274
15pF 50V NP0,C10,C_0603_1608Metric,PENDING_VERIFY
47pF 50V NP0,"C9,C11,C12",C_0603_1608Metric,PENDING_VERIFY
100pF 50V NP0,C13,C_0603_1608Metric,PENDING_VERIFY
```

---

## 4. Basic vs. Extended Line Count & Per-Board Cost Breakdown

- **Unique JLCPCB SMT BOM Lines (`19` total):**
  - **Live-Verified Basic Lines:** **`12`** lines (`37` SMD components) → `$0.00` feeder setup fee.
  - **Pending `NP0` Feedback Cap Lines:** **`3`** lines (`5` SMD components: `C10`, `C9/C11/C12`, `C13`) — expected Basic once queried with `"NP0"` keyword (`~$0.01–$0.03`/board est.).
  - **Live-Verified Extended Lines:** **`4`** lines (`7` SMD components: `U1/U2`, `R16/R19`, `C1`, `C3/C4`) → `4 × $3.00 = $12.00` total one-time Extended feeder setup fee per assembly order.
- **Per-Board JLCPCB SMT Component Subtotal (44 live-verified SMD parts; excludes 5 pending `NP0` pF caps, PCB fab, and PCBA assembly labor/stencil):**
  - **Basic SMD parts (`37` pcs):** **`$0.2225`**
  - **Extended SMD parts (`7` pcs):** **`$0.7563`**
  - **Verified SMD parts subtotal (`44` pcs):** **`$0.9788 / board`**
  - **Amortized Extended feeder fees (`$12.00 / N`):** `+$2.4000 / board` at 5 boards (`$3.3788` parts + feeder/board) or `+$0.1200 / board` at 100 boards (`$1.0988` parts + feeder/board).
- **LCSC-Sourced Manual THT Parts Subtotal (optional to bundle with order):**
  - `C2` (`C92673`, `$1.1443`) + `J_PWR` (`C53207560`, `$0.1241`) + `D4` (`C84774`, `$0.0359`) = **`$1.3043 / board`** *(plus externally sourced `3× WQP-PJ398SM` jacks and `4× 9 mm` potentiometers `A100k`, `A50k`, `A1M`, `B10k`; `TP1`–`TP8` Ronghe `RH-5001` test points are marked **DNP** / `$0.00` required BOM cost)*.

### Commands to Resolve Remaining `PENDING_VERIFY` LCSC Codes

```bash
python3 /Users/brett/Documents/GitHub/EnvelopeFollower/stages/stage-1/.agents/skills/skidl/scripts/jlcpcb_search.py --in-stock-only \
  "15pF NP0 0603" "47pF NP0 0603" "100pF NP0 0603"

python3 /Users/brett/Documents/GitHub/EnvelopeFollower/stages/stage-1/.agents/skills/lcsc/scripts/search_lcsc.py \
  "RH-5001" --details --json
```
