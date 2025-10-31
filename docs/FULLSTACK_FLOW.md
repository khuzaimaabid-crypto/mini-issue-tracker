# Full-Stack Application Flow

Complete end-to-end flow showing how Frontend, Backend, and Database interact.

## 📋 Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Complete User Journey: Login](#2-complete-user-journey-login)
3. [Complete User Journey: Create Project](#3-complete-user-journey-create-project)
4. [Complete User Journey: View Projects](#4-complete-user-journey-view-projects)
5. [Docker Networking](#5-docker-networking)
6. [Environment Variables Flow](#6-environment-variables-flow)
7. [Error Handling Flow](#7-error-handling-flow)

---

## 1. System Architecture

### Component Overview

```
┌──────────────────────────────────────────────────────────┐
│                    YOUR COMPUTER (Host)                   │
│                                                           │
│  ┌────────────────┐                                      │
│  │   Browser      │                                      │
│  │                │                                      │
│  │ localhost:5173 │                                      │
│  └────────┬───────┘                                      │
│           │                                               │
│           │ HTTP Requests                                 │
│           ↓                                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │           Docker Network                             │ │
│  │                                                      │ │
│  │  ┌──────────────┐   ┌──────────────┐   ┌─────────┐│ │
│  │  │  Frontend    │   │  Backend     │   │Database ││ │
│  │  │  Container   │   │  Container   │   │Container││ │
│  │  │              │   │              │   │         ││ │
│  │  │  Vite        │   │  Uvicorn     │   │ Postgres││ │
│  │  │  Port: 5173  │   │  Port: 8000  │   │Port:5432││ │
│  │  │              │   │              │   │         ││ │
│  │  │  React App   │──>│  FastAPI App │──>│  Tables ││ │
│  │  │  + Tailwind  │   │  + SQLAlchemy│   │  + Data ││ │
│  │  └──────────────┘   └──────────────┘   └─────────┘│ │
│  │                                                      │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Port Mapping

| Service | Container Port | Host Port | URL |
|---------|----------------|-----------|-----|
| Frontend | 5173 | 5173 | http://localhost:5173 |
| Backend | 8000 | 8000 | http://localhost:8000 |
| Database | 5432 | 5432 | localhost:5432 (internal) |

---

## 2. Complete User Journey: Login

### Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: User Opens Application                          │
└─────────────────────────────────────────────────────────┘

User types in browser: http://localhost:5173
     ↓
Browser → Docker → Frontend Container (Vite)
     ↓
Vite serves: index.html
     ↓
Browser loads: main.jsx
     ↓
main.jsx imports:
  - App.jsx
  - index.css
     ↓
CSS Pipeline (Frontend):
  index.css → PostCSS → Tailwind → Autoprefixer → Browser
     ↓
JS Pipeline (Frontend):
  App.jsx → AppProvider → AppRoutes
     ↓
AppRoutes checks: isAuthenticated?
     ↓
AuthContext: user = null, isAuthenticated = false
     ↓
PublicLayout activates
     ↓
Renders: <Login /> component
     ↓
User sees: Login page ✅

┌─────────────────────────────────────────────────────────┐
│ STEP 2: User Enters Credentials                         │
└─────────────────────────────────────────────────────────┘

User types:
  Email: user@example.com
  Password: password123
     ↓
React state updates (controlled inputs)
     ↓
User clicks "Login" button
     ↓
Login component: handleSubmit()
     ↓
```

```javascript
// Frontend: src/pages/Login.jsx
const handleSubmit = async (e) => {
  e.preventDefault();
  setLoading(true);
  
  try {
    // Call auth service
    const data = await login(email, password);
    navigate('/dashboard');
  } catch (error) {
    toast.error('Login failed');
  } finally {
    setLoading(false);
  }
};
```

```
     ↓
Calls: login() from AuthContext
     ↓
```

```javascript
// Frontend: src/context/AuthContext.jsx
const login = async (email, password) => {
  // Call API service
  const data = await authService.login(email, password);
  
  // Store token
  setUser({ token: data.access_token });
  
  return data;
};
```

```
     ↓
Calls: authService.login()
     ↓
```

```javascript
// Frontend: src/services/authService.js
const login = async (email, password) => {
  // Axios makes HTTP request
  const response = await api.post('/auth/login', {
    username: email,  // OAuth2 uses "username" field
    password: password
  }, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
  
  // Store token in localStorage
  localStorage.setItem('token', response.data.access_token);
  
  return response.data;
};
```

```
     ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: HTTP Request Sent                               │
└─────────────────────────────────────────────────────────┘

POST http://localhost:8000/auth/login
Headers:
  Content-Type: application/x-www-form-urlencoded
Body (URL-encoded):
  username=user@example.com&password=password123
     ↓
Browser → Docker Network → Backend Container (Uvicorn)
     ↓
Backend receives request
     ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: Backend Processing                              │
└─────────────────────────────────────────────────────────┘

CORS Middleware:
  Check origin: http://localhost:5173
  Allowed: ["http://localhost:5173"]
  Result: ✅ Allowed
  Add header: Access-Control-Allow-Origin: http://localhost:5173
     ↓
FastAPI Router:
  Match route: POST /auth/login
  Found in: app/routers/auth.py
     ↓
Dependency Injection:
  1. get_db() → Create database session
  2. OAuth2PasswordRequestForm → Parse form data
     ↓
Route Handler:
```

```python
# Backend: app/routers/auth.py
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return auth_service.login(
        db=db,
        email=form_data.username,
        password=form_data.password
    )
```

```
     ↓
Service Layer:
```

```python
# Backend: app/services/auth.py
def login(self, db: Session, email: str, password: str):
    # 1. Get user from database
    user = user_repository.get_by_email(db, email)
    
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # 2. Verify password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    
    # 3. Create JWT token
    access_token = create_access_token(
        data={"sub": user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
```

```
     ↓
Repository Layer:
```

```python
# Backend: app/repositories/user.py
def get_by_email(self, db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
```

```
     ↓
SQLAlchemy → SQL:
```

```sql
SELECT users.id, users.name, users.email, users.hashed_password
FROM users
WHERE users.email = 'user@example.com'
LIMIT 1;
```

```
     ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 5: Database Query                                  │
└─────────────────────────────────────────────────────────┘

SQLAlchemy → psycopg2 (database driver)
     ↓
psycopg2 → Docker Network → Database Container (PostgreSQL)
     ↓
PostgreSQL executes query:
  Table: users
  Filter: email = 'user@example.com'
  Result:
    id: 1
    name: "John Doe"
    email: "user@example.com"
    hashed_password: "$2b$12$abcdef..."
     ↓
PostgreSQL → Docker Network → psycopg2
     ↓
SQLAlchemy converts row → User object
     ↓
Returns to service layer
     ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 6: Password Verification                           │
└─────────────────────────────────────────────────────────┘

Service calls: verify_password()
     ↓
```

```python
# Backend: app/utils/security.py
import bcrypt

def verify_password(plain: str, hashed: str):
    return bcrypt.checkpw(
        plain.encode('utf-8'),
        hashed.encode('utf-8')
    )
```

```
     ↓
bcrypt algorithm:
  Input: "password123"
  Stored hash: "$2b$12$abcdef..."
  
  1. Extract salt from hash: "$2b$12$"
  2. Hash input with same salt
  3. Compare result with stored hash
  
  Result: True ✅
     ↓
Password verified ✅
     ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 7: JWT Token Generation                            │
└─────────────────────────────────────────────────────────┘

Service calls: create_access_token()
     ↓
```

```python
# Backend: app/utils/security.py
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict):
    to_encode = data.copy()
    
    # Token expires in 30 minutes
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    
    # Create JWT
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm="HS256"
    )
    
    return encoded_jwt
```

```
     ↓
JWT Created:
  Header: {"alg": "HS256", "typ": "JWT"}
  Payload: {"sub": "user@example.com", "exp": 1738150000}
  Signature: HMACSHA256(...)
     ↓
Token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzM4MTUwMDAwfQ.abc123..."
     ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 8: Response Sent                                   │
└─────────────────────────────────────────────────────────┘

Service returns dict:
  {
    "access_token": "eyJhbGci...",
    "token_type": "bearer"
  }
     ↓
FastAPI validates against Token schema (Pydantic)
     ↓
Serializes to JSON
     ↓
Uvicorn sends HTTP response:
  Status: 200 OK
  Headers:
    Content-Type: application/json
    Access-Control-Allow-Origin: http://localhost:5173
  Body:
    {
      "access_token": "eyJhbGci...",
      "token_type": "bearer"
    }
     ↓
Backend Container → Docker Network → Browser
     ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 9: Frontend Receives Response                      │
└─────────────────────────────────────────────────────────┘

Axios receives response
     ↓
authService.login() returns data
     ↓
```

```javascript
// Frontend: src/services/authService.js
// Stores token in localStorage
localStorage.setItem('token', response.data.access_token);
```

```
     ↓
AuthContext updates state:
```

```javascript
// Frontend: src/context/AuthContext.jsx
setUser({ token: data.access_token });
```

```
     ↓
React re-renders
     ↓
AppRoutes checks: isAuthenticated?
     ↓
isAuthenticated = true (user has token)
     ↓
ProtectedLayout activates
     ↓
Redirects to: /dashboard
     ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 10: Dashboard Loads                                │
└─────────────────────────────────────────────────────────┘

User sees: Dashboard page ✅
     ↓
Login flow complete! 🎉
```

**Total time: ~100-500ms**

---

## 3. Complete User Journey: Create Project

### Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ User is on Dashboard → Clicks "New Project"             │
└─────────────────────────────────────────────────────────┘
     ↓
Navigate to: /projects
     ↓
Projects page renders
     ↓
User clicks "Create Project" button
     ↓
Modal opens (CreateProjectModal component)
     ↓
User enters:
  Name: "Issue Tracker"
  Description: "Track bugs and features"
     ↓
User clicks "Create"
     ↓
```

```javascript
// Frontend: src/components/projects/CreateProjectModal.jsx
const handleSubmit = async (e) => {
  e.preventDefault();
  
  try {
    await createProject({
      name: formData.name,
      description: formData.description
    });
    
    toast.success('Project created!');
    onClose();  // Close modal
    refetchProjects();  // Refresh project list
  } catch (error) {
    toast.error('Failed to create project');
  }
};
```

```
     ↓
Calls: createProject() from useProjects hook
     ↓
```

```javascript
// Frontend: src/hooks/useProjects.js
const createProject = async (projectData) => {
  return await projectService.createProject(projectData);
};
```

```
     ↓
```

```javascript
// Frontend: src/services/projectService.js
const createProject = async (projectData) => {
  // Axios automatically adds Authorization header
  // (configured in api.js interceptor)
  const response = await api.post('/projects', projectData);
  return response.data;
};
```

```
     ↓
HTTP Request:
  POST http://localhost:8000/projects
  Headers:
    Content-Type: application/json
    Authorization: Bearer eyJhbGci...  ← JWT token from localStorage
  Body:
    {
      "name": "Issue Tracker",
      "description": "Track bugs and features"
    }
     ↓
Frontend Container → Docker Network → Backend Container
     ↓
┌─────────────────────────────────────────────────────────┐
│ Backend Processing                                       │
└─────────────────────────────────────────────────────────┘

CORS Middleware: ✅ Allowed
     ↓
FastAPI Router: POST /projects
     ↓
Dependencies:
  1. get_db() → Database session
  2. get_current_user() → Verify JWT token
     ↓
```

```python
# Backend: app/auth_dependencies.py
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Decode JWT
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    # Extract email
    email = payload.get("sub")
    
    # Get user from database
    user = user_repository.get_by_email(db, email)
    
    if not user:
        raise HTTPException(401, "Invalid token")
    
    return user
```

```
     ↓
SQL Query:
  SELECT * FROM users WHERE email = 'user@example.com'
     ↓
Database → User object
     ↓
current_user available ✅
     ↓
Route Handler:
```

```python
# Backend: app/routers/projects.py
@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return project_service.create_project(
        db,
        project,
        current_user
    )
```

```
     ↓
Service Layer:
```

```python
# Backend: app/services/project.py
def create_project(
    self,
    db: Session,
    project_data: ProjectCreate,
    user: User
):
    # Business logic: Validate, check permissions, etc.
    if not user.is_active:
        raise HTTPException(403, "User is not active")
    
    # Create project via repository
    project = project_repository.create(
        db,
        project_data,
        user.id
    )
    
    return project
```

```
     ↓
Repository Layer:
```

```python
# Backend: app/repositories/project.py
def create(
    self,
    db: Session,
    project_data: ProjectCreate,
    user_id: int
):
    db_project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=user_id
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return db_project
```

```
     ↓
SQLAlchemy → SQL:
```

```sql
INSERT INTO projects (name, description, owner_id, created_at)
VALUES ('Issue Tracker', 'Track bugs and features', 1, NOW())
RETURNING id, name, description, owner_id, created_at;
```

```
     ↓
Database Container (PostgreSQL):
  Executes INSERT
  Returns new row:
    id: 5
    name: "Issue Tracker"
    description: "Track bugs and features"
    owner_id: 1
    created_at: "2025-01-29 10:30:00"
     ↓
SQLAlchemy → Project object
     ↓
Repository → Service → Router
     ↓
FastAPI serializes with ProjectResponse schema
     ↓
HTTP Response:
  Status: 201 Created
  Body:
    {
      "id": 5,
      "name": "Issue Tracker",
      "description": "Track bugs and features",
      "owner_id": 1,
      "created_at": "2025-01-29T10:30:00"
    }
     ↓
Backend → Docker Network → Frontend
     ↓
Frontend receives response
     ↓
toast.success('Project created!')
     ↓
Modal closes
     ↓
Project list refreshes (fetches all projects again)
     ↓
User sees new project in list ✅
```

---

## 4. Complete User Journey: View Projects

### Flow Diagram

```
User on Dashboard → Clicks "Projects" in navbar
     ↓
Navigate to: /projects
     ↓
Projects component mounts
     ↓
```

```javascript
// Frontend: src/pages/Projects.jsx
export const Projects = () => {
  // useProjects hook automatically fetches on mount
  const { projects, loading } = useProjects();
  
  return (
    <div>
      {loading ? <LoadingSpinner /> : <ProjectList projects={projects} />}
    </div>
  );
};
```

```
     ↓
```

```javascript
// Frontend: src/hooks/useProjects.js
const useProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await projectService.getProjects();
        setProjects(data);
      } catch (error) {
        toast.error('Failed to load projects');
      } finally {
        setLoading(false);
      }
    };
    
    fetchProjects();
  }, []);
  
  return { projects, loading };
};
```

```
     ↓
```

```javascript
// Frontend: src/services/projectService.js
const getProjects = async () => {
  const response = await api.get('/projects');
  return response.data;
};
```

```
     ↓
HTTP Request:
  GET http://localhost:8000/projects
  Headers:
    Authorization: Bearer eyJhbGci...
     ↓
Backend receives request
     ↓
Verifies JWT token → current_user
     ↓
```

```python
# Backend: app/routers/projects.py
@router.get("/", response_model=list[ProjectResponse])
async def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return project_service.get_user_projects(db, current_user)
```

```
     ↓
```

```python
# Backend: app/services/project.py
def get_user_projects(self, db: Session, user: User):
    return project_repository.get_all_by_user(db, user.id)
```

```
     ↓
```

```python
# Backend: app/repositories/project.py
def get_all_by_user(self, db: Session, user_id: int):
    return db.query(Project)\
        .filter(Project.owner_id == user_id)\
        .all()
```

```
     ↓
SQL:
```

```sql
SELECT id, name, description, owner_id, created_at
FROM projects
WHERE owner_id = 1
ORDER BY created_at DESC;
```

```
     ↓
PostgreSQL returns:
  [
    {id: 5, name: "Issue Tracker", ...},
    {id: 4, name: "Todo App", ...},
    {id: 3, name: "Blog", ...}
  ]
     ↓
SQLAlchemy → List of Project objects
     ↓
Repository → Service → Router
     ↓
FastAPI serializes with list[ProjectResponse]
     ↓
HTTP Response:
  Status: 200 OK
  Body:
    [
      {
        "id": 5,
        "name": "Issue Tracker",
        "description": "Track bugs and features",
        "owner_id": 1,
        "created_at": "2025-01-29T10:30:00"
      },
      ...
    ]
     ↓
Frontend receives response
     ↓
setProjects(data)
     ↓
React re-renders with projects data
     ↓
ProjectList component displays projects
     ↓
User sees list of projects ✅
```

---

## 5. Docker Networking

### How Containers Communicate

```
┌─────────────────────────────────────────────────────┐
│ Docker Network: issue_tracker_network               │
│                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌────────┐ │
│  │  Frontend    │   │  Backend     │   │Database│ │
│  │  Container   │   │  Container   │   │Container││
│  │              │   │              │   │        ││ │
│  │  Name:       │   │  Name:       │   │ Name:  ││ │
│  │  frontend    │   │  backend     │   │   db   ││ │
│  │              │   │              │   │        ││ │
│  │  Internal IP:│   │  Internal IP:│   │Internal││ │
│  │  172.18.0.3  │   │  172.18.0.2  │   │IP:     ││ │
│  │              │   │              │   │172.18.1││ │
│  └──────┬───────┘   └──────┬───────┘   └────┬───┘│ │
│         │                  │                 │    │ │
│         └──────────────────┴─────────────────┘    │ │
│                  (Can communicate)                 │ │
└─────────────────────────────────────────────────────┘
```

### Communication Paths

**1. Browser → Frontend Container**
```
Browser: http://localhost:5173
     ↓
Host port 5173 → Container port 5173 (port mapping)
     ↓
Frontend container (Vite)
```

**2. Browser → Backend Container**
```
Browser (via Axios): http://localhost:8000
     ↓
Host port 8000 → Container port 8000 (port mapping)
     ↓
Backend container (Uvicorn)
```

**3. Backend → Database**
```
Backend uses DATABASE_URL:
postgresql://postgres:postgres@db:5432/issue_tracker
                              ↑
                         container name (not localhost!)
     ↓
Docker DNS resolves "db" → 172.18.0.1:5432
     ↓
Database container (PostgreSQL)
```

**Why "db" and not "localhost"?**
- Inside container, "localhost" = the container itself
- "db" = Docker container name (DNS resolves to internal IP)
- Containers on same network can use container names

---

## 6. Environment Variables Flow

### How .env Values Reach Containers

```
┌─────────────────────────────────────────────────────┐
│ .env file (root directory)                          │
│                                                     │
│ POSTGRES_USER=postgres                             │
│ POSTGRES_PASSWORD=postgres                         │
│ SECRET_KEY=abc123...                               │
│ VITE_API_URL=http://localhost:8000                 │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ docker-compose.yml reads .env                       │
│                                                     │
│ backend:                                            │
│   environment:                                      │
│     SECRET_KEY: ${SECRET_KEY}  ← From .env         │
│     DATABASE_URL: postgresql://...@db:5432/...     │
│                                                     │
│ frontend:                                           │
│   environment:                                      │
│     VITE_API_URL: ${VITE_API_URL}  ← From .env     │
└────────────────┬────────────────────────────────────┘
                 ↓
        ┌────────┴────────┐
        ↓                 ↓
┌──────────────┐   ┌──────────────┐
│Backend       │   │Frontend      │
│Container     │   │Container     │
│              │   │              │
│os.getenv(    │   │import.meta   │
│'SECRET_KEY') │   │.env.VITE_... │
└──────────────┘   └──────────────┘
        ↓                 ↓
┌──────────────┐   ┌──────────────┐
│Python app    │   │Vite replaces │
│reads value   │   │at build time │
│at runtime    │   │              │
└──────────────┘   └──────────────┘
```

### Key Differences

| Aspect | Backend (Python) | Frontend (Vite) |
|--------|------------------|-----------------|
| **When loaded** | Runtime (when app starts) | Build time (when bundled) |
| **How accessed** | `os.getenv('VAR')` | `import.meta.env.VITE_VAR` |
| **Prefix required** | No | Yes (`VITE_`) |
| **Can change after build** | Yes (restart container) | No (rebuild required) |

---

## 7. Error Handling Flow

### Example: Invalid JWT Token

```
User's token expires (30 minutes passed)
     ↓
User tries to fetch projects
     ↓
GET /projects
Headers: Authorization: Bearer <expired_token>
     ↓
Backend: get_current_user() dependency
     ↓
```

```python
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
except JWTError:
    raise HTTPException(401, "Invalid token")
```

```
     ↓
JWT decode fails (token expired)
     ↓
raises: HTTPException(401, "Invalid token")
     ↓
FastAPI exception handler catches it
     ↓
HTTP Response:
  Status: 401 Unauthorized
  Body: {"detail": "Invalid token"}
     ↓
Frontend: Axios interceptor
     ↓
```

```javascript
// Frontend: src/services/api.js
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      authService.logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

```
     ↓
authService.logout():
  - Remove token from localStorage
  - Clear auth context
     ↓
Redirect to: /login
     ↓
User sees login page with message: "Session expired"
```

---

## Summary

### Complete Request Flow (High-Level)

```
1. User interacts with React UI
   ↓
2. Component calls hook/service
   ↓
3. Service makes Axios request
   ↓
4. Request interceptor adds JWT token
   ↓
5. HTTP request → Docker Network → Backend
   ↓
6. CORS middleware validates origin
   ↓
7. FastAPI matches route
   ↓
8. Dependencies inject DB session + current user
   ↓
9. JWT token verified
   ↓
10. Route handler calls service
   ↓
11. Service implements business logic
   ↓
12. Repository queries database
   ↓
13. SQLAlchemy → SQL → PostgreSQL
   ↓
14. PostgreSQL returns data
   ↓
15. SQLAlchemy → Python objects
   ↓
16. Service processes data
   ↓
17. FastAPI serializes with Pydantic
   ↓
18. HTTP response → Docker Network → Frontend
   ↓
19. Response interceptor handles errors
   ↓
20. React updates state
   ↓
21. UI re-renders
   ↓
22. User sees result
```

### Key Technologies

| Layer | Technology | Purpose |
|-------|------------|---------|
| **UI** | React + Tailwind | User interface |
| **State** | React Context | Global state management |
| **HTTP Client** | Axios | API requests |
| **Build Tool** | Vite | Frontend bundling + dev server |
| **Web Server** | Uvicorn | ASGI server for FastAPI |
| **API Framework** | FastAPI | REST API endpoints |
| **ORM** | SQLAlchemy | Database access |
| **Database** | PostgreSQL | Data storage |
| **Auth** | JWT (jose) | Token-based authentication |
| **Password Hash** | bcrypt | Secure password storage |
| **Containers** | Docker | Isolated environments |
| **Orchestration** | Docker Compose | Multi-container management |

---

**End-to-end time (typical): 100-500ms**
