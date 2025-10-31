import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

/**
 * PublicLayout - Layout wrapper for public routes (login, register)
 * 
 * Features:
 * - Redirects authenticated users to dashboard
 * - No navbar (clean login/register pages)
 * - Uses <Outlet /> to render child routes
 * 
 * Usage in routes:
 * <Route element={<PublicLayout />}>
 *   <Route path="/login" element={<Login />} />
 *   <Route path="/register" element={<Register />} />
 * </Route>
 */
export const PublicLayout = () => {
  const { isAuthenticated } = useAuth();
  
  // Redirect to dashboard if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  // Render child routes (Login, Register)
  return (
    <div className="min-h-screen bg-gray-50">
      <Outlet />  {/* Child routes render here */}
    </div>
  );
};
