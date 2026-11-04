// Shared by sync-catalog.mjs (--check) and docs-stamp.mjs: how a docs page declares the
// repository files it was written from, and how the hash over those files is computed.
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { lstatSync, readdirSync, readFileSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { load as loadYaml } from 'js-yaml';

export const websiteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
export const repoRoot = path.resolve(websiteRoot, '..');
export const docsDir = path.join(websiteRoot, 'docs');
export const homeSourcesFile = path.join(websiteRoot, 'src/components/home/sources.json');

// Local, git-ignored artefacts that a clean checkout (CI, Vercel) never has; hashing them would
// make a page look stale everywhere except on the machine that stamped it.
const IGNORED_FILES = new Set(['.DS_Store', '__pycache__', '.pytest_cache', 'node_modules']);
const FRONTMATTER = /^---\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/;
const HASH_LINE = /^sources_hash[ \t]*:.*$/m;

export const toPosix = (p) => p.split(path.sep).join('/');
export const repoRelative = (absPath) => toPosix(path.relative(repoRoot, absPath));
export const websiteRelative = (absPath) => toPosix(path.relative(websiteRoot, absPath));

/** Splits a Markdown file into its parsed YAML frontmatter and the raw YAML text. */
export function splitFrontmatter(text) {
  const match = FRONTMATTER.exec(text);
  if (!match) return null;
  const data = loadYaml(match[1]);
  return { data: data ?? {}, yamlText: match[1], yamlOffset: match[0].indexOf('\n') + 1 };
}

/** Validates a `sources` value; returns the list or the reason it is unusable. */
export function validateSources(sources) {
  if (!Array.isArray(sources) || sources.length === 0) {
    return { error: '`sources` must be a non-empty list of repo-root-relative paths' };
  }
  for (const entry of sources) {
    if (typeof entry !== 'string' || entry === '') {
      return { error: '`sources` entries must be non-empty strings' };
    }
    if (entry.includes('\\') || path.posix.isAbsolute(entry) || entry.split('/').includes('..')) {
      return { error: `source "${entry}" must be a repo-root-relative path without ".." segments` };
    }
  }
  return { sources };
}

// Fallback for a tree without git metadata (some deploy builders): a clean checkout has no
// local artefacts, so skipping these names is enough there.
function walkFiles(dir) {
  const files = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (IGNORED_FILES.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...walkFiles(full));
    else files.push(full);
  }
  return files;
}

let gitAvailable;
/**
 * Files git would commit under `dir`: tracked plus untracked-but-not-ignored. Hashing exactly
 * this set makes a stamp reproduce on any clean checkout, whatever else the author has locally
 * (caches, virtualenvs, editor files). Returns null when the tree is not a git checkout.
 */
function gitFiles(dir) {
  if (gitAvailable === false) return null;
  try {
    const out = execFileSync(
      'git',
      ['ls-files', '-z', '--cached', '--others', '--exclude-standard', '--', dir],
      { cwd: repoRoot, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] },
    );
    gitAvailable = true;
    // --cached still lists files deleted from the working tree but not yet from the index.
    return out
      .split('\0')
      .filter(Boolean)
      .map((file) => path.join(repoRoot, file))
      .filter((file) => {
        try {
          lstatSync(file);
          return true;
        } catch {
          return false;
        }
      });
  } catch {
    gitAvailable = false;
    return null;
  }
}

function filesUnder(dir) {
  return gitFiles(dir) ?? walkFiles(dir);
}

/**
 * Expands sources to repo-relative files, sorted and de-duplicated. A path ending in `/`
 * stands for every file under that directory, recursively.
 */
export function expandSources(sources) {
  const files = new Set();
  const problems = [];
  for (const entry of sources) {
    const isDirectory = entry.endsWith('/');
    const absPath = path.join(repoRoot, entry);
    let stats;
    try {
      stats = statSync(absPath);
    } catch {
      problems.push(`source "${entry}" does not exist`);
      continue;
    }
    if (isDirectory && !stats.isDirectory()) {
      problems.push(`source "${entry}" ends in "/" but is a file`);
    } else if (!isDirectory && stats.isDirectory()) {
      problems.push(`source "${entry}" is a directory; end it with "/" to include its files`);
    } else if (isDirectory) {
      const inside = filesUnder(absPath);
      if (inside.length === 0) problems.push(`source "${entry}" contains no files`);
      for (const file of inside) {
        if (lstatSync(file).isSymbolicLink()) {
          problems.push(
            `source "${repoRelative(file)}" is a symbolic link; list its target instead`,
          );
        } else {
          files.add(repoRelative(file));
        }
      }
    } else if (lstatSync(absPath).isSymbolicLink()) {
      problems.push(`source "${entry}" is a symbolic link; list its target instead`);
    } else {
      files.add(entry);
    }
  }
  return { files: [...files].sort(), problems };
}

/** sha256 over each file as `path \0 content-with-LF \0`, in sorted path order. */
export function hashFiles(files) {
  const hash = createHash('sha256');
  for (const file of files) {
    const content = readFileSync(path.join(repoRoot, file), 'utf8').replace(/\r\n/g, '\n');
    hash.update(`${file}\0${content}\0`);
  }
  return hash.digest('hex');
}

/** Hand-written pages: every .md/.mdx under docs/ except partials and generated files. */
export function listHandWrittenPages() {
  const pages = [];
  const visit = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.name.startsWith('_')) continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (full !== path.join(docsDir, 'changelog')) visit(full);
      } else if (/\.mdx?$/.test(entry.name) && !entry.name.includes('.generated.')) {
        pages.push(full);
      }
    }
  };
  visit(docsDir);
  return pages.sort();
}

/** Returns `text` with `sources_hash` set in its frontmatter; everything else is untouched. */
export function stampPageText(text, hash) {
  const frontmatter = splitFrontmatter(text);
  const eol = text.includes('\r\n') ? '\r\n' : '\n';
  const line = `sources_hash: "${hash}"`;
  const yamlText = HASH_LINE.test(frontmatter.yamlText)
    ? frontmatter.yamlText.replace(HASH_LINE, line)
    : frontmatter.yamlText + eol + line;
  return (
    text.slice(0, frontmatter.yamlOffset) +
    yamlText +
    text.slice(frontmatter.yamlOffset + frontmatter.yamlText.length)
  );
}

/** Returns sources.json text with `sources_hash` set; the rest of the file is untouched. */
export function stampJsonText(text, hash) {
  const pattern = /("sources_hash"\s*:\s*)"[^"]*"/;
  if (!pattern.test(text)) throw new Error('has no "sources_hash" field to update');
  return text.replace(pattern, `$1"${hash}"`);
}

/**
 * Reads what a freshness-guarded file declares: its sources, the stored hash and the
 * freshly computed one. `kind` is "page" (frontmatter) or "json" (sources.json).
 */
export function inspectGuardedFile(absPath) {
  const text = readFileSync(absPath, 'utf8');
  let declared;
  try {
    if (absPath.endsWith('.json')) {
      declared = JSON.parse(text);
    } else {
      const frontmatter = splitFrontmatter(text);
      if (!frontmatter) return { problems: ['has no frontmatter'] };
      declared = frontmatter.data;
    }
  } catch (error) {
    return { problems: [`cannot be parsed: ${error.message}`] };
  }
  const { sources, error } = validateSources(declared.sources);
  if (error) return { problems: [error] };
  const { files, problems } = expandSources(sources);
  if (problems.length > 0) return { problems };
  return {
    problems: [],
    files,
    declaredHash: typeof declared.sources_hash === 'string' ? declared.sources_hash : null,
    actualHash: hashFiles(files),
  };
}
