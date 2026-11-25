// @vitest-environment node
import { satteri } from '@astrojs/markdown-satteri';
import { Window } from 'happy-dom';
import { describe, expect, it } from 'vitest';
import { classifyPromptChip, promptChipsPlugin } from '../src/plugins/prompt-chips.ts';

async function compileMdxSnippet(mdxSource: string): Promise<string> {
  const processor = satteri({
    hastPlugins: [promptChipsPlugin()],
  });
  const renderer = await processor.createMdxRenderer!(
    {
      syntaxHighlight: { type: 'shiki', excludeLangs: ['mermaid'] },
      shikiConfig: { theme: 'github-dark' },
      gfm: true,
      smartypants: true,
    },
    { optimize: false, srcDir: new URL('file:///tmp/') },
  );
  const result = await renderer.process(mdxSource, '/tmp/prompt-test.mdx', {});
  return result.code;
}

describe('classifyPromptChip', () => {
  it('classifies /skill commands, @[file] references, and neutral inline code', () => {
    expect(classifyPromptChip('/edit-silkscreen')).toBe('chip-skill');
    expect(classifyPromptChip('/wayfinder')).toBe('chip-skill');
    expect(classifyPromptChip('/agy-customizations')).toBe('chip-skill');
    expect(classifyPromptChip('@[README.md]')).toBe('chip-file');
    expect(classifyPromptChip('@[DesignSpec.md]')).toBe('chip-file');
    expect(classifyPromptChip('@[silk_layout.json]')).toBe('chip-file');

    expect(classifyPromptChip('DesignSpec.md')).toBeNull();
    expect(classifyPromptChip('/nested/path')).toBeNull();
    expect(classifyPromptChip('@README.md')).toBeNull();
    expect(classifyPromptChip('')).toBeNull();
  });
});

describe('promptChipsPlugin', () => {
  it('adds .chip-skill and .chip-file inside <PromptBlock> while leaving ordinary inline code neutral', async () => {
    const compiled = await compileMdxSnippet(`
<PromptBlock title="Test Prompt">

Please run \`/edit-silkscreen\` on \`@[README.md]\` and inspect \`DesignSpec.md\`.

</PromptBlock>
`);

    expect(compiled).toContain('class: "chip-skill"');
    expect(compiled).toContain('"/edit-silkscreen"');
    expect(compiled).toContain('class: "chip-file"');
    expect(compiled).toContain('"@[README.md]"');
    // Ordinary inline code should not get chip classes
    expect(compiled).not.toMatch(/chip-(?:skill|file)[^}]*DesignSpec\.md/);
  });

  it('leaves /skill and @[file] outside <PromptBlock> and fenced code blocks inside <PromptBlock> neutral', async () => {
    const compiled = await compileMdxSnippet(`
Outside prose: \`/edit-silkscreen\` and \`@[README.md]\`.

<PromptBlock title="Test Prompt">

Use \`/wayfinder\` with \`@[DesignSpec.md]\`.

\`\`\`bash
echo "/not-a-chip @[nope.md]"
\`\`\`

</PromptBlock>
`);

    const skillMatches = compiled.match(/chip-skill/g) ?? [];
    const fileMatches = compiled.match(/chip-file/g) ?? [];
    expect(skillMatches).toHaveLength(1);
    expect(fileMatches).toHaveLength(1);
  });

  it('preserves clean innerText.trim() without extra chrome when rendered in DOM', () => {
    const window = new Window();
    window.document.body.innerHTML = `
      <div class="c-patch-text" id="prompt-1">
        <p>Please update <code class="chip-file">@[README.md]</code> and run <code class="chip-skill">/edit-silkscreen</code> with <code>DesignSpec.md</code>.</p>
      </div>
    `;
    const target = window.document.getElementById('prompt-1') as unknown as HTMLElement;
    expect(target.innerText.trim()).toBe(
      'Please update @[README.md] and run /edit-silkscreen with DesignSpec.md.',
    );
  });
});
