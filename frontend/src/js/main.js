import Alpine from 'alpinejs';
import '../styles/main.css';
import { createSpaApp } from './app.js';

window.Alpine = Alpine;

document.addEventListener('alpine:init', () => {
    Alpine.data('spaApp', () => createSpaApp());
});

Alpine.start();
