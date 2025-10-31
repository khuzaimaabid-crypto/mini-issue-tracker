// Tool that transforms CSS with JavaScript plugins
// Runs BEFORE the CSS reaches the browser
export default {
// PostCSS plugins for Tailwind CSS and Autoprefixer 
// which provide necessary CSS processing
  plugins: {
    tailwindcss: {},  // adds tailwind classes
    autoprefixer: {},  // adds vendor prefixes for cross-browser compatibility
  },
}