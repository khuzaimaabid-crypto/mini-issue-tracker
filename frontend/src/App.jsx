import { AppProvider } from '@/providers/AppProvider';
import { AppRoutes } from '@/routes/AppRoutes';

/**
 * App - Main application component
 * 
 * This is the root component that combines:
 * - AppProvider: All global providers (Auth, Router, Toaster, ErrorBoundary)
 * - AppRoutes: All application routes
 */
function App() {
  return (
    <AppProvider>
      <AppRoutes />
    </AppProvider>
  );
}

export default App;