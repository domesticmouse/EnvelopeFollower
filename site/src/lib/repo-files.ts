import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

/** Resolve the Build Tutorial repository root from either site/ or root CWD. */
export function resolveRepoRoot(): string {
  const candidates = [process.cwd(), path.dirname(fileURLToPath(import.meta.url))];
  for (const start of candidates) {
    let dir = path.resolve(start);
    while (true) {
      if (
        fs.existsSync(path.join(dir, 'GLOSSARY.md')) &&
        fs.existsSync(path.join(dir, 'docs/adr/0001-astro-core-mdx-tutorial-site.md'))
      ) {
        return dir;
      }
      const parent = path.dirname(dir);
      if (parent === dir) {
        break;
      }
      dir = parent;
    }
  }
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
}
