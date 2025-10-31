import { ProjectList } from '../components/projects/ProjectList';
import { StatsCard } from '../components/app-ui/StatsCard';
import { useProjects } from '../hooks/useProjects';
import { LoadingSpinner } from '../components/app-ui/LoadingSpinner';
import { useEffect, useState } from 'react';
import api from '../api';

export const Dashboard = () => {
  const { projects, loading: projectsLoading } = useProjects();
  const [allIssues, setAllIssues] = useState([]);
  const [issuesLoading, setIssuesLoading] = useState(true);

  useEffect(() => {
    const fetchAllIssues = async () => {
      if (!projects || projects.length === 0) {
        setAllIssues([]);
        setIssuesLoading(false);
        return;
      }

      try {
        setIssuesLoading(true);
        const issuesPromises = projects.map(project =>
          api.get(`/projects/${project.id}/issues`).then(res => res.data)
        );
        const issuesArrays = await Promise.all(issuesPromises);
        const flattenedIssues = issuesArrays.flat();
        setAllIssues(flattenedIssues);
      } catch (error) {
        if (import.meta.env.DEV) {
          console.error('Error fetching issues:', error);
        }
        setAllIssues([]);
      } finally {
        setIssuesLoading(false);
      }
    };

    fetchAllIssues();
  }, [projects]);

  const totalProjects = projects.length;
  const openIssues = allIssues.filter(issue => issue.status === 'Open').length;
  const inProgressIssues = allIssues.filter(issue => issue.status === 'In Progress').length;
  const closedIssues = allIssues.filter(issue => issue.status === 'Closed').length;

  const isLoading = projectsLoading || issuesLoading;

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back! Here's an overview of your projects and issues.
        </p>
      </div>

        {isLoading ? (
          <LoadingSpinner variant="inline" size="sm" />
        ) : (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <StatsCard
              title="Total Projects"
              value={totalProjects}
              color="blue"
              icon={
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
              }
            />
            <StatsCard
              title="Open Issues"
              value={openIssues}
              color="yellow"
              icon={
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              }
            />
            <StatsCard
              title="In Progress"
              value={inProgressIssues}
              color="purple"
              icon={
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              }
            />
            <StatsCard
              title="Closed Issues"
              value={closedIssues}
              color="green"
              icon={
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            />
          </div>
        )}

        {!isLoading && totalProjects === 0 && (
          <div className="bg-white shadow rounded-lg p-12 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No projects yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating your first project to track issues.
            </p>
          </div>
        )}

      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Projects</h2>
        <ProjectList />
      </div>
    </div>
  );
};