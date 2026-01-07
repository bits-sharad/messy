"""Dummy/Mock Mercer Job Library for Development and Testing

This module provides a mock implementation of the Mercer job library
for development and testing when the actual library is not available.
"""

from typing import List, Dict, Any, Optional


class DummyJobLibrary:
    """Dummy implementation of Mercer JobLibrary"""
    
    def __init__(self, config_path=None, api_key=None, api_url=None):
        """Initialize dummy library"""
        self.config_path = config_path
        self.api_key = api_key
        self.api_url = api_url
        self._jobs_cache = {}
        print("Initialized Dummy Mercer Job Library")
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        return self._jobs_cache.get(job_id)
    
    def list_jobs(self, status: str = "active") -> List[Dict[str, Any]]:
        """List jobs by status"""
        return [job for job in self._jobs_cache.values() if job.get("status") == status]
    
    def get_job_taxonomy(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job taxonomy - dummy implementation"""
        job = self.get_job(job_id)
        if not job:
            return None
        
        # Dummy taxonomy based on job title/level
        title = job.get("title", "").lower()
        level = job.get("level", "").lower()
        
        taxonomy = {
            "job_family": "Information Technology" if "engineer" in title or "developer" in title else "Business",
            "job_sub_family": "Software Development" if "software" in title else "General",
            "job_level": level.capitalize() if level else "Mid",
            "mercer_code": f"MERCER-{job_id[:8]}",
            "classification": "Professional"
        }
        
        return taxonomy
    
    def get_competency_model(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get competency model - dummy implementation"""
        job = self.get_job(job_id)
        if not job:
            return None
        
        skills = job.get("required_skills", [])
        
        competencies = {
            "technical_competencies": skills[:5],  # Top 5 technical skills
            "behavioral_competencies": [
                "Problem Solving",
                "Communication",
                "Teamwork"
            ],
            "required_proficiencies": {
                skill: "Proficient" for skill in skills[:3]
            }
        }
        
        return competencies
    
    def search(self, criteria: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
        """Search jobs - dummy implementation"""
        jobs = list(self._jobs_cache.values())
        
        # Simple filtering
        if "status" in criteria:
            jobs = [j for j in jobs if j.get("status") == criteria["status"]]
        if "level" in criteria:
            jobs = [j for j in jobs if j.get("level", "").lower() == criteria["level"].lower()]
        
        return jobs[:limit]


class DummyJobMatcher:
    """Dummy implementation of Mercer JobMatcher"""
    
    def __init__(self, library=None, matching_algorithm="default"):
        """Initialize dummy matcher"""
        self.library = library
        self.algorithm = matching_algorithm
        print(f"Initialized Dummy Mercer Job Matcher (algorithm: {matching_algorithm})")
    
    def match(
        self,
        candidate: Dict[str, Any],
        jobs: List[Dict[str, Any]],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Match candidate to jobs - dummy implementation"""
        candidate_skills = set([s.lower() for s in candidate.get("skills", [])])
        candidate_exp = candidate.get("experience", {}).get("years", 0)
        
        matches = []
        for job in jobs:
            job_skills = set([s.lower() for s in job.get("required_skills", [])])
            
            # Simple scoring
            skill_overlap = len(candidate_skills.intersection(job_skills))
            total_skills = len(job_skills) if job_skills else 1
            score = skill_overlap / total_skills if total_skills > 0 else 0.0
            
            # Adjust score based on experience
            job_level = job.get("level", "").lower()
            if "senior" in job_level and candidate_exp >= 5:
                score += 0.2
            elif "mid" in job_level and 2 <= candidate_exp < 5:
                score += 0.1
            elif "entry" in job_level and candidate_exp < 2:
                score += 0.1
            
            score = min(1.0, score)  # Cap at 1.0
            
            matches.append({
                "job_id": job.get("id") or job.get("_id"),
                "job_title": job.get("title", "Unknown"),
                "score": round(score, 3),
                "details": {
                    "skill_match": f"{skill_overlap}/{total_skills}",
                    "algorithm": "dummy-mercer"
                },
                "competency_scores": {
                    skill: score + 0.1 for skill in candidate_skills.intersection(job_skills)
                },
                "skill_gaps": list(job_skills - candidate_skills)[:5]
            })
        
        # Sort by score
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:top_n]


# Export for use as mock
__all__ = ["DummyJobLibrary", "DummyJobMatcher"]

