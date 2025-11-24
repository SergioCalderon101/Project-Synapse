import { getElement, createElement, addClass, scrollToBottom, nextFrame } from '../../utils/dom.js';
import { renderMarkdown, highlightCodeBlocks } from '../../utils/markdown.js';
import { CONFIG } from '../../config/app.config.js';

/**
 * Chat view for rendering messages and UI updates
 * Handles all chat-related UI rendering
 * 
 * To test: Mock DOM elements and verify rendering methods work correctly
 */
export class ChatView {
    /**
     * Create ChatView
     * @param {Object} elements - DOM element references
     */
    constructor(elements) {
        this.elements = elements;
    }

    /**
     * Get message CSS class based on type
     * @param {string} type - Message type
     * @returns {string} CSS class
     * @private
     */
    getMessageClass(type) {
        const classes = {
            [CONFIG.MESSAGE_TYPES.USER]: 'user-message',
            [CONFIG.MESSAGE_TYPES.BOT]: 'bot-message',
            [CONFIG.MESSAGE_TYPES.ERROR]: 'error-message'
        };
        return classes[type] || 'message';
    }

    /**
     * Create message element
     * @param {string} type - Message type
     * @param {string} content - Message content
     * @param {boolean} [isHTML=false] - Whether content is HTML
     * @returns {HTMLElement} Message element
     * @private
     */
    createMessageElement(type, content, isHTML = false) {
        const messageWrapper = createElement('div', {
            className: `message ${this.getMessageClass(type)}`
        });

        const messageContentDiv = createElement('div', {
            className: 'message-content'
        });

        if (type === CONFIG.MESSAGE_TYPES.BOT && !isHTML) {
            const { html, isRendered } = renderMarkdown(content);
            messageContentDiv.innerHTML = html;
            
            if (isRendered) {
                highlightCodeBlocks(messageContentDiv);
            }
        } else {
            messageContentDiv[isHTML ? 'innerHTML' : 'textContent'] = content;
        }

        if (type === CONFIG.MESSAGE_TYPES.ERROR) {
            const errorIcon = createElement('i', { className: 'bx bx-error-circle' });
            messageContentDiv.prepend(errorIcon);
        }

        messageWrapper.appendChild(messageContentDiv);
        return messageWrapper;
    }

    /**
     * Add message to chat log
     * @param {string} type - Message type
     * @param {string} content - Message content
     * @param {boolean} [isHTML=false] - Whether content is HTML
     */
    addMessage(type, content, isHTML = false) {
        if (this.elements.welcomeMessage?.style.display !== 'none') {
            this.elements.welcomeMessage.style.display = 'none';
        }

        const messageElement = this.createMessageElement(type, content, isHTML);
        this.elements.chatLog.appendChild(messageElement);

        nextFrame().then(() => {
            addClass(messageElement, 'message-visible');
        });

        this.scrollToBottom();
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        const typingDiv = createElement('div', {
            className: 'message bot-message typing-indicator',
            id: 'typing-indicator',
            innerHTML: `
                <div class="message-content">
                    <div class="dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `
        });
        
        this.elements.chatLog.appendChild(typingDiv);
        this.scrollToBottom();
    }

    /**
     * Remove typing indicator
     */
    removeTypingIndicator() {
        getElement('typing-indicator')?.remove();
    }

    /**
     * Clear chat log
     */
    clearChatLog() {
        this.elements.chatLog.innerHTML = '';
        if (this.elements.welcomeMessage) {
            this.elements.welcomeMessage.style.setProperty('display', 'flex');
        }
        this.clearInput();
    }

    /**
     * Clear and reset input field
     */
    clearInput() {
        this.elements.userInput.value = '';
        this.elements.userInput.style.height = 'auto';
    }

    /**
     * Adjust textarea height based on content
     */
    adjustTextareaHeight() {
        this.elements.userInput.style.height = 'auto';
        this.elements.userInput.style.height = (this.elements.userInput.scrollHeight) + 'px';
    }

    /**
     * Scroll chat to bottom
     * @param {boolean} [smooth=true] - Use smooth scrolling
     */
    scrollToBottom(smooth = true) {
        scrollToBottom(this.elements.chatLog, smooth);
    }

    /**
     * Set loading state for UI
     * @param {boolean} loading - Whether loading
     */
    setLoadingState(loading) {
        this.elements.userInput.disabled = loading;
        this.elements.sendButton.disabled = loading;

        if (loading) {
            this.elements.sendButton.innerHTML = "<i class='bx bx-loader-alt bx-spin'></i>";
        } else {
            this.elements.sendButton.innerHTML = "<i class='bx bxs-send'></i>";
            this.elements.userInput.focus();
        }
    }

    /**
     * Render messages in the chat
     * @param {Array} messages - Array of message objects
     */
    renderMessages(messages) {
        if (!messages || messages.length === 0) return;

        messages.forEach(msg => {
            if (msg.role !== 'system') {
                const messageType = msg.role === 'user' 
                    ? CONFIG.MESSAGE_TYPES.USER 
                    : CONFIG.MESSAGE_TYPES.BOT;
                this.addMessage(messageType, msg.content, false);
            }
        });
    }
}
