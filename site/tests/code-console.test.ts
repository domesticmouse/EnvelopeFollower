// @vitest-environment node
import { satteri } from '@astrojs/markdown-satteri';
import { describe, expect, it } from 'vitest';
import { codeConsolePlugin } from '../src/plugins/code-console.ts';

async function compileMdxWithConsole(mdxSource: string): Promise<string> {
  const processor = satteri({
    hastPlugins: [codeConsolePlugin()],
  });
  const renderer = await processor.createMdxRenderer!(
    {
      syntaxHighlight: { type: 'shiki', excludeLangs: ['mermaid'] },
      shikiConfig: { theme: 'github-dark', langAlias: { gitignore: 'plaintext' } },
      gfm: true,
      smartypants: true,
    },
    { optimize: false, srcDir: new URL('file:///tmp/') },
  );
  const result = await renderer.process(mdxSource, '/tmp/code-console-test.mdx', {});
  return result.code;
}

describe('codeConsolePlugin', () => {
  it.each(['csv', 'bash', 'python', 'json', 'yaml', 'gitignore', 'text'])(
    'wraps %s Shiki code blocks with console header, copy button, and tabindex="0" well',
    async (lang) => {
      const compiled = await compileMdxWithConsole(`\`\`\`${lang}\nhello\n\`\`\`\n`);

      expect(compiled).toContain('class: "code-console"');
      expect(compiled).toContain('class: "code-console-head"');
      expect(compiled).toContain('"data-pagefind-ignore": ""');
      expect(compiled).toContain(`children: "${lang.toUpperCase()}"`);
      expect(compiled).toContain('command: "--copy"');
      expect(compiled).toContain('commandfor: "code-well-1"');
      expect(compiled).toContain(`"aria-label": "Copy ${lang} code"`);
      expect(compiled).toContain('role: "status"');
      expect(compiled).toContain('tabindex: "0"');
      expect(compiled).toContain('id: "code-well-1"');
    },
  );

  it('leaves mermaid code blocks unwrapped and preserves MDX JSX nodes such as <Disclosure>', async () => {
    const compiled = await compileMdxWithConsole(`
<Disclosure title="Preview \`jlcpcb_bom.csv\`">

\`\`\`csv
Designator,Quantity
R4,14
\`\`\`

</Disclosure>

\`\`\`mermaid
flowchart TD
  A --> B
\`\`\`
`);

    expect(compiled).toContain('_missingMdxReference("Disclosure", true)');
    expect(compiled).toContain('children: "CSV"');
    expect(compiled).toContain('"aria-label": "Copy csv code"');
    expect(compiled).toContain('language-mermaid');
    expect(compiled).not.toContain('Copy mermaid code');
    // Only the CSV block should be wrapped in .code-console
    expect(compiled.match(/class: "code-console"/g)).toHaveLength(1);
  });

  it('assigns sequential unique code-well IDs across multiple blocks in one document', async () => {
    const compiled = await compileMdxWithConsole(`
\`\`\`bash
echo 1
\`\`\`

\`\`\`python
print(2)
\`\`\`
`);

    expect(compiled).toContain('commandfor: "code-well-1"');
    expect(compiled).toContain('id: "code-well-1"');
    expect(compiled).toContain('commandfor: "code-well-2"');
    expect(compiled).toContain('id: "code-well-2"');
  });
});
