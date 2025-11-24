import { SettingsView } from './SettingsView.js';

/**
 * Settings controller for business logic
 * Coordinates between SettingsView and AppState
 * 
 * To test: Mock SettingsView and AppState, verify controller orchestrates correctly
 */
export class SettingsController {
    /**
     * Create SettingsController
     * @param {SettingsView} settingsView - Settings view instance
     * @param {Object} appState - Application state
     */
    constructor(settingsView, appState) {
        this.view = settingsView;
        this.appState = appState;
    }

    /**
     * Initialize settings
     */
    initialize() {
        const savedModel = this.appState.getSelectedModel();
        this.view.initializeModelSelection(savedModel);
        this.view.setupEventListeners((model) => this.handleModelChange(model));
    }

    /**
     * Handle model change
     * @param {string} model - New model identifier
     * @private
     */
    handleModelChange(model) {
        this.appState.setSelectedModel(model);
        this.view.updateModelDisplay(model);
    }

    /**
     * Toggle settings panel
     */
    toggle() {
        this.appState.toggleSettings();
        this.view.togglePanel(this.appState.areSettingsOpen());
    }
}
