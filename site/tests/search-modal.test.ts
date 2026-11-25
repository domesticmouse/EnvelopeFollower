import { Window } from 'happy-dom';
import { describe, expect, it, vi } from 'vitest';
import {
  classifyRouteSection,
  initSearchModal,
  type PagefindApi,
} from '../src/lib/search-modal.ts';

function setupSearchDom() {
  const win = new Window();
  win.document.body.innerHTML = `
    <header>
      <button type="button" data-search-trigger aria-label="Search build tutorial">Search ⌘K</button>
    </header>
    <main>
      <input type="text" id="text-field" />
      <textarea id="textarea-field"></textarea>
      <select id="select-field"><option>One</option></select>
      <div id="editable-field" contenteditable="true" tabindex="0">Editable</div>
      <button type="button" id="other-btn">Other</button>
    </main>
    <dialog id="site-search-dialog" data-search-dialog data-managed-dialog closedby="any">
      <div>
        <button type="button" data-search-close aria-label="Close search">Esc</button>
        <input
          type="text"
          inputmode="search"
          data-search-input
          placeholder="Search stages, prompts, tools (e.g. SKiDL, silk_layout.json, /wayfinder, TP7)…"
        />
        <p data-search-status>Type to search</p>
        <ul id="site-search-results" data-search-results role="listbox" aria-label="Search results"></ul>
      </div>
    </dialog>
  `;

  const doc = win.document as unknown as Document;
  const dialog = doc.querySelector<HTMLDialogElement>('[data-search-dialog]')!;
  dialog.getBoundingClientRect = () =>
    ({ left: 100, top: 80, right: 600, bottom: 480, width: 500, height: 400 }) as DOMRect;
  dialog.showModal = () => {
    dialog.setAttribute('open', '');
  };
  dialog.close = (rv?: string) => {
    if (rv !== undefined) dialog.returnValue = rv;
    dialog.removeAttribute('open');
    dialog.dispatchEvent(new win.Event('close') as unknown as Event);
  };

  return { win, doc, dialog };
}

describe('classifyRouteSection', () => {
  it('maps all 5 Build Tutorial curriculum sections from canonical and prefixed URLs', () => {
    expect(classifyRouteSection('/EnvelopeFollower/')).toEqual({
      key: 'overview',
      label: 'Overview',
    });
    expect(
      classifyRouteSection(
        'https://domesticmouse.github.io/EnvelopeFollower/stages/04-skidl-and-schematic/#netlist',
      ),
    ).toEqual({
      key: 'hardware',
      label: 'Hardware Build',
    });
    expect(classifyRouteSection('/EnvelopeFollower/stages/08-wayfinder-site-planning/')).toEqual({
      key: 'companion-site',
      label: 'Companion Site',
    });
    expect(classifyRouteSection('/EnvelopeFollower/optional/ac-dc-input-coupling/')).toEqual({
      key: 'optional',
      label: 'Optional',
    });
    expect(classifyRouteSection('/appendix/engineering-sign-off-checklist/')).toEqual({
      key: 'appendix',
      label: 'Appendix',
    });
  });
});

describe('initSearchModal — triggers, lazy load, fallback & focus restoration', () => {
  it('lazy-loads Pagefind only on first open, supports Cmd+K, Ctrl+K, and /, and restores focus on close', async () => {
    const { win, doc, dialog } = setupSearchDom();
    const searchMock = vi.fn(async () => ({ results: [] }));
    const loadPagefind = vi.fn<() => Promise<PagefindApi>>(async () => ({
      init: vi.fn(async () => {}),
      search: searchMock,
    }));

    const cleanup = initSearchModal({ root: doc, loadPagefind, debounceMs: 0 });
    try {
      expect(loadPagefind).not.toHaveBeenCalled();

      // Open via header trigger and restore focus to it on close
      const trigger = doc.querySelector<HTMLButtonElement>('[data-search-trigger]')!;
      trigger.focus();
      trigger.click();
      await Promise.resolve();
      await Promise.resolve();

      expect(dialog.hasAttribute('open')).toBe(true);
      expect(loadPagefind).toHaveBeenCalledTimes(1);
      expect(doc.activeElement).toBe(doc.querySelector('[data-search-input]'));

      dialog.close();
      expect(dialog.hasAttribute('open')).toBe(false);
      expect(doc.activeElement).toBe(trigger);

      // Re-open via Ctrl+K (must NOT call loadPagefind a second time)
      const otherBtn = doc.getElementById('other-btn') as HTMLButtonElement;
      otherBtn.focus();
      doc.dispatchEvent(
        new win.KeyboardEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true }) as unknown as Event,
      );
      await Promise.resolve();

      expect(dialog.hasAttribute('open')).toBe(true);
      expect(loadPagefind).toHaveBeenCalledTimes(1);

      // Close via close button and verify focus restored to otherBtn
      doc.querySelector<HTMLButtonElement>('[data-search-close]')!.click();
      expect(dialog.hasAttribute('open')).toBe(false);
      expect(doc.activeElement).toBe(otherBtn);

      // Open via '/' outside editable fields
      doc.dispatchEvent(
        new win.KeyboardEvent('keydown', { key: '/', bubbles: true }) as unknown as Event,
      );
      await Promise.resolve();
      expect(dialog.hasAttribute('open')).toBe(true);

      // Backdrop click outside dialog closes it
      dialog.dispatchEvent(
        new win.PointerEvent('pointerdown', { clientX: 10, clientY: 10 }) as unknown as Event,
      );
      dialog.dispatchEvent(
        new win.PointerEvent('pointerup', { clientX: 10, clientY: 10 }) as unknown as Event,
      );
      expect(dialog.hasAttribute('open')).toBe(false);
    } finally {
      cleanup();
      win.close();
    }
  });

  it('ignores "/" shortcut when focus is inside input, textarea, select, or contenteditable', () => {
    const { win, doc, dialog } = setupSearchDom();
    const loadPagefind = vi.fn<() => Promise<PagefindApi>>(async () => ({
      search: async () => ({ results: [] }),
    }));

    const cleanup = initSearchModal({ root: doc, loadPagefind });
    try {
      const editableTargets = [
        doc.getElementById('text-field')!,
        doc.getElementById('textarea-field')!,
        doc.getElementById('select-field')!,
        doc.getElementById('editable-field')!,
      ];

      for (const el of editableTargets) {
        el.focus();
        el.dispatchEvent(
          new win.KeyboardEvent('keydown', { key: '/', bubbles: true }) as unknown as Event,
        );
        expect(dialog.hasAttribute('open')).toBe(false);
      }

      expect(loadPagefind).not.toHaveBeenCalled();
    } finally {
      cleanup();
      win.close();
    }
  });

  it('displays a clear dev-mode fallback message when Pagefind bundle is absent', async () => {
    const { win, doc } = setupSearchDom();
    const loadPagefind = vi.fn<() => Promise<PagefindApi>>(async () => {
      throw new Error('Failed to fetch /EnvelopeFollower/pagefind/pagefind.js');
    });

    const cleanup = initSearchModal({ root: doc, loadPagefind, debounceMs: 0 });
    try {
      doc.querySelector<HTMLButtonElement>('[data-search-trigger]')!.click();
      await Promise.resolve();
      await Promise.resolve();

      const status = doc.querySelector('[data-search-status]')?.textContent ?? '';
      expect(status).toContain('npm run build');
      expect(status.toLowerCase()).toContain('dev');
    } finally {
      cleanup();
      win.close();
    }
  });
});

describe('initSearchModal — debounce, safe <mark> excerpts & keyboard navigation', () => {
  it('debounces search queries by 120 ms by default', async () => {
    vi.useFakeTimers();
    const { win, doc } = setupSearchDom();
    const searchMock = vi.fn(async () => ({ results: [] }));
    const loadPagefind = vi.fn<() => Promise<PagefindApi>>(async () => ({
      search: searchMock,
    }));

    const cleanup = initSearchModal({ root: doc, loadPagefind });
    try {
      doc.querySelector<HTMLButtonElement>('[data-search-trigger]')!.click();
      await vi.advanceTimersByTimeAsync(0);

      const input = doc.querySelector<HTMLInputElement>('[data-search-input]')!;
      input.value = 'SK';
      input.dispatchEvent(new win.Event('input', { bubbles: true }) as unknown as Event);
      await vi.advanceTimersByTimeAsync(80);
      expect(searchMock).not.toHaveBeenCalled();

      input.value = 'SKiDL';
      input.dispatchEvent(new win.Event('input', { bubbles: true }) as unknown as Event);
      await vi.advanceTimersByTimeAsync(119);
      expect(searchMock).not.toHaveBeenCalled();

      await vi.advanceTimersByTimeAsync(1);
      expect(searchMock).toHaveBeenCalledTimes(1);
      expect(searchMock).toHaveBeenCalledWith('SKiDL');
    } finally {
      cleanup();
      win.close();
      vi.useRealTimers();
    }
  });

  it('renders section badges and safe DOM-node <mark> excerpts without HTML injection, and supports ↑/↓/Enter navigation', async () => {
    const { win, doc, dialog } = setupSearchDom();
    const navigate = vi.fn<(url: string) => void>();

    const loadPagefind = vi.fn<() => Promise<PagefindApi>>(async () => ({
      search: async (q: string) => {
        if (!q.includes('SKiDL')) {
          return { results: [] };
        }
        return {
          results: [
            {
              data: async () => ({
                url: '/EnvelopeFollower/stages/04-skidl-and-schematic/',
                meta: { title: 'Stage 04: SKiDL & Schematic' },
                excerpt:
                  'Run <mark onclick="alert(1)">SKiDL</mark> check<img src=x onerror=alert(1)><script>alert(2)</script> for &lt;PromptBlock&gt;.',
              }),
            },
            {
              data: async () => ({
                url: '/EnvelopeFollower/stages/08-wayfinder-site-planning/',
                meta: { title: 'Stage 08: Wayfinder Site Planning' },
                excerpt: 'Invoke <mark>/wayfinder</mark> after <mark>SKiDL</mark> sign-off.',
              }),
            },
            {
              data: async () => ({
                url: '/EnvelopeFollower/appendix/netlist-and-bom/',
                meta: { title: 'Netlist, BOM & Silkscreen' },
                excerpt: '<mark>TP7</mark> test point verification.',
              }),
            },
          ],
        };
      },
    }));

    const cleanup = initSearchModal({ root: doc, loadPagefind, debounceMs: 0, navigate });
    try {
      doc.querySelector<HTMLButtonElement>('[data-search-trigger]')!.click();
      await Promise.resolve();
      await Promise.resolve();

      const input = doc.querySelector<HTMLInputElement>('[data-search-input]')!;
      input.value = 'SKiDL';
      input.dispatchEvent(new win.Event('input', { bubbles: true }) as unknown as Event);
      await new Promise((r) => setTimeout(r, 15));

      const items = [...doc.querySelectorAll<HTMLElement>('[data-search-result]')];
      expect(items).toHaveLength(3);
      expect(items[0]?.getAttribute('aria-selected')).toBe('true');
      expect(items[1]?.getAttribute('aria-selected')).toBe('false');

      // Badges across sections
      const badges = [...doc.querySelectorAll('[data-search-results] .search-result-badge')].map(
        (el) => el.textContent,
      );
      expect(badges).toEqual(['Hardware Build', 'Companion Site', 'Appendix']);

      // XSS payloads stripped / never parsed as HTML; <mark> has no attributes
      expect(doc.querySelector('[data-search-results] img')).toBeNull();
      expect(doc.querySelector('[data-search-results] script')).toBeNull();
      const marks = [...doc.querySelectorAll('[data-search-results] mark')];
      expect(marks).toHaveLength(4);
      expect(marks[0]?.textContent).toBe('SKiDL');
      expect(marks[0]?.hasAttribute('onclick')).toBe(false);
      expect(items[0]?.textContent).toContain('<PromptBlock>');

      // ArrowUp wraps from index 0 to last item (index 2), ArrowDown wraps back to 0, then ArrowDown -> 1
      input.dispatchEvent(
        new win.KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true }) as unknown as Event,
      );
      expect(items[2]?.getAttribute('aria-selected')).toBe('true');
      input.dispatchEvent(
        new win.KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }) as unknown as Event,
      );
      expect(items[0]?.getAttribute('aria-selected')).toBe('true');
      input.dispatchEvent(
        new win.KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }) as unknown as Event,
      );
      expect(items[1]?.getAttribute('aria-selected')).toBe('true');

      // Enter closes dialog and navigates to selected result
      input.dispatchEvent(
        new win.KeyboardEvent('keydown', { key: 'Enter', bubbles: true }) as unknown as Event,
      );
      expect(dialog.hasAttribute('open')).toBe(false);
      expect(navigate).toHaveBeenCalledWith(
        '/EnvelopeFollower/stages/08-wayfinder-site-planning/',
      );
    } finally {
      cleanup();
      win.close();
    }
  });
});
