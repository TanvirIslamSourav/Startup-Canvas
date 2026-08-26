import { useQuery } from '@tanstack/react-query';
import { projectsApi, type StartupProject } from '@/services/modules';

export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list(),
    select: (data): StartupProject[] => data.items ?? [],
  });
}