import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface Props {
  titleKey: string;
  description?: string;
}

export default function PlaceholderPage({ titleKey, description }: Props) {
  const { t } = useTranslation();
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">{t(titleKey)}</h1>
      <Card>
        <CardHeader>
          <CardTitle>{t(titleKey)}</CardTitle>
          <CardDescription>{description ?? t('common.empty')}</CardDescription>
        </CardHeader>
        <CardContent />
      </Card>
    </div>
  );
}