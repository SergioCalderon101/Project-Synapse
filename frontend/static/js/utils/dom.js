/**
 * DOM manipulation utilities
 * Helper functions for common DOM operations
 */

/**
 * Get element by ID
 * @param {string} id - Element ID
 * @returns {HTMLElement|null} The element or null if not found
 */
export function getElement(id) {
    return document.getElementById(id);
}

/**
 * Query selector
 * @param {string} selector - CSS selector
 * @param {HTMLElement} [parent=document] - Parent element to query from
 * @returns {HTMLElement|null} The element or null if not found
 */
export function querySelector(selector, parent = document) {
    return parent.querySelector(selector);
}

/**
 * Query all elements
 * @param {string} selector - CSS selector
 * @param {HTMLElement} [parent=document] - Parent element to query from
 * @returns {NodeList} List of matching elements
 */
export function querySelectorAll(selector, parent = document) {
    return parent.querySelectorAll(selector);
}

/**
 * Create element with optional attributes and content
 * @param {string} tag - HTML tag name
 * @param {Object} [attributes={}] - Element attributes
 * @param {string} [content=''] - Element content (text or HTML)
 * @returns {HTMLElement} Created element
 */
export function createElement(tag, attributes = {}, content = '') {
    const element = document.createElement(tag);
    
    Object.entries(attributes).forEach(([key, value]) => {
        if (key === 'className') {
            element.className = value;
        } else if (key === 'innerHTML') {
            element.innerHTML = value;
        } else if (key === 'textContent') {
            element.textContent = value;
        } else {
            element.setAttribute(key, value);
        }
    });
    
    if (content) {
        element.innerHTML = content;
    }
    
    return element;
}

/**
 * Add class to element
 * @param {HTMLElement} element - Target element
 * @param {string} className - Class name to add
 */
export function addClass(element, className) {
    if (element) {
        element.classList.add(className);
    }
}

/**
 * Remove class from element
 * @param {HTMLElement} element - Target element
 * @param {string} className - Class name to remove
 */
export function removeClass(element, className) {
    if (element) {
        element.classList.remove(className);
    }
}

/**
 * Toggle class on element
 * @param {HTMLElement} element - Target element
 * @param {string} className - Class name to toggle
 */
export function toggleClass(element, className) {
    if (element) {
        element.classList.toggle(className);
    }
}

/**
 * Scroll element to bottom
 * @param {HTMLElement} element - Element to scroll
 * @param {boolean} [smooth=true] - Use smooth scrolling
 */
export function scrollToBottom(element, smooth = true) {
    if (element) {
        element.scrollTo({
            top: element.scrollHeight,
            behavior: smooth ? 'smooth' : 'auto'
        });
    }
}

/**
 * Wait for next animation frame
 * @returns {Promise<void>} Promise that resolves on next animation frame
 */
export function nextFrame() {
    return new Promise(resolve => requestAnimationFrame(resolve));
}
