import React, { useEffect, useState } from 'react';

const REPO_API = 'https://api.github.com/repos/TheSoftwareHouse/agentic-collections';

const formatStars = (n: number): string =>
  n >= 1000 ? (n / 1000).toFixed(n >= 10000 ? 0 : 1).replace(/\.0$/, '') + 'k' : String(n);

let cached: string | null = null;
let pending: Promise<string | null> | null = null;

function fetchStars(): Promise<string | null> {
  if (cached) return Promise.resolve(cached);
  pending ??= fetch(REPO_API)
    .then((r) => (r.ok ? r.json() : null))
    .then((d) =>
      d && typeof d.stargazers_count === 'number' ? formatStars(d.stargazers_count) : null,
    )
    .catch(() => null);
  return pending.then((v) => (cached = v));
}

/**
 * Live GitHub star count. Renders an empty span until the API answers, and stays empty if it is
 * unavailable or rate-limited: no star count is ever hard-coded. home.css hides the enclosing
 * `<em>` (with its ★) while the span is empty.
 */
export default function GhStars(): React.JSX.Element {
  const [stars, setStars] = useState<string | null>(cached);

  useEffect(() => {
    let alive = true;
    fetchStars().then((v) => alive && v && setStars(v));
    return () => {
      alive = false;
    };
  }, []);

  return <span className="gh-stars">{stars}</span>;
}
