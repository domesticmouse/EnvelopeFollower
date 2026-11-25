/** Build-time feature flags detected from a tutorial entry's raw MDX body. */
export interface ContentFeatures {
  hasMath: boolean;
  hasMermaid: boolean;
}

const DISPLAY_MATH_RE = /(^|[^\\])\$\$[\s\S]+?\$\$/m;
const INLINE_MATH_RE = /(^|[^\\$])\$(?!\s|\$)(?:[^\n$]*?\S)?(?<!\s)\$(?!\$)/;

interface FenceState {
  char: '`' | '~';
  length: number;
  info: string;
}

/**
 * Scan Markdown/MDX lines to separate non-code prose lines from fenced code blocks
 * and record whether any top-level ```mermaid fence exists.
 */
function scanMarkdownBlocks(body: string): { prose: string; hasMermaidBlock: boolean } {
  const proseLines: string[] = [];
  let activeFence: FenceState | null = null;
  let hasMermaidBlock = false;

  for (const line of body.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!activeFence) {
      const openMatch = /^(`{3,}|~{3,})(.*)$/.exec(trimmed);
      if (openMatch) {
        const marker = openMatch[1] ?? '';
        const info = (openMatch[2] ?? '').trim();
        const char = marker[0] as '`' | '~';
        // Backtick info strings cannot contain backticks in CommonMark
        if (char === '`' && info.includes('`')) {
          proseLines.push(line);
          continue;
        }
        activeFence = { char, length: marker.length, info };
        if (/^mermaid(?:\s|$)/i.test(info)) {
          hasMermaidBlock = true;
        }
        continue;
      }
      proseLines.push(line);
    } else {
      const closeMatch = /^(`{3,}|~{3,})\s*$/.exec(trimmed);
      if (
        closeMatch &&
        closeMatch[1]?.[0] === activeFence.char &&
        closeMatch[1].length >= activeFence.length
      ) {
        activeFence = null;
      }
    }
  }

  return { prose: proseLines.join('\n'), hasMermaidBlock };
}

function stripInlineCodeSpans(text: string): string {
  return text.replace(/(`+)([^`]|(?!(?<!`)\1(?!`))`)*?\1/g, ' ');
}

/** Return true if the raw Markdown/MDX body contains inline `$...$` or display `$$...$$` math outside code. */
export function hasMath(body: string | undefined): boolean {
  if (!body) {
    return false;
  }
  const { prose } = scanMarkdownBlocks(body);
  const withoutInlineCode = stripInlineCodeSpans(prose);
  return DISPLAY_MATH_RE.test(withoutInlineCode) || INLINE_MATH_RE.test(withoutInlineCode);
}

/** Return true if the raw Markdown/MDX body contains a top-level `mermaid` fenced code block. */
export function hasMermaid(body: string | undefined): boolean {
  if (!body) {
    return false;
  }
  return scanMarkdownBlocks(body).hasMermaidBlock;
}

/** Detect build-time KaTeX math and Mermaid diagram usage for conditional asset loading. */
export function detectContentFeatures(body: string | undefined): ContentFeatures {
  if (!body) {
    return { hasMath: false, hasMermaid: false };
  }
  const { prose, hasMermaidBlock } = scanMarkdownBlocks(body);
  const withoutInlineCode = stripInlineCodeSpans(prose);
  return {
    hasMath: DISPLAY_MATH_RE.test(withoutInlineCode) || INLINE_MATH_RE.test(withoutInlineCode),
    hasMermaid: hasMermaidBlock,
  };
}
