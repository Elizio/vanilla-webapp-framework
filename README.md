**"Help me build a modern SPA with these specifications:**  

### **Core Stack**  
- **Frontend**: Vanilla JS + Handlebars (templating) + Alpine.js (reactivity) + Tailwind CSS  
- **Build**: Vite (with Handlebars plugin)  
- **Routing**: Custom client-side router (History API) with:  
  - Route parameters (`/users/:id`)  
  - Guards (auth checks)  
  - Lazy loading  
- **Containerization**: Docker (multi-stage for frontend/backend)  

### **Backend Requirements**  
- **Framework**: Python/Flask  
- **Database**: SQLAlchemy (PostgreSQL)  
- **API**: RESTful + Swagger docs  
- **Auth**: JWT (stateless)  

### **Key Constraints**  
1. Zero heavy frameworks (React/Vue)  
2. Minimal dependencies  
3. Optimized for Docker deployment  

**Prioritize:**  
- Clean component architecture  
- Efficient DOM updates  
- Secure API communication  
- Smooth dev experience (Vite HMR + Flask reload)"  

---  
**Why this works:**  
- Gives the AI clear boundaries (vanilla JS + micro-libs)  
- Specifies critical integrations (Handlebars + Alpine)  
- Calls out key features without overspecifying implementation  
