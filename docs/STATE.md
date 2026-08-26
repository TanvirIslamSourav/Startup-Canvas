# State Management — Decision Matrix

> Where does each piece of state live?

| Concern                                   | Owner                  | Why                                                       |
| ----------------------------------------- | ---------------------- | --------------------------------------------------------- |
| Server‑owned entities (ideas, tasks, …)   | **TanStack Query**     | Cache, invalidation, retries, background refresh          |
| Filter / sort / page for a list view      | **URL query string** + Zustand mirror | Shareable links, back/forward works |
| Open/closed dialog                        | **Local `useState`**   | Trivially scoped, no cross‑tree impact                    |
| Selected row(s) in a table                | **Local `useState`**   | Ephemeral, per‑page                                       |
| Theme (light/dark/system)                 | **next-themes**        | Handles `prefers-color-scheme`, persistence, FOUC          |
| Language (bn/en)                          | **i18next**            | Persistence, lazy loading, namespaces                     |
| Toasts / notifications                    | **Custom `useToast`**  | App‑wide queue, no external dep                           |
| Form values & errors                      | **React Hook Form**    | Performance (isolated re‑renders), Zod integration       |
| Cross‑page flags (e.g. "tour seen")       | **Zustand**            | Tiny, persisted to localStorage                           |
| Drafts (unsaved idea title)               | **Zustand `useDrafts`** | Survives navigation within session                       |
| Auth (future)                             | **Zustand** + HTTP‑only cookie | Single source, no provider tree gymnastics        |

---

## Anti‑patterns (we avoid)

- Putting server data in Zustand.
- Putting UI state in TanStack Query.
- Using `localStorage` as a database.
- Prop‑drilling 5+ levels (we colocate with composition or use Zustand).
- Global `useEffect` chains for cross‑component sync.

---

## Why not Redux?

Zustand + TanStack Query covers ~95 % of needs with ~5 % of the boilerplate. The remaining 5 % (rare global app state) goes in a single Zustand slice.

## Why not Context for everything?

Context re‑renders every consumer on every change. Zustand selectors avoid that.