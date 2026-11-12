import React from 'react';

export default function HomeFooter(): React.JSX.Element {
  return (
    <>
      <footer>
        <div className="wrap">
          <a href="https://github.com/TheSoftwareHouse/agentic-collections">GitHub</a>
          <a href="/docs/">Read the docs</a>
          <a href="https://tsh.io">tsh.io</a>
          <span>Built by The Software House · MIT license</span>
        </div>
      </footer>
    </>
  );
}
