#!/usr/bin/env python3
"""Eurorack Analog Envelope Follower circuit defined in SKiDL.

Implements the upgraded Hagiwo Envelope Follower specification from
ENVELOPE_FOLLOWER_NETLIST_AND_TODO.md using dual Texas Instruments TL074H
quad op-amps (U1, U2), Schottky reverse-polarity protection, local IC
decoupling, minimum gain series resistance, output short-circuit protection,
and unity-gain termination for unused op-amp channels (U2C, U2D).
"""

import builtins
import csv
import os

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
    Interface,
    Net,
    NetClass,
    Part,
    erc_assert,
    generate_netlist,
    generate_schematic,
    generate_xml,
    subcircuit,
)

# Verified JLCPCB SMT catalog entries for 0603 1% thick-film resistors.
JLCPCB_RESISTORS_0603 = {
    "1k": ("C21190", "0603WAF1001T5E", "Basic"),
    "10k": ("C25804", "0603WAF1002T5E", "Basic"),
    "22k": ("C31850", "0603WAF2202T5E", "Basic"),
    "33k": ("C4216", "0603WAF3302T5E", "Basic"),
    "1M": ("C22935", "0603WAF1004T5E", "Basic"),
}

FOOTPRINTS = {
    "opamp": "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
    "r_0603": "Resistor_SMD:R_0603_1608Metric",
    "c_0603": "Capacitor_SMD:C_0603_1608Metric",
    "c_0805": "Capacitor_SMD:C_0805_2012Metric",
    "c_elec": "Capacitor_SMD:CP_Elec_4x5.4",
    "d_sod123": "Diode_SMD:D_SOD-123",
    "pot": "Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical",
    "jack": "Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles",
    "led": "LED_THT:LED_D3.0mm",
    "pwr_hdr": "Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical",
}


def make_templates():
    """Create reusable SKiDL Part templates with KiCad footprints and BOM fields."""
    r_t = Part("Device", "R", dest=TEMPLATE, footprint=FOOTPRINTS["r_0603"])
    c_0603_t = Part("Device", "C", dest=TEMPLATE, footprint=FOOTPRINTS["c_0603"])
    pot_t = Part(
        "Device", "R_Potentiometer", dest=TEMPLATE, footprint=FOOTPRINTS["pot"]
    )
    pot_t.fields["JLCPCB_Class"] = "Manual THT"

    d_sig_t = Part(
        "Device",
        "D",
        dest=TEMPLATE,
        value="1N4148W",
        footprint=FOOTPRINTS["d_sod123"],
    )
    d_sig_t.fields["LCSC"] = "C81598"
    d_sig_t.fields["MPN"] = "1N4148W"
    d_sig_t.fields["JLCPCB_Class"] = "Basic"

    d_sch_t = Part(
        "Device",
        "D_Schottky",
        dest=TEMPLATE,
        value="B5819W",
        footprint=FOOTPRINTS["d_sod123"],
    )
    d_sch_t.fields["LCSC"] = "C8598"
    d_sch_t.fields["MPN"] = "B5819W SL"
    d_sch_t.fields["JLCPCB_Class"] = "Basic"
    d_sch_t.fields["Notes"] = "Schottky reverse polarity protection (1N5817/1N5819 SMD)"

    jack_t = Part(
        "Connector_Audio",
        "AudioJack2_SwitchT",
        dest=TEMPLATE,
        value="3.5mm_Jack",
        footprint=FOOTPRINTS["jack"],
    )
    jack_t.fields["JLCPCB_Class"] = "Manual THT"

    return {
        "r": r_t,
        "c_0603": c_0603_t,
        "pot": pot_t,
        "d_sig": d_sig_t,
        "d_sch": d_sch_t,
        "jack": jack_t,
    }


def make_resistor(r_template, ref, value, notes=""):
    """Instantiate a 0603 resistor with verified LCSC/MPN metadata."""
    lcsc, mpn, jlc_class = JLCPCB_RESISTORS_0603[value]
    part = r_template(ref=ref, value=value, tag=ref.lower())
    part.fields["LCSC"] = lcsc
    part.fields["MPN"] = mpn
    part.fields["JLCPCB_Class"] = jlc_class
    if notes:
        part.fields["Notes"] = notes
    return part


def make_tl074h(ref, notes=""):
    """Instantiate a TI TL074H quad op-amp in SOIC-14."""
    part = Part(
        "Amplifier_Operational",
        "TL074",
        ref=ref,
        value="TL074H",
        footprint=FOOTPRINTS["opamp"],
        tag=ref.lower(),
    )
    part.fields["LCSC"] = "C2878713"
    part.fields["MPN"] = "TL074HIDR"
    part.fields["JLCPCB_Class"] = "Extended"
    if notes:
        part.fields["Notes"] = notes
    return part


@subcircuit
def power_and_protection(tpl, u1, u2, pwr):
    """Block 1: Eurorack 10-pin power header, Schottky protection, bulk & bypass caps."""
    j_pwr = Part(
        "Connector_Generic",
        "Conn_02x05_Odd_Even",
        ref="J_PWR",
        value="Eurorack_10Pin",
        footprint=FOOTPRINTS["pwr_hdr"],
        tag="j_pwr",
    )
    j_pwr.fields["LCSC"] = "C53207560"
    j_pwr.fields["MPN"] = "IDC2.54-2*5PZ"
    j_pwr.fields["JLCPCB_Class"] = "Manual THT"

    pwr.neg_raw += j_pwr[1, 2]
    pwr.gnd += j_pwr[3, 4, 5, 6, 7, 8]
    pwr.pos_raw += j_pwr[9, 10]

    d4 = tpl["d_sch"](ref="D4", tag="d4")
    d5 = tpl["d_sch"](ref="D5", tag="d5")
    pwr.pos_raw & d4["A", "K"] & pwr.pos
    pwr.neg & d5["A", "K"] & pwr.neg_raw

    c3 = Part(
        "Device",
        "C_Polarized",
        ref="C3",
        value="4.7uF",
        footprint=FOOTPRINTS["c_elec"],
        tag="c3",
    )
    c4 = Part(
        "Device",
        "C_Polarized",
        ref="C4",
        value="4.7uF",
        footprint=FOOTPRINTS["c_elec"],
        tag="c4",
    )
    for cap in (c3, c4):
        cap.fields["LCSC"] = "C5246584"
        cap.fields["MPN"] = "VT4.7UF50V167RV0133"
        cap.fields["JLCPCB_Class"] = "Extended"
        cap.fields["Notes"] = "Bulk power rail electrolytic decoupling (50V)"

    pwr.pos += c3[1]
    pwr.gnd += c3[2]
    pwr.gnd += c4[1]
    pwr.neg += c4[2]

    # Local 100 nF ceramic decoupling directly across each TL074H supply rail.
    for ref, rail in (
        ("C5", pwr.pos),
        ("C6", pwr.neg),
        ("C7", pwr.pos),
        ("C8", pwr.neg),
    ):
        cap = tpl["c_0603"](ref=ref, value="100nF", tag=ref.lower())
        cap.fields["LCSC"] = "C14663"
        cap.fields["MPN"] = "CC0603KRX7R9BB104"
        cap.fields["JLCPCB_Class"] = "Basic"
        rail & cap & pwr.gnd

    pwr.pos += u1[4], u2[4]
    pwr.neg += u1[11], u2[11]


@subcircuit
def input_gain_stage(tpl, u1, gnd):
    """Block 2: AC-coupled audio/CV input and variable inverting gain stage (U1A)."""
    signal_in = Net("SIGNAL_IN")
    ac_in = Net("AC_IN")
    gain_fb_in = Net("GAIN_FB_IN")
    gain_fb_mid = Net("GAIN_FB_MID")
    out_gain = Net("OUT_GAIN")

    j_in = tpl["jack"](ref="J_IN", tag="j_in")
    signal_in += j_in["T"]
    gnd += j_in["S"]
    j_in["TN"] += builtins.NC

    c1 = Part(
        "Device",
        "C",
        ref="C1",
        value="4.7uF",
        footprint=FOOTPRINTS["c_0805"],
        tag="c1",
    )
    c1.fields["LCSC"] = "C354262"
    c1.fields["MPN"] = "CC0805KKX7R8BB475"
    c1.fields["JLCPCB_Class"] = "Extended"
    c1.fields["Notes"] = "Non-polarized MLCC (25V X7R) for bipolar AC input coupling"

    r1 = make_resistor(tpl["r"], "R1", "1M", "Input pulldown")
    r2 = make_resistor(tpl["r"], "R2", "10k", "Gain stage inverting input resistor")
    r_gain_min = make_resistor(
        tpl["r"],
        "R_GAIN_MIN",
        "1k",
        "Minimum closed-loop feedback resistance limiter",
    )

    rv_gain = tpl["pot"](ref="RV_GAIN", value="100k", tag="rv_gain")

    signal_in & c1 & ac_in
    ac_in & r1 & gnd
    ac_in & r2 & gain_fb_in

    gain_fb_in += u1[2], rv_gain[1]
    gnd += u1[3]
    gain_fb_mid += rv_gain[2, 3]
    gain_fb_mid & r_gain_min & out_gain
    out_gain += u1[1]

    return out_gain


@subcircuit
def precision_rectifier_stage(tpl, u1, out_gain, gnd):
    """Block 3: Full-wave precision rectifier (U1B half-wave + U1C summer)."""
    half_wave_in = Net("HALF_WAVE_IN")
    half_wave_op_out = Net("HALF_WAVE_OP_OUT")
    half_wave_node = Net("HALF_WAVE_NODE")
    sum_top_mid = Net("SUM_TOP_MID")
    sum_in = Net("SUM_IN")
    rect_out = Net("RECT_OUT")

    r3 = make_resistor(tpl["r"], "R3", "10k", "Half-wave rectifier input")
    r4 = make_resistor(tpl["r"], "R4", "10k", "Half-wave rectifier feedback")
    r5 = make_resistor(tpl["r"], "R5", "10k", "Direct summer input leg part 1")
    r6 = make_resistor(tpl["r"], "R6", "10k", "Direct summer input leg part 2")
    r7 = make_resistor(tpl["r"], "R7", "10k", "Half-wave summer input leg")
    r8 = make_resistor(tpl["r"], "R8", "22k", "Precision summer feedback")

    d1 = tpl["d_sig"](ref="D1", tag="d1")
    d2 = tpl["d_sig"](ref="D2", tag="d2")

    # U1B inverting half-wave precision rectifier
    out_gain & r3 & half_wave_in
    half_wave_in += u1[6]
    gnd += u1[5]
    half_wave_op_out += u1[7]
    half_wave_op_out & d1["A", "K"] & half_wave_in
    half_wave_op_out & d2["A", "K"] & half_wave_node
    half_wave_in & r4 & half_wave_node

    # U1C summing amplifier: combines direct path (20k) and half-wave path (10k)
    out_gain & r5 & sum_top_mid & r6 & sum_in
    half_wave_node & r7 & sum_in
    sum_in += u1[9]
    gnd += u1[10]
    rect_out += u1[8]
    sum_in & r8 & rect_out

    return rect_out


@subcircuit
def peak_detector_stage(tpl, rect_out, gnd):
    """Block 4: Peak charging diode, attack/release controls, and smoothing cap."""
    atk_in = Net("ATK_IN")
    env_filt = Net("ENV_FILT")
    led_in = Net("LED_IN")
    rel_node = Net("REL_NODE")

    d3 = tpl["d_sig"](ref="D3", tag="d3")
    rv_atk = tpl["pot"](ref="RV_ATK", value="50k", tag="rv_atk")
    rv_rel = tpl["pot"](ref="RV_REL", value="1M", tag="rv_rel")

    c2 = tpl["c_0603"](ref="C2", value="1uF", tag="c2")
    c2.fields["LCSC"] = "C559769"
    c2.fields["MPN"] = "CC0603KRX7R9BB105"
    c2.fields["JLCPCB_Class"] = "Extended"
    c2.fields["Notes"] = "Envelope smoothing capacitor (50V X7R)"

    r9 = make_resistor(tpl["r"], "R9", "1k", "Envelope peak isolation resistor")
    r10 = make_resistor(tpl["r"], "R10", "10k", "Release pot minimum resistance")

    rect_out & d3["A", "K"] & atk_in
    atk_in += rv_atk[1]
    env_filt += rv_atk[2, 3]
    env_filt & c2 & gnd
    env_filt & r9 & led_in
    led_in & r10 & rel_node
    rel_node += rv_rel[3]
    gnd += rv_rel[1, 2]

    return led_in


@subcircuit
def output_offset_stage(tpl, u1, led_in, pwr):
    """Block 5: Envelope output stage (U1D) with +/-12V DC offset and protection."""
    offset_hi = Net("OFFSET_HI")
    offset_lo = Net("OFFSET_LO")
    offset_wiper = Net("OFFSET_WIPER")
    offset_sum_in = Net("OFFSET_SUM_IN")
    out_buf_node = Net("OUT_BUF_NODE")
    signal_out = Net("SIGNAL_OUT")

    r11 = make_resistor(tpl["r"], "R11", "10k", "Offset +12V limit resistor")
    r12 = make_resistor(tpl["r"], "R12", "10k", "Offset -12V limit resistor")
    r13 = make_resistor(tpl["r"], "R13", "10k", "Offset wiper summing resistor")
    r14 = make_resistor(tpl["r"], "R14", "10k", "U1D inverting node ground ref")
    r15 = make_resistor(tpl["r"], "R15", "10k", "U1D feedback resistor")
    r16 = make_resistor(tpl["r"], "R16", "1k", "OUT short-circuit protection")

    rv_offset = tpl["pot"](ref="RV_OFFSET", value="100k", tag="rv_offset")

    j_out = tpl["jack"](ref="J_OUT", tag="j_out")

    pwr.pos & r11 & offset_hi
    offset_lo & r12 & pwr.neg
    offset_lo += rv_offset[1]
    offset_wiper += rv_offset[2]
    offset_hi += rv_offset[3]

    offset_wiper & r13 & offset_sum_in
    offset_sum_in & r14 & pwr.gnd
    led_in += u1[12]
    offset_sum_in += u1[13]
    out_buf_node += u1[14]
    offset_sum_in & r15 & out_buf_node

    out_buf_node & r16 & signal_out
    signal_out += j_out["T"]
    pwr.gnd += j_out["S"]
    j_out["TN"] += builtins.NC

    return out_buf_node


@subcircuit
def aux_inverter_led_and_termination(tpl, u2, out_buf_node, led_in, pwr):
    """Block 6: Inverted CV output (U2A), LED driver (U2B), and unused U2C/U2D."""
    inv_sum_in = Net("INV_SUM_IN")
    inv_buf_node = Net("INV_BUF_NODE")
    signal_inv_out = Net("SIGNAL_INV_OUT")
    led_buf_in = Net("LED_BUF_IN")
    led_drv = Net("LED_DRV")
    led_anode = Net("LED_ANODE")
    led_cathode = Net("LED_CATHODE")
    u2c_term = Net("U2C_TERM")
    u2d_term = Net("U2D_TERM")

    # U2A unity-gain inverting output stage
    r17 = make_resistor(tpl["r"], "R17", "10k", "Inverter input resistor")
    r18 = make_resistor(tpl["r"], "R18", "10k", "Inverter feedback resistor")
    r19 = make_resistor(tpl["r"], "R19", "1k", "INV_OUT short-circuit protection")
    j_inv_out = tpl["jack"](ref="J_INV_OUT", tag="j_inv_out")

    out_buf_node & r17 & inv_sum_in
    inv_sum_in += u2[2]
    pwr.gnd += u2[3]
    inv_buf_node += u2[1]
    inv_sum_in & r18 & inv_buf_node
    inv_buf_node & r19 & signal_inv_out
    signal_inv_out += j_inv_out["T"]
    pwr.gnd += j_inv_out["S"]
    j_inv_out["TN"] += builtins.NC

    # U2B voltage follower driving level LED with pre-biased cathode divider
    r20 = make_resistor(tpl["r"], "R20", "10k", "LED driver input isolation")
    r21 = make_resistor(tpl["r"], "R21", "22k", "LED current limiting resistor")
    r22 = make_resistor(tpl["r"], "R22", "10k", "LED cathode ground bias")
    r23 = make_resistor(tpl["r"], "R23", "33k", "LED cathode -12V pulldown")

    led1 = Part(
        "Device",
        "LED",
        ref="LED1",
        value="LED_3mm",
        footprint=FOOTPRINTS["led"],
        tag="led1",
    )
    led1.fields["JLCPCB_Class"] = "Manual THT"

    led_in & r20 & led_buf_in
    led_buf_in += u2[5]
    led_drv += u2[6, 7]
    led_drv & r21 & led_anode
    led_anode & led1["A", "K"] & led_cathode
    pwr.gnd & r22 & led_cathode
    led_cathode & r23 & pwr.neg

    # Terminate unused TL074H channels (U2C, U2D) as grounded unity-gain followers
    u2c_term += u2[8, 9]
    pwr.gnd += u2[10]
    u2d_term += u2[13, 14]
    pwr.gnd += u2[12]


def generate_jlcpcb_bom(file_="jlcpcb_bom.csv", include_tht=False):
    """Export a grouped JLCPCB PCBA BOM CSV (Comment,Designator,Footprint,LCSC Part #)."""
    groups = {}
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


def build_circuit():
    """Construct the complete Eurorack Envelope Follower circuit."""
    tpl = make_templates()

    pwr_netclass = NetClass("Power", priority=1, trace_width=0.6, clearance=0.25)
    pwr = Interface(
        pos_raw=Net("+12V_RAW"),
        neg_raw=Net("-12V_RAW"),
        pos=Net("+12V"),
        neg=Net("-12V"),
        gnd=Net("GND"),
    )
    for rail in (pwr.pos_raw, pwr.neg_raw, pwr.pos, pwr.neg, pwr.gnd):
        rail.drive = POWER
        rail.netclasses = pwr_netclass

    u1 = make_tl074h("U1", "Gain, Precision Full-Wave Rectifier & Output Stage")
    u2 = make_tl074h("U2", "Inverted Output, LED Driver & Terminated Channels")

    power_and_protection(tpl, u1, u2, pwr, tag="blk_power")
    out_gain = input_gain_stage(tpl, u1, pwr.gnd, tag="blk_input")
    rect_out = precision_rectifier_stage(
        tpl, u1, out_gain, pwr.gnd, tag="blk_rectifier"
    )
    led_in = peak_detector_stage(tpl, rect_out, pwr.gnd, tag="blk_peak")
    out_buf_node = output_offset_stage(tpl, u1, led_in, pwr, tag="blk_output")
    aux_inverter_led_and_termination(tpl, u2, out_buf_node, led_in, pwr, tag="blk_aux")

    erc_assert("len(u1.get_pins()) == 14", "U1 must be a 14-pin TL074H")
    erc_assert("len(u2.get_pins()) == 14", "U2 must be a 14-pin TL074H")
    erc_assert(
        "u1[4].is_connected() and u1[11].is_connected()", "U1 power rails missing"
    )
    erc_assert(
        "u2[4].is_connected() and u2[11].is_connected()", "U2 power rails missing"
    )


if __name__ == "__main__":
    import schematizer.engine.gen_schematic as _gs

    # Disable two-pin snapping in schematizer so series protection diodes (D4, D5)
    # do not overlap J_PWR pins and short -12V_RAW to GND.
    _gs._snap_two_pin_parts = lambda node: None

    build_circuit()
    ERC()
    generate_netlist(file_="envelope_follower.net")
    generate_xml(file_="envelope_follower_bom.xml")
    generate_jlcpcb_bom(file_="jlcpcb_bom.csv")
    generate_schematic(
        filepath=".",
        top_name="EnvelopeFollower",
        title="Eurorack Analog Envelope Follower",
        flatness=1.0,
        auto_stub=True,
        label_clearance=True,
    )
    if os.path.exists("EnvelopeFollower-erc.rpt"):
        os.remove("EnvelopeFollower-erc.rpt")
