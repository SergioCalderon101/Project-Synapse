import { Store } from './Store.js';
import { CONFIG } from '../config/app.config.js';

/**
 * Application state management
 * Manages the global application state
 */
export class AppState extends Store {
    /**
     * Create application state with initial values
     */
    constructor() {
        super({
            currentChatId: null,
            isLoading: false,
            selectedModel: localStorage.getItem(CONFIG.STORAGE_KEY) || CONFIG.DEFAULT_MODEL,
            settingsOpen: false,
            pendingDelete: null
        });
    }

    /**
     * Set current chat ID
     * @param {string|null} chatId - The chat ID or null
     */
    setCurrentChatId(chatId) {
        this.setState({ currentChatId: chatId });
    }

    /**
     * Get current chat ID
     * @returns {string|null} Current chat ID
     */
    getCurrentChatId() {
        return this.state.currentChatId;
    }

    /**
     * Set loading state
     * @param {boolean} loading - Whether app is loading
     */
    setLoading(loading) {
        this.setState({ isLoading: loading });
    }

    /**
     * Check if app is loading
     * @returns {boolean} Loading state
     */
    isLoadingState() {
        return this.state.isLoading;
    }

    /**
     * Set selected AI model
     * @param {string} model - Model identifier
     */
    setSelectedModel(model) {
        localStorage.setItem(CONFIG.STORAGE_KEY, model);
        this.setState({ selectedModel: model });
    }

    /**
     * Get selected model
     * @returns {string} Selected model
     */
    getSelectedModel() {
        return this.state.selectedModel;
    }

    /**
     * Toggle settings panel
     */
    toggleSettings() {
        this.setState({ settingsOpen: !this.state.settingsOpen });
    }

    /**
     * Check if settings are open
     * @returns {boolean} Settings open state
     */
    areSettingsOpen() {
        return this.state.settingsOpen;
    }

    /**
     * Set pending delete info
     * @param {Object|null} deleteInfo - Object with chatId and chatTitle, or null
     */
    setPendingDelete(deleteInfo) {
        this.setState({ pendingDelete: deleteInfo });
    }

    /**
     * Get pending delete info
     * @returns {Object|null} Pending delete info
     */
    getPendingDelete() {
        return this.state.pendingDelete;
    }
}
