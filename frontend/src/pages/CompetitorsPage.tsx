import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Edit, Plus, Trash2 } from 'lucide-react';
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
  competitorsApi,
  type Competitor,
  type CompetitorCreate,
} from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

interface FormState {
  name: string;
  website_url: string;
  pricing: string;
  pricing_currency: string;
  strengths: string;
  weaknesses: string;
  features: string;
  market_position: string;
  notes: string;
}

const EMPTY: FormState = {
  name: '',
  website_url: '',
  pricing: '',
  pricing_currency: 'USD',
  strengths: '',
  weaknesses: '',
  features: '',
  market_position: '',
  notes: '',
};

function toForm(c: Competitor): FormState {
  return {
    name: c.name,
    website_url: c.website_url ?? '',
    pricing: c.pricing != null ? String(c.pricing) : '',
    pricing_currency: c.pricing_currency ?? 'USD',
    strengths: c.strengths ?? '',
    weaknesses: c.weaknesses ?? '',
    features: '',
    market_position: c.market_position ?? '',
    notes: c.notes ?? '',
  };
}

function fromForm(f: FormState): CompetitorCreate {
  return {
    name: f.name,
    website_url: f.website_url || null,
    pricing: f.pricing ? Number(f.pricing) : null,
    pricing_currency: f.pricing_currency || 'USD',
    strengths: f.strengths || null,
    weaknesses: f.weaknesses || null,
    features: [],
    market_position: f.market_position || null,
    notes: f.notes || null,
  };
}

export default function CompetitorsPage() {
  const { t } = useTranslation();
  const { toast } = useToast();
  const qc = useQueryClient();
  const ideaId = useSelectedIdea();
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Competitor | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [toDelete, setToDelete] = useState<string | null>(null);

  const query = useQuery({
    queryKey: ['competitors', ideaId],
    queryFn: () => competitorsApi.list(ideaId!),
    enabled: !!ideaId,
  });

  const createMut = useMutation({
    mutationFn: (values: CompetitorCreate) => competitorsApi.create(ideaId!, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['competitors', ideaId] });
      setOpen(false);
      setForm(EMPTY);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, values }: { id: string; values: CompetitorCreate }) =>
      competitorsApi.update(ideaId!, id, values),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['competitors', ideaId] });
      setEditing(null);
      setForm(EMPTY);
      setOpen(false);
      toast({ title: t('common.save'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => competitorsApi.delete(ideaId!, id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['competitors', ideaId] });
      setToDelete(null);
      toast({ title: t('common.delete'), variant: 'success' });
    },
    onError: () => toast({ title: t('common.error'), variant: 'destructive' }),
  });

  const items = query.data?.items ?? [];

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="competitors.title"
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
              {t('competitors.newCompetitor')}
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
            <div className="grid gap-3 md:grid-cols-2">
              {items.map((c) => (
                <Card key={c.id}>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle className="text-base">{c.name}</CardTitle>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          setEditing(c);
                          setForm(toForm(c));
                          setOpen(true);
                        }}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => setToDelete(c.id)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-1 text-sm">
                    {c.website_url && (
                      <p className="truncate text-xs text-muted-foreground">{c.website_url}</p>
                    )}
                    {c.pricing != null && (
                      <p className="text-xs">
                        {t('competitors.fields.pricing')}: {c.pricing} {c.pricing_currency}
                      </p>
                    )}
                    {c.market_position && (
                      <p className="text-xs">{c.market_position}</p>
                    )}
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
              {editing ? t('competitors.editCompetitor') : t('competitors.newCompetitor')}
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
                <Label htmlFor="name">{t('competitors.fields.name')}</Label>
                <Input id="name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="url">{t('competitors.fields.websiteUrl')}</Label>
                <Input id="url" value={form.website_url} onChange={(e) => setForm({ ...form, website_url: e.target.value })} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="pricing">{t('competitors.fields.pricing')}</Label>
                <Input id="pricing" type="number" value={form.pricing} onChange={(e) => setForm({ ...form, pricing: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="currency">{t('competitors.fields.pricingCurrency')}</Label>
                <Input id="currency" value={form.pricing_currency} onChange={(e) => setForm({ ...form, pricing_currency: e.target.value })} />
              </div>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="strengths">{t('competitors.fields.strengths')}</Label>
              <Textarea id="strengths" rows={2} value={form.strengths} onChange={(e) => setForm({ ...form, strengths: e.target.value })} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="weaknesses">{t('competitors.fields.weaknesses')}</Label>
              <Textarea id="weaknesses" rows={2} value={form.weaknesses} onChange={(e) => setForm({ ...form, weaknesses: e.target.value })} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="position">{t('competitors.fields.marketPosition')}</Label>
              <Input id="position" value={form.market_position} onChange={(e) => setForm({ ...form, market_position: e.target.value })} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="notes">{t('competitors.fields.notes')}</Label>
              <Textarea id="notes" rows={2} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
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
        title={t('competitors.confirmDelete')}
        destructive
        onConfirm={() => toDelete && deleteMut.mutate(toDelete)}
      />
    </div>
  );
}