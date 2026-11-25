import fs from 'node:fs';
import path from 'node:path';
import {
  parseFaceplateLayersFromStrings,
  parseFaceplateMotifsFromStrings,
  type FaceplateLayerMarkup,
  type FaceplateMotifs,
} from './panel-svg-shared.ts';
import { resolveRepoRoot } from './repo-files.ts';

export * from './panel-svg-shared.ts';

function readPanelSvgFile(resolvedRoot: string, relPath: string): string {
  const fullPath = path.join(resolvedRoot, relPath);
  if (!fs.existsSync(fullPath) || !fs.statSync(fullPath).isFile()) {
    throw new Error(
      `Missing required panel artwork file: ${relPath}. ` +
        `Initialize the reference/ submodule with: git submodule update --init --recursive`,
    );
  }
  const content = fs.readFileSync(fullPath, 'utf8');
  if (!content.trim()) {
    throw new Error(
      `Empty panel artwork file: ${relPath}. ` +
        `Initialize the reference/ submodule with: git submodule update --init --recursive`,
    );
  }
  return content;
}

/** Read reference/panel_art/front_soldermask.svg and front_silkscreen.svg layers at build time. */
export function extractFaceplateLayers(repoRoot?: string): FaceplateLayerMarkup {
  const resolvedRoot = path.resolve(repoRoot ?? resolveRepoRoot());
  const maskText = readPanelSvgFile(resolvedRoot, 'reference/panel_art/front_soldermask.svg');
  const silkText = readPanelSvgFile(resolvedRoot, 'reference/panel_art/front_silkscreen.svg');

  return parseFaceplateLayersFromStrings(maskText, silkText);
}

/** Extract discrete UI motifs at build time directly from reference/panel_art/front_soldermask.svg. */
export function extractFaceplateMotifs(repoRoot?: string): FaceplateMotifs {
  const resolvedRoot = path.resolve(repoRoot ?? resolveRepoRoot());
  const maskText = readPanelSvgFile(resolvedRoot, 'reference/panel_art/front_soldermask.svg');

  return parseFaceplateMotifsFromStrings(maskText);
}
