import { getElement, querySelectorAll, addClass, removeClass, toggleClass, querySelector } from '../../utils/dom.js';
import { CONFIG } from '../../config/app.config.js';

/**
 * Settings view for rendering settings UI
 * Handles all settings-related UI rendering
 * 
 * To test: Mock DOM elements and verify rendering methods work correctly
 */
export class SettingsView {
    /**
     * Create SettingsView
     * @param {Object} elements - DOM element references
     */
    constructor(elements) {
        this.elements = elements;
    }

    /**
     * Update model display text
     * @param {string} model - Model identifier
     */
    updateModelDisplay(model) {
        if (this.elements.currentModelText) {
            const displayName = CONFIG.MODEL_NAMES[model] || model;
            this.elements.currentModelText.textContent = displayName;
        }
    }

    /**
     * Initialize model selection based on saved model
     * @param {string} savedModel - Saved model identifier
     */
    initializeModelSelection(savedModel) {
        const radioToCheck = querySelector(
            `input[name="modelo"][value="${savedModel}"]`
        );

        if (radioToCheck) {
            radioToCheck.checked = true;
        }

        this.updateModelDisplay(savedModel);
    }

    /**
     * Toggle settings panel
     * @param {boolean} open - Whether to open or close
     */
    togglePanel(open) {
        if (open) {
            addClass(this.elements.settingsPanel, 'open');
            addClass(this.elements.settingsToggle, 'active');
        } else {
            removeClass(this.elements.settingsPanel, 'open');
            removeClass(this.elements.settingsToggle, 'active');
        }
    }

    /**
     * Setup event listeners for settings
     * @param {Function} onModelChange - Callback when model changes
     */
    setupEventListeners(onModelChange) {
        // Model option clicks
        this.elements.modelOptions?.forEach(option => {
            option.addEventListener('click', function () {
                const radio = this.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                    onModelChange(radio.value);
                }
            });
        });

        // Radio button changes
        this.elements.modelRadios?.forEach(radio => {
            radio.addEventListener('change', function () {
                if (this.checked) {
                    onModelChange(this.value);
                }
            });
        });
    }
}
