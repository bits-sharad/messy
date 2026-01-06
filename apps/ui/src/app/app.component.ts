import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule],
  template: `
    <div class="app-container">
      <header class="app-header">
        <h1>MMC Job Matching Model</h1>
        <nav>
          <a routerLink="/" routerLinkActive="active">Home</a>
          <a routerLink="/projects" routerLinkActive="active">Projects</a>
          <a routerLink="/jobs" routerLinkActive="active">Jobs</a>
        </nav>
      </header>
      <main class="app-content">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [`
    .app-container {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .app-header {
      background-color: #1976d2;
      color: white;
      padding: 1rem 2rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .app-header h1 {
      margin: 0 0 1rem 0;
      font-size: 1.5rem;
    }
    nav {
      display: flex;
      gap: 1rem;
    }
    nav a {
      color: white;
      text-decoration: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      transition: background-color 0.3s;
    }
    nav a:hover,
    nav a.active {
      background-color: rgba(255, 255, 255, 0.2);
    }
    .app-content {
      flex: 1;
      padding: 2rem;
      max-width: 1200px;
      width: 100%;
      margin: 0 auto;
    }
  `]
})
export class AppComponent {
  title = 'MMC Job Matching UI';
}

