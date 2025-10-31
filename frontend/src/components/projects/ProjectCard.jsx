import { Link } from 'react-router-dom';
import { Button } from '../app-ui/Button';
import { DateHelper } from '../../helpers/dateHelper';

export const ProjectCard = ({ project, onDelete }) => {
  // Early return for invalid data
  if (!project || !project.id) {
    return null;
  }

  // ...existing code...

  return (
    <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow duration-200 overflow-hidden">
      <div className="p-6">
        <Link to={`/projects/${project.id}`}>
          <h3 className="text-xl font-semibold text-gray-900 hover:text-primary-600 mb-2">
            {project.name || 'Untitled Project'}
          </h3>
        </Link>
        
        {project.description && (
          <p className="text-gray-600 text-sm mb-4 line-clamp-2">
            {project.description}
          </p>
        )}
        
        <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
          <span>Created {DateHelper.formatDate(project.created_at)}</span>
        </div>
        
        <div className="flex space-x-2">
          <Link
            to={`/projects/${project.id}`}
            className="flex-1 text-center px-4 py-2 border border-primary-600 text-primary-600 rounded-md hover:bg-primary-50 transition-colors text-sm font-medium"
          >
            View Issues
          </Link>
          <Button
            onClick={() => onDelete && onDelete(project.id)} // Check onDelete exists(Safeguard)
            variant="outline_danger"
            size="md"
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
};