"""Script to seed dummy data for development"""
import asyncio
from datetime import datetime
from bson import ObjectId

from apps.database.connection import db_manager
from apps.services.mmc_project import ProjectService
from apps.services.mmc_jobs import JobService
from apps.core.client import CoreAPIClient
from apps.core.principal import Principal


def create_dummy_principal():
    """Create a dummy principal for seeding data"""
    return Principal(
        subject="seed-user-001",
        tenant_id="default",
        roles=["admin"],
        permissions=["read", "write", "admin"]
    )


async def seed_projects(core_api: CoreAPIClient, principal: Principal):
    """Seed dummy projects"""
    project_service = ProjectService(core_api)
    
    projects_data = [
        {
            "name": "Q1 2025 Engineering Hiring",
            "description": "Recruitment drive for engineering roles in Q1 2025. Focus on backend and full-stack developers.",
            "tenant_id": "default",
            "status": "active",
            "metadata": {"department": "Engineering", "budget": 500000, "target_hires": 20}
        },
        {
            "name": "Sales & Marketing Expansion",
            "description": "Expanding our sales and marketing teams to support new product launches and market expansion.",
            "tenant_id": "default",
            "status": "active",
            "metadata": {"department": "Sales", "budget": 300000, "target_hires": 15}
        },
        {
            "name": "Data Science Initiative",
            "description": "Building a world-class data science team to drive AI/ML initiatives and advanced analytics.",
            "tenant_id": "default",
            "status": "active",
            "metadata": {"department": "Data Science", "budget": 400000, "target_hires": 10}
        },
        {
            "name": "Product Management Growth",
            "description": "Scaling product management organization to support product portfolio expansion.",
            "tenant_id": "default",
            "status": "inactive",
            "metadata": {"department": "Product", "budget": 250000, "target_hires": 8}
        }
    ]
    
    created_projects = []
    for project_data in projects_data:
        try:
            from apps.schemas.requests import ProjectCreateRequest
            project_request = ProjectCreateRequest(
                name=project_data["name"],
                description=project_data["description"],
                tenant_id=project_data["tenant_id"],
                status=project_data["status"],
                metadata=project_data.get("metadata", {}),
                created_by=principal.subject
            )
            project = await project_service.create_project(project_request, principal)
            created_projects.append(project)
            print(f"[OK] Created project: {project['name']} (ID: {project['id']})")
        except Exception as e:
            print(f"[ERROR] Error creating project {project_data['name']}: {e}")
    
    return created_projects


async def seed_jobs(core_api: CoreAPIClient, principal: Principal, project_ids: list):
    """Seed dummy jobs"""
    job_service = JobService(core_api)
    
    jobs_data = [
        # Engineering jobs
        {
            "project_id": project_ids[0] if project_ids else None,
            "title": "Senior Software Engineer - Backend",
            "description": "We are looking for an experienced backend engineer to design and develop scalable APIs. You will work with modern technologies like Python, FastAPI, and cloud infrastructure.",
            "job_code": "ENG-001",
            "status": "published",
            "department": "Engineering",
            "level": "senior",
            "required_skills": ["Python", "FastAPI", "MongoDB", "Docker", "AWS", "REST APIs"],
            "responsibilities": [
                "Design and develop scalable backend APIs",
                "Write clean, maintainable, and tested code",
                "Participate in code reviews and technical discussions",
                "Collaborate with frontend and DevOps teams",
                "Optimize application performance"
            ],
            "metadata": {"remote": True, "salary_range": "120k-160k", "location": "Remote/New York"}
        },
        {
            "project_id": project_ids[0] if project_ids else None,
            "title": "Full Stack Developer",
            "description": "Join our team to build modern web applications. We use React, TypeScript, Node.js, and cloud technologies. Great opportunity for growth and learning.",
            "job_code": "ENG-002",
            "status": "published",
            "department": "Engineering",
            "level": "mid",
            "required_skills": ["JavaScript", "TypeScript", "React", "Node.js", "MongoDB", "Git"],
            "responsibilities": [
                "Develop frontend and backend features",
                "Build reusable components and services",
                "Write unit and integration tests",
                "Participate in agile ceremonies"
            ],
            "metadata": {"remote": True, "salary_range": "90k-120k"}
        },
        {
            "project_id": project_ids[0] if project_ids else None,
            "title": "DevOps Engineer",
            "description": "Looking for a DevOps engineer to manage our infrastructure, CI/CD pipelines, and cloud resources. Experience with Kubernetes and Terraform preferred.",
            "job_code": "ENG-003",
            "status": "published",
            "department": "Engineering",
            "level": "mid",
            "required_skills": ["Docker", "Kubernetes", "Terraform", "AWS", "CI/CD", "Linux"],
            "responsibilities": [
                "Manage cloud infrastructure",
                "Build and maintain CI/CD pipelines",
                "Monitor system performance and reliability",
                "Automate deployment processes"
            ],
            "metadata": {"remote": True, "salary_range": "100k-140k"}
        },
        {
            "project_id": project_ids[0] if project_ids else None,
            "title": "Junior Software Engineer",
            "description": "Entry-level position for recent graduates or career changers. We provide mentorship and growth opportunities. Learn from experienced engineers.",
            "job_code": "ENG-004",
            "status": "published",
            "department": "Engineering",
            "level": "entry",
            "required_skills": ["Python", "JavaScript", "Git", "Basic Algorithms"],
            "responsibilities": [
                "Learn and contribute to codebase",
                "Fix bugs and implement small features",
                "Participate in code reviews",
                "Attend training sessions"
            ],
            "metadata": {"remote": True, "salary_range": "70k-90k"}
        },
        # Sales jobs
        {
            "project_id": project_ids[1] if len(project_ids) > 1 else None,
            "title": "Sales Development Representative",
            "description": "We're looking for motivated SDRs to generate leads and qualify prospects. Great opportunity to grow into an Account Executive role.",
            "job_code": "SALES-001",
            "status": "published",
            "department": "Sales",
            "level": "entry",
            "required_skills": ["Sales", "CRM", "Communication", "Lead Generation"],
            "responsibilities": [
                "Generate and qualify leads",
                "Schedule meetings for account executives",
                "Maintain CRM database",
                "Achieve monthly quota targets"
            ],
            "metadata": {"remote": False, "salary_range": "50k-70k + commission"}
        },
        {
            "project_id": project_ids[1] if len(project_ids) > 1 else None,
            "title": "Account Executive",
            "description": "Experienced sales professional needed to close enterprise deals. Track record of success in B2B software sales required.",
            "job_code": "SALES-002",
            "status": "published",
            "department": "Sales",
            "level": "senior",
            "required_skills": ["Enterprise Sales", "Negotiation", "CRM", "B2B", "Presentation Skills"],
            "responsibilities": [
                "Manage enterprise sales pipeline",
                "Close large deals",
                "Build relationships with key accounts",
                "Exceed revenue targets"
            ],
            "metadata": {"remote": False, "salary_range": "100k-150k + commission"}
        },
        # Data Science jobs
        {
            "project_id": project_ids[2] if len(project_ids) > 2 else None,
            "title": "Senior Data Scientist",
            "description": "Lead data science initiatives and build machine learning models. Work with large datasets and deploy models to production.",
            "job_code": "DS-001",
            "status": "published",
            "department": "Data Science",
            "level": "senior",
            "required_skills": ["Python", "Machine Learning", "TensorFlow", "Pandas", "SQL", "Statistics"],
            "responsibilities": [
                "Develop and deploy ML models",
                "Analyze large datasets",
                "Collaborate with engineering teams",
                "Present findings to stakeholders"
            ],
            "metadata": {"remote": True, "salary_range": "140k-180k"}
        },
        {
            "project_id": project_ids[2] if len(project_ids) > 2 else None,
            "title": "Data Engineer",
            "description": "Build and maintain data pipelines, ETL processes, and data infrastructure. Experience with Spark and cloud data warehouses preferred.",
            "job_code": "DS-002",
            "status": "published",
            "department": "Data Science",
            "level": "mid",
            "required_skills": ["Python", "Spark", "SQL", "ETL", "AWS", "Data Warehousing"],
            "responsibilities": [
                "Build and maintain data pipelines",
                "Optimize data processing workflows",
                "Ensure data quality and reliability",
                "Work with data scientists on model deployment"
            ],
            "metadata": {"remote": True, "salary_range": "110k-150k"}
        },
        {
            "project_id": project_ids[2] if len(project_ids) > 2 else None,
            "title": "Machine Learning Engineer",
            "description": "Bridge the gap between data science and engineering. Deploy ML models to production and optimize for scale.",
            "job_code": "DS-003",
            "status": "draft",
            "department": "Data Science",
            "level": "senior",
            "required_skills": ["Python", "MLOps", "Docker", "Kubernetes", "TensorFlow", "MLflow"],
            "responsibilities": [
                "Deploy ML models to production",
                "Build MLOps infrastructure",
                "Optimize model performance",
                "Monitor model drift and retraining"
            ],
            "metadata": {"remote": True, "salary_range": "130k-170k"}
        }
    ]
    
    created_jobs = []
    for job_data in jobs_data:
        if not job_data["project_id"]:
            continue
        try:
            from apps.schemas.requests import JobCreateRequest
            job_request = JobCreateRequest(
                project_id=job_data["project_id"],
                title=job_data["title"],
                description=job_data["description"],
                job_code=job_data["job_code"],
                status=job_data["status"],
                department=job_data.get("department"),
                level=job_data.get("level"),
                required_skills=job_data.get("required_skills", []),
                responsibilities=job_data.get("responsibilities", []),
                metadata=job_data.get("metadata", {}),
                created_by=principal.subject
            )
            job = await job_service.create_job(job_request, principal)
            created_jobs.append(job)
            print(f"[OK] Created job: {job['title']} (ID: {job['id']}, Code: {job['job_code']})")
        except Exception as e:
            print(f"[ERROR] Error creating job {job_data['title']}: {e}")
    
    return created_jobs


async def main():
    """Main seeding function"""
    print("=" * 60)
    print("Seeding Dummy Data")
    print("=" * 60)
    
    # Connect to database
    db_manager.connect()
    if not db_manager.is_connected():
        print("[WARNING] Database not connected. Data will not be persisted.")
        print("[WARNING] To fix: Start MongoDB or set MONGODB_URL environment variable.")
        print("\nAttempting to continue anyway (may fail)...")
        # Try to continue - let it fail on actual DB operations
    
    # Initialize services
    core_api = CoreAPIClient()
    principal = create_dummy_principal()
    
    print("\n1. Seeding Projects...")
    projects = await seed_projects(core_api, principal)
    
    if not projects:
        print("[WARNING] No projects created. Cannot create jobs.")
        return
    
    project_ids = [p["id"] for p in projects]
    print(f"\n[OK] Created {len(projects)} projects")
    
    print("\n2. Seeding Jobs...")
    jobs = await seed_jobs(core_api, principal, project_ids)
    print(f"\n[OK] Created {len(jobs)} jobs")
    
    print("\n" + "=" * 60)
    print("Seeding Complete!")
    print("=" * 60)
    print(f"Total Projects: {len(projects)}")
    print(f"Total Jobs: {len(jobs)}")
    print("\nYou can now test the API at http://127.0.0.1:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())

