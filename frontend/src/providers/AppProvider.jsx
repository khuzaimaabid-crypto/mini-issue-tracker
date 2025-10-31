import { BrowserRouter as Router } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from '@/context/AuthContext';
import { ErrorBoundary } from '@/components/app-ui/errors/ErrorBoundary';
import { toastConfig } from '@/config/toastConfig';

/**
 * AppProvider - Wraps the entire application with global providers
 * 
 * This component centralizes all global context providers and configurations:
 * - ErrorBoundary: Catches and handles React errors gracefully
 * - AuthProvider: Manages authentication state across the app
 * - Router: Enables client-side routing
 * - Toaster: Configures global toast notifications
 * 
 * Benefits:
 * - Easy to add new global providers
 * - Keeps App.jsx clean and focused
 * - Providers are composed in the correct order
 */
export const AppProvider = ({ children }) => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <Toaster 
            position={toastConfig.position}
            toastOptions={{
              duration: toastConfig.duration,
              style: toastConfig.style,
              iconTheme: toastConfig.iconTheme,
            }}
          />
          {children}
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
};
