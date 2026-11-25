import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { describe, expect, it } from 'vitest';
import {
  PANEL_CONTROL_COORDS,
  PANEL_VIEWBOX,
  extractFaceplateLayers,
  extractFaceplateMotifs,
  parseFaceplateLayersFromStrings,
  parseFaceplateMotifsFromStrings,
  renderAssembledFaceplateSvg,
} from '../src/lib/panel-svg.ts';

describe('panel-svg extractor', () => {
  it('extracts and recolors faceplate layers from reference/panel_art/ and strips registration frame', () => {
    const layers = extractFaceplateLayers();

    expect(layers.goldLayerSvg).toContain('id="_01_F_Mask_Gold"');
    expect(layers.goldLayerSvg).toContain('#D8B154');
    expect(layers.goldLayerSvg).not.toContain('#C89B3C');
    expect(layers.goldLayerSvg).not.toContain('_03_Registration_Frame');
    expect(layers.goldLayerSvg).not.toContain('registration_frame');

    expect(layers.silkLayerSvg).toContain('id="_02_F_SilkS_White"');
    expect(layers.silkLayerSvg).toContain('#F4F5F7');
    expect(layers.silkLayerSvg).not.toContain('#000000');
    expect(layers.silkLayerSvg).not.toContain('_03_Registration_Frame');
    expect(layers.silkLayerSvg).not.toContain('registration_frame');
  });

  it('extracts all discrete UI motifs from front_soldermask.svg with currentColor and zero registration frame', () => {
    const motifs = extractFaceplateMotifs();

    expect(motifs.heroEnvelopeSvg).toContain('viewBox="13.5 1.0 15.5 5.0"');
    expect(motifs.heroEnvelopeSvg).toContain('class="motif-hero-env"');
    expect(motifs.heroEnvelopeSvg).toContain('points="13.9,4.9');
    expect(motifs.heroEnvelopeSvg).toContain('fill="currentColor"');
    expect(motifs.heroEnvelopeSvg).not.toContain('#C89B3C');

    expect(motifs.gainBarsSvg).toContain('viewBox="23.5 16.5 4.8 9.5"');
    expect(motifs.gainBarsSvg).toContain('class="motif-gain-bars"');
    expect(motifs.gainBarsSvg).toContain('points="23.9,23.3');
    expect(motifs.gainBarsSvg).toContain('points="27.26,16.8');
    expect(motifs.gainBarsSvg).toContain('fill="currentColor"');

    expect(motifs.ledOctagonSvg).toContain('viewBox="11.5 78.8 7.0 7.0"');
    expect(motifs.ledOctagonSvg).toContain('class="motif-led-octagon"');
    expect(motifs.ledOctagonSvg).toContain('M13.8131 79.3847');
    expect(motifs.ledOctagonSvg).toContain('fill="currentColor"');

    expect(motifs.normalArrowSvg).toContain('viewBox="13.2 94.5 3.6 2.5"');
    expect(motifs.normalArrowSvg).toContain('class="motif-normal-arrow"');
    expect(motifs.normalArrowSvg).toContain('points="13.45,95.47');
    expect(motifs.normalArrowSvg).toContain('fill="currentColor"');

    expect(motifs.framingWingsSvg).toContain('class="motif-framing-wings"');
    expect(motifs.framingWingsSvg).toContain('width="0.42"');
    expect(motifs.framingWingsSvg).toContain('fill="currentColor"');

    expect(motifs.envSkewSlabSvg).toContain('aria-label="ENV / SKEW"');
    expect(motifs.slewRiseSvg).toContain('class="motif-slew-rise"');
    expect(motifs.slewFallSvg).toContain('class="motif-slew-fall"');

    for (const svg of Object.values(motifs)) {
      expect(svg).not.toContain('registration_frame');
      expect(svg).not.toContain('_03_Registration_Frame');
    }
  });

  it('renders an assembled 6 HP faceplate SVG with viewBox 0 0 30.00 128.50 and all 11 hardware controls', () => {
    const layers = extractFaceplateLayers();
    const svg = renderAssembledFaceplateSvg(layers);

    expect(PANEL_VIEWBOX).toBe('0 0 30.00 128.50');
    expect(Object.keys(PANEL_CONTROL_COORDS)).toHaveLength(11);
    expect(svg).toContain(`viewBox="${PANEL_VIEWBOX}"`);
    expect(svg).toContain('#141518');
    expect(svg).toContain('#D8B154');
    expect(svg).toContain('#F4F5F7');
    expect(svg).not.toContain('registration_frame');
  });

  it('strips _03_Registration_Frame even when nested or ordered differently in raw SVG input', () => {
    const mask = `
      <svg viewBox="0 0 30.00 128.50">
        <g id="_01_F_Mask_Gold">
          <polygon points="13.9,4.9 15.2,4.9 16.85,1.35" fill="#C89B3C" />
        </g>
        <g id="_03_Registration_Frame"><path id="registration_frame" d="M0 0 Z" fill="#C89B3C" /></g>
      </svg>`;
    const silk = `
      <svg viewBox="0 0 30.00 128.50">
        <g id="_02_F_SilkS_White"><rect x="1.6" y="12.03" width="26.8" height="0.24" fill="#000000" /></g>
        <g id="_03_Registration_Frame"><path id="registration_frame" d="M0 0 Z" fill="#000000" /></g>
      </svg>`;

    const parsed = parseFaceplateLayersFromStrings(mask, silk);
    expect(parsed.goldLayerSvg).toContain('#D8B154');
    expect(parsed.goldLayerSvg).not.toContain('registration_frame');
    expect(parsed.silkLayerSvg).toContain('#F4F5F7');
    expect(parsed.silkLayerSvg).not.toContain('registration_frame');
  });

  it('throws when required motif geometry is missing from soldermask input', () => {
    expect(() =>
      parseFaceplateMotifsFromStrings('<svg><g id="_01_F_Mask_Gold"></g></svg>'),
    ).toThrow(/motif/i);
  });

  it('fails fast with actionable git submodule update --init --recursive message when reference/panel_art is missing', () => {
    const emptyRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'env-skew-missing-ref-'));
    try {
      expect(() => extractFaceplateLayers(emptyRoot)).toThrow(
        /git submodule update --init --recursive/,
      );
      expect(() => extractFaceplateMotifs(emptyRoot)).toThrow(
        /git submodule update --init --recursive/,
      );
    } finally {
      fs.rmSync(emptyRoot, { recursive: true, force: true });
    }
  });
});
