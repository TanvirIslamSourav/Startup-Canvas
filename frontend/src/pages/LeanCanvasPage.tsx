import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Trash2, Wand2 } from 'lucide-react';
import { PageHeader } from '@/components/layout/PageHeader';
import { EmptyState } from '@/components/layout/EmptyState';
import { IdeaPicker } from '@/components/layout/IdeaPicker';
import { ConfirmDialog } from '@/components/layout/ConfirmDialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/toast';
import { aiApi, leanCanvasApi, type LeanCanvasUpdate } from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

const FIELDS: { key: keyof LeanCanvasUpdate; labelKey: string }[] = [
  { key: 'problem', labelKey: 'leanCanvas.problem' },
  { key: 'solution', labelKey: 'leanCanvas.solution' },
  { key: 'key_metrics', labelKey: 'leanCanvas.keyMetrics' },
  { key: 'unique_value_prop', labelKey: 'leanCanvas.valueProposition' },
  { key: 'unfair_advantage', labelKey: 'leanCanvas.unfairAdvantage' },
  { key: 'channels', labelKey: 'leanCanvas.channels' },
  { key: 'customer_segments', labelKey: 'leanCanvas.customerSegments' },
  { key: 'cost_structure', labelKey: 'leanCanvas.costStructure' },
  { key: 'revenue_streams', labelKey: 'leanCanvas.revenueStreams' },
];

export default function LeanCanvasPage() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const qc = useQueryClient();
  const ideaId = useSelectedIdea();
  const [draft, setDraft] = useState<LeanCanvasUpdate>({});
  const [toDelete, setToDelete] = useState(false);

  const query = useQuery({
    queryKey: ['lean-canvas', ideaId],
    queryFn: () => leanCanvasApi.get(ideaId!),
    enabled: !!ideaId,
  });

  useEffect(() => {
    if (query.data) setDraft(query.data);
  }, [query.data]);

  const saveMut = useMutation({
    mutationFn: (values: LeanCanvasUpdate) => leanCanvasApi.upsert(ideaId!, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['lean-canvas', ideaId] });
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteMut = useMutation({
    mutationFn: () => leanCanvasApi.delete(ideaId!),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['lean-canvas', ideaId] });
      setDraft({});
      setToDelete(false);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const aiMut = useMutation({
    mutationFn: () =>
      aiApi.validate({
        idea_id: ideaId,
        title: query.data?.unique_value_prop ?? '',
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['lean-canvas', ideaId] });
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="leanCanvas.title"
        actions={
          ideaId &&
          query.data && (
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => aiMut.mutate()} disabled={aiMut.isPending}>
                <Wand2 className="mr-2 h-4 w-4" />
                {t('leanCanvas.aiHelper')}
              </Button>
              <Button variant="ghost" onClick={() => setToDelete(true)}>
                <Trash2 className="mr-2 h-4 w-4 text-destructive" />
                {t('common.delete')}
              </Button>
            </div>
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
              action={
                <Button onClick={() => saveMut.mutate(draft)}>
                  {t('leanCanvas.create')}
                </Button>
              }
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-3">
              {FIELDS.map((f) => (
                <Card key={f.key as string}>
                  <CardHeader>
                    <CardTitle className="text-sm">{t(f.labelKey)}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Textarea
                      rows={4}
                      value={(draft[f.key] as string | null | undefined) ?? ''}
                      onChange={(e) => setDraft({ ...draft, [f.key]: e.target.value } as LeanCanvasUpdate)}
                    />
                  </CardContent>
                </Card>
              ))}
              <div className="md:col-span-3 flex justify-end">
                <Badge variant="outline">{t('leanCanvas.savedAt', { time: new Date(query.data.updated_at).toLocaleString() })}</Badge>
                <Button className="ml-2" onClick={() => saveMut.mutate(draft)} disabled={saveMut.isPending}>
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
        title={t('leanCanvas.confirmDelete')}
        destructive
        onConfirm={() => deleteMut.mutate()}
      />
    </div>
  );
}