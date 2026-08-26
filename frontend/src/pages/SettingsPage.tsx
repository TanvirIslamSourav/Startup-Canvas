import { useTranslation } from 'react-i18next';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useTheme, THEMES, type Theme } from '@/hooks/useTheme';
import { useLanguage } from '@/hooks/useLanguage';

export default function SettingsPage() {
  const { t } = useTranslation();
  const { theme, setTheme } = useTheme();
  const { language, setLanguage } = useLanguage();

  return (
    <div className="space-y-4">
      <PageHeader titleKey="settings.title" />

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">{t('settings.appearance')}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid gap-2 max-w-sm">
            <Label htmlFor="settings-theme">{t('common.theme')}</Label>
            <Select
              value={theme}
              onValueChange={(v: string) => setTheme(v as Theme)}
            >
              <SelectTrigger id="settings-theme">
                <SelectValue placeholder={t('common.theme')} />
              </SelectTrigger>
              <SelectContent>
                {THEMES.map((value) => (
                  <SelectItem key={value} value={value}>
                    {value === 'light'
                      ? t('common.themeLight')
                      : value === 'dark'
                        ? t('common.themeDark')
                        : t('common.themeSystem')}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">{t('settings.preferences')}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid gap-2 max-w-sm">
            <Label htmlFor="settings-language">{t('common.language')}</Label>
            <Select
              value={language}
              onValueChange={(v: string) => setLanguage(v as 'en' | 'bn')}
            >
              <SelectTrigger id="settings-language">
                <SelectValue placeholder={t('common.language')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">{t('common.languageEn')}</SelectItem>
                <SelectItem value="bn">{t('common.languageBn')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
