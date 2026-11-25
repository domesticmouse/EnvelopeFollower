/** Segment produced by splitting a plain title string on inline backtick code spans. */
export type InlineSegment =
  | { kind: 'text'; value: string }
  | { kind: 'code'; value: string };

/** Parse inline `backtick` code spans into safe text/code segments without HTML interpolation. */
export function parseInlineBackticks(input: string): InlineSegment[] {
  const segments: InlineSegment[] = [];
  const pattern = /`([^`]+)`/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(input)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ kind: 'text', value: input.slice(lastIndex, match.index) });
    }
    segments.push({ kind: 'code', value: match[1] ?? '' });
    lastIndex = pattern.lastIndex;
  }

  if (lastIndex < input.length) {
    segments.push({ kind: 'text', value: input.slice(lastIndex) });
  }

  return segments.length > 0 ? segments : [{ kind: 'text', value: input }];
}
