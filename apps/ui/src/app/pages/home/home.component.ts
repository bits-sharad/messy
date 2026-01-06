import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="home-container">
      <h2>Welcome to MMC Job Matching Model</h2>
      <p>This application helps manage projects and jobs for the job matching system.</p>
      <div class="cards">
        <div class="card">
          <h3>Projects</h3>
          <p>Manage your hiring projects</p>
          <a routerLink="/projects" class="btn">View Projects</a>
        </div>
        <div class="card">
          <h3>Jobs</h3>
          <p>Manage job postings</p>
          <a routerLink="/jobs" class="btn">View Jobs</a>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .home-container {
      text-align: center;
    }
    h2 {
      color: #1976d2;
      margin-bottom: 1rem;
    }
    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 2rem;
      margin-top: 2rem;
    }
    .card {
      background: white;
      padding: 2rem;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .card h3 {
      color: #1976d2;
      margin-top: 0;
    }
    .btn {
      display: inline-block;
      margin-top: 1rem;
      padding: 0.75rem 1.5rem;
      background-color: #1976d2;
      color: white;
      text-decoration: none;
      border-radius: 4px;
      transition: background-color 0.3s;
    }
    .btn:hover {
      background-color: #1565c0;
    }
  `]
})
export class HomeComponent {
}

