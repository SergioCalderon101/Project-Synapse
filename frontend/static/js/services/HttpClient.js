/**
 * Base HTTP client for API calls
 * Provides common functionality for all API requests
 */
export class HttpClient {
    /**
     * Create HTTP client
     * @param {string} baseURL - Base URL for API calls
     */
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    /**
     * Make a GET request
     * @param {string} url - URL to fetch
     * @returns {Promise<Object>} Response data
     * @throws {Error} If request fails
     */
    async get(url) {
        return this.request(url, { method: 'GET' });
    }

    /**
     * Make a POST request
     * @param {string} url - URL to post to
     * @param {Object} data - Data to send
     * @returns {Promise<Object>} Response data
     * @throws {Error} If request fails
     */
    async post(url, data) {
        return this.request(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        });
    }

    /**
     * Make a DELETE request
     * @param {string} url - URL to delete
     * @returns {Promise<Object>} Response data
     * @throws {Error} If request fails
     */
    async delete(url) {
        return this.request(url, { method: 'DELETE' });
    }

    /**
     * Core request method
     * @param {string} url - URL to request
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} Response data
     * @throws {Error} If request fails
     * @private
     */
    async request(url, options) {
        const fullUrl = this.baseURL + url;
        
        try {
            const response = await fetch(fullUrl, options);
            
            if (!response.ok) {
                const errorMsg = await this.extractErrorMessage(response);
                throw new Error(errorMsg);
            }

            // Check if response has content
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return { success: true };
        } catch (error) {
            console.error(`HTTP ${options.method} error for ${url}:`, error);
            throw error;
        }
    }

    /**
     * Extract error message from response
     * @param {Response} response - Fetch response
     * @returns {Promise<string>} Error message
     * @private
     */
    async extractErrorMessage(response) {
        let errorMsg = `Error HTTP ${response.status}`;
        try {
            const data = await response.json();
            errorMsg = data.error || errorMsg;
        } catch (e) {
            // If JSON parsing fails, use default message
        }
        return errorMsg;
    }
}
