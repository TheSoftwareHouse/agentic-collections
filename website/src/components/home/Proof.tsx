import React from 'react';

export default function Proof(): React.JSX.Element {
  return (
    <>
      <section className="sec">
        <div className="wrap">
          {/* PHASE2(narrative): the whole section — heading, 40%, 2–3×, the US healthtech case study and the footnote are the source site's proof, kept verbatim — they measured that product, not these plugins — replace with evidence gathered for Agentic Collections */}
          {/* TODO(marketing): "Battle-tested on commercial projects" is the source site's claim; confirm it holds for these plugins */}
          <h2 style={{ maxWidth: 'none' }}>Battle-tested on commercial projects</h2>
          <div className="pr-grid">
            {/* TODO(marketing): "40% shorter lead time on average" is the source site's figure, kept verbatim. Conflicts with docs/for-ctos.md (30%) */}
            <div className="prc">
              <b className="big">
                40%<sup>*</sup>
              </b>
              <span>shorter lead time on average</span>
            </div>
            {/* TODO(marketing): "2–3× faster requirement gathering" is the source site's figure, kept verbatim */}
            <div className="prc">
              <b className="big" style={{ whiteSpace: 'nowrap', fontSize: '104px' }}>
                2–3×
              </b>
              <span>faster requirement gathering</span>
            </div>
            {/* TODO(marketing): the case study (1 developer in the time of 3, 600 tasks from the BA agent, 30–40 min per feature) describes the source site's product, kept verbatim */}
            <a className="prc case" href="https://tsh.io/portfolio/100-percent-ai-driven-project">
              <span className="tag">Case study · US healthtech</span>
              <h3 className="q">
                &ldquo;We delivered a full project with 1&nbsp;developer in the time 3&nbsp;would
                normally take.&rdquo;
              </h3>
              <div className="facts">
                <div>
                  <strong>600</strong>
                  <small>tasks from the BA agent</small>
                </div>
                <div>
                  <strong>30–40</strong>
                  <small>min per feature</small>
                </div>
              </div>
              <span className="case-link">Read the case study →</span>
            </a>
          </div>
          {/* TODO(marketing): footnote for the 40% figure, kept verbatim. Conflicts with docs/for-ctos.md (30%) */}
          <p className="pr-note">
            * Average across several AI agentic projects at The Software House, compared with the
            same teams before adoption.
          </p>
        </div>
      </section>
    </>
  );
}
