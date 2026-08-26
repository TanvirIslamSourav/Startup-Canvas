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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/toast';
import { tasksApi, TASK_STATUSES, TASK_PRIORITIES, type Task, type TaskCreate } from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

interface FormState {
  title: string;
  description: string;
  status: string;
  priority: string;
  due_date: string;
}

const EMPTY: FormState = {
  title: '',
  description: '',
  status: 'todo',
  priority: 'medium',
  due_date: '',
};

function toForm(t: Task): FormState {
  return {
    title: t.title,
    description: t.description ?? '',
    status: t.status,
    priority: t.priority,
    due_date: t.due_date ?? '',
  };
}

function fromForm(f: FormState): TaskCreate {
  return {
    title: f.title,
    description: f.description || null,
    status: f.status as TaskCreate['status'],
    priority: f.priority as TaskCreate['priority'],
    due_date: f.due_date || null,
    progress: f.status === 'done' ? 100 : 0,
    started_at: null,
    completed_at: f.status === 'done' ? new Date().toISOString() : null,
  };
}

export default function TasksPage() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const qc = useQueryClient();
  const ideaId = useSelectedIdea();
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Task | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [toDelete, setToDelete] = useState<string | null>(null);

  const query = useQuery({
    queryKey: ['tasks', ideaId],
    queryFn: () => tasksApi.list(ideaId!),
    enabled: !!ideaId,
  });

  const createMut = useMutation({
    mutationFn: (values: TaskCreate) => tasksApi.create(ideaId!, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['tasks', ideaId] });
      setOpen(false);
      setForm(EMPTY);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, values }: { id: string; values: Partial<TaskCreate> }) =>
      tasksApi.update(ideaId!, id, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['tasks', ideaId] });
      setEditing(null);
      setForm(EMPTY);
      setOpen(false);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => tasksApi.delete(ideaId!, id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['tasks', ideaId] });
      setToDelete(null);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const quickCompleteMut = useMutation({
    mutationFn: (id: string) =>
      tasksApi.update(ideaId!, id, { status: 'done' }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['tasks', ideaId] });
      toast({ title: t('tasks.markedDone'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const items = query.data?.items ?? [];

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="tasks.title"
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
              {t('tasks.newTask')}
            </Button>
          )
        }
      />

      <IdeaPicker>
        {ideaId ? (
          query.isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : items.length === 0 ? (
            <EmptyState titleKey="tasks.empty" />
          ) : (
            <div className="space-y-2">
              {items.map((task) => (
                <Card key={task.id}>
                  <CardContent className="flex items-start gap-3 py-3">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => quickCompleteMut.mutate(task.id)}
                      disabled={task.status === 'done' || quickCompleteMut.isPending}
                      title={t('tasks.markDone')}
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                    <div className="flex-1 min-w-0">
                      <h3 className={`font-medium ${task.status === 'done' ? 'line-through text-muted-foreground' : ''}`}>
                        {task.title}
                      </h3>
                      {task.description && (
                        <p className="text-xs text-muted-foreground line-clamp-2">{task.description}</p>
                      )}
                      <div className="mt-1 flex flex-wrap gap-1">
                        <Badge variant="secondary">{task.status}</Badge>
                        <Badge variant="outline">{task.priority}</Badge>
                        {task.due_date && (
                          <Badge variant="outline">{task.due_date}</Badge>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          setEditing(task);
                          setForm(toForm(task));
                          setOpen(true);
                        }}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => setToDelete(task.id)}>
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
            <DialogTitle>{editing ? t('tasks.editTask') : t('tasks.newTask')}</DialogTitle>
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
              <Label htmlFor="task-title">{t('tasks.fields.title')}</Label>
              <Input id="task-title" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="task-desc">{t('tasks.fields.description')}</Label>
              <Textarea id="task-desc" rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="task-status">{t('tasks.fields.status')}</Label>
                <Select
                  value={form.status}
                  onValueChange={(v) => setForm({ ...form, status: v })}
                >
                  <SelectTrigger id="task-status">
                    <SelectValue placeholder={t('tasks.fields.status')} />
                  </SelectTrigger>
                  <SelectContent>
                    {TASK_STATUSES.map((s) => (
                      <SelectItem key={s} value={s}>
                        {t(`tasks.statuses.${s}`)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="task-priority">{t('tasks.fields.priority')}</Label>
                <Select
                  value={form.priority}
                  onValueChange={(v) => setForm({ ...form, priority: v })}
                >
                  <SelectTrigger id="task-priority">
                    <SelectValue placeholder={t('tasks.fields.priority')} />
                  </SelectTrigger>
                  <SelectContent>
                    {TASK_PRIORITIES.map((p) => (
                      <SelectItem key={p} value={p}>
                        {t(`tasks.priorities.${p}`)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="task-due">{t('tasks.fields.dueDate')}</Label>
                <Input id="task-due" type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
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
        title={t('tasks.confirmDelete')}
        destructive
        onConfirm={() => toDelete && deleteMut.mutate(toDelete)}
      />
    </div>
  );
}