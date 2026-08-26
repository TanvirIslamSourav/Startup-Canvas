import { useTranslation } from 'react-i18next';
import { cn } from '@/utils/cn';

interface Props {
  titleKey?: string;
  description?: string;
  descriptionKey?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({ titleKey, descriptionKey, description, icon, action, className }: Props) {
  const { t } = useTranslation();
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed bg-card/40 p-10 text-center', className)}>
      {icon ? <div className="text-muted-foreground">{icon}</div> : null}
      <h3 className="text-lg font-semibold">{titleKey ? t(titleKey) : t('common.empty')}</h3>
      {(descriptionKey || description) && (
        <p className="max-w-md text-sm text-muted-foreground">
          {descriptionKey ? t(descriptionKey) : description}
        </p>
      )}
      {action}
    </div>
  );
}