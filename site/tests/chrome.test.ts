import { describe, expect, it, vi } from 'vitest';
import { initDialogChrome } from '../src/lib/dialog-chrome.ts';
import { parseInlineBackticks } from '../src/lib/inline-code.ts';
import { initTocScrollSpy } from '../src/lib/toc-scrollspy.ts';

describe('parseInlineBackticks', () => {
  it('splits inline backtick code spans while preserving surrounding text', () => {
    expect(
      parseInlineBackticks(
        'Real-World Capacitor Substitutions (`manufacturing/orders/tayda-1000489380.md`)',
      ),
    ).toEqual([
      { kind: 'text', value: 'Real-World Capacitor Substitutions (' },
      { kind: 'code', value: 'manufacturing/orders/tayda-1000489380.md' },
      { kind: 'text', value: ')' },
    ]);
  });

  it('keeps unmatched backticks as plain text', () => {
    expect(parseInlineBackticks('Plain `unclosed text')).toEqual([
      { kind: 'text', value: 'Plain `unclosed text' },
    ]);
  });
});

describe('initDialogChrome', () => {
  it('conditionally loads invokers-polyfill only when commandForElement is unsupported', () => {
    document.body.innerHTML = `
      <button type="button" command="show-modal" commandfor="mobile-nav-drawer" aria-expanded="false">Rack</button>
      <dialog id="mobile-nav-drawer" closedby="any"></dialog>
    `;

    const loaderTrue = vi.fn().mockResolvedValue(undefined);
    initDialogChrome(document, {
      supportsCommandFor: true,
      supportsClosedBy: true,
      loadInvokersPolyfill: loaderTrue,
    });
    expect(loaderTrue).not.toHaveBeenCalled();

    const loaderFalse = vi.fn().mockResolvedValue(undefined);
    initDialogChrome(document, {
      supportsCommandFor: false,
      supportsClosedBy: false,
      loadInvokersPolyfill: loaderFalse,
    });
    expect(loaderFalse).toHaveBeenCalledTimes(1);
  });

  it('opens dialog via fallback, syncs aria-expanded, and supports backdrop light-dismiss', () => {
    document.body.innerHTML = `
      <button type="button" id="menu-btn" command="show-modal" commandfor="mobile-nav-drawer" aria-expanded="false">Rack</button>
      <dialog id="mobile-nav-drawer" closedby="any"></dialog>
    `;

    const btn = document.getElementById('menu-btn') as HTMLButtonElement;
    const dialog = document.getElementById('mobile-nav-drawer') as HTMLDialogElement;
    dialog.getBoundingClientRect = () =>
      ({ left: 0, top: 0, right: 320, bottom: 800, width: 320, height: 800 }) as DOMRect;
    dialog.showModal = () => {
      dialog.setAttribute('open', '');
    };
    dialog.close = (val?: string) => {
      if (val !== undefined) dialog.returnValue = val;
      dialog.removeAttribute('open');
      dialog.dispatchEvent(new Event('close'));
    };

    initDialogChrome(document, {
      supportsCommandFor: false,
      supportsClosedBy: false,
      loadInvokersPolyfill: async () => undefined,
    });

    btn.click();
    expect(dialog.open).toBe(true);
    expect(btn.getAttribute('aria-expanded')).toBe('true');

    // Drag starting inside and ending outside should NOT dismiss
    dialog.dispatchEvent(new PointerEvent('pointerdown', { clientX: 50, clientY: 50 }));
    dialog.dispatchEvent(new PointerEvent('pointerup', { clientX: 400, clientY: 50 }));
    expect(dialog.open).toBe(true);

    // Click starting and ending outside SHOULD dismiss and restore aria-expanded
    dialog.dispatchEvent(new PointerEvent('pointerdown', { clientX: 400, clientY: 50 }));
    dialog.dispatchEvent(new PointerEvent('pointerup', { clientX: 400, clientY: 50 }));
    expect(dialog.open).toBe(false);
    expect(btn.getAttribute('aria-expanded')).toBe('false');
  });
});

describe('initTocScrollSpy', () => {
  it('highlights the intersecting heading link and sets aria-current="true"', () => {
    document.body.innerHTML = `
      <nav class="c-toc-nav">
        <a class="toc-link" href="#summary-metrics">Summary Metrics</a>
        <a class="toc-link" href="#complete-bom">Complete BOM</a>
      </nav>
      <article>
        <h2 id="summary-metrics">Summary Metrics</h2>
        <h2 id="complete-bom">Complete BOM</h2>
      </article>
    `;

    let observerCallback: IntersectionObserverCallback | undefined;
    class MockObserver implements IntersectionObserver {
      readonly root = null;
      readonly rootMargin = '';
      readonly thresholds = [];
      constructor(cb: IntersectionObserverCallback) {
        observerCallback = cb;
      }
      observe = vi.fn();
      unobserve = vi.fn();
      disconnect = vi.fn();
      takeRecords = () => [];
    }

    initTocScrollSpy(document, { ObserverCtor: MockObserver });

    const targetHeading = document.getElementById('complete-bom')!;
    observerCallback?.(
      [{ target: targetHeading, isIntersecting: true } as unknown as IntersectionObserverEntry],
      {} as IntersectionObserver,
    );

    const links = Array.from(document.querySelectorAll<HTMLAnchorElement>('.toc-link'));
    expect(links[0].classList.contains('is-active')).toBe(false);
    expect(links[0].hasAttribute('aria-current')).toBe(false);
    expect(links[1].classList.contains('is-active')).toBe(true);
    expect(links[1].getAttribute('aria-current')).toBe('true');
  });
});
