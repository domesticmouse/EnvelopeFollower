import mdx from '@astrojs/mdx';
import { defineConfig } from 'astro/config';
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
    syntaxHighlight: {
      type: 'shiki',
      excludeLangs: ['mermaid'],
    },
    shikiConfig: {
      theme: 'github-dark',
    },
  },
});
