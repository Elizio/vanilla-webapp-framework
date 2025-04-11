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

        // Updated logout function
        logout() {
            localStorage.removeItem('token');
            // No need to manually update isLoggedIn, token, or currentPage here.
            // A full page reload will reset the entire application state based on the token's absence.
            window.location.href = '/'; // Redirect to root to force reload and re-initialization
        }
    };
    
    // // Initialize the app with login controller methods - REMOVED, handled by x-init now
    // Object.assign(app, loginController); 
    
    return app;
}; 