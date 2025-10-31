import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedLayout } from '@/routes/ProtectedLayout';
import { PublicLayout } from '@/routes/PublicLayout';
import { Login } from '@/pages/Login';
import { Register } from '@/pages/Register';
import { Dashboard } from '@/pages/Dashboard';
import { Projects } from '@/pages/Projects';
import { ProjectDetail } from '@/pages/ProjectDetail';
import { NotFound } from '@/pages/NotFound';

/**
 * AppRoutes - Defines all application routes
 * 
 * Route Structure:
 * - Public Routes (PublicLayout): /login, /register
 *   → Redirects to /dashboard if already authenticated
 * 
 * - Protected Routes (ProtectedLayout): /dashboard, /projects, /projects/:id
 *   → Redirects to /login if NOT authenticated
 *   → Shared Navbar layout for all protected pages
 * 
 * - Root: / → redirects to /dashboard
 * - 404: * → NotFound page
 */
export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes - redirect to dashboard if already authenticated */}
      <Route element={<PublicLayout />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>
      
      {/* Protected Routes - redirect to login if NOT authenticated */}
      <Route element={<ProtectedLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/projects/:projectId" element={<ProjectDetail />} />
      </Route>
      
      {/* Root redirect */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      
      {/* 404 Not Found */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};
