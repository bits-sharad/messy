import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-projects',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="projects-container">
      <h2>Projects</h2>
      <div class="api-info">
        <small>Connected to: {{ apiUrl }}</small>
      </div>
      <div *ngIf="loading">Loading...</div>
      <div *ngIf="error" class="error">{{ error }}</div>
      <div *ngIf="projects && projects.length > 0" class="projects-list">
        <div *ngFor="let project of projects" class="project-card">
          <h3>{{ project.name }}</h3>
          <p>{{ project.description }}</p>
          <div class="project-meta">
            <span>Status: {{ project.status }}</span>
            <span>Jobs: {{ project.job_count || 0 }}</span>
          </div>
        </div>
      </div>
      <div *ngIf="projects && projects.length === 0 && !loading" class="empty-state">
        No projects found
      </div>
    </div>
  `,
  styles: [`
    .projects-container {
      max-width: 800px;
    }
    .projects-list {
      display: grid;
      gap: 1rem;
      margin-top: 1rem;
    }
    .project-card {
      background: white;
      padding: 1.5rem;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .project-card h3 {
      margin-top: 0;
      color: #1976d2;
    }
    .project-meta {
      display: flex;
      gap: 1rem;
      margin-top: 1rem;
      font-size: 0.9rem;
      color: #666;
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
export class ProjectsComponent implements OnInit {
  projects: any[] = [];
  loading = false;
  error: string | null = null;
  apiUrl = environment.apiUrl;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadProjects();
  }

  loadProjects() {
    this.loading = true;
    this.error = null;
    this.apiService.getProjects('default').subscribe({
      next: (data) => {
        this.projects = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = `Failed to load projects. Make sure the API is running at ${this.apiUrl}`;
        this.loading = false;
        console.error('Error loading projects:', err);
      }
    });
  }
}

