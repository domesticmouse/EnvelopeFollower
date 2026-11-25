import { describe, expect, it } from 'vitest';
import {
  CANONICAL_ROUTES,
  PRIMARY_JUMP_NAV,
  SECTION_LABELS,
  SITE_BASE,
  SITE_ORIGIN,
  SITE_URL,
  TUTORIAL_ROUTES,
  formatPrevNextKicker,
  getPrevNextRoutes,
  getProgressMeterLabel,
  getRouteByPath,
  getRouteGroups,
  isJumpNavActive,
  normalizeRoutePath,
  withBase,
} from '../src/lib/routes.ts';
import { tutorialSchema } from '../src/lib/tutorial-schema.ts';

describe('routes registry', () => {
  it('defines canonical site origin, base, and 13 ordered routes (0..12)', () => {
    expect(SITE_ORIGIN).toBe('https://domesticmouse.github.io');
    expect(SITE_BASE).toBe('/EnvelopeFollower');
    expect(SITE_URL).toBe('https://domesticmouse.github.io/EnvelopeFollower/');

    expect(TUTORIAL_ROUTES).toHaveLength(13);
    expect(CANONICAL_ROUTES).toHaveLength(13);

    TUTORIAL_ROUTES.forEach((route, idx) => {
      expect(route.order).toBe(idx);
      expect(route.path.startsWith('/')).toBe(true);
      expect(route.path.endsWith('/')).toBe(true);
    });

    expect(CANONICAL_ROUTES).toEqual([
      '/',
      '/stages/01-hardware-agent-skills/',
      '/stages/02-sketch-extraction-and-critique/',
      '/stages/03-design-spec-and-dft/',
      '/stages/04-skidl-and-schematic/',
      '/stages/05-main-pcb-and-silkscreen/',
      '/stages/06-front-panel-and-artwork/',
      '/stages/07-fabrication-checklists-and-patches/',
      '/stages/08-wayfinder-site-planning/',
      '/stages/09-companion-site-delivery/',
      '/optional/ac-dc-input-coupling/',
      '/appendix/netlist-and-bom/',
      '/appendix/engineering-sign-off-checklist/',
    ]);
  });

  it('groups all 13 routes into 5 glossary-aligned sections', () => {
    expect(SECTION_LABELS).toEqual({
      overview: 'Overview',
      hardware: 'Hardware Build',
      'companion-site': 'Companion Site',
      optional: 'Optional Exploration',
      appendix: 'Tutorial Appendix',
    });

    const groups = getRouteGroups();
    expect(groups.map((g) => [g.section, g.label, g.routes.length])).toEqual([
      ['overview', 'Overview', 1],
      ['hardware', 'Hardware Build', 7],
      ['companion-site', 'Companion Site', 2],
      ['optional', 'Optional Exploration', 1],
      ['appendix', 'Tutorial Appendix', 2],
    ]);
  });

  it('normalizes URLs and prefixes SITE_BASE without double-prefixing', () => {
    expect(withBase('/')).toBe('/EnvelopeFollower/');
    expect(withBase('/appendix/netlist-and-bom/')).toBe(
      '/EnvelopeFollower/appendix/netlist-and-bom/',
    );
    expect(withBase('/EnvelopeFollower/stages/04-skidl-and-schematic/#bom')).toBe(
      '/EnvelopeFollower/stages/04-skidl-and-schematic/#bom',
    );
    expect(withBase('#top')).toBe('#top');
    expect(withBase('https://example.com/foo')).toBe('https://example.com/foo');

    expect(normalizeRoutePath('/EnvelopeFollower')).toBe('/');
    expect(normalizeRoutePath('/EnvelopeFollower/')).toBe('/');
    expect(normalizeRoutePath('/EnvelopeFollower/index.html')).toBe('/');
    expect(normalizeRoutePath('/EnvelopeFollower/appendix/netlist-and-bom')).toBe(
      '/appendix/netlist-and-bom/',
    );
    expect(normalizeRoutePath('/appendix/netlist-and-bom/?q=1#parts')).toBe(
      '/appendix/netlist-and-bom/',
    );
  });

  it('provides 4 desktop jump nav items and highlights active section', () => {
    expect(PRIMARY_JUMP_NAV.map((item) => item.label)).toEqual([
      'Overview',
      'Hardware',
      'Companion Site',
      'Appendix',
    ]);

    expect(isJumpNavActive('/', PRIMARY_JUMP_NAV[0])).toBe(true);
    expect(isJumpNavActive('/', PRIMARY_JUMP_NAV[1])).toBe(false);
    expect(
      isJumpNavActive('/EnvelopeFollower/stages/05-main-pcb-and-silkscreen/', PRIMARY_JUMP_NAV[1]),
    ).toBe(true);
    expect(
      isJumpNavActive('/EnvelopeFollower/stages/08-wayfinder-site-planning/', PRIMARY_JUMP_NAV[2]),
    ).toBe(true);
    expect(
      isJumpNavActive('/EnvelopeFollower/appendix/netlist-and-bom/', PRIMARY_JUMP_NAV[3]),
    ).toBe(true);
  });

  it('resolves linear prev/next routes and section-labeled kickers across 0..12', () => {
    const first = getPrevNextRoutes(0);
    expect(first.prev).toBeUndefined();
    expect(first.next?.order).toBe(1);
    expect(formatPrevNextKicker(first.next!, 'next')).toBe('Next · Stage 01 →');

    const stage9 = getPrevNextRoutes(9);
    expect(stage9.prev?.order).toBe(8);
    expect(stage9.next?.order).toBe(10);
    expect(formatPrevNextKicker(stage9.prev!, 'prev')).toBe('← Stage 08');
    expect(formatPrevNextKicker(stage9.next!, 'next')).toBe('Next · Optional →');

    const last = getPrevNextRoutes(12);
    expect(last.prev?.order).toBe(11);
    expect(last.next).toBeUndefined();
    expect(formatPrevNextKicker(last.prev!, 'prev')).toBe('← Appendix');
  });

  it('formats Stage Progress Meter labels cleanly for all route types', () => {
    expect(getProgressMeterLabel(getRouteByPath('/')!)).toBe('PROGRESS · STAGE 00 / 09');
    expect(getProgressMeterLabel(getRouteByPath('/stages/05-main-pcb-and-silkscreen/')!)).toBe(
      'PROGRESS · STAGE 05 / 09',
    );
    expect(getProgressMeterLabel(getRouteByPath('/optional/ac-dc-input-coupling/')!)).toBe(
      'PROGRESS · OPT',
    );
    expect(getProgressMeterLabel(getRouteByPath('/appendix/netlist-and-bom/')!)).toBe(
      'PROGRESS · APP',
    );
  });
});

describe('tutorialSchema', () => {
  it('accepts valid frontmatter with and without optional heroMeta/stage', () => {
    const parsed = tutorialSchema.parse({
      title: 'Netlist, BOM & Silkscreen Schedule',
      navTitle: 'Netlist, BOM & Silkscreen',
      description: 'Complete 80-part BOM and 48-net schedule.',
      section: 'appendix',
      order: 11,
      badge: 'APP',
      heroMeta: [
        { label: 'PARTS', value: '50 SMD + 18 THT' },
        { label: 'NETS', value: '48 Active' },
      ],
    });
    expect(parsed.section).toBe('appendix');
    expect(parsed.heroMeta).toHaveLength(2);

    const minimal = tutorialSchema.parse({
      title: 'Overview',
      navTitle: 'Overview',
      description: 'Overview page.',
      section: 'overview',
      order: 0,
    });
    expect(minimal.order).toBe(0);
  });

  it('rejects invalid section, negative order, out-of-range stage, and >4 heroMeta rows', () => {
    expect(() =>
      tutorialSchema.parse({
        title: 'Bad',
        navTitle: 'Bad',
        description: 'Bad section',
        section: 'reference',
        order: 1,
      }),
    ).toThrow();

    expect(() =>
      tutorialSchema.parse({
        title: 'Bad',
        navTitle: 'Bad',
        description: 'Bad stage',
        section: 'hardware',
        order: 1,
        stage: 10,
      }),
    ).toThrow();

    expect(() =>
      tutorialSchema.parse({
        title: 'Bad',
        navTitle: 'Bad',
        description: 'Too many heroMeta',
        section: 'appendix',
        order: 11,
        heroMeta: [
          { label: '1', value: 'a' },
          { label: '2', value: 'b' },
          { label: '3', value: 'c' },
          { label: '4', value: 'd' },
          { label: '5', value: 'e' },
        ],
      }),
    ).toThrow();
  });
});
