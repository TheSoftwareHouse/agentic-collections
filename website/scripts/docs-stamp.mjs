// Recomputes `sources_hash` after a docs page was updated to match its sources.
// Usage: npm run docs:stamp -- <page path>...   |   npm run docs:stamp -- --all
// Run it AFTER updating the page content: the new hash records that the page was reviewed
// against the current sources, and the changed hash shows up in the PR diff.
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import {
  docsDir,
  homeSourcesFile,
  inspectGuardedFile,
  listHandWrittenPages,
  stampJsonText,
  stampPageText,
  websiteRelative,
} from './lib/docs-sources.mjs';

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: npm run docs:stamp -- <page path>... | --all');
  process.exit(2);
}

const targets = args.includes('--all')
  ? [...listHandWrittenPages(), ...(existsSync(homeSourcesFile) ? [homeSourcesFile] : [])]
  : args.map((arg) => path.resolve(process.cwd(), arg));

let failed = false;
for (const target of targets) {
  const label = websiteRelative(target);
  const isPage = target.startsWith(docsDir + path.sep) && /\.mdx?$/.test(target);
  if (!isPage && target !== homeSourcesFile) {
    console.error(`${label}: not a docs page or src/components/home/sources.json`);
    failed = true;
    continue;
  }
  if (!existsSync(target)) {
    console.error(`${label}: file does not exist`);
    failed = true;
    continue;
  }
  const inspected = inspectGuardedFile(target);
  if (inspected.problems.length > 0) {
    for (const problem of inspected.problems) console.error(`${label}: ${problem}`);
    failed = true;
    continue;
  }
  const before = readFileSync(target, 'utf8');
  let after;
  try {
    after = isPage
      ? stampPageText(before, inspected.actualHash)
      : stampJsonText(before, inspected.actualHash);
  } catch (error) {
    console.error(`${label}: ${error.message}`);
    failed = true;
    continue;
  }
  if (after === before) {
    console.log(`unchanged  ${label}`);
  } else {
    writeFileSync(target, after);
    console.log(`stamped    ${label}`);
  }
}
process.exit(failed ? 1 : 0);
