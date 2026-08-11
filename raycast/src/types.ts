export interface Stat {
  stat_key: string;
  value: number;
  label: string;
  public: boolean;
  source: string;
  updated_at: string;
  fun_fact_template?: string;
}

export interface VolunteerEntry {
  pk: string;
  sk: string;
  entity_type: string;
  date: string;
  minutes: number;
  organization?: string;
  group_name?: string;
  notes?: string;
  fmsc_meals?: number;
  created_at: string;
  updated_at: string;
}

export interface VolunteerSummary {
  total_minutes: number;
  total_hours: number;
  entry_count: number;
  total_fmsc_meals?: number;
}

export interface CtlWeek {
  pk: string;
  sk: string;
  entity_type: string;
  week_end_date: string;
  minutes: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CtlSummary {
  total_minutes: number;
  total_hours: number;
  week_count: number;
}

export interface Solve {
  pk: string;
  sk: string;
  entity_type: string;
  event: string;
  scramble: string;
  time_ms: number;
  penalty?: "+2" | "DNF";
  timestamp: string;
  source: string;
}

export interface SolveSummary {
  count_total: number;
  pr_single_ms: number | null;
  current_ao5_ms: number | null;
  current_ao12_ms: number | null;
}

export interface Preferences {
  apiUrl: string;
  apiKey: string;
}

export interface ApiKeyJson {
  username: string;
  user_pool_id: string;
  client_id: string;
  region: string;
  refresh_token: string;
}
