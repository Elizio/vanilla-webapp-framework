## **Semi-Vanilla SPA Web Framework Documentation (Progressive Enhancement Approach)**

### **Overview**
This framework is designed to build modern, lightweight **Single Page Applications (SPAs)** using a **semi-vanilla approach**. It combines the simplicity of plain HTML, CSS, and JavaScript with modern tools like **Vite**, **Alpine.js**, and **Tailwind CSS** for enhanced productivity. The backend is powered by **Flask** and **PostgreSQL**, with **JWT** for authentication and **Swagger with Flasgger** for API documentation. The entire application is containerized using **Docker** and deployed to **DigitalOcean** via **GitHub Actions**.

The frontend uses **Progressive Enhancement** to dynamically load and render content, enabling **SPA-like behavior** without heavy frameworks.

---

### **Tools and Technologies**
#### **Backend**
- **Python**: The primary programming language.
- **Flask**: A lightweight web framework for building RESTful APIs.
- **SQLAlchemy**: An ORM for interacting with the PostgreSQL database.
- **PostgreSQL**: A powerful, open-source relational database.
- **JWT (JSON Web Tokens)**: For stateless, secure authentication.
- **Swagger (OpenAPI) with Flasgger**: For API documentation and testing.
- **Pytest**: For unit and integration testing.

#### **Frontend**
- **Handlebars.js**: A templating engine for dynamic HTML rendering.
- **Alpine.js**: A lightweight JavaScript framework for interactivity.
- **Tailwind CSS**: A utility-first CSS framework for styling.
- **Fetch API**: For making HTTP requests to the backend.
- **Vite**: A modern build tool for bundling and optimizing frontend assets.
- **Progressive Enhancement**: For dynamic content loading and SPA-like behavior.

#### **DevOps**
- **Docker**: For containerizing the application.
- **GitHub Actions**: For CI/CD (continuous integration and deployment).
- **DigitalOcean**: For hosting the application.

---

### **Framework Features**
1. **Backend**:
   - RESTful APIs built with Flask.
   - JWT-based authentication for secure user sessions.
   - Swagger with Flasgger for interactive API documentation.
   - PostgreSQL for data storage, managed via SQLAlchemy.
   - File storage and logging handled by dedicated modules in the infra folder.

2. **Frontend**:
   - **SPA-Like Behavior**: Dynamically load and render content using the Fetch API and Handlebars.js.
   - Handlebars.js for server-side and client-side templating.
   - Alpine.js for adding interactivity without heavy frameworks.
   - Tailwind CSS for rapid, responsive styling.
   - Fetch API for seamless communication with the backend.

3. **DevOps**:
   - Docker for consistent development and deployment environments.
   - GitHub Actions for automated testing and deployment.
   - DigitalOcean for scalable, production-ready hosting.

4. **Environment Management**:
   - Uses a `.venv` virtual environment to manage Python dependencies.
   - Includes `setup.cfg` and `setup.py` for dependency management and project configuration.
