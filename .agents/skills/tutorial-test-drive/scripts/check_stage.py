#!/usr/bin/env python3
"""Reset and deterministic stage-gate checks for EnvelopeFollower tutorial test drives."""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
from pathlib import Path

EXPECTED_SKILLS: tuple[str, ...] = (
    "bom",
    "datasheets",
    "eurorack-panel",
    "jlcpcb",
    "kicad",
    "kicad-pcbnew-layout",
    "kicad-silkscreen-markup",
    "lcsc",
    "skidl",
)

EXPECTED_STAGE1_PATHS: tuple[str, ...] = (
    "skidl/scripts/jlcpcb_search.py",
    "kicad-pcbnew-layout/scripts/pcbnew_layout_template.py",
    "kicad-pcbnew-layout/references/kicad10_pcbnew_api.md",
    "kicad-pcbnew-layout/references/routing_and_dfm_patterns.md",
    "kicad-silkscreen-markup/scripts/silk_annotator.py",
    "eurorack-panel/scripts/generate_eurorack_panel.py",
    "kicad/scripts/analyze_schematic.py",
    "kicad/scripts/analyze_pcb.py",
    "kicad/scripts/cross_analysis.py",
    "kicad/scripts/analyze_gerbers.py",
)

STRAY_ROOT_FILES: tuple[str, ...] = (
    "envelope_follower.erc",
    "envelope_follower.log",
    "skidl_REPL.erc",
    "skidl_REPL.log",
)

CPL_EXPECTED_HEADER: list[str] = [
    "Designator",
    "Val",
    "Package",
    "Mid X",
    "Mid Y",
    "Rotation",
    "Layer",
]

STAGE_DIR_PATTERN = re.compile(r"^stage-[0-9]+$")


def find_repo_root(start: Path | None = None) -> Path:
    """Resolve the EnvelopeFollower repository root from script location or CWD."""
    candidates = [Path(__file__).resolve(), *(Path.cwd(),)]
    if start is not None:
        candidates.insert(0, start.resolve())
    for base in candidates:
        for parent in (base, *base.parents):
            if (parent / ".git").exists():
                return parent
    raise RuntimeError("Could not locate repository root (.git directory).")


def _stage_dirs(stages_root: Path) -> list[Path]:
    """Return sorted `stages/stage-<N>` directories."""
    if not stages_root.is_dir():
        return []
    return sorted(
        p
        for p in stages_root.iterdir()
        if p.is_dir() and STAGE_DIR_PATTERN.match(p.name)
    )


def _gitignore_has_venv(repo_root: Path) -> bool:
    """Return True if `.gitignore` ignores `.venv/` or `.venv`."""
    gitignore = repo_root / ".gitignore"
    if not gitignore.is_file():
        return False
    lines = {
        line.strip() for line in gitignore.read_text(encoding="utf-8").splitlines()
    }
    return ".venv/" in lines or ".venv" in lines


def cmd_reset(repo_root: Path, dry_run: bool) -> int:
    """Remove `stages/stage-*` directories to prepare a clean-room tutorial test drive."""
    stages_root = repo_root / "stages"
    targets = _stage_dirs(stages_root)
    if not targets:
        print(f"[OK] No stage-* directories found under {stages_root}")
    else:
        for target in targets:
            if target.parent.resolve() != stages_root.resolve():
                print(
                    f"[FAIL] Refusing to remove non-child path: {target}",
                    file=sys.stderr,
                )
                return 1
            if dry_run:
                print(f"[DRY-RUN] Would remove {target}")
            else:
                shutil.rmtree(target)
                print(f"[REMOVED] {target}")

    if _gitignore_has_venv(repo_root):
        print("[OK] .gitignore excludes .venv/")
    else:
        print(
            "[WARN] .gitignore does not contain '.venv/'; add it before Stage 4",
            file=sys.stderr,
        )
    return 0


def cmd_check_clean_root(repo_root: Path, strict: bool) -> int:
    """Verify Stage 1 skills did not leak to root `.agents/` or `skills-lock.json`."""
    failures = 0
    warnings = 0

    root_skills_dir = repo_root / ".agents" / "skills"
    if root_skills_dir.is_dir():
        installed_root = sorted(p.name for p in root_skills_dir.iterdir() if p.is_dir())
        leaked = [name for name in installed_root if name in EXPECTED_SKILLS]
        if leaked:
            print(
                f"[FAIL] Hardware skills leaked into root .agents/skills/: {leaked}",
                file=sys.stderr,
            )
            failures += 1
        else:
            print(f"[OK] Root .agents/skills/ clean: {installed_root}")
    else:
        print("[WARN] Root .agents/skills/ directory missing")
        warnings += 1

    lock_path = repo_root / "skills-lock.json"
    if lock_path.is_file():
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        lock_keys = sorted((data.get("skills") or {}).keys())
        leaked_lock = [k for k in lock_keys if k in EXPECTED_SKILLS]
        if leaked_lock or lock_keys != ["agy-brain-explorer"]:
            print(
                f"[FAIL] Root skills-lock.json altered: {lock_keys}",
                file=sys.stderr,
            )
            failures += 1
        else:
            print(f"[OK] Root skills-lock.json untouched: {lock_keys}")
    else:
        print("[FAIL] Root skills-lock.json missing", file=sys.stderr)
        failures += 1

    if _gitignore_has_venv(repo_root):
        print("[OK] .gitignore contains .venv/")
    else:
        print("[FAIL] .gitignore missing .venv/", file=sys.stderr)
        failures += 1

    stray_found = [name for name in STRAY_ROOT_FILES if (repo_root / name).exists()]
    if stray_found:
        msg = f"Stray SKiDL files at repo root: {stray_found}"
        if strict:
            print(f"[FAIL] {msg}", file=sys.stderr)
            failures += 1
        else:
            print(f"[WARN] {msg}")
            warnings += 1
    else:
        print("[OK] No stray SKiDL .erc/.log files at repo root")

    return 1 if failures else 0


def cmd_init_stage(repo_root: Path, stage: int) -> int:
    """Initialize `stages/stage-N` (empty for Stage 1, full clone of `stage-(N-1)` for 2-7)."""
    if not 1 <= stage <= 7:
        print(f"[FAIL] Stage must be between 1 and 7, got {stage}", file=sys.stderr)
        return 1

    stages_root = repo_root / "stages"
    stages_root.mkdir(parents=True, exist_ok=True)
    target_dir = stages_root / f"stage-{stage}"

    if stage == 1:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        print("[OK] Initialized empty stages/stage-1")
        return 0

    prev_dir = stages_root / f"stage-{stage - 1}"
    if not prev_dir.is_dir():
        print(f"[FAIL] Missing previous stage directory: {prev_dir}", file=sys.stderr)
        return 1

    prev_skills_dir = prev_dir / ".agents" / "skills"
    missing_skills = [
        skill
        for skill in EXPECTED_SKILLS
        if not (prev_skills_dir / skill / "SKILL.md").is_file()
    ]
    if not prev_skills_dir.is_dir() or missing_skills:
        print(
            f"[FAIL] {prev_dir} missing expected skills in .agents/skills/: {missing_skills}",
            file=sys.stderr,
        )
        return 1

    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(prev_dir, target_dir, symlinks=True)
    print(
        f"[OK] Copied full directory stages/stage-{stage - 1} -> stages/stage-{stage}"
    )
    return 0


def cmd_check_stage1(repo_root: Path) -> int:
    """Verify Stage 1 installed all 9 copied hardware skills and helper files cleanly."""
    stage1 = repo_root / "stages" / "stage-1"
    skills_dir = stage1 / ".agents" / "skills"
    failures = 0

    if not skills_dir.is_dir():
        print(f"[FAIL] Missing directory: {skills_dir}", file=sys.stderr)
        return 1

    for skill in EXPECTED_SKILLS:
        skill_md = skills_dir / skill / "SKILL.md"
        if not skill_md.is_file():
            print(f"[FAIL] Missing SKILL.md: {skill_md}", file=sys.stderr)
            failures += 1

    lock_path = stage1 / "skills-lock.json"
    if not lock_path.is_file():
        print(f"[FAIL] Missing lockfile: {lock_path}", file=sys.stderr)
        failures += 1
    else:
        lock_skills = sorted(
            (
                json.loads(lock_path.read_text(encoding="utf-8")).get("skills") or {}
            ).keys()
        )
        missing_lock = [s for s in EXPECTED_SKILLS if s not in lock_skills]
        if missing_lock:
            print(
                f"[FAIL] skills-lock.json missing skills: {missing_lock}",
                file=sys.stderr,
            )
            failures += 1

    symlinks = [p for p in stage1.rglob("*") if p.is_symlink()]
    if symlinks:
        print(
            f"[FAIL] Found {len(symlinks)} symlink(s) inside stage-1: {symlinks[:5]}",
            file=sys.stderr,
        )
        failures += 1

    for rel in EXPECTED_STAGE1_PATHS:
        target = skills_dir / rel
        if not target.is_file():
            print(f"[FAIL] Missing referenced helper/doc: {target}", file=sys.stderr)
            failures += 1

    if failures == 0:
        print(
            f"[PASS] Stage 1 verified: {len(EXPECTED_SKILLS)}/9 skills, "
            f"{len(EXPECTED_STAGE1_PATHS)}/{len(EXPECTED_STAGE1_PATHS)} helpers/docs, "
            "0 symlinks"
        )
    return 1 if failures else 0


def cmd_check_stage4(repo_root: Path) -> int:
    """Verify Stage 4 SKiDL ERC, netlist health, and JLCPCB BOM CSV."""
    stage4 = repo_root / "stages" / "stage-4"
    failures = 0

    erc_path = stage4 / "envelope_follower.erc"
    if not erc_path.is_file():
        print(f"[FAIL] Missing {erc_path}", file=sys.stderr)
        failures += 1
    else:
        erc_text = erc_path.read_text(encoding="utf-8").strip()
        if "No errors or warnings found while running ERC." not in erc_text:
            print(f"[FAIL] ERC did not pass cleanly: {erc_text}", file=sys.stderr)
            failures += 1
        else:
            print(f"[OK] ERC clean: {erc_text}")

    log_path = stage4 / "envelope_follower.log"
    if not log_path.is_file():
        print(f"[FAIL] Missing {log_path}", file=sys.stderr)
        failures += 1
    else:
        log_text = log_path.read_text(encoding="utf-8")
        if "0 errors found while generating netlist" not in log_text:
            print("[FAIL] Netlist generation reported errors in log", file=sys.stderr)
            failures += 1
        if "0 errors found while generating XML" not in log_text:
            print("[FAIL] XML generation reported errors in log", file=sys.stderr)
            failures += 1

    net_path = stage4 / "envelope_follower.net"
    if not net_path.is_file():
        print(f"[FAIL] Missing {net_path}", file=sys.stderr)
        failures += 1
    else:
        net_text = net_path.read_text(encoding="utf-8")
        no_lib = net_text.count("NO_LIB")
        comp_count = len(re.findall(r"\(comp\s+\(ref\s+", net_text))
        net_count = len(re.findall(r"\(net\s+\(code\s+", net_text))
        dnp_count = len(re.findall(r"\(property\s+\(name\s+\"dnp\"\)", net_text))
        if dnp_count == 0:
            dnp_count = net_text.count('"dnp"')
        lcsc_count = net_text.count('"LCSC"')
        silk_count = net_text.count('"Silkscreen"')
        if no_lib > 0:
            print(f"[FAIL] Found {no_lib} NO_LIB entries in netlist", file=sys.stderr)
            failures += 1
        if comp_count == 0 or net_count == 0:
            print("[FAIL] Empty components or nets in netlist", file=sys.stderr)
            failures += 1
        print(
            f"[OK] Netlist: {comp_count} comps, {net_count} nets, {no_lib} NO_LIB, "
            f"{dnp_count} dnp, {lcsc_count} LCSC fields, {silk_count} Silkscreen fields"
        )
        if silk_count == 0:
            print(
                "[INFO] 0 Silkscreen fields in netlist; Stage 5 must read SilkscreenInstructions.md"
            )

    bom_csv = stage4 / "jlcpcb_bom.csv"
    if not bom_csv.is_file():
        print(f"[FAIL] Missing {bom_csv}", file=sys.stderr)
        failures += 1
    else:
        with bom_csv.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        if not rows or rows[0] != [
            "Comment",
            "Designator",
            "Footprint",
            "LCSC Part #",
        ]:
            print(
                f"[FAIL] Unexpected jlcpcb_bom.csv header: {rows[:1]}",
                file=sys.stderr,
            )
            failures += 1
        else:
            data_rows = rows[1:]
            total_parts = 0
            for comment, designator, footprint, lcsc in data_rows:
                refs = [r.strip() for r in designator.split(",") if r.strip()]
                total_parts += len(refs)
                if (
                    not footprint.strip()
                    or not lcsc.strip()
                    or "PENDING" in lcsc.upper()
                ):
                    print(
                        f"[FAIL] Invalid BOM row ({comment}): lcsc={lcsc!r}",
                        file=sys.stderr,
                    )
                    failures += 1
                bad_refs = [r for r in refs if r.startswith(("TP", "RV", "J"))]
                if bad_refs:
                    print(
                        f"[FAIL] THT/DNP part leaked into jlcpcb_bom.csv: {bad_refs}",
                        file=sys.stderr,
                    )
                    failures += 1
            print(
                f"[OK] jlcpcb_bom.csv: {len(data_rows)} BOM lines, {total_parts} SMD parts"
            )

    return 1 if failures else 0


def cmd_check_stage7(repo_root: Path) -> int:
    """Verify Stage 7 manufacturing ZIPs, CPL headers, and OrderingNotes.md."""
    stage7 = repo_root / "stages" / "stage-7"
    failures = 0

    for rel in (
        "production/EnvelopeFollower_Main.zip",
        "production/EnvelopeFollower_Panel.zip",
        "OrderingNotes.md",
    ):
        target = stage7 / rel
        if not target.is_file() or target.stat().st_size == 0:
            print(
                f"[FAIL] Missing or empty Stage 7 deliverable: {target}",
                file=sys.stderr,
            )
            failures += 1

    cpl_path = stage7 / "production" / "main" / "EnvelopeFollower_cpl.csv"
    if not cpl_path.is_file():
        print(f"[FAIL] Missing CPL file: {cpl_path}", file=sys.stderr)
        failures += 1
    else:
        with cpl_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        if not rows or rows[0] != CPL_EXPECTED_HEADER:
            print(
                f"[FAIL] Unexpected CPL header: {rows[:1]} (expected {CPL_EXPECTED_HEADER})",
                file=sys.stderr,
            )
            failures += 1
        else:
            data_rows = rows[1:]
            bad_layers = [r[0] for r in data_rows if r[6].strip() != "Bottom"]
            bad_refs = [
                r[0] for r in data_rows if r[0].strip().startswith(("TP", "RV", "J"))
            ]
            if bad_layers:
                print(
                    f"[FAIL] Non-Bottom layer entries in CPL: {bad_layers}",
                    file=sys.stderr,
                )
                failures += 1
            if bad_refs:
                print(
                    f"[FAIL] THT/DNP designators leaked into CPL: {bad_refs}",
                    file=sys.stderr,
                )
                failures += 1
            print(f"[OK] EnvelopeFollower_cpl.csv: {len(data_rows)} Bottom SMD rows")

    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Reset and verify clean-room EnvelopeFollower tutorial stages."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    reset_p = sub.add_parser(
        "reset", help="Remove stages/stage-* directories before a fresh test drive."
    )
    reset_p.add_argument(
        "--dry-run", action="store_true", help="Print directories without deleting."
    )

    clean_p = sub.add_parser(
        "check-clean-root",
        help="Confirm root .agents/, skills-lock.json, and .gitignore stay clean.",
    )
    clean_p.add_argument(
        "--strict",
        action="store_true",
        help="Fail if stray .erc/.log files exist at repo root.",
    )

    init_p = sub.add_parser(
        "init-stage",
        help="Initialize stages/stage-N (empty for Stage 1, full copy of stage-(N-1) for 2-7).",
    )
    init_p.add_argument(
        "stage",
        type=int,
        choices=range(1, 8),
        help="Stage number (1-7) to initialize.",
    )
    sub.add_parser("check-stage1", help="Verify Stage 1 skill installation and layout.")
    sub.add_parser("check-stage4", help="Verify Stage 4 ERC, netlist, and BOM CSV.")
    sub.add_parser(
        "check-stage7", help="Verify Stage 7 ZIPs, CPL CSV, and OrderingNotes."
    )
    return parser


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    repo_root = find_repo_root()

    if args.command == "reset":
        return cmd_reset(repo_root, dry_run=args.dry_run)
    if args.command == "check-clean-root":
        return cmd_check_clean_root(repo_root, strict=args.strict)
    if args.command == "init-stage":
        return cmd_init_stage(repo_root, stage=args.stage)
    if args.command == "check-stage1":
        return cmd_check_stage1(repo_root)
    if args.command == "check-stage4":
        return cmd_check_stage4(repo_root)
    if args.command == "check-stage7":
        return cmd_check_stage7(repo_root)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
