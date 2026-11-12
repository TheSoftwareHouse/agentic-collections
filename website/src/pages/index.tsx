import React from 'react';
import Head from '@docusaurus/Head';
import Layout from '@theme/Layout';
import HomeNav from '@site/src/components/home/HomeNav';
import Hero from '@site/src/components/home/Hero';
import UseCases from '@site/src/components/home/UseCases';
import Skills from '@site/src/components/home/Skills';
import Proof from '@site/src/components/home/Proof';
import Setup from '@site/src/components/home/Setup';
import TshBlock from '@site/src/components/home/TshBlock';
import HomeFooter from '@site/src/components/home/HomeFooter';
import '@site/src/components/home/home.css';
import catalog from '@site/src/data/catalog.generated.json';

const { totals } = catalog;

// PHASE2(narrative): page meta "Claude Code plugins for the agentic SDLC" — adapted from the source site's "open-source framework for the agentic SDLC"; this repo is a plugin marketplace, not a framework — rewrite together with the Hero headline
const TITLE = 'Agentic Collections | Claude Code plugins for the agentic SDLC';
// TODO(marketing): confirm before publishing
const DESCRIPTION = `Open-source Claude Code plugins from The Software House: ${totals.skills} skills and ${totals.agents} agents for product management, engineering, testing and platform work. 40% shorter lead time. MIT license.`;
const SOCIAL_TITLE = 'Agentic Collections: Claude Code plugins for the agentic SDLC';
const SOCIAL_DESCRIPTION = `${totals.skills} skills and ${totals.agents} agents take work from workshop notes to a Jira backlog, and from a ticket to a reviewed change. Every non-trivial change starts from a plan you have approved.`;

export default function Home(): React.JSX.Element {
  return (
    <Layout description={DESCRIPTION} noFooter>
      <Head>
        <title>{TITLE}</title>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500;600&display=swap"
          rel="stylesheet"
        />
        <meta property="og:title" content={SOCIAL_TITLE} />
        <meta property="og:description" content={SOCIAL_DESCRIPTION} />
        <meta property="og:image:alt" content={SOCIAL_TITLE} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={SOCIAL_TITLE} />
        <meta name="twitter:description" content={SOCIAL_DESCRIPTION} />
        <meta name="twitter:image:alt" content={SOCIAL_TITLE} />
      </Head>
      <div className="cc-home">
        <HomeNav />
        <Hero />
        <UseCases />
        <Skills />
        <Proof />
        <Setup />
        <TshBlock />
        <HomeFooter />
      </div>
    </Layout>
  );
}
