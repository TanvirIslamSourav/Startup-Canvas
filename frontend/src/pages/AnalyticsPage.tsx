import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { PageHeader } from '@/components/layout/PageHeader';
import { EmptyState } from '@/components/layout/EmptyState';
import { IdeaPicker } from '@/components/layout/IdeaPicker';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { dashboardApi, tasksApi, TASK_STATUSES } from '@/services/modules';
import { useSelectedIdea } from '@/hooks/useSelectedIdea';

const STATUS_COLORS: Record<string, string> = {
  todo: 'hsl(var(--muted))',
  in_progress: 'hsl(var(--primary))',
  blocked: 'hsl(var(--destructive))',
  done: 'hsl(var(--accent))',
};

export default function AnalyticsPage() {
  const { t } = useTranslation();
  const ideaId = useSelectedIdea();

  const summary = useQuery({
    queryKey: ['dashboard', ideaId],
    queryFn: () => dashboardApi.summary(ideaId!),
    enabled: !!ideaId,
  });

  const tasks = useQuery({
    queryKey: ['tasks', ideaId],
    queryFn: () => tasksApi.list(ideaId!),
    enabled: !!ideaId,
  });

  const summaryData = summary.data;
  const taskItems = tasks.data?.items ?? [];

  const taskData = TASK_STATUSES.map((s) => ({
    name: s,
    value: taskItems.filter((tk) => tk.status === s).length,
  })).filter((d) => d.value > 0 || d.name === 'todo' || d.name === 'in_progress' || d.name === 'blocked' || d.name === 'done');

  const resourceData = summaryData
    ? [
        { name: t('analytics.competitors'), value: summaryData.resource_counts.competitors },
        { name: t('analytics.personas'), value: summaryData.resource_counts.personas },
        { name: t('analytics.tasks'), value: summaryData.resource_counts.tasks },
        { name: t('analytics.milestones'), value: summaryData.resource_counts.milestones },
        { name: t('analytics.documents'), value: summaryData.resource_counts.documents },
        { name: t('analytics.notes'), value: summaryData.resource_counts.notes },
      ]
    : [];

  return (
    <div className="space-y-4">
      <PageHeader titleKey="analytics.title" descriptionKey="analytics.subtitle" />

      <IdeaPicker>
        {ideaId ? (
          summary.isLoading ? (
            <Skeleton className="h-64 w-full" />
          ) : !summaryData ? (
            <EmptyState titleKey="analytics.empty" />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>{t('analytics.taskBreakdown')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={260}>
                    <PieChart>
                      <Pie
                        data={taskData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label
                      >
                        {taskData.map((d) => (
                          <Cell key={d.name} fill={STATUS_COLORS[d.name] ?? 'hsl(var(--muted))'} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>{t('analytics.resources')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={260}>
                    <BarChart data={resourceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="value" fill="hsl(var(--primary))" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>{t('analytics.keyMetrics')}</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-3">
                  <MetricRow
                    label={t('analytics.milestoneAvg')}
                    value={summaryData.milestone_completion_avg}
                    suffix="%"
                  />
                  <MetricRow
                    label={t('analytics.roadmapCompletion')}
                    value={summaryData.roadmap_completion ?? 0}
                    suffix="%"
                  />
                  <MetricRow
                    label={t('analytics.roadmapStages')}
                    value={summaryData.roadmap_stage_count}
                  />
                </CardContent>
              </Card>
            </div>
          )
        ) : null}
      </IdeaPicker>
    </div>
  );
}

function MetricRow({ label, value, suffix }: { label: string; value: number; suffix?: string }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium">
        {value}
        {suffix ?? ''}
      </span>
    </div>
  );
}