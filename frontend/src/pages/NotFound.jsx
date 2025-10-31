import { Link, useNavigate } from 'react-router-dom';

/**
 * NotFound - 404 Error Page
 * 
 * Displayed when a user navigates to a route that doesn't exist.
 * Provides options to:
 * - Go to dashboard
 * - Go back to previous page
 */
export const NotFound = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="text-center max-w-md">
        {/* 404 Number */}
        <h1 className="text-9xl font-bold text-primary-600 mb-4">404</h1>
        
        {/* Error Message */}
        <h2 className="text-3xl font-semibold text-gray-900 mb-2">
          Page not found
        </h2>
        <p className="text-gray-600 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        
        {/* Action Buttons */}
        <div className="flex gap-4 justify-center flex-wrap">
          <Link
            to="/dashboard"
            className="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
          >
            Go to Dashboard
          </Link>
          
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    </div>
  );
};
