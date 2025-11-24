/**
 * Application configuration constants
 * Centralized configuration for the entire application
 */

/**
 * @typedef {Object} AppConfig
 * @property {string} DEFAULT_MODEL - Default AI model
 * @property {string} STORAGE_KEY - LocalStorage key for model selection
 * @property {Object} MESSAGE_TYPES - Message type constants
 * @property {number} TOAST_DURATION - Toast notification duration in ms
 * @property {Object} MODEL_NAMES - Display names for AI models
 * @property {Object} MARKED_OPTIONS - Marked.js configuration
 */

export const CONFIG = {
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

/**
 * Configure Marked.js for markdown rendering
 * Sets up syntax highlighting with Highlight.js
 */
export function configureMarked() {
    if (typeof marked !== 'undefined') {
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
    }
}
