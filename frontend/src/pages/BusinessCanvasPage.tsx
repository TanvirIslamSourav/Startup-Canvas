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
import { Skeleton } from '@/components/ui/skeleton';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/toast';
import { businessCanvasApi, type BusinessCanvasUpdate } from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

const FIELDS: { key: keyof BusinessCanvasUpdate; labelKey: string }[] = [
  { key: 'key_partners', labelKey: 'businessCanvas.keyPartners' },
  { key: 'key_activities', labelKey: 'businessCanvas.keyActivities' },
  { key: 'key_resources', labelKey: 'businessCanvas.keyResources' },
  { key: 'value_propositions', labelKey: 'businessCanvas.valuePropositions' },
  { key: 'customer_relationships', labelKey: 'businessCanvas.customerRelationships' },
  { key: 'channels', labelKey: 'businessCanvas.channels' },
  { key: 'customer_segments', labelKey: 'businessCanvas.customerSegments' },
  { key: 'cost_structure', labelKey: 'businessCanvas.costStructure' },
  { key: 'revenue_streams', labelKey: 'businessCanvas.revenueStreams' },
];

export default function BusinessCanvasPage() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const qc = useQueryClient();
  const ideaId = useSelectedIdea();
  const [draft, setDraft] = useState<BusinessCanvasUpdate>({});
  const [toDelete, setToDelete] = useState(false);

  const query = useQuery({
    queryKey: ['business-canvas', ideaId],
    queryFn: () => businessCanvasApi.get(ideaId!),
    enabled: !!ideaId,
  });

  useEffect(() => {
    if (query.data) setDraft(query.data);
  }, [query.data]);

  const saveMut = useMutation({
    mutationFn: (values: BusinessCanvasUpdate) => businessCanvasApi.upsert(ideaId!, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['business-canvas', ideaId] });
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteMut = useMutation({
    mutationFn: () => businessCanvasApi.delete(ideaId!),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['business-canvas', ideaId] });
      setDraft({});
      setToDelete(false);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="businessCanvas.title"
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
              action={<Button onClick={() => saveMut.mutate(draft)}>{t('businessCanvas.create')}</Button>}
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
                      onChange={(e) => setDraft({ ...draft, [f.key]: e.target.value } as BusinessCanvasUpdate)}
                    />
                  </CardContent>
                </Card>
              ))}
              <div className="md:col-span-3 flex justify-end">
                <Button onClick={() => saveMut.mutate(draft)} disabled={saveMut.isPending}>
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
        title={t('businessCanvas.confirmDelete')}
        destructive
        onConfirm={() => deleteMut.mutate()}
      />
    </div>
  );
}