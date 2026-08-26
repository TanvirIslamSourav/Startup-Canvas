import { useTranslation } from 'react-i18next';
import { cn } from '@/utils/cn';

interface Props {
  titleKey: string;
  descriptionKey?: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}

export function PageHeader({ titleKey, descriptionKey, description, actions, className }: Props) {
  const { t } = useTranslation();
  return (
    <div className={cn('flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between', className)}>
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{t(titleKey)}</h1>
        {(descriptionKey || description) && (
          <p className="text-sm text-muted-foreground">
            {descriptionKey ? t(descriptionKey) : description}
          </p>
        )}
      </div>
      {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
    </div>
  );
}