/**
 * Main entry point for the application
 * Initializes the app when DOM is ready
 */
import { App } from './core/App.js';

/**
 * Initialize application on DOMContentLoaded
 */
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const app = new App();
        await app.start();
    } catch (error) {
        console.error('Failed to initialize application:', error);
    }
});
