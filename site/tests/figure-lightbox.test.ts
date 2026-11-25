import { Window } from 'happy-dom';
import { describe, expect, it } from 'vitest';
import { initFigureLightbox } from '../src/lib/figure-lightbox.ts';

function setupLightboxDom() {
  const win = new Window();
  win.document.body.innerHTML = `
    <main>
      <figure class="tutorial-figure">
        <button
          type="button"
          id="trigger-with-caption"
          data-lightbox-trigger
          data-lightbox-src="/EnvelopeFollower/_astro/panel_front.webp"
          data-lightbox-alt="6 HP Matte Black and ENIG Gold Front Panel"
          data-lightbox-caption="Matte Black + ENIG Front Panel"
          aria-label="Zoom image: 6 HP Matte Black and ENIG Gold Front Panel"
        >
          <img src="/EnvelopeFollower/_astro/panel_front.webp" alt="6 HP Matte Black and ENIG Gold Front Panel" width="230" height="985" />
        </button>
        <figcaption>Matte Black + ENIG Front Panel</figcaption>
      </figure>

      <figure class="tutorial-figure">
        <button
          type="button"
          id="trigger-no-caption"
          data-lightbox-trigger
          data-lightbox-src="/EnvelopeFollower/_astro/pcb_front.webp"
          data-lightbox-alt="Main PCB Front Controls F.Cu"
          data-lightbox-caption=""
          aria-label="Zoom image: Main PCB Front Controls F.Cu"
        >
          <img src="/EnvelopeFollower/_astro/pcb_front.webp" alt="Main PCB Front Controls F.Cu" width="230" height="828" />
        </button>
      </figure>
    </main>

    <dialog
      id="figure-lightbox"
      class="figure-lightbox"
      data-figure-lightbox
      data-managed-dialog
      data-pagefind-ignore
      closedby="any"
      aria-labelledby="figure-lightbox-title"
    >
      <div class="figure-lightbox-shell">
        <div class="figure-lightbox-head">
          <span id="figure-lightbox-title" class="figure-lightbox-title" data-figure-lightbox-title>
            Figure Preview
          </span>
          <button type="button" class="figure-lightbox-close" data-figure-lightbox-close aria-label="Close figure preview">
            Close
          </button>
        </div>
        <figure class="figure-lightbox-stage">
          <img class="figure-lightbox-img" data-figure-lightbox-img alt="" />
          <figcaption class="figure-lightbox-caption" data-figure-lightbox-caption hidden></figcaption>
        </figure>
      </div>
    </dialog>
  `;

  const doc = win.document as unknown as Document;
  const dialog = doc.querySelector<HTMLDialogElement>('[data-figure-lightbox]')!;
  dialog.getBoundingClientRect = () =>
    ({ left: 80, top: 60, right: 720, bottom: 660, width: 640, height: 600 }) as DOMRect;
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

describe('initFigureLightbox', () => {
  it('opens modal dialog from trigger, syncs full-res image and caption, and moves focus to close button', () => {
    const { win, doc, dialog } = setupLightboxDom();
    const cleanup = initFigureLightbox({ root: doc });

    try {
      const trigger = doc.getElementById('trigger-with-caption') as HTMLButtonElement;
      const img = dialog.querySelector<HTMLImageElement>('[data-figure-lightbox-img]')!;
      const caption = dialog.querySelector<HTMLElement>('[data-figure-lightbox-caption]')!;
      const closeBtn = dialog.querySelector<HTMLButtonElement>('[data-figure-lightbox-close]')!;

      trigger.focus();
      trigger.click();

      expect(dialog.hasAttribute('open')).toBe(true);
      expect(img.getAttribute('src')).toBe('/EnvelopeFollower/_astro/panel_front.webp');
      expect(img.getAttribute('alt')).toBe('6 HP Matte Black and ENIG Gold Front Panel');
      expect(caption.textContent).toBe('Matte Black + ENIG Front Panel');
      expect(caption.hidden).toBe(false);
      expect(doc.activeElement).toBe(closeBtn);
    } finally {
      cleanup();
      win.close();
    }
  });

  it('dismisses via Close button and Escape, clears image and caption, and restores focus to trigger', () => {
    const { win, doc, dialog } = setupLightboxDom();
    const cleanup = initFigureLightbox({ root: doc });

    try {
      const trigger1 = doc.getElementById('trigger-with-caption') as HTMLButtonElement;
      const trigger2 = doc.getElementById('trigger-no-caption') as HTMLButtonElement;
      const img = dialog.querySelector<HTMLImageElement>('[data-figure-lightbox-img]')!;
      const caption = dialog.querySelector<HTMLElement>('[data-figure-lightbox-caption]')!;
      const closeBtn = dialog.querySelector<HTMLButtonElement>('[data-figure-lightbox-close]')!;

      // Open from trigger1 and dismiss with Close button
      trigger1.focus();
      trigger1.click();
      expect(dialog.hasAttribute('open')).toBe(true);

      dialog.returnValue = 'stale';
      closeBtn.click();
      expect(dialog.hasAttribute('open')).toBe(false);
      expect(dialog.returnValue).toBe('');
      expect(img.hasAttribute('src')).toBe(false);
      expect(img.getAttribute('alt')).toBe('');
      expect(caption.textContent).toBe('');
      expect(caption.hidden).toBe(true);
      expect(doc.activeElement).toBe(trigger1);

      // Open from trigger2 (no caption) and dismiss with Escape key
      trigger2.focus();
      trigger2.click();
      expect(dialog.hasAttribute('open')).toBe(true);
      expect(img.getAttribute('src')).toBe('/EnvelopeFollower/_astro/pcb_front.webp');
      expect(caption.hidden).toBe(true);

      doc.dispatchEvent(
        new win.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }) as unknown as Event,
      );
      expect(dialog.hasAttribute('open')).toBe(false);
      expect(img.hasAttribute('src')).toBe(false);
      expect(doc.activeElement).toBe(trigger2);
    } finally {
      cleanup();
      win.close();
    }
  });

  it('supports Safari backdrop light-dismiss via getBoundingClientRect() and restores focus on dismiss', () => {
    const { win, doc, dialog } = setupLightboxDom();
    const cleanup = initFigureLightbox({ root: doc });

    try {
      const trigger = doc.getElementById('trigger-with-caption') as HTMLButtonElement;
      const triggerImg = trigger.querySelector('img')!;

      // Clicking nested <img> inside trigger button still opens lightbox
      trigger.focus();
      triggerImg.click();
      expect(dialog.hasAttribute('open')).toBe(true);

      // Drag starting inside dialog and ending outside must NOT dismiss
      dialog.dispatchEvent(
        new win.PointerEvent('pointerdown', { clientX: 200, clientY: 200 }) as unknown as Event,
      );
      dialog.dispatchEvent(
        new win.PointerEvent('pointerup', { clientX: 10, clientY: 10 }) as unknown as Event,
      );
      expect(dialog.hasAttribute('open')).toBe(true);

      // Press and release outside dialog bounds MUST dismiss and restore focus
      dialog.dispatchEvent(
        new win.PointerEvent('pointerdown', { clientX: 10, clientY: 10 }) as unknown as Event,
      );
      dialog.dispatchEvent(
        new win.PointerEvent('pointerup', { clientX: 10, clientY: 10 }) as unknown as Event,
      );
      expect(dialog.hasAttribute('open')).toBe(false);
      expect(doc.activeElement).toBe(trigger);

      // Cleanup detaches listeners
      cleanup();
      trigger.click();
      expect(dialog.hasAttribute('open')).toBe(false);
    } finally {
      cleanup();
      win.close();
    }
  });
});
