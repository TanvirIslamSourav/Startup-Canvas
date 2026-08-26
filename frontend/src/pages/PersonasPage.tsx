import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Edit, Plus, Trash2 } from 'lucide-react';
import { PageHeader } from '@/components/layout/PageHeader';
import { EmptyState } from '@/components/layout/EmptyState';
import { IdeaPicker } from '@/components/layout/IdeaPicker';
import { ConfirmDialog } from '@/components/layout/ConfirmDialog';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
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
import { personasApi, type Persona, type PersonaCreate } from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

interface FormState {
  name: string;
  age: string;
  occupation: string;
  goals: string;
  pain_points: string;
  needs: string;
  behaviour: string;
  avatar_url: string;
}

const EMPTY: FormState = {
  name: '',
  age: '',
  occupation: '',
  goals: '',
  pain_points: '',
  needs: '',
  behaviour: '',
  avatar_url: '',
};

function toForm(p: Persona): FormState {
  return {
    name: p.name,
    age: p.age != null ? String(p.age) : '',
    occupation: p.occupation ?? '',
    goals: p.goals ?? '',
    pain_points: p.pain_points ?? '',
    needs: p.needs ?? '',
    behaviour: p.behaviour ?? '',
    avatar_url: p.avatar_url ?? '',
  };
}

function fromForm(f: FormState): PersonaCreate {
  return {
    name: f.name,
    age: f.age ? Number(f.age) : null,
    occupation: f.occupation || null,
    goals: f.goals || null,
    pain_points: f.pain_points || null,
    needs: f.needs || null,
    behaviour: f.behaviour || null,
    avatar_url: f.avatar_url || null,
  };
}

function initials(name: string): string {
  return name
    .split(/\s+/)
    .map((p) => p.charAt(0))
    .join('')
    .slice(0, 2)
    .toUpperCase() || '?';
}

export default function PersonasPage() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const qc = useQueryClient();
  const ideaId = useSelectedIdea();
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Persona | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [toDelete, setToDelete] = useState<string | null>(null);

  const query = useQuery({
    queryKey: ['personas', ideaId],
    queryFn: () => personasApi.list(ideaId!),
    enabled: !!ideaId,
  });

  const createMut = useMutation({
    mutationFn: (values: PersonaCreate) => personasApi.create(ideaId!, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['personas', ideaId] });
      setOpen(false);
      setForm(EMPTY);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, values }: { id: string; values: PersonaCreate }) =>
      personasApi.update(ideaId!, id, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['personas', ideaId] });
      setEditing(null);
      setForm(EMPTY);
      setOpen(false);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => personasApi.delete(ideaId!, id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['personas', ideaId] });
      setToDelete(null);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const items = query.data?.items ?? [];

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="personas.title"
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
              {t('personas.newPersona')}
            </Button>
          )
        }
      />

      <IdeaPicker>
        {ideaId ? (
          query.isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : items.length === 0 ? (
            <EmptyState titleKey="common.empty" />
          ) : (
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {items.map((p) => (
                <Card key={p.id}>
                  <CardContent className="flex items-start gap-3 pt-4">
                    <Avatar className="h-12 w-12">
                      {p.avatar_url && <AvatarImage src={p.avatar_url} alt={p.name} />}
                      <AvatarFallback>{initials(p.name)}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium">{p.name}</h3>
                      {p.occupation && (
                        <p className="text-xs text-muted-foreground">{p.occupation}</p>
                      )}
                      {p.age != null && (
                        <p className="text-xs text-muted-foreground">{p.age} yrs</p>
                      )}
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          setEditing(p);
                          setForm(toForm(p));
                          setOpen(true);
                        }}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => setToDelete(p.id)}>
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
            <DialogTitle>
              {editing ? t('personas.editPersona') : t('personas.newPersona')}
            </DialogTitle>
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
                <Label htmlFor="p-name">{t('personas.fields.name')}</Label>
                <Input id="p-name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="p-age">{t('personas.fields.age')}</Label>
                <Input id="p-age" type="number" value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="p-occupation">{t('personas.fields.occupation')}</Label>
                <Input id="p-occupation" value={form.occupation} onChange={(e) => setForm({ ...form, occupation: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="p-avatar">{t('personas.fields.avatarUrl')}</Label>
                <Input id="p-avatar" value={form.avatar_url} onChange={(e) => setForm({ ...form, avatar_url: e.target.value })} />
              </div>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="p-goals">{t('personas.fields.goals')}</Label>
              <Textarea id="p-goals" rows={2} value={form.goals} onChange={(e) => setForm({ ...form, goals: e.target.value })} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="p-pain">{t('personas.fields.painPoints')}</Label>
              <Textarea id="p-pain" rows={2} value={form.pain_points} onChange={(e) => setForm({ ...form, pain_points: e.target.value })} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="p-needs">{t('personas.fields.needs')}</Label>
              <Textarea id="p-needs" rows={2} value={form.needs} onChange={(e) => setForm({ ...form, needs: e.target.value })} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="p-beh">{t('personas.fields.behaviour')}</Label>
              <Textarea id="p-beh" rows={2} value={form.behaviour} onChange={(e) => setForm({ ...form, behaviour: e.target.value })} />
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
        title={t('personas.confirmDelete')}
        destructive
        onConfirm={() => toDelete && deleteMut.mutate(toDelete)}
      />
    </div>
  );
}