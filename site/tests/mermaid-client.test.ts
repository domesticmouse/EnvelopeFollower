import { describe, expect, it, vi } from 'vitest';
import { Window } from 'happy-dom';
import {
  MERMAID_THEME_CONFIG,
  hydrateMermaidDiagrams,
  type MermaidRuntime,
} from '../src/lib/mermaid-client.ts';

describe('lazy dark-only client-side Mermaid hydration module', () => {
  it('never loads the mermaid bundle when the document contains zero .mermaid blocks', async () => {
    const win = new Window();
    const doc = win.document as unknown as Document;
    doc.body.innerHTML = `<main><h1>No diagrams here</h1><pre><code>{"hp":6}</code></pre></main>`;

    const loadMermaid = vi.fn<() => Promise<MermaidRuntime>>();
    const rendered = await hydrateMermaidDiagrams({ root: doc, loadMermaid });

    expect(rendered).toBe(0);
    expect(loadMermaid).not.toHaveBeenCalled();
    win.close();
  });

  it('lazy-loads mermaid once, configures Matte Black + ENIG Gold strict theme, renders SVGs, and is idempotent', async () => {
    const win = new Window();
    const doc = win.document as unknown as Document;
    doc.body.innerHTML = `
      <figure class="mermaid-card" data-pagefind-ignore="true">
        <div class="mermaid-scroll" tabindex="0" role="region" aria-label="Signal flow diagram">
          <pre class="mermaid">flowchart LR\n  IN --&gt; OUT</pre>
        </div>
      </figure>
      <figure class="mermaid-card" data-pagefind-ignore="true">
        <div class="mermaid-scroll" tabindex="0" role="region" aria-label="Signal flow diagram">
          <pre class="mermaid">flowchart LR\n  SLEW --&gt; ENV</pre>
        </div>
      </figure>
    `;

    const initialize = vi.fn();
    const render = vi.fn(async (id: string, source: string) => ({
      svg: `<svg data-id="${id}" data-src-len="${source.length}"><rect /></svg>`,
    }));
    const loadMermaid = vi.fn(async () => ({ initialize, render }));

    const firstCount = await hydrateMermaidDiagrams({ root: doc, loadMermaid });
    expect(firstCount).toBe(2);
    expect(loadMermaid).toHaveBeenCalledTimes(1);
    expect(initialize).toHaveBeenCalledTimes(1);
    expect(initialize).toHaveBeenCalledWith(
      expect.objectContaining({
        startOnLoad: false,
        theme: 'base',
        securityLevel: 'strict',
        themeVariables: expect.objectContaining({
          darkMode: true,
          background: '#090a0d',
          mainBkg: '#1b1d22',
          secondaryColor: '#141518',
          primaryBorderColor: '#d8b154',
          lineColor: '#d8b154',
          primaryTextColor: '#f4f5f7',
          textColor: '#e8eaef',
        }),
      }),
    );
    expect(MERMAID_THEME_CONFIG.theme).toBe('base');
    expect(MERMAID_THEME_CONFIG.securityLevel).toBe('strict');

    expect(render).toHaveBeenCalledTimes(2);
    expect(render.mock.calls[0]?.[1]).toContain('IN --> OUT');
    expect(render.mock.calls[1]?.[1]).toContain('SLEW --> ENV');

    const renderedNodes = doc.querySelectorAll('.mermaid-svg[data-mermaid-rendered="true"] svg');
    expect(renderedNodes).toHaveLength(2);
    expect(renderedNodes[0]?.parentElement?.getAttribute('role')).toBe('img');
    expect(renderedNodes[0]?.parentElement?.getAttribute('aria-label')).toBeTruthy();

    // Second pass must be a no-op without reloading mermaid
    const secondCount = await hydrateMermaidDiagrams({ root: doc, loadMermaid });
    expect(secondCount).toBe(0);
    expect(loadMermaid).toHaveBeenCalledTimes(1);
    expect(render).toHaveBeenCalledTimes(2);

    win.close();
  });

  it('provides an accessible error fallback while preserving readable source if rendering fails', async () => {
    const win = new Window();
    const doc = win.document as unknown as Document;
    doc.body.innerHTML = `
      <figure class="mermaid-card" data-pagefind-ignore="true">
        <div class="mermaid-scroll" tabindex="0" role="region" aria-label="Signal flow diagram">
          <pre class="mermaid">flowchart LR\n  BROKEN --&gt;</pre>
        </div>
      </figure>
    `;

    const initialize = vi.fn();
    const render = vi.fn(async () => {
      throw new Error('Syntax error in diagram');
    });
    const loadMermaid = vi.fn(async () => ({ initialize, render }));

    const rendered = await hydrateMermaidDiagrams({ root: doc, loadMermaid });
    expect(rendered).toBe(0);

    const pre = doc.querySelector('pre.mermaid');
    expect(pre?.getAttribute('data-mermaid-error')).toBe('true');
    expect(pre?.textContent).toContain('BROKEN -->');

    const fallbackNote = doc.querySelector('.mermaid-error-note[role="status"]');
    expect(fallbackNote?.textContent).toContain('Diagram preview unavailable');

    win.close();
  });
});
