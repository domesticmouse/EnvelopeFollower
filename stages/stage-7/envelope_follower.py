#!/usr/bin/env python3
"""SKiDL circuit definition for the Improved ±12 V Eurorack Envelope Follower.

Implements the hardware specification from:
  - EnvelopeFollowerImproved.md (2x TL074H, 8 op-amp stages, protections, netlist)
  - EnvelopeFollowerBOM.md (live-verified LCSC/MPN metadata & JLCPCB Economic BOM)
  - SilkscreenInstructions.md (Silkscreen tokens, DNP test points, SMT fiducials)
"""

import builtins
import csv
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)

os.environ.setdefault("XDG_DATA_HOME", "/tmp/xdg_data")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_config")
if os.path.isdir("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"):
    for _ver in ("", "6", "7", "8", "9", "10"):
        os.environ.setdefault(
            f"KICAD{_ver}_SYMBOL_DIR",
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
)


def _apply_fields(
    part,
    *,
    lcsc: str = "",
    mpn: str = "",
    manufacturer: str = "",
    jlc_class: str = "",
    silkscreen: str = "",
    notes: str = "",
) -> None:
    """Populate BOM, catalog, silkscreen, and assembly metadata into part.fields."""
    metadata = {
        "LCSC": lcsc,
        "MPN": mpn,
        "Manufacturer": manufacturer,
        "JLCPCB_Class": jlc_class,
        "Silkscreen": silkscreen,
        "Notes": notes,
    }
    for key, val in metadata.items():
        if val:
            part.fields[key] = val


def build_circuit() -> None:
    """Instantiate all 71 PCB footprints (68 BOM/DNP + 3 fiducials) and wire all nets."""
    # =========================================================================
    # 1. Nets & Power Classes
    # =========================================================================
    pwr_class = NetClass("Power", priority=1, trace_width=0.5, clearance=0.2)

    # Power rails (Stage 0)
    v12p_in = Net("+12V_IN")
    v12n_in = Net("-12V_IN")
    v12p_prot = Net("+12V_PROT")
    v12n_prot = Net("-12V_PROT")
    v12p = Net("+12V")
    v12n = Net("-12V")
    gnd = Net("GND")

    for pwr_net in (v12p_in, v12n_in, v12p_prot, v12n_prot, v12p, v12n, gnd):
        pwr_net.drive = POWER
        pwr_net.netclasses = pwr_class

    # Stage 1A: Input buffer
    in_tip = Net("IN_TIP")
    in_ac_pre = Net("IN_AC_PRE")
    in_ac = Net("IN_AC")
    u2d_in = Net("U2D_IN")
    in_buf = Net("IN_BUF")

    # Stage 1B: Preamp
    u1a_inv = Net("U1A_INV")
    gain_pot_1 = Net("GAIN_POT_1")
    preamp_out = Net("PREAMP_OUT")

    # Stages 2 & 3: Precision rectifier
    u1b_inv = Net("U1B_INV")
    u1b_out = Net("U1B_OUT")
    rect_hw = Net("RECT_HW")
    ff_mid = Net("FF_MID")
    u1c_inv = Net("U1C_INV")
    rect_fb_mid = Net("RECT_FB_MID")
    rect_out = Net("RECT_OUT")

    # Stage 4: Active peak detector & Attack/Release
    u2c_out = Net("U2C_OUT")
    atk_in = Net("ATK_IN")
    atk_pot_1 = Net("ATK_POT_1")
    env_node = Net("ENV_NODE")
    rel_pot_top = Net("REL_POT_TOP")

    # Stage 5: Offset, OUT, INV_OUT
    u1d_in = Net("U1D_IN")
    off_top = Net("OFF_TOP")
    off_bot = Net("OFF_BOT")
    off_wiper = Net("OFF_WIPER")
    u1d_inv = Net("U1D_INV")
    u1d_out = Net("U1D_OUT")
    out_clamp = Net("OUT_CLAMP")
    out_tip = Net("OUT_TIP")
    u2a_inv = Net("U2A_INV")
    u2a_out = Net("U2A_OUT")
    inv_out_clamp = Net("INV_OUT_CLAMP")
    inv_out_tip = Net("INV_OUT_TIP")

    # Stage 6: Precision LED current sink
    u2b_in = Net("U2B_IN")
    u2b_out = Net("U2B_OUT")
    led_k = Net("LED_K")

    # =========================================================================
    # 2. Templates
    # =========================================================================
    r0603_t = Part(
        "Device",
        "R",
        dest=TEMPLATE,
        footprint="Resistor_SMD:R_0603_1608Metric",
    )
    r1206_t = Part(
        "Device",
        "R",
        dest=TEMPLATE,
        footprint="Resistor_SMD:R_1206_3216Metric",
    )
    r1210_t = Part(
        "Device",
        "R",
        dest=TEMPLATE,
        footprint="Resistor_SMD:R_1210_3225Metric",
    )
    c0603_t = Part(
        "Device",
        "C",
        dest=TEMPLATE,
        footprint="Capacitor_SMD:C_0603_1608Metric",
    )
    pot_t = Part(
        "Device",
        "R_Potentiometer",
        dest=TEMPLATE,
        footprint="Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical",
    )
    jack_t = Part(
        "Connector_Audio",
        "AudioJack2_SwitchT",
        dest=TEMPLATE,
        footprint="Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles",
    )
    tp_t = Part(
        "Connector",
        "TestPoint",
        dest=TEMPLATE,
        value="RH-5001",
        footprint="TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm",
    )
    fid_t = Part(
        "Mechanical",
        "Fiducial",
        dest=TEMPLATE,
        value="Fiducial",
        footprint="Fiducial:Fiducial_1mm_Mask2mm",
    )
    if getattr(fid_t, "lib", None) is not None:
        fid_t.lib.filename = "Mechanical"

    def make_r(
        tmpl,
        ref: str,
        value: str,
        *,
        lcsc: str,
        mpn: str,
        manufacturer: str,
        jlc_class: str,
        silkscreen: str,
        notes: str = "",
    ):
        part = tmpl(ref=ref, value=value, tag=ref.lower())
        _apply_fields(
            part,
            lcsc=lcsc,
            mpn=mpn,
            manufacturer=manufacturer,
            jlc_class=jlc_class,
            silkscreen=silkscreen,
            notes=notes,
        )
        return part

    def make_r_10k(ref: str, notes: str = "F.Cu SMT"):
        return make_r(
            r0603_t,
            ref,
            "10k",
            lcsc="C25804",
            mpn="0603WAF1002T5E",
            manufacturer="UNI-ROYAL",
            jlc_class="Basic",
            silkscreen="10k",
            notes=notes,
        )

    def make_r_10k_01(ref: str):
        return make_r(
            r0603_t,
            ref,
            "10k 0.1%",
            lcsc="C95204",
            mpn="RT0603BRD0710KL",
            manufacturer="YAGEO",
            jlc_class="Extended",
            silkscreen="10k",
            notes="F.Cu SMT; 0.1% 25ppm matched rectifier network at U1B/U1C",
        )

    def make_r_1k(ref: str, notes: str = "F.Cu SMT"):
        return make_r(
            r0603_t,
            ref,
            "1k",
            lcsc="C21190",
            mpn="0603WAF1001T5E",
            manufacturer="UNI-ROYAL",
            jlc_class="Basic",
            silkscreen="1k",
            notes=notes,
        )

    def make_r_470_05w(ref: str):
        return make_r(
            r1210_t,
            ref,
            "470R 0.5W",
            lcsc="C333193",
            mpn="RTT124700FTP",
            manufacturer="RALEC",
            jlc_class="Extended",
            silkscreen="470R",
            notes="F.Cu SMT; 0.5W clash-rated with copper thermal relief; Alt 2010: C341646",
        )

    # =========================================================================
    # 3. Components (Ordered cleanly to match EnvelopeFollowerBOM.md)
    # =========================================================================
    # --- ICs (2 x TL074H SOIC-14) ---
    u1 = Part(
        "Amplifier_Operational",
        "TL074",
        ref="U1",
        value="TL074H",
        footprint="Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
        tag="u1",
    )
    _apply_fields(
        u1,
        lcsc="C2878713",
        mpn="TL074HIDR",
        manufacturer="Texas Instruments",
        jlc_class="Extended",
        silkscreen="U1 TL074H",
        notes="F.Cu SMT; Pin-1 dot on F.SilkS; place 100nF bypasses within 3-5mm of V+/V-",
    )

    u2 = Part(
        "Amplifier_Operational",
        "TL074",
        ref="U2",
        value="TL074H",
        footprint="Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
        tag="u2",
    )
    _apply_fields(
        u2,
        lcsc="C2878713",
        mpn="TL074HIDR",
        manufacturer="Texas Instruments",
        jlc_class="Extended",
        silkscreen="U2 TL074H",
        notes="F.Cu SMT; Pin-1 dot on F.SilkS; place 100nF bypasses within 3-5mm of V+/V-",
    )

    # --- SMT Diodes (8) ---
    # KiCad Device:D_Schottky / Diode:1N4148WS / Device:LED: Pin 1 = K, Pin 2 = A
    d_pwr_p = Part(
        "Device",
        "D_Schottky",
        ref="D_PWR_P",
        value="B5819W",
        footprint="Diode_SMD:D_SOD-123",
        tag="d_pwr_p",
    )
    _apply_fields(
        d_pwr_p,
        lcsc="C8598",
        mpn="B5819W SL",
        manufacturer="Changjing Elec",
        jlc_class="Basic",
        silkscreen="D_PWR_P B5819W",
        notes="F.Cu SMT; 0.25mm cathode bar outside Pad 1 (K to +12V_PROT); Alt SOD-323: 1N5819WS (C191023)",
    )

    d_pwr_n = Part(
        "Device",
        "D_Schottky",
        ref="D_PWR_N",
        value="B5819W",
        footprint="Diode_SMD:D_SOD-123",
        tag="d_pwr_n",
    )
    _apply_fields(
        d_pwr_n,
        lcsc="C8598",
        mpn="B5819W SL",
        manufacturer="Changjing Elec",
        jlc_class="Basic",
        silkscreen="D_PWR_N B5819W",
        notes="F.Cu SMT; 0.25mm cathode bar outside Pad 1 (K to -12V_IN, reversed vs D_PWR_P); Alt SOD-323: C191023",
    )

    # BAT54S SOT-23: Pin 1 = A1, Pin 2 = K2, Pin 3 = COM (K1/A2)
    d1_d2 = Part(
        "Diode",
        "BAT54S",
        ref="D1_D2",
        value="BAT54S",
        footprint="Package_TO_SOT_SMD:SOT-23",
        tag="d1_d2",
    )
    _apply_fields(
        d1_d2,
        lcsc="C47546",
        mpn="BAT54S,215",
        manufacturer="Nexperia",
        jlc_class="Extended",
        silkscreen="D1_D2 BAT54S",
        notes="F.Cu SMT; Pin-1 (A1) dot on F.SilkS",
    )

    d3 = Part(
        "Diode",
        "1N4148WS",
        ref="D3",
        value="1N4148WS",
        footprint="Diode_SMD:D_SOD-323",
        tag="d3",
    )
    _apply_fields(
        d3,
        lcsc="C2128",
        mpn="1N4148WS",
        manufacturer="Changjing Elec",
        jlc_class="Basic",
        silkscreen="D3 1N4148WS",
        notes="F.Cu SMT; 0.25mm cathode bar outside Pad 1 (K to ATK_IN); Alt SOD-123: 1N4148W (C81598)",
    )

    d_led_clamp = Part(
        "Diode",
        "1N4148WS",
        ref="D_LED_CLAMP",
        value="1N4148WS",
        footprint="Diode_SMD:D_SOD-323",
        tag="d_led_clamp",
    )
    _apply_fields(
        d_led_clamp,
        lcsc="C2128",
        mpn="1N4148WS",
        manufacturer="Changjing Elec",
        jlc_class="Basic",
        silkscreen="D_LED_CLAMP 1N4148WS",
        notes="F.Cu SMT; 0.25mm cathode bar outside Pad 1 (K to U2B_OUT, anti-parallel across D4); Alt SOD-123: C81598",
    )

    # KiCad Diode:BAV99 physical SOT-23 pinout: Pin 1 = A1, Pin 2 = K2, Pin 3 = COM
    # Always index BAV99 by pin numbers [1, 2, 3] because legacy hidden pin names say K/A/K.
    bav99_defs = (
        ("D_IN", "F.Cu SMT; Pin-1 (A1) dot on F.SilkS; IN_AC ±12V clamp"),
        ("D_OUT", "F.Cu SMT; Pin-1 (A1) dot on F.SilkS; OUT_CLAMP ±12V clamp"),
        ("D_INV_OUT", "F.Cu SMT; Pin-1 (A1) dot on F.SilkS; INV_OUT_CLAMP ±12V clamp"),
    )
    bav99 = {}
    for ref, note in bav99_defs:
        part = Part(
            "Diode",
            "BAV99",
            ref=ref,
            value="BAV99",
            footprint="Package_TO_SOT_SMD:SOT-23",
            tag=ref.lower(),
        )
        _apply_fields(
            part,
            lcsc="C2500",
            mpn="BAV99,215",
            manufacturer="Nexperia",
            jlc_class="Basic",
            silkscreen=f"{ref} BAV99",
            notes=note,
        )
        bav99[ref] = part
    d_in, d_out, d_inv_out = bav99["D_IN"], bav99["D_OUT"], bav99["D_INV_OUT"]

    # --- SMT Resistors (30) ---
    r_pwr_p = make_r(
        r1206_t,
        "R_PWR_P",
        "10R",
        lcsc="C17903",
        mpn="1206W4F100JT5E",
        manufacturer="UNI-ROYAL",
        jlc_class="Basic",
        silkscreen="10R",
        notes="F.Cu SMT; +12V RC damping/inrush limiter",
    )
    r_pwr_n = make_r(
        r1206_t,
        "R_PWR_N",
        "10R",
        lcsc="C17903",
        mpn="1206W4F100JT5E",
        manufacturer="UNI-ROYAL",
        jlc_class="Basic",
        silkscreen="10R",
        notes="F.Cu SMT; -12V RC damping/inrush limiter",
    )
    r_atk_min = make_r(
        r0603_t,
        "R_ATK_MIN",
        "470R",
        lcsc="C23179",
        mpn="0603WAF4700T5E",
        manufacturer="UNI-ROYAL",
        jlc_class="Basic",
        silkscreen="470R",
        notes="F.Cu SMT; Attack current/ringing limiter (0.47ms floor)",
    )
    r16a = make_r_470_05w("R16A")
    r16b = make_r_470_05w("R16B")
    r19a = make_r_470_05w("R19A")
    r19b = make_r_470_05w("R19B")

    r_in_prot = make_r_1k("R_IN_PROT", "F.Cu SMT; J1 Tip ESD/overvoltage limiter")
    r_in_buf = make_r_1k("R_IN_BUF", "F.Cu SMT; U2D+ ESD input current limiter")
    r_gain_min = make_r_1k("R_GAIN_MIN", "F.Cu SMT; U1A minimum gain floor (-0.10x)")
    r11 = make_r_1k("R11", "F.Cu SMT; OFFSET top end resistor (+9.63V)")
    r12 = make_r_1k("R12", "F.Cu SMT; OFFSET bottom end resistor (-9.63V)")

    r_led = make_r(
        r0603_t,
        "R_LED",
        "2.2k",
        lcsc="C4190",
        mpn="0603WAF2201T5E",
        manufacturer="UNI-ROYAL",
        jlc_class="Basic",
        silkscreen="2.2k",
        notes="F.Cu SMT; U2B LED current sink resistor (0-4.5mA)",
    )

    r2 = make_r_10k("R2", "F.Cu SMT; U1A preamp input resistor")
    r10 = make_r_10k("R10", "F.Cu SMT; Release minimum decay resistor (10ms floor)")
    r_env_prot = make_r_10k("R_ENV_PROT", "F.Cu SMT; U1D+ brownout isolation resistor")
    r15 = make_r_10k("R15", "F.Cu SMT; U1D in-loop DC feedback from OUT_CLAMP")
    r17 = make_r_10k("R17", "F.Cu SMT; U2A inverting input from OUT_CLAMP")
    r18 = make_r_10k("R18", "F.Cu SMT; U2A in-loop DC feedback from INV_OUT_CLAMP")
    r20 = make_r_10k("R20", "F.Cu SMT; U2B+ LED buffer input isolation")

    r3 = make_r_10k_01("R3")
    r4 = make_r_10k_01("R4")
    r5 = make_r_10k_01("R5")
    r6 = make_r_10k_01("R6")
    r7 = make_r_10k_01("R7")
    r8a = make_r_10k_01("R8A")
    r8b = make_r_10k_01("R8B")

    r13 = make_r(
        r0603_t,
        "R13",
        "18k",
        lcsc="C25810",
        mpn="0603WAF1802T5E",
        manufacturer="UNI-ROYAL",
        jlc_class="Basic",
        silkscreen="18k",
        notes="F.Cu SMT; OFFSET summing resistor (±5.09V range)",
    )
    r1 = make_r(
        r0603_t,
        "R1",
        "100k",
        lcsc="C25803",
        mpn="0603WAF1003T5E",
        manufacturer="UNI-ROYAL",
        jlc_class="Basic",
        silkscreen="100k",
        notes="F.Cu SMT; Input AC-coupling GND bias (Z_in = 101k)",
    )
    r_gain_fail = make_r(
        r0603_t,
        "R_GAIN_FAIL",
        "1M",
        lcsc="C22935",
        mpn="0603WAF1004T5E",
        manufacturer="UNI-ROYAL",
        jlc_class="Basic",
        silkscreen="1M",
        notes="F.Cu SMT; place close to U1.1/U1.2; open-pot-wiper fail-safe",
    )

    # --- SMT Capacitors (9) ---
    c_decs = []
    for idx in range(1, 5):
        ref = f"C_DEC{idx}"
        cap = c0603_t(ref=ref, value="100nF", tag=ref.lower())
        _apply_fields(
            cap,
            lcsc="C14663",
            mpn="CC0603KRX7R9BB104",
            manufacturer="YAGEO",
            jlc_class="Basic",
            silkscreen="100nF",
            notes="F.Cu SMT; local V+/V- decoupling within 3-5mm of U1/U2 supply pins",
        )
        c_decs.append(cap)
    c_dec1, c_dec2, c_dec3, c_dec4 = c_decs

    c_hf = c0603_t(ref="C_HF", value="47pF C0G", tag="c_hf")
    _apply_fields(
        c_hf,
        lcsc="C1671",
        mpn="CL10C470JB8NNNC",
        manufacturer="Samsung",
        jlc_class="Basic",
        silkscreen="47pF",
        notes="F.Cu SMT; place close to U1.1/U1.2; Alt C0G: 33pF (C1663) or 22pF (C1653)",
    )

    c_out1 = c0603_t(ref="C_OUT1", value="100pF C0G", tag="c_out1")
    _apply_fields(
        c_out1,
        lcsc="C14858",
        mpn="CL10C101JB8NNNC",
        manufacturer="Samsung",
        jlc_class="Basic",
        silkscreen="100pF",
        notes="F.Cu SMT; U1D local HF compensation",
    )

    c_out2 = c0603_t(ref="C_OUT2", value="100pF C0G", tag="c_out2")
    _apply_fields(
        c_out2,
        lcsc="C14858",
        mpn="CL10C101JB8NNNC",
        manufacturer="Samsung",
        jlc_class="Basic",
        silkscreen="100pF",
        notes="F.Cu SMT; U2A local HF compensation",
    )

    # KiCad Device:C_Polarized: Pin 1 = +, Pin 2 = -
    c3 = Part(
        "Device",
        "C_Polarized",
        ref="C3",
        value="22uF 50V",
        footprint="Capacitor_SMD:CP_Elec_6.3x5.4",
        tag="c3",
    )
    _apply_fields(
        c3,
        lcsc="C2836438",
        mpn="RVT22UF50V67RV0028",
        manufacturer="KNSCHA",
        jlc_class="Extended",
        silkscreen="22uF",
        notes="F.Cu SMT; bold + mark on F.SilkS (+12V to GND); Alt 35V D5x5.4: C2887274",
    )

    c4 = Part(
        "Device",
        "C_Polarized",
        ref="C4",
        value="22uF 50V",
        footprint="Capacitor_SMD:CP_Elec_6.3x5.4",
        tag="c4",
    )
    _apply_fields(
        c4,
        lcsc="C2836438",
        mpn="RVT22UF50V67RV0028",
        manufacturer="KNSCHA",
        jlc_class="Extended",
        silkscreen="22uF",
        notes="F.Cu SMT; bold + mark on F.SilkS (+ pad to GND, - pad to -12V); Alt 35V D5x5.4: C2887274",
    )

    # --- Populated THT Components (11, mounted later) ---
    c1 = Part(
        "Device",
        "C",
        ref="C1",
        value="1uF 100V",
        footprint="Capacitor_THT:C_Rect_L7.2mm_W6.0mm_P5.00mm",
        tag="c1",
    )
    _apply_fields(
        c1,
        lcsc="C125397",
        mpn="B32529D1105J000",
        manufacturer="TDK",
        jlc_class="Manual THT",
        silkscreen="1uF",
        notes="B.Cu manual THT; non-polarized PET film; echo 1uF on F.SilkS+B.SilkS; Alt W5.5mm fp: Capacitor_THT:C_Rect_L7.2mm_W5.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2; Alt WIMA: C92673",
    )

    c2 = Part(
        "Device",
        "C",
        ref="C2",
        value="1uF 100V",
        footprint="Capacitor_THT:C_Rect_L7.2mm_W6.0mm_P5.00mm",
        tag="c2",
    )
    _apply_fields(
        c2,
        lcsc="C125397",
        mpn="B32529D1105J000",
        manufacturer="TDK",
        jlc_class="Manual THT",
        silkscreen="1uF",
        notes="B.Cu manual THT; non-polarized PET film hold cap; echo 1uF on F.SilkS+B.SilkS; Alt W5.5mm fp; Alt WIMA: C92673",
    )

    j4 = Part(
        "Connector_Generic",
        "Conn_02x05_Odd_Even",
        ref="J4",
        value="IDC 2x5P 2.54mm",
        footprint="Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical",
        tag="j4",
    )
    _apply_fields(
        j4,
        lcsc="C53207560",
        mpn="IDC2.54-2*5PZ",
        manufacturer="JXTCONN",
        jlc_class="Manual THT",
        silkscreen="J4 PWR",
        notes="B.Cu manual THT; dual-sided silkscreen; RED STRIPE / -12V bar on pins 1-2; +12V on pins 9-10",
    )

    d4 = Part(
        "Device",
        "LED",
        ref="D4",
        value="3mm Red LED",
        footprint="LED_THT:LED_D3.0mm",
        tag="d4",
    )
    _apply_fields(
        d4,
        lcsc="C99771",
        mpn="204-10SURD/S530-A3-L",
        manufacturer="Everlight",
        jlc_class="Manual THT",
        silkscreen="D4 LED",
        notes="F.Cu panel THT; dual-sided silkscreen + +/- polarity marks (Pin 1=K, Pin 2=A)",
    )

    j1 = jack_t(ref="J1", value="WQP-PJ398SM", tag="j1")
    _apply_fields(
        j1,
        mpn="WQP-PJ398SM",
        manufacturer="QingPu",
        jlc_class="Consigned THT",
        silkscreen="J1 IN",
        notes="F.Cu panel THT; J1.TN to GND (mandatory); dual-sided silkscreen; Alt LCSC: C56407602",
    )

    j2 = jack_t(ref="J2", value="WQP-PJ398SM", tag="j2")
    _apply_fields(
        j2,
        mpn="WQP-PJ398SM",
        manufacturer="QingPu",
        jlc_class="Consigned THT",
        silkscreen="J2 OUT",
        notes="F.Cu panel THT; J2.TN = NC; dual-sided silkscreen; Alt LCSC: C56407602",
    )

    j3 = jack_t(ref="J3", value="WQP-PJ398SM", tag="j3")
    _apply_fields(
        j3,
        mpn="WQP-PJ398SM",
        manufacturer="QingPu",
        jlc_class="Consigned THT",
        silkscreen="J3 INV_OUT",
        notes="F.Cu panel THT; J3.TN = NC; dual-sided silkscreen; Alt LCSC: C56407602",
    )

    rv1 = pot_t(ref="RV1", value="A100k", tag="rv1")
    _apply_fields(
        rv1,
        mpn="RV09AF-40-20K-A104",
        manufacturer="Alpha",
        jlc_class="Consigned THT",
        silkscreen="RV1 GAIN A100k",
        notes="F.Cu panel THT; audio taper; mark Pin 1 on F.SilkS+B.SilkS; dual-sided silkscreen",
    )

    rv2 = pot_t(ref="RV2", value="A50k", tag="rv2")
    _apply_fields(
        rv2,
        mpn="RV09AF-40-20K-A503",
        manufacturer="Alpha",
        jlc_class="Consigned THT",
        silkscreen="RV2 ATK A50k",
        notes="F.Cu panel THT; audio taper; mark Pin 1 on F.SilkS+B.SilkS; dual-sided silkscreen",
    )

    rv3 = pot_t(ref="RV3", value="A1M", tag="rv3")
    _apply_fields(
        rv3,
        mpn="RV09AF-40-20K-A105",
        manufacturer="Alpha",
        jlc_class="Consigned THT",
        silkscreen="RV3 REL A1M",
        notes="F.Cu panel THT; audio taper; mark Pin 1 on F.SilkS+B.SilkS; dual-sided silkscreen",
    )

    rv4 = pot_t(ref="RV4", value="B10k", tag="rv4")
    _apply_fields(
        rv4,
        mpn="RV09AF-40-20K-B103",
        manufacturer="Alpha",
        jlc_class="Consigned THT",
        silkscreen="RV4 OFF B10k",
        notes="F.Cu panel THT; linear taper; mark Pin 1 (+9.63V CCW) on F.SilkS+B.SilkS; dual-sided silkscreen",
    )

    # --- Optional DNP Test Points (8, B.Cu pads / optional RH-5001 pins) ---
    tp_specs = [
        ("TP1", gnd, "TP1 GND"),
        ("TP2", v12p, "TP2 +12V"),
        ("TP3", v12n, "TP3 -12V"),
        ("TP4", in_buf, "TP4 IN_BUF"),
        ("TP5", preamp_out, "TP5 PREAMP"),
        ("TP6", rect_out, "TP6 RECT"),
        ("TP7", out_clamp, "TP7 OUT"),
        ("TP8", inv_out_clamp, "TP8 INV_OUT"),
    ]
    for tp_ref, tp_net, tp_silk in tp_specs:
        tp = tp_t(ref=tp_ref, tag=tp_ref.lower())
        tp.dnp = True
        tp.exclude_from_bom = True
        _apply_fields(
            tp,
            lcsc="C5199801",
            mpn="RH-5001",
            manufacturer="Ronghe",
            jlc_class="DNP THT",
            silkscreen=tp_silk,
            notes="DNP; bare B.Cu plated THT pad (optional RH-5001 pin on B.Cu); dual-sided silkscreen; verify 1.0mm drill in C5199801 datasheet",
        )
        tp_net += tp[1]

    # --- SMT Optical Fiducials (3, F.Cu) ---
    for idx in range(1, 4):
        fid_ref = f"FID{idx}"
        fid = fid_t(ref=fid_ref, tag=fid_ref.lower())
        fid.dnp = True
        fid.exclude_from_bom = True
        _apply_fields(
            fid,
            jlc_class="Fiducial",
            notes="F.Cu SMT optical fiducial (1.0mm pad, 2.0mm mask, ±1.25mm silk keepout, zero silkscreen)",
        )

    # =========================================================================
    # 4. Pin-Level Connectivity (EnvelopeFollowerImproved.md §5)
    # =========================================================================
    # Stage 0 — Eurorack Power Entry, Reverse-Polarity Protection & Decoupling
    v12p_in += j4[9, 10], d_pwr_p[2]  # A
    v12n_in += j4[1, 2], d_pwr_n[1]  # K
    v12p_prot += d_pwr_p[1], r_pwr_p[1]  # K -> R_PWR_P.1
    v12n_prot += d_pwr_n[2], r_pwr_n[1]  # A -> R_PWR_N.1

    v12p += (
        r_pwr_p[2],
        c3[1],
        c_dec1[1],
        c_dec3[1],
        u1[4],
        u2[4],
        d_in[2],
        d_out[2],
        d_inv_out[2],
        r11[1],
    )
    v12n += (
        r_pwr_n[2],
        c4[2],
        c_dec2[1],
        c_dec4[1],
        u1[11],
        u2[11],
        d_in[1],
        d_out[1],
        d_inv_out[1],
        r12[1],
    )
    gnd += (
        j4[3, 4, 5, 6, 7, 8],
        c3[2],
        c4[1],
        c_dec1[2],
        c_dec2[2],
        c_dec3[2],
        c_dec4[2],
    )

    # Stage 1A — Input Protection, AC Coupling & 100 kOhm Buffer (U2D)
    gnd += j1["S"], j1["TN"], r1[2]
    in_tip += j1["T"], r_in_prot[1]
    in_ac_pre += r_in_prot[2], c1[1]
    in_ac += c1[2], r1[1], d_in[3], r_in_buf[1]
    u2d_in += r_in_buf[2], u2[12]
    in_buf += u2[14], u2[13], r2[1]

    # Stage 1B — Protected Inverting Preamp (U1A)
    gnd += u1[3]
    u1a_inv += r2[2], u1[2], r_gain_min[1], r_gain_fail[1], c_hf[1]
    gain_pot_1 += r_gain_min[2], rv1[1]
    preamp_out += u1[1], rv1[2], rv1[3], r_gain_fail[2], c_hf[2], r3[1], r4[1]

    # Stages 2 & 3 — 0.1%-Matched Unity-Gain Precision Rectifier (U1B, U1C, D1_D2)
    gnd += u1[5], u1[10]
    u1b_inv += r3[2], u1[6], r6[1], d1_d2[2]
    u1b_out += u1[7], d1_d2[3]
    rect_hw += d1_d2[1], r6[2], r7[1]
    ff_mid += r4[2], r5[1]
    u1c_inv += r5[2], r7[2], u1[9], r8a[1]
    rect_fb_mid += r8a[2], r8b[1]
    rect_out += u1[8], r8b[2], u2[10]

    # Stage 4 — Active Zero-Deadzone Peak Detector & Attack/Release (U2C)
    u2c_out += u2[8], d3[2]  # A
    atk_in += d3[1], u2[9], r_atk_min[1]  # K
    atk_pot_1 += r_atk_min[2], rv2[1]
    env_node += rv2[2], rv2[3], c2[1], r10[1], r_env_prot[1], r20[1]
    rel_pot_top += r10[2], rv3[1]
    gnd += c2[2], rv3[2], rv3[3]

    # Stage 5 — Linearized OFFSET, In-Loop Feedback & Protected Outputs (U1D, U2A)
    u1d_in += r_env_prot[2], u1[12]
    off_top += r11[2], rv4[1]
    off_bot += r12[2], rv4[3]
    off_wiper += rv4[2], r13[1]
    u1d_inv += r13[2], r15[1], c_out1[1], u1[13]
    u1d_out += u1[14], c_out1[2], r16a[1]
    out_clamp += r16a[2], r15[2], d_out[3], r16b[1], r17[1]
    out_tip += r16b[2], j2["T"]
    gnd += j2["S"], u2[3], j3["S"]
    j2["TN"] += builtins.NC

    u2a_inv += r17[2], r18[1], c_out2[1], u2[2]
    u2a_out += u2[1], c_out2[2], r19a[1]
    inv_out_clamp += r19a[2], r18[2], d_inv_out[3], r19b[1]
    inv_out_tip += r19b[2], j3["T"]
    j3["TN"] += builtins.NC

    # Stage 6 — In-Loop Precision LED Current Sink (U2B)
    u2b_in += r20[2], u2[5]
    u2b_out += u2[7], d4[2], d_led_clamp[1]  # D4.A, D_LED_CLAMP.K
    led_k += d4[1], d_led_clamp[2], u2[6], r_led[1]  # D4.K, D_LED_CLAMP.A
    gnd += r_led[2]

    # =========================================================================
    # 5. ERC Assertions
    # =========================================================================
    erc_assert(
        "len(builtins.default_circuit.parts) == 71",
        "Expected 71 total footprints (68 BOM/DNP + 3 fiducials)",
    )
    erc_assert(
        "len(builtins.default_circuit.get_nets()) == 42",
        "Expected 42 active signal/power nets",
    )
    erc_assert("len(v12p) == 11", "Expected 11 nodes on +12V rail")
    erc_assert("len(v12n) == 11", "Expected 11 nodes on -12V rail")
    erc_assert("len(gnd) == 26", "Expected 26 nodes on GND net")
    erc_assert("len(preamp_out) == 8", "Expected 8 nodes on PREAMP_OUT")
    erc_assert("len(rect_out) == 4", "Expected 4 nodes on RECT_OUT")
    erc_assert("len(env_node) == 6", "Expected 6 nodes on ENV_NODE")
    erc_assert("len(out_clamp) == 6", "Expected 6 nodes on OUT_CLAMP")
    erc_assert("len(inv_out_clamp) == 5", "Expected 5 nodes on INV_OUT_CLAMP")


def generate_jlcpcb_bom(
    file_: str = "jlcpcb_bom.csv", include_tht: bool = False
) -> tuple[int, int]:
    """Export a grouped 4-column JLCPCB PCBA BOM CSV (`Comment,Designator,Footprint,LCSC Part #`)."""
    groups: dict[tuple[str, str, str], list[str]] = {}
    total_parts = 0
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
        total_parts += 1

    with open(file_, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (comment, footprint, lcsc), refs in groups.items():
            writer.writerow([comment, ", ".join(refs), footprint, lcsc])

    return len(groups), total_parts


def main() -> None:
    """Build the circuit, run ERC, and export netlist, XML BOM, and JLCPCB CSV."""
    build_circuit()
    ERC()
    generate_netlist(file_="envelope_follower.net")
    generate_xml(file_="envelope_follower_bom.xml")
    bom_lines, bom_parts = generate_jlcpcb_bom(file_="jlcpcb_bom.csv")

    total_parts = len(builtins.default_circuit.parts)
    active_nets = len(builtins.default_circuit.get_nets())
    print(
        f"Summary: {total_parts} total footprints, {active_nets} active nets, "
        f"jlcpcb_bom.csv -> {bom_lines} lines ({bom_parts} SMT parts)"
    )


if __name__ == "__main__":
    main()
