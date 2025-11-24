import { ChatService } from '../../services/ChatService.js';
import { ChatView } from './ChatView.js';
import { CONFIG } from '../../config/app.config.js';
import { validateMessage } from '../../utils/validators.js';

/**
 * Chat controller for business logic
 * Coordinates between ChatService and ChatView
 * 
 * To test: Mock ChatService and ChatView, verify controller orchestrates correctly
 */
export class ChatController {
    /**
     * Create ChatController
     * @param {ChatService} chatService - Chat service instance
     * @param {ChatView} chatView - Chat view instance
     * @param {Object} appState - Application state
     * @param {Object} toast - Toast notification component
     * @param {Object} loadingOverlay - Loading overlay component
     */
    constructor(chatService, chatView, appState, toast, loadingOverlay) {
        this.chatService = chatService;
        this.view = chatView;
        this.appState = appState;
        this.toast = toast;
        this.loadingOverlay = loadingOverlay;
    }

    /**
     * Start a new chat
     * @returns {Promise<void>}
     */
    async startNew() {
        if (this.appState.isLoadingState()) return;

        this.appState.setLoading(true);
        this.view.setLoadingState(true);
        this.view.clearChatLog();

        try {
            const data = await this.chatService.createChat();
            this.appState.setCurrentChatId(data.chat_id);
        } catch (error) {
            console.error("Error starting new chat:", error);
            this.view.addMessage(CONFIG.MESSAGE_TYPES.ERROR, `No se pudo iniciar chat: ${error.message}`);
            this.appState.setCurrentChatId(null);
        } finally {
            this.appState.setLoading(false);
            this.view.setLoadingState(false);
        }
    }

    /**
     * Load an existing chat
     * @param {string} chatId - Chat ID to load
     * @returns {Promise<void>}
     */
    async load(chatId) {
        if (this.appState.isLoadingState()) return;

        this.appState.setLoading(true);
        this.view.setLoadingState(true);
        this.loadingOverlay.show('Cargando chat...');
        this.view.clearChatLog();

        try {
            const data = await this.chatService.loadChat(chatId);
            this.appState.setCurrentChatId(data.chat_id);
            this.view.renderMessages(data.messages);
            this.view.scrollToBottom(false);
        } catch (error) {
            console.error("Error loading chat:", error);
            this.toast.error(`Error al cargar chat: ${error.message}`);
            this.appState.setCurrentChatId(null);
        } finally {
            this.appState.setLoading(false);
            this.view.setLoadingState(false);
            this.loadingOverlay.hide();
        }
    }

    /**
     * Send a message
     * @param {string} messageText - Message to send
     * @returns {Promise<void>}
     */
    async sendMessage(messageText) {
        // Validate message
        const validation = validateMessage(messageText);
        if (!validation.valid) {
            this.toast.error(validation.error);
            return;
        }

        if (this.appState.isLoadingState()) return;

        // Create chat if needed
        if (!this.appState.getCurrentChatId()) {
            await this.startNew();
            if (!this.appState.getCurrentChatId()) return;
        }

        const currentText = messageText;
        this.view.clearInput();

        this.appState.setLoading(true);
        this.view.setLoadingState(true);
        this.view.addMessage(CONFIG.MESSAGE_TYPES.USER, currentText, false);
        this.view.showTypingIndicator();

        try {
            const model = this.appState.getSelectedModel();
            const data = await this.chatService.sendMessage(
                this.appState.getCurrentChatId(),
                currentText,
                model
            );
            
            this.view.removeTypingIndicator();
            this.view.addMessage(
                CONFIG.MESSAGE_TYPES.BOT,
                data.respuesta || "No se recibió respuesta.",
                false
            );
        } catch (error) {
            console.error("Error sending message:", error);
            this.view.removeTypingIndicator();
            this.toast.error(error.message || "Error de conexión");
        } finally {
            this.appState.setLoading(false);
            this.view.setLoadingState(false);
            this.view.adjustTextareaHeight();
        }
    }
}
