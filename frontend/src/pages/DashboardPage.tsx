import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { CheckCircle2, Clock, ListChecks, TrendingUp } from 'lucide-react';
import { PageHeader } from '@/components/layout/PageHeader';
import { EmptyState } from '@/components/layout/EmptyState';
import { IdeaPicker } from '@/components/layout/IdeaPicker';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import {
  dashboardApi,
  tasksApi,
  TASK_STATUSES,
  type DashboardSummary,
  type Task,
} from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

function MetricCard({
  title,
  value,
  hint,
  icon: Icon,
}: {
  title: string;
  value: number | string;
  hint?: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <Card>
      <CardContent className="flex items-start gap-3 pt-4">
        <Icon className="mt-1 h-5 w-5 text-muted-foreground" />
        <div className="flex-1">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">{title}</p>
          <p className="text-2xl font-semibold leading-tight">{value}</p>
          {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
        </div>
      </CardContent>
    </Card>
  );
}

function StatusBreakdown({ tasks }: { tasks: Task[] }) {
  const total = tasks.length;
  if (total === 0) {
    return (
      <p className="text-xs text-muted-foreground">No tasks yet.</p>
    );
  }
  return (
    <ul className="space-y-2 text-sm">
      {TASK_STATUSES.map((status) => {
        const count = tasks.filter((t) => t.status === status).length;
        const pct = Math.round((count / total) * 100);
        return (
          <li key={status} className="flex items-center gap-2">
            <span className="w-32 capitalize text-muted-foreground">{status.replace('_', ' ')}</span>
            <div className="h-2 flex-1 rounded-full bg-muted overflow-hidden">
              <div
                className="h-full bg-primary"
                style={{ width: `${pct}%` }}
                aria-hidden
              />
            </div>
            <span className="w-12 text-right tabular-nums">{count}</span>
          </li>
        );
      })}
    </ul>
  );
}

function SummaryCard({ summary }: { summary: DashboardSummary | undefined }) {
  if (!summary) return null;
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Overview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Task completion</span>
          <span className="font-medium">
            {summary.task_counts.total
              ? `${Math.round((summary.task_counts.done / summary.task_counts.total) * 100)}%`
              : '0%'}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Milestone avg</span>
          <span className="font-medium">{summary.milestone_completion_avg ?? 0}%</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Roadmap</span>
          <Badge variant={summary.roadmap_id ? 'default' : 'outline'}>
            {summary.roadmap_id ? `${summary.roadmap_completion ?? 0}%` : '—'}
          </Badge>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Roadmap stages</span>
          <span className="font-medium">{summary.roadmap_stage_count}</span>
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { t } = useTranslation();
  const ideaId = useSelectedIdea();

  const summaryQuery = useQuery({
    queryKey: ['dashboard', ideaId],
    queryFn: () => dashboardApi.summary(ideaId!),
    enabled: !!ideaId,
  });

  const tasksQuery = useQuery({
    queryKey: ['tasks', ideaId],
    queryFn: () => tasksApi.list(ideaId!),
    enabled: !!ideaId,
  });

  const tasks = tasksQuery.data?.items ?? [];
  const done = tasks.filter((tk) => tk.status === 'done').length;
  const inProgress = tasks.filter((tk) => tk.status === 'in_progress').length;

  return (
    <div className="space-y-4">
      <PageHeader
        titleKey="dashboard.title"
        descriptionKey="dashboard.subtitle"
      />

      <IdeaPicker>
        {ideaId ? (
          summaryQuery.isLoading || tasksQuery.isLoading ? (
            <Skeleton className="h-48 w-full" />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              <div className="grid gap-3 md:grid-cols-2">
                <MetricCard
                  title={t('dashboard.metrics.tasks')}
                  value={tasks.length}
                  icon={ListChecks}
                  hint={`${inProgress} ${t('dashboard.metrics.inProgress')}`}
                />
                <MetricCard
                  title={t('dashboard.metrics.done')}
                  value={done}
                  icon={CheckCircle2}
                  hint={t('dashboard.metrics.completedHint')}
                />
                <MetricCard
                  title={t('dashboard.metrics.pending')}
                  value={tasks.length - done}
                  icon={Clock}
                />
                <MetricCard
                  title={t('dashboard.metrics.score')}
                  value={summaryQuery.data ? `${summaryQuery.data.milestone_completion_avg ?? 0}%` : '—'}
                  icon={TrendingUp}
                  hint={t('dashboard.metrics.scoreHint')}
                />
              </div>
              <SummaryCard summary={summaryQuery.data} />
              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle className="text-sm">{t('dashboard.breakdown.title')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <StatusBreakdown tasks={tasks} />
                </CardContent>
              </Card>
            </div>
          )
        ) : (
          <EmptyState titleKey="common.empty" />
        )}
      </IdeaPicker>
    </div>
  );
}
