import { loginController } from './controllers/login.js';
import './controllers/menu.js'; // Import early for dark mode initialization

export const createSpaApp = () => {
    // Create the app object with all the necessary properties
    const app = {
        // UI state
        sidebarOpen: window.innerWidth >= 1024, // Desktop should have sidebar open by default
        currentPage: {}, // Object to hold the current page's state and methods

        async loadPage(elementIdTarget, templatePath, controllerPath = null, controllerName = null) {
            // Load template
            const response = await fetch(templatePath);
            const template = await response.text();
            document.getElementById(elementIdTarget).innerHTML = template;

            // Load controller if specified
            if (controllerPath && controllerName) {
                try {
                    const module = await import(controllerPath);
                    // Get the named export from the module
                    const controller = module[controllerName];
                    if (controller && typeof controller === 'object') {
                        // Assign a copy of the controller to currentPage
                        this.currentPage = Object.assign({}, controller);
                        
                        // Call init method on the currentPage context if it exists
                        if (typeof this.currentPage.init === 'function') {
                            // Pass the main app context ('this') to the init function
                            this.currentPage.init(this);
                        }
                    } else {
                        console.warn(`Controller '${controllerName}' not found or not an object in ${controllerPath}`);
                        this.currentPage = {}; // Clear current page state if controller fails
                    }
                } catch (err) {
                    console.error(`Failed to load controller '${controllerName}' from ${controllerPath}:`, err);
                    this.currentPage = {}; // Clear current page state on error
                }
            } else {
                // No controller specified, clear current page state
                this.currentPage = {};
            }
        },

        // Add the global logout function here
        logout() {
            localStorage.removeItem('token');
            this.isLoggedIn = false;
            this.token = null; 
            this.currentPage = {}; // Clear current page state
            // Optionally, reload the login page immediately
            this.loadPage('login-register-container', '/templates/partials/login.hbs', '/js/controllers/login.js', 'loginController');
            this.loadPage('view-container', ''); // Clear main view
            // Or maybe redirect to root which should show login state
            // window.location.href = '/';
        }
    };
    
    // // Initialize the app with login controller methods - REMOVED, handled by x-init now
    // Object.assign(app, loginController); 
    
    return app;
}; 