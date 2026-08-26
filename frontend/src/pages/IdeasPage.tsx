import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Edit, Plus, Trash2, Archive, ArchiveRestore, Search } from 'lucide-react';
import { PageHeader } from '@/components/layout/PageHeader';
import { EmptyState } from '@/components/layout/EmptyState';
import { ConfirmDialog } from '@/components/layout/ConfirmDialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/components/ui/toast';
import {
  ideasApi,
  IDEA_STATUSES,
  type IdeaStatus,
  type IdeaCreate,
  type IdeaUpdate,
} from '@/services/modules';
import { useWorkspace } from '@/store/workspace';
import { cn } from '@/utils/cn';
import { useProjects } from '@/hooks/useProjects';

function IdeaFormDialog({
  open,
  onOpenChange,
  initial,
  onSubmit,
  busy,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  initial?: Partial<IdeaCreate>;
  onSubmit: (values: IdeaCreate) => void;
  busy?: boolean;
}) {
  const { t } = useTranslation();
  const { selectedProjectId, setSelectedProjectId } = useWorkspace();
  const projectsQuery = useProjects();
  const projects = projectsQuery.data ?? [];
  const activeProjectId =
    selectedProjectId ?? projects[0]?.id ?? '00000000-0000-0000-0000-000000000000';
  const [title, setTitle] = useState(initial?.title ?? '');
  const [problem, setProblem] = useState(initial?.problem ?? '');
  const [solution, setSolution] = useState(initial?.solution ?? '');
  const [audience, setAudience] = useState(initial?.audience ?? '');
  const [category, setCategory] = useState(initial?.category ?? '');
  const [status, setStatus] = useState<IdeaStatus>(initial?.status ?? 'draft');
  const [priority, setPriority] = useState<number>(initial?.priority ?? 3);
  const [score, setScore] = useState<number>(initial?.score ?? 0);
  const [tags, setTags] = useState((initial?.tags ?? []).join(', '));

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{initial?.title ? t('ideas.editIdea') : t('ideas.newIdea')}</DialogTitle>
        </DialogHeader>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (!selectedProjectId && activeProjectId) setSelectedProjectId(activeProjectId);
            onSubmit({
              project_id: activeProjectId,
              title,
              problem: problem || null,
              solution: solution || null,
              audience: audience || null,
              category: category || null,
              status,
              priority,
              score,
              tags: tags.split(',').map((s) => s.trim()).filter(Boolean),
            });
          }}
          className="grid gap-4"
        >
          <div className="grid gap-2">
            <Label htmlFor="title">{t('ideas.fields.title')}</Label>
            <Input id="title" required value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="status">{t('ideas.fields.status')}</Label>
              <Select value={status} onValueChange={(v) => setStatus(v as IdeaStatus)}>
                <SelectTrigger id="status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {IDEA_STATUSES.map((s) => (
                    <SelectItem key={s} value={s}>
                      {t(`ideas.statuses.${s}`)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="priority">{t('ideas.fields.priority')}</Label>
              <Select value={String(priority)} onValueChange={(v) => setPriority(Number(v))}>
                <SelectTrigger id="priority">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {[0, 1, 2, 3, 4, 5].map((p) => (
                    <SelectItem key={p} value={String(p)}>
                      {t(`ideas.priorities.${p}`)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="problem">{t('ideas.fields.problem')}</Label>
            <Textarea id="problem" rows={3} value={problem} onChange={(e) => setProblem(e.target.value)} />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="solution">{t('ideas.fields.solution')}</Label>
            <Textarea id="solution" rows={3} value={solution} onChange={(e) => setSolution(e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="audience">{t('ideas.fields.audience')}</Label>
              <Input id="audience" value={audience} onChange={(e) => setAudience(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="category">{t('ideas.fields.category')}</Label>
              <Input id="category" value={category} onChange={(e) => setCategory(e.target.value)} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="score">{t('ideas.fields.score')}</Label>
              <Input
                id="score"
                type="number"
                min={0}
                max={100}
                value={score}
                onChange={(e) => setScore(Number(e.target.value))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="tags">{t('ideas.fields.tags')}</Label>
              <Input id="tags" value={tags} onChange={(e) => setTags(e.target.value)} />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>
              {t('common.cancel')}
            </Button>
            <Button type="submit" disabled={busy}>
              {busy ? t('common.saving') : t('common.save')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function IdeasPage() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const qc = useQueryClient();
  const { selectedIdeaId, setSelectedIdeaId } = useWorkspace();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<IdeaStatus | 'all'>('all');
  const [includeArchived, setIncludeArchived] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [editing, setEditing] = useState<string | null>(null);
  const [toDelete, setToDelete] = useState<string | null>(null);

  const query = useQuery({
    queryKey: ['ideas', { search, statusFilter, includeArchived }],
    queryFn: () =>
      ideasApi.list({
        search: search || undefined,
        status: statusFilter === 'all' ? undefined : statusFilter,
        include_archived: includeArchived,
        limit: 100,
      }),
  });

  const ideas = useMemo(() => query.data?.items ?? [], [query.data]);

  const createMut = useMutation({
    mutationFn: (values: IdeaCreate) => ideasApi.create(values),
    onSuccess: (idea) => {
      void qc.invalidateQueries({ queryKey: ['ideas'] });
      setCreateOpen(false);
      setSelectedIdeaId(idea.id);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, values }: { id: string; values: IdeaUpdate }) =>
      ideasApi.update(id, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['ideas'] });
      setEditing(null);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const archiveMut = useMutation({
    mutationFn: ({ id, archived }: { id: string; archived: boolean }) =>
      ideasApi.update(id, { is_archived: archived }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['ideas'] });
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => ideasApi.delete(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['ideas'] });
      setToDelete(null);
      if (selectedIdeaId === toDelete) setSelectedIdeaId(null);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const editingIdea = ideas.find((i) => i.id === editing);

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="ideas.title"
        descriptionKey="app.tagline"
        actions={
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            {t('ideas.newIdea')}
          </Button>
        }
      />

      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder={t('common.search')}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-8"
          />
        </div>
        <Select value={statusFilter} onValueChange={(v) => setStatusFilter(v as IdeaStatus | 'all')}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder={t('ideas.filters.status')} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t('common.selectAll')}</SelectItem>
            {IDEA_STATUSES.map((s) => (
              <SelectItem key={s} value={s}>
                {t(`ideas.statuses.${s}`)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          variant={includeArchived ? 'secondary' : 'outline'}
          onClick={() => setIncludeArchived((v) => !v)}
        >
          {t('ideas.filters.includeArchived')}
        </Button>
      </div>

      {query.isLoading ? (
        <div className="space-y-2">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      ) : ideas.length === 0 ? (
        <EmptyState
          titleKey="ideas.noIdeasTitle"
          descriptionKey="ideas.noIdeasHelper"
          action={
            <Button onClick={() => setCreateOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              {t('ideas.newIdea')}
            </Button>
          }
        />
      ) : (
        <div className="overflow-hidden rounded-md border">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 text-left">
              <tr>
                <th className="px-3 py-2 font-medium">{t('ideas.fields.title')}</th>
                <th className="px-3 py-2 font-medium">{t('ideas.fields.status')}</th>
                <th className="px-3 py-2 font-medium">{t('ideas.fields.priority')}</th>
                <th className="px-3 py-2 font-medium">{t('ideas.fields.score')}</th>
                <th className="px-3 py-2 font-medium text-right">{t('common.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {ideas.map((idea) => {
                const isSelected = idea.id === selectedIdeaId;
                return (
                  <tr
                    key={idea.id}
                    className={cn(
                      'border-t cursor-pointer transition-colors hover:bg-accent/40',
                      isSelected && 'bg-accent/60',
                    )}
                    onClick={() => setSelectedIdeaId(idea.id)}
                  >
                    <td className="px-3 py-2">
                      <div className="font-medium">{idea.title}</div>
                      {idea.tags && idea.tags.length > 0 && (
                        <div className="mt-1 flex flex-wrap gap-1">
                          {idea.tags.map((tag) => (
                            <Badge key={tag} variant="secondary">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </td>
                    <td className="px-3 py-2">
                      <Badge variant={idea.is_archived ? 'outline' : 'default'}>
                        {t(`ideas.statuses.${idea.status}`)}
                      </Badge>
                    </td>
                    <td className="px-3 py-2">{t(`ideas.priorities.${idea.priority}`)}</td>
                    <td className="px-3 py-2">{idea.score}</td>
                    <td className="px-3 py-2 text-right">
                      <div className="inline-flex gap-1" onClick={(e) => e.stopPropagation()}>
                        <Button variant="ghost" size="icon" onClick={() => setEditing(idea.id)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => archiveMut.mutate({ id: idea.id, archived: !idea.is_archived })}
                          title={idea.is_archived ? t('ideas.restoreIdea') : t('ideas.archiveIdea')}
                        >
                          {idea.is_archived ? (
                            <ArchiveRestore className="h-4 w-4" />
                          ) : (
                            <Archive className="h-4 w-4" />
                          )}
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => setToDelete(idea.id)}>
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <IdeaFormDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        busy={createMut.isPending}
        onSubmit={(v) => createMut.mutate(v)}
      />

      {editingIdea && (
        <IdeaFormDialog
          open
          onOpenChange={(v) => !v && setEditing(null)}
          initial={{
            title: editingIdea.title,
            problem: editingIdea.problem ?? '',
            solution: editingIdea.solution ?? '',
            audience: editingIdea.audience ?? '',
            category: editingIdea.category ?? '',
            status: editingIdea.status,
            priority: editingIdea.priority,
            score: editingIdea.score,
            tags: editingIdea.tags ?? [],
          }}
          busy={updateMut.isPending}
          onSubmit={(v) => updateMut.mutate({ id: editingIdea.id, values: v })}
        />
      )}

      <ConfirmDialog
        open={!!toDelete}
        onOpenChange={(v) => !v && setToDelete(null)}
        title={t('ideas.confirmDelete')}
        destructive
        onConfirm={() => toDelete && deleteMut.mutate(toDelete)}
      />
    </div>
  );
}