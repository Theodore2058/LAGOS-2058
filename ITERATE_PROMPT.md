# Autonomous Frontend Iteration Prompt

Paste this into a new Claude Code session for the LAGOS-2058 project.

---

## Prompt

You are working on LAGOS-2058, a Game Master console for a Nigerian election simulation (Merrill-Grofman spatial voting model). The codebase has a React 19 + TypeScript + Vite + Tailwind frontend in `frontend/` and a FastAPI + Python election engine backend in `api/` and `src/election_engine/`.

Your job is to **autonomously iterate** on this codebase in batches. Each batch should contain a coherent set of improvements. After each batch, commit and push, then immediately start the next batch. Repeat until no worthwhile changes remain or you are told to stop. Remember that you can preview the frontend, take screenshots of it, and interact with it. You should try to interact with it as a human would, including attempting to run full campaigns with actions every so often to make sure the GMs will really be able to use it.

### Rules

1. **NO new mechanics.** Do not add new game mechanics or new simulation logic. The election engine math, campaign action system, PC economy, crisis system, etc. are locked.
2. **Improve what exists.** You may:
   - Fix bugs (frontend or backend)
   - Fix TypeScript errors, warnings, and strict-mode issues
   - Fix ESLint warnings/errors
   - Improve error handling (missing loading states, error boundaries, failed API calls)
   - Improve UX (layout, spacing, responsiveness, accessibility, keyboard nav, focus management)
   - Improve visual polish (consistency, hover states, transitions, empty states, skeleton loaders)
   - Optimize performance (unnecessary re-renders, memo, lazy loading, bundle size)
   - Refactor for clarity (extract components, reduce duplication, simplify logic)
   - Improve type safety (remove `any`, add proper interfaces, fix type mismatches)
   - Clean up dead code, unused imports, unused variables
   - Improve API error responses and validation on the backend
   - Fix data display issues (formatting numbers, sorting, missing data handling)
3. **Backend changes only to fix bugs or support frontend fixes.** Don't refactor the engine internals unless something is broken.
4. **Don't break tests.** Run `cd /c/Default/LAGOS-2058 && python -m pytest tests/ -x -q` after any backend change. If tests fail, fix them before committing.
5. **Don't break the build.** Run `cd /c/Default/LAGOS-2058/frontend && npx tsc --noEmit && npx vite build` to verify. Fix any errors before committing.

### Workflow

For each batch:

1. **Scan** — Read the relevant source files. Identify a coherent set of 3-8 improvements. Prioritize by impact: bugs > type errors > UX issues > polish > refactoring.
2. **Implement** — Make the changes. Be surgical. Don't touch code that doesn't need changing.
3. **Verify** — Run the TypeScript compiler, Vite build, and pytest (if backend touched). Fix any issues.
4. **Commit & push** — Use the project's commit convention:
   - `fix:` for bug fixes
   - `style:` for visual/UX polish
   - `refactor:` for code cleanup
   - `perf:` for performance improvements
   - Format: `<type>: batch N - brief description of changes`
   - Example: `fix: batch 9 - type safety, error handling, campaign state edge cases`
   - Push to `main`.
5. **Report** — Briefly list what you changed and why.
6. **Repeat** — Start the next batch immediately. Do NOT wait for instructions.

### What to look for

Here's a non-exhaustive checklist of the kinds of issues to find and fix:

**Frontend bugs & type safety:**
- `any` types that should be properly typed
- Missing null/undefined checks causing runtime errors
- API response data not matching TypeScript interfaces
- Stale closures in useEffect/useCallback
- Missing dependency arrays or incorrect dependencies
- Race conditions in async operations (component unmounts during fetch)

**UX & accessibility:**
- Missing loading indicators during API calls
- No error messages when API calls fail (silent failures)
- Tables/lists with no empty state
- Buttons with no disabled state during operations
- Missing aria-labels, roles, or keyboard navigation
- Poor contrast or readability issues
- Inputs without labels or placeholder text

**Visual polish:**
- Inconsistent spacing, padding, margins
- Inconsistent button styles or sizes
- Missing hover/focus/active states
- Jarring layout shifts on data load
- Truncated text without tooltips or overflow handling
- Inconsistent number formatting (decimals, percentages)
- Come up with an improved visual theme. Pull on 70s retrofuturism, afrofuturism and warroom aesthetics. Make the frontend visually appealing.

**Performance:**
- Large components that should be split
- Missing React.memo on expensive pure components
- Inline object/array creation in render causing unnecessary child re-renders
- Data transformations that could be memoized with useMemo

**Code quality:**
- Duplicated logic across components
- Magic numbers without named constants
- Console.log statements left in production code
- Dead code or unused imports
- Overly complex conditional rendering

**Backend:**
- API endpoints returning raw error traces to the client
- Missing input validation on request bodies
- Inconsistent response formats
- Unhandled edge cases in data transformation

### Project structure reference

```
frontend/src/
  api/          — Axios client + endpoint modules (client.ts, election.ts, campaign.ts, parties.ts, config.ts, scenarios.ts, crises.ts)
  components/   — Reusable UI (Sidebar, ActionBuilder, CheatSheet, ElectionDashboard, PartyComparison, PartyForm, PositionSlider)
  pages/        — Route pages (Dashboard, Parties, Params, Election, Campaign, Crises, Results, Map, Scenarios)
  types/        — TypeScript interfaces
  utils/        — Issue descriptions

api/
  main.py       — FastAPI app
  routes/       — API route handlers
  schemas/      — Pydantic request/response models
  services/     — Business logic layer (session state, election runner, campaign manager, party loader)

src/election_engine/  — Core simulation engine (DO NOT refactor unless fixing a bug)
tests/                — 224+ pytest tests (must pass after any backend change)
```

### Stopping criteria

Stop iterating when:
- You've gone through all source files and found nothing worth changing
- Remaining issues are purely cosmetic with negligible impact
- You've completed 5+ batches and improvements are becoming marginal
- The user tells you to stop

Start now. Read the frontend source files, identify the first batch of improvements, and begin.
