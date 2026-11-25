import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { tutorialSchema } from './lib/tutorial-schema.ts';

const tutorial = defineCollection({
  loader: glob({
    pattern: '**/*.mdx',
    base: './src/content/tutorial',
  }),
  schema: tutorialSchema,
});

export const collections = {
  tutorial,
};
