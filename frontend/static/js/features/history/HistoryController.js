import { HistoryService } from '../../services/HistoryService.js';
import { ChatService } from '../../services/ChatService.js';
import { HistoryView } from './HistoryView.js';

/**
 * History controller for business logic
 * Coordinates between HistoryService and HistoryView
 * 
 * To test: Mock HistoryService and HistoryView, verify controller orchestrates correctly
 */
export class HistoryController {
    /**
     * Create HistoryController
     * @param {HistoryService} historyService - History service instance
     * @param {ChatService} chatService - Chat service instance
     * @param {HistoryView} historyView - History view instance
     * @param {Object} appState - Application state
     * @param {Object} toast - Toast notification component
     * @param {Object} loadingOverlay - Loading overlay component
     * @param {Object} chatController - Chat controller for loading chats
     */
    constructor(historyService, chatService, historyView, appState, toast, loadingOverlay, chatController) {
        this.historyService = historyService;
        this.chatService = chatService;
        this.view = historyView;
        this.appState = appState;
        this.toast = toast;
        this.loadingOverlay = loadingOverlay;
        this.chatController = chatController;
    }

    /**
     * Load and display history
     * @returns {Promise<Array>} History data
     */
    async load() {
        const previouslyActiveId = this.appState.getCurrentChatId();
        let historyData = [];

        try {
            const data = await this.historyService.loadHistory();
            historyData = data.history || [];

            this.view.render(
                historyData,
                this.appState.getCurrentChatId(),
                (chatId, link) => this.handleItemClick(chatId, link),
                (chatId, title, itemElement) => this.handleDeleteClick(chatId, title, itemElement)
            );
        } catch (error) {
            console.error("Error loading history:", error);
            this.view.showError('Error al cargar historial');
            if (previouslyActiveId) {
                this.appState.setCurrentChatId(previouslyActiveId);
            }
        }

        return historyData;
    }

    /**
     * Handle history item click
     * @param {string} chatId - Chat ID
     * @param {HTMLElement} link - Link element clicked
     * @private
     */
    async handleItemClick(chatId, link) {
        if (this.appState.isLoadingState() || this.appState.getCurrentChatId() === chatId) {
            return;
        }

        await this.chatController.load(chatId);
        this.view.updateActiveItem(chatId);
    }

    /**
     * Handle delete button click
     * @param {string} chatId - Chat ID
     * @param {string} title - Chat title
     * @param {HTMLElement} itemElement - Item element
     * @private
     */
    handleDeleteClick(chatId, title, itemElement) {
        if (!this.appState.isLoadingState()) {
            // Store for later use in delete confirmation
            this.pendingDeleteElement = itemElement;
            // Emit event for modal to show
            this.onDeleteRequested?.(chatId, title);
        }
    }

    /**
     * Delete a chat
     * @param {string} chatId - Chat ID to delete
     * @returns {Promise<void>}
     */
    async delete(chatId) {
        if (this.appState.isLoadingState()) return;

        this.appState.setLoading(true);
        this.loadingOverlay.show('Eliminando chat...');

        try {
            await this.chatService.deleteChat(chatId);

            // Remove from UI
            const itemElement = this.pendingDeleteElement || this.view.getItemElement(chatId);
            itemElement?.remove();
            
            this.toast.success('Chat eliminado correctamente');

            await this.handlePostDelete(chatId);
        } catch (error) {
            console.error("Error deleting chat:", error);
            this.toast.error(`No se pudo borrar: ${error.message}`);
        } finally {
            this.appState.setLoading(false);
            this.loadingOverlay.hide();
            this.pendingDeleteElement = null;
        }
    }

    /**
     * Handle actions after delete
     * @param {string} deletedChatId - ID of deleted chat
     * @private
     */
    async handlePostDelete(deletedChatId) {
        if (this.appState.getCurrentChatId() === deletedChatId) {
            this.appState.setCurrentChatId(null);
            
            // Clear chat view
            if (this.chatController.view) {
                this.chatController.view.clearChatLog();
            }

            const remainingHistory = await this.load();

            if (remainingHistory.length > 0) {
                const firstChatId = remainingHistory[0].id;
                await this.chatController.load(firstChatId);
                this.view.updateActiveItem(firstChatId);
            }
        } else {
            await this.load();
        }
    }

    /**
     * Set callback for delete requested
     * @param {Function} callback - Callback function
     */
    setOnDeleteRequested(callback) {
        this.onDeleteRequested = callback;
    }
}
