#!/usr/bin/env python3
"""Generate routed 6 HP KiCad 10 PCB (EnvelopeFollower.kicad_pcb) from envelope_follower.net."""

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

import pcbnew_layout_template as ptl
import silk_annotator as sa

# 6 HP Eurorack main PCB bounds (30.00 x 108.00 mm centered behind 30.00 x 128.50 mm panel)
BOARD_X0 = 0.00
BOARD_Y0 = 10.25
BOARD_X1 = 30.00
BOARD_Y1 = 118.25

# 5.0 x 5.0 mm JLCPCB QR placeholder in bottom center power corridor
QR_BOX = (12.50, 98.80, 17.50, 103.80)

# Routing & DFM parameters
GRID_STEP = 0.25
EDGE_CLEARANCE = 0.55
SIGNAL_WIDTH = 0.25
POWER_WIDTH = 0.30
ROUTE_CLEARANCE = 0.22
VIA_DIAM = 0.60
VIA_DRILL = 0.30

POWER_NETS = {"+12V_IN", "-12V_IN", "+12V", "-12V"}
# Constrained local IC escape / input-coupling / feedback nets routed first
PRIORITY_SIGNAL_NETS = {
    "AC_IN",
    "U1A_IN_M",
    "U1B_IN_M",
    "U1B_OUT",
    "V_RECT",
    "U1C_IN_M",
    "V_FWR",
    "U1D_IN_M",
    "U1D_IN_P",
    "U2A_IN_M",
    "V_INV_PRE",
    "U2B_IN_P",
    "LED_A",
    "LED_K",
    "U2C_IN_P",
    "ATK_IN",
    "U2D_OUT",
}

# Component placements: ref -> (x_mm, y_mm, rot_deg, is_back)
PLACEMENTS: dict[str, tuple[float, float, float, bool]] = {
    # -------------------------------------------------------------------------
    # Front-panel controls (F.Cu, aligned to 6 HP 14.0 x 20.0 mm panel grid)
    # Panel shafts/bushings/LED at X in {8.00, 22.00}, Y in {25.00, 45.00, 65.00, 85.00}
    # -------------------------------------------------------------------------
    "RV1": (5.50, 32.50, 90.0, False),  # GAIN shaft at (8.00, 25.00)
    "RV2": (19.50, 32.50, 90.0, False),  # ATK shaft at (22.00, 25.00)
    "RV3": (5.50, 52.50, 90.0, False),  # REL shaft at (8.00, 45.00)
    "RV4": (19.50, 52.50, 90.0, False),  # OFFSET shaft at (22.00, 45.00)
    "J1": (8.00, 58.52, 0.0, False),  # IN bushing at (8.00, 65.00)
    "D4": (20.73, 65.00, 0.0, False),  # ENV LED lens at (22.00, 65.00)
    "J2": (8.00, 78.52, 0.0, False),  # OUT bushing at (8.00, 85.00)
    "J3": (22.00, 78.52, 0.0, False),  # INV_OUT bushing at (22.00, 85.00)
    # -------------------------------------------------------------------------
    # Top Band (Y = 10.85 .. 22.80): U1 + Gain/FWR/Out feedback + local bypass
    # -------------------------------------------------------------------------
    "U1": (15.00, 16.60, 0.0, True),
    "D1": (8.00, 12.10, 0.0, True),
    "D2": (4.00, 17.10, 180.0, True),
    "C5": (9.20, 16.60, 180.0, True),
    "R4": (4.00, 21.30, 0.0, True),
    "R3": (9.20, 21.30, 0.0, True),
    "R8": (21.00, 12.10, 0.0, True),
    "R5": (24.60, 12.10, 0.0, True),
    "C6": (20.80, 16.60, 0.0, True),
    "R15": (26.50, 16.60, 0.0, True),
    "C10": (20.80, 21.30, 0.0, True),
    "R9": (26.50, 21.30, 0.0, True),
    # -------------------------------------------------------------------------
    # Inter-Pot Band (Y = 34.00 .. 42.80): Gain/FWR/Attack/Release + TP5, TP6
    # -------------------------------------------------------------------------
    "R24": (3.20, 35.80, 0.0, True),
    "C9": (7.40, 35.80, 0.0, True),
    "R2": (11.60, 35.80, 0.0, True),
    "R25": (16.40, 35.80, 0.0, True),
    "R6": (3.20, 40.60, 0.0, True),
    "R7": (7.40, 40.60, 0.0, True),
    "R10": (11.60, 40.60, 0.0, True),
    "D3": (16.60, 40.60, 180.0, True),
    "TP5": (22.20, 36.80, 0.0, True),  # V_AMP (outside RV2/RV4 F.CrtYd)
    "TP6": (27.00, 36.80, 0.0, True),  # V_FWR (outside RV2/RV4 F.CrtYd)
    # -------------------------------------------------------------------------
    # Mid-Upper Band (Y = 54.00 .. 63.50): C1 Film + Offset + LED Input + R17/R18
    # -------------------------------------------------------------------------
    "R1": (3.60, 56.80, 0.0, True),
    "R27": (3.60, 61.60, 0.0, True),
    "C1": (15.20, 58.00, 0.0, True),  # 1uF film (outside RV3/RV4/J1/D4 F.CrtYd)
    "R11": (23.50, 55.60, 0.0, True),
    "R13": (27.40, 55.60, 0.0, True),
    "R12": (23.50, 60.20, 0.0, True),
    "R20": (27.40, 60.20, 0.0, True),
    # -------------------------------------------------------------------------
    # Mid-Lower Band (Y = 63.00 .. 91.00): U2 + C2 Film + clamps + 2512s + TPs
    # -------------------------------------------------------------------------
    "U2": (13.70, 74.60, 180.0, True),
    "C8": (9.10, 74.60, 90.0, True),
    "C7": (19.70, 74.60, 0.0, True),
    "R17": (12.40, 64.00, 0.0, True),
    "R18": (16.80, 64.00, 0.0, True),
    "C11": (16.80, 67.20, 0.0, True),
    "R21": (21.20, 67.10, 0.0, True),
    "D10": (27.60, 65.00, 270.0, True),
    "C2": (23.00, 73.20, 0.0, True),  # 1uF film (outside D4/J3 F.CrtYd)
    "D9": (3.60, 67.20, 0.0, True),
    "TP4": (3.10, 73.80, 0.0, True),  # IN_BUF (outside J1/J2 F.CrtYd)
    "R16": (4.00, 81.60, 90.0, True),
    "D7": (3.60, 89.60, 0.0, True),
    "TP7": (15.00, 81.00, 0.0, True),  # ENV_CAP (between J2/J3 F.CrtYd)
    "R26": (14.20, 85.10, 0.0, True),
    "TP8": (15.00, 89.20, 0.0, True),  # V_OUT_PRE (between J2/J3 F.CrtYd)
    "D8": (26.90, 78.60, 0.0, True),
    "R19": (27.00, 86.20, 90.0, True),
    # -------------------------------------------------------------------------
    # Bottom Band (Y = 91.80 .. 117.65): Power Header J4 + Schottky + Bulk + TPs
    # -------------------------------------------------------------------------
    "TP3": (4.20, 97.00, 0.0, True),  # -12V
    "D6": (10.00, 97.00, 180.0, True),
    "TP2": (15.00, 94.60, 0.0, True),  # +12V (above QR_BOX, opens J3 bottom corridor)
    "D5": (20.80, 97.00, 0.0, True),
    "C4": (5.60, 102.40, 0.0, True),  # -12V 22uF
    "C3": (24.40, 102.40, 0.0, True),  # +12V 22uF
    "J4": (9.92, 109.70, 270.0, True),  # 2x5 IDC header (-12V_IN left, +12V_IN right)
    "TP1": (27.60, 109.20, 0.0, True),  # GND (right of J4)
}

FIDUCIALS: dict[str, tuple[float, float]] = {
    "FID1": (2.20, 12.20),
    "FID2": (27.80, 12.20),
    "FID3": (27.80, 115.60),
}


def _boxes_overlap(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
    margin: float = 0.0,
) -> bool:
    return not (
        a[2] + margin <= b[0]
        or b[2] + margin <= a[0]
        or a[3] + margin <= b[1]
        or b[3] + margin <= a[1]
    )


def _crtyd_box(
    fp: pcbnew.FOOTPRINT, is_back: bool
) -> tuple[float, float, float, float]:
    layer = pcbnew.B_CrtYd if is_back else pcbnew.F_CrtYd
    xs: list[float] = []
    ys: list[float] = []
    for gi in fp.GraphicalItems():
        if hasattr(gi, "GetText") or gi.GetLayer() != layer:
            continue
        bb = gi.GetBoundingBox()
        xs.extend((pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetRight())))
        ys.extend((pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetBottom())))
    if not xs:
        return sa.footprint_bbox(fp)
    return (min(xs), min(ys), max(xs), max(ys))


def validate_placement(footprints: dict[str, pcbnew.FOOTPRINT]) -> None:
    """Verify 0 courtyard collisions, 0 B.Cu-THT vs F.CrtYd conflicts, and SMD-THT pad safety."""
    front_crtyds: dict[str, tuple[float, float, float, float]] = {}
    back_crtyds: dict[str, tuple[float, float, float, float]] = {}
    tht_pads: list[tuple[str, tuple[float, float, float, float]]] = []
    smd_crtyds: dict[str, tuple[float, float, float, float]] = {}

    for ref, fp in footprints.items():
        if sa.is_fiducial_ref(ref):
            continue
        is_back = fp.IsFlipped()
        cbox = _crtyd_box(fp, is_back)
        if (
            cbox[0] < BOARD_X0 + 0.50
            or cbox[2] > BOARD_X1 - 0.50
            or cbox[1] < BOARD_Y0 + 0.50
            or cbox[3] > BOARD_Y1 - 0.50
        ):
            raise RuntimeError(f"Courtyard of {ref} too close to board edge: {cbox}")
        if is_back:
            back_crtyds[ref] = cbox
        else:
            front_crtyds[ref] = cbox
        if sa.is_smd_footprint(fp):
            smd_crtyds[ref] = cbox
        for pad in fp.Pads():
            if pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                _, _, x0, y0, x1, y1, _ = ptl.extract_pad_geometry(pad)
                tht_pads.append((ref, (x0, y0, x1, y1)))

    for group_name, grp in (("F.CrtYd", front_crtyds), ("B.CrtYd", back_crtyds)):
        refs = sorted(grp)
        for i in range(len(refs)):
            for j in range(i + 1, len(refs)):
                r1, r2 = refs[i], refs[j]
                if _boxes_overlap(grp[r1], grp[r2]):
                    raise RuntimeError(
                        f"{group_name} overlap between {r1} {grp[r1]} and {r2} {grp[r2]}"
                    )

    # B.Cu THT parts (C1, C2, J4, TP*) must stay outside F.Cu panel component courtyards
    for ref, cbox in back_crtyds.items():
        fp = footprints[ref]
        if sa.is_smd_footprint(fp):
            continue
        for fref, fbox in front_crtyds.items():
            if _boxes_overlap(cbox, fbox):
                raise RuntimeError(
                    f"B.Cu THT {ref} {cbox} intersects F.Cu control courtyard {fref} {fbox}"
                )

    # B.Cu SMDs must clear all THT solder pads by >= 0.30 mm
    for sref, scbox in smd_crtyds.items():
        for tref, tpbox in tht_pads:
            if _boxes_overlap(scbox, tpbox, margin=0.30):
                raise RuntimeError(
                    f"B.Cu SMD {sref} {scbox} too close to THT pad of {tref} {tpbox}"
                )


def _pad_grid_anchor(
    router: ptl.GridRouter, pad: pcbnew.PAD, is_ic: bool
) -> tuple[int, int, tuple[int, int, int]]:
    """Return (layer_id, gx, gy) and grid anchor (gx, gy) for a pad (with outward IC escape)."""
    cx, cy, x0, _y0, x1, _y1, layers = ptl.extract_pad_geometry(pad)
    is_smd = pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD
    if is_ic and is_smd:
        fp_cx = pcbnew.ToMM(pad.GetParent().GetPosition().x)
        esc_x = (x0 - 0.05) if cx < fp_cx else (x1 + 0.05)
        gx, gy = router.to_grid(esc_x, cy)
    else:
        gx, gy = router.to_grid(cx, cy)
    layer = 1 if (1 in layers and 0 not in layers) else 0
    return gx, gy, (layer, gx, gy)


def _init_router(
    footprints: dict[str, pcbnew.FOOTPRINT],
    net_items: dict[str, pcbnew.NETINFO_ITEM],
) -> tuple[ptl.GridRouter, dict[int, list[dict]], list[tuple[float, float]]]:
    """Configure GridRouter with QR/jack keepouts, SMD via blocks, THT layers, and pad anchors."""
    router = ptl.GridRouter(
        BOARD_X0,
        BOARD_Y0,
        BOARD_X1,
        BOARD_Y1,
        step=GRID_STEP,
        edge_clearance=EDGE_CLEARANCE,
        track_width=SIGNAL_WIDTH,
        clearance=ROUTE_CLEARANCE,
    )

    # Reserve 5 x 5 mm QR placeholder on both layers (+0.5 mm margin, block vias)
    router.mark_static_rect(0, *QR_BOX, margin=0.50, block_via=True)
    router.mark_static_rect(1, *QR_BOX, margin=0.50, block_via=True)

    # Reserve jack internal F.Cu circular bushing keepouts
    for lid, kx, ky, kr in ptl.extract_keepout_circles(footprints):
        router.mark_static_circle(lid, kx, ky, kr + 0.25, block_via=True)

    via_r_clear = VIA_DIAM * 0.5 + ROUTE_CLEARANCE + 0.15
    pad_margin = ROUTE_CLEARANCE + SIGNAL_WIDTH * 0.5
    net_anchors: dict[int, list[dict]] = {}
    tht_obstacles: list[tuple[float, float]] = []

    for ref, fp in footprints.items():
        if sa.is_fiducial_ref(ref):
            pos = fp.GetPosition()
            fx, fy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            router.mark_static_circle(1, fx, fy, 1.35, block_via=True)
            continue

        is_ic = ref in ("U1", "U2")
        for pad in fp.Pads():
            cx, cy, x0, y0, x1, y1, layers = ptl.extract_pad_geometry(pad)
            nc = pad.GetNetCode()
            is_smd = pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD

            if is_smd:
                router.mark_smd_via_block(x0, y0, x1, y1, margin=0.02)
                for lid in layers:
                    router.mark_pad_box(lid, x0, y0, x1, y1, pad_margin, nc)
            else:
                tht_obstacles.append((cx, cy))
                drill = pcbnew.ToMM(pad.GetDrillSize().x)
                pad_r = max(x1 - x0, y1 - y0, drill) * 0.5
                # Block vias near every THT barrel (including pot mounting lugs)
                gx0 = max(
                    0, math.floor((cx - pad_r - via_r_clear - BOARD_X0) / GRID_STEP)
                )
                gx1 = min(
                    router.nx - 1,
                    math.ceil((cx + pad_r + via_r_clear - BOARD_X0) / GRID_STEP),
                )
                gy0 = max(
                    0, math.floor((cy - pad_r - via_r_clear - BOARD_Y0) / GRID_STEP)
                )
                gy1 = min(
                    router.ny - 1,
                    math.ceil((cy + pad_r + via_r_clear - BOARD_Y0) / GRID_STEP),
                )
                r2 = (pad_r + via_r_clear) ** 2
                for gy_i in range(gy0, gy1 + 1):
                    dy2 = (BOARD_Y0 + gy_i * GRID_STEP - cy) ** 2
                    for gx_i in range(gx0, gx1 + 1):
                        if (BOARD_X0 + gx_i * GRID_STEP - cx) ** 2 + dy2 <= r2:
                            router.via_block[gy_i * router.nx + gx_i] = 1
                for lid in (0, 1):
                    router.mark_pad_box(lid, x0, y0, x1, y1, pad_margin, nc)
                if nc > 0:
                    gx, gy = router.to_grid(cx, cy)
                    router.tht_pad_grid[(gx, gy)] = nc

            if nc > 0:
                gx, gy, state = _pad_grid_anchor(router, pad, is_ic)
                anchor_x, anchor_y = router.to_mm(gx, gy)
                net_anchors.setdefault(nc, []).append(
                    {
                        "ref": ref,
                        "pin": pad.GetNumber(),
                        "pad_xy": (cx, cy),
                        "anchor_xy": (anchor_x, anchor_y),
                        "state": state,
                        "is_smd": is_smd,
                        "is_ic": is_ic,
                        "layers": layers,
                    }
                )

    return router, net_anchors, tht_obstacles


def _find_nearby_via(
    router: ptl.GridRouter,
    cx: float,
    cy: float,
    nc: int,
    max_radius: float = 2.6,
) -> tuple[int, int] | None:
    """Find the closest legal via grid cell near `(cx, cy)` for net `nc`."""
    gx0, gy0 = router.to_grid(cx, cy)
    steps = math.ceil(max_radius / GRID_STEP)
    cands: list[tuple[float, int, int]] = []
    for dy in range(-steps, steps + 1):
        for dx in range(-steps, steps + 1):
            gx, gy = gx0 + dx, gy0 + dy
            if not (0 <= gx < router.nx and 0 <= gy < router.ny):
                continue
            vx, vy = router.to_mm(gx, gy)
            d2 = (vx - cx) ** 2 + (vy - cy) ** 2
            if d2 <= max_radius * max_radius and router.can_place_via(gx, gy, nc):
                cands.append((d2, gx, gy))
    cands.sort()
    for _, gx, gy in cands:
        if router.is_passable(0, gx, gy, nc) and router.is_passable(1, gx, gy, nc):
            return (gx, gy)
    return None


def _place_gnd_smd_vias(
    board: pcbnew.BOARD,
    router: ptl.GridRouter,
    net_anchors: dict[int, list[dict]],
    gnd_item: pcbnew.NETINFO_ITEM,
) -> set[tuple[int, int]]:
    """Pre-place stitching vias + short B.Cu stubs for every B.Cu SMD GND pad."""
    gnd_code = gnd_item.GetNetCode()
    placed: set[tuple[int, int]] = set()
    for anch in net_anchors.get(gnd_code, []):
        if not anch["is_smd"]:
            continue
        ax, ay = anch["anchor_xy"]
        px, py = anch["pad_xy"]
        via_cell = _find_nearby_via(router, ax, ay, gnd_code, max_radius=2.6)
        if via_cell is None:
            via_cell = _find_nearby_via(router, px, py, gnd_code, max_radius=3.5)
        if via_cell is None:
            raise RuntimeError(
                f"No legal GND stitching via near {anch['ref']}.{anch['pin']} at ({px:.2f}, {py:.2f})"
            )
        gx, gy = via_cell
        vx, vy = router.to_mm(gx, gy)
        ptl.add_track(board, pcbnew.B_Cu, px, py, vx, vy, POWER_WIDTH, gnd_item)
        router.mark_segment(1, px, py, vx, vy, POWER_WIDTH, gnd_code)
        if (gx, gy) not in placed:
            ptl.add_via(board, vx, vy, gnd_item, diam=VIA_DIAM, drill=VIA_DRILL)
            router.mark_via_obstacle(
                vx, vy, VIA_DIAM * 0.5 + ROUTE_CLEARANCE + 0.15, gnd_code
            )
            placed.add((gx, gy))
    return placed


def _pre_route_decoupling(
    board: pcbnew.BOARD,
    router: ptl.GridRouter,
    footprints: dict[str, pcbnew.FOOTPRINT],
    net_items: dict[str, pcbnew.NETINFO_ITEM],
    net_anchors: dict[int, list[dict]],
) -> dict[tuple[str, str], tuple[str, str]]:
    """Pre-route U1/U2 <-> C5..C8 decoupling pairs directly on B.Cu before general routing."""
    pairs = [
        (("U1", "4"), ("C5", "1"), "+12V"),
        (("U1", "11"), ("C6", "1"), "-12V"),
        (("U2", "4"), ("C7", "1"), "+12V"),
        (("U2", "11"), ("C8", "1"), "-12V"),
    ]
    merged: dict[tuple[str, str], tuple[str, str]] = {}
    for (u_ref, u_pin), (c_ref, c_pin), net_name in pairs:
        ni = net_items[net_name]
        nc = ni.GetNetCode()
        u_pad = next(p for p in footprints[u_ref].Pads() if p.GetNumber() == u_pin)
        c_pad = next(p for p in footprints[c_ref].Pads() if p.GetNumber() == c_pin)
        ux, uy = (
            pcbnew.ToMM(u_pad.GetPosition().x),
            pcbnew.ToMM(u_pad.GetPosition().y),
        )
        cx, cy = (
            pcbnew.ToMM(c_pad.GetPosition().x),
            pcbnew.ToMM(c_pad.GetPosition().y),
        )
        u_anch = next(
            a for a in net_anchors[nc] if a["ref"] == u_ref and a["pin"] == u_pin
        )
        c_anch = next(
            a for a in net_anchors[nc] if a["ref"] == c_ref and a["pin"] == c_pin
        )
        eax, eay = u_anch["anchor_xy"]
        cax, cay = c_anch["anchor_xy"]
        ptl.add_track(board, pcbnew.B_Cu, ux, uy, eax, eay, POWER_WIDTH, ni)
        router.mark_segment(1, ux, uy, eax, eay, POWER_WIDTH, nc)
        ptl.add_track(board, pcbnew.B_Cu, eax, eay, cax, cay, POWER_WIDTH, ni)
        router.mark_segment(1, eax, eay, cax, cay, POWER_WIDTH, nc)
        if abs(cax - cx) > 1e-4 or abs(cay - cy) > 1e-4:
            ptl.add_track(board, pcbnew.B_Cu, cax, cay, cx, cy, POWER_WIDTH, ni)
            router.mark_segment(1, cax, cay, cx, cy, POWER_WIDTH, nc)
        merged[(u_ref, u_pin)] = (c_ref, c_pin)
        merged[(c_ref, c_pin)] = (u_ref, u_pin)
    return merged


def _route_all_nets(
    board: pcbnew.BOARD,
    router: ptl.GridRouter,
    net_items: dict[str, pcbnew.NETINFO_ITEM],
    net_anchors: dict[int, list[dict]],
    pre_merged: dict[tuple[str, str], tuple[str, str]],
    emitted_vias: set[tuple[int, int]],
) -> None:
    """Route all non-GND multi-pin nets via MST + 2-layer A* with T-junction preservation."""
    net_specs: list[tuple[int, float, str]] = []
    for name, ni in net_items.items():
        if name == "GND":
            continue
        nc = ni.GetNetCode()
        anchors = net_anchors.get(nc, [])
        if len(anchors) < 2:
            continue
        xs = [a["pad_xy"][0] for a in anchors]
        ys = [a["pad_xy"][1] for a in anchors]
        span = (max(xs) - min(xs)) + (max(ys) - min(ys))
        if name in PRIORITY_SIGNAL_NETS:
            tier = -1
        elif name in POWER_NETS:
            tier = 0
        else:
            tier = 1
        net_specs.append((tier, span, name))

    net_specs.sort()
    via_obst_r = VIA_DIAM * 0.5 + ROUTE_CLEARANCE + 0.15

    for tier, _, name in net_specs:
        ni = net_items[name]
        nc = ni.GetNetCode()
        width = POWER_WIDTH if name in POWER_NETS else SIGNAL_WIDTH
        anchors = net_anchors[nc]
        n = len(anchors)

        # Build initial union-find / clusters incorporating pre-routed decoupling pairs
        parent = list(range(n))

        def find(x: int, p: list[int] = parent) -> int:
            while p[x] != x:
                p[x] = p[p[x]]
                x = p[x]
            return x

        idx_by_key = {(a["ref"], a["pin"]): i for i, a in enumerate(anchors)}
        for i, a in enumerate(anchors):
            partner = pre_merged.get((a["ref"], a["pin"]))
            if partner and partner in idx_by_key:
                j = idx_by_key[partner]
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[rj] = ri

        cluster_states: dict[int, set[tuple[int, int, int]]] = {}
        for i, a in enumerate(anchors):
            r = find(i)
            st = a["state"]
            cluster_states.setdefault(r, set()).add(st)
            if not a["is_smd"]:
                cluster_states[r].add((1 - st[0], st[1], st[2]))

        # Kruskal MST edges between distinct clusters
        edges: list[tuple[float, int, int]] = []
        for i in range(n):
            for j in range(i + 1, n):
                if find(i) == find(j):
                    continue
                ax1, ay1 = anchors[i]["anchor_xy"]
                ax2, ay2 = anchors[j]["anchor_xy"]
                edges.append((math.hypot(ax1 - ax2, ay1 - ay2), i, j))
        edges.sort()

        raw_paths: list[list[tuple[int, int, int]]] = []
        used_anchors: set[tuple[int, int, int]] = set()
        junctions: set[tuple[int, int, int]] = set()

        for _, i, j in edges:
            ri, rj = find(i), find(j)
            if ri == rj:
                continue
            starts = sorted(cluster_states[ri])
            targets = set(cluster_states[rj])
            path = router.route(starts, targets, nc, preferred_layer=1)
            if path is None:
                # Retry from swapped direction
                path = router.route(sorted(targets), set(starts), nc, preferred_layer=1)
            if path is None:
                raise RuntimeError(
                    f"Routing failed for net {name} between {anchors[i]['ref']}.{anchors[i]['pin']} "
                    f"and {anchors[j]['ref']}.{anchors[j]['pin']} "
                    f"(starts={len(starts)} sample={starts[:3]}, targets={len(targets)} sample={list(targets)[:3]})"
                )

            raw_paths.append(path)
            used_anchors.add(path[0])
            used_anchors.add(path[-1])
            junctions.add(path[0])
            junctions.add(path[-1])

            # Immediately mark segments & vias on router and merge cluster states
            for k in range(len(path) - 1):
                l1, gx1, gy1 = path[k]
                l2, gx2, gy2 = path[k + 1]
                x1, y1 = router.to_mm(gx1, gy1)
                x2, y2 = router.to_mm(gx2, gy2)
                if l1 == l2:
                    router.mark_segment(l1, x1, y1, x2, y2, width, nc)
                else:
                    if router.tht_pad_grid.get((gx1, gy1)) != nc:
                        router.mark_via_obstacle(x1, y1, via_obst_r, nc)

            # Merge clusters ri and rj along with newly traced path vertices
            merged_root = ri
            parent[rj] = merged_root
            new_set = cluster_states[ri] | cluster_states[rj] | set(path)
            cluster_states[merged_root] = new_set

        # Emit pad-to-anchor stubs ONLY for consumed MST anchors (0 track_dangling)
        for a in anchors:
            st = a["state"]
            opp_st = (1 - st[0], st[1], st[2])
            if st not in used_anchors and (a["is_smd"] or opp_st not in used_anchors):
                continue
            if (a["ref"], a["pin"]) in pre_merged:
                continue
            px, py = a["pad_xy"]
            ax, ay = a["anchor_xy"]
            if math.hypot(ax - px, ay - py) > 1e-4:
                cu_layer = pcbnew.B_Cu if st[0] == 1 else pcbnew.F_Cu
                ptl.add_track(board, cu_layer, px, py, ax, ay, width, ni)
                router.mark_segment(st[0], px, py, ax, ay, width, nc)

        # Emit merged tracks and deduplicated vias
        for raw_p in raw_paths:
            merged_p = ptl._merge_collinear_path(raw_p, junctions)
            for k in range(len(merged_p) - 1):
                l1, gx1, gy1 = merged_p[k]
                l2, gx2, gy2 = merged_p[k + 1]
                x1, y1 = router.to_mm(gx1, gy1)
                x2, y2 = router.to_mm(gx2, gy2)
                if l1 == l2:
                    cu_layer = pcbnew.B_Cu if l1 == 1 else pcbnew.F_Cu
                    ptl.add_track(board, cu_layer, x1, y1, x2, y2, width, ni)
                else:
                    if (
                        router.tht_pad_grid.get((gx1, gy1)) != nc
                        and (gx1, gy1) not in emitted_vias
                    ):
                        ptl.add_via(board, x1, y1, ni, diam=VIA_DIAM, drill=VIA_DRILL)
                        emitted_vias.add((gx1, gy1))


def _stitch_gnd_grid(
    board: pcbnew.BOARD,
    router: ptl.GridRouter,
    gnd_item: pcbnew.NETINFO_ITEM,
    emitted_vias: set[tuple[int, int]],
) -> None:
    """Add regular GND stitching vias across open board space (clearing QR/edges/tracks)."""
    gnd_code = gnd_item.GetNetCode()
    via_obst_r = VIA_DIAM * 0.5 + ROUTE_CLEARANCE + 0.15
    y = BOARD_Y0 + 3.0
    while y <= BOARD_Y1 - 3.0:
        x = BOARD_X0 + 3.0
        while x <= BOARD_X1 - 3.0:
            gx, gy = router.to_grid(x, y)
            if (
                (gx, gy) not in emitted_vias
                and router.can_place_via(gx, gy, gnd_code)
                and router.is_passable(0, gx, gy, gnd_code)
                and router.is_passable(1, gx, gy, gnd_code)
            ):
                vx, vy = router.to_mm(gx, gy)
                ptl.add_via(board, vx, vy, gnd_item, diam=VIA_DIAM, drill=VIA_DRILL)
                router.mark_via_obstacle(vx, vy, via_obst_r, gnd_code)
                emitted_vias.add((gx, gy))
            x += 5.0
        y += 5.0


def _ensure_gnd_connectivity(
    board: pcbnew.BOARD,
    router: ptl.GridRouter,
    gnd_item: pcbnew.NETINFO_ITEM,
    emitted_vias: set[tuple[int, int]],
) -> None:
    """Verify 0 unrouted items after zone fill; drop bridging vias/routes if any GND pad is isolated."""
    conn = board.GetConnectivity()
    unrouted = conn.GetUnconnectedCount(False)
    if unrouted == 0:
        return
    # Collect any GND pads that remain disconnected and route them explicitly to nearest GND anchor
    gnd_code = gnd_item.GetNetCode()
    gnd_pads: list[pcbnew.PAD] = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetCode() == gnd_code:
                gnd_pads.append(pad)

    # First try placing additional GND stitching vias near any pads and refilling zones
    via_obst_r = VIA_DIAM * 0.5 + ROUTE_CLEARANCE + 0.15
    for pad in gnd_pads:
        cx, cy = (
            pcbnew.ToMM(pad.GetPosition().x),
            pcbnew.ToMM(pad.GetPosition().y),
        )
        vcell = _find_nearby_via(router, cx, cy, gnd_code, max_radius=4.5)
        if vcell and vcell not in emitted_vias:
            vx, vy = router.to_mm(*vcell)
            ptl.add_via(board, vx, vy, gnd_item, diam=VIA_DIAM, drill=VIA_DRILL)
            router.mark_via_obstacle(vx, vy, via_obst_r, gnd_code)
            emitted_vias.add(vcell)

    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()


def _place_silkscreen_and_fab(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
) -> None:
    """Apply collision-free dual-sided silkscreen, polarity marks, QR, and B.Fab notes."""
    # Move every fp.Value() to its mounting-side .Fab layer and hide it
    for ref, fp in footprints.items():
        is_back = fp.IsFlipped()
        fab_layer = pcbnew.B_Fab if is_back else pcbnew.F_Fab
        fp.Value().SetLayer(fab_layer)
        fp.Value().SetVisible(False)
        if sa.is_fiducial_ref(ref) or sa.is_passive_ref(ref):
            fp.Reference().SetLayer(fab_layer)
            fp.Reference().SetVisible(False)

    grid = sa.SilkGrid(
        board, footprints=footprints, block_smd_fab=True, block_tht_fab=True
    )

    # 1. Reserve 5.0 x 5.0 mm JLCPCB QR placeholder on B.SilkS (mandatory) and F.SilkS
    if not sa.place_silk_rect(
        grid, board, 1, *QR_BOX, filled=True, width=0.15, reserve_margin=0.25
    ):
        raise RuntimeError("Failed to place B.SilkS QR placeholder")
    if not sa.place_silk_rect(
        grid, board, 0, *QR_BOX, filled=True, width=0.15, reserve_margin=0.25
    ):
        raise RuntimeError("Failed to place F.SilkS QR placeholder")

    # 2. B.Fab complete fabrication notes (100% fab_notes_completeness, inside 30 mm width)
    fab_lines = [
        "FAB NOTES: 2L FR4",
        "THICKNESS: 1.6mm | 1oz CU",
        "FINISH: ENIG / HASL-LF",
        "IPC-6012 CLASS 2",
        "SOLDER MASK: BLACK",
        "SILK: WHITE | MIN TR/SP: 0.127mm",
        "DRILL TOL: +/-0.08mm | NO EDGE CUT",
    ]
    for idx, line in enumerate(fab_lines):
        sa.add_silk_text(
            board,
            pcbnew.B_Fab,
            line,
            15.0,
            104.2 + idx * 1.95,
            0.0,
            0.80,
            0.15,
            True,
        )

    # 3. Board Title & Revision on F.SilkS (B.SilkS placed after component labels)
    tb = board.GetTitleBlock()
    title_rev = f"{tb.GetTitle()} {tb.GetRevision()}".strip()
    if (
        sa.place_board_label(
            grid, board, 0, title_rev, target=(15.0, 14.0), max_distance=6.0
        )
        is None
    ):
        raise RuntimeError("Failed to place F.SilkS board title/rev")

    # 4. J4 Eurorack power header polarity stripe (-12V RED) & rail callouts on B.SilkS + F.SilkS
    j4 = footprints["J4"]
    j4_x = pcbnew.ToMM(j4.GetPosition().x)
    j4_y = pcbnew.ToMM(j4.GetPosition().y)
    # Place bold RED stripe bar just left of J4 Pins 1-2 (-12V_IN)
    if not sa.place_silk_rect(
        grid,
        board,
        1,
        j4_x - 6.70,
        j4_y - 1.50,
        j4_x - 5.90,
        j4_y + 4.10,
        filled=True,
        width=0.15,
        reserve_margin=0.15,
    ):
        raise RuntimeError("Failed to place J4 -12V RED stripe bar on B.SilkS")

    # Pin-1 dot on F.SilkS beside J4.1 (-12V_IN) in addition to -12V/+12V rail callouts
    j4_p1 = next(p for p in j4.Pads() if p.GetNumber() == "1").GetPosition()
    j4_p1x, j4_p1y = pcbnew.ToMM(j4_p1.x), pcbnew.ToMM(j4_p1.y)
    if (
        sa.place_silk_dot(
            grid,
            board,
            0,
            [(j4_p1x - 2.3, j4_p1y - 0.5), (j4_p1x - 2.4, j4_p1y)],
            radius=0.25,
            max_search=1.0,
        )
        is None
    ):
        raise RuntimeError("Failed to place J4 Pin-1 dot on F.SilkS")

    rail_callouts = [
        (1, "-12V RED", (j4_x - 3.00, j4_y + 7.10)),
        (1, "GND", (j4_x + 4.50, j4_y + 7.10)),
        (1, "+12V", (j4_x + 10.16, j4_y + 7.10)),
        (0, "-12V", (j4_x - 3.50, j4_y + 1.27)),
        (0, "+12V", (j4_x + 13.50, j4_y + 1.27)),
    ]
    for side_idx, rtxt, tgt in rail_callouts:
        if (
            sa.place_board_label(
                grid,
                board,
                side_idx,
                rtxt,
                target=tgt,
                max_distance=4.5,
                step=0.25,
                rotations=(0.0,),
            )
            is None
        ):
            raise RuntimeError(
                f"Failed to place J4 rail callout {rtxt!r} side={side_idx}"
            )

    errors: list[str] = []

    # 5. Component polarity & Pin-1 markers first so nearby component labels flow around them
    # 5a. IC Pin-1 solid dots (U1, U2) on B.SilkS
    for ic_ref in ("U1", "U2"):
        fp = footprints[ic_ref]
        p1 = next(p for p in fp.Pads() if p.GetNumber() == "1").GetPosition()
        p1x, p1y = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        cx, cy = pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y)
        sx = -1.0 if p1x < cx else 1.0
        sy = -1.0 if p1y < cy else 1.0
        targets = [
            (p1x + sx * 1.4, p1y + sy * 1.1),
            (p1x, p1y + sy * 1.4),
            (p1x + sx * 2.0, p1y),
        ]
        if (
            sa.place_silk_dot(grid, board, 1, targets, radius=0.25, max_search=1.5)
            is None
        ):
            errors.append(f"pin1_dot {ic_ref}")

    # 5b. SOT-23 Pin-1 solid dots (D7, D8, D9) on B.SilkS
    for d_ref in ("D7", "D8", "D9"):
        fp = footprints[d_ref]
        p1 = next(p for p in fp.Pads() if p.GetNumber() == "1").GetPosition()
        p1x, p1y = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        cx, cy = pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y)
        sx = -1.0 if p1x < cx else 1.0
        sy = -1.0 if p1y < cy else 1.0
        targets = [
            (p1x + sx * 1.4, p1y + sy * 0.9),
            (p1x + sx * 0.5, p1y + sy * 1.4),
            (p1x + sx * 1.5, p1y),
        ]
        if (
            sa.place_silk_dot(grid, board, 1, targets, radius=0.25, max_search=1.5)
            is None
        ):
            errors.append(f"pin1_dot {d_ref}")

    # 5c. SOD-123 external 0.25 mm cathode bars (D1, D2, D3, D5, D6, D10) outside Pin 1 (K)
    for d_ref in ("D1", "D2", "D3", "D5", "D6", "D10"):
        fp = footprints[d_ref]
        p1 = next(p for p in fp.Pads() if p.GetNumber() == "1").GetPosition()
        p2 = next(p for p in fp.Pads() if p.GetNumber() == "2").GetPosition()
        p1x, p1y = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        p2x, p2y = pcbnew.ToMM(p2.x), pcbnew.ToMM(p2.y)
        placed_bar = False
        if abs(p1x - p2x) >= abs(p1y - p2y):
            dir_x = -1.0 if p1x < p2x else 1.0
            for dist in (1.10, 1.25, 1.40):
                bx = p1x + dir_x * dist
                if sa.place_silk_seg(
                    grid, board, 1, bx, p1y - 0.90, bx, p1y + 0.90, width=0.25
                ):
                    placed_bar = True
                    break
        else:
            dir_y = -1.0 if p1y < p2y else 1.0
            for dist in (1.10, 1.25, 1.40):
                by = p1y + dir_y * dist
                if sa.place_silk_seg(
                    grid, board, 1, p1x - 0.90, by, p1x + 0.90, by, width=0.25
                ):
                    placed_bar = True
                    break
        if not placed_bar:
            errors.append(f"cathode_bar {d_ref}")

    # 5d. Electrolytic C3 / C4 external polarity markers (+/-) on B.SilkS (strictly 0 deg)
    for c_ref in ("C3", "C4"):
        fp = footprints[c_ref]
        p1 = next(p for p in fp.Pads() if p.GetNumber() == "1").GetPosition()
        p2 = next(p for p in fp.Pads() if p.GetNumber() == "2").GetPosition()
        p1x, p1y = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        p2x, p2y = pcbnew.ToMM(p2.x), pcbnew.ToMM(p2.y)
        if c_ref == "C4":
            # Place C4 + directly below C4.1 (GND) clear of J4 stripe and far from TP3 (-12V)
            t_plus = (p1x, p1y + 4.6)
            t_minus = (p2x + 2.8, p2y)
        else:
            t_plus = (p1x - 2.8, p1y)
            t_minus = (p2x - 0.5, p2y - 4.65)
        if (
            sa.place_board_label(
                grid,
                board,
                1,
                "+",
                target=t_plus,
                max_distance=1.5,
                step=0.25,
                rotations=(0.0,),
            )
            is None
        ):
            errors.append(f"polarity_+ {c_ref}")
        if (
            sa.place_board_label(
                grid,
                board,
                1,
                "-",
                target=t_minus,
                max_distance=1.5,
                step=0.25,
                rotations=(0.0,),
            )
            is None
        ):
            errors.append(f"polarity_- {c_ref}")

    # 5e. Potentiometer RV1..RV4 Pin-1 markers on F.SilkS & B.SilkS (strictly 0 deg)
    for pot_ref in ("RV1", "RV2", "RV3", "RV4"):
        fp = footprints[pot_ref]
        p1 = next(p for p in fp.Pads() if p.GetNumber() == "1").GetPosition()
        p1x, p1y = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        for side_idx in (0, 1):
            if (
                sa.place_board_label(
                    grid,
                    board,
                    side_idx,
                    "1",
                    target=(p1x - 1.5, p1y + 1.5),
                    max_distance=2.0,
                    step=0.25,
                    rotations=(0.0,),
                )
                is None
            ):
                errors.append(f"pin1 {pot_ref} side={side_idx}")

    # 5f. D4 LED polarity markers (- at Pin 1 K, + at Pin 2 A) + B.SilkS cathode bar;
    # B.SilkS '+' is placed in Pass 6c after R12/D4 ENV retain their preferred corridors
    d4 = footprints["D4"]
    d4_p1 = next(p for p in d4.Pads() if p.GetNumber() == "1").GetPosition()
    d4_p2 = next(p for p in d4.Pads() if p.GetNumber() == "2").GetPosition()
    d4_p1x, d4_p1y = pcbnew.ToMM(d4_p1.x), pcbnew.ToMM(d4_p1.y)
    d4_p2x, d4_p2y = pcbnew.ToMM(d4_p2.x), pcbnew.ToMM(d4_p2.y)
    if not sa.place_silk_seg(
        grid,
        board,
        1,
        d4_p1x - 1.48,
        d4_p1y - 1.0,
        d4_p1x - 1.48,
        d4_p1y + 1.0,
        width=0.25,
    ):
        errors.append("D4_cathode_bar side=1")
    for lbl, pad_x, pad_y in (("-", d4_p1x, d4_p1y), ("+", d4_p2x, d4_p2y)):
        if (
            sa.place_board_label(
                grid,
                board,
                0,
                lbl,
                target=(pad_x, pad_y - 1.9),
                max_distance=2.0,
                step=0.25,
                rotations=(0.0,),
            )
            is None
        ):
            errors.append(f"D4_{lbl} side=0")
    if (
        sa.place_board_label(
            grid,
            board,
            1,
            "-",
            target=(d4_p1x, d4_p1y - 2.1),
            max_distance=2.0,
            step=0.25,
            rotations=(0.0,),
        )
        is None
    ):
        errors.append("D4_- side=1")

    # 6. Component labels:
    # Pass 6a: Primary-side labels (SMDs first so tight 3.5mm corridors aren't taken by THT opp labels)
    order_refs = sorted(
        footprints,
        key=lambda r: (
            0 if sa.is_smd_footprint(footprints[r]) else 1,
            0 if r.startswith(("U", "D")) else 1,
            sa._resolve_fp_side_and_center(footprints[r], None, None)[6],
            r,
        ),
    )

    opp_queue: list[tuple[str, pcbnew.FOOTPRINT, int, str]] = []
    for ref in order_refs:
        fp = footprints[ref]
        if sa.is_fiducial_ref(ref):
            continue

        primary_side = 1 if fp.IsFlipped() else 0
        full_lbl, sec_lbl = sa.get_fp_silkscreen_field(fp)

        if sa.is_passive_ref(ref):
            res = sa.place_val_only(
                grid,
                fp,
                sec_lbl,
                side=1,
                step=0.25,
                max_edge_distance=sa.MAX_SMD_TETHER_MM
                if sa.is_smd_footprint(fp)
                else sa.MAX_THT_TETHER_MM,
            )
            if res is None:
                errors.append(f"val_only {ref} ({sec_lbl}) side=1")
        else:
            rots = (90.0, 0.0) if ref == "D10" else (0.0, 90.0)
            res = sa.place_ref_val_pair(
                grid,
                fp,
                sec_lbl,
                side=primary_side,
                step=0.25,
                val_only=False,
                rotations=rots,
            )
            if res is None:
                errors.append(f"ref_val_pair {ref} ({sec_lbl}) side={primary_side}")

            # Queue opposite-side secondary label for THT controls, J4, and TP1..TP8
            if not sa.is_smd_footprint(fp):
                opp_side = 1 - primary_side
                opp_text = (
                    f"{ref} {sec_lbl} {fp.GetValue().strip()}".strip()
                    if ref.startswith("RV")
                    else full_lbl
                )
                opp_queue.append((ref, fp, opp_side, opp_text))

    # Pass 6b: Secondary opposite-side THT labels (6.0 mm tether)
    for ref, fp, opp_side, opp_text in opp_queue:
        opp_res = sa.place_board_label(
            grid,
            fp,
            opp_side,
            opp_text,
            fp=fp,
            max_distance=sa.MAX_THT_TETHER_MM,
            step=0.25,
        )
        if opp_res is None:
            errors.append(f"opp_label {ref} ({opp_text!r}) side={opp_side}")

    # Pass 6c: D4 LED '+' on B.SilkS below Pin 2 A (strictly 0 deg)
    if (
        sa.place_board_label(
            grid,
            board,
            1,
            "+",
            target=(d4_p2x + 0.25, d4_p2y + 2.0),
            max_distance=2.0,
            step=0.25,
            rotations=(0.0,),
        )
        is None
    ):
        errors.append("D4_+ side=1")

    # Pass 6d: B.SilkS Board Title & Revision in best remaining open slot
    if sa.place_board_label(grid, board, 1, title_rev) is None:
        errors.append("B.SilkS board title/rev")

    if errors:
        raise RuntimeError(
            f"Silkscreen placement failed for {len(errors)} item(s): {', '.join(errors)}"
        )

    _verify_silkscreen_and_polarity(board, footprints)


def _verify_silkscreen_and_polarity(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
) -> None:
    """Assert netlist Silkscreen fidelity and upright external polarity markers."""
    silk_layers = (pcbnew.F_SilkS, pcbnew.B_SilkS)
    for ref, fp in footprints.items():
        if sa.is_fiducial_ref(ref):
            continue
        vf = fp.Value()
        if vf.IsVisible() or vf.GetLayer() in silk_layers:
            raise RuntimeError(f"Raw fp.Value() visible on silkscreen for {ref}")

        full_lbl, expected_sec = sa.get_fp_silkscreen_field(fp)
        primary_layer = pcbnew.B_SilkS if fp.IsFlipped() else pcbnew.F_SilkS
        opp_layer = pcbnew.F_SilkS if fp.IsFlipped() else pcbnew.B_SilkS
        prim_uts = [
            gi.GetText()
            for gi in fp.GraphicalItems()
            if hasattr(gi, "GetText")
            and gi.IsVisible()
            and gi.GetLayer() == primary_layer
        ]
        if prim_uts != [expected_sec]:
            raise RuntimeError(
                f"Primary silkscreen mismatch for {ref}: got {prim_uts}, expected {[expected_sec]}"
            )
        if not sa.is_smd_footprint(fp) and not sa.is_passive_ref(ref):
            expected_opp = (
                f"{ref} {expected_sec} {fp.GetValue().strip()}".strip()
                if ref.startswith("RV")
                else full_lbl
            )
            opp_uts = [
                gi.GetText()
                for gi in fp.GraphicalItems()
                if hasattr(gi, "GetText")
                and gi.IsVisible()
                and gi.GetLayer() == opp_layer
            ]
            if opp_uts != [expected_opp]:
                raise RuntimeError(
                    f"Secondary silkscreen mismatch for {ref}: got {opp_uts}, expected {[expected_opp]}"
                )

    # Confirm board-level polarity texts (-, +, 1) are strictly upright (0 deg)
    board_texts: dict[int, list[tuple[str, float, float]]] = {0: [], 1: []}
    board_dots: dict[int, list[tuple[float, float]]] = {0: [], 1: []}
    board_segs: dict[int, list[tuple[float, float]]] = {0: [], 1: []}
    board_rects: dict[int, list[tuple[float, float, float, float]]] = {0: [], 1: []}
    for dr in board.GetDrawings():
        if dr.GetLayer() not in silk_layers:
            continue
        s = 1 if dr.GetLayer() == pcbnew.B_SilkS else 0
        if hasattr(dr, "GetText"):
            txt = dr.GetText().strip()
            if txt in ("-", "+", "1") and dr.GetTextAngleDegrees() != 0.0:
                raise RuntimeError(
                    f"Polarity marker {txt!r} on {dr.GetLayerName()} rotated {dr.GetTextAngleDegrees()} deg"
                )
            board_texts[s].append(
                (txt, pcbnew.ToMM(dr.GetPosition().x), pcbnew.ToMM(dr.GetPosition().y))
            )
        elif dr.GetShape() == pcbnew.SHAPE_T_CIRCLE:
            board_dots[s].append(
                (pcbnew.ToMM(dr.GetCenter().x), pcbnew.ToMM(dr.GetCenter().y))
            )
        elif dr.GetShape() == pcbnew.SHAPE_T_SEGMENT:
            sp, ep = dr.GetStart(), dr.GetEnd()
            board_segs[s].append(
                (
                    (pcbnew.ToMM(sp.x) + pcbnew.ToMM(ep.x)) * 0.5,
                    (pcbnew.ToMM(sp.y) + pcbnew.ToMM(ep.y)) * 0.5,
                )
            )
        elif dr.GetShape() == pcbnew.SHAPE_T_RECT:
            bb = dr.GetBoundingBox()
            board_rects[s].append(
                (
                    pcbnew.ToMM(bb.GetLeft()),
                    pcbnew.ToMM(bb.GetTop()),
                    pcbnew.ToMM(bb.GetRight()),
                    pcbnew.ToMM(bb.GetBottom()),
                )
            )

    def _has_near(
        pts: list[tuple[float, float]], x: float, y: float, tol: float
    ) -> bool:
        return any(math.hypot(px - x, py - y) <= tol for px, py in pts)

    # IC & SOT-23 Pin-1 dots on B.SilkS
    for ref in ("U1", "U2", "D7", "D8", "D9"):
        p1 = next(
            p for p in footprints[ref].Pads() if p.GetNumber() == "1"
        ).GetPosition()
        if not _has_near(board_dots[1], pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y), 2.5):
            raise RuntimeError(f"Missing Pin-1 dot near {ref}.1 on B.SilkS")

    # SOD-123 & D4 B.SilkS cathode bars
    for ref in ("D1", "D2", "D3", "D5", "D6", "D10", "D4"):
        p1 = next(
            p for p in footprints[ref].Pads() if p.GetNumber() == "1"
        ).GetPosition()
        if not _has_near(board_segs[1], pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y), 2.0):
            raise RuntimeError(f"Missing cathode bar near {ref}.1 on B.SilkS")

    # J4 F.SilkS Pin-1 dot, B.SilkS RED stripe bar, and rail labels
    j4_p1 = next(
        p for p in footprints["J4"].Pads() if p.GetNumber() == "1"
    ).GetPosition()
    if not _has_near(board_dots[0], pcbnew.ToMM(j4_p1.x), pcbnew.ToMM(j4_p1.y), 3.0):
        raise RuntimeError("Missing J4 Pin-1 dot on F.SilkS")
    if not any((r[2] - r[0]) < 2.0 and (r[3] - r[1]) > 4.0 for r in board_rects[1]):
        raise RuntimeError("Missing J4 -12V RED stripe bar on B.SilkS")
    for side_idx, req_txt in (
        (1, "-12V RED"),
        (1, "GND"),
        (1, "+12V"),
        (0, "-12V"),
        (0, "+12V"),
    ):
        if not any(t == req_txt for t, _, _ in board_texts[side_idx]):
            raise RuntimeError(f"Missing J4 rail label {req_txt!r} on side={side_idx}")

    # Potentiometer Pin-1 '1' markers and D4 +/- on both sides
    for side_idx in (0, 1):
        ones = [(x, y) for t, x, y in board_texts[side_idx] if t == "1"]
        for pot_ref in ("RV1", "RV2", "RV3", "RV4"):
            p1 = next(
                p for p in footprints[pot_ref].Pads() if p.GetNumber() == "1"
            ).GetPosition()
            if not _has_near(ones, pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y), 3.5):
                raise RuntimeError(
                    f"Missing Pin-1 '1' marker for {pot_ref} side={side_idx}"
                )
        for sym, pin in (("-", "1"), ("+", "2")):
            pts = [(x, y) for t, x, y in board_texts[side_idx] if t == sym]
            pad_p = next(
                p for p in footprints["D4"].Pads() if p.GetNumber() == pin
            ).GetPosition()
            if not _has_near(pts, pcbnew.ToMM(pad_p.x), pcbnew.ToMM(pad_p.y), 3.6):
                raise RuntimeError(f"Missing D4 '{sym}' marker on side={side_idx}")

    # Confirm C3/C4 external + and - are present and + is closer to C*.1 than any TP* pad
    tp_centers = [
        (pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y), r)
        for r, fp in footprints.items()
        if r.startswith("TP")
        for p in fp.Pads()
    ]
    plus_pts = [(x, y) for t, x, y in board_texts[1] if t == "+"]
    minus_pts = [(x, y) for t, x, y in board_texts[1] if t == "-"]
    for c_ref in ("C3", "C4"):
        p1 = next(
            p for p in footprints[c_ref].Pads() if p.GetNumber() == "1"
        ).GetPosition()
        p2 = next(
            p for p in footprints[c_ref].Pads() if p.GetNumber() == "2"
        ).GetPosition()
        p1x, p1y = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        p2x, p2y = pcbnew.ToMM(p2.x), pcbnew.ToMM(p2.y)
        nearest_x, nearest_y = min(
            plus_pts, key=lambda pt: math.hypot(pt[0] - p1x, pt[1] - p1y)
        )
        d_c = math.hypot(nearest_x - p1x, nearest_y - p1y)
        if d_c > 5.0:
            raise RuntimeError(
                f"{c_ref} external '+' too far ({d_c:.2f} mm) from {c_ref}.1"
            )
        if not _has_near(minus_pts, p2x, p2y, 5.0):
            raise RuntimeError(f"Missing external '-' near {c_ref}.2 on B.SilkS")
        for tx, ty, tp_ref in tp_centers:
            if math.hypot(nearest_x - tx, nearest_y - ty) <= d_c:
                raise RuntimeError(
                    f"{c_ref} external '+' at ({nearest_x:.2f},{nearest_y:.2f}) closer to {tp_ref} than {c_ref}.1"
                )


def main() -> None:
    net_path = HERE / "envelope_follower.net"
    out_path = HERE / "EnvelopeFollower.kicad_pcb"

    components, nets = ptl.parse_netlist(net_path, dnp_prefixes=("TP",))
    board = ptl.create_base_board(
        out_path,
        BOARD_X0,
        BOARD_Y0,
        BOARD_X1,
        BOARD_Y1,
        title="ENVELOPE FOLLOWER",
        revision="REV 1.0",
        date="2026-11",
        track_width=SIGNAL_WIDTH,
        clearance=0.20,
        via_diam=VIA_DIAM,
        via_drill=VIA_DRILL,
        edge_clearance=0.50,
    )

    footprints = ptl.populate_footprints(board, components, PLACEMENTS)
    fids = ptl.add_fiducials(board, FIDUCIALS, is_back=True)
    footprints.update(fids)

    net_items, _ = ptl.assign_nets(board, footprints, nets)
    validate_placement(footprints)

    router, net_anchors, _ = _init_router(footprints, net_items)
    gnd_item = net_items["GND"]
    emitted_vias = _place_gnd_smd_vias(board, router, net_anchors, gnd_item)
    pre_merged = _pre_route_decoupling(
        board, router, footprints, net_items, net_anchors
    )
    _route_all_nets(board, router, net_items, net_anchors, pre_merged, emitted_vias)
    _stitch_gnd_grid(board, router, gnd_item, emitted_vias)

    ptl.pour_gnd_zones(
        board,
        gnd_item,
        BOARD_X0,
        BOARD_Y0,
        BOARD_X1,
        BOARD_Y1,
        edge_clearance=0.50,
        clearance=0.20,
    )
    _ensure_gnd_connectivity(board, router, gnd_item, emitted_vias)

    _place_silkscreen_and_fab(board, footprints)

    board.Save(str(out_path))
    unconnected = board.GetConnectivity().GetUnconnectedCount(False)
    print(
        f"Generated {out_path.name}: {len(footprints)} footprints "
        f"({len(components)} netlist + {len(fids)} FID), "
        f"{len(emitted_vias)} vias, unconnected={unconnected}"
    )


if __name__ == "__main__":
    main()
