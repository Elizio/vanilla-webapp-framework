// REMOVE initial dark mode check - Handled in init
// const isDarkMode = localStorage.getItem('darkMode') === 'true';
// if (isDarkMode) {
//     document.documentElement.classList.add('dark');
// } else {
//     document.documentElement.classList.remove('dark');
// }

export const menuController = {
    // REMOVE sidebarOpen - Use global one from app.js
    // sidebarOpen: true,
    darkMode: false,

    init(appContext) { // Accept appContext (though not strictly needed here now)
        this.appContext = appContext;
        // REMOVE sidebar check - Relies on global app state now
        // if (window.innerWidth >= 1024) { // lg breakpoint in Tailwind
        //     this.sidebarOpen = true;
        // }
        
        // Apply theme on initialization
        this.darkMode = localStorage.getItem('darkMode') === 'true';
        this.applyTheme();
        
        // Check for system preference if no local storage setting
        if (localStorage.getItem('darkMode') === null) {
            this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
            localStorage.setItem('darkMode', this.darkMode);
            this.applyTheme();
        }

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            // Only update if the user hasn't manually set it
            if (localStorage.getItem('darkMode') === null) {
                this.darkMode = e.matches;
                // Don't automatically set localStorage here, let user toggle override system
                // localStorage.setItem('darkMode', this.darkMode);
                this.applyTheme();
            }
        });
    },

    toggleDarkMode() {
        this.darkMode = !this.darkMode;
        localStorage.setItem('darkMode', this.darkMode);
        this.applyTheme();
    },

    applyTheme() {
        if (this.darkMode) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }
};
