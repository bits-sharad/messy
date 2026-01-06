import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-projects',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="projects-container">
      <h2>Projects</h2>
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
      <div *ngIf="projects && projects.length === 0" class="empty-state">
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
  `]
})
export class ProjectsComponent implements OnInit {
  projects: any[] = [];
  loading = false;
  error: string | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadProjects();
  }

  loadProjects() {
    this.loading = true;
    this.error = null;
    // Update this URL to match your API endpoint
    const apiUrl = 'http://localhost:8000/api/v1/projects?tenant_id=default';
    this.http.get<any[]>(apiUrl).subscribe({
      next: (data) => {
        this.projects = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load projects. Make sure the API is running.';
        this.loading = false;
        console.error('Error loading projects:', err);
      }
    });
  }
}

