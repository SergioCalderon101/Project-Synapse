import { getElement, addClass, removeClass } from '../utils/dom.js';

/**
 * Modal component for confirmations
 * Reusable modal dialog
 * 
 * To test: Create instance, call show() and verify DOM changes
 */
export class Modal {
    /**
     * Create Modal component
     * @param {string} modalId - ID of the modal element
     * @param {string} titleId - ID of the title element
     * @param {string} cancelBtnId - ID of cancel button
     * @param {string} confirmBtnId - ID of confirm button
     */
    constructor(modalId, titleId, cancelBtnId, confirmBtnId) {
        this.modal = getElement(modalId);
        this.titleElement = getElement(titleId);
        this.cancelBtn = getElement(cancelBtnId);
        this.confirmBtn = getElement(confirmBtnId);
        
        this.onConfirm = null;
        this.onCancel = null;
        
        this.setupEventListeners();
    }

    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Cancel button
        this.cancelBtn?.addEventListener('click', () => this.hide());
        
        // Confirm button
        this.confirmBtn?.addEventListener('click', () => {
            if (this.onConfirm) {
                this.onConfirm();
            }
            this.hide();
        });
        
        // Click outside to close
        this.modal?.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hide();
            }
        });
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal?.classList.contains('active')) {
                this.hide();
            }
        });
    }

    /**
     * Show the modal
     * @param {string} title - Modal title
     * @param {Function} [onConfirm] - Callback for confirm action
     * @param {Function} [onCancel] - Callback for cancel action
     */
    show(title, onConfirm = null, onCancel = null) {
        if (this.titleElement) {
            this.titleElement.textContent = title;
        }
        
        this.onConfirm = onConfirm;
        this.onCancel = onCancel;
        
        addClass(this.modal, 'active');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Hide the modal
     */
    hide() {
        removeClass(this.modal, 'active');
        document.body.style.overflow = '';
        
        if (this.onCancel) {
            this.onCancel();
        }
        
        this.onConfirm = null;
        this.onCancel = null;
    }
}
