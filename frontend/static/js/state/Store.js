/**
 * Simple state management store using Observer pattern
 * Allows components to subscribe to state changes
 */
export class Store {
    /**
     * Create a new Store instance
     * @param {Object} initialState - Initial state object
     */
    constructor(initialState = {}) {
        this.state = initialState;
        this.listeners = new Set();
    }

    /**
     * Get current state
     * @returns {Object} Current state
     */
    getState() {
        return this.state;
    }

    /**
     * Update state and notify listeners
     * @param {Object} updates - Partial state updates
     * @param {boolean} silent - If true, don't notify listeners
     */
    setState(updates, silent = false) {
        this.state = { ...this.state, ...updates };
        if (!silent) {
            this.notify();
        }
    }

    /**
     * Subscribe to state changes
     * @param {Function} listener - Callback function to call on state change
     * @returns {Function} Unsubscribe function
     */
    subscribe(listener) {
        this.listeners.add(listener);
        // Return unsubscribe function
        return () => this.listeners.delete(listener);
    }

    /**
     * Notify all listeners of state change
     */
    notify() {
        this.listeners.forEach(listener => {
            try {
                listener(this.state);
            } catch (error) {
                console.error('Error in state listener:', error);
            }
        });
    }
}
