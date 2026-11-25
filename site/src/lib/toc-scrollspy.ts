/** Options for dependency-injecting IntersectionObserver in tests. */
export interface TocScrollSpyOptions {
  ObserverCtor?: typeof IntersectionObserver;
}

/**
 * Observe h2/h3 headings referenced by the right-rail TOC and highlight the active link
 * via `.is-active` and `aria-current="true"`.
 */
export function initTocScrollSpy(
  doc: Document = document,
  options?: TocScrollSpyOptions,
): (() => void) | undefined {
  const Observer =
    options?.ObserverCtor ??
    (typeof IntersectionObserver !== 'undefined' ? IntersectionObserver : undefined);
  if (!Observer) {
    return undefined;
  }

  const links = Array.from(doc.querySelectorAll<HTMLAnchorElement>('.c-toc-nav .toc-link'));
  if (links.length === 0) {
    return undefined;
  }

  const linkById = new Map<string, HTMLAnchorElement>();
  const headings: Element[] = [];

  for (const link of links) {
    const href = link.getAttribute('href') ?? '';
    if (!href.startsWith('#')) {
      continue;
    }
    const id = href.slice(1);
    const target = doc.getElementById(id);
    if (target) {
      linkById.set(id, link);
      headings.push(target);
    }
  }

  if (headings.length === 0) {
    return undefined;
  }

  const setActive = (activeId: string): void => {
    for (const link of links) {
      const matches = link.getAttribute('href') === `#${activeId}`;
      link.classList.toggle('is-active', matches);
      if (matches) {
        link.setAttribute('aria-current', 'true');
      } else {
        link.removeAttribute('aria-current');
      }
    }
  };

  setActive(headings[0].id);

  const observer = new Observer(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting && entry.target.id) {
          setActive(entry.target.id);
          break;
        }
      }
    },
    { rootMargin: '-20% 0px -65% 0px', threshold: 0 },
  );

  for (const heading of headings) {
    observer.observe(heading);
  }

  return () => observer.disconnect();
}
