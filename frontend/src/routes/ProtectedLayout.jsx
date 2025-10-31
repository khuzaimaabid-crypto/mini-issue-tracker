import { Outlet } from 'react-router-dom';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Navbar } from '@/components/app-ui/Navbar';

/**
 * ProtectedLayout - Layout wrapper for authenticated routes
 * 
 * Features:
 * - Reuses existing ProtectedRoute logic (auth check, loading, redirect)
 * - Renders shared layout (Navbar) for all protected pages
 * - Uses <Outlet /> to render child routes
 * 
 * Why separate from ProtectedRoute?
 * - ProtectedRoute: Handles authentication logic only
 * - ProtectedLayout: Handles authentication + shared UI (Navbar)
 * - Single Responsibility Principle
 * 
 * Usage in routes:
 * <Route element={<ProtectedLayout />}>
 *   <Route path="/dashboard" element={<Dashboard />} />
 *   <Route path="/projects" element={<Projects />} />
 * </Route>
 */
export const ProtectedLayout = () => {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <Outlet />  {/* Child routes render here */}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
};
