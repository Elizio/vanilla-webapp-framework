import Alpine from 'alpinejs';
import Handlebars from 'handlebars';
import '../styles/main.css';
import { createAppState } from './state.js';

// Register Handlebars helpers
Handlebars.registerHelper('json', function(context) {
    return JSON.stringify(context, null, 2);
});

// Initialize Alpine.js
window.Alpine = Alpine;
window.appState = createAppState();
Alpine.start(); 