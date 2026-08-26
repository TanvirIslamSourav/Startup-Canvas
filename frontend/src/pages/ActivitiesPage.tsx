import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Activity as ActivityIcon } from 'lucide-react';
import { PageHeader } from '@/components/layout/PageHeader';
import { EmptyState } from '@/components/layout/EmptyState';
import { IdeaPicker } from '@/components/layout/IdeaPicker';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { activitiesApi } from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

const EVENT_TONE: Record<string, string> = {
  idea_created: 'default',
  idea_updated: 'secondary',
  task_created: 'outline',
  task_completed: 'default',
  milestone_created: 'outline',
  milestone_completed: 'default',
  document_added: 'outline',
  note_added: 'outline',
};

export default function ActivitiesPage() {
  const { i18n } = useTranslation();
  const ideaId = useSelectedIdea();

  const query = useQuery({
    queryKey: ['activities', ideaId],
    queryFn: () => activitiesApi.list(ideaId!),
    enabled: !!ideaId,
  });

  const items = query.data?.items ?? [];

  return (
    <div className="space-y-4">
      <PageHeader titleKey="activities.title" descriptionKey="activities.subtitle" />

      <IdeaPicker>
        {ideaId ? (
          query.isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : items.length === 0 ? (
            <EmptyState titleKey="activities.empty" />
          ) : (
            <div className="space-y-2">
              {items.map((a) => (
                <Card key={a.id}>
                  <CardContent className="flex items-start gap-3 py-3">
                    <ActivityIcon className="mt-0.5 h-4 w-4 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <Badge variant={(EVENT_TONE[a.event_type] as 'default') ?? 'secondary'}>
                          {a.event_type}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {new Date(a.created_at).toLocaleString(i18n.language)}
                        </span>
                      </div>
                      {a.event_data && Object.keys(a.event_data).length > 0 && (
                        <pre className="mt-1 text-xs text-muted-foreground whitespace-pre-wrap break-words">
                          {JSON.stringify(a.event_data, null, 2)}
                        </pre>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )
        ) : null}
      </IdeaPicker>
    </div>
  );
}