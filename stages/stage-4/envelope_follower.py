#!/usr/bin/env python3
"""SKiDL circuit definition for the Stage 3 Improved Eurorack Envelope Follower."""

import builtins
import csv
import os
from dataclasses import dataclass
from pathlib import Path

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
if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)

from skidl import (
    ERC,
    POWER,
    Net,
    NetClass,
    Part,
    erc_assert,
    generate_netlist,
    generate_xml,
    subcircuit,
)


@dataclass(frozen=True)
class PartSpec:
    """Verified component specification linking KiCad symbol/footprint to BOM data."""

    lib: str
    symbol: str
    value: str
    footprint: str
    mpn: str = ""
    manufacturer: str = ""
    lcsc: str = ""
    jlcpcb_class: str = ""
    notes: str = ""


PART_CATALOG: dict[str, PartSpec] = {
    # Active ICs and semiconductors (JLCPCB SMT)
    "TL074H": PartSpec(
        lib="Amplifier_Operational",
        symbol="TL074",
        value="TL074HIDR",
        footprint="Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
        mpn="TL074HIDR",
        manufacturer="Texas Instruments",
        lcsc="C2878713",
        jlcpcb_class="Extended",
        notes="Stock backups: TL074HIPWR (C4370424, TSSOP-14) or TL074HIDYYR (C5116353)",
    ),
    "1N4148W": PartSpec(
        lib="Device",
        symbol="D",
        value="1N4148W",
        footprint="Diode_SMD:D_SOD-123",
        mpn="1N4148W",
        manufacturer="ST (Semtech)",
        lcsc="C81598",
        jlcpcb_class="Basic",
    ),
    "BAV99": PartSpec(
        lib="Diode",
        symbol="BAV99",
        value="BAV99",
        footprint="Package_TO_SOT_SMD:SOT-23",
        mpn="BAV99,215",
        manufacturer="Nexperia",
        lcsc="C2500",
        jlcpcb_class="Basic",
    ),
    "B5819W": PartSpec(
        lib="Device",
        symbol="D",
        value="B5819W",
        footprint="Diode_SMD:D_SOD-123",
        mpn="B5819W SL",
        manufacturer="Jiangsu Changjing",
        lcsc="C8598",
        jlcpcb_class="Basic",
        notes="Compact alt: 1N5819WS (SOD-323, C191023)",
    ),
    # SMD Resistors (JLCPCB SMT)
    "R_470R": PartSpec(
        lib="Device",
        symbol="R",
        value="470R 1%",
        footprint="Resistor_SMD:R_0603_1608Metric",
        mpn="0603WAF4700T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C23179",
        jlcpcb_class="Basic",
    ),
    "R_1K": PartSpec(
        lib="Device",
        symbol="R",
        value="1k 1%",
        footprint="Resistor_SMD:R_0603_1608Metric",
        mpn="0603WAF1001T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C21190",
        jlcpcb_class="Basic",
    ),
    "R_2K2": PartSpec(
        lib="Device",
        symbol="R",
        value="2.2k 1%",
        footprint="Resistor_SMD:R_0603_1608Metric",
        mpn="0603WAF2201T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C4190",
        jlcpcb_class="Basic",
        notes="Use 4.7k 1% if populating ultrabright LED (e.g. C99761)",
    ),
    "R_10K": PartSpec(
        lib="Device",
        symbol="R",
        value="10k 1%",
        footprint="Resistor_SMD:R_0603_1608Metric",
        mpn="0603WAF1002T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C25804",
        jlcpcb_class="Basic",
    ),
    "R_20K": PartSpec(
        lib="Device",
        symbol="R",
        value="20k 1%",
        footprint="Resistor_SMD:R_0603_1608Metric",
        mpn="0603WAF2002T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C4184",
        jlcpcb_class="Basic",
    ),
    "R_47K": PartSpec(
        lib="Device",
        symbol="R",
        value="47k 1%",
        footprint="Resistor_SMD:R_0603_1608Metric",
        mpn="0603WAF4702T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C25819",
        jlcpcb_class="Basic",
    ),
    "R_1M": PartSpec(
        lib="Device",
        symbol="R",
        value="1M 1%",
        footprint="Resistor_SMD:R_0603_1608Metric",
        mpn="0603WAF1004T5E",
        manufacturer="UNI-ROYAL",
        lcsc="C22935",
        jlcpcb_class="Basic",
    ),
    "R_10R_1206": PartSpec(
        lib="Device",
        symbol="R",
        value="10R 1% 0.25W",
        footprint="Resistor_SMD:R_1206_3216Metric",
        mpn="1206W4F100JT5E",
        manufacturer="UNI-ROYAL",
        lcsc="C17903",
        jlcpcb_class="Basic",
    ),
    "R_1K_2512": PartSpec(
        lib="Device",
        symbol="R",
        value="1k 1% 1W",
        footprint="Resistor_SMD:R_2512_6332Metric",
        mpn="25121WF1001T4E",
        manufacturer="UNI-ROYAL",
        lcsc="C54315",
        jlcpcb_class="Extended",
    ),
    # SMD Capacitors (JLCPCB SMT)
    "C_100N": PartSpec(
        lib="Device",
        symbol="C",
        value="100nF 50V X7R",
        footprint="Capacitor_SMD:C_0603_1608Metric",
        mpn="CC0603KRX7R9BB104",
        manufacturer="YAGEO",
        lcsc="C14663",
        jlcpcb_class="Basic",
    ),
    "C_10U_1206": PartSpec(
        lib="Device",
        symbol="C",
        value="10uF 50V X7R",
        footprint="Capacitor_SMD:C_1206_3216Metric",
        mpn="TCC1206X7R106K500HT",
        manufacturer="CCTC",
        lcsc="C5449000",
        jlcpcb_class="Extended",
        notes="Alternates: C132170 (4.7uF 50V X7R 1206) or C694197 (TDK 10uF 50V 1206)",
    ),
    "CP_22U_35V": PartSpec(
        lib="Device",
        symbol="C_Polarized",
        value="22uF 35V Elec",
        footprint="Capacitor_SMD:CP_Elec_5x5.4",
        mpn="RVT22UF35V67RV0104",
        manufacturer="KNSCHA",
        lcsc="C2887274",
        jlcpcb_class="Extended",
        notes="Alternates: C5246583 or C48587226 (D5xL5.4mm)",
    ),
    "C_15P": PartSpec(
        lib="Device",
        symbol="C",
        value="15pF 50V C0G",
        footprint="Capacitor_SMD:C_0603_1608Metric",
        mpn="CL10C150JB8NNNC",
        manufacturer="Samsung Electro-Mechanics",
        lcsc="C1644",
        jlcpcb_class="Basic",
    ),
    "C_47P": PartSpec(
        lib="Device",
        symbol="C",
        value="47pF 50V C0G",
        footprint="Capacitor_SMD:C_0603_1608Metric",
        mpn="CL10C470JB8NNNC",
        manufacturer="Samsung Electro-Mechanics",
        lcsc="C1671",
        jlcpcb_class="Basic",
    ),
    "C_100P": PartSpec(
        lib="Device",
        symbol="C",
        value="100pF 50V C0G",
        footprint="Capacitor_SMD:C_0603_1608Metric",
        mpn="CL10C101JB8NNNC",
        manufacturer="Samsung Electro-Mechanics",
        lcsc="C14858",
        jlcpcb_class="Basic",
    ),
    # Manual Through-Hole Components (excluded from JLCPCB SMT BOM)
    "C_1U_FILM": PartSpec(
        lib="Device",
        symbol="C",
        value="1uF 63V Film",
        footprint="Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm",
        mpn="MKS2C041001F00JSSD",
        manufacturer="WIMA",
        lcsc="C92673",
        jlcpcb_class="Manual THT",
        notes="Mount on B.Cu (rear) to avoid 10.5mm front-panel standoff constraint",
    ),
    "IDC_2X5": PartSpec(
        lib="Connector_Generic",
        symbol="Conn_02x05_Odd_Even",
        value="Eurorack_Power_2x5",
        footprint="Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical",
        mpn="IDC2.54-2*5PZ",
        manufacturer="JXTCONN",
        lcsc="C53207560",
        jlcpcb_class="Manual THT",
        notes="Mount on B.Cu; Pin 1/2 (-12Vin red stripe) matches key notch",
    ),
    "LED_3MM": PartSpec(
        lib="Device",
        symbol="LED",
        value="LED 3mm",
        footprint="LED_THT:LED_D3.0mm",
        manufacturer="Everlight",
        lcsc="C84774",
        jlcpcb_class="Manual THT",
        notes="Red C84774 default; alts: Yellow C85160, Yel-Grn C85161, Ultrabright C99761",
    ),
    "JACK_35MM": PartSpec(
        lib="Connector_Audio",
        symbol="AudioJack2_SwitchT",
        value="WQP-PJ398SM",
        footprint="Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles",
        mpn="WQP-PJ398SM",
        manufacturer="QingPu",
        jlcpcb_class="Manual THT",
        notes="Source externally (Thonkiconn); 10.5mm front-panel standoff",
    ),
    "POT_9MM": PartSpec(
        lib="Device",
        symbol="R_Potentiometer",
        value="9mm_Pot",
        footprint="Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical",
        manufacturer="Alpha/Bourns",
        jlcpcb_class="Manual THT",
        notes="Source externally (Alpha RD901F / RV09AF-40 or Bourns PTV09A); 10.5mm standoff",
    ),
    # Optional DNP Test Points
    "TP_RH5001": PartSpec(
        lib="Connector",
        symbol="TestPoint",
        value="RH-5001",
        footprint="TestPoint:TestPoint_Keystone_5000-5004_Miniature",
        mpn="RH-5001",
        manufacturer="Ronghe",
        lcsc="C5199801",
        jlcpcb_class="Manual THT (DNP)",
        notes="Optional DNP; mount on B.Cu if soldered or needle-probe plated pads",
    ),
}


def add_part(
    spec_key: str,
    ref: str,
    *,
    value_override: str | None = None,
    notes_override: str | None = None,
    dnp: bool = False,
    exclude_from_bom: bool = False,
) -> Part:
    """Instantiate a KiCad Part with verified BOM fields and deterministic tag."""
    spec = PART_CATALOG[spec_key]
    part = Part(
        spec.lib,
        spec.symbol,
        value=value_override or spec.value,
        footprint=spec.footprint,
        ref=ref,
        tag=ref.lower(),
    )
    notes = notes_override if notes_override is not None else spec.notes
    if spec.mpn:
        part.fields["MPN"] = spec.mpn
    if spec.manufacturer:
        part.fields["Manufacturer"] = spec.manufacturer
    if spec.lcsc:
        part.fields["LCSC"] = spec.lcsc
    if spec.jlcpcb_class:
        part.fields["JLCPCB_Class"] = spec.jlcpcb_class
    if notes:
        part.fields["Notes"] = notes
    if dnp:
        part.dnp = True
    if exclude_from_bom:
        part.exclude_from_bom = True
    return part


@subcircuit
def power_supply(
    p12v_prot: Net,
    n12v_prot: Net,
    gnd: Net,
    u1: Part,
    u2: Part,
    pwr_netclass: NetClass,
) -> None:
    """Eurorack 2x5 power header, Schottky reverse-polarity guard, RC surge filter, and IC decoupling."""
    p12v_in = Net("+12Vin")
    n12v_in = Net("-12Vin")
    p12v_diode = Net("+12V_DIODE")
    n12v_diode = Net("-12V_DIODE")
    for net in (p12v_in, n12v_in, p12v_diode, n12v_diode):
        net.netclasses = pwr_netclass

    j_pwr = add_part("IDC_2X5", "J_PWR")
    d10 = add_part("B5819W", "D10")
    d11 = add_part("B5819W", "D11")
    r24 = add_part("R_10R_1206", "R24")
    r25 = add_part("R_10R_1206", "R25")
    c3 = add_part("CP_22U_35V", "C3")
    c4 = add_part("CP_22U_35V", "C4")
    c5 = add_part("C_100N", "C5")
    c6 = add_part("C_100N", "C6")
    c7 = add_part("C_100N", "C7")
    c8 = add_part("C_100N", "C8")

    n12v_in += j_pwr[1], j_pwr[2]
    for pin_num in range(3, 9):
        gnd += j_pwr[pin_num]
    p12v_in += j_pwr[9], j_pwr[10]

    p12v_in += d10["A"]
    p12v_diode += d10["K"]
    n12v_diode += d11["A"]
    n12v_in += d11["K"]

    p12v_diode += r24[1]
    p12v_prot += r24[2]
    n12v_diode += r25[1]
    n12v_prot += r25[2]

    # Bulk electrolytics (C4 positive pin ties to GND, negative pin ties to -12V_PROT)
    p12v_prot += c3[1]
    gnd += c3[2]
    gnd += c4[1]
    n12v_prot += c4[2]

    # Local 100nF decoupling per rail per op-amp IC
    p12v_prot += c5[1], c7[1], u1[4], u2[4]
    n12v_prot += c6[1], c8[1], u1[11], u2[11]
    gnd += c5[2], c6[2], c7[2], c8[2]


@subcircuit
def input_preamp(
    gnd: Net,
    preamp_out: Net,
    u1: Part,
) -> None:
    """Switched mono input jack, AC coupling, clamp diodes, and U1A inverting preamp."""
    in_jack = Net("IN_JACK")
    in_ac = Net("IN_AC")
    preamp_inv = Net("PREAMP_INV")
    gain_min = Net("GAIN_MIN")

    j1 = add_part("JACK_35MM", "J1", value_override="IN")
    r1 = add_part("R_1M", "R1")
    c1 = add_part("C_10U_1206", "C1")
    r2 = add_part("R_10K", "R2")
    r26 = add_part("R_1K", "R26")
    rv1 = add_part(
        "POT_9MM",
        "RV1",
        value_override="A100k",
        notes_override="GAIN Audio/Log A100k 9mm vertical pot (Alpha RD901F/RV09AF-40 or Bourns PTV09A); external",
    )
    c9 = add_part("C_47P", "C9")
    d5 = add_part("1N4148W", "D5")
    d6 = add_part("1N4148W", "D6")

    in_jack += j1["T"], r1[1], c1[1]
    gnd += j1["S"], j1["TN"], r1[2]

    in_ac += c1[2], r2[1]
    preamp_inv += r2[2], u1[2], r26[1], c9[1], d5["A"], d6["K"]
    gnd += u1[3], d5["K"], d6["A"]

    gain_min += r26[2], rv1[1]
    preamp_out += u1[1], rv1[2], rv1[3], c9[2]


@subcircuit
def full_wave_rectifier(
    gnd: Net,
    preamp_out: Net,
    half_wave: Net,
    rect_out: Net,
    u1: Part,
) -> None:
    """-0.5x precision half-wave rectifier (U1B) summed into 1.00x full-wave rectifier (U1C)."""
    rect_inv = Net("RECT_INV")
    u1b_out = Net("U1B_OUT")
    rect_ff_mid = Net("RECT_FF_MID")
    sum_inv = Net("SUM_INV")
    rect_fb_mid = Net("RECT_FB_MID")

    r3 = add_part("R_20K", "R3")
    r4 = add_part("R_20K", "R4")
    r5 = add_part("R_20K", "R5")
    r6 = add_part("R_10K", "R6")
    r7 = add_part("R_10K", "R7")
    r8a = add_part("R_20K", "R8A")
    r8b = add_part("R_20K", "R8B")
    c10 = add_part("C_15P", "C10")
    d1 = add_part("1N4148W", "D1")
    d2 = add_part("1N4148W", "D2")

    preamp_out += r3[1], r4[1]
    rect_inv += r3[2], u1[6], d1["K"], r6[1]
    gnd += u1[5]
    u1b_out += u1[7], d1["A"], d2["K"]
    half_wave += d2["A"], r6[2], r7[1]

    rect_ff_mid += r4[2], r5[1]
    sum_inv += r5[2], r7[2], u1[9], r8a[1], c10[1]
    gnd += u1[10]
    rect_fb_mid += r8a[2], r8b[1]
    rect_out += u1[8], r8b[2], c10[2]


@subcircuit
def peak_detector_envelope(
    gnd: Net,
    rect_out: Net,
    peak_det: Net,
    env_raw_buf: Net,
    u2: Part,
) -> None:
    """Active zero-deadzone peak detector (U2C), Attack/Release RC tank (C2), and unity buffer (U2D)."""
    u2c_out = Net("U2C_OUT")
    atk_min = Net("ATK_MIN")
    env_raw = Net("ENV_RAW")
    rel_mid = Net("REL_MID")

    d3 = add_part("1N4148W", "D3")
    r28 = add_part("R_470R", "R28")
    rv2 = add_part(
        "POT_9MM",
        "RV2",
        value_override="A50k",
        notes_override="ATK Audio/Log A50k 9mm vertical pot; source externally",
    )
    c2 = add_part("C_1U_FILM", "C2")
    r10 = add_part("R_47K", "R10")
    rv3 = add_part(
        "POT_9MM",
        "RV3",
        value_override="A1M",
        notes_override="RELEASE Audio/Log A1M 9mm vertical pot; source externally",
    )

    rect_out += u2[10]
    u2c_out += u2[8], d3["A"]
    peak_det += d3["K"], u2[9], r28[1]

    atk_min += r28[2], rv2[1]
    env_raw += rv2[2], rv2[3], c2[1], r10[1], u2[12]
    gnd += c2[2], rv3[2], rv3[3]

    rel_mid += r10[2], rv3[1]
    env_raw_buf += u2[14], u2[13]


@subcircuit
def led_driver(
    p12v_prot: Net,
    gnd: Net,
    env_raw_buf: Net,
    u2: Part,
) -> None:
    """Closed-loop LED current sink (U2B) with +25mV idle cutoff threshold."""
    led_a = Net("LED_A")
    led_k = Net("LED_K")

    d4 = add_part("LED_3MM", "D4")
    d7 = add_part("1N4148W", "D7")
    c13 = add_part("C_100P", "C13")
    r29 = add_part("R_2K2", "R29")
    r30 = add_part("R_1M", "R30")

    env_raw_buf += u2[5]
    led_a += u2[7], d4["A"], d7["K"], c13[1]
    led_k += d4["K"], u2[6], d7["A"], c13[2], r29[1], r30[2]
    p12v_prot += r30[1]
    gnd += r29[2]


@subcircuit
def offset_and_outputs(
    p12v_prot: Net,
    n12v_prot: Net,
    gnd: Net,
    env_raw_buf: Net,
    u1: Part,
    u2: Part,
) -> None:
    """CW-positive offset summer (U2A -> INV_OUT) and unity inverter (U1D -> OUT) with rail clamps."""
    off_top = Net("OFF_TOP")
    off_bot = Net("OFF_BOT")
    off_wiper = Net("OFF_WIPER")
    sum_off_inv = Net("SUM_OFF_INV")
    inv_drv = Net("INV_DRV")
    inv_out_jack = Net("INV_OUT_JACK")
    out_inv = Net("OUT_INV")
    env_out = Net("ENV_OUT")
    out_jack = Net("OUT_JACK")

    r11 = add_part("R_470R", "R11")
    r12 = add_part("R_470R", "R12")
    rv4 = add_part(
        "POT_9MM",
        "RV4",
        value_override="B10k",
        notes_override="OFFSET Linear B10k 9mm pot (center detent, e.g. Alpha RD901F-40-15F-B10K-C); external",
    )
    r13 = add_part("R_20K", "R13")
    r14 = add_part("R_10K", "R14")
    r15 = add_part("R_10K", "R15")
    r17 = add_part("R_10K", "R17")
    r18 = add_part("R_10K", "R18")
    c11 = add_part("C_47P", "C11")
    c12 = add_part("C_47P", "C12")
    d8 = add_part("BAV99", "D8")
    d9 = add_part("BAV99", "D9")
    r16 = add_part("R_1K_2512", "R16")
    r19 = add_part("R_1K_2512", "R19")
    j2 = add_part("JACK_35MM", "J2", value_override="OUT")
    j3 = add_part("JACK_35MM", "J3", value_override="INV_OUT")

    # Offset divider (+/-5.15V span, CW Pin 3 toward +12V_PROT)
    p12v_prot += r11[1]
    off_top += r11[2], rv4[3]
    n12v_prot += r12[1]
    off_bot += r12[2], rv4[1]
    off_wiper += rv4[2], r13[1]

    # U2A Inverting Offset Summer -> J3 INV_OUT
    env_raw_buf += r14[1]
    sum_off_inv += r13[2], r14[2], u2[2], r18[1], c11[1]
    gnd += u2[3]
    inv_drv += u2[1], r18[2], c11[2], r17[1], d9[3], r19[1]
    n12v_prot += d9[1]
    p12v_prot += d9[2]
    inv_out_jack += r19[2], j3["T"]
    gnd += j3["S"]
    j3["TN"] += builtins.NC

    # U1D Unity Inverter -> J2 OUT
    out_inv += r17[2], u1[13], r15[1], c12[1]
    gnd += u1[12]
    env_out += u1[14], r15[2], c12[2], d8[3], r16[1]
    n12v_prot += d8[1]
    p12v_prot += d8[2]
    out_jack += r16[2], j2["T"]
    gnd += j2["S"]
    j2["TN"] += builtins.NC


@subcircuit
def bench_test_points(nodes: tuple[tuple[str, Net], ...]) -> None:
    """Eight optional DNP Ronghe RH-5001 test points for rear B.Cu bench probing."""
    for idx, (label, net) in enumerate(nodes, start=1):
        ref = f"TP{idx}"
        tp = add_part(
            "TP_RH5001",
            ref,
            notes_override=f"Optional DNP test point on {label}; mount on B.Cu if populated",
            dnp=True,
            exclude_from_bom=True,
        )
        net += tp[1]


def generate_jlcpcb_bom(
    file_: str | Path = "jlcpcb_bom.csv", include_tht: bool = False
) -> None:
    """Export a grouped 4-column JLCPCB PCBA BOM CSV (`Comment,Designator,Footprint,LCSC Part #`)."""
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

    with open(file_, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (comment, footprint, lcsc), refs in groups.items():
            writer.writerow([comment, ", ".join(refs), footprint, lcsc])


def build_circuit() -> None:
    """Assemble the complete Envelope Follower circuit, net classes, and ERC assertions."""
    pwr_netclass = NetClass("PowerRails", priority=1, trace_width=0.6, clearance=0.25)
    sig_netclass = NetClass("AnalogSignal", priority=2, trace_width=0.25, clearance=0.2)

    p12v_prot = Net("+12V_PROT")
    n12v_prot = Net("-12V_PROT")
    gnd = Net("GND")
    for pwr_net in (p12v_prot, n12v_prot, gnd):
        pwr_net.drive = POWER
        pwr_net.netclasses = pwr_netclass

    preamp_out = Net("PREAMP_OUT")
    half_wave = Net("HALF_WAVE")
    rect_out = Net("RECT_OUT")
    peak_det = Net("PEAK_DET")
    env_raw_buf = Net("ENV_RAW_BUF")

    u1 = add_part("TL074H", "U1")
    u2 = add_part("TL074H", "U2")

    power_supply(p12v_prot, n12v_prot, gnd, u1, u2, pwr_netclass, tag="pwr")
    input_preamp(gnd, preamp_out, u1, tag="preamp")
    full_wave_rectifier(gnd, preamp_out, half_wave, rect_out, u1, tag="rectifier")
    peak_detector_envelope(gnd, rect_out, peak_det, env_raw_buf, u2, tag="envelope")
    led_driver(p12v_prot, gnd, env_raw_buf, u2, tag="led")
    offset_and_outputs(p12v_prot, n12v_prot, gnd, env_raw_buf, u1, u2, tag="outputs")
    bench_test_points(
        (
            ("GND", gnd),
            ("+12V_PROT", p12v_prot),
            ("-12V_PROT", n12v_prot),
            ("PREAMP_OUT", preamp_out),
            ("HALF_WAVE", half_wave),
            ("RECT_OUT", rect_out),
            ("PEAK_DET", peak_det),
            ("ENV_RAW_BUF", env_raw_buf),
        ),
        tag="test_points",
    )

    for net in builtins.default_circuit.nets:
        if net is not builtins.NC and not getattr(net, "netclasses", None):
            net.netclasses = sig_netclass

    erc_assert(
        "len(builtins.default_circuit.parts) == 67", "Expected 67 total footprints"
    )


def main() -> None:
    """Build circuit, run ERC, and export KiCad netlist, XML BOM, and JLCPCB BOM CSV."""
    out_dir = Path(__file__).resolve().parent
    os.chdir(out_dir)
    build_circuit()
    ERC()
    generate_netlist(file_=str(out_dir / "envelope_follower.net"))
    generate_xml(file_=str(out_dir / "envelope_follower_bom.xml"))
    generate_jlcpcb_bom(file_=out_dir / "jlcpcb_bom.csv")


if __name__ == "__main__":
    main()
