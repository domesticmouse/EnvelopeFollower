/** Canonical GitHub Pages origin for ENV / SKEW Build Tutorial. */
export const SITE_ORIGIN = 'https://domesticmouse.github.io';

/** Canonical GitHub Pages repository base path (no trailing slash). */
export const SITE_BASE = '/EnvelopeFollower';

/** Full canonical Build Tutorial site URL including trailing slash. */
export const SITE_URL = `${SITE_ORIGIN}${SITE_BASE}/`;

/** Build Tutorial GitHub repository URL. */
export const TUTORIAL_REPO_URL = 'https://github.com/domesticmouse/EnvelopeFollower';

/** Hardware & Companion Site GitHub repository URL. */
export const HARDWARE_REPO_URL =
  'https://github.com/domesticmouse/EnvelopeFollowerWithSkewLimiter';

/** Live ENV / SKEW Companion Site URL. */
export const COMPANION_SITE_URL =
  'https://domesticmouse.github.io/EnvelopeFollowerWithSkewLimiter/';

/** Upstream HAGIWO No. 43 inspiration article URL. */
export const HAGIWO_NOTE_URL = 'https://note.com/solder_state/n/n110e9ba066b3?hl=en';

/** Canonical section identifiers matching the tutorial Zod schema. */
export type TutorialSection = 'overview' | 'hardware' | 'companion-site' | 'optional' | 'appendix';

/** Glossary-aligned display labels for all five tutorial sections. */
export const SECTION_LABELS: Readonly<Record<TutorialSection, string>> = {
  overview: 'Overview',
  hardware: 'Hardware Build',
  'companion-site': 'Companion Site',
  optional: 'Optional Exploration',
  appendix: 'Tutorial Appendix',
};

/** Compact section badge labels for search result hits across all five curriculum sections. */
export const SEARCH_SECTION_LABELS: Readonly<Record<TutorialSection, string>> = {
  overview: 'Overview',
  hardware: 'Hardware Build',
  'companion-site': 'Companion Site',
  optional: 'Optional',
  appendix: 'Appendix',
};

/** Ordered list of all five tutorial curriculum groups. */
export const SECTION_ORDER: readonly TutorialSection[] = [
  'overview',
  'hardware',
  'companion-site',
  'optional',
  'appendix',
];

/** Canonical metadata for each of the 13 Build Tutorial routes. */
export interface TutorialRoute {
  order: number;
  id: string;
  path: string;
  section: TutorialSection;
  badge: string;
  stage?: number;
  navTitle: string;
}

/** Complete 13-route curriculum registry in canonical linear order (0..12). */
export const TUTORIAL_ROUTES: readonly TutorialRoute[] = [
  {
    order: 0,
    id: 'index',
    path: '/',
    section: 'overview',
    badge: '00',
    navTitle: 'Overview',
  },
  {
    order: 1,
    id: 'stages/01-hardware-agent-skills',
    path: '/stages/01-hardware-agent-skills/',
    section: 'hardware',
    badge: '01',
    stage: 1,
    navTitle: 'Hardware Agent Skills',
  },
  {
    order: 2,
    id: 'stages/02-sketch-extraction-and-critique',
    path: '/stages/02-sketch-extraction-and-critique/',
    section: 'hardware',
    badge: '02',
    stage: 2,
    navTitle: 'Sketch & Circuit Critique',
  },
  {
    order: 3,
    id: 'stages/03-design-spec-and-dft',
    path: '/stages/03-design-spec-and-dft/',
    section: 'hardware',
    badge: '03',
    stage: 3,
    navTitle: 'DesignSpec & DFT',
  },
  {
    order: 4,
    id: 'stages/04-skidl-and-schematic',
    path: '/stages/04-skidl-and-schematic/',
    section: 'hardware',
    badge: '04',
    stage: 4,
    navTitle: 'SKiDL & Schematic',
  },
  {
    order: 5,
    id: 'stages/05-main-pcb-and-silkscreen',
    path: '/stages/05-main-pcb-and-silkscreen/',
    section: 'hardware',
    badge: '05',
    stage: 5,
    navTitle: '6 HP PCB & Silkscreen',
  },
  {
    order: 6,
    id: 'stages/06-front-panel-and-artwork',
    path: '/stages/06-front-panel-and-artwork/',
    section: 'hardware',
    badge: '06',
    stage: 6,
    navTitle: 'Front Panel & Artwork',
  },
  {
    order: 7,
    id: 'stages/07-fabrication-checklists-and-patches',
    path: '/stages/07-fabrication-checklists-and-patches/',
    section: 'hardware',
    badge: '07',
    stage: 7,
    navTitle: 'Fab, Checklists & Patches',
  },
  {
    order: 8,
    id: 'stages/08-wayfinder-site-planning',
    path: '/stages/08-wayfinder-site-planning/',
    section: 'companion-site',
    badge: '08',
    stage: 8,
    navTitle: 'Wayfinder Site Planning',
  },
  {
    order: 9,
    id: 'stages/09-companion-site-delivery',
    path: '/stages/09-companion-site-delivery/',
    section: 'companion-site',
    badge: '09',
    stage: 9,
    navTitle: 'Companion Site Delivery',
  },
  {
    order: 10,
    id: 'optional/ac-dc-input-coupling',
    path: '/optional/ac-dc-input-coupling/',
    section: 'optional',
    badge: 'OPT',
    navTitle: 'AC/DC Input Coupling',
  },
  {
    order: 11,
    id: 'appendix/netlist-and-bom',
    path: '/appendix/netlist-and-bom/',
    section: 'appendix',
    badge: 'APP',
    navTitle: 'Netlist, BOM & Silkscreen',
  },
  {
    order: 12,
    id: 'appendix/engineering-sign-off-checklist',
    path: '/appendix/engineering-sign-off-checklist/',
    section: 'appendix',
    badge: 'APP',
    navTitle: 'Engineering Sign-Off',
  },
];

/** Canonical route path list beneath SITE_BASE. */
export const CANONICAL_ROUTES: readonly string[] = TUTORIAL_ROUTES.map((route) => route.path);

/** Desktop header jump navigation descriptor. */
export interface JumpNavItem {
  label: string;
  shortLabel: string;
  href: string;
  sections: readonly TutorialSection[];
}

/** Four primary section jump links displayed in the desktop rack header. */
export const PRIMARY_JUMP_NAV: readonly JumpNavItem[] = [
  {
    label: 'Overview',
    shortLabel: '00 OVERVIEW',
    href: '/',
    sections: ['overview'],
  },
  {
    label: 'Hardware',
    shortLabel: '01–07 HARDWARE',
    href: '/stages/01-hardware-agent-skills/',
    sections: ['hardware'],
  },
  {
    label: 'Companion Site',
    shortLabel: '08–09 SITE',
    href: '/stages/08-wayfinder-site-planning/',
    sections: ['companion-site'],
  },
  {
    label: 'Appendix',
    shortLabel: 'APPENDIX',
    href: '/appendix/netlist-and-bom/',
    sections: ['appendix'],
  },
];

/** Prefix an internal site route with SITE_BASE, preserving hashes and external protocols. */
export function withBase(path: string): string {
  if (!path || path === '/') {
    return `${SITE_BASE}/`;
  }
  if (path.startsWith('#') || /^[a-z][a-z0-9+.-]*:/i.test(path)) {
    return path;
  }

  const hashIndex = path.indexOf('#');
  const rawPathname = hashIndex === -1 ? path : path.slice(0, hashIndex);
  const hashSuffix = hashIndex === -1 ? '' : path.slice(hashIndex);

  const leadingSlashPath = rawPathname.startsWith('/') ? rawPathname : `/${rawPathname}`;
  if (leadingSlashPath === SITE_BASE || leadingSlashPath.startsWith(`${SITE_BASE}/`)) {
    return `${leadingSlashPath}${hashSuffix}`;
  }

  return `${SITE_BASE}${leadingSlashPath}${hashSuffix}`;
}

/** Normalize a URL pathname (with or without SITE_BASE, query, or hash) to a canonical route path. */
export function normalizeRoutePath(rawPath: string): string {
  const withoutHash = rawPath.split('#')[0] ?? '/';
  const withoutQuery = withoutHash.split('?')[0] ?? '/';
  let pathname = withoutQuery.startsWith('/') ? withoutQuery : `/${withoutQuery}`;

  if (pathname === SITE_BASE) {
    pathname = '/';
  } else if (pathname.startsWith(`${SITE_BASE}/`)) {
    pathname = pathname.slice(SITE_BASE.length);
  }

  if (pathname.endsWith('/index.html')) {
    pathname = pathname.slice(0, -'index.html'.length);
  }

  if (pathname === '' || pathname === '/') {
    return '/';
  }

  return pathname.endsWith('/') ? pathname : `${pathname}/`;
}

/** Look up the canonical TutorialRoute metadata for a given URL path. */
export function getRouteByPath(rawPath: string): TutorialRoute | undefined {
  const normalized = normalizeRoutePath(rawPath);
  return TUTORIAL_ROUTES.find((route) => route.path === normalized);
}

/** Return the five ordered curriculum groups for the left rail and mobile drawer. */
export function getRouteGroups(): readonly {
  section: TutorialSection;
  label: string;
  routes: readonly TutorialRoute[];
}[] {
  return SECTION_ORDER.map((section) => ({
    section,
    label: SECTION_LABELS[section],
    routes: TUTORIAL_ROUTES.filter((route) => route.section === section),
  }));
}

/** Return true when currentPath belongs to the given desktop jump nav item. */
export function isJumpNavActive(currentPath: string, item: JumpNavItem): boolean {
  const currentRoute = getRouteByPath(currentPath);
  if (!currentRoute) {
    return false;
  }
  return item.sections.includes(currentRoute.section);
}

/** Return linear previous and next routes across canonical order 0..12. */
export function getPrevNextRoutes(order: number): {
  prev?: TutorialRoute;
  next?: TutorialRoute;
} {
  const idx = TUTORIAL_ROUTES.findIndex((route) => route.order === order);
  if (idx === -1) {
    return {};
  }
  return {
    prev: idx > 0 ? TUTORIAL_ROUTES[idx - 1] : undefined,
    next: idx < TUTORIAL_ROUTES.length - 1 ? TUTORIAL_ROUTES[idx + 1] : undefined,
  };
}

/** Format section-aware Prev/Next card kickers (e.g. "Next · Stage 02 →", "Next · Appendix →"). */
export function formatPrevNextKicker(route: TutorialRoute, direction: 'prev' | 'next'): string {
  let targetLabel: string;
  if (route.stage !== undefined) {
    targetLabel = `Stage ${String(route.stage).padStart(2, '0')}`;
  } else if (route.section === 'overview') {
    targetLabel = 'Overview';
  } else if (route.section === 'optional') {
    targetLabel = 'Optional';
  } else {
    targetLabel = 'Appendix';
  }

  return direction === 'prev' ? `← ${targetLabel}` : `Next · ${targetLabel} →`;
}

/** Format the Stage Progress Meter header string for the active route. */
export function getProgressMeterLabel(route: TutorialRoute): string {
  if (route.section === 'overview') {
    return 'PROGRESS · STAGE 00 / 09';
  }
  if (route.stage !== undefined) {
    return `PROGRESS · STAGE ${String(route.stage).padStart(2, '0')} / 09`;
  }
  return `PROGRESS · ${route.badge}`;
}

/** Resolve a built or relative URL to its canonical TutorialSection via TUTORIAL_ROUTES. */
export function getSectionByUrl(rawUrl: string): TutorialSection {
  const withoutOrigin = rawUrl.replace(/^https?:\/\/[^/]+/i, '');
  const matched = getRouteByPath(withoutOrigin);
  if (matched) {
    return matched.section;
  }

  const normalized = normalizeRoutePath(withoutOrigin);
  if (normalized.startsWith('/optional/')) {
    return 'optional';
  }
  if (normalized.startsWith('/appendix/')) {
    return 'appendix';
  }
  if (normalized.startsWith('/stages/08') || normalized.startsWith('/stages/09')) {
    return 'companion-site';
  }
  if (normalized.startsWith('/stages/')) {
    return 'hardware';
  }
  return 'overview';
}
