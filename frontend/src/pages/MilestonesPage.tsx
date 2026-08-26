import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Check, Edit, Plus, Trash2 } from 'lucide-react';
import { PageHeader } from '@/components/layout/PageHeader';
import { EmptyState } from '@/components/layout/EmptyState';
import { IdeaPicker } from '@/components/layout/IdeaPicker';
import { ConfirmDialog } from '@/components/layout/ConfirmDialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
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
import { milestonesApi, type Milestone, type MilestoneCreate } from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

interface FormState {
  title: string;
  description: string;
  target_date: string;
  completed_at: string;
}

const EMPTY: FormState = {
  title: '',
  description: '',
  target_date: '',
  completed_at: '',
};

function toForm(m: Milestone): FormState {
  return {
    title: m.title,
    description: m.description ?? '',
    target_date: m.target_date ?? '',
    completed_at: m.completed_at ?? '',
  };
}

function fromForm(f: FormState): MilestoneCreate {
  return {
    title: f.title,
    description: f.description || null,
    target_date: f.target_date || null,
    completed_at: f.completed_at || null,
    completion: f.completed_at ? 100 : 0,
  };
}

export default function MilestonesPage() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const qc = useQueryClient();
  const ideaId = useSelectedIdea();
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Milestone | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [toDelete, setToDelete] = useState<string | null>(null);

  const query = useQuery({
    queryKey: ['milestones', ideaId],
    queryFn: () => milestonesApi.list(ideaId!),
    enabled: !!ideaId,
  });

  const createMut = useMutation({
    mutationFn: (values: MilestoneCreate) => milestonesApi.create(ideaId!, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['milestones', ideaId] });
      setOpen(false);
      setForm(EMPTY);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, values }: { id: string; values: Partial<MilestoneCreate> }) =>
      milestonesApi.update(ideaId!, id, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['milestones', ideaId] });
      setEditing(null);
      setForm(EMPTY);
      setOpen(false);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => milestonesApi.delete(ideaId!, id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['milestones', ideaId] });
      setToDelete(null);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const todayIso = new Date().toISOString().slice(0, 10);
  const quickCompleteMut = useMutation({
    mutationFn: (id: string) =>
      milestonesApi.update(ideaId!, id, { completed_at: todayIso }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['milestones', ideaId] });
      toast({ title: t('milestones.markedDone'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const items = query.data?.items ?? [];

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="milestones.title"
        actions={
          ideaId && (
            <Button
              onClick={() => {
                setEditing(null);
                setForm(EMPTY);
                setOpen(true);
              }}
            >
              <Plus className="mr-2 h-4 w-4" />
              {t('milestones.newMilestone')}
            </Button>
          )
        }
      />

      <IdeaPicker>
        {ideaId ? (
          query.isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : items.length === 0 ? (
            <EmptyState titleKey="milestones.empty" />
          ) : (
            <div className="space-y-2">
              {items.map((m) => (
                <Card key={m.id}>
                  <CardContent className="flex items-start gap-3 py-3">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => quickCompleteMut.mutate(m.id)}
                      disabled={!!m.completed_at || quickCompleteMut.isPending}
                      title={t('milestones.markDone')}
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium">{m.title}</h3>
                      {m.description && (
                        <p className="text-xs text-muted-foreground line-clamp-2">{m.description}</p>
                      )}
                      <div className="mt-1 flex flex-wrap gap-1">
                        {m.target_date && <Badge variant="outline">{m.target_date}</Badge>}
                        {m.completed_at && (
                          <Badge variant="secondary">✓ {m.completed_at}</Badge>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          setEditing(m);
                          setForm(toForm(m));
                          setOpen(true);
                        }}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => setToDelete(m.id)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )
        ) : null}
      </IdeaPicker>

      <Dialog
        open={open}
        onOpenChange={(v) => {
          setOpen(v);
          if (!v) {
            setEditing(null);
            setForm(EMPTY);
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? t('milestones.editMilestone') : t('milestones.newMilestone')}</DialogTitle>
          </DialogHeader>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const values = fromForm(form);
              if (editing) updateMut.mutate({ id: editing.id, values });
              else createMut.mutate(values);
            }}
            className="grid gap-4"
          >
            <div className="grid gap-2">
              <Label htmlFor="milestone-title">{t('milestones.fields.title')}</Label>
              <Input id="milestone-title" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="milestone-desc">{t('milestones.fields.description')}</Label>
              <Textarea id="milestone-desc" rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="milestone-target">{t('milestones.fields.targetDate')}</Label>
                <Input id="milestone-target" type="date" value={form.target_date} onChange={(e) => setForm({ ...form, target_date: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="milestone-completed">{t('milestones.fields.completedAt')}</Label>
                <Input id="milestone-completed" type="date" value={form.completed_at} onChange={(e) => setForm({ ...form, completed_at: e.target.value })} />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
                {t('common.cancel')}
              </Button>
              <Button type="submit" disabled={createMut.isPending || updateMut.isPending}>
                {t('common.save')}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!toDelete}
        onOpenChange={(v) => !v && setToDelete(null)}
        title={t('milestones.confirmDelete')}
        destructive
        onConfirm={() => toDelete && deleteMut.mutate(toDelete)}
      />
    </div>
  );
}