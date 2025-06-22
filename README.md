# 🏢 ERP System with FastAPI and Streamlit

A modern, containerized ERP (Enterprise Resource Planning) system featuring a FastAPI backend and Streamlit frontend, designed for simplicity and scalability.

## ✨ Features

- 🔐 **JWT Authentication** - Secure user authentication with JWT tokens
- 📦 **Inventory Management** - Full CRUD operations for inventory items
  - Add, view, update, and delete items
  - Search and filter functionality
  - Real-time inventory value calculation
- 📊 **Dashboard** - Visual analytics and metrics
  - Inventory overview
  - Low stock alerts
  - Value calculations
- 🌐 **Modern UI** - Responsive and user-friendly interface
- 🐳 **Containerized** - Easy deployment with Docker
- 🔄 **RESTful API** - Well-documented endpoints with OpenAPI/Swagger

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- Git (for cloning the repository)

### Running with Docker Compose

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/erp-system.git
   cd erp-system
   ```

2. **Set up environment variables**
   - Copy the example environment files and update as needed:
     ```bash
     cp erp_backend/.env.example erp_backend/.env
     cp erp_frontend/.env.example erp_frontend/.env
     ```
   - Update the `.env` files with your configuration (at minimum, set a strong `SECRET_KEY` in the backend)

3. **Build and start the services**
   ```bash
   docker-compose up --build -d
   ```

4. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

5. **Create an account**
   - Open the frontend in your browser
   - Click "Create New Account"
   - Fill in the registration form
   - Log in with your credentials

## 📚 API Documentation

Interactive API documentation is available when the backend is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Project Structure

```
erp_project/
├── erp_backend/                 # FastAPI backend
│   ├── app/                    # Application code
│   │   ├── __init__.py         # Package initialization
│   │   ├── main.py             # FastAPI app and routes
│   │   ├── database.py         # Database configuration
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── schemas.py          # Pydantic models
│   │   ├── crud.py             # Database operations
│   │   └── auth.py             # Authentication utilities
│   ├── .env                    # Environment variables
│   ├── .env.example            # Example env file
│   ├── Dockerfile              # Backend Dockerfile
│   └── requirements.txt        # Python dependencies
│
├── erp_frontend/              # Streamlit frontend
│   ├── .env                    # Environment variables
│   ├── .env.example           # Example env file
│   ├── app.py                 # Streamlit application
│   ├── Dockerfile             # Frontend Dockerfile
│   └── requirements.txt       # Python dependencies
│
├── docker-compose.yml        # Docker Compose configuration
└── README.md                  # This file
```

## 🛠 Development

### Local Development (Without Docker)

#### Backend Setup

1. **Create and activate virtual environment**
   ```bash
   cd erp_backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the backend**
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Setup

1. **Create and activate virtual environment**
   ```bash
   cd ../erp_frontend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the frontend**
   ```bash
   streamlit run app.py
   ```

## ⚙️ Configuration

### Environment Variables

#### Backend (erp_backend/.env)

```env
# Application
ENVIRONMENT=development
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./erp_system.db

# CORS (comma-separated origins)
ALLOWED_ORIGINS=*

# Security
BCRYPT_ROUNDS=12
```

#### Frontend (erp_frontend/.env)

```env
# API Configuration
API_BASE_URL=http://localhost:8000/api

# Session
SESSION_TIMEOUT_MINUTES=30

# UI
DEFAULT_PAGE_TITLE=ERP System
DEFAULT_PAGE_ICON=📊

# Theme
PRIMARY_COLOR=#4F8BF9
BACKGROUND_COLOR=#F8F9FA
SECONDARY_BACKGROUND_COLOR=#FFFFFF
TEXT_COLOR=#31333F
FONT=sans serif
```

## 🔄 Database Migrations

For database schema changes, use Alembic:

1. Install Alembic:
   ```bash
   pip install alembic
   ```

2. Generate a new migration:
   ```bash
   alembic revision --autogenerate -m "Your migration message"
   ```

3. Apply migrations:
   ```bash
   alembic upgrade head
   ```

## 🧪 Testing

Run tests with pytest:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest
```

## 🚀 Deployment

### Production Deployment

1. Set `ENVIRONMENT=production` in the backend `.env` file
2. Update `ALLOWED_ORIGINS` with your production domain
3. Use a production-grade database (PostgreSQL/MySQL) in production
4. Consider using a reverse proxy (Nginx) and process manager (Gunicorn/Uvicorn with multiple workers)

### Docker Deployment

```bash
# Build and start in detached mode
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the amazing backend framework
- Streamlit for the simple yet powerful frontend
- SQLAlchemy for the ORM
- Docker for containerization
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## License

This project is open source and available under the [MIT License](LICENSE).
