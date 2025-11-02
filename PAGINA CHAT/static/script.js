// --- script.js (v6.0 - Optimizado y limpio) ---
document.addEventListener("DOMContentLoaded", () => {
    // --- Elementos UI ---
    const elements = {
        userInput: document.getElementById("user-input"),
        sendButton: document.getElementById("send-btn"),
        chatLog: document.getElementById("chat-log"),
        welcomeMessage: document.getElementById("welcome-message"),
        newChatButton: document.querySelector(".new-chat-btn"),
        chatHistoryNav: document.querySelector(".chat-history"),
        modelSelector: document.getElementById("modelo-selector")
    };

    // --- Estado App ---
    let state = {
        currentChatId: null,
        isLoading: false
    };

    // --- Funciones UI ---
    const UI = {
        createMessageElement(type, content, isHTML = false) {
            const messageWrapper = document.createElement("div");
            messageWrapper.className = `message ${type === "usuario" ? "user-message" : type === "bot" ? "bot-message" : "error-message"}`;

            const messageContentDiv = document.createElement("div");
            messageContentDiv.className = "message-content";

            if (isHTML) {
                messageContentDiv.innerHTML = content;
            } else {
                messageContentDiv.textContent = content;
            }

            if (type === "error") {
                const errorLabel = document.createElement("strong");
                errorLabel.textContent = "Error: ";
                messageContentDiv.prepend(errorLabel);
            }

            messageWrapper.appendChild(messageContentDiv);
            return messageWrapper;
        },

        clearChatLog() {
            elements.chatLog.innerHTML = '';
            if (elements.welcomeMessage) {
                elements.welcomeMessage.style.display = 'flex';
            }
            elements.userInput.value = "";
            elements.userInput.style.height = 'auto';
        },

        addMessageToLog(type, content, isHTML = false) {
            if (elements.welcomeMessage && elements.welcomeMessage.style.display !== 'none') {
                elements.welcomeMessage.style.display = 'none';
            }
            const messageElement = this.createMessageElement(type, content, isHTML);
            elements.chatLog.appendChild(messageElement);
            elements.chatLog.scrollTop = elements.chatLog.scrollHeight;
        },

        setLoadingState(loading) {
            state.isLoading = loading;
            elements.userInput.disabled = loading;
            elements.sendButton.disabled = loading;
            if (!loading) {
                elements.userInput.focus();
            }
        },

        adjustTextareaHeight() {
            elements.userInput.style.height = 'auto';
            elements.userInput.style.height = (elements.userInput.scrollHeight) + 'px';
        }
    };

    // --- Funciones de Historia ---
    const History = {
        async loadList() {
            if (!elements.chatHistoryNav) return;
            console.log("Cargando historial...");

            const previouslyActiveId = state.currentChatId;
            let historyData = [];

            try {
                const response = await fetch("/history");
                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const data = await response.json();
                historyData = data.history || [];

                this.renderHistory(historyData);

                // Solo mostrar mensaje de bienvenida si no hay chats
                // No crear automáticamente un nuevo chat
                if (historyData.length === 0) {
                    console.log("No hay chats en el historial. Esperando input del usuario...");
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
                    itemContainer.querySelector('.history-item').classList.add('active');
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

            deleteButton.addEventListener("click", async (e) => {
                e.stopPropagation();
                if (state.isLoading) return;
                if (confirm(`¿Estás seguro de que quieres borrar el chat "${link.textContent}"?`)) {
                    await this.delete(chat.id, itemContainer);
                }
            });

            itemContainer.appendChild(link);
            itemContainer.appendChild(deleteButton);
            return itemContainer;
        },

        async delete(chatId, itemElement) {
            if (state.isLoading) return;

            UI.setLoadingState(true);
            console.log(`Intentando borrar chat: ${chatId}`);

            try {
                const response = await fetch(`/chat/${chatId}`, { method: 'DELETE' });
                if (!response.ok) {
                    let errorMsg = `Error HTTP ${response.status}`;
                    try {
                        const data = await response.json();
                        errorMsg = data.error || errorMsg;
                    } catch (e) { }
                    throw new Error(errorMsg);
                }

                console.log(`Chat ${chatId} borrado en backend.`);
                itemElement.remove();

                if (state.currentChatId === chatId) {
                    console.log("El chat activo fue borrado.");
                    state.currentChatId = null;
                    UI.clearChatLog();

                    const remainingHistory = await this.loadList();
                    if (remainingHistory.length > 0) {
                        const firstChatId = remainingHistory[0].id;
                        await Chat.load(firstChatId);
                        const firstLink = elements.chatHistoryNav.querySelector(`.history-item[data-chat-id="${firstChatId}"]`);
                        if (firstLink) firstLink.classList.add('active');
                    } else {
                        // No crear automáticamente un nuevo chat, solo mostrar mensaje de bienvenida
                        console.log("No quedan chats. Esperando input del usuario...");
                        if (elements.welcomeMessage) {
                            elements.welcomeMessage.style.display = 'flex';
                        }
                    }
                } else {
                    await this.loadList();
                }
            } catch (error) {
                console.error("Error borrando chat:", error);
                alert(`No se pudo borrar el chat: ${error.message}`);
            } finally {
                UI.setLoadingState(false);
            }
        }
    };

    // --- Funciones de Chat ---
    const Chat = {
        async startNew() {
            if (state.isLoading) return;

            UI.setLoadingState(true);
            console.log("Iniciando nuevo chat...");
            UI.clearChatLog();

            try {
                const response = await fetch("/new_chat", { method: "POST" });
                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const data = await response.json();
                state.currentChatId = data.chat_id;
                console.log("Nuevo chat iniciado:", state.currentChatId);

                await History.loadList();
                const newLink = elements.chatHistoryNav.querySelector(`.history-item[data-chat-id="${state.currentChatId}"]`);
                if (newLink) newLink.classList.add('active');
            } catch (error) {
                console.error("Error en startNewChat:", error);
                UI.addMessageToLog("error", `No se pudo iniciar chat: ${error.message}`);
                state.currentChatId = null;
            } finally {
                UI.setLoadingState(false);
            }
        },

        async load(chatId) {
            if (state.isLoading) return;

            UI.setLoadingState(true);
            console.log(`Cargando chat: ${chatId}`);
            UI.clearChatLog();

            try {
                const response = await fetch(`/chat/${chatId}`);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const data = await response.json();
                state.currentChatId = data.chat_id;

                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(msg => {
                        if (msg.role !== 'system') {
                            UI.addMessageToLog(msg.role === 'user' ? 'usuario' : 'bot', msg.content, true);
                        }
                    });
                }
                console.log(`Chat ${state.currentChatId} cargado.`);
            } catch (error) {
                console.error("Error cargando chat:", error);
                UI.addMessageToLog("error", `No se pudo cargar chat: ${error.message}`);
                state.currentChatId = null;
            } finally {
                UI.setLoadingState(false);
                document.querySelectorAll('.history-item.active').forEach(el => el.classList.remove('active'));
                const activeLink = elements.chatHistoryNav.querySelector(`.history-item[data-chat-id="${state.currentChatId}"]`);
                if (activeLink) activeLink.classList.add('active');
            }
        },

        async sendMessage() {
            const messageText = elements.userInput.value.trim();

            // Validaciones básicas
            if (!messageText || state.isLoading) {
                return;
            }

            // Si no hay chat activo, crear uno nuevo automáticamente
            if (!state.currentChatId) {
                console.log("No hay chat activo. Creando nuevo chat automáticamente...");
                await this.startNew();

                // Si aún no hay chat después de intentar crear uno, salir
                if (!state.currentChatId) {
                    console.error("No se pudo crear un nuevo chat automáticamente.");
                    return;
                }
            }

            // Obtener modelo seleccionado
            const selectedModel = elements.modelSelector?.value || null;
            if (!selectedModel) {
                console.warn("Selector de modelo no encontrado. Usando modelo default del backend.");
            }

            UI.setLoadingState(true);
            const currentText = messageText;
            elements.userInput.value = "";
            elements.userInput.style.height = 'auto';

            UI.addMessageToLog("usuario", currentText, false);

            try {
                const requestBody = { mensaje: currentText };
                if (selectedModel) {
                    requestBody.modelo = selectedModel;
                }

                console.log("Enviando al backend:", requestBody);

                const response = await fetch(`/chat/${state.currentChatId}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify(requestBody)
                });

                if (!response.ok) {
                    let errorMsg = `Error HTTP ${response.status}`;
                    try {
                        const data = await response.json();
                        errorMsg = data.error || errorMsg;
                    } catch (e) { }
                    throw new Error(errorMsg);
                }

                const data = await response.json();
                UI.addMessageToLog("bot", data.respuesta || "No se recibió respuesta.", true);

                // Actualizar historial si cambió el título
                await History.loadList();

            } catch (error) {
                console.error("Error en sendMessage:", error);
                UI.addMessageToLog("error", error.message || "Error de conexión.");
            } finally {
                UI.setLoadingState(false);
                UI.adjustTextareaHeight();
            }
        }
    };

    // --- Event Listeners ---
    elements.sendButton.addEventListener("click", Chat.sendMessage);

    elements.userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            Chat.sendMessage();
        }
    });

    elements.userInput.addEventListener('input', UI.adjustTextareaHeight);

    if (elements.newChatButton) {
        elements.newChatButton.addEventListener("click", Chat.startNew);
    }

    // --- Inicialización ---
    async function initializeApp() {
        const initialHistory = await History.loadList();
        const mostRecentChatLink = elements.chatHistoryNav.querySelector('.history-item');

        if (mostRecentChatLink) {
            await Chat.load(mostRecentChatLink.dataset.chatId);
            // Marcar el chat activo
            const activeLink = elements.chatHistoryNav.querySelector(`.history-item[data-chat-id="${state.currentChatId}"]`);
            if (activeLink) activeLink.classList.add('active');
        } else {
            // No hay chats existentes, mostrar mensaje de bienvenida y esperar input del usuario
            console.log("No hay chats previos. Esperando que el usuario escriba algo...");
            if (elements.welcomeMessage) {
                elements.welcomeMessage.style.display = 'flex';
            }
        }
    }

    initializeApp();
});