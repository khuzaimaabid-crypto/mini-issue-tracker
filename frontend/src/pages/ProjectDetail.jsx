import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { IssueList } from '../components/issues/IssueList';
import { projectService } from '../api_services/projectService';
import { LoadingSpinner } from '../components/app-ui/LoadingSpinner';
import toast from 'react-hot-toast';

export const ProjectDetail = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadProject = useCallback(async () => {

    // Validate projectId
    if (!projectId) {
      setLoading(false);
      return;
    }

    try {
      const data = await projectService.getProject(projectId);
      setProject(data);
    } catch (error) {
      toast.error('Failed to load project');
      setProject(null);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadProject();
  }, [loadProject]);

  if (loading) {
    return <LoadingSpinner variant="fullScreen" />;
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">Project not found</p>
        <Link to="/projects" className="text-primary-600 hover:text-primary-700">
          Back to Projects
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <Link to="/projects" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
          ← Back to Projects
        </Link>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900">{project.name || 'Untitled Project'}</h1>
        {project.description && (
          <p className="mt-2 text-gray-600">{project.description}</p>
        )}
      </div>

      <div>
        <IssueList />
      </div>
    </div>
  );
};