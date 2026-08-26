import { apiRequest } from '@/lib/api';
import type {
  Activity,
  BusinessCanvas,
  BusinessCanvasUpdate,
  Competitor,
  CompetitorCreate,
  CompetitorUpdate,
  Document,
  DocumentCreate,
  DocumentUpdate,
  Idea,
  IdeaCreate,
  IdeaUpdate,
  LeanCanvas,
  LeanCanvasUpdate,
  Milestone,
  MilestoneCreate,
  MilestoneUpdate,
  Note,
  NoteCreate,
  NoteUpdate,
  Paginated,
  Persona,
  PersonaCreate,
  PersonaUpdate,
  ProgressTracker,
  ProgressTrackerUpsert,
  Roadmap,
  RoadmapStage,
  RoadmapStageCreate,
  RoadmapStageUpdate,
  StartupProject,
  StartupProjectCreate,
  Swot,
  SwotUpdate,
  Task,
  TaskCreate,
  TaskUpdate,
  User,
  DashboardSummary,
} from '@/types/api';

export type {
  Activity,
  BusinessCanvas,
  BusinessCanvasUpdate,
  Competitor,
  CompetitorCreate,
  CompetitorUpdate,
  Document,
  DocumentCreate,
  DocumentUpdate,
  Idea,
  IdeaCreate,
  IdeaUpdate,
  LeanCanvas,
  LeanCanvasUpdate,
  Milestone,
  MilestoneCreate,
  MilestoneUpdate,
  Note,
  NoteCreate,
  NoteUpdate,
  Paginated,
  Persona,
  PersonaCreate,
  PersonaUpdate,
  ProgressTracker,
  ProgressTrackerUpsert,
  Roadmap,
  RoadmapStage,
  RoadmapStageCreate,
  RoadmapStageUpdate,
  StartupProject,
  StartupProjectCreate,
  Swot,
  SwotUpdate,
  Task,
  TaskCreate,
  TaskUpdate,
  User,
  DashboardSummary,
};

export {
  IDEA_STATUSES,
  TASK_STATUSES,
  TASK_PRIORITIES,
  DOCUMENT_KINDS,
  type IdeaStatus,
  type TaskStatus,
  type TaskPriority,
  type DocumentKind,
} from '@/types/api';

/** ------------------------------------------------------------------ */
/** Idea helpers                                                       */
/** ------------------------------------------------------------------ */
export const ideasApi = {
  list: (query: Record<string, string | number | boolean | undefined | null> = {}) =>
    apiRequest<Paginated<Idea>>('/ideas', { query }),
  get: (id: string) => apiRequest<Idea>(`/ideas/${id}`),
  create: (payload: IdeaCreate) =>
    apiRequest<Idea>('/ideas', { method: 'POST', body: payload }),
  update: (id: string, payload: IdeaUpdate) =>
    apiRequest<Idea>(`/ideas/${id}`, { method: 'PATCH', body: payload }),
  archive: (id: string) =>
    apiRequest<Idea>(`/ideas/${id}`, { method: 'DELETE' }),
  delete: (id: string) =>
    apiRequest<void>(`/ideas/${id}`, { method: 'DELETE' }),
  restore: (id: string) =>
    apiRequest<Idea>(`/ideas/${id}/restore`, { method: 'POST' }),
};

/** ------------------------------------------------------------------ */
/** Project helpers                                                    */
/** ------------------------------------------------------------------ */
export const projectsApi = {
  list: () => apiRequest<Paginated<StartupProject>>('/projects'),
  get: (id: string) => apiRequest<StartupProject>(`/projects/${id}`),
  create: (payload: StartupProjectCreate) =>
    apiRequest<StartupProject>('/projects', { method: 'POST', body: payload }),
  update: (id: string, payload: Partial<StartupProjectCreate>) =>
    apiRequest<StartupProject>(`/projects/${id}`, { method: 'PATCH', body: payload }),
  delete: (id: string) => apiRequest<void>(`/projects/${id}`, { method: 'DELETE' }),
};

/** ------------------------------------------------------------------ */
/** User helpers                                                       */
/** ------------------------------------------------------------------ */
export const usersApi = {
  list: () => apiRequest<Paginated<User>>('/users'),
  get: (id: string) => apiRequest<User>(`/users/${id}`),
  create: (payload: { email: string; display_name?: string | null; locale?: string; theme?: string }) =>
    apiRequest<User>('/users', { method: 'POST', body: payload }),
  update: (id: string, payload: Partial<{ display_name: string | null; locale: string; theme: string; is_active: boolean }>) =>
    apiRequest<User>(`/users/${id}`, { method: 'PATCH', body: payload }),
};

/** ------------------------------------------------------------------ */
/** Canvas helpers (1:1 with idea)                                      */
/** ------------------------------------------------------------------ */
export const leanCanvasApi = {
  get: (ideaId: string) => apiRequest<LeanCanvas | null>(`/ideas/${ideaId}/lean-canvas`),
  upsert: (ideaId: string, payload: LeanCanvasUpdate) =>
    apiRequest<LeanCanvas>(`/ideas/${ideaId}/lean-canvas`, { method: 'PUT', body: payload }),
  delete: (ideaId: string) =>
    apiRequest<void>(`/ideas/${ideaId}/lean-canvas`, { method: 'DELETE' }),
};

export const businessCanvasApi = {
  get: (ideaId: string) =>
    apiRequest<BusinessCanvas | null>(`/ideas/${ideaId}/business-canvas`),
  upsert: (ideaId: string, payload: BusinessCanvasUpdate) =>
    apiRequest<BusinessCanvas>(`/ideas/${ideaId}/business-canvas`, { method: 'PUT', body: payload }),
  delete: (ideaId: string) =>
    apiRequest<void>(`/ideas/${ideaId}/business-canvas`, { method: 'DELETE' }),
};

export const swotApi = {
  get: (ideaId: string) => apiRequest<Swot | null>(`/ideas/${ideaId}/swot`),
  upsert: (ideaId: string, payload: SwotUpdate) =>
    apiRequest<Swot>(`/ideas/${ideaId}/swot`, { method: 'PUT', body: payload }),
  delete: (ideaId: string) =>
    apiRequest<void>(`/ideas/${ideaId}/swot`, { method: 'DELETE' }),
};

export const progressApi = {
  get: (ideaId: string) =>
    apiRequest<ProgressTracker | null>(`/ideas/${ideaId}/progress`),
  upsert: (ideaId: string, payload: ProgressTrackerUpsert) =>
    apiRequest<ProgressTracker>(`/ideas/${ideaId}/progress`, { method: 'PUT', body: payload }),
  delete: (ideaId: string) =>
    apiRequest<void>(`/ideas/${ideaId}/progress`, { method: 'DELETE' }),
};

/** ------------------------------------------------------------------ */
/** Resource collections (1:N under idea)                              */
/** ------------------------------------------------------------------ */
export const competitorsApi = {
  list: (ideaId: string, q: Record<string, string | number | undefined> = {}) =>
    apiRequest<Paginated<Competitor>>(`/ideas/${ideaId}/competitors`, { query: q }),
  create: (ideaId: string, payload: Omit<CompetitorCreate, 'idea_id'>) =>
    apiRequest<Competitor>(`/ideas/${ideaId}/competitors`, { method: 'POST', body: payload }),
  get: (ideaId: string, id: string) =>
    apiRequest<Competitor>(`/ideas/${ideaId}/competitors/${id}`),
  update: (ideaId: string, id: string, payload: CompetitorUpdate) =>
    apiRequest<Competitor>(`/ideas/${ideaId}/competitors/${id}`, { method: 'PATCH', body: payload }),
  delete: (ideaId: string, id: string) =>
    apiRequest<void>(`/ideas/${ideaId}/competitors/${id}`, { method: 'DELETE' }),
};

export const personasApi = {
  list: (ideaId: string, q: Record<string, string | number | undefined> = {}) =>
    apiRequest<Paginated<Persona>>(`/ideas/${ideaId}/personas`, { query: q }),
  create: (ideaId: string, payload: Omit<PersonaCreate, 'idea_id'>) =>
    apiRequest<Persona>(`/ideas/${ideaId}/personas`, { method: 'POST', body: payload }),
  get: (ideaId: string, id: string) =>
    apiRequest<Persona>(`/ideas/${ideaId}/personas/${id}`),
  update: (ideaId: string, id: string, payload: PersonaUpdate) =>
    apiRequest<Persona>(`/ideas/${ideaId}/personas/${id}`, { method: 'PATCH', body: payload }),
  delete: (ideaId: string, id: string) =>
    apiRequest<void>(`/ideas/${ideaId}/personas/${id}`, { method: 'DELETE' }),
};

export const tasksApi = {
  list: (ideaId: string, q: Record<string, string | number | undefined> = {}) =>
    apiRequest<Paginated<Task>>(`/ideas/${ideaId}/tasks`, { query: q }),
  create: (ideaId: string, payload: Omit<TaskCreate, 'idea_id'>) =>
    apiRequest<Task>(`/ideas/${ideaId}/tasks`, { method: 'POST', body: payload }),
  get: (ideaId: string, id: string) =>
    apiRequest<Task>(`/ideas/${ideaId}/tasks/${id}`),
  update: (ideaId: string, id: string, payload: TaskUpdate) =>
    apiRequest<Task>(`/ideas/${ideaId}/tasks/${id}`, { method: 'PATCH', body: payload }),
  delete: (ideaId: string, id: string) =>
    apiRequest<void>(`/ideas/${ideaId}/tasks/${id}`, { method: 'DELETE' }),
};

export const milestonesApi = {
  list: (ideaId: string, q: Record<string, string | number | undefined> = {}) =>
    apiRequest<Paginated<Milestone>>(`/ideas/${ideaId}/milestones`, { query: q }),
  create: (ideaId: string, payload: Omit<MilestoneCreate, 'idea_id'>) =>
    apiRequest<Milestone>(`/ideas/${ideaId}/milestones`, { method: 'POST', body: payload }),
  get: (ideaId: string, id: string) =>
    apiRequest<Milestone>(`/ideas/${ideaId}/milestones/${id}`),
  update: (ideaId: string, id: string, payload: MilestoneUpdate) =>
    apiRequest<Milestone>(`/ideas/${ideaId}/milestones/${id}`, { method: 'PATCH', body: payload }),
  delete: (ideaId: string, id: string) =>
    apiRequest<void>(`/ideas/${ideaId}/milestones/${id}`, { method: 'DELETE' }),
};

export const documentsApi = {
  list: (ideaId: string, q: Record<string, string | number | undefined> = {}) =>
    apiRequest<Paginated<Document>>(`/ideas/${ideaId}/documents`, { query: q }),
  create: (ideaId: string, payload: Omit<DocumentCreate, 'idea_id'>) =>
    apiRequest<Document>(`/ideas/${ideaId}/documents`, { method: 'POST', body: payload }),
  get: (ideaId: string, id: string) =>
    apiRequest<Document>(`/ideas/${ideaId}/documents/${id}`),
  update: (ideaId: string, id: string, payload: DocumentUpdate) =>
    apiRequest<Document>(`/ideas/${ideaId}/documents/${id}`, { method: 'PATCH', body: payload }),
  delete: (ideaId: string, id: string) =>
    apiRequest<void>(`/ideas/${ideaId}/documents/${id}`, { method: 'DELETE' }),
};

export const notesApi = {
  list: (ideaId: string, q: Record<string, string | number | undefined> = {}) =>
    apiRequest<Paginated<Note>>(`/ideas/${ideaId}/notes`, { query: q }),
  create: (ideaId: string, payload: Omit<NoteCreate, 'idea_id'>) =>
    apiRequest<Note>(`/ideas/${ideaId}/notes`, { method: 'POST', body: payload }),
  get: (ideaId: string, id: string) =>
    apiRequest<Note>(`/ideas/${ideaId}/notes/${id}`),
  update: (ideaId: string, id: string, payload: NoteUpdate) =>
    apiRequest<Note>(`/ideas/${ideaId}/notes/${id}`, { method: 'PATCH', body: payload }),
  delete: (ideaId: string, id: string) =>
    apiRequest<void>(`/ideas/${ideaId}/notes/${id}`, { method: 'DELETE' }),
};

export const roadmapApi = {
  get: (ideaId: string) =>
    apiRequest<Roadmap | null>(`/ideas/${ideaId}/roadmap`),
  upsert: (ideaId: string, payload: { title: string; summary?: string | null; target_completion?: string | null }) =>
    apiRequest<Roadmap>(`/ideas/${ideaId}/roadmap`, { method: 'PUT', body: payload }),
  patch: (ideaId: string, payload: Partial<{ title: string; summary: string | null; target_completion: string | null; completion: number }>) =>
    apiRequest<Roadmap>(`/ideas/${ideaId}/roadmap`, { method: 'PATCH', body: payload }),
  delete: (ideaId: string) =>
    apiRequest<void>(`/ideas/${ideaId}/roadmap`, { method: 'DELETE' }),
};

export const roadmapStagesApi = {
  list: (ideaId: string, q: Record<string, string | number | undefined> = {}) =>
    apiRequest<Paginated<RoadmapStage>>(`/ideas/${ideaId}/roadmap/stages`, { query: q }),
  create: (ideaId: string, payload: RoadmapStageCreate) =>
    apiRequest<RoadmapStage>(`/ideas/${ideaId}/roadmap/stages`, { method: 'POST', body: payload }),
  get: (ideaId: string, id: string) =>
    apiRequest<RoadmapStage>(`/ideas/${ideaId}/roadmap/stages/${id}`),
  update: (ideaId: string, id: string, payload: RoadmapStageUpdate) =>
    apiRequest<RoadmapStage>(`/ideas/${ideaId}/roadmap/stages/${id}`, { method: 'PATCH', body: payload }),
  delete: (ideaId: string, id: string) =>
    apiRequest<void>(`/ideas/${ideaId}/roadmap/stages/${id}`, { method: 'DELETE' }),
};

export const activitiesApi = {
  list: (ideaId: string, q: Record<string, string | number | undefined> = {}) =>
    apiRequest<Paginated<Activity>>(`/ideas/${ideaId}/activities`, { query: q }),
  get: (ideaId: string, id: string) =>
    apiRequest<Activity>(`/ideas/${ideaId}/activities/${id}`),
};

export const dashboardApi = {
  summary: (ideaId: string) =>
    apiRequest<DashboardSummary>('/dashboard/summary', { query: { idea_id: ideaId } }),
};

export const aiApi = {
  validate: (payload: { idea_id?: string | null; title: string; problem?: string | null; solution?: string | null; audience?: string | null; category?: string | null }) =>
    apiRequest<unknown>('/ai/validate', { method: 'POST', body: payload }),
  swot: (payload: { title: string; problem?: string | null; solution?: string | null; audience?: string | null; category?: string | null }) =>
    apiRequest<unknown>('/ai/swot-suggestions', { method: 'POST', body: payload }),
  risks: (payload: { title: string; problem?: string | null; solution?: string | null; audience?: string | null; category?: string | null }) =>
    apiRequest<unknown>('/ai/risk-suggestions', { method: 'POST', body: payload }),
  competitors: (payload: { title: string; problem?: string | null; solution?: string | null; audience?: string | null; category?: string | null; market?: string | null }) =>
    apiRequest<unknown>('/ai/competitors', { method: 'POST', body: payload }),
  roadmap: (payload: { title: string; problem?: string | null; solution?: string | null; audience?: string | null; category?: string | null }) =>
    apiRequest<unknown>('/ai/growth-roadmap', { method: 'POST', body: payload }),
};