# Backend System - Complete Flow Guide

## 📋 Table of Contents

1. [Application Startup](#1-application-startup)
2. [Request Lifecycle](#2-request-lifecycle)
3. [Database Layer](#3-database-layer)
4. [Architecture Layers](#4-architecture-layers)
5. [Authentication Flow](#5-authentication-flow)
6. [Docker Configuration](#6-docker-configuration)
7. [Configuration Files](#7-configuration-files)

---

## 1. Application Startup

### Command Execution Flow

```bash
$ docker-compose up
```

```
1. Docker Compose reads: docker-compose.yml
   ↓
2. Starts database container (PostgreSQL)
   ↓
3. Waits for healthcheck: pg_isready -U postgres
   ↓
4. Starts backend container
   ↓
5. Mounts volumes:
   - ./backend:/app (bind mount - your source code)
   - backend_cache:/root/.cache (cache pip packages)
   ↓
6. Sets environment variables:
   - DATABASE_URL
   - SECRET_KEY
   - BACKEND_CORS_ORIGINS
   - ENVIRONMENT=development
   ↓
7. Runs command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ↓
8. Uvicorn (ASGI server) starts:
   ├─ Imports: app.main
   ├─ Finds: app = FastAPI()
   ├─ Loads all routers
   ├─ Sets up middleware (CORS)
   ├─ Configures database connection pool
   └─ Starts HTTP server
   ↓
9. Server listening on: http://0.0.0.0:8000
   ↓
10. Docker maps: localhost:8000 → container:8000
   ↓
11. Ready! ✅ http://localhost:8000
    - API docs: http://localhost:8000/docs
    - Redoc: http://localhost:8000/redoc
```

### Uvicorn Server Explained

**What is Uvicorn?**
- ASGI server (Asynchronous Server Gateway Interface)
- Similar to Gunicorn/uWSGI but supports async Python
- Runs your FastAPI application

**Key Flags:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

| Flag | Meaning | Purpose |
|------|---------|---------|
| `app.main:app` | Import `app` from `app.main` module | Entry point |
| `--host 0.0.0.0` | Bind to all interfaces | Docker accessibility |
| `--port 8000` | Listen on port 8000 | API server port |
| `--reload` | Auto-restart on code changes | Development only |

---

## 2. Request Lifecycle

### Example: Login Request

**Frontend makes request:**
```javascript
// Frontend: src/services/authService.js
await axios.post('http://localhost:8000/auth/login', {
  email: 'user@example.com',
  password: 'password123'
})
```

**Complete flow through backend:**

```
┌──────────────────────────────────────────────────┐
│ Step 1: Request Arrives                          │
└──────────────────────────────────────────────────┘
     ↓
POST http://localhost:8000/auth/login
Headers:
  Content-Type: application/json
Body:
  {
    "email": "user@example.com",
    "password": "password123"
  }
     ↓
Docker port mapping: localhost:8000 → container:8000
     ↓
Uvicorn receives request
     ↓
┌──────────────────────────────────────────────────┐
│ Step 2: Middleware Processing                    │
└──────────────────────────────────────────────────┘
     ↓
CORS Middleware (app/main.py):
  Check: Is origin allowed?
  Origin: http://localhost:5173
  Allowed origins: ["http://localhost:5173", "http://localhost:3000"]
  Result: ✅ Allowed
  
  Add headers:
    Access-Control-Allow-Origin: http://localhost:5173
    Access-Control-Allow-Credentials: true
     ↓
┌──────────────────────────────────────────────────┐
│ Step 3: Route Matching                           │
└──────────────────────────────────────────────────┘
     ↓
FastAPI router searches for matching route:
  POST /auth/login
     ↓
Finds in: app/routers/auth.py
     ↓
Route handler:
  @router.post("/login", response_model=Token)
  async def login(...):
     ↓
┌──────────────────────────────────────────────────┐
│ Step 4: Dependency Injection                     │
└──────────────────────────────────────────────────┘
     ↓
FastAPI resolves dependencies:
     ↓
Dependency #1: db: Session = Depends(get_db)
     ↓
Calls: app/database.py → get_db()
     ↓
┌────────────────────────────────────────────┐
│ get_db() function execution                │
│                                            │
│ 1. SessionMaker() creates new session      │
│ 2. Session borrows connection from pool   │
│ 3. yield session (passes to route)        │
│ 4. (waits for route to finish)            │
│ 5. session.close() (cleanup)              │
│ 6. Connection returns to pool             │
└────────────────────────────────────────────┘
     ↓
Session available for route handler ✅
     ↓
Dependency #2: form_data: OAuth2PasswordRequestForm
     ↓
FastAPI parses request body:
  username: user@example.com  (email used as username)
  password: password123
     ↓
form_data available for route handler ✅
     ↓
┌──────────────────────────────────────────────────┐
│ Step 5: Request Validation (Pydantic)            │
└──────────────────────────────────────────────────┘
     ↓
FastAPI validates form_data against OAuth2PasswordRequestForm schema:
  - username: str ✅
  - password: str ✅
     ↓
If validation fails → 422 Unprocessable Entity
If validation succeeds → Continue
     ↓
┌──────────────────────────────────────────────────┐
│ Step 6: Route Handler Execution                  │
└──────────────────────────────────────────────────┘
     ↓
Route: app/routers/auth.py → login()
     ↓
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Service layer call
    return auth_service.login(
        db=db,
        email=form_data.username,
        password=form_data.password
    )
     ↓
┌──────────────────────────────────────────────────┐
│ Step 7: Service Layer                            │
└──────────────────────────────────────────────────┘
     ↓
Service: app/services/auth.py → AuthService.login()
     ↓
class AuthService:
    def login(self, db: Session, email: str, password: str):
        # 1. Find user in database
        user = user_repository.get_by_email(db, email)
        
        if not user:
            raise HTTPException(401, "Invalid credentials")
        
        # 2. Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(401, "Invalid credentials")
        
        # 3. Create JWT token
        token = create_access_token({"sub": user.email})
        
        return {"access_token": token, "token_type": "bearer"}
     ↓
┌──────────────────────────────────────────────────┐
│ Step 8: Repository Layer (Database Access)       │
└──────────────────────────────────────────────────┘
     ↓
Repository: app/repositories/user.py → UserRepository.get_by_email()
     ↓
class UserRepository:
    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()
     ↓
SQLAlchemy translates to SQL:
     ↓
SQL Query:
  SELECT users.id, users.name, users.email, users.hashed_password
  FROM users
  WHERE users.email = 'user@example.com'
  LIMIT 1
     ↓
PostgreSQL executes query
     ↓
Returns row:
  id: 1
  name: "John Doe"
  email: "user@example.com"
  hashed_password: "$2b$12$..."
     ↓
SQLAlchemy converts row → User object
     ↓
User object returned to service layer
     ↓
┌──────────────────────────────────────────────────┐
│ Step 9: Password Verification                    │
└──────────────────────────────────────────────────┘
     ↓
Service: app/utils/security.py → verify_password()
     ↓
import bcrypt

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
     ↓
bcrypt.checkpw():
  Input: "password123"
  Stored hash: "$2b$12$..."
  
  Process:
  1. Extract salt from stored hash
  2. Hash input password with same salt
  3. Compare hashes
  
  Result: True ✅
     ↓
Password verified ✅
     ↓
┌──────────────────────────────────────────────────┐
│ Step 10: JWT Token Creation                      │
└──────────────────────────────────────────────────┘
     ↓
Service: app/utils/security.py → create_access_token()
     ↓
from jose import jwt

def create_access_token(data: dict):
    to_encode = data.copy()
    
    # Add expiration
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    
    # Create JWT
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm="HS256"
    )
    
    return encoded_jwt
     ↓
Token created:
  Header: {"alg": "HS256", "typ": "JWT"}
  Payload: {"sub": "user@example.com", "exp": 1738150000}
  Signature: HMACSHA256(base64(header) + "." + base64(payload), SECRET_KEY)
     ↓
JWT Token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzM4MTUwMDAwfQ.signature"
     ↓
┌──────────────────────────────────────────────────┐
│ Step 11: Response Serialization (Pydantic)       │
└──────────────────────────────────────────────────┘
     ↓
Service returns dict:
  {
    "access_token": "eyJhbGci...",
    "token_type": "bearer"
  }
     ↓
FastAPI validates response against Token schema:
     ↓
class Token(BaseModel):
    access_token: str  ✅
    token_type: str    ✅
     ↓
Pydantic serializes to JSON:
     ↓
┌──────────────────────────────────────────────────┐
│ Step 12: Response Sent                           │
└──────────────────────────────────────────────────┘
     ↓
HTTP Response:
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
Uvicorn sends response
     ↓
Docker forwards to host
     ↓
Frontend receives response ✅
     ↓
┌──────────────────────────────────────────────────┐
│ Step 13: Cleanup (Dependency Teardown)           │
└──────────────────────────────────────────────────┘
     ↓
get_db() dependency finishes:
  finally:
      db.close()  # Close session
     ↓
Database connection returned to pool
     ↓
Request complete! ✅
```

**Total time: ~50-200ms**

---

## 3. Database Layer

### SQLAlchemy Architecture

```
┌─────────────────────────────────────────────────┐
│ Application Layer                                │
│ (Your Python Code)                              │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│ SQLAlchemy ORM (Object-Relational Mapping)      │
│                                                 │
│ Python Objects ↔ Database Rows                 │
│                                                 │
│ user = User(name="John", email="john@ex.com")  │
│   ↓                                             │
│ INSERT INTO users (name, email) VALUES (...)   │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│ SQLAlchemy Core (SQL Expression Language)       │
│                                                 │
│ Builds SQL queries                              │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│ Database Driver (psycopg2)                      │
│                                                 │
│ Communicates with PostgreSQL                    │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│ PostgreSQL Database                             │
│                                                 │
│ Stores actual data                              │
└─────────────────────────────────────────────────┘
```

### Connection Pool Explained

**What is a Connection Pool?**

A pool of reusable database connections to avoid the overhead of creating new connections for each request.

```
┌─────────────────────────────────────────────────┐
│ Connection Pool (DatabaseEngine)                │
│                                                 │
│ [Connection 1] ─┐                               │
│ [Connection 2]  ├─ Idle connections (available) │
│ [Connection 3] ─┘                               │
│ [Connection 4] ← In use by Request A            │
│ [Connection 5] ← In use by Request B            │
│                                                 │
│ Pool size: 5 connections                        │
│ Max overflow: 10 additional if needed           │
└─────────────────────────────────────────────────┘
```

**Flow:**

```
Request comes in
     ↓
get_db() creates Session
     ↓
Session borrows connection from pool
     ↓
Execute queries using that connection
     ↓
Request completes
     ↓
Session closes
     ↓
Connection returns to pool (reused by next request)
```

**Without Pool (Bad):**
```
Request 1: Open connection → Query → Close connection
Request 2: Open connection → Query → Close connection  ❌ Slow!
Request 3: Open connection → Query → Close connection
```

**With Pool (Good):**
```
Request 1: Borrow connection → Query → Return to pool
Request 2: Borrow same connection → Query → Return to pool  ✅ Fast!
Request 3: Borrow same connection → Query → Return to pool
```

### Session vs Connection

| Aspect | Connection | Session |
|--------|------------|---------|
| **What** | Direct link to database | Workspace for operations |
| **Lifespan** | Long-lived (reused) | Short-lived (per-request) |
| **Purpose** | Send SQL to database | Track objects, changes |
| **Pool** | Yes (5-15 connections) | No (created on-demand) |
| **Cleanup** | Returns to pool | Closed after request |

**Example:**

```python
# Connection Pool (created once at startup)
engine = create_engine(DATABASE_URL, pool_size=5)

# SessionMaker (factory for creating sessions)
SessionMaker = sessionmaker(bind=engine)

# Session (created per request)
def get_db():
    db = SessionMaker()  # Creates new session
    try:
        yield db  # Passes to route handler
    finally:
        db.close()  # Closes session, returns connection to pool
```

---

## 4. Architecture Layers

### Layered Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│ Router Layer (app/routers/)                     │
│ - HTTP request/response handling                │
│ - Route definitions                             │
│ - Input validation (Pydantic)                   │
│ - Authentication checks                         │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│ Service Layer (app/services/)                   │
│ - Business logic                                │
│ - Orchestrates repositories                     │
│ - Transaction management                        │
│ - Error handling                                │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│ Repository Layer (app/repositories/)            │
│ - Database queries (CRUD operations)            │
│ - SQLAlchemy ORM usage                          │
│ - Data access abstraction                       │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│ Model Layer (app/models/)                       │
│ - SQLAlchemy models (database schema)           │
│ - Relationships between tables                  │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│ Schema Layer (app/schemas/)                     │
│ - Pydantic models (validation)                  │
│ - Request/response serialization                │
└─────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### Router Layer (`app/routers/`)

**Purpose:** Handle HTTP requests and responses

**Example:**
```python
# app/routers/projects.py

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,  # Request validation
    db: Session = Depends(get_db),  # Database dependency
    current_user: User = Depends(get_current_user)  # Auth dependency
):
    # Delegate to service layer
    return project_service.create_project(db, project, current_user)
```

**Responsibilities:**
- ✅ Define routes (`@router.get`, `@router.post`)
- ✅ Validate input (Pydantic schemas)
- ✅ Check authentication
- ✅ Call service layer
- ❌ NO business logic
- ❌ NO database queries

#### Service Layer (`app/services/`)

**Purpose:** Implement business logic

**Example:**
```python
# app/services/project.py

class ProjectService:
    def create_project(self, db: Session, project_data: ProjectCreate, user: User):
        # Business logic: Check permissions, validate data, etc.
        if not user.is_active:
            raise HTTPException(403, "User is not active")
        
        # Create project via repository
        project = project_repository.create(db, project_data, user.id)
        
        # Additional logic: Send notification, log event, etc.
        # ...
        
        return project
```

**Responsibilities:**
- ✅ Business logic and rules
- ✅ Orchestrate multiple repositories
- ✅ Transaction management
- ✅ Error handling
- ❌ NO HTTP handling
- ❌ NO direct SQL (use repositories)

#### Repository Layer (`app/repositories/`)

**Purpose:** Database access abstraction

**Example:**
```python
# app/repositories/project.py

class ProjectRepository:
    def create(self, db: Session, project_data: ProjectCreate, user_id: int):
        # Database query (SQLAlchemy ORM)
        db_project = Project(
            name=project_data.name,
            description=project_data.description,
            owner_id=user_id
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    def get_by_id(self, db: Session, project_id: int):
        return db.query(Project).filter(Project.id == project_id).first()
    
    def get_all_by_user(self, db: Session, user_id: int):
        return db.query(Project).filter(Project.owner_id == user_id).all()
```

**Responsibilities:**
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Complex queries
- ✅ Joins, filters, aggregations
- ❌ NO business logic
- ❌ NO HTTP handling

#### Model Layer (`app/models/`)

**Purpose:** Define database schema

**Example:**
```python
# app/models/project.py

class Project(ModelBase):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    issues = relationship("Issue", back_populates="project")
```

**SQLAlchemy generates:**
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Schema Layer (`app/schemas/`)

**Purpose:** Request/response validation

**Example:**
```python
# app/schemas/project.py

class ProjectCreate(BaseModel):
    """Schema for creating a project (request body)"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None

class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True  # Allow SQLAlchemy models → Pydantic
```

---

## 5. Authentication Flow

### JWT Token Generation

```
User logs in
     ↓
POST /auth/login
  Body: {"email": "user@ex.com", "password": "pass123"}
     ↓
Route: auth.py → login()
     ↓
Service: auth_service.login()
     ↓
Repository: user_repository.get_by_email()
     ↓
SQL: SELECT * FROM users WHERE email = 'user@ex.com'
     ↓
User found ✅
     ↓
Verify password: bcrypt.checkpw(plain_password, hashed_password)
     ↓
Password correct ✅
     ↓
Create JWT token:
     ↓
┌────────────────────────────────────────────┐
│ JWT Token Structure                        │
│                                            │
│ Header:                                    │
│ {                                          │
│   "alg": "HS256",                          │
│   "typ": "JWT"                             │
│ }                                          │
│                                            │
│ Payload:                                   │
│ {                                          │
│   "sub": "user@example.com",  ← User email │
│   "exp": 1738150000  ← Expires in 30 min  │
│ }                                          │
│                                            │
│ Signature:                                 │
│ HMACSHA256(                                │
│   base64(header) + "." + base64(payload),  │
│   SECRET_KEY                               │
│ )                                          │
└────────────────────────────────────────────┘
     ↓
Token: "eyJhbGci...payload...signature"
     ↓
Return to frontend:
  {
    "access_token": "eyJhbGci...",
    "token_type": "bearer"
  }
```

### Authenticated Request Flow

```
Frontend makes request:
  GET /projects
  Headers:
    Authorization: Bearer eyJhbGci...
     ↓
Route handler has dependency:
  current_user: User = Depends(get_current_user)
     ↓
FastAPI calls: get_current_user()
     ↓
┌────────────────────────────────────────────┐
│ get_current_user() function                │
│                                            │
│ 1. Extract token from header              │
│    token = authorization.split(" ")[1]    │
│                                            │
│ 2. Decode and verify JWT                  │
│    payload = jwt.decode(                  │
│        token,                              │
│        SECRET_KEY,                         │
│        algorithms=["HS256"]                │
│    )                                       │
│                                            │
│ 3. Check expiration                        │
│    if payload["exp"] < now:               │
│        raise HTTPException(401)           │
│                                            │
│ 4. Extract email                           │
│    email = payload.get("sub")             │
│                                            │
│ 5. Fetch user from database                │
│    user = user_repository.get_by_email()  │
│                                            │
│ 6. Return user object                      │
│    return user                             │
└────────────────────────────────────────────┘
     ↓
User object available in route handler ✅
     ↓
Route uses current_user to fetch user-specific data
```

---

## 6. Docker Configuration

### Backend Container Setup

```yaml
# docker-compose.yml
backend:
  build:
    context: ./backend
    dockerfile: Dockerfile
  ports:
    - "8000:8000"
  environment:
    DATABASE_URL: postgresql://user:pass@db:5432/dbname
    SECRET_KEY: your-secret-key
  volumes:
    - ./backend:/app
    - backend_cache:/root/.cache
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Volume Purposes

**1. Bind Mount: `./backend:/app`**
- Live code editing
- Changes reflected immediately (with --reload)

**2. Named Volume: `backend_cache:/root/.cache`**
- Cache pip packages
- Faster container rebuilds

### --reload Flag

```python
# With --reload:
You edit: app/services/project.py
     ↓
Uvicorn detects file change
     ↓
Restart server (takes ~1-2s)
     ↓
New code loaded ✅
```

**Unlike frontend (HMR), backend requires full restart!**

---

## 7. Configuration Files

### File Relationships

```
docker-compose.yml
  ├─ Sets environment variables
  ├─ Defines volumes
  └─ Runs: uvicorn app.main:app
       ↓
app/main.py
  ├─ Creates FastAPI app
  ├─ Adds CORS middleware
  ├─ Registers routers
  └─ Imports database models
       ↓
app/database.py
  ├─ Creates DatabaseEngine (connection pool)
  ├─ Creates SessionMaker (session factory)
  └─ Defines get_db() dependency
       ↓
app/models/*.py
  ├─ Define database schemas
  └─ Inherit from ModelBase
       ↓
app/routers/*.py
  ├─ Define API endpoints
  ├─ Use dependencies (get_db, get_current_user)
  └─ Call service layer
       ↓
app/services/*.py
  ├─ Implement business logic
  └─ Call repository layer
       ↓
app/repositories/*.py
  ├─ Execute database queries
  └─ Return model instances
```

---

## Summary

### Request Flow (High-Level)

```
1. Frontend sends HTTP request
   ↓
2. Uvicorn receives request
   ↓
3. CORS middleware processes
   ↓
4. FastAPI matches route
   ↓
5. Dependencies resolved (DB session, auth)
   ↓
6. Request validated (Pydantic)
   ↓
7. Route handler calls service
   ↓
8. Service implements logic
   ↓
9. Repository queries database
   ↓
10. SQLAlchemy executes SQL
   ↓
11. PostgreSQL returns data
   ↓
12. Response serialized (Pydantic)
   ↓
13. Sent back to frontend
```

### Key Differences from Frontend

| Aspect | Frontend (Vite) | Backend (Uvicorn) |
|--------|-----------------|-------------------|
| **Hot Reload** | HMR (instant, no restart) | Full restart (~1-2s) |
| **File Watching** | Polling (Docker) | Native (--reload works) |
| **Build Process** | Transpile JSX → JS | No build (Python runtime) |
| **Server** | Dev server (Vite) | ASGI server (Uvicorn) |
| **Middleware** | None | CORS, authentication |

---

**Performance Metrics (Typical):**

| Action | Time |
|--------|------|
| Container startup | 5-10s |
| Code change → reload | 1-2s |
| Database query | 1-10ms |
| JWT verification | <1ms |
| Full request → response | 50-200ms |
