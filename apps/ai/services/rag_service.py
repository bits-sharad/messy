"""RAG (Retrieval-Augmented Generation) Service for Job Matching"""
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

# Import Mercer job library service
try:
    from apps.ai.services.mercer_job_library import get_mercer_service, MercerJobLibraryService
    HAS_MERCER = True
except ImportError:
    HAS_MERCER = False
    print("Mercer job library service not available")

try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    print("Warning: sentence-transformers or chromadb not installed. RAG features will be limited.")

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("Warning: openai package not installed. LLM features will be limited.")


@dataclass
class MatchResult:
    """Result of a job-candidate match"""
    job_id: str
    job_title: str
    match_score: float
    match_reasons: List[str]
    missing_skills: List[str]
    matched_skills: List[str]


class RAGService:
    """Service for RAG-based job matching and generation"""
    
    def __init__(
        self, 
        embedding_model_name: str = "all-MiniLM-L6-v2", 
        chroma_persist_dir: str = "./chroma_db",
        use_mercer: bool = True
    ):
        """
        Initialize RAG Service
        
        Args:
            embedding_model_name: Name of the sentence transformer model to use
            chroma_persist_dir: Directory to persist ChromaDB data
            use_mercer: Whether to integrate with Mercer job library
        """
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.llm_api_key = os.getenv("OPENAI_API_KEY")
        self.use_mercer = use_mercer and HAS_MERCER
        self.mercer_service = None
        
        # Initialize Mercer job library if enabled
        if self.use_mercer:
            try:
                self.mercer_service = get_mercer_service()
                print("Mercer job library integrated with RAG service")
            except Exception as e:
                print(f"Warning: Could not initialize Mercer service: {e}")
                self.use_mercer = False
        
        if HAS_EMBEDDINGS:
            try:
                # Initialize embedding model
                self.embedding_model = SentenceTransformer(embedding_model_name)
                
                # Initialize ChromaDB client
                self.chroma_client = chromadb.PersistentClient(
                    path=chroma_persist_dir,
                    settings=Settings(anonymized_telemetry=False)
                )
                
                # Get or create collection for job embeddings
                self.collection = self.chroma_client.get_or_create_collection(
                    name="jobs",
                    metadata={"description": "Job postings and descriptions"}
                )
                print(f"RAG Service initialized with model: {embedding_model_name}")
            except Exception as e:
                print(f"Error initializing RAG service: {e}")
                self.embedding_model = None
        
        if HAS_OPENAI and self.llm_api_key:
            openai.api_key = self.llm_api_key
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a text string
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if model not available
        """
        if not self.embedding_model or not text:
            return None
        
        try:
            embedding = self.embedding_model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def index_job(self, job_id: str, job_data: Dict[str, Any]) -> bool:
        """
        Index a job posting for semantic search
        
        Args:
            job_id: Unique job identifier
            job_data: Job data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.collection or not self.embedding_model:
            return False
        
        try:
            # Create a searchable text from job data
            searchable_text = self._create_searchable_text(job_data)
            
            # Generate embedding
            embedding = self.generate_embedding(searchable_text)
            if not embedding:
                return False
            
            # Store in ChromaDB
            metadata = {
                "job_id": job_id,
                "title": job_data.get("title", ""),
                "department": job_data.get("department", ""),
                "level": job_data.get("level", ""),
                "status": job_data.get("status", ""),
                "project_id": job_data.get("project_id", ""),
                "skills": json.dumps(job_data.get("required_skills", []))
            }
            
            self.collection.add(
                ids=[job_id],
                embeddings=[embedding],
                documents=[searchable_text],
                metadatas=[metadata]
            )
            
            return True
        except Exception as e:
            print(f"Error indexing job {job_id}: {e}")
            return False
    
    def search_similar_jobs(
        self, 
        query: str, 
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs similar to the query using semantic search
        
        Args:
            query: Search query text
            limit: Maximum number of results
            filters: Optional filters (e.g., {"status": "published"})
            
        Returns:
            List of matching job results with scores
        """
        if not self.collection or not self.embedding_model:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                return []
            
            # Prepare where clause for filters
            where = {}
            if filters:
                where = {f"metadata.{k}": v for k, v in filters.items()}
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where if where else None
            )
            
            # Format results
            matches = []
            if results["ids"] and len(results["ids"]) > 0:
                for i, job_id in enumerate(results["ids"][0]):
                    matches.append({
                        "job_id": job_id,
                        "score": 1 - results["distances"][0][i] if results["distances"] else 0.0,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "document": results["documents"][0][i] if results["documents"] else ""
                    })
            
            return matches
        except Exception as e:
            print(f"Error searching jobs: {e}")
            return []
    
    def match_candidate_to_jobs(
        self,
        candidate_profile: Dict[str, Any],
        job_ids: Optional[List[str]] = None,
        limit: int = 10,
        use_mercer: Optional[bool] = None
    ) -> List[MatchResult]:
        """
        Match a candidate profile to relevant jobs using RAG and/or Mercer library
        
        Args:
            candidate_profile: Candidate data with skills, experience, etc.
            job_ids: Optional list of job IDs to consider (None = search all)
            limit: Maximum number of matches to return
            use_mercer: Whether to use Mercer library (None = use default setting)
            
        Returns:
            List of MatchResult objects
        """
        # Determine if we should use Mercer
        should_use_mercer = (use_mercer if use_mercer is not None else self.use_mercer) and self.mercer_service
        
        # Try Mercer library first if enabled
        if should_use_mercer:
            try:
                mercer_matches = self.mercer_service.match_candidate_to_jobs(
                    candidate_profile=candidate_profile,
                    job_ids=job_ids,
                    limit=limit
                )
                
                if mercer_matches:
                    # Convert Mercer results to MatchResult format
                    results = []
                    for mercer_match in mercer_matches:
                        match_reasons = [
                            f"Mercer match score: {mercer_match.match_score:.2f}"
                        ]
                        if mercer_match.competency_scores:
                            match_reasons.append(f"Competency match: {len(mercer_match.competency_scores)} competencies")
                        if mercer_match.match_details:
                            match_reasons.extend(
                                [f"{k}: {v}" for k, v in list(mercer_match.match_details.items())[:3]]
                            )
                        
                        results.append(MatchResult(
                            job_id=mercer_match.job_id,
                            job_title=mercer_match.job_title,
                            match_score=mercer_match.match_score,
                            match_reasons=match_reasons,
                            missing_skills=mercer_match.skill_gaps or [],
                            matched_skills=list(mercer_match.competency_scores.keys()) if mercer_match.competency_scores else []
                        ))
                    
                    if results:
                        return results[:limit]
            except Exception as e:
                print(f"Error using Mercer library, falling back to RAG: {e}")
        
        # Fallback to RAG-based matching
        if not self.collection or not self.embedding_model:
            return []
        
        try:
            # Create candidate query from profile
            candidate_query = self._create_candidate_query(candidate_profile)
            
            # Search for matching jobs
            filters = {"status": "published"}  # Only active jobs
            if job_ids:
                # Filter by specific job IDs if provided
                # Note: ChromaDB doesn't support OR queries easily, 
                # so we'd need to filter results after
                pass
            
            matches = self.search_similar_jobs(
                query=candidate_query,
                limit=limit * 2,  # Get more to filter
                filters=filters
            )
            
            # Process matches and calculate detailed scores
            results = []
            candidate_skills = set(
                [s.lower() for s in candidate_profile.get("skills", [])]
            )
            
            for match in matches[:limit]:
                if job_ids and match["job_id"] not in job_ids:
                    continue
                
                metadata = match.get("metadata", {})
                job_skills = json.loads(metadata.get("skills", "[]"))
                job_skills_set = set([s.lower() for s in job_skills])
                
                # Calculate skill overlap
                matched_skills = list(candidate_skills.intersection(job_skills_set))
                missing_skills = list(job_skills_set - candidate_skills)
                
                # Generate match reasons
                match_reasons = self._generate_match_reasons(
                    candidate_profile,
                    metadata,
                    matched_skills,
                    match["score"]
                )
                
                results.append(MatchResult(
                    job_id=match["job_id"],
                    job_title=metadata.get("title", "Unknown"),
                    match_score=match["score"],
                    match_reasons=match_reasons,
                    missing_skills=missing_skills,
                    matched_skills=matched_skills
                ))
            
            # Sort by match score
            results.sort(key=lambda x: x.match_score, reverse=True)
            return results[:limit]
            
        except Exception as e:
            print(f"Error matching candidate: {e}")
            return []
    
    def generate_job_description(
        self,
        requirements: Dict[str, Any],
        use_llm: bool = True
    ) -> str:
        """
        Generate a job description using AI
        
        Args:
            requirements: Job requirements (title, skills, level, etc.)
            use_llm: Whether to use LLM (OpenAI) or template-based generation
            
        Returns:
            Generated job description
        """
        if use_llm and HAS_OPENAI and self.llm_api_key:
            return self._generate_with_llm(requirements)
        else:
            return self._generate_from_template(requirements)
    
    def answer_job_question(
        self,
        question: str,
        job_id: str,
        context_jobs: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Answer a question about a job using RAG
        
        Args:
            question: User question
            job_id: Job ID to answer about
            context_jobs: Optional list of job documents for context
            
        Returns:
            Answer string
        """
        if not HAS_OPENAI or not self.llm_api_key:
            return "LLM service not available. Please configure OPENAI_API_KEY."
        
        try:
            # Retrieve relevant context
            if context_jobs:
                context = self._format_jobs_for_context(context_jobs)
            else:
                # Try to retrieve job from ChromaDB or database
                context = f"Job ID: {job_id}"
            
            # Construct prompt
            prompt = f"""You are a helpful assistant answering questions about job postings.

Context about the job:
{context}

Question: {question}

Provide a clear, concise answer based on the job information above."""
            
            # Call OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful job matching assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error answering question: {e}")
            return f"Error generating answer: {str(e)}"
    
    def _create_searchable_text(self, job_data: Dict[str, Any]) -> str:
        """Create searchable text from job data"""
        parts = [
            job_data.get("title", ""),
            job_data.get("description", ""),
            ", ".join(job_data.get("required_skills", [])),
            job_data.get("department", ""),
            job_data.get("level", ""),
            " ".join(job_data.get("responsibilities", []))
        ]
        return " ".join(filter(None, parts))
    
    def _create_candidate_query(self, candidate_profile: Dict[str, Any]) -> str:
        """Create search query from candidate profile"""
        parts = [
            ", ".join(candidate_profile.get("skills", [])),
            candidate_profile.get("experience_summary", ""),
            candidate_profile.get("education", ""),
            candidate_profile.get("desired_role", "")
        ]
        return " ".join(filter(None, parts))
    
    def _generate_match_reasons(
        self,
        candidate: Dict[str, Any],
        job_metadata: Dict[str, Any],
        matched_skills: List[str],
        score: float
    ) -> List[str]:
        """Generate human-readable match reasons"""
        reasons = []
        
        if score > 0.8:
            reasons.append("Excellent semantic match")
        elif score > 0.6:
            reasons.append("Strong semantic match")
        
        if matched_skills:
            reasons.append(f"Matches {len(matched_skills)} required skills")
        
        if job_metadata.get("level"):
            reasons.append(f"Level: {job_metadata['level']}")
        
        return reasons
    
    def _generate_with_llm(self, requirements: Dict[str, Any]) -> str:
        """Generate job description using OpenAI LLM"""
        try:
            prompt = f"""Generate a professional job description based on these requirements:

Title: {requirements.get('title', 'Software Engineer')}
Department: {requirements.get('department', 'Engineering')}
Level: {requirements.get('level', 'Mid-level')}
Required Skills: {', '.join(requirements.get('required_skills', []))}
Key Responsibilities: {requirements.get('responsibilities', '')}

Create a comprehensive job description with:
- Job summary
- Key responsibilities
- Required qualifications
- Preferred qualifications
- Benefits (brief)"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert HR professional writing job descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating with LLM: {e}")
            return self._generate_from_template(requirements)
    
    def _generate_from_template(self, requirements: Dict[str, Any]) -> str:
        """Generate job description from template"""
        title = requirements.get('title', 'Software Engineer')
        department = requirements.get('department', 'Engineering')
        level = requirements.get('level', 'Mid-level')
        skills = ', '.join(requirements.get('required_skills', []))
        
        template = f"""# {title}

**Department:** {department}
**Level:** {level}

## Job Summary
We are looking for a {level} {title} to join our {department} team.

## Key Responsibilities
{chr(10).join(['- ' + r for r in requirements.get('responsibilities', ['Perform assigned tasks'])])}

## Required Skills
{chr(10).join(['- ' + skill for skill in requirements.get('required_skills', [])])}

## Qualifications
- Relevant experience in {department}
- {level} level expertise
- Strong communication skills"""
        
        return template
    
    def _format_jobs_for_context(self, jobs: List[Dict[str, Any]]) -> str:
        """Format jobs for LLM context"""
        formatted = []
        for job in jobs:
            formatted.append(f"""
Job: {job.get('title', 'Unknown')}
ID: {job.get('id', 'Unknown')}
Description: {job.get('description', 'N/A')}
Skills: {', '.join(job.get('required_skills', []))}
Department: {job.get('department', 'N/A')}
Level: {job.get('level', 'N/A')}
""")
        return "\n".join(formatted)

