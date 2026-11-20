#!/usr/bin/env python3
"""SKiDL circuit definition for the Improved Eurorack Envelope Follower."""

import builtins
import csv
import os
import re
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)

os.environ.setdefault("XDG_DATA_HOME", "/tmp/xdg_data")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_config")
if os.path.isdir("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"):
    os.environ.setdefault(
        "KICAD10_SYMBOL_DIR",
        "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols",
    )
    os.environ.setdefault(
        "KICAD_SYMBOL_DIR",
        "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols",
    )
if os.path.isdir("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"):
    os.environ.setdefault(
        "KICAD10_FOOTPRINT_DIR",
        "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints",
    )

from skidl import (
    ERC,
    POWER,
    TEMPLATE,
    Net,
    NetClass,
    Part,
    erc_assert,
    generate_netlist,
    generate_xml,
    subcircuit,
)


def make_part(
    lib: str,
    symbol: str,
    ref: str,
    value: str,
    footprint: str,
    *,
    mpn: str,
    manufacturer: str,
    lcsc: str = "",
    jlcpcb_class: str,
    silkscreen: str,
    notes: str = "",
    dnp: bool = False,
    exclude_from_bom: bool = False,
) -> Part:
    """Instantiate a KiCad part with BOM and silkscreen metadata fields."""
    part = Part(lib, symbol, value=value, footprint=footprint, tag=ref.lower())
    part.ref = ref
    part.fields["MPN"] = mpn
    part.fields["Manufacturer"] = manufacturer
    if lcsc:
        part.fields["LCSC"] = lcsc
    part.fields["JLCPCB_Class"] = jlcpcb_class
    part.fields["Silkscreen"] = silkscreen
    if notes:
        part.fields["Notes"] = notes
    if dnp:
        part.dnp = True
    if exclude_from_bom:
        part.exclude_from_bom = True
    return part


def make_r0603(
    ref: str,
    value: str,
    *,
    mpn: str,
    manufacturer: str,
    lcsc: str,
    jlcpcb_class: str,
    silkscreen: str | None = None,
    notes: str = "",
) -> Part:
    """Create an 0603 SMD resistor."""
    return make_part(
        "Device",
        "R",
        ref=ref,
        value=value,
        footprint="Resistor_SMD:R_0603_1608Metric",
        mpn=mpn,
        manufacturer=manufacturer,
        lcsc=lcsc,
        jlcpcb_class=jlcpcb_class,
        silkscreen=silkscreen or value,
        notes=notes,
    )


def make_r10k(ref: str, notes: str = "") -> Part:
    """Create a standard 10k 1% 0603 resistor."""
    return make_r0603(
        ref=ref,
        value="10k",
        mpn="0603WAF1002T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C25804",
        jlcpcb_class="Basic",
        notes=notes,
    )


def make_r1k_0603(ref: str, notes: str = "") -> Part:
    """Create a standard 1k 1% 0603 resistor."""
    return make_r0603(
        ref=ref,
        value="1k",
        mpn="0603WAF1001T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C21190",
        jlcpcb_class="Basic",
        notes=notes,
    )


def make_r1m(ref: str, notes: str = "") -> Part:
    """Create a standard 1M 1% 0603 resistor."""
    return make_r0603(
        ref=ref,
        value="1M",
        mpn="0603WAF1004T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C22935",
        jlcpcb_class="Basic",
        notes=notes,
    )


def make_r100k_01(ref: str, notes: str = "") -> Part:
    """Create a precision 100k 0.1% 0603 thin-film resistor."""
    return make_r0603(
        ref=ref,
        value="100k 0.1%",
        mpn="RT0603BRD07100KL",
        manufacturer="YAGEO",
        lcsc="C122538",
        jlcpcb_class="Extended",
        silkscreen="100k 0.1%",
        notes=notes,
    )


def make_r1k_1w(ref: str, notes: str = "") -> Part:
    """Create a 1k 1W 2512 fault-rated protection resistor."""
    return make_part(
        "Device",
        "R",
        ref=ref,
        value="1k 1W",
        footprint="Resistor_SMD:R_2512_6332Metric",
        mpn="25121WF1001T4E",
        manufacturer="UNI-ROYAL",
        lcsc="C54315",
        jlcpcb_class="Extended",
        silkscreen="1k 1W",
        notes=notes,
    )


def make_c100n(ref: str, notes: str = "") -> Part:
    """Create a 100nF 50V X7R 0603 decoupling capacitor."""
    return make_part(
        "Device",
        "C",
        ref=ref,
        value="100nF 50V",
        footprint="Capacitor_SMD:C_0603_1608Metric",
        mpn="CC0603KRX7R9BB104",
        manufacturer="YAGEO",
        lcsc="C14663",
        jlcpcb_class="Basic",
        silkscreen="100nF",
        notes=notes,
    )


def make_c22u_elec(ref: str, notes: str = "") -> Part:
    """Create a 22uF 50V SMD aluminum electrolytic capacitor."""
    return make_part(
        "Device",
        "C_Polarized",
        ref=ref,
        value="22uF 50V",
        footprint="Capacitor_SMD:CP_Elec_6.3x5.4",
        mpn="RVT1H220M0605",
        manufacturer="DMBJ",
        lcsc="C970664",
        jlcpcb_class="Extended",
        silkscreen="22uF 50V",
        notes=notes,
    )


def make_c1u_film(ref: str, notes: str = "") -> Part:
    """Create a 1uF 63V WIMA MKS2 THT box film capacitor."""
    return make_part(
        "Device",
        "C",
        ref=ref,
        value="1uF 63V Film",
        footprint="Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm",
        mpn="MKS2C041001F00JSSD",
        manufacturer="WIMA",
        lcsc="C92673",
        jlcpcb_class="Manual THT",
        silkscreen="1uF FILM",
        notes=notes,
    )


def make_1n4148w(ref: str, notes: str = "") -> Part:
    """Create a 1N4148W fast switching diode in SOD-123."""
    return make_part(
        "Diode",
        "1N4148W",
        ref=ref,
        value="1N4148W",
        footprint="Diode_SMD:D_SOD-123",
        mpn="1N4148W",
        manufacturer="ST (Semtech)",
        lcsc="C81598",
        jlcpcb_class="Basic",
        silkscreen="1N4148W",
        notes=notes,
    )


def make_b5819w(ref: str, notes: str = "") -> Part:
    """Create a B5819W 40V/1A Schottky diode in SOD-123."""
    return make_part(
        "Device",
        "D_Schottky",
        ref=ref,
        value="B5819W",
        footprint="Diode_SMD:D_SOD-123",
        mpn="B5819W SL",
        manufacturer="Jiangsu Changjing",
        lcsc="C8598",
        jlcpcb_class="Basic",
        silkscreen="B5819W",
        notes=notes,
    )


def make_pot(
    ref: str,
    value: str,
    mpn: str,
    silkscreen: str,
    notes: str = "",
) -> Part:
    """Create a 9mm vertical panel potentiometer (1=CCW, 2=Wiper, 3=CW)."""
    return make_part(
        "Device",
        "R_Potentiometer",
        ref=ref,
        value=value,
        footprint="Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical",
        mpn=mpn,
        manufacturer="Alpha (Taiwan)",
        lcsc="",
        jlcpcb_class="User-Sourced / Manual THT",
        silkscreen=silkscreen,
        notes=notes,
    )


def make_jack(ref: str, silkscreen: str, notes: str = "") -> Part:
    """Create a QingPu WQP-PJ398SM switched 3.5mm mono Eurorack jack."""
    return make_part(
        "Connector_Audio",
        "AudioJack2_SwitchT",
        ref=ref,
        value="3.5mm Mono Jack",
        footprint="Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles",
        mpn="WQP-PJ398SM",
        manufacturer="QingPu",
        lcsc="",
        jlcpcb_class="User-Sourced / Manual THT",
        silkscreen=silkscreen,
        notes=notes,
    )


@subcircuit
def power_supply_section(
    vcc_p12_in: Net,
    vcc_n12_in: Net,
    vcc_p12: Net,
    vcc_n12: Net,
    gnd: Net,
    u1: Part,
    u2: Part,
) -> None:
    """Eurorack 2x5 IDC power header, reverse-polarity Schottkys, and decoupling."""
    j4 = make_part(
        "Connector_Generic",
        "Conn_02x05_Odd_Even",
        ref="J4",
        value="IDC 2x5 Header",
        footprint="Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical",
        mpn="IDC2.54-2*5PZ",
        manufacturer="JXTCONN",
        lcsc="C53207560",
        jlcpcb_class="Manual THT",
        silkscreen="±12V PWR",
        notes="Mount on B.Cu; pins 1-2 = -12V_IN (red stripe), 3-8 = GND, 9-10 = +12V_IN",
    )
    vcc_n12_in += j4[1, 2]
    gnd += j4[3, 4, 5, 6, 7, 8]
    vcc_p12_in += j4[9, 10]

    # D4 and D5 point in opposing electrical directions for +12V and -12V polarity protection.
    # KiCad D_SOD-123 / Device:D_Schottky: Pin 1 = K (Cathode), Pin 2 = A (Anode).
    d4 = make_b5819w("D4", notes="+12V reverse-polarity protection (B.Cu)")
    d5 = make_b5819w("D5", notes="-12V reverse-polarity protection (B.Cu)")
    vcc_p12_in += d4["A"]
    vcc_p12 += d4["K"]
    vcc_n12_in += d5["K"]
    vcc_n12 += d5["A"]

    # Bulk electrolytics downstream of D4/D5 (C4.1 '+' must connect to GND!).
    c3 = make_c22u_elec("C3", notes="+12V bulk decoupling (+ to +12V, - to GND)")
    c4 = make_c22u_elec("C4", notes="-12V bulk decoupling (+ to GND, - to -12V)")
    vcc_p12 += c3[1]
    gnd += c3[2]
    gnd += c4[1]
    vcc_n12 += c4[2]

    # Op-amp power pins and local 100nF bypass capacitors.
    vcc_p12 += u1[4], u2[4]
    vcc_n12 += u1[11], u2[11]

    c5 = make_c100n("C5", notes="U1 +12V local bypass (<3-5mm from Pin 4)")
    c6 = make_c100n("C6", notes="U1 -12V local bypass (<3-5mm from Pin 11)")
    c7 = make_c100n("C7", notes="U2 +12V local bypass (<3-5mm from Pin 4)")
    c8 = make_c100n("C8", notes="U2 -12V local bypass (<3-5mm from Pin 11)")
    vcc_p12 & c5 & gnd
    vcc_n12 & c6 & gnd
    vcc_p12 & c7 & gnd
    vcc_n12 & c8 & gnd


@subcircuit
def stage1_input_preamp(
    vcc_p12: Net,
    vcc_n12: Net,
    gnd: Net,
    u1: Part,
    preamp_out: Net,
) -> None:
    """Stage 1: Protected high-Z input (J1, R25, D6), AC coupling (C1), and U1A preamp."""
    in_tip = Net("IN_TIP")
    in_clamp = Net("IN_CLAMP")
    ac_in = Net("AC_IN")
    gain_floor = Net("GAIN_FLOOR")
    gain_wiper = Net("GAIN_WIPER")
    preamp_in = Net("PREAMP_IN")
    preamp_inv = Net("PREAMP_INV")

    j1 = make_jack(
        "J1",
        silkscreen="IN",
        notes="Catalog ref C9900009788 (0 stock); J1.TN shorted to GND",
    )
    in_tip += j1["T"]
    gnd += j1["S"], j1["TN"]

    r25 = make_r1k_1w("R25", notes="IN jack surge/ESD limiting resistor")
    in_tip & r25 & in_clamp

    # KiCad 10 Diode:BAV99 has misnamed symbol pins (1="K", 2="A", 3="K"),
    # so wire strictly by physical SOT-23 / Nexperia BAV99 pin numbers:
    # Pin 1 = A1 (-12V), Pin 2 = K2 (+12V), Pin 3 = K1/A2 (IN_CLAMP).
    d6 = make_part(
        "Diode",
        "BAV99",
        ref="D6",
        value="BAV99",
        footprint="Package_TO_SOT_SMD:SOT-23",
        mpn="BAV99,215",
        manufacturer="Nexperia",
        lcsc="C2500",
        jlcpcb_class="Basic",
        silkscreen="BAV99",
        notes="Input rail clamp (1=A1->-12V, 2=K2->+12V, 3=K1/A2->IN_CLAMP)",
    )
    vcc_n12 += d6[1]
    vcc_p12 += d6[2]
    in_clamp += d6[3]

    c1 = make_c1u_film(
        "C1", notes="Input AC coupling (fc=1.52 Hz); Alt: JLC Standard THT"
    )
    in_clamp & c1 & ac_in

    rv1 = make_pot(
        "RV1",
        value="A100k",
        mpn="RV09AF-40-15K-A100K",
        silkscreen="A100k (GAIN)",
        notes="CW=higher gain (0.494x to 11.0x)",
    )
    ac_in += rv1[3]
    gain_wiper += rv1[2]
    gain_floor += rv1[1]

    r24 = make_r0603(
        "R24",
        value="4.7k",
        mpn="0603WAF4701T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C23162",
        jlcpcb_class="Basic",
        notes="GAIN floor resistor (0.494x min gain)",
    )
    gain_floor & r24 & gnd

    r1 = make_r1m("R1", notes="GAIN wiper-lift bleed to GND")
    gain_wiper & r1 & gnd

    r28 = make_r1k_0603("R28", notes="U1A(+) internal ESD clamp current limiter")
    gain_wiper & r28 & preamp_in

    # U1A non-inverting 11.0x preamp.
    preamp_in += u1[3]
    preamp_inv += u1[2]
    preamp_out += u1[1]

    r2 = make_r10k("R2", notes="U1A gain shunt resistor to GND")
    r29 = make_r0603(
        "R29",
        value="100k",
        mpn="0603WAF1003T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C25803",
        jlcpcb_class="Basic",
        notes="U1A 11.0x feedback (1% thick film)",
    )
    c10 = make_part(
        "Device",
        "C",
        ref="C10",
        value="15pF 50V",
        footprint="Capacitor_SMD:C_0603_1608Metric",
        mpn="CL10C150JB8NNNC",
        manufacturer="Samsung Electro-Mechanics",
        lcsc="C1644",
        jlcpcb_class="Basic",
        silkscreen="15pF C0G",
        notes="U1A feedback stability compensation (fp=106.1 kHz)",
    )
    preamp_inv & r2 & gnd
    preamp_inv & (r29 | c10) & preamp_out


@subcircuit
def stages2_3_precision_fwr(
    gnd: Net,
    u1: Part,
    preamp_out: Net,
    fwr_out: Net,
) -> None:
    """Stages 2 & 3: AC-coupled 0.1% precision full-wave rectifier (U1B, U1C)."""
    ac_pre = Net("AC_PRE")
    rect_sum = Net("RECT_SUM")
    rect_out_n = Net("RECT_OUT_N")
    rect_half = Net("RECT_HALF")
    ff_mid = Net("FF_MID")
    fwr_sum = Net("FWR_SUM")

    c9 = make_c1u_film(
        "C9", notes="Inter-stage AC coupling (fc=2.55 Hz); Alt: JLC Standard THT"
    )
    r26 = make_r1m("R26", notes="AC_PRE DC ground reference after C9")
    preamp_out & c9 & ac_pre
    ac_pre & r26 & gnd

    # Precision 0.1% thin-film FWR network.
    r3 = make_r100k_01("R3", notes="U1B precision half-wave input resistor")
    r4 = make_r100k_01("R4", notes="FWR feedforward resistor 1 (R4+R5=200k)")
    r5 = make_r100k_01("R5", notes="FWR feedforward resistor 2 to FWR_SUM")
    r6 = make_r100k_01("R6", notes="U1B precision half-wave feedback resistor")
    r7 = make_r100k_01("R7", notes="Half-wave summing resistor into U1C")
    r8 = make_r0603(
        "R8",
        value="200k 0.1%",
        mpn="RT0603BRE07200KL",
        manufacturer="YAGEO",
        lcsc="C136955",
        jlcpcb_class="Extended",
        silkscreen="200k 0.1%",
        notes="U1C FWR feedback (1.000x gain); Alt: 2x C122538 in series",
    )
    c17 = make_part(
        "Device",
        "C",
        ref="C17",
        value="15pF 50V",
        footprint="Capacitor_SMD:C_0603_1608Metric",
        mpn="CL10C150JB8NNNC",
        manufacturer="Samsung Electro-Mechanics",
        lcsc="C1644",
        jlcpcb_class="Basic",
        silkscreen="15pF C0G",
        notes="U1C FWR feedback compensation across R8 (fp=53.1 kHz)",
    )

    # U1B precision half-wave rectifier.
    gnd += u1[5]
    rect_sum += u1[6]
    rect_out_n += u1[7]

    d1 = make_1n4148w("D1", notes="U1B negative-input clamp diode")
    d2 = make_1n4148w("D2", notes="U1B rectifier output diode")
    ac_pre & r3 & rect_sum
    rect_sum += d1["K"]
    rect_out_n += d1["A"]
    rect_out_n += d2["K"]
    rect_half += d2["A"]
    rect_sum & r6 & rect_half

    # U1C summing amp (+1.000x |V_pre|).
    gnd += u1[10]
    fwr_sum += u1[9]
    fwr_out += u1[8]

    ac_pre & r4 & ff_mid & r5 & fwr_sum
    rect_half & r7 & fwr_sum
    fwr_sum & (r8 | c17) & fwr_out


@subcircuit
def stage4_peak_detector(
    gnd: Net,
    u2: Part,
    fwr_out: Net,
    env_node: Net,
) -> None:
    """Stage 4: Active zero-deadzone peak detector (U2C) and unity buffer (U2D)."""
    det_fb = Net("DET_FB")
    det_op_out = Net("DET_OP_OUT")
    rect_diode_out = Net("RECT_DIODE_OUT")
    atk_in = Net("ATK_IN")
    env_cap = Net("ENV_CAP")
    rel_mid = Net("REL_MID")

    fwr_out += u2[10]
    det_fb += u2[9]
    det_op_out += u2[8]

    d9 = make_1n4148w("D9", notes="U2C anti-saturation clamp diode")
    c16 = make_part(
        "Device",
        "C",
        ref="C16",
        value="47pF 50V",
        footprint="Capacitor_SMD:C_0603_1608Metric",
        mpn="CL10C470JB8NNNC",
        manufacturer="Samsung Electro-Mechanics",
        lcsc="C1671",
        jlcpcb_class="Basic",
        silkscreen="47pF C0G",
        notes="U2C active peak-detector lead compensation (338 kHz)",
    )
    det_op_out += d9["K"]
    det_fb += d9["A"]
    det_fb & c16 & det_op_out

    d3 = make_1n4148w("D3", notes="Active peak-detector charging diode (U2C)")
    r9 = make_r0603(
        "R9",
        value="470R",
        mpn="0603WAF4700T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C23179",
        jlcpcb_class="Basic",
        notes="Pre-C2 attack surge limiter (D3 -> RV2)",
    )
    rv2 = make_pot(
        "RV2",
        value="A50k",
        mpn="RV09AF-40-15K-A50K",
        silkscreen="A50k (ATK)",
        notes="CW=slower attack (~0.2 ms to ~25 ms)",
    )
    det_op_out += d3["A"]
    rect_diode_out += d3["K"]
    rect_diode_out & r9 & atk_in
    atk_in += rv2[1]
    env_cap += rv2[2], rv2[3]

    c2 = make_c1u_film(
        "C2", notes="Envelope peak-hold integration cap; Alt: JLC Standard THT"
    )
    env_cap & c2 & gnd

    r10 = make_r0603(
        "R10",
        value="22k",
        mpn="0603WAF2202T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C31850",
        jlcpcb_class="Basic",
        notes="Minimum release discharge resistor (22 ms floor)",
    )
    rv3 = make_pot(
        "RV3",
        value="A1M",
        mpn="RV09AF-40-15K-A1M",
        silkscreen="A1M (REL)",
        notes="CW=slower release (22 ms to 1.022 s)",
    )
    env_cap & r10 & rel_mid
    rel_mid += rv3[1]
    gnd += rv3[2], rv3[3]

    # U2D unity buffer + closed-loop feedback to U2C(-).
    env_cap += u2[12]
    env_node += u2[13], u2[14]

    r27 = make_r10k(
        "R27", notes="U2C active peak-detector feedback (ENV_NODE -> DET_FB)"
    )
    det_fb & r27 & env_node


@subcircuit
def stages5_6_output_offset(
    vcc_p12: Net,
    vcc_n12: Net,
    gnd: Net,
    u1: Part,
    u2: Part,
    env_node: Net,
    env_out: Net,
    inv_out_raw: Net,
) -> None:
    """Stages 5 & 6: Filtered OFFSET divider, U2A summer, U1D inverter, output clamps."""
    offset_top = Net("OFFSET_TOP")
    offset_bot = Net("OFFSET_BOT")
    offset_wiper = Net("OFFSET_WIPER")
    inv_sum = Net("INV_SUM")
    inv_out_tip = Net("INV_OUT_TIP")
    out_sum = Net("OUT_SUM")
    out_tip = Net("OUT_TIP")

    # Filtered ±9.71V OFFSET divider (C13.1 '+' must connect to GND!).
    r11 = make_r1k_0603("R11", notes="OFFSET upper rail RC filter/divider (+12V)")
    c11 = make_c22u_elec(
        "C11", notes="OFFSET_TOP RC PSU filter (+ to OFFSET_TOP, - to GND)"
    )
    c12 = make_c100n("C12", notes="OFFSET_TOP HF bypass to GND")
    vcc_p12 & r11 & offset_top
    offset_top += c11[1]
    gnd += c11[2]
    offset_top & c12 & gnd

    r12 = make_r1k_0603("R12", notes="OFFSET lower rail RC filter/divider (-12V)")
    c13 = make_c22u_elec(
        "C13", notes="OFFSET_BOT RC PSU filter (+ to GND, - to OFFSET_BOT)"
    )
    c14 = make_c100n("C14", notes="OFFSET_BOT HF bypass to GND")
    vcc_n12 & r12 & offset_bot
    gnd += c13[1]
    offset_bot += c13[2]
    offset_bot & c14 & gnd

    rv4 = make_pot(
        "RV4",
        value="B10k",
        mpn="RV09AF-40-15K-B10K",
        silkscreen="B10k (OFFSET)",
        notes="Catalog ref C2839839 (0 stock); CW=+OUT (-8.89V to +8.89V)",
    )
    offset_top += rv4[3]
    offset_wiper += rv4[2]
    offset_bot += rv4[1]

    c15 = make_c100n("C15", notes="OFFSET_WIPER noise suppression bypass to GND")
    offset_wiper & c15 & gnd

    # U2A virtual-ground summer (INV_OUT_RAW).
    gnd += u2[3]
    inv_sum += u2[2]
    inv_out_raw += u2[1]

    r17 = make_r10k("R17", notes="ENV_NODE summing resistor into U2A(-)")
    r13 = make_r10k("R13", notes="OFFSET_WIPER summing resistor into U2A(-)")
    r18 = make_r10k("R18", notes="U2A inverting summer feedback resistor")
    env_node & r17 & inv_sum
    offset_wiper & r13 & inv_sum
    inv_sum & r18 & inv_out_raw

    # INV_OUT protection & jack J3 (J3.TN = NC).
    d8 = make_part(
        "Diode",
        "BAT54S",
        ref="D8",
        value="BAT54S",
        footprint="Package_TO_SOT_SMD:SOT-23",
        mpn="BAT54S,215",
        manufacturer="Nexperia",
        lcsc="C47546",
        jlcpcb_class="Extended",
        silkscreen="BAT54S",
        notes="INV_OUT_RAW Schottky clamp (1=A->-12V, 2=K->+12V, 3=COM->INV_OUT_RAW)",
    )
    vcc_n12 += d8[1]
    vcc_p12 += d8[2]
    inv_out_raw += d8[3]

    r19 = make_r1k_1w("R19", notes="INV_OUT jack fault-rated protection resistor")
    inv_out_raw & r19 & inv_out_tip

    j3 = make_jack(
        "J3",
        silkscreen="INV_OUT",
        notes="Catalog ref C9900009788 (0 stock); J3.TN = NC",
    )
    inv_out_tip += j3["T"]
    gnd += j3["S"]
    j3["TN"] += builtins.NC

    # U1D unity inverter (ENV_OUT).
    gnd += u1[12]
    out_sum += u1[13]
    env_out += u1[14]

    r14 = make_r10k("R14", notes="U1D unity inverter input resistor")
    r15 = make_r10k("R15", notes="U1D unity inverter feedback resistor")
    inv_out_raw & r14 & out_sum & r15 & env_out

    # OUT protection & jack J2 (J2.TN = NC).
    d7 = make_part(
        "Diode",
        "BAT54S",
        ref="D7",
        value="BAT54S",
        footprint="Package_TO_SOT_SMD:SOT-23",
        mpn="BAT54S,215",
        manufacturer="Nexperia",
        lcsc="C47546",
        jlcpcb_class="Extended",
        silkscreen="BAT54S",
        notes="ENV_OUT Schottky clamp (1=A->-12V, 2=K->+12V, 3=COM->ENV_OUT)",
    )
    vcc_n12 += d7[1]
    vcc_p12 += d7[2]
    env_out += d7[3]

    r16 = make_r1k_1w("R16", notes="OUT jack fault-rated protection resistor")
    env_out & r16 & out_tip

    j2 = make_jack(
        "J2",
        silkscreen="OUT",
        notes="Catalog ref C9900009788 (0 stock); J2.TN = NC",
    )
    out_tip += j2["T"]
    gnd += j2["S"]
    j2["TN"] += builtins.NC


@subcircuit
def stage7_led_driver(gnd: Net, u2: Part, env_node: Net) -> None:
    """Stage 7: Active transconductance LED1 driver (U2B, R20, R21, D10)."""
    led_buf_in = Net("LED_BUF_IN")
    led_anode = Net("LED_ANODE")
    led_fb = Net("LED_FB")

    r20 = make_r10k("R20", notes="U2B(+) input isolation resistor")
    env_node & r20 & led_buf_in

    led_buf_in += u2[5]
    led_fb += u2[6]
    led_anode += u2[7]

    led1 = make_part(
        "Device",
        "LED",
        ref="LED1",
        value="3mm LED Yellow",
        footprint="LED_THT:LED_D3.0mm",
        mpn="204-10UYD/S530-A3-L",
        manufacturer="Everlight Elec",
        lcsc="C85160",
        jlcpcb_class="Manual THT",
        silkscreen="ENV",
        notes="Panel-aligned 3mm diffused yellow LED (Pin 1=K, Pin 2=A)",
    )
    d10 = make_1n4148w(
        "D10", notes="Anti-parallel reverse-protection clamp across LED1"
    )
    r21 = make_r0603(
        "R21",
        value="1.5k",
        mpn="0603WAF1501T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C22843",
        jlcpcb_class="Basic",
        notes="LED1 transconductance current-setting resistor (I_LED = V_env / 1.5k)",
    )

    led_anode += led1["A"], d10["K"]
    led_fb += led1["K"], d10["A"]
    led_fb & r21 & gnd


@subcircuit
def diagnostic_test_points(
    gnd: Net,
    vcc_p12: Net,
    vcc_n12: Net,
    preamp_out: Net,
    fwr_out: Net,
    env_node: Net,
    env_out: Net,
    inv_out_raw: Net,
) -> None:
    """Optional DNP through-hole test points TP1-TP8 (Ronghe RH-5001)."""
    tp_specs = [
        ("TP1", gnd, "GND", "GND scope clip anchor"),
        ("TP2", vcc_p12, "+12V", "+12V protected rail downstream of D4"),
        ("TP3", vcc_n12, "-12V", "-12V protected rail downstream of D5"),
        ("TP4", preamp_out, "PREAMP", "PREAMP_OUT (U1A Pin 1)"),
        ("TP5", fwr_out, "FWR_OUT", "FWR_OUT (U1C Pin 8)"),
        ("TP6", env_node, "ENV_NODE", "ENV_NODE (U2D Pin 14)"),
        ("TP7", env_out, "ENV_OUT", "ENV_OUT (U1D Pin 14 pre-R16/D7)"),
        ("TP8", inv_out_raw, "INV_RAW", "INV_OUT_RAW (U2A Pin 1 pre-R19/D8)"),
    ]
    for ref, net, silk_label, note in tp_specs:
        tp = make_part(
            "Connector",
            "TestPoint",
            ref=ref,
            value="RH-5001 (DNP)",
            footprint="TestPoint:TestPoint_Keystone_5000-5004_Miniature",
            mpn="RH-5001",
            manufacturer="ronghe",
            lcsc="C5199801",
            jlcpcb_class="DNP THT",
            silkscreen=silk_label,
            notes=f"{note}; optional manual B.Cu solder or needle probe",
            dnp=True,
            exclude_from_bom=True,
        )
        net += tp[1]


def generate_jlcpcb_bom(
    file_: str = "jlcpcb_bom.csv",
    *,
    include_tht: bool = False,
) -> None:
    """Export a grouped JLCPCB PCBA BOM CSV (`Comment,Designator,Footprint,LCSC Part #`)."""
    groups: dict[tuple[str, str, str], list[str]] = {}
    for part in builtins.default_circuit.parts:
        lcsc = part.fields.get("LCSC", "")
        jlc_class = part.fields.get("JLCPCB_Class", "")
        if (
            not lcsc
            or getattr(part, "dnp", False)
            or getattr(part, "exclude_from_bom", False)
        ):
            continue
        if not include_tht and "THT" in jlc_class:
            continue

        comment = part.value_to_str()
        footprint = getattr(part, "footprint", "").split(":")[-1]
        key = (comment, footprint, lcsc)
        groups.setdefault(key, []).append(part.ref)

    def _ref_sort_key(ref: str) -> tuple[str, int]:
        m = re.match(r"^([A-Za-z]+)(\d+)$", ref)
        return (m.group(1), int(m.group(2))) if m else (ref, 0)

    with open(file_, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (comment, footprint, lcsc), refs in groups.items():
            sorted_refs = sorted(refs, key=_ref_sort_key)
            writer.writerow([comment, ", ".join(sorted_refs), footprint, lcsc])


def build_circuit() -> None:
    """Construct the complete Envelope Follower circuit, run ERC, and export deliverables."""
    pwr_netclass = NetClass("Power", priority=1, trace_width=0.5, clearance=0.25)

    vcc_p12_in = Net("+12V_IN")
    vcc_n12_in = Net("-12V_IN")
    vcc_p12 = Net("+12V")
    vcc_n12 = Net("-12V")
    gnd = Net("GND")

    for pwr_net in (vcc_p12_in, vcc_n12_in, vcc_p12, vcc_n12, gnd):
        pwr_net.drive = POWER
        pwr_net.netclasses = pwr_netclass

    preamp_out = Net("PREAMP_OUT")
    fwr_out = Net("FWR_OUT")
    env_node = Net("ENV_NODE")
    env_out = Net("ENV_OUT")
    inv_out_raw = Net("INV_OUT_RAW")

    tl074_t = Part(
        "Amplifier_Operational",
        "TL074",
        dest=TEMPLATE,
        value="TL074HIDR",
        footprint="Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
    )
    tl074_t.fields["MPN"] = "TL074HIDR"
    tl074_t.fields["Manufacturer"] = "Texas Instruments"
    tl074_t.fields["LCSC"] = "C2878713"
    tl074_t.fields["JLCPCB_Class"] = "Extended"
    tl074_t.fields["Silkscreen"] = "TL074H"

    u1 = tl074_t(ref="U1", tag="u1")
    u1.fields["Notes"] = "Front-end preamp (U1A), FWR (U1B/U1C), OUT inverter (U1D)"
    u2 = tl074_t(ref="U2", tag="u2")
    u2.fields["Notes"] = "INV_OUT summer (U2A), LED driver (U2B), peak det (U2C/U2D)"

    power_supply_section(
        vcc_p12_in,
        vcc_n12_in,
        vcc_p12,
        vcc_n12,
        gnd,
        u1,
        u2,
        tag="power_supply",
    )
    stage1_input_preamp(
        vcc_p12,
        vcc_n12,
        gnd,
        u1,
        preamp_out,
        tag="stage1_preamp",
    )
    stages2_3_precision_fwr(
        gnd,
        u1,
        preamp_out,
        fwr_out,
        tag="stages2_3_fwr",
    )
    stage4_peak_detector(
        gnd,
        u2,
        fwr_out,
        env_node,
        tag="stage4_peak_det",
    )
    stages5_6_output_offset(
        vcc_p12,
        vcc_n12,
        gnd,
        u1,
        u2,
        env_node,
        env_out,
        inv_out_raw,
        tag="stages5_6_output",
    )
    stage7_led_driver(
        gnd,
        u2,
        env_node,
        tag="stage7_led",
    )
    diagnostic_test_points(
        gnd,
        vcc_p12,
        vcc_n12,
        preamp_out,
        fwr_out,
        env_node,
        env_out,
        inv_out_raw,
        tag="test_points",
    )

    erc_assert("len(builtins.default_circuit.parts) == 73", "Expected 73 parts!")
    ERC()
    generate_netlist(file_="envelope_follower.net")
    generate_xml(file_="envelope_follower_bom.xml")
    generate_jlcpcb_bom(file_="jlcpcb_bom.csv", include_tht=False)


if __name__ == "__main__":
    build_circuit()
