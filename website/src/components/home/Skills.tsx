import React from 'react';
import catalog from '@site/src/data/catalog.generated.json';
import featured from '@site/src/data/home-featured.json';

const { totals } = catalog;
const plugins = catalog.plugins.filter((p) => !p.empty);

type Plugin = (typeof catalog.plugins)[number];

/** "TSH Stack: Node.js" → "Node.js", "TSH Product Engineering" → "Product Engineering". */
const shortName = (p: Plugin): string => p.displayName.replace(/^TSH (Stack: )?/, '');
const skillCount = (list: Plugin[]): number => list.reduce((sum, p) => sum + p.skills.length, 0);
const pluginWord = (n: number): string => `${n} ${n === 1 ? 'plugin' : 'plugins'}`;

const disciplines = plugins.filter((p) => p.family === 'discipline');
const stacks = plugins.filter((p) => p.family === 'stack');
const core = plugins.filter((p) => p.family === 'core');
// The marketplace files cloud providers under "platform" and runtime targets under "engineering".
const cloudStacks = stacks.filter((p) => p.category === 'platform');
const runtimeStacks = stacks.filter((p) => p.category !== 'platform');

const FAMILIES = [
  {
    label: `Disciplines · ${pluginWord(disciplines.length)}`,
    skills: skillCount(disciplines),
    names: disciplines.map(shortName).join(' · '),
  },
  {
    label: `Stacks · ${pluginWord(stacks.length)}`,
    skills: skillCount(stacks),
    names: `Runtime: ${runtimeStacks.map(shortName).join(', ')} · Cloud: ${cloudStacks.map(shortName).join(', ')}`,
  },
  {
    label: 'Core · tsh-core',
    skills: skillCount(core),
    names: 'Needed regardless of discipline or stack',
  },
];

/** The cloud shows the components the ranking put first, grouped by the plugin that ships them. */
const featuredGroups: { title: string; chips: { text: string; href: string; label: string }[] }[] =
  [];
for (const { component, label } of featured.featured) {
  const [pluginName, kind, name] = component.split('/');
  const plugin = plugins.find((p) => p.name === pluginName);
  if (!plugin) continue; // sync-catalog --check fails the build before this can happen
  const title = plugin.family === 'stack' ? 'Stacks' : shortName(plugin);
  let group = featuredGroups.find((g) => g.title === title);
  if (!group) featuredGroups.push((group = { title, chips: [] }));
  group.chips.push({
    text: name, // the group names the plugin; the docs page shows the full /plugin:skill form
    href: `/docs/plugins/${pluginName}/${kind}/${name}`,
    label,
  });
}
const featuredCount = featured.featured.length;

/** One avatar per discipline, in the colour and icon its card uses. */
const AVATARS: Record<string, { color: string; icon: React.JSX.Element }> = {
  'tsh-product-management': {
    color: '#ffc269',
    icon: (
      <>
        <path d="M9 4h6v3H9z" />
        <path d="M8 5H6v15h12V5h-2" />
        <path d="M9 11h6M9 15h4" />
      </>
    ),
  },
  'tsh-product-testing': {
    color: '#9d8cf3',
    icon: <path d="M9 3h6M10 3v6l-5 10h14L14 9V3" />,
  },
  'tsh-product-engineering': {
    color: '#9d8cf3',
    icon: (
      <>
        <rect x="9" y="3" width="6" height="5" rx="1" />
        <rect x="3" y="16" width="6" height="5" rx="1" />
        <rect x="15" y="16" width="6" height="5" rx="1" />
        <path d="M12 8v4M6 16v-4h12v4" />
      </>
    ),
  },
  'tsh-platform-engineering': {
    color: '#8fcaf2',
    icon: <path d="M4 6l5 5-5 5M12 18h8" />,
  },
};

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
            <div className="cats">
              {FAMILIES.map(({ label, skills, names }) => (
                <div key={label}>
                  <p>
                    {label}
                    <small>{names}</small>
                  </p>
                  <span>{skills} skills</span>
                </div>
              ))}
            </div>
            <p className="skl-foot">
              Wrote a skill your team relies on? Contribute it, and everyone who installs that
              plugin gets it with the next release, on their next <code>/plugin update</code>. To
              write one, start with{' '}
              <a className="inl" href="/docs/plugins/tsh-core/skills/authoring-claude-extensions">
                authoring-claude-extensions
              </a>
              .
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
                  Skills and agents to start with
                </div>
                {/* TODO(marketing): the cloud lists the ranking's tier A (src/data/home-featured.json). How often teams run the cloud cost audits is not in the repository (component-ranking.md, question 4) — confirm they belong here */}
                <div className="cloud-g">
                  {featuredGroups.map(({ title, chips }) => (
                    <div key={title}>
                      <h4>{title}</h4>
                      <div className="cloud">
                        {chips.map(({ text, href, label }) => (
                          <a key={href} href={href} title={label} aria-label={`${text}: ${label}`}>
                            {text}
                          </a>
                        ))}
                      </div>
                    </div>
                  ))}
                  <div className="cloud">
                    <a className="more" href="/docs/plugins/">
                      +{totals.skills + totals.agents - featuredCount} more
                    </a>
                  </div>
                </div>
                <div className="ld">
                  <div className="ld-av">
                    {disciplines.map((p) => {
                      const avatar = AVATARS[p.name];
                      return (
                        <span
                          key={p.name}
                          style={{ background: avatar?.color ?? '#9d8cf3' }}
                          title={shortName(p)}
                        >
                          <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="#fff"
                            strokeWidth="2.2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          >
                            {avatar?.icon}
                          </svg>
                        </span>
                      );
                    })}
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
