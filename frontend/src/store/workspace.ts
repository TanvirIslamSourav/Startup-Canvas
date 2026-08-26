import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Idea } from '@/types/api';

interface WorkspaceState {
  /** Last selected idea id; drives the per-idea modules. */
  selectedIdeaId: string | null;
  setSelectedIdeaId: (id: string | null) => void;
  selectedProjectId: string | null;
  setSelectedProjectId: (id: string | null) => void;
}

export const useWorkspace = create<WorkspaceState>()(
  persist(
    (set) => ({
      selectedIdeaId: null,
      selectedProjectId: null,
      setSelectedIdeaId: (id) => set({ selectedIdeaId: id }),
      setSelectedProjectId: (id) => set({ selectedProjectId: id }),
    }),
    { name: 'startup-canvas.workspace' },
  ),
);

/**
 * Pick the next sensible idea id from a list when the currently
 * selected one disappears.
 */
export function pickFallbackIdea(ideas: Idea[]): string | null {
  const active = ideas.find((i) => !i.is_archived);
  return active ? active.id : ideas[0]?.id ?? null;
}