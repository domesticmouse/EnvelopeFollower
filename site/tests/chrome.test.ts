import { describe, expect, it, vi } from 'vitest';
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
