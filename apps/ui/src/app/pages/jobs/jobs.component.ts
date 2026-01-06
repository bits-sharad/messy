import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-jobs',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="jobs-container">
      <h2>Jobs</h2>
      <div class="api-info">
        <small>Connected to: {{ apiUrl }}</small>
      </div>
      <div *ngIf="loading">Loading...</div>
      <div *ngIf="error" class="error">{{ error }}</div>
      <div *ngIf="jobs && jobs.length > 0" class="jobs-list">
        <div *ngFor="let job of jobs" class="job-card">
          <h3>{{ job.title }}</h3>
          <p class="job-code">Code: {{ job.job_code }}</p>
          <p>{{ job.description }}</p>
          <div class="job-meta">
            <span>Status: {{ job.status }}</span>
            <span *ngIf="job.level">Level: {{ job.level }}</span>
            <span *ngIf="job.department">Department: {{ job.department }}</span>
          </div>
          <div *ngIf="job.required_skills && job.required_skills.length > 0" class="skills">
            <strong>Skills:</strong>
            <span *ngFor="let skill of job.required_skills" class="skill-tag">{{ skill }}</span>
          </div>
        </div>
      </div>
      <div *ngIf="jobs && jobs.length === 0 && !loading" class="empty-state">
        No jobs found
      </div>
    </div>
  `,
  styles: [`
    .jobs-container {
      max-width: 800px;
    }
    .jobs-list {
      display: grid;
      gap: 1rem;
      margin-top: 1rem;
    }
    .job-card {
      background: white;
      padding: 1.5rem;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .job-card h3 {
      margin-top: 0;
      color: #1976d2;
    }
    .job-code {
      font-family: monospace;
      color: #666;
      font-size: 0.9rem;
    }
    .job-meta {
      display: flex;
      gap: 1rem;
      margin-top: 1rem;
      font-size: 0.9rem;
      color: #666;
    }
    .skills {
      margin-top: 1rem;
      padding-top: 1rem;
      border-top: 1px solid #eee;
    }
    .skill-tag {
      display: inline-block;
      background: #e3f2fd;
      color: #1976d2;
      padding: 0.25rem 0.75rem;
      border-radius: 12px;
      margin: 0.25rem;
      font-size: 0.85rem;
    }
    .error {
      color: #d32f2f;
      padding: 1rem;
      background: #ffebee;
      border-radius: 4px;
      margin-top: 1rem;
    }
    .empty-state {
      text-align: center;
      padding: 2rem;
      color: #666;
    }
    .api-info {
      margin-bottom: 1rem;
      padding: 0.5rem;
      background: #e3f2fd;
      border-radius: 4px;
    }
    .api-info small {
      color: #1976d2;
      font-family: monospace;
    }
  `]
})
export class JobsComponent implements OnInit {
  jobs: any[] = [];
  loading = false;
  error: string | null = null;
  apiUrl = environment.apiUrl;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadJobs();
  }

  loadJobs() {
    this.loading = true;
    this.error = null;
    // Search all jobs (empty query returns all)
    this.apiService.searchJobs('').subscribe({
      next: (data) => {
        this.jobs = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = `Failed to load jobs. Make sure the API is running at ${this.apiUrl}`;
        this.loading = false;
        console.error('Error loading jobs:', err);
      }
    });
  }
}

