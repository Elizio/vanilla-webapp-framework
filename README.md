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
│   ├── models/            # SQLAlchemy models
│   ├── templates/         # Shared Flask/Handlebars base templates
│   ├── db_repository/     
│   └── tests/             # Backend tests
├── frontend/
│   ├── src/
│   │   ├── js/            # JavaScript modules
│   │   │   └── api.js     # Centralized Fetch API calls
│   │   └── styles/        # Tailwind styles
│   │   └── templates/     # Handlebars templates
│   ├── public/            # Static assets (favicon, etc.)
├── Dockerfile             # Docker configuration
├── setup.cfg
├── setup.py
├── vite.config.js         # Vite setup
└── .github/               # GitHub Actions workflows
```

## 🚀 Getting Started

1. **Environment Setup**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

2. **Development**
   ```bash
   # Start backend server
   flask run
   
   # Start frontend dev server
   npm run dev
   ```

3. **Docker Setup**
   ```bash
   # Build and run the Docker container
   docker build -t vanilla-webapp .
   docker run -p 5000:5000 vanilla-webapp
   ```

4. **Testing**
   ```bash
   pytest
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