/**
 * Validation utilities
 * Reusable validation functions
 */

/**
 * Validate message text
 * @param {string} message - Message to validate
 * @returns {Object} Validation result { valid: boolean, error: string|null }
 */
export function validateMessage(message) {
    const trimmed = message.trim();
    
    if (!trimmed) {
        return { valid: false, error: 'El mensaje no puede estar vacío' };
    }
    
    if (trimmed.length > 4000) {
        return { valid: false, error: 'El mensaje es demasiado largo (máximo 4000 caracteres)' };
    }
    
    return { valid: true, error: null };
}

/**
 * Validate chat ID format
 * @param {string} chatId - Chat ID to validate
 * @returns {boolean} Whether chat ID is valid
 */
export function isValidChatId(chatId) {
    return typeof chatId === 'string' && chatId.length > 0;
}

/**
 * Validate model selection
 * @param {string} model - Model identifier
 * @param {string[]} availableModels - Array of available model IDs
 * @returns {boolean} Whether model is valid
 */
export function isValidModel(model, availableModels) {
    return availableModels.includes(model);
}
