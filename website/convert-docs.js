#!/usr/bin/env node
/**
 * Converts MkDocs Material markdown to Docusaurus-compatible markdown.
 */
const fs = require('fs');
const path = require('path');

const SRC = path.join(__dirname, '..', 'docs');
const DST = path.join(__dirname, 'docs');

const ADMONITION_MAP = {
  tip: 'tip', note: 'note', info: 'info', warning: 'warning',
  danger: 'danger', caution: 'caution', example: 'note',
  abstract: 'info', success: 'tip', question: 'info',
  bug: 'danger', failure: 'danger',
};

/* ── Admonitions ── */
function convertAdmonitions(text) {
  const lines = text.split('\n');
  const out = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const m = line.match(/^(?:!!!|\?\?\?)\s+(\w+)(?:\s+"([^"]*)")?$/);
    if (m) {
      const docType = ADMONITION_MAP[m[1].toLowerCase()] || 'note';
      const title = m[2];
      out.push(title ? `:::${docType}[${title}]` : `:::${docType}`);
      i++;
      // Collect indented body
      while (i < lines.length && (lines[i].startsWith('    ') || lines[i].startsWith('\t') || lines[i] === '')) {
        // Stop if it's a blank line followed by non-indented content
        if (lines[i] === '') {
          const next = lines[i + 1];
          if (!next || (!next.startsWith('    ') && !next.startsWith('\t'))) break;
          out.push(''); i++; continue;
        }
        out.push(lines[i].replace(/^(?:    |\t)/, ''));
        i++;
      }
      out.push(':::');
      out.push('');
    } else {
      out.push(line);
      i++;
    }
  }
  return out.join('\n');
}

/* ── Tabs (line-by-line parser) ── */
function convertTabs(text) {
  if (!text.includes('=== "')) return text;

  const lines = text.split('\n');
  const out = [];
  let hasTabs = false;
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    // Detect start of a tab group
    if (/^=== "/.test(line)) {
      hasTabs = true;
      const tabItems = [];

      // Collect all consecutive === blocks in this group
      while (i < lines.length && /^=== "/.test(lines[i])) {
        const labelMatch = lines[i].match(/^=== "([^"]+)"/);
        const label = labelMatch ? labelMatch[1] : 'Tab';
        const value = label.toLowerCase().replace(/[^a-z0-9]+/g, '-');
        i++; // skip the === line

        // Skip blank line after label
        if (i < lines.length && lines[i] === '') i++;

        // Collect body: lines starting with 4 spaces OR blank lines surrounded by indented content
        const body = [];
        while (i < lines.length) {
          const l = lines[i];
          if (/^=== "/.test(l)) break; // next tab starts

          // Indented line — definitely part of this tab
          if (l.startsWith('    ') || l.startsWith('\t')) {
            body.push(l.replace(/^(?:    |\t)/, ''));
            i++;
          } else if (l === '') {
            // Blank line: include only if next non-blank line is also indented
            let j = i + 1;
            while (j < lines.length && lines[j] === '') j++;
            if (j < lines.length && (lines[j].startsWith('    ') || lines[j].startsWith('\t'))) {
              body.push('');
              i++;
            } else {
              break; // end of tab content
            }
          } else {
            break; // non-indented, non-blank: end of tab content
          }
        }

        // Trim trailing blank lines from body
        while (body.length && body[body.length - 1] === '') body.pop();

        tabItems.push({ label, value, body: body.join('\n') });
      }

      // Emit <Tabs> block
      out.push('<Tabs>');
      for (const item of tabItems) {
        out.push(`<TabItem value="${item.value}" label="${item.label}">`);
        out.push('');
        out.push(item.body);
        out.push('');
        out.push('</TabItem>');
        out.push('');
      }
      out.push('</Tabs>');
      out.push('');
    } else {
      out.push(line);
      i++;
    }
  }

  let result = out.join('\n');

  if (hasTabs) {
    const importLine = `import Tabs from '@theme/Tabs';\nimport TabItem from '@theme/TabItem';\n\n`;
    if (result.startsWith('---')) {
      // Insert after front matter
      const end = result.indexOf('\n---', 3);
      if (end !== -1) {
        result = result.slice(0, end + 4) + '\n\n' + importLine + result.slice(end + 5);
      } else {
        result = importLine + result;
      }
    } else {
      result = importLine + result;
    }
  }

  return result;
}

/* ── Remove MkDocs-specific icons ── */
function removeIcons(text) {
  return text.replace(/:(?:material|octicons|fontawesome)-[\w-]+:(?:\{[^}]*\})?/g, '');
}

/* ── Remove mkdocstrings directives ── */
function removeMkdocsDirectives(text) {
  return text.replace(/^:::\s+[\w.]+\s*$/gm, '');
}

/* ── Fix HTML for MDX ── */
function fixHtml(text) {
  text = text.replace(/<br>/g, '<br />');
  text = text.replace(/<hr>/g, '<hr />');
  // Remove MkDocs-specific HTML blocks
  text = text.replace(/<div class="(?:hero-section|stats-bar|section-divider|feature-grid|feature-card|framework-row|pipeline-wrapper|get-started-grid|get-started-card)[^"]*"[^>]*>[\s\S]*?<\/div>/gm, '');
  text = text.replace(/<hr class="[^"]*"[^>]*\/?>/g, '---');
  return text;
}

/* ── Add Docusaurus front matter if missing ── */
function addFrontMatter(text) {
  if (text.startsWith('---')) return text;
  const h1 = text.match(/^#\s+(.+)$/m);
  if (h1) {
    const title = h1[1].trim().replace(/"/g, '\\"');
    return `---\ntitle: "${title}"\n---\n\n${text}`;
  }
  return text;
}

/* ── Process one file ── */
function convertFile(srcPath, dstPath) {
  let text = fs.readFileSync(srcPath, 'utf8');

  const relPath = path.relative(SRC, srcPath).replace(/\\/g, '/');
  if (relPath === 'index.md') {
    console.log(`  SKIP  ${relPath} (replaced by React landing page)`);
    return;
  }

  text = convertAdmonitions(text);
  text = convertTabs(text);
  text = removeIcons(text);
  text = removeMkdocsDirectives(text);
  text = fixHtml(text);
  text = addFrontMatter(text);

  fs.mkdirSync(path.dirname(dstPath), { recursive: true });
  fs.writeFileSync(dstPath, text, 'utf8');
  console.log(`  OK    ${relPath}`);
}

function walkDir(dir, callback) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) walkDir(fullPath, callback);
    else if (entry.name.endsWith('.md')) callback(fullPath);
  }
}

console.log('Converting MkDocs → Docusaurus...\n');
let count = 0;
walkDir(SRC, (srcPath) => {
  const rel = path.relative(SRC, srcPath);
  convertFile(srcPath, path.join(DST, rel));
  count++;
});
console.log(`\nDone! ${count} files processed.`);
