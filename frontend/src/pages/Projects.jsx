import { ProjectList } from '../components/projects/ProjectList';

export const Projects = () => {
  return (
    <div className="space-y-6">
      {/* Projects Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900">All Projects</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage and organize all your projects in one place.
        </p>
      </div>

      {/* Project List with potential filters/search */}
      <ProjectList />
    </div>
  );
};