import { HttpClient } from './HttpClient.js';

/**
 * Service for history-related API calls
 * Handles loading chat history
 * 
 * To test: Mock HttpClient and verify HistoryService calls it correctly
 * Example: const mockHttp = { get: jest.fn() }; new HistoryService(mockHttp);
 */
export class HistoryService {
    /**
     * Create HistoryService
     * @param {HttpClient} httpClient - HTTP client instance
     */
    constructor(httpClient = new HttpClient()) {
        this.http = httpClient;
    }

    /**
     * Load chat history
     * @returns {Promise<Object>} Response with history array
     * @throws {Error} If request fails
     */
    async loadHistory() {
        return this.http.get('/api/v1/history');
    }
}
