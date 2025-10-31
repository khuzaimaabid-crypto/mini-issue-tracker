import { useState, useEffect, useCallback } from 'react';
import { projectService } from '../api_services/projectService';

export const useProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true);
      const data = await projectService.getProjects();
      setProjects(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const createProject = async (projectData) => {
    const newProject = await projectService.createProject(projectData);
    setProjects([...projects, newProject]);
    return newProject;
  };

  const updateProject = async (projectId, projectData) => {
    const updated = await projectService.updateProject(projectId, projectData);
    setProjects(projects.map((p) => (p.id === projectId ? updated : p)));
    return updated;
  };

  const deleteProject = async (projectId) => {
    await projectService.deleteProject(projectId);
    setProjects(projects.filter((p) => p.id !== projectId));
  };

  return {
    projects,
    loading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
  };
};