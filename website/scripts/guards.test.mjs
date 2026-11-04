// Tests for the two docs guards (sync-catalog.mjs --check), the stamp script and the Vercel
// guard. Each docs test builds a throwaway repository under the OS temp directory, copies the
// scripts into it, and runs them as the build does — the real repository is never touched.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import {
  cpSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptsDir = path.dirname(fileURLToPath(import.meta.url));
const websiteDir = path.dirname(scriptsDir);

const README = `# Fixture\n\n## Step 1 — add the marketplace\n\n\`/plugin marketplace add x\`\n\n## Using what you installed\n`;

function write(root, file, content) {
  const full = path.join(root, file);
  mkdirSync(path.dirname(full), { recursive: true });
  writeFileSync(full, content);
}

/** A repository with one plugin, one skill and a correctly stamped page for each. */
function fixture() {
  const root = mkdtempSync(path.join(tmpdir(), 'ac-guards-'));
  cpSync(scriptsDir, path.join(root, 'website/scripts'), { recursive: true });
  symlinkSync(path.join(websiteDir, 'node_modules'), path.join(root, 'website/node_modules'));
  write(root, 'README.md', README);
  write(
    root,
    '.claude-plugin/marketplace.json',
    JSON.stringify({ name: 'm', plugins: [{ name: 'tsh-core', source: './plugins/tsh-core' }] }),
  );
  write(
    root,
    'plugins/tsh-core/.claude-plugin/plugin.json',
    JSON.stringify({ name: 'tsh-core', version: '1.0.0', description: 'Core.' }),
  );
  write(
    root,
    'plugins/tsh-core/skills/demo/SKILL.md',
    '---\nname: demo\ndescription: "Does a demo."\n---\n\n# Demo\n',
  );
  write(root, 'plugins/tsh-core/skills/demo/references/more.md', 'More.\n');
  const page = (sources) =>
    `---\ntitle: T\nsources:\n${sources.map((s) => `  - ${s}`).join('\n')}\n---\n\nBody.\n`;
  write(
    root,
    'website/docs/plugins/tsh-core/index.md',
    page(['plugins/tsh-core/.claude-plugin/plugin.json']),
  );
  write(
    root,
    'website/docs/plugins/tsh-core/skills/demo.md',
    page(['plugins/tsh-core/skills/demo/']),
  );
  assert.equal(run(root, 'docs-stamp.mjs', ['--all']).status, 0);
  return root;
}

function run(root, script, args = [], env = {}) {
  return spawnSync(process.execPath, [path.join(root, 'website/scripts', script), ...args], {
    cwd: path.join(root, 'website'),
    encoding: 'utf8',
    env: { ...process.env, ...env },
  });
}

const check = (root) => run(root, 'sync-catalog.mjs', ['--check']);
const output = (result) => `${result.stdout}${result.stderr}`;

function withFixture(fn) {
  const root = fixture();
  try {
    fn(root);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

test('a fresh, fully documented fixture passes --check', () =>
  withFixture((root) => {
    const result = check(root);
    assert.equal(result.status, 0, output(result));
  }));

test('generate mode writes the files the site imports', () =>
  withFixture((root) => {
    const result = run(root, 'sync-catalog.mjs');
    assert.equal(result.status, 0, output(result));
    const catalog = JSON.parse(
      readFileSync(path.join(root, 'website/src/data/catalog.generated.json'), 'utf8'),
    );
    assert.equal(catalog.totals.skills, 1);
    readFileSync(path.join(root, 'website/docs/getting-started/_install.generated.md'), 'utf8');
  }));

test('a skill without a page fails the structure guard', () =>
  withFixture((root) => {
    write(
      root,
      'plugins/tsh-core/skills/extra/SKILL.md',
      '---\nname: extra\ndescription: "X."\n---\n',
    );
    const result = check(root);
    assert.notEqual(result.status, 0);
    assert.match(output(result), /missing page: docs\/plugins\/tsh-core\/skills\/extra\.md/);
  }));

test('a page for a component that does not exist fails as an orphan', () =>
  withFixture((root) => {
    write(root, 'website/docs/plugins/tsh-core/skills/ghost.md', '---\ntitle: G\n---\n');
    const result = check(root);
    assert.notEqual(result.status, 0);
    assert.match(output(result), /ghost/);
  }));

test('changing a source file makes its page stale, and re-stamping clears it', () =>
  withFixture((root) => {
    write(root, 'plugins/tsh-core/skills/demo/references/more.md', 'More, changed.\n');
    const stale = check(root);
    assert.notEqual(stale.status, 0);
    assert.match(output(stale), /stale page: docs\/plugins\/tsh-core\/skills\/demo\.md/);
    assert.equal(run(root, 'docs-stamp.mjs', ['docs/plugins/tsh-core/skills/demo.md']).status, 0);
    assert.equal(check(root).status, 0);
  }));

test('CRLF line endings in a source do not change the hash', () =>
  withFixture((root) => {
    const file = path.join(root, 'plugins/tsh-core/skills/demo/SKILL.md');
    writeFileSync(file, readFileSync(file, 'utf8').replace(/\n/g, '\r\n'));
    assert.equal(check(root).status, 0);
  }));

test('a source path escaping the repo fails', () =>
  withFixture((root) => {
    write(
      root,
      'website/docs/plugins/tsh-core/index.md',
      '---\ntitle: T\nsources:\n  - ../outside.md\n---\n',
    );
    const result = check(root);
    assert.notEqual(result.status, 0);
    assert.match(output(result), /without "\.\." segments/);
  }));

test('a symbolic link inside a source directory is rejected by name', () =>
  withFixture((root) => {
    symlinkSync(
      path.join(root, 'README.md'),
      path.join(root, 'plugins/tsh-core/skills/demo/references/link.md'),
    );
    const result = check(root);
    assert.notEqual(result.status, 0);
    assert.match(output(result), /link\.md" is a symbolic link/);
  }));

const featured = (root, entries) =>
  write(root, 'website/src/data/home-featured.json', JSON.stringify({ featured: entries }));

test('featured components must exist, once, with a label', () =>
  withFixture((root) => {
    const demo = { component: 'tsh-core/skills/demo', label: 'Does a demo' };
    featured(root, [demo]);
    assert.equal(check(root).status, 0, output(check(root)));
    for (const [entries, problem] of [
      [
        [{ ...demo, component: 'tsh-core/skills/ghost' }],
        /does not exist: tsh-core\/skills\/ghost/,
      ],
      [
        [{ ...demo, component: 'tsh-core/skills/demo/x' }],
        /is not <plugin>\/skills\|agents\/<name>/,
      ],
      [[{ ...demo, component: 'tsh-other/skills/demo' }], /plugin is empty or unknown/],
      [[demo, demo], /featured twice/],
      [[{ component: demo.component }], /has no label/],
      [[null, null], /needs a "component" string/],
    ]) {
      featured(root, entries);
      const result = check(root);
      assert.notEqual(result.status, 0);
      assert.match(output(result), problem);
    }
  }));

const guard = (env) =>
  spawnSync(process.execPath, [path.join(scriptsDir, 'vercel-guard.mjs')], {
    encoding: 'utf8',
    env: { PATH: process.env.PATH, ...env },
  }).status;

test('the Vercel guard refuses outside Vercel and inside the Copilot Collections project', () => {
  assert.notEqual(guard({}), 0);
  assert.notEqual(
    guard({ VERCEL: '1', VERCEL_PROJECT_PRODUCTION_URL: 'copilot-collections.tsh.io' }),
    0,
  );
  assert.notEqual(guard({ VERCEL: '1', VERCEL_PROJECT_NAME: 'copilot-collections' }), 0);
  assert.notEqual(guard({ VERCEL: '1', VERCEL_GIT_REPO_SLUG: 'copilot-collections' }), 0);
  assert.equal(
    guard({
      VERCEL: '1',
      VERCEL_PROJECT_PRODUCTION_URL: 'agentic-collections.tsh.io',
      VERCEL_GIT_REPO_SLUG: 'agentic-collections',
    }),
    0,
  );
});
