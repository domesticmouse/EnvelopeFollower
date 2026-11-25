/** Shared SVG icon geometry for Copy / Check / Error states on Copy buttons. */
export const COPY_ICON_DEFS = [
  {
    className: 'prompt-copy-icon prompt-icon-copy',
    pathD:
      'M19 21H8V7h11m0-2H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2m-3-4H4a2 2 0 0 0-2 2v14h2V3h12z',
  },
  {
    className: 'prompt-copy-icon prompt-icon-check',
    pathD: 'M21 7 9 19l-5.5-5.5 1.41-1.41L9 16.17 19.59 5.59z',
  },
  {
    className: 'prompt-copy-icon prompt-icon-error',
    pathD: 'M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2m1 15h-2v-2h2zm0-4h-2V7h2z',
  },
] as const;
