# Seeding Dummy Data

This guide explains how to seed the database with dummy data for development and testing.

## Quick Start

Run the seeding script:

```bash
python run_seed_data.py
```

Or directly:

```bash
python apps/database/seed_data.py
```

## What Gets Created

### Projects (4 projects)
1. **Q1 2025 Engineering Hiring** - Active
2. **Sales & Marketing Expansion** - Active  
3. **Data Science Initiative** - Active
4. **Product Management Growth** - Inactive

### Jobs (9 jobs)

#### Engineering (4 jobs)
- Senior Software Engineer - Backend
- Full Stack Developer
- DevOps Engineer
- Junior Software Engineer

#### Sales (2 jobs)
- Sales Development Representative
- Account Executive

#### Data Science (3 jobs)
- Senior Data Scientist
- Data Engineer
- Machine Learning Engineer

## Requirements

- MongoDB must be running (or set `MONGODB_URL`)
- All Python dependencies installed

## Customizing Data

Edit `apps/database/seed_data.py` to:
- Add more projects
- Add more jobs
- Modify job details
- Change skills and requirements

## Verifying Data

After seeding, you can verify:

1. **Via API:**
   ```bash
   curl http://127.0.0.1:8000/projects/
   curl http://127.0.0.1:8000/jobs/
   ```

2. **Via Swagger UI:**
   - Open http://127.0.0.1:8000/docs
   - Test the GET endpoints

## Re-seeding

To re-seed (clear and add new data):
1. Clear existing data from MongoDB (optional)
2. Run the seed script again

Note: The script will create new records, so running multiple times will create duplicates.

