// --- script.js (v5 - CON BORRADO DE CHAT y ENVÍO DE MODELO) ---
document.addEventListener("DOMContentLoaded", () => {
    // --- Elementos UI ---
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-btn");
    const chatLog = document.getElementById("chat-log");
    const welcomeMessage = document.getElementById("welcome-message");
    const newChatButton = document.querySelector(".new-chat-btn");
    const chatHistoryNav = document.querySelector(".chat-history");
    // ---> AQUI CAMBIO <--- : Referencia al selector de modelo (Asegúrate que este ID exista en tu HTML)
    const modelSelector = document.getElementById("modelo-selector");

    // --- Estado App ---
    let currentChatId = null;
    let isLoading = false;

    // --- Funciones UI (createMessageElement, displayPdfLink, clearChatLog, addMessageToLog - sin cambios) ---
    function createMessageElement(type, content, isHTML = false) {
        const messageWrapper = document.createElement("div");
        messageWrapper.className = `message ${type === "usuario" ? "user-message" : type === "bot" ? "bot-message" : "error-message"}`;
        const messageContentDiv = document.createElement("div");
        messageContentDiv.className = "message-content";
        if (isHTML) { messageContentDiv.innerHTML = content; }
        else { messageContentDiv.textContent = content; }
        if (type === "error") { const p = document.createElement("strong"); p.textContent = "Error: "; messageContentDiv.prepend(p); }
        messageWrapper.appendChild(messageContentDiv);
        return messageWrapper;
    }
    function displayPdfLink(pdfUrl) {
        const el = createMessageElement("bot", '', true); const content = el.querySelector('.message-content');
        const a = document.createElement("a"); a.href = pdfUrl; a.target = "_blank";
        a.textContent = "📄 Descargar PDF generado"; a.style.color = "#93C5FD"; a.style.textDecoration = "underline";
        content.appendChild(a); chatLog.appendChild(el); chatLog.scrollTop = chatLog.scrollHeight;
    }
    function clearChatLog() {
        chatLog.innerHTML = ''; if (welcomeMessage) { welcomeMessage.style.display = 'flex'; }
        userInput.value = ""; userInput.style.height = 'auto';
    }
    function addMessageToLog(type, content, isHTML = false) {
        if (welcomeMessage && welcomeMessage.style.display !== 'none') { welcomeMessage.style.display = 'none'; }
        const el = createMessageElement(type, content, isHTML); chatLog.appendChild(el);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    // --- Funciones Historial (loadHistoryList, deleteChat, loadSpecificChat - sin cambios respecto a v4) ---
    // (Copiar las funciones loadHistoryList, deleteChat, loadSpecificChat de la versión anterior aquí)
    // ...
    // --- (Inicio funciones historial sin cambios v4) ---
    async function loadHistoryList() {
        if (!chatHistoryNav) return; console.log("Cargando historial...");
        const previouslyActiveId = currentChatId; let historyData = [];
        try {
            const response = await fetch("/history"); if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json(); historyData = data.history || [];
            chatHistoryNav.innerHTML = '';
            if (historyData.length > 0) {
                historyData.forEach(chat => {
                    const itemContainer = document.createElement("div"); itemContainer.className = "history-item-container";
                    const link = document.createElement("a"); link.href = "#"; link.className = "history-item";
                    link.textContent = chat.title || `Chat ${chat.id.substring(0, 8)}`; link.dataset.chatId = chat.id;
                    link.addEventListener("click", async (e) => {
                        e.preventDefault(); if (isLoading || currentChatId === chat.id) return;
                        await loadSpecificChat(chat.id);
                        document.querySelectorAll('.history-item.active').forEach(el => el.classList.remove('active'));
                        link.classList.add('active');
                    });
                    const deleteButton = document.createElement("button"); deleteButton.className = "delete-chat-btn"; deleteButton.innerHTML = "&times;";
                    deleteButton.title = "Borrar este chat"; deleteButton.dataset.chatId = chat.id;
                    deleteButton.addEventListener("click", async (e) => {
                        e.stopPropagation(); if (isLoading) return;
                        if (confirm(`¿Estás seguro de que quieres borrar el chat "${link.textContent}"?`)) {
                            await deleteChat(chat.id, itemContainer);
                        }
                    });
                    itemContainer.appendChild(link); itemContainer.appendChild(deleteButton);
                    chatHistoryNav.appendChild(itemContainer);
                    if (currentChatId === chat.id) { link.classList.add('active'); }
                });
            } else {
                console.log("No se encontró historial."); if (!currentChatId) await startNewChat();
            }
        } catch (error) {
            console.error("Error cargando historial:", error); chatHistoryNav.innerHTML = '<span class="history-error">Error al cargar historial</span>';
            if (previouslyActiveId) currentChatId = previouslyActiveId;
        }
        return historyData;
    }
    async function deleteChat(chatId, itemElement) {
        if (isLoading) return; isLoading = true; console.log(`Intentando borrar chat: ${chatId}`);
        try {
            const response = await fetch(`/chat/${chatId}`, { method: 'DELETE' });
            if (!response.ok) { let errorMsg = `Error HTTP ${response.status}`; try { const data = await response.json(); errorMsg = data.error || errorMsg; } catch (e) { } throw new Error(errorMsg); }
            console.log(`Chat ${chatId} borrado en backend.`); itemElement.remove();
            if (currentChatId === chatId) {
                console.log("El chat activo fue borrado."); currentChatId = null; clearChatLog();
                const remainingHistory = await loadHistoryList();
                if (remainingHistory.length > 0) {
                    const firstChatId = remainingHistory[0].id; await loadSpecificChat(firstChatId);
                    const firstLink = chatHistoryNav.querySelector(`.history-item[data-chat-id="${firstChatId}"]`); if (firstLink) firstLink.classList.add('active');
                } else { await startNewChat(); }
            } else { await loadHistoryList(); }
        } catch (error) { console.error("Error borrando chat:", error); alert(`No se pudo borrar el chat: ${error.message}`); }
        finally { isLoading = false; }
    }
    async function loadSpecificChat(chatId) {
        if (isLoading) return; isLoading = true; console.log(`Cargando chat: ${chatId}`); clearChatLog();
        try {
            const response = await fetch(`/chat/${chatId}`); if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json(); currentChatId = data.chat_id;
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => { if (msg.role !== 'system') { addMessageToLog(msg.role === 'user' ? 'usuario' : 'bot', msg.content, true); } });
            } console.log(`Chat ${currentChatId} cargado.`);
        } catch (error) { console.error("Error cargando chat:", error); addMessageToLog("error", `No se pudo cargar chat: ${error.message}`); currentChatId = null; }
        finally {
            isLoading = false; userInput.disabled = false; sendButton.disabled = false; userInput.focus();
            document.querySelectorAll('.history-item.active').forEach(el => el.classList.remove('active'));
            const activeLink = chatHistoryNav.querySelector(`.history-item[data-chat-id="${currentChatId}"]`);
            if (activeLink) activeLink.classList.add('active');
        }
    }
    // --- (Fin funciones historial sin cambios v4) ---


    // --- Funciones de Lógica de Chat ---

    // (startNewChat - sin cambios respecto a v4)
    async function startNewChat() {
        if (isLoading) return; isLoading = true; console.log("Iniciando nuevo chat..."); clearChatLog();
        try {
            const response = await fetch("/new_chat", { method: "POST" }); if (!response.ok) { throw new Error(`HTTP ${response.status}`) }
            const data = await response.json(); currentChatId = data.chat_id; console.log("Nuevo chat iniciado:", currentChatId);
            await loadHistoryList();
            const newLink = chatHistoryNav.querySelector(`.history-item[data-chat-id="${currentChatId}"]`);
            if (newLink) newLink.classList.add('active');
        } catch (error) { console.error("Error en startNewChat:", error); addMessageToLog("error", `No se pudo iniciar chat: ${error.message}`); currentChatId = null; }
        finally { isLoading = false; userInput.disabled = false; sendButton.disabled = false; userInput.focus(); }
    }


    // ---> AQUI CAMBIO <--- : Modificada la función sendMessage
    async function sendMessage() {
        const messageText = userInput.value.trim();

        // 1. ---> AQUI CAMBIO <--- : Obtener el modelo seleccionado
        //    Asegúrate de que el elemento con id 'modelo-selector' exista en tu HTML
        //    y tenga 'value's que correspondan a los nombres de modelo de OpenAI (ej. gpt-3.5-turbo)
        let selectedModel = null;
        if (modelSelector) {
            selectedModel = modelSelector.value;
        } else {
            console.warn("Selector de modelo no encontrado (ID: modelo-selector). Usando modelo default del backend.");
            // No enviamos la clave 'modelo', el backend usará su default
        }

        if (!messageText || !currentChatId || isLoading) {
            if (!currentChatId) console.error("No hay chat ID activo.");
            return;
        }

        isLoading = true;
        const currentText = messageText; // Guardar antes de limpiar
        userInput.value = "";
        userInput.disabled = true;
        sendButton.disabled = true;
        userInput.style.height = 'auto'; // Reset height

        addMessageToLog("usuario", currentText, false); // Añadir mensaje de usuario a la UI

        try {
            // 2. ---> AQUI CAMBIO <--- : Construir el cuerpo (body) del request
            const requestBody = {
                mensaje: currentText
            };
            // Añadir el modelo solo si se seleccionó uno
            if (selectedModel) {
                requestBody.modelo = selectedModel;
            }
            console.log("Enviando al backend:", requestBody); // Para depurar

            const response = await fetch(`/chat/${currentChatId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(requestBody) // Enviar el cuerpo construido
            });

            if (!response.ok) {
                let errorMsg = `Error HTTP ${response.status}`;
                try { const data = await response.json(); errorMsg = data.error || errorMsg; } catch (e) { }
                throw new Error(errorMsg);
            }

            const data = await response.json();
            addMessageToLog("bot", data.respuesta || "No se recibió respuesta.", true); // Añadir respuesta del bot
            if (data.link_pdf) {
                displayPdfLink(data.link_pdf); // Mostrar enlace PDF si existe
            }

            // Actualizar historial por si cambió el título o para mantener consistencia
            // Podríamos optimizar esto para solo recargar si data.new_title existe y es diferente
            await loadHistoryList();

        } catch (error) {
            console.error("Error en sendMessage:", error);
            addMessageToLog("error", error.message || "Error de conexión.");
        } finally {
            isLoading = false;
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
            // Reajustar altura por si acaso
            userInput.style.height = 'auto';
            userInput.style.height = (userInput.scrollHeight) + 'px';
        }
    }

    // --- Event Listeners (sin cambios) ---
    sendButton.addEventListener("click", sendMessage);
    userInput.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } });
    userInput.addEventListener('input', () => { userInput.style.height = 'auto'; userInput.style.height = (userInput.scrollHeight) + 'px'; });
    if (newChatButton) { newChatButton.addEventListener("click", startNewChat); }

    // --- Inicialización (sin cambios) ---
    async function initializeApp() {
        const initialHistory = await loadHistoryList();
        const mostRecentChatLink = chatHistoryNav.querySelector('.history-item');
        if (mostRecentChatLink) {
            await loadSpecificChat(mostRecentChatLink.dataset.chatId);
        } else {
            await startNewChat();
        }
        // Asegurarse de marcar el activo después de cargar
        const activeLink = chatHistoryNav.querySelector(`.history-item[data-chat-id="${currentChatId}"]`);
        if (activeLink) activeLink.classList.add('active');
    }
    initializeApp();

});