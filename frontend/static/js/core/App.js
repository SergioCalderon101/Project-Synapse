import { configureMarked } from '../config/app.config.js';
import { AppState } from '../state/AppState.js';
import { HttpClient } from '../services/HttpClient.js';
import { ChatService } from '../services/ChatService.js';
import { HistoryService } from '../services/HistoryService.js';
import { Toast } from '../components/Toast.js';
import { LoadingOverlay } from '../components/LoadingOverlay.js';
import { Modal } from '../components/Modal.js';
import { ChatView } from '../features/chat/ChatView.js';
import { ChatController } from '../features/chat/ChatController.js';
import { HistoryView } from '../features/history/HistoryView.js';
import { HistoryController } from '../features/history/HistoryController.js';
import { SettingsView } from '../features/settings/SettingsView.js';
import { SettingsController } from '../features/settings/SettingsController.js';
import { getElement, querySelectorAll, querySelector } from '../utils/dom.js';

/**
 * Main application class
 * Initializes and coordinates all application components
 */
export class App {
    /**
     * Create and initialize the application
     */
    constructor() {
        this.elements = this.cacheElements();
        this.initializeComponents();
        this.setupEventHandlers();
    }

    /**
     * Cache DOM element references
     * @returns {Object} Object with all DOM element references
     * @private
     */
    cacheElements() {
        return {
            userInput: getElement('user-input'),
            sendButton: getElement('send-btn'),
            chatLog: getElement('chat-log'),
            welcomeMessage: getElement('welcome-message'),
            newChatButton: querySelector('.new-chat-btn'),
            chatHistoryNav: querySelector('.chat-history'),
            settingsToggle: getElement('settings-toggle'),
            settingsPanel: getElement('settings-panel'),
            currentModelText: getElement('current-model-text'),
            modelOptions: querySelectorAll('.model-option'),
            modelRadios: querySelectorAll('input[name="modelo"]'),
            deleteModal: getElement('delete-modal'),
            modalTitle: getElement('modal-chat-title'),
            modalCancel: getElement('modal-cancel'),
            modalConfirm: getElement('modal-confirm'),
            loadingOverlay: getElement('loading-overlay')
        };
    }

    /**
     * Initialize all application components
     * @private
     */
    initializeComponents() {
        // Configure libraries
        configureMarked();

        // Initialize state
        this.appState = new AppState();

        // Initialize services
        const httpClient = new HttpClient();
        this.chatService = new ChatService(httpClient);
        this.historyService = new HistoryService(httpClient);

        // Initialize components
        this.toast = new Toast();
        this.loadingOverlay = new LoadingOverlay('loading-overlay');
        this.modal = new Modal('delete-modal', 'modal-chat-title', 'modal-cancel', 'modal-confirm');

        // Initialize views
        this.chatView = new ChatView(this.elements);
        this.historyView = new HistoryView(this.elements);
        this.settingsView = new SettingsView(this.elements);

        // Initialize controllers
        this.chatController = new ChatController(
            this.chatService,
            this.chatView,
            this.appState,
            this.toast,
            this.loadingOverlay
        );

        this.historyController = new HistoryController(
            this.historyService,
            this.chatService,
            this.historyView,
            this.appState,
            this.toast,
            this.loadingOverlay,
            this.chatController
        );

        this.settingsController = new SettingsController(
            this.settingsView,
            this.appState
        );

        // Connect history delete to modal
        this.historyController.setOnDeleteRequested((chatId, title) => {
            this.modal.show(title, async () => {
                await this.historyController.delete(chatId);
            });
        });
    }

    /**
     * Setup event handlers
     * @private
     */
    setupEventHandlers() {
        // Send message
        this.elements.sendButton?.addEventListener('click', () => {
            const message = this.elements.userInput.value.trim();
            if (message) {
                this.chatController.sendMessage(message);
            }
        });

        // Send on Enter (but not Shift+Enter)
        this.elements.userInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const message = this.elements.userInput.value.trim();
                if (message) {
                    this.chatController.sendMessage(message);
                }
            }
        });

        // Auto-resize textarea
        this.elements.userInput?.addEventListener('input', () => {
            this.chatView.adjustTextareaHeight();
        });

        // New chat button
        this.elements.newChatButton?.addEventListener('click', async () => {
            await this.chatController.startNew();
            await this.historyController.load();
        });

        // Settings toggle
        this.elements.settingsToggle?.addEventListener('click', () => {
            this.settingsController.toggle();
        });
    }

    /**
     * Start the application
     * Loads initial data and sets up UI
     */
    async start() {
        // Initialize settings
        this.settingsController.initialize();

        // Load history
        const initialHistory = await this.historyController.load();

        // Load most recent chat if exists
        const mostRecentChat = initialHistory[0];
        if (mostRecentChat) {
            await this.chatController.load(mostRecentChat.id);
        } else if (this.elements.welcomeMessage) {
            this.elements.welcomeMessage.style.display = 'flex';
        }
    }
}
