import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    // Add required headers for FastAPI backend
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'X-Principal-Subject': 'ui-user', // Default user for UI
      'X-Tenant-ID': 'default', // Default tenant
      'X-Roles': 'user',
      'X-Permissions': 'read,write'
    });
  }

  // Project endpoints
  getProjects(tenantId: string = 'default', skip: number = 0, limit: number = 100, status?: string): Observable<any[]> {
    let params = new HttpParams()
      .set('tenant_id', tenantId)
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    
    if (status) {
      params = params.set('status', status);
    }

    return this.http.get<any[]>(`${this.baseUrl}/projects`, {
      headers: this.getHeaders(),
      params
    });
  }

  getProject(projectId: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/projects/${projectId}`, {
      headers: this.getHeaders()
    });
  }

  createProject(project: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/projects`, project, {
      headers: this.getHeaders()
    });
  }

  updateProject(projectId: string, project: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/projects/${projectId}`, project, {
      headers: this.getHeaders()
    });
  }

  deleteProject(projectId: string): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/projects/${projectId}`, {
      headers: this.getHeaders()
    });
  }

  // Job endpoints
  getJobs(projectId?: string, skip: number = 0, limit: number = 100, status?: string): Observable<any[]> {
    if (projectId) {
      let params = new HttpParams()
        .set('skip', skip.toString())
        .set('limit', limit.toString());
      
      if (status) {
        params = params.set('status', status);
      }

      return this.http.get<any[]>(`${this.baseUrl}/projects/${projectId}/jobs`, {
        headers: this.getHeaders(),
        params
      });
    } else {
      // Search all jobs
      return this.searchJobs('', skip, limit);
    }
  }

  getJob(jobId: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/jobs/${jobId}`, {
      headers: this.getHeaders()
    });
  }

  createJob(projectId: string, job: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/projects/${projectId}/jobs`, job, {
      headers: this.getHeaders()
    });
  }

  updateJob(jobId: string, job: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/jobs/${jobId}`, job, {
      headers: this.getHeaders()
    });
  }

  deleteJob(jobId: string): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/jobs/${jobId}`, {
      headers: this.getHeaders()
    });
  }

  searchJobs(query: string, skip: number = 0, limit: number = 100, projectId?: string): Observable<any[]> {
    let params = new HttpParams()
      .set('q', query || '')
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    
    if (projectId) {
      params = params.set('project_id', projectId);
    }

    return this.http.get<any[]>(`${this.baseUrl}/jobs/search`, {
      headers: this.getHeaders(),
      params
    });
  }
}

