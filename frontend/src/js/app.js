import { loginController } from './controllers/login.js';
import './controllers/menu.js'; // Import early for dark mode initialization

export const createSpaApp = () => {
    // Create the app object with all the necessary properties
    const app = {
        // UI state
        sidebarOpen: window.innerWidth >= 1024, // Desktop should have sidebar open by default

        async loadPage(elementIdTarget, templatePath, controllerPath = null) {
            // Load template
            const response = await fetch(templatePath);
            const template = await response.text();
            document.getElementById(elementIdTarget).innerHTML = template;

            // Load controller if specified
            if (controllerPath) {
                try {
                    const module = await import(controllerPath);
                    // Get the first exported object from the module
                    const controller = Object.values(module)[0];
                    if (controller && typeof controller === 'object') {
                        // Merge controller methods with current app instance
                        Object.assign(this, controller);
                        
                        // Call init method if it exists
                        if (typeof this.init === 'function') {
                            this.init();
                        }
                    }
                } catch (err) {
                    console.error('Failed to load controller:', err);
                }
            }
        }
    };
    
    // Initialize the app with login controller methods
    Object.assign(app, loginController);
    
    return app;
}; 