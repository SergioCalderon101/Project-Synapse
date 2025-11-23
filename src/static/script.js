document.addEventListener("DOMContentLoaded", () => {
    // Configuración de constantes
    const CONFIG = {
        DEFAULT_MODEL: 'gpt-3.5-turbo',
        STORAGE_KEY: 'selectedModel',
        MESSAGE_TYPES: {
            USER: 'usuario',
            BOT: 'bot',
            ERROR: 'error'
        },
        TOAST_DURATION: 3000,
        MODEL_NAMES: {
            'gpt-3.5-turbo': 'GPT-3.5 Turbo',
            'gpt-4o-mini': 'GPT-4o Mini',
            'gpt-4o': 'GPT-4o',
            'gpt-4': 'GPT-4'
        }
    };

    // Configurar Marked.js
    marked.setOptions({
        highlight: (code, lang) => {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(code, { language: lang }).value;
                } catch (e) {
                    console.error('Error highlighting code:', e);
                }
            }
            return hljs.highlightAuto(code).value;
        },
        breaks: true,
        gfm: true
    });

    // Cache de elementos DOM
    const elements = {
        userInput: document.getElementById("user-input"),
        sendButton: document.getElementById("send-btn"),
        chatLog: document.getElementById("chat-log"),
        welcomeMessage: document.getElementById("welcome-message"),
        newChatButton: document.querySelector(".new-chat-btn"),
        chatHistoryNav: document.querySelector(".chat-history"),
        settingsToggle: document.getElementById("settings-toggle"),
        settingsPanel: document.getElementById("settings-panel"),
        currentModelText: document.getElementById("current-model-text"),
        modelOptions: document.querySelectorAll('.model-option'),
        modelRadios: document.querySelectorAll('input[name="modelo"]'),
        deleteModal: document.getElementById("delete-modal"),
        modalTitle: document.getElementById("modal-chat-title"),
        modalCancel: document.getElementById("modal-cancel"),
        modalConfirm: document.getElementById("modal-confirm"),
        loadingOverlay: document.getElementById("loading-overlay")
    };

    // Estado de la aplicación
    const state = {
        currentChatId: null,
        isLoading: false,
        selectedModel: localStorage.getItem(CONFIG.STORAGE_KEY) || CONFIG.DEFAULT_MODEL,
        settingsOpen: false,
        pendingDelete: null
    };

    const UI = {
        getMessageClass(type) {
            const classes = {
                [CONFIG.MESSAGE_TYPES.USER]: 'user-message',
                [CONFIG.MESSAGE_TYPES.BOT]: 'bot-message',
                [CONFIG.MESSAGE_TYPES.ERROR]: 'error-message'
            };
            return classes[type] || 'message';
        },

        renderBotContent(content) {
            try {
                const htmlContent = marked.parse(content);
                return { html: htmlContent, isRendered: true };
            } catch (e) {
                console.error('Error parsing markdown:', e);
                return { html: content, isRendered: false };
            }
        },

        createMessageElement(type, content, isHTML = false) {
            const messageWrapper = document.createElement("div");
            messageWrapper.className = `message ${this.getMessageClass(type)}`;

            const messageContentDiv = document.createElement("div");
            messageContentDiv.className = "message-content";

            if (type === CONFIG.MESSAGE_TYPES.BOT && !isHTML) {
                const { html, isRendered } = this.renderBotContent(content);
                messageContentDiv.innerHTML = html;
                
                if (isRendered) {
                    messageContentDiv.querySelectorAll('pre code').forEach(block => {
                        hljs.highlightElement(block);
                    });
                }
            } else {
                messageContentDiv[isHTML ? 'innerHTML' : 'textContent'] = content;
            }

            if (type === CONFIG.MESSAGE_TYPES.ERROR) {
                const errorIcon = document.createElement("i");
                errorIcon.className = 'bx bx-error-circle';
                messageContentDiv.prepend(errorIcon);
            }

            messageWrapper.appendChild(messageContentDiv);
            return messageWrapper;
        },

        showTypingIndicator() {
            const typingDiv = document.createElement("div");
            typingDiv.className = "message bot-message typing-indicator";
            typingDiv.id = "typing-indicator";
            typingDiv.innerHTML = `
                <div class="message-content">
                    <div class="dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            elements.chatLog.appendChild(typingDiv);
            this.scrollToBottom();
        },

        removeTypingIndicator() {
            document.getElementById("typing-indicator")?.remove();
        },

        clearChatLog() {
            elements.chatLog.innerHTML = '';
            elements.welcomeMessage?.style.setProperty('display', 'flex');
            elements.userInput.value = "";
            elements.userInput.style.height = 'auto';
        },

        addMessageToLog(type, content, isHTML = false) {
            if (elements.welcomeMessage?.style.display !== 'none') {
                elements.welcomeMessage.style.display = 'none';
            }

            const messageElement = this.createMessageElement(type, content, isHTML);
            elements.chatLog.appendChild(messageElement);

            requestAnimationFrame(() => {
                messageElement.classList.add('message-visible');
            });

            this.scrollToBottom();
        },

        scrollToBottom(smooth = true) {
            elements.chatLog.scrollTo({
                top: elements.chatLog.scrollHeight,
                behavior: smooth ? 'smooth' : 'auto'
            });
        },

        setLoadingState(loading) {
            state.isLoading = loading;
            elements.userInput.disabled = loading;
            elements.sendButton.disabled = loading;

            if (loading) {
                elements.sendButton.innerHTML = "<i class='bx bx-loader-alt bx-spin'></i>";
            } else {
                elements.sendButton.innerHTML = "<i class='bx bxs-send'></i>";
                elements.userInput.focus();
            }
        },

        showLoadingOverlay(show, message = 'Procesando...') {
            if (show) {
                elements.loadingOverlay.querySelector('p').textContent = message;
                elements.loadingOverlay.classList.add('active');
            } else {
                elements.loadingOverlay.classList.remove('active');
            }
        },

        getToastIcon(type) {
            const icons = {
                success: 'bx-check-circle',
                error: 'bx-error-circle',
                info: 'bx-info-circle'
            };
            return icons[type] || icons.info;
        },

        showToast(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.innerHTML = `
                <i class='bx ${this.getToastIcon(type)}'></i>
                <span>${message}</span>
            `;
            document.body.appendChild(toast);

            requestAnimationFrame(() => toast.classList.add('toast-visible'));

            setTimeout(() => {
                toast.classList.remove('toast-visible');
                setTimeout(() => toast.remove(), 300);
            }, CONFIG.TOAST_DURATION);
        },

        adjustTextareaHeight() {
            elements.userInput.style.height = 'auto';
            elements.userInput.style.height = (elements.userInput.scrollHeight) + 'px';
        },

        toggleSettings() {
            state.settingsOpen = !state.settingsOpen;

            if (state.settingsOpen) {
                elements.settingsPanel.classList.add('open');
                elements.settingsToggle.classList.add('active');
            } else {
                elements.settingsPanel.classList.remove('open');
                elements.settingsToggle.classList.remove('active');
            }
        },

        showDeleteModal(chatId, chatTitle) {
            state.pendingDelete = { chatId, chatTitle };
            elements.modalTitle.textContent = chatTitle;
            elements.deleteModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        },

        hideDeleteModal() {
            elements.deleteModal.classList.remove('active');
            document.body.style.overflow = '';
            state.pendingDelete = null;
        },

        updateModelDisplay() {
            elements.currentModelText.textContent = CONFIG.MODEL_NAMES[state.selectedModel] || state.selectedModel;
        },

        initializeModelSelection() {
            const savedModel = state.selectedModel;
            const radioToCheck = document.querySelector(`input[name="modelo"][value="${savedModel}"]`);

            if (radioToCheck) {
                radioToCheck.checked = true;
            }

            this.updateModelDisplay();
        }
    };

    const History = {
        async loadList() {
            if (!elements.chatHistoryNav) return;

            const previouslyActiveId = state.currentChatId;
            let historyData = [];

            try {
                const response = await fetch("/api/v1/history");
                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const data = await response.json();
                historyData = data.history || [];

                this.renderHistory(historyData);

                if (historyData.length === 0) {
                    if (elements.welcomeMessage) {
                        elements.welcomeMessage.style.display = 'flex';
                    }
                }
            } catch (error) {
                console.error("Error cargando historial:", error);
                elements.chatHistoryNav.innerHTML = '<span class="history-error">Error al cargar historial</span>';
                if (previouslyActiveId) state.currentChatId = previouslyActiveId;
            }

            return historyData;
        },

        renderHistory(historyData) {
            elements.chatHistoryNav.innerHTML = '';

            historyData.forEach(chat => {
                const itemContainer = this.createHistoryItem(chat);
                elements.chatHistoryNav.appendChild(itemContainer);

                if (state.currentChatId === chat.id) {
                    itemContainer.querySelector('.history-item')?.classList.add('active');
                }
            });
        },

        createHistoryItem(chat) {
            const itemContainer = document.createElement("div");
            itemContainer.className = "history-item-container";

            const link = document.createElement("a");
            link.href = "#";
            link.className = "history-item";
            link.textContent = chat.title || `Chat ${chat.id.substring(0, 8)}`;
            link.dataset.chatId = chat.id;

            link.addEventListener("click", async (e) => {
                e.preventDefault();
                if (state.isLoading || state.currentChatId === chat.id) return;
                
                await Chat.load(chat.id);
                document.querySelectorAll('.history-item.active').forEach(el => el.classList.remove('active'));
                link.classList.add('active');
            });

            const deleteButton = document.createElement("button");
            deleteButton.className = "delete-chat-btn";
            deleteButton.innerHTML = "&times;";
            deleteButton.title = "Borrar este chat";
            deleteButton.dataset.chatId = chat.id;

            deleteButton.addEventListener("click", (e) => {
                e.stopPropagation();
                if (!state.isLoading) {
                    UI.showDeleteModal(chat.id, link.textContent);
                }
            });

            itemContainer.append(link, deleteButton);
            return itemContainer;
        },

        async delete(chatId, itemElement) {
            if (state.isLoading) return;

            UI.setLoadingState(true);
            UI.showLoadingOverlay(true, 'Eliminando chat...');

            try {
                const response = await fetch(`/api/v1/chat/${chatId}`, { method: 'DELETE' });
                
                if (!response.ok) {
                    const errorMsg = await this.extractErrorMessage(response);
                    throw new Error(errorMsg);
                }

                itemElement.remove();
                UI.showToast('Chat eliminado correctamente', 'success');

                await this.handlePostDelete(chatId);
            } catch (error) {
                console.error("Error borrando chat:", error);
                UI.showToast(`No se pudo borrar: ${error.message}`, 'error');
            } finally {
                UI.setLoadingState(false);
                UI.showLoadingOverlay(false);
            }
        },

        async extractErrorMessage(response) {
            let errorMsg = `Error HTTP ${response.status}`;
            try {
                const data = await response.json();
                errorMsg = data.error || errorMsg;
            } catch (e) { 
                // Si falla el parse, usa el mensaje por defecto
            }
            return errorMsg;
        },

        async handlePostDelete(chatId) {
            if (state.currentChatId === chatId) {
                state.currentChatId = null;
                UI.clearChatLog();

                const remainingHistory = await this.loadList();
                
                if (remainingHistory.length > 0) {
                    const firstChatId = remainingHistory[0].id;
                    await Chat.load(firstChatId);
                    const firstLink = elements.chatHistoryNav.querySelector(`.history-item[data-chat-id="${firstChatId}"]`);
                    firstLink?.classList.add('active');
                } else {
                    elements.welcomeMessage?.style.setProperty('display', 'flex');
                }
            } else {
                await this.loadList();
            }
        }
    };

    const Chat = {
        async startNew() {
            if (state.isLoading) return;

            UI.setLoadingState(true);
            UI.clearChatLog();

            try {
                const response = await fetch("/api/v1/chat", { method: "POST" });
                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const data = await response.json();
                state.currentChatId = data.chat_id;

                await History.loadList();
                const newLink = elements.chatHistoryNav.querySelector(`.history-item[data-chat-id="${state.currentChatId}"]`);
                newLink?.classList.add('active');
            } catch (error) {
                console.error("Error en startNewChat:", error);
                UI.addMessageToLog(CONFIG.MESSAGE_TYPES.ERROR, `No se pudo iniciar chat: ${error.message}`);
                state.currentChatId = null;
            } finally {
                UI.setLoadingState(false);
            }
        },

        async load(chatId) {
            if (state.isLoading) return;

            UI.setLoadingState(true);
            UI.showLoadingOverlay(true, 'Cargando chat...');
            UI.clearChatLog();

            try {
                const response = await fetch(`/api/v1/chat/${chatId}`);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const data = await response.json();
                state.currentChatId = data.chat_id;

                this.renderMessages(data.messages);
                UI.scrollToBottom(false);
            } catch (error) {
                console.error("Error cargando chat:", error);
                UI.showToast(`Error al cargar chat: ${error.message}`, 'error');
                state.currentChatId = null;
            } finally {
                UI.setLoadingState(false);
                UI.showLoadingOverlay(false);
                this.updateActiveHistoryItem(chatId);
            }
        },

        renderMessages(messages) {
            if (!messages || messages.length === 0) return;

            messages.forEach(msg => {
                if (msg.role !== 'system') {
                    const messageType = msg.role === 'user' ? CONFIG.MESSAGE_TYPES.USER : CONFIG.MESSAGE_TYPES.BOT;
                    UI.addMessageToLog(messageType, msg.content, false);
                }
            });
        },

        updateActiveHistoryItem(chatId) {
            document.querySelectorAll('.history-item.active').forEach(el => el.classList.remove('active'));
            const activeLink = elements.chatHistoryNav.querySelector(`.history-item[data-chat-id="${chatId}"]`);
            activeLink?.classList.add('active');
        },

        async sendMessage() {
            const messageText = elements.userInput.value.trim();

            if (!messageText || state.isLoading) return;

            if (!state.currentChatId) {
                await this.startNew();
                if (!state.currentChatId) return;
            }

            const currentText = messageText;
            this.resetInput();

            UI.setLoadingState(true);
            UI.addMessageToLog(CONFIG.MESSAGE_TYPES.USER, currentText, false);
            UI.showTypingIndicator();

            try {
                const data = await this.sendMessageRequest(currentText);
                UI.removeTypingIndicator();
                UI.addMessageToLog(CONFIG.MESSAGE_TYPES.BOT, data.respuesta || "No se recibió respuesta.", false);
                await History.loadList();
            } catch (error) {
                console.error("Error en sendMessage:", error);
                UI.removeTypingIndicator();
                UI.showToast(error.message || "Error de conexión", 'error');
            } finally {
                UI.setLoadingState(false);
                UI.adjustTextareaHeight();
            }
        },

        resetInput() {
            elements.userInput.value = "";
            elements.userInput.style.height = 'auto';
        },

        async sendMessageRequest(messageText) {
            const requestBody = { 
                mensaje: messageText,
                ...(state.selectedModel && { modelo: state.selectedModel })
            };

            const response = await fetch(`/api/v1/chat/${state.currentChatId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const errorMsg = await History.extractErrorMessage(response);
                throw new Error(errorMsg);
            }

            return await response.json();
        }
    };

    // Event Listeners
    const EventHandlers = {
        setupMessageInput() {
            elements.sendButton.addEventListener("click", () => Chat.sendMessage());

            elements.userInput.addEventListener("keydown", (e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    Chat.sendMessage();
                }
            });

            elements.userInput.addEventListener('input', () => UI.adjustTextareaHeight());
        },

        setupNavigation() {
            elements.newChatButton?.addEventListener("click", () => Chat.startNew());
            elements.settingsToggle?.addEventListener("click", () => UI.toggleSettings());
        },

        setupModal() {
            elements.modalCancel.addEventListener('click', () => UI.hideDeleteModal());

            elements.modalConfirm.addEventListener('click', async () => {
                if (!state.pendingDelete || state.isLoading) return;

                const { chatId } = state.pendingDelete;
                UI.hideDeleteModal();

                const itemElement = elements.chatHistoryNav
                    .querySelector(`.history-item[data-chat-id="${chatId}"]`)
                    ?.parentElement;
                
                if (itemElement) {
                    await History.delete(chatId, itemElement);
                }
            });

            elements.deleteModal.addEventListener('click', (e) => {
                if (e.target === elements.deleteModal) {
                    UI.hideDeleteModal();
                }
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && elements.deleteModal.classList.contains('active')) {
                    UI.hideDeleteModal();
                }
            });
        },

        setupModelSelection() {
            elements.modelOptions.forEach(option => {
                option.addEventListener('click', function () {
                    const radio = this.querySelector('input[type="radio"]');
                    if (radio) {
                        radio.checked = true;
                        state.selectedModel = radio.value;
                        localStorage.setItem(CONFIG.STORAGE_KEY, radio.value);
                        UI.updateModelDisplay();
                    }
                });
            });

            elements.modelRadios.forEach(radio => {
                radio.addEventListener('change', function () {
                    if (this.checked) {
                        state.selectedModel = this.value;
                        localStorage.setItem(CONFIG.STORAGE_KEY, this.value);
                        UI.updateModelDisplay();
                    }
                });
            });
        },

        init() {
            this.setupMessageInput();
            this.setupNavigation();
            this.setupModal();
            this.setupModelSelection();
        }
    };

    // Inicialización de la aplicación
    async function initializeApp() {
        UI.initializeModelSelection();
        EventHandlers.init();

        const initialHistory = await History.loadList();
        const mostRecentChatLink = elements.chatHistoryNav.querySelector('.history-item');

        if (mostRecentChatLink) {
            await Chat.load(mostRecentChatLink.dataset.chatId);
        } else {
            elements.welcomeMessage?.style.setProperty('display', 'flex');
        }
    }

    initializeApp();
});