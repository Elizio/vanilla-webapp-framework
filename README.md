# Vanilla WebApp Framework

A modern, lightweight web application framework that combines Flask backend with a vanilla JavaScript frontend, leveraging Alpine.js and Tailwind CSS for enhanced functionality and styling.

## 🚀 Features

### Backend
- **Flask-based RESTful API**
  - Modular routing with Blueprints
  - SQLAlchemy ORM for database operations
  - JWT authentication for secure endpoints
  - Swagger documentation for API endpoints
  - Comprehensive error handling and logging

### Frontend
- **SPA-like Behavior**
  - Dynamic data loading with Fetch API
  - Handlebars.js templating
  - Alpine.js for lightweight state management
  - Tailwind CSS for utility-first styling
  - Responsive design support

### Development & DevOps
- **Modern Development Workflow**
  - Vite for build optimization
  - Docker support with multi-stage builds
  - GitHub Actions CI/CD pipeline
  - Automated testing with pytest
  - DigitalOcean deployment integration

## 🛠️ Tech Stack

### Backend
- Flask
- SQLAlchemy
- JWT Authentication
- Flasgger (Swagger)
- Python 3.x

### Frontend
- Vanilla JavaScript (ES6+)
- Alpine.js
- Handlebars.js
- Tailwind CSS
- Vite

### DevOps
- Docker
- GitHub Actions
- pytest
- DigitalOcean

## 📁 Project Structure

```
vanilla-webapp-framework/
├── backend/
│   ├── api/               # Flask blueprints
│   ├── config/            # Application configuration
│   ├── models/            # SQLAlchemy models
│   ├── templates/         # Shared Flask templates
│   ├── db_repository/     # Database migration scripts
│   ├── tests/             # Backend tests
│   ├── __init__.py        # Application initialization
│   └── app.py             # Main Flask application
├── frontend/
│   ├── src/
│   │   ├── js/            # JavaScript modules
│   │   │   ├── controllers/ # Page-specific controllers
│   │   │   ├── app.js     # Application logic
│   │   │   └── main.js    # Main entry point
│   │   ├── styles/        # CSS and Tailwind styles
│   │   ├── templates/     # Handlebars templates
│   │   │   ├── pages/     # Page templates
│   │   │   └── partials/  # Reusable template parts
│   │   └── index.html     # Main HTML entry point
│   ├── public/            # Static assets
│   ├── package.json       # Frontend dependencies
│   ├── vite.config.js     # Vite configuration
│   └── tailwind.config.js # Tailwind CSS configuration
├── .env                   # Environment variables
├── Dockerfile             # Docker configuration
├── requirements.txt       # Python dependencies
├── setup.cfg              # Python package configuration
├── setup.py               # Python package setup
└── package.json           # Root package configuration
```

## 🚀 Getting Started

1. **Environment Setup**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

2. **Environment Variables**
   Create a `.env` file in the root directory with the following variables:
   ```
   FLASK_SECRET=<your-flask-secret-key>
   JWT_SECRET=<your-jwt-secret-key>
   
   DATABASE_URI=<your-database-connection-string>
   PROJECT_FOLDER=<your-project-folder-path>
   APP_PROFILE=<development|production|testing>
   ```
   
   | Variable | Description |
   | --- | --- |
   | `FLASK_SECRET` | Secret key used for Flask sessions and CSRF protection |
   | `JWT_SECRET` | Secret key used for JWT token generation and validation |
   | `DATABASE_URI` | URI for database connection (SQLite, PostgreSQL, MySQL, etc.) |
   | `PROJECT_FOLDER` | Absolute path to the project folder |
   | `APP_PROFILE` | Application environment profile (development, production, testing) |

3. **Development**
   ```bash
   # Terminal 1 — API
   flask run

   # Terminal 2 — SPA (use http://localhost:5173 in browser)
   cd frontend && npm install && npm run dev
   ```

4. **Docker Setup**
   ```bash
   docker build -t vanilla-webapp .
   docker run -p 5000:5000      -e DATABASE_URI=sqlite:////data/app.db      -e FLASK_SECRET=your-secret      -e JWT_SECRET=your-jwt-secret      -e PROJECT_FOLDER=/data      -e APP_PROFILE=production      vanilla-webapp
   ```

5. **Testing**
   ```bash
   pytest
   cd frontend && npm run build && npm run test
   ```

## 📝 Development Guidelines

### Backend Development
- Use Flask Blueprints for modular routing
- Follow RESTful conventions
- Implement proper error handling
- Write comprehensive tests
- Document all API endpoints

### Frontend Development
- Use Fetch API for data operations
- Implement responsive design
- Keep Alpine.js logic simple
- Leverage Tailwind utility classes
- Optimize assets with Vite

### Code Standards
- Follow PEP 8 for Python code
- Use ES6+ for JavaScript
- Keep functions modular
- Add proper documentation
- Avoid global variables

## 🔒 Security

- JWT authentication for protected routes
- Secure session management
- Input validation
- Error handling without sensitive information exposure

## 📦 Deployment

- Docker-based deployment
- Multi-stage builds for optimized images
- Automated CI/CD pipeline
- DigitalOcean deployment integration

## 📚 Documentation

- API documentation via Swagger
- Code documentation with JSDoc/type hints
- Comprehensive README files
- Development guidelines

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow coding standards
4. Add tests for new features
5. Submit a pull request

## 📄 License

[Your License Here]

---

Built with ❤️ using modern web technologies 