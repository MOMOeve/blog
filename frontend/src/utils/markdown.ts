/**
 * 轻量 Markdown → HTML（无外部依赖，适合博客正文）
 * 支持：标题、粗斜体、行内/块代码、链接、引用、列表、分隔线、段落
 */
export function renderMarkdown(source: string): string {
  const text = (source || '').replace(/\r\n/g, '\n').trim()
  if (!text) return ''

  const codeBlocks: string[] = []
  let html = text.replace(/```([\w-]*)\n?([\s\S]*?)```/g, (_m, _lang, code) => {
    const i = codeBlocks.length
    codeBlocks.push(
      `<pre><code>${escapeHtml(String(code).replace(/\n$/, ''))}</code></pre>`,
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
      out.push(`<h${level}>${inline(heading[2])}</h${level}>`)
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

  return out
    .join('\n')
    .replace(/%%CODEBLOCK_(\d+)%%/g, (_m, idx) => codeBlocks[Number(idx)] || '')
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
  s = s.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, '<img src="$2" alt="$1" />')
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
