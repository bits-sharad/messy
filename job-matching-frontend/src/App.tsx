import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useParams, useNavigate } from 'react-router-dom';
import { Briefcase, Users, Search, Plus, ArrowLeft, Sparkles, Building2, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { projectsApi, jobsApi, aiApi } from './services/api';
import type { Project, Job, CandidateProfile, MatchResult } from './types';
import './App.css';

function Navbar() {
  return (
    <nav className="bg-slate-900 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <Briefcase className="h-8 w-8 text-blue-400" />
            <span className="text-xl font-bold">Job Matcher</span>
          </Link>
          <div className="flex items-center space-x-4">
            <Link to="/jobs" className="flex items-center space-x-1 hover:text-blue-400 transition-colors">
              <Briefcase className="h-5 w-5" />
              <span>Jobs</span>
            </Link>
            <Link to="/projects" className="flex items-center space-x-1 hover:text-blue-400 transition-colors">
              <Building2 className="h-5 w-5" />
              <span>Projects</span>
            </Link>
            <Link to="/match" className="flex items-center space-x-1 hover:text-blue-400 transition-colors">
              <Users className="h-5 w-5" />
              <span>Match</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

function HomePage() {
  const [stats, setStats] = useState({ projects: 0, jobs: 0 });
  const [recentJobs, setRecentJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projects, jobs] = await Promise.all([
          projectsApi.list().catch(() => []),
          jobsApi.list().catch(() => []),
        ]);
        setStats({ projects: projects.length, jobs: jobs.length });
        setRecentJobs(jobs.slice(0, 5));
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-slate-900 mb-4">
            AI-Powered Job Matching Platform
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Find the perfect match between candidates and jobs using advanced RAG and LLM technology.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card className="bg-white shadow-md hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">Total Projects</CardTitle>
              <Building2 className="h-5 w-5 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">{loading ? '...' : stats.projects}</div>
            </CardContent>
          </Card>
          <Card className="bg-white shadow-md hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">Total Jobs</CardTitle>
              <Briefcase className="h-5 w-5 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">{loading ? '...' : stats.jobs}</div>
            </CardContent>
          </Card>
          <Card className="bg-white shadow-md hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">AI Matching</CardTitle>
              <Sparkles className="h-5 w-5 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">Active</div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="bg-white shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Briefcase className="h-5 w-5" />
                <span>Recent Jobs</span>
              </CardTitle>
              <CardDescription>Latest job postings in the system</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8 text-slate-500">Loading...</div>
              ) : recentJobs.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  No jobs found. Create your first job posting!
                </div>
              ) : (
                <div className="space-y-4">
                  {recentJobs.map((job) => (
                    <Link
                      key={job.id}
                      to={`/jobs/${job.id}`}
                      className="block p-4 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-slate-50 transition-all"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold text-slate-900">{job.title}</h3>
                          <p className="text-sm text-slate-500">{job.department || 'No department'}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={job.status === 'published' ? 'default' : 'secondary'}>
                            {job.status}
                          </Badge>
                          <ChevronRight className="h-4 w-4 text-slate-400" />
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
              <div className="mt-4">
                <Link to="/jobs">
                  <Button variant="outline" className="w-full">View All Jobs</Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Sparkles className="h-5 w-5" />
                <span>Quick Actions</span>
              </CardTitle>
              <CardDescription>Get started with common tasks</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Link to="/match">
                <Button className="w-full justify-start" variant="outline">
                  <Users className="h-4 w-4 mr-2" />
                  Match Candidate to Jobs
                </Button>
              </Link>
              <Link to="/jobs/search">
                <Button className="w-full justify-start" variant="outline">
                  <Search className="h-4 w-4 mr-2" />
                  Search Jobs
                </Button>
              </Link>
              <Link to="/projects/new">
                <Button className="w-full justify-start" variant="outline">
                  <Plus className="h-4 w-4 mr-2" />
                  Create New Project
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function JobsListPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const data = await jobsApi.list();
        setJobs(data);
      } catch (error) {
        console.error('Error fetching jobs:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      const data = await jobsApi.list();
      setJobs(data);
      return;
    }
    setLoading(true);
    try {
      const results = await jobsApi.search(searchQuery);
      setJobs(results);
    } catch (error) {
      console.error('Error searching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredJobs = jobs.filter(
    (job) =>
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.job_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (job.department && job.department.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Jobs</h1>
            <p className="text-slate-600">Browse and manage job postings</p>
          </div>
          <Button onClick={() => navigate('/projects')}>
            <Plus className="h-4 w-4 mr-2" />
            Create Job
          </Button>
        </div>

        <div className="flex items-center space-x-4 mb-6">
          <div className="flex-1">
            <Input
              placeholder="Search jobs by title, code, or department..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <Button onClick={handleSearch}>
            <Search className="h-4 w-4 mr-2" />
            Search
          </Button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="text-slate-500">Loading jobs...</div>
          </div>
        ) : filteredJobs.length === 0 ? (
          <Card className="bg-white">
            <CardContent className="text-center py-12">
              <Briefcase className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">No jobs found</h3>
              <p className="text-slate-500 mb-4">
                {searchQuery ? 'Try a different search term' : 'Create your first job posting to get started'}
              </p>
              <Button onClick={() => navigate('/projects')}>
                <Plus className="h-4 w-4 mr-2" />
                Create Job
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredJobs.map((job) => (
              <Card key={job.id} className="bg-white hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate(`/jobs/${job.id}`)}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{job.title}</CardTitle>
                      <CardDescription>{job.job_code}</CardDescription>
                    </div>
                    <Badge variant={job.status === 'published' ? 'default' : job.status === 'draft' ? 'secondary' : 'destructive'}>
                      {job.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {job.department && (
                      <div className="flex items-center text-sm text-slate-600">
                        <Building2 className="h-4 w-4 mr-2" />
                        {job.department}
                      </div>
                    )}
                    {job.level && (
                      <div className="text-sm text-slate-600">
                        Level: <span className="capitalize">{job.level}</span>
                      </div>
                    )}
                    {job.required_skills && job.required_skills.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {job.required_skills.slice(0, 3).map((skill, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                        {job.required_skills.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{job.required_skills.length - 3} more
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function JobDetailPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [askingQuestion, setAskingQuestion] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchJob = async () => {
      if (!jobId) return;
      try {
        const data = await jobsApi.get(jobId);
        setJob(data);
      } catch (error) {
        console.error('Error fetching job:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchJob();
  }, [jobId]);

  const handleAskQuestion = async () => {
    if (!question.trim() || !jobId) return;
    setAskingQuestion(true);
    try {
      const response = await aiApi.askJobQuestion(jobId, question);
      setAnswer(response.answer);
    } catch (error) {
      console.error('Error asking question:', error);
      setAnswer('Sorry, I could not answer that question. Please try again.');
    } finally {
      setAskingQuestion(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-500">Loading job details...</div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Card className="bg-white p-8 text-center">
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Job not found</h2>
          <p className="text-slate-500 mb-4">The job you're looking for doesn't exist.</p>
          <Button onClick={() => navigate('/jobs')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Jobs
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Button variant="ghost" onClick={() => navigate('/jobs')} className="mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Jobs
        </Button>

        <Card className="bg-white mb-6">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-2xl">{job.title}</CardTitle>
                <CardDescription className="text-lg">{job.job_code}</CardDescription>
              </div>
              <Badge variant={job.status === 'published' ? 'default' : job.status === 'draft' ? 'secondary' : 'destructive'} className="text-sm">
                {job.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              {job.department && (
                <div>
                  <Label className="text-slate-500">Department</Label>
                  <p className="font-medium">{job.department}</p>
                </div>
              )}
              {job.level && (
                <div>
                  <Label className="text-slate-500">Level</Label>
                  <p className="font-medium capitalize">{job.level}</p>
                </div>
              )}
            </div>

            {job.description && (
              <div>
                <Label className="text-slate-500">Description</Label>
                <p className="mt-1 text-slate-700 whitespace-pre-wrap">{job.description}</p>
              </div>
            )}

            {job.required_skills && job.required_skills.length > 0 && (
              <div>
                <Label className="text-slate-500">Required Skills</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {job.required_skills.map((skill, index) => (
                    <Badge key={index} variant="secondary">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {job.responsibilities && job.responsibilities.length > 0 && (
              <div>
                <Label className="text-slate-500">Responsibilities</Label>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  {job.responsibilities.map((resp, index) => (
                    <li key={index} className="text-slate-700">{resp}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 text-sm text-slate-500">
              <div>Created: {new Date(job.created_at).toLocaleDateString()}</div>
              <div>Updated: {new Date(job.updated_at).toLocaleDateString()}</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-purple-500" />
              <span>Ask AI About This Job</span>
            </CardTitle>
            <CardDescription>Use AI to get insights about this job posting</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex space-x-2">
              <Input
                placeholder="Ask a question about this job..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAskQuestion()}
              />
              <Button onClick={handleAskQuestion} disabled={askingQuestion}>
                {askingQuestion ? 'Asking...' : 'Ask'}
              </Button>
            </div>
            {answer && (
              <div className="p-4 bg-slate-50 rounded-lg">
                <Label className="text-slate-500 text-sm">AI Response</Label>
                <p className="mt-1 text-slate-700">{answer}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newProject, setNewProject] = useState<{ name: string; description: string; status: 'active' | 'inactive' | 'archived' }>({ name: '', description: '', status: 'active' });
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();

  const fetchProjects = async () => {
    try {
      const data = await projectsApi.list();
      setProjects(data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async () => {
    if (!newProject.name.trim()) return;
    setCreating(true);
    try {
      await projectsApi.create(newProject);
      setIsCreateDialogOpen(false);
      setNewProject({ name: '', description: '', status: 'active' });
      fetchProjects();
    } catch (error) {
      console.error('Error creating project:', error);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Projects</h1>
            <p className="text-slate-600">Manage your recruitment projects</p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Project
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Project</DialogTitle>
                <DialogDescription>Add a new recruitment project to organize your jobs.</DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <Label htmlFor="name">Project Name</Label>
                  <Input
                    id="name"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    placeholder="e.g., Q1 2026 Hiring"
                  />
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    placeholder="Describe the project..."
                  />
                </div>
                <div>
                  <Label htmlFor="status">Status</Label>
                  <Select value={newProject.status} onValueChange={(value: 'active' | 'inactive' | 'archived') => setNewProject({ ...newProject, status: value })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="inactive">Inactive</SelectItem>
                      <SelectItem value="archived">Archived</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={handleCreateProject} disabled={creating} className="w-full">
                  {creating ? 'Creating...' : 'Create Project'}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="text-slate-500">Loading projects...</div>
          </div>
        ) : projects.length === 0 ? (
          <Card className="bg-white">
            <CardContent className="text-center py-12">
              <Building2 className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">No projects yet</h3>
              <p className="text-slate-500 mb-4">Create your first project to start organizing jobs</p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Project
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <Card key={project.id} className="bg-white hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate(`/projects/${project.id}`)}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{project.name}</CardTitle>
                      <CardDescription>{project.job_count || 0} jobs</CardDescription>
                    </div>
                    <Badge variant={project.status === 'active' ? 'default' : project.status === 'inactive' ? 'secondary' : 'destructive'}>
                      {project.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  {project.description && (
                    <p className="text-sm text-slate-600 line-clamp-2">{project.description}</p>
                  )}
                  <div className="mt-4 text-xs text-slate-500">
                    Created: {new Date(project.created_at).toLocaleDateString()}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateJobDialogOpen, setIsCreateJobDialogOpen] = useState(false);
    const [newJob, setNewJob] = useState<{
      title: string;
      description: string;
      job_code: string;
      status: 'draft' | 'published' | 'closed';
      department: string;
      level: '' | 'entry' | 'mid' | 'senior' | 'lead';
      required_skills: string;
      responsibilities: string;
    }>({
      title: '',
      description: '',
      job_code: '',
      status: 'draft',
      department: '',
      level: '',
      required_skills: '',
      responsibilities: '',
    });
  const [creating, setCreating] = useState(false);
  const [generatingDescription, setGeneratingDescription] = useState(false);
  const navigate = useNavigate();

  const fetchData = async () => {
    if (!projectId) return;
    try {
      const [projectData, jobsData] = await Promise.all([
        projectsApi.get(projectId),
        jobsApi.list(projectId),
      ]);
      setProject(projectData);
      setJobs(jobsData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

  const handleCreateJob = async () => {
    if (!newJob.title.trim() || !newJob.job_code.trim() || !projectId) return;
    setCreating(true);
    try {
      await jobsApi.create(projectId, {
        title: newJob.title,
        description: newJob.description || undefined,
        job_code: newJob.job_code,
        status: newJob.status,
        department: newJob.department || undefined,
        level: newJob.level || undefined,
        required_skills: newJob.required_skills ? newJob.required_skills.split(',').map((s) => s.trim()) : undefined,
        responsibilities: newJob.responsibilities ? newJob.responsibilities.split('\n').filter((r) => r.trim()) : undefined,
      });
      setIsCreateJobDialogOpen(false);
      setNewJob({
        title: '',
        description: '',
        job_code: '',
        status: 'draft',
        department: '',
        level: '',
        required_skills: '',
        responsibilities: '',
      });
      fetchData();
    } catch (error) {
      console.error('Error creating job:', error);
    } finally {
      setCreating(false);
    }
  };

  const handleGenerateDescription = async () => {
    if (!newJob.title.trim()) return;
    setGeneratingDescription(true);
    try {
      const response = await aiApi.generateJobDescription(
        newJob.title,
        newJob.department || undefined,
        newJob.level || undefined,
        newJob.required_skills ? newJob.required_skills.split(',').map((s) => s.trim()) : undefined,
        newJob.responsibilities ? newJob.responsibilities.split('\n').filter((r) => r.trim()) : undefined
      );
      setNewJob({ ...newJob, description: response.description });
    } catch (error) {
      console.error('Error generating description:', error);
    } finally {
      setGeneratingDescription(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-500">Loading project...</div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Card className="bg-white p-8 text-center">
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Project not found</h2>
          <p className="text-slate-500 mb-4">The project you're looking for doesn't exist.</p>
          <Button onClick={() => navigate('/projects')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Projects
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Button variant="ghost" onClick={() => navigate('/projects')} className="mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Projects
        </Button>

        <Card className="bg-white mb-6">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-2xl">{project.name}</CardTitle>
                <CardDescription>{project.job_count || 0} jobs in this project</CardDescription>
              </div>
              <Badge variant={project.status === 'active' ? 'default' : project.status === 'inactive' ? 'secondary' : 'destructive'}>
                {project.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {project.description && (
              <p className="text-slate-700 mb-4">{project.description}</p>
            )}
            <div className="text-sm text-slate-500">
              Created: {new Date(project.created_at).toLocaleDateString()}
            </div>
          </CardContent>
        </Card>

        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-slate-900">Jobs</h2>
          <Dialog open={isCreateJobDialogOpen} onOpenChange={setIsCreateJobDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Job
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create New Job</DialogTitle>
                <DialogDescription>Add a new job posting to this project.</DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="job-title">Job Title *</Label>
                    <Input
                      id="job-title"
                      value={newJob.title}
                      onChange={(e) => setNewJob({ ...newJob, title: e.target.value })}
                      placeholder="e.g., Senior Software Engineer"
                    />
                  </div>
                  <div>
                    <Label htmlFor="job-code">Job Code *</Label>
                    <Input
                      id="job-code"
                      value={newJob.job_code}
                      onChange={(e) => setNewJob({ ...newJob, job_code: e.target.value })}
                      placeholder="e.g., ENG-001"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="department">Department</Label>
                    <Input
                      id="department"
                      value={newJob.department}
                      onChange={(e) => setNewJob({ ...newJob, department: e.target.value })}
                      placeholder="e.g., Engineering"
                    />
                  </div>
                  <div>
                    <Label htmlFor="level">Level</Label>
                    <Select value={newJob.level} onValueChange={(value: '' | 'entry' | 'mid' | 'senior' | 'lead') => setNewJob({ ...newJob, level: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select level" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="entry">Entry</SelectItem>
                        <SelectItem value="mid">Mid</SelectItem>
                        <SelectItem value="senior">Senior</SelectItem>
                        <SelectItem value="lead">Lead</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="status">Status</Label>
                  <Select value={newJob.status} onValueChange={(value: 'draft' | 'published' | 'closed') => setNewJob({ ...newJob, status: value })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="published">Published</SelectItem>
                      <SelectItem value="closed">Closed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="skills">Required Skills (comma-separated)</Label>
                  <Input
                    id="skills"
                    value={newJob.required_skills}
                    onChange={(e) => setNewJob({ ...newJob, required_skills: e.target.value })}
                    placeholder="e.g., Python, FastAPI, MongoDB"
                  />
                </div>
                <div>
                  <Label htmlFor="responsibilities">Responsibilities (one per line)</Label>
                  <Textarea
                    id="responsibilities"
                    value={newJob.responsibilities}
                    onChange={(e) => setNewJob({ ...newJob, responsibilities: e.target.value })}
                    placeholder="Design and develop APIs&#10;Mentor junior developers&#10;Code reviews"
                    rows={3}
                  />
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Label htmlFor="description">Description</Label>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleGenerateDescription}
                      disabled={generatingDescription || !newJob.title.trim()}
                    >
                      <Sparkles className="h-4 w-4 mr-1" />
                      {generatingDescription ? 'Generating...' : 'Generate with AI'}
                    </Button>
                  </div>
                  <Textarea
                    id="description"
                    value={newJob.description}
                    onChange={(e) => setNewJob({ ...newJob, description: e.target.value })}
                    placeholder="Job description..."
                    rows={6}
                  />
                </div>
                <Button onClick={handleCreateJob} disabled={creating} className="w-full">
                  {creating ? 'Creating...' : 'Create Job'}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {jobs.length === 0 ? (
          <Card className="bg-white">
            <CardContent className="text-center py-12">
              <Briefcase className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">No jobs in this project</h3>
              <p className="text-slate-500 mb-4">Add your first job posting to get started</p>
              <Button onClick={() => setIsCreateJobDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Job
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {jobs.map((job) => (
              <Card key={job.id} className="bg-white hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate(`/jobs/${job.id}`)}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{job.title}</CardTitle>
                      <CardDescription>{job.job_code}</CardDescription>
                    </div>
                    <Badge variant={job.status === 'published' ? 'default' : job.status === 'draft' ? 'secondary' : 'destructive'}>
                      {job.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {job.department && (
                      <div className="text-sm text-slate-600">
                        <Building2 className="h-4 w-4 inline mr-1" />
                        {job.department}
                      </div>
                    )}
                    {job.required_skills && job.required_skills.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {job.required_skills.slice(0, 3).map((skill, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function CandidateMatchPage() {
  const [candidateProfile, setCandidateProfile] = useState<CandidateProfile>({
    skills: [],
    experience_summary: '',
    education: '',
    desired_role: '',
    years_of_experience: undefined,
    location: '',
  });
  const [skillsInput, setSkillsInput] = useState('');
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const navigate = useNavigate();

  const handleMatch = async () => {
    const skills = skillsInput.split(',').map((s) => s.trim()).filter((s) => s);
    if (skills.length === 0) return;

    setLoading(true);
    setHasSearched(true);
    try {
      const profile: CandidateProfile = {
        ...candidateProfile,
        skills,
      };
      const results = await aiApi.matchCandidate(profile);
      setMatches(results);
    } catch (error) {
      console.error('Error matching candidate:', error);
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Candidate Job Matching</h1>
          <p className="text-slate-600">Find the best job matches for a candidate using AI</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="bg-white">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>Candidate Profile</span>
              </CardTitle>
              <CardDescription>Enter the candidate's information to find matching jobs</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="skills">Skills * (comma-separated)</Label>
                <Input
                  id="skills"
                  value={skillsInput}
                  onChange={(e) => setSkillsInput(e.target.value)}
                  placeholder="e.g., Python, FastAPI, MongoDB, Docker"
                />
              </div>
              <div>
                <Label htmlFor="desired-role">Desired Role</Label>
                <Input
                  id="desired-role"
                  value={candidateProfile.desired_role}
                  onChange={(e) => setCandidateProfile({ ...candidateProfile, desired_role: e.target.value })}
                  placeholder="e.g., Senior Software Engineer"
                />
              </div>
              <div>
                <Label htmlFor="experience">Years of Experience</Label>
                <Input
                  id="experience"
                  type="number"
                  value={candidateProfile.years_of_experience || ''}
                  onChange={(e) => setCandidateProfile({ ...candidateProfile, years_of_experience: e.target.value ? parseInt(e.target.value) : undefined })}
                  placeholder="e.g., 5"
                />
              </div>
              <div>
                <Label htmlFor="education">Education</Label>
                <Input
                  id="education"
                  value={candidateProfile.education}
                  onChange={(e) => setCandidateProfile({ ...candidateProfile, education: e.target.value })}
                  placeholder="e.g., BS Computer Science"
                />
              </div>
              <div>
                <Label htmlFor="location">Preferred Location</Label>
                <Input
                  id="location"
                  value={candidateProfile.location}
                  onChange={(e) => setCandidateProfile({ ...candidateProfile, location: e.target.value })}
                  placeholder="e.g., Remote, New York"
                />
              </div>
              <div>
                <Label htmlFor="experience-summary">Experience Summary</Label>
                <Textarea
                  id="experience-summary"
                  value={candidateProfile.experience_summary}
                  onChange={(e) => setCandidateProfile({ ...candidateProfile, experience_summary: e.target.value })}
                  placeholder="Brief summary of work experience..."
                  rows={4}
                />
              </div>
              <Button onClick={handleMatch} disabled={loading || !skillsInput.trim()} className="w-full">
                <Sparkles className="h-4 w-4 mr-2" />
                {loading ? 'Finding Matches...' : 'Find Matching Jobs'}
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-white">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Briefcase className="h-5 w-5" />
                <span>Matching Jobs</span>
              </CardTitle>
              <CardDescription>
                {hasSearched
                  ? `Found ${matches.length} matching jobs`
                  : 'Enter candidate profile to see matches'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-12">
                  <div className="text-slate-500">Analyzing candidate profile...</div>
                </div>
              ) : !hasSearched ? (
                <div className="text-center py-12">
                  <Users className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                  <p className="text-slate-500">Enter candidate skills and click "Find Matching Jobs"</p>
                </div>
              ) : matches.length === 0 ? (
                <div className="text-center py-12">
                  <Briefcase className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                  <p className="text-slate-500">No matching jobs found. Try different skills or check if jobs are indexed.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {matches.map((match, index) => (
                    <div
                      key={match.job_id}
                      className="p-4 border rounded-lg hover:border-blue-300 hover:bg-slate-50 transition-all cursor-pointer"
                      onClick={() => navigate(`/jobs/${match.job_id}`)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="font-semibold text-slate-900">{match.job_title}</h3>
                          <p className="text-sm text-slate-500">Match #{index + 1}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-blue-600">
                            {Math.round(match.match_score * 100)}%
                          </div>
                          <Progress value={match.match_score * 100} className="w-20 h-2" />
                        </div>
                      </div>
                      {match.matched_skills.length > 0 && (
                        <div className="mb-2">
                          <span className="text-xs text-slate-500">Matched Skills: </span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {match.matched_skills.map((skill, i) => (
                              <Badge key={i} variant="default" className="text-xs bg-green-100 text-green-800">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      {match.missing_skills.length > 0 && (
                        <div className="mb-2">
                          <span className="text-xs text-slate-500">Missing Skills: </span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {match.missing_skills.slice(0, 3).map((skill, i) => (
                              <Badge key={i} variant="outline" className="text-xs text-orange-600 border-orange-300">
                                {skill}
                              </Badge>
                            ))}
                            {match.missing_skills.length > 3 && (
                              <Badge variant="outline" className="text-xs">
                                +{match.missing_skills.length - 3} more
                              </Badge>
                            )}
                          </div>
                        </div>
                      )}
                      {match.match_reasons.length > 0 && (
                        <div className="text-xs text-slate-600 mt-2">
                          {match.match_reasons.slice(0, 2).join(' | ')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function JobSearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setHasSearched(true);
    try {
      const jobs = await jobsApi.search(query);
      setResults(jobs);
    } catch (error) {
      console.error('Error searching jobs:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Search Jobs</h1>
          <p className="text-slate-600">Search for jobs by title, description, or job code</p>
        </div>

        <Card className="bg-white mb-6">
          <CardContent className="pt-6">
            <div className="flex space-x-4">
              <Input
                placeholder="Search jobs..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="flex-1"
              />
              <Button onClick={handleSearch} disabled={loading}>
                <Search className="h-4 w-4 mr-2" />
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {loading ? (
          <div className="text-center py-12">
            <div className="text-slate-500">Searching...</div>
          </div>
        ) : !hasSearched ? (
          <Card className="bg-white">
            <CardContent className="text-center py-12">
              <Search className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <p className="text-slate-500">Enter a search term to find jobs</p>
            </CardContent>
          </Card>
        ) : results.length === 0 ? (
          <Card className="bg-white">
            <CardContent className="text-center py-12">
              <Briefcase className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">No results found</h3>
              <p className="text-slate-500">Try a different search term</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {results.map((job) => (
              <Card key={job.id} className="bg-white hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate(`/jobs/${job.id}`)}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900">{job.title}</h3>
                      <p className="text-sm text-slate-500">{job.job_code}</p>
                      {job.description && (
                        <p className="text-sm text-slate-600 mt-2 line-clamp-2">{job.description}</p>
                      )}
                      {job.required_skills && job.required_skills.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {job.required_skills.slice(0, 5).map((skill, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                    <Badge variant={job.status === 'published' ? 'default' : 'secondary'}>
                      {job.status}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/jobs" element={<JobsListPage />} />
          <Route path="/jobs/search" element={<JobSearchPage />} />
          <Route path="/jobs/:jobId" element={<JobDetailPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/projects/new" element={<ProjectsPage />} />
          <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
          <Route path="/match" element={<CandidateMatchPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
