# React implementation patterns

React-specific implementations of the generic patterns in `implementing-frontend`.
Load this reference when the project uses React.

## Component composition

| Generic pattern | React implementation |
| --- | --- |
| Content projection | `children` prop |
| Render delegation | Render props: `renderItem={(item) => <Item data={item} />}` |
| Compound components | Shared context between parent and sub-components (`Select` + `Select.Option`) |
| Slots | Named props accepting `ReactNode`: `header`, `footer`, `sidebar` |

Prefer `children` for single content projection. Use named `ReactNode` props (slots)
when multiple projection points are needed. Use compound components for tightly
coupled UI groups (tabs, accordion, select).

## State patterns

| State type (from the skill) | React implementation | Hook |
| --- | --- | --- |
| Local state | Component-scoped | `useState`, `useReducer` |
| Lifted state | Prop drilling or callback props | Parent `useState` + pass down |
| Context / DI | React Context API | `createContext` + `useContext` |
| Server cache | Data fetching library | TanStack Query, SWR, or framework-specific |

Use `useReducer` over `useState` when state transitions are complex (multiple
related values, action-based updates).

## Error handling

React uses **error boundaries** — class components with `componentDidCatch` /
`getDerivedStateFromError`:

- Wrap data-dependent sections with an `<ErrorBoundary>` component.
- Per-feature boundaries beat one global boundary.
- Error boundaries do NOT catch errors in event handlers, async code, or
  server-side rendering — handle those with try/catch.

## Performance patterns

| Technique | React API | When to use |
| --- | --- | --- |
| Component memoization | `React.memo(Component)` | Prevent re-render when props unchanged |
| Expensive computation | `useMemo(() => compute(data), [data])` | Heavy calculations derived from state/props |
| Stable callbacks | `useCallback(fn, [deps])` | Callbacks passed to memoized children |
| Code splitting | `React.lazy(() => import('./Heavy'))` + `<Suspense>` | Route-level and heavy component splitting |

**Rule of thumb**: don't memoize by default. Measure first. `React.memo` only helps
when re-renders are measurably expensive and props don't change often.

## Anti-patterns

| Anti-pattern | Why | Fix |
| --- | --- | --- |
| Inline `{}` / `[]` as prop to a memo child | New reference every render defeats memo | Lift to a module constant or `useMemo` |
| Missing/wrong dependency array | Stale closures, infinite loops | Include all reactive values; lint with `exhaustive-deps` |
| `useEffect` for derived state | Unnecessary render cycle | Compute during render: `const x = fn(props.y)` |
| Index as list key | Breaks reconciliation on reorder/delete | Use a stable unique ID |
| Class component for new code | Inconsistent patterns, no hooks | Use functional components |
