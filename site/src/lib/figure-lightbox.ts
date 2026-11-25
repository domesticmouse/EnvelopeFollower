import { showModalSafe, wireBackdropLightDismiss } from './dialog-chrome.ts';

/** Options for hydrating the shared native `<dialog>` figure lightbox. */
export interface FigureLightboxOptions {
  root?: Document;
}

/**
 * Hydrate the shared page-level `<dialog data-figure-lightbox closedby="any">`
 * to preview zoomable `<Figure>` triggers at full resolution.
 */
export function initFigureLightbox(options: FigureLightboxOptions = {}): () => void {
  const root = options.root ?? document;
  const dialog = root.querySelector<HTMLDialogElement>('[data-figure-lightbox]');
  if (!dialog) {
    return () => {};
  }

  const img = dialog.querySelector<HTMLImageElement>('[data-figure-lightbox-img]');
  const captionEl = dialog.querySelector<HTMLElement>('[data-figure-lightbox-caption]');
  const closeBtn = dialog.querySelector<HTMLButtonElement>('[data-figure-lightbox-close]');
  if (!img || !captionEl) {
    return () => {};
  }

  const controller = new AbortController();
  const { signal } = controller;
  let activeTrigger: HTMLElement | null = null;

  wireBackdropLightDismiss(dialog, signal);

  dialog.addEventListener(
    'close',
    () => {
      dialog.returnValue = '';
      img.removeAttribute('src');
      img.setAttribute('alt', '');
      captionEl.textContent = '';
      captionEl.hidden = true;
      if (activeTrigger && activeTrigger.isConnected) {
        activeTrigger.focus();
      }
      activeTrigger = null;
    },
    { signal },
  );

  closeBtn?.addEventListener('click', () => dialog.close(), { signal });

  root.addEventListener(
    'keydown',
    (event) => {
      if (
        event.key === 'Escape' &&
        !event.defaultPrevented &&
        (dialog.open || dialog.hasAttribute('open'))
      ) {
        event.preventDefault();
        dialog.close();
      }
    },
    { signal },
  );

  root.addEventListener(
    'click',
    (event) => {
      const target = event.target;
      if (!target || typeof (target as Element).closest !== 'function') {
        return;
      }
      const trigger = (target as Element).closest<HTMLElement>('[data-lightbox-trigger]');
      if (!trigger) {
        return;
      }

      const src = trigger.getAttribute('data-lightbox-src');
      if (!src) {
        return;
      }

      const alt = trigger.getAttribute('data-lightbox-alt') ?? '';
      const caption = (trigger.getAttribute('data-lightbox-caption') ?? '').trim();

      activeTrigger = typeof trigger.focus === 'function' ? trigger : null;

      img.setAttribute('src', src);
      img.setAttribute('alt', alt);

      if (caption) {
        captionEl.textContent = caption;
        captionEl.hidden = false;
      } else {
        captionEl.textContent = '';
        captionEl.hidden = true;
      }

      showModalSafe(dialog);
      closeBtn?.focus();
    },
    { signal },
  );

  return () => {
    controller.abort();
  };
}
