# playwright-cli command reference

The subset of `playwright-cli` used for UI verification capture. Full docs:
`playwright-cli --help`.

## Availability and install

```bash
playwright-cli --version                 # global install?
npx --no-install playwright cli --version   # local install? (NOT `playwright-cli`: that npm name is a deprecated package)
npm install -g @playwright/cli@latest    # install globally when neither works
```

When only the local version is available, run every command as `npx playwright cli <cmd>`
in place of `playwright-cli <cmd>`.

## Sessions

Always use a named session so parallel work cannot cross-contaminate, and always
close it:

```bash
playwright-cli open -s ui-verify
playwright-cli list                      # list sessions
playwright-cli close -s ui-verify
playwright-cli close-all                 # close all browsers
```

## Navigation and viewport

```bash
playwright-cli goto "https://localhost:3000/reports?tab=summary" -s ui-verify
playwright-cli resize 1440 1080 -s ui-verify    # width = Figma frame width
playwright-cli reload -s ui-verify
```

Quote full URLs. On Windows, `cmd.exe`/PowerShell treat `&` as a separator — escape
with `^&` (cmd) or use `--%` (PowerShell).

## Snapshots and element refs

```bash
playwright-cli snapshot -s ui-verify                     # page snapshot with refs (e1, e2, …)
playwright-cli --raw snapshot -s ui-verify > a11y-snapshot.yml
playwright-cli snapshot --boxes -s ui-verify             # include bounding boxes
playwright-cli snapshot "#main" -s ui-verify             # snapshot an element
```

Interact using refs from the snapshot, CSS selectors, or Playwright locators:

```bash
playwright-cli click e15 -s ui-verify
playwright-cli fill e5 "user@example.com" -s ui-verify
playwright-cli fill e6 "value" --submit -s ui-verify     # --submit presses Enter
playwright-cli hover e4 -s ui-verify
playwright-cli press Enter -s ui-verify
playwright-cli click "getByRole('button', { name: 'Submit' })" -s ui-verify
```

## Screenshots

```bash
playwright-cli screenshot --filename="$ARTIFACT_DIR/actual.png" -s ui-verify
# Fallback with explicit full-page control:
playwright-cli run-code -s ui-verify "async page => { await page.screenshot({ path: '$ARTIFACT_DIR/actual.png', fullPage: true }); }"
```

Never leave a screenshot at the default `.playwright-cli/` location — always pass an
explicit `--filename`/`path`.

## Evaluating JavaScript (computed styles)

```bash
playwright-cli eval "document.title" -s ui-verify
playwright-cli --raw eval -s ui-verify "JSON.stringify(...)" > "$ARTIFACT_DIR/computed-styles.json"
```

`--raw` strips page status and snapshot sections, returning only the result value —
required when piping to a file. Example measurement payload shape:

The payload contract — object shape, required fields, no nulls, CSS-only selectors —
is in `capturing-ui-evidence`'s rules table. This is the worked example of it.

Scope the query to the component under verification — never a page-wide generic
pattern, whose first match is as likely to be the page banner as the target. The
pattern has three parts, and none of it depends on a UI library: resolve a root the
caller named, **prove** it is the right element, then measure inside it. `:contains()`
is jQuery, not CSS — `querySelector` silently matches nothing with it, so find by
text in JavaScript as the fallback below does.

```js
// 1. Resolve the root, then PROVE it. ROOT_TEXT is the proof and is always required;
//    ROOT_HOOKS is whatever this project actually offers — check the page source and
//    the plan's Technical Context, and delete the lines that do not apply. Some
//    repos use test attributes (named data-testid, data-test, data-qa, …), some
//    expose ids or ARIA landmarks, some offer nothing but rendered text. The text
//    proof is what makes every one of these safe, so the ladder degrades cleanly.
const ROOT_TEXT = 'REPLACE-ME: text this component always renders';
const ROOT_HOOKS = [
  // '[data-testid="company-details"]',   // a test attribute, if this project has one
  // '#company-details',                  // a stable id
  // 'main section[aria-labelledby="…"]', // a landmark or labelled region
];

const root =
  ROOT_HOOKS.map((sel) => document.querySelector(sel)).find(Boolean) ??
  // Last resort, and fine on its own: the smallest element containing the text.
  // CSS has no :contains(), so filter in JS.
  [...document.querySelectorAll('section, article, div')]
    .filter((el) => el.textContent?.includes(ROOT_TEXT))
    .sort((a, b) => a.getElementsByTagName('*').length - b.getElementsByTagName('*').length)[0];

if (!root) throw new Error(`no element contains "${ROOT_TEXT}" — wrong page or wrong text`);
if (!root.textContent?.includes(ROOT_TEXT)) {
  throw new Error(`root does not contain "${ROOT_TEXT}" — wrong element, fix the hook`);
}

// 2. The visible box of a control is often an ancestor of the focusable element:
//    walk up until something actually paints a border or a background. This finds
//    the wrapper in any component library without naming one.
const visibleBox = (el) => {
  let node = el;
  for (let hops = 0; hops < 4 && node && node !== root; hops += 1) {
    const cs = getComputedStyle(node);
    const paints =
      parseFloat(cs.borderTopWidth) > 0 ||
      (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent');
    if (paints) return node;
    node = node.parentElement;
  }
  return el;
};

// 3. Measure the root and every control, labeling each entry so a mis-scoped
//    measurement is visible on sight.
const controls = [...root.querySelectorAll('input, textarea, select, button, [role="textbox"]')];

JSON.stringify(
  [
    { label: 'root', el: root },
    ...controls.flatMap((el, i) => [
      { label: `control-${i}-box`, el: visibleBox(el) },
      { label: `control-${i}-inner`, el },
    ]),
  ].map(({ label, el }) => {
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      return {
        label,
        selector: el.tagName + (el.className ? '.' + String(el.className).split(' ').join('.') : ''),
        textSample: (el.textContent ?? '').trim().slice(0, 40),
        rect: { x: r.x, y: r.y, width: r.width, height: r.height },
        display: cs.display, flexDirection: cs.flexDirection,
        justifyContent: cs.justifyContent, alignItems: cs.alignItems,
        width: cs.width, maxWidth: cs.maxWidth, height: cs.height, minHeight: cs.minHeight,
        padding: cs.padding, margin: cs.margin, gap: cs.gap,
        fontFamily: cs.fontFamily, fontSize: cs.fontSize, fontWeight: cs.fontWeight,
        lineHeight: cs.lineHeight, color: cs.color, backgroundColor: cs.backgroundColor,
        borderRadius: cs.borderRadius, boxShadow: cs.boxShadow,
      };
    }),
  null,
  2,
)
```

Set `ROOT_TEXT` to something the component always renders, fill `ROOT_HOOKS` with
whatever stable hooks this project actually has (none is fine — the text path stands
on its own), and adjust the control selector list to the elements this project
renders; keep the three-part shape. Never assume a hook convention: read the page or
the plan's Technical Context to see what exists here, and if a hook you expected is
absent, that is a fact about the project, not a reason to stop. Two things make the output
reviewable: `label` and `textSample` expose a mis-scoped measurement immediately — an
entry labeled `root` whose `textSample` reads like the page header is a capture
defect, not a design difference — and capturing both `-box` and `-inner` per control
means the design is compared against the box that paints the border, while the inner
value stays available to explain a difference.

The failure this prevents: a component library commonly wraps the real control, so
the focusable element is smaller than the bordered box a design specifies. Measuring
only the inner element makes every width comparison wrong by the horizontal padding.
Finding the wrapper by asking which ancestor paints, rather than by hard-coding a
library's class names, keeps this working on any stack.

## Render stabilization

```bash
playwright-cli run-code -s ui-verify "async page => { await page.emulateMedia({ reducedMotion: 'reduce' }); await page.waitForLoadState('networkidle'); }"
```

## Route mocking (only when the task requires deterministic data)

```bash
playwright-cli route "https://api.example.com/**" --body='{"mock": true}' -s ui-verify
playwright-cli route-list -s ui-verify
playwright-cli unroute -s ui-verify
```

Use mocks to remove nondeterministic backend data, never to hide real UI defects.

## Storage state (authenticated session reuse)

```bash
playwright-cli state-save /tmp/ui-auth.json -s ui-verify   # after a real login
playwright-cli state-load /tmp/ui-auth.json -s ui-verify   # later iterations
```

Keep state files outside `specifications/**` and out of version control — see
[authenticated-capture.md](./authenticated-capture.md).

## Diagnostics

```bash
playwright-cli console -s ui-verify        # console messages
playwright-cli requests -s ui-verify       # network requests
```
