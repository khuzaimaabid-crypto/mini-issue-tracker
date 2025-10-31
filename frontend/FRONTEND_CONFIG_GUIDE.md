# Frontend Configuration Guide

## 📋 Quick Reference

### Path Aliases
Use `@/` instead of relative paths for cleaner imports:

```javascript
// ❌ Before (messy)
import { Button } from '../../../components/common/Button';
import { useAuth } from '../../hooks/useAuth';

// ✅ After (clean)
import { Button } from '@/components/common/Button';
import { useAuth } from '@/hooks/useAuth';
```

### Toast Configuration
Global toast settings are in `src/utils/toastConfig.js`:

```javascript
export const toastConfig = {
  style: {
    background: '#363636',
    color: '#fff',
  },
  duration: 4000,  // 4 seconds
  position: 'top-right',
};
```

To customize, edit this file instead of AppProvider.jsx.

## 🛠️ Build System Overview

### 1. Vite (`vite.config.js`)
- **Purpose**: Build tool and dev server
- **Runs**: `npm run dev` or `npm run build`
- **Key Features**:
  - Hot Module Replacement (instant updates)
  - Path aliases (`@/` → `src/`)
  - Docker-friendly file watching

### 2. PostCSS (`postcss.config.js`)
- **Purpose**: CSS transformation tool
- **Plugins**:
  1. Tailwind CSS (generates utility classes)
  2. Autoprefixer (adds browser prefixes)
- **Runs**: Automatically when Vite processes CSS

### 3. Tailwind (`tailwind.config.js`)
- **Purpose**: Utility-first CSS framework
- **Key Config**:
  - `content`: Files to scan for classes
  - `theme.extend`: Custom colors (primary palette)
- **Usage**: `className="bg-primary-600 text-white"`

### 4. Styles Entry (`index.css`)
- **Purpose**: Main CSS file
- **Contains**:
  - `@tailwind base` - CSS reset + base styles
  - `@tailwind components` - Component classes
  - `@tailwind utilities` - Utility classes
  - Custom utilities (e.g., `.line-clamp-2`)

## 🔄 Build Flow

```
npm run dev
    ↓
vite.config.js (starts server)
    ↓
index.html (loads main.jsx)
    ↓
main.jsx (imports index.css + App.jsx)
    ↓
    ├─→ CSS Pipeline:
    │   index.css → PostCSS → Tailwind → Autoprefixer → Browser
    │
    └─→ JS Pipeline:
        App.jsx → React components → JSX→JS → Browser
```

## 📦 Environment Variables

All environment variables are managed in the root `.env` file and passed via Docker Compose:

```yaml
# docker-compose.yml
frontend:
  environment:
    VITE_API_URL: http://localhost:8000
```

**Access in code**:
```javascript
const API_URL = import.meta.env.VITE_API_URL;
```

**Rules**:
- Must start with `VITE_` prefix
- Injected at build time (not runtime)
- Already configured via Docker ✅

## 🎨 Styling System

### Tailwind Directives in index.css

1. **@tailwind base** - Resets and base styles
   ```css
   /* Generated: */
   * { margin: 0; padding: 0; }
   h1 { font-size: 2em; }
   ```

2. **@tailwind components** - Component classes
   ```css
   /* For custom components like .btn, .card */
   ```

3. **@tailwind utilities** - All utility classes
   ```css
   .bg-blue-500 { background-color: #3b82f6; }
   .flex { display: flex; }
   ```

### Custom Layers

```css
@layer base {
  /* Custom base styles - applied to HTML elements */
  body { @apply antialiased; }
}

@layer utilities {
  /* Custom utility classes */
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    overflow: hidden;
  }
}
```

## 🚀 Development Commands

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Preview production build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── vite.config.js          # Build tool config
├── postcss.config.js       # CSS processor config
├── tailwind.config.js      # Tailwind config
├── jsconfig.json           # Path aliases for VS Code
├── index.html              # HTML entry point
├── src/
│   ├── main.jsx            # JavaScript entry point
│   ├── index.css           # CSS entry point
│   ├── App.jsx             # Root component
│   ├── components/         # Reusable UI components
│   ├── pages/              # Page components
│   ├── routes/             # Routing logic
│   ├── hooks/              # Custom React hooks
│   ├── context/            # React Context
│   ├── services/           # API services
│   ├── utils/              # Utility functions
│   └── providers/          # Global providers
```

## 🔍 Troubleshooting

### Path Aliases Not Working
1. Restart VS Code for `jsconfig.json` to take effect
2. Restart dev server (`npm run dev`)
3. Check `vite.config.js` has the alias configured

### Tailwind Classes Not Working
1. Check file is listed in `tailwind.config.js` content array
2. Restart dev server
3. Verify class name is spelled correctly

### Environment Variables Not Loading
1. Check variable starts with `VITE_` prefix
2. Restart dev server (env vars loaded at build time)
3. Verify Docker Compose passes the variable

## ✅ Recent Changes

- ✅ Removed duplicate `Layout.jsx` component
- ✅ Moved layout logic to route-level (`ProtectedLayout`, `PublicLayout`)
- ✅ Extracted toast config to `utils/toastConfig.js`
- ✅ Added path aliases (`@/` points to `src/`)
- ✅ Configured `jsconfig.json` for better VS Code intellisense
