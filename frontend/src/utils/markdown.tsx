/**
 * Safe Markdown rendering pipeline:
 *   user content -> marked (parse) -> DOMPurify (sanitize) -> React renderer.
 * Raw HTML is never injected without sanitization.
 */
import DOMPurify from "dompurify";
import { marked } from "marked";

marked.setOptions({ breaks: true, gfm: true });

export function renderMarkdown(source: string): string {
  const html = marked.parse(source, { async: false }) as string;
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ["p", "br", "strong", "em", "ul", "ol", "li", "code", "blockquote"],
    ALLOWED_ATTR: [],
  });
}
