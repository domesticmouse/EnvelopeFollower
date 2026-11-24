#!/usr/bin/env python3
"""Pure-Python built-site and repository contract verifier for ENV / SKEW Build Tutorial."""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Sequence
from urllib.parse import unquote, urlparse

CANONICAL_ROUTES: tuple[str, ...] = (
    "index.html",
    "tutorial/stage-1-agent-skills/index.html",
    "tutorial/stage-2-circuit-upgrades/index.html",
    "tutorial/stage-3-bom-and-dfm/index.html",
    "tutorial/stage-4-skidl/index.html",
    "tutorial/stage-5-schematic-and-pcb/index.html",
    "tutorial/stage-6-front-panel/index.html",
    "tutorial/stage-7-manufacturing/index.html",
    "tutorial/stage-8-wayfinder-site-planning/index.html",
    "tutorial/stage-9-companion-site-delivery/index.html",
    "tutorial/optional-dc-coupled-mode/index.html",
    "reference/netlist-and-bom/index.html",
    "reference/build-checklist/index.html",
)

EXCLUDED_SITE_DIRS: tuple[str, ...] = ("agents", "adr", "research")
SITE_PATH_PREFIX = "/EnvelopeFollower/"
EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "//")

REQUIRED_FONT_FILES: tuple[str, ...] = (
    "space-grotesk-latin-500-normal.woff2",
    "space-grotesk-latin-600-normal.woff2",
    "space-grotesk-latin-700-normal.woff2",
    "ibm-plex-sans-latin-400-normal.woff2",
    "ibm-plex-sans-latin-400-italic.woff2",
    "ibm-plex-sans-latin-500-normal.woff2",
    "ibm-plex-sans-latin-600-normal.woff2",
    "ibm-plex-sans-latin-700-normal.woff2",
    "ibm-plex-mono-latin-400-normal.woff2",
    "ibm-plex-mono-latin-500-normal.woff2",
    "ibm-plex-mono-latin-600-normal.woff2",
    "ibm-plex-mono-latin-700-normal.woff2",
)
GOOGLE_FONT_DOMAINS = ("fonts.googleapis.com", "fonts.gstatic.com")
CSS_URL_RE = re.compile(r"""url\(\s*['"]?([^'")]+?)['"]?\s*\)""")

BASE_RENDERS: tuple[str, ...] = (
    "EnvelopeFollower.webp",
    "schematic.png",
    "pcb_front.png",
    "pcb_back.png",
    "panel_front.png",
    "panel_back.png",
    "panel_preview_clean.png",
    "panel_preview_keepouts.png",
)
CHECKLIST_PNGS: tuple[str, ...] = (
    "checklists/pcba_alignment_U1.png",
    "checklists/hand_assembly_J_PWR.png",
    "checklists/board_bringup_00_test_point_map.png",
)
SITE_WEBPS: tuple[str, ...] = (
    "site/patch-workbench.webp",
    "site/hardware-panel-inspector.webp",
    "site/landing-showcase.webp",
)
CHECKLIST_MAX_BYTES = 500 * 1024
SITE_WEBP_MAX_BYTES = 250 * 1024

VOID_HTML_TAGS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)

EXPECTED_PROMPTS_BY_ROUTE: dict[str, tuple[tuple[str, bool], ...]] = {
    "index.html": (),
    "tutorial/stage-1-agent-skills/index.html": (
        ("AI Agent Prompt — Living Context Map Bootstrap", False),
    ),
    "tutorial/stage-2-circuit-upgrades/index.html": (
        ("AI Agent Prompt — Sketch Extraction", False),
        ("AI Agent Prompt — Quantitative Circuit Critique", False),
    ),
    "tutorial/stage-3-bom-and-dfm/index.html": (
        ("AI Agent Prompt — Interactive Design Q&A", False),
        ("Turn 1 — Test-Point Options", False),
        ("Turn 2 — Lock All 12 Test Points", True),
    ),
    "tutorial/stage-4-skidl/index.html": (
        ("AI Agent Prompt — SKiDL Circuit Capture", False),
        ("Turn 1 — Generate KiCad Schematic", False),
        ("Turn 2 — Export PDF & Commit", True),
    ),
    "tutorial/stage-5-schematic-and-pcb/index.html": (
        ("AI Agent Prompt — Generate 6 HP Main PCB", False),
        ("Turn 1 — Declarative Silkscreen Strategy", False),
        ("Turn 2 — Extract silk_layout.json", True),
    ),
    "tutorial/stage-6-front-panel/index.html": (),
    "tutorial/stage-7-manufacturing/index.html": (),
    "tutorial/stage-8-wayfinder-site-planning/index.html": (
        ("AI Agent Prompt — Chart Wayfinder Map", False),
    ),
    "tutorial/stage-9-companion-site-delivery/index.html": (),
    "tutorial/optional-dc-coupled-mode/index.html": (),
    "reference/netlist-and-bom/index.html": (),
    "reference/build-checklist/index.html": (),
}

FORBIDDEN_PROMPT_HEADING_RE = re.compile(
    r"^#{1,6}\s+(?:AI\s+Agent\s+Prompts?|Motivating\s+Prompts?)\b",
    re.MULTILINE,
)
PROTOTYPE_LEFTOVERS: tuple[str, ...] = (
    "prototype-switcher",
    "prototype-theme",
    "prototype-variants",
    "data-proto-variant",
)
TABLIST_RE = re.compile(r"""(?:role\s*=\s*["']tablist["']|setAttribute\(\s*["']role["']\s*,\s*["']tablist["'])""")

EXPECTED_MERMAID_COUNTS: dict[str, int] = {
    "docs/index.md": 1,
    "docs/tutorial/stage-3-bom-and-dfm.md": 1,
    "docs/tutorial/stage-6-front-panel.md": 1,
    "docs/tutorial/stage-7-manufacturing.md": 1,
    "docs/tutorial/stage-8-wayfinder-site-planning.md": 1,
    "docs/tutorial/stage-9-companion-site-delivery.md": 2,
    "docs/tutorial/optional-dc-coupled-mode.md": 1,
}
MERMAID_BLOCK_RE = re.compile(r"```mermaid[ \t]*\r?\n(.*?)```", re.DOTALL)
MERMAID_HEX_STYLE_RE = re.compile(
    r"^\s*(?:style|classDef)\b[^\n]*#[0-9a-fA-F]{3,8}\b", re.MULTILINE
)
MERMAID_EDGE_ARROW_RE = re.compile(r"\s*(?:<[-.=]+|[-.=]+>|--+|==+|\.-\.)(?:\|[^|]*\|)?\s*")
MERMAID_NODE_ID_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_-]*)")

UNPINNED_MAIN_RE = re.compile(
    r"EnvelopeFollowerWithSkewLimiter/(?:blob|tree)/main/"
)
PINNED_8AD81D0_RE = re.compile(
    r"https://github\.com/domesticmouse/EnvelopeFollowerWithSkewLimiter/(blob|tree)/8ad81d0/([^\s\)\"'>]+)"
)
LOCAL_MAIN_RE = re.compile(
    r"https://github\.com/domesticmouse/EnvelopeFollower/(blob|tree)/main/([^\s\)\"'>]+)"
)
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_ATTR_LINK_RE = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""")

AVOIDED_GLOSSARY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("codelab", re.compile(r"\bcodelabs?\b", re.IGNORECASE)),
    ("motivating prompt", re.compile(r"\bmotivating\s+prompts?\b", re.IGNORECASE)),
    ("context anchor", re.compile(r"\bcontext\s+anchors?\b", re.IGNORECASE)),
    ("Optional Branch", re.compile(r"\bOptional\s+Branch(?:es)?\b", re.IGNORECASE)),
    ("Technical References", re.compile(r"\bTechnical\s+References?\b", re.IGNORECASE)),
    ("Master Build Checklist", re.compile(r"\bMaster\s+Build\s+Checklists?\b", re.IGNORECASE)),
    ("EnvFollower", re.compile(r"\bEnvFollower\b", re.IGNORECASE)),
    ("EFSL", re.compile(r"\bEFSL\b", re.IGNORECASE)),
    ("SkewFollower", re.compile(r"\bSkewFollower\b", re.IGNORECASE)),
)
# Documented intentional historical-contrast phrases permitted by GLOSSARY lint.
HISTORICAL_GLOSSARY_ALLOWLIST: tuple[str, ...] = ()
COMPANION_SPECS_URL = "https://domesticmouse.github.io/EnvelopeFollowerWithSkewLimiter/specs/"


@dataclass
class PromptBlockInfo:
    """Metadata for a rendered .admonition.prompt block."""

    title: str
    body_text: str
    adjacent_to_previous: bool


@dataclass
class ParsedPage:
    """Extracted HTML metadata from one built page."""

    path: Path
    raw_text: str
    ids: set[str] = field(default_factory=set)
    hrefs: list[tuple[str, str]] = field(default_factory=list)
    imgs: list[tuple[str, set[str]]] = field(default_factory=list)
    prompt_blocks: list[PromptBlockInfo] = field(default_factory=list)
    blockquote_count: int = 0


class SiteHTMLParser(HTMLParser):
    """Single-pass HTML parser extracting ids, links, images, prompts, and blockquotes."""

    def __init__(self, path: Path, raw_text: str) -> None:
        super().__init__(convert_charrefs=True)
        self.page = ParsedPage(path=path, raw_text=raw_text)
        # Stack entries: [tag, is_prompt_div, last_child_was_prompt]
        self._stack: list[list[object]] = [["__root__", False, False]]
        self._active_prompt_depth: int | None = None
        self._in_prompt_title: bool = False
        self._prompt_title_parts: list[str] = []
        self._prompt_body_parts: list[str] = []
        self._prompt_adjacent: bool = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k: (v or "") for k, v in attrs}
        elem_id = attr_map.get("id", "")
        if elem_id:
            self.page.ids.add(elem_id)

        classes = set(attr_map.get("class", "").split())
        if tag in ("a", "link") and "href" in attr_map:
            self.page.hrefs.append((tag, attr_map["href"]))
        elif tag == "img" and "src" in attr_map:
            self.page.imgs.append((attr_map["src"], classes))
        elif tag == "blockquote":
            self.page.blockquote_count += 1

        is_prompt_div = tag == "div" and {"admonition", "prompt"}.issubset(classes)

        if self._active_prompt_depth is None:
            parent_state = self._stack[-1]
            if is_prompt_div:
                self._prompt_adjacent = bool(parent_state[2])
                self._active_prompt_depth = len(self._stack)
                self._prompt_title_parts = []
                self._prompt_body_parts = []
                parent_state[2] = False
            else:
                parent_state[2] = False
        elif tag == "p" and "admonition-title" in classes:
            self._in_prompt_title = True

        if tag not in VOID_HTML_TAGS:
            self._stack.append([tag, is_prompt_div, False])

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_HTML_TAGS:
            return

        if self._in_prompt_title and tag == "p":
            self._in_prompt_title = False

        # Pop back to matching open tag (defensive for malformed HTML)
        while len(self._stack) > 1:
            entry = self._stack.pop()
            if entry[1] and self._active_prompt_depth == len(self._stack):
                title = " ".join("".join(self._prompt_title_parts).split())
                body = " ".join("".join(self._prompt_body_parts).split())
                self.page.prompt_blocks.append(
                    PromptBlockInfo(
                        title=title,
                        body_text=body,
                        adjacent_to_previous=self._prompt_adjacent,
                    )
                )
                self._active_prompt_depth = None
                self._in_prompt_title = False
                self._stack[-1][2] = True
            if entry[0] == tag:
                break

    def handle_data(self, data: str) -> None:
        if self._active_prompt_depth is not None:
            if self._in_prompt_title:
                self._prompt_title_parts.append(data)
            else:
                self._prompt_body_parts.append(data)
        elif data.strip():
            self._stack[-1][2] = False


def parse_built_pages(site_dir: Path) -> dict[Path, ParsedPage]:
    """Parse every HTML file in site_dir keyed by resolved path."""
    pages: dict[Path, ParsedPage] = {}
    if not site_dir.is_dir():
        return pages
    for html_path in sorted(site_dir.rglob("*.html")):
        resolved = html_path.resolve()
        raw = resolved.read_text(encoding="utf-8")
        parser = SiteHTMLParser(resolved, raw)
        parser.feed(raw)
        parser.close()
        pages[resolved] = parser.page
    return pages


def _resolve_site_target(
    site_root: Path, page_path: Path, raw_url: str
) -> tuple[Path | None, str, str | None]:
    """Resolve an internal URL relative to page_path or SITE_PATH_PREFIX.

    Returns (resolved_path, fragment, error_message).
    """
    if raw_url == "" or raw_url.startswith(EXTERNAL_SCHEMES):
        return None, "", None

    if raw_url.startswith("#"):
        return page_path, unquote(raw_url[1:]), None

    parsed = urlparse(raw_url)
    path_part = unquote(parsed.path)
    fragment = unquote(parsed.fragment)

    if path_part.startswith(SITE_PATH_PREFIX):
        rel_part = path_part[len(SITE_PATH_PREFIX) :]
        target = (site_root / rel_part).resolve()
    elif path_part.startswith("/"):
        return None, fragment, f"Unexpected root-relative path outside {SITE_PATH_PREFIX}: {raw_url}"
    else:
        target = (page_path.parent / path_part).resolve()

    if not target.is_relative_to(site_root):
        return None, fragment, f"Internal path escapes built site root: {raw_url}"

    if target.is_dir():
        target = (target / "index.html").resolve()

    return target, fragment, None


@dataclass
class VerificationResult:
    """Collects contract errors and non-fatal warnings across all checks."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def fail(self, check: str, message: str) -> None:
        self.errors.append(f"[{check}] {message}")

    def warn(self, check: str, message: str) -> None:
        self.warnings.append(f"[{check}] {message}")


def check_routes_and_exclusions(site_dir: Path, result: VerificationResult) -> None:
    """Check 1: Verify all 13 canonical routes exist and excluded dirs are absent."""
    if not site_dir.is_dir():
        result.fail("Check 1", f"Built site directory does not exist: {site_dir}")
        return

    for route in CANONICAL_ROUTES:
        if not (site_dir / route).is_file():
            result.fail("Check 1", f"Missing canonical built route: {route}")

    for excluded in EXCLUDED_SITE_DIRS:
        if (site_dir / excluded).exists():
            result.fail("Check 1", f"Excluded directory leaked into built site: site/{excluded}")


def check_html_links_and_images(
    site_dir: Path, pages: dict[Path, ParsedPage], result: VerificationResult
) -> None:
    """Check 2: Verify internal relative hrefs, #fragments, and <img src> resolve."""
    site_root = site_dir.resolve()
    for page_path, page in pages.items():
        rel_page = page_path.relative_to(site_root)
        for tag, href in page.hrefs:
            target, fragment, err = _resolve_site_target(site_root, page_path, href)
            if err:
                result.fail("Check 2", f"{rel_page} <{tag} href='{href}'>: {err}")
                continue
            if target is None:
                continue
            if not target.exists():
                result.fail(
                    "Check 2",
                    f"{rel_page} <{tag} href='{href}'> points to missing target",
                )
                continue
            if fragment:
                target_page = pages.get(target)
                if target_page is None:
                    result.fail(
                        "Check 2",
                        f"{rel_page} <{tag} href='{href}'> uses fragment on non-HTML target",
                    )
                elif fragment not in target_page.ids:
                    result.fail(
                        "Check 2",
                        f"{rel_page} <{tag} href='{href}'> missing target id '#{fragment}'",
                    )

        for src, _ in page.imgs:
            target, _, err = _resolve_site_target(site_root, page_path, src)
            if err:
                result.fail("Check 2", f"{rel_page} <img src='{src}'>: {err}")
                continue
            if target is not None and not target.is_file():
                result.fail("Check 2", f"{rel_page} <img src='{src}'> points to missing file")


def check_self_hosted_typography(
    root: Path,
    site_dir: Path,
    pages: dict[Path, ParsedPage],
    result: VerificationResult,
) -> None:
    """Check 3: Verify 12 self-hosted .woff2 files, OFL notice, fonts.css URLs, and 0 Google Fonts."""
    fonts_dir = site_dir / "assets/fonts"
    for font_file in REQUIRED_FONT_FILES:
        if not (fonts_dir / font_file).is_file():
            result.fail("Check 3", f"Missing self-hosted font file: site/assets/fonts/{font_file}")

    has_license = fonts_dir.is_dir() and any(
        p.is_file() and (p.name == "OFL.txt" or p.name.startswith("LICENSE"))
        for p in fonts_dir.iterdir()
    )
    if not has_license:
        result.fail("Check 3", "Missing SIL OFL license notice (OFL.txt or LICENSE*) in site/assets/fonts/")

    fonts_css = root / "docs/stylesheets/fonts.css"
    if not fonts_css.is_file():
        result.fail("Check 3", "Missing docs/stylesheets/fonts.css")
    else:
        css_text = fonts_css.read_text(encoding="utf-8")
        urls = CSS_URL_RE.findall(css_text)
        if not urls:
            result.fail("Check 3", "docs/stylesheets/fonts.css contains no url(...) rules")
        for url in urls:
            if url.startswith(("http://", "https://", "data:", "//")):
                result.fail("Check 3", f"Non-local url(...) in docs/stylesheets/fonts.css: {url}")
                continue
            target = (fonts_css.parent / url.split("?")[0].split("#")[0]).resolve()
            if not target.is_file():
                result.fail("Check 3", f"Broken url(...) in docs/stylesheets/fonts.css: {url}")

    for page_path, page in pages.items():
        lowered = page.raw_text.lower()
        for domain in GOOGLE_FONT_DOMAINS:
            if domain in lowered:
                result.fail(
                    "Check 3",
                    f"External Google Fonts reference ({domain}) in {page_path.relative_to(site_dir.resolve())}",
                )

    for css_path in sorted(site_dir.rglob("*.css")) if site_dir.is_dir() else []:
        lowered = css_path.read_text(encoding="utf-8").lower()
        for domain in GOOGLE_FONT_DOMAINS:
            if domain in lowered:
                result.fail(
                    "Check 3",
                    f"External Google Fonts reference ({domain}) in {css_path.relative_to(site_dir)}",
                )


def check_visual_assets_and_framing(
    site_dir: Path, pages: dict[Path, ParsedPage], result: VerificationResult
) -> None:
    """Check 4: Verify 8 base renders (no .framed-shot) and 6 capped captures (with .framed-shot)."""
    site_root = site_dir.resolve()
    images_root = (site_root / "images").resolve()

    base_paths = {(images_root / name).resolve(): name for name in BASE_RENDERS}
    checklist_paths = {(images_root / name).resolve(): name for name in CHECKLIST_PNGS}
    webp_paths = {(images_root / name).resolve(): name for name in SITE_WEBPS}

    for path, name in base_paths.items():
        if not path.is_file():
            result.fail("Check 4", f"Missing base render: site/images/{name}")

    for path, name in checklist_paths.items():
        if not path.is_file():
            result.fail("Check 4", f"Missing Build Checklist PNG: site/images/{name}")
        elif path.stat().st_size > CHECKLIST_MAX_BYTES:
            result.fail(
                "Check 4",
                f"Build Checklist PNG exceeds 500 KiB ({path.stat().st_size} B): site/images/{name}",
            )

    for path, name in webp_paths.items():
        if not path.is_file():
            result.fail("Check 4", f"Missing Companion Site WebP: site/images/{name}")
        elif path.stat().st_size > SITE_WEBP_MAX_BYTES:
            result.fail(
                "Check 4",
                f"Companion Site WebP exceeds 250 KiB ({path.stat().st_size} B): site/images/{name}",
            )

    seen_framed_captures: set[Path] = set()
    for page_path, page in pages.items():
        rel_page = page_path.relative_to(site_root)
        for src, classes in page.imgs:
            target, _, err = _resolve_site_target(site_root, page_path, src)
            if err or target is None:
                continue
            has_framed = "framed-shot" in classes
            if target in base_paths and has_framed:
                result.fail(
                    "Check 4",
                    f"Base render must NOT carry .framed-shot in {rel_page}: {base_paths[target]}",
                )
            elif target in checklist_paths or target in webp_paths:
                seen_framed_captures.add(target)
                if not has_framed:
                    name = checklist_paths.get(target) or webp_paths[target]
                    result.fail(
                        "Check 4",
                        f"Capture must carry .framed-shot in {rel_page}: {name}",
                    )

    for path, name in {**checklist_paths, **webp_paths}.items():
        if path not in seen_framed_captures:
            result.fail("Check 4", f"Capture is never rendered in built HTML: site/images/{name}")


def _published_markdown_files(root: Path) -> list[Path]:
    """Return published Markdown files under docs/ (excluding agents, adr, research)."""
    docs_dir = root / "docs"
    if not docs_dir.is_dir():
        return []
    files: list[Path] = []
    for md_path in sorted(docs_dir.rglob("*.md")):
        rel_parts = md_path.relative_to(docs_dir).parts
        if rel_parts and rel_parts[0] in EXCLUDED_SITE_DIRS:
            continue
        files.append(md_path)
    return files


def check_prompt_blocks_and_prototype_cleanup(
    root: Path,
    site_dir: Path,
    pages: dict[Path, ParsedPage],
    result: VerificationResult,
) -> None:
    """Check 5: Verify 13 Variant B Prompt Blocks, Stage 6 blockquote, and 0 prototype leftovers."""
    site_root = site_dir.resolve()
    total_prompts = 0

    for route, expected in EXPECTED_PROMPTS_BY_ROUTE.items():
        page_path = (site_root / route).resolve()
        page = pages.get(page_path)
        if page is None:
            continue

        actual = page.prompt_blocks
        total_prompts += len(actual)
        if len(actual) != len(expected):
            result.fail(
                "Check 5",
                f"{route}: expected {len(expected)} .admonition.prompt block(s), found {len(actual)}",
            )
            continue

        for idx, (block, (exp_title, exp_adjacent)) in enumerate(zip(actual, expected)):
            if block.title != exp_title:
                result.fail(
                    "Check 5",
                    f"{route} prompt #{idx + 1}: expected title {exp_title!r}, found {block.title!r}",
                )
            if exp_adjacent and not block.adjacent_to_previous:
                result.fail(
                    "Check 5",
                    f"{route} prompt #{idx + 1} ({block.title!r}) is not directly adjacent to previous turn",
                )
            body = block.body_text.strip()
            if (body.startswith(('"', "“")) and body.endswith(('"', "”"))) or (
                body.startswith('*"') and body.endswith('"*')
            ):
                result.fail(
                    "Check 5",
                    f"{route} prompt #{idx + 1} ({block.title!r}) retains outer quote wrapper",
                )

    if total_prompts != 13:
        result.fail("Check 5", f"Expected 13 total .admonition.prompt blocks across built site, found {total_prompts}")

    stage6_page = pages.get((site_root / "tutorial/stage-6-front-panel/index.html").resolve())
    if stage6_page is not None and stage6_page.blockquote_count < 1:
        result.fail("Check 5", "tutorial/stage-6-front-panel/index.html lost its editorial <blockquote>")

    for md_path in _published_markdown_files(root):
        md_text = md_path.read_text(encoding="utf-8")
        if FORBIDDEN_PROMPT_HEADING_RE.search(md_text):
            result.fail(
                "Check 5",
                f"Forbidden standalone prompt heading in {md_path.relative_to(root)}",
            )

    # Prototype leftovers across mkdocs.yml, docs/stylesheets/, docs/javascripts/, and site/
    scan_paths: list[Path] = []
    mkdocs_yml = root / "mkdocs.yml"
    if mkdocs_yml.is_file():
        scan_paths.append(mkdocs_yml)
    for subdir in ("docs/stylesheets", "docs/javascripts"):
        d = root / subdir
        if d.is_dir():
            scan_paths.extend(sorted(p for p in d.rglob("*") if p.is_file()))
    if site_dir.is_dir():
        scan_paths.extend(
            sorted(p for p in site_dir.rglob("*") if p.is_file() and p.suffix in {".html", ".css", ".js"})
        )

    for path in scan_paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        for token in PROTOTYPE_LEFTOVERS:
            if token in text:
                result.fail("Check 5", f"Prototype leftover {token!r} found in {rel}")
        if TABLIST_RE.search(text):
            result.fail("Check 5", f"Prototype leftover role=tablist found in {rel}")


def _has_mixed_lr_subgraph_cross_edges(diagram: str) -> bool:
    """Detect any `direction LR` subgraph whose nodes connect across its boundary."""
    subgraph_stack: list[dict[str, object]] = []
    lr_subgraphs: list[set[str]] = []
    edges: list[tuple[str, str]] = []

    for raw_line in diagram.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%%"):
            continue
        if line.startswith("subgraph "):
            subgraph_stack.append({"has_lr": False, "nodes": set()})
            continue
        if line == "end" and subgraph_stack:
            finished = subgraph_stack.pop()
            if finished["has_lr"]:
                lr_subgraphs.append(finished["nodes"])  # type: ignore[arg-type]
            continue
        if re.match(r"^direction\s+LR\b", line, re.IGNORECASE) and subgraph_stack:
            subgraph_stack[-1]["has_lr"] = True
            continue

        # Parse chained edges (A --> B --> C) or standalone node declarations
        parts = MERMAID_EDGE_ARROW_RE.split(line)
        line_nodes: list[str] = []
        for part in parts:
            m = MERMAID_NODE_ID_RE.match(part)
            if m and m.group(1) not in {"flowchart", "graph", "subgraph", "direction", "style", "classDef"}:
                node_id = m.group(1)
                line_nodes.append(node_id)
                for sg in subgraph_stack:
                    sg["nodes"].add(node_id)  # type: ignore[union-attr]

        if len(parts) > 1 and len(line_nodes) >= 2:
            for src, dst in zip(line_nodes, line_nodes[1:]):
                edges.append((src, dst))

    for sg_nodes in lr_subgraphs:
        for src, dst in edges:
            if (src in sg_nodes) != (dst in sg_nodes):
                return True
    return False


def check_mermaid_guardrails(root: Path, result: VerificationResult) -> None:
    """Check 6: Verify exact 8 Mermaid blocks, 0 hex style/classDef fills, and 0 mixed LR cross-edges."""
    total_blocks = 0
    for md_path in _published_markdown_files(root):
        rel = md_path.relative_to(root).as_posix()
        text = md_path.read_text(encoding="utf-8")
        blocks = MERMAID_BLOCK_RE.findall(text)
        expected_count = EXPECTED_MERMAID_COUNTS.get(rel, 0)
        total_blocks += len(blocks)
        if len(blocks) != expected_count:
            result.fail(
                "Check 6",
                f"{rel}: expected {expected_count} mermaid block(s), found {len(blocks)}",
            )

        for idx, block in enumerate(blocks, 1):
            if MERMAID_HEX_STYLE_RE.search(block):
                result.fail(
                    "Check 6",
                    f"{rel} mermaid block #{idx}: hardcoded inline style/classDef hex fill is forbidden",
                )
            if _has_mixed_lr_subgraph_cross_edges(block):
                result.fail(
                    "Check 6",
                    f"{rel} mermaid block #{idx}: mixed `direction LR` inside subgraph with cross-subgraph edge",
                )

    if total_blocks != 8:
        result.fail("Check 6", f"Expected 8 total mermaid blocks across published docs, found {total_blocks}")


def _all_repo_markdown_files(root: Path) -> list[Path]:
    """Return all Markdown files under docs/ plus root README.md and PotentialImprovements.md."""
    files: list[Path] = []
    for name in ("README.md", "PotentialImprovements.md"):
        p = root / name
        if p.is_file():
            files.append(p)
    docs_dir = root / "docs"
    if docs_dir.is_dir():
        files.extend(sorted(docs_dir.rglob("*.md")))
    return files


def _check_reference_8ad81d0_links(
    root: Path,
    md_files: list[Path],
    reference_dir: Path,
    require_reference: bool,
    result: VerificationResult,
) -> None:
    """Validate EnvelopeFollowerWithSkewLimiter/{blob,tree}/8ad81d0/... against reference_dir."""
    ref_populated = reference_dir.is_dir() and any(reference_dir.iterdir())
    if not ref_populated:
        msg = (
            f"Reference submodule directory is uninitialized/empty ({reference_dir}); "
            "skipping 8ad81d0 target path resolution."
        )
        if require_reference:
            result.fail("Check 7", msg + " (--require-reference / GITHUB_ACTIONS=true)")
        else:
            result.warn("Check 7", msg)
        return

    ref_root = reference_dir.resolve()
    for md_path in md_files:
        rel = md_path.relative_to(root)
        text = md_path.read_text(encoding="utf-8")
        for kind, raw_subpath in PINNED_8AD81D0_RE.findall(text):
            subpath = unquote(raw_subpath.split("#", 1)[0]).rstrip("/")
            target = (ref_root / subpath).resolve()
            if not target.is_relative_to(ref_root):
                result.fail("Check 7", f"{rel}: 8ad81d0 link escapes reference dir: {raw_subpath}")
                continue
            exists = target.is_file() if kind == "blob" else target.is_dir()
            if not exists:
                result.fail(
                    "Check 7",
                    f"{rel}: pinned {kind}/8ad81d0/{raw_subpath} missing in reference dir",
                )


def _check_root_doc_relative_links(
    root: Path, doc_path: Path, result: VerificationResult
) -> None:
    """Verify relative links in root README.md and PotentialImprovements.md resolve in root."""
    root_resolved = root.resolve()
    rel_doc = doc_path.relative_to(root)
    text = doc_path.read_text(encoding="utf-8")
    candidates = MD_LINK_RE.findall(text) + HTML_ATTR_LINK_RE.findall(text)
    for target_raw in candidates:
        if target_raw.startswith(("http://", "https://", "mailto:", "#")):
            continue
        rel_path = unquote(target_raw.split("#", 1)[0].split("?", 1)[0])
        if not rel_path:
            continue
        resolved = (doc_path.parent / rel_path).resolve()
        if not resolved.is_relative_to(root_resolved) or not resolved.exists():
            result.fail("Check 7", f"{rel_doc}: broken relative link '{target_raw}'")


def check_links_hygiene_and_glossary(
    root: Path,
    reference_dir: Path,
    require_reference: bool,
    result: VerificationResult,
) -> None:
    """Check 7: Outbound link pinning, local link resolution, repo hygiene, and GLOSSARY lint."""
    all_md = _all_repo_markdown_files(root)
    root_resolved = root.resolve()

    for md_path in all_md:
        rel = md_path.relative_to(root)
        text = md_path.read_text(encoding="utf-8")
        if UNPINNED_MAIN_RE.search(text):
            result.fail("Check 7", f"{rel}: contains unpinned EnvelopeFollowerWithSkewLimiter/{{blob,tree}}/main/ link")
        if "TutorialUpdateTodo.md" in text:
            result.fail("Check 7", f"{rel}: references deleted TutorialUpdateTodo.md")

        for kind, raw_subpath in LOCAL_MAIN_RE.findall(text):
            subpath = unquote(raw_subpath.split("#", 1)[0]).rstrip("/")
            target = (root_resolved / subpath).resolve()
            exists = target.is_file() if kind == "blob" else target.is_dir()
            if not target.is_relative_to(root_resolved) or not exists:
                result.fail(
                    "Check 7",
                    f"{rel}: broken local repo link {kind}/main/{raw_subpath}",
                )

    _check_reference_8ad81d0_links(root, all_md, reference_dir, require_reference, result)

    if (root / "TutorialUpdateTodo.md").exists():
        result.fail("Check 7", "Superseded TutorialUpdateTodo.md still exists on disk")

    readme = root / "README.md"
    if not readme.is_file():
        result.fail("Check 7", "Missing root README.md")
    else:
        _check_root_doc_relative_links(root, readme, result)
        if "analysis/capability_mode.json" in readme.read_text(encoding="utf-8"):
            result.fail("Check 7", "README.md still references analysis/capability_mode.json")

    pot = root / "PotentialImprovements.md"
    if not pot.is_file():
        result.fail("Check 7", "Missing root PotentialImprovements.md")
    else:
        _check_root_doc_relative_links(root, pot, result)
        pot_text = pot.read_text(encoding="utf-8")
        if "Note for ENV / SKEW builders" not in pot_text:
            result.fail("Check 7", "PotentialImprovements.md missing 'Note for ENV / SKEW builders' callout")
        if COMPANION_SPECS_URL not in pot_text:
            result.fail(
                "Check 7",
                f"PotentialImprovements.md missing live Companion Site link {COMPANION_SPECS_URL}",
            )

    # GLOSSARY.md avoided-terms lint across published docs + README.md + PotentialImprovements.md
    glossary_targets = _published_markdown_files(root) + [
        p for p in (readme, pot) if p.is_file()
    ]
    for path in glossary_targets:
        rel = path.relative_to(root)
        for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            scrubbed = raw_line
            for allowed in HISTORICAL_GLOSSARY_ALLOWLIST:
                scrubbed = scrubbed.replace(allowed, "")
            for term, pattern in AVOIDED_GLOSSARY_PATTERNS:
                if pattern.search(scrubbed):
                    result.fail(
                        "Check 7",
                        f"{rel}:{line_no}: avoided GLOSSARY.md term '{term}'",
                    )


def verify_site(
    root: Path,
    site_dir: Path,
    reference_dir: Path,
    require_reference: bool = False,
) -> VerificationResult:
    """Run all built-site and repository contract checks."""
    result = VerificationResult()
    check_routes_and_exclusions(site_dir, result)
    pages = parse_built_pages(site_dir)
    check_html_links_and_images(site_dir, pages, result)
    check_self_hosted_typography(root, site_dir, pages, result)
    check_visual_assets_and_framing(site_dir, pages, result)
    check_prompt_blocks_and_prototype_cleanup(root, site_dir, pages, result)
    check_mermaid_guardrails(root, result)
    check_links_hygiene_and_glossary(root, reference_dir, require_reference, result)
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    default_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Verify ENV / SKEW Build Tutorial built site and repository contract."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help="Repository root directory (default: parent of scripts/).",
    )
    parser.add_argument(
        "--site",
        type=Path,
        default=None,
        help="Built MkDocs site directory (default: <root>/site).",
    )
    parser.add_argument(
        "--reference-dir",
        type=Path,
        default=None,
        help="Hardware reference submodule directory (default: <root>/reference).",
    )
    parser.add_argument(
        "--require-reference",
        action="store_true",
        help="Fail if reference-dir is uninitialized (also enforced when GITHUB_ACTIONS=true).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    site_dir = (args.site if args.site is not None else root / "site").resolve()
    reference_dir = (
        args.reference_dir if args.reference_dir is not None else root / "reference"
    ).resolve()
    require_reference = args.require_reference or os.environ.get("GITHUB_ACTIONS") == "true"

    result = verify_site(
        root=root,
        site_dir=site_dir,
        reference_dir=reference_dir,
        require_reference=require_reference,
    )
    for warning in result.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    if result.errors:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"Verification FAILED with {len(result.errors)} error(s) "
            f"and {len(result.warnings)} warning(s).",
            file=sys.stderr,
        )
        return 1

    print(
        f"Verification PASSED (all 7 checks clean, {len(result.warnings)} warning(s))."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
