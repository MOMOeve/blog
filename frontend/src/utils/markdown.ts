import MarkdownIt from 'markdown-it'
import taskLists from 'markdown-it-task-lists'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import typescript from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import bash from 'highlight.js/lib/languages/bash'
import json from 'highlight.js/lib/languages/json'
import css from 'highlight.js/lib/languages/css'
import xml from 'highlight.js/lib/languages/xml'
import yaml from 'highlight.js/lib/languages/yaml'

export interface MarkdownTocItem {
  level: number
  text: string
  id: string
}

export interface MarkdownResult {
  html: string
  toc: MarkdownTocItem[]
}

for (const [name, grammar] of Object.entries({ javascript, typescript, python, bash, json, css, xml, yaml })) {
  hljs.registerLanguage(name, grammar)
}

const md = new MarkdownIt({ html: false }).use(taskLists)
// The parser normalizes URLs before validation; reject data/file/custom protocols too.
md.validateLink = (url: string) => !/^[\s\u0000-\u0020]*(?:[a-z][a-z\d+.-]*:)/i.test(url)
  || /^(?:https?|mailto):/i.test(url)

const aliases: Record<string, string> = { js: 'javascript', ts: 'typescript', py: 'python', sh: 'bash', shell: 'bash', html: 'xml', yml: 'yaml' }
md.renderer.rules.fence = (tokens, index) => {
  const token = tokens[index]!
  const info = token.info.trim().split(/\s+/)[0]?.toLowerCase() || 'plain'
  const language = aliases[info] || info
  const code = hljs.getLanguage(language)
    ? hljs.highlight(token.content, { language, ignoreIllegals: true }).value
    : md.utils.escapeHtml(token.content)
  return `<pre class="md-codeblock" data-lang="${md.utils.escapeHtml(info)}"><code>${code}</code></pre>\n`
}

const linkOpen = md.renderer.rules.link_open
md.renderer.rules.link_open = (tokens, index, options, env, renderer) => {
  const token = tokens[index]!
  const href = String(token.attrGet('href') || '')
  if (/^https?:\/\//i.test(href) || href.startsWith('//')) {
    token.attrSet('target', '_blank')
    token.attrSet('rel', 'noopener noreferrer')
  }
  return linkOpen ? linkOpen(tokens, index, options, env, renderer) : renderer.renderToken(tokens, index, options)
}

const image = md.renderer.rules.image!
md.renderer.rules.image = (tokens, index, options, env, renderer) => {
  tokens[index]!.attrSet('loading', 'lazy')
  return image(tokens, index, options, env, renderer)
}
md.renderer.rules.table_open = () => '<div class="md-table-wrap"><table>\n'
md.renderer.rules.table_close = () => '</table></div>\n'

export function renderMarkdownDocument(source: string): MarkdownResult {
  const env = {}
  const tokens = md.parse(source || '', env)
  const toc: MarkdownTocItem[] = []
  const ids = new Set<string>()
  for (let index = 0; index < tokens.length; index += 1) {
    const token = tokens[index]!
    if (token.type !== 'heading_open') continue
    const inline = tokens[index + 1]!
    const text = (inline.children || [])
      .filter((child) => ['text', 'code_inline', 'image', 'softbreak', 'hardbreak'].includes(child.type))
      .map((child) => child.type.endsWith('break') ? ' ' : child.content).join('').trim()
    const base = text.toLowerCase().replace(/\s+/g, '-').replace(/[^\w\u4e00-\u9fff-]/g, '').slice(0, 48) || 'section'
    let id = base
    let suffix = 1
    while (ids.has(id)) id = `${base}-${suffix++}`
    ids.add(id)
    token.attrSet('id', id)
    token.attrSet('data-heading', text)
    const level = Number(token.tag.slice(1))
    if (level === 2 || level === 3) toc.push({ level, text, id })
  }
  return { html: md.renderer.render(tokens, md.options, env), toc }
}

export function renderMarkdown(source: string): string {
  return renderMarkdownDocument(source).html
}

export function extractToc(source: string): MarkdownTocItem[] {
  return renderMarkdownDocument(source).toc
}
