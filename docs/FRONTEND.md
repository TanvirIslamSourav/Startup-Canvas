# Frontend — Startup Canvas

> React 19 · TypeScript · Vite · Tailwind CSS · shadcn/ui · TanStack Query · Zustand · React Hook Form · Zod · Framer Motion · Recharts · react-i18next

---

## 1. Routing

```
/                       Landing (public)
/login                  (placeholder)
/dashboard              Dashboard
/ideas                  Ideas list
/ideas/new              Idea create wizard
/ideas/:ideaId          Idea detail (tabs)
/ideas/:ideaId/lean-canvas
/ideas/:ideaId/business-canvas
/ideas/:ideaId/swot
/ideas/:ideaId/competitors
/ideas/:ideaId/personas
/ideas/:ideaId/roadmap
/ideas/:ideaId/tasks
/ideas/:ideaId/milestones
/ideas/:ideaId/progress
/ideas/:ideaId/documents
/ideas/:ideaId/notes
/analytics              Analytics
/settings               Settings (theme + language)
/about                  About
*                       404
```

`<AppShell>` is the persistent layout (top bar + sidebar + content area). Routes nested under it use `<Outlet />`.

---

## 2. Providers (mount order, outermost → innermost)

```
<ErrorBoundary>
  <ThemeProvider>            // next-themes
    <I18nProvider>           // react-i18next
      <QueryClientProvider>  // TanStack Query
        <TooltipProvider>    // shadcn/ui
          <ToastProvider>    // custom, wraps sonner
            <RouterProvider />
          </ToastProvider>
        </TooltipProvider>
      </QueryClientProvider>
    </I18nProvider>
  </ThemeProvider>
</ErrorBoundary>
```

---

## 3. Folder layout (frontend/src)

```
components/
  ui/           # shadcn-style primitives: Button, Card, Dialog, …
  layout/       # AppShell, Sidebar, TopBar, PageHeader, EmptyState
  common/       # DataTable, SearchBar, FilterBar, ConfirmDialog, …
features/
  ideas/        # IdeasList, IdeaCard, IdeaForm, useIdeas, schema.ts
  dashboard/    # SummaryCards, ProgressChart, ActivityFeed
  lean-canvas/
  business-canvas/
  swot/
  competitors/
  personas/
  roadmap/
  tasks/
  milestones/
  progress/
  documents/
  notes/
  analytics/
hooks/          # useDebounce, useMediaQuery, useReducedMotion
services/       # http client, ai client
store/          # zustand slices
utils/          # cn, formatDate, formatNumber, buildQueryString
types/          # api.ts mirrors + shared domain types
theme/          # tokens.css, theme.ts
providers/      # QueryProvider, ThemeProvider, I18nProvider, ToastProvider
i18n/           # index.ts, locales/{bn,en}.json
__tests__/      # vitest specs
pages/          # top-level route components (thin, delegate to features)
layouts/        # AppLayout, AuthLayout
main.tsx
App.tsx
```

---

## 4. Data flow

```
User action ─► RHF + Zod ─► TanStack Query mutation ─► fetch /api/... ─►
  onSuccess: invalidate keys, toast, close dialog
  onError:   map to toast, keep dialog open, surface field errors

Read path:
  useQuery(['ideas', filters]) ─► fetch /api/ideas?… ─► cache
  ─► selector hook returns { data, isLoading, isError, refetch }
  ─► Skeleton on first load, empty state on zero rows, error card on fail
```

---

## 5. State matrix

| Concern                         | Lives in                |
| ------------------------------- | ----------------------- |
| Server data (ideas, tasks, …)   | TanStack Query cache    |
| Filters / sort / page           | URL query string + Zustand `useUiStore` (hydrated from URL) |
| Open dialog state               | Local component state   |
| Selected rows                   | Local component state   |
| Theme                           | next-themes (persisted) |
| Language                        | i18next (persisted)     |
| Toasts                          | Custom `useToast()`     |
| Form values                     | React Hook Form         |

---

## 6. Theming

- Tokens in `src/theme/tokens.css` as CSS variables, mapped to Tailwind in `tailwind.config.ts`.
- `ThemeProvider` toggles `class="dark"` on `<html>`.
- Use semantic class names (`bg-surface`, `text-fg`, `border-border`) instead of raw `bg-white`.
- Honors `prefers-reduced-motion`.

## 7. i18n

- Locales: `bn` (default) and `en`.
- Files: `src/i18n/locales/{bn,en}.json`.
- Persisted in `localStorage` under `i18nextLng`.
- Translation keys are dot‑namespaced: `ideas.list.empty`, `dashboard.cards.total_ideas`.
- Pluralization via i18next's `_one` / `_other` suffixes.
- Bangla uses **Noto Sans Bengali** as the primary font for consistent rendering.

## 8. Accessibility

- Every interactive element has a visible focus ring (`focus-visible:ring-2 ring-offset-2`).
- Dialogs trap focus and restore on close.
- Toasts use `aria-live="polite"`.
- Tables have proper `<caption>`, `<th scope="col">`.
- Icons are `aria-hidden`; accessible labels come from adjacent text or `aria-label`.
- Respects `prefers-reduced-motion` via a global `<MotionConfig reducedMotion="user">`.

## 9. Build & run

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # type-checks + builds to dist/
npm run preview    # serve dist/
npm run test       # vitest
npm run lint       # eslint
```

Vite proxies `/api` to `http://localhost:8000` in dev (see `vite.config.ts`).