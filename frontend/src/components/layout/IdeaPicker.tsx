import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { useEffect } from 'react';
import { Lightbulb } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ideasApi } from '@/services/modules';
import { pickFallbackIdea, useWorkspace } from '@/store/workspace';

/**
 * Pulls the active idea from the workspace store and exposes a
 * dropdown to switch between ideas. Renders children only when an
 * idea is selected, otherwise invites the user to create one.
 */
export function IdeaPicker({ children }: { children: React.ReactNode }) {
  const { t } = useTranslation();
  const { selectedIdeaId, setSelectedIdeaId } = useWorkspace();

  const ideasQuery = useQuery({
    queryKey: ['ideas', 'all'],
    queryFn: () => ideasApi.list({ limit: 100, include_archived: false }),
  });

  useEffect(() => {
    if (!selectedIdeaId && ideasQuery.data && ideasQuery.data.items.length > 0) {
      setSelectedIdeaId(pickFallbackIdea(ideasQuery.data.items));
    }
  }, [selectedIdeaId, ideasQuery.data, setSelectedIdeaId]);

  const active = ideasQuery.data?.items.find((i) => i.id === selectedIdeaId) ?? null;

  if (ideasQuery.isLoading) {
    return <p className="text-sm text-muted-foreground">{t('common.loading')}</p>;
  }

  if (!ideasQuery.data || ideasQuery.data.items.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <Lightbulb className="h-8 w-8 text-muted-foreground" />
          <h3 className="text-lg font-semibold">{t('ideas.noIdeasTitle')}</h3>
          <p className="max-w-md text-sm text-muted-foreground">{t('ideas.noIdeasHelper')}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm font-medium">{t('common.currentIdea')}</label>
        <Select
          value={selectedIdeaId ?? ''}
          onValueChange={(v) => setSelectedIdeaId(v)}
        >
          <SelectTrigger className="w-full max-w-sm">
            <SelectValue placeholder={t('common.pickIdea')} />
          </SelectTrigger>
          <SelectContent>
            {ideasQuery.data.items.map((i) => (
              <SelectItem key={i.id} value={i.id}>
                {i.title}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      {active ? children : null}
    </div>
  );
}