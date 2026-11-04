// Fails the Vercel build when it runs in the wrong place: outside Vercel, in the Copilot
// Collections project, or from a repository other than agentic-collections.
// Variable names come from the Vercel docs, "System environment variables".

const EXPECTED_REPO_SLUG = 'agentic-collections';

const env = process.env;
const problems = [];

if (!env.VERCEL) {
  problems.push(
    'VERCEL is not set. Vercel only exposes system environment variables when ' +
      '"Enable access to System Environment Variables" is checked under ' +
      'Project Settings > Environment Variables.',
  );
}

for (const name of ['VERCEL_PROJECT_PRODUCTION_URL', 'VERCEL_PROJECT_NAME']) {
  if (env[name]?.toLowerCase().includes('copilot')) {
    problems.push(`${name}="${env[name]}" points at the Copilot Collections project.`);
  }
}

const slug = env.VERCEL_GIT_REPO_SLUG;
if (slug && slug !== EXPECTED_REPO_SLUG) {
  problems.push(`VERCEL_GIT_REPO_SLUG="${slug}", expected "${EXPECTED_REPO_SLUG}".`);
}

if (problems.length > 0) {
  console.error('vercel-guard: refusing to build.');
  for (const problem of problems) {
    console.error(`  - ${problem}`);
  }
  process.exit(1);
}

console.log('vercel-guard: OK');
