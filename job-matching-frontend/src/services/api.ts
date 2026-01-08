import type {
  Project,
  Job,
  CandidateProfile,
  MatchResult,
  SemanticSearchResult,
  JobDescriptionResponse,
  ProjectCreateRequest,
  JobCreateRequest,
  JobUpdateRequest,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const DEFAULT_TENANT_ID = 'default_tenant';
const DEFAULT_USER_ID = 'default_user';

const getHeaders = () => ({
  'Content-Type': 'application/json',
  'X-Principal-Subject': DEFAULT_USER_ID,
  'X-Tenant-ID': DEFAULT_TENANT_ID,
  'X-Roles': 'admin',
  'X-Permissions': 'read,write,delete',
});

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }
  if (response.status === 204) {
    return {} as T;
  }
  return response.json();
}

export const projectsApi = {
  list: async (tenantId: string = DEFAULT_TENANT_ID, skip = 0, limit = 100): Promise<Project[]> => {
    const params = new URLSearchParams({
      tenant_id: tenantId,
      skip: skip.toString(),
      limit: limit.toString(),
    });
    const response = await fetch(`${API_BASE_URL}/api/v1/projects?${params}`, {
      headers: getHeaders(),
    });
    return handleResponse<Project[]>(response);
  },

  get: async (projectId: string): Promise<Project> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}`, {
      headers: getHeaders(),
    });
    return handleResponse<Project>(response);
  },

  create: async (data: Omit<ProjectCreateRequest, 'tenant_id' | 'created_by'>): Promise<Project> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/projects`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        ...data,
        tenant_id: DEFAULT_TENANT_ID,
        created_by: DEFAULT_USER_ID,
      }),
    });
    return handleResponse<Project>(response);
  },

  update: async (projectId: string, data: Partial<ProjectCreateRequest>): Promise<Project> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<Project>(response);
  },

  delete: async (projectId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return handleResponse<void>(response);
  },
};

export const jobsApi = {
  list: async (projectId?: string, skip = 0, limit = 100): Promise<Job[]> => {
    if (projectId) {
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString(),
      });
      const response = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/jobs?${params}`, {
        headers: getHeaders(),
      });
      return handleResponse<Job[]>(response);
    }
    const response = await fetch(`${API_BASE_URL}/jobs?skip=${skip}&limit=${limit}`, {
      headers: getHeaders(),
    });
    return handleResponse<Job[]>(response);
  },

  get: async (jobId: string): Promise<Job> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/jobs/${jobId}`, {
      headers: getHeaders(),
    });
    return handleResponse<Job>(response);
  },

  create: async (projectId: string, data: Omit<JobCreateRequest, 'project_id' | 'created_by'>): Promise<Job> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/jobs`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        ...data,
        project_id: projectId,
        created_by: DEFAULT_USER_ID,
      }),
    });
    return handleResponse<Job>(response);
  },

  update: async (jobId: string, data: JobUpdateRequest): Promise<Job> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/jobs/${jobId}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<Job>(response);
  },

  delete: async (jobId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/jobs/${jobId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return handleResponse<void>(response);
  },

  search: async (query: string, projectId?: string): Promise<Job[]> => {
    const params = new URLSearchParams({ q: query });
    if (projectId) {
      params.append('project_id', projectId);
    }
    const response = await fetch(`${API_BASE_URL}/api/v1/jobs/search?${params}`, {
      headers: getHeaders(),
    });
    return handleResponse<Job[]>(response);
  },
};

export const aiApi = {
  matchCandidate: async (
    candidate: CandidateProfile,
    jobIds?: string[],
    limit = 10,
    useMercer?: boolean
  ): Promise<MatchResult[]> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (jobIds && jobIds.length > 0) {
      jobIds.forEach((id) => params.append('job_ids', id));
    }
    if (useMercer !== undefined) {
      params.append('use_mercer', useMercer.toString());
    }
    const response = await fetch(`${API_BASE_URL}/api/v1/ai/jobs/match-candidate?${params}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(candidate),
    });
    return handleResponse<MatchResult[]>(response);
  },

  generateJobDescription: async (
    title: string,
    department?: string,
    level?: string,
    requiredSkills?: string[],
    responsibilities?: string[],
    useLlm = true
  ): Promise<JobDescriptionResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai/jobs/generate-description`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        title,
        department,
        level,
        required_skills: requiredSkills,
        responsibilities,
        use_llm: useLlm,
      }),
    });
    return handleResponse<JobDescriptionResponse>(response);
  },

  semanticSearch: async (
    query: string,
    limit = 10,
    filters?: Record<string, unknown>
  ): Promise<SemanticSearchResult[]> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai/jobs/search-semantic`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        query,
        limit,
        filters,
      }),
    });
    return handleResponse<SemanticSearchResult[]>(response);
  },

  askJobQuestion: async (jobId: string, question: string): Promise<{ answer: string; job_id: string }> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai/jobs/${jobId}/ask`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        job_id: jobId,
        question,
      }),
    });
    return handleResponse<{ answer: string; job_id: string }>(response);
  },

  indexJob: async (jobId: string): Promise<{ message: string; job_id: string }> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai/jobs/${jobId}/index`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse<{ message: string; job_id: string }>(response);
  },
};
