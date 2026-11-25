import mdx from '@astrojs/mdx';
import { unified } from '@astrojs/markdown-remark';
import { defineConfig } from 'astro/config';
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';
import { SITE_BASE, SITE_ORIGIN } from './src/lib/routes.ts';
import { rehypeMermaidBlocks } from './src/plugins/rehype-mermaid.ts';
import { remarkPromoteDoubleDollarMath } from './src/plugins/remark-double-dollar-math.ts';

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
    processor: unified({
      gfm: true,
      remarkPlugins: [remarkMath, remarkPromoteDoubleDollarMath],
      rehypePlugins: [[rehypeKatex, { strict: false }], rehypeMermaidBlocks],
    }),
  },
});
