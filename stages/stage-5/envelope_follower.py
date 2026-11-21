#!/usr/bin/env python3
"""
Eurorack Envelope Follower (Improved Revision) — SKiDL Circuit & Netlist Generator.

Implements the complete 68-footprint (60 populated + 8 DNP test points), 170-pin
Eurorack Envelope Follower circuit specified in:
  - EnvelopeFollowerImproved.md
  - EnvelopeFollowerBOM.md
  - SilkscreenInstructions.md

Exports (in the script directory):
  - envelope_follower.erc
  - envelope_follower.net
  - envelope_follower_bom.xml
  - jlcpcb_bom.csv (49 B.Cu SMT placements for JLCPCB Economic PCBA)
"""

import builtins
import csv
import os
import re
from pathlib import Path

# Keep SKiDL caches, matplotlib config, and generated .erc/.log files strictly inside stage-4.
STAGE_DIR = Path(__file__).resolve().parent
os.chdir(STAGE_DIR)
os.environ.setdefault("XDG_DATA_HOME", "/tmp/xdg_data")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_config")

KICAD_SHARED = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport")
KICAD_SYM_DIR = KICAD_SHARED / "symbols"
KICAD_FP_DIR = KICAD_SHARED / "footprints"
if KICAD_SYM_DIR.is_dir():
    os.environ.setdefault("KICAD_SYMBOL_DIR", str(KICAD_SYM_DIR))
    for _ver in (6, 7, 8, 9, 10):
        os.environ.setdefault(f"KICAD{_ver}_SYMBOL_DIR", str(KICAD_SYM_DIR))
if KICAD_FP_DIR.is_dir():
    os.environ.setdefault("KICAD10_FOOTPRINT_DIR", str(KICAD_FP_DIR))

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
)

# ---------------------------------------------------------------------------
# Catalog Specifications (100% LCSC/JLCPCB Verified per EnvelopeFollowerBOM.md)
# ---------------------------------------------------------------------------

RESISTOR_SPECS: dict[str, dict[str, str]] = {
    "10k": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "LCSC": "C25804",
        "MPN": "0603WAF1002T5E",
        "Manufacturer": "UNI-ROYAL",
        "JLCPCB_Class": "Basic",
        "Notes": "B.Cu SMT; 10k 1% 100mW 0603 thick film",
    },
    "100k": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "LCSC": "C25803",
        "MPN": "0603WAF1003T5E",
        "Manufacturer": "UNI-ROYAL",
        "JLCPCB_Class": "Basic",
        "Notes": "B.Cu SMT; 100k 1% 100mW 0603 thick film",
    },
    "20k": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "LCSC": "C4184",
        "MPN": "0603WAF2002T5E",
        "Manufacturer": "UNI-ROYAL",
        "JLCPCB_Class": "Basic",
        "Notes": "B.Cu SMT; 20k 1% 100mW 0603 thick film (1.00x rectifier)",
    },
    "6.8k": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "LCSC": "C23212",
        "MPN": "0603WAF6801T5E",
        "Manufacturer": "UNI-ROYAL",
        "JLCPCB_Class": "Basic",
        "Notes": "B.Cu SMT; 6.8k 1% 100mW 0603 thick film (OFFSET divider)",
    },
    "10R": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "LCSC": "C22859",
        "MPN": "0603WAF100JT5E",
        "Manufacturer": "UNI-ROYAL",
        "JLCPCB_Class": "Basic",
        "Notes": "B.Cu SMT; 10R 1% 100mW 0603 RC rail damping",
    },
    "1k 1W": {
        "footprint": "Resistor_SMD:R_2512_6332Metric",
        "LCSC": "C54315",
        "MPN": "25121WF1001T4E",
        "Manufacturer": "UNI-ROYAL",
        "JLCPCB_Class": "Extended",
        "Notes": "B.Cu SMT; 1k 1% 1W 2512 fault-rated output build-out; keep C54315",
    },
    "1k": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "LCSC": "C21190",
        "MPN": "0603WAF1001T5E",
        "Manufacturer": "UNI-ROYAL",
        "JLCPCB_Class": "Basic",
        "Notes": "B.Cu SMT; 1k 1% 100mW 0603 LED constant-current sense",
    },
    "4.7k": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "LCSC": "C23162",
        "MPN": "0603WAF4701T5E",
        "Manufacturer": "UNI-ROYAL",
        "JLCPCB_Class": "Basic",
        "Notes": "B.Cu SMT; 4.7k 1% 100mW 0603 GAIN floor",
    },
    "150R": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "LCSC": "C22808",
        "MPN": "0603WAF1500T5E",
        "Manufacturer": "UNI-ROYAL",
        "JLCPCB_Class": "Basic",
        "Notes": "B.Cu SMT; 150R 1% 100mW 0603 minimum attack protection",
    },
    "200k": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "LCSC": "C25811",
        "MPN": "0603WAF2003T5E",
        "Manufacturer": "UNI-ROYAL",
        "JLCPCB_Class": "Basic",
        "Notes": "B.Cu SMT; 200k 1% 100mW 0603 U2C peak-detector feedback",
    },
    "1M": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "LCSC": "C22935",
        "MPN": "0603WAF1004T5E",
        "Manufacturer": "UNI-ROYAL",
        "JLCPCB_Class": "Basic",
        "Notes": "B.Cu SMT; 1M 1% 100mW 0603 U1A+ open-wiper pull-down",
    },
    "4.7M": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "LCSC": "C23163",
        "MPN": "0603WAF4704T5E",
        "Manufacturer": "UNI-ROYAL",
        "JLCPCB_Class": "Preferred Extended",
        "Notes": "B.Cu SMT; 4.7M 1% 100mW 0603 Release open-wiper safety bleed",
    },
}

CAP_SMD_SPECS: dict[str, dict[str, str]] = {
    "100nF 50V": {
        "footprint": "Capacitor_SMD:C_0603_1608Metric",
        "LCSC": "C14663",
        "MPN": "CC0603KRX7R9BB104",
        "Manufacturer": "YAGEO",
        "JLCPCB_Class": "Basic",
        "Silkscreen": "100nF",
        "Notes": "B.Cu SMT; 100nF 50V X7R 10% 0603 local IC decoupling (<5mm to U1/U2)",
    },
    "22pF 50V": {
        "footprint": "Capacitor_SMD:C_0603_1608Metric",
        "LCSC": "C1653",
        "MPN": "CL10C220JB8NNNC",
        "Manufacturer": "Samsung Electro-Mechanics",
        "JLCPCB_Class": "Basic",
        "Silkscreen": "22pF",
        "Notes": "B.Cu SMT; 22pF 50V C0G 5% 0603 U1A HF compensation (72kHz)",
    },
    "100pF 50V": {
        "footprint": "Capacitor_SMD:C_0603_1608Metric",
        "LCSC": "C14858",
        "MPN": "CL10C101JB8NNNC",
        "Manufacturer": "Samsung Electro-Mechanics",
        "JLCPCB_Class": "Basic",
        "Silkscreen": "100pF",
        "Notes": "B.Cu SMT; 100pF 50V C0G 5% 0603 U2C peak-detector loop comp (>70deg PM)",
    },
}


# ---------------------------------------------------------------------------
# Part Factory Helpers
# ---------------------------------------------------------------------------


def _apply_fields(part: Part, fields: dict[str, str]) -> Part:
    """Populate custom BOM and silkscreen metadata into `part.fields`."""
    for key, val in fields.items():
        part.fields[key] = val
    return part


def make_resistor(ref: str, value: str, tag: str | None = None) -> Part:
    """Instantiate a B.Cu SMT resistor matching EnvelopeFollowerBOM.md."""
    spec = RESISTOR_SPECS[value]
    part = Part(
        "Device",
        "R",
        ref=ref,
        value=value,
        footprint=spec["footprint"],
        tag=tag or ref.lower(),
    )
    return _apply_fields(
        part,
        {
            "LCSC": spec["LCSC"],
            "MPN": spec["MPN"],
            "Manufacturer": spec["Manufacturer"],
            "JLCPCB_Class": spec["JLCPCB_Class"],
            "Side": "B.Cu",
            "Silkscreen": "1k" if value == "1k 1W" else value,
            "Notes": spec["Notes"],
        },
    )


def make_smd_cap(ref: str, value: str, tag: str | None = None) -> Part:
    """Instantiate a B.Cu 0603 SMD ceramic capacitor."""
    spec = CAP_SMD_SPECS[value]
    part = Part(
        "Device",
        "C",
        ref=ref,
        value=value,
        footprint=spec["footprint"],
        tag=tag or ref.lower(),
    )
    return _apply_fields(
        part,
        {
            "LCSC": spec["LCSC"],
            "MPN": spec["MPN"],
            "Manufacturer": spec["Manufacturer"],
            "JLCPCB_Class": spec["JLCPCB_Class"],
            "Side": "B.Cu",
            "Silkscreen": spec["Silkscreen"],
            "Notes": spec["Notes"],
        },
    )


def make_bulk_cap(ref: str, role_note: str) -> Part:
    """Instantiate a B.Cu 47uF 35V SMD aluminum electrolytic capacitor."""
    part = Part(
        "Device",
        "C_Polarized",
        ref=ref,
        value="47uF 35V",
        footprint="Capacitor_SMD:CP_Elec_6.3x5.4",
        tag=ref.lower(),
    )
    return _apply_fields(
        part,
        {
            "LCSC": "C2836440",
            "MPN": "RVT47UF35V67RV0039",
            "Manufacturer": "KNSCHA",
            "JLCPCB_Class": "Extended",
            "Side": "B.Cu",
            "Silkscreen": "47uF",
            "Notes": (
                f"B.Cu SMT; {role_note}; mandatory +/- polarity on B.SilkS; "
                "Alt: C2836438 (22uF 50V)"
            ),
        },
    )


def make_film_cap(ref: str, role_note: str) -> Part:
    """Instantiate a B.Cu rear manual THT 1uF 63V PET box film capacitor."""
    part = Part(
        "Device",
        "C",
        ref=ref,
        value="1uF 63V",
        footprint="Capacitor_THT:C_Rect_L7.2mm_W5.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2",
        tag=ref.lower(),
    )
    return _apply_fields(
        part,
        {
            "LCSC": "C328852",
            "MPN": "C241J105J2SA201",
            "Manufacturer": "Xiamen Faratronic",
            "JLCPCB_Class": "Manual THT",
            "Side": "B.Cu",
            "Silkscreen": "1uF",
            "Notes": (
                f"B.Cu Rear Manual THT; {role_note}; P=5.0mm box film; "
                "Alt: C3975271 (KNSCHA), C92673 (WIMA)"
            ),
        },
    )


def make_opamp(ref: str) -> Part:
    """Instantiate a B.Cu TL074HIDR SOIC-14 quad FET-input op-amp."""
    part = Part(
        "Amplifier_Operational",
        "TL074",
        ref=ref,
        value="TL074H",
        footprint="Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
        tag=ref.lower(),
    )
    return _apply_fields(
        part,
        {
            "LCSC": "C2878713",
            "MPN": "TL074HIDR",
            "Manufacturer": "Texas Instruments",
            "JLCPCB_Class": "Extended",
            "Side": "B.Cu",
            "Silkscreen": f"{ref} TL074H",
            "Notes": "B.Cu SMT; 40V FET-input quad op-amp; Pin 1 dot on B.SilkS",
        },
    )


def make_1n4148ws(ref: str) -> Part:
    """Instantiate a B.Cu 1N4148WS SOD-323 switching diode (Pin 1=K, Pin 2=A)."""
    part = Part(
        "Diode",
        "1N4148WS",
        ref=ref,
        value="1N4148WS",
        footprint="Diode_SMD:D_SOD-323",
        tag=ref.lower(),
    )
    return _apply_fields(
        part,
        {
            "LCSC": "C2128",
            "MPN": "1N4148WS",
            "Manufacturer": "Jiangsu Changjing (JSCJ)",
            "JLCPCB_Class": "Basic",
            "Side": "B.Cu",
            "Silkscreen": f"{ref} 1N4148WS",
            "Notes": (
                "B.Cu SMT; Pad 1 = K (0.25mm cathode bar on B.SilkS); "
                "Alt: C81598 (1N4148W SOD-123 Basic)"
            ),
        },
    )


def make_1n5819ws(ref: str) -> Part:
    """Instantiate a B.Cu 1N5819WS SOD-323 Schottky diode (Pin 1=K, Pin 2=A)."""
    part = Part(
        "Diode",
        "1N5819WS",
        ref=ref,
        value="1N5819WS",
        footprint="Diode_SMD:D_SOD-323",
        tag=ref.lower(),
    )
    return _apply_fields(
        part,
        {
            "LCSC": "C191023",
            "MPN": "1N5819WS",
            "Manufacturer": "Guangdong Hottech",
            "JLCPCB_Class": "Basic",
            "Side": "B.Cu",
            "Silkscreen": f"{ref} 1N5819WS",
            "Notes": (
                "B.Cu SMT; 40V 1A Schottky reverse-polarity protection; "
                "Pad 1 = K (cathode bar on B.SilkS); Alt: C8598 (B5819W SOD-123 Basic)"
            ),
        },
    )


def make_bat54s(ref: str) -> Part:
    """Instantiate a B.Cu BAT54S SOT-23 dual series Schottky clamp."""
    part = Part(
        "Diode",
        "BAT54S",
        ref=ref,
        value="BAT54S",
        footprint="Package_TO_SOT_SMD:SOT-23",
        tag=ref.lower(),
    )
    return _apply_fields(
        part,
        {
            "LCSC": "C47546",
            "MPN": "BAT54S,215",
            "Manufacturer": "Nexperia",
            "JLCPCB_Class": "Extended",
            "Side": "B.Cu",
            "Silkscreen": f"{ref} BAT54S",
            "Notes": (
                "B.Cu SMT; Pin 1=A (-12V_PROT), Pin 2=K (+12V_PROT), Pin 3=COM; "
                "Alt: C19726 (onsemi), C12765 (LRC)"
            ),
        },
    )


def make_jack(ref: str, label: str, tn_note: str) -> Part:
    """Instantiate an F.Cu WQP-PJ398SM 3.5mm mono switched jack."""
    part = Part(
        "Connector_Audio",
        "AudioJack2_SwitchT",
        ref=ref,
        value=label,
        footprint="Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles",
        tag=ref.lower(),
    )
    return _apply_fields(
        part,
        {
            "MPN": "WQP-PJ398SM",
            "Manufacturer": "QingPu",
            "JLCPCB_Class": "Manual THT",
            "Side": "F.Cu",
            "Silkscreen": f"{ref} {label}",
            "Notes": (
                f"F.Cu Front-Panel Manual THT; 3.5mm Mono Switched Jack (Thonkiconn); "
                f"{tn_note}"
            ),
        },
    )


def make_pot(ref: str, value: str, panel_label: str, mpn: str, note: str) -> Part:
    """Instantiate an F.Cu Alpha RD901F 9mm vertical potentiometer."""
    part = Part(
        "Device",
        "R_Potentiometer",
        ref=ref,
        value=value,
        footprint="Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical",
        tag=ref.lower(),
    )
    return _apply_fields(
        part,
        {
            "MPN": mpn,
            "Manufacturer": "Taiwan Alpha",
            "JLCPCB_Class": "Manual THT",
            "Side": "F.Cu",
            "Silkscreen": f"{ref} {panel_label} {value}",
            "Notes": f"F.Cu Front-Panel Manual THT; {note}",
        },
    )


def make_test_point(ref: str, net: Net) -> Part:
    """Instantiate a rear B.Cu DNP Ronghe RH-5001 test point attached to `net`."""
    tp_t = Part(
        "Connector",
        "TestPoint",
        dest=TEMPLATE,
        footprint="TestPoint:TestPoint_Keystone_5000-5004_Miniature",
    )
    tp = tp_t(ref=ref, value=net.name, tag=ref.lower())
    tp.dnp = True
    tp.exclude_from_bom = True
    _apply_fields(
        tp,
        {
            "LCSC": "C5199801",
            "MPN": "RH-5001",
            "Manufacturer": "Ronghe",
            "JLCPCB_Class": "Manual THT (DNP)",
            "Side": "B.Cu",
            "Silkscreen": f"{ref} {net.name}",
            "Notes": (
                f"DNP — Optional rear B.Cu test point ({net.name}); "
                "Ronghe RH-5001 (C5199801), bare 1.0mm plated hole if unpopulated"
            ),
        },
    )
    net += tp[1]
    return tp


# ---------------------------------------------------------------------------
# Circuit Construction
# ---------------------------------------------------------------------------


def build_envelope_follower() -> None:
    """Construct the complete Eurorack Envelope Follower circuit in default_circuit."""
    pwr_class = NetClass("Power", priority=1, trace_width=0.5, clearance=0.25)

    # Power rails (externally fed via J4, reverse-protected & RC-filtered to +/-12V_PROT)
    vplus_in = Net("+12V_IN")
    vminus_in = Net("-12V_IN")
    vplus_filt_in = Net("+12V_FILT_IN")
    vminus_filt_in = Net("-12V_FILT_IN")
    vplus_prot = Net("+12V_PROT")
    vminus_prot = Net("-12V_PROT")
    gnd = Net("GND")

    for rail in (
        vplus_in,
        vminus_in,
        vplus_filt_in,
        vminus_filt_in,
        vplus_prot,
        vminus_prot,
        gnd,
    ):
        rail.netclasses = pwr_class

    # External bus power rails and protected internal rails fed through passive D7/R28 & D8/R29
    vplus_in.drive = POWER
    vminus_in.drive = POWER
    vplus_prot.drive = POWER
    vminus_prot.drive = POWER
    gnd.drive = POWER

    # Signal nets
    in_tip = Net("IN_TIP")
    in_clamp = Net("IN_CLAMP")
    in_pot_top = Net("IN_POT_TOP")
    in_pot_bot = Net("IN_POT_BOT")
    in_wiper = Net("IN_WIPER")
    in_gain_inv = Net("IN_GAIN_INV")
    v_gain = Net("V_GAIN")

    rect_inv = Net("RECT_INV")
    rect_op_out = Net("RECT_OP_OUT")
    rect_mid = Net("RECT_MID")
    sum_inv = Net("SUM_INV")
    v_rect = Net("V_RECT")

    peak_inv = Net("PEAK_INV")
    peak_op_out = Net("PEAK_OP_OUT")
    rect_diode_out = Net("RECT_DIODE_OUT")
    atk_mid = Net("ATK_MID")
    env_cap = Net("ENV_CAP")
    rel_mid = Net("REL_MID")
    v_env_buf = Net("V_ENV_BUF")

    out_noninv = Net("OUT_NONINV")
    off_top = Net("OFF_TOP")
    off_bot = Net("OFF_BOT")
    off_wiper = Net("OFF_WIPER")
    out_inv_node = Net("OUT_INV_NODE")
    v_out_buf = Net("V_OUT_BUF")
    out_tip = Net("OUT_TIP")

    inv_sum = Net("INV_SUM")
    v_inv_buf = Net("V_INV_BUF")
    inv_out_tip = Net("INV_OUT_TIP")

    led_ref_in = Net("LED_REF_IN")
    led_sense = Net("LED_SENSE")
    v_led_drv = Net("V_LED_DRV")

    # -----------------------------------------------------------------------
    # Quad Op-Amps (U1, U2) & Supply Rails + Local Decoupling (C5-C8)
    # -----------------------------------------------------------------------
    u1 = make_opamp("U1")
    u2 = make_opamp("U2")

    vplus_prot += u1[4], u2[4]
    vminus_prot += u1[11], u2[11]

    c5 = make_smd_cap("C5", "100nF 50V")
    c6 = make_smd_cap("C6", "100nF 50V")
    c7 = make_smd_cap("C7", "100nF 50V")
    c8 = make_smd_cap("C8", "100nF 50V")
    vplus_prot & c5 & gnd
    vminus_prot & c6 & gnd
    vplus_prot & c7 & gnd
    vminus_prot & c8 & gnd

    # -----------------------------------------------------------------------
    # Section 4.1: Power Input, Reverse-Polarity Protection & Filtering
    # -----------------------------------------------------------------------
    j4 = Part(
        "Connector_Generic",
        "Conn_02x05_Odd_Even",
        ref="J4",
        value="PWR_2x5",
        footprint="Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical",
        tag="j4",
    )
    _apply_fields(
        j4,
        {
            "LCSC": "C53207560",
            "MPN": "IDC2.54-2*5PZ",
            "Manufacturer": "JXTCONN",
            "JLCPCB_Class": "Manual THT",
            "Side": "B.Cu",
            "Silkscreen": "J4 PWR",
            "Notes": (
                "B.Cu Rear Manual THT; Doepfer A-100 2x5 keyed IDC header "
                "(Pins 1-2=-12V_IN RED, 3-8=GND, 9-10=+12V_IN)"
            ),
        },
    )
    vminus_in += j4[1], j4[2]
    gnd += j4[3], j4[4], j4[5], j4[6], j4[7], j4[8]
    vplus_in += j4[9], j4[10]

    d7 = make_1n5819ws("D7")
    d8 = make_1n5819ws("D8")
    vplus_in += d7["A"]
    vplus_filt_in += d7["K"]
    vminus_in += d8["K"]
    vminus_filt_in += d8["A"]

    r28 = make_resistor("R28", "10R")
    r29 = make_resistor("R29", "10R")
    vplus_filt_in & r28 & vplus_prot
    vminus_filt_in & r29 & vminus_prot

    c3 = make_bulk_cap("C3", "+12V_PROT bulk storage (+ -> +12V_PROT, - -> GND)")
    c4 = make_bulk_cap("C4", "-12V_PROT bulk storage (+ -> GND, - -> -12V_PROT)")
    vplus_prot += c3[1]
    gnd += c3[2]
    gnd += c4[1]
    vminus_prot += c4[2]

    # -----------------------------------------------------------------------
    # Section 4.2: Stage 1 — High-Z Protected AC Input & Gain Stage (U1A)
    # -----------------------------------------------------------------------
    j1 = make_jack("J1", "IN", "TN->GND")
    in_tip += j1["T"]
    gnd += j1["S"], j1["TN"]

    r1 = make_resistor("R1", "10k")
    d9 = make_bat54s("D9")
    c1 = make_film_cap("C1", "AC input coupling ahead of RV1")
    rv1 = make_pot(
        "RV1",
        "A100k",
        "GAIN",
        "RD901F-40-15F-A100K",
        "100k Log pot (GAIN); Pin 1=CCW, Pin 2=Wiper, Pin 3=CW",
    )
    r2 = make_resistor("R2", "4.7k")
    r3 = make_resistor("R3", "1M")
    r4 = make_resistor("R4", "10k")
    r5 = make_resistor("R5", "100k")
    c9 = make_smd_cap("C9", "22pF 50V")

    in_tip & r1 & in_clamp & c1 & in_pot_top
    vminus_prot += d9[1]
    vplus_prot += d9[2]
    in_clamp += d9[3]

    in_pot_top += rv1[3]
    in_pot_bot += rv1[1]
    in_pot_bot & r2 & gnd
    in_wiper += rv1[2], u1[3]
    in_wiper & r3 & gnd

    gnd & r4[2, 1] & in_gain_inv
    in_gain_inv += u1[2]
    in_gain_inv & (r5 | c9) & v_gain
    v_gain += u1[1]

    # -----------------------------------------------------------------------
    # Section 4.3: Stage 2 — Precision 1.00x Full-Wave Rectifier (U1B, U1C)
    # -----------------------------------------------------------------------
    r6 = make_resistor("R6", "10k")
    r7 = make_resistor("R7", "10k")
    r8 = make_resistor("R8", "20k")
    r9 = make_resistor("R9", "10k")
    r10 = make_resistor("R10", "20k")
    d1 = make_1n4148ws("D1")
    d2 = make_1n4148ws("D2")

    gnd += u1[5], u1[10]
    v_gain & r6 & rect_inv
    rect_inv += u1[6]
    rect_op_out += u1[7]

    rect_op_out += d1["A"], d2["K"]
    rect_inv += d1["K"]
    rect_mid += d2["A"]
    rect_inv & r7 & rect_mid

    v_gain & r8 & sum_inv
    rect_mid & r9 & sum_inv
    sum_inv += u1[9]
    sum_inv & r10 & v_rect
    v_rect += u1[8]

    # -----------------------------------------------------------------------
    # Section 4.4: Stage 3 — Active Peak Detector (U2C), C2 Buffer (U2D)
    # -----------------------------------------------------------------------
    d3 = make_1n4148ws("D3")
    d5 = make_1n4148ws("D5")
    r11 = make_resistor("R11", "200k")
    c10 = make_smd_cap("C10", "100pF 50V")
    r12 = make_resistor("R12", "150R")
    rv2 = make_pot(
        "RV2",
        "A50k",
        "ATK",
        "RD901F-40-15F-A50K",
        "50k Log pot (ATK); Pin 1=CCW, Pin 2=Wiper, Pin 3=CW",
    )
    c2 = make_film_cap("C2", "Envelope hold timing cap (ENV_CAP)")
    r13 = make_resistor("R13", "10k")
    rv3 = make_pot(
        "RV3",
        "A1M",
        "REL",
        "RD901F-40-15F-A1M",
        "1M Log pot (Release); Pin 1=CCW, Pin 2=Wiper, Pin 3=CW",
    )
    r14 = make_resistor("R14", "4.7M")

    v_rect += u2[10]
    peak_inv += u2[9]
    peak_op_out += u2[8]

    peak_inv += d5["A"]
    peak_op_out += d5["K"], d3["A"]
    peak_inv & c10 & peak_op_out

    rect_diode_out += d3["K"]
    rect_diode_out & r12 & atk_mid
    atk_mid += rv2[1]
    env_cap += rv2[2], rv2[3]

    env_cap & c2 & gnd
    env_cap & r13 & rel_mid
    rel_mid += rv3[1]
    gnd += rv3[2], rv3[3]
    rel_mid & r14 & gnd

    env_cap += u2[12]
    v_env_buf += u2[13], u2[14]
    v_env_buf & r11 & peak_inv

    # -----------------------------------------------------------------------
    # Section 4.5: Stage 4 — Difference/Offset (U1D), Inv Output (U2A), Jacks
    # -----------------------------------------------------------------------
    r15 = make_resistor("R15", "100k")
    r16 = make_resistor("R16", "100k")
    r17 = make_resistor("R17", "6.8k")
    r18 = make_resistor("R18", "6.8k")
    rv4 = make_pot(
        "RV4",
        "B10k",
        "OFFSET",
        "RD901F-40-15F-B10K",
        "10k Linear pot (OFFSET); Pin 1=CCW (+12V leg), Pin 2=Wiper, Pin 3=CW (-12V leg)",
    )
    r19 = make_resistor("R19", "100k")
    r20 = make_resistor("R20", "100k")
    d10 = make_bat54s("D10")
    r21 = make_resistor("R21", "1k 1W")
    j2 = make_jack("J2", "OUT", "TN=NC")

    v_env_buf & r15 & out_noninv
    out_noninv & r16 & gnd
    out_noninv += u1[12]

    vplus_prot & r17 & off_top
    off_top += rv4[1]
    vminus_prot & r18 & off_bot
    off_bot += rv4[3]
    off_wiper += rv4[2]

    off_wiper & r19 & out_inv_node
    out_inv_node += u1[13]
    out_inv_node & r20 & v_out_buf
    v_out_buf += u1[14]

    vminus_prot += d10[1]
    vplus_prot += d10[2]
    v_out_buf += d10[3]
    v_out_buf & r21 & out_tip
    out_tip += j2["T"]
    gnd += j2["S"]
    j2["TN"] += builtins.NC

    r22 = make_resistor("R22", "10k")
    r23 = make_resistor("R23", "10k")
    d11 = make_bat54s("D11")
    r24 = make_resistor("R24", "1k 1W")
    j3 = make_jack("J3", "INV_OUT", "TN=NC")

    gnd += u2[3]
    v_out_buf & r22 & inv_sum
    inv_sum += u2[2]
    inv_sum & r23 & v_inv_buf
    v_inv_buf += u2[1]

    vminus_prot += d11[1]
    vplus_prot += d11[2]
    v_inv_buf += d11[3]
    v_inv_buf & r24 & inv_out_tip
    inv_out_tip += j3["T"]
    gnd += j3["S"]
    j3["TN"] += builtins.NC

    # -----------------------------------------------------------------------
    # Section 4.6: Stage 5 — Precision Constant-Current LED Driver (U2B)
    # -----------------------------------------------------------------------
    r25 = make_resistor("R25", "10k")
    r26 = make_resistor("R26", "10k")
    r27 = make_resistor("R27", "1k")
    d6 = make_1n4148ws("D6")
    d4 = Part(
        "Device",
        "LED",
        ref="D4",
        value="3mm Green LED",
        footprint="LED_THT:LED_D3.0mm",
        tag="d4",
    )
    _apply_fields(
        d4,
        {
            "LCSC": "C85161",
            "MPN": "204-10SYGD/S530-E3",
            "Manufacturer": "Everlight",
            "JLCPCB_Class": "Manual THT",
            "Side": "F.Cu",
            "Silkscreen": "D4 ENV",
            "Notes": (
                "F.Cu Front-Panel Manual THT; Pin 1 rect = Cathode (K), "
                "Pin 2 round = Anode (A); Alt LCSC: C84774 (Red), C85160 (Yellow)"
            ),
        },
    )

    v_env_buf & r25 & led_ref_in
    led_ref_in & r26 & gnd
    led_ref_in += u2[5]

    v_led_drv += u2[7], d4["A"], d6["K"]
    led_sense += u2[6], d4["K"], d6["A"]
    led_sense & r27 & gnd

    # -----------------------------------------------------------------------
    # Section 5.4: Rear B.Cu Optional Test Points (TP1-TP8, DNP)
    # -----------------------------------------------------------------------
    test_point_map = (
        ("TP1", vplus_prot),
        ("TP2", vminus_prot),
        ("TP3", gnd),
        ("TP4", v_gain),
        ("TP5", v_rect),
        ("TP6", v_env_buf),
        ("TP7", v_out_buf),
        ("TP8", v_inv_buf),
    )
    for tp_ref, tp_net in test_point_map:
        make_test_point(tp_ref, tp_net)

    # -----------------------------------------------------------------------
    # Structural & Electrical ERC Assertions
    # -----------------------------------------------------------------------
    erc_assert(
        "len(builtins.default_circuit.parts) == 68",
        "Expected 68 footprints (60 populated + 8 DNP test points).",
    )
    erc_assert(
        "sum(len(p.pins) for p in builtins.default_circuit.parts) == 170",
        "Expected 170 total component pins.",
    )
    erc_assert(
        "len(vplus_prot) == 11 and len(vminus_prot) == 11",
        "Protected +/-12V rails must have 11 pins each.",
    )
    erc_assert(
        "len(gnd) == 30",
        "GND net must have 30 pins.",
    )
    erc_assert(
        "len(env_cap) == 5",
        "ENV_CAP must stay isolated to RV2.2, RV2.3, C2.1, R13.1, and U2.12.",
    )
    erc_assert(
        "j2['TN'].net == builtins.NC and j3['TN'].net == builtins.NC",
        "Output jack normalling switches (J2.TN, J3.TN) must remain NC.",
    )


# ---------------------------------------------------------------------------
# JLCPCB BOM Exporter
# ---------------------------------------------------------------------------


def _natural_ref_key(ref: str) -> tuple[str, int, str]:
    """Sort component designators naturally (e.g., R1, R4, R13, R22)."""
    match = re.match(r"^([A-Za-z]+)(\d+)$", ref.strip())
    if match:
        return (match.group(1), int(match.group(2)), ref)
    return (ref, 0, ref)


def generate_jlcpcb_bom(
    file_: Path | str = "jlcpcb_bom.csv", include_tht: bool = False
) -> int:
    """
    Export a grouped 4-column JLCPCB PCBA BOM CSV (`Comment,Designator,Footprint,LCSC Part #`).

    Excludes DNP parts, `exclude_from_bom` parts, and manual THT components unless
    `include_tht=True`, matching the 49 B.Cu SMT placements in EnvelopeFollowerBOM.md.
    """
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

    out_path = Path(file_)
    total_qty = 0
    with out_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, lineterminator="\n")
        writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (comment, footprint, lcsc), refs in groups.items():
            sorted_refs = sorted(refs, key=_natural_ref_key)
            total_qty += len(sorted_refs)
            writer.writerow([comment, ", ".join(sorted_refs), footprint, lcsc])

    return total_qty


def main() -> None:
    """Build circuit, run ERC, and export KiCad netlist, XML BOM, and JLCPCB CSV."""
    build_envelope_follower()
    ERC()
    generate_netlist(file_=str(STAGE_DIR / "envelope_follower.net"))
    generate_xml(file_=str(STAGE_DIR / "envelope_follower_bom.xml"))
    smt_count = generate_jlcpcb_bom(file_=STAGE_DIR / "jlcpcb_bom.csv")
    print(f"Exported JLCPCB SMT BOM with {smt_count} placements.")


if __name__ == "__main__":
    main()
