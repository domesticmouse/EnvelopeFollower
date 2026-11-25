/** Canonical 6 HP × 3U Eurorack panel SVG coordinate space (mm). */
export const PANEL_VIEWBOX = '0 0 30.00 128.50';

/** Hardware control category on the ENV / SKEW front panel. */
export type PanelControlKind = 'pot' | 'switch' | 'led' | 'jack';

/** All 11 front-panel control identifiers. */
export type PanelControlId =
  | 'rv1'
  | 'rv2'
  | 'rv3'
  | 'rv4'
  | 'sw1'
  | 'led1'
  | 'sw2'
  | 'j1'
  | 'j2'
  | 'j3'
  | 'j4';

/** Physical control center metadata in millimeters. */
export interface PanelControlMeta {
  x: number;
  y: number;
  kind: PanelControlKind;
  label: string;
}

/** Exact hardware centers (mm) for all 11 front-panel controls. */
export const PANEL_CONTROL_COORDS: Readonly<Record<PanelControlId, PanelControlMeta>> = {
  rv1: { x: 15.0, y: 21.25, kind: 'pot', label: 'GAIN' },
  rv2: { x: 15.0, y: 36.75, kind: 'pot', label: 'ATK' },
  rv3: { x: 15.0, y: 52.25, kind: 'pot', label: 'REL' },
  rv4: { x: 15.0, y: 67.75, kind: 'pot', label: 'OFFSET' },
  sw1: { x: 7.0, y: 82.25, kind: 'switch', label: 'SMOOTH / RAW' },
  led1: { x: 15.0, y: 82.25, kind: 'led', label: '+ / − LED' },
  sw2: { x: 23.0, y: 82.25, kind: 'switch', label: 'SLOW / FAST' },
  j1: { x: 8.0, y: 95.75, kind: 'jack', label: 'IN' },
  j2: { x: 22.0, y: 95.75, kind: 'jack', label: 'SLEW IN' },
  j3: { x: 8.0, y: 110.75, kind: 'jack', label: 'OUT' },
  j4: { x: 22.0, y: 110.75, kind: 'jack', label: 'INV OUT' },
};

/** Extracted and recolored F.Mask (gold) and F.SilkS (white) layers with registration frame stripped. */
export interface FaceplateLayerMarkup {
  goldLayerSvg: string;
  silkLayerSvg: string;
}

/** Discrete SVG UI motifs extracted directly from front_soldermask.svg `_01_F_Mask_Gold`. */
export interface FaceplateMotifs {
  heroEnvelopeSvg: string;
  envSkewSlabSvg: string;
  gainBarsSvg: string;
  slewRiseSvg: string;
  slewFallSvg: string;
  ledOctagonSvg: string;
  normalArrowSvg: string;
  framingWingsSvg: string;
}

/** Convert an 11-tick dial step (0..10) to pointer rotation angle in degrees from 12 o'clock. */
export function tickToDeg(tick: number): number {
  return -150 + tick * 30;
}

function extractGroupById(svgText: string, groupId: string, sourceFile: string): string {
  const openRe = new RegExp(`<g\\b[^>]*\\bid=["']${groupId}["'][^>]*>`);
  const openMatch = openRe.exec(svgText);
  if (!openMatch) {
    throw new Error(`Missing <g id="${groupId}"> layer in ${sourceFile}`);
  }

  const startIndex = openMatch.index;
  const tagRe = /<(\/?)g\b([^>]*)>/g;
  tagRe.lastIndex = startIndex;

  let depth = 0;
  let tagMatch: RegExpExecArray | null;
  while ((tagMatch = tagRe.exec(svgText)) !== null) {
    const isClosing = tagMatch[1] === '/';
    const attrs = tagMatch[2] ?? '';
    const isSelfClosing = !isClosing && attrs.trimEnd().endsWith('/');

    if (isClosing) {
      depth -= 1;
      if (depth === 0) {
        return svgText.slice(startIndex, tagRe.lastIndex);
      }
    } else if (!isSelfClosing) {
      depth += 1;
    }
  }

  throw new Error(`Unclosed <g id="${groupId}"> layer in ${sourceFile}`);
}

function stripRegistrationFrame(svgText: string): string {
  return svgText
    .replace(/<g\b[^>]*\bid=["']_03_Registration_Frame["'][^>]*>[\s\S]*?<\/g>/g, '')
    .replace(/<[^>]*\bid=["']registration_frame["'][^>]*\/>/g, '');
}

function recolorGroupSvg(groupSvg: string, color: string): string {
  return groupSvg
    .replace(/\bfill="(?!none")[^"]*"/g, `fill="${color}"`)
    .replace(/\bstroke="(?!none")[^"]*"/g, `stroke="${color}"`);
}

function collectMatchingNodes(groupSvg: string, pattern: RegExp, label: string): string[] {
  const matches = groupSvg.match(pattern);
  if (!matches || matches.length === 0) {
    throw new Error(`Missing ${label} motif geometry in front_soldermask.svg`);
  }
  return matches;
}

function collectRequiredNode(groupSvg: string, pattern: RegExp, label: string): string {
  const match = pattern.exec(groupSvg);
  if (!match) {
    throw new Error(`Missing ${label} motif geometry in front_soldermask.svg`);
  }
  return match[0];
}

function wrapMotifSvg(
  viewBox: string,
  className: string,
  innerMarkup: string,
  accessible?: { ariaLabel: string },
): string {
  const a11yAttrs = accessible
    ? `role="img" aria-label="${accessible.ariaLabel}"`
    : 'aria-hidden="true" focusable="false"';
  return `<svg viewBox="${viewBox}" class="${className}" ${a11yAttrs}>\n  ${innerMarkup}\n</svg>`;
}

/** Pure string-based parser for front_soldermask.svg and front_silkscreen.svg layers. */
export function parseFaceplateLayersFromStrings(
  maskText: string,
  silkText: string,
): FaceplateLayerMarkup {
  const cleanMask = stripRegistrationFrame(maskText);
  const cleanSilk = stripRegistrationFrame(silkText);

  const rawGoldGroup = extractGroupById(
    cleanMask,
    '_01_F_Mask_Gold',
    'reference/panel_art/front_soldermask.svg',
  );
  const rawSilkGroup = extractGroupById(
    cleanSilk,
    '_02_F_SilkS_White',
    'reference/panel_art/front_silkscreen.svg',
  );

  return {
    goldLayerSvg: recolorGroupSvg(stripRegistrationFrame(rawGoldGroup), '#D8B154'),
    silkLayerSvg: recolorGroupSvg(stripRegistrationFrame(rawSilkGroup), '#F4F5F7'),
  };
}

/** Extract discrete UI motifs directly from front_soldermask.svg `_01_F_Mask_Gold` geometry. */
export function parseFaceplateMotifsFromStrings(maskText: string): FaceplateMotifs {
  const cleanMask = stripRegistrationFrame(maskText);
  const rawGoldGroup = extractGroupById(
    cleanMask,
    '_01_F_Mask_Gold',
    'reference/panel_art/front_soldermask.svg',
  );
  const currentGold = recolorGroupSvg(stripRegistrationFrame(rawGoldGroup), 'currentColor');

  const heroPoly = collectRequiredNode(
    currentGold,
    /<polygon\b[^>]*\bpoints="13\.9,4\.9[^"]*"[^>]*\/>/,
    'hero-envelope polygon',
  );
  const heroBars = collectMatchingNodes(
    currentGold,
    /<rect\b[^>]*\bx="(?:17\.65|19\.56|21\.47|23\.38|25\.29|27\.2)"[^>]*\/>/g,
    'hero-envelope decay bars',
  );
  if (heroBars.length !== 6) {
    throw new Error(
      `Expected 6 hero-envelope decay bars motif elements, found ${heroBars.length}`,
    );
  }

  const slabPath = collectRequiredNode(
    currentGold,
    /<path\b[^>]*\bd="M1\.2 10\.3[^"]*"[^>]*\/>/,
    'env-skew slab',
  );

  const gainBarNodes = collectMatchingNodes(
    currentGold,
    /<polygon\b[^>]*\bpoints="(?:23\.9,23\.3|25\.02,21\.3|26\.14,19\.1|27\.26,16\.8)[^"]*"[^>]*\/>/g,
    'progressive gain bars',
  );
  if (gainBarNodes.length !== 4) {
    throw new Error(`Expected 4 progressive gain bars motif elements, found ${gainBarNodes.length}`);
  }

  const slewRiseNode = collectRequiredNode(
    currentGold,
    /<polygon\b[^>]*\bpoints="23\.9,40\.35[^"]*"[^>]*\/>/,
    'slew-rise slope',
  );
  const slewFallNode = collectRequiredNode(
    currentGold,
    /<polygon\b[^>]*\bpoints="23\.9,47\.85[^"]*"[^>]*\/>/,
    'slew-fall slope',
  );
  const ledOctagonNode = collectRequiredNode(
    currentGold,
    /<path\b[^>]*\bd="M13\.8131 79\.3847[^"]*"[^>]*\/>/,
    'octagonal LED1',
  );
  const normalArrowNode = collectRequiredNode(
    currentGold,
    /<polygon\b[^>]*\bpoints="13\.45,95\.47[^"]*"[^>]*\/>/,
    'normaling arrow',
  );
  const wingNodes = collectMatchingNodes(
    currentGold,
    /<rect\b[^>]*\bwidth="0\.42"[^>]*\/>/g,
    'framing wings',
  );
  if (wingNodes.length !== 8) {
    throw new Error(`Expected 8 framing wings motif elements, found ${wingNodes.length}`);
  }

  return {
    heroEnvelopeSvg: wrapMotifSvg(
      '13.5 1.0 15.5 5.0',
      'motif-hero-env',
      [heroPoly, ...heroBars].join('\n  '),
    ),
    envSkewSlabSvg: wrapMotifSvg('1.0 6.6 28.0 5.0', 'motif-slab-svg', slabPath, {
      ariaLabel: 'ENV / SKEW',
    }),
    gainBarsSvg: wrapMotifSvg('23.5 16.5 4.8 9.5', 'motif-gain-bars', gainBarNodes.join('\n  ')),
    slewRiseSvg: wrapMotifSvg('23.5 32.0 5.0 9.5', 'motif-slew-rise', slewRiseNode),
    slewFallSvg: wrapMotifSvg('23.5 47.5 5.0 9.5', 'motif-slew-fall', slewFallNode),
    ledOctagonSvg: wrapMotifSvg('11.5 78.8 7.0 7.0', 'motif-led-octagon', ledOctagonNode),
    normalArrowSvg: wrapMotifSvg('13.2 94.5 3.6 2.5', 'motif-normal-arrow', normalArrowNode),
    framingWingsSvg: wrapMotifSvg('0.5 13.0 29.0 61.2', 'motif-framing-wings', wingNodes.join('\n  ')),
  };
}

/** Assemble the 6 HP Matte Black + ENIG Gold + Silkscreen White faceplate SVG. */
export function renderAssembledFaceplateSvg(layers: FaceplateLayerMarkup): string {
  const knobs = [
    { key: 'rv1' as const, tick: 7 },
    { key: 'rv2' as const, tick: 3 },
    { key: 'rv3' as const, tick: 6 },
    { key: 'rv4' as const, tick: 5 },
  ]
    .map(({ key, tick }) => {
      const { x, y } = PANEL_CONTROL_COORDS[key];
      return `
    <circle cx="${x}" cy="${y}" r="4.75" fill="#0B0C0F" stroke="#3A3F4D" stroke-width="0.22" />
    <circle cx="${x}" cy="${y}" r="4.35" fill="url(#tutorial-knob-cap-grad)" stroke="#484F61" stroke-width="0.2" />
    <g transform="rotate(${tickToDeg(tick)} ${x} ${y})">
      <line x1="${x}" y1="${y - 1.1}" x2="${x}" y2="${y - 4.15}" stroke="#F4F5F7" stroke-width="0.95" stroke-linecap="round" />
      <circle cx="${x}" cy="${y}" r="0.85" fill="#303542" />
    </g>`;
    })
    .join('');

  const switches = [
    { key: 'sw1' as const, up: true },
    { key: 'sw2' as const, up: false },
  ]
    .map(({ key, up }) => {
      const { x, y } = PANEL_CONTROL_COORDS[key];
      const tipY = up ? y - 2.55 : y + 2.55;
      return `
    <circle cx="${x}" cy="${y}" r="2.55" fill="url(#tutorial-jack-nut-grad)" stroke="#6C7387" stroke-width="0.25" />
    <circle cx="${x}" cy="${y}" r="1.2" fill="#0B0C0F" />
    <line x1="${x}" y1="${y}" x2="${x}" y2="${tipY}" stroke="#090A0D" stroke-width="1.9" stroke-linecap="round" />
    <line x1="${x}" y1="${y}" x2="${x}" y2="${tipY}" stroke="#E2BE66" stroke-width="1.3" stroke-linecap="round" />
    <circle cx="${x}" cy="${tipY}" r="0.85" fill="#F4F5F7" />`;
    })
    .join('');

  const led = PANEL_CONTROL_COORDS.led1;
  const jacks = (['j1', 'j2', 'j3', 'j4'] as const)
    .map((key) => {
      const { x, y } = PANEL_CONTROL_COORDS[key];
      return `
    <circle cx="${x}" cy="${y}" r="3.1" fill="url(#tutorial-jack-nut-grad)" stroke="#666D80" stroke-width="0.24" />
    <circle cx="${x}" cy="${y}" r="2.35" fill="#1E222B" stroke="#4E5466" stroke-width="0.18" />
    <circle cx="${x}" cy="${y}" r="1.55" fill="#07080A" />`;
    })
    .join('');

  const slots = [3.0, 125.5]
    .map(
      (cy) => `
    <rect x="4.55" y="${(cy - 1.8).toFixed(2)}" width="5.9" height="3.6" rx="1.8" fill="#262A34" stroke="#464C5C" stroke-width="0.18" />
    <rect x="4.75" y="${(cy - 1.6).toFixed(2)}" width="5.5" height="3.2" rx="1.6" fill="#090A0D" />`,
    )
    .join('');

  return `<svg class="faceplate-svg" viewBox="${PANEL_VIEWBOX}" width="108" height="463" role="img" aria-label="ENV / SKEW 6 HP assembled front panel with ENIG gold artwork, four knobs, two toggle switches, bi-color LED, and four 3.5 mm jack sockets">
  <defs>
    <radialGradient id="tutorial-led-glow-grad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#4ADE80" stop-opacity="0.95" />
      <stop offset="55%" stop-color="#4ADE80" stop-opacity="0.4" />
      <stop offset="100%" stop-color="#4ADE80" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="tutorial-knob-cap-grad" cx="38%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#2E3340" />
      <stop offset="75%" stop-color="#191B22" />
      <stop offset="100%" stop-color="#101115" />
    </radialGradient>
    <radialGradient id="tutorial-jack-nut-grad" cx="40%" cy="35%" r="70%">
      <stop offset="0%" stop-color="#585E6E" />
      <stop offset="100%" stop-color="#252932" />
    </radialGradient>
  </defs>
  <rect class="panel-substrate" x="0.25" y="0.25" width="29.5" height="128.0" rx="0.5" fill="#141518" stroke="#6E7485" stroke-width="0.5" />
  <g>${slots}
  </g>
  ${layers.goldLayerSvg}
  ${layers.silkLayerSvg}
  <g class="controls-layer">${knobs}${switches}
    <circle cx="${led.x}" cy="${led.y}" r="4.6" fill="url(#tutorial-led-glow-grad)" opacity="0.78" />
    <circle cx="${led.x}" cy="${led.y}" r="1.95" fill="#101216" stroke="#3E4352" stroke-width="0.22" />
    <circle cx="${led.x}" cy="${led.y}" r="1.55" fill="#4ADE80" stroke="#16A34A" stroke-width="0.2" />
    <circle cx="${led.x - 0.45}" cy="${led.y - 0.45}" r="0.42" fill="#FFFFFF" opacity="0.4" />${jacks}
  </g>
</svg>`;
}
