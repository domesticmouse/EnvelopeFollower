import { satteri } from '@astrojs/markdown-satteri';
import mdx from '@astrojs/mdx';
import { defineConfig } from 'astro/config';
import { codeConsolePlugin } from './src/plugins/code-console.ts';
import { promptChipsPlugin } from './src/plugins/prompt-chips.ts';
import { SITE_BASE, SITE_ORIGIN } from './src/lib/routes.ts';

export default defineConfig({
  site: SITE_ORIGIN,
  base: SITE_BASE,
  trailingSlash: 'always',
  build: {
    format: 'directory',
  },
  integrations: [mdx()],
  markdown: {
    processor: satteri({
      hastPlugins: [promptChipsPlugin(), codeConsolePlugin()],
    }),
    syntaxHighlight: {
      type: 'shiki',
      excludeLangs: ['mermaid'],
    },
    shikiConfig: {
      theme: 'github-dark',
      langAlias: {
        gitignore: 'plaintext',
      },
    },
  },
});
