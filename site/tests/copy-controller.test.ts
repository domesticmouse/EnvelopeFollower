import { afterEach, describe, expect, it, vi } from 'vitest';
import { initCopyController, legacyCopy } from '../src/lib/copy-controller.ts';

function flushMicrotasks(): Promise<void> {
  return Promise.resolve().then(() => Promise.resolve());
}

describe('initCopyController', () => {
  let cleanup: (() => void) | undefined;

  afterEach(() => {
    cleanup?.();
    cleanup = undefined;
    document.body.innerHTML = '';
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('handles native Invoker command="--copy" events, writes trimmed innerText, sets data-copied, and updates role="status" without disabling the button', async () => {
    document.body.innerHTML = `
      <span class="prompt-copy-wrap">
        <button type="button" id="btn-1" class="prompt-copy-btn" command="--copy" commandfor="prompt-1" aria-label="Copy Prompt"><span>Copy</span></button>
        <span class="prompt-copy-tip" role="status"></span>
      </span>
      <div class="c-patch-text" id="prompt-1">
        <p>Update <code class="chip-file">@[README.md]</code> via <code class="chip-skill">/edit-silkscreen</code>.</p>
      </div>
    `;

    const writeClipboard = vi.fn().mockResolvedValue(undefined);
    cleanup = initCopyController(document, {
      supportsCommandEvent: true,
      writeClipboard,
      scheduleFrame: (cb) => {
        cb(0);
        return 0;
      },
    });

    const btn = document.getElementById('btn-1') as HTMLButtonElement;
    const target = document.getElementById('prompt-1') as HTMLElement;
    const tip = btn.nextElementSibling as HTMLElement;

    const cmdEvent = Object.assign(new Event('command'), {
      command: '--copy',
      source: btn,
    });
    target.dispatchEvent(cmdEvent);
    await flushMicrotasks();

    expect(writeClipboard).toHaveBeenCalledTimes(1);
    expect(writeClipboard).toHaveBeenCalledWith('Update @[README.md] via /edit-silkscreen.');
    expect(btn.hasAttribute('data-copied')).toBe(true);
    expect(btn.hasAttribute('data-failed')).toBe(false);
    expect(btn.disabled).toBe(false);
    expect(tip.textContent).toBe('Copied');

    // Native command mode must NOT register a duplicate click fallback
    btn.click();
    await flushMicrotasks();
    expect(writeClipboard).toHaveBeenCalledTimes(1);
  });

  it('activates click fallback when CommandEvent is unavailable and copies Shiki code-console targets', async () => {
    document.body.innerHTML = `
      <div class="code-console">
        <div class="code-console-head" data-pagefind-ignore>
          <span class="code-console-lang">BASH</span>
          <span class="prompt-copy-wrap">
            <button type="button" id="code-btn" class="prompt-copy-btn code-copy-btn" command="--copy" commandfor="code-well-1" aria-label="Copy bash code"><span>Copy</span></button>
            <span class="prompt-copy-tip" role="status"></span>
          </span>
        </div>
        <pre id="code-well-1" tabindex="0"><code>echo "hello world"</code></pre>
      </div>
    `;

    const writeClipboard = vi.fn().mockResolvedValue(undefined);
    cleanup = initCopyController(document, {
      supportsCommandEvent: false,
      writeClipboard,
      scheduleFrame: (cb) => {
        cb(0);
        return 0;
      },
    });

    const btn = document.getElementById('code-btn') as HTMLButtonElement;
    const labelSpan = btn.querySelector('span') as HTMLSpanElement;
    const tip = btn.nextElementSibling as HTMLElement;

    labelSpan.click();
    await flushMicrotasks();

    expect(writeClipboard).toHaveBeenCalledTimes(1);
    expect(writeClipboard).toHaveBeenCalledWith('echo "hello world"');
    expect(btn.hasAttribute('data-copied')).toBe(true);
    expect(tip.textContent).toBe('Copied');
  });

  it('falls back to legacyCopy when async clipboard rejects and reports Copy failed if both fail', async () => {
    document.body.innerHTML = `
      <span class="prompt-copy-wrap">
        <button type="button" id="btn-legacy" class="prompt-copy-btn" command="--copy" commandfor="code-well-2" aria-label="Copy text code">Copy</button>
        <span class="prompt-copy-tip" role="status"></span>
      </span>
      <pre id="code-well-2" tabindex="0"><code>*.kicad_prl</code></pre>
    `;

    const writeClipboard = vi.fn().mockRejectedValue(new Error('Clipboard denied'));
    const execMock = vi.fn().mockReturnValueOnce(true).mockReturnValueOnce(false);
    document.execCommand = execMock;

    cleanup = initCopyController(document, {
      supportsCommandEvent: false,
      writeClipboard,
      scheduleFrame: (cb) => {
        cb(0);
        return 0;
      },
    });

    const btn = document.getElementById('btn-legacy') as HTMLButtonElement;
    const tip = btn.nextElementSibling as HTMLElement;
    btn.focus();

    btn.click();
    await flushMicrotasks();

    expect(execMock).toHaveBeenCalledWith('copy');
    expect(btn.hasAttribute('data-copied')).toBe(true);
    expect(btn.hasAttribute('data-failed')).toBe(false);
    expect(tip.textContent).toBe('Copied');
    expect(document.activeElement).toBe(btn);

    btn.click();
    await flushMicrotasks();

    expect(btn.hasAttribute('data-copied')).toBe(false);
    expect(btn.hasAttribute('data-failed')).toBe(true);
    expect(tip.textContent).toBe('Copy failed');
  });

  it('deduplicates consecutive VoiceOver live-region announcements with NBSP and resets after 2000ms', async () => {
    vi.useFakeTimers();

    document.body.innerHTML = `
      <span class="prompt-copy-wrap">
        <button type="button" id="btn-vo" class="prompt-copy-btn" command="--copy" commandfor="prompt-vo" aria-label="Copy Prompt">Copy</button>
        <span class="prompt-copy-tip" role="status"></span>
      </span>
      <div class="c-patch-text" id="prompt-vo"><p>Repeat me</p></div>
    `;

    const writeClipboard = vi.fn().mockResolvedValue(undefined);
    cleanup = initCopyController(document, {
      supportsCommandEvent: false,
      writeClipboard,
      scheduleFrame: (cb) => {
        cb(0);
        return 0;
      },
    });

    const btn = document.getElementById('btn-vo') as HTMLButtonElement;
    const tip = btn.nextElementSibling as HTMLElement;

    // 1st copy -> "Copied"
    btn.click();
    await flushMicrotasks();
    expect(tip.textContent).toBe('Copied');
    expect(btn.hasAttribute('data-copied')).toBe(true);

    // 2nd repeat copy after 1000ms -> "Copied\u00A0" and resets the 2000ms timer
    vi.advanceTimersByTime(1000);
    btn.click();
    await flushMicrotasks();
    expect(tip.textContent).toBe('Copied\u00A0');

    // At +1500ms (total 2500ms from 1st, 1500ms from 2nd), feedback must still be visible
    vi.advanceTimersByTime(1500);
    expect(btn.hasAttribute('data-copied')).toBe(true);
    expect(tip.textContent).toBe('Copied\u00A0');

    // At +500ms (2000ms from 2nd), feedback clears
    vi.advanceTimersByTime(500);
    expect(btn.hasAttribute('data-copied')).toBe(false);
    expect(tip.textContent).toBe('');

    // 3rd copy -> alternates back to "Copied"
    btn.click();
    await flushMicrotasks();
    expect(tip.textContent).toBe('Copied');
  });

  it('legacyCopy cleans up its temporary textarea even if execCommand throws', () => {
    document.execCommand = vi.fn(() => {
      throw new Error('execCommand blocked');
    });
    expect(legacyCopy('hello', document)).toBe(false);
    expect(document.querySelectorAll('textarea')).toHaveLength(0);
  });
});
