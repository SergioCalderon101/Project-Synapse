import { createElement, addClass, removeClass, nextFrame } from '../utils/dom.js';
import { CONFIG } from '../config/app.config.js';

/**
 * Toast notification component
 * Shows temporary notifications
 * 
 * To test: Create instance, call show() and verify toast appears and disappears
 */
export class Toast {
    /**
     * Create Toast component
     */
    constructor() {
        this.duration = CONFIG.TOAST_DURATION;
    }

    /**
     * Get icon class for toast type
     * @param {string} type - Toast type (success, error, info)
     * @returns {string} Icon class
     * @private
     */
    getIconClass(type) {
        const icons = {
            success: 'bx-check-circle',
            error: 'bx-error-circle',
            info: 'bx-info-circle'
        };
        return icons[type] || icons.info;
    }

    /**
     * Show toast notification
     * @param {string} message - Message to display
     * @param {string} [type='info'] - Toast type (success, error, info)
     * @param {number} [duration] - Duration in ms (optional, uses default if not provided)
     */
    show(message, type = 'info', duration = null) {
        const toastDuration = duration || this.duration;
        
        const toast = createElement('div', {
            className: `toast toast-${type}`,
            innerHTML: `
                <i class='bx ${this.getIconClass(type)}'></i>
                <span>${message}</span>
            `
        });
        
        document.body.appendChild(toast);

        // Trigger animation
        nextFrame().then(() => {
            addClass(toast, 'toast-visible');
        });

        // Auto-dismiss
        setTimeout(() => {
            removeClass(toast, 'toast-visible');
            setTimeout(() => toast.remove(), 300);
        }, toastDuration);
    }

    /**
     * Show success toast
     * @param {string} message - Message to display
     */
    success(message) {
        this.show(message, 'success');
    }

    /**
     * Show error toast
     * @param {string} message - Message to display
     */
    error(message) {
        this.show(message, 'error');
    }

    /**
     * Show info toast
     * @param {string} message - Message to display
     */
    info(message) {
        this.show(message, 'info');
    }
}
