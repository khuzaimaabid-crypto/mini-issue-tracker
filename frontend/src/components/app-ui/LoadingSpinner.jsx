/**
 * LoadingSpinner Component
 * 
 * A reusable loading spinner with three display modes:
 * - fullScreen: For page-level loading (auth, navigation)
 * - section: For content sections within a page (lists, cards)
 * - inline: For small inline content areas (stats, buttons)
 * 
 * @param {string} size - Spinner size: 'sm' (32px), 'md' (48px), 'lg' (64px)
 * @param {string} variant - Display variant: 'fullScreen', 'section', 'inline'
 * @param {string} className - Additional custom classes
 */
export const LoadingSpinner = ({ 
  size = 'md', 
  variant = 'section',
  className = '' 
}) => {
  // Spinner sizes
  const sizes = {
    sm: 'h-8 w-8',   // 32px - for inline/stats
    md: 'h-12 w-12', // 48px - default
    lg: 'h-16 w-16', // 64px - for emphasis
  };

  // Container variants
  const variants = {
    fullScreen: 'flex items-center justify-center min-h-screen',
    section: 'flex justify-center items-center h-64',
    inline: 'flex justify-center py-8',
  };

  const spinnerClasses = `animate-spin rounded-full border-b-2 border-primary-600 ${sizes[size]}`;
  const containerClasses = `${variants[variant]} ${className}`;

  return (
    <div className={containerClasses}>
      <div className={spinnerClasses} />
    </div>
  );
};