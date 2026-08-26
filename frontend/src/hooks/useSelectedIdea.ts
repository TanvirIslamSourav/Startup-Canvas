import { useWorkspace } from '@/store/workspace';

/** Convenience hook: returns the currently selected idea id (string or null). */
export function useSelectedIdea(): string | null {
  return useWorkspace((s) => s.selectedIdeaId);
}
