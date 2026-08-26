import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from '@/layouts/AppLayout';
import AboutPage from '@/pages/AboutPage';
import ActivitiesPage from '@/pages/ActivitiesPage';
import AnalyticsPage from '@/pages/AnalyticsPage';
import BusinessCanvasPage from '@/pages/BusinessCanvasPage';
import CompetitorsPage from '@/pages/CompetitorsPage';
import DashboardPage from '@/pages/DashboardPage';
import DocumentsPage from '@/pages/DocumentsPage';
import IdeasPage from '@/pages/IdeasPage';
import LeanCanvasPage from '@/pages/LeanCanvasPage';
import MilestonesPage from '@/pages/MilestonesPage';
import NotesPage from '@/pages/NotesPage';
import PersonasPage from '@/pages/PersonasPage';
import PlaceholderPage from '@/pages/PlaceholderPage';
import ProgressPage from '@/pages/ProgressPage';
import RoadmapPage from '@/pages/RoadmapPage';
import SettingsPage from '@/pages/SettingsPage';
import SwotPage from '@/pages/SwotPage';
import TasksPage from '@/pages/TasksPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'ideas', element: <IdeasPage /> },
      { path: 'lean-canvas', element: <LeanCanvasPage /> },
      { path: 'business-canvas', element: <BusinessCanvasPage /> },
      { path: 'swot', element: <SwotPage /> },
      { path: 'competitors', element: <CompetitorsPage /> },
      { path: 'personas', element: <PersonasPage /> },
      { path: 'roadmap', element: <RoadmapPage /> },
      { path: 'tasks', element: <TasksPage /> },
      { path: 'milestones', element: <MilestonesPage /> },
      { path: 'progress', element: <ProgressPage /> },
      { path: 'documents', element: <DocumentsPage /> },
      { path: 'notes', element: <NotesPage /> },
      { path: 'analytics', element: <AnalyticsPage /> },
      { path: 'activities', element: <ActivitiesPage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: 'about', element: <AboutPage /> },
      { path: '*', element: <PlaceholderPage titleKey="common.error" description="404" /> },
    ],
  },
]);