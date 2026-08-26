import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Trash2, Wand2 } from 'lucide-react';
import { PageHeader } from '@/components/layout/PageHeader';
import { EmptyState } from '@/components/layout/EmptyState';
import { IdeaPicker } from '@/components/layout/IdeaPicker';
import { ConfirmDialog } from '@/components/layout/ConfirmDialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/toast';
import { aiApi, swotApi, type Swot, type SwotUpdate } from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

interface SwotDraft {
  strengths: string;
  weaknesses: string;
  opportunities: string;
  threats: string;
  summary: string;
  score: string;
}

const EMPTY: SwotDraft = {
  strengths: '',
  weaknesses: '',
  opportunities: '',
  threats: '',
  summary: '',
  score: '0',
};

function toForm(s: Swot): SwotDraft {
  return {
    strengths: s.strengths ?? '',
    weaknesses: s.weaknesses ?? '',
    opportunities: s.opportunities ?? '',
    threats: s.threats ?? '',
    summary: s.summary ?? '',
    score: String(s.score ?? 0),
  };
}

function fromForm(f: SwotDraft): SwotUpdate {
  return {
    strengths: f.strengths || null,
    weaknesses: f.weaknesses || null,
    opportunities: f.opportunities || null,
    threats: f.threats || null,
    summary: f.summary || null,
    score: Number(f.score) || 0,
  };
}

export default function SwotPage() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const qc = useQueryClient();
  const ideaId = useSelectedIdea();
  const [draft, setDraft] = useState<SwotDraft>(EMPTY);
  const [toDelete, setToDelete] = useState(false);

  const query = useQuery({
    queryKey: ['swot', ideaId],
    queryFn: () => swotApi.get(ideaId!),
    enabled: !!ideaId,
  });

  useEffect(() => {
    if (query.data) setDraft(toForm(query.data));
  }, [query.data]);

  const saveMut = useMutation({
    mutationFn: (values: SwotUpdate) => swotApi.upsert(ideaId!, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['swot', ideaId] });
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteMut = useMutation({
    mutationFn: () => swotApi.delete(ideaId!),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['swot', ideaId] });
      setDraft(EMPTY);
      setToDelete(false);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const aiMut = useMutation({
    mutationFn: async () => {
      const result = await aiApi.swot({
        title: draft.summary || 'Idea',
        problem: draft.summary || null,
        solution: null,
        audience: null,
        category: null,
      });
      const data = result as { strengths?: string[]; weaknesses?: string[]; opportunities?: string[]; threats?: string[] };
      return data;
    },
    onSuccess: (data) => {
      setDraft({
        ...draft,
        strengths: (data.strengths ?? []).join('\n'),
        weaknesses: (data.weaknesses ?? []).join('\n'),
        opportunities: (data.opportunities ?? []).join('\n'),
        threats: (data.threats ?? []).join('\n'),
      });
      toast({ title: t('swot.aiReady'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const quadrants: { key: keyof Omit<SwotDraft, 'summary' | 'score'>; labelKey: string; tone: string }[] = [
    { key: 'strengths', labelKey: 'swot.strengths', tone: 'border-emerald-500/30 bg-emerald-50 dark:bg-emerald-950/20' },
    { key: 'weaknesses', labelKey: 'swot.weaknesses', tone: 'border-rose-500/30 bg-rose-50 dark:bg-rose-950/20' },
    { key: 'opportunities', labelKey: 'swot.opportunities', tone: 'border-sky-500/30 bg-sky-50 dark:bg-sky-950/20' },
    { key: 'threats', labelKey: 'swot.threats', tone: 'border-amber-500/30 bg-amber-50 dark:bg-amber-950/20' },
  ];

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="swot.title"
        actions={
          ideaId &&
          query.data && (
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => aiMut.mutate()} disabled={aiMut.isPending}>
                <Wand2 className="mr-2 h-4 w-4" />
                {t('swot.aiHelper')}
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
              action={<Button onClick={() => saveMut.mutate(fromForm(draft))}>{t('swot.create')}</Button>}
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {quadrants.map((q) => (
                <Card key={q.key as string} className={q.tone}>
                  <CardHeader>
                    <CardTitle className="text-sm">{t(q.labelKey)}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Textarea
                      rows={5}
                      value={draft[q.key]}
                      onChange={(e) => setDraft({ ...draft, [q.key]: e.target.value })}
                    />
                  </CardContent>
                </Card>
              ))}
              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle className="text-sm">{t('swot.summary')}</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-3">
                  <Textarea
                    rows={2}
                    value={draft.summary}
                    onChange={(e) => setDraft({ ...draft, summary: e.target.value })}
                  />
                  <div className="grid grid-cols-[1fr,auto,auto] items-end gap-2">
                    <div className="grid gap-1">
                      <Label htmlFor="score">{t('swot.score')}</Label>
                      <Input
                        id="score"
                        type="number"
                        min={0}
                        max={100}
                        value={draft.score}
                        onChange={(e) => setDraft({ ...draft, score: e.target.value })}
                      />
                    </div>
                    <Button onClick={() => saveMut.mutate(fromForm(draft))} disabled={saveMut.isPending}>
                      {t('common.save')}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )
        ) : null}
      </IdeaPicker>

      <ConfirmDialog
        open={toDelete}
        onOpenChange={setToDelete}
        title={t('swot.confirmDelete')}
        destructive
        onConfirm={() => deleteMut.mutate()}
      />
    </div>
  );
}