/**
 * Markdown rendering utilities
 * Wrapper for marked.js with syntax highlighting
 */

/**
 * Render markdown to HTML
 * @param {string} content - Markdown content
 * @returns {Object} Result with { html: string, isRendered: boolean }
 */
export function renderMarkdown(content) {
    if (typeof marked === 'undefined') {
        console.warn('Marked.js not loaded');
        return { html: content, isRendered: false };
    }
    
    try {
        const htmlContent = marked.parse(content);
        return { html: htmlContent, isRendered: true };
    } catch (e) {
        console.error('Error parsing markdown:', e);
        return { html: content, isRendered: false };
    }
}

/**
 * Apply syntax highlighting to code blocks
 * @param {HTMLElement} container - Container element with code blocks
 */
export function highlightCodeBlocks(container) {
    if (typeof hljs === 'undefined') {
        console.warn('Highlight.js not loaded');
        return;
    }
    
    const codeBlocks = container.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        try {
            hljs.highlightElement(block);
        } catch (e) {
            console.error('Error highlighting code block:', e);
        }
    });
}
