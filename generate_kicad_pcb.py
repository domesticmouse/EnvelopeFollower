#!/usr/bin/env python3
"""Generate EnvelopeFollower.kicad_pcb directly from envelope_follower.net.

Uses KiCad's bundled Python `pcbnew` and `kinet2pcb` to:
1. Import all 48 components and 35 nets from `envelope_follower.net`.
2. Copy custom BOM/catalog fields (`LCSC`, `MPN`, `JLCPCB_Class`, `Notes`) from
   the netlist onto every PCB footprint.
3. Define a 6 HP (29.60 mm x 107.00 mm) Eurorack `Edge.Cuts` board outline
   centered behind a 30.00 mm x 128.50 mm Doepfer A-100 3U panel.
4. Pre-place the 8 front-panel controls (`RV_GAIN`, `RV_ATK`, `RV_REL`,
   `RV_OFFSET`, `LED1`, `J_IN`, `J_OUT`, `J_INV_OUT`) on `F.Cu` aligned to an
   ergonomic Eurorack control grid.
5. Flip `J_PWR` and all 39 SMT components to `B.Cu`, place them cleanly by
   functional stage with local IC decoupling adjacent to `U1`/`U2` power pins,
   and add rear `-12V RED STRIPE` / `+12V` polarity markings on `B.SilkS`.
"""

import glob
import os
import pathlib
import sys

KICAD_PYTHON = (
    "/Applications/KiCad/KiCad.app/Contents/Frameworks/"
    "Python.framework/Versions/Current/bin/python3"
)
KICAD_FP_DIR = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"

# Ensure KiCad's bundled Python (with `pcbnew`) and local `.venv` packages
# (`kinet2pcb`, `simp_sexp`) are both available when invoked from any Python.
try:
    import pcbnew
except ImportError:
    if os.path.exists(KICAD_PYTHON) and sys.executable != KICAD_PYTHON:
        os.execv(KICAD_PYTHON, [KICAD_PYTHON, *sys.argv])
    raise

REPO_DIR = pathlib.Path(__file__).resolve().parent
for site_pkg in sorted(
    glob.glob(str(REPO_DIR / ".venv" / "lib" / "python*" / "site-packages"))
):
    if site_pkg not in sys.path:
        sys.path.append(site_pkg)

import kinet2pcb
import simp_sexp

# 6 HP Eurorack main PCB dimensions (mm):
# Panel is 30.00 x 128.50 mm spanning X=[100.00, 130.00], Y=[10.00, 138.50].
# Main PCB has 0.20 mm side clearance and 10.75 mm top/bottom rail clearance.
BOARD_MIN_X = 100.20
BOARD_MAX_X = 129.80
BOARD_MIN_Y = 20.75
BOARD_MAX_Y = 127.75

# Placement table: ref -> (x_mm, y_mm, rot_deg, side) where side is "F" or "B".
# Front-panel controls are placed so their shaft/bushing/lens centers sit at:
#   RV_GAIN:   (115.00,  29.00)  [RD901F offset (+2.50, -7.50) at rot=90]
#   RV_ATK:    (115.00,  45.50)
#   RV_REL:    (115.00,  62.00)
#   RV_OFFSET: (115.00,  78.50)
#   J_IN:      (108.00,  98.00)  [WQP-PJ398SM offset (0.00, +6.48) at rot=0]
#   LED1:      (122.00,  98.00)  [LED_D3.0mm offset (+1.27, 0.00) at rot=0]
#   J_OUT:     (108.00, 116.00)
#   J_INV_OUT: (122.00, 116.00)
COMPONENT_PLACEMENTS: dict[str, tuple[float, float, float, str]] = {
    # --- Front Panel Controls (F.Cu) ---
    "RV_GAIN": (112.50, 36.50, 90.0, "F"),
    "RV_ATK": (112.50, 53.00, 90.0, "F"),
    "RV_REL": (112.50, 69.50, 90.0, "F"),
    "RV_OFFSET": (112.50, 86.00, 90.0, "F"),
    "J_IN": (108.00, 91.52, 0.0, "F"),
    "LED1": (120.73, 98.00, 0.0, "F"),
    "J_OUT": (108.00, 109.52, 0.0, "F"),
    "J_INV_OUT": (122.00, 109.52, 0.0, "F"),
    # --- Rear Power Entry & Protection (B.Cu) ---
    "J_PWR": (113.73, 119.20, 0.0, "B"),
    "D5": (111.50, 97.50, 90.0, "B"),
    "D4": (117.50, 97.50, 90.0, "B"),
    "C4": (111.90, 91.00, 90.0, "B"),
    "C3": (117.10, 91.00, 90.0, "B"),
    # --- Quad Op-Amps & Local Decoupling (B.Cu) ---
    "U1": (105.00, 53.00, 180.0, "B"),
    "C5": (110.20, 49.80, 90.0, "B"),
    "C6": (102.70, 46.40, 90.0, "B"),
    "U2": (125.00, 86.00, 0.0, "B"),
    "C7": (119.80, 82.80, 90.0, "B"),
    "C8": (127.30, 92.60, 90.0, "B"),
    # --- Block 2: Input Coupling & Gain Stage (B.Cu) ---
    "R_GAIN_MIN": (104.35, 34.00, 0.0, "B"),
    "R2": (104.35, 37.50, 0.0, "B"),
    "R1": (104.35, 40.50, 0.0, "B"),
    "C1": (104.35, 43.40, 0.0, "B"),
    # --- Block 3: Precision Full-Wave Rectifier (B.Cu) ---
    "R5": (102.80, 59.30, 0.0, "B"),
    "R3": (106.50, 59.30, 0.0, "B"),
    "D1": (104.35, 62.00, 0.0, "B"),
    "D2": (104.35, 65.20, 0.0, "B"),
    "R6": (102.80, 68.00, 0.0, "B"),
    "R4": (106.50, 68.00, 0.0, "B"),
    "R8": (102.80, 70.60, 0.0, "B"),
    "R7": (106.50, 70.60, 0.0, "B"),
    # --- Block 4: Peak Detector & Timing (B.Cu) ---
    "D3": (115.00, 56.60, 0.0, "B"),
    "C2": (115.00, 59.50, 0.0, "B"),
    "R9": (115.00, 62.50, 0.0, "B"),
    "R10": (115.00, 65.50, 0.0, "B"),
    # --- Block 5: Output Amplifier & DC Offset (B.Cu) ---
    "R11": (104.35, 73.50, 0.0, "B"),
    "R12": (104.35, 76.10, 0.0, "B"),
    "R13": (104.35, 78.70, 0.0, "B"),
    "R14": (104.35, 81.30, 0.0, "B"),
    "R15": (104.35, 83.90, 0.0, "B"),
    "R16": (104.35, 86.50, 0.0, "B"),
    # --- Block 6: Inverter & LED Driver (B.Cu) ---
    "R17": (125.50, 69.00, 0.0, "B"),
    "R18": (125.50, 71.70, 0.0, "B"),
    "R20": (125.50, 74.40, 0.0, "B"),
    "R21": (125.50, 77.10, 0.0, "B"),
    "R22": (125.50, 79.80, 0.0, "B"),
    "R23": (123.50, 92.60, 0.0, "B"),
    "R19": (126.50, 104.00, 0.0, "B"),
}


def parse_netlist_metadata(net_path: pathlib.Path) -> dict[str, dict]:
    """Extract custom BOM fields and sheetpaths for each component in the netlist."""
    parsed = simp_sexp.Sexp(net_path.read_text(encoding="utf-8"))
    meta: dict[str, dict] = {}
    for comp in parsed.search("export/components/comp"):
        ref = ""
        fields: dict[str, str] = {}
        sheet_name = "/"
        sheet_tstamp = ""
        comp_tstamp = ""
        for item in comp[1:]:
            if not isinstance(item, list) or not item:
                continue
            tag = str(item[0])
            if tag == "ref" and len(item) >= 2:
                ref = str(item[1])
            elif tag == "description" and len(item) >= 2:
                fields.setdefault("Description", str(item[1]))
            elif tag == "fields":
                for fld in item[1:]:
                    if not isinstance(fld, list) or not fld or fld[0] != "field":
                        continue
                    fname = ""
                    for sub in fld[1:]:
                        if isinstance(sub, list) and len(sub) >= 2 and sub[0] == "name":
                            fname = str(sub[1])
                    if fname and len(fld) >= 3 and isinstance(fld[2], str) and fld[2]:
                        fields[fname] = fld[2]
            elif tag == "sheetpath":
                for sub in item[1:]:
                    if isinstance(sub, list) and len(sub) >= 2:
                        if sub[0] == "names":
                            sheet_name = str(sub[1])
                        elif sub[0] == "tstamps":
                            sheet_tstamp = str(sub[1])
            elif tag == "tstamps" and len(item) >= 2:
                comp_tstamp = str(item[1])
        if not ref:
            continue
        meta[ref] = {
            "fields": fields,
            "sheet_path": f"{sheet_tstamp}{comp_tstamp}"
            if sheet_tstamp and comp_tstamp
            else "",
            "sheet_name": sheet_name,
        }
    return meta


def add_board_outline(brd: pcbnew.BOARD) -> None:
    """Create the 6 HP Edge.Cuts rectangular outline and set board origins."""
    outline = pcbnew.PCB_SHAPE(brd)
    outline.SetShape(pcbnew.SHAPE_T_RECT)
    outline.SetLayer(pcbnew.Edge_Cuts)
    outline.SetStart(
        pcbnew.VECTOR2I(pcbnew.FromMM(BOARD_MIN_X), pcbnew.FromMM(BOARD_MIN_Y))
    )
    outline.SetEnd(
        pcbnew.VECTOR2I(pcbnew.FromMM(BOARD_MAX_X), pcbnew.FromMM(BOARD_MAX_Y))
    )
    outline.SetWidth(pcbnew.FromMM(0.05))
    brd.Add(outline)

    ds = brd.GetDesignSettings()
    origin = pcbnew.VECTOR2I(pcbnew.FromMM(BOARD_MIN_X), pcbnew.FromMM(BOARD_MIN_Y))
    ds.SetGridOrigin(origin)
    ds.SetAuxOrigin(origin)


def add_rear_silkscreen(brd: pcbnew.BOARD) -> None:
    """Add rear power polarity and module title labels on B.SilkS."""
    labels = [
        ("+12V", 115.00, 102.70, 0.8, 0.13),
        ("-12V RED", 115.00, 125.70, 0.8, 0.13),
        ("ENV FOLLOWER 6HP", 115.00, 22.80, 1.0, 0.15),
    ]
    for text, x_mm, y_mm, size_mm, thick_mm in labels:
        item = pcbnew.PCB_TEXT(brd)
        item.SetText(text)
        item.SetLayer(pcbnew.B_SilkS)
        item.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm)))
        item.SetMirrored(True)
        item.SetTextSize(
            pcbnew.VECTOR2I(pcbnew.FromMM(size_mm), pcbnew.FromMM(size_mm))
        )
        item.SetTextThickness(pcbnew.FromMM(thick_mm))
        brd.Add(item)


def configure_netclasses(brd: pcbnew.BOARD) -> None:
    """Define the Power netclass (0.6 mm width, 0.25 mm clearance) for power rails."""
    ns = brd.GetDesignSettings().m_NetSettings
    pwr_nc = pcbnew.NETCLASS("Power")
    pwr_nc.SetTrackWidth(pcbnew.FromMM(0.6))
    pwr_nc.SetClearance(pcbnew.FromMM(0.25))
    pwr_nc.SetViaDiameter(pcbnew.FromMM(0.8))
    pwr_nc.SetViaDrill(pcbnew.FromMM(0.4))
    ns.SetNetclass("Power", pwr_nc)
    for rail in ("+12V_RAW", "-12V_RAW", "+12V", "-12V", "GND"):
        ns.SetNetclassPatternAssignment(rail, "Power")


def generate_pcb(
    net_path: pathlib.Path = REPO_DIR / "envelope_follower.net",
    pcb_path: pathlib.Path = REPO_DIR / "EnvelopeFollower.kicad_pcb",
) -> None:
    """Generate and populate EnvelopeFollower.kicad_pcb from envelope_follower.net."""
    kinet2pcb.kinet2pcb(str(net_path), str(pcb_path), [KICAD_FP_DIR])

    brd = pcbnew.LoadBoard(str(pcb_path))
    metadata = parse_netlist_metadata(net_path)

    placed_refs = set()
    for fp in brd.GetFootprints():
        ref = fp.GetReference()
        if ref not in COMPONENT_PLACEMENTS:
            raise ValueError(f"Missing placement coordinates for component {ref!r}")
        placed_refs.add(ref)

        x_mm, y_mm, rot_deg, side = COMPONENT_PLACEMENTS[ref]

        # Reset placement at origin before flipping so side & orientation are exact.
        fp.SetPosition(pcbnew.VECTOR2I(0, 0))
        if side == "B" and not fp.IsFlipped() or side == "F" and fp.IsFlipped():
            fp.Flip(pcbnew.VECTOR2I(0, 0), False)

        fp.SetOrientationDegrees(rot_deg)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm)))

        # Apply netlist custom fields (LCSC, MPN, JLCPCB_Class, Notes, etc.).
        comp_meta = metadata.get(ref, {})
        for key, val in comp_meta.get("fields", {}).items():
            if key in ("Footprint", "SKiDL Tag", "SKiDL Line"):
                continue
            fp.SetField(key, val)
        for fld in fp.GetFields():
            if fld.GetName() not in ("Reference", "Value"):
                fld.SetVisible(False)
        if comp_meta.get("sheet_path"):
            fp.SetPath(pcbnew.KIID_PATH(comp_meta["sheet_path"]))

        # Keep component reference text clean inside Fab or clear of adjacent pads
        # to avoid silkscreen-over-pad clutter and DRC silkscreen warnings.
        if ref == "J_PWR":
            fp.Reference().SetPosition(
                pcbnew.VECTOR2I(pcbnew.FromMM(115.00), pcbnew.FromMM(101.20))
            )
            fp.Reference().SetTextSize(
                pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8))
            )
            fp.Reference().SetTextThickness(pcbnew.FromMM(0.13))
        elif ref == "J_INV_OUT":
            fp.Reference().SetPosition(
                pcbnew.VECTOR2I(pcbnew.FromMM(124.80), pcbnew.FromMM(107.60))
            )
            fp.Reference().SetTextSize(
                pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8))
            )
            fp.Reference().SetTextThickness(pcbnew.FromMM(0.13))
        elif side == "B" and ref not in ("U1", "U2"):
            fp.Reference().SetLayer(pcbnew.B_Fab)
            fp.Reference().SetTextSize(
                pcbnew.VECTOR2I(pcbnew.FromMM(0.6), pcbnew.FromMM(0.6))
            )
            fp.Reference().SetTextThickness(pcbnew.FromMM(0.1))

    missing = set(COMPONENT_PLACEMENTS) - placed_refs
    if missing:
        raise RuntimeError(
            f"Placement table has references not in netlist: {sorted(missing)}"
        )

    add_board_outline(brd)
    add_rear_silkscreen(brd)
    configure_netclasses(brd)

    brd.BuildListOfNets()
    brd.GetConnectivity().RecalculateRatsnest()
    pcbnew.SaveBoard(str(pcb_path), brd)
    print(
        f"Generated {pcb_path.name}: {len(placed_refs)} footprints, "
        f"{brd.GetNetCount() - 1} nets, outline "
        f"{BOARD_MAX_X - BOARD_MIN_X:.2f} x {BOARD_MAX_Y - BOARD_MIN_Y:.2f} mm."
    )


if __name__ == "__main__":
    generate_pcb()
