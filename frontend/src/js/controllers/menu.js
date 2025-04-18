// Apply dark mode before Alpine initializes to prevent flicker
const isDarkMode = localStorage.getItem('darkMode') === 'true';
if (isDarkMode) {
    document.documentElement.classList.add('dark');
} else {
    document.documentElement.classList.remove('dark');
}

export const menuController = {
    // Initialize with default values
    sidebarOpen: false,
    darkMode: false,

    init() { // Remove appContext parameter to avoid recursion
        // Check if this is desktop size and keep sidebar open
        if (typeof window !== 'undefined' && window.innerWidth >= 1024) {
            this.sidebarOpen = true;
        }
        
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
            if (localStorage.getItem('darkMode') === null) {
                this.darkMode = e.matches;
                localStorage.setItem('darkMode', this.darkMode);
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
