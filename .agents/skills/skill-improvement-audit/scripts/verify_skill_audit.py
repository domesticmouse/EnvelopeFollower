#!/usr/bin/env python3
"""Deterministic verification checks for skill-improvement-audit runs."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS: tuple[str, ...] = (
    "Executive Summary",
    "Per-Prompt Coverage Matrix",
    "Consolidated Skill Improvements",
    "Per-Prompt Raw Findings Summary",
    "Prioritized Upstream Action Plan",
)

REQUIRED_REVIEW_SLUGS: tuple[str, ...] = (
    "stage-1.md",
    "stage-2.1.md",
    "stage-2.2.md",
    "stage-2.3.md",
    "stage-3.1.md",
    "stage-3.2.md",
    "stage-3.3a.md",
    "stage-3.3b.md",
    "stage-3.3c.md",
    "stage-4.md",
    "stage-5.1.md",
    "stage-5.2a.md",
    "stage-6.1.md",
    "stage-7.md",
)

OPTIONAL_REVIEW_SLUGS: tuple[str, ...] = ("stage-5.2b.md", "stage-6.2.md")

FINDING_PATTERN = re.compile(
    r"^- \*\*([A-Z]+-\d+) \(`(High|Medium|Low)`\)\s+—\s+.+?\*\*",
    re.MULTILINE,
)

SUMMARY_COUNT_PATTERN = re.compile(
    r"\*\*(\d+)\s+deduplicated,\s+evidence-backed\s+skill\s+improvements\*\*\s*"
    r"\(`(\d+)\s+High`,\s*`(\d+)\s+Medium`,\s*`(\d+)\s+Low`\)",
)

SKILL_LINK_PATTERN = re.compile(
    r"\[[^\]]+\]\(([^)#\s]*stages/stage-[0-9]+/\.agents/skills/[^)#\s]+)(?:#[^)\s]+)?\)",
)


def find_repo_root(start: Path | None = None) -> Path:
    """Resolve the repository root containing .git."""
    candidates = [Path(__file__).resolve(), Path.cwd()]
    if start is not None:
        candidates.insert(0, start.resolve())
    for base in candidates:
        for parent in (base, *base.parents):
            if (parent / ".git").exists():
                return parent
    raise RuntimeError("Could not locate repository root (.git directory).")


def _snapshot_skills(skills_dir: Path) -> dict[str, bytes]:
    """Read all non-cache files under a stage's .agents/skills directory."""
    snapshot: dict[str, bytes] = {}
    for path in sorted(skills_dir.rglob("*")):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.is_file() or path.is_symlink():
            rel = path.relative_to(skills_dir).as_posix()
            snapshot[rel] = path.read_bytes() if path.is_file() else b"<SYMLINK>"
    return snapshot


def cmd_check_zero_mutations(repo_root: Path) -> int:
    """Verify stages/stage-1/.agents/skills and stages/stage-7/.agents/skills match identically."""
    s1 = repo_root / "stages" / "stage-1" / ".agents" / "skills"
    s7 = repo_root / "stages" / "stage-7" / ".agents" / "skills"
    failures = 0

    for label, path in (("Stage 1", s1), ("Stage 7", s7)):
        if not path.is_dir():
            print(f"[FAIL] {label} skills directory missing: {path}", file=sys.stderr)
            failures += 1
    if failures:
        return 1

    snap1 = _snapshot_skills(s1)
    snap7 = _snapshot_skills(s7)
    added = sorted(set(snap7) - set(snap1))
    removed = sorted(set(snap1) - set(snap7))
    changed = sorted(k for k in set(snap1) & set(snap7) if snap1[k] != snap7[k])

    if added or removed or changed:
        print(
            "[FAIL] Skill files mutated between stage-1 and stage-7: "
            f"added={added[:5]}, removed={removed[:5]}, changed={changed[:5]}",
            file=sys.stderr,
        )
        return 1

    print(
        f"[OK] Zero skill mutations verified across {len(snap1)} files "
        "(stages/stage-1 vs stages/stage-7)"
    )
    return 0


def cmd_check_report(repo_root: Path, report_path: Path) -> int:
    """Validate structure, file citations, and finding severity counts in SkillImprovementAuditReport.md."""
    resolved = report_path if report_path.is_absolute() else repo_root / report_path
    if not resolved.is_file():
        print(f"[FAIL] Missing report file: {resolved}", file=sys.stderr)
        return 1

    text = resolved.read_text(encoding="utf-8")
    failures = 0

    for heading in REQUIRED_SECTIONS:
        if heading not in text:
            print(
                f"[FAIL] Missing required section heading: {heading}", file=sys.stderr
            )
            failures += 1

    findings = FINDING_PATTERN.findall(text)
    if not findings:
        print(
            "[FAIL] Found 0 formatted Section 2 finding bullets matching '<ID> (`High|Medium|Low`)'",
            file=sys.stderr,
        )
        failures += 1
    else:
        counts = {"High": 0, "Medium": 0, "Low": 0}
        seen_ids: list[str] = []
        for fid, sev in findings:
            counts[sev] += 1
            seen_ids.append(fid)

        dupes = sorted({fid for fid in seen_ids if seen_ids.count(fid) > 1})
        if dupes:
            print(
                f"[FAIL] Duplicate finding IDs in Section 2: {dupes}", file=sys.stderr
            )
            failures += 1

        summary_match = SUMMARY_COUNT_PATTERN.search(text)
        if not summary_match:
            print(
                "[FAIL] Executive Summary missing standard count phrase "
                "'**<N> deduplicated, evidence-backed skill improvements** (`H High`, `M Medium`, `L Low`)'",
                file=sys.stderr,
            )
            failures += 1
        else:
            exp_total, exp_h, exp_m, exp_l = (int(g) for g in summary_match.groups())
            actual_total = len(findings)
            if (exp_total, exp_h, exp_m, exp_l) != (
                actual_total,
                counts["High"],
                counts["Medium"],
                counts["Low"],
            ):
                print(
                    "[FAIL] Executive Summary count mismatch: "
                    f"summary=({exp_total}, {exp_h}H/{exp_m}M/{exp_l}L) vs "
                    f"Section 2=({actual_total}, {counts['High']}H/{counts['Medium']}M/{counts['Low']}L)",
                    file=sys.stderr,
                )
                failures += 1
            else:
                print(
                    f"[OK] Report counts verified: {actual_total} findings "
                    f"({counts['High']} High, {counts['Medium']} Medium, {counts['Low']} Low)"
                )

    links = SKILL_LINK_PATTERN.findall(text)
    broken_links: list[str] = []
    for raw_target in links:
        clean = raw_target.removeprefix("./")
        target = (repo_root / clean).resolve()
        if not target.exists():
            broken_links.append(raw_target)

    if broken_links:
        print(
            f"[FAIL] Broken skill link(s) in report ({len(broken_links)}): {broken_links}",
            file=sys.stderr,
        )
        failures += 1
    else:
        print(f"[OK] Verified {len(links)} skill path link(s) exist on disk")

    return 1 if failures else 0


def cmd_check_reviews(scratch_dir: Path) -> int:
    """Verify per-prompt scratch review markdown files exist and are non-empty."""
    if not scratch_dir.is_dir():
        print(
            f"[FAIL] Scratch review directory missing: {scratch_dir}", file=sys.stderr
        )
        return 1

    failures = 0
    present_required = 0
    for name in REQUIRED_REVIEW_SLUGS:
        path = scratch_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            print(
                f"[FAIL] Missing or empty required scratch review: {path}",
                file=sys.stderr,
            )
            failures += 1
        else:
            present_required += 1

    present_optional = [
        name
        for name in OPTIONAL_REVIEW_SLUGS
        if (scratch_dir / name).is_file() and (scratch_dir / name).stat().st_size > 0
    ]

    if failures == 0:
        print(
            f"[OK] Scratch reviews verified: {present_required}/{len(REQUIRED_REVIEW_SLUGS)} "
            f"required + {len(present_optional)} optional ({present_optional})"
        )
    return 1 if failures else 0


def cmd_check_stage_hygiene(repo_root: Path) -> int:
    """Verify stages/ contains no nested .git directories or stray .ruff_cache directories."""
    stages_root = repo_root / "stages"
    if not stages_root.is_dir():
        print(f"[WARN] No stages/ directory at {stages_root}")
        return 0

    failures = 0
    nested_git = [p for p in stages_root.rglob(".git")]
    if nested_git:
        print(f"[FAIL] Nested .git found inside stages/: {nested_git}", file=sys.stderr)
        failures += 1

    ruff_caches = [p for p in stages_root.glob("stage-*/.ruff_cache")]
    if ruff_caches:
        print(
            f"[FAIL] Stray .ruff_cache directories inside stages/: {ruff_caches} "
            "(remove before committing)",
            file=sys.stderr,
        )
        failures += 1

    if failures == 0:
        print("[OK] stages/ hygiene clean (0 nested .git, 0 .ruff_cache)")
    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Verify skill-improvement-audit deliverables and zero-mutation invariants."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "check-zero-mutations",
        help="Verify stages/stage-1/.agents/skills and stages/stage-7/.agents/skills match.",
    )

    rep_p = sub.add_parser(
        "check-report",
        help="Verify SkillImprovementAuditReport.md structure, counts, and skill links.",
    )
    rep_p.add_argument(
        "--report",
        type=Path,
        default=Path("SkillImprovementAuditReport.md"),
        help="Path to SkillImprovementAuditReport.md.",
    )

    rev_p = sub.add_parser(
        "check-reviews",
        help="Verify per-prompt scratch/skill_reviews/*.md files exist and are non-empty.",
    )
    rev_p.add_argument(
        "--scratch-dir",
        type=Path,
        required=True,
        help="Directory holding per-prompt <slug>.md review files.",
    )

    all_p = sub.add_parser(
        "check-all",
        help="Run zero-mutations, report, hygiene, and optional scratch-review checks.",
    )
    all_p.add_argument(
        "--report",
        type=Path,
        default=Path("SkillImprovementAuditReport.md"),
        help="Path to SkillImprovementAuditReport.md.",
    )
    all_p.add_argument(
        "--scratch-dir",
        type=Path,
        default=None,
        help="Optional scratch review directory to verify.",
    )
    return parser


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    repo_root = find_repo_root()

    if args.command == "check-zero-mutations":
        return cmd_check_zero_mutations(repo_root)
    if args.command == "check-report":
        return cmd_check_report(repo_root, args.report)
    if args.command == "check-reviews":
        return cmd_check_reviews(args.scratch_dir)
    if args.command == "check-all":
        rc = 0
        rc |= cmd_check_zero_mutations(repo_root)
        rc |= cmd_check_report(repo_root, args.report)
        rc |= cmd_check_stage_hygiene(repo_root)
        if args.scratch_dir is not None:
            rc |= cmd_check_reviews(args.scratch_dir)
        return 1 if rc else 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
