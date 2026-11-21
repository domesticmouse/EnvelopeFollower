#!/usr/bin/env python3
"""
Generate a 6 HP (30.00 x 108.00 mm) 2-layer KiCad 10 PCB (`EnvelopeFollower.kicad_pcb`)
from `envelope_follower.net`, following `EnvelopeFollowerImproved.md` and
`SilkscreenInstructions.md`.

Side Allocation:
  - F.Cu (8 front-panel THT controls): RV1-RV4, J1-J3, D4
  - B.Cu (49 SMT + 3 populated rear THT + 8 DNP TPs + 3 fiducials):
      U1-U2, D1-D3, D5-D11, R1-R29, C3-C10, J4, C1-C2, TP1-TP8 (DNP), FID1-FID3
"""

from __future__ import annotations

import math
import os
import pathlib
import sys
from collections.abc import Iterator, Sequence
from typing import TypeVar

_T = TypeVar("_T")


def _iter_pairs(seq: Sequence[_T]) -> Iterator[tuple[_T, _T]]:
    """Yield consecutive pairs from `seq` cleanly on Python 3.9+."""
    for i in range(len(seq) - 1):
        yield seq[i], seq[i + 1]


KICAD_PYTHON = pathlib.Path(
    "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
)

try:
    import pcbnew
except ModuleNotFoundError:
    if KICAD_PYTHON.exists():
        os.execv(str(KICAD_PYTHON), [str(KICAD_PYTHON), *sys.argv])
    raise

STAGE_DIR = pathlib.Path(__file__).resolve().parent
LAYOUT_SCRIPTS = STAGE_DIR / ".agents/skills/kicad-pcbnew-layout/scripts"
SILK_SCRIPTS = STAGE_DIR / ".agents/skills/kicad-silkscreen-markup/scripts"
for _p in (str(LAYOUT_SCRIPTS), str(SILK_SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pcbnew_layout_template import (
    FP_DIR,
    GridRouter,
    _merge_collinear_path,
    add_track,
    add_via,
    assign_nets,
    create_base_board,
    extract_keepout_circles,
    extract_pad_geometry,
    parse_netlist,
    populate_footprints,
)
from silk_annotator import (
    SILK_EDGE_CLEARANCE,
    SILK_HEIGHT,
    SILK_THICKNESS,
    SilkGrid,
    _configure_ref_field,
    _make_box,
    add_silk_dot,
    add_silk_rect,
    add_silk_seg,
    add_silk_text,
    add_standard_fab_notes,
    box_edge_distance,
    footprint_bbox,
    is_fiducial_ref,
    is_passive_ref,
    is_smd_footprint,
    place_ref_val_pair,
    place_val_only,
)

BOARD_W = 30.00
BOARD_H = 108.00
EDGE_CLEARANCE = 0.50
TRACK_CLEARANCE = 0.20
SIGNAL_WIDTH = 0.25
POWER_WIDTH = 0.30
VIA_DIAM = 0.60
VIA_DRILL = 0.30

POWER_RAILS = {
    "+12V_IN",
    "-12V_IN",
    "+12V_FILT_IN",
    "-12V_FILT_IN",
    "+12V_PROT",
    "-12V_PROT",
}

BREAKOUT_NETS = {
    "V_GAIN",
    "V_RECT",
    "PEAK_INV",
    "PEAK_OP_OUT",
    "V_ENV_BUF",
    "OUT_NONINV",
    "OUT_INV_NODE",
    "V_OUT_BUF",
    "V_INV_BUF",
    "LED_REF_IN",
    "LED_SENSE",
    "V_LED_DRV",
    "IN_GAIN_INV",
    "IN_WIPER",
    "RECT_INV",
    "SUM_INV",
    "INV_SUM",
    "REL_MID",
    "RECT_DIODE_OUT",
    "RECT_MID",
}

# 3 B.Cu fiducials (not in netlist; wide non-collinear triangle across board)
FIDUCIALS: dict[str, tuple[float, float]] = {
    "FID1": (2.00, 2.00),
    "FID2": (28.00, 72.50),
    "FID3": (2.00, 72.30),
}

# 5 x 5 mm JLCPCB QR placeholder on B.SilkS (bottom-right clear corner)
QR_BOX = (24.25, 102.45, 29.25, 107.45)


def get_clean_placements() -> dict[str, tuple[float, float, float, bool]]:
    """Compute exact non-overlapping placements across all 5 B.Cu corridors and F.Cu panel grid."""
    return {
        # ------------------------------------------------------------------
        # F.Cu: Front-Panel Controls (6 HP grid: columns X=7.25, X=22.75)
        # ------------------------------------------------------------------
        "RV1": (
            4.75,
            24.00,
            90.0,
            False,
        ),  # shaft (7.25, 16.50)  F.CrtYd Y:[11.38, 25.18]
        "RV2": (
            20.25,
            24.00,
            90.0,
            False,
        ),  # shaft (22.75, 16.50) F.CrtYd Y:[11.38, 25.18]
        "RV3": (
            4.75,
            44.50,
            90.0,
            False,
        ),  # shaft (7.25, 37.00)  F.CrtYd Y:[31.88, 45.68]
        "RV4": (
            20.25,
            44.50,
            90.0,
            False,
        ),  # shaft (22.75, 37.00) F.CrtYd Y:[31.88, 45.68]
        "J1": (
            7.25,
            57.52,
            0.0,
            False,
        ),  # bushing (7.25, 64.00) F.CrtYd Y:[56.08, 70.53]
        "D4": (
            21.48,
            64.00,
            0.0,
            False,
        ),  # lens (22.75, 64.00) F.CrtYd Y:[61.77, 66.24]
        "J2": (
            7.25,
            75.52,
            0.0,
            False,
        ),  # bushing (7.25, 82.00) F.CrtYd Y:[74.08, 88.53]
        "J3": (
            22.75,
            75.52,
            0.0,
            False,
        ),  # bushing (22.75, 82.00) F.CrtYd Y:[74.08, 88.53]
        # ------------------------------------------------------------------
        # B.Cu Corridor 0 (Top: Y = 0.50 .. 11.375)
        # ------------------------------------------------------------------
        "U1": (13.10, 5.90, 0.0, True),  # vertical: 1..7 on L, 8..14 on R
        "C5": (6.90, 5.90, 90.0, True),  # +12V_PROT decoupling (<3.8mm to U1.4)
        "C6": (19.00, 9.20, 90.0, True),  # -12V_PROT decoupling (<4.8mm to U1.11)
        "TP4": (7.65, 9.60, 0.0, True),  # <= 3mm to U1.1 (10.63, 9.71)
        "R4": (2.80, 5.90, 0.0, True),
        "R5": (3.60, 9.60, 0.0, True),
        "C9": (5.80, 2.00, 0.0, True),
        "D1": (23.15, 2.55, 0.0, True),
        "D2": (23.15, 6.70, 0.0, True),
        "TP5": (18.55, 2.20, 0.0, True),  # <= 3mm to U1.8 (15.58, 2.09)
        "R6": (28.00, 2.00, 0.0, True),
        "R7": (28.00, 5.70, 180.0, True),  # Pad 2 (RECT_MID) faces LEFT toward D2.2
        "R8": (28.00, 9.20, 0.0, True),
        # ------------------------------------------------------------------
        # B.Cu Corridor 1 (Pot-to-Pot: Y = 25.175 .. 31.875)
        # ------------------------------------------------------------------
        "C1": (6.90, 28.50, 180.0, True),  # Pad 1 (IN_CLAMP) at 6.90 inside RV3 arch
        "R2": (10.10, 26.75, 0.0, True),
        "R3": (10.10, 30.35, 0.0, True),
        "R9": (14.10, 26.75, 0.0, True),
        "R10": (14.10, 30.35, 0.0, True),
        "R12": (18.10, 26.75, 0.0, True),
        "R13": (18.10, 30.35, 0.0, True),
        "C2": (22.80, 28.50, 0.0, True),
        # ------------------------------------------------------------------
        # B.Cu Corridor 2 (Pot-to-Jack: Y = 45.675 .. 56.075 L / 61.765 R)
        # ------------------------------------------------------------------
        "R17": (18.10, 46.80, 0.0, True),  # directly under RV4.1 (17.75, 44.5)
        "R19": (22.30, 46.80, 0.0, True),
        "R18": (27.00, 46.80, 0.0, True),
        "U2": (20.40, 56.60, 180.0, True),  # Y:[52.00, 61.20] X:[16.68, 24.13]
        "C7": (26.80, 56.20, 90.0, True),  # +12V_PROT decoupling (<4.0mm to U2.4)
        "C8": (13.45, 57.10, 90.0, True),  # -12V_PROT decoupling (<4.7mm to U2.11)
        "TP6": (14.70, 52.60, 0.0, True),  # <= 3mm to U2.14 (17.93, 52.79)
        "TP8": (25.83, 52.70, 0.0, True),  # <= 3mm to U2.1 (22.88, 52.79)
        "R14": (3.00, 49.30, 180.0, True),  # Pad 1 (REL_MID) faces RIGHT toward RV3.1
        "R11": (7.60, 49.30, 0.0, True),
        "D3": (11.60, 49.30, 0.0, True),  # Pad 1 (K) L toward RV3/RV4 gap -> R12
        "R1": (2.40, 53.70, 0.0, True),
        "D9": (6.90, 53.70, 180.0, True),
        "C10": (11.00, 53.70, 0.0, True),
        # ------------------------------------------------------------------
        # B.Cu Corridor 3 (Mid-Jack & around D4/J2/J3)
        # ------------------------------------------------------------------
        "D5": (14.20, 61.70, 0.0, True),
        "R15": (15.20, 63.80, 0.0, True),
        "R16": (15.20, 66.40, 0.0, True),
        "R20": (15.20, 69.00, 0.0, True),
        "R23": (15.20, 71.60, 0.0, True),
        "D6": (21.50, 67.35, 0.0, True),
        "R27": (27.50, 60.20, 0.0, True),
        "R25": (27.50, 63.40, 0.0, True),
        "R26": (27.50, 66.60, 0.0, True),
        "R22": (27.50, 69.80, 0.0, True),
        "D10": (15.00, 74.85, 90.0, True),
        "R21": (15.00, 80.80, 90.0, True),  # R21.1 (V_OUT_BUF) at Y=83.76 near TP7
        "TP7": (14.40, 86.50, 0.0, True),  # <= 3mm to R21.1 (15.00, 83.76)
        "R24": (21.70, 72.10, 0.0, True),  # between D6 and J3, clear of J3(F)
        # ------------------------------------------------------------------
        # B.Cu Corridor 4 (Bottom: Y = 88.525 .. 107.50 -> 18.975 mm tall!)
        # ------------------------------------------------------------------
        "D7": (23.15, 89.65, 0.0, True),
        "R28": (27.45, 89.30, 0.0, True),
        "D11": (
            5.30,
            72.30,
            0.0,
            True,
        ),  # clear gap between J1(F) and J2(F), >FID3 3.28
        "J4": (6.40, 101.25, 270.0, True),
        "D8": (3.30, 89.60, 0.0, True),
        "R29": (5.80, 90.20, 90.0, True),
        "TP2": (3.30, 92.40, 0.0, True),
        "C4": (11.45, 92.20, 0.0, True),
        "TP1": (19.35, 90.40, 0.0, True),
        "TP3": (20.45, 95.50, 0.0, True),
        "C3": (25.85, 95.60, 90.0, True),
    }


def add_fiducials(
    board: pcbnew.BOARD, fiducials: dict[str, tuple[float, float]]
) -> dict[str, pcbnew.FOOTPRINT]:
    """Place B.Cu assembly fiducials (not present in netlist) with hidden text."""
    fids: dict[str, pcbnew.FOOTPRINT] = {}
    lib_path = str(FP_DIR / "Fiducial.pretty")
    for ref, (fx, fy) in fiducials.items():
        fp = pcbnew.FootprintLoad(lib_path, "Fiducial_1mm_Mask2mm")
        if fp is None:
            raise RuntimeError("Failed to load Fiducial:Fiducial_1mm_Mask2mm")
        board.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(fx), pcbnew.FromMM(fy)))
        fp.Flip(fp.GetPosition(), False)
        fp.SetOrientationDegrees(0.0)
        fp.SetReference(ref)
        fp.SetValue("Fiducial")
        fp.SetExcludedFromBOM(True)
        fp.SetExcludedFromPosFiles(True)
        fp.SetDNP(True)
        for fld in fp.GetFields():
            fld.SetVisible(False)
        fp.Reference().SetLayer(pcbnew.B_Fab)
        fp.Reference().SetVisible(False)
        fp.Value().SetLayer(pcbnew.B_Fab)
        fp.Value().SetVisible(False)
        for pad in fp.Pads():
            pad.SetNetCode(0)
        fids[ref] = fp
    return fids


def check_placement_constraints(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
    fids: dict[str, pcbnew.FOOTPRINT],
) -> None:
    """Verify zero F/B courtyard collisions and edge clearances before routing."""
    all_fps = {**footprints, **fids}
    crtyd_boxes: dict[str, tuple[str, float, float, float, float]] = {}
    for ref, fp in all_fps.items():
        layer = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
        xs: list[float] = []
        ys: list[float] = []
        for gi in fp.GraphicalItems():
            if not hasattr(gi, "GetText") and gi.GetLayer() == layer:
                bb = gi.GetBoundingBox()
                xs.extend((pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetRight())))
                ys.extend((pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetBottom())))
        if not xs:
            continue
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        side = "B" if fp.IsFlipped() else "F"
        crtyd_boxes[ref] = (side, x0, y0, x1, y1)
        if x0 < 0.45 or x1 > BOARD_W - 0.45 or y0 < 0.45 or y1 > BOARD_H - 0.45:
            print(
                f"WARNING edge clearance: {ref} ({side}) box=({x0:.2f},{y0:.2f},{x1:.2f},{y1:.2f})"
            )

    refs = sorted(crtyd_boxes)
    overlaps = []
    for i, r1 in enumerate(refs):
        s1, x0, y0, x1, y1 = crtyd_boxes[r1]
        for r2 in refs[i + 1 :]:
            s2, a0, b0, a1, b1 = crtyd_boxes[r2]
            # Enforce zero overlap even between F.Cu panel controls and B.Cu components
            if not (
                x1 <= a0 + 0.01 or a1 <= x0 + 0.01 or y1 <= b0 + 0.01 or b1 <= y0 + 0.01
            ):
                overlaps.append((r1, s1, (x0, y0, x1, y1), r2, s2, (a0, b0, a1, b1)))
    if overlaps:
        for item in overlaps:
            print(
                f"COURTYARD OVERLAP: {item[0]}({item[1]}) {item[2]} vs {item[3]}({item[4]}) {item[5]}"
            )
        raise RuntimeError(f"Found {len(overlaps)} courtyard overlaps!")


class SafeGridRouter(GridRouter):
    """GridRouter with full via clearance checks and edge safety for BV-001/VP-001."""

    def can_place_via(self, gx: int, gy: int, net_code: int) -> bool:
        idx = gy * self.nx + gx
        if self.via_block[idx] or self.smd_via_block[idx]:
            return False
        vx, vy = self.to_mm(gx, gy)
        if vx < 0.65 or vx > BOARD_W - 0.65 or vy < 0.65 or vy > BOARD_H - 0.65:
            return False
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx_i, ny_i = gx + dx, gy + dy
                if nx_i < 0 or nx_i >= self.nx or ny_i < 0 or ny_i >= self.ny:
                    return False
                nidx = ny_i * self.nx + nx_i
                for layer in (0, 1):
                    if self.static_block[layer][nidx]:
                        return False
                    own = self.owner[layer][nidx]
                    if own != -1 and own != net_code:
                        return False
                    pnet = self.pad_net[layer][nidx]
                    if pnet != -1 and pnet != net_code:
                        return False
        return True


def _pad_in_copper(
    px: float, py: float, x0: float, y0: float, x1: float, y1: float
) -> bool:
    return (x0 + 0.05) <= px <= (x1 - 0.05) and (y0 + 0.05) <= py <= (y1 - 0.05)


def route_pcb(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
    fids: dict[str, pcbnew.FOOTPRINT],
    net_items: dict[str, pcbnew.NETINFO_ITEM],
    nets: list[dict],
) -> None:
    """Route all nets with DFM-safe clearances, decoupling pre-routes, and GND zone fill."""
    router = SafeGridRouter(
        0.0,
        0.0,
        BOARD_W,
        BOARD_H,
        step=0.25,
        edge_clearance=EDGE_CLEARANCE,
        track_width=SIGNAL_WIDTH,
        clearance=TRACK_CLEARANCE,
    )

    # 1. Extract internal F.Cu keepout zones (WQP-PJ398SM jack bushings)
    for lid, cx, cy, r in extract_keepout_circles(footprints):
        router.mark_static_circle(
            lid, cx, cy, r + TRACK_CLEARANCE + SIGNAL_WIDTH * 0.5, block_via=(lid == 0)
        )

    # 2. Mark fiducial B.Cu keepouts (2.0 mm solder mask openings) and 5x5 mm QR zone (no vias or B.Cu tracks)
    for fid_fp in fids.values():
        pos = fid_fp.GetPosition()
        fx, fy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        router.mark_static_circle(1, fx, fy, 1.35, block_via=True)
    qx0, qy0, qx1, qy1 = QR_BOX
    qr_margin = 0.50
    gx0 = max(0, math.floor((qx0 - qr_margin - router.x0) / router.step))
    gx1 = min(router.nx - 1, math.ceil((qx1 + qr_margin - router.x0) / router.step))
    gy0 = max(0, math.floor((qy0 - qr_margin - router.y0) / router.step))
    gy1 = min(router.ny - 1, math.ceil((qy1 + qr_margin - router.y0) / router.step))
    for qgy in range(gy0, gy1 + 1):
        for qgx in range(gx0, gx1 + 1):
            qidx = qgy * router.nx + qgx
            router.via_block[qidx] = 1
            router.static_block[1][qidx] = 1

    # 3. Map every pad, block SMD via-in-pad, block THT drills & net=0 pads
    all_pads_by_net: dict[
        int,
        list[
            tuple[str, pcbnew.PAD, float, float, float, float, float, float, set[int]]
        ],
    ] = {}
    pad_lookup: dict[
        tuple[str, str],
        tuple[pcbnew.PAD, float, float, float, float, float, float, set[int]],
    ] = {}

    for ref, fp in footprints.items():
        for pad in fp.Pads():
            nc = pad.GetNetCode()
            cx, cy, x0, y0, x1, y1, layers = extract_pad_geometry(pad)
            pnum = pad.GetNumber()
            is_tht = pad.GetAttribute() in (
                pcbnew.PAD_ATTRIB_PTH,
                pcbnew.PAD_ATTRIB_NPTH,
            )
            if nc == 0:
                # Unconnected pads (pot mounting lugs, J2.TN, J3.TN)
                margin = TRACK_CLEARANCE + POWER_WIDTH * 0.5
                for lid in layers:
                    router.mark_pad_box(lid, x0, y0, x1, y1, margin, -2)
                if is_tht:
                    dr = (
                        max(
                            pcbnew.ToMM(pad.GetDrillSize().x),
                            pcbnew.ToMM(pad.GetDrillSize().y),
                        )
                        * 0.5
                    )
                    router.mark_static_circle(
                        0, cx, cy, max(x1 - x0, y1 - y0) * 0.5 + 0.1, block_via=True
                    )
                    router.mark_static_circle(
                        1, cx, cy, max(x1 - x0, y1 - y0) * 0.5 + 0.1, block_via=True
                    )
                    _ = dr
                continue

            pad_lookup[(ref, pnum)] = (pad, cx, cy, x0, y0, x1, y1, layers)
            all_pads_by_net.setdefault(nc, []).append(
                (ref, pad, cx, cy, x0, y0, x1, y1, layers)
            )

            margin = TRACK_CLEARANCE + POWER_WIDTH * 0.5
            for lid in layers:
                router.mark_pad_box(lid, x0, y0, x1, y1, margin, nc)

            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
                router.mark_smd_via_block(x0, y0, x1, y1, margin=0.02)
            elif is_tht:
                gx, gy = router.to_grid(cx, cy)
                router.tht_pad_grid[(gx, gy)] = nc
                dr = (
                    max(
                        pcbnew.ToMM(pad.GetDrillSize().x),
                        pcbnew.ToMM(pad.GetDrillSize().y),
                    )
                    * 0.5
                )
                # Block vias from overlapping THT holes (other than 0-cost THT transition at (gx, gy))
                vr = dr + VIA_DIAM * 0.5 + 0.10
                gx0 = max(0, math.floor((cx - vr - router.x0) / router.step))
                gx1 = min(router.nx - 1, math.ceil((cx + vr - router.x0) / router.step))
                gy0 = max(0, math.floor((cy - vr - router.y0) / router.step))
                gy1 = min(router.ny - 1, math.ceil((cy + vr - router.y0) / router.step))
                for ny_i in range(gy0, gy1 + 1):
                    for nx_i in range(gx0, gx1 + 1):
                        px_g, py_g = router.to_mm(nx_i, ny_i)
                        if (px_g - cx) ** 2 + (py_g - cy) ** 2 <= vr * vr:
                            router.via_block[ny_i * router.nx + nx_i] = 1

    # 4. Compute clean grid anchor (with outward escape stubs for SOIC-14 pads)
    pad_anchors: dict[tuple[str, str], tuple[int, int, int, float, float]] = {}
    used_escapes: list[tuple[int, float, float, float, float, float, int]] = []

    for (ref, pnum), (pad, cx, cy, x0, y0, x1, y1, layers) in pad_lookup.items():
        nc = pad.GetNetCode()
        lid = 1 if 1 in layers else 0
        fp = footprints[ref]
        if ref in ("U1", "U2"):
            # Outward escape just past actual outer copper edge of SOIC-14 pad
            fc = fp.GetPosition()
            fcx, fcy = pcbnew.ToMM(fc.x), pcbnew.ToMM(fc.y)
            rot = fp.GetOrientation().AsDegrees() % 360.0
            if rot in (0.0, 180.0):
                dir_x = -1.0 if cx < fcx else 1.0
                ex_raw = (x0 - 0.35) if dir_x < 0 else (x1 + 0.35)
                gx, gy = router.to_grid(ex_raw, cy)
            else:
                dir_y = -1.0 if cy < fcy else 1.0
                ey_raw = (y0 - 0.35) if dir_y < 0 else (y1 + 0.35)
                gx, gy = router.to_grid(cx, ey_raw)
            ex, ey = router.to_mm(gx, gy)
            w = (
                POWER_WIDTH
                if pad.GetNetname() in POWER_RAILS or pad.GetNetname() == "GND"
                else SIGNAL_WIDTH
            )
            router.mark_segment(lid, cx, cy, ex, ey, w, nc)
            pad_anchors[(ref, pnum)] = (lid, gx, gy, cx, cy)
            used_escapes.append((lid, cx, cy, ex, ey, w, nc))
        else:
            gx, gy = router.to_grid(cx, cy)
            gx_mm, gy_mm = router.to_mm(gx, gy)
            if not _pad_in_copper(gx_mm, gy_mm, x0, y0, x1, y1):
                w = (
                    POWER_WIDTH
                    if pad.GetNetname() in POWER_RAILS or pad.GetNetname() == "GND"
                    else SIGNAL_WIDTH
                )
                router.mark_segment(lid, cx, cy, gx_mm, gy_mm, w, nc)
            pad_anchors[(ref, pnum)] = (lid, gx, gy, cx, cy)

    # Emit pad-to-grid stubs for all non-GND connected pads (GND pads via zone/vias)
    emitted_stubs: set[tuple[str, str]] = set()

    def ensure_pad_stub(ref: str, pnum: str, net_name: str, nc: int) -> None:
        key = (ref, pnum)
        if key in emitted_stubs:
            return
        emitted_stubs.add(key)
        lid, gx, gy, cx, cy = pad_anchors[key]
        ex, ey = router.to_mm(gx, gy)
        if abs(ex - cx) > 0.005 or abs(ey - cy) > 0.005:
            _, _, _, x0, y0, x1, y1, _ = pad_lookup[key]
            if ref in ("U1", "U2") or not _pad_in_copper(ex, ey, x0, y0, x1, y1):
                w = (
                    POWER_WIDTH
                    if net_name in POWER_RAILS or net_name == "GND"
                    else SIGNAL_WIDTH
                )
                add_track(
                    board,
                    pcbnew.B_Cu if lid == 1 else pcbnew.F_Cu,
                    cx,
                    cy,
                    ex,
                    ey,
                    w,
                    net_items[net_name],
                )

    # Track emitted vias and pre-connected clusters
    emitted_vias: set[tuple[int, int]] = set()
    gnd_nc = net_items["GND"].GetNetCode()

    def emit_via_once(
        gx: int, gy: int, net_name: str, nc: int
    ) -> pcbnew.PCB_VIA | None:
        if (gx, gy) in emitted_vias:
            return None
        if router.tht_pad_grid.get((gx, gy)) == nc:
            return None
        emitted_vias.add((gx, gy))
        vx, vy = router.to_mm(gx, gy)
        via_obj = add_via(
            board, vx, vy, net_items[net_name], diam=VIA_DIAM, drill=VIA_DRILL
        )
        router.mark_via_obstacle(
            vx, vy, VIA_DIAM * 0.5 + TRACK_CLEARANCE + POWER_WIDTH * 0.5, nc
        )
        return via_obj

    # 5. Pre-route direct decoupling pairs, adjacent pin shorts, and supply escape vias FIRST
    pre_connected: dict[str, list[tuple[tuple[str, str], tuple[str, str]]]] = {}
    pre_vias: dict[str, list[tuple[tuple[str, str], int, int]]] = {}
    pre_via_records: dict[
        str, list[tuple[int, int, pcbnew.PCB_VIA | None, list[pcbnew.PCB_TRACK]]]
    ] = {}
    direct_pin_merged: set[tuple[str, str]] = set()
    decoupling_pairs = [
        ("+12V_PROT", ("U1", "4"), ("C5", "1")),
        ("-12V_PROT", ("U1", "11"), ("C6", "1")),
        ("+12V_PROT", ("U2", "4"), ("C7", "1")),
        ("-12V_PROT", ("U2", "11"), ("C8", "1")),
        ("V_ENV_BUF", ("U2", "13"), ("U2", "14")),
    ]
    for net_name, pin_a, pin_b in decoupling_pairs:
        nc = net_items[net_name].GetNetCode()
        w = POWER_WIDTH if net_name in POWER_RAILS else SIGNAL_WIDTH
        la, gxa, gya, cxa, cya = pad_anchors[pin_a]
        lb, gxb, gyb, cxb, cyb = pad_anchors[pin_b]
        if pin_a[0] == pin_b[0] == "U2":
            # Adjacent pins on U2: connect directly between pad centers without extra pin_a stub
            add_track(board, pcbnew.B_Cu, cxa, cya, cxb, cyb, w, net_items[net_name])
            router.mark_segment(1, cxa, cya, cxb, cyb, w, nc)
            pre_connected.setdefault(net_name, []).append((pin_a, pin_b))
            direct_pin_merged.add(pin_a)
            continue
        path = router.route([(la, gxa, gya)], {(lb, gxb, gyb)}, nc, preferred_layer=1)
        if path is not None:
            ensure_pad_stub(pin_a[0], pin_a[1], net_name, nc)
            ensure_pad_stub(pin_b[0], pin_b[1], net_name, nc)
            merged = _merge_collinear_path(path)
            for p_a, p_b in _iter_pairs(merged):
                if p_a[0] == p_b[0]:
                    ax, ay = router.to_mm(p_a[1], p_a[2])
                    bx, by = router.to_mm(p_b[1], p_b[2])
                    kl = pcbnew.B_Cu if p_a[0] == 1 else pcbnew.F_Cu
                    add_track(board, kl, ax, ay, bx, by, w, net_items[net_name])
                    router.mark_segment(p_a[0], ax, ay, bx, by, w, nc)
                else:
                    emit_via_once(p_a[1], p_a[2], net_name, nc)
            pre_connected.setdefault(net_name, []).append((pin_a, pin_b))

        # Lift decoupling supply pin up to F.Cu via a clean nearby via before breakout routing
        if net_name in POWER_RAILS:
            best_sv: tuple[float, int, int] | None = None
            for dy in range(-8, 9):
                for dx in range(-8, 9):
                    vgx, vgy = gxb + dx, gyb + dy
                    if not (0 <= vgx < router.nx and 0 <= vgy < router.ny):
                        continue
                    if not router.can_place_via(vgx, vgy, nc):
                        continue
                    vx, vy = router.to_mm(vgx, vgy)
                    d2 = (vx - cxb) ** 2 + (vy - cyb) ** 2
                    if d2 <= 5.0 and (best_sv is None or d2 < best_sv[0]):
                        best_sv = (d2, vgx, vgy)
            if best_sv is not None:
                _, vgx, vgy = best_sv
                vpath = router.route(
                    [(lb, gxb, gyb)], {(lb, vgx, vgy)}, nc, preferred_layer=1
                )
                if vpath is not None:
                    ensure_pad_stub(pin_b[0], pin_b[1], net_name, nc)
                    merged_v = _merge_collinear_path(vpath)
                    v_tracks: list[pcbnew.PCB_TRACK] = []
                    for p_a, p_b in _iter_pairs(merged_v):
                        if p_a[0] == p_b[0]:
                            ax, ay = router.to_mm(p_a[1], p_a[2])
                            bx, by = router.to_mm(p_b[1], p_b[2])
                            kl = pcbnew.B_Cu if p_a[0] == 1 else pcbnew.F_Cu
                            tr = add_track(
                                board, kl, ax, ay, bx, by, w, net_items[net_name]
                            )
                            v_tracks.append(tr)
                            router.mark_segment(p_a[0], ax, ay, bx, by, w, nc)
                    via_obj = emit_via_once(vgx, vgy, net_name, nc)
                    pre_vias.setdefault(net_name, []).append((pin_b, vgx, vgy))
                    pre_via_records.setdefault(net_name, []).append(
                        (vgx, vgy, via_obj, v_tracks)
                    )

    # 6. Pre-place immediate B.Cu SMD GND stitching vias (prevents boxing in GND pads)
    for ref, pad, cx, cy, x0, y0, x1, y1, layers in all_pads_by_net.get(gnd_nc, []):
        if pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
            continue
        pnum = pad.GetNumber()
        lid, gx, gy, _, _ = pad_anchors[(ref, pnum)]
        sx, sy = router.to_mm(gx, gy)
        # Search local offsets (within 2.0 mm) for a clean stitching via
        best_via: tuple[float, int, int] | None = None
        for r_step in range(2, 9):
            for dy in range(-r_step, r_step + 1):
                for dx in range(-r_step, r_step + 1):
                    vgx, vgy = gx + dx, gy + dy
                    if not (0 <= vgx < router.nx and 0 <= vgy < router.ny):
                        continue
                    if not router.can_place_via(vgx, vgy, gnd_nc):
                        continue
                    vx, vy = router.to_mm(vgx, vgy)
                    d2 = (vx - sx) ** 2 + (vy - sy) ** 2
                    if d2 > 4.5:
                        continue
                    if best_via is None or d2 < best_via[0]:
                        best_via = (d2, vgx, vgy)
        if best_via is not None:
            _, vgx, vgy = best_via
            path = router.route(
                [(lid, gx, gy)], {(lid, vgx, vgy)}, gnd_nc, preferred_layer=1
            )
            if path is not None:
                ensure_pad_stub(ref, pnum, "GND", gnd_nc)
                merged = _merge_collinear_path(path)
                for p_a, p_b in _iter_pairs(merged):
                    if p_a[0] == p_b[0]:
                        ax, ay = router.to_mm(p_a[1], p_a[2])
                        bx, by = router.to_mm(p_b[1], p_b[2])
                        kl = pcbnew.B_Cu if p_a[0] == 1 else pcbnew.F_Cu
                        add_track(
                            board, kl, ax, ay, bx, by, POWER_WIDTH, net_items["GND"]
                        )
                        router.mark_segment(p_a[0], ax, ay, bx, by, POWER_WIDTH, gnd_nc)
                emit_via_once(vgx, vgy, "GND", gnd_nc)

    # 7. Sort remaining non-GND nets: IC breakouts (-1) -> Power (0) -> Signals (1)
    net_jobs: list[tuple[int, float, dict]] = []
    for net_def in nets:
        name = net_def["name"]
        if name == "GND" or len(net_def["nodes"]) < 2:
            continue
        xs = [pad_lookup[(r, p)][1] for r, p in net_def["nodes"]]
        ys = [pad_lookup[(r, p)][2] for r, p in net_def["nodes"]]
        span = (max(xs) - min(xs)) + (max(ys) - min(ys))
        if name in BREAKOUT_NETS:
            prio = -1
        elif name in POWER_RAILS:
            prio = 0
        else:
            prio = 1
        net_jobs.append((prio, span, net_def))

    net_jobs.sort(key=lambda item: (item[0], item[1], item[2]["name"]))

    unrouted_branches: list[str] = []
    for _, _, net_def in net_jobs:
        name = net_def["name"]
        ni = net_items[name]
        nc = ni.GetNetCode()
        w = POWER_WIDTH if name in POWER_RAILS else SIGNAL_WIDTH
        nodes = list(net_def["nodes"])

        # Union-find over pre-connected pairs
        parent = {nd: nd for nd in nodes}

        def find(
            x: tuple[str, str],
            p_map: dict[tuple[str, str], tuple[str, str]] = parent,
        ) -> tuple[str, str]:
            while p_map[x] != x:
                p_map[x] = p_map[p_map[x]]
                x = p_map[x]
            return x

        for pa, pb in pre_connected.get(name, []):
            if pa in parent and pb in parent:
                ra, rb = find(pa), find(pb)
                if ra != rb:
                    parent[rb] = ra

        # Build MST edges among components
        edges: list[tuple[float, tuple[str, str], tuple[str, str]]] = []
        for i, na in enumerate(nodes):
            _, cxa, cya, *_ = pad_lookup[na]
            for nb in nodes[i + 1 :]:
                _, cxb, cyb, *_ = pad_lookup[nb]
                edges.append((math.hypot(cxa - cxb, cya - cyb), na, nb))
        edges.sort(key=lambda e: e[0])

        # Maintain copper vertices per connected cluster
        cluster_pts: dict[tuple[str, str], list[tuple[int, int, int]]] = {}
        for nd in nodes:
            if nd in direct_pin_merged:
                continue
            la, gxa, gya, *_ = pad_anchors[nd]
            is_tht = pad_lookup[nd][0].GetAttribute() in (
                pcbnew.PAD_ATTRIB_PTH,
                pcbnew.PAD_ATTRIB_NPTH,
            )
            pts = [(0, gxa, gya), (1, gxa, gya)] if is_tht else [(la, gxa, gya)]
            cluster_pts.setdefault(find(nd), []).extend(pts)

        branches: list[list[tuple[int, int, int]]] = []
        junctions: set[tuple[int, int, int]] = set()
        for nd, vgx, vgy in pre_vias.get(name, []):
            root_nd = find(nd)
            cluster_pts[root_nd].extend([(0, vgx, vgy), (1, vgx, vgy)])
            junctions.add((0, vgx, vgy))
            junctions.add((1, vgx, vgy))

        pref_layer = 0 if name in POWER_RAILS else 1
        for _, na, nb in edges:
            ra, rb = find(na), find(nb)
            if ra == rb:
                continue
            starts = cluster_pts[ra]
            targets = set(cluster_pts[rb])
            path = router.route(starts, targets, nc, preferred_layer=pref_layer)
            if path is None:
                unrouted_branches.append(f"{name}: {na} -> {nb}")
                continue
            # Immediately mark segments/vias so subsequent branches can tap T-junctions
            for p_a, p_b in _iter_pairs(path):
                if p_a[0] == p_b[0]:
                    ax, ay = router.to_mm(p_a[1], p_a[2])
                    bx, by = router.to_mm(p_b[1], p_b[2])
                    router.mark_segment(p_a[0], ax, ay, bx, by, w, nc)
                else:
                    vx, vy = router.to_mm(p_a[1], p_a[2])
                    if router.tht_pad_grid.get((p_a[1], p_a[2])) != nc:
                        router.mark_via_obstacle(
                            vx,
                            vy,
                            VIA_DIAM * 0.5 + TRACK_CLEARANCE + POWER_WIDTH * 0.5,
                            nc,
                        )
            branches.append(path)
            junctions.add(path[0])
            junctions.add(path[-1])

            parent[rb] = ra
            merged_pts = cluster_pts[ra] + cluster_pts.pop(rb)
            for pt in path:
                merged_pts.append(pt)
            cluster_pts[ra] = list(dict.fromkeys(merged_pts))

        # Emit pad stubs only for pads actually connected by MST branches
        used_pts: set[tuple[int, int, int]] = set()
        for path in branches:
            used_pts.update(path)
        for nd in nodes:
            if nd in direct_pin_merged:
                continue
            la, gxa, gya, *_ = pad_anchors[nd]
            if (
                (la, gxa, gya) in used_pts
                or (0, gxa, gya) in used_pts
                or (1, gxa, gya) in used_pts
            ):
                ensure_pad_stub(nd[0], nd[1], name, nc)

        # Prune pre-placed supply lift vias that MST branches did not tap on F.Cu
        for vgx, vgy, via_obj, v_tracks in pre_via_records.get(name, []):
            if (0, vgx, vgy) not in used_pts:
                if via_obj is not None:
                    board.Remove(via_obj)
                    emitted_vias.discard((vgx, vgy))
                if (1, vgx, vgy) not in used_pts:
                    for tr in v_tracks:
                        board.Remove(tr)

        # Emit merged collinear tracks preserving all T-junctions
        for path in branches:
            merged = _merge_collinear_path(path, junctions)
            for p_a, p_b in _iter_pairs(merged):
                if p_a[0] == p_b[0]:
                    ax, ay = router.to_mm(p_a[1], p_a[2])
                    bx, by = router.to_mm(p_b[1], p_b[2])
                    kl = pcbnew.B_Cu if p_a[0] == 1 else pcbnew.F_Cu
                    add_track(board, kl, ax, ay, bx, by, w, ni)
                else:
                    emit_via_once(p_a[1], p_a[2], name, nc)

    # Ensure TP3 GND test point connects via thermal-relief spokes rather than solid flood
    if "TP3" in footprints:
        for pad in footprints["TP3"].Pads():
            pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_THERMAL)

    if unrouted_branches:
        print("UNROUTED BRANCHES:")
        for ub in unrouted_branches:
            print("  ", ub)
        raise RuntimeError(f"Failed to route {len(unrouted_branches)} branch(es)")

    # 8. Add board-wide GND stitching vias in open spaces before pouring zones
    for vy in (8.0, 15.0, 23.0, 35.0, 42.5, 50.0, 60.0, 70.0, 79.0, 86.0, 96.5, 103.5):
        for vx in (3.5, 15.0, 26.5):
            gx, gy = router.to_grid(vx, vy)
            if router.can_place_via(gx, gy, gnd_nc):
                emit_via_once(gx, gy, "GND", gnd_nc)

    # 9. Pour F.Cu and B.Cu GND zones with thermal-relief spokes & refill twice
    zx0, zy0 = EDGE_CLEARANCE, EDGE_CLEARANCE
    zx1, zy1 = BOARD_W - EDGE_CLEARANCE, BOARD_H - EDGE_CLEARANCE
    for layer_id in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer_id)
        zone.SetNet(net_items["GND"])
        zone.SetLocalClearance(pcbnew.FromMM(TRACK_CLEARANCE))
        zone.SetMinThickness(pcbnew.FromMM(0.20))
        zone.SetThermalReliefGap(pcbnew.FromMM(0.25))
        zone.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.30))
        if hasattr(pcbnew, "ISLAND_REMOVAL_MODE_ALWAYS"):
            zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        outline = zone.Outline()
        outline.NewOutline()
        for px, py in ((zx0, zy0), (zx1, zy0), (zx1, zy1), (zx0, zy1)):
            outline.Append(pcbnew.VECTOR2I(pcbnew.FromMM(px), pcbnew.FromMM(py)))
        board.Add(zone)

    board.BuildConnectivity()
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.BuildConnectivity()


def _place_board_silk_local(
    grid: SilkGrid,
    board: pcbnew.BOARD,
    fp: pcbnew.FOOTPRINT,
    text: str,
    side: int,
    *,
    height: float = SILK_HEIGHT,
    thickness: float = SILK_THICKNESS,
    max_edge_dist: float = 6.0,
    step: float = 0.35,
    attach_to_fp: bool = True,
    rotations: tuple[float, ...] = (0.0, 90.0),
) -> tuple[float, float, float] | None:
    """Place an auxiliary silkscreen label within local tether distance of `fp`."""
    silk_layer = pcbnew.B_SilkS if side == 1 else pcbnew.F_SilkS
    mirrored = side == 1
    fp_box = footprint_bbox(fp)
    pos = fp.GetPosition()
    cx, cy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
    tw, th = grid.measure_text(text, height, thickness)
    margin = max(tw, th) * 0.5 + 0.25
    ix0 = math.floor((fp_box[0] - max_edge_dist - margin - cx) / step)
    ix1 = math.ceil((fp_box[2] + max_edge_dist + margin - cx) / step)
    iy0 = math.floor((fp_box[1] - max_edge_dist - margin - cy) / step)
    iy1 = math.ceil((fp_box[3] + max_edge_dist + margin - cy) / step)

    candidates: list[
        tuple[
            float,
            float,
            float,
            int,
            float,
            float,
            float,
            tuple[float, float, float, float],
        ]
    ] = []
    for iy in range(iy0, iy1 + 1):
        ty = cy + iy * step
        for ix in range(ix0, ix1 + 1):
            tx = cx + ix * step
            d2 = (tx - cx) ** 2 + (ty - cy) ** 2
            for deg_idx, deg in enumerate(rotations):
                box = _make_box(tx, ty, tw, th, deg)
                ed = box_edge_distance(fp_box, box)
                if ed <= max_edge_dist:
                    candidates.append(
                        (round(ed, 4), d2, abs(ty - cy), deg_idx, tx, ty, deg, box)
                    )
    candidates.sort()
    for _, _, _, _, tx, ty, deg, box in candidates:
        if grid.box_ok(side, *box):
            parent: pcbnew.BOARD | pcbnew.FOOTPRINT = fp if attach_to_fp else board
            add_silk_text(
                parent, silk_layer, text, tx, ty, deg, height, thickness, mirrored
            )
            grid.reserve(side, *box)
            return (tx, ty, deg)
    return None


def _place_point_silk(
    grid: SilkGrid,
    parent: pcbnew.BOARD | pcbnew.FOOTPRINT,
    side: int,
    text: str,
    target_x: float,
    target_y: float,
    *,
    height: float = 0.80,
    thickness: float = 0.15,
    max_dist: float = 3.0,
    step: float = 0.25,
) -> tuple[float, float] | None:
    """Place a short polarity marker ('+', '-', '1') as close as possible to (target_x, target_y)."""
    silk_layer = pcbnew.B_SilkS if side == 1 else pcbnew.F_SilkS
    mirrored = side == 1
    tw, th = grid.measure_text(text, height, thickness)
    r_steps = math.ceil(max_dist / step)
    candidates: list[tuple[float, float, float, tuple[float, float, float, float]]] = []
    for iy in range(-r_steps, r_steps + 1):
        ty = target_y + iy * step
        for ix in range(-r_steps, r_steps + 1):
            tx = target_x + ix * step
            d2 = (tx - target_x) ** 2 + (ty - target_y) ** 2
            if d2 <= max_dist * max_dist:
                box = _make_box(tx, ty, tw, th, 0.0)
                candidates.append((d2, abs(ty - target_y), tx, box))
    candidates.sort()
    for _, _, tx, box in candidates:
        ty = (box[1] + box[3]) * 0.5
        if grid.box_ok(side, *box):
            add_silk_text(
                parent, silk_layer, text, tx, ty, 0.0, height, thickness, mirrored
            )
            grid.reserve(side, *box)
            return (tx, ty)
    return None


def _get_fp_field(fp: pcbnew.FOOTPRINT, field_name: str) -> str:
    """Return trimmed text of custom footprint field `field_name`, or empty string."""
    for fld in fp.GetFields():
        if fld.GetName() == field_name:
            return fld.GetText().strip()
    return ""


def _parse_silkscreen_spec(fp: pcbnew.FOOTPRINT) -> tuple[str, str]:
    """Derive (full_label, secondary_value_or_func) directly from netlist `Silkscreen` field."""
    ref = fp.GetReference().strip()
    spec = _get_fp_field(fp, "Silkscreen")
    if spec:
        if is_passive_ref(ref):
            return spec, spec
        tokens = spec.split(None, 1)
        if tokens[0] == ref:
            return spec, (tokens[1] if len(tokens) > 1 else "")
        return f"{ref} {spec}".strip(), spec
    val = fp.GetValue().strip()
    if is_passive_ref(ref):
        return val, val
    return f"{ref} {val}".strip(), val


def _bbox_mm(bb: pcbnew.BOX2I) -> tuple[float, float, float, float]:
    return (
        pcbnew.ToMM(bb.GetLeft()),
        pcbnew.ToMM(bb.GetTop()),
        pcbnew.ToMM(bb.GetRight()),
        pcbnew.ToMM(bb.GetBottom()),
    )


def _pad_mask_margin_mm(pad: pcbnew.PAD, default_margin: float = 0.05) -> float:
    mclr = pad.GetLocalSolderMaskMargin()
    if mclr is not None and mclr > 0:
        return pcbnew.ToMM(mclr)
    return default_margin


def _fp_fab_bbox_mm(
    fp: pcbnew.FOOTPRINT, side: int | None = None
) -> tuple[float, float, float, float] | None:
    """Return tight mounting-side .Fab body bounding box in mm, or None if no Fab shapes."""
    if side is None:
        side = 1 if fp.IsFlipped() else 0
    fab_layer = pcbnew.B_Fab if side == 1 else pcbnew.F_Fab
    xs: list[float] = []
    ys: list[float] = []
    for gi in fp.GraphicalItems():
        if hasattr(gi, "GetText") or gi.GetLayer() != fab_layer:
            continue
        x0, y0, x1, y1 = _bbox_mm(gi.GetBoundingBox())
        xs.extend((x0, x1))
        ys.extend((y0, y1))
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def _seed_extra_keepouts(
    grid: SilkGrid,
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
    fids: dict[str, pcbnew.FOOTPRINT],
) -> None:
    """Seed SilkGrid with solder-mask margins (F.Mask/B.Mask + 0.25mm) and THT .Fab bodies."""
    ds = board.GetDesignSettings()
    board_mask = (
        pcbnew.ToMM(ds.m_SolderMaskMargin)
        if hasattr(ds, "m_SolderMaskMargin") and ds.m_SolderMaskMargin > 0
        else 0.05
    )
    pad_pad = 0.25
    for fp in (*footprints.values(), *fids.values()):
        for pad in fp.Pads():
            _, _, x0, y0, x1, y1, layers = extract_pad_geometry(pad)
            mask_exp = _pad_mask_margin_mm(pad, board_mask)
            exp = mask_exp + pad_pad
            lset = pad.GetLayerSet()
            if 0 in layers or lset.Contains(pcbnew.F_Mask):
                grid.keepout[0].append((x0 - exp, y0 - exp, x1 + exp, y1 + exp))
            if 1 in layers or lset.Contains(pcbnew.B_Mask):
                grid.keepout[1].append((x0 - exp, y0 - exp, x1 + exp, y1 + exp))

        ref = fp.GetReference()
        if is_fiducial_ref(ref) or is_smd_footprint(fp):
            continue
        fp_side = 1 if fp.IsFlipped() else 0
        fab_bb = _fp_fab_bbox_mm(fp, fp_side)
        if fab_bb is not None:
            grid.keepout[fp_side].append(
                (
                    fab_bb[0] - 0.05,
                    fab_bb[1] - 0.05,
                    fab_bb[2] + 0.05,
                    fab_bb[3] + 0.05,
                )
            )


def _place_checked_dot(
    grid: SilkGrid,
    board: pcbnew.BOARD,
    side: int,
    targets: Sequence[tuple[float, float]],
    *,
    radius: float,
    max_search: float = 1.0,
    step: float = 0.15,
) -> tuple[float, float] | None:
    """Place a filled Pin-1 silkscreen dot verified clear in SilkGrid and reserve it."""
    silk_layer = pcbnew.B_SilkS if side == 1 else pcbnew.F_SilkS
    half_bb = radius + 0.075  # 0.15 mm stroke half-width included in KiCad bbox
    r_steps = math.ceil(max_search / step)
    for tx0, ty0 in targets:
        candidates: list[tuple[float, float, float]] = []
        for iy in range(-r_steps, r_steps + 1):
            cy = ty0 + iy * step
            for ix in range(-r_steps, r_steps + 1):
                cx = tx0 + ix * step
                d2 = (cx - tx0) ** 2 + (cy - ty0) ** 2
                if d2 <= max_search * max_search:
                    candidates.append((d2, cx, cy))
        candidates.sort()
        for _, cx, cy in candidates:
            box = (cx - half_bb, cy - half_bb, cx + half_bb, cy + half_bb)
            if grid.box_ok(side, *box):
                add_silk_dot(board, silk_layer, cx, cy, radius=radius)
                grid.reserve(side, *box)
                return (cx, cy)
    return None


def _place_checked_seg(
    grid: SilkGrid,
    board: pcbnew.BOARD,
    side: int,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    *,
    width: float,
) -> bool:
    """Place a silkscreen bar/segment if clear in SilkGrid and reserve its footprint."""
    silk_layer = pcbnew.B_SilkS if side == 1 else pcbnew.F_SilkS
    hw = width * 0.5
    box = (min(x0, x1) - hw, min(y0, y1) - hw, max(x0, x1) + hw, max(y0, y1) + hw)
    if not grid.box_ok(side, *box):
        return False
    add_silk_seg(board, silk_layer, x0, y0, x1, y1, width=width)
    grid.reserve(side, *box)
    return True


def _j4_rail_callouts(fp_j4: pcbnew.FOOTPRINT, side: int) -> list[tuple[str, float]]:
    """Derive J4 rail callout strings and X-centers directly from J4 pad net assignments."""
    groups: dict[str, list[float]] = {}
    for pad in fp_j4.Pads():
        net_name = pad.GetNetname().strip()
        if not net_name:
            continue
        px = pcbnew.ToMM(pad.GetPosition().x)
        groups.setdefault(net_name, []).append(px)
    callouts: list[tuple[str, float]] = []
    for net_name, xs in sorted(groups.items(), key=lambda kv: sum(kv[1]) / len(kv[1])):
        cx = sum(xs) / len(xs)
        base = net_name.removesuffix("_IN")
        label = f"{base} RED" if (side == 1 and base == "-12V") else base
        callouts.append((label, cx))
    return callouts


def _verify_silkscreen_and_polarity(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
    polarity_shapes: list[tuple[str, int, tuple[float, float, float, float]]],
) -> None:
    """Assert netlist Silkscreen field compliance, clearances, and polarized markers."""
    ds = board.GetDesignSettings()
    board_mask = (
        pcbnew.ToMM(ds.m_SolderMaskMargin)
        if hasattr(ds, "m_SolderMaskMargin") and ds.m_SolderMaskMargin > 0
        else 0.05
    )

    # 1. Verify every non-fiducial footprint carries its expected Silkscreen field tokens
    for ref, fp in sorted(footprints.items()):
        if is_fiducial_ref(ref):
            continue
        full_spec, val_part = _parse_silkscreen_spec(fp)
        vis_texts: dict[int, list[str]] = {0: [], 1: []}
        ref_fld = fp.Reference()
        if ref_fld.IsVisible() and ref_fld.GetLayer() in (
            pcbnew.F_SilkS,
            pcbnew.B_SilkS,
        ):
            s = 0 if ref_fld.GetLayer() == pcbnew.F_SilkS else 1
            vis_texts[s].append(ref_fld.GetText().strip())
        if fp.Value().IsVisible() and fp.Value().GetLayer() in (
            pcbnew.F_SilkS,
            pcbnew.B_SilkS,
        ):
            raise RuntimeError(f"Raw fp.Value() visible on silkscreen for {ref}")
        for gi in fp.GraphicalItems():
            if hasattr(gi, "GetText") and gi.GetLayer() in (
                pcbnew.F_SilkS,
                pcbnew.B_SilkS,
            ):
                s = 0 if gi.GetLayer() == pcbnew.F_SilkS else 1
                vis_texts[s].append(gi.GetText().strip())

        prim_side = 1 if fp.IsFlipped() else 0
        joined_prim = " ".join(vis_texts[prim_side])
        if is_passive_ref(ref):
            if full_spec not in vis_texts[prim_side]:
                raise RuntimeError(
                    f"Passive {ref} missing Silkscreen '{full_spec}' on primary side: {vis_texts[prim_side]}"
                )
        else:
            if ref not in vis_texts[prim_side] or (
                val_part and val_part not in joined_prim
            ):
                raise RuntimeError(
                    f"Component {ref} missing '{ref} {val_part}' on primary side: {vis_texts[prim_side]}"
                )
            if not is_smd_footprint(fp):
                sec_side = 1 - prim_side
                joined_sec = " ".join(vis_texts[sec_side])
                if full_spec not in joined_sec:
                    raise RuntimeError(
                        f"THT {ref} missing secondary label '{full_spec}': {vis_texts[sec_side]}"
                    )

    # 2. Verify all required text polarity/rail marks exist on the expected layers
    def _has_fp_txt(ref: str, side: int, token: str) -> bool:
        lyr = pcbnew.B_SilkS if side == 1 else pcbnew.F_SilkS
        fp = footprints[ref]
        return any(
            hasattr(gi, "GetText") and gi.GetLayer() == lyr and gi.GetText() == token
            for gi in fp.GraphicalItems()
        )

    for c_ref in ("C3", "C4"):
        for pol in ("+", "-"):
            if not _has_fp_txt(c_ref, 1, pol):
                raise RuntimeError(f"Missing external '{pol}' on B.SilkS for {c_ref}")
    for side in (0, 1):
        for pol in ("+", "-"):
            if not _has_fp_txt("D4", side, pol):
                raise RuntimeError(f"Missing '{pol}' on side={side} for LED D4")
        for rv_ref in ("RV1", "RV2", "RV3", "RV4"):
            if not _has_fp_txt(rv_ref, side, "1"):
                raise RuntimeError(f"Missing Pin-1 '1' on side={side} for {rv_ref}")
    for rail in ("-12V RED", "GND", "+12V"):
        if not _has_fp_txt("J4", 1, rail):
            raise RuntimeError(f"Missing J4 B.SilkS rail label '{rail}'")
    for rail in ("-12V", "GND", "+12V"):
        if not _has_fp_txt("J4", 0, rail):
            raise RuntimeError(f"Missing J4 F.SilkS rail label '{rail}'")

    # 3. Verify all polarity graphics + silk texts clear masks (>=0.25mm), Fab bodies, and edges (>=0.45mm)
    mask_boxes: dict[int, list[tuple[str, tuple[float, float, float, float]]]] = {
        0: [],
        1: [],
    }
    fab_boxes: dict[int, list[tuple[str, tuple[float, float, float, float]]]] = {
        0: [],
        1: [],
    }
    for ref, fp in footprints.items():
        fp_side = 1 if fp.IsFlipped() else 0
        if not is_fiducial_ref(ref):
            fbb = _fp_fab_bbox_mm(fp, fp_side)
            if fbb is not None:
                fab_boxes[fp_side].append((ref, fbb))
        for pad in fp.Pads():
            _, _, x0, y0, x1, y1, layers = extract_pad_geometry(pad)
            mexp = _pad_mask_margin_mm(pad, board_mask)
            mbb = (x0 - mexp, y0 - mexp, x1 + mexp, y1 + mexp)
            lset = pad.GetLayerSet()
            if 0 in layers or lset.Contains(pcbnew.F_Mask):
                mask_boxes[0].append((f"{ref}.{pad.GetNumber()}", mbb))
            if 1 in layers or lset.Contains(pcbnew.B_Mask):
                mask_boxes[1].append((f"{ref}.{pad.GetNumber()}", mbb))

    check_items: list[tuple[str, int, tuple[float, float, float, float]]] = list(
        polarity_shapes
    )
    for ref, fp in footprints.items():
        for it in (fp.Reference(), *fp.GraphicalItems()):
            if hasattr(it, "GetText") and (
                not hasattr(it, "IsVisible") or it.IsVisible()
            ):
                lyr = it.GetLayer()
                if lyr in (pcbnew.F_SilkS, pcbnew.B_SilkS):
                    s = 0 if lyr == pcbnew.F_SilkS else 1
                    check_items.append(
                        (f"{ref}:{it.GetText()}", s, _bbox_mm(it.GetBoundingBox()))
                    )
    for dr in board.GetDrawings():
        if (
            hasattr(dr, "GetText")
            and dr.IsVisible()
            and dr.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)
        ):
            s = 0 if dr.GetLayer() == pcbnew.F_SilkS else 1
            check_items.append(
                (f"BOARD:{dr.GetText()}", s, _bbox_mm(dr.GetBoundingBox()))
            )

    violations: list[str] = []
    for name, side, bb in check_items:
        ed = min(bb[0], BOARD_W - bb[2], bb[1], BOARD_H - bb[3])
        if ed < SILK_EDGE_CLEARANCE - 0.005:
            violations.append(f"EDGE({ed:.3f}mm) {name} side={side}")
        for pname, mbb in mask_boxes[side]:
            d = box_edge_distance(bb, mbb)
            if d < 0.25 - 0.005:
                violations.append(f"MASK({d:.3f}mm) {name} vs {pname} side={side}")
        for fref, fbb in fab_boxes[side]:
            d = box_edge_distance(bb, fbb)
            if d < 0.045:
                violations.append(
                    f"FAB_BODY({d:.3f}mm) {name} inside {fref} side={side}"
                )
    if violations:
        raise RuntimeError(f"Silkscreen/polarity verification failed: {violations}")


def apply_silkscreen_and_fab(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
    fids: dict[str, pcbnew.FOOTPRINT],
) -> None:
    """Apply SilkscreenInstructions.md & netlist-driven silkscreen and B.Fab markup."""
    # Hide all default Reference/Value fields first so SilkGrid isn't polluted
    for fp in (*footprints.values(), *fids.values()):
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)

    grid = SilkGrid(
        board,
        footprints={**footprints, **fids},
        board_bounds=(0.0, 0.0, BOARD_W, BOARD_H),
        edge_clearance=SILK_EDGE_CLEARANCE,
    )
    _seed_extra_keepouts(grid, board, footprints, fids)

    # Reserve JLCPCB 5x5 mm QR square on B.SilkS and draw it (0.10 + 0.20 grid margin = 0.30 mm)
    qx0, qy0, qx1, qy1 = QR_BOX
    add_silk_rect(board, pcbnew.B_SilkS, qx0, qy0, qx1, qy1, filled=True, width=0.15)
    grid.reserve(1, qx0 - 0.10, qy0 - 0.10, qx1 + 0.10, qy1 + 0.10)

    failed_labels: list[str] = []
    polarity_shapes: list[tuple[str, int, tuple[float, float, float, float]]] = []

    # ------------------------------------------------------------------
    # Polarity & Orientation Graphics (Grid-Checked Outside Bodies & Masks)
    # ------------------------------------------------------------------
    # 1. U1, U2 Pin-1 solid dots (Ø 0.5 mm, r=0.25) outside Pin 1 & B.Fab/B.SilkS
    for ic_ref in ("U1", "U2"):
        fp = footprints[ic_ref]
        p1 = fp.FindPadByNumber("1").GetPosition()
        p1x, p1y = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        rot = fp.GetOrientation().AsDegrees() % 360.0
        if ic_ref == "U2" and rot == 180.0:
            # Place cleanly between U2.1, U2 Pin-1 corner, and TP8 pad keepout
            targets = [(23.835, 51.80), (p1x + 1.20, p1y - 1.15)]
        elif rot == 180.0:
            targets = [(p1x + 1.20, p1y - 1.15), (p1x + 1.10, p1y - 1.30)]
        elif rot == 270.0:
            targets = [(p1x - 1.15, p1y - 1.15)]
        else:
            targets = [(p1x - 1.25, p1y + 1.35), (p1x - 1.05, p1y + 1.45)]
        placed = _place_checked_dot(
            grid,
            board,
            1,
            targets,
            radius=0.25,
            max_search=0.90,
            step=0.05 if ic_ref == "U2" else 0.10,
        )
        if placed is None:
            failed_labels.append(f"{ic_ref} Pin-1 dot")
        else:
            r_bb = 0.25 + 0.075
            polarity_shapes.append(
                (
                    f"{ic_ref}:PIN1_DOT",
                    1,
                    (
                        placed[0] - r_bb,
                        placed[1] - r_bb,
                        placed[0] + r_bb,
                        placed[1] + r_bb,
                    ),
                )
            )

    # 2. Discrete diodes (D1-D3, D5-D8): bold 0.25 mm cathode (K) bar outside Pad 1 (K)
    for d_ref in ("D1", "D2", "D3", "D5", "D6", "D7", "D8"):
        fp = footprints[d_ref]
        p1 = fp.FindPadByNumber("1").GetPosition()
        p2 = fp.FindPadByNumber("2").GetPosition()
        p1x, p1y = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        p2x, p2y = pcbnew.ToMM(p2.x), pcbnew.ToMM(p2.y)
        vx, vy = p1x - p2x, p1y - p2y
        length = math.hypot(vx, vy) or 1.0
        ux, uy = vx / length, vy / length
        px_n, py_n = -uy, ux
        bx = p1x + ux * 0.95
        by = p1y + uy * 0.95
        x0, y0 = bx - px_n * 0.65, by - py_n * 0.65
        x1, y1 = bx + px_n * 0.65, by + py_n * 0.65
        if not _place_checked_seg(grid, board, 1, x0, y0, x1, y1, width=0.25):
            failed_labels.append(f"{d_ref} K-bar")
        else:
            polarity_shapes.append(
                (
                    f"{d_ref}:K_BAR",
                    1,
                    (
                        min(x0, x1) - 0.125,
                        min(y0, y1) - 0.125,
                        max(x0, x1) + 0.125,
                        max(y0, y1) + 0.125,
                    ),
                )
            )

    # 3. Multi-pin diodes BAT54S (D9-D11): Ø 0.4 mm Pin-1 dot outside Pin 1 (away from Pin 2)
    for d_ref in ("D9", "D10", "D11"):
        fp = footprints[d_ref]
        p1 = fp.FindPadByNumber("1").GetPosition()
        p2 = fp.FindPadByNumber("2").GetPosition()
        p1x, p1y = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        p2x, p2y = pcbnew.ToMM(p2.x), pcbnew.ToMM(p2.y)
        vx, vy = p1x - p2x, p1y - p2y
        if abs(vx) >= abs(vy):
            ux = 1.0 if vx >= 0 else -1.0
            targets = [(p1x + ux * 1.25, p1y)]
        else:
            uy = 1.0 if vy >= 0 else -1.0
            targets = [(p1x, p1y + uy * 1.25)]
        placed = _place_checked_dot(
            grid, board, 1, targets, radius=0.20, max_search=0.60, step=0.10
        )
        if placed is None:
            failed_labels.append(f"{d_ref} Pin-1 dot")
        else:
            r_bb = 0.20 + 0.075
            polarity_shapes.append(
                (
                    f"{d_ref}:PIN1_DOT",
                    1,
                    (
                        placed[0] - r_bb,
                        placed[1] - r_bb,
                        placed[0] + r_bb,
                        placed[1] + r_bb,
                    ),
                )
            )

    # 4. J4 -12V / RED STRIPE bar along Pins 1-2 edge OUTSIDE J4 shroud on BOTH B.SilkS & F.SilkS
    fp_j4 = footprints["J4"]
    j4_p1 = fp_j4.FindPadByNumber("1").GetPosition()
    j4_p2 = fp_j4.FindPadByNumber("2").GetPosition()
    j4_p1x, j4_p1y = pcbnew.ToMM(j4_p1.x), pcbnew.ToMM(j4_p1.y)
    j4_p2y = pcbnew.ToMM(j4_p2.y)
    j4_fab = _fp_fab_bbox_mm(fp_j4, 1)
    assert j4_fab is not None
    stripe_x = round(
        j4_fab[0] - 0.50, 2
    )  # cleanly outside J4 shroud & >=0.50mm from edge
    sy_min = min(j4_p1y, j4_p2y) - 0.40
    sy_max = max(j4_p1y, j4_p2y) + 0.40
    for side in (0, 1):
        if not _place_checked_seg(
            grid, board, side, stripe_x, sy_min, stripe_x, sy_max, width=0.30
        ):
            failed_labels.append(f"J4 RED stripe side={side}")
        else:
            polarity_shapes.append(
                (
                    "J4:RED_STRIPE",
                    side,
                    (stripe_x - 0.15, sy_min - 0.15, stripe_x + 0.15, sy_max + 0.15),
                )
            )
    # J4 Pin-1 dot outside J4 shroud near Pins 1-2
    j4_dot_targets = [
        (j4_p1x - 1.15, j4_fab[1] - 0.90),
        (stripe_x, sy_min - 0.85),
    ]
    j4_dot = _place_checked_dot(
        grid, board, 1, j4_dot_targets, radius=0.25, max_search=0.60, step=0.10
    )
    if j4_dot is None:
        failed_labels.append("J4 B.SilkS Pin-1 dot")
    else:
        r_bb = 0.25 + 0.075
        polarity_shapes.append(
            (
                "J4:PIN1_DOT",
                1,
                (
                    j4_dot[0] - r_bb,
                    j4_dot[1] - r_bb,
                    j4_dot[0] + r_bb,
                    j4_dot[1] + r_bb,
                ),
            )
        )

    # ------------------------------------------------------------------
    # Place Primary & Secondary Silkscreen Labels Derived From Netlist `Silkscreen` Fields
    # ------------------------------------------------------------------
    # Active ICs & Diodes (B.Cu, <REF> + <VAL> from netlist `Silkscreen` field)
    # Keep U1/U2 horizontal so their labels don't block C7/C8 decoupling slots;
    # place D8 after J4 rail callouts & TP2 so '-12V RED' and TP2 retain clean alignment.
    for ref in (
        "U1",
        "U2",
        "D1",
        "D2",
        "D3",
        "D5",
        "D6",
        "D7",
        "D9",
        "D10",
        "D11",
    ):
        fp = footprints[ref]
        _, val_part = _parse_silkscreen_spec(fp)
        rots = (0.0,) if ref in ("U1", "U2") else (0.0, 90.0)
        center_override = (19.90, 56.60) if ref == "U2" else None
        step_val = 0.15 if ref == "U2" else 0.25
        res = place_ref_val_pair(
            grid,
            fp,
            val_part,
            side=1,
            center=center_override,
            val_only=False,
            step=step_val,
            max_edge_distance=3.5,
            rotations=rots,
        )
        if res is None:
            failed_labels.append(f"{ref} ({val_part})")

    # J4 Power Header rail callouts first so '-12V RED', 'GND', '+12V' sit aligned over their pins
    j4_full_spec, j4_val = _parse_silkscreen_spec(fp_j4)
    for lbl_txt, tx_target in _j4_rail_callouts(fp_j4, side=1):
        eff_x = tx_target - 1.38 if lbl_txt == "-12V RED" else tx_target
        target_y = 95.50 if lbl_txt == "-12V RED" else 96.68
        if (
            _place_point_silk(
                grid, fp_j4, 1, lbl_txt, eff_x, target_y, max_dist=3.5, step=0.15
            )
            is None
        ):
            failed_labels.append(f"B.SilkS J4 {lbl_txt}")

    # Test Points TP1-TP8 on B.SilkS & F.SilkS before decoupling caps C5-C8 and J4 PWR
    # (exact netlist `Silkscreen` net names, no truncation)
    for idx in range(1, 9):
        tp_ref = f"TP{idx}"
        fp = footprints[tp_ref]
        tp_spec, tp_val = _parse_silkscreen_spec(fp)
        b_center = (4.10, 84.00) if tp_ref == "TP2" else None
        b_rots = (90.0,) if tp_ref == "TP2" else (0.0, 90.0)
        b_res = place_ref_val_pair(
            grid,
            fp,
            tp_val,
            side=1,
            center=b_center,
            val_only=False,
            step=0.15,
            max_edge_distance=5.5,
            rotations=b_rots,
        )
        if b_res is None:
            failed_labels.append(f"B.SilkS {tp_spec}")
        if (
            _place_board_silk_local(
                grid, board, fp, tp_spec, side=0, max_edge_dist=6.0, step=0.25
            )
            is None
        ):
            failed_labels.append(f"F.SilkS {tp_spec}")

    # D8 diode label (Cols 1 & 2 bottom beside TP2 above D8)
    fp_d8 = footprints["D8"]
    _, d8_val = _parse_silkscreen_spec(fp_d8)
    d8_val_res = place_val_only(
        grid,
        fp_d8,
        d8_val,
        side=1,
        center=(1.25, 85.10),
        step=0.10,
        max_edge_distance=3.5,
        compact=False,
        rotations=(90.0,),
    )
    rw_d8, rh_d8 = grid.measure_text("D8")
    d8_fp_box = footprint_bbox(fp_d8)
    d8_ref_placed = False
    for d8_cy in (87.35, 87.25, 87.45, 87.15, 87.00, 86.80):
        for d8_cx in (3.165, 3.10, 3.20, 3.05, 3.00):
            rbox = _make_box(d8_cx, d8_cy, rw_d8, rh_d8, 90.0)
            if box_edge_distance(d8_fp_box, rbox) <= 3.5 and grid.box_ok(1, *rbox):
                _configure_ref_field(
                    fp_d8.Reference(),
                    pcbnew.B_SilkS,
                    d8_cx,
                    d8_cy,
                    90.0,
                    SILK_HEIGHT,
                    SILK_THICKNESS,
                    True,
                )
                grid.reserve(1, *rbox)
                d8_ref_placed = True
                break
        if d8_ref_placed:
            break
    if d8_val_res is None or not d8_ref_placed:
        failed_labels.append(f"D8 ({d8_val})")

    # J4 PWR primary (B.SilkS cleanly between J4 shroud and QR_BOX) & F.SilkS callouts/label
    if (
        place_ref_val_pair(
            grid,
            fp_j4,
            j4_val,
            side=1,
            center=(22.80, 104.00),
            val_only=False,
            step=0.15,
            max_edge_distance=6.0,
            rotations=(90.0, 0.0),
        )
        is None
    ):
        failed_labels.append(f"B.SilkS {j4_full_spec}")
    for lbl_txt, tx_target in _j4_rail_callouts(fp_j4, side=0):
        if (
            _place_point_silk(
                grid, fp_j4, 0, lbl_txt, tx_target, 98.35, max_dist=3.5, step=0.15
            )
            is None
        ):
            failed_labels.append(f"F.SilkS J4 {lbl_txt}")
    if (
        _place_board_silk_local(
            grid, board, fp_j4, j4_full_spec, side=0, max_edge_dist=6.0
        )
        is None
    ):
        failed_labels.append(f"F.SilkS {j4_full_spec}")

    # Decoupling caps C5-C8 (tight <= 3.5 mm local slots around U1/U2)
    for ref in [f"C{i}" for i in range(5, 9)]:
        fp = footprints[ref]
        silk_val, _ = _parse_silkscreen_spec(fp)
        res = place_val_only(
            grid, fp, silk_val, side=1, step=0.15, max_edge_distance=3.5, compact=True
        )
        if res is None:
            failed_labels.append(f"B.SilkS {ref} ({silk_val})")

    # C3, C4 mandatory external + and - polarity markers on B.SilkS tightly adjacent to Pads 1 (+) & 2 (-)
    for c_ref in ("C3", "C4"):
        fp_c = footprints[c_ref]
        c_pos = fp_c.FindPadByNumber("1").GetPosition()
        c_neg = fp_c.FindPadByNumber("2").GetPosition()
        c_px, c_py = pcbnew.ToMM(c_pos.x), pcbnew.ToMM(c_pos.y)
        c_nx, c_ny = pcbnew.ToMM(c_neg.x), pcbnew.ToMM(c_neg.y)
        if abs(c_px - c_nx) >= abs(c_py - c_ny):
            pos_target = (c_px, c_py - 3.60)
            neg_target = (c_nx, c_ny - 3.60)
        else:
            pos_target = (c_px - 2.00, c_py + 2.00)
            neg_target = (c_nx + 2.75, c_ny - 1.65)
        if (
            _place_point_silk(
                grid,
                fp_c,
                1,
                "+",
                pos_target[0],
                pos_target[1],
                max_dist=3.5,
                step=0.20,
            )
            is None
        ):
            failed_labels.append(f"B.SilkS {c_ref} (+)")
        if (
            _place_point_silk(
                grid,
                fp_c,
                1,
                "-",
                neg_target[0],
                neg_target[1],
                max_dist=3.5,
                step=0.20,
            )
            is None
        ):
            failed_labels.append(f"B.SilkS {c_ref} (-)")

    # Front Panel Controls (F.Cu primary F.SilkS + secondary B.SilkS, all from netlist `Silkscreen` field)
    front_refs = ("J1", "J2", "J3", "RV1", "RV2", "RV3", "RV4", "D4")
    for ref in front_refs:
        fp = footprints[ref]
        _, val_part = _parse_silkscreen_spec(fp)
        res = place_ref_val_pair(
            grid,
            fp,
            val_part,
            side=0,
            val_only=False,
            step=0.25,
            max_edge_distance=6.0,
        )
        if res is None:
            failed_labels.append(f"F.SilkS {ref} ({val_part})")

    # Pot Pin-1 markers ("1") on BOTH sides, cleanly beside Pad 1 outside pot & cap bodies
    for rv_ref in ("RV1", "RV2", "RV3", "RV4"):
        fp = footprints[rv_ref]
        p1 = fp.FindPadByNumber("1").GetPosition()
        p1x, p1y = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        for side in (0, 1):
            if (
                _place_point_silk(
                    grid, fp, side, "1", p1x - 1.90, p1y, max_dist=2.5, step=0.20
                )
                is None
            ):
                failed_labels.append(f"side={side} {rv_ref} Pin-1")

    # D4 LED polarity markers (- at Pad 1 square K, + at Pad 2 round A) on BOTH sides
    fp_d4 = footprints["D4"]
    d4_k = fp_d4.FindPadByNumber("1").GetPosition()
    d4_a = fp_d4.FindPadByNumber("2").GetPosition()
    for side in (0, 1):
        d4_neg_x = pcbnew.ToMM(d4_k.x) - (2.00 if side == 1 else 1.25)
        d4_pos_x = pcbnew.ToMM(d4_a.x) + (0.48 if side == 1 else 1.25)
        d4_pos_y = pcbnew.ToMM(d4_a.y) + (2.00 if side == 1 else 0.0)
        if (
            _place_point_silk(
                grid,
                fp_d4,
                side,
                "-",
                d4_neg_x,
                pcbnew.ToMM(d4_k.y),
                max_dist=2.5,
            )
            is None
        ):
            failed_labels.append(f"side={side} D4 (-)")
        if (
            _place_point_silk(
                grid,
                fp_d4,
                side,
                "+",
                d4_pos_x,
                d4_pos_y,
                max_dist=2.5,
            )
            is None
        ):
            failed_labels.append(f"side={side} D4 (+)")

    # Reserve tight R25/R26 horizontal gaps before D4 ENV secondary B.SilkS label
    for r_tight, ty_tight in (("R25", 61.80), ("R26", 65.00)):
        fp_r = footprints[r_tight]
        r_val, _ = _parse_silkscreen_spec(fp_r)
        if (
            place_val_only(
                grid,
                fp_r,
                r_val,
                side=1,
                center=(pcbnew.ToMM(fp_r.GetPosition().x), ty_tight),
                step=0.10,
                max_edge_distance=3.5,
                compact=True,
                rotations=(0.0,),
            )
            is None
        ):
            failed_labels.append(f"B.SilkS {r_tight} ({r_val})")

    # 1. Secondary B.SilkS labels for front-panel controls (before remaining resistors)
    for ref in front_refs:
        fp = footprints[ref]
        sec_lbl, _ = _parse_silkscreen_spec(fp)
        if (
            _place_board_silk_local(
                grid, board, fp, sec_lbl, side=1, max_edge_dist=6.0, step=0.25
            )
            is None
        ):
            failed_labels.append(f"B.SilkS {ref} ({sec_lbl})")

    # 2. Remaining Passives R1-R29 (excluding R25/R26), C1-C4, C9-C10 (from netlist `Silkscreen`)
    for ref in [f"R{i}" for i in range(1, 30) if i not in (25, 26)] + [
        f"C{i}" for i in (1, 2, 3, 4, 9, 10)
    ]:
        fp = footprints[ref]
        silk_val, _ = _parse_silkscreen_spec(fp)
        res = place_val_only(
            grid,
            fp,
            silk_val,
            side=1,
            step=0.10 if ref == "C3" else 0.20,
            max_edge_distance=3.5 if ref not in ("C1", "C2") else 6.0,
            compact=True,
        )
        if res is None:
            failed_labels.append(f"B.SilkS {ref} ({silk_val})")
        if not is_smd_footprint(fp):
            _place_board_silk_local(
                grid, board, fp, silk_val, side=0, max_edge_dist=6.0
            )

    # 4. Jack pinout / normalling markers (SilkscreenInstructions.md §3.2) where space clears
    for j_ref, tn_lbl in (("J1", "TN=GND"), ("J2", "TN=NC"), ("J3", "TN=NC")):
        fp_j = footprints[j_ref]
        tn_pad = fp_j.FindPadByNumber("TN")
        if tn_pad is not None:
            tx, ty = (
                pcbnew.ToMM(tn_pad.GetPosition().x),
                pcbnew.ToMM(tn_pad.GetPosition().y),
            )
            _place_point_silk(
                grid, fp_j, 0, tn_lbl, tx + 5.20, ty, max_dist=6.0, step=0.25
            )

    # Board Name & Revision derived from KiCad TitleBlock on B.SilkS and F.SilkS
    tb = board.GetTitleBlock()
    board_title = f"{tb.GetTitle().strip()} {tb.GetRevision().strip()}".strip()
    for side, layer_id, mirrored in (
        (1, pcbnew.B_SilkS, True),
        (0, pcbnew.F_SilkS, False),
    ):
        placed_title = False
        for bx, by in (
            (15.0, 12.8),
            (15.0, 33.8),
            (15.0, 19.5),
            (15.0, 9.5),
            (15.0, 56.5),
        ):
            tw, th = grid.measure_text(board_title, 0.85, 0.15)
            box = _make_box(bx, by, tw, th, 0.0)
            if grid.box_ok(side, *box):
                add_silk_text(
                    board,
                    layer_id,
                    board_title,
                    bx,
                    by,
                    0.0,
                    0.85,
                    0.15,
                    mirrored,
                )
                grid.reserve(side, *box)
                placed_title = True
                break
        if not placed_title:
            for by in [y * 0.5 for y in range(2, 214)]:
                for bx in (15.0, 11.0, 19.0):
                    tw, th = grid.measure_text(board_title, 0.80, 0.15)
                    box = _make_box(bx, by, tw, th, 0.0)
                    if grid.box_ok(side, *box):
                        add_silk_text(
                            board,
                            layer_id,
                            board_title,
                            bx,
                            by,
                            0.0,
                            0.80,
                            0.15,
                            mirrored,
                        )
                        grid.reserve(side, *box)
                        placed_title = True
                        break
                if placed_title:
                    break
            if not placed_title:
                failed_labels.append(f"Board title side={side}")

    # B.Fab fabrication notes (100% fab_notes_completeness) + rear TP DNP note
    add_standard_fab_notes(board, cx=15.0, y_start=111.0)
    add_silk_text(
        board, pcbnew.B_Fab, "TP1-8: RH-5001 (DNP)", 15.0, 119.8, 0.0, 0.80, 0.15, True
    )

    if failed_labels:
        raise RuntimeError(f"Failed local silkscreen placement for: {failed_labels}")

    _verify_silkscreen_and_polarity(board, footprints, polarity_shapes)


def main() -> None:
    net_path = STAGE_DIR / "envelope_follower.net"
    out_path = STAGE_DIR / "EnvelopeFollower.kicad_pcb"

    components, nets = parse_netlist(net_path, dnp_prefixes=("TP",))
    placements = get_clean_placements()

    board = create_base_board(
        out_path,
        0.0,
        0.0,
        BOARD_W,
        BOARD_H,
        title="ENVELOPE FOLLOWER",
        revision="Rev 1.0",
        date="2026-11",
        track_width=SIGNAL_WIDTH,
        clearance=TRACK_CLEARANCE,
        via_diam=VIA_DIAM,
        via_drill=VIA_DRILL,
        edge_clearance=EDGE_CLEARANCE,
    )

    footprints = populate_footprints(board, components, placements)
    for ref, fp in footprints.items():
        if ref.startswith("TP"):
            fp.SetExcludedFromBOM(True)
            fp.SetExcludedFromPosFiles(True)
            fp.SetDNP(True)
    fids = add_fiducials(board, FIDUCIALS)
    net_items, _ = assign_nets(board, footprints, nets)

    check_placement_constraints(board, footprints, fids)
    route_pcb(board, footprints, fids, net_items, nets)
    apply_silkscreen_and_fab(board, footprints, fids)

    pcbnew.SaveBoard(str(out_path), board)
    print(f"Saved {out_path} ({len(footprints)} netlist + {len(fids)} fiducials).")


if __name__ == "__main__":
    main()
