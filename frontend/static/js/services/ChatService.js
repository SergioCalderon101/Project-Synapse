import { HttpClient } from './HttpClient.js';

/**
 * Service for chat-related API calls
 * Handles all chat operations: create, load, send message
 * 
 * To test: Mock HttpClient and verify ChatService calls it correctly
 * Example: const mockHttp = { post: jest.fn() }; new ChatService(mockHttp);
 */
export class ChatService {
    /**
     * Create ChatService
     * @param {HttpClient} httpClient - HTTP client instance
     */
    constructor(httpClient = new HttpClient()) {
        this.http = httpClient;
    }

    /**
     * Create a new chat
     * @returns {Promise<Object>} Response with chat_id
     * @throws {Error} If request fails
     */
    async createChat() {
        return this.http.post('/api/v1/chat');
    }

    /**
     * Load an existing chat
     * @param {string} chatId - The chat ID to load
     * @returns {Promise<Object>} Response with chat data and messages
     * @throws {Error} If request fails
     */
    async loadChat(chatId) {
        return this.http.get(`/api/v1/chat/${chatId}`);
    }

    /**
     * Send a message to a chat
     * @param {string} chatId - The chat ID
     * @param {string} message - The message content
     * @param {string} [model] - Optional AI model to use
     * @returns {Promise<Object>} Response with bot reply
     * @throws {Error} If request fails
     */
    async sendMessage(chatId, message, model = null) {
        const requestBody = {
            mensaje: message,
            ...(model && { modelo: model })
        };
        
        return this.http.post(`/api/v1/chat/${chatId}`, requestBody);
    }

    /**
     * Delete a chat
     * @param {string} chatId - The chat ID to delete
     * @returns {Promise<Object>} Success response
     * @throws {Error} If request fails
     */
    async deleteChat(chatId) {
        return this.http.delete(`/api/v1/chat/${chatId}`);
    }
}
