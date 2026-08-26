import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGUAGES, type Language } from '@/i18n';

export { SUPPORTED_LANGUAGES };

export const LANGUAGE_LABELS: Record<Language, { label: string; nativeLabel: string }> = {
  en: { label: 'English', nativeLabel: 'English' },
  bn: { label: 'Bangla', nativeLabel: 'বাংলা' },
};

export function useLanguage() {
  const { i18n } = useTranslation();
  const language = (i18n.language ?? 'en').startsWith('bn') ? 'bn' : 'en';
  const setLanguage = useCallback((lang: Language) => {
    void i18n.changeLanguage(lang);
  }, [i18n]);
  return { language, setLanguage };
}
