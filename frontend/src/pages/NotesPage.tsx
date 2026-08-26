import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Pin, PinOff, Plus, Trash2, X } from 'lucide-react';
import { PageHeader } from '@/components/layout/PageHeader';
import { EmptyState } from '@/components/layout/EmptyState';
import { IdeaPicker } from '@/components/layout/IdeaPicker';
import { ConfirmDialog } from '@/components/layout/ConfirmDialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/toast';
import { notesApi, type Note, type NoteCreate } from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

export default function NotesPage() {
  const { t, i18n } = useTranslation();
  const { toast } = useToast();
  const qc = useQueryClient();
  const ideaId = useSelectedIdea();
  const [open, setOpen] = useState(false);
  const [body, setBody] = useState('');
  const [pinned, setPinned] = useState(false);
  const [toDelete, setToDelete] = useState<string | null>(null);

  const query = useQuery({
    queryKey: ['notes', ideaId],
    queryFn: () => notesApi.list(ideaId!),
    enabled: !!ideaId,
  });

  const createMut = useMutation({
    mutationFn: (values: NoteCreate) => notesApi.create(ideaId!, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['notes', ideaId] });
      setOpen(false);
      setBody('');
      setPinned(false);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => notesApi.delete(ideaId!, id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['notes', ideaId] });
      setToDelete(null);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const togglePinMut = useMutation({
    mutationFn: (n: Note) => notesApi.update(ideaId!, n.id, { pinned: !n.pinned }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['notes', ideaId] });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const items = useMemo(() => {
    const list = query.data?.items ?? [];
    return [...list].sort((a, b) => {
      if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });
  }, [query.data]);

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="notes.title"
        actions={
          ideaId && (
            <Button
              onClick={() => {
                setBody('');
                setPinned(false);
                setOpen(true);
              }}
            >
              <Plus className="mr-2 h-4 w-4" />
              {t('notes.newNote')}
            </Button>
          )
        }
      />

      <IdeaPicker>
        {ideaId ? (
          query.isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : items.length === 0 ? (
            <EmptyState titleKey="notes.empty" />
          ) : (
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {items.map((n) => (
                <Card key={n.id}>
                  <CardContent className="py-4">
                    <div className="flex items-start justify-between gap-2">
                      <p className="whitespace-pre-wrap text-sm flex-1">{n.body}</p>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => togglePinMut.mutate(n)}
                          title={n.pinned ? t('notes.unpin') : t('notes.pin')}
                        >
                          {n.pinned ? (
                            <PinOff className="h-4 w-4" />
                          ) : (
                            <Pin className="h-4 w-4" />
                          )}
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => setToDelete(n.id)}>
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </div>
                    <p className="mt-2 text-xs text-muted-foreground">
                      {new Date(n.created_at).toLocaleString(i18n.language)}
                    </p>
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
            setBody('');
            setPinned(false);
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('notes.newNote')}</DialogTitle>
          </DialogHeader>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!body.trim()) return;
              createMut.mutate({ body: body.trim(), pinned });
            }}
            className="grid gap-4"
          >
            <div className="grid gap-2">
              <Label htmlFor="note-body">{t('notes.fields.body')}</Label>
              <Textarea
                id="note-body"
                rows={6}
                required
                value={body}
                onChange={(e) => setBody(e.target.value)}
              />
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={pinned}
                onChange={(e) => setPinned(e.target.checked)}
              />
              {t('notes.fields.pinned')}
            </label>
            <DialogFooter>
              <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
                <X className="mr-2 h-4 w-4" />
                {t('common.cancel')}
              </Button>
              <Button type="submit" disabled={createMut.isPending || !body.trim()}>
                {t('common.save')}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!toDelete}
        onOpenChange={(v) => !v && setToDelete(null)}
        title={t('notes.confirmDelete')}
        destructive
        onConfirm={() => toDelete && deleteMut.mutate(toDelete)}
      />
    </div>
  );
}