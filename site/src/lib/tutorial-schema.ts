import { z } from 'astro/zod';

/** Decision-rich YAML frontmatter contract for the `tutorial` MDX Content Collection. */
export const tutorialSchema = z.object({
  title: z.string(),
  navTitle: z.string(),
  description: z.string(),
  section: z.enum(['overview', 'hardware', 'companion-site', 'optional', 'appendix']),
  order: z.number().int().nonnegative(),
  badge: z.string().optional(),
  stage: z.number().int().min(1).max(9).optional(),
  heroMeta: z
    .array(z.object({ label: z.string(), value: z.string() }))
    .min(1)
    .max(4)
    .optional(),
});

export type TutorialFrontmatter = z.infer<typeof tutorialSchema>;
