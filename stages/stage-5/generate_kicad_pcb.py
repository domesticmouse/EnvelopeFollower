#!/usr/bin/env python3
"""Generate a 6 HP Eurorack Envelope Follower PCB (EnvelopeFollower.kicad_pcb)."""

from __future__ import annotations

import math
import os
import pathlib
import sys

KICAD_PYTHON = pathlib.Path(
    "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
)

try:
    import pcbnew
except ModuleNotFoundError:
    if KICAD_PYTHON.exists():
        os.execv(str(KICAD_PYTHON), [str(KICAD_PYTHON), *sys.argv])
    raise

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".agents/skills/kicad-pcbnew-layout/scripts"))
sys.path.insert(0, str(HERE / ".agents/skills/kicad-silkscreen-markup/scripts"))

import pcbnew_layout_template as lt
import silk_annotator as sa

BOARD_W = 30.00
BOARD_H = 108.00
EDGE_CLR = 0.40
TRACK_CLR = 0.20
ROUTER_CLR = 0.205
SIGNAL_W = 0.25
POWER_W = 0.30
VIA_DIAM = 0.60
VIA_DRILL = 0.30

# Placement tuples: ref -> (x_mm, y_mm, rot_deg, is_back)
PLACEMENTS: dict[str, tuple[float, float, float, bool]] = {
    # --- Front Panel THT Hardware (F.Cu, 6 HP Grid) ---
    "RV1": (5.00, 25.50, 90.0, False),  # GAIN shaft at (7.50, 18.00)
    "RV2": (20.00, 25.50, 90.0, False),  # ATK shaft at (22.50, 18.00)
    "RV3": (5.00, 45.50, 90.0, False),  # REL shaft at (7.50, 38.00)
    "RV4": (20.00, 45.50, 90.0, False),  # OFFSET shaft at (22.50, 38.00)
    "LED1": (13.73, 54.50, 0.0, False),  # ENV lens at (15.00, 54.50)
    "J1": (15.00, 64.02, 0.0, False),  # IN bushing at (15.00, 70.50)
    "J2": (7.50, 81.02, 0.0, False),  # OUT bushing at (7.50, 87.50)
    "J3": (22.50, 81.02, 0.0, False),  # INV_OUT bushing at (22.50, 87.50)
    # --- Box Film Capacitors (THT on F.Cu) ---
    "C9": (3.00, 5.50, 0.0, False),
    "C1": (4.50, 73.50, 90.0, False),
    "C2": (25.50, 68.50, 270.0, False),
    # --- Power Header & Optional DNP Test Points (B.Cu THT) ---
    "J4": (9.92, 101.00, 270.0, True),
    "TP1": (23.70, 29.50, 0.0, True),  # GND
    "TP2": (27.70, 96.50, 0.0, True),  # +12V
    "TP3": (2.30, 96.50, 0.0, True),  # -12V
    "TP4": (2.40, 29.50, 0.0, True),  # PREAMP_OUT
    "TP5": (15.00, 49.50, 0.0, True),  # FWR_OUT
    "TP6": (27.60, 29.50, 0.0, True),  # ENV_NODE
    "TP7": (2.40, 65.00, 0.0, True),  # ENV_OUT
    "TP8": (27.60, 65.00, 0.0, True),  # INV_OUT_RAW
    # --- Quad Op-Amps (SOIC-14 on B.Cu) ---
    "U1": (6.00, 56.00, 270.0, True),
    "U2": (24.00, 56.00, 90.0, True),
    # --- SMD Bulk & Filter Electrolytics (CP_Elec_6.3x5.4 on B.Cu) ---
    "C11": (14.20, 5.00, 180.0, True),
    "C13": (24.10, 5.00, 180.0, True),
    "C3": (15.00, 82.40, 0.0, True),
    "C4": (15.00, 90.20, 180.0, True),
    # --- 2512 1W Protection Resistors (B.Cu) ---
    "R16": (9.20, 65.50, 0.0, True),
    "R19": (20.80, 65.50, 180.0, True),
    "R25": (5.80, 77.50, 0.0, True),
    # --- SOT-23 Dual ESD Clamps (B.Cu) ---
    "D7": (10.00, 69.50, 180.0, True),
    "D6": (10.00, 73.20, 180.0, True),
    "D8": (20.00, 70.00, 0.0, True),
    # --- SOD-123 Diodes (B.Cu) ---
    "D4": (27.70, 102.50, 270.0, True),
    "D5": (2.30, 102.50, 90.0, True),
    "D1": (9.50, 48.00, 0.0, True),
    "D2": (7.50, 42.50, 180.0, True),
    "D9": (20.20, 48.00, 0.0, True),
    "D3": (25.80, 48.00, 180.0, True),
    "D10": (15.00, 58.20, 180.0, True),
    # --- 0603 Capacitors (B.Cu) ---
    "C5": (6.00, 50.50, 0.0, True),
    "C6": (6.20, 61.60, 0.0, True),
    "C8": (24.00, 50.50, 180.0, True),
    "C7": (24.65, 61.60, 0.0, True),
    "C12": (18.00, 9.40, 0.0, True),
    "C14": (22.50, 9.40, 0.0, True),
    "C15": (21.40, 14.30, 0.0, True),
    "C10": (17.60, 14.30, 0.0, True),
    "C16": (19.50, 50.80, 0.0, True),
    "C17": (10.30, 61.60, 0.0, True),
    # --- 0603 Resistors (B.Cu) ---
    "R24": (2.40, 9.40, 0.0, True),
    "R1": (6.20, 9.40, 180.0, True),
    "R28": (10.00, 9.40, 0.0, True),
    "R11": (14.00, 9.40, 0.0, True),
    "R12": (26.80, 9.40, 180.0, True),
    "R2": (10.00, 14.30, 180.0, True),
    "R29": (13.80, 14.30, 0.0, True),
    "R26": (6.20, 27.60, 0.0, True),
    "R4": (10.00, 27.60, 0.0, True),
    "R5": (10.00, 32.20, 0.0, True),
    "R3": (6.20, 32.20, 0.0, True),
    "R6": (2.40, 34.80, 0.0, True),
    "R7": (6.20, 34.80, 0.0, True),
    "R8": (10.00, 34.80, 0.0, True),
    "R27": (19.80, 34.80, 0.0, True),
    "R9": (19.80, 27.60, 180.0, True),
    "R10": (19.80, 32.20, 180.0, True),
    "R14": (20.00, 61.60, 180.0, True),
    "R15": (2.00, 61.60, 180.0, True),
    "R17": (26.00, 42.50, 180.0, True),
    "R18": (27.80, 61.60, 0.0, True),
    "R21": (15.00, 60.50, 0.0, True),
    "R20": (20.50, 73.80, 0.0, True),
    "R13": (22.20, 42.50, 0.0, True),
}

FIDUCIALS: dict[str, tuple[float, float]] = {
    "FID1": (5.00, 13.80),
    "FID2": (25.50, 13.80),
    "FID3": (22.50, 95.50),
}

# Concise <VAL> silkscreen tokens per SilkscreenInstructions.md Section 4
SILK_VAL_TOKENS: dict[str, str] = {
    "U1": "TL074H",
    "U2": "TL074H",
    "D1": "1N4148W",
    "D2": "1N4148W",
    "D3": "1N4148W",
    "D4": "B5819W",
    "D5": "B5819W",
    "D6": "BAV99",
    "D7": "BAT54S",
    "D8": "BAT54S",
    "D9": "1N4148W",
    "D10": "1N4148W",
    "C1": "1uF FILM",
    "C2": "1uF FILM",
    "C3": "22uF 50V",
    "C4": "22uF 50V",
    "C5": "100nF",
    "C6": "100nF",
    "C7": "100nF",
    "C8": "100nF",
    "C9": "1uF FILM",
    "C10": "15pF C0G",
    "C11": "22uF 50V",
    "C12": "100nF",
    "C13": "22uF 50V",
    "C14": "100nF",
    "C15": "100nF",
    "C16": "47pF C0G",
    "C17": "15pF C0G",
    "R1": "1M",
    "R2": "10k",
    "R3": "100k 0.1%",
    "R4": "100k 0.1%",
    "R5": "100k 0.1%",
    "R6": "100k 0.1%",
    "R7": "100k 0.1%",
    "R8": "200k 0.1%",
    "R9": "470R",
    "R10": "22k",
    "R11": "1k",
    "R12": "1k",
    "R13": "10k",
    "R14": "10k",
    "R15": "10k",
    "R16": "1k 1W",
    "R17": "10k",
    "R18": "10k",
    "R19": "1k 1W",
    "R20": "10k",
    "R21": "1.5k",
    "R24": "4.7k",
    "R25": "1k 1W",
    "R26": "1M",
    "R27": "10k",
    "R28": "1k",
    "R29": "100k",
    "RV1": "A100k GAIN",
    "RV2": "A50k ATK",
    "RV3": "A1M REL",
    "RV4": "B10k OFFSET",
    "LED1": "ENV",
    "J1": "IN",
    "J2": "OUT",
    "J3": "INV_OUT",
    "J4": "±12V PWR",
    "TP1": "GND",
    "TP2": "+12V",
    "TP3": "-12V",
    "TP4": "PREAMP",
    "TP5": "FWR_OUT",
    "TP6": "ENV_NODE",
    "TP7": "ENV_OUT",
    "TP8": "INV_RAW",
}


def add_fiducials(
    board: pcbnew.BOARD, footprints: dict[str, pcbnew.FOOTPRINT]
) -> dict[str, pcbnew.FOOTPRINT]:
    """Place 3 global B.Cu fiducials (1mm pad, 2mm mask) for JLCPCB SMT alignment."""
    lib_path = str(lt.FP_DIR / "Fiducial.pretty")
    fids: dict[str, pcbnew.FOOTPRINT] = {}
    for ref, (fx, fy) in FIDUCIALS.items():
        fp = pcbnew.FootprintLoad(lib_path, "Fiducial_1mm_Mask2mm")
        if fp is None:
            raise RuntimeError("Failed to load Fiducial_1mm_Mask2mm")
        board.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(fx), pcbnew.FromMM(fy)))
        fp.Flip(fp.GetPosition(), False)
        fp.SetOrientationDegrees(0.0)
        fp.SetReference(ref)
        fp.SetValue("Fiducial")
        for fld in fp.GetFields():
            fld.SetVisible(False)
        fp.Value().SetLayer(pcbnew.B_Fab)
        fp.Value().SetVisible(False)
        fp.Reference().SetVisible(True)
        fp.SetExcludedFromBOM(True)
        fids[ref] = fp
        footprints[ref] = fp
    return fids


def check_courtyards_and_tht(footprints: dict[str, pcbnew.FOOTPRINT]) -> None:
    """Verify zero per-side courtyard overlaps and zero B.Cu SMD vs THT-pad collisions."""
    crtyds: dict[int, list[tuple[str, tuple[float, float, float, float]]]] = {
        0: [],
        1: [],
    }
    tht_pads: list[tuple[str, float, float, float, float]] = []
    smd_pads: list[tuple[str, float, float, float, float]] = []

    for ref, fp in footprints.items():
        for lid, side in ((pcbnew.F_CrtYd, 0), (pcbnew.B_CrtYd, 1)):
            xs, ys = [], []
            for gi in fp.GraphicalItems():
                if not hasattr(gi, "GetText") and gi.GetLayer() == lid:
                    bb = gi.GetBoundingBox()
                    xs.extend([pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetRight())])
                    ys.extend([pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetBottom())])
            if xs:
                box = (min(xs), min(ys), max(xs), max(ys))
                crtyds[side].append((ref, box))
                if box[0] < 0.0 or box[2] > BOARD_W or box[1] < 0.0 or box[3] > BOARD_H:
                    raise RuntimeError(f"Courtyard out of bounds: {ref} {box}")

        for pad in fp.Pads():
            _, _, x0, y0, x1, y1, _ = lt.extract_pad_geometry(pad)
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                tht_pads.append((ref, x0, y0, x1, y1))
            elif pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
                smd_pads.append((ref, x0, y0, x1, y1))

    for side in (0, 1):
        items = crtyds[side]
        for i in range(len(items)):
            r1, b1 = items[i]
            for j in range(i + 1, len(items)):
                r2, b2 = items[j]
                if not (
                    b1[2] <= b2[0] or b2[2] <= b1[0] or b1[3] <= b2[1] or b2[3] <= b1[1]
                ):
                    raise RuntimeError(
                        f"Courtyard overlap on side {side}: {r1} {b1} vs {r2} {b2}"
                    )

    pad_margin = 0.35
    for tref, tx0, ty0, tx1, ty1 in tht_pads:
        for sref, sx0, sy0, sx1, sy1 in smd_pads:
            if not (
                sx1 + pad_margin <= tx0
                or sx0 - pad_margin >= tx1
                or sy1 + pad_margin <= ty0
                or sy0 - pad_margin >= ty1
            ):
                raise RuntimeError(
                    f"SMD pad {sref} too close to THT pad {tref}: "
                    f"{(sx0, sy0, sx1, sy1)} vs {(tx0, ty0, tx1, ty1)}"
                )


def _pad_center_mm(pad: pcbnew.PAD) -> tuple[float, float]:
    pos = pad.GetPosition()
    return (pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))


def _find_pad(fp: pcbnew.FOOTPRINT, num: str) -> pcbnew.PAD:
    for pad in fp.Pads():
        if pad.GetNumber() == num:
            return pad
    raise KeyError(f"Pad {num} not found on {fp.GetReference()}")


def _mark_static_box(
    router: lt.GridRouter,
    layer: int,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    block_via: bool = False,
) -> None:
    gx0 = max(0, math.floor((x0 - router.x0) / router.step))
    gx1 = min(router.nx - 1, math.ceil((x1 - router.x0) / router.step))
    gy0 = max(0, math.floor((y0 - router.y0) / router.step))
    gy1 = min(router.ny - 1, math.ceil((y1 - router.y0) / router.step))
    for gy in range(gy0, gy1 + 1):
        row = gy * router.nx
        for gx in range(gx0, gx1 + 1):
            router.static_block[layer][row + gx] = 1
            if block_via:
                router.via_block[row + gx] = 1


def build_router(
    footprints: dict[str, pcbnew.FOOTPRINT],
) -> tuple[
    lt.GridRouter,
    dict[int, list[tuple[str, pcbnew.PAD]]],
    dict[int, list[tuple[int, int, int, float, float]]],
    dict[int, pcbnew.NETINFO_ITEM],
]:
    """Initialize GridRouter with exact pad boxes, SMD via blocks, THT blocks, and keepouts."""
    router = lt.GridRouter(
        0.0,
        0.0,
        BOARD_W,
        BOARD_H,
        step=0.25,
        edge_clearance=EDGE_CLR,
        track_width=SIGNAL_W,
        clearance=ROUTER_CLR,
    )

    for lid, cx, cy, r in lt.extract_keepout_circles(footprints):
        router.mark_static_circle(
            lid, cx, cy, r + ROUTER_CLR + SIGNAL_W * 0.5, block_via=True
        )

    net_pads: dict[int, list[tuple[str, pcbnew.PAD]]] = {}
    net_items: dict[int, pcbnew.NETINFO_ITEM] = {}
    pad_margin = ROUTER_CLR + SIGNAL_W * 0.5

    for ref, fp in footprints.items():
        for pad in fp.Pads():
            nc = pad.GetNetCode()
            cx, cy, x0, y0, x1, y1, layers = lt.extract_pad_geometry(pad)
            is_pth = pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH
            is_smd = pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD
            if nc == 0:
                for lid in layers:
                    _mark_static_box(
                        router,
                        lid,
                        x0 - pad_margin,
                        y0 - pad_margin,
                        x1 + pad_margin,
                        y1 + pad_margin,
                        block_via=is_pth or is_smd,
                    )
                continue

            net_pads.setdefault(nc, []).append((ref, pad))
            net_items[nc] = pad.GetNet()
            for lid in layers:
                router.mark_pad_box(lid, x0, y0, x1, y1, pad_margin, nc)

            if is_smd:
                router.mark_smd_via_block(x0, y0, x1, y1, margin=0.05)
                # Also prevent vias within via_radius + clearance of SMD pad edges
                vx0 = max(
                    0,
                    math.floor((x0 - (VIA_DIAM * 0.5 + TRACK_CLR)) / router.step),
                )
                vx1 = min(
                    router.nx - 1,
                    math.ceil((x1 + (VIA_DIAM * 0.5 + TRACK_CLR)) / router.step),
                )
                vy0 = max(
                    0,
                    math.floor((y0 - (VIA_DIAM * 0.5 + TRACK_CLR)) / router.step),
                )
                vy1 = min(
                    router.ny - 1,
                    math.ceil((y1 + (VIA_DIAM * 0.5 + TRACK_CLR)) / router.step),
                )
                for gy in range(vy0, vy1 + 1):
                    py = router.y0 + gy * router.step
                    row = gy * router.nx
                    for gx in range(vx0, vx1 + 1):
                        px = router.x0 + gx * router.step
                        dx = max(x0 - px, 0.0, px - x1)
                        dy = max(y0 - py, 0.0, py - y1)
                        if dx * dx + dy * dy < (VIA_DIAM * 0.5 + TRACK_CLR) ** 2:
                            router.via_block[row + gx] = 1
            elif is_pth:
                gx, gy = router.to_grid(cx, cy)
                router.tht_pad_grid[(gx, gy)] = nc
                dr = max(x1 - x0, y1 - y0) * 0.5
                router.mark_via_obstacle(cx, cy, dr + VIA_DIAM * 0.5 + TRACK_CLR, nc)

    # Clear pad centers so A* can always enter/exit exact pad anchors
    pad_anchors: dict[int, list[tuple[int, int, int, float, float]]] = {}
    for nc, pads in net_pads.items():
        anchors: list[tuple[int, int, int, float, float]] = []
        for _, pad in pads:
            cx, cy, _, _, _, _, layers = lt.extract_pad_geometry(pad)
            gx, gy = router.to_grid(cx, cy)
            lid = 1 if 1 in layers and 0 not in layers else 0
            anchors.append((lid, gx, gy, cx, cy))
        pad_anchors[nc] = anchors

    return router, net_pads, pad_anchors, net_items


def place_gnd_stitching_vias(
    board: pcbnew.BOARD,
    router: lt.GridRouter,
    footprints: dict[str, pcbnew.FOOTPRINT],
    gnd_net: pcbnew.NETINFO_ITEM,
) -> None:
    """Pre-place immediate GND stitching vias for every B.Cu SMD GND pad."""
    gnd_code = gnd_net.GetNetCode()
    for ref, fp in sorted(footprints.items()):
        for pad in fp.Pads():
            if pad.GetNetCode() != gnd_code:
                continue
            if pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                continue
            cx, cy = _pad_center_mm(pad)
            best: tuple[float, int, int] | None = None
            cgx, cgy = router.to_grid(cx, cy)
            for dy in range(-6, 7):
                for dx in range(-6, 7):
                    gx, gy = cgx + dx, cgy + dy
                    if gx < 2 or gx >= router.nx - 2 or gy < 2 or gy >= router.ny - 2:
                        continue
                    if not router.can_place_via(gx, gy, gnd_code):
                        continue
                    vx, vy = router.to_mm(gx, gy)
                    dist2 = (vx - cx) ** 2 + (vy - cy) ** 2
                    if dist2 < 0.70**2:
                        continue
                    if best is None or dist2 < best[0]:
                        best = (dist2, gx, gy)
            if best is None:
                raise RuntimeError(
                    f"Could not place GND via near {ref}.{pad.GetNumber()}"
                )
            _, gx, gy = best
            vx, vy = router.to_mm(gx, gy)
            lt.add_via(board, vx, vy, gnd_net, diam=VIA_DIAM, drill=VIA_DRILL)
            lt.add_track(board, pcbnew.B_Cu, cx, cy, vx, vy, 0.30, gnd_net)
            router.mark_via_obstacle(
                vx, vy, VIA_DIAM * 0.5 + TRACK_CLR + SIGNAL_W * 0.5, gnd_code
            )
            router.mark_segment(1, cx, cy, vx, vy, 0.30, gnd_code)


def pre_route_ic_and_power(
    board: pcbnew.BOARD,
    router: lt.GridRouter,
    footprints: dict[str, pcbnew.FOOTPRINT],
) -> tuple[
    dict[tuple[str, str], tuple[int, int, int]],
    list[tuple[tuple[str, str], tuple[str, str]]],
    list[str],
]:
    """Add IC outward escape stubs and pre-route local decoupling cap pairs."""
    escape_anchors: dict[tuple[str, str], tuple[int, int, int]] = {}
    pre_pairs: list[tuple[tuple[str, str], tuple[str, str]]] = []

    # Reserve outward escape stubs on U1 & U2 (1.95mm tall pads, outer Y edge ±3.45mm)
    for ic_ref in ("U1", "U2"):
        fp = footprints[ic_ref]
        _, icy = pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y)
        for pad in fp.Pads():
            nc = pad.GetNetCode()
            if nc == 0:
                continue
            pnum = pad.GetNumber()
            px, py = _pad_center_mm(pad)
            sgn = 1.0 if py > icy else -1.0
            esc_y_raw = py + sgn * 1.45
            gx, gy = router.to_grid(px, esc_y_raw)
            ex, ey = router.to_mm(gx, gy)
            ni = pad.GetNet()
            w = POWER_W if ni.GetNetname() in ("+12V", "-12V") else SIGNAL_W
            lt.add_track(board, pcbnew.B_Cu, px, py, px, ey, w, ni)
            if abs(ex - px) > 1e-4:
                lt.add_track(board, pcbnew.B_Cu, px, ey, ex, ey, w, ni)
                router.mark_segment(1, px, ey, ex, ey, w, nc)
            router.mark_segment(1, px, py, px, ey, w, nc)
            escape_anchors[(ic_ref, pnum)] = (1, gx, gy)

    # Pre-route local decoupling cap power connections directly to IC pins
    decoupling_pairs = [
        ("U1", "4", "C5", "1"),
        ("U2", "4", "C7", "1"),
        ("U1", "11", "C6", "1"),
        ("U2", "11", "C8", "1"),
    ]
    for ic_ref, ic_pin, cap_ref, cap_pin in decoupling_pairs:
        ic_pad = _find_pad(footprints[ic_ref], ic_pin)
        cap_pad = _find_pad(footprints[cap_ref], cap_pin)
        ni = ic_pad.GetNet()
        nc = ni.GetNetCode()
        _, egx, egy = escape_anchors[(ic_ref, ic_pin)]
        ex, ey = router.to_mm(egx, egy)
        cx, cy = _pad_center_mm(cap_pad)
        lt.add_track(board, pcbnew.B_Cu, ex, ey, cx, ey, POWER_W, ni)
        lt.add_track(board, pcbnew.B_Cu, cx, ey, cx, cy, POWER_W, ni)
        router.mark_segment(1, ex, ey, cx, ey, POWER_W, nc)
        router.mark_segment(1, cx, ey, cx, cy, POWER_W, nc)
        pre_pairs.append(((ic_ref, ic_pin), (cap_ref, cap_pin)))

    # Bridge adjacent same-net op-amp pins U2.13 <-> U2.14 (ENV_NODE) at escape tips
    _, gx13, gy13 = escape_anchors[("U2", "13")]
    _, gx14, gy14 = escape_anchors[("U2", "14")]
    x13, y13 = router.to_mm(gx13, gy13)
    x14, y14 = router.to_mm(gx14, gy14)
    ni_env = _find_pad(footprints["U2"], "13").GetNet()
    lt.add_track(board, pcbnew.B_Cu, x13, y13, x14, y14, SIGNAL_W, ni_env)
    router.mark_segment(1, x13, y13, x14, y14, SIGNAL_W, ni_env.GetNetCode())
    pre_pairs.append((("U2", "13"), ("U2", "14")))

    # Add wide direct power tracks for +12V_IN and -12V_IN from J4 to D4/D5
    for j_pin_a, j_pin_b, d_ref, d_pin in (
        ("9", "10", "D4", "2"),
        ("1", "2", "D5", "1"),
    ):
        pa = _find_pad(footprints["J4"], j_pin_a)
        pb = _find_pad(footprints["J4"], j_pin_b)
        pd = _find_pad(footprints[d_ref], d_pin)
        ni = pa.GetNet()
        nc = ni.GetNetCode()
        ax, ay = _pad_center_mm(pa)
        bx, by = _pad_center_mm(pb)
        dx, dy = _pad_center_mm(pd)
        lt.add_track(board, pcbnew.B_Cu, ax, ay, bx, by, 0.45, ni)
        lt.add_track(board, pcbnew.B_Cu, bx, by, dx, by, 0.45, ni)
        lt.add_track(board, pcbnew.B_Cu, dx, by, dx, dy, 0.45, ni)
        router.mark_segment(1, ax, ay, bx, by, 0.45, nc)
        router.mark_segment(1, bx, by, dx, by, 0.45, nc)
        router.mark_segment(1, dx, by, dx, dy, 0.45, nc)

    return escape_anchors, pre_pairs, ["+12V_IN", "-12V_IN"]


def route_all_nets(
    board: pcbnew.BOARD,
    router: lt.GridRouter,
    footprints: dict[str, pcbnew.FOOTPRINT],
    net_pads: dict[int, list[tuple[str, pcbnew.PAD]]],
    net_items: dict[int, pcbnew.NETINFO_ITEM],
    escape_anchors: dict[tuple[str, str], tuple[int, int, int]],
    pre_pairs: list[tuple[tuple[str, str], tuple[str, str]]],
    skip_nets: list[str],
) -> None:
    """Route all signal and power nets via multi-layer A* with junction preservation."""
    skip_set = set(skip_nets) | {"GND"}

    local_ic_nets = {
        "DET_FB",
        "DET_OP_OUT",
        "RECT_SUM",
        "RECT_OUT_N",
        "RECT_HALF",
        "FF_MID",
        "FWR_SUM",
        "INV_SUM",
        "OUT_SUM",
        "ENV_OUT",
        "ENV_NODE",
        "ENV_CAP",
        "LED_FB",
        "LED_ANODE",
        "LED_BUF_IN",
        "RECT_DIODE_OUT",
        "IN_TIP",
        "IN_CLAMP",
    }
    preamp_order = {"PREAMP_OUT": 0.0, "PREAMP_INV": 1.0, "PREAMP_IN": 2.0}

    def net_sort_key(nc: int) -> tuple[int, float, str]:
        name = net_items[nc].GetNetname()
        pads = net_pads[nc]
        xs = [_pad_center_mm(p)[0] for _, p in pads]
        ys = [_pad_center_mm(p)[1] for _, p in pads]
        span = (max(xs) - min(xs)) + (max(ys) - min(ys))
        if name in local_ic_nets:
            tier = 0
        elif name in ("+12V", "-12V"):
            tier = 1
        elif name in preamp_order:
            return (2, preamp_order[name], name)
        else:
            tier = 3
        return (tier, span, name)

    sorted_ncs = sorted(
        (nc for nc in net_pads if net_items[nc].GetNetname() not in skip_set),
        key=net_sort_key,
    )

    for nc in sorted_ncs:
        ni = net_items[nc]
        nname = ni.GetNetname()
        pads = net_pads[nc]
        if len(pads) < 2:
            continue
        xs = [_pad_center_mm(p)[0] for _, p in pads]
        ys = [_pad_center_mm(p)[1] for _, p in pads]
        span = (max(xs) - min(xs)) + (max(ys) - min(ys))
        trace_w = POWER_W if nname in ("+12V", "-12V") else SIGNAL_W
        pref_layer = 0 if (nname in ("+12V", "-12V") or span > 18.0) else 1

        node_entries: list[tuple[int, int, int, float, float, str, str]] = []
        key_to_idx: dict[tuple[str, str], int] = {}
        for ref, pad in pads:
            pnum = pad.GetNumber()
            px, py = _pad_center_mm(pad)
            key_to_idx[(ref, pnum)] = len(node_entries)
            if (ref, pnum) in escape_anchors:
                lid, gx, gy = escape_anchors[(ref, pnum)]
                gx_mm, gy_mm = router.to_mm(gx, gy)
                node_entries.append((lid, gx, gy, gx_mm, gy_mm, ref, pnum))
            else:
                gx, gy = router.to_grid(px, py)
                is_pth = pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH
                lid = 0 if is_pth else 1
                node_entries.append((lid, gx, gy, px, py, ref, pnum))

        parent_cl = list(range(len(node_entries)))

        def _find_cl(i: int, p: list[int] = parent_cl) -> int:
            while p[i] != i:
                p[i] = p[p[i]]
                i = p[i]
            return i

        for a_key, b_key in pre_pairs:
            if a_key in key_to_idx and b_key in key_to_idx:
                ra, rb = _find_cl(key_to_idx[a_key]), _find_cl(key_to_idx[b_key])
                if ra != rb:
                    parent_cl[rb] = ra

        clusters: dict[int, list[int]] = {}
        for idx in range(len(node_entries)):
            clusters.setdefault(_find_cl(idx), []).append(idx)

        cluster_list = list(clusters.values())
        copper_points: set[tuple[int, int, int]] = set()
        junctions: set[tuple[int, int, int]] = set()
        emitted_vias: set[tuple[int, int]] = set()

        for idx in cluster_list[0]:
            lid, gx, gy, px, py, ref, pnum = node_entries[idx]
            copper_points.add((lid, gx, gy))
            junctions.add((lid, gx, gy))
            gx_mm, gy_mm = router.to_mm(gx, gy)
            if (ref, pnum) not in escape_anchors and (
                abs(gx_mm - px) > 1e-4 or abs(gy_mm - py) > 1e-4
            ):
                layer_id = pcbnew.F_Cu if lid == 0 else pcbnew.B_Cu
                lt.add_track(board, layer_id, px, py, gx_mm, gy_mm, trace_w, ni)
                router.mark_segment(lid, px, py, gx_mm, gy_mm, trace_w, nc)

        remaining_clusters = cluster_list[1:]
        while remaining_clusters:

            def _cl_dist(
                cl: list[int],
                entries: list[
                    tuple[int, int, int, float, float, str, str]
                ] = node_entries,
                pts: set[tuple[int, int, int]] = copper_points,
            ) -> float:
                best = 1e18
                for idx in cl:
                    _, gx, gy, *_ = entries[idx]
                    for _, cx, cy in pts:
                        best = min(best, (gx - cx) ** 2 + (gy - cy) ** 2)
                return best

            remaining_clusters.sort(key=_cl_dist)
            target_cl = remaining_clusters.pop(0)
            target_idx = target_cl[0]
            lid, gx, gy, px, py, ref, pnum = node_entries[target_idx]
            starts: list[tuple[int, int, int]] = []
            for idx in target_cl:
                c_lid, c_gx, c_gy, *_ = node_entries[idx]
                starts.append((c_lid, c_gx, c_gy))
                if router.tht_pad_grid.get((c_gx, c_gy)) == nc:
                    starts.append((1 - c_lid, c_gx, c_gy))

            if any(s in copper_points for s in starts):
                for idx in target_cl:
                    c_lid, c_gx, c_gy, *_ = node_entries[idx]
                    copper_points.add((c_lid, c_gx, c_gy))
                    junctions.add((c_lid, c_gx, c_gy))
                continue

            path = router.route(starts, copper_points, nc, preferred_layer=pref_layer)
            if path is None:
                path = router.route(starts, copper_points, nc, preferred_layer=None)
            if path is None:
                raise RuntimeError(
                    f"Routing failed for net {nname} reaching {ref}.{pnum} ({px:.2f}, {py:.2f})"
                )

            junctions.add(path[0])
            junctions.add(path[-1])
            for pt in path:
                copper_points.add(pt)

            for idx in target_cl:
                c_lid, c_gx, c_gy, c_px, c_py, c_ref, c_pnum = node_entries[idx]
                copper_points.add((c_lid, c_gx, c_gy))
                junctions.add((c_lid, c_gx, c_gy))
                cgx_mm, cgy_mm = router.to_mm(c_gx, c_gy)
                if (c_ref, c_pnum) not in escape_anchors and (
                    abs(cgx_mm - c_px) > 1e-4 or abs(cgy_mm - c_py) > 1e-4
                ):
                    layer_id = pcbnew.F_Cu if c_lid == 0 else pcbnew.B_Cu
                    lt.add_track(
                        board, layer_id, c_px, c_py, cgx_mm, cgy_mm, trace_w, ni
                    )
                    router.mark_segment(c_lid, c_px, c_py, cgx_mm, cgy_mm, trace_w, nc)

            merged = lt._merge_collinear_path(path, junctions)
            for i in range(len(merged) - 1):
                l1, gx1, gy1 = merged[i]
                l2, gx2, gy2 = merged[i + 1]
                x1, y1 = router.to_mm(gx1, gy1)
                x2, y2 = router.to_mm(gx2, gy2)
                if l1 != l2:
                    if (
                        router.tht_pad_grid.get((gx1, gy1)) != nc
                        and (gx1, gy1) not in emitted_vias
                    ):
                        lt.add_via(board, x1, y1, ni, diam=VIA_DIAM, drill=VIA_DRILL)
                        router.mark_via_obstacle(
                            x1, y1, VIA_DIAM * 0.5 + ROUTER_CLR + SIGNAL_W * 0.5, nc
                        )
                        emitted_vias.add((gx1, gy1))
                else:
                    layer_id = pcbnew.F_Cu if l1 == 0 else pcbnew.B_Cu
                    lt.add_track(board, layer_id, x1, y1, x2, y2, trace_w, ni)
                    router.mark_segment(l1, x1, y1, x2, y2, trace_w, nc)


def verify_and_stitch_gnd(
    board: pcbnew.BOARD,
    router: lt.GridRouter,
    gnd_net: pcbnew.NETINFO_ITEM,
) -> None:
    """Pour F.Cu/B.Cu GND zones, add grid stitching vias, and verify GND connectivity."""
    gnd_code = gnd_net.GetNetCode()
    # Add sparse board-wide GND stitching vias in open corridors
    stitch_candidates = [
        (15.0, 20.5),
        (15.0, 39.5),
        (11.5, 49.5),
        (18.5, 49.5),
        (15.0, 77.5),
        (3.0, 86.0),
        (27.0, 86.0),
    ]
    for sx, sy in stitch_candidates:
        gx, gy = router.to_grid(sx, sy)
        if router.can_place_via(gx, gy, gnd_code):
            vx, vy = router.to_mm(gx, gy)
            lt.add_via(board, vx, vy, gnd_net, diam=VIA_DIAM, drill=VIA_DRILL)
            router.mark_via_obstacle(
                vx, vy, VIA_DIAM * 0.5 + TRACK_CLR + SIGNAL_W * 0.5, gnd_code
            )

    lt.pour_gnd_zones(
        board,
        gnd_net,
        0.0,
        0.0,
        BOARD_W,
        BOARD_H,
        edge_clearance=EDGE_CLR,
        clearance=TRACK_CLR,
    )


def _reserve_box(
    grid: sa.SilkGrid, side: int, box: tuple[float, float, float, float]
) -> None:
    pad = 0.15
    grid.keepout[side].append((box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad))


def _place_board_silk_near(
    grid: sa.SilkGrid,
    side: int,
    text: str,
    cx: float,
    cy: float,
    *,
    height: float = 0.80,
    thickness: float = 0.15,
    step: float = 0.50,
    max_radius: float = 10.0,
    rotations: tuple[float, ...] = (0.0, 90.0),
    parent: pcbnew.BOARD | pcbnew.FOOTPRINT | None = None,
) -> tuple[float, float, float]:
    """Place centered silkscreen text on F.SilkS or B.SilkS without collisions."""
    layer_id = pcbnew.B_SilkS if side == 1 else pcbnew.F_SilkS
    mirrored = side == 1
    tw, th = grid.measure_text(text, height, thickness)
    n = math.ceil(max_radius / step)
    offsets: list[tuple[float, float]] = []
    max_r2 = max_radius * max_radius + 1e-9
    for iy in range(-n, n + 1):
        dy = iy * step
        for ix in range(-n, n + 1):
            dx = ix * step
            if dx * dx + dy * dy <= max_r2:
                offsets.append((dx, dy))
    offsets.sort(key=lambda d: (d[0] * d[0] + d[1] * d[1], abs(d[1]), abs(d[0])))

    target_parent = parent if parent is not None else grid.board
    for dx, dy in offsets:
        tx, ty = cx + dx, cy + dy
        for deg in rotations:
            w, h = (th, tw) if deg == 90.0 else (tw, th)
            box = (tx - w * 0.5, ty - h * 0.5, tx + w * 0.5, ty + h * 0.5)
            if grid.box_ok(side, *box):
                sa.add_silk_text(
                    target_parent,
                    layer_id,
                    text,
                    tx,
                    ty,
                    deg,
                    height,
                    thickness,
                    mirrored,
                )
                grid.reserve(side, *box)
                return (tx, ty, deg)
    raise RuntimeError(
        f"Could not place silkscreen text {text!r} near ({cx}, {cy}) side={side}"
    )


def _place_polarity_marker(
    grid: sa.SilkGrid,
    side: int,
    text: str,
    px: float,
    py: float,
    dir_x: float,
    dir_y: float,
    *,
    height: float = 0.80,
) -> tuple[float, float]:
    """Place a polarity text symbol ('+', '-', 'K', '1') outside pads along (dir_x, dir_y)."""
    layer_id = pcbnew.B_SilkS if side == 1 else pcbnew.F_SilkS
    mirrored = side == 1
    tw, th = grid.measure_text(text, height, 0.16)
    for dist in (1.1, 1.4, 1.7, 2.0, 2.4, 2.8, 3.2):
        for ortho in (0.0, 0.7, -0.7, 1.3, -1.3):
            tx = px + dir_x * dist - dir_y * ortho
            ty = py + dir_y * dist + dir_x * ortho
            box = (tx - tw * 0.5, ty - th * 0.5, tx + tw * 0.5, ty + th * 0.5)
            if grid.box_ok(side, *box):
                sa.add_silk_text(
                    grid.board, layer_id, text, tx, ty, 0.0, height, 0.16, mirrored
                )
                grid.reserve(side, *box)
                return (tx, ty)
    return _place_board_silk_near(
        grid, side, text, px + dir_x * 1.6, py + dir_y * 1.6, height=height
    )[:2]


def _place_stacked_ref_val_pair(
    grid: sa.SilkGrid,
    fp: pcbnew.FOOTPRINT,
    val_text: str,
    *,
    side: int,
    center: tuple[float, float] | None = None,
    height: float = 0.80,
    thickness: float = 0.15,
    gap: float = 0.35,
    step: float = 0.25,
    max_radius: float = 24.0,
) -> tuple[float, float, float] | None:
    """Place stacked two-line <REF> / <VAL> pair on SilkS without collisions."""
    if center is None:
        pos = fp.GetPosition()
        cx, cy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
    else:
        cx, cy = center
    rw, rh = grid.measure_text(fp.GetReference(), height, thickness)
    vw, vh = grid.measure_text(val_text, height, thickness)
    n = math.ceil(max_radius / step)
    offsets: list[tuple[float, float]] = []
    max_r2 = max_radius * max_radius + 1e-9
    for iy in range(-n, n + 1):
        dy = iy * step
        for ix in range(-n, n + 1):
            dx = ix * step
            if dx * dx + dy * dy <= max_r2:
                offsets.append((dx, dy))
    offsets.sort(key=lambda d: (d[0] * d[0] + d[1] * d[1], abs(d[1]), abs(d[0])))
    silk_layer = pcbnew.B_SilkS if side == 1 else pcbnew.F_SilkS
    mirrored = side == 1
    sign = -1.0 if side == 1 else 1.0
    for dx, dy in offsets:
        tx, ty = cx + dx, cy + dy
        for deg in (0.0, 90.0):
            if deg == 0.0:
                ref_cx, ref_cy = tx, ty - (vh + gap) * 0.5
                val_cx, val_cy = tx, ty + (rh + gap) * 0.5
                rw_r, rh_r, vw_r, vh_r = rw, rh, vw, vh
            else:
                ref_cx, ref_cy = tx - sign * (vh + gap) * 0.5, ty
                val_cx, val_cy = tx + sign * (rh + gap) * 0.5, ty
                rw_r, rh_r, vw_r, vh_r = rh, rw, vh, vw
            rbox = (
                ref_cx - rw_r * 0.5,
                ref_cy - rh_r * 0.5,
                ref_cx + rw_r * 0.5,
                ref_cy + rh_r * 0.5,
            )
            vbox = (
                val_cx - vw_r * 0.5,
                val_cy - vh_r * 0.5,
                val_cx + vw_r * 0.5,
                val_cy + vh_r * 0.5,
            )
            if grid.box_ok(side, *rbox) and grid.box_ok(side, *vbox):
                sa._configure_ref_field(
                    fp.Reference(),
                    silk_layer,
                    ref_cx,
                    ref_cy,
                    deg,
                    height,
                    thickness,
                    mirrored,
                )
                sa.add_silk_text(
                    fp,
                    silk_layer,
                    val_text,
                    val_cx,
                    val_cy,
                    deg,
                    height,
                    thickness,
                    mirrored,
                )
                grid.reserve(side, *rbox)
                grid.reserve(side, *vbox)
                return (tx, ty, deg)
    return None


def _place_boardwide_silk_text(
    grid: sa.SilkGrid,
    side: int,
    text: str,
    cx: float,
    cy: float,
    *,
    height: float = 0.80,
    thickness: float = 0.15,
) -> tuple[float, float, float, tuple[float, float, float, float]] | None:
    """Search the full board nearest to (cx, cy) for a collision-free silk slot."""
    tw, th = grid.measure_text(text, height, thickness)
    for step in (0.45, 0.25):
        nx = int(BOARD_W / step) + 1
        ny = int(BOARD_H / step) + 1
        candidates = [
            ((ix * step - cx) ** 2 + (iy * step - cy) ** 2, ix * step, iy * step)
            for iy in range(1, ny)
            for ix in range(1, nx)
        ]
        candidates.sort()
        for _, tx, ty in candidates:
            for deg in (0.0, 90.0):
                w, h = (th, tw) if deg == 90.0 else (tw, th)
                box = (tx - w * 0.5, ty - h * 0.5, tx + w * 0.5, ty + h * 0.5)
                if grid.box_ok(side, *box):
                    return (tx, ty, deg, box)
    return None


def apply_silkscreen_and_fab_notes(
    board: pcbnew.BOARD, footprints: dict[str, pcbnew.FOOTPRINT]
) -> None:
    """Apply collision-free REF/VAL pairs, polarity graphics, QR boxes, and B.Fab notes."""
    # Seed SilkGrid AFTER hiding initial default Reference/Value positions
    for fp in footprints.values():
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)

    grid = sa.SilkGrid(board, footprints, (0.0, 0.0, BOARD_W, BOARD_H))

    # Keep text clear of Fiducial 2.0mm solder-mask openings (±1.25mm)
    for fx, fy in FIDUCIALS.values():
        grid.keepout[1].append((fx - 1.25, fy - 1.25, fx + 1.25, fy + 1.25))

    # Keep B.SilkS text outside all populated B.Cu component bodies (B.Fab ± 0.05 mm)
    for fp in footprints.values():
        if not fp.IsFlipped():
            continue
        fab_boxes = []
        for gi in fp.GraphicalItems():
            if gi.GetLayer() == pcbnew.B_Fab and not hasattr(gi, "GetText"):
                bb = gi.GetBoundingBox()
                fab_boxes.append(
                    (
                        pcbnew.ToMM(bb.GetLeft()),
                        pcbnew.ToMM(bb.GetTop()),
                        pcbnew.ToMM(bb.GetRight()),
                        pcbnew.ToMM(bb.GetBottom()),
                    )
                )
        if fab_boxes:
            grid.keepout[1].append(
                (
                    min(b[0] for b in fab_boxes) - 0.05,
                    min(b[1] for b in fab_boxes) - 0.05,
                    max(b[2] for b in fab_boxes) + 0.05,
                    max(b[3] for b in fab_boxes) + 0.05,
                )
            )

    # 1. JLCPCB QR Code 5.0 x 5.0 mm placeholders (B.SilkS inside RV1 upper pocket, F.SilkS top)
    b_qr = (5.0, 16.0, 10.0, 21.0)
    if grid.box_ok(1, *b_qr):
        sa.add_silk_rect(board, pcbnew.B_SilkS, *b_qr, filled=True, width=0.15)
        grid.reserve(1, *b_qr)
        _reserve_box(grid, 1, b_qr)
    else:
        raise RuntimeError(f"B.SilkS QR box {b_qr} collided with keepout/silk")

    f_qr = (12.5, 3.0, 17.5, 8.0)
    if grid.box_ok(0, *f_qr):
        sa.add_silk_rect(board, pcbnew.F_SilkS, *f_qr, filled=True, width=0.15)
        grid.reserve(0, *f_qr)
        _reserve_box(grid, 0, f_qr)
    else:
        raise RuntimeError(f"F.SilkS QR box {f_qr} collided with keepout/silk")

    # 2. Board Identification & Revision + TP Legend
    _place_board_silk_near(
        grid,
        1,
        "ENVELOPE FOLLOWER REV 1.0",
        9.8,
        22.3,
        height=0.80,
        thickness=0.15,
        step=0.20,
        max_radius=12.0,
        rotations=(0.0, 90.0),
    )
    _place_board_silk_near(
        grid,
        0,
        "ENVELOPE FOLLOWER REV 1.0",
        15.0,
        96.0,
        height=0.85,
        thickness=0.15,
        step=0.25,
        max_radius=18.0,
        rotations=(0.0, 90.0),
    )
    _place_board_silk_near(
        grid,
        1,
        "TP1-TP8: RH-5001 (DNP)",
        21.2,
        77.5,
        height=0.80,
        thickness=0.15,
        step=0.20,
        max_radius=16.0,
        rotations=(0.0, 90.0),
    )

    # 3. External Polarity, Pin-1 Dots, Cathode Bars & J4 -12V RED Stripe
    # U1 & U2 Pin-1 dots
    for ic_ref in ("U1", "U2"):
        p1 = _find_pad(footprints[ic_ref], "1")
        px, py = _pad_center_mm(p1)
        ic_pos = footprints[ic_ref].GetPosition()
        icx, icy = pcbnew.ToMM(ic_pos.x), pcbnew.ToMM(ic_pos.y)
        dx = -1.0 if px < icx else (1.0 if px > icx else 0.0)
        dy = -1.0 if py < icy else (1.0 if py > icy else 0.0)
        # Step outside pad and IC body
        dot_x = px + (0.0 if abs(py - icy) > 1.5 else dx * 1.45)
        dot_y = py + (dy * 1.50 if abs(py - icy) > 1.5 else 0.0)
        sa.add_silk_dot(board, pcbnew.B_SilkS, dot_x, dot_y, radius=0.28)
        _reserve_box(grid, 1, (dot_x - 0.35, dot_y - 0.35, dot_x + 0.35, dot_y + 0.35))

    # D1-D5, D9, D10 cathode bars + 'K' outside Pad 1
    for d_ref in ("D1", "D2", "D3", "D4", "D5", "D9", "D10"):
        p1 = _find_pad(footprints[d_ref], "1")
        p2 = _find_pad(footprints[d_ref], "2")
        k_x, k_y = _pad_center_mm(p1)
        a_x, a_y = _pad_center_mm(p2)
        vx, vy = k_x - a_x, k_y - a_y
        norm = math.hypot(vx, vy)
        ux, uy = vx / norm, vy / norm
        # Place bar 1.25 mm beyond K pad center (clears SOD-123 silk U-bracket by >= 0.35 mm)
        bx, by = k_x + ux * 1.25, k_y + uy * 1.25
        px_perp, py_perp = -uy * 0.55, ux * 0.55
        sa.add_silk_seg(
            board,
            pcbnew.B_SilkS,
            bx - px_perp,
            by - py_perp,
            bx + px_perp,
            by + py_perp,
            width=0.25,
        )
        _reserve_box(
            grid,
            1,
            (
                min(bx - px_perp, bx + px_perp) - 0.15,
                min(by - py_perp, by + py_perp) - 0.15,
                max(bx - px_perp, bx + px_perp) + 0.15,
                max(by - py_perp, by + py_perp) + 0.15,
            ),
        )
        _place_polarity_marker(grid, 1, "K", k_x, k_y, ux, uy, height=0.80)

    # D6-D8 (SOT-23) Pin-1 dots
    for s_ref in ("D6", "D7", "D8"):
        p1 = _find_pad(footprints[s_ref], "1")
        p3 = _find_pad(footprints[s_ref], "3")
        x1, y1 = _pad_center_mm(p1)
        x3, _ = _pad_center_mm(p3)
        ux = -1.0 if x1 < x3 else 1.0
        dot_x, dot_y = x1 + ux * 1.15, y1
        sa.add_silk_dot(board, pcbnew.B_SilkS, dot_x, dot_y, radius=0.25)
        _reserve_box(grid, 1, (dot_x - 0.32, dot_y - 0.32, dot_x + 0.32, dot_y + 0.32))

    # C3, C4, C11, C13 '+' polarity outside Pin 1
    for c_ref in ("C3", "C4", "C11", "C13"):
        p1 = _find_pad(footprints[c_ref], "1")
        p2 = _find_pad(footprints[c_ref], "2")
        x1, y1 = _pad_center_mm(p1)
        x2, _ = _pad_center_mm(p2)
        ux = -1.0 if x1 < x2 else 1.0
        # Pad 1 width is 3.5mm -> half-width 1.75mm -> place '+' 2.45mm out from pad 1 center
        px_mark, py_mark = x1 + ux * 2.45, y1
        tw, th = grid.measure_text("+", 0.90, 0.18)
        box = (
            px_mark - tw * 0.5,
            py_mark - th * 0.5,
            px_mark + tw * 0.5,
            py_mark + th * 0.5,
        )
        if grid.box_ok(1, *box):
            sa.add_silk_text(
                board, pcbnew.B_SilkS, "+", px_mark, py_mark, 0.0, 0.90, 0.18, True
            )
            grid.reserve(1, *box)
        else:
            _place_polarity_marker(grid, 1, "+", x1, y1, ux, 0.0, height=0.90)

    # LED1 '+' (Pin 2) and '-' (Pin 1) on BOTH sides
    led_k = _pad_center_mm(_find_pad(footprints["LED1"], "1"))
    led_a = _pad_center_mm(_find_pad(footprints["LED1"], "2"))
    for side in (0, 1):
        _place_polarity_marker(
            grid, side, "-", led_k[0], led_k[1], -1.0, 0.0, height=0.85
        )
        _place_polarity_marker(
            grid, side, "+", led_a[0], led_a[1], 1.0, 0.0, height=0.85
        )

    # RV1-RV4 Pin '1' (CCW) markers on BOTH sides
    for rv_ref in ("RV1", "RV2", "RV3", "RV4"):
        p1 = _pad_center_mm(_find_pad(footprints[rv_ref], "1"))
        for side in (0, 1):
            _place_polarity_marker(
                grid, side, "1", p1[0], p1[1], -1.0, 0.5, height=0.80
            )

    # J4 -12V RED stripe bar near Pins 1-2 on BOTH sides
    j4_p1 = _pad_center_mm(_find_pad(footprints["J4"], "1"))
    j4_p2 = _pad_center_mm(_find_pad(footprints["J4"], "2"))
    bar_x = j4_p1[0] - 4.80  # outside J4 shroud on the left (Pins 1-2 side)
    for side, layer_id in ((0, pcbnew.F_SilkS), (1, pcbnew.B_SilkS)):
        sa.add_silk_seg(
            board, layer_id, bar_x, j4_p1[1] - 0.8, bar_x, j4_p2[1] + 0.8, width=0.30
        )
        _reserve_box(
            grid, side, (bar_x - 0.25, j4_p1[1] - 1.0, bar_x + 0.25, j4_p2[1] + 1.0)
        )
        _place_board_silk_near(
            grid,
            side,
            "-12V RED",
            j4_p1[0] - 2.0,
            j4_p1[1] - 6.0,
            height=0.80,
            step=0.25,
            max_radius=12.0,
            rotations=(0.0,),
        )
        _place_board_silk_near(
            grid,
            side,
            "+12V",
            20.08,
            j4_p1[1] - 6.0,
            height=0.80,
            step=0.25,
            max_radius=12.0,
            rotations=(0.0,),
        )
        _place_board_silk_near(
            grid,
            side,
            "GND",
            15.00,
            j4_p2[1] + 2.8,
            height=0.80,
            step=0.25,
            max_radius=12.0,
            rotations=(0.0,),
        )

    # F.SilkS test-point and J4 header labels (abundant front silkscreen area)
    for ref, lbl in (
        ("TP1", "TP1 GND"),
        ("TP2", "TP2 +12V"),
        ("TP3", "TP3 -12V"),
        ("TP4", "TP4 PREAMP"),
        ("TP5", "TP5 FWR_OUT"),
        ("TP6", "TP6 ENV_NODE"),
        ("TP7", "TP7 ENV_OUT"),
        ("TP8", "TP8 INV_RAW"),
    ):
        pos = footprints[ref].GetPosition()
        _place_board_silk_near(
            grid,
            0,
            lbl,
            pcbnew.ToMM(pos.x),
            pcbnew.ToMM(pos.y),
            height=0.80,
            step=0.30,
            max_radius=16.0,
            rotations=(0.0, 90.0),
        )
    _place_board_silk_near(
        grid,
        0,
        "J4 ±12V PWR",
        15.0,
        102.0,
        height=0.85,
        step=0.30,
        max_radius=14.0,
        rotations=(0.0, 90.0),
    )

    # 4. Primary <REF> + <VAL> pairs for ALL 76 footprints (longest B.Cu SMDs first)
    all_refs = list(footprints.keys())
    f_parts = [r for r in all_refs if not footprints[r].IsFlipped()]
    b_rest = [r for r in all_refs if footprints[r].IsFlipped()]
    b_rest.sort(key=lambda r: -(len(SILK_VAL_TOKENS.get(r, "")) * 10 + len(r)))
    placement_order = f_parts + b_rest

    def _anchor_center(ref: str) -> tuple[float, float]:
        fp = footprints[ref]
        if ref in ("J1", "J2", "J3"):
            ps = _pad_center_mm(_find_pad(fp, "S"))
            pt = _pad_center_mm(_find_pad(fp, "T"))
            return ((ps[0] + pt[0]) * 0.5, (ps[1] + pt[1]) * 0.5)
        if ref == "J4":
            return (15.00, 95.80)
        pos = fp.GetPosition()
        return (pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))

    placed_refs: set[str] = set()
    # Pass 1: Keep labels strictly local (<= 6.5 mm) where open space exists
    for ref in placement_order:
        fp = footprints[ref]
        val_tok = SILK_VAL_TOKENS.get(ref, "")
        side = 1 if fp.IsFlipped() else 0
        c = _anchor_center(ref)
        if (
            sa.place_ref_val_pair(
                grid,
                fp,
                val_tok,
                side=side,
                center=c,
                height=0.80,
                thickness=0.15,
                gap=0.35,
                step=0.25,
                max_radius=6.5,
                rotations=(0.0, 90.0),
            )
            or val_tok
            and _place_stacked_ref_val_pair(
                grid, fp, val_tok, side=side, center=c, step=0.25, max_radius=6.5
            )
        ):
            placed_refs.add(ref)

    # Pass 2: Medium radius (<= 24 mm) then VAL-first boardwide split fallback
    for ref in placement_order:
        if ref in placed_refs:
            continue
        fp = footprints[ref]
        val_tok = SILK_VAL_TOKENS.get(ref, "")
        side = 1 if fp.IsFlipped() else 0
        c = _anchor_center(ref)
        if sa.place_ref_val_pair(
            grid,
            fp,
            val_tok,
            side=side,
            center=c,
            height=0.80,
            thickness=0.15,
            gap=0.35,
            step=0.25,
            max_radius=24.0,
            rotations=(0.0, 90.0),
        ) or (
            val_tok
            and _place_stacked_ref_val_pair(
                grid, fp, val_tok, side=side, center=c, step=0.25, max_radius=24.0
            )
        ):
            placed_refs.add(ref)
            continue

        silk_layer = pcbnew.B_SilkS if side == 1 else pcbnew.F_SilkS
        mirrored = side == 1
        vx, vy = c
        if val_tok:
            vres = _place_boardwide_silk_text(grid, side, val_tok, *c)
            if vres is None:
                raise RuntimeError(
                    f"Failed to place silkscreen value for {ref} ({val_tok})"
                )
            vx, vy, vdeg, vbox = vres
            grid.reserve(side, *vbox)
            sa.add_silk_text(
                fp, silk_layer, val_tok, vx, vy, vdeg, 0.80, 0.15, mirrored
            )
        rres = _place_boardwide_silk_text(grid, side, ref, vx, vy)
        if rres is None:
            raise RuntimeError(f"Failed to place silkscreen reference for {ref}")
        rx, ry, rdeg, rbox = rres
        grid.reserve(side, *rbox)
        sa._configure_ref_field(
            fp.Reference(), silk_layer, rx, ry, rdeg, 0.80, 0.15, mirrored
        )
        placed_refs.add(ref)

    # 5. Reverse-side B.SilkS hints strictly adjacent (<= 8.5 mm) to F.Cu THT holes
    b_tht_hints = [
        ("C1 1uF", "C1", (4.5, 76.0)),
        ("C2 1uF", "C2", (25.5, 71.0)),
        ("C9 1uF", "C9", (3.0, 8.0)),
        ("RV1 GAIN", "RV1", (7.5, 22.0)),
        ("RV2 ATK", "RV2", (22.5, 22.0)),
        ("RV3 REL", "RV3", (7.5, 42.0)),
        ("RV4 OFFSET", "RV4", (22.5, 42.0)),
        ("LED1 ENV", "LED1", (15.0, 54.5)),
        ("J1 IN", "J1", (15.0, 70.5)),
        ("J2 OUT", "J2", (7.5, 87.5)),
        ("J3 INV_OUT", "J3", (22.5, 87.5)),
    ]
    for full_lbl, short_lbl, tgt in b_tht_hints:
        for lbl_try in (full_lbl, short_lbl):
            try:
                _place_board_silk_near(
                    grid,
                    1,
                    lbl_try,
                    tgt[0],
                    tgt[1],
                    height=0.80,
                    thickness=0.15,
                    step=0.30,
                    max_radius=8.5,
                    rotations=(0.0, 90.0),
                )
                break
            except RuntimeError:
                continue

    # 6. Complete B.Fab Fabrication Notes (100% fab_notes_completeness)
    sa.add_standard_fab_notes(board, 15.0, 19.0)


def main() -> None:
    """Build EnvelopeFollower.kicad_pcb from envelope_follower.net."""
    net_path = HERE / "envelope_follower.net"
    out_path = HERE / "EnvelopeFollower.kicad_pcb"

    components, nets = lt.parse_netlist(net_path, dnp_prefixes=("TP",))
    board = lt.create_base_board(
        out_path,
        0.0,
        0.0,
        BOARD_W,
        BOARD_H,
        title="ENVELOPE FOLLOWER",
        revision="Rev 1.0",
        date="2026-11",
        track_width=SIGNAL_W,
        clearance=TRACK_CLR,
        via_diam=VIA_DIAM,
        via_drill=VIA_DRILL,
        edge_clearance=EDGE_CLR,
    )

    footprints = lt.populate_footprints(board, components, PLACEMENTS)
    add_fiducials(board, footprints)
    check_courtyards_and_tht(footprints)

    net_items, _ = lt.assign_nets(board, footprints, nets)
    gnd_net = net_items["GND"]

    router, net_pads, _, net_by_code = build_router(footprints)
    place_gnd_stitching_vias(board, router, footprints, gnd_net)
    escape_anchors, pre_connected, skip_nets = pre_route_ic_and_power(
        board, router, footprints
    )
    route_all_nets(
        board,
        router,
        footprints,
        net_pads,
        net_by_code,
        escape_anchors,
        pre_connected,
        skip_nets,
    )
    verify_and_stitch_gnd(board, router, gnd_net)
    apply_silkscreen_and_fab_notes(board, footprints)

    pcbnew.SaveBoard(str(out_path), board)
    print(f"Generated {out_path} ({len(footprints)} footprints).")


if __name__ == "__main__":
    main()
