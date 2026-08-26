import {
  Languages,
  Moon,
  Sun,
  MonitorSmartphone,
  LayoutDashboard,
  Lightbulb,
  ClipboardList,
  BarChart3,
  Scale,
  Swords,
  Users,
  Map,
  CheckSquare,
  Flag,
  TrendingUp,
  FileText,
  StickyNote,
  PieChart,
  Activity,
  Settings as SettingsIcon,
  Info,
  type LucideIcon,
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { NavLink, Outlet } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { SUPPORTED_LANGUAGES } from '@/i18n';
import { useTheme, type Theme } from '@/theme/ThemeProvider';
import { cn } from '@/utils/cn';

const NAV: Array<{ to: string; key: string; icon: LucideIcon }> = [
  { to: '/', key: 'dashboard', icon: LayoutDashboard },
  { to: '/ideas', key: 'ideas', icon: Lightbulb },
  { to: '/lean-canvas', key: 'leanCanvas', icon: ClipboardList },
  { to: '/business-canvas', key: 'businessCanvas', icon: BarChart3 },
  { to: '/swot', key: 'swot', icon: Scale },
  { to: '/competitors', key: 'competitors', icon: Swords },
  { to: '/personas', key: 'personas', icon: Users },
  { to: '/roadmap', key: 'roadmap', icon: Map },
  { to: '/tasks', key: 'tasks', icon: CheckSquare },
  { to: '/milestones', key: 'milestones', icon: Flag },
  { to: '/progress', key: 'progress', icon: TrendingUp },
  { to: '/documents', key: 'documents', icon: FileText },
  { to: '/notes', key: 'notes', icon: StickyNote },
  { to: '/analytics', key: 'analytics', icon: PieChart },
  { to: '/activities', key: 'activities', icon: Activity },
  { to: '/settings', key: 'settings', icon: SettingsIcon },
  { to: '/about', key: 'about', icon: Info },
];

const THEME_OPTIONS: Array<{ value: Theme; icon: LucideIcon; labelKey: string }> = [
  { value: 'light', icon: Sun, labelKey: 'common.themeLight' },
  { value: 'dark', icon: Moon, labelKey: 'common.themeDark' },
  { value: 'system', icon: MonitorSmartphone, labelKey: 'common.themeSystem' },
];

export function AppLayout() {
  const { t, i18n } = useTranslation();
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      <aside className="hidden w-64 shrink-0 border-r bg-card md:flex md:flex-col">
        <div className="border-b p-4">
          <p className="text-lg font-semibold leading-tight">{t('app.name')}</p>
          <p className="text-xs text-muted-foreground">{t('app.tagline')}</p>
        </div>
        <nav className="flex-1 overflow-y-auto p-2" aria-label="Primary">
          {NAV.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-accent hover:text-accent-foreground',
                  )
                }
              >
                <Icon className="h-4 w-4" aria-hidden />
                <span>{t(`nav.${item.key}`)}</span>
              </NavLink>
            );
          })}
        </nav>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between gap-2 border-b bg-card/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-card/75">
          <h1 className="text-sm font-medium text-muted-foreground md:hidden">{t('app.name')}</h1>
          <div className="ml-auto flex items-center gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" aria-label={t('common.language')}>
                  <Languages className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>{t('common.language')}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {SUPPORTED_LANGUAGES.map((lng) => (
                  <DropdownMenuItem
                    key={lng}
                    onSelect={() => void i18n.changeLanguage(lng)}
                    data-active={i18n.language === lng}
                  >
                    {t(`common.language${lng === 'en' ? 'En' : 'Bn'}`)}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" aria-label={t('common.theme')}>
                  {theme === 'dark' ? (
                    <Moon className="h-4 w-4" />
                  ) : theme === 'light' ? (
                    <Sun className="h-4 w-4" />
                  ) : (
                    <MonitorSmartphone className="h-4 w-4" />
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>{t('common.theme')}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {THEME_OPTIONS.map(({ value, icon: Icon, labelKey }) => (
                  <DropdownMenuItem
                    key={value}
                    onSelect={() => setTheme(value)}
                    data-active={theme === value}
                  >
                    <Icon className="mr-2 h-4 w-4" />
                    {t(labelKey)}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}