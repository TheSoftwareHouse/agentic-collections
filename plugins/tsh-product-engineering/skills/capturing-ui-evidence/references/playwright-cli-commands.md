# playwright-cli command reference

The subset of `playwright-cli` used for UI verification capture. Full docs:
`playwright-cli --help`.

## Availability and install

```bash
playwright-cli --version                 # global install?
npx --no-install playwright-cli --version   # local install?
npm install -g @playwright/cli@latest    # install globally when neither works
```

When only the local version is available, prefix every command with `npx `.

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

```js
JSON.stringify(
  [...document.querySelectorAll('main, header, [class*="card"], [class*="container"], button, nav')]
    .slice(0, 60)
    .map((el) => {
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      return {
        selector: el.tagName + (el.className ? '.' + String(el.className).split(' ').join('.') : ''),
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

Adjust the selector list to the containers and controls actually under
verification, and target the VISIBLE box of each control — the element that paints
the border and background. Component libraries wrap the real input (in MUI,
`.MuiInputBase-root` paints the text-field box; the inner `.MuiInputBase-input` is
smaller by the horizontal padding), so measuring only inner elements makes every
width comparison wrong. When in doubt, capture the wrapper and the inner control
both, with a label distinguishing them.

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
