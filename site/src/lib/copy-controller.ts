/** Dependency injection options for testing `initCopyController` deterministically. */
export interface CopyControllerOptions {
  supportsCommandEvent?: boolean;
  writeClipboard?: (text: string) => Promise<void>;
  execCopy?: (text: string, doc: Document) => boolean;
  scheduleFrame?: (callback: FrameRequestCallback) => number;
  resetDelayMs?: number;
}

const DEFAULT_RESET_DELAY_MS = 2000;

/**
 * Fallback copy via temporary readonly `<textarea>` and `document.execCommand('copy')`,
 * preserving and restoring the caller's active focus element.
 */
export function legacyCopy(text: string, doc: Document = document): boolean {
  const previousFocus = doc.activeElement;
  const field = doc.createElement('textarea');
  field.value = text;
  field.setAttribute('readonly', '');
  field.style.cssText = 'position:fixed;inset-block-start:0;opacity:0';
  doc.body.append(field);
  field.select();
  try {
    return typeof doc.execCommand === 'function' ? doc.execCommand('copy') : false;
  } catch {
    return false;
  } finally {
    field.remove();
    if (previousFocus && 'focus' in previousFocus && typeof previousFocus.focus === 'function') {
      (previousFocus as HTMLElement).focus({ preventScroll: true });
    }
  }
}

function resolveStatusTip(button: HTMLButtonElement): HTMLElement | null {
  const sibling = button.nextElementSibling;
  if (sibling instanceof HTMLElement && sibling.getAttribute('role') === 'status') {
    return sibling;
  }
  const wrapTip = button.closest('.prompt-copy-wrap')?.querySelector('[role="status"]');
  return wrapTip instanceof HTMLElement ? wrapTip : null;
}

function readCopyTargetText(target: HTMLElement): string {
  if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) {
    return target.value.trim();
  }
  return (target.innerText ?? target.textContent ?? '').trim();
}

/**
 * Initialize the shared Invoker Commands copy controller for both `<PromptBlock>`
 * and Shiki `.code-console` copy buttons. Returns a cleanup function that aborts listeners.
 */
export function initCopyController(
  doc: Document = document,
  options?: CopyControllerOptions,
): () => void {
  const controller = new AbortController();
  const win = doc.defaultView ?? (typeof window !== 'undefined' ? window : undefined);
  const copyTimers = new WeakMap<HTMLButtonElement, ReturnType<typeof setTimeout>>();
  let lastMessage = '';

  const scheduleFrame =
    options?.scheduleFrame ??
    (win && typeof win.requestAnimationFrame === 'function'
      ? win.requestAnimationFrame.bind(win)
      : (cb: FrameRequestCallback) => setTimeout(() => cb(0), 0) as unknown as number);
  const resetDelayMs = options?.resetDelayMs ?? DEFAULT_RESET_DELAY_MS;

  const writeClipboard =
    options?.writeClipboard ??
    (async (text: string) => {
      if (!win?.navigator?.clipboard?.writeText) {
        throw new Error('Async Clipboard API unavailable');
      }
      await win.navigator.clipboard.writeText(text);
    });

  const execCopy = options?.execCopy ?? ((text: string) => legacyCopy(text, doc));

  function reportCopyFeedback(button: HTMLButtonElement, ok: boolean): void {
    const tip = resolveStatusTip(button);
    if (!tip) {
      return;
    }

    const existingTimer = copyTimers.get(button);
    if (existingTimer !== undefined) {
      clearTimeout(existingTimer);
    }

    button.removeAttribute('data-copied');
    button.removeAttribute('data-failed');

    let message = ok ? 'Copied' : 'Copy failed';
    if (message === lastMessage) {
      message += '\u00A0';
    }
    lastMessage = message;

    tip.textContent = '';
    void button.offsetWidth;
    button.setAttribute(ok ? 'data-copied' : 'data-failed', '');

    scheduleFrame(() => {
      tip.textContent = message;
    });

    copyTimers.set(
      button,
      setTimeout(() => {
        button.removeAttribute('data-copied');
        button.removeAttribute('data-failed');
        tip.textContent = '';
      }, resetDelayMs),
    );
  }

  async function handleCopyCommand(button: HTMLButtonElement, target: HTMLElement): Promise<void> {
    const text = readCopyTargetText(target);
    if (!text) {
      return;
    }
    try {
      await writeClipboard(text);
      reportCopyFeedback(button, true);
    } catch {
      reportCopyFeedback(button, execCopy(text, doc));
    }
  }

  doc.addEventListener(
    'command',
    (event) => {
      const cmdEvent = event as Event & { command?: unknown; source?: unknown };
      if (typeof cmdEvent.command !== 'string' || !cmdEvent.command.startsWith('--copy')) {
        return;
      }
      const button = cmdEvent.source;
      const target = event.target;
      if (button instanceof HTMLElement && button.tagName === 'BUTTON' && target instanceof HTMLElement) {
        void handleCopyCommand(button as HTMLButtonElement, target);
      }
    },
    { capture: true, signal: controller.signal },
  );

  const supportsCommandEvent =
    options?.supportsCommandEvent ?? (win !== undefined && 'CommandEvent' in win);

  if (!supportsCommandEvent) {
    doc.addEventListener(
      'click',
      (event) => {
        if (event.defaultPrevented) {
          return;
        }
        // If invokers-polyfill loaded after init, let its `command` event handle activation.
        if (options?.supportsCommandEvent === undefined && win !== undefined && 'CommandEvent' in win) {
          return;
        }
        const eventTarget = event.target;
        if (!(eventTarget instanceof Element)) {
          return;
        }
        const button = eventTarget.closest<HTMLButtonElement>('button[command^="--copy"]');
        if (!button) {
          return;
        }
        const targetId = button.getAttribute('commandfor');
        const target = targetId ? doc.getElementById(targetId) : null;
        if (target instanceof HTMLElement) {
          void handleCopyCommand(button, target);
        }
      },
      { signal: controller.signal },
    );
  }

  return () => {
    controller.abort();
  };
}
