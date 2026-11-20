#!/usr/bin/env python3
"""Generate 6 HP Eurorack Envelope Follower PCB (EnvelopeFollower.kicad_pcb)."""

from __future__ import annotations

import argparse
import heapq
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

from pcbnew_layout_template import (
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
    pour_gnd_zones,
)
from silk_annotator import (
    MAX_THT_TETHER_MM,
    SILK_HEIGHT,
    SILK_THICKNESS,
    SilkGrid,
    add_silk_dot,
    add_silk_rect,
    add_silk_seg,
    add_silk_text,
    box_edge_distance,
    footprint_bbox,
    inspect_board_silk,
    place_ref_val_pair,
    place_val_only,
)

BOARD_W = 30.00
BOARD_H = 108.00
POWER_NETS = {"+12V", "-12V", "+12V_IN", "-12V_IN", "+12V_PROT", "-12V_PROT"}


QR_RECT = (12.50, 7.80, 17.50, 12.80)


def build_placements() -> dict[str, tuple[float, float, float, bool]]:
    """Return (x, y, rot_deg, is_back) for all 71 footprints."""
    return {
        # --- 8 Front-panel THT strictly on F.Cu ---
        # Rows at Y_shaft/bushing = 15.0, 42.5, 67.0, 86.8 (X = 7.5, 22.5)
        "RV1": (5.00, 22.50, 90.0, False),  # shaft (7.50, 15.00)
        "RV2": (20.00, 22.50, 90.0, False),  # shaft (22.50, 15.00)
        "RV3": (5.00, 50.00, 90.0, False),  # shaft (7.50, 42.50)
        "RV4": (20.00, 50.00, 90.0, False),  # shaft (22.50, 42.50)
        "J1": (7.50, 60.52, 0.0, False),  # bushing (7.50, 67.00)
        "D4": (21.23, 67.00, 0.0, False),  # lens (22.50, 67.00)
        "J2": (7.50, 80.32, 0.0, False),  # bushing (7.50, 86.80)
        "J3": (22.50, 80.32, 0.0, False),  # bushing (22.50, 86.80)
        # --- 3 SMT optical fiducials on B.Cu (bottom-side SMT pass, excluded from BOM/CPL) ---
        "FID1": (2.30, 2.30, 0.0, True),
        "FID2": (27.70, 2.40, 0.0, True),
        "FID3": (2.30, 106.15, 0.0, True),
        # --- 11 Rear THT on B.Cu ---
        "J4": (
            13.73,
            99.30,
            0.0,
            True,
        ),  # vertical 2x5 shrouded IDC, centered at X=15.00
        "C1": (3.50, 54.50, 0.0, True),
        "C2": (13.60, 52.50, 270.0, True),
        "TP1": (27.30, 105.20, 0.0, True),  # GND
        "TP2": (12.90, 35.20, 0.0, True),  # +12V
        "TP3": (12.60, 31.90, 0.0, True),  # -12V
        "TP4": (27.60, 6.20, 0.0, True),  # IN_BUF
        "TP5": (15.00, 4.20, 0.0, True),  # PREAMP_OUT
        "TP6": (27.60, 33.80, 0.0, True),  # RECT_OUT
        "TP7": (12.20, 75.50, 0.0, True),  # OUT_CLAMP
        "TP8": (15.00, 80.80, 0.0, True),  # INV_OUT_CLAMP
        # --- 49 SMT parts strictly on B.Cu ---
        # Corridor A (Y = 0.45..7.50)
        "R_GAIN_MIN": (6.80, 2.10, 0.0, True),
        "R_GAIN_FAIL": (10.80, 2.10, 0.0, True),
        "C_HF": (6.80, 5.80, 0.0, True),
        "R2": (10.80, 5.80, 0.0, True),
        "R_ATK_MIN": (19.50, 2.10, 0.0, True),
        "D3": (24.00, 2.10, 0.0, True),
        "R10": (19.50, 5.80, 0.0, True),
        "R20": (24.00, 5.80, 0.0, True),
        # Corridor B (Y = 23.68..41.20)
        "U1": (5.50, 30.20, 90.0, True),
        "C_DEC2": (4.75, 24.90, 180.0, True),
        "C_DEC1": (6.00, 35.40, 0.0, True),
        "R3": (15.00, 24.80, 180.0, True),
        "R4": (19.00, 24.80, 0.0, True),
        "R5": (23.00, 24.80, 0.0, True),
        "R15": (27.50, 25.00, 90.0, True),
        "R6": (15.00, 29.00, 0.0, True),
        "R7": (19.00, 29.00, 0.0, True),
        "R8A": (23.00, 29.00, 0.0, True),
        "R8B": (27.20, 29.00, 0.0, True),
        "R11": (9.80, 35.40, 0.0, True),
        "D1_D2": (17.00, 33.40, 0.0, True),
        "R_ENV_PROT": (21.20, 33.40, 0.0, True),
        "C_OUT1": (24.40, 35.40, 0.0, True),
        # Corridor C & D (Y = 45.00..78.50)
        "R13": (15.00, 47.40, 90.0, True),
        "R12": (27.20, 48.00, 180.0, True),
        "C_OUT2": (18.80, 51.90, 0.0, True),
        "R17": (28.20, 54.60, 90.0, True),
        "R18": (28.20, 61.90, 270.0, True),
        "U2": (21.55, 60.05, 0.0, True),
        "C_DEC3": (14.70, 60.90, 90.0, True),
        "C_DEC4": (26.50, 59.25, 90.0, True),
        "R1": (10.20, 61.00, 90.0, True),
        "D_IN": (11.60, 64.90, 90.0, True),
        "R_IN_BUF": (10.60, 69.20, 0.0, True),
        "R_IN_PROT": (3.40, 68.50, 90.0, True),
        "R_LED": (27.30, 71.20, 90.0, True),
        "D_LED_CLAMP": (14.60, 71.25, 90.0, True),
        "D_OUT": (22.20, 70.85, 90.0, True),
        "R16A": (3.00, 75.20, 0.0, True),
        "R16B": (7.80, 75.20, 0.0, True),
        "R19A": (17.20, 75.15, 0.0, True),
        "R19B": (22.20, 75.15, 0.0, True),
        # Lower Board Power Block & Output Clamp (Y = 78.50..107.00)
        "D_INV_OUT": (10.80, 79.30, 0.0, True),
        "R_PWR_N": (3.20, 84.00, 90.0, True),
        "D_PWR_N": (2.40, 89.60, 90.0, True),
        "C4": (4.40, 99.80, 270.0, True),
        "R_PWR_P": (27.60, 84.60, 90.0, True),
        "D_PWR_P": (27.60, 90.00, 270.0, True),
        "C3": (25.60, 98.50, 270.0, True),
    }


def _get_crtyd_bbox(fp: pcbnew.FOOTPRINT) -> tuple[float, float, float, float] | None:
    layer = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    xs, ys = [], []
    for gi in fp.GraphicalItems():
        if not hasattr(gi, "GetText") and gi.GetLayer() == layer:
            bb = gi.GetBoundingBox()
            xs.extend([pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetRight())])
            ys.extend([pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetBottom())])
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def check_geometry(fps: dict[str, pcbnew.FOOTPRINT]) -> None:
    refs = sorted(fps)
    for i, r1 in enumerate(refs):
        fp1 = fps[r1]
        b1 = _get_crtyd_bbox(fp1)
        if not b1:
            continue
        if b1[0] < 0.2 or b1[1] < 0.2 or b1[2] > BOARD_W - 0.2 or b1[3] > BOARD_H - 0.2:
            raise RuntimeError(f"EDGE WARN: {r1} CrtYd={b1}")
        for r2 in refs[i + 1 :]:
            fp2 = fps[r2]
            if fp1.IsFlipped() != fp2.IsFlipped():
                continue
            b2 = _get_crtyd_bbox(fp2)
            if not b2:
                continue
            if not (
                b1[2] <= b2[0] or b2[2] <= b1[0] or b1[3] <= b2[1] or b2[3] <= b1[1]
            ):
                raise RuntimeError(f"CRTYD OVERLAP: {r1} {b1} vs {r2} {b2}")

    tht_pads = []
    for r, fp in fps.items():
        for p in fp.Pads():
            if p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                pos = p.GetPosition()
                sz = p.GetSize()
                cx, cy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
                w, h = pcbnew.ToMM(sz.x), pcbnew.ToMM(sz.y)
                tht_pads.append(
                    (r, p.GetNumber(), (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
                )

    for i, (r1, p1, b1) in enumerate(tht_pads):
        for r2, p2, b2 in tht_pads[i + 1 :]:
            if r1 == r2:
                continue
            if not (
                b1[2] + 0.25 <= b2[0]
                or b2[2] + 0.25 <= b1[0]
                or b1[3] + 0.25 <= b2[1]
                or b2[3] + 0.25 <= b1[1]
            ):
                raise RuntimeError(f"THT PAD OVERLAP: {r1}.{p1} vs {r2}.{p2}")
        for rs, fps_item in fps.items():
            if rs == r1:
                continue
            is_smt_or_fid = any(
                p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD for p in fps_item.Pads()
            ) or rs.startswith("FID")
            is_opp_tht_body = not fps_item.IsFlipped() and fps[r1].IsFlipped()
            if not (is_smt_or_fid or is_opp_tht_body):
                continue
            sb = _get_crtyd_bbox(fps_item)
            margin = 0.05 if is_opp_tht_body and not is_smt_or_fid else 0.20
            if sb and not (
                b1[2] + margin <= sb[0]
                or sb[2] + margin <= b1[0]
                or b1[3] + margin <= sb[1]
                or sb[3] + margin <= b1[1]
            ):
                raise RuntimeError(
                    f"THT PAD VS OPPOSITE/SMD CRTYD: {r1}.{p1} {b1} vs {rs} {sb}"
                )


def _place_silk_dot_checked(
    grid: SilkGrid,
    board: pcbnew.BOARD,
    side: int,
    candidates: list[tuple[float, float]],
    *,
    radius: float = 0.22,
    width: float = 0.15,
) -> tuple[float, float]:
    """Place a filled silkscreen dot at the first clear candidate and reserve keepout."""
    layer_id = pcbnew.B_SilkS if side == 1 else pcbnew.F_SilkS
    r_eff = radius + width * 0.5
    for cx, cy in candidates:
        box = (cx - r_eff, cy - r_eff, cx + r_eff, cy + r_eff)
        if grid.box_ok(side, *box):
            add_silk_dot(board, layer_id, cx, cy, radius=radius)
            grid.keepout[side].append(
                (box[0] - 0.20, box[1] - 0.20, box[2] + 0.20, box[3] + 0.20)
            )
            grid.reserve(side, *box)
            return (cx, cy)
    raise RuntimeError(
        f"Failed to place silkscreen dot on side={side} among {candidates}"
    )


def _place_silk_seg_checked(
    grid: SilkGrid,
    board: pcbnew.BOARD,
    side: int,
    candidates: list[tuple[float, float, float, float]],
    *,
    width: float = 0.25,
) -> tuple[float, float, float, float]:
    """Place a silkscreen segment at the first clear candidate and reserve keepout."""
    layer_id = pcbnew.B_SilkS if side == 1 else pcbnew.F_SilkS
    hw = width * 0.5
    for x0, y0, x1, y1 in candidates:
        box = (
            min(x0, x1) - hw,
            min(y0, y1) - hw,
            max(x0, x1) + hw,
            max(y0, y1) + hw,
        )
        if grid.box_ok(side, *box):
            add_silk_seg(board, layer_id, x0, y0, x1, y1, width=width)
            grid.keepout[side].append(
                (box[0] - 0.20, box[1] - 0.20, box[2] + 0.20, box[3] + 0.20)
            )
            grid.reserve(side, *box)
            return (x0, y0, x1, y1)
    raise RuntimeError(
        f"Failed to place silkscreen segment on side={side} among {candidates}"
    )


def _block_tht_fab_bodies(
    grid: SilkGrid,
    fps: dict[str, pcbnew.FOOTPRINT],
    refs: tuple[str, ...],
    margin: float = 0.08,
) -> None:
    """Reserve THT component .Fab body outlines so labels stay visible outside housings."""
    for ref in refs:
        fp = fps[ref]
        side = 1 if fp.IsFlipped() else 0
        fab_layer = pcbnew.B_Fab if side == 1 else pcbnew.F_Fab
        xs, ys = [], []
        for gi in fp.GraphicalItems():
            if not hasattr(gi, "GetText") and gi.GetLayer() == fab_layer:
                bb = gi.GetBoundingBox()
                xs.extend((pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetRight())))
                ys.extend((pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetBottom())))
        if xs and ys:
            grid.keepout[side].append(
                (
                    min(xs) - margin,
                    min(ys) - margin,
                    max(xs) + margin,
                    max(ys) + margin,
                )
            )


def _add_bounded_fab_notes(board: pcbnew.BOARD, cx: float, y_start: float) -> None:
    """Place complete B.Fab notes wrapped strictly inside the 30.0 mm board width."""
    lines = [
        "FAB: 2L FR4 | THICKNESS: 1.6mm",
        "1oz CU | FINISH: ENIG / HASL-LF",
        "IPC-6012 CLASS 2 | NO EDGE CUT",
        "SOLDER MASK: BLACK | SILK: WHITE",
        "MIN TR/SP: 0.127mm",
        "DRILL TOL: +/-0.08mm",
    ]
    for idx, line in enumerate(lines):
        add_silk_text(
            board,
            pcbnew.B_Fab,
            line,
            cx,
            y_start + idx * 1.9,
            0.0,
            0.70,
            0.12,
            True,
        )


def _place_single_silk_text(
    grid: SilkGrid,
    parent: pcbnew.BOARD | pcbnew.FOOTPRINT,
    side: int,
    text: str,
    anchor: tuple[float, float],
    fp_box: tuple[float, float, float, float] | None = None,
    *,
    max_tether: float = MAX_THT_TETHER_MM,
    height: float = SILK_HEIGHT,
    thickness: float = SILK_THICKNESS,
    step: float = 0.25,
    rotations: tuple[float, ...] = (0.0, 90.0),
) -> tuple[float, float, float] | None:
    """Place a single silkscreen text near `anchor` checking SilkGrid keepouts & overlaps."""
    layer_id = pcbnew.B_SilkS if side == 1 else pcbnew.F_SilkS
    mirrored = side == 1
    tw, th = grid.measure_text(text, height, thickness)
    cx, cy = anchor
    r_lim = max_tether + 3.0
    ix0, ix1 = math.floor(-r_lim / step), math.ceil(r_lim / step)
    iy0, iy1 = math.floor(-r_lim / step), math.ceil(r_lim / step)

    cands = []
    for iy in range(iy0, iy1 + 1):
        for ix in range(ix0, ix1 + 1):
            tx, ty = cx + ix * step, cy + iy * step
            dist2 = (tx - cx) ** 2 + (ty - cy) ** 2
            for deg_idx, deg in enumerate(rotations):
                rw, rh = (th, tw) if deg == 90.0 else (tw, th)
                box = (tx - rw * 0.5, ty - rh * 0.5, tx + rw * 0.5, ty + rh * 0.5)
                ed = (
                    box_edge_distance(fp_box, box)
                    if fp_box is not None
                    else math.hypot(tx - cx, ty - cy)
                )
                if ed <= max_tether:
                    cands.append((round(ed, 4), dist2, deg_idx, tx, ty, deg, box))
    cands.sort()
    for _, _, _, tx, ty, deg, box in cands:
        if grid.box_ok(side, *box):
            add_silk_text(
                parent, layer_id, text, tx, ty, deg, height, thickness, mirrored
            )
            grid.reserve(side, *box)
            return (tx, ty, deg)
    return None


def apply_silkscreen_and_fab(
    board: pcbnew.BOARD,
    fps: dict[str, pcbnew.FOOTPRINT],
    components: dict[str, dict],
) -> None:
    """Apply all SilkscreenInstructions.md labels, dual-sided echoes, polarity marks, QR & fab notes."""
    for fp in fps.values():
        fab_lyr = pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab
        fp.Reference().SetLayer(fab_lyr)
        fp.Reference().SetVisible(False)
        fp.Value().SetLayer(fab_lyr)
        fp.Value().SetVisible(False)

    grid = SilkGrid(board, fps, board_bounds=(0.0, 0.0, BOARD_W, BOARD_H))

    # Reserve THT housing .Fab bodies so component labels remain legible after assembly
    _block_tht_fab_bodies(
        grid, fps, ("RV1", "RV2", "RV3", "RV4", "J1", "J2", "J3", "D4", "J4")
    )

    # 1. Reserve 5.0 x 5.0 mm JLCPCB QR code placeholder on B.SilkS (via-free & >=0.25mm mask-clear)
    qr_x0, qr_y0, qr_x1, qr_y1 = QR_RECT
    add_silk_rect(
        board, pcbnew.B_SilkS, qr_x0, qr_y0, qr_x1, qr_y1, filled=True, width=0.15
    )
    grid.keepout[1].append((qr_x0 - 0.30, qr_y0 - 0.30, qr_x1 + 0.30, qr_y1 + 0.30))

    # 2. Mandatory polarity, Pin-1 & orientation marks on mounting silkscreen layer
    for ic_ref in ("U1", "U2"):
        fp = fps[ic_ref]
        ic_side = 1 if fp.IsFlipped() else 0
        p1 = next(p for p in fp.Pads() if p.GetNumber() == "1").GetPosition()
        p2 = next(p for p in fp.Pads() if p.GetNumber() == "2").GetPosition()
        fpos = fp.GetPosition()
        px, py = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        fx, fy = pcbnew.ToMM(fpos.x), pcbnew.ToMM(fpos.y)
        if abs(pcbnew.ToMM(p1.y) - pcbnew.ToMM(p2.y)) < 0.1:
            sx = 1.0 if px > fx else -1.0
            sy = 1.0 if py > fy else -1.0
            cands = [(px + sx * 0.75, py + sy * 1.55), (px + sx * 1.45, py + sy * 1.45)]
        else:
            sx = 1.0 if px > fx else -1.0
            sy = 1.0 if py > fy else -1.0
            cands = [(px + sx * 1.65, py + sy * 0.50), (px + sx * 1.55, py + sy * 1.25)]
        _place_silk_dot_checked(grid, board, ic_side, cands, radius=0.25)

    for d_ref in ("D_PWR_P", "D_PWR_N", "D3", "D_LED_CLAMP"):
        fp = fps[d_ref]
        d_side = 1 if fp.IsFlipped() else 0
        p1 = next(p for p in fp.Pads() if p.GetNumber() == "1").GetPosition()
        p2 = next(p for p in fp.Pads() if p.GetNumber() == "2").GetPosition()
        x1, y1 = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        x2, y2 = pcbnew.ToMM(p2.x), pcbnew.ToMM(p2.y)
        vx, vy = x1 - x2, y1 - y2
        vlen = math.hypot(vx, vy) or 1.0
        ux, uy = vx / vlen, vy / vlen
        nx, ny = -uy, ux
        base_off = 1.20 if "SOD-123" in components[d_ref]["footprint"] else 1.05
        half_len = 0.85 if "SOD-123" in components[d_ref]["footprint"] else 0.60
        cands = []
        for off in (base_off, base_off + 0.15, base_off + 0.30):
            bx, by = x1 + ux * off, y1 + uy * off
            cands.append(
                (
                    bx - nx * half_len,
                    by - ny * half_len,
                    bx + nx * half_len,
                    by + ny * half_len,
                )
            )
        _place_silk_seg_checked(grid, board, d_side, cands, width=0.25)

    for s_ref in ("D1_D2", "D_IN", "D_OUT", "D_INV_OUT"):
        fp = fps[s_ref]
        s_side = 1 if fp.IsFlipped() else 0
        p1 = next(p for p in fp.Pads() if p.GetNumber() == "1").GetPosition()
        p2 = next(p for p in fp.Pads() if p.GetNumber() == "2").GetPosition()
        p3 = next(p for p in fp.Pads() if p.GetNumber() == "3").GetPosition()
        x1, y1 = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        x2, y2 = pcbnew.ToMM(p2.x), pcbnew.ToMM(p2.y)
        x3, y3 = pcbnew.ToMM(p3.x), pcbnew.ToMM(p3.y)
        # Outward unit vectors: u = away from Pad 3 (pin side), v = away from Pad 2 (edge side)
        ux, uy = x1 - x3, y1 - y3
        ul = math.hypot(ux, uy) or 1.0
        ux, uy = ux / ul, uy / ul
        vx, vy = x1 - x2, y1 - y2
        vl = math.hypot(vx, vy) or 1.0
        vx, vy = vx / vl, vy / vl
        if abs(ux) > abs(uy):
            sx = -1.0 if ux < 0 else 1.0
            sy = -1.0 if vy < 0 else 1.0
            cands = [
                (x1 + sx * 1.38, y1),
                (x1 + sx * 1.45, y1 + sy * 0.25),
                (x1 + sx * 1.45, y1 - sy * 0.20),
                (x1 + sx * 1.30, y1 + sy * 0.50),
                (x1, y1 + sy * 1.25),
                (x1 - sx * 0.25, y1 + sy * 1.25),
            ]
        else:
            sx = -1.0 if vx < 0 else 1.0
            sy = -1.0 if uy < 0 else 1.0
            cands = [
                (x1, y1 + sy * 1.38),
                (x1 + sx * 0.25, y1 + sy * 1.45),
                (x1 - sx * 0.20, y1 + sy * 1.45),
                (x1 + sx * 0.50, y1 + sy * 1.30),
                (x1 + sx * 1.25, y1),
                (x1 + sx * 1.25, y1 - sy * 0.25),
            ]
        _place_silk_dot_checked(grid, board, s_side, cands, radius=0.22)

    # J4 horizontal RED STRIPE / -12V bar along Pins 1-2 bottom edge (0.85 mm wide, clear of Pin-1 triangle & shroud)
    j4_fp = fps["J4"]
    j4_p1 = next(p for p in j4_fp.Pads() if p.GetNumber() == "1").GetPosition()
    p1x, p1y = pcbnew.ToMM(j4_p1.x), pcbnew.ToMM(j4_p1.y)
    j4_fab_xs, j4_fab_ys = [], []
    for gi in j4_fp.GraphicalItems():
        if not hasattr(gi, "GetText") and gi.GetLayer() == pcbnew.B_Fab:
            bb = gi.GetBoundingBox()
            j4_fab_xs.extend((pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetRight())))
            j4_fab_ys.extend((pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetBottom())))
    bar_x0 = min(j4_fab_xs)
    bar_x1 = max(j4_fab_xs)
    bar_y0 = max(j4_fab_ys) + 0.35  # 0.23+ mm clear of J4 bottom B.SilkS edge
    bar_y1 = bar_y0 + 0.85
    add_silk_rect(
        board, pcbnew.B_SilkS, bar_x0, bar_y0, bar_x1, bar_y1, filled=True, width=0.15
    )
    grid.keepout[1].append((bar_x0 - 0.20, bar_y0 - 0.20, bar_x1 + 0.20, bar_y1 + 0.20))
    grid.reserve(1, bar_x0 - 0.08, bar_y0 - 0.08, bar_x1 + 0.08, bar_y1 + 0.08)

    # Reserve C1/C2 3D capacitor body areas on B.SilkS so their '1uF' values sit cleanly outside the body
    for film_ref in ("C1", "C2"):
        fb = _get_crtyd_bbox(fps[film_ref])
        if fb:
            grid.keepout[1].append(
                (fb[0] - 0.15, fb[1] - 0.15, fb[2] + 0.15, fb[3] + 0.15)
            )

    # 3. Board ID (B.SilkS + open F.SilkS corner) & J4 rail callouts
    j4_mid_y = p1y - 5.08
    j4_top_y = p1y - 10.16
    for side, text, anchor, lim in (
        # B.SilkS board title block
        (1, "ENVELOPE FOLLOWER", (15.0, 18.55), 6.0),
        (1, "6HP ±12V EURORACK", (15.0, 20.30), 6.0),
        (1, "REV 1.0", (23.0, 11.2), 6.0),
        # F.SilkS open top-left corner title echo
        (0, "ENVELOPE FOLLOWER", (7.2, 2.0), 4.0),
        (0, "6HP ±12V EURORACK", (7.2, 3.8), 4.0),
        (0, "REV 1.0", (7.2, 5.6), 4.0),
        # J4 rail polarity & callouts
        (1, "RED STRIPE / -12V", (15.0, bar_y1 + 0.95), 4.0),
        (1, "GND", (21.2, j4_mid_y), 6.0),
        (1, "+12V", (21.4, j4_top_y), 5.0),
        (0, "-12V Pin 1", (p1x - 3.5, p1y), 6.0),
    ):
        res = _place_single_silk_text(
            grid, board, side, text, anchor, max_tether=lim, step=0.15
        )
        if res is None:
            raise RuntimeError(f"Board text {text!r} failed on side={side}")

    # Place RV1-RV4 Pin "1" markers tightly beside Pad 1 BEFORE dense passive labels fill corridors
    for rv_ref in ("RV1", "RV2", "RV3", "RV4"):
        fp = fps[rv_ref]
        pads = {p.GetNumber(): p.GetPosition() for p in fp.Pads()}
        p1x_rv, p1y_rv = pcbnew.ToMM(pads["1"].x), pcbnew.ToMM(pads["1"].y)
        p2x_rv, p2y_rv = pcbnew.ToMM(pads["2"].x), pcbnew.ToMM(pads["2"].y)
        p1_box = (p1x_rv - 0.90, p1y_rv - 0.90, p1x_rv + 0.90, p1y_rv + 0.90)
        for side in (0, 1):
            res = _place_single_silk_text(
                grid,
                fp,
                side,
                "1",
                (p1x_rv, p1y_rv),
                p1_box,
                max_tether=1.10,
                step=0.10,
            )
            if res is None:
                raise RuntimeError(f"Failed Pin '1' mark on {rv_ref} side={side}")
            rx, ry, _ = res
            d1 = math.hypot(rx - p1x_rv, ry - p1y_rv)
            d2 = math.hypot(rx - p2x_rv, ry - p2y_rv)
            if d1 > 2.0 or d1 >= d2:
                raise RuntimeError(
                    f"{rv_ref} side={side} '1'@({rx:.2f},{ry:.2f}) too far from Pad 1 "
                    f"(d1={d1:.2f}, d2={d2:.2f})"
                )

    # Primary silkscreen labels: priority actives/interfaces -> panel THT echoes -> SMDs -> film caps
    priority = [
        "U1",
        "U2",
        "D_PWR_N",
        "D_PWR_P",
        "D_LED_CLAMP",
        "D_OUT",
        "TP8",
        "R19B",
        "R19A",
        "D_INV_OUT",
        "D_IN",
        "D1_D2",
        "D3",
        "J4",
        "C3",
        "C4",
        "TP2",
        "TP3",
        "TP5",
        "TP6",
        "TP7",
        "D4",
        "J1",
        "J2",
        "J3",
        "TP1",
        "TP4",
    ]
    pri_rank = {r: idx for idx, r in enumerate(priority)}
    order = sorted(
        fps,
        key=lambda r: (
            (0, pri_rank[r])
            if r in pri_rank
            else ((2, r) if r in ("C1", "C2") else (1, r))
        ),
    )
    done_echoes: set[str] = set()
    for ref in order:
        fp = fps[ref]
        if ref.startswith("FID"):
            continue
        comp = components[ref]
        silk = comp["fields"].get("Silkscreen", "")
        is_passive = ref.startswith(("R", "C")) and not ref.startswith("RV")
        if is_passive:
            res = place_val_only(grid, fp, silk or comp["value"])
            if res is None:
                raise RuntimeError(f"Primary passive silkscreen failed for {ref}")
        else:
            toks = silk.split()
            val_tok = (
                " ".join(toks[1:])
                if toks and toks[0] == ref
                else (silk or comp["value"])
            )
            res = place_ref_val_pair(grid, fp, val_tok, val_only=False, step=0.25)
            if res is None:
                raise RuntimeError(
                    f"Primary ref/val silkscreen failed for {ref} ({val_tok})"
                )
            if ref.startswith("TP"):
                pos = fp.GetPosition()
                tx_tp, ty_tp = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
                # Keep TP1 ${REFERENCE} inside Edge.Cuts and add "DNP" on B.Fab for all TP1-TP8
                for gi in fp.GraphicalItems():
                    if (
                        hasattr(gi, "GetText")
                        and gi.GetText() == "${REFERENCE}"
                        and gi.GetLayer() == pcbnew.B_Fab
                        and ref == "TP1"
                    ):
                        gi.SetPosition(
                            pcbnew.VECTOR2I(
                                pcbnew.FromMM(tx_tp), pcbnew.FromMM(ty_tp - 1.9)
                            )
                        )
                add_silk_text(
                    fp,
                    pcbnew.B_Fab,
                    "DNP",
                    tx_tp,
                    ty_tp + (1.7 if ref != "TP1" else 1.55),
                    0.0,
                    0.50,
                    0.08,
                    True,
                )
                echo_res = _place_single_silk_text(
                    grid,
                    fp,
                    0,
                    silk or comp["value"],
                    (tx_tp, ty_tp),
                    footprint_bbox(fp),
                    max_tether=MAX_THT_TETHER_MM,
                )
                if echo_res is None:
                    raise RuntimeError(
                        f"Dual-sided echo failed for {ref} ({silk}) on side=0"
                    )
                done_echoes.add(ref)
        if ref in ("D4", "J1", "J2", "J3"):
            opp_side = 0 if fp.IsFlipped() else 1
            echo_text = silk or comp["value"]
            pos = fp.GetPosition()
            anchor_map = {"D4": (27.1, 66.8), "J2": (4.2, 80.2), "J3": (26.2, 80.2)}
            anchor_pt = (
                anchor_map[ref]
                if (opp_side == 1 and ref in anchor_map)
                else (pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))
            )
            echo_res = _place_single_silk_text(
                grid,
                fp,
                opp_side,
                echo_text,
                anchor_pt,
                footprint_bbox(fp),
                max_tether=MAX_THT_TETHER_MM,
            )
            if echo_res is None:
                raise RuntimeError(
                    f"Dual-sided echo failed for {ref} ({echo_text}) on side={opp_side}"
                )
            done_echoes.add(ref)

    # 4. Electrolytic '+' and D4 '+'/'-' polarity symbols checked cleanly against SilkGrid
    for cap_ref in ("C3", "C4"):
        fp = fps[cap_ref]
        cap_side = 1 if fp.IsFlipped() else 0
        p1 = next(p for p in fp.Pads() if p.GetNumber() == "1").GetPosition()
        p2 = next(p for p in fp.Pads() if p.GetNumber() == "2").GetPosition()
        px1, py1 = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        px2, py2 = pcbnew.ToMM(p2.x), pcbnew.ToMM(p2.y)
        ux, uy = px1 - px2, py1 - py2
        ul = math.hypot(ux, uy) or 1.0
        res = _place_single_silk_text(
            grid,
            fp,
            cap_side,
            "+",
            (px1 + (ux / ul) * 2.5, py1 + (uy / ul) * 2.5),
            footprint_bbox(fp),
            max_tether=3.5,
        )
        if res is None:
            raise RuntimeError(f"Failed '+' mark on {cap_ref}")

    d4_fp = fps["D4"]
    d4_p1 = next(p for p in d4_fp.Pads() if p.GetNumber() == "1").GetPosition()
    d4_p2 = next(p for p in d4_fp.Pads() if p.GetNumber() == "2").GetPosition()
    d4_p1x, d4_p1y = pcbnew.ToMM(d4_p1.x), pcbnew.ToMM(d4_p1.y)
    d4_p2x, d4_p2y = pcbnew.ToMM(d4_p2.x), pcbnew.ToMM(d4_p2.y)
    d4_k_box = (d4_p1x - 0.85, d4_p1y - 0.85, d4_p1x + 0.85, d4_p1y + 0.85)
    d4_a_box = (d4_p2x - 0.85, d4_p2y - 0.85, d4_p2x + 0.85, d4_p2y + 0.85)
    for side in (0, 1):
        res_k = _place_single_silk_text(
            grid,
            d4_fp,
            side,
            "-",
            (d4_p1x, d4_p1y + 1.8),
            d4_k_box,
            max_tether=1.8,
            step=0.20,
        )
        res_a = _place_single_silk_text(
            grid,
            d4_fp,
            side,
            "+",
            (d4_p2x, d4_p2y + 1.8),
            d4_a_box,
            max_tether=1.8,
            step=0.20,
        )
        if res_k is None or res_a is None:
            raise RuntimeError(f"Failed D4 +/- marks on side={side}")

    # 5. Dual-sided THT echoes (remaining front-panel pots first, then rear THT)
    for ref, fp in sorted(
        fps.items(), key=lambda kv: (1 if kv[1].IsFlipped() else 0, kv[0])
    ):
        if ref in done_echoes:
            continue
        is_tht = all(p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD for p in fp.Pads())
        if not is_tht:
            continue
        opp_side = 0 if fp.IsFlipped() else 1
        comp = components[ref]
        echo_text = comp["fields"].get("Silkscreen", "") or comp["value"]
        pos = fp.GetPosition()
        fp_box = footprint_bbox(fp)
        res = _place_single_silk_text(
            grid,
            fp,
            opp_side,
            echo_text,
            (pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)),
            fp_box,
            max_tether=MAX_THT_TETHER_MM,
        )
        if res is None:
            raise RuntimeError(
                f"Dual-sided echo failed for {ref} ({echo_text}) on side={opp_side}"
            )

    _add_bounded_fab_notes(board, 15.0, 27.0)


class HVGridRouter(GridRouter):
    """GridRouter with F.Cu-horizontal / B.Cu-vertical routing bias and soft silkscreen via-avoidance."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.silk_via_avoid = bytearray(self.nx * self.ny)

    def mark_via_block_rect(
        self, x0: float, y0: float, x1: float, y1: float, margin: float = 0.35
    ) -> None:
        """Hard-block vias inside a rectangular keepout box (e.g., QR code placeholder)."""
        gx0 = max(0, math.floor((x0 - margin - self.x0) / self.step))
        gx1 = min(self.nx - 1, math.ceil((x1 + margin - self.x0) / self.step))
        gy0 = max(0, math.floor((y0 - margin - self.y0) / self.step))
        gy1 = min(self.ny - 1, math.ceil((y1 + margin - self.y0) / self.step))
        for gy in range(gy0, gy1 + 1):
            row = gy * self.nx
            for gx in range(gx0, gx1 + 1):
                self.via_block[row + gx] = 1

    def mark_silk_via_rect(
        self, x0: float, y0: float, x1: float, y1: float, margin: float = 0.45
    ) -> None:
        """Soft-penalize/avoid placing vias over placed silkscreen text bboxes."""
        gx0 = max(0, math.floor((x0 - margin - self.x0) / self.step))
        gx1 = min(self.nx - 1, math.ceil((x1 + margin - self.x0) / self.step))
        gy0 = max(0, math.floor((y0 - margin - self.y0) / self.step))
        gy1 = min(self.ny - 1, math.ceil((y1 + margin - self.y0) / self.step))
        for gy in range(gy0, gy1 + 1):
            row = gy * self.nx
            for gx in range(gx0, gx1 + 1):
                self.silk_via_avoid[row + gx] = 1

    def route(
        self,
        starts: list[tuple[int, int, int]],
        targets: set[tuple[int, int, int]],
        net_code: int,
        preferred_layer: int | None = None,
    ) -> list[tuple[int, int, int]] | None:
        target_coords = sorted(targets)

        def heuristic(gx: int, gy: int) -> float:
            best = 1e9
            for _, tx, ty in target_coords:
                dx_t, dy_t = abs(gx - tx), abs(gy - ty)
                d = max(dx_t, dy_t) + 0.414 * min(dx_t, dy_t)
                best = min(best, d)
            return best

        pq: list[tuple[float, float, int, int, int, int]] = []
        best_g: dict[tuple[int, int, int], float] = {}
        parent: dict[tuple[int, int, int], tuple[int, int, int] | None] = {}
        for s in starts:
            best_g[s] = 0.0
            parent[s] = None
            heapq.heappush(pq, (heuristic(s[1], s[2]), 0.0, s[0], s[1], s[2], -1))

        dirs = (
            (1, 0, 1.0),
            (-1, 0, 1.0),
            (0, 1, 1.0),
            (0, -1, 1.0),
            (1, 1, 1.414),
            (1, -1, 1.414),
            (-1, 1, 1.414),
            (-1, -1, 1.414),
        )
        while pq:
            _, cg, cl, cx, cy, cdir = heapq.heappop(pq)
            state = (cl, cx, cy)
            if cg > best_g.get(state, 1e18):
                continue
            if state in targets:
                path: list[tuple[int, int, int]] = []
                cur: tuple[int, int, int] | None = state
                while cur is not None:
                    path.append(cur)
                    cur = parent[cur]
                path.reverse()
                return path

            for d_i, (dx, dy, step_cost) in enumerate(dirs):
                nx_i, ny_i = cx + dx, cy + dy
                nstate = (cl, nx_i, ny_i)
                if nstate not in targets and not self.is_passable(
                    cl, nx_i, ny_i, net_code
                ):
                    continue
                if (
                    dx != 0
                    and dy != 0
                    and (
                        (
                            (cl, cx + dx, cy) not in targets
                            and not self.is_passable(cl, cx + dx, cy, net_code)
                        )
                        or (
                            (cl, cx, cy + dy) not in targets
                            and not self.is_passable(cl, cx, cy + dy, net_code)
                        )
                    )
                ):
                    continue
                bend = 0.25 if (cdir != -1 and cdir != d_i) else 0.0
                hv_pen = (
                    1.2 if ((cl == 0 and dy != 0) or (cl == 1 and dx != 0)) else 0.0
                )
                layer_pen = (
                    0.08
                    if (preferred_layer is not None and cl != preferred_layer)
                    else 0.0
                )
                ng = cg + step_cost + bend + hv_pen + layer_pen
                if ng < best_g.get(nstate, 1e18):
                    best_g[nstate] = ng
                    parent[nstate] = state
                    heapq.heappush(
                        pq, (ng + heuristic(nx_i, ny_i), ng, cl, nx_i, ny_i, d_i)
                    )

            nl = 1 - cl
            vstate = (nl, cx, cy)
            is_tht_pad = self.tht_pad_grid.get((cx, cy)) == net_code
            if is_tht_pad and (
                vstate in targets or self.is_passable(nl, cx, cy, net_code)
            ):
                if cg < best_g.get(vstate, 1e18):
                    best_g[vstate] = cg
                    parent[vstate] = state
                    heapq.heappush(pq, (cg + heuristic(cx, cy), cg, nl, cx, cy, -1))
            elif self.can_place_via(cx, cy, net_code) and (
                vstate in targets or self.is_passable(nl, cx, cy, net_code)
            ):
                silk_pen = 20.0 if self.silk_via_avoid[cy * self.nx + cx] else 0.0
                ng = cg + 6.0 + silk_pen
                if ng < best_g.get(vstate, 1e18):
                    best_g[vstate] = ng
                    parent[vstate] = state
                    heapq.heappush(pq, (ng + heuristic(cx, cy), ng, nl, cx, cy, -1))

        return None


def _pad_anchor(
    router: GridRouter,
    pad: pcbnew.PAD,
    fp: pcbnew.FOOTPRINT,
    layer: int,
    net_code: int,
    is_tht: bool,
) -> tuple[float, float, int, int]:
    """Find a passable grid anchor (ax, ay, gx, gy) on `layer` for `pad`."""
    pos = pad.GetPosition()
    px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
    gx0, gy0 = router.to_grid(px, py)
    if is_tht:
        return px, py, gx0, gy0

    # If pad center's nearest grid point is passable (or belongs to this net in pad_net), use it
    idx0 = gy0 * router.nx + gx0
    if not router.static_block[layer][idx0]:
        own0 = router.owner[layer][idx0]
        pnet0 = router.pad_net[layer][idx0]
        if (own0 in (-1, net_code)) and (pnet0 in (-1, net_code)):
            return px, py, gx0, gy0

    # Otherwise search outward from the pad's copper edge away from the footprint center
    fpos = fp.GetPosition()
    fx, fy = pcbnew.ToMM(fpos.x), pcbnew.ToMM(fpos.y)
    _, _, bx0, by0, bx1, by1, _ = extract_pad_geometry(pad)
    dx_out = px - fx
    dy_out = py - fy

    # Candidate ring around pad edges within 1.5 mm
    cands: list[tuple[float, float, int, int]] = []
    min_gx = max(0, math.floor((bx0 - 1.2) / router.step))
    max_gx = min(router.nx - 1, math.ceil((bx1 + 1.2) / router.step))
    min_gy = max(0, math.floor((by0 - 1.2) / router.step))
    max_gy = min(router.ny - 1, math.ceil((by1 + 1.2) / router.step))
    for gy in range(min_gy, max_gy + 1):
        ay = router.y0 + gy * router.step
        for gx in range(min_gx, max_gx + 1):
            ax = router.x0 + gx * router.step
            if not router.is_passable(layer, gx, gy, net_code):
                continue
            # Prefer outward direction and shortest distance
            dot = (ax - px) * dx_out + (ay - py) * dy_out
            out_pen = 0.0 if dot >= 0 else 2.0
            d = math.hypot(ax - px, ay - py)
            cands.append((out_pen + d, d, gx, gy))
    if cands:
        cands.sort()
        _, _, gx, gy = cands[0]
        return px, py, gx, gy
    return px, py, gx0, gy0


def route_board(
    board: pcbnew.BOARD,
    fps: dict[str, pcbnew.FOOTPRINT],
    net_items: dict[str, pcbnew.NETINFO_ITEM],
    nets: list[dict],
) -> None:
    """Route all nets with pre-placed SMD GND vias, IC escapes, decoupling pre-routes, and 2-layer A*."""
    router = HVGridRouter(
        0.0,
        0.0,
        BOARD_W,
        BOARD_H,
        step=0.25,
        edge_clearance=0.55,
        track_width=0.25,
        clearance=0.205,
    )

    # 1. Block internal F.Cu keepouts (WQP-PJ398SM bushing circles) & QR code via keepout
    for lid, cx, cy, r in extract_keepout_circles(fps):
        router.mark_static_circle(lid, cx, cy, r + 0.35, block_via=True)
    router.mark_via_block_rect(*QR_RECT, margin=0.35)

    # Mark all placed F.SilkS / B.SilkS texts and board polarity graphics for via avoidance
    silk_layers = (pcbnew.F_SilkS, pcbnew.B_SilkS)
    for dr in board.GetDrawings():
        if (
            not hasattr(dr, "IsVisible") or dr.IsVisible()
        ) and dr.GetLayer() in silk_layers:
            bb = dr.GetBoundingBox()
            router.mark_silk_via_rect(
                pcbnew.ToMM(bb.GetLeft()),
                pcbnew.ToMM(bb.GetTop()),
                pcbnew.ToMM(bb.GetRight()),
                pcbnew.ToMM(bb.GetBottom()),
                margin=0.45,
            )
    for fp in fps.values():
        for gi in (fp.Reference(), fp.Value(), *fp.GraphicalItems()):
            if (
                hasattr(gi, "GetText")
                and (not hasattr(gi, "IsVisible") or gi.IsVisible())
                and gi.GetLayer() in silk_layers
            ):
                bb = gi.GetBoundingBox()
                router.mark_silk_via_rect(
                    pcbnew.ToMM(bb.GetLeft()),
                    pcbnew.ToMM(bb.GetTop()),
                    pcbnew.ToMM(bb.GetRight()),
                    pcbnew.ToMM(bb.GetBottom()),
                )

    # 2. Register all pads into GridRouter, blocking SMD pads from receiving vias (VP-001)
    #    and blocking THT holes from receiving co-located vias
    for ref, fp in fps.items():
        for pad in fp.Pads():
            nc = pad.GetNetCode()
            cx, cy, bx0, by0, bx1, by1, layers = extract_pad_geometry(pad)
            is_smd = pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD
            margin = 0.33
            for lid in layers:
                router.mark_pad_box(lid, bx0, by0, bx1, by1, margin, nc)
            if is_smd:
                router.mark_smd_via_block(bx0, by0, bx1, by1, margin=0.05)
            else:
                gx, gy = router.to_grid(cx, cy)
                drill_r = (
                    max(
                        pcbnew.ToMM(pad.GetDrillSize().x),
                        pcbnew.ToMM(pad.GetDrillSize().y),
                    )
                    * 0.5
                )
                hole_block_r = drill_r + 0.15 + 0.30
                hbr2 = hole_block_r * hole_block_r
                span = math.ceil(hole_block_r / router.step)
                for dy_i in range(-span, span + 1):
                    ny_i = gy + dy_i
                    if not (0 <= ny_i < router.ny):
                        continue
                    dy_m = router.to_mm(0, ny_i)[1] - cy
                    for dx_i in range(-span, span + 1):
                        nx_i = gx + dx_i
                        if not (0 <= nx_i < router.nx):
                            continue
                        if dx_i == 0 and dy_i == 0 and nc > 0:
                            router.tht_pad_grid[(nx_i, ny_i)] = nc
                        if (router.to_mm(nx_i, 0)[0] - cx) ** 2 + dy_m * dy_m <= hbr2:
                            router.via_block[ny_i * router.nx + nx_i] = 1

    gnd_item = net_items["GND"]
    gnd_code = gnd_item.GetNetCode()
    emitted_vias: set[tuple[int, int]] = set()
    gnd_via_mm: list[tuple[float, float]] = []

    def mark_via_full(vx: float, vy: float, nc: int) -> None:
        router.mark_via_obstacle(vx, vy, 0.68, nc)
        # Keep adjacent vias >= 0.85 mm center-to-center (0.60mm pad + 0.20mm DRC clearance)
        r_vb = 0.83
        r2 = r_vb * r_vb
        gx0 = max(0, math.floor((vx - r_vb - router.x0) / router.step))
        gx1 = min(router.nx - 1, math.ceil((vx + r_vb - router.x0) / router.step))
        gy0 = max(0, math.floor((vy - r_vb - router.y0) / router.step))
        gy1 = min(router.ny - 1, math.ceil((vy + r_vb - router.y0) / router.step))
        for gy_i in range(gy0, gy1 + 1):
            dy2 = (router.to_mm(0, gy_i)[1] - vy) ** 2
            row = gy_i * router.nx
            for gx_i in range(gx0, gx1 + 1):
                if (router.to_mm(gx_i, 0)[0] - vx) ** 2 + dy2 <= r2:
                    router.via_block[row + gx_i] = 1

    def emit_via_safe(gx: int, gy: int, net_item: pcbnew.NETINFO_ITEM) -> None:
        nc = net_item.GetNetCode()
        if router.tht_pad_grid.get((gx, gy)) == nc:
            return
        if (gx, gy) in emitted_vias:
            return
        vx, vy = router.to_mm(gx, gy)
        add_via(board, vx, vy, net_item, diam=0.60, drill=0.30)
        mark_via_full(vx, vy, nc)
        emitted_vias.add((gx, gy))
        if nc == gnd_code:
            gnd_via_mm.append((vx, vy))

    # 3. Pre-place immediate GND stitching vias for every SMD GND pad on its mounting layer
    for ref, fp in sorted(fps.items()):
        smd_layer = 1 if fp.IsFlipped() else 0
        smd_lid = pcbnew.B_Cu if smd_layer == 1 else pcbnew.F_Cu
        for pad in fp.Pads():
            if (
                pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD
                or pad.GetNetCode() != gnd_code
            ):
                continue
            pos = pad.GetPosition()
            px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            fpos = fp.GetPosition()
            fx, fy = pcbnew.ToMM(fpos.x), pcbnew.ToMM(fpos.y)
            gx_p, gy_p = router.to_grid(px, py)
            is_ic = ref in ("U1", "U2")
            cands: list[tuple[float, int, int]] = []
            for dy_g in range(-12, 13):
                for dx_g in range(-12, 13):
                    gx, gy = gx_p + dx_g, gy_p + dy_g
                    if not (2 <= gx < router.nx - 2 and 2 <= gy < router.ny - 2):
                        continue
                    if not router.can_place_via(gx, gy, gnd_code):
                        continue
                    vx, vy = router.to_mm(gx, gy)
                    d = math.hypot(vx - px, vy - py)
                    if d > 3.2:
                        continue
                    inward = (vx - px) * (fx - px) + (vy - py) * (fy - py)
                    bias = (
                        (-0.5 if inward > 0 else 0.5)
                        if is_ic
                        else (-0.2 if inward < 0 else 0.0)
                    )
                    silk_pen = (
                        10.0 if router.silk_via_avoid[gy * router.nx + gx] else 0.0
                    )
                    cands.append((d + bias + silk_pen, gx, gy))
            cands.sort()
            placed = False
            for _, gx, gy in cands:
                vx, vy = router.to_mm(gx, gy)
                steps = max(2, math.ceil(math.hypot(vx - px, vy - py) / 0.15))
                ok = True
                for s_i in range(1, steps + 1):
                    t = s_i / steps
                    sx, sy = px + (vx - px) * t, py + (vy - py) * t
                    sgx, sgy = router.to_grid(sx, sy)
                    if (
                        not router.is_passable(smd_layer, sgx, sgy, gnd_code)
                        and router.pad_net[smd_layer][sgy * router.nx + sgx] != gnd_code
                    ):
                        ok = False
                        break
                if ok:
                    add_track(board, smd_lid, px, py, vx, vy, 0.25, gnd_item)
                    router.mark_segment(smd_layer, px, py, vx, vy, 0.25, gnd_code)
                    emit_via_safe(gx, gy, gnd_item)
                    placed = True
                    break
            if not placed:
                raise RuntimeError(
                    f"Failed to place GND stitching via for {ref}.{pad.GetNumber()}"
                )

    # 4. Pre-route local IC decoupling pairs on their mounting layer & reserve outward IC signal escape stubs
    pre_routed_clusters: dict[str, list[tuple[int, int, int]]] = {}
    pre_anchors: dict[tuple[str, str], tuple[int, int, int]] = {}
    pre_junctions: dict[str, set[tuple[int, int, int]]] = {}

    def add_pre_seg(
        nname: str, layer: int, ax: float, ay: float, bx: float, by: float, width: float
    ) -> None:
        ni = net_items[nname]
        nc = ni.GetNetCode()
        lid = pcbnew.F_Cu if layer == 0 else pcbnew.B_Cu
        add_track(board, lid, ax, ay, bx, by, width, ni)
        router.mark_segment(layer, ax, ay, bx, by, width, nc)

    # Pre-route U1/U2 <-> C_DEC1..C_DEC4 power pairs directly on B.Cu
    for ic_ref, ic_pin, cap_ref, cap_pin, nname in (
        ("U1", "4", "C_DEC1", "1", "+12V"),
        ("U1", "11", "C_DEC2", "1", "-12V"),
        ("U2", "4", "C_DEC3", "1", "+12V"),
        ("U2", "11", "C_DEC4", "1", "-12V"),
    ):
        ic_layer = 1 if fps[ic_ref].IsFlipped() else 0
        p_ic = next(
            p for p in fps[ic_ref].Pads() if p.GetNumber() == ic_pin
        ).GetPosition()
        p_cap = next(
            p for p in fps[cap_ref].Pads() if p.GetNumber() == cap_pin
        ).GetPosition()
        ix, iy = pcbnew.ToMM(p_ic.x), pcbnew.ToMM(p_ic.y)
        cx, cy = pcbnew.ToMM(p_cap.x), pcbnew.ToMM(p_cap.y)
        gx_c, gy_c = router.to_grid(cx, cy)
        gx_i, gy_i = router.to_grid(ix, iy)
        gix, giy = router.to_mm(gx_i, gy_i)
        gcx, gcy = router.to_mm(gx_c, gy_c)
        add_pre_seg(nname, ic_layer, ix, iy, gix, giy, 0.30)
        add_pre_seg(nname, ic_layer, gix, giy, gcx, gcy, 0.30)
        add_pre_seg(nname, ic_layer, gcx, gcy, cx, cy, 0.30)
        pre_anchors[(ic_ref, ic_pin)] = (ic_layer, gx_i, gy_i)
        pre_anchors[(cap_ref, cap_pin)] = (ic_layer, gx_c, gy_c)
        pre_routed_clusters.setdefault(nname, []).extend(
            [(ic_layer, gx_i, gy_i), (ic_layer, gx_c, gy_c)]
        )
        pre_junctions.setdefault(nname, set()).update(
            [(ic_layer, gx_i, gy_i), (ic_layer, gx_c, gy_c)]
        )

    # Reserve outward escape stubs for U1 & U2 signal pins before general routing
    for ic_ref in ("U1", "U2"):
        fp = fps[ic_ref]
        ic_layer = 1 if fp.IsFlipped() else 0
        fpos = fp.GetPosition()
        fx, fy = pcbnew.ToMM(fpos.x), pcbnew.ToMM(fpos.y)
        for pad in fp.Pads():
            pin = pad.GetNumber()
            nname = pad.GetNetname()
            if not nname or nname == "GND" or (ic_ref, pin) in pre_anchors:
                continue
            nc = pad.GetNetCode()
            pos = pad.GetPosition()
            px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            _, _, bx0, by0, bx1, by1, _ = extract_pad_geometry(pad)
            if ic_ref == "U1":  # rot=90: pads on top (y < fy) and bottom (y > fy)
                ey = by0 - 0.50 if py < fy else by1 + 0.50
                gx, gy = router.to_grid(px, ey)
            else:  # U2 rot=0: pads on left (x < fx) and right (x > fx)
                ex = bx0 - 0.50 if px < fx else bx1 + 0.50
                gx, gy = router.to_grid(ex, py)
            ax, ay = router.to_mm(gx, gy)
            add_pre_seg(nname, ic_layer, px, py, ax, ay, 0.25)
            pre_anchors[(ic_ref, pin)] = (ic_layer, gx, gy)
            pre_junctions.setdefault(nname, set()).add((ic_layer, gx, gy))

    # Pre-bridge adjacent same-net pins (RV1.2-3, RV2.2-3, U2.13-14)
    for r1, p1, r2, p2, nname in (
        ("RV1", "2", "RV1", "3", "PREAMP_OUT"),
        ("RV2", "2", "RV2", "3", "ENV_NODE"),
        ("U2", "13", "U2", "14", "IN_BUF"),
    ):
        if (r1, p1) in pre_anchors and (r2, p2) in pre_anchors:
            a1, a2 = pre_anchors[(r1, p1)], pre_anchors[(r2, p2)]
            layer = a1[0]
        else:
            layer = (
                1
                if (
                    fps[r1].IsFlipped()
                    and any(
                        p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD
                        for p in fps[r1].Pads()
                    )
                )
                else 0
            )
            pos1 = next(p for p in fps[r1].Pads() if p.GetNumber() == p1).GetPosition()
            pos2 = next(p for p in fps[r2].Pads() if p.GetNumber() == p2).GetPosition()
            gx1, gy1 = router.to_grid(pcbnew.ToMM(pos1.x), pcbnew.ToMM(pos1.y))
            gx2, gy2 = router.to_grid(pcbnew.ToMM(pos2.x), pcbnew.ToMM(pos2.y))
            a1, a2 = (layer, gx1, gy1), (layer, gx2, gy2)
            pre_anchors[(r1, p1)] = a1
            pre_anchors[(r2, p2)] = a2
            pre_junctions.setdefault(nname, set()).update([a1, a2])
        x1, y1 = router.to_mm(a1[1], a1[2])
        x2, y2 = router.to_mm(a2[1], a2[2])
        add_pre_seg(nname, layer, x1, y1, x2, y2, 0.25)

    # 5. Order remaining nets: tight constrained pins & cross-board spines first, then power, then short signals
    net_map = {n["name"]: n for n in nets}
    net_order: list[str] = []
    constrained = [
        "OFF_WIPER",
        "OFF_TOP",
        "OFF_BOT",
        "U1B_OUT",
        "U2A_OUT",
        "U1D_IN",
        "ATK_IN",
        "U2C_OUT",
        "RECT_HW",
        "FF_MID",
        "RECT_FB_MID",
        "U2B_IN",
        "U2B_OUT",
        "LED_K",
        "U2A_INV",
        "REL_POT_TOP",
        "IN_BUF",
        "U1B_INV",
        "U1C_INV",
        "U1A_INV",
        "U1D_INV",
        "PREAMP_OUT",
        "U1D_OUT",
        "ENV_NODE",
        "RECT_OUT",
        "OUT_CLAMP",
        "INV_OUT_CLAMP",
        "IN_AC",
        "U2D_IN",
        "-12V",
        "+12V",
        "IN_AC_PRE",
        "IN_TIP",
        "+12V_IN",
        "-12V_IN",
        "+12V_PROT",
        "-12V_PROT",
    ]
    for nname in constrained:
        if nname in net_map and nname not in net_order:
            net_order.append(nname)
    for nname in sorted(POWER_NETS):
        if nname in net_map and nname not in net_order:
            net_order.append(nname)

    def net_span(nname: str) -> float:
        xs, ys = [], []
        for ref, pin in net_map[nname]["nodes"]:
            pad = next(p for p in fps[ref].Pads() if p.GetNumber() == pin)
            pos = pad.GetPosition()
            xs.append(pcbnew.ToMM(pos.x))
            ys.append(pcbnew.ToMM(pos.y))
        return (max(xs) - min(xs)) + (max(ys) - min(ys)) if xs else 0.0

    rest = [n["name"] for n in nets if n["name"] not in ("GND", *net_order)]
    rest.sort(key=net_span)
    net_order.extend(rest)

    # 6. Route every non-GND net via Prim/MST A*
    for nname in net_order:
        ndef = net_map[nname]
        nodes = ndef["nodes"]
        if len(nodes) < 2:
            continue
        net_item = net_items[nname]
        nc = net_item.GetNetCode()
        width = 0.30 if nname in POWER_NETS else 0.25
        layer_id_map = {0: pcbnew.F_Cu, 1: pcbnew.B_Cu}

        terminals: list[tuple[int, int, int]] = []
        junctions: set[tuple[int, int, int]] = set(pre_junctions.get(nname, set()))
        for ref, pin in nodes:
            if (ref, pin) in pre_anchors:
                terminals.append(pre_anchors[(ref, pin)])
                continue
            fp = fps[ref]
            pad = next(p for p in fp.Pads() if p.GetNumber() == pin)
            is_tht = pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD
            layer = 0 if is_tht or not fp.IsFlipped() else 1
            px, py, gx, gy = _pad_anchor(router, pad, fp, layer, nc, is_tht)
            ax, ay = router.to_mm(gx, gy)
            if math.hypot(ax - px, ay - py) > 0.01:
                add_track(board, layer_id_map[layer], px, py, ax, ay, width, net_item)
                router.mark_segment(layer, px, py, ax, ay, width, nc)
            terminals.append((layer, gx, gy))
            junctions.add((layer, gx, gy))

        unique_terms: list[tuple[int, int, int]] = []
        for t in terminals:
            if t not in unique_terms:
                unique_terms.append(t)
        if len(unique_terms) < 2:
            continue

        # Handle already-connected decoupling pairs in +12V / -12V
        connected: list[tuple[int, int, int]] = [unique_terms[0]]
        remaining = list(unique_terms[1:])
        raw_paths: list[list[tuple[int, int, int]]] = []

        # Keep track of pre-connected pairs (IC + decoupling cap, adjacent same-net pins)
        pair_table = {
            "+12V": [("U1", "4", "C_DEC1", "1"), ("U2", "4", "C_DEC3", "1")],
            "-12V": [("U1", "11", "C_DEC2", "1"), ("U2", "11", "C_DEC4", "1")],
            "PREAMP_OUT": [("RV1", "2", "RV1", "3")],
            "ENV_NODE": [("RV2", "2", "RV2", "3")],
            "IN_BUF": [("U2", "13", "U2", "14")],
        }
        paired_anchors: dict[tuple[int, int, int], tuple[int, int, int]] = {}
        for r1, p1, r2, p2 in pair_table.get(nname, ()):
            a1, a2 = pre_anchors[(r1, p1)], pre_anchors[(r2, p2)]
            paired_anchors[a1] = a2
            paired_anchors[a2] = a1
        if connected[0] in paired_anchors and paired_anchors[connected[0]] in remaining:
            partner = paired_anchors[connected[0]]
            remaining.remove(partner)
            connected.append(partner)

        while remaining:
            best_idx = 0
            best_d = 1e9
            for idx, rterm in enumerate(remaining):
                for cterm in connected:
                    d = abs(rterm[1] - cterm[1]) + abs(rterm[2] - cterm[2])
                    if d < best_d:
                        best_d = d
                        best_idx = idx
            src = remaining.pop(best_idx)
            starts = [src]
            partner = paired_anchors.get(src)
            if partner is not None and partner in remaining:
                remaining.remove(partner)
                starts.append(partner)
            targets = set(connected)
            pref = 1 if nname in POWER_NETS else None
            path = router.route(starts, targets, nc, preferred_layer=pref)
            if path is None:
                raise RuntimeError(
                    f"Routing failed for net {nname} from {starts} to {len(targets)} targets"
                )
            raw_paths.append(path)
            junctions.add(path[0])
            junctions.add(path[-1])
            connected.extend(path)
            for s in starts:
                if s not in connected:
                    connected.append(s)
            for k in range(len(path) - 1):
                l0, x0, y0 = path[k]
                l1, x1, y1 = path[k + 1]
                if l0 == l1:
                    ax0, ay0 = router.to_mm(x0, y0)
                    ax1, ay1 = router.to_mm(x1, y1)
                    router.mark_segment(l0, ax0, ay0, ax1, ay1, width, nc)
                else:
                    if router.tht_pad_grid.get((x0, y0)) != nc:
                        vx, vy = router.to_mm(x0, y0)
                        mark_via_full(vx, vy, nc)

        for path in raw_paths:
            merged = _merge_collinear_path(path, junctions)
            for k in range(len(merged) - 1):
                l0, x0, y0 = merged[k]
                l1, x1, y1 = merged[k + 1]
                if l0 == l1:
                    ax0, ay0 = router.to_mm(x0, y0)
                    ax1, ay1 = router.to_mm(x1, y1)
                    add_track(
                        board, layer_id_map[l0], ax0, ay0, ax1, ay1, width, net_item
                    )
                else:
                    emit_via_safe(x0, y0, net_item)

    # 7. Add distributed GND stitching vias (avoiding QR & silk text), pour copper zones, and stitch any isolated pockets
    for gy in range(8, router.ny - 7, 4):
        for gx in range(8, router.nx - 7, 4):
            if router.silk_via_avoid[gy * router.nx + gx] or not router.can_place_via(
                gx, gy, gnd_code
            ):
                continue
            vx, vy = router.to_mm(gx, gy)
            if any(math.hypot(vx - ox, vy - oy) < 3.2 for ox, oy in gnd_via_mm):
                continue
            emit_via_safe(gx, gy, gnd_item)

    pour_gnd_zones(
        board, gnd_item, 0.0, 0.0, BOARD_W, BOARD_H, edge_clearance=0.50, clearance=0.20
    )

    def _in_outline(outline: pcbnew.SHAPE_LINE_CHAIN, x_mm: float, y_mm: float) -> bool:
        n = outline.PointCount()
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = pcbnew.ToMM(outline.CPoint(i).x), pcbnew.ToMM(outline.CPoint(i).y)
            xj, yj = pcbnew.ToMM(outline.CPoint(j).x), pcbnew.ToMM(outline.CPoint(j).y)
            if ((yi > y_mm) != (yj > y_mm)) and (
                x_mm < (xj - xi) * (y_mm - yi) / (yj - yi + 1e-12) + xi
            ):
                inside = not inside
            j = i
        return inside

    for _ in range(3):
        board.BuildConnectivity()
        zones_by_layer = {next(iter(z.GetLayerSet().Seq())): z for z in board.Zones()}
        added_stitch = False
        for lid, zone in zones_by_layer.items():
            pset = zone.GetFilledPolysList(lid)
            if pset.OutlineCount() <= 1:
                continue
            opp_lid = pcbnew.B_Cu if lid == pcbnew.F_Cu else pcbnew.F_Cu
            opp_pset = zones_by_layer[opp_lid].GetFilledPolysList(opp_lid)
            opp_main = max(
                range(opp_pset.OutlineCount()),
                key=lambda k: opp_pset.Outline(k).PointCount(),
            )
            opp_outline = opp_pset.Outline(opp_main)
            main_idx = max(
                range(pset.OutlineCount()), key=lambda k: pset.Outline(k).PointCount()
            )
            for k in range(pset.OutlineCount()):
                if k == main_idx:
                    continue
                outline = pset.Outline(k)
                xs = [
                    pcbnew.ToMM(outline.CPoint(j).x)
                    for j in range(outline.PointCount())
                ]
                ys = [
                    pcbnew.ToMM(outline.CPoint(j).y)
                    for j in range(outline.PointCount())
                ]
                gx0, gx1 = (
                    max(2, math.floor(min(xs) / router.step)),
                    min(router.nx - 3, math.ceil(max(xs) / router.step)),
                )
                gy0, gy1 = (
                    max(2, math.floor(min(ys) / router.step)),
                    min(router.ny - 3, math.ceil(max(ys) / router.step)),
                )
                pocket_cands: list[tuple[int, int, int]] = []
                for gy in range(gy0, gy1 + 1):
                    for gx in range(gx0, gx1 + 1):
                        if not router.can_place_via(gx, gy, gnd_code):
                            continue
                        vx, vy = router.to_mm(gx, gy)
                        if _in_outline(outline, vx, vy) and _in_outline(
                            opp_outline, vx, vy
                        ):
                            pen = 1 if router.silk_via_avoid[gy * router.nx + gx] else 0
                            pocket_cands.append((pen, gx, gy))
                if pocket_cands:
                    pocket_cands.sort()
                    _, gx, gy = pocket_cands[0]
                    emit_via_safe(gx, gy, gnd_item)
                    added_stitch = True
        if not added_stitch:
            break
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        board.BuildConnectivity()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate 6 HP Envelope Follower KiCad PCB."
    )
    parser.add_argument(
        "--check-pack", action="store_true", help="Place and check silkscreen only."
    )
    args = parser.parse_args()

    components, nets = parse_netlist(
        HERE / "envelope_follower.net", dnp_prefixes=("TP", "FID")
    )
    placements = build_placements()
    out_path = HERE / "EnvelopeFollower.kicad_pcb"
    board = create_base_board(
        out_path,
        0.0,
        0.0,
        BOARD_W,
        BOARD_H,
        title="ENVELOPE FOLLOWER",
        revision="REV 1.0",
        date="2026-11",
        edge_clearance=0.50,
    )
    fps = populate_footprints(board, components, placements)
    for ref, fp in fps.items():
        if ref.startswith(("FID", "TP")):
            fp.SetDNP(True)
            fp.SetExcludedFromBOM(True)
            fp.SetExcludedFromPosFiles(True)
    net_items, _ = assign_nets(board, fps, nets)
    check_geometry(fps)
    apply_silkscreen_and_fab(board, fps, components)

    if not args.check_pack:
        route_board(board, fps, net_items, nets)

    pcbnew.SaveBoard(str(out_path), board)
    print(f"Saved {out_path} ({len(fps)} footprints, {len(nets)} nets)")
    ok = inspect_board_silk(out_path)
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
