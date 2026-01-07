"""Mercer Job Library Integration Service"""
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    # Try importing Mercer job library
    # Adjust import based on actual library name/path
    from mercer_job_library import JobMatcher, JobLibrary  # Example import
    # Alternative: from apps.libs.mercer import JobMatcher
    HAS_MERCER_LIB = True
except ImportError:
    HAS_MERCER_LIB = False
    # Use dummy/mock implementation
    try:
        from apps.ai.libs.dummy_mercer import DummyJobLibrary as JobLibrary, DummyJobMatcher as JobMatcher
        print("Using dummy Mercer job library for development")
    except ImportError:
        JobMatcher = None
        JobLibrary = None


@dataclass
class MercerMatchResult:
    """Result from Mercer job library matching"""
    job_id: str
    job_title: str
    match_score: float
    match_details: Dict[str, Any]
    competency_scores: Optional[Dict[str, float]] = None
    skill_gaps: Optional[List[str]] = None


class MercerJobLibraryService:
    """Service for integrating with Mercer Job Library"""
    
    def __init__(self, library_config: Optional[Dict[str, Any]] = None):
        """
        Initialize Mercer Job Library Service
        
        Args:
            library_config: Configuration dictionary for Mercer library
        """
        self.job_matcher = None
        self.job_library = None
        self.config = library_config or {}
        self.initialized = False
        
        if HAS_MERCER_LIB:
            try:
                # Initialize Mercer job library
                self._initialize_mercer_library()
            except Exception as e:
                print(f"Error initializing Mercer job library: {e}")
        else:
            # Use dummy/mock implementation when library is not available
            self.initialized = True  # Mark as initialized so dummy matching is used
            print("Mercer job library not available. Using dummy/mock implementation.")
    
    def _initialize_mercer_library(self):
        """Initialize the Mercer job library components"""
        try:
            # Initialize job library
            # Adjust based on actual Mercer library API
            self.job_library = JobLibrary(
                config_path=self.config.get("config_path"),
                api_key=self.config.get("api_key"),
                api_url=self.config.get("api_url")
            )
            
            # Initialize job matcher
            self.job_matcher = JobMatcher(
                library=self.job_library,
                matching_algorithm=self.config.get("algorithm", "default")
            )
            
            self.initialized = True
            print("Mercer job library initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Mercer job library: {e}")
            self.initialized = False
    
    def match_candidate_to_jobs(
        self,
        candidate_profile: Dict[str, Any],
        job_ids: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[MercerMatchResult]:
        """
        Match candidate to jobs using Mercer job library
        
        Args:
            candidate_profile: Candidate profile with skills, experience, etc.
            job_ids: Optional list of job IDs to match against
            limit: Maximum number of results
            
        Returns:
            List of MercerMatchResult objects
        """
        # Use dummy matching if real library is not available
        if not HAS_MERCER_LIB or not self.job_matcher:
            return self._fallback_match(candidate_profile, job_ids, limit)
        
        try:
            # Convert candidate profile to Mercer format
            mercer_candidate = self._convert_candidate_to_mercer_format(candidate_profile)
            
            # Get jobs from library or filter by job_ids
            if job_ids:
                jobs = self._get_jobs_by_ids(job_ids)
            else:
                jobs = self._get_all_active_jobs()
            
            # Perform matching using Mercer library
            matches = self.job_matcher.match(
                candidate=mercer_candidate,
                jobs=jobs,
                top_n=limit
            )
            
            # Convert results to our format
            results = []
            for match in matches:
                results.append(MercerMatchResult(
                    job_id=match.get("job_id") or match.get("id"),
                    job_title=match.get("job_title") or match.get("title", "Unknown"),
                    match_score=match.get("score", 0.0),
                    match_details=match.get("details", {}),
                    competency_scores=match.get("competency_scores"),
                    skill_gaps=match.get("skill_gaps", [])
                ))
            
            return results
            
        except Exception as e:
            print(f"Error in Mercer job matching: {e}")
            return self._fallback_match(candidate_profile, job_ids, limit)
    
    def get_job_taxonomy(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job taxonomy/classification from Mercer library
        
        Args:
            job_id: Job ID
            
        Returns:
            Job taxonomy information or None
        """
        if not self.initialized or not self.job_library:
            return None
        
        try:
            return self.job_library.get_job_taxonomy(job_id)
        except Exception as e:
            print(f"Error getting job taxonomy: {e}")
            return None
    
    def get_competency_model(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get competency model for a job from Mercer library
        
        Args:
            job_id: Job ID
            
        Returns:
            Competency model or None
        """
        if not self.initialized or not self.job_library:
            return None
        
        try:
            return self.job_library.get_competency_model(job_id)
        except Exception as e:
            print(f"Error getting competency model: {e}")
            return None
    
    def search_jobs_by_criteria(
        self,
        criteria: Dict[str, Any],
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search jobs using Mercer library search capabilities
        
        Args:
            criteria: Search criteria (skills, level, department, etc.)
            limit: Maximum number of results
            
        Returns:
            List of matching jobs
        """
        if not self.initialized or not self.job_library:
            return []
        
        try:
            return self.job_library.search(criteria=criteria, limit=limit)
        except Exception as e:
            print(f"Error searching jobs: {e}")
            return []
    
    def enrich_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich job data with Mercer library information
        
        Args:
            job_data: Basic job data
            
        Returns:
            Enriched job data with Mercer classifications, competencies, etc.
        """
        if not self.initialized or not self.job_library:
            return job_data
        
        try:
            job_id = job_data.get("id") or job_data.get("_id")
            if not job_id:
                return job_data
            
            # Get additional data from Mercer library
            taxonomy = self.get_job_taxonomy(str(job_id))
            competency_model = self.get_competency_model(str(job_id))
            
            enriched = job_data.copy()
            if taxonomy:
                enriched["mercer_taxonomy"] = taxonomy
            if competency_model:
                enriched["mercer_competencies"] = competency_model
            
            return enriched
            
        except Exception as e:
            print(f"Error enriching job data: {e}")
            return job_data
    
    def _convert_candidate_to_mercer_format(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Convert candidate profile to Mercer library format"""
        return {
            "skills": candidate.get("skills", []),
            "experience": {
                "years": candidate.get("years_of_experience", 0),
                "summary": candidate.get("experience_summary", "")
            },
            "education": candidate.get("education", ""),
            "role": candidate.get("desired_role", ""),
            "location": candidate.get("location"),
            "metadata": candidate.get("metadata", {})
        }
    
    def _get_jobs_by_ids(self, job_ids: List[str]) -> List[Dict[str, Any]]:
        """Get jobs from Mercer library by IDs"""
        if not self.job_library:
            return []
        try:
            return [self.job_library.get_job(job_id) for job_id in job_ids]
        except Exception as e:
            print(f"Error getting jobs by IDs: {e}")
            return []
    
    def _get_all_active_jobs(self) -> List[Dict[str, Any]]:
        """Get all active jobs from Mercer library"""
        if not self.job_library:
            return []
        try:
            return self.job_library.list_jobs(status="active")
        except Exception as e:
            print(f"Error getting active jobs: {e}")
            return []
    
    def _fallback_match(
        self,
        candidate_profile: Dict[str, Any],
        job_ids: Optional[List[str]],
        limit: int
    ) -> List[MercerMatchResult]:
        """Fallback matching when Mercer library is not available - Dummy implementation"""
        print("Using dummy Mercer matching (Mercer library not available)")
        
        # Import here to avoid circular dependency
        try:
            from apps.core.client import CoreAPIClient
            from apps.services.mmc_jobs import JobService
            
            core_api = CoreAPIClient()
            job_service = JobService(core_api)
            
            # Get candidate skills
            candidate_skills = set([s.lower() for s in candidate_profile.get("skills", [])])
            candidate_experience = candidate_profile.get("years_of_experience", 0)
            desired_role = candidate_profile.get("desired_role", "").lower()
            
            # Get jobs from database
            all_jobs_result = job_service.list_all_jobs(
                tenant_id="default",
                skip=0,
                limit=100
            )
            
            jobs = all_jobs_result.get("jobs", [])
            
            # Filter by job_ids if provided
            if job_ids:
                jobs = [j for j in jobs if j.get("id") in job_ids]
            
            # Filter only published jobs
            jobs = [j for j in jobs if j.get("status") == "published"]
            
            # Calculate matches
            matches = []
            for job in jobs:
                job_id = job.get("id")
                job_title = job.get("title", "Unknown")
                job_skills = set([s.lower() for s in job.get("required_skills", [])])
                job_level = job.get("level", "").lower()
                
                # Calculate skill overlap
                skill_overlap = len(candidate_skills.intersection(job_skills))
                total_skills = len(job_skills) if job_skills else 1
                skill_score = skill_overlap / total_skills if total_skills > 0 else 0.0
                
                # Calculate level match
                level_score = 1.0
                if job_level:
                    if "senior" in job_level and candidate_experience < 5:
                        level_score = 0.6
                    elif "mid" in job_level and candidate_experience < 2:
                        level_score = 0.7
                    elif "entry" in job_level and candidate_experience > 5:
                        level_score = 0.8
                
                # Title relevance
                title_score = 1.0
                if desired_role:
                    title_words = set(desired_role.split())
                    job_words = set(job_title.lower().split())
                    common_words = len(title_words.intersection(job_words))
                    if title_words:
                        title_score = min(1.0, common_words / len(title_words))
                
                # Combined score (weighted)
                match_score = (skill_score * 0.5) + (level_score * 0.3) + (title_score * 0.2)
                
                # Skill gaps
                skill_gaps = list(job_skills - candidate_skills)
                matched_skills = list(candidate_skills.intersection(job_skills))
                
                # Match details
                match_details = {
                    "skill_match": f"{skill_overlap}/{total_skills}",
                    "level_match": level_score,
                    "title_relevance": title_score,
                    "algorithm": "dummy-mercer"
                }
                
                # Competency scores (dummy)
                competency_scores = {}
                for skill in matched_skills:
                    competency_scores[skill] = min(1.0, match_score + 0.1)
                
                matches.append(MercerMatchResult(
                    job_id=job_id,
                    job_title=job_title,
                    match_score=round(match_score, 3),
                    match_details=match_details,
                    competency_scores=competency_scores if competency_scores else None,
                    skill_gaps=skill_gaps[:5]  # Top 5 gaps
                ))
            
            # Sort by match score
            matches.sort(key=lambda x: x.match_score, reverse=True)
            return matches[:limit]
            
        except Exception as e:
            print(f"Error in dummy Mercer matching: {e}")
            import traceback
            traceback.print_exc()
            return []


# Singleton instance
_mercer_service: Optional[MercerJobLibraryService] = None


def get_mercer_service(config: Optional[Dict[str, Any]] = None) -> MercerJobLibraryService:
    """Get singleton instance of Mercer Job Library Service"""
    global _mercer_service
    if _mercer_service is None:
        # Load config from environment or defaults
        mercer_config = config or {
            "config_path": os.getenv("MERCER_CONFIG_PATH"),
            "api_key": os.getenv("MERCER_API_KEY"),
            "api_url": os.getenv("MERCER_API_URL", "https://api.mercer.com/jobs"),
            "algorithm": os.getenv("MERCER_ALGORITHM", "default")
        }
        _mercer_service = MercerJobLibraryService(library_config=mercer_config)
    return _mercer_service

