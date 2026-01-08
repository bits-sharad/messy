export interface Project {
  id: string;
  name: string;
  description?: string;
  tenant_id: string;
  status: 'active' | 'inactive' | 'archived';
  metadata?: Record<string, unknown>;
  created_by: string;
  created_at: string;
  updated_at: string;
  job_count?: number;
}

export interface Job {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  job_code: string;
  status: 'draft' | 'published' | 'closed';
  department?: string;
  level?: 'entry' | 'mid' | 'senior' | 'lead';
  required_skills?: string[];
  responsibilities?: string[];
  metadata?: Record<string, unknown>;
  created_by: string;
  created_at: string;
  updated_at: string;
  match_count?: number;
}

export interface CandidateProfile {
  skills: string[];
  experience_summary?: string;
  education?: string;
  desired_role?: string;
  years_of_experience?: number;
  location?: string;
  metadata?: Record<string, unknown>;
}

export interface MatchResult {
  job_id: string;
  job_title: string;
  match_score: number;
  match_reasons: string[];
  missing_skills: string[];
  matched_skills: string[];
}

export interface SemanticSearchResult {
  job_id: string;
  score: number;
  title: string;
  department?: string;
  level?: string;
}

export interface JobDescriptionResponse {
  description: string;
  generated_by: 'llm' | 'template';
}

export interface ProjectCreateRequest {
  name: string;
  description?: string;
  tenant_id: string;
  status: 'active' | 'inactive' | 'archived';
  metadata?: Record<string, unknown>;
  created_by: string;
}

export interface JobCreateRequest {
  project_id: string;
  title: string;
  description?: string;
  job_code: string;
  status: 'draft' | 'published' | 'closed';
  department?: string;
  level?: 'entry' | 'mid' | 'senior' | 'lead';
  required_skills?: string[];
  responsibilities?: string[];
  metadata?: Record<string, unknown>;
  created_by: string;
}

export interface JobUpdateRequest {
  title?: string;
  description?: string;
  status?: 'draft' | 'published' | 'closed';
  department?: string;
  level?: 'entry' | 'mid' | 'senior' | 'lead';
  required_skills?: string[];
  responsibilities?: string[];
  metadata?: Record<string, unknown>;
}
