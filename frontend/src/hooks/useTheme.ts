import {
  useTheme as useThemeContext,
  type Theme,
} from '@/theme/ThemeProvider';

export type { Theme };
export const THEMES: Theme[] = ['light', 'dark', 'system'];

export function useTheme() {
  return useThemeContext();
}
