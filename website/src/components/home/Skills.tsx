import React from 'react';
import catalog from '@site/src/data/catalog.generated.json';

const { totals } = catalog;
const plugins = catalog.plugins.filter((p) => !p.empty);

const FAMILIES = [
  { family: 'core', label: 'Core' },
  { family: 'discipline', label: 'Disciplines' },
  { family: 'stack', label: 'Stacks' },
];

/** Skills you can type as a command, taken round-robin across plugins so every plugin shows. */
const CLOUD_SIZE = 16;
const commandSkills = plugins.map((p) => p.skills.filter((s) => s.userInvocable));
const cloud: string[] = [];
for (let round = 0; cloud.length < CLOUD_SIZE; round++) {
  const picked = commandSkills.map((skills) => skills[round]).filter(Boolean);
  if (picked.length === 0) break;
  cloud.push(...picked.slice(0, CLOUD_SIZE - cloud.length).map((s) => s.name));
}

export default function Skills(): React.JSX.Element {
  return (
    <>
      <section className="skl" id="skills">
        <div className="wrap skl-grid">
          <div>
            {/* PHASE2(narrative): heading "N skills of senior know-how across our disciplines and stacks" (the source site said "engineering know-how", which these skills outgrow) and the "160+ projects" lead are inherited from the source site — rewrite for the three plugin families */}
            <h2>
              {totals.skills} skills of senior know&#8209;how across our disciplines and stacks
            </h2>
            <p className="lead">
              {/* TODO(marketing): "160+ projects" is the source site's figure, kept verbatim; confirm it holds for these plugins. Conflicts with docs/for-ctos.md (50+ projects) */}
              Practice drawn from 160+ projects The Software House has delivered, packaged as Claude
              Code plugins. Claude loads the skills a task needs when the work matches their
              description, so you don't have to remember the commands.
            </p>
            {/* PHASE2(narrative): skill categories — the source site listed five hand-counted topic categories; here they are the three plugin families, counted from the catalog — decide whether families or topics are the better grouping for a reader */}
            <div className="cats">
              {FAMILIES.map(({ family, label }) => {
                const inFamily = plugins.filter((p) => p.family === family);
                const skills = inFamily.reduce((sum, p) => sum + p.skills.length, 0);
                return (
                  <div key={family}>
                    {label}
                    {inFamily.length > 1 && ` · ${inFamily.length} plugins`}
                    <span>{skills} skills</span>
                  </div>
                );
              })}
            </div>
            <p className="skl-foot">
              Wrote a skill your team relies on? Contribute it, and everyone who installs that
              plugin gets it with the next release, on their next <code>/plugin update</code>.
              <br />
              <a
                className="contrib"
                href="https://github.com/TheSoftwareHouse/agentic-collections#contributing"
              >
                <img src="/img/home/asset-02-0962e269.png" alt="" />
                Contribute a skill on GitHub →
              </a>
            </p>
          </div>
          <div className="skl-vis">
            <div className="lay">
              <div className="band">
                <div className="bt">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#313435"
                    strokeWidth="1.7"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M12 3l9 5-9 5-9-5 9-5z" />
                    <path d="M3 13l9 5 9-5" />
                  </svg>
                  Claude loads the skills each task needs
                </div>
                <div className="cloud">
                  {cloud.map((name) => (
                    <span key={name}>{name}</span>
                  ))}
                  <span className="more">+{totals.skills - cloud.length} more</span>
                </div>
                {/* PHASE2(visual): row of twelve agent avatars — inherited from the source site, where each stood for one of its agents; here they are decorative and do not map to our agents — draw one avatar per discipline, or drop the row */}
                <div className="ld">
                  <div className="ld-av">
                    <span style={{ background: '#ffc269' }}>
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
                    <span style={{ background: '#9d8cf3' }}>
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
                    <span style={{ background: '#9d8cf3' }}>
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#fff"
                        strokeWidth="2.2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M12 3l9 5-9 5-9-5 9-5z" />
                        <path d="M3 13l9 5 9-5" />
                      </svg>
                    </span>
                    <span style={{ background: '#9d8cf3' }}>
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
                    <span style={{ background: '#9d8cf3' }}>
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
                    <span style={{ background: '#8fcaf2' }}>
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
                    <span style={{ background: '#8fcaf2' }}>
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
                    <span style={{ background: '#8fcaf2' }}>
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
                    <span style={{ background: '#ffc269' }}>
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
                    <span style={{ background: '#9d8cf3' }}>
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
                    <span style={{ background: '#8fcaf2' }}>
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#fff"
                        strokeWidth="2.2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M4 20l4-1 11-11-3-3L5 16z" />
                      </svg>
                    </span>
                    <span style={{ background: '#9d8cf3' }}>
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#fff"
                        strokeWidth="2.2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1" />
                        <circle cx="12" cy="12" r="3" />
                      </svg>
                    </span>
                  </div>
                  <b>{totals.agents} agents ship alongside them</b>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
