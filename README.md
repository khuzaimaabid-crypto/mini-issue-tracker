# Mini Issue Tracker

A full-stack issue tracking application built with React, FastAPI, and PostgreSQL, featuring JWT authentication and Docker containerization.

## 🚀 Features

- **User Authentication**: JWT-based authentication with registration and login
- **Project Management**: Create, read, update, and delete projects
- **Issue Tracking**: Manage issues with status and priority filtering
- **Responsive Design**: Mobile-friendly UI built with TailwindCSS
- **Docker Support**: Fully containerized with Docker Compose
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

## 🛠️ Tech Stack

### Frontend
- React 18 with Vite
- TailwindCSS for styling
- React Router for navigation
- Axios for API calls
- React Hot Toast for notifications
- Vitest & React Testing Library for testing

### Backend
- FastAPI (Python 3.11)
- SQLAlchemy ORM
- PostgreSQL database
- JWT authentication
- Pytest for testing
- Alembic for migrations

### DevOps
- Docker & Docker Compose
- GitHub Actions CI/CD
- Vercel (Frontend deployment)
- Render (Backend deployment)

## 📦 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mini-issue-tracker
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start with Quick Start Script**
   ```bash
   chmod +x quick-start.sh
   ./quick-start.sh
   ```

   **Or use Make commands**
   ```bash
   make setup
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up --build

# Access backend shell
docker-compose exec backend bash

# Access frontend shell
docker-compose exec frontend sh
```

## 🧪 Running Tests

### Backend Tests
```bash
# Using Docker
docker-compose exec backend pytest tests/ -v

# Or using Make
make test-backend
```

### Frontend Tests
```bash
# Using Docker
docker-compose exec frontend npm test

# Or using Make
make test-frontend
```

## 📚 API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token

### Projects
- `GET /projects` - Get all user projects
- `GET /projects/{id}` - Get specific project
- `POST /projects` - Create new project
- `PATCH /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Issues
- `GET /projects/{id}/issues` - Get project issues (with filters)
- `POST /projects/{id}/issues` - Create new issue
- `GET /issues/{id}` - Get specific issue
- `PATCH /issues/{id}` - Update issue
- `DELETE /issues/{id}` - Delete issue

## 🏗️ Project Structure

```
mini-issue-tracker/
├── backend/
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── repositories/   # Data access layer
│   │   ├── services/       # Business logic layer
│   │   ├── routers/        # API endpoints
│   │   └── utils/          # Utilities
│   ├── tests/              # Backend tests
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── context/        # React contexts
│   │   └── hooks/          # Custom hooks
│   ├── tests/              # Frontend tests
│   └── Dockerfile
└── docker-compose.yml
```

## 🔑 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/issue_tracker
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS='["http://localhost:5173"]'
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 📝 Make Commands

```bash
make help           # Show all available commands
make setup          # Initial project setup
make up             # Start all services
make down           # Stop all services
make logs           # View all logs
make test           # Run all tests
make db-shell       # Access database shell
make clean          # Remove containers and volumes
```

## 🚀 Deployment

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Backend (Render)
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables
4. Deploy automatically on push to main branch

## 🔒 Security Features

- ✅ JWT token authentication
- ✅ Password hashing with bcrypt
- ✅ CORS configuration
- ✅ SQL injection prevention (SQLAlchemy)
- ✅ Input validation (Pydantic)
- ✅ Environment variables for secrets

## 🎯 Design Patterns Used

- **Repository Pattern**: Data access abstraction
- **Service Layer Pattern**: Business logic encapsulation
- **Dependency Injection**: FastAPI's DI system
- **Factory Pattern**: Database session management
- **Context Pattern**: React global state management

## 📖 Documentation

- [Setup Guide](SETUP_GUIDE.md) - Detailed setup instructions
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Architecture details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Support

For issues and questions:
- Open an issue on GitHub
- Check the [Troubleshooting Guide](TROUBLESHOOTING.md)

## Backend Flow

HTTP Request
    ↓
1. ROUTERS/ - "Front door" - receives request
    ↓
2. SCHEMAS/ - Validates incoming JSON data
    ↓
3. SERVICES/ - Business logic (what to do)
    ↓
4. REPOSITORIES/ - Database operations (how to do it)
    ↓
5. MODELS/ - Database tables structure
    ↓
6. SCHEMAS/ - Formats response back to JSON
    ↓
HTTP Response

## 🙏 Acknowledgments

Built with modern best practices and design patterns for a production-ready application.

---

**Happy Coding! 🚀**