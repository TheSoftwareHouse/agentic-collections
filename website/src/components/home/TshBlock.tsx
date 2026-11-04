import React from 'react';

export default function TshBlock(): React.JSX.Element {
  return (
    <>
      <section className="tsh">
        <div className="wrap">
          {/* PHASE2(narrative): two TSH offer cards — copy inherited from the source site; "this framework" became "these plugins", nothing else changed — rewrite the offers around the marketplace once marketing confirms them */}
          <h2 className="tsh-h">Want a team that already works this&nbsp;way?</h2>
          <div className="tsh-grid">
            {/* TODO(marketing): "a self-managed team in 2 weeks" and "senior engineers who run these plugins on client projects" (the source site said "this framework") — confirm both */}
            <a className="tc t1" href="https://tsh.io/contact-us">
              <b>Work with The Software House</b>
              <span>
                A self-managed team in 2 weeks: senior engineers who run these plugins on client
                projects.
              </span>
              <span className="tc-link">Talk to an engineer →</span>
            </a>
            {/* TODO(marketing): confirm the AI Enablement program covers adopting these plugins */}
            <a className="tc t2" href="https://tsh.io/services/ai-enablement">
              <b>Roll it out in your team</b>
              <span>
                Our AI Enablement program covers training and support while your engineers adopt it.
              </span>
              <span className="tc-link">See AI Enablement →</span>
            </a>
          </div>
        </div>
      </section>
    </>
  );
}
