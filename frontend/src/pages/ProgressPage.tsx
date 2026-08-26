import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Trash2 } from 'lucide-react';
import { PageHeader } from '@/components/layout/PageHeader';
import { EmptyState } from '@/components/layout/EmptyState';
import { IdeaPicker } from '@/components/layout/IdeaPicker';
import { ConfirmDialog } from '@/components/layout/ConfirmDialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/components/ui/toast';
import { progressApi, type ProgressTrackerUpsert } from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

interface Draft {
  overall_completion: string;
  health_score: string;
  milestone_progress: string;
  task_completion: string;
}

const EMPTY: Draft = {
  overall_completion: '0',
  health_score: '70',
  milestone_progress: '0',
  task_completion: '0',
};

function toForm(values: Partial<Draft>): ProgressTrackerUpsert {
  return {
    overall_completion: Number(values.overall_completion ?? 0),
    health_score: Number(values.health_score ?? 0),
    milestone_progress: Number(values.milestone_progress ?? 0),
    task_completion: Number(values.task_completion ?? 0),
  };
}

export default function ProgressPage() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const qc = useQueryClient();
  const ideaId = useSelectedIdea();
  const [draft, setDraft] = useState<Draft>(EMPTY);
  const [toDelete, setToDelete] = useState(false);

  const query = useQuery({
    queryKey: ['progress', ideaId],
    queryFn: () => progressApi.get(ideaId!),
    enabled: !!ideaId,
  });

  useEffect(() => {
    if (query.data) {
      setDraft({
        overall_completion: String(query.data.overall_completion),
        health_score: String(query.data.health_score),
        milestone_progress: String(query.data.milestone_progress),
        task_completion: String(query.data.task_completion),
      });
    }
  }, [query.data]);

  const saveMut = useMutation({
    mutationFn: (values: ProgressTrackerUpsert) => progressApi.upsert(ideaId!, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['progress', ideaId] });
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteMut = useMutation({
    mutationFn: () => progressApi.delete(ideaId!),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['progress', ideaId] });
      setDraft(EMPTY);
      setToDelete(false);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const fields: { key: keyof Draft; labelKey: string; hint?: string }[] = [
    { key: 'overall_completion', labelKey: 'progress.fields.overallCompletion' },
    { key: 'health_score', labelKey: 'progress.fields.healthScore' },
    { key: 'milestone_progress', labelKey: 'progress.fields.milestoneProgress' },
    { key: 'task_completion', labelKey: 'progress.fields.taskCompletion' },
  ];

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="progress.title"
        actions={
          ideaId &&
          query.data && (
            <Button variant="ghost" onClick={() => setToDelete(true)}>
              <Trash2 className="mr-2 h-4 w-4 text-destructive" />
              {t('common.delete')}
            </Button>
          )
        }
      />

      <IdeaPicker>
        {ideaId ? (
          query.isLoading ? (
            <Skeleton className="h-64 w-full" />
          ) : !query.data ? (
            <EmptyState
              titleKey="common.empty"
              action={<Button onClick={() => saveMut.mutate(toForm(draft))}>{t('progress.create')}</Button>}
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {fields.map((f) => (
                <Card key={f.key}>
                  <CardHeader>
                    <CardTitle className="text-sm">{t(f.labelKey)}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Label htmlFor={f.key}>{t(f.labelKey)}</Label>
                    <Input
                      id={f.key}
                      type="number"
                      min={0}
                      max={100}
                      value={draft[f.key]}
                      onChange={(e) => setDraft({ ...draft, [f.key]: e.target.value })}
                    />
                  </CardContent>
                </Card>
              ))}
              <div className="md:col-span-2 flex justify-end">
                <Button onClick={() => saveMut.mutate(toForm(draft))} disabled={saveMut.isPending}>
                  {t('common.save')}
                </Button>
              </div>
            </div>
          )
        ) : null}
      </IdeaPicker>

      <ConfirmDialog
        open={toDelete}
        onOpenChange={setToDelete}
        title={t('progress.confirmDelete')}
        destructive
        onConfirm={() => deleteMut.mutate()}
      />
    </div>
  );
}