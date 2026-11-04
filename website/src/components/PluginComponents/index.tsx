import React from 'react';
import Link from '@docusaurus/Link';
import catalog from '@site/src/data/catalog.generated.json';

type Skill = {
  name: string;
  description: string;
  userInvocable: boolean;
  disableModelInvocation: boolean;
};

type Agent = {
  name: string;
  description: string;
  model: string | null;
};

type Plugin = {
  name: string;
  displayName: string;
  family: 'core' | 'discipline' | 'stack';
  version: string;
  description: string;
  empty: boolean;
  skills: Skill[];
  agents: Agent[];
  mcpServers: string[];
  hasHooks: boolean;
};

const plugins = (catalog as { plugins: Plugin[] }).plugins;

function findPlugin(name: string): Plugin {
  const plugin = plugins.find((p) => p.name === name);
  if (!plugin) throw new Error(`PluginComponents: unknown plugin "${name}"`);
  return plugin;
}

/**
 * How a skill is started, read from its frontmatter flags: `user-invocable: false` removes the
 * command; `disable-model-invocation: true` stops Claude from loading it on its own.
 */
function invocation(plugin: string, skill: Skill): React.ReactNode {
  if (!skill.userInvocable) {
    return skill.disableModelInvocation
      ? 'No command — only agents that preload it'
      : 'No command — Claude or an agent loads it when the work matches';
  }
  const command = <code>{`/${plugin}:${skill.name}`}</code>;
  return skill.disableModelInvocation ? <>{command} (on request only)</> : command;
}

/**
 * The skills and agents a plugin ships, rendered from the catalog generated at build time, so the
 * list can never drift from plugins/.
 */
export default function PluginComponents({ plugin }: { plugin: string }): React.JSX.Element {
  const p = findPlugin(plugin);
  const base = `/docs/plugins/${p.name}`;
  return (
    <>
      {p.skills.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Skill</th>
              <th>Invoke</th>
              <th>What it does</th>
            </tr>
          </thead>
          <tbody>
            {p.skills.map((s) => (
              <tr key={s.name}>
                <td>
                  <Link to={`${base}/skills/${s.name}`}>{s.name}</Link>
                </td>
                <td>{invocation(p.name, s)}</td>
                <td>{s.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {p.agents.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Agent</th>
              <th>Mention</th>
              <th>Model</th>
              <th>What it does</th>
            </tr>
          </thead>
          <tbody>
            {p.agents.map((a) => (
              <tr key={a.name}>
                <td>
                  <Link to={`${base}/agents/${a.name}`}>{a.name}</Link>
                </td>
                <td>
                  <code>{`@${p.name}:${a.name}`}</code>
                </td>
                <td>{a.model ?? '—'}</td>
                <td>{a.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}

/** Every non-empty plugin of one family, linked to its page. */
export function PluginList({ family }: { family: Plugin['family'] }): React.JSX.Element {
  const list = plugins.filter((p) => p.family === family && !p.empty);
  return (
    <table>
      <thead>
        <tr>
          <th>Plugin</th>
          <th>Version</th>
          <th>Skills</th>
          <th>Agents</th>
          <th>Covers</th>
        </tr>
      </thead>
      <tbody>
        {list.map((p) => (
          <tr key={p.name}>
            <td>
              <Link to={`/docs/plugins/${p.name}/`}>{p.name}</Link>
            </td>
            <td>{p.version}</td>
            <td>{p.skills.length}</td>
            <td>{p.agents.length}</td>
            <td>{p.description}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
