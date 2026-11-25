import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { verifyBuiltSite } from '../src/lib/site-contract.ts';

interface CliArgs {
  root?: string;
  dist?: string;
  referenceDir?: string;
  requireReference: boolean;
}

function parseCliArgs(argv: readonly string[]): CliArgs {
  const args: CliArgs = {
    requireReference: process.env.GITHUB_ACTIONS === 'true',
  };

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i] ?? '';
    if (token === '--require-reference') {
      args.requireReference = true;
    } else if (token === '--root' && argv[i + 1]) {
      args.root = argv[++i];
    } else if (token === '--dist' && argv[i + 1]) {
      args.dist = argv[++i];
    } else if (token === '--reference-dir' && argv[i + 1]) {
      args.referenceDir = argv[++i];
    } else {
      console.error(`Unknown or incomplete CLI argument: ${token}`);
      process.exit(2);
    }
  }

  return args;
}

const cli = parseCliArgs(process.argv.slice(2));
const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const siteDir = path.resolve(scriptDir, '..');
const repoRoot = path.resolve(cli.root ?? path.join(siteDir, '..'));
const distDir = path.resolve(cli.dist ?? path.join(siteDir, 'dist'));
const referenceDir = path.resolve(cli.referenceDir ?? path.join(repoRoot, 'reference'));

const result = verifyBuiltSite({
  distDir,
  repoRoot,
  referenceDir,
  requireReference: cli.requireReference,
  requirePagefind: true,
});

for (const warning of result.warnings) {
  console.warn(`WARNING: ${warning}`);
}

if (result.errors.length > 0) {
  console.error('Built-site and repository contract FAILED:');
  for (const err of result.errors) {
    console.error(`  - ${err}`);
  }
  console.error(
    `Verification FAILED with ${result.errors.length} error(s) and ${result.warnings.length} warning(s).`,
  );
  process.exit(1);
}

console.log(
  `Verification PASSED: ${result.checkedHtmlRoutes.length} route(s), ${result.verifiedImages} image(s), ${result.verifiedFigures} figure(s), ${result.verifiedPrompts} prompt(s), ${result.verifiedLinks} link(s), ${result.warnings.length} warning(s).`,
);
