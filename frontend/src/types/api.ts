/** Shared TypeScript types that mirror the Pydantic schemas 1:1. */
export type UUID = string;
export type ISODateString = string;

export interface Paginated<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export const IDEA_STATUSES = [
  'draft',
  'validating',
  'planned',
  'in_progress',
  'on_hold',
  'completed',
  'archived',
] as const;
export type IdeaStatus = (typeof IDEA_STATUSES)[number];

export interface Idea {
  id: UUID;
  project_id: UUID;
  title: string;
  problem: string | null;
  solution: string | null;
  audience: string | null;
  category: string | null;
  tags: string[];
  status: IdeaStatus;
  priority: number;
  score: number;
  is_archived: boolean;
  archived_at: ISODateString | null;
  created_at: ISODateString;
  updated_at: ISODateString;
}

export interface IdeaCreate {
  project_id: UUID;
  title: string;
  problem?: string | null;
  solution?: string | null;
  audience?: string | null;
  category?: string | null;
  tags?: string[];
  status?: IdeaStatus;
  priority?: number;
  score?: number;
  is_archived?: boolean;
}

export type IdeaUpdate = Partial<Omit<IdeaCreate, 'project_id'>>;

export interface StartupProject {
  id: UUID;
  owner_id: UUID;
  name: string;
  description: string | null;
  stage: string;
  status: string;
  tags: string[];
  metadata_json: Record<string, unknown>;
  created_at: ISODateString;
  updated_at: ISODateString;
}

export interface StartupProjectCreate {
  owner_id: UUID;
  name: string;
  description?: string | null;
  stage?: string;
  status?: string;
  tags?: string[];
  metadata_json?: Record<string, unknown>;
}

export interface User {
  id: UUID;
  email: string;
  display_name: string | null;
  locale: string;
  theme: string;
  is_active: boolean;
  created_at: ISODateString;
  updated_at: ISODateString;
}

export interface LeanCanvas {
  id: UUID;
  idea_id: UUID;
  problem: string | null;
  solution: string | null;
  key_metrics: string | null;
  unique_value_prop: string | null;
  unfair_advantage: string | null;
  channels: string | null;
  customer_segments: string | null;
  cost_structure: string | null;
  revenue_streams: string | null;
  created_at: ISODateString;
  updated_at: ISODateString;
}
export type LeanCanvasUpdate = Partial<Omit<LeanCanvas, 'id' | 'idea_id' | 'created_at' | 'updated_at'>>;

export interface BusinessCanvas extends Omit<LeanCanvas, 'key_metrics' | 'unique_value_prop' | 'unfair_advantage'> {
  id: UUID;
  idea_id: UUID;
  key_partners: string | null;
  key_activities: string | null;
  key_resources: string | null;
  value_propositions: string | null;
  customer_relationships: string | null;
  created_at: ISODateString;
  updated_at: ISODateString;
}
export type BusinessCanvasUpdate = Partial<
  Omit<BusinessCanvas, 'id' | 'idea_id' | 'created_at' | 'updated_at'>
>;

export interface Swot {
  id: UUID;
  idea_id: UUID;
  strengths: string | null;
  weaknesses: string | null;
  opportunities: string | null;
  threats: string | null;
  score: number;
  summary: string | null;
  created_at: ISODateString;
  updated_at: ISODateString;
}
export type SwotUpdate = Partial<Omit<Swot, 'id' | 'idea_id' | 'created_at' | 'updated_at'>>;

export interface ProgressTracker {
  id: UUID;
  idea_id: UUID;
  overall_completion: number;
  health_score: number;
  milestone_progress: number;
  task_completion: number;
  last_computed_at: ISODateString;
}
export interface ProgressTrackerUpsert {
  overall_completion: number;
  health_score: number;
  milestone_progress: number;
  task_completion: number;
}

export interface Competitor {
  id: UUID;
  idea_id: UUID;
  name: string;
  website_url: string | null;
  pricing: number | null;
  pricing_currency: string;
  strengths: string | null;
  weaknesses: string | null;
  features: Array<Record<string, unknown>>;
  market_position: string | null;
  notes: string | null;
  created_at: ISODateString;
  updated_at: ISODateString;
}
export type CompetitorCreate = Omit<Competitor, 'id' | 'idea_id' | 'created_at' | 'updated_at'>;
export type CompetitorUpdate = Partial<CompetitorCreate>;

export interface Persona {
  id: UUID;
  idea_id: UUID;
  name: string;
  age: number | null;
  occupation: string | null;
  goals: string | null;
  pain_points: string | null;
  needs: string | null;
  behaviour: string | null;
  avatar_url: string | null;
  created_at: ISODateString;
  updated_at: ISODateString;
}
export type PersonaCreate = Omit<Persona, 'id' | 'idea_id' | 'created_at' | 'updated_at'>;
export type PersonaUpdate = Partial<PersonaCreate>;

export const TASK_STATUSES = ['todo', 'in_progress', 'blocked', 'done'] as const;
export type TaskStatus = (typeof TASK_STATUSES)[number];
export const TASK_PRIORITIES = ['low', 'medium', 'high', 'critical'] as const;
export type TaskPriority = (typeof TASK_PRIORITIES)[number];

export interface Task {
  id: UUID;
  idea_id: UUID;
  title: string;
  description: string | null;
  priority: TaskPriority;
  status: TaskStatus;
  progress: number;
  due_date: string | null;
  started_at: ISODateString | null;
  completed_at: ISODateString | null;
  created_at: ISODateString;
  updated_at: ISODateString;
}
export type TaskCreate = Omit<Task, 'id' | 'idea_id' | 'created_at' | 'updated_at'>;
export type TaskUpdate = Partial<TaskCreate>;

export interface Milestone {
  id: UUID;
  idea_id: UUID;
  title: string;
  description: string | null;
  target_date: string | null;
  completed_at: ISODateString | null;
  completion: number;
  created_at: ISODateString;
  updated_at: ISODateString;
}
export type MilestoneCreate = Omit<Milestone, 'id' | 'idea_id' | 'created_at' | 'updated_at'>;
export type MilestoneUpdate = Partial<MilestoneCreate>;

export const DOCUMENT_KINDS = ['attachment', 'pitch', 'spec', 'contract', 'note'] as const;
export type DocumentKind = (typeof DOCUMENT_KINDS)[number];

export interface Document {
  id: UUID;
  idea_id: UUID;
  kind: DocumentKind;
  title: string;
  file_path: string | null;
  mime_type: string | null;
  size_bytes: number | null;
  notes: string | null;
  created_at: ISODateString;
  updated_at: ISODateString;
}
export type DocumentCreate = Omit<Document, 'id' | 'idea_id' | 'created_at' | 'updated_at'>;
export type DocumentUpdate = Partial<DocumentCreate>;

export interface Note {
  id: UUID;
  idea_id: UUID;
  body: string;
  pinned: boolean;
  created_at: ISODateString;
  updated_at: ISODateString;
}
export type NoteCreate = Omit<Note, 'id' | 'idea_id' | 'created_at' | 'updated_at'>;
export type NoteUpdate = Partial<NoteCreate>;

export interface Roadmap {
  id: UUID;
  idea_id: UUID;
  title: string;
  summary: string | null;
  target_completion: string | null;
  completion: number;
  created_at: ISODateString;
  updated_at: ISODateString;
}
export interface RoadmapStage {
  id: UUID;
  roadmap_id: UUID;
  title: string;
  description: string | null;
  target_date: string | null;
  completion: number;
  position: number;
  completed_at: ISODateString | null;
  created_at: ISODateString;
  updated_at: ISODateString;
}
export interface RoadmapStageCreate {
  title: string;
  description?: string | null;
  target_date?: string | null;
  completion?: number;
  position?: number;
}
export type RoadmapStageUpdate = Partial<RoadmapStageCreate>;

export interface Activity {
  id: UUID;
  idea_id: UUID;
  actor_id: UUID | null;
  event_type: string;
  event_data: Record<string, unknown>;
  created_at: ISODateString;
}

export interface DashboardSummary {
  idea_id: UUID;
  task_counts: {
    todo: number;
    in_progress: number;
    blocked: number;
    done: number;
    total: number;
  };
  resource_counts: {
    competitors: number;
    personas: number;
    tasks: number;
    milestones: number;
    documents: number;
    notes: number;
    activities: number;
  };
  milestone_completion_avg: number;
  roadmap_id: UUID | null;
  roadmap_completion: number | null;
  roadmap_stage_count: number;
  generated_at: ISODateString;
}