const { test } = require('node:test')
const assert = require('node:assert/strict')
const { Worker } = require('node:worker_threads')
const path = require('node:path')

// A worker timeout also catches synchronous parser loops without hanging CI.
function render(source) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(`
      const { parentPort, workerData } = require('node:worker_threads');
      const fs = require('node:fs');
      const path = require('node:path');
      const Module = require('node:module');
      const ts = require(workerData.typescript);
      const compiled = ts.transpileModule(fs.readFileSync(workerData.file, 'utf8'), {
        compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true }
      }).outputText;
      const mod = new Module(workerData.file);
      mod.filename = workerData.file;
      mod.paths = Module._nodeModulePaths(path.dirname(workerData.file));
      mod._compile(compiled, workerData.file);
      parentPort.postMessage({ ...mod.exports.renderMarkdownDocument(workerData.source), extracted: mod.exports.extractToc(workerData.source) });
    `, {
      eval: true,
      workerData: { file: path.resolve(__dirname, '../src/utils/markdown.ts'), source, typescript: require.resolve('typescript') },
    })
    const timer = setTimeout(() => { void worker.terminate(); reject(new Error('Markdown render exceeded 5 seconds')) }, 5000)
    worker.once('message', (result) => { clearTimeout(timer); resolve(result); void worker.terminate() })
    worker.once('error', (error) => { clearTimeout(timer); reject(error) })
    worker.once('exit', (code) => { if (code !== 0) { clearTimeout(timer); reject(new Error(`Markdown worker exited ${code}`)) } })
  })
}

test('pipe text returns as a paragraph instead of looping', async () => {
  assert.equal((await render('|hello|')).html.trim(), '<p>|hello|</p>')
})

test('highlighter preserves source and generates intact markup', async () => {
  const { html } = await render('```javascript\nconst x = 1\n```')
  assert.match(html, /<span class="hljs-keyword">const<\/span>/)
  assert.doesNotMatch(html, /<span\s+<span/)
  assert.equal(html.replace(/<[^>]+>/g, '').trim(), 'const x = 1')
})

test('unknown language is escaped plain text', async () => {
  const { html } = await render('```unknown\n<script>alert(1)</script>\n```')
  assert.match(html, /&lt;script&gt;/)
  assert.doesNotMatch(html, /<script>/)
})

test('TOC excludes code, strips formatting and uses unique document-local anchors', async () => {
  const source = '# Intro\n## **中文** `code`\n## 中文 code\n## 中文-code-1\n## 中文 code\n```md\n## fake\n```'
  const result = await render(source)
  assert.deepEqual(result.toc.map((item) => item.id), ['中文-code', '中文-code-1', '中文-code-1-1', '中文-code-2'])
  assert.deepEqual(result.extracted, result.toc)
  assert.equal(result.toc[0].text, '中文 code')
  assert.match(result.html, /id="中文-code"/)
  assert.deepEqual((await render('## 中文 code')).toc.map((item) => item.id), ['中文-code'])
})

test('tables, nested lists, tasks, quotes and images remain supported', async () => {
  const { html } = await render('| A | B |\n| --- | --- |\n| 1 | 2 |\n\n- [x] done\n- [ ] todo\n  - child\n\n> quote\n\n![photo](/media/test.png)')
  assert.match(html, /class="md-table-wrap"/)
  assert.match(html, /<td>2<\/td>/)
  assert.equal((html.match(/type="checkbox"/g) || []).length, 2)
  assert.match(html, /checked="" disabled=""/)
  assert.match(html, /<blockquote>/)
  assert.match(html, /loading="lazy"/)
})

test('raw HTML and unsafe link/image protocols never become executable markup', async () => {
  const { html } = await render('<img src=x onerror=alert(1)>\n\n[bad](javascript:alert%281%29)\n\n![bad](data:image/svg+xml;base64,PHN2Zz4=)\n\n[file](file:///etc/passwd)\n\n[encoded](jav&#x61;script:alert%281%29)')
  assert.doesNotMatch(html, /<img\b|href="(?:javascript|file|data):/i)
  assert.match(html, /&lt;img/)
})

test('external links have safe attributes and local anchors still work', async () => {
  const { html } = await render('[external](https://example.com) [local](#heading)')
  assert.match(html, /target="_blank" rel="noopener noreferrer"/)
  assert.match(html, /href="#heading"/)
})

test('empty documents return an empty result', async () => {
  const result = await render('  \n ')
  assert.equal(result.html, '')
  assert.deepEqual(result.toc, [])
})
