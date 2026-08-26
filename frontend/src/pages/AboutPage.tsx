import { useTranslation } from 'react-i18next';
import { Github, Heart, Languages, Moon, Sparkles } from 'lucide-react';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const STACK = [
  'React 19',
  'TypeScript',
  'Vite',
  'Tailwind CSS',
  'TanStack Query',
  'Zustand',
  'React Hook Form',
  'Zod',
  'i18next',
  'FastAPI',
  'Python 3.12',
  'PostgreSQL',
  'SQLAlchemy 2.0',
  'Pydantic v2',
  'Alembic',
  'Docker',
];

export default function AboutPage() {
  const { t } = useTranslation();

  return (
    <div className="space-y-4">
      <PageHeader titleKey="about.title" descriptionKey="about.subtitle" />

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              {t('about.visionTitle')}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            {t('about.visionBody')}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="h-4 w-4" />
              {t('about.principlesTitle')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
              <li>{t('about.principleLocal')}</li>
              <li>{t('about.principlePrivacy')}</li>
              <li>{t('about.principleA11y')}</li>
              <li>{t('about.principleI18n')}</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Languages className="h-4 w-4" />
              {t('about.i18nTitle')}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            {t('about.i18nBody')}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Moon className="h-4 w-4" />
              {t('about.themingTitle')}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            {t('about.themingBody')}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Github className="h-4 w-4" />
              {t('about.stackTitle')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {STACK.map((s) => (
                <span
                  key={s}
                  className="rounded-md border bg-muted/40 px-2 py-1 text-xs"
                >
                  {s}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}