import React from 'react';
import catalog from '@site/src/data/catalog.generated.json';
import GhStars from './GhStars';

const { totals } = catalog;
// The marketplace also lists empty scaffolds; count only plugins that ship something.
const shippingPlugins = catalog.plugins.filter((p) => !p.empty).length;

export default function Hero(): React.JSX.Element {
  return (
    <>
      <section className="home-hero">
        <div className="wrap">
          <div className="hero-head">
            <div>
              {/* PHASE2(narrative): headline "Claude Code plugins for the agentic SDLC" — adapted from the source site's "An open-source framework for the agentic SDLC"; this repo is a plugin marketplace, not a framework — write a headline for the marketplace itself (three families, install only what your job and repo need) */}
              <h1>
                Claude Code plugins <span>for the agentic&nbsp;SDLC</span>
              </h1>
            </div>
            <div style={{ paddingTop: '12px' }}>
              <p className="lead">
                {totals.skills} skills and {totals.agents} agents in {shippingPlugins} plugins take
                work from workshop notes to a Jira backlog, and from a ticket to a reviewed change.
                Every non-trivial change starts from a plan you have approved.
              </p>
              <div className="ctas">
                <a
                  className="btn btn-p"
                  href="https://github.com/TheSoftwareHouse/agentic-collections"
                >
                  <img src="/img/home/asset-02-0962e269.png" alt="" />
                  Get it on GitHub{' '}
                  <em>
                    ★ <GhStars />
                  </em>
                </a>
                <a className="btn btn-g" href="/docs/">
                  Read the docs
                </a>
              </div>
            </div>
          </div>
          <div className="hero-stage">
            {/* PHASE2(visual): a Claude Code terminal session with the plan file in a side pane, drawn inside the frame, size and palette of the source site's IDE mock — the frame, the side-column width and the ticket-to-review story are inherited from that mock — design a terminal scene of our own, kept in step with the OG image (website/scripts/og/og.html) */}
            <div className="vs">
              <div className="vs-top">
                <i></i>
                <i></i>
                <i></i>
                <span className="vs-cc">payments-api — claude</span>
              </div>
              <div className="term">
                <div className="term-s">
                  <div className="term-u">&gt; Implement PROJ-123</div>
                  <div className="term-e">
                    <div>
                      <i className="p">⏺</i>Skill
                      <span className="term-sk">
                        tsh-product-engineering:orchestrating-feature-implementation
                      </span>
                    </div>
                    <div className="term-r">⎿ No plan for PROJ-123 yet, so one comes first</div>
                  </div>
                  <div className="term-e">
                    <div>
                      <i className="p">⏺</i>Skill
                      <span className="term-sk">
                        tsh-product-engineering:creating-implementation-plans
                      </span>
                    </div>
                    <div className="term-r">
                      ⎿ Wrote <b>specifications/PROJ-123/payout-retry.plan.md</b> · 2 phases, 4
                      tasks
                    </div>
                    <div className="term-r">
                      ⎿ Drafted <b>payout-retry.verification.md</b> · 3 scenarios you picked
                    </div>
                  </div>
                  <div className="term-q">
                    <div className="term-qt">The plan is ready. Read it, then choose:</div>
                    <div className="on">❯ Execute the plan</div>
                    <div>&nbsp;&nbsp;Wait — I want changes</div>
                  </div>
                  <div className="term-e">
                    <div>
                      <i>⏺</i>
                      <b>@tsh-product-engineering:software-engineer</b> ×2 · Tasks 1.1 and 1.2,
                      parallel group A
                    </div>
                    <div className="term-r">
                      ⎿ <span className="term-ok">✓</span> Definition of Done passed · plan
                      checkboxes ticked
                    </div>
                    <div className="term-r">
                      ⎿ <span className="term-ok">✓</span> Phase 1 verification passed
                    </div>
                  </div>
                  <div className="term-e">
                    <div>
                      <i>⏺</i>Final verification, in parallel
                    </div>
                    <div className="term-r">
                      ⎿ <b>@tsh-product-engineering:code-reviewer</b>{' '}
                      <span className="term-ok">✓ approve · 0 blockers</span>
                    </div>
                    <div className="term-r">
                      ⎿ <b>@tsh-product-engineering:feature-verifier</b>{' '}
                      <span className="term-ok">✓ 3/3 scenarios pass</span>
                    </div>
                  </div>
                  <div className="term-e">
                    <div>
                      <i>⏺</i>PROJ-123 is ready for your review
                    </div>
                    <div className="term-r">
                      ⎿ What shipped, the review outcome and the verification results
                    </div>
                  </div>
                  <div className="term-in">
                    &gt; <span className="cursor"></span>
                  </div>
                </div>
                <div className="term-side">
                  <div className="term-side-h">specifications/PROJ-123/payout-retry.plan.md</div>
                  <div className="vs-code">
                    <div>
                      <em>1</em>
                      <span className="c-h"># PROJ-123 · Payout retry on bank timeout</span>
                    </div>
                    <div>
                      <em>2</em>
                    </div>
                    <div>
                      <em>3</em>
                      <span className="c-h">## Goal</span>
                    </div>
                    <div>
                      <em>4</em>
                      <span>Retry a timed-out payout, at most 3 times</span>
                    </div>
                    <div>
                      <em>5</em>
                    </div>
                    <div>
                      <em>6</em>
                      <span className="c-h">## Technical Context</span>
                    </div>
                    <div>
                      <em>7</em>
                      <span className="c-m">- Test: npm test · Lint: npm run lint</span>
                    </div>
                    <div>
                      <em>8</em>
                    </div>
                    <div>
                      <em>9</em>
                      <span className="c-h">## Phase 1 — Payouts (parallel group A)</span>
                    </div>
                    <div>
                      <em>10</em>
                      <span className="c-ok">- [x]</span>
                      <span> Task 1.1 </span>
                      <span className="c-k">RetryPolicy</span>
                      <span> with backoff</span>
                    </div>
                    <div>
                      <em>11</em>
                      <span className="c-m">{'      Files: retry.policy.ts (create)'}</span>
                    </div>
                    <div>
                      <em>12</em>
                      <span className="c-ok">- [x]</span>
                      <span> Task 1.2 Bank timeout metric</span>
                    </div>
                    <div>
                      <em>13</em>
                      <span className="c-m">{'      Files: timeout.metric.ts (create)'}</span>
                    </div>
                    <div>
                      <em>14</em>
                      <span className="c-m">Verification: npm test -- payouts</span>
                    </div>
                    <div>
                      <em>15</em>
                    </div>
                    <div>
                      <em>16</em>
                      <span className="c-h">## Phase 2 — Final verification</span>
                    </div>
                    <div>
                      <em>17</em>
                      <span className="c-ok">- [x]</span>
                      <span> Task 2.1 Code review</span>
                    </div>
                    <div>
                      <em>18</em>
                      <span className="c-ok">- [x]</span>
                      <span> Task 2.2 Functional verification</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="vs-st">
                <span>⎇ feature/PROJ-123</span>
                <span>specifications/PROJ-123/</span>
                <span>Claude Code</span>
              </div>
            </div>
          </div>
          {/* PHASE2(visual): stats bar of four figures — layout and the two marketing figures are inherited from the source site, where they described that product — pick the figures that prove this marketplace, all but the marketing ones read from the catalog */}
          <div className="proof">
            <div>
              {/* TODO(marketing): "40% shorter lead time" is the source site's figure, kept verbatim; confirm it holds for these plugins. Conflicts with docs/for-ctos.md (30%) */}
              <b>40%</b>
              <small>shorter lead time</small>
            </div>
            <div>
              {/* TODO(marketing): "300+ engineers use it" is the source site's figure, kept verbatim; confirm it holds for these plugins */}
              <b>300+</b>
              <small>engineers use it</small>
            </div>
            <div>
              <b>{totals.agents}</b>
              <small>specialised AI agents</small>
            </div>
            <div>
              <b>Free</b>
              <small>open source, MIT licence</small>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
