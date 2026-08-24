/**
 * 轻量 Markdown → HTML（无外部依赖）
 * 支持：标题（含 TOC id）、粗斜体、代码块（语法高亮）、链接、引用、列表、图片
 */

export interface MarkdownTocItem {
  level: number
  text: string
  id: string
}

export interface MarkdownResult {
  html: string
  toc: MarkdownTocItem[]
}

const KEYWORDS: Record<string, string[]> = {
  javascript: [
    'const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while', 'class',
    'import', 'export', 'from', 'async', 'await', 'new', 'true', 'false', 'null', 'undefined',
  ],
  typescript: [
    'const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while', 'class',
    'import', 'export', 'from', 'async', 'await', 'new', 'true', 'false', 'null', 'undefined',
    'interface', 'type', 'enum', 'implements', 'extends', 'public', 'private', 'readonly',
  ],
  python: [
    'def', 'class', 'return', 'if', 'elif', 'else', 'for', 'while', 'import', 'from', 'as',
    'True', 'False', 'None', 'and', 'or', 'not', 'in', 'with', 'lambda', 'yield', 'async', 'await',
  ],
  bash: ['if', 'then', 'else', 'fi', 'for', 'do', 'done', 'echo', 'export', 'cd', 'sudo'],
  json: ['true', 'false', 'null'],
  css: ['@media', '@import', 'important'],
  html: ['DOCTYPE', 'html', 'head', 'body', 'div', 'span', 'script', 'style'],
}

const slugCounts = new Map<string, number>()

function resetSlugCounts() {
  slugCounts.clear()
}

function slugify(text: string): string {
  const base = text
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^\w\u4e00-\u9fff-]/g, '')
    .slice(0, 48) || 'section'
  const count = slugCounts.get(base) ?? 0
  slugCounts.set(base, count + 1)
  return count ? `${base}-${count}` : base
}

function normalizeLang(lang: string): string {
  const key = (lang || '').trim().toLowerCase()
  const aliases: Record<string, string> = {
    js: 'javascript',
    ts: 'typescript',
    py: 'python',
    sh: 'bash',
    shell: 'bash',
    yml: 'yaml',
  }
  return aliases[key] || key || 'plain'
}

function highlightCode(code: string, lang: string): string {
  const language = normalizeLang(lang)
  let html = escapeHtml(code)

  if (language === 'json') {
    html = html.replace(/"([^"\\]|\\.)*"/g, (m) => `<span class="md-hl-string">${m}</span>`)
    html = html.replace(/\b(true|false|null)\b/g, '<span class="md-hl-keyword">$1</span>')
    html = html.replace(/\b(-?\d+(?:\.\d+)?)\b/g, '<span class="md-hl-number">$1</span>')
    return html
  }

  html = html.replace(/(^|\s)(\/\/.*$|#.*$)/gm, '$1<span class="md-hl-comment">$2</span>')
  html = html.replace(/('(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`)/g, (m) =>
    `<span class="md-hl-string">${m}</span>`,
  )
  html = html.replace(/\b(-?\d+(?:\.\d+)?)\b/g, '<span class="md-hl-number">$1</span>')

  const words = KEYWORDS[language] || KEYWORDS.javascript
  for (const word of words) {
    html = html.replace(new RegExp(`\\b(${word})\\b`, 'g'), '<span class="md-hl-keyword">$1</span>')
  }

  return html
}

export function extractToc(source: string): MarkdownTocItem[] {
  const toc: MarkdownTocItem[] = []
  resetSlugCounts()
  for (const line of (source || '').replace(/\r\n/g, '\n').split('\n')) {
    const match = /^(#{2,3})\s+(.+)$/.exec(line)
    if (!match) continue
    const level = match[1].length
    const text = match[2].trim()
    toc.push({ level, text, id: slugify(text) })
  }
  resetSlugCounts()
  return toc
}

export function renderMarkdown(source: string): string {
  return renderMarkdownDocument(source).html
}

export function renderMarkdownDocument(source: string): MarkdownResult {
  const toc: MarkdownTocItem[] = []
  resetSlugCounts()

  const text = (source || '').replace(/\r\n/g, '\n').trim()
  if (!text) {
    resetSlugCounts()
    return { html: '', toc: [] }
  }

  const codeBlocks: string[] = []
  let html = text.replace(/```([\w-]*)\n?([\s\S]*?)```/g, (_m, lang, code) => {
    const i = codeBlocks.length
    const language = normalizeLang(String(lang || ''))
    const body = highlightCode(String(code).replace(/\n$/, ''), language)
    codeBlocks.push(
      `<pre class="md-codeblock" data-lang="${escapeHtml(language)}"><code>${body}</code></pre>`,
    )
    return `\n%%CODEBLOCK_${i}%%\n`
  })

  const lines = html.split('\n')
  const out: string[] = []
  let i = 0

  while (i < lines.length) {
    const line = lines[i]

    if (/^%%CODEBLOCK_\d+%%$/.test(line.trim())) {
      out.push(line.trim())
      i += 1
      continue
    }

    if (/^---+$/.test(line.trim()) || /^\*\*\*+$/.test(line.trim())) {
      out.push('<hr />')
      i += 1
      continue
    }

    const heading = /^(#{1,4})\s+(.+)$/.exec(line)
    if (heading) {
      const level = heading[1].length
      const textContent = heading[2].trim()
      const id = slugify(textContent)
      if (level >= 2 && level <= 3) {
        toc.push({ level, text: textContent, id })
      }
      out.push(`<h${level} id="${id}">${inline(textContent)}</h${level}>`)
      i += 1
      continue
    }

    if (/^>\s?/.test(line)) {
      const quote: string[] = []
      while (i < lines.length && /^>\s?/.test(lines[i])) {
        quote.push(lines[i].replace(/^>\s?/, ''))
        i += 1
      }
      out.push(`<blockquote><p>${inline(quote.join(' '))}</p></blockquote>`)
      continue
    }

    if (/^[-*+]\s+/.test(line)) {
      const items: string[] = []
      while (i < lines.length && /^[-*+]\s+/.test(lines[i])) {
        items.push(`<li>${inline(lines[i].replace(/^[-*+]\s+/, ''))}</li>`)
        i += 1
      }
      out.push(`<ul>${items.join('')}</ul>`)
      continue
    }

    if (/^\d+\.\s+/.test(line)) {
      const items: string[] = []
      while (i < lines.length && /^\d+\.\s+/.test(lines[i])) {
        items.push(`<li>${inline(lines[i].replace(/^\d+\.\s+/, ''))}</li>`)
        i += 1
      }
      out.push(`<ol>${items.join('')}</ol>`)
      continue
    }

    if (!line.trim()) {
      i += 1
      continue
    }

    const para: string[] = []
    while (i < lines.length && lines[i].trim() && !isBlockStart(lines[i])) {
      para.push(lines[i])
      i += 1
    }
    out.push(`<p>${inline(para.join(' '))}</p>`)
  }

  resetSlugCounts()
  return {
    html: out
      .join('\n')
      .replace(/%%CODEBLOCK_(\d+)%%/g, (_m, idx) => codeBlocks[Number(idx)] || ''),
    toc,
  }
}

function isBlockStart(line: string): boolean {
  return (
    /^#{1,4}\s+/.test(line) ||
    /^>\s?/.test(line) ||
    /^[-*+]\s+/.test(line) ||
    /^\d+\.\s+/.test(line) ||
    /^---+$/.test(line.trim()) ||
    /^\*\*\*+$/.test(line.trim()) ||
    /^%%CODEBLOCK_/.test(line.trim())
  )
}

function inline(text: string): string {
  let s = escapeHtml(text)
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>')
  s = s.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, '<img src="$2" alt="$1" loading="lazy" />')
  s = s.replace(
    /\[([^\]]+)\]\((https?:[^)\s]+|\/[^)\s]*)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>',
  )
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  s = s.replace(/__([^_]+)__/g, '<strong>$1</strong>')
  s = s.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>')
  s = s.replace(/(?<!_)_([^_]+)_(?!_)/g, '<em>$1</em>')
  return s
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}
