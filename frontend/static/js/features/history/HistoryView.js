import { createElement, querySelectorAll } from '../../utils/dom.js';

/**
 * History view for rendering chat history
 * Handles all history-related UI rendering
 * 
 * To test: Mock DOM elements and verify rendering methods work correctly
 */
export class HistoryView {
    /**
     * Create HistoryView
     * @param {Object} elements - DOM element references
     */
    constructor(elements) {
        this.elements = elements;
    }

    /**
     * Render history list
     * @param {Array} historyData - Array of chat history items
     * @param {string|null} currentChatId - Currently active chat ID
     * @param {Function} onItemClick - Callback for item click
     * @param {Function} onDeleteClick - Callback for delete button click
     */
    render(historyData, currentChatId, onItemClick, onDeleteClick) {
        if (!this.elements.chatHistoryNav) return;

        this.elements.chatHistoryNav.innerHTML = '';

        if (historyData.length === 0) {
            if (this.elements.welcomeMessage) {
                this.elements.welcomeMessage.style.display = 'flex';
            }
            return;
        }

        historyData.forEach(chat => {
            const itemContainer = this.createHistoryItem(
                chat,
                currentChatId === chat.id,
                onItemClick,
                onDeleteClick
            );
            this.elements.chatHistoryNav.appendChild(itemContainer);
        });
    }

    /**
     * Create a single history item element
     * @param {Object} chat - Chat data
     * @param {boolean} isActive - Whether this chat is active
     * @param {Function} onItemClick - Callback for item click
     * @param {Function} onDeleteClick - Callback for delete button click
     * @returns {HTMLElement} History item container
     * @private
     */
    createHistoryItem(chat, isActive, onItemClick, onDeleteClick) {
        const itemContainer = createElement('div', {
            className: 'history-item-container'
        });

        const link = createElement('a', {
            href: '#',
            className: `history-item${isActive ? ' active' : ''}`,
            textContent: chat.title || `Chat ${chat.id.substring(0, 8)}`
        });
        link.dataset.chatId = chat.id;

        link.addEventListener('click', (e) => {
            e.preventDefault();
            onItemClick(chat.id, link);
        });

        const deleteButton = createElement('button', {
            className: 'delete-chat-btn',
            innerHTML: '&times;',
            title: 'Borrar este chat'
        });
        deleteButton.dataset.chatId = chat.id;

        deleteButton.addEventListener('click', (e) => {
            e.stopPropagation();
            onDeleteClick(chat.id, link.textContent, itemContainer);
        });

        itemContainer.append(link, deleteButton);
        return itemContainer;
    }

    /**
     * Update active history item
     * @param {string} chatId - Chat ID to mark as active
     */
    updateActiveItem(chatId) {
        // Remove active class from all
        querySelectorAll('.history-item.active').forEach(el => {
            el.classList.remove('active');
        });

        // Add active class to selected
        const activeLink = this.elements.chatHistoryNav
            ?.querySelector(`.history-item[data-chat-id="${chatId}"]`);
        activeLink?.classList.add('active');
    }

    /**
     * Show error in history
     * @param {string} message - Error message
     */
    showError(message) {
        if (this.elements.chatHistoryNav) {
            this.elements.chatHistoryNav.innerHTML = 
                `<span class="history-error">${message}</span>`;
        }
    }

    /**
     * Get item element by chat ID
     * @param {string} chatId - Chat ID
     * @returns {HTMLElement|null} Item container element
     */
    getItemElement(chatId) {
        return this.elements.chatHistoryNav
            ?.querySelector(`.history-item[data-chat-id="${chatId}"]`)
            ?.parentElement;
    }
}
