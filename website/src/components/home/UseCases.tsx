import React from 'react';
import catalog from '@site/src/data/catalog.generated.json';

const agentCount = (plugin: string): string => {
  const n = catalog.plugins.find((p) => p.name === plugin)?.agents.length ?? 0;
  return `${n} ${n === 1 ? 'agent' : 'agents'}`;
};

export default function UseCases(): React.JSX.Element {
  return (
    <>
      <section className="sec pzs" id="uc">
        <div className="wrap">
          {/* PHASE2(narrative): five cards, one per vertical (Product Management, Testing, Engineering, Platform, context management), poured into the source site's five card slots — the slots and their visuals were drawn for that product's agent hand-off chain (analyst → architect → engineering manager → reviewers), so each vertical got the nearest visual rather than one of its own — tell the story per discipline, with a card layout chosen for each vertical */}
          <h2>
            Plugins for how each discipline works,
            <br />
            and for the context they all&nbsp;share
          </h2>
          <div className="pz-grid">
            <div className="pz pz-bk tint-o">
              <div className="pz-t">
                <div className="pz-top">
                  <span className="pz-ag">
                    <span className="agvs">
                      <span className="agv sm" style={{ background: '#ffc269' }}>
                        <svg
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="#fff"
                          strokeWidth="2.2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M9 4h6v3H9z" />
                          <path d="M8 5H6v15h12V5h-2" />
                          <path d="M9 11h6M9 15h4" />
                        </svg>
                      </span>
                      <span className="agv sm" style={{ background: '#ffc269' }}>
                        <svg
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="#fff"
                          strokeWidth="2.2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <circle cx="11" cy="11" r="6" />
                          <path d="M20 20l-4.5-4.5" />
                        </svg>
                      </span>
                    </span>
                    Product Management · {agentCount('tsh-product-management')}
                  </span>
                  <a className="pz-lk" href="/docs/workflows/business-analysis">
                    See the workflow →
                  </a>
                </div>
                <h3>Turns workshop material into a Jira-ready backlog</h3>
              </div>
              <div className="feed">
                <div className="fsrc">
                  <div className="fs">
                    <span className="fi">
                      <svg
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#313435"
                        strokeWidth="1.6"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16v4z" />
                        <path d="M13.5 6.5l4 4" />
                      </svg>
                    </span>
                    <div>
                      <b>Workshop</b>
                      <small>transcript</small>
                    </div>
                  </div>
                  <div className="fs">
                    <span className="fi">
                      <img src="/img/home/asset-03-b084c527.png" alt="" />
                    </span>
                    <div>
                      <b>Jira</b>
                      <small>existing backlog</small>
                    </div>
                  </div>
                  <div className="fs">
                    <span className="fi">
                      <img src="/img/home/asset-04-34ed93f4.png" alt="" />
                    </span>
                    <div>
                      <b>Figma</b>
                      <small>designs and FigJam</small>
                    </div>
                  </div>
                  <div className="fs">
                    <span className="fi">
                      <svg
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#313435"
                        strokeWidth="1.6"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M6 3h8l4 4v14H6z" />
                        <path d="M14 3v4h4M9 13h6M9 17h4" />
                      </svg>
                    </span>
                    <div>
                      <b>PDF</b>
                      <small>briefs and specs</small>
                    </div>
                  </div>
                  <div className="fs">
                    <span className="fi">
                      <img src="/img/home/asset-06-05b9c8ec.png" alt="" />
                    </span>
                    <div>
                      <b>Confluence</b>
                      <small>linked pages</small>
                    </div>
                  </div>
                  <div className="fs">
                    <span className="fi">
                      <img src="/img/home/asset-02-0962e269.png" alt="" />
                    </span>
                    <div>
                      <b>Codebase</b>
                      <small>what exists today</small>
                    </div>
                  </div>
                </div>
                <svg className="farr" width="56" height="345" viewBox="0 0 56 345" fill="none">
                  <g stroke="#e0a352" strokeWidth="1.4" strokeDasharray="4 4">
                    <path d="M0 25 C30 25 26 172 54 172" />
                    <path d="M0 84 C30 84 26 172 54 172" />
                    <path d="M0 143 C30 143 26 172 54 172" />
                    <path d="M0 202 C30 202 26 172 54 172" />
                    <path d="M0 261 C30 261 26 172 54 172" />
                    <path d="M0 320 C30 320 26 172 54 172" />
                  </g>
                </svg>
                <div className="fboard">
                  <div className="v">
                    <div className="v-h">
                      <img
                        src="/img/home/asset-03-b084c527.png"
                        alt="Jira"
                        style={{ height: '20px' }}
                      />
                      <b>PROJ · Epic: Payouts</b>
                      <small>Pushed only after you approve Gate 2</small>
                    </div>
                    <div className="jb">
                      <div className="jc">
                        <div className="t">Retry payout on bank timeout</div>
                        <div className="ac">✓ 4 acceptance criteria</div>
                        <div className="m">
                          <i>PROJ-201</i>Story
                        </div>
                      </div>
                      <div className="jc">
                        <div className="t">Notify ops after 3rd failed attempt</div>
                        <div className="ac">✓ 3 acceptance criteria</div>
                        <div className="m">
                          <i>PROJ-202</i>Story
                        </div>
                      </div>
                      <div className="jc">
                        <div className="t">Show payout status to the merchant</div>
                        <div className="ac">✓ 5 acceptance criteria</div>
                        <div className="m">
                          <i>PROJ-203</i>Story
                        </div>
                      </div>
                      <div className="jc">
                        <div className="t">Audit log for every retry</div>
                        <div className="ac">✓ 3 acceptance criteria</div>
                        <div className="m">
                          <i>PROJ-204</i>Story
                        </div>
                      </div>
                      <div className="jc">
                        <div className="t">Cap retries to bank rate limits</div>
                        <div className="ac">✓ 2 acceptance criteria</div>
                        <div className="m">
                          <i>PROJ-205</i>Story
                        </div>
                      </div>
                      <div className="jc">
                        <div className="t">Admin view of failed payouts</div>
                        <div className="ac">✓ 4 acceptance criteria</div>
                        <div className="m">
                          <i>PROJ-206</i>Story
                        </div>
                      </div>
                      <div className="jmore">+ 18 more stories in 3 epics</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="pz pz-pl tint-p">
              <div className="pz-t">
                <div className="pz-top">
                  <span className="pz-ag">
                    <span className="agvs">
                      <span className="agv sm" style={{ background: '#9d8cf3' }}>
                        <svg
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="#fff"
                          strokeWidth="2.2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M9 3h6M10 3v6l-5 10h14L14 9V3" />
                        </svg>
                      </span>
                    </span>
                    Product Testing · {agentCount('tsh-product-testing')}
                  </span>
                  <a className="pz-lk" href="/docs/plugins/tsh-product-testing/">
                    See the plugin →
                  </a>
                </div>
                <h3>Writes end-to-end tests and proves them stable before handing them over</h3>
              </div>
              <div className="pz-v">
                <div className="pled">
                  <div className="pled-h">
                    <span className="dots">
                      <i></i>
                      <i></i>
                      <i></i>
                    </span>
                    <b>retry.spec.ts</b>
                    <small>3/3 headless runs</small>
                  </div>
                  <div className="pled-b">
                    <div>
                      <em>1</em>
                      <span className="m">{'// PROJ-201 · criterion 1'}</span>
                    </div>
                    <div>
                      <em>2</em>
                      <span className="s">{"test('retries a payout',"}</span>
                    </div>
                    <div>
                      <em>3</em>
                      <span className="s">{'async ({ page }) => {'}</span>
                    </div>
                    <div>
                      <em>4</em>
                      <span className="s">{'  const po ='}</span>
                    </div>
                    <div>
                      <em>5</em>
                      <span className="s">{'    new PayoutsPage(page);'}</span>
                    </div>
                    <div>
                      <em>6</em>
                      <span className="s">{"  await po.open('PO-1042');"}</span>
                    </div>
                    <div>
                      <em>7</em>
                      <span className="s">{'  await po.retry();'}</span>
                    </div>
                    <div>
                      <em>8</em>
                      <span className="s">{'  await expect(po.status)'}</span>
                    </div>
                    <div>
                      <em>9</em>
                      <span className="s">{"    .toHaveText('Paid');"}</span>
                    </div>
                    <div>
                      <em>10</em>
                      <span className="s">{'});'}</span>
                    </div>
                    <div>
                      <em>11</em>
                      <span className="h">{'// ✓ user-visible locators'}</span>
                    </div>
                    <div>
                      <em>12</em>
                      <span className="h">{'// ✓ no waitForTimeout'}</span>
                    </div>
                    <div className="cur">
                      <em>13</em>
                      <span className="cursor"></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="pz pz-dg tint-p">
              <div className="pz-t">
                <div className="pz-top">
                  <span className="pz-ag">
                    <span className="agvs">
                      <span className="agv sm" style={{ background: '#9d8cf3' }}>
                        <svg
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="#fff"
                          strokeWidth="2.2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <rect x="9" y="3" width="6" height="5" rx="1" />
                          <rect x="3" y="16" width="6" height="5" rx="1" />
                          <rect x="15" y="16" width="6" height="5" rx="1" />
                          <path d="M12 8v4M6 16v-4h12v4" />
                        </svg>
                      </span>
                    </span>
                    Product Engineering · {agentCount('tsh-product-engineering')}
                  </span>
                  <a className="pz-lk" href="/docs/workflows/feature-implementation">
                    See the workflow →
                  </a>
                </div>
                <h3>Plans the work, then hands it to specialized agents</h3>
              </div>
              <div className="pz-v">
                <div className="hb">
                  <svg className="hbl" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <g
                      stroke="#a99cf0"
                      strokeWidth="1.5"
                      strokeDasharray="4 4"
                      vectorEffect="non-scaling-stroke"
                    >
                      <line x1="50" y1="50" x2="19" y2="12" />
                      <line x1="50" y1="50" x2="81" y2="12" />
                      <line x1="50" y1="50" x2="19" y2="88" />
                      <line x1="50" y1="50" x2="81" y2="88" />
                    </g>
                  </svg>
                  <div className="hbn" style={{ left: '19%', top: '12%' }}>
                    <span className="agv" style={{ background: '#ffc269' }} title="UI">
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#fff"
                        strokeWidth="2.2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M4 20c3 0 4-1.5 4-3.5S9.5 13 11 13s3 1.5 3 3.5" />
                        <path d="M11 13l8-9 1 1-8 9" />
                      </svg>
                    </span>
                    <div>
                      <b>ui-engineer</b>
                      <span>✓ Figma gate passed</span>
                    </div>
                  </div>
                  <div className="hbn" style={{ left: '81%', top: '12%' }}>
                    <span className="agv" style={{ background: '#9d8cf3' }} title="SE">
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#fff"
                        strokeWidth="2.2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M8 7l-5 5 5 5M16 7l5 5-5 5" />
                      </svg>
                    </span>
                    <div>
                      <b>software-engineer</b>
                      <span>✓ tasks done</span>
                    </div>
                  </div>
                  <div className="hbn" style={{ left: '19%', top: '88%' }}>
                    <span className="agv" style={{ background: '#8fcaf2' }} title="CR">
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#fff"
                        strokeWidth="2.2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <circle cx="6" cy="6" r="2.2" />
                        <circle cx="6" cy="18" r="2.2" />
                        <circle cx="18" cy="18" r="2.2" />
                        <path d="M6 8.2v7.6M18 15.8V9a3 3 0 0 0-3-3h-4" />
                        <path d="M13 4l-2 2 2 2" />
                      </svg>
                    </span>
                    <div>
                      <b>code-reviewer</b>
                      <span>✓ approve</span>
                    </div>
                  </div>
                  <div className="hbn" style={{ left: '81%', top: '88%' }}>
                    <span className="agv" style={{ background: '#ffc269' }} title="FV">
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#fff"
                        strokeWidth="2.2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z" />
                        <circle cx="12" cy="12" r="2.6" />
                      </svg>
                    </span>
                    <div>
                      <b>feature-verifier</b>
                      <span>✓ 3/3 scenarios</span>
                    </div>
                  </div>
                  <div className="hbc">
                    <span
                      className="agv"
                      style={{ background: '#9d8cf3' }}
                      title="Main conversation"
                    >
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#fff"
                        strokeWidth="2.2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <rect x="9" y="3" width="6" height="5" rx="1" />
                        <rect x="3" y="16" width="6" height="5" rx="1" />
                        <rect x="15" y="16" width="6" height="5" rx="1" />
                        <path d="M12 8v4M6 16v-4h12v4" />
                      </svg>
                    </span>
                    <b>Main conversation</b>
                    <span>orchestrating-feature-implementation skill</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="pz pz-rv tint-b">
              <div className="pz-t">
                <div className="pz-top">
                  <span className="pz-ag">
                    <span className="agvs">
                      <span className="agv sm" style={{ background: '#8fcaf2' }}>
                        <svg
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="#fff"
                          strokeWidth="2.2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M4 6l5 5-5 5M12 18h8" />
                        </svg>
                      </span>
                    </span>
                    Platform Engineering · {agentCount('tsh-platform-engineering')}
                  </span>
                  <a className="pz-lk" href="/docs/plugins/tsh-platform-engineering/">
                    See the plugin →
                  </a>
                </div>
                <h3>
                  Builds and audits infrastructure, and never applies it unless you name
                  the&nbsp;command
                </h3>
              </div>
              <div className="pz-v">
                <div className="rvs">
                  <div className="rvs-card">
                    <div className="rvs-h">
                      <b>infrastructure-auditor · payments-api</b>
                      <span>1 High</span>
                    </div>
                    <div className="rvs-code">
                      <div className="fn">infra/iam.tf</div>
                      <div className="">
                        <em>12</em>data "aws_iam_policy_document" "worker" &#123;
                      </div>
                      <div className="">
                        <em>13</em>
                        {'  statement {'}
                      </div>
                      <div className="bad">
                        <em>14</em>
                        {'    actions   = ["s3:*"]'}
                      </div>
                      <div className="bad">
                        <em>15</em>
                        {'    resources = ["*"]'}
                      </div>
                      <div className="">
                        <em>16</em>
                        {'  }'}
                      </div>
                      <div className="">
                        <em>17</em>&#125;
                      </div>
                      <div className="">
                        <em>18</em>
                      </div>
                      <div className="">
                        <em>19</em>resource "aws_iam_role_policy" "worker" &#123;
                      </div>
                      <div className="">
                        <em>20</em>&#125;
                      </div>
                    </div>
                    <div className="rvs-note">
                      <span>High</span>
                      <p>
                        Wildcard actions on every resource. Scope the policy to the bucket it reads.
                      </p>
                    </div>
                  </div>
                  <div className="rvs-you">
                    <span className="av">You</span>
                    <b>devops-engineer: plan validated, cost impact reported</b>
                    <code>terraform apply ← you run this</code>
                  </div>
                </div>
              </div>
            </div>
            <div className="pz pz-ui tint-b">
              <div className="pz-t">
                <div className="pz-top">
                  <span className="pz-ag">
                    <span className="agvs">
                      <span className="agv sm" style={{ background: '#8fcaf2' }}>
                        <svg
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="#fff"
                          strokeWidth="2.2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M6 3h8l4 4v14H6z" />
                          <path d="M14 3v4h4M9 13h6M9 17h4" />
                        </svg>
                      </span>
                    </span>
                    Context management · tsh-core and tsh-product-management
                  </span>
                  <a className="pz-lk" href="/docs/workflows/project-context">
                    See the workflow →
                  </a>
                </div>
                <h3>Keeps what the project knows where Claude reads&nbsp;it</h3>
              </div>
              <div className="pz-v">
                <div className="ul">
                  <div className="ul-pair">
                    <div className="ul-s d">
                      <span className="ul-lb">CLAUDE.md</span>
                      <i className="t"></i>
                      <i className="l"></i>
                      <i className="l s"></i>
                      <i className="b"></i>
                    </div>
                    <span className="ul-eq">→</span>
                    <div className="ul-s bd">
                      <span className="ul-lb">&lt;project&gt;-context</span>
                      <i className="t"></i>
                      <i className="l"></i>
                      <i className="l s"></i>
                      <i className="b ulmk"></i>
                    </div>
                  </div>
                  <div className="ul-it">
                    <span>/tsh-core:init</span>
                    <span>CLAUDE.md, rules, decision index</span>
                  </div>
                  <div className="ul-it">
                    <span>initializing-project-context</span>
                    <span className="ok">✓ navigating-project-context cites every fact</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
