**Goal**: Create a minimal but robust demo SPA showcasing:  
1. **Flask API** (1 protected route, 1 public route)  
2. **JWT auth** (login/logout)  
3. **Handlebars.js** dynamic rendering  
4. **Alpine.js** for interactivity  
5. **Tailwind CSS** styling  

**Requirements**:  
- **Backend**:  
  - Flask endpoint `/api/data` (protected, returns `{ "message": "Secure data" }`)  
  - Flask endpoint `/api/public` (public, returns `{ "info": "Hello world" }`)  
  - JWT auth with `/api/login` (POST username/password)  
  - SQLAlchemy `User` model (id, username, password_hash)  

- **Frontend**:  
  - Single `index.html` with:  
    - Login form (Alpine.js `x-data` for state)  
    - Button to fetch `/api/data` (shows alert if unauthorized)  
    - Dynamic content section (rendered via Handlebars.js)  
  - Handlebars template for API response display  
  - Tailwind for responsive layout (centered card, buttons)  

- **SPA Behavior**:  
  - No page reloads (use `fetch()` + Handlebars)  
  - Auto-redirect to login if JWT expires  

**Deliverables**:  
1. Flask app structure (`app.py`, `models.py`, `auth.py`)  
2. Frontend files (`index.html`, `static/js/app.js`, Handlebars template)  
3. Minimal Tailwind CSS (no custom CSS files)  
4. Docker-compose setup (Flask + PostgreSQL)  

**Constraints**:  
- Keep all logic in vanilla JS (no frameworks except Alpine.js)  
- Use Vite only for bundling (no React/Vue)  
- Document API with Swagger (Flasgger)  
- the solution MUST follows the project structure defined on @README.md  and also my cursor ai rules.