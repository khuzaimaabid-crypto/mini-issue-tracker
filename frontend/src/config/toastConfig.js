/**
 * Toast Notification Configuration
 * 
 * Centralized configuration for react-hot-toast.
 * Used in AppProvider to configure global toast settings.
 * 
 * Customize:
 * - style: Toast appearance (colors, fonts, etc.)
 * - duration: How long toasts stay visible (ms)
 * - position: Where toasts appear on screen
 * - icon theme: Icon colors
 */
export const toastConfig = {
  // Toast appearance
  style: {
    background: '#363636',  // Dark background
    color: '#fff',          // White text
  },
  
  // How long toasts stay visible (milliseconds)
  duration: 4000,  // 4 seconds
  
  // Default position (can be overridden per toast)
  // Options: 'top-left', 'top-center', 'top-right', 
  //          'bottom-left', 'bottom-center', 'bottom-right'
  position: 'top-right',
  
  // Icon theme
  iconTheme: {
    primary: '#0284c7',  // primary-600
    secondary: '#fff',
  },
};
