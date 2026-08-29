/**
 * Markdown 渲染：基于 marked（GFM）+ highlight.js
 * 支持表格、嵌套列表、任务列表、自动换行、代码高亮、标题目录
 */
import { Marked } from 'marked'
import hljs from 'highlight.js/lib/core'
import bash from 'highlight.js/lib/languages/bash'
import css from 'highlight.js/lib/languages/css'
import javascript from 'highlight.js/lib/languages/javascript'
import json from 'highlight.js/lib/languages/json'
import python from 'highlight.js/lib/languages/python'
import typescript from 'highlight.js/lib/languages/typescript'
import xml from 'highlight.js/lib/languages/xml'

hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('ts', typescript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('py', python)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('sh', bash)
hljs.registerLanguage('shell', bash)
hljs.registerLanguage('json', json)
hljs.registerLanguage('css', css)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('xml', xml)

export interface MarkdownTocItem {
  level: number
  text: string
  id: string
}

export interface MarkdownResult {
  html: string
  toc: MarkdownTocItem[]
}

const slugCounts = new Map<string, number>()

function resetSlugCounts() {
  slugCounts.clear()
}

function slugify(text: string): string {
  const base =
    text
      .trim()
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^\w\u4e00-\u9fff-]/g, '')
      .slice(0, 48) || 'section'
  const count = slugCounts.get(base) ?? 0
  slugCounts.set(base, count + 1)
  return count ? `${base}-${count}` : base
}

function stripTags(html: string): string {
  return html.replace(/<[^>]+>/g, '')
}

function escapeAttr(value: string): string {
  return value.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;')
}

function highlightCode(code: string, lang?: string): string {
  const key = (lang || '').trim().toLowerCase()
  try {
    if (key && hljs.getLanguage(key)) {
      return hljs.highlight(code, { language: key }).value
    }
  } catch {
    /* fall through */
  }
  return hljs.highlightAuto(code).value
}

const md = new Marked({
  gfm: true,
  breaks: true, // 单个回车换行
})

md.use({
  renderer: {
    code({ text, lang }) {
      const language = (lang || '').trim()
      const highlighted = highlightCode(text, language)
      const langAttr = language ? ` data-lang="${escapeAttr(language)}"` : ''
      return `<pre class="md-codeblock hljs"${langAttr}><code>${highlighted}</code></pre>\n`
    },
    heading({ tokens, depth }) {
      const text = this.parser.parseInline(tokens)
      const id = slugify(stripTags(text))
      return `<h${depth} id="${id}">${text}</h${depth}>\n`
    },
  },
})

export function extractToc(source: string): MarkdownTocItem[] {
  const toc: MarkdownTocItem[] = []
  resetSlugCounts()
  let inFence = false
  for (const line of (source || '').replace(/\r\n/g, '\n').split('\n')) {
    if (/^```/.test(line.trim())) {
      inFence = !inFence
      continue
    }
    if (inFence) continue
    const match = /^(#{2,3})\s+(.+)$/.exec(line)
    if (!match) continue
    toc.push({ level: match[1].length, text: match[2].trim(), id: slugify(match[2].trim()) })
  }
  resetSlugCounts()
  return toc
}

export function renderMarkdown(source: string): string {
  return renderMarkdownDocument(source).html
}

export function renderMarkdownDocument(source: string): MarkdownResult {
  const text = source || ''
  const toc = extractToc(text)
  resetSlugCounts()
  const html = md.parse(text, { async: false }) as string
  return {
    html: typeof html === 'string' ? html : '',
    toc,
  }
}
