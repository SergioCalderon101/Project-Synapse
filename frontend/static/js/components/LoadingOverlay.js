import { getElement, addClass, removeClass, querySelector } from '../utils/dom.js';

/**
 * Loading overlay component
 * Shows/hides full-screen loading overlay
 * 
 * To test: Create instance, call show() and verify overlay appears
 */
export class LoadingOverlay {
    /**
     * Create LoadingOverlay component
     * @param {string} overlayId - ID of the overlay element
     */
    constructor(overlayId) {
        this.overlay = getElement(overlayId);
        this.messageElement = querySelector('p', this.overlay);
    }

    /**
     * Show loading overlay
     * @param {string} [message='Procesando...'] - Loading message
     */
    show(message = 'Procesando...') {
        if (this.messageElement) {
            this.messageElement.textContent = message;
        }
        addClass(this.overlay, 'active');
    }

    /**
     * Hide loading overlay
     */
    hide() {
        removeClass(this.overlay, 'active');
    }
}
