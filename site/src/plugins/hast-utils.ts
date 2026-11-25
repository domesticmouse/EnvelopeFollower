import type { Root, RootContent } from 'hast';

/** Normalize a HAST `className` or `class` property value into an array of non-empty class tokens. */
export function readClassNames(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value
      .filter((item): item is string | number => typeof item === 'string' || typeof item === 'number')
      .map((item) => String(item).trim())
      .filter(Boolean);
  }
  if (typeof value === 'string') {
    return value.split(/\s+/).filter(Boolean);
  }
  return [];
}

/** Recursively extract plain text content from a HAST root or content node. */
export function extractText(node: Root | RootContent): string {
  if (node.type === 'text') {
    return node.value;
  }
  if ('children' in node && Array.isArray(node.children)) {
    return (node.children as RootContent[]).map((child) => extractText(child)).join('');
  }
  return '';
}
