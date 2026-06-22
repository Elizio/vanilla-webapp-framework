import Alpine from 'alpinejs';
import '../styles/main.css';
import { createSpaApp } from './app.js';

window.Alpine = Alpine;
window.spaApp = createSpaApp();
Alpine.start();
window.spaApp.bootApp();
