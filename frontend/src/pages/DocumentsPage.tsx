import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Edit, FileText, Plus, Trash2 } from 'lucide-react';
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
import { documentsApi, DOCUMENT_KINDS, type Document, type DocumentCreate } from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

interface FormState {
  title: string;
  kind: string;
  file_path: string;
  mime_type: string;
  size_bytes: string;
  notes: string;
}

const EMPTY: FormState = {
  title: '',
  kind: 'other',
  file_path: '',
  mime_type: '',
  size_bytes: '',
  notes: '',
};

function toForm(d: Document): FormState {
  return {
    title: d.title,
    kind: d.kind,
    file_path: d.file_path ?? '',
    mime_type: d.mime_type ?? '',
    size_bytes: d.size_bytes != null ? String(d.size_bytes) : '',
    notes: d.notes ?? '',
  };
}

function fromForm(f: FormState): DocumentCreate {
  return {
    title: f.title,
    kind: f.kind as DocumentCreate['kind'],
    file_path: f.file_path || null,
    mime_type: f.mime_type || null,
    size_bytes: f.size_bytes ? Number(f.size_bytes) : null,
    notes: f.notes || null,
  };
}

function formatSize(bytes: number | null): string {
  if (!bytes) return '';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentsPage() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const qc = useQueryClient();
  const ideaId = useSelectedIdea();
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Document | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [toDelete, setToDelete] = useState<string | null>(null);

  const query = useQuery({
    queryKey: ['documents', ideaId],
    queryFn: () => documentsApi.list(ideaId!),
    enabled: !!ideaId,
  });

  const createMut = useMutation({
    mutationFn: (values: DocumentCreate) => documentsApi.create(ideaId!, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['documents', ideaId] });
      setOpen(false);
      setForm(EMPTY);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, values }: { id: string; values: Partial<DocumentCreate> }) =>
      documentsApi.update(ideaId!, id, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['documents', ideaId] });
      setEditing(null);
      setForm(EMPTY);
      setOpen(false);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => documentsApi.delete(ideaId!, id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['documents', ideaId] });
      setToDelete(null);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const items = query.data?.items ?? [];

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="documents.title"
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
              {t('documents.newDocument')}
            </Button>
          )
        }
      />

      <IdeaPicker>
        {ideaId ? (
          query.isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : items.length === 0 ? (
            <EmptyState titleKey="documents.empty" />
          ) : (
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {items.map((d) => (
                <Card key={d.id}>
                  <CardContent className="flex items-start gap-3 py-4">
                    <FileText className="mt-1 h-5 w-5 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium truncate">{d.title}</h3>
                      <div className="mt-1 flex flex-wrap gap-1">
                        <Badge variant="secondary">{d.kind}</Badge>
                        {d.mime_type && <Badge variant="outline">{d.mime_type}</Badge>}
                        {d.size_bytes != null && (
                          <Badge variant="outline">{formatSize(d.size_bytes)}</Badge>
                        )}
                      </div>
                      {d.notes && (
                        <p className="mt-1 text-xs text-muted-foreground line-clamp-2">{d.notes}</p>
                      )}
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          setEditing(d);
                          setForm(toForm(d));
                          setOpen(true);
                        }}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => setToDelete(d.id)}>
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
            <DialogTitle>{editing ? t('documents.editDocument') : t('documents.newDocument')}</DialogTitle>
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
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="doc-title">{t('documents.fields.title')}</Label>
                <Input id="doc-title" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="doc-kind">{t('documents.fields.kind')}</Label>
                <Select
                  value={form.kind}
                  onValueChange={(v) => setForm({ ...form, kind: v })}
                >
                  <SelectTrigger id="doc-kind">
                    <SelectValue placeholder={t('documents.fields.kind')} />
                  </SelectTrigger>
                  <SelectContent>
                    {DOCUMENT_KINDS.map((k) => (
                      <SelectItem key={k} value={k}>
                        {t(`documents.kinds.${k}`, { defaultValue: k })}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="doc-path">{t('documents.fields.filePath')}</Label>
                <Input id="doc-path" value={form.file_path} onChange={(e) => setForm({ ...form, file_path: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="doc-mime">{t('documents.fields.mimeType')}</Label>
                <Input id="doc-mime" value={form.mime_type} onChange={(e) => setForm({ ...form, mime_type: e.target.value })} />
              </div>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="doc-size">{t('documents.fields.sizeBytes')}</Label>
              <Input id="doc-size" type="number" value={form.size_bytes} onChange={(e) => setForm({ ...form, size_bytes: e.target.value })} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="doc-notes">{t('documents.fields.notes')}</Label>
              <Textarea id="doc-notes" rows={2} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
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
        title={t('documents.confirmDelete')}
        destructive
        onConfirm={() => toDelete && deleteMut.mutate(toDelete)}
      />
    </div>
  );
}