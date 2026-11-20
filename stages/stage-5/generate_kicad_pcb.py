#!/usr/bin/env python3
"""Generate 6 HP Eurorack Envelope Follower PCB (EnvelopeFollower.kicad_pcb)."""

from __future__ import annotations

import argparse
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
sys.path.insert(
    0, str(HERE / ".agents/skills/kicad-pcbnew-layout/scripts")
)
sys.path.insert(
    0, str(HERE / ".agents/skills/kicad-silkscreen-markup/scripts")
)

from pcbnew_layout_template import (  # noqa: E402
    create_base_board,
    parse_netlist,
    populate_footprints,
)
from silk_annotator import (  # noqa: E402
    SilkGrid,
    place_ref_val_pair,
    place_val_only,
)

BOARD_W = 30.00
BOARD_H = 108.00


def build_placements() -> dict[str, tuple[float, float, float, bool]]:
    """Return (x, y, rot_deg, is_back) for all 71 footprints."""
    return {
        # --- 8 Front-panel THT on F.Cu ---
        # Rows at Y_shaft/bushing = 15.0, 43.0, 68.5, 88.5 (X = 7.5, 22.5)
        "RV1": (5.00, 22.50, 90.0, False),   # shaft (7.50, 15.00), CrtYd Y=[9.22..23.68]
        "RV2": (20.00, 22.50, 90.0, False),  # shaft (22.50, 15.00)
        "RV3": (5.00, 50.50, 90.0, False),   # shaft (7.50, 43.00), CrtYd Y=[37.22..51.68]
        "RV4": (20.00, 50.50, 90.0, False),  # shaft (22.50, 43.00)
        "J1": (7.50, 62.02, 0.0, False),     # bushing (7.50, 68.50), CrtYd Y=[60.58..75.03]
        "D4": (21.23, 68.50, 0.0, False),    # lens (22.50, 68.50), CrtYd Y=[66.27..70.73]
        "J2": (7.50, 82.02, 0.0, False),     # bushing (7.50, 88.50), CrtYd Y=[80.58..95.03]
        "J3": (22.50, 82.02, 0.0, False),    # bushing (22.50, 88.50), CrtYd Y=[80.58..95.03]

        # --- 3 SMT optical fiducials on F.Cu ---
        "FID1": (2.20, 2.20, 0.0, False),
        "FID2": (27.80, 3.00, 0.0, False),
        "FID3": (1.80, 77.80, 0.0, False),

        # --- 11 Rear THT on B.Cu ---
        "J4": (9.92, 97.90, 270.0, True),    # pads X=[9.07..20.93], Y=[97.05..101.29]
        "C1": (3.80, 54.60, 0.0, True),      # pads (3.8,54.6) & (8.8,54.6)
        "C2": (22.20, 53.80, 0.0, True),     # pads (22.2,53.8) & (27.2,53.8)
        # Test points (DNP), clear of J4/C1/C2/THT pads & F.Cu SMDs
        "TP1": (15.00, 92.60, 0.0, True),    # GND
        "TP2": (15.00, 35.80, 0.0, True),    # +12V (wait: check R12/R13!)
        "TP3": (3.20, 25.40, 0.0, True),     # -12V (check C_DEC2!)
        "TP4": (14.20, 66.20, 0.0, True),    # IN_BUF
        "TP5": (15.00, 4.20, 0.0, True),     # PREAMP_OUT
        "TP6": (27.20, 35.80, 0.0, True),    # RECT_OUT
        "TP7": (14.50, 77.80, 0.0, True),    # OUT_CLAMP
        "TP8": (28.00, 77.80, 0.0, True),    # INV_OUT_CLAMP

        # --- Corridor A (Y = 0.45..9.22) ---
        "R_GAIN_MIN": (6.80, 2.10, 0.0, False),
        "R_GAIN_FAIL": (10.80, 2.10, 0.0, False),
        "C_HF": (6.80, 5.80, 0.0, False),
        "R2": (10.80, 5.80, 0.0, False),
        "R_ATK_MIN": (19.50, 2.10, 0.0, False),
        "D3": (24.00, 2.10, 0.0, False),
        "R10": (19.50, 5.80, 0.0, False),
        "R20": (24.00, 5.80, 0.0, False),

        # --- Corridor B (Y = 23.68..37.22) ---
        "U1": (5.50, 30.50, 90.0, False),    # X=[0.89..10.11], Y=[26.77..34.23]
        "C_DEC2": (6.80, 25.10, 0.0, False), # <3mm from U1.11 (5.50, 28.02)
        "C_DEC1": (4.50, 35.70, 0.0, False), # <3mm from U1.4 (5.50, 32.98)
        "R3": (15.00, 25.40, 0.0, False),
        "R4": (19.00, 25.40, 0.0, False),
        "R5": (23.00, 25.40, 0.0, False),
        "R15": (27.20, 25.40, 0.0, False),
        "R6": (15.00, 29.00, 0.0, False),
        "R7": (19.00, 29.00, 0.0, False),
        "R8A": (23.00, 29.00, 0.0, False),
        "R8B": (27.20, 29.00, 0.0, False),
        "D1_D2": (14.80, 32.60, 0.0, False),
        "R_ENV_PROT": (20.20, 32.40, 0.0, False),
        "C_OUT1": (27.20, 32.40, 0.0, False),
        "R11": (9.80, 36.10, 0.0, False),
        "R12": (19.20, 36.10, 0.0, False),
        "R13": (23.20, 36.10, 0.0, False),

        # --- Corridor C & D (Y = 51.68..80.58) ---
        "R_IN_PROT": (3.20, 58.60, 0.0, False),
        "R1": (7.20, 58.60, 0.0, False),
        "R_IN_BUF": (11.20, 58.60, 0.0, False),
        "D_IN": (14.40, 54.40, 0.0, False),

        "U2": (21.50, 61.20, 0.0, False),    # X=[17.77..25.23], Y=[56.59..65.81]
        "C_DEC3": (16.40, 61.50, 90.0, False),  # 3.0mm from U2.4 (19.02, 61.20)
        "C_DEC4": (26.60, 61.50, 90.0, False),  # 3.0mm from U2.11 (23.98, 61.20)
        "C_OUT2": (18.40, 53.00, 0.0, False),
        "R17": (14.00, 58.60, 0.0, False),
        "R18": (28.40, 57.60, 90.0, False),

        "D_LED_CLAMP": (15.40, 70.00, 0.0, False),
        "R_LED": (27.60, 68.50, 90.0, False),
        "D_OUT": (14.60, 73.60, 0.0, False),
        "D_INV_OUT": (27.40, 73.60, 90.0, False),

        "R16A": (6.00, 77.80, 0.0, False),
        "R16B": (11.00, 77.80, 0.0, False),
        "R19A": (18.80, 77.80, 0.0, False),
        "R19B": (23.80, 77.80, 0.0, False),

        # --- Center J2/J3 + Corridor E (Y = 95.03..107.55) ---
        "R_PWR_N": (15.00, 82.80, 90.0, False),
        "R_PWR_P": (15.00, 88.00, 90.0, False),
        "C4": (4.20, 100.30, 270.0, False),
        "C3": (25.80, 100.30, 90.0, False),
        "D_PWR_N": (11.40, 103.60, 180.0, False),
        "D_PWR_P": (18.60, 103.60, 180.0, False),
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
            print(f"EDGE WARN: {r1} CrtYd={tuple(round(v,2) for v in b1)}")
        for r2 in refs[i + 1 :]:
            fp2 = fps[r2]
            if fp1.IsFlipped() != fp2.IsFlipped():
                continue
            b2 = _get_crtyd_bbox(fp2)
            if not b2:
                continue
            if not (b1[2] <= b2[0] or b2[2] <= b1[0] or b1[3] <= b2[1] or b2[3] <= b1[1]):
                print(f"CRTYD OVERLAP: {r1} {tuple(round(v,2) for v in b1)} vs {r2} {tuple(round(v,2) for v in b2)}")

    tht_pads = []
    for r, fp in fps.items():
        for p in fp.Pads():
            if p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                pos = p.GetPosition()
                sz = p.GetSize()
                cx, cy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
                w, h = pcbnew.ToMM(sz.x), pcbnew.ToMM(sz.y)
                tht_pads.append((r, p.GetNumber(), (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)))

    for i, (r1, p1, b1) in enumerate(tht_pads):
        for r2, p2, b2 in tht_pads[i + 1 :]:
            if r1 == r2:
                continue
            if not (b1[2] + 0.25 <= b2[0] or b2[2] + 0.25 <= b1[0] or b1[3] + 0.25 <= b2[1] or b2[3] + 0.25 <= b1[1]):
                print(f"THT PAD OVERLAP: {r1}.{p1} vs {r2}.{p2}")
        for rs, fps_item in fps.items():
            if fps_item.IsFlipped():
                continue
            if not any(p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD for p in fps_item.Pads()):
                continue
            sb = _get_crtyd_bbox(fps_item)
            if sb and not (b1[2] + 0.2 <= sb[0] or sb[2] + 0.2 <= b1[0] or b1[3] + 0.2 <= sb[1] or sb[3] + 0.2 <= b1[1]):
                print(f"THT PAD VS F.Cu SMD CRTYD: {r1}.{p1} {tuple(round(v,2) for v in b1)} vs {rs} {tuple(round(v,2) for v in sb)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-pack", action="store_true")
    args = parser.parse_args()

    components, _ = parse_netlist(HERE / "envelope_follower.net", dnp_prefixes=("TP",))
    placements = build_placements()
    out_path = HERE / "EnvelopeFollower.kicad_pcb"
    board = create_base_board(out_path, 0.0, 0.0, BOARD_W, BOARD_H)
    fps = populate_footprints(board, components, placements)
    check_geometry(fps)

    for fp in fps.values():
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
    grid = SilkGrid(board, fps, board_bounds=(0.0, 0.0, BOARD_W, BOARD_H))
    fails = []
    order = sorted(
        fps,
        key=lambda r: (
            0 if r in ("U1", "U2", "D_PWR_N", "D_PWR_P", "D_LED_CLAMP", "D_INV_OUT", "D_OUT", "D_IN", "D1_D2", "D3") else 1,
            r,
        ),
    )
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
                fails.append((ref, "val_only", silk))
        else:
            toks = silk.split()
            val_tok = " ".join(toks[1:]) if toks and toks[0] == ref else (silk or comp["value"])
            res = place_ref_val_pair(grid, fp, val_tok, val_only=False)
            if res is None:
                fails.append((ref, "ref_val", val_tok))
    print(f"Silk placement failures: {len(fails)}")
    for f in fails:
        print(" ", f)
    if args.check_pack:
        pcbnew.SaveBoard(str(out_path), board)


if __name__ == "__main__":
    main()
