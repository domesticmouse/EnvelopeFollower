#!/usr/bin/env python3
"""SKiDL circuit definition for the Improved 6 HP Eurorack Envelope Follower."""

from __future__ import annotations

import builtins
import csv
import os
import re
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)
os.environ.setdefault("XDG_DATA_HOME", "/tmp/xdg_data")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_config")
if os.path.isdir("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"):
    _SYM_DIR = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
    os.environ.setdefault("KICAD_SYMBOL_DIR", _SYM_DIR)
    for _ver in (6, 7, 8, 9, 10):
        os.environ.setdefault(f"KICAD{_ver}_SYMBOL_DIR", _SYM_DIR)
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
)

# Resistor catalog specs: (value, footprint, lcsc, mpn, jlc_class, silkscreen, notes)
_RESISTOR_SPECS: dict[str, tuple[str, str, str, str, str, str, str]] = {
    "10k": (
        "10k",
        "Resistor_SMD:R_0603_1608Metric",
        "C25804",
        "0603WAF1002T5E",
        "Basic",
        "10k",
        "0603 1% 100mW thick film",
    ),
    "1k": (
        "1k",
        "Resistor_SMD:R_0603_1608Metric",
        "C21190",
        "0603WAF1001T5E",
        "Basic",
        "1k",
        "0603 1% 100mW thick film",
    ),
    "1k_1W": (
        "1k 1W",
        "Resistor_SMD:R_2512_6332Metric",
        "C54315",
        "25121WF1001T4E",
        "Extended",
        "1k_1W",
        "2512 1W 1% fault/surge limiter; Alt: 1210 0.5W C52444",
    ),
    "100k": (
        "100k",
        "Resistor_SMD:R_0603_1608Metric",
        "C25803",
        "0603WAF1003T5E",
        "Basic",
        "100k",
        "0603 1% 100mW thick film",
    ),
    "20k": (
        "20k",
        "Resistor_SMD:R_0603_1608Metric",
        "C4184",
        "0603WAF2002T5E",
        "Basic",
        "20k",
        "0603 1% 100mW thick film",
    ),
    "22k": (
        "22k",
        "Resistor_SMD:R_0603_1608Metric",
        "C31850",
        "0603WAF2202T5E",
        "Basic",
        "22k",
        "0603 1% 100mW thick film",
    ),
    "4.7k": (
        "4.7k",
        "Resistor_SMD:R_0603_1608Metric",
        "C23162",
        "0603WAF4701T5E",
        "Basic",
        "4.7k",
        "0603 1% 100mW thick film",
    ),
    "3.3k": (
        "3.3k",
        "Resistor_SMD:R_0603_1608Metric",
        "C22978",
        "0603WAF3301T5E",
        "Basic",
        "3.3k",
        "0603 1% 100mW thick film",
    ),
    "330R": (
        "330R",
        "Resistor_SMD:R_0603_1608Metric",
        "C23138",
        "0603WAF3300T5E",
        "Basic",
        "330R",
        "0603 1% 100mW thick film",
    ),
}

# Capacitor catalog specs: (symbol, value, footprint, lcsc, mpn, mfg, jlc_class, side, silkscreen, notes)
_CAPACITOR_SPECS: dict[str, tuple[str, str, str, str, str, str, str, str, str, str]] = {
    "1uF_film": (
        "C",
        "1uF 63V",
        "Capacitor_THT:C_Rect_L7.2mm_W6.0mm_P5.00mm",
        "C328852",
        "C241J105J2SA201",
        "XIAMEN FARATRONIC",
        "Manual THT",
        "B.Cu",
        "1uF",
        "Rear B.Cu THT film box cap P=5.0mm; Alt: C3975271 or C92673",
    ),
    "22uF_elec": (
        "C_Polarized",
        "22uF 50V",
        "Capacitor_SMD:CP_Elec_6.3x5.4",
        "C2836438",
        "RVT22UF50V67RV0028",
        "KNSCHA",
        "Extended",
        "B.Cu",
        "22uF",
        "50V SMD electrolytic D6.3xL5.4mm; Alt: 47uF 35V C970678",
    ),
    "100nF": (
        "C",
        "100nF",
        "Capacitor_SMD:C_0603_1608Metric",
        "C14663",
        "CC0603KRX7R9BB104",
        "YAGEO",
        "Basic",
        "B.Cu",
        "100nF",
        "0603 50V X7R 10% local op-amp bypass",
    ),
    "22pF": (
        "C",
        "22pF",
        "Capacitor_SMD:C_0603_1608Metric",
        "C1653",
        "CL10C220JB8NNNC",
        "Samsung Electro-Mechanics",
        "Basic",
        "B.Cu",
        "22pF",
        "0603 50V C0G 5% ultrasonic compensation",
    ),
    "47pF": (
        "C",
        "47pF",
        "Capacitor_SMD:C_0603_1608Metric",
        "C1671",
        "CL10C470JB8NNNC",
        "Samsung Electro-Mechanics",
        "Basic",
        "B.Cu",
        "47pF",
        "0603 50V C0G 5% op-amp stabilization",
    ),
}


def _apply_fields(part: Part, fields: dict[str, str]) -> None:
    """Assign custom catalog and layout metadata into `part.fields`."""
    for key, val in fields.items():
        if val:
            part.fields[key] = val


def _make_resistor(ref: str, spec_key: str) -> Part:
    """Instantiate a populated B.Cu SMT resistor with catalog and silkscreen metadata."""
    value, footprint, lcsc, mpn, jlc_class, silk, notes = _RESISTOR_SPECS[spec_key]
    part = Part(
        "Device",
        "R",
        ref=ref,
        value=value,
        footprint=footprint,
        tag=f"res_{ref.lower()}",
    )
    _apply_fields(
        part,
        {
            "LCSC": lcsc,
            "MPN": mpn,
            "Manufacturer": "UNI-ROYAL",
            "JLCPCB_Class": jlc_class,
            "Side": "B.Cu",
            "Silkscreen": silk,
            "Notes": notes,
        },
    )
    return part


def _make_capacitor(ref: str, spec_key: str, *, extra_notes: str = "") -> Part:
    """Instantiate a fixed capacitor with catalog and silkscreen metadata."""
    sym, value, footprint, lcsc, mpn, mfg, jlc_class, side, silk, notes = (
        _CAPACITOR_SPECS[spec_key]
    )
    part = Part(
        "Device",
        sym,
        ref=ref,
        value=value,
        footprint=footprint,
        tag=f"cap_{ref.lower()}",
    )
    full_notes = f"{notes}; {extra_notes}" if extra_notes else notes
    _apply_fields(
        part,
        {
            "LCSC": lcsc,
            "MPN": mpn,
            "Manufacturer": mfg,
            "JLCPCB_Class": jlc_class,
            "Side": side,
            "Silkscreen": silk,
            "Notes": full_notes,
        },
    )
    return part


def _make_pot(ref: str, value: str, label: str, notes: str) -> Part:
    """Instantiate a front-panel 9 mm vertical potentiometer (consigned THT)."""
    part = Part(
        "Device",
        "R_Potentiometer",
        ref=ref,
        value=value,
        footprint="Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical",
        tag=f"pot_{ref.lower()}",
    )
    _apply_fields(
        part,
        {
            "MPN": "RD901F-40-00D",
            "Manufacturer": "Alpha",
            "JLCPCB_Class": "Manual THT",
            "Side": "F.Cu",
            "Silkscreen": label,
            "Notes": f"{notes}; Alt: Alps RK09K (Consigned THT)",
        },
    )
    return part


def _make_jack(ref: str, label: str, notes: str) -> Part:
    """Instantiate a front-panel 3.5 mm mono switched jack (consigned THT)."""
    part = Part(
        "Connector_Audio",
        "AudioJack2_SwitchT",
        ref=ref,
        value=label,
        footprint="Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles",
        tag=f"jack_{ref.lower()}",
    )
    _apply_fields(
        part,
        {
            "MPN": "WQP-PJ398SM",
            "Manufacturer": "QingPu",
            "JLCPCB_Class": "Manual THT",
            "Side": "F.Cu",
            "Silkscreen": label,
            "Notes": f"{notes} (Consigned THT)",
        },
    )
    return part


def _natural_ref_key(ref: str) -> tuple[tuple[int, int | str], ...]:
    """Sort designators naturally (e.g., R1, R2, R10 instead of R1, R10, R2)."""
    return tuple(
        (0, int(tok)) if tok.isdigit() else (1, tok)
        for tok in re.split(r"(\d+)", ref.strip())
        if tok
    )


def generate_jlcpcb_bom(
    file_: str = "jlcpcb_bom.csv", *, include_tht: bool = False
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
        writer = csv.writer(csvfile, lineterminator="\n")
        writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (comment, footprint, lcsc), refs in groups.items():
            sorted_refs = sorted(refs, key=_natural_ref_key)
            writer.writerow([comment, ", ".join(sorted_refs), footprint, lcsc])


def build_envelope_follower() -> dict[str, Net]:
    """Build the complete Improved Envelope Follower circuit and return key nets."""
    # Power NetClass for Eurorack ±12V rails and ground
    pwr_class = NetClass("Power", priority=1, trace_width=0.50, clearance=0.25)

    # Power & reference nets
    v_plus_in = Net("+12V_IN")
    v_minus_in = Net("-12V_IN")
    v_plus = Net("+12V")
    v_minus = Net("-12V")
    gnd = Net("GND")
    for pnet in (v_plus_in, v_minus_in, v_plus, v_minus, gnd):
        pnet.drive = POWER
        pnet.netclasses = pwr_class

    # Signal nets matching EnvelopeFollowerImproved.md Section 5
    in_tip = Net("IN_TIP")
    in_surge = Net("IN_SURGE")
    ac_in = Net("AC_IN")
    u2c_in_p = Net("U2C_IN_P")
    in_buf = Net("IN_BUF")
    u1a_in_m = Net("U1A_IN_M")
    gain_mid = Net("GAIN_MID")
    v_amp = Net("V_AMP")
    u1b_in_m = Net("U1B_IN_M")
    u1b_out = Net("U1B_OUT")
    v_rect = Net("V_RECT")
    ff_mid = Net("FF_MID")
    u1c_in_m = Net("U1C_IN_M")
    v_fwr = Net("V_FWR")
    u2d_out = Net("U2D_OUT")
    atk_in = Net("ATK_IN")
    atk_pot_in = Net("ATK_POT_IN")
    env_cap = Net("ENV_CAP")
    rel_mid = Net("REL_MID")
    u1d_in_p = Net("U1D_IN_P")
    offset_top = Net("OFFSET_TOP")
    offset_bot = Net("OFFSET_BOT")
    offset_wiper = Net("OFFSET_WIPER")
    u1d_in_m = Net("U1D_IN_M")
    v_out_pre = Net("V_OUT_PRE")
    out_tip = Net("OUT_TIP")
    u2a_in_m = Net("U2A_IN_M")
    v_inv_pre = Net("V_INV_PRE")
    inv_out_tip = Net("INV_OUT_TIP")
    u2b_in_p = Net("U2B_IN_P")
    led_a = Net("LED_A")
    led_k = Net("LED_K")

    # Reusable templates for multi-instance ICs and SMT diodes
    opamp_t = Part(
        "Amplifier_Operational",
        "TL074",
        dest=TEMPLATE,
        value="TL074HIDR",
        footprint="Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
    )
    opamp_t.datasheet = (
        "https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/"
        "2302282300_Texas-Instruments-TL074HIDR_C2878713.pdf"
    )
    _apply_fields(
        opamp_t,
        {
            "LCSC": "C2878713",
            "MPN": "TL074HIDR",
            "Manufacturer": "Texas Instruments",
            "JLCPCB_Class": "Extended",
            "Side": "B.Cu",
            "Silkscreen": "TL074H",
            "Notes": "TI CMOS/FET-input quad op-amp, zero phase reversal; Alt: TL074CDR C12594",
        },
    )

    d1n4148_t = Part(
        "Diode",
        "1N4148W",
        dest=TEMPLATE,
        value="1N4148W",
        footprint="Diode_SMD:D_SOD-123",
    )
    _apply_fields(
        d1n4148_t,
        {
            "LCSC": "C81598",
            "MPN": "1N4148W",
            "Manufacturer": "ST (Semtech)",
            "JLCPCB_Class": "Basic",
            "Side": "B.Cu",
            "Silkscreen": "1N4148W",
            "Notes": "SOD-123 fast diode (1=K, 2=A); Alt: SOD-323 1N4148WS C2128",
        },
    )

    bav99_t = Part(
        "Diode",
        "BAV99",
        dest=TEMPLATE,
        value="BAV99",
        footprint="Package_TO_SOT_SMD:SOT-23",
    )
    _apply_fields(
        bav99_t,
        {
            "LCSC": "C2500",
            "MPN": "BAV99,215",
            "Manufacturer": "Nexperia",
            "JLCPCB_Class": "Basic",
            "Side": "B.Cu",
            "Silkscreen": "BAV99",
            "Notes": "Physical SOT-23 pinout: 1=A1(-12V), 2=K2(+12V), 3=COM(signal); KiCad symbol names 1/3 inverted",
        },
    )

    schottky_t = Part(
        "Device",
        "D_Schottky",
        dest=TEMPLATE,
        value="B5819W",
        footprint="Diode_SMD:D_SOD-123",
    )
    _apply_fields(
        schottky_t,
        {
            "LCSC": "C8598",
            "MPN": "B5819W SL",
            "Manufacturer": "Jiangsu Changjing",
            "JLCPCB_Class": "Basic",
            "Side": "B.Cu",
            "Silkscreen": "B5819W",
            "Notes": "40V 1A Schottky (1=K, 2=A); Alt: SOD-323 1N5819WS C191023",
        },
    )

    u1 = opamp_t(ref="U1", tag="ic_u1")
    u2 = opamp_t(ref="U2", tag="ic_u2")

    # -------------------------------------------------------------------------
    # Stage 3.1: Power Supply, Reverse-Polarity Protection & Decoupling
    # -------------------------------------------------------------------------
    j4 = Part(
        "Connector_Generic",
        "Conn_02x05_Odd_Even",
        ref="J4",
        value="Eurorack_Power_2x5",
        footprint="Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical",
        tag="conn_j4_pwr",
    )
    _apply_fields(
        j4,
        {
            "LCSC": "C53207560",
            "MPN": "IDC2.54-2*5PZ",
            "Manufacturer": "JXTCONN",
            "JLCPCB_Class": "Manual THT",
            "Side": "B.Cu",
            "Silkscreen": "PWR",
            "Notes": "Rear B.Cu shrouded 2x5 IDC header; 1-2=-12V_IN (RED), 3-8=GND, 9-10=+12V_IN",
        },
    )
    v_minus_in += j4[1, 2]
    gnd += j4[3, 4, 5, 6, 7, 8]
    v_plus_in += j4[9, 10]

    d5 = schottky_t(ref="D5", tag="diode_d5_vp")
    d6 = schottky_t(ref="D6", tag="diode_d6_vm")
    # D5: Pin 2 (A) -> +12V_IN, Pin 1 (K) -> +12V
    v_plus_in += d5.p[2]
    v_plus += d5.p[1]
    # D6: Pin 2 (A) -> -12V, Pin 1 (K) -> -12V_IN
    v_minus += d6.p[2]
    v_minus_in += d6.p[1]

    c3 = _make_capacitor("C3", "22uF_elec", extra_notes="Pin 1(+)=+12V, Pin 2(-)=GND")
    c4 = _make_capacitor(
        "C4",
        "22uF_elec",
        extra_notes="CRITICAL -12V polarity: Pin 1(+)=GND, Pin 2(-)=-12V",
    )
    v_plus += c3[1]
    gnd += c3[2]
    gnd += c4[1]
    v_minus += c4[2]

    c5 = _make_capacitor("C5", "100nF", extra_notes="U1.4 +12V bypass")
    c6 = _make_capacitor("C6", "100nF", extra_notes="U1.11 -12V bypass")
    c7 = _make_capacitor("C7", "100nF", extra_notes="U2.4 +12V bypass")
    c8 = _make_capacitor("C8", "100nF", extra_notes="U2.11 -12V bypass")

    v_plus += u1[4], u2[4], c5[1], c7[1]
    v_minus += u1[11], u2[11], c6[1], c8[1]
    gnd += c5[2], c6[2], c7[2], c8[2]

    # -------------------------------------------------------------------------
    # Stage 3.2: 100k Input Buffer & ESD/Surge Protection (J1, R26, C1, R1, R27, D9, U2C)
    # -------------------------------------------------------------------------
    j1 = _make_jack("J1", "IN", "IN jack; T=IN_TIP, TN=GND, S=GND")
    r26 = _make_resistor("R26", "1k_1W")
    c1 = _make_capacitor(
        "C1", "1uF_film", extra_notes="Input AC coupling (1.58 Hz HPF)"
    )
    r1 = _make_resistor("R1", "100k")
    r27 = _make_resistor("R27", "10k")
    d9 = bav99_t(ref="D9", tag="clamp_d9_in")

    in_tip += j1["T"], r26[1]
    gnd += j1["S"], j1["TN"]
    in_surge += r26[2], c1[1]
    ac_in += c1[2], r1[1], r27[1]
    gnd += r1[2]
    # BAV99 physical SOT-23 pins must be indexed by number (.p[1]=A1, .p[2]=K2, .p[3]=COM)
    u2c_in_p += r27[2], d9.p[3], u2[10]
    v_minus += d9.p[1]
    v_plus += d9.p[2]
    in_buf += u2[8], u2[9]

    # -------------------------------------------------------------------------
    # Stage 3.3: Variable Input Gain Stage (U1A, R2, R24, RV1, C9)
    # -------------------------------------------------------------------------
    r2 = _make_resistor("R2", "10k")
    r24 = _make_resistor("R24", "4.7k")
    rv1 = _make_pot("RV1", "A100k", "GAIN", "1=GAIN_MID, 2+3=V_AMP; CW=higher gain")
    c9 = _make_capacitor("C9", "22pF", extra_notes="U1A ultrasonic compensation")

    in_buf += r2[1]
    u1a_in_m += r2[2], r24[1], c9[1], u1[2]
    gnd += u1[3]
    gain_mid += r24[2], rv1[1]
    v_amp += u1[1], rv1[2], rv1[3], c9[2]

    # -------------------------------------------------------------------------
    # Stage 3.4: Unity-Gain Precision Full-Wave Rectifier (U1B, U1C, R3-R8, D1, D2)
    # -------------------------------------------------------------------------
    r3 = _make_resistor("R3", "10k")
    r4 = _make_resistor("R4", "10k")
    r5 = _make_resistor("R5", "10k")
    r6 = _make_resistor("R6", "10k")
    r7 = _make_resistor("R7", "10k")
    r8 = _make_resistor("R8", "20k")
    d1 = d1n4148_t(ref="D1", tag="diode_d1_hwr")
    d2 = d1n4148_t(ref="D2", tag="diode_d2_hwr")

    v_amp += r3[1], r6[1]
    u1b_in_m += r3[2], r4[1], d1.p[1], u1[6]
    gnd += u1[5], u1[10]
    u1b_out += u1[7], d1.p[2], d2.p[1]
    v_rect += d2.p[2], r4[2], r5[1]
    ff_mid += r6[2], r7[1]
    u1c_in_m += r5[2], r7[2], r8[1], u1[9]
    v_fwr += u1[8], r8[2]

    # -------------------------------------------------------------------------
    # Stage 3.5: Active Zero-Deadzone Peak Detector & Attack/Release
    # -------------------------------------------------------------------------
    d3 = d1n4148_t(ref="D3", tag="diode_d3_peak")
    r25 = _make_resistor("R25", "330R")
    rv2 = _make_pot("RV2", "A50k", "ATK", "1=ATK_POT_IN, 2+3=ENV_CAP; CW=slower attack")
    c2 = _make_capacitor("C2", "1uF_film", extra_notes="Envelope storage timing cap")
    r10 = _make_resistor("R10", "10k")
    rv3 = _make_pot("RV3", "A1M", "REL", "1=REL_MID, 2+3=GND; CW=longer release")
    r9 = _make_resistor("R9", "10k")
    r20 = _make_resistor("R20", "10k")

    v_fwr += u2[12]
    u2d_out += u2[14], d3.p[2]
    atk_in += d3.p[1], u2[13], r25[1]
    atk_pot_in += r25[2], rv2[1]
    env_cap += rv2[2], rv2[3], c2[1], r10[1], r9[1], r20[1]
    gnd += c2[2], rv3[2], rv3[3]
    rel_mid += r10[2], rv3[1]
    u1d_in_p += r9[2], u1[12]
    u2b_in_p += r20[2], u2[5]

    # -------------------------------------------------------------------------
    # Stage 3.6: Output Gain, Linearized B10k Offset & Protected Outputs
    # -------------------------------------------------------------------------
    r11 = _make_resistor("R11", "1k")
    r12 = _make_resistor("R12", "1k")
    rv4 = _make_pot(
        "RV4", "B10k", "OFFSET", "1=OFFSET_TOP(+12V), 2=WIPER, 3=OFFSET_BOT(-12V)"
    )
    r13 = _make_resistor("R13", "22k")
    r15 = _make_resistor("R15", "10k")
    c10 = _make_capacitor("C10", "47pF", extra_notes="U1D output stage stabilization")
    r16 = _make_resistor("R16", "1k_1W")
    d7 = bav99_t(ref="D7", tag="clamp_d7_out")
    j2 = _make_jack("J2", "OUT", "OUT jack; T=OUT_TIP, TN=NC (isolated!), S=GND")

    r17 = _make_resistor("R17", "10k")
    r18 = _make_resistor("R18", "10k")
    c11 = _make_capacitor("C11", "47pF", extra_notes="U2A inverter stabilization")
    r19 = _make_resistor("R19", "1k_1W")
    d8 = bav99_t(ref="D8", tag="clamp_d8_inv")
    j3 = _make_jack("J3", "INV_OUT", "INV_OUT jack; T=INV_OUT_TIP, TN=NC, S=GND")

    v_plus += r11[1]
    offset_top += r11[2], rv4[1]
    v_minus += r12[2]
    offset_bot += r12[1], rv4[3]
    offset_wiper += rv4[2], r13[1]
    u1d_in_m += r13[2], r15[1], c10[1], u1[13]
    v_out_pre += u1[14], r15[2], c10[2], d7.p[3], r16[1], r17[1]
    v_minus += d7.p[1]
    v_plus += d7.p[2]
    out_tip += r16[2], j2["T"]
    gnd += j2["S"]
    j2["TN"] += builtins.NC

    u2a_in_m += r17[2], r18[1], c11[1], u2[2]
    gnd += u2[3]
    v_inv_pre += u2[1], r18[2], c11[2], d8.p[3], r19[1]
    v_minus += d8.p[1]
    v_plus += d8.p[2]
    inv_out_tip += r19[2], j3["T"]
    gnd += j3["S"]
    j3["TN"] += builtins.NC

    # -------------------------------------------------------------------------
    # Stage 3.7: Active Linear Feedback LED Current Driver
    # -------------------------------------------------------------------------
    d4 = Part(
        "Device",
        "LED",
        ref="D4",
        value="LED_3mm_YG",
        footprint="LED_THT:LED_D3.0mm",
        tag="led_d4_env",
    )
    d4.datasheet = (
        "https://www.lcsc.com/datasheet/lcsc_datasheet_1811141531_"
        "Everlight-Elec-204-10SYGD-S530-E3_C85161.pdf"
    )
    _apply_fields(
        d4,
        {
            "LCSC": "C85161",
            "MPN": "204-10SYGD/S530-E3",
            "Manufacturer": "Everlight Elec",
            "JLCPCB_Class": "Manual THT",
            "Side": "F.Cu",
            "Silkscreen": "ENV",
            "Notes": "3mm Yellow-Green diffused LED (1=K, 2=A); F.Cu panel-aligned",
        },
    )
    d10 = d1n4148_t(ref="D10", tag="diode_d10_led_clamp")
    r21 = _make_resistor("R21", "3.3k")

    led_a += u2[7], d4.p[2], d10.p[1]
    led_k += d4.p[1], d10.p[2], u2[6], r21[1]
    gnd += r21[2]

    # -------------------------------------------------------------------------
    # Stage 4: Optional Rear DNP Test Points (TP1-TP8, B.Cu, 1.0 mm drill)
    # -------------------------------------------------------------------------
    tp_specs: list[tuple[str, Net, str]] = [
        ("TP1", gnd, "GND"),
        ("TP2", v_plus, "+12V"),
        ("TP3", v_minus, "-12V"),
        ("TP4", in_buf, "IN_BUF"),
        ("TP5", v_amp, "V_AMP"),
        ("TP6", v_fwr, "V_FWR"),
        ("TP7", env_cap, "ENV_CAP"),
        ("TP8", v_out_pre, "V_OUT_PRE"),
    ]
    tp_t = Part(
        "Connector",
        "TestPoint",
        dest=TEMPLATE,
        footprint="TestPoint:TestPoint_Keystone_5000-5004_Miniature",
    )
    _apply_fields(
        tp_t,
        {
            "LCSC": "C5199801",
            "MPN": "RH-5001",
            "Manufacturer": "ronghe",
            "JLCPCB_Class": "DNP THT",
            "Side": "B.Cu",
            "Notes": "DNP optional rear test point (1.0mm drill / 2.0mm pad, RH-5001)",
        },
    )
    for ref, net_obj, silk_lbl in tp_specs:
        tp = tp_t(ref=ref, value=silk_lbl, tag=f"tp_{ref.lower()}")
        tp.fields["Silkscreen"] = silk_lbl
        tp.dnp = True
        tp.exclude_from_bom = True
        tp.exclude_from_pos_files = True
        net_obj += tp[1]

    # Electrical & structural ERC assertions
    erc_assert("len(v_plus_in) == 3", "Expected 3 pins on +12V_IN")
    erc_assert("len(v_minus_in) == 3", "Expected 3 pins on -12V_IN")
    erc_assert("len(v_plus) == 11", "Expected 11 pins on +12V")
    erc_assert("len(v_minus) == 11", "Expected 11 pins on -12V")
    erc_assert("len(gnd) == 26", "Expected 26 pins on GND")
    erc_assert("len(env_cap) == 7", "Expected 7 pins on ENV_CAP")
    erc_assert("len(v_out_pre) == 7", "Expected 7 pins on V_OUT_PRE")
    erc_assert("j2['TN'].net is builtins.NC", "OUT jack TN pin must be explicitly NC")
    erc_assert(
        "j3['TN'].net is builtins.NC", "INV_OUT jack TN pin must be explicitly NC"
    )

    return {
        "+12V_IN": v_plus_in,
        "-12V_IN": v_minus_in,
        "+12V": v_plus,
        "-12V": v_minus,
        "GND": gnd,
        "IN_BUF": in_buf,
        "V_AMP": v_amp,
        "V_FWR": v_fwr,
        "ENV_CAP": env_cap,
        "V_OUT_PRE": v_out_pre,
    }


def main() -> None:
    """Build circuit, run ERC, and export netlist, XML BOM, and JLCPCB BOM CSV."""
    nets = build_envelope_follower()
    # Keep references accessible in globals if needed by erc_assert expressions
    _ = nets

    ERC()
    generate_netlist(file_="envelope_follower.net")
    generate_xml(file_="envelope_follower_bom.xml")
    generate_jlcpcb_bom(file_="jlcpcb_bom.csv", include_tht=False)


if __name__ == "__main__":
    main()
