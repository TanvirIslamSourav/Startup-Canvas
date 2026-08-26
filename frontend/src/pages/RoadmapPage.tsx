import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Edit, Plus, Sparkles, Trash2 } from 'lucide-react';
import { PageHeader } from '@/components/layout/PageHeader';
import { EmptyState } from '@/components/layout/EmptyState';
import { IdeaPicker } from '@/components/layout/IdeaPicker';
import { ConfirmDialog } from '@/components/layout/ConfirmDialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/toast';
import {
  aiApi,
  ideasApi,
  roadmapApi,
  roadmapStagesApi,
  type Roadmap,
  type RoadmapStage,
  type RoadmapStageCreate,
} from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

interface RoadmapDraft {
  title: string;
  summary: string;
  target_completion: string;
  completion: string;
}

const EMPTY_ROADMAP: RoadmapDraft = {
  title: '',
  summary: '',
  target_completion: '',
  completion: '0',
};

function roadmapToForm(r: Roadmap | null | undefined): RoadmapDraft {
  if (!r) return EMPTY_ROADMAP;
  return {
    title: r.title,
    summary: r.summary ?? '',
    target_completion: r.target_completion ?? '',
    completion: String(r.completion ?? 0),
  };
}

function roadmapFromForm(f: RoadmapDraft): { title: string; summary: string | null; target_completion: string | null; completion: number } {
  return {
    title: f.title,
    summary: f.summary || null,
    target_completion: f.target_completion || null,
    completion: f.completion ? Number(f.completion) : 0,
  };
}

interface StageFormState {
  title: string;
  description: string;
  target_date: string;
  completion: string;
  position: string;
}

const EMPTY_STAGE: StageFormState = {
  title: '',
  description: '',
  target_date: '',
  completion: '0',
  position: '0',
};

function stageToForm(s: RoadmapStage): StageFormState {
  return {
    title: s.title,
    description: s.description ?? '',
    target_date: s.target_date ?? '',
    completion: String(s.completion ?? 0),
    position: String(s.position ?? 0),
  };
}

function stageFromForm(f: StageFormState): RoadmapStageCreate {
  return {
    title: f.title,
    description: f.description || null,
    target_date: f.target_date || null,
    completion: f.completion ? Number(f.completion) : 0,
    position: f.position ? Number(f.position) : 0,
  };
}

export default function RoadmapPage() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const qc = useQueryClient();
  const ideaId = useSelectedIdea();

  const [rmOpen, setRmOpen] = useState(false);
  const [rmForm, setRmForm] = useState<RoadmapDraft>(EMPTY_ROADMAP);
  const [toDeleteRm, setToDeleteRm] = useState(false);

  const [stageOpen, setStageOpen] = useState(false);
  const [stageEditing, setStageEditing] = useState<RoadmapStage | null>(null);
  const [stageForm, setStageForm] = useState<StageFormState>(EMPTY_STAGE);
  const [toDeleteStage, setToDeleteStage] = useState<string | null>(null);

  const ideaQuery = useQuery({
    queryKey: ['idea', ideaId],
    queryFn: () => ideasApi.get(ideaId!),
    enabled: !!ideaId,
  });

  const roadmapQuery = useQuery({
    queryKey: ['roadmap', ideaId],
    queryFn: () => roadmapApi.get(ideaId!),
    enabled: !!ideaId,
  });

  const stagesQuery = useQuery({
    queryKey: ['roadmap-stages', ideaId],
    queryFn: () => roadmapStagesApi.list(ideaId!),
    enabled: !!ideaId,
  });

  useEffect(() => {
    setRmForm(roadmapToForm(roadmapQuery.data ?? null));
  }, [roadmapQuery.data]);

  const saveRoadmapMut = useMutation({
    mutationFn: (values: { title: string; summary: string | null; target_completion: string | null; completion: number }) =>
      roadmapApi.upsert(ideaId!, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['roadmap', ideaId] });
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteRoadmapMut = useMutation({
    mutationFn: () => roadmapApi.delete(ideaId!),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['roadmap', ideaId] });
      setToDeleteRm(false);
      setRmForm(EMPTY_ROADMAP);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const createStageMut = useMutation({
    mutationFn: (values: RoadmapStageCreate) => roadmapStagesApi.create(ideaId!, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['roadmap-stages', ideaId] });
      setStageOpen(false);
      setStageForm(EMPTY_STAGE);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const updateStageMut = useMutation({
    mutationFn: ({ id, values }: { id: string; values: RoadmapStageCreate }) =>
      roadmapStagesApi.update(ideaId!, id, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['roadmap-stages', ideaId] });
      setStageEditing(null);
      setStageForm(EMPTY_STAGE);
      setStageOpen(false);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteStageMut = useMutation({
    mutationFn: (id: string) => roadmapStagesApi.delete(ideaId!, id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['roadmap-stages', ideaId] });
      setToDeleteStage(null);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const aiMut = useMutation({
    mutationFn: async () => {
      const idea = ideaQuery.data;
      return aiApi.roadmap({
        title: idea?.title ?? '',
        problem: idea?.problem ?? null,
        solution: idea?.solution ?? null,
        audience: idea?.audience ?? null,
        category: idea?.category ?? null,
      });
    },
    onSuccess: (data: unknown) => {
      const raw = data as { stages?: Array<{ title?: string; description?: string }> };
      const stages = Array.isArray(raw?.stages) ? raw.stages : [];
      let i = 0;
      for (const s of stages) {
        if (!s.title) continue;
        createStageMut.mutate({
          title: s.title,
          description: s.description ?? null,
          position: i++,
          completion: 0,
        });
      }
      toast({ title: t('roadmap.aiGenerated'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const stages = (stagesQuery.data?.items ?? []).slice().sort((a, b) => a.position - b.position);
  const roadmap = roadmapQuery.data;

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="roadmap.title"
        actions={
          ideaId && (
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => aiMut.mutate()}
                disabled={aiMut.isPending}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                {t('roadmap.aiGenerate')}
              </Button>
              <Button
                onClick={() => {
                  setRmForm(roadmapToForm(roadmap));
                  setRmOpen(true);
                }}
              >
                <Edit className="mr-2 h-4 w-4" />
                {roadmap ? t('common.edit') : t('common.create')}
              </Button>
            </div>
          )
        }
      />

      <IdeaPicker>
        {ideaId ? (
          roadmapQuery.isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : (
            <div className="space-y-4">
              {!roadmap ? (
                <EmptyState
                  titleKey="roadmap.empty"
                  action={
                    <Button onClick={() => { setRmForm(EMPTY_ROADMAP); setRmOpen(true); }}>
                      <Plus className="mr-2 h-4 w-4" />
                      {t('common.create')}
                    </Button>
                  }
                />
              ) : (
                <Card>
                  <CardHeader className="flex flex-row items-start justify-between">
                    <div>
                      <CardTitle>{roadmap.title}</CardTitle>
                      {roadmap.summary && (
                        <p className="mt-1 text-sm text-muted-foreground">{roadmap.summary}</p>
                      )}
                      {roadmap.target_completion && (
                        <p className="mt-1 text-xs text-muted-foreground">
                          {t('roadmap.target')}: {roadmap.target_completion}
                        </p>
                      )}
                    </div>
                    <Button variant="ghost" size="icon" onClick={() => setToDeleteRm(true)}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs text-muted-foreground">
                      {t('roadmap.completion')}: {roadmap.completion}%
                    </div>
                  </CardContent>
                </Card>
              )}

              {roadmap && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h2 className="text-sm font-medium">{t('roadmap.stages')}</h2>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setStageEditing(null);
                        setStageForm({ ...EMPTY_STAGE, position: String(stages.length) });
                        setStageOpen(true);
                      }}
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      {t('roadmap.newStage')}
                    </Button>
                  </div>
                  {stages.length === 0 ? (
                    <EmptyState titleKey="roadmap.stagesEmpty" />
                  ) : (
                    <div className="space-y-2">
                      {stages.map((s) => (
                        <Card key={s.id}>
                          <CardContent className="flex items-start gap-3 py-3">
                            <div className="flex-1 min-w-0">
                              <h3 className="font-medium">{s.title}</h3>
                              {s.description && (
                                <p className="text-xs text-muted-foreground line-clamp-2">{s.description}</p>
                              )}
                              <div className="mt-1 text-xs text-muted-foreground">
                                {s.target_date && <span>{s.target_date}</span>}
                                {' · '}
                                {s.completion}%
                              </div>
                            </div>
                            <div className="flex gap-1">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => {
                                  setStageEditing(s);
                                  setStageForm(stageToForm(s));
                                  setStageOpen(true);
                                }}
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="icon" onClick={() => setToDeleteStage(s.id)}>
                                <Trash2 className="h-4 w-4 text-destructive" />
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        ) : null}
      </IdeaPicker>

      <Dialog open={rmOpen} onOpenChange={setRmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{roadmap ? t('roadmap.edit') : t('roadmap.create')}</DialogTitle>
          </DialogHeader>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              saveRoadmapMut.mutate(roadmapFromForm(rmForm));
              setRmOpen(false);
            }}
            className="grid gap-4"
          >
            <div className="grid gap-2">
              <Label htmlFor="r-title">{t('roadmap.fields.title')}</Label>
              <Input id="r-title" required value={rmForm.title} onChange={(e) => setRmForm({ ...rmForm, title: e.target.value })} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="r-summary">{t('roadmap.fields.summary')}</Label>
              <Textarea id="r-summary" rows={2} value={rmForm.summary} onChange={(e) => setRmForm({ ...rmForm, summary: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="r-target">{t('roadmap.fields.targetCompletion')}</Label>
                <Input id="r-target" type="date" value={rmForm.target_completion} onChange={(e) => setRmForm({ ...rmForm, target_completion: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="r-completion">{t('roadmap.fields.completion')}</Label>
                <Input id="r-completion" type="number" min="0" max="100" value={rmForm.completion} onChange={(e) => setRmForm({ ...rmForm, completion: e.target.value })} />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="ghost" onClick={() => setRmOpen(false)}>
                {t('common.cancel')}
              </Button>
              <Button type="submit" disabled={saveRoadmapMut.isPending}>
                {t('common.save')}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog
        open={stageOpen}
        onOpenChange={(v) => {
          setStageOpen(v);
          if (!v) {
            setStageEditing(null);
            setStageForm(EMPTY_STAGE);
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{stageEditing ? t('roadmap.editStage') : t('roadmap.newStage')}</DialogTitle>
          </DialogHeader>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const values = stageFromForm(stageForm);
              if (stageEditing) updateStageMut.mutate({ id: stageEditing.id, values });
              else createStageMut.mutate(values);
            }}
            className="grid gap-4"
          >
            <div className="grid gap-2">
              <Label htmlFor="s-title">{t('roadmap.fields.stageTitle')}</Label>
              <Input id="s-title" required value={stageForm.title} onChange={(e) => setStageForm({ ...stageForm, title: e.target.value })} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="s-desc">{t('roadmap.fields.stageDescription')}</Label>
              <Textarea id="s-desc" rows={2} value={stageForm.description} onChange={(e) => setStageForm({ ...stageForm, description: e.target.value })} />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="s-target">{t('roadmap.fields.stageTargetDate')}</Label>
                <Input id="s-target" type="date" value={stageForm.target_date} onChange={(e) => setStageForm({ ...stageForm, target_date: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="s-completion">{t('roadmap.fields.completion')}</Label>
                <Input id="s-completion" type="number" min="0" max="100" value={stageForm.completion} onChange={(e) => setStageForm({ ...stageForm, completion: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="s-position">{t('roadmap.fields.position')}</Label>
                <Input id="s-position" type="number" value={stageForm.position} onChange={(e) => setStageForm({ ...stageForm, position: e.target.value })} />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="ghost" onClick={() => setStageOpen(false)}>
                {t('common.cancel')}
              </Button>
              <Button type="submit" disabled={createStageMut.isPending || updateStageMut.isPending}>
                {t('common.save')}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={toDeleteRm}
        onOpenChange={setToDeleteRm}
        title={t('roadmap.confirmDelete')}
        destructive
        onConfirm={() => deleteRoadmapMut.mutate()}
      />

      <ConfirmDialog
        open={!!toDeleteStage}
        onOpenChange={(v) => !v && setToDeleteStage(null)}
        title={t('roadmap.confirmStageDelete')}
        destructive
        onConfirm={() => toDeleteStage && deleteStageMut.mutate(toDeleteStage)}
      />
    </div>
  );
}