// Builds everything the site derives from the repository, so nothing the site states about
// the plugins is typed by hand:
//   src/data/catalog.generated.json              plugins, skills, agents, totals
//   docs/changelog/<plugin>.md (+ _category_)    a copy of each plugin's CHANGELOG.md
//   docs/getting-started/_install.generated.md   the README's install steps, verbatim
// With --check it writes nothing and runs two guards instead, exiting 1 on any problem:
//   structure  every skill and agent has its docs page, and no page describes a missing one
//   freshness  every hand-written page declares `sources` + `sources_hash` and the hash
//              still matches those files (`npm run docs:stamp` records a reviewed page)
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { dump as dumpYaml } from 'js-yaml';
import {
  docsDir,
  homeSourcesFile,
  inspectGuardedFile,
  listHandWrittenPages,
  repoRoot,
  splitFrontmatter,
  websiteRelative,
  websiteRoot,
} from './lib/docs-sources.mjs';

const GITHUB_REPO = 'https://github.com/TheSoftwareHouse/agentic-collections';
const INSTALL_FROM = '## Step 1';
const INSTALL_UNTIL = '## Using what you installed';

const readText = (...segments) => readFileSync(path.join(repoRoot, ...segments), 'utf8');
const readJson = (...segments) => JSON.parse(readText(...segments));
const exists = (...segments) => existsSync(path.join(repoRoot, ...segments));
const rel = (...segments) => segments.join('/');

function familyOf(name) {
  if (name === 'tsh-core') return 'core';
  if (name.startsWith('tsh-stack-')) return 'stack';
  if (name.startsWith('tsh-')) return 'discipline';
  throw new Error(`plugin "${name}" is not tsh-core, tsh-stack-* or tsh-<discipline>`);
}

function readFrontmatter(repoPath) {
  try {
    const frontmatter = splitFrontmatter(readText(repoPath));
    if (!frontmatter) throw new Error('no frontmatter block');
    return frontmatter.data;
  } catch (error) {
    throw new Error(`${repoPath}: ${error.message}`);
  }
}

function toolList(value) {
  if (value == null) return null;
  const list = Array.isArray(value) ? value : String(value).split(',');
  return list.map((tool) => String(tool).trim()).filter(Boolean);
}

function readComponent(repoPath, expectedName) {
  const data = readFrontmatter(repoPath);
  if (data.name != null && data.name !== expectedName) {
    throw new Error(`${repoPath}: frontmatter name "${data.name}" differs from "${expectedName}"`);
  }
  if (typeof data.description !== 'string' || data.description.trim() === '') {
    throw new Error(`${repoPath}: missing description`);
  }
  return {
    name: expectedName,
    description: data.description.trim(),
    whenToUse: typeof data.when_to_use === 'string' ? data.when_to_use.trim() : null,
    model: data.model == null ? null : String(data.model),
    tools: toolList(data.tools),
    userInvocable: data['user-invocable'] !== false,
    disableModelInvocation: data['disable-model-invocation'] === true,
  };
}

function readPlugin(entry) {
  const dir = path.posix.normalize(entry.source);
  const pluginPath = rel(dir, '.claude-plugin/plugin.json');
  const manifest = readJson(pluginPath);
  if (manifest.name !== entry.name || path.posix.basename(dir) !== entry.name) {
    throw new Error(`marketplace entry "${entry.name}" does not match ${pluginPath}`);
  }

  const skillsDir = path.join(repoRoot, dir, 'skills');
  const skills = !existsSync(skillsDir)
    ? []
    : readdirSync(skillsDir, { withFileTypes: true })
        .filter((d) => d.isDirectory() && exists(dir, 'skills', d.name, 'SKILL.md'))
        .map((d) => {
          const { tools, ...skill } = readComponent(rel(dir, 'skills', d.name, 'SKILL.md'), d.name);
          return { ...skill, tools };
        });

  const agentsDir = path.join(repoRoot, dir, 'agents');
  const agents = !existsSync(agentsDir)
    ? []
    : readdirSync(agentsDir)
        .filter((file) => file.endsWith('.md'))
        .map((file) => {
          const { userInvocable, disableModelInvocation, whenToUse, ...agent } = readComponent(
            rel(dir, 'agents', file),
            file.slice(0, -'.md'.length),
          );
          return agent;
        });

  const mcpServers = exists(dir, '.mcp.json')
    ? Object.keys(readJson(dir, '.mcp.json').mcpServers ?? {})
    : [];
  const hooks = exists(dir, 'hooks/hooks.json') ? readJson(dir, 'hooks/hooks.json').hooks : null;

  const byName = (a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
  return {
    name: manifest.name,
    displayName: entry.displayName ?? manifest.displayName ?? manifest.name,
    family: familyOf(manifest.name),
    version: manifest.version,
    description: manifest.description,
    empty: skills.length === 0 && agents.length === 0,
    hasChangelog: exists(dir, 'CHANGELOG.md'),
    skills: skills.sort(byName),
    agents: agents.sort(byName),
    mcpServers,
    hasHooks: hooks != null && Object.keys(hooks).length > 0,
  };
}

function buildCatalog() {
  const marketplace = readJson('.claude-plugin/marketplace.json');
  const plugins = marketplace.plugins.map(readPlugin);
  const listed = new Set(plugins.map((plugin) => plugin.name));
  const unlisted = readdirSync(path.join(repoRoot, 'plugins')).filter(
    (name) => exists('plugins', name, '.claude-plugin/plugin.json') && !listed.has(name),
  );
  if (unlisted.length > 0) {
    throw new Error(`plugins missing from marketplace.json: ${unlisted.join(', ')}`);
  }
  const active = plugins.filter((plugin) => !plugin.empty);
  return {
    totals: {
      plugins: active.length,
      skills: active.reduce((sum, plugin) => sum + plugin.skills.length, 0),
      agents: active.reduce((sum, plugin) => sum + plugin.agents.length, 0),
    },
    plugins,
  };
}

// --- Generated Markdown -------------------------------------------------------------------

// Docusaurus 3 compiles every .md as MDX, and a `format: md` frontmatter key does not change
// that (verified on 3.10.2): a bare `<tag>` or `{expression}` outside code fails the build.
// Repository Markdown is written for GitHub, so the copies escape those characters instead.
// Fenced blocks and inline code are left alone; nothing else in the text changes.
function escapeForMdx(markdown) {
  const escapeChar = { '<': '&lt;', '{': '\\{', '}': '\\}' };
  // `<https://…>` autolinks are not MDX either; they become the equivalent inline link.
  const escapeProse = (prose) =>
    prose.replace(
      /(`+)(?:(?!\n[ \t]*\n)[\s\S])*?\1|<(https?:\/\/[^>\s]+)>|[<{}]/g,
      (match, ticks, url) => (ticks ? match : url ? `[${url}](${url})` : escapeChar[match]),
    );
  const out = [];
  let prose = [];
  let fence = null;
  const flushProse = () => {
    if (prose.length > 0) out.push(escapeProse(prose.join('\n')));
    prose = [];
  };
  for (const line of markdown.split('\n')) {
    const opening = /^\s*(```+|~~~+)/.exec(line)?.[1];
    if (fence === null && opening) {
      flushProse();
      fence = opening;
      out.push(line);
    } else if (fence !== null) {
      out.push(line);
      if (opening && opening[0] === fence[0] && opening.length >= fence.length) fence = null;
    } else {
      prose.push(line);
    }
  }
  flushProse();
  return out.join('\n');
}

/** Rewrites relative link targets to GitHub URLs: a docs page has no such files to link to. */
function absolutizeLinks(markdown, baseDir) {
  let inFence = false;
  return markdown
    .split('\n')
    .map((line) => {
      if (/^\s*(```|~~~)/.test(line)) inFence = !inFence;
      if (inFence) return line;
      return line.replace(/\]\(([^)\s]+)\)/g, (whole, target) => {
        if (/^([a-z][a-z0-9+.-]*:|#|\/)/i.test(target)) return whole;
        const resolved = path.posix.normalize(path.posix.join(baseDir, target));
        return `](${GITHUB_REPO}/blob/main/${resolved})`;
      });
    })
    .join('\n');
}

function extractInstallSection() {
  const lines = readText('README.md').replace(/\r\n/g, '\n').split('\n');
  const headings = [];
  let inFence = false;
  lines.forEach((line, index) => {
    if (/^\s*(```|~~~)/.test(line)) inFence = !inFence;
    if (!inFence && line.startsWith('## ')) headings.push({ index, line });
  });
  const start = headings.find(({ line }) => line.startsWith(INSTALL_FROM));
  const end = headings.find(({ line }) => line.startsWith(INSTALL_UNTIL));
  if (!start) throw new Error(`README.md has no "${INSTALL_FROM}" heading`);
  if (!end) throw new Error(`README.md has no "${INSTALL_UNTIL}" heading`);
  if (end.index <= start.index) {
    throw new Error(`README.md: "${INSTALL_UNTIL}" must come after "${INSTALL_FROM}"`);
  }
  const section = lines.slice(start.index, end.index).join('\n').trimEnd();
  return `${escapeForMdx(absolutizeLinks(section, ''))}\n`;
}

function changelogPage(plugin) {
  const repoPath = rel('plugins', plugin.name, 'CHANGELOG.md');
  const body = readText(repoPath)
    .replace(/\r\n/g, '\n')
    .replace(/^# .*\n+/, ''); // the page title replaces the file's own H1
  const frontmatter = dumpYaml({ title: `${plugin.name} changelog`, sidebar_label: plugin.name });
  return (
    `---\n${frontmatter}---\n\n` +
    `> This page is a generated copy. The canonical file is ` +
    `[${repoPath}](${GITHUB_REPO}/blob/main/${repoPath}).\n\n` +
    escapeForMdx(absolutizeLinks(body, rel('plugins', plugin.name)))
  );
}

function writeFileEnsuringDir(file, content) {
  mkdirSync(path.dirname(file), { recursive: true });
  writeFileSync(file, content);
}

function generate() {
  const catalog = buildCatalog();
  const install = extractInstallSection();

  writeFileEnsuringDir(
    path.join(websiteRoot, 'src/data/catalog.generated.json'),
    `${JSON.stringify(catalog, null, 2)}\n`,
  );
  writeFileEnsuringDir(path.join(docsDir, 'getting-started/_install.generated.md'), install);

  const changelogDir = path.join(docsDir, 'changelog');
  rmSync(changelogDir, { recursive: true, force: true });
  const withChangelog = catalog.plugins.filter((plugin) => plugin.hasChangelog);
  for (const plugin of withChangelog) {
    writeFileEnsuringDir(path.join(changelogDir, `${plugin.name}.md`), changelogPage(plugin));
  }
  writeFileEnsuringDir(
    path.join(changelogDir, '_category_.json'),
    `${JSON.stringify(
      { label: 'Changelog', position: 99, link: { type: 'generated-index' } },
      null,
      2,
    )}\n`,
  );

  const { totals } = catalog;
  console.log(
    `catalog: ${totals.plugins} plugins, ${totals.skills} skills, ${totals.agents} agents; ` +
      `${withChangelog.length} changelog pages; install section from README.md`,
  );
}

// --- Guards -------------------------------------------------------------------------------

function listComponentPages(pluginName, kind) {
  const dir = path.join(docsDir, 'plugins', pluginName, kind);
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile() && !entry.name.startsWith('_'))
    .map((entry) => path.relative(dir, path.join(entry.parentPath, entry.name)));
}

function checkStructure(catalog) {
  const problems = [];
  const docsPath = (...segments) => websiteRelative(path.join(docsDir, 'plugins', ...segments));
  const pluginsDocsDir = path.join(docsDir, 'plugins');
  const documented = existsSync(pluginsDocsDir)
    ? readdirSync(pluginsDocsDir, { withFileTypes: true }).filter((d) => d.isDirectory())
    : [];
  const names = new Set([...catalog.plugins.map((p) => p.name), ...documented.map((d) => d.name)]);

  for (const name of [...names].sort()) {
    const plugin = catalog.plugins.find((candidate) => candidate.name === name);
    const components = { skills: plugin?.skills ?? [], agents: plugin?.agents ?? [] };
    if (plugin && !plugin.empty && !existsSync(path.join(pluginsDocsDir, name, 'index.md'))) {
      problems.push(`missing page: ${docsPath(name, 'index.md')}`);
    }
    for (const kind of ['skills', 'agents']) {
      const expected = new Set(components[kind].map((component) => `${component.name}.md`));
      for (const file of expected) {
        if (!existsSync(path.join(pluginsDocsDir, name, kind, file))) {
          problems.push(`missing page: ${docsPath(name, kind, file)}`);
        }
      }
      for (const file of listComponentPages(name, kind).sort()) {
        if (!expected.has(file)) {
          problems.push(
            `orphan page (no matching ${kind.slice(0, -1)}): ${docsPath(name, kind, file)}`,
          );
        }
      }
    }
  }
  return problems;
}

function checkFreshness() {
  const problems = [];
  const guarded = [
    ...listHandWrittenPages(),
    ...(existsSync(homeSourcesFile) ? [homeSourcesFile] : []),
  ];
  for (const file of guarded) {
    const label = websiteRelative(file);
    const result = inspectGuardedFile(file);
    if (file === homeSourcesFile && result.problems.length === 0) {
      const declared = JSON.parse(readFileSync(file, 'utf8'));
      if (Object.keys(declared).sort().join() !== 'sources,sources_hash') {
        result.problems.push('must have exactly the fields "sources" and "sources_hash"');
      }
    }
    if (result.problems.length > 0) {
      for (const problem of result.problems) problems.push(`${label}: ${problem}`);
    } else if (result.declaredHash === null) {
      problems.push(`${label}: has no sources_hash (run: npm run docs:stamp -- ${label})`);
    } else if (result.declaredHash !== result.actualHash) {
      problems.push(
        `stale page: ${label}\n    its sources changed since the page was last stamped; ` +
          `update the page, then run: npm run docs:stamp -- ${label}\n    sources:\n` +
          result.files.map((source) => `      ${source}`).join('\n'),
      );
    }
  }
  return problems;
}

function check() {
  const problems = [...checkStructure(buildCatalog()), ...checkFreshness()];
  if (problems.length === 0) {
    console.log('docs check: every component has a page and every page is fresh');
    return;
  }
  console.error(`docs check failed, ${problems.length} problem(s):\n`);
  for (const problem of problems) console.error(`- ${problem}`);
  process.exit(1);
}

try {
  if (process.argv.includes('--check')) check();
  else generate();
} catch (error) {
  console.error(`sync-catalog: ${error.message}`);
  process.exit(1);
}
