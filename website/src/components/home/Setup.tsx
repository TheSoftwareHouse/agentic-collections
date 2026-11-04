import React from 'react';
import catalog from '@site/src/data/catalog.generated.json';
import GhStars from './GhStars';
import CopyButton from './CopyButton';

/** Plugins the catalog registers per family, empty scaffolds included, as the marketplace lists them. */
const pluginCount = (family: string): string => {
  const n = catalog.plugins.filter((p) => p.family === family).length;
  return `${n} ${n === 1 ? 'plugin' : 'plugins'}`;
};

export default function Setup(): React.JSX.Element {
  return (
    <>
      <section className="su" id="setup">
        <div className="wrap">
          <div className="su-head">
            <div>
              <h2>
                Your discipline travels with you,
                <br />
                the stacks travel with the&nbsp;repo
              </h2>
            </div>
            <a className="btn btn-p" href="https://github.com/TheSoftwareHouse/agentic-collections">
              <img src="/img/home/asset-02-0962e269.png" alt="" />
              Get it on GitHub{' '}
              <em>
                ★ <GhStars />
              </em>
            </a>
          </div>
          {/* PHASE2(visual): three step cards (terminal, connection list, run card) — the card visuals are inherited from the source site's clone → connect → run flow; the terminal now shows a mocked catalog summary, not real CLI output — design the steps around the marketplace install and link each to its docs page */}
          <div className="su-grid">
            <div className="su-c">
              <div>
                <span className="n">01</span>
                <h3>Add the marketplace</h3>
                <p>
                  Run it inside any Claude Code session. It registers the catalog; nothing is
                  installed yet.
                </p>
              </div>
              <div className="su-v su-t">
                <CopyButton text="/plugin marketplace add TheSoftwareHouse/agentic-collections" />
                <span className="pr">&gt;</span> /plugin marketplace add \<br />
                &nbsp;&nbsp;TheSoftwareHouse/
                <br />
                &nbsp;&nbsp;agentic-collections
                <br />
                <br />
                <span className="d">▸ Core</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <span className="mu">{pluginCount('core')}</span>
                <br />
                <span className="d">▸ Disciplines</span>&nbsp;
                <span className="mu">{pluginCount('discipline')}</span>
                <br />
                <span className="d">▸ Stacks</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <span className="mu">{pluginCount('stack')}</span>
                <br />
                <span className="ok2">✓</span> Catalog registered
              </div>
            </div>
            <div className="su-c">
              <div>
                <span className="n">02</span>
                <h3>Install, then sign in</h3>
                <p>
                  <code>/plugin install tsh-core@tsh-agentic-collections</code>, plus your
                  discipline and the repo's stacks; run <code>/reload-plugins</code> if the install
                  asks. Then <code>/mcp</code> signs you in to Jira and Figma, once per machine.
                </p>
              </div>
              <div className="su-v su-cn">
                <div className="cn-r">
                  <img src="/img/home/icon-terminal.png" alt="" />
                  <div>
                    <b>Claude Code</b>
                    <small>v2.1 or newer</small>
                  </div>
                  <span className="ok">● Installed</span>
                </div>
                <div className="cn-r">
                  <img src="/img/home/asset-03-b084c527.png" alt="" />
                  <div>
                    <b>Jira</b>
                    <small>Via Atlassian MCP</small>
                  </div>
                  <span className="ok">● Connected</span>
                </div>
                <div className="cn-r">
                  <img src="/img/home/asset-06-05b9c8ec.png" alt="" />
                  <div>
                    <b>Confluence</b>
                    <small>Via Atlassian MCP</small>
                  </div>
                  <span className="ok">● Connected</span>
                </div>
                <div className="cn-r">
                  <img src="/img/home/asset-04-34ed93f4.png" alt="" />
                  <div>
                    <b>Figma</b>
                    <small>Via Figma MCP</small>
                  </div>
                  <span className="ok">● Connected</span>
                </div>
                <div className="cn-r">
                  <img src="/img/home/asset-08-ba9638a3.png" alt="" />
                  <div>
                    <b>Playwright CLI</b>
                    <small>Separate install</small>
                  </div>
                  <span className="ok">● On your machine</span>
                </div>
              </div>
            </div>
            <div className="su-c">
              <div>
                <span className="n">03</span>
                <h3>Run it on a ticket</h3>
                <p>
                  Claude plans, builds and reviews. You approve the plan first and get the report at
                  the end.
                </p>
              </div>
              <div className="su-v su-run">
                <span className="cmd">Implement PROJ-123</span>
                <div className="box">
                  <div className="su-s">
                    <i>✓</i>Plan<em>creating-implementation-plans</em>
                  </div>
                  <div className="su-s">
                    <i>✓</i>Code and tests<em>software-engineer</em>
                  </div>
                  <div className="su-s">
                    <i>✓</i>Review: approve<em>code-reviewer</em>
                  </div>
                  <div className="su-s">
                    <i>✓</i>Scenarios pass<em>feature-verifier</em>
                  </div>
                  <div className="ap">Report: what shipped, review, verification</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
