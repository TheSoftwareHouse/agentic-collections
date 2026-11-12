import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// The container ID is not committed: it is set in Vercel (see .env.example). Without it the
// site ships no Google Tag Manager at all.
const gtmContainerId = process.env.GTM_CONTAINER_ID;

const config: Config = {
  title: 'Agentic Collections',
  // PHASE2(narrative): provisional tagline derived from the README; Phase 2 writes the real one.
  tagline:
    'A Claude Code plugin marketplace by The Software House: skills and agents for how we work, what we work with, and a small core under both',
  favicon: 'img/favicon.ico',

  url: 'https://agentic-collections.tsh.io',
  baseUrl: '/',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: 'docs',
          admonitions: {
            keywords: ['note', 'tip', 'info', 'warning', 'danger', 'brand'],
          },
        },
        blog: false,
        pages: {},
        theme: {
          customCss: './src/css/custom.css',
        },
        ...(gtmContainerId ? { googleTagManager: { containerId: gtmContainerId } } : {}),
      } satisfies Preset.Options,
    ],
  ],

  themes: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        indexBlog: false,
      },
    ],
  ],

  headTags: [
    {
      tagName: 'link',
      attributes: {
        rel: 'preconnect',
        href: 'https://fonts.googleapis.com',
      },
    },
    {
      tagName: 'link',
      attributes: {
        rel: 'preconnect',
        href: 'https://fonts.gstatic.com',
        crossorigin: 'anonymous',
      },
    },
    {
      tagName: 'link',
      attributes: {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap',
      },
    },
  ],

  themeConfig: {
    image: 'img/opengraph.png',
    metadata: [
      {
        property: 'og:type',
        content: 'website',
      },
      {
        property: 'og:image:width',
        content: '1200',
      },
      {
        property: 'og:image:height',
        content: '630',
      },
      {
        property: 'og:image:alt',
        content:
          'Agentic Collections social preview: a Claude Code session implementing a ticket with TSH plugins, from plan to code review and functional verification.',
      },
      {
        name: 'twitter:image:alt',
        content: 'Agentic Collections by The Software House',
      },
    ],
    navbar: {
      title: 'Agentic Collections',
      logo: {
        alt: 'Agentic Collections',
        src: 'img/logo-white.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/docs/workflows/overview',
          label: 'Workflows',
          position: 'left',
        },
        {
          to: '/docs/plugins/',
          label: 'Plugins',
          position: 'left',
        },
        {
          to: '/docs/integrations/overview',
          label: 'Integrations',
          position: 'left',
        },
        {
          to: '/docs/use-cases',
          label: 'Use Cases',
          position: 'left',
        },
        {
          to: '/docs/for-ctos',
          label: 'For CTOs',
          position: 'left',
          className: 'navbar__link--cto',
        },
        {
          to: '/docs/category/changelog',
          label: 'Changelog',
          position: 'right',
          className: 'navbar__link--meta',
        },
        {
          href: 'https://github.com/TheSoftwareHouse/agentic-collections',
          html: `
            <span class="navbar__github-content">
              <svg class="navbar__github-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.57.11.78-.25.78-.56 0-.27-.01-1.17-.02-2.12-3.2.7-3.88-1.36-3.88-1.36-.52-1.33-1.28-1.68-1.28-1.68-1.05-.72.08-.71.08-.71 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.69 1.26 3.35.97.1-.75.4-1.26.73-1.55-2.56-.29-5.24-1.28-5.24-5.71 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.04 0 0 .97-.31 3.19 1.18A11.1 11.1 0 0 1 12 6.13c.98 0 1.98.13 2.91.38 2.22-1.49 3.18-1.18 3.18-1.18.64 1.58.24 2.75.12 3.04.74.81 1.19 1.84 1.19 3.1 0 4.44-2.68 5.41-5.25 5.69.41.35.78 1.03.78 2.08 0 1.5-.01 2.71-.01 3.08 0 .31.2.68.79.56A11.5 11.5 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z" />
              </svg>
              <span class="navbar__github-wordmark">GitHub</span>
              <svg class="navbar__github-arrow" viewBox="0 0 12 12" aria-hidden="true">
                <path d="M3 9 9 3M4 3h5v5" />
              </svg>
            </span>
          `,
          position: 'right',
          className: 'navbar__link--github',
        },
      ],
    },
    footer: {
      style: 'light',
      copyright: `agentic-collections · Built by <a href="https://tsh.io" target="_blank" rel="noopener noreferrer">The Software House</a> · MIT license · Free`,
      links: [
        {
          title: ' ',
          items: [
            {
              href: 'https://github.com/TheSoftwareHouse/agentic-collections',
              label: 'GitHub',
            },
            { label: 'Docs', to: '/docs/' },
            { label: 'Workflows', to: '/docs/workflows/overview' },
            { label: 'Plugins', to: '/docs/plugins/' },
            { label: 'Integrations', to: '/docs/integrations/overview' },
            { label: 'Use Cases', to: '/docs/use-cases' },
            { label: 'For CTOs', to: '/docs/for-ctos' },
            { label: 'Changelog', to: '/docs/category/changelog' },
            {
              label: 'tsh.io',
              href: 'https://tsh.io',
            },
          ],
        },
      ],
    },
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: true,
      respectPrefersColorScheme: false,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
